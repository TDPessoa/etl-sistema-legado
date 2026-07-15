"""
Funções para extração de informações a partir do conteúdo HTML.
"""


import datetime
from hashlib import sha256

from bs4 import BeautifulSoup
from shapely.geometry import Point

from utils.geospatial.maps import (
    gerar_mapas,
    verificar_insercao
)
from utils.config import (
    ETIQUETAS_HTML
)

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
        datetime.datetime.today().strftime("%Y-%m-%d"),
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
                if span:
                    valor = span.text
            elif ETIQUETAS_HTML[etiqueta] == 'c_input':
                # Caso seja etiqueta 'input'(checkbox) onde o item foi marcado;
                tds = BeautifulSoup(  # Extraindo todos os 'tabledetails'(td) marcados
                    str(sopa.find_all('td')),
                    'html.parser'
                ).find_all('input', checked='checked')
                lbl_id = ''
                for _td in tds:  # Iterando sobre todos os 'tabledetails'.
                    detail = BeautifulSoup(str(_td), 'html.parser').find()
                    if detail:
                        _attrs = detail.attrs
                        if _attrs['name'] == etiqueta:
                            lbl_id = _attrs['value']  # Encontrado o id da tag.
                            break
                # Extraindo o dado com atributos
                label = sopa.find('label', {'for': lbl_id})
                if label:
                    valor = label.text

            elif ETIQUETAS_HTML[etiqueta] == 'input':
                # Caso o dado esteja em caixas de texto preenchíveis.
                _input = sopa.find('input', id=etiqueta)
                if _input:
                    _attrs = _input.attrs
                    valor = str(_input['value'])
            elif ETIQUETAS_HTML[etiqueta] == 'select':
                # Caso o dado esteja em caixas de seleção única.
                select = sopa.find_all('select', id=etiqueta)
                option = (BeautifulSoup(str(select), 'html.parser')
                          .find('option', selected='selected'))
                if option:
                    valor = option.text
        
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
