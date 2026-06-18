"""Componentes visuais para a pagina de Parametrizacao de Pricing."""

from typing import Any

import dash_ag_grid
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html

_PRIMARY = "#1045C8"
_PCT_FORMATTER = {"function": "params.value != null ? (params.value * 100).toFixed(2) + '%' : ''"}
_DEC4_FORMATTER = {"function": "params.value != null ? parseFloat(params.value).toFixed(4) : ''"}
_CURRENCY_FORMATTER = {"function": "params.value != null ? 'R$ ' + parseFloat(params.value).toLocaleString('pt-BR', {minimumFractionDigits: 2}) : ''"}


def build_grid_produtos(df: pd.DataFrame) -> Any:
    """Monta o AG Grid de produtos."""
    column_defs = [
        {"field": "id", "headerName": "ID", "width": 80, "type": "numericColumn"},
        {"field": "sku", "headerName": "SKU", "width": 120},
        {"field": "descricao", "headerName": "Descricao", "minWidth": 200},
        {"field": "familia", "headerName": "Familia", "width": 140},
        {"field": "embalagem", "headerName": "Embalagem", "width": 160},
        {
            "field": "classificacao",
            "headerName": "Classificacao",
            "width": 140,
            "cellStyle": {
                "function": (
                    "params.value === 'Capitao' ? {'color': '#1045C8', 'fontWeight': '600'} : "
                    "params.value === 'MainOffender' ? {'color': '#f59e0b', 'fontWeight': '600'} : "
                    "{'color': '#6b7280'}"
                )
            },
        },
        {"field": "canal", "headerName": "Canal", "width": 120},
        {"field": "regiao", "headerName": "Regiao", "width": 120},
        {"field": "preco_atual", "headerName": "Preco Atual", "width": 130, "type": "numericColumn", "valueFormatter": _CURRENCY_FORMATTER},
        {
            "field": "ativo",
            "headerName": "Ativo",
            "width": 90,
            "valueFormatter": {"function": "params.value === 1 ? 'Sim' : 'Nao'"},
            "cellStyle": {
                "function": "params.value === 1 ? {'color': '#10b981', 'fontWeight': '600'} : {'color': '#6b7280'}"
            },
        },
    ]

    return dash_ag_grid.AgGrid(
        id="pricing-grid",
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


def build_grid_margens(df: pd.DataFrame) -> Any:
    """Monta o AG Grid de margens da cadeia."""
    column_defs = [
        {"field": "id", "headerName": "ID", "width": 80, "type": "numericColumn"},
        {"field": "familia", "headerName": "Familia", "width": 140},
        {"field": "canal", "headerName": "Canal", "width": 120},
        {"field": "margem_industria", "headerName": "Mg. Industria", "width": 130, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "margem_distribuidor", "headerName": "Mg. Distribuidor", "width": 150, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "margem_varejo", "headerName": "Mg. Varejo", "width": 120, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "price_index", "headerName": "Price Index", "width": 120, "type": "numericColumn", "valueFormatter": _DEC4_FORMATTER},
        {"field": "relatividade", "headerName": "Relatividade", "width": 120, "type": "numericColumn", "valueFormatter": _DEC4_FORMATTER},
        {"field": "vigencia_inicio", "headerName": "Vigencia Inicio", "width": 140},
        {"field": "vigencia_fim", "headerName": "Vigencia Fim", "width": 130},
    ]

    return dash_ag_grid.AgGrid(
        id="pricing-grid-margens",
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


def build_kpis(df_produtos: pd.DataFrame, df_margens: pd.DataFrame) -> list:
    """Monta cards de KPI."""
    from frontend.pages.pricing.pricing_queries import calcular_kpis_pricing

    kpis = calcular_kpis_pricing(df_produtos, df_margens)

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
                    html.P("Capitaes Definidos", className="text-muted small mb-1"),
                    html.H4(str(kpis["capitaes"]), className="fw-bold mb-0", style={"color": "#1045C8"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#06b6d4 !important"},
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Familias Distintas", className="text-muted small mb-1"),
                    html.H4(str(kpis["familias"]), className="fw-bold mb-0", style={"color": "#f59e0b"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#f59e0b !important"},
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Canais", className="text-muted small mb-1"),
                    html.H4(str(kpis["canais"]), className="fw-bold mb-0", style={"color": "#10b981"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#10b981 !important"},
            ),
            md=3,
        ),
    ]


def build_filtros() -> dbc.Card:
    """Monta o card de filtros."""
    return dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Canal", className="text-muted small fw-medium mb-1"),
                            dbc.Input(id="pricing-filtro-canal", placeholder="Todos", debounce=True),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Regiao", className="text-muted small fw-medium mb-1"),
                            dbc.Input(id="pricing-filtro-regiao", placeholder="Todas", debounce=True),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Familia", className="text-muted small fw-medium mb-1"),
                            dbc.Input(id="pricing-filtro-familia", placeholder="Todas", debounce=True),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Classificacao", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="pricing-filtro-classificacao",
                                options=[
                                    {"label": v, "value": v}
                                    for v in ["Capitao", "MainOffender", "Seguidor"]
                                ],
                                placeholder="Todas",
                                clearable=True,
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-search me-1"), "Filtrar"],
                            id="pricing-btn-filtrar",
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


def build_modal_produto() -> dbc.Modal:
    """Modal de edicao de produto."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Editar Produto")),
            dbc.ModalBody(
                [
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Classificacao *", className="fw-medium"),
                            dcc.Dropdown(
                                id="pricing-modal-classificacao",
                                options=[{"label": v, "value": v} for v in ["Capitao", "MainOffender", "Seguidor"]],
                                placeholder="Selecione...",
                            ),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Canal *", className="fw-medium"),
                            dbc.Input(id="pricing-modal-canal", placeholder="Ex: Varejo"),
                        ], md=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Regiao", className="fw-medium"),
                            dbc.Input(id="pricing-modal-regiao", placeholder="Ex: Sudeste"),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Preco Atual", className="fw-medium"),
                            dbc.Input(id="pricing-modal-preco", type="number", min=0, step=0.0001, placeholder="0.0000"),
                        ], md=6),
                    ], className="mb-3"),
                    dbc.Alert(id="pricing-modal-alerta-produto", is_open=False, dismissable=True),
                ]
            ),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="pricing-btn-modal-produto-cancelar", color="secondary", outline=True, className="me-2"),
                dbc.Button([html.I(className="bi bi-save me-1"), "Salvar"], id="pricing-btn-modal-produto-confirmar", color="primary"),
            ]),
        ],
        id="pricing-modal-produto",
        is_open=False,
        size="lg",
    )


def build_modal_margem() -> dbc.Modal:
    """Modal de edicao de margem da cadeia."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Editar Margem da Cadeia")),
            dbc.ModalBody(
                [
                    dbc.Row([
                        dbc.Col([dbc.Label("Familia *", className="fw-medium"), dbc.Input(id="pricing-modal-margem-familia", placeholder="Ex: Bebidas")], md=6),
                        dbc.Col([dbc.Label("Canal *", className="fw-medium"), dbc.Input(id="pricing-modal-margem-canal", placeholder="Ex: Varejo")], md=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("Mg. Industria *", className="fw-medium"), dbc.Input(id="pricing-modal-margem-ind", type="number", min=0, max=1, step=0.0001)], md=4),
                        dbc.Col([dbc.Label("Mg. Distribuidor *", className="fw-medium"), dbc.Input(id="pricing-modal-margem-dist", type="number", min=0, max=1, step=0.0001)], md=4),
                        dbc.Col([dbc.Label("Mg. Varejo *", className="fw-medium"), dbc.Input(id="pricing-modal-margem-var", type="number", min=0, max=1, step=0.0001)], md=4),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("Price Index *", className="fw-medium"), dbc.Input(id="pricing-modal-price-index", type="number", min=0, step=0.0001)], md=6),
                        dbc.Col([dbc.Label("Relatividade *", className="fw-medium"), dbc.Input(id="pricing-modal-relatividade", type="number", min=0, step=0.0001)], md=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("Vigencia Inicio *", className="fw-medium"), dcc.DatePickerSingle(id="pricing-modal-vigencia-inicio", display_format="DD/MM/YYYY")], md=6),
                        dbc.Col([dbc.Label("Vigencia Fim", className="fw-medium"), dcc.DatePickerSingle(id="pricing-modal-vigencia-fim", display_format="DD/MM/YYYY", clearable=True)], md=6),
                    ], className="mb-3"),
                    dbc.Alert(id="pricing-modal-alerta-margem", is_open=False, dismissable=True),
                ]
            ),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="pricing-btn-modal-margem-cancelar", color="secondary", outline=True, className="me-2"),
                dbc.Button([html.I(className="bi bi-save me-1"), "Salvar"], id="pricing-btn-modal-margem-confirmar", color="primary"),
            ]),
        ],
        id="pricing-modal-margem",
        is_open=False,
        size="xl",
    )
