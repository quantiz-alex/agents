# Skill 06 — Screen Definition Skill

Leia `docs/requirements.yaml` e gere a definição de telas em `docs/screens_definition.yaml`.

## Instruções

1. Leia APENAS `docs/requirements.yaml`.
2. Para cada módulo/feature, defina a(s) tela(s) correspondentes.
3. Especifique os componentes de cada tela com seus dados e comportamentos.
4. Gere `docs/screens_definition.yaml` com a estrutura abaixo.
5. Se o arquivo já existir, aplique patch incremental.

## Estrutura de Saída

```yaml
pages:
  <nome_pagina>:
    title: string
    route: string             # ex.: /aprovacao
    module: string
    description: string
    layout: sidebar | topnav | fullscreen
    screen_type: dashboard | grid | form | report | mixed | simulation | approval_queue
    # simulation    → tela com painel de parâmetros + resultado calculado + cenários salvos
    # approval_queue → fila dedicada para supervisor aprovar/rejeitar itens pendentes
    data_sources:             # entidades do data_model.yaml usadas
      - entity: string
        mock_file: string     # ex.: mock_data/clientes.csv
    has_simulation:     bool  # true → gerar bloco de simulação (skill-simulation)
    has_approval_flow:  bool  # true → gerar fluxo de aprovação (skill-approval-flow)
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

| screen_type      | Skills extras invocadas pelo frontend-builder       |
|------------------|-----------------------------------------------------|
| `dashboard`      | (padrão — nenhuma extra)                            |
| `grid`           | (padrão — nenhuma extra)                            |
| `form`           | (padrão — nenhuma extra)                            |
| `report`         | (padrão — nenhuma extra)                            |
| `mixed`          | (padrão — nenhuma extra)                            |
| `simulation`     | `skill-simulation.md` — gera painel + resultado + cenários salvos |
| `approval_queue` | `skill-approval-flow.md` — gera fila + modais + callbacks de aprovação |

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
      type: text | number | date | currency | badge | action
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

```yaml
config:
  params:           # campos de parâmetro de entrada
    - name: string
      type: number | select | date
      label: string
      unit: string  # ex.: "%", "R$", "un."
      min: number
      max: number
      required: bool
  result_kpis:      # KPIs calculados a exibir no resultado
    - label: string
      source_field: string   # campo do resultado calculado
      format: number | currency | percent
  comparativo_columns:  # colunas da tabela comparativa
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
2. Verificar que todas as rotas são únicas
3. Verificar que data_sources referenciam entidades existentes
4. Se validação falhar → reportar erros e sugestões
5. Se validação passar → criar checkpoint e avançar

## Argumento opcional (módulo específico)

$ARGUMENTS
