"""
Pipeline ETL para coleta e transformação de dados provenientes
de um sistema web legado.
"""

from utils.classes.Interface import InterfaceDeCarregamento

# A splash é inicializada antes dos demais imports para fornecer feedback
# visual imediato durante a carga inicial da aplicação.
inicio = InterfaceDeCarregamento()

# Os imports abaixo são realizados após a exibição da splash para que o
# usuário receba feedback durante a inicialização.
import os
import pyodbc
import requests
import subprocess
import gc
import selenium.common.exceptions
from time import sleep
from utils.funcoes import (
    raspar_conteudo,
    coletar_alvos,
    acessar_servico,
    digerir_dados,
    salvar_dados,
    salvar_metadados
)
from utils.classes.Excecoes import (
    AlvosJaConstamNoBancoDeDados,
    ErroParametrosDeLoginNaoEncontrados,
    ErroCaminhoDoBancoDeDadosAusente,
    ErroArquivoBancoDeDadosNaoEncontrado,
    ErroCaminhoChromeAusente,
    ErroArquivoChromeInexistente,
    ErroFalhaConexaoBancoDeDados,
    ErroNenhumAlvoPassado,
    ErroPastaDeAlvosVazia,
    ErroNenhumArquivoValidoEmAlvos,
    ErroNaoFoiPossivelRealizarOLogin,
    ErroFalhaSQL
)
from utils.classes.Interface import InterfaceDaJanela


inicio.mensagem_config()

# As configurações são carregadas após a etapa de inicialização das dependências.
from utils.config import (
    ACESSO_AUTOMATICO,
    LIMITE_DE_TAREFAS,
    STR_CONEXAO_ACCESS,
    CAMINHO_BANCO_DE_DADOS,
    CAMINHO_DADOS
)


inicio.mensagem_instrucoes()


class Aplicativo:
    def __init__(self):
        self._interface: InterfaceDaJanela = InterfaceDaJanela()
        self._conexao: None | pyodbc.Connection = None
        self._paginas: None | list = None
        self._cookies: None | dict = None
        self._coleta: list = []
        self._sessao: requests.Session = requests.session()
        self._interface.janela.after(100, self._roteiro_principal)
        self._interface.janela.mainloop()

    @property
    def _quantidade_paginas(self) -> int:
        return len(self._paginas)

    @property
    def _alcance_loop(self) -> range:
        return range(self._quantidade_paginas)

    def _execucao(self) -> None:
        self._interface.automatizado(ACESSO_AUTOMATICO)
        self._acessar_banco()
        self._identificar_paginas()
        self._realizar_acesso()
        self._interface.iniciar_coleta(self._quantidade_paginas, LIMITE_DE_TAREFAS)

        for c in self._alcance_loop:
            self._coleta.append(
                raspar_conteudo(self._paginas[c], self._sessao, self._cookies)
            )
            self._interface.atualizar_passo()
            if self._interface.dados_de_execucao.ciclo_foi_concluido:
                self._salvar_coleta()
                if not self._interface.permissao_para_coletar:
                    self._interface.fechar_com_seguranca()
                    break
            gc.collect()

        self._conexao.close()
        self._transformar_dados_no_banco()
        self._sessao.close()
        self._interface.janela.quit()

    def _roteiro_principal(self) -> None:
        try:
            self._execucao()
        # Exceções Boas:
        except AlvosJaConstamNoBancoDeDados:
            self._interface.excecao_bd_atualizado()
        # Exceções Ruins:
        #   Exceções de inicialização
        except (
                ErroParametrosDeLoginNaoEncontrados,
                ErroCaminhoDoBancoDeDadosAusente,
                ErroArquivoBancoDeDadosNaoEncontrado,
                ErroCaminhoChromeAusente,
                ErroArquivoChromeInexistente
        ) as e:
            self._interface.excecao_inicializacao(e.mensagem)

        #   Exceções de Conexao com Banco de dados
        except ErroFalhaConexaoBancoDeDados:
            self._interface.excecao_falha_acesso_db()

        #   Exceções de Identificação de Alvos
        except ErroNenhumAlvoPassado:
            self._interface.excecao_falha_arquivo_alvos()
        except ErroPastaDeAlvosVazia:
            self._interface.excecao_nenhum_arquivo_alvos()
        except ErroNenhumArquivoValidoEmAlvos:
            self._interface.excecao_sem_arquivo_alvo_valido()
        #   Exceções de conexão com o sistema:
        except ErroNaoFoiPossivelRealizarOLogin:
            self._interface.excecao_falha_login()
        except selenium.common.exceptions.UnexpectedAlertPresentException:
            self._interface.excecao_falha_selenium()
        #   Exceções de tratamento de dados
        except ErroFalhaSQL as e:
            self._interface.excecao_integridade(e)
        #   Exceção Coringa
        except Exception as e:
            self._interface.excecao_falha_desconhecida(e)

        finally:
            self._interface.janela.update()

    def _acessar_banco(self) -> None:
        self._interface.iniciar_conexao()

        str_conexao: str = STR_CONEXAO_ACCESS.format(CAMINHO_BANCO_DE_DADOS)
        self._conexao = pyodbc.connect(str_conexao)
        self._conexao.autocommit = False

        self._interface.finalizar_conexao()

    def _identificar_paginas(self) -> None:
        self._interface.iniciar_identificacao()
        self._paginas = coletar_alvos(self._conexao)
        self._interface.finalizar_identificacao(self._quantidade_paginas)

    def _realizar_acesso(self) -> None:
        self._interface.iniciar_login()
        self._cookies = acessar_servico()
        self._interface.finalizar_login()

    def _salvar_coleta(self) -> None:
        self._interface.iniciar_salvamento()
        dados_coletados, metadados_coleta = digerir_dados(self._coleta)
        salvar_dados(self._conexao, dados_coletados)
        salvar_metadados(metadados_coleta)
        self._coleta = []
        self._interface.finalizar_salvamento()

    def _transformar_dados_no_banco(self) -> None:
        self._interface.iniciar_transformacao()

        with open(f'{CAMINHO_DADOS}/permissao.txt', 'w') as _:
            pass
        subprocess.run(f'"{CAMINHO_BANCO_DE_DADOS}"', shell=True)
        conclusao: str = f'{CAMINHO_DADOS}/conclusao.txt'
        while True:
            sleep(3)
            try:
                with open(conclusao, 'r') as _:
                    pass
                os.remove(conclusao)
                break
            except FileNotFoundError:
                continue

        self._interface.finalizar_transformacao()


inicio.fechar()

if __name__ == "__main__":
    app = Aplicativo()
