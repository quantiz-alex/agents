"""Componentes visuais para a pagina de Simulacao de Impactos."""

from typing import Any, Union

import dash_ag_grid
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html

_PRIMARY = "#1045C8"
_COLOR_SEQ = ["#1045C8", "#10b981", "#f59e0b", "#ef4444", "#06b6d4"]
_CURRENCY_FORMATTER = {"function": "params.value != null ? 'R$ ' + parseFloat(params.value).toLocaleString('pt-BR', {minimumFractionDigits: 2}) : ''"}
_DEC2_FORMATTER = {"function": "params.value != null ? parseFloat(params.value).toFixed(2) : ''"}


def build_grid(df: pd.DataFrame) -> Any:
    """Monta o AG Grid de resultados de simulacao por SKU."""
    column_defs = [
        {"field": "id", "headerName": "ID", "width": 80, "type": "numericColumn"},
        {"field": "sku", "headerName": "SKU", "width": 120},
        {"field": "descricao", "headerName": "Produto", "minWidth": 180},
        {"field": "familia", "headerName": "Familia", "width": 130},
        {"field": "canal", "headerName": "Canal", "width": 120},
        {"field": "tipo_cenario", "headerName": "Cenario", "width": 140},
        {"field": "volume_simulado", "headerName": "Volume Simulado", "width": 150, "type": "numericColumn", "valueFormatter": _DEC2_FORMATTER},
        {"field": "receita_niv_simulada", "headerName": "Receita NIV (R$)", "width": 160, "type": "numericColumn", "valueFormatter": _CURRENCY_FORMATTER},
        {"field": "margem_industria", "headerName": "Mg. Industria (R$)", "width": 160, "type": "numericColumn", "valueFormatter": _CURRENCY_FORMATTER},
        {"field": "margem_distribuidor", "headerName": "Mg. Distribuidor (R$)", "width": 180, "type": "numericColumn", "valueFormatter": _CURRENCY_FORMATTER},
        {"field": "margem_varejo", "headerName": "Mg. Varejo (R$)", "width": 150, "type": "numericColumn", "valueFormatter": _CURRENCY_FORMATTER},
    ]

    return dash_ag_grid.AgGrid(
        id="simulacao-grid",
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


def build_kpis(df_cenarios: pd.DataFrame, df_itens: pd.DataFrame) -> list:
    """Monta os cards de KPI de simulacao."""
    from frontend.pages.simulacao.simulacao_queries import calcular_kpis_simulacao

    kpis = calcular_kpis_simulacao(df_cenarios, df_itens)

    def _sign_color(val: float) -> str:
        return "#10b981" if val >= 0 else "#ef4444"

    return [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Delta Volume %", className="text-muted small mb-1"),
                    html.H4(f"{kpis['delta_volume_pct']:+.2f}%", className="fw-bold mb-0", style={"color": _sign_color(kpis["delta_volume_pct"])}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": _PRIMARY + " !important"},
            ),
            md=2,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Delta Receita NIV", className="text-muted small mb-1"),
                    html.H5(
                        f"R$ {kpis['delta_receita_niv']:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        className="fw-bold mb-0",
                        style={"color": _sign_color(kpis["delta_receita_niv"]), "fontSize": "0.95rem"},
                    ),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#06b6d4 !important"},
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Delta Mg. Industria", className="text-muted small mb-1"),
                    html.H5(
                        f"R$ {kpis['delta_margem_industria']:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        className="fw-bold mb-0",
                        style={"color": _sign_color(kpis["delta_margem_industria"]), "fontSize": "0.95rem"},
                    ),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#f59e0b !important"},
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Mg. Distribuidor %", className="text-muted small mb-1"),
                    html.H4(f"{kpis['delta_margem_distribuidor_pct']:.1f}%", className="fw-bold mb-0", style={"color": "#10b981"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#10b981 !important"},
            ),
            md=2,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Mg. Varejo %", className="text-muted small mb-1"),
                    html.H4(f"{kpis['delta_margem_varejo_pct']:.1f}%", className="fw-bold mb-0", style={"color": "#ef4444"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#ef4444 !important"},
            ),
            md=2,
        ),
    ]


def build_chart_margem_cadeia(df_itens: pd.DataFrame) -> Union[dcc.Graph, dbc.Alert]:
    """Grafico de barras: impacto em margem por elo da cadeia."""
    if df_itens.empty:
        return dbc.Alert("Sem dados para o periodo selecionado.", color="info")

    elos = {
        "Industria": df_itens["margem_industria"].sum(),
        "Distribuidor": df_itens["margem_distribuidor"].sum(),
        "Varejo": df_itens["margem_varejo"].sum(),
    }
    df_elo = pd.DataFrame({"elo_cadeia": list(elos.keys()), "delta_margem": list(elos.values())})

    fig = px.bar(
        df_elo,
        x="elo_cadeia",
        y="delta_margem",
        title="Impacto em Margem por Elo da Cadeia",
        labels={"elo_cadeia": "Elo", "delta_margem": "Margem (R$)"},
        color="elo_cadeia",
        color_discrete_sequence=_COLOR_SEQ,
        template="plotly_white",
        height=300,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="system-ui, sans-serif", size=12, color="#374151"),
        showlegend=False,
    )
    return dcc.Graph(figure=fig, id="simulacao-chart-1", config={"displayModeBar": False})


def build_chart_receita_familia(df_itens: pd.DataFrame) -> Union[dcc.Graph, dbc.Alert]:
    """Grafico de barras: receita NIV simulada por familia/canal."""
    if df_itens.empty:
        return dbc.Alert("Sem dados para o periodo selecionado.", color="info")

    df_agg = df_itens.groupby("familia").agg(
        receita_niv_simulada=("receita_niv_simulada", "sum"),
    ).reset_index()

    fig = px.bar(
        df_agg,
        x="familia",
        y="receita_niv_simulada",
        title="Receita NIV Simulada por Familia",
        labels={"familia": "Familia", "receita_niv_simulada": "Receita NIV (R$)"},
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
    return dcc.Graph(figure=fig, id="simulacao-chart-2", config={"displayModeBar": False})


def build_filtros() -> dbc.Card:
    """Monta o card de filtros."""
    return dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Cenario", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="simulacao-filtro-cenario",
                                options=[{"label": v, "value": v} for v in ["Mantem Margem", "Mantem PPC"]],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Familia", className="text-muted small fw-medium mb-1"),
                            dbc.Input(id="simulacao-filtro-familia", placeholder="Todas", debounce=True),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Canal", className="text-muted small fw-medium mb-1"),
                            dbc.Input(id="simulacao-filtro-canal", placeholder="Todos", debounce=True),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Regiao", className="text-muted small fw-medium mb-1"),
                            dbc.Input(id="simulacao-filtro-regiao", placeholder="Todas", debounce=True),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Ano Transicao", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="simulacao-filtro-ano",
                                options=[{"label": str(a), "value": str(a)} for a in range(2026, 2034)],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-search me-1"), "Filtrar"],
                            id="simulacao-btn-filtrar",
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
