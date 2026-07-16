# ETL para Extração de Dados de Sistema Legado

Aplicação desktop desenvolvida em Python para automatizar a extração, transformação e persistência de dados provenientes de um sistema legado.

O projeto surgiu da necessidade de substituir um processo manual que consumia horas de trabalho e ainda limitava o acesso às informações disponíveis na plataforma. A solução automatiza autenticação, navegação, extração, tratamento e persistência dos dados, permitindo a construção de bases completas para análises operacionais e geração de indicadores.

*Situação atual*: este repositório contém a versão pública do projeto, atualmente em evolução incremental. As alterações, melhorias arquiteturais e decisões de organização são registradas através do histórico de commits, Pull Requests e documentação complementar.


## Documentação

- [CHANGELOG](CHANGELOG.md) — histórico das alterações realizadas no projeto.
- [ROADMAP](ROADMAP.md) — objetivos e direção planejada para evolução do projeto.
- [LICENSE](LICENSE) — termos de utilização e distribuição.

---

## O problema

O sistema original apresentava diversas limitações:

- exportação incompleta dos dados;
- necessidade de consultas manuais repetitivas;
- coleta extremamente demorada;
- dificuldade para construção de bases históricas consistentes;
- elevado risco de erros humanos.

Em determinadas situações, uma atividade que demandava horas passou a ser executada em poucos minutos.

---

## A solução

Foi desenvolvido um pipeline ETL responsável por:

- autenticar automaticamente no sistema;
- navegar pelas páginas de consulta;
- coletar informações indisponíveis na exportação nativa;
- tratar inconsistências encontradas durante a coleta;
- persistir os dados em banco de dados;
- acompanhar a execução por meio de uma interface de monitoramento.

O projeto também implementa mecanismos para retomada da execução, tratamento de exceções e controle do progresso da coleta.

### Fluxo do pipeline: 
```
Sistema legado
        │  
        ▼  
Autenticação  
        │  
        ▼  
Coleta automatizada  
        │  
        ▼  
Tratamento  
        │  
        ▼  
Persistência  
        │  
        ▼  
Base de dados estruturada  
```
---

## Principais funcionalidades

- Extração automatizada de dados
- Pipeline ETL
- Automação de navegação autenticada
- Interface de acompanhamento em tempo real
- Persistência em banco de dados
- Tratamento de erros
- Controle de progresso
- Execução em lotes
- Configuração parametrizada

---

## Tecnologias e conceitos

- Python
- ETL
- Selenium
- Requests
- BeautifulSoup
- Pandas
- PyODBC
- Tkinter
- SQL
- Web Scraping
- Automação Desktop
---

## Estrutura do projeto
```
etl-sistema-legado/
│
├── extraction/              # Recursos relacionados à autenticação e extração
├── geospatial/              # Recursos de processamento espacial
├── persistence/             # Comunicação com estruturas de dados
├── transformation/          # Tratamento e transformação dos dados
│
├── utils/
│   ├── classes/             # Classes auxiliares
│   ├── config.py            # Configurações internas
│   └── instrucoes_sql.py    # Consultas SQL utilizadas pela aplicação
│
├── dados/
│
├── config.txt
├── main.py
├── README.md
├── CHANGELOG.md
├── ROADMAP.md
└── LICENSE
```

*A estrutura apresentada representa a organização atual do projeto e poderá evoluir conforme as próximas etapas de desenvolvimento.*

---

## Próximos passos

As próximas etapas de evolução do projeto estão descritas no arquivo [ROADMAP](ROADMAP.md).

---

## Objetivo deste repositório

Além de documentar um projeto desenvolvido para resolver uma necessidade operacional real, este repositório registra a evolução da sua refatoração para um padrão mais próximo de projetos profissionais de software, preservando a lógica construída durante sua utilização em ambiente real.

---

## Licença

Este projeto está licenciado sob os termos da licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais informações.