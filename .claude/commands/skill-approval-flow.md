# Skill — Approval Flow Pattern

Gera o padrão completo de ciclo de vida de aprovação: status enum, badges, botões condicionais por role, callbacks de envio, aprovação e rejeição.

## Quando usar

Invocada pelo `frontend-builder` quando:
- `actions` contém `type: submit_approval`, `type: approve` ou `type: reject`
- `screen_type: approval_queue`

Ou diretamente:
```
/skill-approval-flow <nome_pagina>
```
Exemplo: `/skill-approval-flow gestao-precos`

---

## Status Enum Padrão

Todo fluxo de aprovação usa este enum fixo. Os valores devem existir no `data_model.yaml` e no `mock_data`.

| Status              | Badge color | Descrição                                      |
|---------------------|-------------|------------------------------------------------|
| `Rascunho`          | secondary   | Criado mas não enviado para aprovação           |
| `Pendente Aprovação`| warning     | Enviado, aguardando aprovação do supervisor     |
| `Aprovado`          | success     | Aprovado — pode ser aplicado                   |
| `Rejeitado`         | danger      | Rejeitado — deve ser revisado antes de reenviar|

---

## Campos obrigatórios na entidade

Para que o fluxo funcione, a entidade deve ter estes campos no `data_model.yaml` e no `mock_data`:

```yaml
# Adicionar à entidade em data_model.yaml
- name: status
  type: enum
  values: [Rascunho, Pendente Aprovação, Aprovado, Rejeitado]
  default: Rascunho
- name: aprovado_por
  type: varchar(100)
  nullable: true
- name: aprovado_em
  type: datetime2
  nullable: true
- name: comentario_aprovacao
  type: text
  nullable: true
```

---

## `_queries.py` — Funções de aprovação

Adicionar às funções de `_queries.py` da página:

```python
import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent.parent.parent / "mock_data"
_ARQUIVO = DATA_DIR / "<entidade>.csv"


def atualizar_status_aprovacao(
    ids: list[int],
    novo_status: str,
    aprovado_por: str | None = None,
    comentario: str | None = None,
) -> int:
    """
    Atualiza o status dos registros com os IDs fornecidos.
    Retorna o número de registros atualizados.
    """
    df = pd.read_csv(_ARQUIVO)
    mascara = df["id"].isin(ids)
    df.loc[mascara, "status"] = novo_status

    if novo_status in ("Aprovado", "Rejeitado"):
        agora = datetime.now().isoformat()
        df.loc[mascara, "aprovado_por"] = aprovado_por or "sistema"
        df.loc[mascara, "aprovado_em"]  = agora
        if comentario:
            df.loc[mascara, "comentario_aprovacao"] = comentario

    df.to_csv(_ARQUIVO, index=False)
    return int(mascara.sum())


def get_pendentes_aprovacao() -> pd.DataFrame:
    """Retorna apenas registros com status Pendente Aprovação."""
    df = pd.read_csv(_ARQUIVO)
    return df[df["status"] == "Pendente Aprovação"].copy()
```

---

## `_components.py` — Componentes de aprovação

### Badge de status (cellRenderer para AG Grid)

```python
# Adicionar em _components.py

STATUS_BADGE_COLORS: dict[str, str] = {
    "Rascunho":           "secondary",
    "Pendente Aprovação": "warning",
    "Aprovado":           "success",
    "Rejeitado":          "danger",
}

def get_status_column_def(field: str = "status") -> dict:
    """
    Retorna a columnDef do AG Grid para coluna de status com badge colorido.
    Uso: incluir em column_defs do build_grid().
    """
    return {
        "field": field,
        "headerName": "Status",
        "width": 160,
        "cellRenderer": "agAnimateShowChangeCellRenderer",
        "cellStyle": {
            "function": (
                "params.value === 'Aprovado' ? {color: '#16A34A', fontWeight: '600'} : "
                "params.value === 'Rejeitado' ? {color: '#DC2626', fontWeight: '600'} : "
                "params.value === 'Pendente Aprovação' ? {color: '#B45309', fontWeight: '600'} : "
                "{color: '#6B7280'}"
            )
        },
    }
```

### Barra de ações de aprovação

```python
def build_barra_aprovacao(pagina: str) -> html.Div:
    """
    Barra de ações condicionais por role.
    Visibilidade controlada pelo callback controlar_visibilidade_aprovacao().
    - Analista: vê apenas "Enviar para Aprovação"
    - Supervisor/Admin: vê "Aprovar" e "Rejeitar"
    """
    return html.Div([
        # Botões visíveis para analista
        html.Div([
            dbc.Button(
                [html.I(className="bi bi-send me-2"), "Enviar para Aprovação"],
                id=f"{pagina}-btn-enviar-aprovacao",
                color="primary", size="sm", className="me-2",
            ),
        ], id=f"{pagina}-acoes-analista", style={"display": "none"}),

        # Botões visíveis para supervisor/admin
        html.Div([
            dbc.Button(
                [html.I(className="bi bi-check-circle me-2"), "Aprovar"],
                id=f"{pagina}-btn-aprovar",
                color="success", size="sm", className="me-2",
            ),
            dbc.Button(
                [html.I(className="bi bi-x-circle me-2"), "Rejeitar"],
                id=f"{pagina}-btn-rejeitar",
                color="danger", size="sm", outline=True,
            ),
        ], id=f"{pagina}-acoes-supervisor", style={"display": "none"}),
    ], id=f"{pagina}-barra-aprovacao",
       className="d-flex align-items-center gap-2 mb-2",
       style={"display": "none"})
```

### Modal de confirmação de envio

```python
def build_modal_confirmar_envio(pagina: str) -> dbc.Modal:
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Confirmar Envio"), close_button=True),
        dbc.ModalBody(
            "Deseja enviar o(s) item(ns) selecionado(s) para aprovação? "
            "Após o envio, não será possível editar até a avaliação do supervisor."
        ),
        dbc.ModalFooter([
            dbc.Button("Cancelar",  id=f"{pagina}-btn-cancelar-envio",
                       color="outline-secondary", className="me-2"),
            dbc.Button("Confirmar Envio", id=f"{pagina}-btn-confirmar-envio",
                       color="primary"),
        ]),
    ], id=f"{pagina}-modal-confirmar-envio", is_open=False, centered=True)
```

### Modal de aprovação/rejeição com comentário

```python
def build_modal_aprovacao(pagina: str) -> dbc.Modal:
    return dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle(id=f"{pagina}-modal-aprovacao-titulo"),
            close_button=True,
        ),
        dbc.ModalBody([
            html.P(id=f"{pagina}-modal-aprovacao-descricao",
                   className="text-muted small mb-3"),
            dbc.Label("Comentário", className="fw-semibold small"),
            dbc.Textarea(
                id=f"{pagina}-input-comentario-aprovacao",
                placeholder="Opcional para aprovação. Obrigatório para rejeição.",
                rows=3,
            ),
            dbc.FormText(
                "Rejeições exigem comentário explicando o motivo.",
                color="muted",
            ),
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancelar",  id=f"{pagina}-btn-cancelar-aprovacao",
                       color="outline-secondary", className="me-2"),
            dbc.Button("Confirmar", id=f"{pagina}-btn-confirmar-aprovacao",
                       color="primary"),
        ]),
        # Store oculto para guardar a ação (aprovar | rejeitar)
        dcc.Store(id=f"{pagina}-hidden-acao-aprovacao"),
    ], id=f"{pagina}-modal-aprovacao", is_open=False, centered=True)
```

---

## `_callbacks.py` — Callbacks completos de aprovação

```python
from dash import Input, Output, State, callback, no_update, ctx
import dash_bootstrap_components as dbc
from dash import html
from frontend.pages.<pagina>.<pagina>_queries import (
    get_<entidade>_data,
    atualizar_status_aprovacao,
)


def register_approval_callbacks(pagina: str) -> None:
    """
    Registra todos os callbacks do fluxo de aprovação para a página especificada.
    Chamar dentro de register_callbacks() da página.
    """

    # ── Visibilidade por role ──────────────────────────────────────────────
    @callback(
        Output(f"{pagina}-acoes-analista",   "style"),
        Output(f"{pagina}-acoes-supervisor", "style"),
        Output(f"{pagina}-barra-aprovacao",  "style"),
        Input("current-user", "data"),
        prevent_initial_call=False,
    )
    def controlar_visibilidade(user_data: dict) -> tuple:
        if not user_data:
            return {"display": "none"}, {"display": "none"}, {"display": "none"}

        role = user_data.get("role", "")
        barra_style = {"display": "flex", "alignItems": "center", "gap": "0.5rem"}

        if role == "analista":
            return {"display": "block"}, {"display": "none"}, barra_style
        if role in ("supervisor", "admin"):
            return {"display": "none"}, {"display": "flex", "gap": "0.5rem"}, barra_style
        return {"display": "none"}, {"display": "none"}, {"display": "none"}


    # ── Enviar para aprovação ─────────────────────────────────────────────
    @callback(
        Output(f"{pagina}-modal-confirmar-envio", "is_open"),
        Input(f"{pagina}-btn-enviar-aprovacao", "n_clicks"),
        Input(f"{pagina}-btn-cancelar-envio",   "n_clicks"),
        State(f"{pagina}-grid", "selectedRows"),
        prevent_initial_call=True,
    )
    def toggle_modal_envio(n_enviar: int, n_cancelar: int, selected_rows: list) -> bool:
        triggered = ctx.triggered_id
        if triggered == f"{pagina}-btn-enviar-aprovacao":
            if not selected_rows:
                return False   # sem seleção — não abre modal
            return True
        return False


    @callback(
        Output(f"{pagina}-grid", "rowData"),
        Output(f"{pagina}-toast", "is_open"),
        Output(f"{pagina}-toast", "children"),
        Output(f"{pagina}-toast", "color"),
        Output(f"{pagina}-modal-confirmar-envio", "is_open", allow_duplicate=True),
        Input(f"{pagina}-btn-confirmar-envio", "n_clicks"),
        State(f"{pagina}-grid", "selectedRows"),
        State("current-user", "data"),
        prevent_initial_call=True,
    )
    def confirmar_envio(
        n_clicks: int, selected_rows: list, user_data: dict
    ) -> tuple:
        if not n_clicks or not selected_rows:
            return no_update, False, "", "success", False

        ids = [row["id"] for row in selected_rows]
        atualizados = atualizar_status_aprovacao(ids, "Pendente Aprovação")
        df = get_<entidade>_data()
        return (
            df.to_dict("records"),
            True, f"{atualizados} item(ns) enviado(s) para aprovação.", "success",
            False,
        )


    # ── Aprovar / Rejeitar ────────────────────────────────────────────────
    @callback(
        Output(f"{pagina}-modal-aprovacao",          "is_open"),
        Output(f"{pagina}-modal-aprovacao-titulo",   "children"),
        Output(f"{pagina}-modal-aprovacao-descricao","children"),
        Output(f"{pagina}-hidden-acao-aprovacao",    "data"),
        Output(f"{pagina}-input-comentario-aprovacao","value"),
        Input(f"{pagina}-btn-aprovar",   "n_clicks"),
        Input(f"{pagina}-btn-rejeitar",  "n_clicks"),
        Input(f"{pagina}-btn-cancelar-aprovacao", "n_clicks"),
        State(f"{pagina}-grid", "selectedRows"),
        prevent_initial_call=True,
    )
    def toggle_modal_aprovacao(
        n_aprovar: int, n_rejeitar: int, n_cancelar: int, selected_rows: list
    ) -> tuple:
        triggered = ctx.triggered_id

        if triggered == f"{pagina}-btn-cancelar-aprovacao":
            return False, "", "", None, ""

        if not selected_rows:
            return False, "", "", None, ""

        n = len(selected_rows)
        if triggered == f"{pagina}-btn-aprovar":
            return (
                True,
                f"Aprovar {n} item(ns)",
                f"Os {n} item(ns) selecionados serão marcados como Aprovados.",
                "aprovar",
                "",
            )
        return (
            True,
            f"Rejeitar {n} item(ns)",
            f"Informe o motivo da rejeição dos {n} item(ns) selecionados.",
            "rejeitar",
            "",
        )


    @callback(
        Output(f"{pagina}-grid", "rowData", allow_duplicate=True),
        Output(f"{pagina}-toast", "is_open", allow_duplicate=True),
        Output(f"{pagina}-toast", "children", allow_duplicate=True),
        Output(f"{pagina}-toast", "color", allow_duplicate=True),
        Output(f"{pagina}-modal-aprovacao", "is_open", allow_duplicate=True),
        Input(f"{pagina}-btn-confirmar-aprovacao", "n_clicks"),
        State(f"{pagina}-hidden-acao-aprovacao",    "data"),
        State(f"{pagina}-grid", "selectedRows"),
        State(f"{pagina}-input-comentario-aprovacao", "value"),
        State("current-user", "data"),
        prevent_initial_call=True,
    )
    def executar_aprovacao(
        n_clicks: int,
        acao: str,
        selected_rows: list,
        comentario: str,
        user_data: dict,
    ) -> tuple:
        if not n_clicks or not selected_rows or not acao:
            return no_update, False, "", "success", False

        if acao == "rejeitar" and not comentario:
            return (
                no_update, True,
                "Informe o motivo da rejeição antes de confirmar.", "warning",
                True,
            )

        ids = [row["id"] for row in selected_rows]
        aprovador = user_data.get("nome", "sistema") if user_data else "sistema"
        novo_status = "Aprovado" if acao == "aprovar" else "Rejeitado"

        atualizados = atualizar_status_aprovacao(
            ids, novo_status,
            aprovado_por=aprovador,
            comentario=comentario,
        )

        df = get_<entidade>_data()
        msg = f"{atualizados} item(ns) {novo_status.lower()}(s) com sucesso."
        cor = "success" if novo_status == "Aprovado" else "danger"
        return df.to_dict("records"), True, msg, cor, False
```

---

## Screen type: approval_queue

Quando `screen_type: approval_queue`, gerar uma tela dedicada para supervisores:

### Layout da fila de aprovações

```python
def layout() -> html.Div:
    return html.Div([
        # Toast global
        dbc.Toast(id="<pagina>-toast", ...),

        # Header
        html.Div([
            html.H4("Fila de Aprovações", className="fw-bold mb-0 text-dark"),
            html.Small("Itens pendentes de avaliação", className="text-muted"),
        ], className="d-flex flex-column mb-3"),

        # KPIs da fila
        dbc.Row([
            dbc.Col(build_kpi_card("Pendentes",       "0", "warning"),  md=3),
            dbc.Col(build_kpi_card("Aprovados Hoje",  "0", "success"),  md=3),
            dbc.Col(build_kpi_card("Rejeitados Hoje", "0", "danger"),   md=3),
            dbc.Col(build_kpi_card("Tempo Médio",     "—",  "info"),    md=3),
        ], id="<pagina>-kpis-row", className="mb-3"),

        # Filtros
        build_filtros_fila(),

        # Barra de ações (supervisor/admin)
        build_barra_aprovacao("<pagina>"),

        # Grid de pendências
        build_grid_pendencias(),

        # Modais
        build_modal_aprovacao("<pagina>"),
    ], className="page-wrapper px-4 py-3", style={"background": "#f8fafc", "minHeight": "100vh"})
```

### Grid de pendências

```python
def build_grid_pendencias() -> dbc.Card:
    column_defs = [
        {"headerCheckboxSelection": True, "checkboxSelection": True,
         "width": 50, "pinned": "left", "suppressMenu": True},
        {"field": "id",           "headerName": "ID",        "width": 70},
        # campos específicos da entidade
        get_status_column_def(),
        {"field": "aprovado_por", "headerName": "Avaliado por", "flex": 1},
        {"field": "aprovado_em",  "headerName": "Avaliado em",  "flex": 1},
        {"field": "comentario_aprovacao", "headerName": "Comentário", "flex": 2},
    ]
    return dbc.Card([
        dbc.CardHeader("Itens Pendentes", className="bg-white border-bottom fw-semibold"),
        dbc.CardBody([
            dag.AgGrid(
                id="<pagina>-grid",
                columnDefs=column_defs,
                rowData=[],
                defaultColDef={"resizable": True, "sortable": True, "suppressMenu": True},
                dashGridOptions={
                    "pagination": True, "paginationPageSize": 20,
                    "rowHeight": 44, "headerHeight": 44,
                    "rowSelection": "multiple",
                    "suppressRowClickSelection": True,
                },
                className="ag-theme-alpine",
                style={"height": "500px"},
            ),
        ], className="p-0"),
    ], className="shadow-sm border-0")
```

---

## Integração com `register_callbacks()`

Na `_callbacks.py` da página, importar e chamar:

```python
from frontend.pages.<pagina>.<pagina>_callbacks import register_approval_callbacks


def register_callbacks() -> None:
    # callbacks normais da página (filtros, etc.)
    ...
    # fluxo de aprovação
    register_approval_callbacks("<pagina>")
```

---

## Restrições

- `atualizar_status_aprovacao()` sempre lê e reescreve o CSV completo — aceitável em modo mock.
- Visibilidade de botões por role: SEMPRE via callback + `dcc.Store("current-user")` — nunca hardcodado no layout.
- `comentario_aprovacao` é obrigatório para rejeição, opcional para aprovação.
- Aprovador registrado como `user_data["nome"]` — nunca hardcodado.
- Tipagem Python obrigatória em todas as funções.
- Contexto máximo: **8.000 tokens** de saída por arquivo.
