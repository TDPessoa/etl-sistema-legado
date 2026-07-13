"""
Instruções SQL utilizadas pela aplicação.
"""

# Criação de estruturas
NOVO_METADADOS: str = """
CREATE TABLE [dados] (
    [id]                COUNTER,
    [id_pagina]         CHAR(10),
    [data_coleta]       TIMESTAMP,
    [sha]               CHAR(64),
    [texto_html]        MEMO,
        CONSTRAINT [PrimaryKey] PRIMARY KEY ([id]),
        CONSTRAINT [Unique Index] UNIQUE (id_pagina)
    )
;"""

# Inserções
POPULAR_METADADOS: str = """
INSERT INTO [dados](id_pagina, data_coleta, sha, texto_html)
VALUES ('{0}', #{1}#, '{2}', '{3}');
"""
POPULAR_DADOS: str = """
INSERT INTO [_dados_nao_tratados](
    lblCodigo, lblDataCriacao, lblTitulo, lblCategoria, lblResponsavel, 
    txtLatitude, txtLongitude, txtCidade, txtEndereco, txtReferencia, 
    txtDestino, txtOrigem, txtDescricao, lblTipoRegistro, lblPrioridade, 
    lblSituacao, lblHistorico, lblHoraCriacao, lblHoraAtualizacao, 
    lblHoraProcessamento, lblHoraInicio, lblHoraFim, lblTempoTotal, 
    rptrObservacoes_ctl01_txtTexto, rptrAnotacoes_ctl01_txtTexto, 
    txtQuantidade, rbTipoRegistro, ddlCategoria, ddlStatus, 
    ddlPrioridade, localizacao) 
VALUES (
    '{0}', '{1}', '{2}', '{3}', '{4}', 
    '{5}', '{6}', '{7}', '{8}', '{9}', 
    '{10}', '{11}', '{12}', '{13}', '{14}', 
    '{15}', '{16}', '{17}', '{18}', 
    '{19}', '{20}', '{21}', '{22}', 
    '{23}', '{24}', 
    '{25}', '{26}', '{27}', '{28}', 
    '{29}', '{30}');
"""

# Consultas
SELECAO_IDS_BANCO_DE_DADOS: str = """
SELECT [_dados_nao_tratados].[lblCodigo] 
FROM [_dados_nao_tratados];
"""
SELECAO_IDS_METADADOS: str = """
SELECT [dados].[id_pagina] 
FROM [dados];
"""

# Exclusões
EXCLUSAO_DADOS: str = """
DELETE FROM [_dados_nao_tratados] 
WHERE (([_dados_nao_tratados].[lblCodigo])='{}');
"""
EXCLUSAO_METADADOS: str = """
DELETE FROM [dados] 
WHERE (([dados].[id_pagina])='{}');
"""
