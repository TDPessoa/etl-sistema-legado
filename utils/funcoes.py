"""
Funções utilitárias responsáveis pela coleta, leitura de arquivos,
persistência em banco de dados e processamento de páginas.
"""

import datetime
import os
import re
import json

import openpyxl
import pyodbc
from openpyxl import load_workbook
from bs4 import BeautifulSoup
from hashlib import sha256
from win32com.client import Dispatch
from numpy import array
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import requests
from selenium import webdriver, common
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from utils.config import (
    ETIQUETAS_HTML,
    CAMINHO_METADADOS,
    STR_CONEXAO_ACCESS,
    CAMINHO_ALVOS,
    URL_PARA_LOGIN,
    URL_DE_DADOS,
    MAPAS,
    ACESSO_AUTOMATICO,
    TAMANHO_DA_TELA,
    USUARIO,
    SENHA,
    CAMINHO_CHROME
)
from utils.instrucoes_sql import (
    SELECAO_IDS_BANCO_DE_DADOS,
    POPULAR_DADOS,
    POPULAR_METADADOS,
    NOVO_METADADOS,
    SELECAO_IDS_METADADOS,
    EXCLUSAO_METADADOS,
    EXCLUSAO_DADOS
)
from utils.classes.Excecoes import (
    ErroFalhaConexaoBancoDeDados,
    ErroPastaDeAlvosVazia,
    ErroNenhumAlvoPassado,
    ErroNenhumArquivoValidoEmAlvos,
    AlvosJaConstamNoBancoDeDados
)


def salvar_dados(conexao: pyodbc.Connection, dados: dict) -> None:
    """Salva os dados coletados no banco principal."""
    chaves: list[str] = list(ETIQUETAS_HTML.keys())
    cursor: pyodbc.Cursor = conexao.cursor()

    blocos_de_dados: list[tuple[str]] = gerar_tuplas_de_insercao(dados, chaves)
    for bloco in blocos_de_dados:
        cursor.execute(POPULAR_DADOS.format(*bloco))

    cursor.commit()
    cursor.close()


def selecionar_ids(conexao: pyodbc.Connection, declaracao: str) -> list[str]:
    """Retorna os identificadores obtidos por uma consulta SQL."""
    cursor: pyodbc.Cursor = conexao.cursor()
    lista_ids: list[pyodbc.Row] = cursor.execute(declaracao).fetchall()
    lista_final: list[str] = []
    for resultado in lista_ids:
        lista_final.append(str(resultado[0]))
    cursor.close()
    return lista_final


def salvar_metadados(metadados: dict) -> None:
    """Salva os metadados nos bancos correspondentes a cada ano."""
    anos: list[str] = list(metadados.keys())
    chaves: list[str] = ['id', 'data_coleta', 'sha', 'texto_html']
    for ano in anos:
        nome_banco: str = f'metadados_{ano}.accdb'
        caminho_metadados: str = f'{CAMINHO_METADADOS}\\{nome_banco}'
        conexao: pyodbc.Connection = abrir_conexao(caminho_metadados, True)
        conexao.autocommit = False
        cursor: pyodbc.Cursor = conexao.cursor()

        blocos_de_dados: list[tuple[str]] = gerar_tuplas_de_insercao(metadados[ano], chaves)
        for bloco in blocos_de_dados:
            cursor.execute(POPULAR_METADADOS.format(*bloco))

        cursor.commit()
        cursor.close()
        conexao.close()


def abrir_conexao(caminho: str, gerar_se_inexistente=False) -> pyodbc.Connection:
    """Abre uma conexão com o banco de dados, criando-o quando necessário."""
    nome_arquivo: str = str(caminho.split('\\')[-1])
    nomes_arquivos: list[str] = os.listdir("\\".join(caminho.split('\\')[:-1]))
    str_conexao: str = STR_CONEXAO_ACCESS.format(caminho)
    if nome_arquivo in nomes_arquivos:
        try:
            return pyodbc.connect(str_conexao)
        except pyodbc.Error:
            raise ErroFalhaConexaoBancoDeDados

    elif gerar_se_inexistente:
        aplicativo_access = Dispatch("Access.Application")
        maquina = aplicativo_access.DBEngine
        area_de_trabalho = maquina.Workspaces(0)
        linguagem_geral_bd: str = ';LANGID=0x0409;CP=1252;COUNTRY=0'
        novo_banco = area_de_trabalho.CreateDatabase(caminho, linguagem_geral_bd, 64)
        novo_banco.Execute(NOVO_METADADOS)
        aplicativo_access.Quit()
        conexao: pyodbc.Connection = pyodbc.connect(str_conexao)
        cursor: pyodbc.Cursor = conexao.cursor()
        try:
            cursor.execute(NOVO_METADADOS)
        except Exception:
            cursor.commit()
            cursor.close()

        return conexao


def coletar_alvos(conexao: pyodbc.Connection) -> list[str]:
    """Coleta os identificadores válidos presentes nos arquivos de alvos."""
    arquivos_na_pasta_alvo: list[str] = os.listdir(CAMINHO_ALVOS)
    if not arquivos_na_pasta_alvo:
        raise ErroPastaDeAlvosVazia

    extensoes_validas: list[str] = ['xls', 'xlsx']
    arquivos_alvo: list[str] = []
    for nome_arquivo in arquivos_na_pasta_alvo:
        if nome_arquivo.split('.')[-1] in extensoes_validas:
            arquivos_alvo.append(nome_arquivo)

    if not arquivos_alvo:
        raise ErroNenhumArquivoValidoEmAlvos

    alvos: list[str] = []
    for nome_arquivo in arquivos_alvo:
        extensao = nome_arquivo.split('.')[-1]
        caminho_ao_arquivo = f'{CAMINHO_ALVOS}/{nome_arquivo}'
        alvos_encontrados: list[str] = []
        if extensao == 'xls':
            alvos_encontrados += extrair_de_xls(caminho_ao_arquivo)
        elif extensao == 'xlsx':
            alvos_encontrados += extrair_de_xlsx(caminho_ao_arquivo)

        for alvo in alvos_encontrados:
            if alvo not in alvos:
                alvos.append(alvo)

    if not alvos:
        raise ErroNenhumAlvoPassado

    if not isinstance(conexao, str):
        alvos = verificar_pendencia(alvos, conexao)

    if not alvos:
        raise AlvosJaConstamNoBancoDeDados

    return alvos


def extrair_de_xlsx(nome_arquivo: str) -> list[str]:
    """Extrai identificadores de páginas de um arquivo '.xlsx'."""
    extrato: list[str] = []
    livro_alvos: openpyxl.Workbook = load_workbook(nome_arquivo)
    folha_alvos = livro_alvos.active
    for row in folha_alvos.iter_rows(1, folha_alvos.max_row):
        for col in range(len(row)):
            conteudo_celula: str = str(row[col].value)
            if e_id_pagina(conteudo_celula):
                extrato.append(conteudo_celula)

    livro_alvos.close()
    return extrato


def extrair_de_xls(nome_arquivo: str) -> list[str]:
    """Extrai identificadores de páginas de um arquivo '.xls'."""
    extrato: list[str] = []
    with open(nome_arquivo, 'r') as dados_arquivo:
        dados_xls: list[str] = ''.join(dados_arquivo.readlines()).replace("</td>", "").split("<td>")
        for dado_xls in dados_xls:
            if e_id_pagina(dado_xls):
                extrato.append(dado_xls)
    return extrato


def e_id_pagina(possivel_id: str) -> bool:
    """Retorna se o texto corresponde a um identificador de página."""
    return bool(re.match('^[0-9]{8}$', possivel_id))


def verificar_pendencia(paginas: list[str], conexao: pyodbc.Connection) -> list[str]:
    """Remove inconsistências e retorna as páginas ainda pendentes."""
    paginas_pendentes: list[str] = []
    paginas_para_excluir_do_banco: list[str] = []
    paginas_para_excluir_do_metadados: dict[str, list[str]] = {}

    arquivos_metadados = os.listdir(CAMINHO_METADADOS)
    for nome_arquivo in arquivos_metadados:
        extensao = nome_arquivo.split('.')[-1]
        if extensao != "accdb":
            arquivos_metadados.remove(nome_arquivo)

    paginas_no_banco = selecionar_ids(conexao, SELECAO_IDS_BANCO_DE_DADOS)
    metadados: dict[str, str] = {}

    if arquivos_metadados:
        for nome_arquivo in arquivos_metadados:
            conexao_metadados = pyodbc.connect(STR_CONEXAO_ACCESS.format(CAMINHO_METADADOS + nome_arquivo))
            paginas_nos_metadados = selecionar_ids(conexao_metadados, SELECAO_IDS_METADADOS)

            for pagina in paginas_nos_metadados:
                metadados[pagina.strip()] = nome_arquivo

            conexao_metadados.close()

    for pagina in paginas:
        pagina_esta_no_banco = pagina in paginas_no_banco
        pagina_esta_nos_metadados = pagina in metadados
        if (not pagina_esta_no_banco) and (not pagina_esta_nos_metadados):
            paginas_pendentes.append(pagina)

        else:
            if pagina_esta_no_banco and (not pagina_esta_nos_metadados):
                paginas_para_excluir_do_banco.append(pagina)

            elif pagina_esta_nos_metadados and (not pagina_esta_no_banco):
                try:
                    paginas_para_excluir_do_metadados[metadados[pagina]].append(pagina)
                except KeyError:
                    paginas_para_excluir_do_metadados[metadados[pagina]] = [pagina]

    excluir_do_banco(paginas_para_excluir_do_banco, conexao)
    excluir_dos_metadados(paginas_para_excluir_do_metadados)

    return paginas_pendentes


def excluir_do_banco(paginas: list[str], conexao: pyodbc.Connection) -> None:
    """Remove as páginas informadas do banco de dados principal."""
    cursor = conexao.cursor()
    for pagina in paginas:
        cursor.execute(EXCLUSAO_DADOS.format(pagina))


def excluir_dos_metadados(metadados: dict[str, list[str]]) -> None:
    """Remove páginas dos respectivos bancos de metadados."""
    for nome_arquivo in metadados:
        conexao_metadados = pyodbc.connect(STR_CONEXAO_ACCESS.format(CAMINHO_METADADOS + nome_arquivo))
        cursor = conexao_metadados.cursor()
        for pagina in metadados[nome_arquivo]:
            cursor.execute(EXCLUSAO_METADADOS.format(pagina))


def transformar_em_url(_id: str) -> str:
    """Gera a URL de acesso para uma página a partir de seu identificador."""
    return URL_DE_DADOS.format(_id)


def digerir_dados(grupo_de_paginas: list[str]) -> tuple[dict, dict]:
    """Extrai dados e metadados de um conjunto de páginas HTML."""
    dicionario_estruturado, metadados_estruturados = {}, {}
    for pagina in grupo_de_paginas:
        pagina = pagina.replace('', '[err_char]')
        dicionario_estruturado = extrair_dados(pagina, dicionario_estruturado)
        pagina_limpa = pagina.replace('\n', '')
        pagina_limpa = pagina_limpa.replace('\r', '')
        pagina_limpa = pagina_limpa.replace(',', '*')
        pagina_limpa = pagina_limpa.replace(';', '*-*')
        sopa = BeautifulSoup(pagina_limpa, 'html.parser')
        sopa_de_dados = sopa.find('table', id='tblPrincipal')
        metadados_estruturados = extrair_metadados(dicionario_estruturado, str(sopa_de_dados), metadados_estruturados)

    return dicionario_estruturado, metadados_estruturados


def extrair_metadados(dados: dict, pagina: str, metadados: dict) -> dict:
    """Adiciona os metadados de uma página à estrutura correspondente."""
    chaves = ['id', 'data_coleta', 'sha', 'texto_html']
    ano = dados['lblDataCriacao'][-1][-4:]
    pagina_limpa = pagina.replace("'", '*a*')
    pagina_limpa = pagina_limpa.replace('"', "*b*")
    valores = [
        dados['id'][-1],
        str(datetime.datetime.today())[:10].replace('.', '/'),
        sha256(str(pagina).encode()).hexdigest(),
        pagina_limpa
    ]
    if ano not in metadados:
        metadados[ano] = {}

    for indice in range(len(chaves)):
        chave = chaves[indice]
        try:
            metadados[ano][chave].append(valores[indice])

        except KeyError:
            metadados[ano][chave] = [valores[indice]]

    return metadados


def extrair_dados(html: str, valores: dict) -> dict:
    """Extrai os dados definidos em ETIQUETAS_HTML de uma página HTML."""
    sopa = BeautifulSoup(html, 'html.parser')
    mapas = gerar_mapas()
    for etiqueta in ETIQUETAS_HTML.keys():
        valor = ''
        try:
            # Os dados desejados podem aparecer em (até o momento)
            # quatro tipos de etiquetas, abaixo se encontram os passos
            # a para extrair estes dados em cada caso
            if ETIQUETAS_HTML[etiqueta] == 'span':
                # Caso mais comum, simplesmente extrair o conteúdo da
                # etiqueta
                span = sopa.find('span', id=etiqueta)
                valor = span.text
            elif ETIQUETAS_HTML[etiqueta] == 'c_input':
                # Caso seja etiqueta 'input'(checkbox) onde o item foi marcado;
                tds = BeautifulSoup(  # Extraindo todos os 'tabledetails'(td) marcados
                    str(sopa.find_all('td')),
                    'html.parser'
                ).find_all('input', checked='checked')
                lbl_id = ''
                for _td in tds:  # Iterando sobre todos os 'tabledetails'.
                    _attrs = BeautifulSoup(str(_td), 'html.parser').find().attrs
                    if _attrs['name'] == etiqueta:
                        lbl_id = _attrs['value']  # Encontrado o id da tag.
                        break
                # Extraindo o dado com atributos
                valor = sopa.find('label', {'for': lbl_id}).text

            elif ETIQUETAS_HTML[etiqueta] == 'input':
                # Caso o dado esteja em caixas de texto preenchíveis.
                _input = sopa.find('input', id=etiqueta).attrs
                valor = str(_input['value'])
            elif ETIQUETAS_HTML[etiqueta] == 'select':
                # Caso o dado esteja em caixas de seleção única.
                select = sopa.find_all('select', id=etiqueta)
                valor = (
                    BeautifulSoup(str(select), 'html.parser')
                    .find('option', selected='selected')
                    .text
                )
            elif "(" in ETIQUETAS_HTML[etiqueta]:
                metodo = ETIQUETAS_HTML[etiqueta].split("(")[0]
                colunas_alvo = ETIQUETAS_HTML[etiqueta].split("(")[1].strip(")").split(",")
                valores_alvo = []
                for coluna in colunas_alvo:
                    if valores[coluna][-1] != "":
                        valores_alvo.append(valores[coluna][-1])
                if len(valores_alvo) != len(colunas_alvo):
                    valores_alvo = "N/A"
                if metodo == "poly":
                    if valores_alvo == "N/A":
                        valor = "," * (len(mapas) - 1)
                    else:
                        coordenadas = Point(valores_alvo)
                        for mapa in mapas:
                            valor = verificar_insercao(valor, coordenadas, mapas[mapa])

                valor = valor.strip(",")

        except AttributeError:
            pass

        try:
            valores[etiqueta].append(valor)
        except KeyError:
            # Gerando nova lista caso não tenha sido gerada ainda.
            valores[etiqueta] = [valor]

    return valores


def gerar_tuplas_de_insercao(dados: dict, estrutura: list) -> list[tuple[str]]:
    """Converte um dicionário de colunas em linhas para inserção no banco."""
    quantidade_registros = len(dados[estrutura[0]])
    linhas: list[tuple[str]] = []
    for indice in range(quantidade_registros):
        linha = []
        for chave in estrutura:
            linha.append(dados[chave][indice])

        linhas.append(tuple(linha))

    return linhas


def verificar_insercao(valor_atual: str, coords: Point, mapa: dict) -> str:
    """Retorna os polígonos do mapa que contêm as coordenadas informadas."""
    novo_valor = ""
    for poligono in mapa:
        if mapa[poligono].contains(coords):
            novo_valor += f'{poligono},'

    if not novo_valor:
        return f'{valor_atual}F.A.A.,'

    return f'{valor_atual}{novo_valor}'


def gerar_mapas() -> dict[str, dict[str, Polygon]]:
    """Carrega os mapas configurados e suas geometrias em memória."""
    mapas: dict[str, dict[str, Polygon]] = {}
    for _mapa in MAPAS:
        with open(MAPAS[_mapa], 'r', encoding='utf-8') as file:
            file_data = ""
            mapa = {}
            for line in file.readlines():
                file_data += line
            features = json.loads(file_data)['features']
            for feature in features:
                geometry = feature['geometry']
                if geometry['type'] == 'Polygon':
                    name = feature['properties']['name']
                    coordinates = geometry['coordinates'][0]
                    trimmed_coordinates = []
                    for coordinate in coordinates:
                        trimmed_coordinates.append(
                            [coordinate[0], coordinate[1]]
                        )
                    mapa[name] = Polygon(array(trimmed_coordinates))

            mapas[_mapa] = mapa
    return mapas


def raspar_conteudo(_id: str, _sessao: requests.Session, _ck: dict[str, str]) -> str:
    """Obtém o conteúdo HTML de uma página."""
    url = transformar_em_url(_id)
    return _sessao.get(url, cookies=_ck).text


def acessar_servico() -> dict[str, str]:
    """Realiza a autenticação e retorna os cookies da sessão."""
    opcoes_chrome = Options()
    if ACESSO_AUTOMATICO:
        opcoes_chrome.add_argument("--headless")
    else:
        opcoes_chrome.add_argument("--window-size=%s" % TAMANHO_DA_TELA)

    opcoes_chrome.binary_location = CAMINHO_CHROME
    driver = webdriver.Chrome(options=opcoes_chrome)
    driver.get(URL_PARA_LOGIN)

    if ACESSO_AUTOMATICO:
        driver.find_element(By.XPATH, '//*[@id="txtLogin"]').send_keys(USUARIO)
        driver.find_element(By.XPATH, '//*[@id="txtSenha"]').send_keys(SENHA)
        driver.find_element(By.XPATH, '//*[@id="btnLogin"]').click()

    cookies: dict[str, str] = {}
    while not cookies:
        try:
            cookies_do_driver = driver.get_cookies()
            if not cookies_do_driver or len(cookies_do_driver) < 10:
                if ACESSO_AUTOMATICO:
                    driver.find_element(By.XPATH, '//*[@id="btnAtualizar"]').click()
            else:
                driver.quit()
                for item in cookies_do_driver:
                    cookies[item['name'].strip()] = item['value'].strip()
        except common.UnexpectedAlertPresentException:
            try:
                if ACESSO_AUTOMATICO:
                    alerta = driver.switch_to.alert
                    alerta.accept()
            finally:
                continue
        except (common.exceptions.NoSuchElementException,
                common.exceptions.StaleElementReferenceException):
            continue

    return cookies
