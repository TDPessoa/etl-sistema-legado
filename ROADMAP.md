# Roadmap

Este documento apresenta os objetivos de alto nível para a evolução do projeto.

Diferentemente do `CHANGELOG.md`, que registra as alterações já realizadas, o roadmap descreve a direção planejada para o projeto. As prioridades podem ser ajustadas conforme novas necessidades surgirem durante a evolução da aplicação.

---

# Situação atual

A série **1.x** representa a publicação pública da aplicação utilizada em ambiente de produção e sua evolução incremental.

O foco atual é consolidar a organização do repositório e preparar a base para a próxima etapa de modernização da arquitetura.

---

# Versão 2.0 — Modernização da arquitetura

A próxima grande evolução do projeto consiste na revisão da arquitetura da aplicação, preservando a lógica de negócio construída ao longo de sua utilização em produção.

Os principais objetivos são:

## Extração

* Implementar um novo mecanismo de extração baseado em documentos PDF.
* Reduzir a dependência da navegação automatizada para obtenção dos dados.

## Persistência

* Evoluir o modelo de persistência da aplicação.
* Reorganizar a estrutura de armazenamento dos dados.

## Configuração

* Centralizar as configurações da aplicação.
* Simplificar a parametrização do ambiente de execução.

## Arquitetura

* Reorganizar as responsabilidades entre os módulos.
* Reduzir o acoplamento entre as etapas do pipeline.
* Melhorar a extensibilidade da aplicação para futuras evoluções.

---

# Evoluções futuras

Após a modernização da arquitetura, estão previstos estudos para:

* atualização da interface da aplicação;
* execução assíncrona do pipeline;
* ampliação da cobertura de testes;
* expansão da documentação técnica;
* melhoria da experiência de desenvolvimento.

---

# Princípios do projeto

A evolução deste projeto é guiada por alguns princípios:

* preservar a estabilidade da aplicação utilizada em produção;
* realizar mudanças de forma incremental;
* priorizar simplicidade em vez de complexidade desnecessária;
* registrar a evolução do projeto por meio de branches e Pull Requests bem definidas;
* manter a documentação compatível com o estado real da aplicação.

Este roadmap representa a visão atual do projeto e poderá ser atualizado conforme novas necessidades surgirem ao longo do desenvolvimento.
