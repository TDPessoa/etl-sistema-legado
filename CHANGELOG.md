# Changelog

Todas as alterações relevantes deste repositório serão documentadas neste arquivo.

Este documento registra a evolução da versão pública do projeto. O desenvolvimento anterior ocorreu em ambiente privado e não faz parte deste histórico.

O projeto segue uma convenção inspirada em *Keep a Changelog* e utiliza *Conventional Commits* para organização do histórico de desenvolvimento.

---

## [Unreleased]

### Planned

* Modernização da arquitetura da aplicação.
* Evolução do mecanismo de extração.
* Revisão do modelo de persistência.
* Aprimoramento do sistema de configuração.

> Esta etapa representa a próxima grande evolução do projeto, prevista para a versão **2.0**.

---

## [1.5.0] - 2026-07-16

### Added

* Inclusão do arquivo `CHANGELOG.md` para registro da evolução pública do projeto.
* Inclusão do arquivo `ROADMAP.md` para documentar a direção planejada do projeto.
* Inclusão da licença MIT para distribuição do repositório.

### Changed

* Atualizada a documentação principal do projeto.
* Atualizada a estrutura documentada do repositório conforme a organização atual dos módulos.
* Adicionadas referências aos documentos complementares (`CHANGELOG`, `ROADMAP` e `LICENSE`).

---

## [1.4.1] - 2026-07-16

### Changed

* Atualizadas as referências de importação após a reorganização dos módulos realizada na versão anterior.

## [1.4.0] - 2026-07-15

### Added

* Criação do módulo `extraction/` para concentrar as rotinas de autenticação e extração.
* Criação do módulo `transformation/` para concentrar o tratamento e manipulação dos dados.
* Criação do módulo `persistence/` para centralizar a comunicação com a camada de persistência.
* Criação do módulo `geospatial/` para reunir as ferramentas de processamento e identificação espacial.

### Changed

* Reorganizada a estrutura do projeto, distribuindo responsabilidades anteriormente concentradas em `utils/funcoes.py`.

## [1.3.1] - 2026-07-13

### Removed

* Removido um arquivo residual de configuração de IDE não identificado na publicação anterior.

## [1.3.0] - 2026-07-13

### Added

* Inclusão do arquivo `.gitignore` para padronização dos arquivos versionados.

### Changed

* Definidas as regras iniciais de versionamento e organização do repositório público.

### Removed

* Removidos arquivos de configuração específicos da IDE utilizados durante o desenvolvimento.

## [1.2.0] - 2026-07-13

### Changed

* Sanitizado o código-fonte para publicação pública.
* Aprimorada a legibilidade do projeto por meio de ajustes estruturais e padronização do código.

## [1.1.0] - 2026-07-09

### Changed

* Padronizada a organização das importações do projeto, eliminando importações coringa (`*`).

## [1.0.0] - 2026-07-08

### Added

* Primeira publicação pública do projeto.
* Inclusão do `README.md` com a documentação inicial.
* Estrutura inicial do repositório disponibilizada para acompanhamento da evolução do projeto.

---

## Convenções

* Versionamento: Semantic Versioning (SemVer)
* Histórico de commits: Conventional Commits
* Estrutura do changelog inspirada em *Keep a Changelog*
