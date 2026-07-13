# ETL para Extração de Dados de Sistema Legado

Aplicação desktop desenvolvida em Python para automatizar a extração, transformação e persistência de dados provenientes de um sistema legado.

O projeto surgiu da necessidade de substituir um processo manual que consumia horas de trabalho e ainda limitava o acesso às informações disponíveis na plataforma. A solução automatiza autenticação, navegação, extração, tratamento e persistência dos dados, permitindo a construção de bases completas para análises operacionais e geração de indicadores.

*Situação atual*: este repositório contém a versão base publicada do projeto, atualmente em evolução incremental. As refatorações, melhorias de arquitetura e documentação são registradas ao longo do histórico de commits, preservando a lógica utilizada em produção.

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
- acompanhar toda a execução através de uma interface de monitoramento.

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
├── main.py                  # Ponto de entrada da aplicação
│
├── utils/
│   ├── chrome/             # Dependências do navegador para automação
│   ├── classes/            # Classes auxiliares da aplicação
│   ├── imagens/            # Recursos utilizados pela interface
│   ├── poligonos/          # Arquivos GIS utilizados na identificação espacial
│   ├── config.py           # Configurações internas
│   ├── funcoes.py          # Funções auxiliares
│   └── instrucoes_sql.py   # Consultas SQL utilizadas pela aplicação
│
├── dados/
│   ├── alvos/              # Arquivos de referência utilizados durante a coleta
│   ├── metadados/          # Dados brutos coletados
│   └── dados.accdb         # Banco de dados da aplicação
│
├── config.txt              # Configuração da execução
│
└── README.md
```

*A estrutura será atualizada conforme a refatoração evoluir.*

---

## Próximas melhorias

### Arquitetura

- [ ] Reorganizar responsabilidades entre módulos
- [ ] Melhorar a estrutura do projeto
- [ ] Centralizar configurações em `.env`

### Qualidade

- [ ] Logging estruturado
- [ ] Testes automatizados
- [ ] Cobertura de tipos
- [ ] Revisão incremental de código

### Documentação

- [ ] Diagramas da arquitetura
- [ ] Documentação técnica
- [ ] Exemplos de execução
---

## Objetivo deste repositório

Além de documentar um projeto desenvolvido para resolver uma necessidade operacional real, este repositório registra a evolução da sua refatoração para um padrão mais próximo de projetos profissionais de software, preservando a lógica construída durante sua utilização em ambiente real.