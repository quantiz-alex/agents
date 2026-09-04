# Skill 05 — SQL Seed Validation Skill (v4 — validação/ajuste)

Valida e ajusta `database/seed.sql` **gerado pelo `mock_generator.py`** (Step 4). Em v3 o LLM escrevia INSERTs à mão (limite 8.000 tokens, truncava tabelas grandes). Agora o motor gera o arquivo completo e este skill apenas **audita**.

> Se `database/seed.sql` não existir → voltar ao Step 4 (`/skill04-mock-data`). Este skill **não gera** seed do zero.

## Instruções

1. Verificar que `database/seed.sql` existe. Se não → PARAR e reportar "seed.sql ausente — execute Step 4 primeiro".
2. Ler `docs/data_model.yaml` para obter a estrutura das tabelas e a ordem topológica de FKs.
3. Ler `database/seed.sql` em blocos (pode ser grande — ler por partes se necessário).
4. Aplicar os checks abaixo. Se algum falhar → reportar o problema e sugerir correção no **spec** (`docs/mock_spec.yaml`), não no SQL diretamente (o motor regenera a partir do spec).

## Checks

### Estrutura
- [ ] Cabeçalho comentado por entidade: `-- ============================================================ -- SEED: <entidade>`
- [ ] Uma seção por entidade do `data_model.yaml` (nenhuma faltando, nenhuma extra)
- [ ] `SET IDENTITY_INSERT [dbo].[<table>] ON;` antes dos INSERTs, `OFF;` depois, `GO` entre blocos

### Ordem de FKs
- [ ] Entidades sem FK aparecem antes das que referenciam elas (ordem topológica)
- [ ] Comparar com a ordem de `data_model.yaml → entities` (que já é topológica)

### Idempotência
- [ ] Cada bloco usa `IF NOT EXISTS (SELECT 1 FROM [dbo].[<table>] WHERE id = N)` ou `MERGE` — reexecução não duplica
- [ ] NÃO usar `TRUNCATE` nem `DELETE` (compatível com ambiente compartilhado)

### Sintaxe SQL Server/Fabric
- [ ] Strings com aspas simples escapadas (`''`)
- [ ] Datas no formato `'YYYY-MM-DDTHH:MM:SS'` (datetime2) ou `'YYYY-MM-DD'` (date)
- [ ] Decimais com ponto (`.`), não vírgula
- [ ] Bits como `1`/`0` (não `true`/`false`)
- [ ] `GO` entre batches (não `;`)

### Volume
- [ ] Cada tabela tem ≤ `seed_cap` linhas no seed.sql (default 2000 — o motor faz o cap automaticamente; CSV em `mock_data/` mantém o volume completo)
- [ ] Se uma tabela exceder o cap → confirmar que `mock_data/<entidade>.csv` tem o volume completo (o seed.sql é apenas para bootstrap rápido)

### Integridade referencial (amostragem)
- [ ] IDs referenciados em FKs existem nos INSERTs da tabela pai (checar pelo menos 3 FKs aleatórias)
- [ ] Valores de enum estão dentro do `enums` do `data_model.yaml`

## Ajustes permitidos (somente se o motor não cobriu)

- Adicionar `SET IDENTITY_INSERT` faltante.
- Corrigir ordem de blocos (mover seção inteira — não reescrever INSERTs).
- Adicionar `IF NOT EXISTS` wrapper em bloco que não tem.

**NÃO reescrever INSERTs** — se o conteúdo estiver erroado, corrigir o spec e regenerar via `python scripts/generate_mock.py`.

## Pós-processamento

1. Executar `/skill00-validator step5` automaticamente.
2. Se validação falhar → reportar erros e sugestões (apontar para `docs/mock_spec.yaml`).
3. Se validação passar → criar checkpoint `.build/checkpoints/step5.json` com `{step, timestamp, files: {path: sha256}, validation: "ok", checks_passed: N, checks_failed: 0}` e exibir `✓ Step 5 → seed.sql validado (<N> entidades, <N> linhas)`.

## Argumento opcional (entidade específica)

$ARGUMENTS — validar apenas a seção da entidade indicada.
