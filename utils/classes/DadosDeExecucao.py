"""
Controle de métricas temporais e progresso da execução.
"""


from datetime import timedelta
from time import (
    time,
    strftime,
    localtime
)


class DadosDeExecucao:
    """Gera, calcula, guarda e formata dados temporais e de progresso."""
    def __init__(self, total_de_paginas: int, limite: int) -> None:
        self._hora_anterior: float = time()  # Sempre em UTC
        self._tempos_paginas: list[float] = []  # Todas as fatias de tempo
        self._tempos_ciclos: list[float] = []
        self.paginas_coletadas: int = 0
        self.paginas_salvas: int = 0
        self.paginas_ciclo: int = limite
        self.paginas_totais: int = total_de_paginas

    def encerrar_ciclo(self) -> None:
        """Atualiza os dados relativos à execução geral."""
        self.paginas_salvas += self.paginas_ciclo
        if self.paginas_salvas > self.paginas_totais:
            self.paginas_salvas = self.paginas_totais
        fatia_ultimo_ciclo: int = -1 * self.paginas_ciclo
        tempo_ultimo_ciclo: float = sum(self._tempos_ciclos[fatia_ultimo_ciclo:])
        self._tempos_ciclos.append(tempo_ultimo_ciclo)

    def encerrar_coleta(self) -> None:
        """Atualiza os dados relativos à execução unitária."""
        hora_atual: float = time()
        tempo_passado: float = hora_atual - self._hora_anterior
        self._tempos_paginas.append(tempo_passado)
        self._hora_anterior = hora_atual
        self.paginas_coletadas += 1

    @property
    def progresso_geral(self) -> float:
        """
        Retorna o percentual de quantas páginas foram feitas no
        total.
        """
        return (self.paginas_ciclo / self.paginas_totais) * 100

    @property
    def progresso_ciclo(self) -> float:
        """Retorna o percentual de quantas páginas foram feitas no ciclo."""
        return (1 / self.paginas_ciclo) * 100

    @property
    def str_tempo_medio_por_ciclo(self) -> str:
        """
        Retorna o texto formatado do tempo médio para conclusão de um
        ciclo.
        """
        return str(timedelta(seconds=(self._tempo_medio_por_pagina * self.paginas_ciclo)))

    @property
    def str_tempo_medio_por_pagina(self) -> str:
        """
        Retorna o texto formatado do tempo médio para conclusão de uma
        página.
        """
        return str(timedelta(seconds=self._tempo_medio_por_pagina))

    @property
    def str_hora_final(self) -> str:
        """Retorna o texto formatado da hora final estimada."""
        return strftime("%d/%m/%Y %H:%M:%S", localtime(self._hora_final))

    @property
    def str_tempo_para_conclusao_ciclo(self) -> str:
        """
        Retorna o texto formatado do tempo estimado necessário para
        conclusão do ciclo.
        """
        return f'TEMPO RESTANTE: {timedelta(seconds=self._tempo_para_conclusao_ciclo)}'

    @property
    def str_tempo_para_conclusao_geral(self) -> str:
        """
        Retorna o texto formatado do tempo estimado necessário para
        conclusão do funcionamento.
        """
        return f'TEMPO RESTANTE: {timedelta(seconds=self._tempo_para_conclusao_geral)}'

    @property
    def str_paginas_coletadas(self) -> str:
        """Retorna o texto formatado da quantidade de páginas já coletadas."""
        return f'{self.paginas_coletadas:05}'

    @property
    def str_paginas_salvas(self) -> str:
        """
        Retorna o texto formatado da quantidade de páginas já salvas
        com a porcentágem do total.
        """
        porcento: float = (100*(self.paginas_salvas/self.paginas_totais))
        porcento_inteiro: int = int(porcento // 1)
        porcento_fracao: str = f'{porcento - porcento_inteiro}'[2]
        return f'{self.paginas_salvas:05} ({porcento_inteiro:03}.{porcento_fracao}%)'

    @property
    def str_paginas_ciclo(self) -> str:
        """Retorna o texto formatado da quantidade de páginas por ciclo."""
        return f'{self.paginas_ciclo:05}'

    @property
    def str_paginas_totais(self) -> str:
        """Retorna o texto formatado da quantidade de páginas totais."""
        return f'{self.paginas_totais:05}'

    @property
    def str_hora_anterior(self) -> str:
        """
        Retorna o texto formatado da hora anterior guardada (utilizada para
        definir a hora inicial).
        """
        return strftime("%d/%m/%Y %H:%M:%S", localtime(self._hora_anterior))

    @property
    def tempo_em_execucao(self) -> str:
        """Retorna o texto formatado do tempo passado desde o início."""
        return str(timedelta(seconds=self._segundos_desde_o_inicio))

    @property
    def ciclo_foi_concluido(self) -> bool:
        """Retorna o boolean para término do ciclo atual."""
        return (
            (
                (self.paginas_coletadas % self.paginas_ciclo) == 0
                and self.paginas_coletadas != 0
            )
            or self.paginas_coletadas == self.paginas_totais
        )

    @property
    def _tempo_passado(self) -> float:
        """Retorna a soma de todos os valores de tempo coletados."""
        return sum(self._tempos_paginas)

    @property
    def _tempo_medio_por_pagina(self) -> float:
        """Retorna a média de duração da coleta de uma página."""
        return self._tempo_passado / len(self._tempos_paginas)

    @property
    def _paginas_faltantes_geral(self) -> float:
        """
        Retorna a quantidade de páginas que faltam para concluir a
        execução.
        """
        return self.paginas_totais - self.paginas_coletadas

    @property
    def _paginas_coletadas_neste_ciclo(self) -> float:
        """Retorna a quantidade de páginas coletadas no ciclo."""
        return self.paginas_coletadas % self.paginas_ciclo

    @property
    def _paginas_faltantes_ciclo(self) -> float:
        """Retorna a quantidade de páginas que faltam para concluir o ciclo."""
        return self.paginas_ciclo - self._paginas_coletadas_neste_ciclo

    @property
    def _tempo_para_conclusao_geral(self) -> float:
        """Retorna uma estimativa em segundos para conclusão geral."""
        return (self._tempo_medio_por_pagina * self._paginas_faltantes_geral) // 1

    @property
    def _tempo_para_conclusao_ciclo(self) -> float:
        """Retorna uma estimativa em segundos para conclusão do ciclo."""
        return (self._tempo_medio_por_pagina * self._paginas_faltantes_ciclo) // 1

    @property
    def _segundos_desde_o_inicio(self) -> float:
        """
        Retorna o tempo passado em segundos da hora inicial até o momento
        atual.
        """
        return sum(self._tempos_paginas) // 1

    @property
    def _hora_final(self) -> float:
        """Retorna uma estimativa da hora de conclusão da execução."""
        return (
                self._hora_anterior
                + self._tempo_medio_por_pagina * self._paginas_faltantes_geral
        ) // 1
