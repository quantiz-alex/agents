# Skill 07 — Dash Page Generation Skill

Leia `docs/screens_definition.yaml` e gere os 4 arquivos de uma página Dash com layout sidebar + design clean.

## Argumento obrigatório

Nome da página a gerar: $ARGUMENTS

Exemplo de uso: `/skill07-dash-page aprovacao`

## Instruções

1. Leia `docs/screens_definition.yaml` e extraia APENAS a página solicitada.
2. Leia `docs/data_model.yaml` para entender os campos disponíveis.
3. Gere os 4 arquivos da página: `_page.py`, `_components.py`, `_queries.py`, `_callbacks.py`.
4. Se os arquivos já existirem, aplique patch incremental.

---

## Design System Obrigatório

**IMPORTANTE**: Todos os valores de design estão centralizados em `design-system.yaml`.
Consulte esse arquivo para cores, espaçamentos, componentes e convenções de nomenclatura.

### Tokens de cor (referência rápida)

```
Sidebar bg:        #1e293b   (slate-800)
Sidebar active:    #334155   (slate-700)
Sidebar text:      #cbd5e1   (slate-300)
Sidebar highlight: #1045C8   (blue-500)
Page bg:           #f8fafc   (slate-50)
Card bg:           #ffffff
Card border:       #e2e8f0   (slate-200)
Heading:           #1e293b
Body text:         #374151
Muted:             #6b7280
```

### Regras de layout

- O `layout()` retorna `html.Div` com className `"page-wrapper"` — NÃO usa `dbc.Container` como raiz.
- A sidebar é externa ao layout de cada página — gerada em `frontend/components/sidebar.py` e renderizada em `app.py`.
- Cada página só gera o conteúdo interno da área principal.
- Estrutura interna da página:

```
.page-wrapper
  └── .page-header        ← título + breadcrumb
  └── .page-body          ← filtros + conteúdo principal (grids, cards, charts)
```

### Cards e componentes

- Todo bloco de conteúdo fica dentro de `dbc.Card` com `className="shadow-sm border-0 mb-3"`.
- Títulos de card: `dbc.CardHeader` com `className="bg-white border-bottom fw-semibold text-slate"`.
- Filtros: fundo branco, label pequeno, inputs sem border-radius excessivo.
- KPIs: card com borda esquerda colorida (`border-start border-4 border-primary`).
- Grids AG Grid: tema `ag-theme-alpine`, altura `500px`, floatingFilter ativo.
- Gráficos Plotly: `template="plotly_white"`, sem background, `height=300`.
- Badges de status: `dbc.Badge` com cores semânticas (success/warning/danger/secondary).
- Botões: `color="primary"`, sem shadow extra, tamanho padrão.
- Espaçamento: usar `mb-3`, `py-2`, `px-3` do Bootstrap — sem espaços manuais.

---

## Estrutura dos Arquivos Gerados

### `_page.py`

```python
from dash import html, register_page
import dash_bootstrap_components as dbc
from frontend.pages.<pagina>.<pagina>_components import (
    build_filters,
    build_kpis,      # se houver KPIs
    build_grid,      # se houver grid
    build_charts,    # se houver gráficos
)
from frontend.pages.<pagina>.<pagina>_queries import <funcoes_necessarias>

register_page(__name__, path="/<pagina>", title="<title>", name="<name>")


def layout() -> html.Div:
    # Carrega dados iniciais para KPIs e select options
    return html.Div([
        # Cabeçalho da página
        html.Div([
            html.H4("<title>", className="fw-bold mb-0 text-dark"),
            html.Small("<descrição breve>", className="text-muted"),
        ], className="page-header d-flex flex-column mb-3"),

        # Filtros (card compacto)
        build_filters(),

        # KPIs (se a página tiver)
        dbc.Row([...], id="<pagina>-kpis-row"),

        # Conteúdo principal (grid ou charts)
        build_grid(),  # ou build_charts()

    ], className="page-wrapper px-4 py-3", style={"background": "#f8fafc", "minHeight": "100vh"})
```

### `_components.py`

```python
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html


# KPI card com borda lateral colorida
def build_kpi_card(title: str, value: str, color: str = "primary", icon: str = "") -> dbc.Card:
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.P(title, className="text-muted small mb-1 text-uppercase fw-semibold", style={"fontSize": "0.7rem", "letterSpacing": "0.05em"}),
                html.H4(value, className="fw-bold mb-0"),
            ])
        ], className="py-3")
    ], className=f"shadow-sm border-0 border-start border-4 border-{color} mb-3 h-100")


# Painel de filtros compacto
def build_filters(...) -> dbc.Card:
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # inputs de filtro
            ], className="g-2 align-items-end")
        ], className="py-2")
    ], className="shadow-sm border-0 mb-3")


# Grid AG Grid clean
def build_grid() -> dbc.Card:
    column_defs = [...]
    return dbc.Card([
        dbc.CardHeader([
            html.Span("<título>", className="fw-semibold"),
            # botão exportar à direita
        ], className="bg-white border-bottom d-flex justify-content-between align-items-center"),
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
                    "suppressMenu": True,
                },
                dashGridOptions={
                    "pagination": True,
                    "paginationPageSize": 20,
                    "paginationPageSizeSelector": [10, 20, 50, 100],
                    "animateRows": True,
                    "rowHeight": 44,
                    "headerHeight": 44,
                },
                className="ag-theme-alpine",
                style={"height": "500px"},
                csvExportParams={"fileName": "<pagina>.csv"},
            )
        ], className="p-0"),
    ], className="shadow-sm border-0")


# Gráfico clean
def build_chart(...) -> dbc.Card:
    fig = px.bar(...)  # ou line, pie, etc.
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        font=dict(family="system-ui, sans-serif", size=12, color="#374151"),
    )
    return dbc.Card([
        dbc.CardHeader("<título>", className="bg-white border-bottom fw-semibold"),
        dbc.CardBody(dcc.Graph(figure=fig, config={"displayModeBar": False}), className="p-2"),
    ], className="shadow-sm border-0 mb-3")
```

### `_queries.py`

```python
import pandas as pd
from pathlib import Path

DATA_DIR = Path("mock_data")

# Funções de leitura e filtro de mock_data
# NÃO conectar ao banco
```

### `_callbacks.py`

```python
from dash import Input, Output, State, callback
from frontend.pages.<pagina>.<pagina>_queries import <funções>


def register_callbacks() -> None:

    @callback(
        Output("<pagina>-grid", "rowData"),
        Input("<pagina>-btn-filtrar", "n_clicks"),
        State(...),
        prevent_initial_call=False,
    )
    def update_grid(...) -> list[dict]:
        df = get_data(...)
        return df.to_dict("records")
```

---

## Padrões de ID

| Elemento          | Padrão de ID                    |
| ----------------- | ------------------------------- |
| Grid              | `<pagina>-grid`                 |
| Botão filtrar     | `<pagina>-btn-filtrar`          |
| Filtro dropdown   | `<pagina>-filtro-<campo>`       |
| Filtro período    | `<pagina>-filtro-periodo`       |
| Gráfico           | `<pagina>-chart-<tipo>`         |
| Linha de KPIs     | `<pagina>-kpis-row`             |
| Botão de ação     | `<pagina>-btn-<acao>`           |

---

## Autenticação e Avatar

- A sidebar exibe automaticamente o avatar do usuário logado (nome + cargo) no rodapé — gerado via `dcc.Store(id="current-user")`.
- Cada página NÃO precisa verificar autenticação internamente — o guard de rota em `app.py` redireciona para `/login` se `current-user` estiver vazio.
- A página `/login` é um caso especial: não usa sidebar, ocupa a tela inteira com fundo degradê escuro e card centralizado.
- Para exibir nome/cargo do usuário dentro de uma página (ex.: "Olá, Ana"), leia `dcc.Store` via `Input("current-user", "data")` em um callback.

## Branding e Padrão Visual

- O rodapé **"Desenvolvido por / Quantiz Pricing Solution"** é gerado **apenas** em `frontend/components/sidebar.py` — nunca dentro de páginas individuais.
- Todas as páginas compartilham o mesmo padrão visual definido em `docs/design-system.yaml` — leia esse arquivo antes de gerar qualquer componente.
- Nomes de projeto, cores, tipografia e configurações de grid/plotly devem vir **exclusivamente** do `design-system.yaml`, nunca hardcoded na página.
- Esse padrão se aplica a **todos os projetos** — o visual muda apenas via `design-system.yaml`, nunca editando as páginas diretamente.

## Restrições

- NUNCA usar `dbc.Container` como raiz do `layout()` — use `html.Div` com `className="page-wrapper"`.
- NUNCA usar `dbc.Navbar` dentro de páginas — a navbar/sidebar é responsabilidade do `app.py`.
- NUNCA usar inline styles para cores — usar className do Bootstrap ou o style dict apenas para valores do design system.
- NUNCA replicar o footer de branding dentro de páginas — ele existe apenas na sidebar.
- Tipagem Python obrigatória em todas as funções.
- Contexto máximo: **8.000 tokens** de saída por arquivo (anteriormente 2.000).
- Se exceder 8.000 tokens, dividir em chunks com continuação automática.
- **Consultar `design-system.yaml`** para todos os valores de design.

## Pós-processamento

1. Executar `/skill00-validator step7 --page <page>` automaticamente
2. Verificar que arquivos Python são válidos (parse)
3. Verificar que IDs seguem padrão `<page>-<component>`
4. Verificar que design system está aplicado
5. Se validação falhar → reportar erros e sugestões
6. Se validação passar → criar checkpoint parcial e avançar
