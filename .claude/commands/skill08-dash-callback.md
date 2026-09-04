# Skill 08 — Dash Callback Generation Skill

Leia `docs/screens_definition.yaml` e gere os callbacks de uma página Dash.

## Argumento obrigatório

Nome da página a gerar: $ARGUMENTS

Exemplo de uso: `/skill08-dash-callback aprovacao`

## Instruções

1. Leia `docs/screens_definition.yaml` — extraia APENAS a página solicitada.
2. Leia `docs/data_model.yaml` para saber os campos disponíveis.
3. Identifique os `actions` da página para determinar quais padrões de callback aplicar.
4. Gere APENAS `frontend/pages/<pagina>/<pagina>_callbacks.py`.
5. Se o arquivo já existir, aplique patch incremental.

---

## Catálogo de Padrões

Cada página pode ter um ou mais padrões combinados. Identifique pelos `actions.type` definidos em `screens_definition.yaml`:

| action type            | Padrão a aplicar                        |
|------------------------|-----------------------------------------|
| `filter`               | Padrão 1 — Filtrar grid                 |
| `simulate`             | Padrão 2 — Simular cenário              |
| `submit_approval`      | Padrão 3 — Enviar para aprovação        |
| `approve`              | Padrão 4 — Aprovar com comentário       |
| `reject`               | Padrão 4 — Rejeitar com comentário      |
| `modal` / row action   | Padrão 5 — Row action → modal           |
| `download`             | Padrão 6 — Export Excel                 |
| qualquer ação          | Padrão 7 — Toast de feedback            |
| `drilldowns[]` na tela | Padrão 8 — Drill-down gráfico → grid    |
| `recalc_mode: live`    | Padrão 9 — Recálculo ao vivo (sliders)  |
| `detalhar` / `detail_panel` | Padrão 10 — Detalhe em offcanvas   |
| `actions[].roles` definido | Padrão 11 — UI role-aware           |
| `sidebar_badge` (app.py) | Padrão 12 — Contador de pendências     |
| `quick_filter_input`   | Padrão 13 — Busca rápida no grid        |

---

## Padrão 1 — Filtrar Grid

Aplicar sempre que a página tiver filtros. `prevent_initial_call=False` para carregar dados na abertura.

```python
@callback(
    Output("<pagina>-grid", "rowData"),
    Output("<pagina>-kpis-row", "children"),   # incluir apenas se a página tiver KPIs
    Input("<pagina>-btn-filtrar", "n_clicks"),
    State("<pagina>-filtro-<campo1>", "value"),
    State("<pagina>-filtro-<campo2>", "value"),
    # ... demais filtros
    prevent_initial_call=False,
)
def update_grid(n_clicks: int, filtro1, filtro2, ...) -> tuple:
    df = get_<entidade>_data(filtro1=filtro1, filtro2=filtro2)
    row_data = df.to_dict("records")
    kpis = build_kpis(df)   # retorna html.Div com os cards de KPI
    return row_data, kpis
```

---

## Padrão 2 — Simular Cenário

Aplicar quando `actions` contiver `type: simulate`. O cálculo fica em `_queries.py` — o callback apenas orquestra. O resultado é exibido em uma seção inicialmente oculta (`display: none`) que se torna visível após a simulação.

**A lista de `State(...)` do callback NÃO é genérica** (`param1`, `param2` abaixo são só ilustrativos) — gerar um `State("<pagina>-param-<name>", "value")` para CADA `formula.variables[]` com `interactive: true` da regra `logic_type: interactive_formula` vinculada em `docs/business_logic.yaml` (a mesma regra referenciada em `simulation_panel.config.business_logic_rule_id` de `screens_definition.yaml`). O corpo do callback chama `calcular_simulacao()` de `_queries.py` passando exatamente esses parâmetros pelo nome — ver `skill-simulation.md`.

```python
from dash import Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
from dash import html
import pandas as pd
from frontend.pages.<pagina>.<pagina>_queries import calcular_simulacao

@callback(
    Output("<pagina>-resultado-simulacao", "children"),
    Output("<pagina>-resultado-simulacao", "style"),
    Output("<pagina>-btn-simular", "disabled"),
    Output("<pagina>-toast", "is_open"),
    Output("<pagina>-toast", "children"),
    Output("<pagina>-toast", "color"),
    Input("<pagina>-btn-simular", "n_clicks"),
    State("<pagina>-param-<campo1>", "value"),
    State("<pagina>-param-<campo2>", "value"),
    # ... demais parâmetros do cenário
    prevent_initial_call=True,
)
def executar_simulacao(n_clicks: int, param1, param2, ...) -> tuple:
    if not n_clicks:
        return no_update, no_update, False, False, "", "success"

    # Validação de parâmetros obrigatórios
    if param1 is None or param2 is None:
        return (
            no_update, no_update, False,
            True, "Preencha todos os parâmetros antes de simular.", "warning"
        )

    resultado = calcular_simulacao(param1=param1, param2=param2)

    resultado_layout = html.Div([
        dbc.Row([
            dbc.Col(build_kpi_resultado(k, v), md=3)
            for k, v in resultado["kpis"].items()
        ], className="mb-3"),
        build_tabela_comparativa(resultado["comparativo"]),
    ])

    return (
        resultado_layout,
        {"display": "block"},   # torna a seção visível
        False,                  # re-habilita o botão
        True, "Simulação concluída com sucesso.", "success"
    )
```

**Regra:** `calcular_simulacao()` em `_queries.py` recebe parâmetros e retorna dict com `kpis` e `comparativo`. Nunca persiste dados — apenas calcula.

---

## Padrão 3 — Enviar para Aprovação

Aplicar quando `actions` contiver `type: submit_approval`. Usa dois callbacks encadeados: um para abrir o modal de confirmação, outro para confirmar o envio.

```python
# Callback 3a — abre modal de confirmação
@callback(
    Output("<pagina>-modal-confirmar-envio", "is_open"),
    Input("<pagina>-btn-enviar-aprovacao", "n_clicks"),
    State("<pagina>-grid", "selectedRows"),
    prevent_initial_call=True,
)
def abrir_modal_envio(n_clicks: int, selected_rows: list) -> bool:
    if not n_clicks or not selected_rows:
        return False
    return True


# Callback 3b — confirma envio e atualiza status
@callback(
    Output("<pagina>-grid", "rowData"),
    Output("<pagina>-toast", "is_open"),
    Output("<pagina>-toast", "children"),
    Output("<pagina>-toast", "color"),
    Output("<pagina>-modal-confirmar-envio", "is_open", allow_duplicate=True),
    Input("<pagina>-btn-confirmar-envio", "n_clicks"),
    State("<pagina>-grid", "selectedRows"),
    prevent_initial_call=True,
)
def confirmar_envio_aprovacao(n_clicks: int, selected_rows: list) -> tuple:
    if not n_clicks or not selected_rows:
        return no_update, False, "", "success", False

    ids = [row["id"] for row in selected_rows]
    atualizar_status_aprovacao(ids, novo_status="Pendente Aprovação")

    df = get_<entidade>_data()
    return (
        df.to_dict("records"),
        True, f"{len(ids)} item(ns) enviado(s) para aprovação.", "success",
        False
    )
```

---

## Padrão 4 — Aprovar / Rejeitar com Comentário

Aplicar quando `actions` contiver `type: approve` ou `type: reject`. Visibilidade dos botões é controlada pela role do usuário logado via `dcc.Store(id="current-user")`.

```python
# Callback 4a — controla visibilidade dos botões por role
@callback(
    Output("<pagina>-barra-aprovacao", "style"),
    Input("current-user", "data"),
    prevent_initial_call=False,
)
def controlar_visibilidade_aprovacao(user_data: dict) -> dict:
    if user_data and user_data.get("role") in ("supervisor", "admin"):
        return {"display": "flex"}
    return {"display": "none"}


# Callback 4b — abre modal de aprovação/rejeição
@callback(
    Output("<pagina>-modal-aprovacao", "is_open"),
    Output("<pagina>-modal-aprovacao-titulo", "children"),
    Output("<pagina>-hidden-acao-aprovacao", "data"),
    Input("<pagina>-btn-aprovar", "n_clicks"),
    Input("<pagina>-btn-rejeitar", "n_clicks"),
    State("<pagina>-grid", "selectedRows"),
    prevent_initial_call=True,
)
def abrir_modal_aprovacao(
    n_aprovar: int, n_rejeitar: int, selected_rows: list
) -> tuple:
    from dash import ctx
    if not selected_rows:
        return False, "", None
    acao = "aprovar" if ctx.triggered_id == "<pagina>-btn-aprovar" else "rejeitar"
    titulo = "Aprovar selecionados" if acao == "aprovar" else "Rejeitar selecionados"
    return True, titulo, acao


# Callback 4c — executa aprovação/rejeição
@callback(
    Output("<pagina>-grid", "rowData", allow_duplicate=True),
    Output("<pagina>-toast", "is_open", allow_duplicate=True),
    Output("<pagina>-toast", "children", allow_duplicate=True),
    Output("<pagina>-toast", "color", allow_duplicate=True),
    Output("<pagina>-modal-aprovacao", "is_open", allow_duplicate=True),
    Input("<pagina>-btn-confirmar-aprovacao", "n_clicks"),
    State("<pagina>-hidden-acao-aprovacao", "data"),
    State("<pagina>-grid", "selectedRows"),
    State("<pagina>-input-comentario-aprovacao", "value"),
    prevent_initial_call=True,
)
def executar_aprovacao(
    n_clicks: int, acao: str, selected_rows: list, comentario: str
) -> tuple:
    if not n_clicks or not selected_rows:
        return no_update, False, "", "success", False

    # Rejeição exige comentário
    if acao == "rejeitar" and not comentario:
        return no_update, True, "Informe o motivo da rejeição.", "warning", True

    ids = [row["id"] for row in selected_rows]
    novo_status = "Aprovado" if acao == "aprovar" else "Rejeitado"
    atualizar_status_aprovacao(ids, novo_status=novo_status, comentario=comentario)

    df = get_<entidade>_data()
    msg = f"{len(ids)} item(ns) {novo_status.lower()}(s) com sucesso."
    return df.to_dict("records"), True, msg, "success", False
```

---

## Padrão 5 — Row Action → Modal (cellClicked)

Aplicar quando a página tiver ações de edição/visualização por linha do grid.

```python
@callback(
    Output("<pagina>-modal-edicao", "is_open"),
    Output("<pagina>-form-<campo1>", "value"),
    Output("<pagina>-form-<campo2>", "value"),
    Output("<pagina>-hidden-id-selecionado", "data"),
    # ... demais campos do form
    Input("<pagina>-grid", "cellClicked"),
    prevent_initial_call=True,
)
def abrir_modal_edicao(cell_clicked: dict) -> tuple:
    if not cell_clicked:
        return False, None, None, None

    row = cell_clicked.get("rowData", {})
    return (
        True,
        row.get("<campo1>"),
        row.get("<campo2>"),
        row.get("id"),
    )


@callback(
    Output("<pagina>-grid", "rowData", allow_duplicate=True),
    Output("<pagina>-modal-edicao", "is_open", allow_duplicate=True),
    Output("<pagina>-toast", "is_open", allow_duplicate=True),
    Output("<pagina>-toast", "children", allow_duplicate=True),
    Output("<pagina>-toast", "color", allow_duplicate=True),
    Input("<pagina>-btn-salvar-edicao", "n_clicks"),
    State("<pagina>-hidden-id-selecionado", "data"),
    State("<pagina>-form-<campo1>", "value"),
    State("<pagina>-form-<campo2>", "value"),
    prevent_initial_call=True,
)
def salvar_edicao(n_clicks: int, id_selecionado, campo1, campo2) -> tuple:
    if not n_clicks or id_selecionado is None:
        return no_update, False, False, "", "success"

    salvar_<entidade>(id_selecionado, campo1=campo1, campo2=campo2)
    df = get_<entidade>_data()
    return df.to_dict("records"), False, True, "Registro salvo com sucesso.", "success"
```

---

## Padrão 6 — Export Excel

Aplicar quando `actions` contiver `type: download`. Usa `dcc.Download` + `dcc.send_data_frame`.

```python
from dash import dcc

# No layout (_page.py), adicionar: dcc.Download(id="<pagina>-download-excel")

@callback(
    Output("<pagina>-download-excel", "data"),
    Input("<pagina>-btn-exportar-excel", "n_clicks"),
    State("<pagina>-filtro-<campo>", "value"),
    # ... states dos filtros ativos
    prevent_initial_call=True,
)
def exportar_excel(n_clicks: int, filtro) -> dict:
    if not n_clicks:
        return no_update

    df = get_<entidade>_data(filtro=filtro)
    return dcc.send_data_frame(
        df.to_excel,
        "<pagina>_export.xlsx",
        sheet_name="Dados",
        index=False,
    )
```

---

## Padrão 7 — Toast de Feedback

O `dbc.Toast` é um componente global por página, declarado uma vez no `_page.py` e controlado por todos os callbacks via `allow_duplicate=True`.

**Declaração no `_page.py`** (adicionar ao layout):
```python
dbc.Toast(
    id="<pagina>-toast",
    header="Notificação",
    is_open=False,
    dismissable=True,
    duration=4000,           # fecha automaticamente após 4s
    style={"position": "fixed", "top": "1rem", "right": "1rem", "zIndex": 9999, "minWidth": "300px"},
    color="success",
)
```

**Outputs padrão** (usar em qualquer callback que precise de feedback):
```python
Output("<pagina>-toast", "is_open"),
Output("<pagina>-toast", "children"),
Output("<pagina>-toast", "icon"),   # "success" | "warning" | "danger" | "info"
```

Preferir `toast("<pagina>-toast")` da biblioteca no layout e `notify("Mensagem", "success")` no callback — retorna exatamente a tupla `(is_open, children, icon)` dos 3 Outputs.

---

## Padrão 8 — Drill-down: clique no gráfico filtra o grid

Aplicar para cada item em `pages.<pagina>.drilldowns[]` (`source_chart`, `target`, `target_field`). O gráfico é a fonte, o grid (ou outro gráfico) é o alvo; um `dcc.Store` guarda a seleção ativa e um `chips_row` mostra o filtro com ✕ para limpar. O gráfico-fonte destaca a barra clicada com `with_selection()`.

```python
from frontend.components.ui_components import chip, chips_row, empty_state   # chips_row já está no _page.py: chips_row("<pagina>-chips")
from frontend.components.charts import with_selection

# 1) Clique no gráfico → seleção (heatmap: usar point["x"] e point["y"]; treemap: point["label"])
@callback(
    Output("<pagina>-drill", "data"),
    Input("<pagina>-chart-<source>", "clickData"),
    Input({"type": "<pagina>-chip", "field": ALL}, "n_clicks"),
    State("<pagina>-drill", "data"),
    prevent_initial_call=True,
)
def set_drill(click_data, chip_clicks, current):
    trig = ctx.triggered_id
    if isinstance(trig, dict):                      # ✕ no chip → limpa aquele campo
        current = dict(current or {}); current.pop(trig["field"], None); return current
    if not click_data:
        return no_update
    point = click_data["points"][0]
    value = point.get("y") if point.get("orientation") == "h" else point.get("x")   # bar_ranking é horizontal → categoria em y
    value = point.get("label", value)                                                # treemap/pie
    return {**(current or {}), "<target_field>": value}

# 2) Seleção → grid + chips + destaque no gráfico (o callback de filtro (Padrão 1) também recebe State("<pagina>-drill","data"))
@callback(
    Output("<pagina>-grid", "rowData", allow_duplicate=True),
    Output("<pagina>-chips", "children"),
    Output("<pagina>-chart-<source>", "figure", allow_duplicate=True),
    Input("<pagina>-drill", "data"),
    State("<pagina>-chart-<source>", "figure"),
    State("<pagina>-filtro-<campo1>", "value"), ...,
    prevent_initial_call=True,
)
def apply_drill(drill, fig, filtro1, ...):
    df = carregar_<entidade>(filtro1=filtro1, ..., **(drill or {}))
    chips = [chip("<Label do campo>", v, {"type": "<pagina>-chip", "field": k}) for k, v in (drill or {}).items()]
    fig = with_selection(go.Figure(fig), (drill or {}).get("<target_field>"))
    return df.to_dict("records"), chips, fig
```

Regras: `dcc.Store(id="<pagina>-drill", storage_type="memory")` no `_page.py`; funções de `_queries.py` aceitam os campos de drill como kwargs opcionais; ao trocar filtros principais, o Padrão 1 zera o drill (`Output("<pagina>-drill","data")` = `{}` com `allow_duplicate=True`).

---

## Padrão 9 — Recálculo ao vivo (telas `simulation` com `recalc_mode: live`)

Sliders (`param_slider`) e selects de parâmetro entram como **`Input`** (não `State`); o botão "Simular" deixa de existir ou vira "Recalcular" opcional. Um `dbc.Switch(id="<pagina>-auto", value=True, label="Recalcular ao vivo")` permite desligar o modo ao vivo quando o cálculo for pesado.

```python
@callback(
    Output("<pagina>-store-resultado", "data"),
    Output("<pagina>-kpis-row", "children"),
    Output("<pagina>-chart-principal", "figure"),
    Output("<pagina>-chart-secundario", "figure"),
    Output("<pagina>-grid", "rowData"),
    Output("<pagina>-resultado", "style"),
    Input("<pagina>-param-<var1>", "value"),        # sliders como Input
    Input("<pagina>-param-<var2>", "value"),
    Input("<pagina>-filtro-<select>", "value"),
    Input("<pagina>-btn-simular", "n_clicks"),      # fallback quando auto=False
    State("<pagina>-auto", "value"),
    prevent_initial_call=False,                     # calcula já na abertura com os defaults → tela nunca abre vazia
)
def recalcular(v1, v2, sel, n, auto):
    if not auto and ctx.triggered_id != "<pagina>-btn-simular":
        return (no_update,) * 6
    df = carregar_base_simulacao(filtros={"<select>": sel or None})
    r = calcular_simulacao(df, <var1>=v1, <var2>=v2)          # fórmula literal de business_logic.yaml
    return r, build_kpis_resultado(r), build_chart_principal(r), build_chart_secundario(r), r["comparativo"], {"display": "block"}
```

Regras: sliders com `step` ≥ 0,5 para evitar tempestade de callbacks; `_queries.py` deve rodar < 300 ms para ≤ 5.000 linhas (usar pandas vetorizado, nunca `iterrows`); envolver KPIs/gráficos em `loading()`. Quando `recalc_mode: button`, usar o Padrão 2 clássico.

---

## Padrão 10 — Detalhe em offcanvas (`detalhar` / `detail_panel`)

Clique na coluna de ação `acao_detalhar` (ou em qualquer célula, se a tela for `master_detail` sem coluna de ação) abre `detail_offcanvas("<pagina>-detail")` com a ficha do registro + relacionados.

```python
from frontend.components.ui_components import detail_field, section_title, data_table, empty_state
from frontend.components.charts import sparkline

@callback(
    Output("<pagina>-detail", "is_open"),
    Output("<pagina>-detail", "title"),
    Output("<pagina>-detail-body", "children"),
    Input("<pagina>-grid", "cellClicked"),
    prevent_initial_call=True,
)
def abrir_detalhe(cell):
    if not cell or cell.get("colId") not in ("acao_detalhar", <colunas clicáveis>):
        return no_update, no_update, no_update
    row = obter_<entidade>(cell["rowId"] or cell["value"])   # id da linha: use hide_cols=["id"] no data_table e rowId
    hist = carregar_historico_<entidade>(row["id"])          # relacionados (últimos N)
    body = [
        dbc.Row([dbc.Col(detail_field("Nome", row["nome"]), md=8), dbc.Col(detail_field("Status", status_badge(row["status"])), md=4)]),
        dbc.Row([dbc.Col(detail_field("Preço atual", format_currency(row["preco_atual"], 2), mono=True), md=6), ...]),
        section_title("Tendência 12 meses"),
        dcc.Graph(figure=sparkline(hist["valor"].tolist(), height=80), config={"displayModeBar": False}, style={"height": "80px"}),
        section_title("Últimos registros"),
        data_table(hist.tail(10), "<pagina>-detail-grid", column_types={...}, page_size=10, height="320px") if not hist.empty else empty_state(compact=True),
    ]
    return True, row["nome"], body
```

Para `approval_queue`, o body inclui parâmetros do item, KPIs de impacto (`kpi_card`) e o gráfico comparativo; os botões Aprovar/Rejeitar do Padrão 4 podem viver no rodapé do offcanvas.

---

## Padrão 11 — UI role-aware (`actions[].roles`)

Botões/ações com `roles` em `screens_definition.yaml` são **ocultados** (não desabilitados) para quem não tem permissão. Um callback por página, disparado por `current-user`:

```python
@callback(
    Output("<pagina>-btn-approve", "style"), Output("<pagina>-btn-reject", "style"), Output("<pagina>-btn-novo", "style"),
    Input("current-user", "data"),
)
def aplicar_roles(user):
    role = (user or {}).get("role")
    show = lambda roles: {} if role in roles else {"display": "none"}
    return show(["admin", "gerente"]), show(["admin", "gerente"]), show(["admin", "analista"])
```

As colunas de ação do grid (`row_actions`) também obedecem: passe `row_actions=[a for a in acoes if role in roles_da_acao]` ao montar o `data_table` no callback de filtro (Padrão 1 recebe `State("current-user","data")`). O backend valida de novo — a UI só esconde.

---

## Padrão 12 — Contador de pendências na sidebar (`sidebar_badge`) — vive em `app.py`

```python
from frontend.pages.<fila>.<fila>_queries import contar_pendentes   # uma função por tela com sidebar_badge

@callback(Output("sidebar-badges", "data"), Input("url", "pathname"), Input("current-user", "data"))
def compute_badges(pathname, user):
    if not user:
        return {}
    return {"/<fila>": contar_pendentes(role=user.get("role"))}      # {route: int}; 0 → sem badge
```

`build_sidebar(pathname, user, badges)` renderiza `html.Span(str(n), className="nav-badge")` para rotas com `n > 0`. Recalcula a cada navegação (após aprovar, o número cai sem reload).

---

## Padrão 13 — Busca rápida no grid (`quick_filter_input`)

```python
@callback(Output("<pagina>-grid", "dashGridOptions"), Input("<pagina>-grid-quick", "value"), State("<pagina>-grid", "dashGridOptions"))
def quick_filter(text, opts):
    return {**(opts or {}), "quickFilterText": text or ""}
```

---

## Estrutura completa do arquivo

```python
from dash import Input, Output, State, callback, no_update, ctx
import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
from frontend.pages.<pagina>.<pagina>_queries import (
    get_<entidade>_data,
    # importar demais funções usadas
)


def register_callbacks() -> None:
    """Registra todos os callbacks da página <pagina>."""

    # [Padrão 1] Filtrar grid
    # [Padrão 2] Simular cenário        — se actions tiver simulate
    # [Padrão 3] Enviar para aprovação  — se actions tiver submit_approval
    # [Padrão 4] Aprovar / Rejeitar     — se actions tiver approve/reject
    # [Padrão 5] Row action → modal     — se actions tiver modal/edit
    # [Padrão 6] Export Excel           — se actions tiver download
    # [Padrão 8] Drill-down             — se drilldowns[] não vazio
    # [Padrão 9] Recálculo ao vivo      — se recalc_mode == live (substitui o Padrão 2)
    # [Padrão 10] Detalhe offcanvas     — se row_actions tiver detalhar ou detail_panel definido
    # [Padrão 11] Role-aware            — se algum actions[].roles definido
    # [Padrão 13] Busca rápida          — se a página usar quick_filter_input
    # Toast é implícito — sempre incluir toast("<pagina>-toast") no layout e usar notify()
```

---

## Regras

- Todos os callbacks dentro de `register_callbacks()`, chamada em `app.py`.
- IDs consistentes com `_page.py` — padrão `<pagina>-<componente>`.
- Dados lidos/escritos via funções de `_queries.py` — nunca lógica de dados no callback.
- `prevent_initial_call=False` para carregamento inicial de dados.
- `prevent_initial_call=True` para ações disparadas pelo usuário (simular, aprovar, exportar).
- `allow_duplicate=True` nos Outputs compartilhados entre callbacks (toast, grid rowData).
- Tipagem Python obrigatória em todos os parâmetros e retornos.
- NÃO conectar ao banco — dados via `mock_data/` em modo de desenvolvimento.

## Restrições

- Gerar APENAS o arquivo `_callbacks.py` desta skill.
- Contexto máximo: **8.000 tokens** de saída por arquivo.
- Se exceder 8.000 tokens, dividir em chunks com continuação automática.

## Pós-processamento

1. Verificar que arquivo Python é válido (parse)
2. Verificar que `register_callbacks()` existe
3. Verificar que IDs são consistentes com `_page.py`
4. Verificar que não há lógica de dados duplicada fora de `_queries.py`
