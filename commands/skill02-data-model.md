# Skill 02 — Data Model Generation Skill

Leia `docs/requirements.yaml` e gere o modelo de dados em `docs/data_model.yaml`.

## Instruções

1. Leia APENAS `docs/requirements.yaml`.
2. Identifique todas as entidades listadas na seção `entities`.
3. Para cada entidade, defina campos com tipos, constraints e relacionamentos.
4. Gere `docs/data_model.yaml` com a estrutura abaixo.
5. Se o arquivo já existir, aplique patch incremental.

## Estrutura de Saída

```yaml
entities:
  <nome_entidade>:
    table: string           # nome da tabela SQL
    description: string
    fields:
      - name: string
        type: string        # int, varchar(N), decimal(P,S), datetime, bit, etc.
        nullable: bool
        primary_key: bool
        foreign_key:
          table: string
          field: string
        default: any
        description: string
    indexes:
      - fields: [string]
        unique: bool

relationships:
  - from: string
    to: string
    type: one_to_one | one_to_many | many_to_many
    description: string

enums:
  <nome_enum>:
    values: [string]
    description: string
```

## Regras

- Toda entidade DEVE ter campo `id` como chave primária (int identity ou uniqueidentifier).
- Campos de auditoria obrigatórios: `created_at`, `updated_at`.
- Nomes de tabelas em snake_case.
- Tipos compatíveis com SQL Server e Microsoft Fabric.
- NÃO gere código SQL aqui — apenas o modelo YAML.
- Contexto máximo: **8.000 tokens** de saída (anteriormente 2.000).
- Se exceder 8.000 tokens, dividir em chunks com continuação automática.

## Pós-processamento

1. Executar `/skill00-validator step2` automaticamente
2. Verificar ciclos de dependência em FKs (topological sort)
3. Se validação falhar → reportar erros e sugestões
4. Se validação passar → criar checkpoint e avançar

## Argumento opcional

$ARGUMENTS
