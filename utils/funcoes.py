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
    """Utiliza de uma conexão com um arquivo `.accdb` para inserir linha a
    linha os dados coletados"""
    chaves: list[str] = list(ETIQUETAS_HTML.keys())
    cursor: pyodbc.Cursor = conexao.cursor()

    blocos_de_dados: list[str] = gerar_tuplas_de_insercao(dados, chaves)
    for bloco in blocos_de_dados:
        cursor.execute(POPULAR_DADOS.format(*bloco))

    cursor.commit()
    cursor.close()


def selecionar_ids(conexao: pyodbc.Connection, declaracao: str) -> list:
    """Utiliza de uma conexão com um arquivo `.accdb` para realizar uma
    consulta passada por parametro, retornando como lista os primeiros itens
    de cada linha"""
    cursor: pyodbc.Cursor = conexao.cursor()
    lista_ids: list[pyodbc.Row] = cursor.execute(declaracao).fetchall()
    lista_final: list[str] = []
    for resultado in lista_ids:
        lista_final.append(str(resultado[0]))
    cursor.close()
    return lista_final


def salvar_metadados(metadados: dict) -> None:
    """Recebe um dicionário com os metadados divididos por ano, se o arquivo
    meta para o ano não existir, irá ser criado um novo, e os dados serão
    salvos no arquivo correspondente"""
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
    """Verifica se o arquivo existe na pasta, retorna uma conexão se o
    arquivo existir ou cria um novo arquivo e retorna a conexão se não
    existir"""
    arquivo: str = str(caminho.split('\\')[-1])
    arquivos: list[str] = os.listdir("\\".join(caminho.split('\\')[:-1]))
    str_conexao: str = STR_CONEXAO_ACCESS.format(caminho)
    if arquivo in arquivos:
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


def coletar_alvos(conexao: pyodbc.Connection) -> list:
    """Identifica todos os arquivos contidos na pasta de alvos, avalia
    se são arquivos válidos, varre todos os arquivos procurando pela
    expressão de um id válido e retorna uma lista de ids alvos
    únicos."""
    arquivos_na_pasta_alvo: list[str] = os.listdir(CAMINHO_ALVOS)
    if len(arquivos_na_pasta_alvo) == 0:
        raise ErroPastaDeAlvosVazia

    extensoes_validas: list[str] = ['xls', 'xlsx']
    arquivos_alvo: list[str] = []
    for arquivo in arquivos_na_pasta_alvo:
        if arquivo.split('.')[-1] in extensoes_validas:
            arquivos_alvo.append(arquivo)

    if len(arquivos_alvo) == 0:
        raise ErroNenhumArquivoValidoEmAlvos

    alvos = []
    for arquivo in arquivos_alvo:
        extensao = arquivo.split('.')[-1]
        caminho_ao_arquivo = f'{CAMINHO_ALVOS}/{arquivo}'
        alvos_encontrados = []
        if extensao == 'xls':
            alvos_encontrados += extrair_de_xls(caminho_ao_arquivo)
        elif extensao == 'xlsx':
            alvos_encontrados += extrair_de_xlsx(caminho_ao_arquivo)

        for alvo in alvos_encontrados:
            if alvo not in alvos:
                alvos.append(alvo)

    if len(alvos) == 0:
        raise ErroNenhumAlvoPassado

    if type(conexao) is not str:
        alvos = verificar_pendencia(alvos, conexao)

    if len(alvos) == 0:
        raise AlvosJaConstamNoBancoDeDados

    return alvos


def extrair_de_xlsx(arquivo: str) -> list[str]:
    """Abre o arquivo com extensão `.xlsx` e retorna os dados encontrados"""
    extrato: list[str] = []
    livro_alvos: openpyxl.Workbook = load_workbook(arquivo)
    folha_alvos = livro_alvos.active
    for row in folha_alvos.iter_rows(1, folha_alvos.max_row):
        for col in range(len(row)):
            conteudo_celula: str = str(row[col].value)
            if e_id_pagina(conteudo_celula):
                extrato.append(conteudo_celula)

    livro_alvos.close()
    return extrato


def extrair_de_xls(arquivo: str) -> list[str]:
    """Abre o arquivo com extensão `.xls` e retorna os dados encontrados"""
    extrato: list[str] = []
    with open(arquivo, 'r') as dados_arquivo:
        dados_xls: list[str] = ''.join(dados_arquivo.readlines()).replace("</td>", "").split("<td>")
        for dado_xls in dados_xls:
            if e_id_pagina(dado_xls):
                extrato.append(dado_xls)
    return extrato


def e_id_pagina(possivel_id: str) -> bool:
    """Retorna se o texto passado segue a expressão regular que define um
    id de página"""
    return bool(re.match('^[0-9]{8}$', possivel_id))


def verificar_pendencia(paginas: list, conexao: pyodbc.Connection) -> list:
    """Compara os identificadores informados com os registros
    existentes no banco principal e nos bancos de metadados.
    Também identifica inconsistências entre ambos os armazenamentos,
    removendo registros órfãos quando necessário.
    Retorna apenas as páginas que ainda precisam ser processadas."""
    paginas_pedentes = []
    paginas_para_excluir_do_banco = []
    paginas_para_excluir_do_metadados = {}

    arquivos_metadados = os.listdir(CAMINHO_METADADOS)  # Identificando os arquivos de metadados
    for arquivo in arquivos_metadados:  # Iterando sobre os nomes e verificando se a extensão é válida
        extensao = arquivo.split('.')[-1]
        if extensao != "accdb":
            arquivos_metadados.remove(arquivo)  # Removendo se a extensão for inválida

    paginas_no_banco = selecionar_ids(conexao, SELECAO_IDS_BANCO_DE_DADOS)
    metadados = {}

    if len(arquivos_metadados) > 0:  # Se ainda existir arquivos
        for arquivo in arquivos_metadados:  # Iterando sobre os arquivos de metadados e gerando conexão
            conexao_metadados = pyodbc.connect(STR_CONEXAO_ACCESS.format(CAMINHO_METADADOS + arquivo))
            paginas_nos_metadados = selecionar_ids(
                conexao_metadados, SELECAO_IDS_METADADOS)  # Consultando os ids do banco de metadados

            for pagina in paginas_nos_metadados:
                metadados[pagina.strip()] = arquivo

            conexao_metadados.close()

    for pagina in paginas:  # Iterando sobre as páginas e removendo os ids que estiverem no
        # banco de metadados
        pagina_esta_no_banco = pagina in paginas_no_banco
        pagina_esta_nos_metadados = pagina in list(metadados.keys())
        if (not pagina_esta_no_banco) and (not pagina_esta_nos_metadados):
            paginas_pedentes.append(pagina)

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

    return paginas_pedentes


def excluir_do_banco(paginas: list, conexao: pyodbc.Connection) -> None:
    cursor = conexao.cursor()
    for pagina in paginas:
        cursor.execute(EXCLUSAO_DADOS.format(pagina))


def excluir_dos_metadados(metadados: dict) -> None:
    for arquivo in metadados:
        conexao_metadados = pyodbc.connect(STR_CONEXAO_ACCESS.format(CAMINHO_METADADOS + arquivo))
        cursor = conexao_metadados.cursor()
        for pagina in metadados[arquivo]:
            cursor.execute(EXCLUSAO_METADADOS.format(pagina))


def transformar_em_url(id: str) -> str:
    """Gera a URL de acesso para uma página a partir de seu identificador."""
    return URL_DE_DADOS.format(id)


def digerir_dados(grupo_de_paginas: list) -> tuple:
    """Percorre a lista contendo códigos html e chama a função
    `extrair_dados` em cada uma para estruturar de forma tabular"""
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
    """"""
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
    if ano not in list(metadados.keys()):
        metadados[ano] = {}

    for c in range(len(chaves)):
        chave = chaves[c]
        try:
            metadados[ano][chave].append(valores[c])

        except KeyError:
            metadados[ano][chave] = [valores[c]]

    return metadados


def extrair_dados(html: str, valores: dict) -> dict:
    """Percorre o dicionário de etiquetas html e extrai, da forma
    específicada, cada informação desejada.
    :param html: Objeto `BeautifulSoup` com o código html extraído da
    página
    :param valores: Dicionário tratado para armazenar os dados
    tabulares"""
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
            # Acrescentando o valor à lista.
            valores[etiqueta].append(valor)
        except KeyError:
            # Gerando nova lista caso não tenha sido gerada ainda.
            valores[etiqueta] = [valor]

    return valores


def gerar_tuplas_de_insercao(dados: dict, estrutura: list) -> list:
    linhas = []
    for c in range(len(dados[estrutura[0]])):
        linha = []
        for chave in estrutura:
            linha.append(dados[chave][c])

        linhas.append(linha)

    return linhas


def verificar_insercao(atual: str, coords: Point, mapa: dict) -> str:
    novo_valor = ""
    for poligono in mapa:
        if mapa[poligono].contains(coords):
            novo_valor += f'{poligono},'

    if novo_valor == "":
        return f'{atual}F.A.A.,'

    return f'{atual}{novo_valor}'


def gerar_mapas() -> dict:
    """Retorna um dicionário aninhado, no formato:
    {
        nome_do_mapa: {
            [
                nome_poligono1: Polygon(coords1),
                nome_poligono2: Polygon(coords2), ...
                ]
            }
        }"""
    mapas = {}
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


def raspar_conteudo(id: str, _sessao: requests.Session, _ck: dict) -> str:
    url = transformar_em_url(id)
    return _sessao.get(url, cookies=_ck).text


def acessar_servico() -> dict:
    """Realiza login no site, se `config.ACESSO_AUTOMATICO` for
    verdadeiro, tenta login com as informações passadas em `USUARIO` e
    `SENHA`, caso contrário, abre uma tela com o site de login."""
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

    cookies = {}
    while len(cookies) == 0:
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
