# Skill 06 — Screen Definition Skill

Leia `docs/requirements.yaml` e `docs/business_logic.yaml`, e gere a definição de telas em `docs/screens_definition.yaml`.

**Este é o schema autoritativo de `screens_definition.yaml`** — `frontend-builder.md` Step 6 é apenas um resumo operacional deste arquivo; em caso de divergência, esta skill prevalece.

## Instruções

Para módulos de arquitetura com impacto em outras telas, incluir `scenario: {key, role: editor|consumer, default_view: draft|applied, scope_fields: [...]}` em cada página relevante, preservando dependências declaradas no roadmap. O editor inclui comparativo inline e ações simulate/apply/discard; reset pertence ao shell. Gerar dependências conforme `skill-demo-scenario.md`; não inferir fórmula apenas porque páginas compartilham entidade.

Assistente: preservar por página os campos/IDs de seleção, filtros e scenario.key para o contexto do assistente global. Catálogo é gerado depois deste YAML conforme `skill-pricing-assistant.md`; perguntas específicas derivam do user_goal, funcionalidades e regras. Não criar uma cópia de chat em cada página.

1. Leia `docs/requirements.yaml` e `docs/business_logic.yaml` (se este último não existir, trate como "nenhuma regra classificada" — ver passo 6).
2. Para cada módulo/feature, defina a(s) tela(s) correspondentes.
3. Especifique os componentes de cada tela com seus dados e comportamentos.
4. Gere `docs/screens_definition.yaml` com a estrutura abaixo.
5. Se o arquivo já existir, aplique patch incremental.
6. **Decisão de `screen_type`/`has_simulation`/`has_approval_flow` a partir de `business_logic.yaml`, não de inferência sobre texto livre:**
   - `screen_type: simulation` (ou `has_simulation: true`) só quando existir ≥1 regra com `logic_type: interactive_formula` vinculada ao módulo daquela tela. Se o roadmap descrever uma "simulação" mas nenhuma regra `interactive_formula` foi extraída (`business_logic.yaml` ausente, ou todas as regras do módulo ficaram `parsed: false`), NÃO atribua `screen_type: simulation` — use `screen_type: mixed` e registre um aviso: "módulo descreve simulação mas nenhuma fórmula pôde ser extraída — revisar `business_rules` no roadmap".
   - `has_approval_flow: true` quando existir ≥1 regra `logic_type: workflow_rule` com `workflow.trigger_action` em `submit_approval|approve|reject` vinculada ao módulo.
   - Colunas de grid/report cujo valor vem de uma regra `logic_type: derived_field` usam `column.type: computed` (ver `skill09-aggrid.md`) em vez de assumir que o campo já existe pré-computado em `data_model.yaml`/mock.

## Estrutura de Saída

**Copiar de `docs/requirements.yaml → modules[]` (Step 1) sem reinterpretar:** `user_goal`, `menu_group`, `icon`, `layout`, `kpis`, `charts`, `grid`, `drilldowns`, `empty_state`, `filters`, `recalc_mode`, `sidebar_badge`, `detail_panel`. Esta skill acrescenta o que depende de `business_logic.yaml`/`data_model.yaml` (flags, `simulation_panel`, `approval_bar`, `data_sources`, `mock_file`, `computed` columns, `access`).

```yaml
pages:
  <nome_pagina>:              # slug kebab-case = rota sem barra = prefixo dos IDs
    title: string
    route: string             # ex.: /aprovacao — única
    module: string
    description: string
    user_goal: string         # subtítulo da tela ("Como <role>, quero ... para ...")
    menu_group: string        # grupo na sidebar (ordem de aparição = ordem no roadmap)
    icon: string              # Bootstrap Icons sem "bi-"
    screen_type: dashboard | analytics | grid | master_detail | form | report | mixed | simulation | approval_queue
    # analytics      → filtros globais + 4–10 gráficos com drill-down
    # master_detail  → grid + detail_offcanvas
    # simulation     → painel de parâmetros + resultado calculado + cenários salvos
    # approval_queue → fila dedicada para supervisor aprovar/rejeitar itens pendentes
    layout: [string]          # DSL de faixas: kpis:N | charts:1col|2col|3col | grid | split:A/B | tabs:A,B | params | detail (ver skill07)
    recalc_mode: live | button        # simulation
    sidebar_badge: string | null      # approval_queue — expressão pandas de contagem (ex.: "status == 'Pendente Aprovação'")
    empty_state: string               # texto do estado vazio
    detail_panel: string | null       # master_detail/approval_queue — o que mostrar no offcanvas
    access: [{role: string, permissions: full | [string]}]   # de requirements.yaml — usado por app.py (_ROUTE_ROLES), sidebar e Padrão 11
    data_sources:             # entidades do data_model.yaml usadas
      - entity: string
        mock_file: string     # ex.: mock_data/clientes.csv
    has_simulation:     bool  # true → gerar bloco de simulação (skill-simulation)
    has_approval_flow:  bool  # true → gerar fluxo de aprovação (skill-approval-flow)

    kpis:
      - id: string                  # <pagina>-kpi-<slug>
        label: string
        kind: comparação | simples  # comparação → kpi_card (precisa de compare_to); simples → kpi_simple
        metric: string              # expressão/descrição do cálculo (campo real do data_model)
        format: currency | percent | number | text
        better: up | down | neutral
        compare_to: mes_anterior | periodo_anterior | cenario_atual | meta | null
        trend: bool                 # simples → sparkline dos últimos 12 períodos
    charts:
      - id: string                  # usado no dcc.Graph: <pagina>-chart-<id>
        type: bar | line | area | pie | donut | scatter | histogram | heatmap | treemap | combo | stacked | grouped | funnel | gauge | sparkline | waterfall | elasticity_curve | scenario_comparison
        title: string
        entity: string
        x_field: string
        y_field: string
        series_field: string | null # múltiplas séries / segunda dimensão (heatmap y, treemap nível 2)
        agg: sum | mean | count | weighted_mean
        top_n: int | null
        orientation: h | v          # bar
    grid:
      entity: string
      title: string
      columns:
        - field: string
          header: string
          format: text | currency | currency0 | number | decimal | percent | pct_delta | date | datetime | bool | badge | computed
          compute_from: string      # OBRIGATÓRIO se format: computed — id da regra derived_field em business_logic.yaml
      joins: [{entity: string, on: string, bring: [string]}]   # dimensões para trocar FK por nome legível
      row_actions: [detalhar | editar | excluir | desativar | approve | reject | duplicar]
      default_sort: {field: string, dir: asc | desc}
      selectable: bool              # checkbox (aprovação em lote)
    drilldowns:
      - source_chart: string        # charts[].id
        target: grid | <charts[].id>
        target_field: string        # campo do grid/gráfico alvo filtrado pelo valor clicado
        description: string
    
    # NOVO: Workflow e navegação contextual
    workflow:
      belongs_to: [string]    # IDs dos workflows que incluem esta tela
      step_id: string         # ID do step neste workflow
      receives_context: [string]  # campos recebidos do step anterior
      provides_context: [string]  # campos fornecidos para próximo step
    components:
      - id: string
        type: filter | grid | modal | form | card | chart | kpi | button | tabs | simulation_panel | approval_bar
        label: string
        description: string
        position: top | left | right | bottom | center | inline
        config:
          # específico por tipo (ver abaixo)
    actions:
      - id: string
        label: string
        type: navigate | modal | api_call | download | filter | simulate | submit_approval | approve | reject
        # simulate         → btn-simular → executa cálculo + exibe resultado (skill-simulation)
        # submit_approval  → btn-enviar-aprovacao → Padrão 3 de skill08
        # approve          → btn-aprovar → Padrão 4 de skill08 (supervisor/admin)
        # reject           → btn-rejeitar → Padrão 4 de skill08 (supervisor/admin)
        target: string
        confirmation: bool    # true → modal de confirmação antes da ação
        roles: [string]       # roles que enxergam este botão; omitir = todos

filters:
  <nome_pagina>:
    - id: string
      label: string
      type: dropdown | date_range | text | multiselect | number_range
      entity_field: string    # campo do data_model.yaml
      placeholder: string
      default: any
      required: bool
```

## Mapeamento screen_type → skills invocadas

| screen_type      | Skills extras invocadas pelo frontend-builder       | Padrões skill08 implícitos |
|------------------|-----------------------------------------------------|----------------------------|
| `dashboard`      | (padrão)                                            | 1, 6, 7 (+8 se drilldowns) |
| `analytics`      | (padrão) — filtros `global: true` alimentam todos os gráficos | 1, 6, 7, 8 |
| `grid`           | (padrão)                                            | 1, 5/10, 6, 7, 11, 13 |
| `master_detail`  | (padrão) — `detail` no layout                       | 1, 10, 11, 13 |
| `form`           | (padrão)                                            | 5, 7 |
| `report`         | (padrão)                                            | 1, 6, 7 |
| `mixed`          | (padrão)                                            | conforme actions |
| `simulation`     | `skill-simulation.md` — gera painel + resultado + cenários salvos | 9 (live) ou 2 (button), 3, 7 |
| `approval_queue` | `skill-approval-flow.md` — gera fila + modais + callbacks de aprovação | 4, 10, 11, 12 |

Se `has_simulation: true` (em qualquer screen_type), também invoca `skill-simulation.md`.
Se `has_approval_flow: true` (em qualquer screen_type), também invoca `skill-approval-flow.md`.

---

## Config por Tipo de Componente

### grid
```yaml
config:
  entity: string
  columns:
    - field: string
      header: string
      type: text | number | date | currency | badge | action | computed
      compute_from: string  # OBRIGATÓRIO se type: computed — id da regra logic_type:derived_field em business_logic.yaml
      sortable: bool
      filterable: bool
      width: int
  pagination: bool
  export_excel: bool
  row_actions: [edit, view, delete]
```

### chart
```yaml
config:
  chart_type: bar | line | pie | scatter | heatmap | kpi
  entity: string
  x_field: string
  y_field: string
  group_by: string
  title: string
```

### form
```yaml
config:
  entity: string
  fields:
    - name: string
      type: text | number | date | select | textarea | checkbox
      label: string
      required: bool
  submit_action: string
```

### simulation_panel

**`params`, `result_kpis` e `comparativo_columns` vêm diretamente da regra `logic_type: interactive_formula` vinculada (em `docs/business_logic.yaml`) — nunca invente nomes de parâmetro genéricos (`margem_desejada`/`desconto_maximo`) quando a regra real do roadmap tiver outras variáveis.**

```yaml
config:
  business_logic_rule_id: string  # id da regra em business_logic.yaml que esta tela implementa
  params:           # 1:1 com formula.variables[] onde interactive: true
    - name: string        # = variables[].name
      type: number | select | date
      label: string
      unit: string  # = variables[].unit — ex.: "%", "R$", "un."
      min: number   # = variables[].min
      max: number   # = variables[].max
      required: bool
  result_kpis:      # 1:1 com formula.output_fields[]
    - label: string
      source_field: string   # = output_fields[].name
      format: number | currency | percent
  comparativo_columns:  # colunas da tabela comparativa — inclui ao menos os output_fields
    - field: string
      header: string
      type: text | number | currency | percent | delta
  allow_save_scenario: bool   # exibe btn "Salvar Cenário"
  allow_submit_approval: bool # exibe btn "Enviar para Aprovação" após salvar
```

### approval_bar

```yaml
config:
  actions_analista:    [submit_approval]
  actions_supervisor:  [approve, reject]
  require_comment_on_reject: bool   # padrão: true
  require_comment_on_approve: bool  # padrão: false
  status_field: string              # campo de status na entidade (padrão: "status")
  status_values:
    pending:  "Pendente Aprovação"
    approved: "Aprovado"
    rejected: "Rejeitado"
    draft:    "Rascunho"
```

---

## Restrições

- NÃO gere código Python.
- Uma tela = uma entrada em `pages`.
- Componentes devem referenciar entidades reais do `data_model.yaml`.
- Contexto máximo: **8.000 tokens** de saída (anteriormente 2.000).
- Se exceder 8.000 tokens, dividir em chunks com continuação automática.

## Pós-processamento

1. Executar `/skill00-validator step6` automaticamente
2. Verificar que todas as rotas são únicas; `screen_type`/`charts[].type` nas listas canônicas do validador
3. Verificar que data_sources referenciam entidades existentes; `grid.columns[].field`, `charts[].x_field/y_field`, `drilldowns[].target_field` existem em `data_model.yaml` (ou em `joins[].bring`, ou são `computed`)
3.1. Verificar que `layout` consome todos os `charts[]` e que `kpis[]` com `kind: comparação` têm `compare_to`
4. **NOVO:** Invocar `skill-workflow-definition` para gerar `docs/workflows.yaml` baseado nas telas definidas
5. **NOVO:** Atualizar `screens_definition.yaml` com campo `workflow` em cada página (mapeamento reverso de `workflows.yaml`)
6. Se validação falhar → reportar erros e sugestões
7. Se validação passar → criar checkpoint e avançar

## Argumento opcional (módulo específico)

$ARGUMENTS
