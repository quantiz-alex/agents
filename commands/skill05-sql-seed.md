# Skill 05 — SQL Seed Generation Skill

Leia `docs/data_model.yaml` e os arquivos em `mock_data/` para gerar `database/seed.sql`.

## Instruções

1. Leia `docs/data_model.yaml` para obter a estrutura das tabelas.
2. Leia cada arquivo `mock_data/<entidade>.json` para obter os dados.
3. Gere `database/seed.sql` com INSERTs para todas as entidades.
4. Respeite a ordem de inserção conforme dependências de FK.
5. Se o arquivo já existir, aplique patch incremental.

## Estrutura de Saída

```sql
-- ============================================================
-- SEED: <entidade>
-- ============================================================
SET IDENTITY_INSERT [dbo].[<table>] ON;
GO

INSERT INTO [dbo].[<table>] (id, campo1, campo2, ...)
VALUES
    (1, 'valor1', 'valor2', ...),
    (2, 'valor1', 'valor2', ...);
GO

SET IDENTITY_INSERT [dbo].[<table>] OFF;
GO
```

## Regras

- Usar `SET IDENTITY_INSERT ON/OFF` para preservar IDs do mock.
- Strings com aspas simples escapadas (`''`).
- Datas no formato `'YYYY-MM-DDTHH:MM:SS'`.
- Decimais com ponto.
- Bits como `1` ou `0`.
- Incluir cabeçalho comentado por entidade.
- Verificar existência antes de inserir para idempotência:

```sql
IF NOT EXISTS (SELECT 1 FROM [dbo].[<table>] WHERE id = 1)
BEGIN
    INSERT INTO ...
END
```

## Restrições

- Compatível com SQL Server e Microsoft Fabric.
- NÃO truncar tabelas — usar insert condicional.
- Contexto máximo: **8.000 tokens** de saída (anteriormente 2.000).
- Se exceder 8.000 tokens, dividir em chunks com continuação automática.

## Pós-processamento

1. Executar `/skill00-validator step5` automaticamente
2. Verificar ordem de INSERTs (respeitar FKs)
3. Se validação falhar → reportar erros e sugestões
4. Se validação passar → criar checkpoint e avançar

## Argumento opcional (entidade específica)

$ARGUMENTS
