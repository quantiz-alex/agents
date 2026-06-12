# Skill 01 — Requirement Extraction Skill

Transforme o conteúdo do `roadmap.md` em requisitos estruturados no arquivo `docs/requirements.yaml`.

## Instruções

1. Leia `roadmap.md` (já fornecido pelo orquestrador ou disponível no projeto).
2. Extraia TODOS os requisitos funcionais e não funcionais.
3. Organize em grupos lógicos: módulos, entidades, regras de negócio, integrações.
4. Gere `docs/requirements.yaml` com a estrutura abaixo.
5. Se `docs/requirements.yaml` já existir, aplique somente o patch incremental — não regere o arquivo inteiro.

## Estrutura de Saída

```yaml
project:
  name: string
  description: string
  version: string

modules:
  - name: string
    description: string
    priority: high | medium | low
    features:
      - id: string
        title: string
        description: string
        user_story: "Como <quem>, quero <o quê>, para <por quê>"
        acceptance_criteria:
          - string

entities:
  - name: string
    description: string
    module: string

business_rules:
  - id: string
    description: string
    module: string

integrations:
  - name: string
    type: database | api | file
    description: string

non_functional:
  performance: string
  security: string
  scalability: string
```

## Restrições

- NÃO leia nenhum outro documento além de `roadmap.md`.
- NÃO gere código — apenas o YAML estruturado.
- NÃO invente requisitos — extraia somente o que está explícito.
- Se um campo não estiver no roadmap, deixe como `null` ou omita.
- Contexto máximo: **8.000 tokens** de saída (anteriormente 2.000).
- Se exceder 8.000 tokens, dividir em chunks com continuação automática.

## Pós-processamento

1. Executar `/skill00-validator step1` automaticamente
2. Se validação falhar → reportar erros e sugestões
3. Se validação passar → criar checkpoint e avançar

## Argumento opcional

$ARGUMENTS
