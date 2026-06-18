-- =============================================================================
-- KC Pricing System — Stored Procedures SQL Server
-- Gerado automaticamente pelo pipeline Lighthouse
-- =============================================================================

USE [kc-pricing-system];
GO

-- =============================================================================
-- USUARIOS
-- =============================================================================

CREATE OR ALTER PROCEDURE [dbo].[usp_usuarios_get_all]
    @skip  INT = 0,
    @limit INT = 100
AS
BEGIN
    SET NOCOUNT ON;
    SELECT [id], [nome], [email], [role], [ativo], [created_at], [updated_at]
    FROM [dbo].[usuarios]
    ORDER BY [id]
    OFFSET @skip ROWS FETCH NEXT @limit ROWS ONLY;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_usuarios_get_by_id]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT [id], [nome], [email], [senha_hash], [role], [ativo], [created_at], [updated_at]
    FROM [dbo].[usuarios]
    WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_usuarios_insert]
    @nome       VARCHAR(100),
    @email      VARCHAR(150),
    @senha_hash VARCHAR(255),
    @role       VARCHAR(30),
    @ativo      BIT = 1
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[usuarios] ([nome], [email], [senha_hash], [role], [ativo])
    OUTPUT inserted.[id]
    VALUES (@nome, @email, @senha_hash, @role, @ativo);
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_usuarios_update]
    @id    BIGINT,
    @nome  VARCHAR(100)  = NULL,
    @role  VARCHAR(30)   = NULL,
    @ativo BIT           = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[usuarios]
    SET
        [nome]       = ISNULL(@nome, [nome]),
        [role]       = ISNULL(@role, [role]),
        [ativo]      = ISNULL(@ativo, [ativo]),
        [updated_at] = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_usuarios_delete]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    -- Soft delete
    UPDATE [dbo].[usuarios]
    SET [ativo] = 0, [updated_at] = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

-- =============================================================================
-- PRODUTOS
-- =============================================================================

CREATE OR ALTER PROCEDURE [dbo].[usp_produtos_get_all]
    @skip  INT = 0,
    @limit INT = 100
AS
BEGIN
    SET NOCOUNT ON;
    SELECT [id], [sku], [descricao], [familia], [embalagem], [classificacao],
           [canal], [regiao], [preco_atual], [ativo], [created_at], [updated_at]
    FROM [dbo].[produtos]
    ORDER BY [id]
    OFFSET @skip ROWS FETCH NEXT @limit ROWS ONLY;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_produtos_get_by_id]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[produtos] WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_produtos_insert]
    @sku           VARCHAR(50),
    @descricao     NVARCHAR(200),
    @familia       VARCHAR(100),
    @embalagem     VARCHAR(100)  = NULL,
    @classificacao VARCHAR(20)   = NULL,
    @canal         VARCHAR(100)  = NULL,
    @regiao        VARCHAR(100)  = NULL,
    @preco_atual   DECIMAL(15,4) = NULL,
    @ativo         BIT           = 1
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[produtos] ([sku], [descricao], [familia], [embalagem], [classificacao], [canal], [regiao], [preco_atual], [ativo])
    OUTPUT inserted.[id]
    VALUES (@sku, @descricao, @familia, @embalagem, @classificacao, @canal, @regiao, @preco_atual, @ativo);
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_produtos_update]
    @id            BIGINT,
    @descricao     NVARCHAR(200) = NULL,
    @familia       VARCHAR(100)  = NULL,
    @embalagem     VARCHAR(100)  = NULL,
    @classificacao VARCHAR(20)   = NULL,
    @canal         VARCHAR(100)  = NULL,
    @regiao        VARCHAR(100)  = NULL,
    @preco_atual   DECIMAL(15,4) = NULL,
    @ativo         BIT           = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[produtos]
    SET
        [descricao]     = ISNULL(@descricao, [descricao]),
        [familia]       = ISNULL(@familia, [familia]),
        [embalagem]     = ISNULL(@embalagem, [embalagem]),
        [classificacao] = ISNULL(@classificacao, [classificacao]),
        [canal]         = ISNULL(@canal, [canal]),
        [regiao]        = ISNULL(@regiao, [regiao]),
        [preco_atual]   = ISNULL(@preco_atual, [preco_atual]),
        [ativo]         = ISNULL(@ativo, [ativo]),
        [updated_at]    = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_produtos_delete]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[produtos]
    SET [ativo] = 0, [updated_at] = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

-- =============================================================================
-- PARAMETROS_TRIBUTARIOS
-- =============================================================================

CREATE OR ALTER PROCEDURE [dbo].[usp_parametros_tributarios_get_all]
    @skip  INT = 0,
    @limit INT = 100
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[parametros_tributarios]
    ORDER BY [ano_vigencia], [regime]
    OFFSET @skip ROWS FETCH NEXT @limit ROWS ONLY;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_parametros_tributarios_get_by_id]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[parametros_tributarios] WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_parametros_tributarios_insert]
    @ano_vigencia      INT,
    @regime            VARCHAR(20),
    @aliquota_ibs      DECIMAL(5,4),
    @aliquota_cbs      DECIMAL(5,4),
    @aliquota_icms     DECIMAL(5,4),
    @aliquota_pis      DECIMAL(5,4),
    @aliquota_cofins   DECIMAL(5,4),
    @aliquota_is       DECIMAL(5,4),
    @credito_pis_cofins DECIMAL(5,4) = NULL,
    @debito_icms       DECIMAL(5,4)  = NULL,
    @ativo             BIT           = 0,
    @usuario_id        BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[parametros_tributarios]
        ([ano_vigencia], [regime], [aliquota_ibs], [aliquota_cbs], [aliquota_icms],
         [aliquota_pis], [aliquota_cofins], [aliquota_is], [credito_pis_cofins],
         [debito_icms], [ativo], [usuario_id])
    OUTPUT inserted.[id]
    VALUES (@ano_vigencia, @regime, @aliquota_ibs, @aliquota_cbs, @aliquota_icms,
            @aliquota_pis, @aliquota_cofins, @aliquota_is, @credito_pis_cofins,
            @debito_icms, @ativo, @usuario_id);
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_parametros_tributarios_update]
    @id                BIGINT,
    @ativo             BIT           = NULL,
    @credito_pis_cofins DECIMAL(5,4) = NULL,
    @debito_icms       DECIMAL(5,4)  = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[parametros_tributarios]
    SET
        [ativo]              = ISNULL(@ativo, [ativo]),
        [credito_pis_cofins] = ISNULL(@credito_pis_cofins, [credito_pis_cofins]),
        [debito_icms]        = ISNULL(@debito_icms, [debito_icms]),
        [updated_at]         = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_parametros_tributarios_delete]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[parametros_tributarios]
    SET [ativo] = 0, [updated_at] = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

-- =============================================================================
-- MARGENS_CADEIA
-- =============================================================================

CREATE OR ALTER PROCEDURE [dbo].[usp_margens_cadeia_get_all]
    @skip  INT = 0,
    @limit INT = 100
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[margens_cadeia]
    ORDER BY [familia], [canal]
    OFFSET @skip ROWS FETCH NEXT @limit ROWS ONLY;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_margens_cadeia_get_by_id]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[margens_cadeia] WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_margens_cadeia_insert]
    @familia             VARCHAR(100),
    @canal               VARCHAR(100),
    @margem_industria    DECIMAL(5,4),
    @margem_distribuidor DECIMAL(5,4),
    @margem_varejo       DECIMAL(5,4),
    @price_index         DECIMAL(10,4),
    @relatividade        DECIMAL(10,4),
    @vigencia_inicio     DATE,
    @vigencia_fim        DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[margens_cadeia]
        ([familia], [canal], [margem_industria], [margem_distribuidor], [margem_varejo],
         [price_index], [relatividade], [vigencia_inicio], [vigencia_fim])
    OUTPUT inserted.[id]
    VALUES (@familia, @canal, @margem_industria, @margem_distribuidor, @margem_varejo,
            @price_index, @relatividade, @vigencia_inicio, @vigencia_fim);
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_margens_cadeia_update]
    @id                  BIGINT,
    @margem_industria    DECIMAL(5,4)  = NULL,
    @margem_distribuidor DECIMAL(5,4)  = NULL,
    @margem_varejo       DECIMAL(5,4)  = NULL,
    @price_index         DECIMAL(10,4) = NULL,
    @relatividade        DECIMAL(10,4) = NULL,
    @vigencia_fim        DATE          = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[margens_cadeia]
    SET
        [margem_industria]    = ISNULL(@margem_industria, [margem_industria]),
        [margem_distribuidor] = ISNULL(@margem_distribuidor, [margem_distribuidor]),
        [margem_varejo]       = ISNULL(@margem_varejo, [margem_varejo]),
        [price_index]         = ISNULL(@price_index, [price_index]),
        [relatividade]        = ISNULL(@relatividade, [relatividade]),
        [vigencia_fim]        = ISNULL(@vigencia_fim, [vigencia_fim]),
        [updated_at]          = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_margens_cadeia_delete]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM [dbo].[margens_cadeia] WHERE [id] = @id;
END
GO

-- =============================================================================
-- IMPORTACOES_BASE
-- =============================================================================

CREATE OR ALTER PROCEDURE [dbo].[usp_importacoes_base_get_all]
    @skip  INT = 0,
    @limit INT = 100
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[importacoes_base]
    ORDER BY [data_importacao] DESC
    OFFSET @skip ROWS FETCH NEXT @limit ROWS ONLY;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_importacoes_base_get_by_id]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[importacoes_base] WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_importacoes_base_insert]
    @fonte           VARCHAR(50),
    @nome_arquivo    VARCHAR(255),
    @data_importacao DATETIME2,
    @usuario_id      BIGINT,
    @total_linhas    INT           = NULL,
    @status          VARCHAR(20),
    @hash_arquivo    VARCHAR(64),
    @observacao      NVARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[importacoes_base]
        ([fonte], [nome_arquivo], [data_importacao], [usuario_id], [total_linhas],
         [status], [hash_arquivo], [observacao])
    OUTPUT inserted.[id]
    VALUES (@fonte, @nome_arquivo, @data_importacao, @usuario_id, @total_linhas,
            @status, @hash_arquivo, @observacao);
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_importacoes_base_update]
    @id           BIGINT,
    @status       VARCHAR(20)   = NULL,
    @total_linhas INT           = NULL,
    @observacao   NVARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[importacoes_base]
    SET
        [status]       = ISNULL(@status, [status]),
        [total_linhas] = ISNULL(@total_linhas, [total_linhas]),
        [observacao]   = ISNULL(@observacao, [observacao]),
        [updated_at]   = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_importacoes_base_delete]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM [dbo].[importacoes_base] WHERE [id] = @id;
END
GO

-- =============================================================================
-- LISTAS_PRECO
-- =============================================================================

CREATE OR ALTER PROCEDURE [dbo].[usp_listas_preco_get_all]
    @skip  INT = 0,
    @limit INT = 100
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[listas_preco]
    ORDER BY [data_geracao] DESC
    OFFSET @skip ROWS FETCH NEXT @limit ROWS ONLY;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_listas_preco_get_by_id]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[listas_preco] WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_listas_preco_insert]
    @descricao               NVARCHAR(200),
    @data_geracao            DATETIME2,
    @usuario_id              BIGINT,
    @parametro_tributario_id BIGINT,
    @status                  VARCHAR(30) = 'Gerada',
    @total_skus              INT         = NULL,
    @pct_dentro_cap          DECIMAL(5,2)= NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[listas_preco]
        ([descricao], [data_geracao], [usuario_id], [parametro_tributario_id],
         [status], [total_skus], [pct_dentro_cap])
    OUTPUT inserted.[id]
    VALUES (@descricao, @data_geracao, @usuario_id, @parametro_tributario_id,
            @status, @total_skus, @pct_dentro_cap);
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_listas_preco_update]
    @id              BIGINT,
    @status          VARCHAR(30)   = NULL,
    @total_skus      INT           = NULL,
    @pct_dentro_cap  DECIMAL(5,2)  = NULL,
    @aprovado_por    BIGINT        = NULL,
    @data_aprovacao  DATETIME2     = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[listas_preco]
    SET
        [status]         = ISNULL(@status, [status]),
        [total_skus]     = ISNULL(@total_skus, [total_skus]),
        [pct_dentro_cap] = ISNULL(@pct_dentro_cap, [pct_dentro_cap]),
        [aprovado_por]   = ISNULL(@aprovado_por, [aprovado_por]),
        [data_aprovacao] = ISNULL(@data_aprovacao, [data_aprovacao]),
        [updated_at]     = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_listas_preco_delete]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    -- Soft delete via status=Arquivada
    UPDATE [dbo].[listas_preco]
    SET [status] = 'Arquivada', [updated_at] = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

-- =============================================================================
-- LISTAS_PRECO_ITENS
-- =============================================================================

CREATE OR ALTER PROCEDURE [dbo].[usp_listas_preco_itens_get_all]
    @skip  INT = 0,
    @limit INT = 500
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[listas_preco_itens]
    ORDER BY [lista_preco_id], [produto_id]
    OFFSET @skip ROWS FETCH NEXT @limit ROWS ONLY;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_listas_preco_itens_get_by_id]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[listas_preco_itens] WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_listas_preco_itens_insert]
    @lista_preco_id    BIGINT,
    @produto_id        BIGINT,
    @ptc_sell_out      DECIMAL(15,4),
    @margem_cadeia_pct DECIMAL(5,4),
    @sell_in_nf        DECIMAL(15,4),
    @sell_in_niv       DECIMAL(15,4),
    @custo_aquisicao   DECIMAL(15,4) = NULL,
    @markup            DECIMAL(5,4)  = NULL,
    @cap_aplicado      BIT           = 0,
    @variacao_pct      DECIMAL(8,4)  = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[listas_preco_itens]
        ([lista_preco_id], [produto_id], [ptc_sell_out], [margem_cadeia_pct],
         [sell_in_nf], [sell_in_niv], [custo_aquisicao], [markup], [cap_aplicado], [variacao_pct])
    OUTPUT inserted.[id]
    VALUES (@lista_preco_id, @produto_id, @ptc_sell_out, @margem_cadeia_pct,
            @sell_in_nf, @sell_in_niv, @custo_aquisicao, @markup, @cap_aplicado, @variacao_pct);
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_listas_preco_itens_update]
    @id                BIGINT,
    @ptc_sell_out      DECIMAL(15,4) = NULL,
    @margem_cadeia_pct DECIMAL(5,4)  = NULL,
    @sell_in_nf        DECIMAL(15,4) = NULL,
    @sell_in_niv       DECIMAL(15,4) = NULL,
    @custo_aquisicao   DECIMAL(15,4) = NULL,
    @markup            DECIMAL(5,4)  = NULL,
    @cap_aplicado      BIT           = NULL,
    @variacao_pct      DECIMAL(8,4)  = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[listas_preco_itens]
    SET
        [ptc_sell_out]      = ISNULL(@ptc_sell_out, [ptc_sell_out]),
        [margem_cadeia_pct] = ISNULL(@margem_cadeia_pct, [margem_cadeia_pct]),
        [sell_in_nf]        = ISNULL(@sell_in_nf, [sell_in_nf]),
        [sell_in_niv]       = ISNULL(@sell_in_niv, [sell_in_niv]),
        [custo_aquisicao]   = ISNULL(@custo_aquisicao, [custo_aquisicao]),
        [markup]            = ISNULL(@markup, [markup]),
        [cap_aplicado]      = ISNULL(@cap_aplicado, [cap_aplicado]),
        [variacao_pct]      = ISNULL(@variacao_pct, [variacao_pct]),
        [updated_at]        = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_listas_preco_itens_delete]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM [dbo].[listas_preco_itens] WHERE [id] = @id;
END
GO

-- =============================================================================
-- CENARIOS_SIMULACAO
-- =============================================================================

CREATE OR ALTER PROCEDURE [dbo].[usp_cenarios_simulacao_get_all]
    @skip  INT = 0,
    @limit INT = 100
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[cenarios_simulacao]
    ORDER BY [data_simulacao] DESC
    OFFSET @skip ROWS FETCH NEXT @limit ROWS ONLY;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_cenarios_simulacao_get_by_id]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[cenarios_simulacao] WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_cenarios_simulacao_insert]
    @descricao               NVARCHAR(200),
    @tipo_cenario            VARCHAR(20),
    @lista_preco_id          BIGINT,
    @parametro_tributario_id BIGINT,
    @data_simulacao          DATETIME2,
    @usuario_id              BIGINT,
    @delta_volume_pct        DECIMAL(8,4)  = NULL,
    @delta_receita_niv       DECIMAL(15,2) = NULL,
    @delta_margem_industria  DECIMAL(15,2) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[cenarios_simulacao]
        ([descricao], [tipo_cenario], [lista_preco_id], [parametro_tributario_id],
         [data_simulacao], [usuario_id], [delta_volume_pct], [delta_receita_niv], [delta_margem_industria])
    OUTPUT inserted.[id]
    VALUES (@descricao, @tipo_cenario, @lista_preco_id, @parametro_tributario_id,
            @data_simulacao, @usuario_id, @delta_volume_pct, @delta_receita_niv, @delta_margem_industria);
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_cenarios_simulacao_update]
    @id                     BIGINT,
    @descricao              NVARCHAR(200) = NULL,
    @delta_volume_pct       DECIMAL(8,4)  = NULL,
    @delta_receita_niv      DECIMAL(15,2) = NULL,
    @delta_margem_industria DECIMAL(15,2) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[cenarios_simulacao]
    SET
        [descricao]              = ISNULL(@descricao, [descricao]),
        [delta_volume_pct]       = ISNULL(@delta_volume_pct, [delta_volume_pct]),
        [delta_receita_niv]      = ISNULL(@delta_receita_niv, [delta_receita_niv]),
        [delta_margem_industria] = ISNULL(@delta_margem_industria, [delta_margem_industria]),
        [updated_at]             = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_cenarios_simulacao_delete]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM [dbo].[cenarios_simulacao] WHERE [id] = @id;
END
GO

-- =============================================================================
-- CENARIOS_SIMULACAO_ITENS
-- =============================================================================

CREATE OR ALTER PROCEDURE [dbo].[usp_cenarios_simulacao_itens_get_all]
    @skip  INT = 0,
    @limit INT = 500
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[cenarios_simulacao_itens]
    ORDER BY [cenario_id], [produto_id]
    OFFSET @skip ROWS FETCH NEXT @limit ROWS ONLY;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_cenarios_simulacao_itens_get_by_id]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM [dbo].[cenarios_simulacao_itens] WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_cenarios_simulacao_itens_insert]
    @cenario_id           BIGINT,
    @produto_id           BIGINT,
    @volume_simulado      DECIMAL(15,2) = NULL,
    @receita_niv_simulada DECIMAL(15,4) = NULL,
    @margem_industria     DECIMAL(15,4) = NULL,
    @margem_distribuidor  DECIMAL(15,4) = NULL,
    @margem_varejo        DECIMAL(15,4) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[cenarios_simulacao_itens]
        ([cenario_id], [produto_id], [volume_simulado], [receita_niv_simulada],
         [margem_industria], [margem_distribuidor], [margem_varejo])
    OUTPUT inserted.[id]
    VALUES (@cenario_id, @produto_id, @volume_simulado, @receita_niv_simulada,
            @margem_industria, @margem_distribuidor, @margem_varejo);
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_cenarios_simulacao_itens_update]
    @id                   BIGINT,
    @volume_simulado      DECIMAL(15,2) = NULL,
    @receita_niv_simulada DECIMAL(15,4) = NULL,
    @margem_industria     DECIMAL(15,4) = NULL,
    @margem_distribuidor  DECIMAL(15,4) = NULL,
    @margem_varejo        DECIMAL(15,4) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[cenarios_simulacao_itens]
    SET
        [volume_simulado]      = ISNULL(@volume_simulado, [volume_simulado]),
        [receita_niv_simulada] = ISNULL(@receita_niv_simulada, [receita_niv_simulada]),
        [margem_industria]     = ISNULL(@margem_industria, [margem_industria]),
        [margem_distribuidor]  = ISNULL(@margem_distribuidor, [margem_distribuidor]),
        [margem_varejo]        = ISNULL(@margem_varejo, [margem_varejo]),
        [updated_at]           = SYSUTCDATETIME()
    WHERE [id] = @id;
END
GO

CREATE OR ALTER PROCEDURE [dbo].[usp_cenarios_simulacao_itens_delete]
    @id BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM [dbo].[cenarios_simulacao_itens] WHERE [id] = @id;
END
GO

PRINT 'Stored Procedures KC Pricing System created successfully.';
GO
