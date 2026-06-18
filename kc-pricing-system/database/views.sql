-- =============================================================================
-- KC Pricing System — Views SQL Server
-- Gerado automaticamente pelo pipeline Lighthouse
-- =============================================================================

USE [kc-pricing-system];
GO

-- =============================================================================
-- vw_importacoes_base — Importações enriquecidas com dados do usuário
-- =============================================================================
CREATE OR ALTER VIEW [dbo].[vw_importacoes_base] AS
SELECT
    ib.[id],
    ib.[fonte],
    ib.[nome_arquivo],
    ib.[data_importacao],
    ib.[usuario_id],
    u.[nome]          AS [usuario_nome],
    u.[email]         AS [usuario_email],
    ib.[total_linhas],
    ib.[status],
    ib.[hash_arquivo],
    ib.[observacao],
    ib.[created_at],
    ib.[updated_at]
FROM [dbo].[importacoes_base] ib
INNER JOIN [dbo].[usuarios] u ON u.[id] = ib.[usuario_id];
GO

-- =============================================================================
-- vw_parametros_tributarios — Parâmetros com nome do usuário criador
-- =============================================================================
CREATE OR ALTER VIEW [dbo].[vw_parametros_tributarios] AS
SELECT
    pt.[id],
    pt.[ano_vigencia],
    pt.[regime],
    pt.[aliquota_ibs],
    pt.[aliquota_cbs],
    pt.[aliquota_icms],
    pt.[aliquota_pis],
    pt.[aliquota_cofins],
    pt.[aliquota_is],
    pt.[credito_pis_cofins],
    pt.[debito_icms],
    pt.[ativo],
    pt.[usuario_id],
    u.[nome]          AS [usuario_nome],
    pt.[created_at],
    pt.[updated_at]
FROM [dbo].[parametros_tributarios] pt
INNER JOIN [dbo].[usuarios] u ON u.[id] = pt.[usuario_id];
GO

-- =============================================================================
-- vw_listas_preco — Listas com dados do usuário gerador e aprovador
-- =============================================================================
CREATE OR ALTER VIEW [dbo].[vw_listas_preco] AS
SELECT
    lp.[id],
    lp.[descricao],
    lp.[data_geracao],
    lp.[usuario_id],
    u.[nome]              AS [usuario_nome],
    lp.[parametro_tributario_id],
    pt.[ano_vigencia]     AS [parametro_ano],
    pt.[regime]           AS [parametro_regime],
    lp.[status],
    lp.[total_skus],
    lp.[pct_dentro_cap],
    lp.[aprovado_por],
    apr.[nome]            AS [aprovador_nome],
    lp.[data_aprovacao],
    lp.[created_at],
    lp.[updated_at]
FROM [dbo].[listas_preco] lp
INNER JOIN [dbo].[usuarios] u ON u.[id] = lp.[usuario_id]
INNER JOIN [dbo].[parametros_tributarios] pt ON pt.[id] = lp.[parametro_tributario_id]
LEFT  JOIN [dbo].[usuarios] apr ON apr.[id] = lp.[aprovado_por];
GO

-- =============================================================================
-- vw_listas_preco_itens — Itens com SKU, descrição e dados da lista
-- =============================================================================
CREATE OR ALTER VIEW [dbo].[vw_listas_preco_itens] AS
SELECT
    lpi.[id],
    lpi.[lista_preco_id],
    lp.[descricao]        AS [lista_descricao],
    lp.[status]           AS [lista_status],
    lpi.[produto_id],
    p.[sku],
    p.[descricao]         AS [produto_descricao],
    p.[familia],
    p.[canal],
    p.[regiao],
    p.[preco_atual],
    lpi.[ptc_sell_out],
    lpi.[margem_cadeia_pct],
    lpi.[sell_in_nf],
    lpi.[sell_in_niv],
    lpi.[custo_aquisicao],
    lpi.[markup],
    lpi.[cap_aplicado],
    lpi.[variacao_pct],
    lpi.[created_at],
    lpi.[updated_at]
FROM [dbo].[listas_preco_itens] lpi
INNER JOIN [dbo].[listas_preco] lp ON lp.[id] = lpi.[lista_preco_id]
INNER JOIN [dbo].[produtos] p ON p.[id] = lpi.[produto_id];
GO

-- =============================================================================
-- vw_cenarios_simulacao — Cenários com dados de lista e parâmetros
-- =============================================================================
CREATE OR ALTER VIEW [dbo].[vw_cenarios_simulacao] AS
SELECT
    cs.[id],
    cs.[descricao],
    cs.[tipo_cenario],
    cs.[lista_preco_id],
    lp.[descricao]        AS [lista_descricao],
    lp.[status]           AS [lista_status],
    cs.[parametro_tributario_id],
    pt.[ano_vigencia]     AS [parametro_ano],
    pt.[regime]           AS [parametro_regime],
    cs.[data_simulacao],
    cs.[usuario_id],
    u.[nome]              AS [usuario_nome],
    cs.[delta_volume_pct],
    cs.[delta_receita_niv],
    cs.[delta_margem_industria],
    cs.[created_at],
    cs.[updated_at]
FROM [dbo].[cenarios_simulacao] cs
INNER JOIN [dbo].[listas_preco] lp ON lp.[id] = cs.[lista_preco_id]
INNER JOIN [dbo].[parametros_tributarios] pt ON pt.[id] = cs.[parametro_tributario_id]
INNER JOIN [dbo].[usuarios] u ON u.[id] = cs.[usuario_id];
GO

-- =============================================================================
-- vw_cenarios_simulacao_itens — Itens de simulação com dados do produto e cenário
-- =============================================================================
CREATE OR ALTER VIEW [dbo].[vw_cenarios_simulacao_itens] AS
SELECT
    csi.[id],
    csi.[cenario_id],
    cs.[descricao]           AS [cenario_descricao],
    cs.[tipo_cenario],
    csi.[produto_id],
    p.[sku],
    p.[descricao]            AS [produto_descricao],
    p.[familia],
    p.[canal],
    p.[regiao],
    csi.[volume_simulado],
    csi.[receita_niv_simulada],
    csi.[margem_industria],
    csi.[margem_distribuidor],
    csi.[margem_varejo],
    csi.[created_at],
    csi.[updated_at]
FROM [dbo].[cenarios_simulacao_itens] csi
INNER JOIN [dbo].[cenarios_simulacao] cs ON cs.[id] = csi.[cenario_id]
INNER JOIN [dbo].[produtos] p ON p.[id] = csi.[produto_id];
GO

PRINT 'Views KC Pricing System created successfully.';
GO
