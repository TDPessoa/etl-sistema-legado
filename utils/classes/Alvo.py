"""
Representa um alvo de coleta do sistema de origem.
"""

import requests

from utils.config import URL_DE_DADOS


class Alvo:
    def __init__(self, id_pagina: str):
        self.id_pagina = id_pagina

    def __eq__(self, __o: Alvo) -> bool:
        return self.id_pagina == __o.id_pagina

    def __hash__(self) -> int:
        return hash(self.id_pagina)

    @property
    def url(self) -> str:
        """Gera a URL de acesso para uma página da web a partir de seu identificador."""
        return URL_DE_DADOS.format(self.id_pagina)

    def obter_conteudo(self, _sessao: requests.Session, _ck: dict[str, str]) -> str:
        """Obtém o conteúdo HTML desejado."""
        return _sessao.get(self.url, cookies=_ck).text