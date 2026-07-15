"""
Funções para acesso e manipulação do banco de dados.
"""


import os

import pyodbc
from win32com.client import Dispatch

from utils.transformation.data_manipulation import (
    gerar_tuplas_de_insercao,
)
from utils.config import (
    ETIQUETAS_HTML,
    STR_CONEXAO_ACCESS,
    CAMINHO_METADADOS
)
from utils.instrucoes_sql import (
    POPULAR_DADOS,
    POPULAR_METADADOS,
    NOVO_METADADOS,
    EXCLUSAO_METADADOS,
    EXCLUSAO_DADOS
)
from utils.classes.Excecoes import ErroFalhaConexaoBancoDeDados


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
            # A tabela já foi criada pela automação do Access. A segunda execução
            # pode falhar dependendo da versão do Access utilizada.
            cursor.commit()
            cursor.close()

        return conexao


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
