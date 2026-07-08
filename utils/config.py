"""
Leitura e interpretação do arquivo de configuração da aplicação.

Dicionário de caractéres:
    Descrição                                   Combinação
    Retorno (Enter/Carriage Left)               %CRLF%
    Tab Space (ou quatro espaços em branco)     %TBSP%
    Ponto e vírgula (Semi-colon)                %SC%
    Dois pontos (Colon)                         %CL%
    Definição de variável                       %V%[nome_da_variavel]%/V%
"""

import pathlib

_dicionario: dict = {
    'CAMINHO_PRINCIPAL': pathlib.Path().resolve()
}

CAMINHO_PRINCIPAL: str = _dicionario['CAMINHO_PRINCIPAL']

with open(f'{CAMINHO_PRINCIPAL}/config.txt', 'r', encoding='utf-8') as file:
    linhas: list = file.readlines()
    texto: str = ""
    for linha in linhas:
        if linha != '\n':
            texto += linha.replace('\n', '%CRLF%').replace('    ', '%TBSP%').strip()
    lista_texto: list = texto.split(';')
    for constante in lista_texto:
        chave: str = constante.split(':')[0].replace('%CRLF%', '')
        if constante.count(': {') == 0:
            valor: str = ''.join(
                constante.split(':')[1:]).strip().replace(
                '%SC%', ';').replace(
                '%CL%', ':').replace(
                '%CRLF%', '')
            if '%V%' in valor:
                novo_valor: str = ''
                for variavel in valor.split('%/V%'):
                    if '%V%' in variavel:
                        partes: list = variavel.split('%V%')
                        nome_variavel: str = partes[1]
                        if partes[0] != '':
                            novo_valor += str(partes[0])
                        novo_valor += str(_dicionario[nome_variavel])
                    else:
                        novo_valor += variavel
                valor = novo_valor
            _dicionario[chave] = valor
        else:
            valores: str = ':'.join(
                constante.split(':')[1:]).replace(
                '%SC%', ';').replace(
                '{', '').replace(
                '}', '')
            sub_dados: list = valores.split('%CRLF%%TBSP%')
            sub_dicionario: dict = {}
            for dado in sub_dados:
                if len(dado) > 1:
                    sub_chave: str = dado.split(':')[0].strip()
                    sub_valor: str = dado.split(':')[1].split(',')[0].strip()
                    if '(' in sub_valor:
                        sub_valor = ','.join(dado.split(':')[1].split(',')[:-1]).strip()
                    sub_dicionario[sub_chave] = sub_valor.replace('%CRLF%', '')
            _dicionario[chave] = sub_dicionario

LIMITE_DE_TAREFAS: int = int(_dicionario['LIMITE_DE_TAREFAS'])

ACESSO_AUTOMATICO: bool = bool(_dicionario['ACESSO_AUTOMATICO'])

USUARIO: str = _dicionario['USUARIO']
SENHA: str = _dicionario['SENHA']

ARQUIVO_BANCO_DE_DADOS: str = _dicionario['ARQUIVO_BANCO_DE_DADOS']

CAMINHO_CHROME: str = 'utils/chrome/chrome.exe'
TAMANHO_DA_TELA: str = _dicionario['TAMANHO_DA_TELA']

URL_PARA_LOGIN: str = _dicionario['URL_PARA_LOGIN']
URL_DE_DADOS: str = _dicionario['URL_DE_DADOS']

MAPAS: dict = _dicionario['MAPAS']

STR_CONEXAO_ACCESS: str = 'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={};'
CAMINHO_DADOS: str = _dicionario['CAMINHO_DADOS']
CAMINHO_METADADOS: str = _dicionario['CAMINHO_METADADOS']
CAMINHO_ALVOS: str = _dicionario['CAMINHO_ALVOS']
CAMINHO_BANCO_DE_DADOS: str = _dicionario['CAMINHO_BANCO_DE_DADOS']

ETIQUETAS_HTML: dict = _dicionario['ETIQUETAS_HTML']
