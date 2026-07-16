"""
Interface gráfica da aplicação.

Este módulo concentra os componentes visuais utilizados durante a
execução do processo, incluindo a janela principal de acompanhamento,
a tela de carregamento inicial e o gerenciamento dos elementos gráficos
responsáveis por exibir o estado da execução.
"""

import tkinter as tk
from typing import Literal
from tkinter import ttk
from PIL import Image, ImageTk
from PIL.ImageFile import ImageFile

from utils.classes.DadosDeExecucao import DadosDeExecucao
from utils.classes.Excecoes import ErroFalhaSQL

Anchor = Literal[
    "nw", "n", "ne",
    "w", "center", "e",
    "sw", "s", "se"
]

class Imagens:
    """Carrega e prepara as imagens utilizadas pela interface gráfica."""
    def __init__(self):
        self.LOGO: ImageTk.PhotoImage = self._condicionar_imagem(
            'utils/imagens/logo.png', 75)
        self.PONTO_VERMELHO: ImageTk.PhotoImage = self._condicionar_imagem(
            'utils/imagens/vermelho.png', 18)
        self.PONTO_VERMELHO_GRANDE: ImageTk.PhotoImage = self._condicionar_imagem(
            'utils/imagens/vermelho.png', 30)
        self.PONTO_VERDE: ImageTk.PhotoImage = self._condicionar_imagem(
            'utils/imagens/verde.png', 18)
        self.PONTO_VERDE_GRANDE: ImageTk.PhotoImage = self._condicionar_imagem(
            'utils/imagens/verde.png', 30)
        self.PONTO_AZUL: ImageTk.PhotoImage = self._condicionar_imagem(
            'utils/imagens/azul.png', 18)
        self.PONTO_AZUL_GRANDE: ImageTk.PhotoImage = self._condicionar_imagem(
            'utils/imagens/azul.png', 30)
        self.PONTO_AMARELO: ImageTk.PhotoImage = self._condicionar_imagem(
            'utils/imagens/amarelo.png', 18)
        self.PONTO_AMARELO_GRANDE: ImageTk.PhotoImage = self._condicionar_imagem(
            'utils/imagens/amarelo.png', 30)

    @staticmethod
    def _condicionar_imagem(caminho: str, tamanho: int) -> ImageTk.PhotoImage:
        """Carrega, redimensiona e converte uma imagem para uso na interface."""
        imagem: ImageFile = Image.open(caminho)
        pixels_x, pixels_y = tuple([int(tamanho / imagem.size[0] * x) for x in imagem.size])
        return ImageTk.PhotoImage(imagem.resize((pixels_x, pixels_y)))


class InterfaceDaJanela:
    """
    Cria e controla a janela principal responsável por acompanhar
    a execução do pipeline ETL.
    """
    def __init__(self):
        self._configurar_janela()
        self._IMAGENS: Imagens = Imagens()
        self._pontos_de_status: dict = {
            0: ttk.Label(self.janela, image=self._IMAGENS.PONTO_AMARELO),  # Conexão com DB
            1: ttk.Label(self.janela, image=self._IMAGENS.PONTO_AMARELO),  # Identificando Alvos
            2: ttk.Label(self.janela, image=self._IMAGENS.PONTO_AMARELO),  # Automatização Login/Senha
            3: ttk.Label(self.janela, image=self._IMAGENS.PONTO_AMARELO),  # Acesso ao site
            4: ttk.Label(self.janela, image=self._IMAGENS.PONTO_AMARELO),  # Coleta de Dados
            5: ttk.Label(self.janela, image=self._IMAGENS.PONTO_AMARELO),  # Salvamento dos dados
            6: ttk.Label(self.janela, image=self._IMAGENS.PONTO_AMARELO),  # Transformação dos dados
            7: ttk.Label(self.janela, image=self._IMAGENS.PONTO_AMARELO),  # Conclusão dos trabalhos
            9: ttk.Label(self.janela, image=self._IMAGENS.PONTO_AMARELO_GRANDE)
        }
        self._textos_variaveis: dict = {
            0: tk.StringVar(self.janela, value='TEMPO RESTANTE: --:--:--'),
            1: tk.StringVar(self.janela, value='TEMPO RESTANTE: --:--:--'),
            2: tk.StringVar(self.janela, value='-----'),
            3: tk.StringVar(self.janela, value='-----'),
            4: tk.StringVar(self.janela, value='-----'),
            5: tk.StringVar(self.janela, value='-----'),
            6: tk.StringVar(self.janela, value='--/--/---- --:--:--'),
            7: tk.StringVar(self.janela, value='--:--:--'),
            8: tk.StringVar(self.janela, value='--/--/---- --:--:--'),
            9: tk.StringVar(self.janela, value='--:--:--'),
            10: tk.StringVar(self.janela, value='--:--:--'),
            11: tk.StringVar(self.janela)
        }
        self._barras_de_progresso: dict = {
            0: ttk.Progressbar(self.janela, value=0, length=100, mode='determinate'),
            1: ttk.Progressbar(self.janela, value=0, length=100, mode='determinate')
        }
        self._mensagem_de_erro: ttk.Label = self._gerar_etiqueta(
            cor_texto="Red", variavel_de_texto=self._textos_variaveis[11])
        self._botao_parar: tk.Button = tk.Button(
            self.janela, text='PARAR COLETA', font=('Agenda', 16, 'bold'),
            command=self._alterar_permissao)
        self._inicializar_cabecalho()
        self._inicializar_painel_de_status()
        self._inicializar_painel_de_execucao()
        self.dados_de_execucao: DadosDeExecucao
        self.permissao_para_coletar: bool = True

    def automatizado(self, permissao: bool) -> None:
        """Atualiza a interface para indicar se o acesso será automático ou manual."""
        if permissao:
            self._pontos_de_status[2].configure(image=self._IMAGENS.PONTO_VERDE)
        else:
            self._pontos_de_status[2].configure(image=self._IMAGENS.PONTO_VERMELHO)

    def iniciar_conexao(self) -> None:
        """Atualiza a interface para indicar o início da conexão com o banco."""
        self._pontos_de_status[0].configure(image=self._IMAGENS.PONTO_AZUL)
        self.janela.update()

    def finalizar_conexao(self) -> None:
        """Atualiza a interface para indicar sucesso na conexão com o banco."""
        self._pontos_de_status[0].configure(image=self._IMAGENS.PONTO_VERDE)
        self.janela.update()

    def iniciar_identificacao(self) -> None:
        """Atualiza a interface para indicar o início da obtenção de alvos."""
        self._pontos_de_status[1].configure(image=self._IMAGENS.PONTO_AZUL)
        self.janela.update()

    def finalizar_identificacao(self, total_paginas: int) -> None:
        """Atualiza a interface para indicar o sucesso na obtenção de alvos."""
        self._textos_variaveis[2].set(value=f'{total_paginas:05}')
        self._pontos_de_status[1].configure(image=self._IMAGENS.PONTO_VERDE)
        self.janela.update()

    def iniciar_login(self) -> None:
        """Atualiza a interface para indicar o início das tentativas de autenticação."""
        self._pontos_de_status[3].configure(image=self._IMAGENS.PONTO_AZUL)
        self._textos_variaveis[11].set(
            "Esta etapa irá demorar para ser concluída se esta for a primeira execução desde a "
            "reinicialização.")
        self._mensagem_de_erro.configure(foreground="Green")
        self.janela.update()

    def finalizar_login(self) -> None:
        """Atualiza a interface para indicar o sucesso na autenticação."""
        self._pontos_de_status[3].configure(image=self._IMAGENS.PONTO_VERDE)
        self._textos_variaveis[11].set("")
        self._mensagem_de_erro.configure(foreground="Red")
        self.janela.update()

    def iniciar_coleta(self, quantidade: int, limite: int) -> None:
        """Prepara variáveis e atualiza a interface para indicar o início da coleta de dados."""
        self.dados_de_execucao = DadosDeExecucao(quantidade, limite)
        self._textos_variaveis[3].set(value=self.dados_de_execucao.str_paginas_coletadas)
        self._textos_variaveis[4].set(value=self.dados_de_execucao.str_paginas_salvas)
        self._textos_variaveis[5].set(value=self.dados_de_execucao.str_paginas_ciclo)
        self._textos_variaveis[6].set(value=self.dados_de_execucao.str_hora_anterior)
        self._pontos_de_status[4].configure(image=self._IMAGENS.PONTO_AZUL)
        self.janela.update()

    def iniciar_salvamento(self) -> None:
        """Atualiza a interface para indicar o processo de persistência de dados."""
        self._pontos_de_status[4].configure(image=self._IMAGENS.PONTO_VERDE)
        self._pontos_de_status[5].configure(image=self._IMAGENS.PONTO_AZUL)
        self._pontos_de_status[9].configure(image=self._IMAGENS.PONTO_VERMELHO_GRANDE)
        self.janela.update()

    def finalizar_salvamento(self) -> None:
        """
        Atualiza as informações de execução e prepara a interface para o
        próximo ciclo de coleta.
        """
        self.dados_de_execucao.encerrar_ciclo()
        self._textos_variaveis[4].set(value=self.dados_de_execucao.str_paginas_salvas)
        self._pontos_de_status[5].configure(image=self._IMAGENS.PONTO_VERDE)
        self._pontos_de_status[4].configure(image=self._IMAGENS.PONTO_AZUL)
        self._pontos_de_status[9].configure(image=self._IMAGENS.PONTO_VERDE_GRANDE)
        self._barras_de_progresso[0].step(self.dados_de_execucao.progresso_geral)
        self._barras_de_progresso[1].configure(value=0)
        self.janela.update()

    def iniciar_transformacao(self) -> None:
        """Atualiza a interface para indicar o início da transformação de dados."""
        self._pontos_de_status[4].configure(image=self._IMAGENS.PONTO_VERDE)
        self._pontos_de_status[5].configure(image=self._IMAGENS.PONTO_VERDE)
        self._pontos_de_status[6].configure(image=self._IMAGENS.PONTO_AZUL)
        self._pontos_de_status[9].configure(image=self._IMAGENS.PONTO_VERMELHO_GRANDE)
        self.janela.update()

    def finalizar_transformacao(self) -> None:
        """Atualiza a interface para indicar o sucesso da transformação de dados."""
        self._pontos_de_status[6].configure(image=self._IMAGENS.PONTO_VERDE)
        self._pontos_de_status[7].configure(image=self._IMAGENS.PONTO_VERDE)
        self._pontos_de_status[9].configure(image=self._IMAGENS.PONTO_VERDE_GRANDE)
        self.janela.update()

    def atualizar_passo(self) -> None:
        """Atualiza os indicadores de execução exibidos na interface."""
        self.dados_de_execucao.encerrar_coleta()
        self._textos_variaveis[0].set(
            value=self.dados_de_execucao.str_tempo_para_conclusao_geral)
        self._textos_variaveis[1].set(
            value=self.dados_de_execucao.str_tempo_para_conclusao_ciclo)
        self._textos_variaveis[3].set(
            value=self.dados_de_execucao.str_paginas_coletadas)
        self._textos_variaveis[7].set(
            value=self.dados_de_execucao.tempo_em_execucao)
        self._textos_variaveis[8].set(
            value=self.dados_de_execucao.str_hora_final)
        self._textos_variaveis[9].set(
            value=self.dados_de_execucao.str_tempo_medio_por_pagina)
        self._textos_variaveis[10].set(
            value=self.dados_de_execucao.str_tempo_medio_por_ciclo)
        self._barras_de_progresso[1].step(
            self.dados_de_execucao.progresso_ciclo)
        self.janela.update()

    def fechar_com_seguranca(self) -> None:
        """Informa ao usuário que a aplicação pode ser encerrada com segurança."""
        self._textos_variaveis[11].set("A tela pode ser fechada com segurança.")
        self._mensagem_de_erro.configure(foreground="Green")
        self.janela.update()

    def _alterar_permissao(self) -> None:
        """Solicita o encerramento da coleta após o ciclo atual."""
        self.permissao_para_coletar = False
        self._textos_variaveis[11].set(
            "Após o final deste ciclo, o script irá encerrar a coleta de dados.")
        self._mensagem_de_erro.configure(foreground="Blue")
        self._botao_parar.configure(state='disabled')
        self.janela.update()

    def _gerar_etiqueta(
            self, texto="", ancora: Anchor = "w", fonte=('Agenda', 10, 'bold'), cor_texto="Black",
            variavel_de_texto=None, esp_borda=None, borda=None) -> ttk.Label:
        """Cria e retorna uma etiqueta configurada para a interface."""
        etiqueta = ttk.Label(
            self.janela, text=texto, anchor=ancora, font=fonte, foreground=cor_texto,
            textvariable=variavel_de_texto, borderwidth=esp_borda, relief=borda)
        return etiqueta

    def _inicializar_cabecalho(self) -> None:
        """Inicializa os componentes visuais do cabeçalho da janela."""
        ttk.Label(self.janela, image=self._IMAGENS.LOGO).grid(
            column=1, row=1, columnspan=4, rowspan=4)
        ttk.Label(self.janela, text='ETL - SISTEMA LEGADO', anchor="center",
                  font=('Agenda', 40, 'bold')).grid(
            column=6, row=1, columnspan=33, rowspan=4)

    def _inicializar_painel_de_status(self) -> None:
        """Inicializa o painel que exibe o status das etapas da execução."""
        self._pontos_de_status[0].grid(
            column=2, row=6, sticky='nwes')
        self._pontos_de_status[1].grid(
            column=2, row=8, sticky='nwes')
        self._pontos_de_status[2].grid(
            column=2, row=10, sticky='nwes')
        self._pontos_de_status[3].grid(
            column=2, row=12, sticky='nwes')
        self._pontos_de_status[4].grid(
            column=2, row=14, sticky='nwes')
        self._pontos_de_status[5].grid(
            column=2, row=16, sticky='nwes')
        self._pontos_de_status[6].grid(
            column=2, row=18, sticky='nwes')
        self._pontos_de_status[7].grid(
            column=2, row=20, sticky='nwes')
        self._pontos_de_status[9].grid(
            column=16, row=22, columnspan=2, rowspan=2, sticky='nwes')

        self._gerar_etiqueta(texto='ACESSO AO BANCO DE DADOS').grid(
            column=4, row=6, columnspan=10, sticky='nwes')
        self._gerar_etiqueta(texto='PÁGINAS IDENTIFICADAS').grid(
            column=4, row=8, columnspan=10, sticky='nwes')
        self._gerar_etiqueta(texto='ACESSO AUTOMATIZADO').grid(
            column=4, row=10, columnspan=10, sticky='nwes')
        self._gerar_etiqueta(texto='ACESSO ADQUIRIDO').grid(
            column=4, row=12, columnspan=10, sticky='nwes')
        self._gerar_etiqueta(texto='COLETA DE DADOS').grid(
            column=4, row=14, columnspan=10, sticky='nwes')
        self._gerar_etiqueta(texto='SALVANDO DADOS').grid(
            column=4, row=16, columnspan=10, sticky='nwes')
        self._gerar_etiqueta(texto='TRANSFORMAÇÃO DOS DADOS').grid(
            column=4, row=18, columnspan=10, sticky='nwes')
        self._gerar_etiqueta(texto='CONCLUSÃO').grid(
            column=4, row=20, columnspan=10, sticky='nwes')
        self._gerar_etiqueta(texto='PERMITIDO', fonte=('Agenda', 12, 'bold')).grid(
            column=19, row=22, columnspan=8, sticky='nwes')
        self._gerar_etiqueta(texto='FECHAR', fonte=('Agenda', 12, 'bold')).grid(
            column=19, row=23, columnspan=8, sticky='nwes')
        self._mensagem_de_erro.grid(
            column=2, row=24, columnspan=38, sticky='nwes')

    def _inicializar_painel_de_execucao(self) -> None:
        """Inicializa o painel com indicadores e controles da execução."""
        self._gerar_etiqueta(texto='PROGRESSO GERAL').grid(
            column=16, row=6, columnspan=11, sticky='nwes')
        self._gerar_etiqueta(variavel_de_texto=self._textos_variaveis[0], ancora='se',
                             fonte=('Agenda', 8, 'bold')).grid(
            column=28, row=6, columnspan=11, sticky='nwes')
        self._gerar_etiqueta(texto='PROGRESSO DO CICLO').grid(
            column=16, row=8, columnspan=11, sticky='nwes')
        self._gerar_etiqueta(variavel_de_texto=self._textos_variaveis[1], ancora='se',
                             fonte=('Agenda', 8, 'bold')).grid(
            column=28, row=8, columnspan=11, sticky='nwes')
        self._gerar_etiqueta(texto='RELATÓRIO DE EXECUÇÃO').grid(
            column=16, row=11, sticky='w')
        self._gerar_etiqueta(esp_borda=2, borda="solid").grid(
            column=16, row=11, columnspan=23, rowspan=10, sticky='nsew'),
        self._gerar_etiqueta(texto='RELATÓRIO DE EXECUÇÃO').grid(
            column=16, row=11, columnspan=23, sticky='nsew', padx=2, pady=2)
        self._gerar_etiqueta(texto='PÁGINAS TOTAIS:').grid(
            column=16, row=12, columnspan=12, sticky='e', padx=1, pady=1),
        self._gerar_etiqueta(variavel_de_texto=self._textos_variaveis[2]).grid(
            column=29, row=12, columnspan=10, sticky='w', padx=1, pady=1)
        self._gerar_etiqueta(texto='PÁGINAS COLETADAS:').grid(
            column=16, row=13, columnspan=12, sticky='e', padx=1, pady=1),
        self._gerar_etiqueta(variavel_de_texto=self._textos_variaveis[3]).grid(
            column=29, row=13, columnspan=10, sticky='w', padx=1, pady=1)
        self._gerar_etiqueta(texto='PÁGINAS SALVAS:').grid(
            column=16, row=14, columnspan=12, sticky='e', padx=1, pady=1),
        self._gerar_etiqueta(variavel_de_texto=self._textos_variaveis[4]).grid(
            column=29, row=14, columnspan=10, sticky='w', padx=1, pady=1)
        self._gerar_etiqueta(texto='PÁGINAS POR CICLO:').grid(
            column=16, row=15, columnspan=12, sticky='e', padx=1, pady=1),
        self._gerar_etiqueta(variavel_de_texto=self._textos_variaveis[5]).grid(
            column=29, row=15, columnspan=10, sticky='w', padx=1, pady=1)
        self._gerar_etiqueta(texto='HORA INICIAL:').grid(
            column=16, row=16, columnspan=12, sticky='e', padx=1, pady=1),
        self._gerar_etiqueta(variavel_de_texto=self._textos_variaveis[6]).grid(
            column=29, row=16, columnspan=10, sticky='w', padx=1, pady=1)
        self._gerar_etiqueta(texto='TEMPO EM EXECUÇÃO:').grid(
            column=16, row=17, columnspan=12, sticky='e', padx=1, pady=1),
        self._gerar_etiqueta(variavel_de_texto=self._textos_variaveis[7]).grid(
            column=29, row=17, columnspan=10, sticky='w', padx=1, pady=1)
        self._gerar_etiqueta(texto='HORA FINAL (ESTIMADA):').grid(
            column=16, row=18, columnspan=12, sticky='e', padx=1, pady=1),
        self._gerar_etiqueta(variavel_de_texto=self._textos_variaveis[8]).grid(
            column=29, row=18, columnspan=10, sticky='w', padx=1, pady=1)
        self._gerar_etiqueta(texto='TEMPO MÉDIO POR PÁGINA:').grid(
            column=16, row=19, columnspan=12, sticky='e', padx=1, pady=1),
        self._gerar_etiqueta(variavel_de_texto=self._textos_variaveis[9]).grid(
            column=29, row=19, columnspan=10, sticky='w', padx=1, pady=1)
        self._gerar_etiqueta(texto='TEMPO MÉDIO POR CICLO:').grid(
            column=16, row=20, columnspan=12, sticky='e', padx=2, pady=2),
        self._gerar_etiqueta(variavel_de_texto=self._textos_variaveis[10]).grid(
            column=29, row=20, columnspan=10, sticky='w', padx=1, pady=1)
        self._botao_parar.grid(
            column=28, row=22, columnspan=11, rowspan=2, sticky='nswe')
        self._barras_de_progresso[0].grid(
            column=16, row=7, columnspan=23, sticky='nwes')
        self._barras_de_progresso[1].grid(
            column=16, row=9, columnspan=23, sticky='nwes')

    def _configurar_janela(self) -> None:
        """Configura as propriedades da janela principal."""
        self.janela: tk.Tk = tk.Tk()
        self.janela.title("Coleta de Páginas")
        self.janela.iconbitmap('utils/imagens/logo.ico')
        self.janela.geometry('800x500')
        self.janela.columnconfigure(tuple(range(0, 40)), weight=1, uniform='a')
        self.janela.rowconfigure(tuple(range(0, 25)), weight=1, uniform='a')

    # Exceções de execução
    def excecao_bd_atualizado(self) -> None:
        """Atualiza a interface quando o banco já está sincronizado."""
        self._pontos_de_status[1].configure(image=self._IMAGENS.PONTO_VERDE)
        self._pontos_de_status[4].configure(image=self._IMAGENS.PONTO_VERDE)
        self._pontos_de_status[5].configure(image=self._IMAGENS.PONTO_VERDE)
        self._pontos_de_status[7].configure(image=self._IMAGENS.PONTO_VERDE)
        self._pontos_de_status[9].configure(image=self._IMAGENS.PONTO_VERDE_GRANDE)
        self._textos_variaveis[11].set(
            "O banco de dados está atualizado com os alvos passados."
        )

    def excecao_falha_acesso_db(self) -> None:
        """Atualiza a interface para indicar falha na conexão com o banco de dados."""
        self._pontos_de_status[0].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._textos_variaveis[11].set(
            "Erro: Falha no acesso ao banco de dados."
        )

    def excecao_falha_arquivo_db(self, excecao) -> None:
        """Atualiza a interface para indicar que o arquivo do banco de dados não foi encontrado."""
        self._pontos_de_status[0].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._textos_variaveis[11].set(
            f"Erro: Falha ao encontrar o arquivo de banco de dados: {excecao.nome_arquivo}"
        )

    def excecao_falha_arquivo_alvos(self) -> None:
        """Atualiza a interface para indicar que não foi possível localizar os alvos."""
        self._pontos_de_status[1].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._textos_variaveis[11].set(
            "Erro: Nenhum alvo encontrado na pasta de alvos."
        )

    def excecao_nenhum_arquivo_alvos(self) -> None:
        """Atualiza a interface para indicar que nenhum arquivo de alvos foi encontrado."""
        self._pontos_de_status[1].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._textos_variaveis[11].set(
            "Erro: Nenhum arquivo encontrado na pasta de alvos."
        )

    def excecao_sem_arquivo_alvo_valido(self) -> None:
        """Atualiza a interface para indicar que não há arquivos de alvos válidos."""
        self._pontos_de_status[1].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._textos_variaveis[11].set(
            "Erro: Nenhum arquivo válido encontrado na pasta de alvos."
        )

    def excecao_falha_login(self) -> None:
        """Atualiza a interface para indicar falha durante a autenticação."""
        self._pontos_de_status[3].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._textos_variaveis[11].set(
            "Erro: Houve um erro no login, tente acessar o sistema via browser e realize logout antes "
            "de tentar novamente."
        )

    def excecao_falha_selenium(self) -> None:
        """Atualiza a interface para indicar falha na sessão automatizada."""
        self._pontos_de_status[3].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._textos_variaveis[11].set(
            "Erro: A conta já tinha sido acessada no sistema, faça login via browser e realize logout"
            " antes de tentar novamente."
        )

    def excecao_integridade(self, excecao: ErroFalhaSQL) -> None:
        """Atualiza a interface para indicar uma falha de integridade dos dados."""
        self._pontos_de_status[6].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._textos_variaveis[11].set(
            f"Erro: Falha de integridade de dados na query: {excecao.declaracao}."
        )

    def excecao_falha_desconhecida(self, excecao: Exception) -> None:
        """Atualiza a interface para indicar uma falha inesperada."""
        self._pontos_de_status[0].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._pontos_de_status[1].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._pontos_de_status[2].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._pontos_de_status[3].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._pontos_de_status[4].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._pontos_de_status[5].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._pontos_de_status[9].configure(image=self._IMAGENS.PONTO_VERDE_GRANDE)
        self._pontos_de_status[6].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._pontos_de_status[7].configure(image=self._IMAGENS.PONTO_VERMELHO)
        self._textos_variaveis[11].set(
            f'Erro Inesperado: "{str(excecao)}".'
        )

    def excecao_inicializacao(self, mensagem) -> None:
        self.excecao_falha_desconhecida(mensagem)


class InterfaceDeCarregamento:
    """
    Exibe uma tela de inicialização enquanto os componentes da
    aplicação são carregados.
    """
    def __init__(self):
        self._janela: tk.Tk = tk.Tk()
        self._janela.geometry("400x100")
        self._janela.overrideredirect(True)
        self._janela.columnconfigure(tuple(range(0, 1)), weight=1, uniform='a')
        self._janela.rowconfigure(tuple(range(0, 2)), weight=1, uniform='a')
        ttk.Label(self._janela, text='ETL - SISTEMA LEGADO', anchor="center", font=('Agenda', 25, 'bold')).grid(
            column=1, row=1)
        self._mensagem: ttk.Label = ttk.Label(
            self._janela, text="Preparando aplicação...", anchor="center", font=("Agenda", 11, 'bold')
        )
        self._mensagem.grid(column=1, row=2)
        self._janela.eval('tk::PlaceWindow . center')
        self._janela.update()

    def mensagem_imports(self):
        """Atualiza a mensagem indicando o carregamento das bibliotecas."""
        self._mensagem['text'] = "Carregando bibliotecas..."
        self._janela.update()

    def mensagem_config(self):
        """Atualiza a mensagem indicando o carregamento das configurações."""
        self._mensagem['text'] = "Carregando configurações (config.txt)..."
        self._janela.update()

    def mensagem_instrucoes(self):
        """Atualiza a mensagem indicando o carregamento do roteiro da aplicação."""
        self._mensagem['text'] = "Inicializando aplicação..."
        self._janela.update()

    def fechar(self):
        self._janela.destroy()
