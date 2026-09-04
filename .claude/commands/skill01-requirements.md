# Skill 01 — Requirement Extraction Skill

Transforme o conteúdo do `roadmap.md` em requisitos estruturados no arquivo `docs/requirements.yaml`.

## Instruções

1. Leia `roadmap.md` (já fornecido pelo orquestrador ou disponível no projeto).
2. Extraia TODOS os requisitos funcionais e não funcionais.
3. Organize em grupos lógicos: módulos, entidades, regras de negócio, integrações.
4. Gere `docs/requirements.yaml` com a estrutura abaixo.
5. Se `docs/requirements.yaml` já existir, aplique somente o patch incremental — não regere o arquivo inteiro.

## Estrutura de Saída

**O schema autoritativo e completo de `docs/requirements.yaml` (incluindo `demo_context`, `modules[].layout/drilldowns/menu_group/user_goal/kpis[].kind/grid/detail_panel/empty_state/simulation_params/recalc_mode/sidebar_badge` e `entities[].role/demo`) está em `../.claude/agents/data-engineer.md` → Step 1, junto com os fallbacks por `screen_type`.** O resumo abaixo cobre apenas o núcleo; em caso de divergência, o data-engineer prevalece.

```yaml
project:
  name: string
  description: string
  version: string

demo_context: {persona, story, anchors: [string], period_months, credentials: [{role, email}]}

modules:
  - name: string
    slug: string
    description: string
    user_goal: string
    priority: high | medium | low
    screen_type: dashboard | analytics | grid | master_detail | form | report | mixed | simulation | approval_queue
    menu_group: string
    icon: string
    layout: [string]                 # ex: ["kpis:4", "charts:2col", "grid"]
    kpis: [{id, label, kind: comparação|simples, format, better, compare_to}]
    charts: [{id, type, title, x_field, y_field, series_field, description}]
    grid: {entity, columns: [{field, header, format}], row_actions: [string], default_sort: {field, dir}}
    drilldowns: [{source_chart, target, target_field, description}]
    empty_state: string
    filters: [{field, type, options, default, global}]
    features:
      - id: string
        title: string
        description: string
        user_story: "Como <quem>, quero <o quê>, para <por quê>"
        actions: [string]
        acceptance_criteria:
          - string
    access: [{role, permissions}]

entities:
  - name: string
    description: string
    module: string
    role: dimensao | fato | apoio
    fields: [{name, type, nullable, notes}]
    relationships: [string]
    demo: {volume: int, distributions: [{field, spec}], example_row: string}

business_rules:
  - id: string
    description: string
    module: string
    # NOVOS campos opcionais — preencher SOMENTE se o roadmap.md tiver a sub-seção
    # estruturada (Tipo/Fórmula/Variáveis de entrada/Campos de saída). Copiar
    # literalmente, sem reformular — a classificação/normalização final é
    # responsabilidade da skill skill-business-logic (Step 2.7), não desta skill.
    logic_type: validation | derived_field | interactive_formula | workflow_rule | null
    formula_hint: string | null       # cópia literal da linha "Fórmula:" do roadmap, se existir
    variables_hint: [string] | null   # cópia literal de "Variáveis de entrada:", se existir

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
- Se um campo não estiver no roadmap, aplique o fallback documentado no data-engineer Step 1 (ex.: `layout` por `screen_type`, `demo.volume` por `role`) e **registre o fallback aplicado** em `validation_reports/step1_fallbacks.yaml` — nunca invente conteúdo de negócio (KPIs, regras, entidades).
- `distributions[].spec` é copiado **literalmente** do roadmap (ex.: `"enum(Ativo:92%, Inativo:8%)"`); quem interpreta é o gerador de mock (Step 4).
- Se o roadmap tiver a sub-seção estruturada de uma regra (Tipo/Fórmula/Variáveis de entrada/Campos de saída), copie literalmente para `logic_type`/`formula_hint`/`variables_hint` — NÃO reformule nem infira fórmula a partir de texto livre aqui; isso é responsabilidade da skill `skill-business-logic` (Step 2.7).
- Contexto máximo: **8.000 tokens** de saída (anteriormente 2.000).
- Se exceder 8.000 tokens, dividir em chunks com continuação automática.

## Pós-processamento

1. Executar `/skill00-validator step1` automaticamente
2. Se validação falhar → reportar erros e sugestões
3. Se validação passar → criar checkpoint e avançar

## Argumento opcional

$ARGUMENTS
