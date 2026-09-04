# Skill 07 — Dash Page Generation Skill (v4)

Leia `docs/screens_definition.yaml` e gere os 4 arquivos de UMA página Dash **exclusivamente com os componentes de `frontend/components/ui_components.py` e `frontend/components/charts.py`**. Nenhum card, KPI, grid ou gráfico é montado "na mão".

## Argumento obrigatório

Nome da página a gerar: $ARGUMENTS — ex.: `/skill07-dash-page simulacao`

## Instruções

1. Ler `docs/screens_definition.yaml` → apenas a página solicitada (`pages.<pagina>`), `docs/design-system.yaml`, `docs/business_logic.yaml` (regras vinculadas ao módulo) e `docs/data_model.yaml` (campos reais).
2. Gerar `frontend/pages/<pagina>/{__init__,<pagina>_queries,<pagina>_components,<pagina>_page,<pagina>_callbacks}.py`. Se existirem, patch incremental.
3. Traduzir `pages.<pagina>.layout` (DSL) em faixas de componentes — ver tabela abaixo.
4. Aplicar as skills especializadas conforme `screen_type`/flags (`skill-simulation.md`, `skill-approval-flow.md`) e os padrões de `skill08-dash-callback.md` conforme `actions`, `drilldowns`, `recalc_mode`, `row_actions`.
5. Validar com `python -m py_compile` e `python -c "import frontend.pages.<pagina>.<pagina>_page"` (a partir da raiz do projeto).

---

## Design System (referência rápida — fonte: `design-system.yaml` + `theme.css`)

| Elemento | Como fazer |
|---|---|
| Raiz da página | `app_shell(...)` / `app_shell_with_workflow(...)` — nunca `dbc.Container`, nunca `html.Div` manual |
| Sidebar | externa (`app.py`), **branca**, 240px — a página não a renderiza |
| Cabeçalho | vem do `app_shell`: breadcrumb `[menu_group, title]`, ícone, título, `subtitle = user_goal`, `meta=[stat_pill("dados até dd/mm/aaaa")]` |
| KPI comparação | `kpi_card(label, atual, simulado, delta_pct, better, compare_label)` |
| KPI simples | `kpi_simple(label, value, delta_pct=None, trend=None, hint=None)` — nunca passar o mesmo valor 2x no `kpi_card` |
| Linha de KPIs | `kpi_row(cards, row_id="<pagina>-kpis-row")` |
| Card | `card(title, body, right=None, icon_key=None)` |
| Grid | `data_table(df, "<pagina>-grid", column_types={...}, headers={...}, row_actions=[...], default_sort=(...), hide_cols=["id"])` |
| Gráfico | helper de `charts.py` dentro de `dcc.Graph(id="<pagina>-chart-<id>", figure=..., config={"displayModeBar": False})` envolvido em `loading()` |
| Filtros | `filter_card([filter_select(...), filter_date_range(...), filter_text(...)], "<pagina>-btn-filtrar", right=chips_row("<pagina>-chips"))` |
| Parâmetros de simulação | `param_slider(...)` para variáveis com min/max; `filter_select` para categóricas |
| Vazio | `empty_state(title=<empty_state do YAML>, hint=...)` no lugar do grid/gráfico quando `df.empty` |
| Feedback | `toast("<pagina>-toast")` no layout + `notify()` no callback; `confirm_modal()` antes de ações destrutivas/decisões |
| Detalhe | `detail_offcanvas("<pagina>-detail")` |
| Cores | nunca hex em páginas — classes `text-primary`, `status_badge()`, tokens `COLORS` |
| IDs | `<pagina>-<componente>` (`-grid`, `-btn-filtrar`, `-filtro-<campo>`, `-chart-<id>`, `-kpis-row`, `-btn-<acao>`, `-param-<var>`, `-detail`, `-toast`, `-drill`, `-chips`) |
| Tipagem | obrigatória em todas as funções |

---

## DSL de layout → componentes

`pages.<pagina>.layout` é uma lista de faixas, de cima para baixo. Filtros (`filter_card`) vêm SEMPRE antes da primeira faixa (exceto em `simulation`, onde `params` faz esse papel).

| Token | Renderização em `_page.py` |
|---|---|
| `kpis:N` | `kpi_row([...N cards...], row_id="<pagina>-kpis-row")` — cards de `kpis[]` (kind → `kpi_card`/`kpi_simple`) |
| `charts:1col` | `card(chart.title, loading(dcc.Graph(...)))` ocupando `dbc.Col(md=12)` |
| `charts:2col` | `dbc.Row([dbc.Col(card(...), md=6), dbc.Col(card(...), md=6)], className="g-3")` consumindo os próximos 2 `charts[]` |
| `charts:3col` | idem com `md=4` e 3 gráficos (o último pode ficar `md=12` se sobrar 1) |
| `grid` | `card(grid.title or "Detalhamento", [quick_filter_input + botão exportar à direita], body=loading(html.Div(data_table(...), id="<pagina>-grid-wrapper")))` |
| `split:A/B` | `dbc.Row([dbc.Col(<próximo chart>, md=A), dbc.Col(<próximo chart ou grid>, md=B)])` |
| `tabs:A,B` | `dbc.Tabs([dbc.Tab(<conteúdo>, label="A"), ...])` — cada aba consome as faixas seguintes até o próximo `tabs`/fim |
| `params` | painel de parâmetros da simulação (`skill-simulation.md`): `card("Parâmetros do cenário", dbc.Row([param_slider(...), filter_select(...)]), right=dbc.Switch(id="<pagina>-auto", value=True, label="Ao vivo"))` |
| `detail` | `detail_offcanvas("<pagina>-detail", title=<entidade>)` declarado no layout (fora do fluxo visual) |

Gráficos são consumidos na ordem de `charts[]`. Se sobrarem gráficos sem faixa, acrescentar `charts:2col` ao final. Se faltar gráfico para uma faixa, a faixa é omitida (nunca gerar card vazio).

### Mapeamento `charts[].type` → helper

| type | helper (`charts.py`) | dado esperado em `_queries.py` |
|---|---|---|
| `bar` (horizontal se ranking) | `bar_ranking` / `bar_vertical` | labels, values |
| `line` | `line_chart` / `multi_line_chart` (com `series_field`) | x, y ou {série: y} |
| `area` | `area_chart` | x, y |
| `pie` / `donut` | `donut` (≤5 categorias — senão `bar_ranking`) | labels, values |
| `scatter` | `scatter_chart` | x, y |
| `histogram` | `histogram` | values |
| `heatmap` | `heatmap` | x_labels, y_labels, matriz (pivot) |
| `treemap` | `treemap` | labels, parents, values (2 níveis) |
| `combo` | `combo_bar_line` | x, bars, line |
| `stacked` | `stacked_bars` | x, {série: values} |
| `grouped` / atual × simulado | `grouped_bars` | x, {"Atual": [...], "Simulado": [...]} |
| `funnel` | `funnel` | stages, values |
| `gauge` | `gauge` | value, target |
| `sparkline` | `sparkline` (dentro de `kpi_simple(trend=...)` ou detalhe) | values |
| `waterfall` | `waterfall_chart` | labels, values (ponte) |
| `elasticity_curve` | `elasticity_curve` | preco_range, volume_estimado, preco_atual, preco_simulado |
| `scenario_comparison` | `scenario_comparison_chart` | lista de cenários |

---

## Estrutura dos 4 arquivos

### `_queries.py` — dados e cálculo (pandas, nunca banco direto)

```python
from __future__ import annotations
from pathlib import Path
import pandas as pd
from frontend.api_client import use_api, api_get           # modo API opcional (USE_API=true)

DATA_DIR = Path(__file__).resolve().parents[3] / "mock_data"

def carregar_<entidade>(periodo: tuple[str, str] | None = None, <filtro>: str | None = None, **drill: str) -> pd.DataFrame:
    if use_api():
        return pd.DataFrame(api_get("/<entidades>", params={...}))
    df = pd.read_csv(DATA_DIR / "<entidade>.csv", parse_dates=[<colunas de data>])
    # JOINs com dimensões para trazer nomes legíveis (nunca exibir só FK numérica)
    dim = pd.read_csv(DATA_DIR / "<dimensao>.csv")[["id", "nome"]].rename(columns={"id": "<dimensao>_id", "nome": "<dimensao>"})
    df = df.merge(dim, on="<dimensao>_id", how="left")
    # Campos derivados (business_logic.yaml → derived_field) SEMPRE calculados aqui
    df["margem_pct"] = (df["receita"] - df["custo_total"]) / df["receita"] * 100
    # filtros + drill-down (kwargs opcionais)
    for campo, valor in {**{"<filtro>": <filtro>}, **drill}.items():
        if valor not in (None, ""):
            df = df[df[campo] == valor]
    return df

def calcular_kpis(df: pd.DataFrame, df_anterior: pd.DataFrame) -> dict: ...   # retorna valores numéricos; formatação fica em _components
def agregar_<chart_id>(df: pd.DataFrame) -> pd.DataFrame: ...                 # uma função por gráfico
def listar_<dimensao>() -> list[str]: ...                                      # opções dos selects
def periodo_dados(df: pd.DataFrame) -> str: ...                                # "dados até dd/mm/aaaa" para o meta do header
```

- KPIs de `kind: comparação` precisam de baseline: `compare_to` (`mes_anterior`, `periodo_anterior`, `cenario_atual`) → `_queries.py` calcula o DataFrame de referência.
- Performance: vetorizado; `groupby`/`pivot_table`; nunca `iterrows`.

### `_components.py` — builders (recebem DataFrame/dict, devolvem componentes da biblioteca)

`build_filtros(opcoes) -> dbc.Card` · `build_kpis(kpis: dict) -> list` (usa `kpi_card` para comparação e `kpi_simple` para simples, com `format_*`) · `build_chart_<id>(df) -> dcc.Graph | html.Div` (retorna `empty_state(compact=True)` se `df.empty`) · `build_grid(df) -> dag.AgGrid | html.Div` (com `column_types` de `grid.columns[].format`, `row_actions` de `grid.row_actions`, `default_sort`) · `build_detalhe(row, relacionados) -> list` (Padrão 10) · modais/`confirm_modal` conforme `actions`.

### `_page.py`

```python
import dash
from dash import dcc, html
from frontend.components.ui_components import app_shell_with_workflow, toast, chips_row, detail_offcanvas, stat_pill, button
from frontend.pages.<pagina>.<pagina>_queries import ...
from frontend.pages.<pagina>.<pagina>_components import ...

dash.register_page(__name__, path="/<pagina>", title="<title>", name="<title>")

def layout() -> html.Div:
    df = carregar_<entidade>(<defaults dos filtros>)                  # tela NUNCA abre vazia
    conteudo = [
        build_filtros(...),
        # ...faixas conforme layout DSL...
        dcc.Store(id="<pagina>-drill", storage_type="memory"),
        dcc.Download(id="<pagina>-download"),
        toast("<pagina>-toast"),
        detail_offcanvas("<pagina>-detail", title="<Entidade>"),     # se detalhar/detail_panel
        <confirm_modal(...)>,                                          # se ações destrutivas/decisão
    ]
    return app_shell_with_workflow(
        active_key="<pagina>", icon_key="<icon>", title="<title>", subtitle="<user_goal>",
        breadcrumb_items=["<menu_group>", "<title>"],
        meta=[stat_pill(periodo_dados(df), "info", "calendar3")],
        content=conteudo,
        actions=[button("Exportar", primary=False, icon_key="download", id="<pagina>-btn-exportar"), <ações primárias da tela>],
        workflow_context=None,   # preenchido via callback quando a tela participa de workflow
    )
```

### `_callbacks.py`

`register_callbacks()` com os padrões de `skill08-dash-callback.md` aplicáveis: 1 (filtrar; zera drill), 6 (export), 7 (toast via `notify`), 8 (drill-down), 9 ou 2 (simulação), 3/4 (aprovação), 10 (detalhe), 11 (roles), 13 (busca rápida).

---

## Regras

- **Tela nunca abre vazia**: `layout()` carrega os dados com filtros padrão; se ainda assim `df.empty`, mostra `empty_state` com o texto de `pages.<pagina>.empty_state`.
- **Nomes legíveis**: grids mostram `fornecedor`, não `fornecedor_id` (JOIN em `_queries.py`); `hide_cols=["id", "*_id"]`.
- **Formatos**: toda coluna monetária `currency`, percentual `percent`/`pct_delta`, data `date`, status `badge` — via `column_types`; nunca formatar no pandas para string.
- **Comparação onde há baseline, simples onde não há** — nunca `kpi_card(x, x, 0)`.
- **Drill-down declarado é drill-down implementado** (Padrão 8) — não deixar `drilldowns[]` sem callback.
- **Loading** em tudo que um callback atualiza; **toast** em toda ação; **confirm_modal** em toda ação irreversível ou decisão.
- Sem `dbc.Container` raiz, sem `dbc.Navbar`, sem hex solto, sem `html.Style`, sem CSS/JS custom.
- Rodapé "Desenvolvido por / Quantiz" só na sidebar.
- Contexto máximo **8.000 tokens** por arquivo; dividir em chunks se necessário.

## Pós-processamento

1. `python -m py_compile` nos 4 arquivos; `python -c "import frontend.pages.<pagina>.<pagina>_callbacks"`.
2. Conferir que todo `id` usado em `_callbacks.py` existe em `_page.py`/`_components.py` (grep).
3. Conferir que cada `charts[]`, `kpis[]`, `drilldowns[]`, `row_actions[]` do YAML tem contraparte no código.
4. `/skill00-validator step7 --page <pagina>`; checkpoint parcial.
