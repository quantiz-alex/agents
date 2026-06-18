"""Componentes visuais para a pagina de Lista de Precos Sell In."""

from typing import Any, Union

import dash_ag_grid
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html

_PRIMARY = "#1045C8"
_COLOR_SEQ = ["#1045C8", "#10b981", "#f59e0b", "#ef4444", "#06b6d4"]

_CURRENCY_FORMATTER = {"function": "params.value != null ? 'R$ ' + parseFloat(params.value).toLocaleString('pt-BR', {minimumFractionDigits: 2}) : ''"}
_PCT_FORMATTER = {"function": "params.value != null ? parseFloat(params.value).toFixed(2) + '%' : ''"}


def build_grid(df: pd.DataFrame) -> Any:
    """Monta o AG Grid de itens da lista de precos."""
    column_defs = [
        {"field": "id", "headerName": "ID", "width": 80, "type": "numericColumn"},
        {"field": "sku", "headerName": "SKU", "width": 120},
        {"field": "descricao", "headerName": "Produto", "minWidth": 180},
        {"field": "familia", "headerName": "Familia", "width": 130},
        {"field": "canal", "headerName": "Canal", "width": 120},
        {"field": "ptc_sell_out", "headerName": "PTC Sell Out", "width": 130, "type": "numericColumn", "valueFormatter": _CURRENCY_FORMATTER},
        {"field": "margem_cadeia_pct", "headerName": "Mg. Cadeia", "width": 120, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "sell_in_nf", "headerName": "Sell In NF", "width": 120, "type": "numericColumn", "valueFormatter": _CURRENCY_FORMATTER},
        {"field": "sell_in_niv", "headerName": "Sell In NIV", "width": 120, "type": "numericColumn", "valueFormatter": _CURRENCY_FORMATTER},
        {"field": "custo_aquisicao", "headerName": "Custo Aq.", "width": 120, "type": "numericColumn", "valueFormatter": _CURRENCY_FORMATTER},
        {"field": "markup", "headerName": "Markup", "width": 100, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {
            "field": "cap_aplicado",
            "headerName": "CAP",
            "width": 100,
            "valueFormatter": {"function": "params.value === 1 ? 'Limitado' : 'Dentro'"},
            "cellStyle": {
                "function": "params.value === 1 ? {'color': '#ef4444', 'fontWeight': '600'} : {'color': '#10b981', 'fontWeight': '600'}"
            },
        },
        {"field": "variacao_pct", "headerName": "Variacao %", "width": 120, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "status", "headerName": "Status Aprovacao", "width": 160},
    ]

    return dash_ag_grid.AgGrid(
        id="lista-preco-grid",
        rowData=df.to_dict("records"),
        columnDefs=column_defs,
        defaultColDef={
            "sortable": True,
            "resizable": True,
            "filter": True,
            "floatingFilter": True,
            "suppressMenu": True,
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 20,
            "rowHeight": 44,
            "suppressCellFocus": True,
        },
        className="ag-theme-alpine",
        style={"height": "500px"},
    )


def build_kpis(df: pd.DataFrame) -> list:
    """Monta os cards de KPI."""
    from frontend.pages.lista_preco.lista_preco_queries import calcular_kpis_lista_preco

    kpis = calcular_kpis_lista_preco(df)

    return [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Total de SKUs", className="text-muted small mb-1"),
                    html.H4(str(kpis["total_skus"]), className="fw-bold mb-0", style={"color": _PRIMARY}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": _PRIMARY + " !important"},
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Dentro dos CAPs", className="text-muted small mb-1"),
                    html.H4(f"{kpis['pct_dentro_cap']}%", className="fw-bold mb-0", style={"color": "#10b981"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#10b981 !important"},
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Variacao Media vs. Base", className="text-muted small mb-1"),
                    html.H4(f"{kpis['variacao_media']}%", className="fw-bold mb-0", style={"color": "#f59e0b"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#f59e0b !important"},
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Receita NIV Total (R$)", className="text-muted small mb-1"),
                    html.H4(
                        f"R$ {kpis['impacto_receita']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        className="fw-bold mb-0",
                        style={"color": "#06b6d4", "fontSize": "1rem"},
                    ),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#06b6d4 !important"},
            ),
            md=3,
        ),
    ]


def build_bar_chart_familia(df: pd.DataFrame) -> Union[dcc.Graph, dbc.Alert]:
    """Grafico de barras: Preco Atual vs. Sell In NIV por familia."""
    if df.empty:
        return dbc.Alert("Sem dados para o periodo.", color="info")

    df_agg = df.groupby("familia").agg(
        sell_in_niv_medio=("sell_in_niv", "mean"),
        preco_atual_medio=("preco_atual", "mean"),
    ).reset_index()

    df_melted = df_agg.melt(
        id_vars="familia",
        value_vars=["preco_atual_medio", "sell_in_niv_medio"],
        var_name="tipo",
        value_name="valor",
    )
    df_melted["tipo"] = df_melted["tipo"].map(
        {"preco_atual_medio": "Preco Atual", "sell_in_niv_medio": "Sell In NIV"}
    )

    fig = px.bar(
        df_melted,
        x="familia",
        y="valor",
        color="tipo",
        barmode="group",
        title="Preco Atual vs. Sell In NIV por Familia",
        labels={"valor": "Preco (R$)", "familia": "Familia", "tipo": ""},
        color_discrete_sequence=_COLOR_SEQ,
        template="plotly_white",
        height=300,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="system-ui, sans-serif", size=12, color="#374151"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return dcc.Graph(figure=fig, id="lista-preco-chart-1", config={"displayModeBar": False})


def build_bar_chart_variacao(df: pd.DataFrame) -> Union[dcc.Graph, dbc.Alert]:
    """Grafico de distribuicao de variacao de preco em faixas."""
    if df.empty:
        return dbc.Alert("Sem dados para o periodo.", color="info")

    df_copy = df.copy()
    df_copy["variacao_pct"] = pd.to_numeric(df_copy["variacao_pct"], errors="coerce").fillna(0)

    bins = [-float("inf"), -5, 0, 5, 10, float("inf")]
    labels = ["< -5%", "-5% a 0%", "0% a 5%", "5% a 10%", "> 10%"]
    df_copy["faixa"] = pd.cut(df_copy["variacao_pct"], bins=bins, labels=labels)
    df_faixa = df_copy.groupby("faixa", observed=True).size().reset_index(name="quantidade")

    fig = px.bar(
        df_faixa,
        x="faixa",
        y="quantidade",
        title="Distribuicao de Variacao de Preco",
        labels={"faixa": "Faixa de Variacao", "quantidade": "Qtd. SKUs"},
        color_discrete_sequence=_COLOR_SEQ,
        template="plotly_white",
        height=300,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="system-ui, sans-serif", size=12, color="#374151"),
    )
    return dcc.Graph(figure=fig, id="lista-preco-chart-2", config={"displayModeBar": False})


def build_filtros(familias: list, canais: list) -> dbc.Card:
    """Monta o card de filtros."""
    return dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Familia", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="lista-preco-filtro-familia",
                                options=[{"label": v, "value": v} for v in familias],
                                placeholder="Todas",
                                clearable=True,
                                searchable=True,
                            ),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Canal", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="lista-preco-filtro-canal",
                                options=[{"label": v, "value": v} for v in canais],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Status CAP", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="lista-preco-filtro-cap",
                                options=[{"label": v, "value": v} for v in ["Dentro", "Limitado pelo CAP"]],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Status Aprovacao", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="lista-preco-filtro-aprovacao",
                                options=[{"label": v, "value": v} for v in ["Aprovada", "Rejeitada", "Gerada", "PendenteAprovacao"]],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-search me-1"), "Filtrar"],
                            id="lista-preco-btn-filtrar",
                            color="primary",
                            className="w-100",
                        ),
                        md=2,
                        className="d-grid align-self-end",
                    ),
                ],
                className="g-2 align-items-end",
            ),
            className="py-2",
        ),
        className="shadow-sm border-0 mb-3",
    )


def build_modal_aprovacao() -> dbc.Modal:
    """Modal de aprovacao/rejeicao de lista."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Confirmar Acao")),
            dbc.ModalBody(
                [
                    dbc.Alert(
                        "Confirma a acao selecionada para esta lista de precos?",
                        color="warning",
                    ),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Observacao", className="fw-medium"),
                            dbc.Textarea(id="lista-preco-modal-obs", rows=3, placeholder="Observacao opcional..."),
                        ])
                    ]),
                ]
            ),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="lista-preco-btn-modal-cancelar", color="secondary", outline=True, className="me-2"),
                dbc.Button([html.I(className="bi bi-check-circle me-1"), "Confirmar"], id="lista-preco-btn-modal-confirmar", color="primary"),
            ]),
        ],
        id="lista-preco-modal-aprovacao",
        is_open=False,
    )
