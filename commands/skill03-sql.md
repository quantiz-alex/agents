# Skill 03 — SQL Generation Skill

Leia `docs/data_model.yaml` e gere os scripts SQL compatíveis com SQL Server e Microsoft Fabric.

## Instruções

1. Leia APENAS `docs/data_model.yaml`.
2. Gere os três arquivos de banco de dados listados abaixo.
3. Se os arquivos já existirem, aplique patch incremental — não regere tudo.
4. Execute as entidades em ordem respeitando dependências de FK.

## Arquivos de Saída

### `database/schema.sql`

Para cada entidade:

```sql
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '<table>')
BEGIN
    CREATE TABLE [dbo].[<table>] (
        id          INT IDENTITY(1,1) PRIMARY KEY,
        -- campos conforme data_model.yaml
        created_at  DATETIME2 DEFAULT GETDATE(),
        updated_at  DATETIME2 DEFAULT GETDATE()
    );
END
GO
```

### `database/views.sql`

Para cada entidade principal, gere uma view de consulta com JOINs de entidades relacionadas:

```sql
CREATE OR ALTER VIEW [dbo].[vw_<entity>] AS
SELECT ...
FROM [dbo].[<table>] t
LEFT JOIN ...
GO
```

### `database/procedures.sql`

Para cada entidade, gere procedures padrão:

- `usp_<entity>_get_all`
- `usp_<entity>_get_by_id`
- `usp_<entity>_insert`
- `usp_<entity>_update`
- `usp_<entity>_delete` (soft delete via campo `ativo`)

## Restrições

- Compatível com SQL Server 2019+ e Microsoft Fabric Warehouse.
- Usar `IF NOT EXISTS` / `CREATE OR ALTER` para idempotência.
- Não usar sintaxe que não existe no Fabric (ex.: cursores, triggers).
- Campos de FK devem ter índice.
- Contexto máximo: **8.000 tokens** de saída por arquivo (anteriormente 2.000).
- Se exceder 8.000 tokens, dividir em chunks com continuação automática.

## Pós-processamento

1. Executar `/skill00-validator step3` automaticamente
2. Verificar ordem de criação de tabelas (topological sort)
3. Se validação falhar → reportar erros e sugestões
4. Se validação passar → criar checkpoint e avançar

## Argumento opcional

$ARGUMENTS
