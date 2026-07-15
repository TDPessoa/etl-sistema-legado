"""
Funções para transformação e preparação de dados.
"""


from utils.config import URL_DE_DADOS


def transformar_em_url(_id: str) -> str:
    """Gera a URL de acesso para uma página a partir de seu identificador."""
    return URL_DE_DADOS.format(_id)


def gerar_tuplas_de_insercao(dados: dict, estrutura: list[str]) -> list[tuple]:
    """Converte um dicionário de colunas em linhas para inserção no banco."""
    quantidade_registros = len(dados[estrutura[0]])
    linhas: list[tuple] = []
    for indice in range(quantidade_registros):
        linha = []
        for chave in estrutura:
            linha.append(dados[chave][indice])

        linhas.append(tuple(linha))

    return linhas
