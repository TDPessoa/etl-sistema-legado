"""Exceções para conter os possíveis erros de execução no painel da UI
Autor: TDPessoa
Email: thiago.d.pessoa@gmail.com
Status: Pronto
"""


class ErroFalhaConexaoBancoDeDados(Exception):
    """Falha ao acessar - com pyocdb - o banco
    de dados da coleta"""
    pass


class ErroFalhaSQL(Exception):
    """Falha ao executar uma declaração SQL"""
    def __init__(self, declaracao):
        self.declaracao = declaracao
    pass


class ErroNaoFoiPossivelRealizarOLogin(Exception):
    """Falha ao realizar login"""
    pass


class ErroPastaDeAlvosVazia(Exception):
    """Falha ao determinar se existem arquivos na pasta `dados/alvos`"""
    pass


class ErroNenhumAlvoPassado(Exception):
    """Falha ao determinar se existem ocorrências nos arquivos da pasta
    `dados/alvos`"""
    pass


class ErroNenhumArquivoValidoEmAlvos(Exception):
    """Falha ao determinar se existem arquivos válidos na pasta
    `dados/alvos`"""
    pass


class AlvosJaConstamNoBancoDeDados(Exception):
    """Falha ao determinar se existem novas ocorrências nos arquivos da
    pasta `dados/alvos"""
    pass


class ErroArquivoBancoDeDadosNaoEncontrado(Exception):
    """Falha ao localizar o arquivo de banco de dados"""
    def __init__(self):
        self.mensagem = ("Não foi encontrado o arquivo de banco de dados, favor consultar "
                         "o manual.")
    pass


class ErroParametrosDeLoginNaoEncontrados(Exception):
    """Falha ao determinar os dados de login quando o login deve ser
    automatizado"""
    def __init__(self):
        self.mensagem = ("O acesso automatizado está como verdadeiro, mas as "
                         "credenciais não foram fornecidas.")
    pass


class ErroCaminhoDoBancoDeDadosAusente(Exception):
    """Falha ao determinar se foi passado um caminho para o banco de
    dados"""
    def __init__(self):
        self.mensagem = ("Não foi fornecido um caminho para o banco de dados, favor "
                         "consultar o manual.")
    pass


class ErroCaminhoChromeAusente(Exception):
    """Falha ao determinar se foi passado um caminho para o arquivo
    binário do navegador Chrome"""
    def __init__(self):
        self.mensagem = ("Não foi fornecido um caminho para o chrome, favor consultar "
                         "o manual.")
    pass


class ErroArquivoChromeInexistente(Exception):
    """Falha ao localizar o arquivo binário do navegador Chrome"""
    def __init__(self):
        self.mensagem = "Não foi encontrado um arquivo chrome, favor consultar o manual."
    pass
