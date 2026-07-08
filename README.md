# ETL para Extração de Dados de Sistema Legado

Pipeline ETL desenvolvido em Python para automatizar a coleta de dados de um sistema legado utilizado em ambiente operacional.

O projeto surgiu da necessidade de substituir um processo manual que consumia horas de trabalho e ainda limitava o acesso às informações disponíveis na plataforma. A solução automatiza autenticação, navegação, extração, tratamento e persistência dos dados, permitindo a construção de bases completas para análises operacionais e geração de indicadores.

> **Situação atual:** este repositório representa a versão em processo de refatoração para publicação. O sistema encontra-se funcional e utilizado em ambiente real, enquanto a estrutura do código, documentação e organização estão sendo gradualmente adaptadas para disponibilização pública.

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

## Tecnologias

- Linguagem
  - Python
- Automação
  - Selenium
  - Requests
  - BeautifulSoup
- Processamento
  - Pandas
- Persistência
  - PyODBC
- Interface
  - Tkinter
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

- [ ] Reorganização da arquitetura do projeto
- [ ] Separação em módulos independentes
- [ ] Configuração via arquivo `.env`
- [ ] Logging estruturado
- [ ] Testes automatizados
- [ ] Documentação completa
- [ ] Diagramas da arquitetura
- [ ] Publicação de exemplos de execução

---

## Objetivo deste repositório

Além de documentar um desenvolvido para resolver uma necessidade operacional real, este repositório registra a evolução da sua refatoração para um padrão mais próximo de projetos profissionais de software, preservando a lógica construída durante sua utilização em ambiente real.