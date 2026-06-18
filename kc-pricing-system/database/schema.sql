-- =============================================================================
-- KC Pricing System — Schema SQL Server 2019+ / Microsoft Fabric
-- Gerado automaticamente pelo pipeline Lighthouse
-- Ordem topológica: tabelas sem FK criadas primeiro
-- =============================================================================

USE [kc-pricing-system];
GO

-- =============================================================================
-- 1. usuarios  (sem FK)
-- =============================================================================
IF OBJECT_ID(N'[dbo].[usuarios]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[usuarios] (
        [id]          BIGINT          NOT NULL IDENTITY(1,1),
        [nome]        VARCHAR(100)    NOT NULL,
        [email]       VARCHAR(150)    NOT NULL,
        [senha_hash]  VARCHAR(255)    NOT NULL,
        [role]        VARCHAR(30)     NOT NULL,
        [ativo]       BIT             NOT NULL CONSTRAINT [DF_usuarios_ativo] DEFAULT (1),
        [created_at]  DATETIME2       NOT NULL CONSTRAINT [DF_usuarios_created_at] DEFAULT (SYSUTCDATETIME()),
        [updated_at]  DATETIME2       NOT NULL CONSTRAINT [DF_usuarios_updated_at] DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT [PK_usuarios] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [UQ_usuarios_email] UNIQUE ([email]),
        CONSTRAINT [CK_usuarios_role] CHECK ([role] IN ('admin', 'gestor_pricing', 'analista_pricing'))
    );
    PRINT 'TABLE [usuarios] created.';
END
GO

-- =============================================================================
-- 2. produtos  (sem FK)
-- =============================================================================
IF OBJECT_ID(N'[dbo].[produtos]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[produtos] (
        [id]            BIGINT          NOT NULL IDENTITY(1,1),
        [sku]           VARCHAR(50)     NOT NULL,
        [descricao]     NVARCHAR(200)   NOT NULL,
        [familia]       VARCHAR(100)    NOT NULL,
        [embalagem]     VARCHAR(100)    NULL,
        [classificacao] VARCHAR(20)     NULL,
        [canal]         VARCHAR(100)    NULL,
        [regiao]        VARCHAR(100)    NULL,
        [preco_atual]   DECIMAL(15,4)   NULL,
        [ativo]         BIT             NOT NULL CONSTRAINT [DF_produtos_ativo] DEFAULT (1),
        [created_at]    DATETIME2       NOT NULL CONSTRAINT [DF_produtos_created_at] DEFAULT (SYSUTCDATETIME()),
        [updated_at]    DATETIME2       NOT NULL CONSTRAINT [DF_produtos_updated_at] DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT [PK_produtos] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [UQ_produtos_sku] UNIQUE ([sku]),
        CONSTRAINT [CK_produtos_classificacao] CHECK ([classificacao] IN ('Capitao', 'MainOffender', 'Seguidor') OR [classificacao] IS NULL)
    );
    PRINT 'TABLE [produtos] created.';
END
GO

-- =============================================================================
-- 3. margens_cadeia  (sem FK)
-- =============================================================================
IF OBJECT_ID(N'[dbo].[margens_cadeia]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[margens_cadeia] (
        [id]                  BIGINT          NOT NULL IDENTITY(1,1),
        [familia]             VARCHAR(100)    NOT NULL,
        [canal]               VARCHAR(100)    NOT NULL,
        [margem_industria]    DECIMAL(5,4)    NOT NULL,
        [margem_distribuidor] DECIMAL(5,4)    NOT NULL,
        [margem_varejo]       DECIMAL(5,4)    NOT NULL,
        [price_index]         DECIMAL(10,4)   NOT NULL,
        [relatividade]        DECIMAL(10,4)   NOT NULL,
        [vigencia_inicio]     DATE            NOT NULL,
        [vigencia_fim]        DATE            NULL,
        [created_at]          DATETIME2       NOT NULL CONSTRAINT [DF_margens_cadeia_created_at] DEFAULT (SYSUTCDATETIME()),
        [updated_at]          DATETIME2       NOT NULL CONSTRAINT [DF_margens_cadeia_updated_at] DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT [PK_margens_cadeia] PRIMARY KEY CLUSTERED ([id] ASC)
    );
    PRINT 'TABLE [margens_cadeia] created.';
END
GO

-- =============================================================================
-- 4. parametros_tributarios  (FK -> usuarios)
-- =============================================================================
IF OBJECT_ID(N'[dbo].[parametros_tributarios]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[parametros_tributarios] (
        [id]                BIGINT          NOT NULL IDENTITY(1,1),
        [ano_vigencia]      INT             NOT NULL,
        [regime]            VARCHAR(20)     NOT NULL,
        [aliquota_ibs]      DECIMAL(5,4)    NOT NULL,
        [aliquota_cbs]      DECIMAL(5,4)    NOT NULL,
        [aliquota_icms]     DECIMAL(5,4)    NOT NULL,
        [aliquota_pis]      DECIMAL(5,4)    NOT NULL,
        [aliquota_cofins]   DECIMAL(5,4)    NOT NULL,
        [aliquota_is]       DECIMAL(5,4)    NOT NULL,
        [credito_pis_cofins] DECIMAL(5,4)   NULL,
        [debito_icms]       DECIMAL(5,4)    NULL,
        [ativo]             BIT             NOT NULL CONSTRAINT [DF_pt_ativo] DEFAULT (0),
        [usuario_id]        BIGINT          NOT NULL,
        [created_at]        DATETIME2       NOT NULL CONSTRAINT [DF_pt_created_at] DEFAULT (SYSUTCDATETIME()),
        [updated_at]        DATETIME2       NOT NULL CONSTRAINT [DF_pt_updated_at] DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT [PK_parametros_tributarios] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [CK_pt_regime] CHECK ([regime] IN ('Legado', 'Reforma')),
        CONSTRAINT [FK_pt_usuario] FOREIGN KEY ([usuario_id]) REFERENCES [dbo].[usuarios] ([id])
    );
    PRINT 'TABLE [parametros_tributarios] created.';
END
GO

-- =============================================================================
-- 5. importacoes_base  (FK -> usuarios)
-- =============================================================================
IF OBJECT_ID(N'[dbo].[importacoes_base]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[importacoes_base] (
        [id]              BIGINT          NOT NULL IDENTITY(1,1),
        [fonte]           VARCHAR(50)     NOT NULL,
        [nome_arquivo]    VARCHAR(255)    NOT NULL,
        [data_importacao] DATETIME2       NOT NULL,
        [usuario_id]      BIGINT          NOT NULL,
        [total_linhas]    INT             NULL,
        [status]          VARCHAR(20)     NOT NULL,
        [hash_arquivo]    VARCHAR(64)     NOT NULL,
        [observacao]      NVARCHAR(500)   NULL,
        [created_at]      DATETIME2       NOT NULL CONSTRAINT [DF_ib_created_at] DEFAULT (SYSUTCDATETIME()),
        [updated_at]      DATETIME2       NOT NULL CONSTRAINT [DF_ib_updated_at] DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT [PK_importacoes_base] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [CK_ib_fonte] CHECK ([fonte] IN ('NielsenRetail', 'NielsenScantrack', 'PrecosERP', 'PL', 'Cadastros', 'DePara')),
        CONSTRAINT [CK_ib_status] CHECK ([status] IN ('Sucesso', 'Erro', 'Processando')),
        CONSTRAINT [FK_ib_usuario] FOREIGN KEY ([usuario_id]) REFERENCES [dbo].[usuarios] ([id])
    );
    PRINT 'TABLE [importacoes_base] created.';
END
GO

-- =============================================================================
-- 6. listas_preco  (FK -> usuarios, parametros_tributarios)
-- =============================================================================
IF OBJECT_ID(N'[dbo].[listas_preco]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[listas_preco] (
        [id]                      BIGINT          NOT NULL IDENTITY(1,1),
        [descricao]               NVARCHAR(200)   NOT NULL,
        [data_geracao]            DATETIME2       NOT NULL,
        [usuario_id]              BIGINT          NOT NULL,
        [parametro_tributario_id] BIGINT          NOT NULL,
        [status]                  VARCHAR(30)     NOT NULL,
        [total_skus]              INT             NULL,
        [pct_dentro_cap]          DECIMAL(5,2)    NULL,
        [aprovado_por]            BIGINT          NULL,
        [data_aprovacao]          DATETIME2       NULL,
        [created_at]              DATETIME2       NOT NULL CONSTRAINT [DF_lp_created_at] DEFAULT (SYSUTCDATETIME()),
        [updated_at]              DATETIME2       NOT NULL CONSTRAINT [DF_lp_updated_at] DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT [PK_listas_preco] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [CK_lp_status] CHECK ([status] IN ('Gerada', 'PendenteAprovacao', 'Aprovada', 'Rejeitada', 'Arquivada')),
        CONSTRAINT [FK_lp_usuario] FOREIGN KEY ([usuario_id]) REFERENCES [dbo].[usuarios] ([id]),
        CONSTRAINT [FK_lp_parametro] FOREIGN KEY ([parametro_tributario_id]) REFERENCES [dbo].[parametros_tributarios] ([id]),
        CONSTRAINT [FK_lp_aprovador] FOREIGN KEY ([aprovado_por]) REFERENCES [dbo].[usuarios] ([id])
    );
    PRINT 'TABLE [listas_preco] created.';
END
GO

-- =============================================================================
-- 7. listas_preco_itens  (FK -> listas_preco, produtos)
-- =============================================================================
IF OBJECT_ID(N'[dbo].[listas_preco_itens]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[listas_preco_itens] (
        [id]                BIGINT          NOT NULL IDENTITY(1,1),
        [lista_preco_id]    BIGINT          NOT NULL,
        [produto_id]        BIGINT          NOT NULL,
        [ptc_sell_out]      DECIMAL(15,4)   NOT NULL,
        [margem_cadeia_pct] DECIMAL(5,4)    NOT NULL,
        [sell_in_nf]        DECIMAL(15,4)   NOT NULL,
        [sell_in_niv]       DECIMAL(15,4)   NOT NULL,
        [custo_aquisicao]   DECIMAL(15,4)   NULL,
        [markup]            DECIMAL(5,4)    NULL,
        [cap_aplicado]      BIT             NOT NULL CONSTRAINT [DF_lpi_cap] DEFAULT (0),
        [variacao_pct]      DECIMAL(8,4)    NULL,
        [created_at]        DATETIME2       NOT NULL CONSTRAINT [DF_lpi_created_at] DEFAULT (SYSUTCDATETIME()),
        [updated_at]        DATETIME2       NOT NULL CONSTRAINT [DF_lpi_updated_at] DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT [PK_listas_preco_itens] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [FK_lpi_lista] FOREIGN KEY ([lista_preco_id]) REFERENCES [dbo].[listas_preco] ([id]),
        CONSTRAINT [FK_lpi_produto] FOREIGN KEY ([produto_id]) REFERENCES [dbo].[produtos] ([id])
    );
    PRINT 'TABLE [listas_preco_itens] created.';
END
GO

-- =============================================================================
-- 8. cenarios_simulacao  (FK -> listas_preco, parametros_tributarios, usuarios)
-- =============================================================================
IF OBJECT_ID(N'[dbo].[cenarios_simulacao]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[cenarios_simulacao] (
        [id]                      BIGINT          NOT NULL IDENTITY(1,1),
        [descricao]               NVARCHAR(200)   NOT NULL,
        [tipo_cenario]            VARCHAR(20)     NOT NULL,
        [lista_preco_id]          BIGINT          NOT NULL,
        [parametro_tributario_id] BIGINT          NOT NULL,
        [data_simulacao]          DATETIME2       NOT NULL,
        [usuario_id]              BIGINT          NOT NULL,
        [delta_volume_pct]        DECIMAL(8,4)    NULL,
        [delta_receita_niv]       DECIMAL(15,2)   NULL,
        [delta_margem_industria]  DECIMAL(15,2)   NULL,
        [created_at]              DATETIME2       NOT NULL CONSTRAINT [DF_cs_created_at] DEFAULT (SYSUTCDATETIME()),
        [updated_at]              DATETIME2       NOT NULL CONSTRAINT [DF_cs_updated_at] DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT [PK_cenarios_simulacao] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [CK_cs_tipo] CHECK ([tipo_cenario] IN ('MantemMargem', 'MantemPPC')),
        CONSTRAINT [FK_cs_lista] FOREIGN KEY ([lista_preco_id]) REFERENCES [dbo].[listas_preco] ([id]),
        CONSTRAINT [FK_cs_parametro] FOREIGN KEY ([parametro_tributario_id]) REFERENCES [dbo].[parametros_tributarios] ([id]),
        CONSTRAINT [FK_cs_usuario] FOREIGN KEY ([usuario_id]) REFERENCES [dbo].[usuarios] ([id])
    );
    PRINT 'TABLE [cenarios_simulacao] created.';
END
GO

-- =============================================================================
-- 9. cenarios_simulacao_itens  (FK -> cenarios_simulacao, produtos)
-- =============================================================================
IF OBJECT_ID(N'[dbo].[cenarios_simulacao_itens]', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[cenarios_simulacao_itens] (
        [id]                    BIGINT          NOT NULL IDENTITY(1,1),
        [cenario_id]            BIGINT          NOT NULL,
        [produto_id]            BIGINT          NOT NULL,
        [volume_simulado]       DECIMAL(15,2)   NULL,
        [receita_niv_simulada]  DECIMAL(15,4)   NULL,
        [margem_industria]      DECIMAL(15,4)   NULL,
        [margem_distribuidor]   DECIMAL(15,4)   NULL,
        [margem_varejo]         DECIMAL(15,4)   NULL,
        [created_at]            DATETIME2       NOT NULL CONSTRAINT [DF_csi_created_at] DEFAULT (SYSUTCDATETIME()),
        [updated_at]            DATETIME2       NOT NULL CONSTRAINT [DF_csi_updated_at] DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT [PK_cenarios_simulacao_itens] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [FK_csi_cenario] FOREIGN KEY ([cenario_id]) REFERENCES [dbo].[cenarios_simulacao] ([id]),
        CONSTRAINT [FK_csi_produto] FOREIGN KEY ([produto_id]) REFERENCES [dbo].[produtos] ([id])
    );
    PRINT 'TABLE [cenarios_simulacao_itens] created.';
END
GO

-- =============================================================================
-- Indexes adicionais
-- =============================================================================
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_parametros_tributarios_ano_regime' AND object_id = OBJECT_ID('[dbo].[parametros_tributarios]'))
    CREATE INDEX [IX_parametros_tributarios_ano_regime] ON [dbo].[parametros_tributarios] ([ano_vigencia], [regime]);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_parametros_tributarios_ativo' AND object_id = OBJECT_ID('[dbo].[parametros_tributarios]'))
    CREATE INDEX [IX_parametros_tributarios_ativo] ON [dbo].[parametros_tributarios] ([ativo]);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_produtos_familia_canal' AND object_id = OBJECT_ID('[dbo].[produtos]'))
    CREATE INDEX [IX_produtos_familia_canal] ON [dbo].[produtos] ([familia], [canal]);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_importacoes_base_usuario' AND object_id = OBJECT_ID('[dbo].[importacoes_base]'))
    CREATE INDEX [IX_importacoes_base_usuario] ON [dbo].[importacoes_base] ([usuario_id]);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_importacoes_base_fonte_data' AND object_id = OBJECT_ID('[dbo].[importacoes_base]'))
    CREATE INDEX [IX_importacoes_base_fonte_data] ON [dbo].[importacoes_base] ([fonte], [data_importacao]);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_listas_preco_status' AND object_id = OBJECT_ID('[dbo].[listas_preco]'))
    CREATE INDEX [IX_listas_preco_status] ON [dbo].[listas_preco] ([status]);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_listas_preco_itens_lista' AND object_id = OBJECT_ID('[dbo].[listas_preco_itens]'))
    CREATE INDEX [IX_listas_preco_itens_lista] ON [dbo].[listas_preco_itens] ([lista_preco_id]);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_listas_preco_itens_produto' AND object_id = OBJECT_ID('[dbo].[listas_preco_itens]'))
    CREATE INDEX [IX_listas_preco_itens_produto] ON [dbo].[listas_preco_itens] ([produto_id]);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_cenarios_simulacao_lista' AND object_id = OBJECT_ID('[dbo].[cenarios_simulacao]'))
    CREATE INDEX [IX_cenarios_simulacao_lista] ON [dbo].[cenarios_simulacao] ([lista_preco_id]);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_cenarios_simulacao_itens_cenario' AND object_id = OBJECT_ID('[dbo].[cenarios_simulacao_itens]'))
    CREATE INDEX [IX_cenarios_simulacao_itens_cenario] ON [dbo].[cenarios_simulacao_itens] ([cenario_id]);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_margens_cadeia_familia_canal' AND object_id = OBJECT_ID('[dbo].[margens_cadeia]'))
    CREATE INDEX [IX_margens_cadeia_familia_canal] ON [dbo].[margens_cadeia] ([familia], [canal]);
GO

PRINT 'Schema KC Pricing System created successfully.';
GO
