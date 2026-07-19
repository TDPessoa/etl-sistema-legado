

class Pagina:
    def __init__(self, id_pagina: str) -> None:
        self.id_pagina: str = id_pagina
        self._html: str | None = None
        self._pdf = None
        self._dados: dict[str, str] = {}

    def inserir_html(self, html: str) -> None:
        """
        Armazena o código HTML da página.
        """
        self._html = html

    def renderizar(self, renderizador) -> None:
        """Renderiza o HTML em um documento PDF."""
        if self._html is None:
            raise RuntimeError("Nenhum HTML foi inserido.")
        
        self._pdf = renderizador.renderizar(self._html)

    def extrair_dados(self, extrator) -> None:
        """Extrai pares chave/valor do documento renderizado."""
        if self._pdf is None:
            raise RuntimeError("A página ainda não foi renderizada.")

        self._dados = extrator.extrair(self._pdf)