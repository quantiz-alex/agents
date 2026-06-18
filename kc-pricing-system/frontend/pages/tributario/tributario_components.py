"""Componentes visuais para a pagina de Parametrizacao Tributaria."""

from typing import Any

import dash_ag_grid
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html

_PRIMARY = "#1045C8"

_PCT_FORMATTER = {"function": "params.value != null ? (params.value * 100).toFixed(2) + '%' : ''"}


def build_grid(df: pd.DataFrame) -> Any:
    """Monta o AG Grid de parametros tributarios."""
    column_defs = [
        {"field": "id", "headerName": "ID", "width": 80, "type": "numericColumn"},
        {"field": "ano_vigencia", "headerName": "Ano", "width": 100},
        {"field": "regime", "headerName": "Regime", "width": 120},
        {"field": "aliquota_ibs", "headerName": "IBS", "width": 100, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "aliquota_cbs", "headerName": "CBS", "width": 100, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "aliquota_icms", "headerName": "ICMS", "width": 100, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "aliquota_pis", "headerName": "PIS", "width": 100, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "aliquota_cofins", "headerName": "COFINS", "width": 110, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "aliquota_is", "headerName": "Imp. Seletivo", "width": 130, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "credito_pis_cofins", "headerName": "Cred. PIS/COFINS", "width": 150, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {"field": "debito_icms", "headerName": "Deb. ICMS", "width": 120, "type": "numericColumn", "valueFormatter": _PCT_FORMATTER},
        {
            "field": "ativo",
            "headerName": "Ativo",
            "width": 90,
            "cellStyle": {
                "function": "params.value === 1 ? {'color': '#10b981', 'fontWeight': '600'} : {'color': '#6b7280'}"
            },
            "valueFormatter": {"function": "params.value === 1 ? 'Sim' : 'Nao'"},
        },
    ]

    return dash_ag_grid.AgGrid(
        id="tributario-grid",
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
    """Monta cards de KPI."""
    from frontend.pages.tributario.tributario_queries import calcular_kpis_tributario

    kpis = calcular_kpis_tributario(df)

    return [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Total de Parametros", className="text-muted small mb-1"),
                    html.H4(str(kpis["total"]), className="fw-bold mb-0", style={"color": _PRIMARY}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": _PRIMARY + " !important"},
            ),
            md=4,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Parametros Ativos", className="text-muted small mb-1"),
                    html.H4(str(kpis["ativos"]), className="fw-bold mb-0", style={"color": "#10b981"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#10b981 !important"},
            ),
            md=4,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Anos Cobertos", className="text-muted small mb-1"),
                    html.H4(str(kpis["anos_cobertos"]), className="fw-bold mb-0", style={"color": "#06b6d4"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#06b6d4 !important"},
            ),
            md=4,
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
                            dbc.Label("Ano de Vigencia", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="tributario-filtro-ano",
                                options=[
                                    {"label": str(a), "value": str(a)}
                                    for a in range(2026, 2034)
                                ],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Regime", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="tributario-filtro-regime",
                                options=[
                                    {"label": v, "value": v}
                                    for v in ["Legado", "Reforma"]
                                ],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-search me-1"), "Filtrar"],
                            id="tributario-btn-filtrar",
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


def build_modal_parametro() -> dbc.Modal:
    """Modal de cadastro de novo parametro tributario."""
    anos = [{"label": str(a), "value": str(a)} for a in range(2026, 2034)]

    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Novo Parametro Tributario")),
            dbc.ModalBody(
                [
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Ano de Vigencia *", className="fw-medium"),
                            dcc.Dropdown(id="tributario-modal-ano", options=anos, placeholder="Selecione..."),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Regime *", className="fw-medium"),
                            dcc.Dropdown(
                                id="tributario-modal-regime",
                                options=[{"label": v, "value": v} for v in ["Legado", "Reforma"]],
                                placeholder="Selecione...",
                            ),
                        ], md=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("Aliquota IBS *", className="fw-medium"), dbc.Input(id="tributario-modal-ibs", type="number", min=0, max=1, step=0.0001, placeholder="0.0000")], md=4),
                        dbc.Col([dbc.Label("Aliquota CBS *", className="fw-medium"), dbc.Input(id="tributario-modal-cbs", type="number", min=0, max=1, step=0.0001, placeholder="0.0000")], md=4),
                        dbc.Col([dbc.Label("Aliquota ICMS *", className="fw-medium"), dbc.Input(id="tributario-modal-icms", type="number", min=0, max=1, step=0.0001, placeholder="0.0000")], md=4),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("Aliquota PIS *", className="fw-medium"), dbc.Input(id="tributario-modal-pis", type="number", min=0, max=1, step=0.0001, placeholder="0.0000")], md=4),
                        dbc.Col([dbc.Label("Aliquota COFINS *", className="fw-medium"), dbc.Input(id="tributario-modal-cofins", type="number", min=0, max=1, step=0.0001, placeholder="0.0000")], md=4),
                        dbc.Col([dbc.Label("Imp. Seletivo *", className="fw-medium"), dbc.Input(id="tributario-modal-is", type="number", min=0, max=1, step=0.0001, placeholder="0.0000")], md=4),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([dbc.Label("Credito PIS/COFINS", className="fw-medium"), dbc.Input(id="tributario-modal-cred-pis", type="number", min=0, max=1, step=0.0001, placeholder="0.0000")], md=6),
                        dbc.Col([dbc.Label("Debito ICMS", className="fw-medium"), dbc.Input(id="tributario-modal-deb-icms", type="number", min=0, max=1, step=0.0001, placeholder="0.0000")], md=6),
                    ], className="mb-3"),
                    dbc.Alert(id="tributario-modal-alerta", is_open=False, dismissable=True),
                ]
            ),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="tributario-btn-modal-cancelar", color="secondary", outline=True, className="me-2"),
                dbc.Button([html.I(className="bi bi-save me-1"), "Salvar"], id="tributario-btn-modal-confirmar", color="primary"),
            ]),
        ],
        id="tributario-modal-form",
        is_open=False,
        size="xl",
    )
