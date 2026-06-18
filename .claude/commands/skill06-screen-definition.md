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
    data_sources:             # entidades do data_model.yaml usadas
      - entity: string
        mock_file: string     # ex.: mock_data/clientes.csv
    components:
      - id: string
        type: filter | grid | modal | form | card | chart | kpi | button | tabs
        label: string
        description: string
        position: top | left | right | bottom | center | inline
        config:
          # específico por tipo (ver abaixo)
    actions:
      - id: string
        label: string
        type: navigate | modal | api_call | download | filter
        target: string
        confirmation: bool

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
