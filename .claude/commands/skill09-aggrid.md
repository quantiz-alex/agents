# Skill 09 — AgGrid Generation Skill

Leia `docs/screens_definition.yaml` e gere o componente de grid para uma página.

## Argumento obrigatório

Nome da página: $ARGUMENTS

Exemplo de uso: `/skill09-aggrid aprovacao`

## Instruções

1. Leia `docs/screens_definition.yaml` — extraia o componente do tipo `grid` da página solicitada.
2. Leia `docs/data_model.yaml` — extraia os campos da entidade correspondente.
3. Gere ou atualize `frontend/pages/<pagina>/<pagina>_components.py` com a função `build_grid()`.
4. Se o arquivo já existir, aplique patch incremental apenas na função `build_grid`.

## Código Gerado

```python
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import html

def build_grid() -> dbc.Card:
    """Retorna o componente AG Grid da página <pagina>."""

    column_defs = [
        {
            "field": "id",
            "headerName": "ID",
            "width": 80,
            "sortable": True,
            "filter": True,
            "pinned": "left",
        },
        {
            "field": "campo",
            "headerName": "Rótulo",
            "flex": 1,
            "sortable": True,
            "filter": True,
            "cellStyle": {"textAlign": "left"},
        },
        # ... demais campos conforme screens_definition e data_model
    ]

    return dbc.Card([
        dbc.CardHeader(html.H5("Título do Grid", className="mb-0")),
        dbc.CardBody([
            dag.AgGrid(
                id="<pagina>-grid",
                columnDefs=column_defs,
                rowData=[],
                defaultColDef={
                    "resizable": True,
                    "sortable": True,
                    "filter": True,
                    "floatingFilter": True,
                },
                dashGridOptions={
                    "pagination": True,
                    "paginationPageSize": 20,
                    "paginationPageSizeSelector": [10, 20, 50, 100],
                    "rowSelection": "multiple",
                    "animateRows": True,
                },
                className="ag-theme-alpine",
                style={"height": "500px"},
                csvExportParams={"fileName": "<pagina>_export.csv"},
            )
        ]),
    ])
```

## Recursos Obrigatórios

- Paginação: `pagination: True` com seletor de tamanho
- Ordenação: `sortable: True` em todas as colunas
- Filtros: `filter: True` com `floatingFilter: True`
- Exportação: botão de exportação CSV (via `csvExportParams`)
- Responsividade: `flex: 1` nas colunas principais, `resizable: True`
- Seleção: `rowSelection: "multiple"` quando a tela tiver ações em lote

## Tipos de Coluna

| Tipo      | Configuração                                              |
| --------- | --------------------------------------------------------- |
| currency  | `valueFormatter: {"function": "d3.format(',.2f')(params.value)"}` |
| date      | `valueFormatter: {"function": "params.value?.split('T')[0]"}` |
| badge     | `cellRenderer: "agCellRendererHtml"` com classe Bootstrap |
| action    | `cellRenderer` com botões edit/view/delete                |

## Restrições

- Usar APENAS `dash_ag_grid` — não usar `dash_table`.
- NÃO conectar ao banco — `rowData` começa vazio e é preenchido via callback.
- Contexto máximo: **8.000 tokens** de saída (anteriormente 2.000).
- **Consultar `design-system.yaml`** para configurações de grid (theme, heights, etc.).

## Pós-processamento

1. Verificar que configurações seguem `design-system.yaml`
2. Verificar que `columnDefs` são válidos
