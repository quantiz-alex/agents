"""Componentes visuais para a pagina de Importacao de Bases."""

from typing import Any

import dash_ag_grid
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html


_PRIMARY = "#1045C8"


def build_grid(df: pd.DataFrame) -> Any:
    """Monta o AG Grid de historico de importacoes."""
    column_defs = [
        {"field": "id", "headerName": "ID", "width": 80, "type": "numericColumn"},
        {"field": "fonte", "headerName": "Fonte", "minWidth": 160},
        {"field": "nome_arquivo", "headerName": "Arquivo", "minWidth": 220},
        {
            "field": "data_importacao",
            "headerName": "Data/Hora",
            "minWidth": 180,
            "valueFormatter": {
                "function": "params.value ? new Date(params.value).toLocaleString('pt-BR') : ''"
            },
        },
        {
            "field": "total_linhas",
            "headerName": "Linhas",
            "width": 100,
            "type": "numericColumn",
        },
        {
            "field": "status",
            "headerName": "Status",
            "width": 120,
            "cellStyle": {
                "function": (
                    "params.value === 'Sucesso' ? {'color': '#10b981', 'fontWeight': '600'} : "
                    "params.value === 'Erro' ? {'color': '#ef4444', 'fontWeight': '600'} : "
                    "{'color': '#f59e0b', 'fontWeight': '600'}"
                )
            },
        },
        {"field": "observacao", "headerName": "Observacao", "minWidth": 200},
    ]

    return dash_ag_grid.AgGrid(
        id="importacao-grid",
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
    """Monta os cards de KPI da pagina de importacao."""
    from frontend.pages.importacao.importacao_queries import calcular_kpis_importacao

    kpis = calcular_kpis_importacao(df)

    cards = [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Total de Importacoes", className="text-muted small mb-1"),
                    html.H4(str(kpis["total_registros"]), className="fw-bold mb-0", style={"color": _PRIMARY}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": _PRIMARY + " !important"},
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Ultima Carga", className="text-muted small mb-1"),
                    html.H6(
                        str(kpis["ultima_carga"])[:19] if kpis["ultima_carga"] != "—" else "—",
                        className="fw-semibold mb-0",
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
                    html.P("Cargas com Sucesso", className="text-muted small mb-1"),
                    html.H4(str(kpis["sucesso"]), className="fw-bold mb-0", style={"color": "#10b981"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#10b981 !important"},
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Cargas com Erro", className="text-muted small mb-1"),
                    html.H4(str(kpis["erros"]), className="fw-bold mb-0", style={"color": "#ef4444"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#ef4444 !important"},
            ),
            md=3,
        ),
    ]
    return cards


def build_filtros() -> dbc.Card:
    """Monta o card de filtros compactos."""
    return dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Fonte", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="importacao-filtro-fonte",
                                options=[
                                    {"label": v, "value": v}
                                    for v in [
                                        "Nielsen Retail",
                                        "Nielsen Scantrack",
                                        "Precos ERP",
                                        "PL",
                                        "Cadastros",
                                        "DePara",
                                    ]
                                ],
                                placeholder="Todas",
                                clearable=True,
                                searchable=True,
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Periodo", className="text-muted small fw-medium mb-1"),
                            dcc.DatePickerRange(
                                id="importacao-filtro-data",
                                display_format="DD/MM/YYYY",
                                clearable=True,
                                start_date_placeholder_text="Inicio",
                                end_date_placeholder_text="Fim",
                                style={"width": "100%"},
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Status", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="importacao-filtro-status",
                                options=[
                                    {"label": v, "value": v}
                                    for v in ["Sucesso", "Erro", "Processando"]
                                ],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-search me-1"), "Filtrar"],
                            id="importacao-btn-filtrar",
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


def build_modal_upload() -> dbc.Modal:
    """Modal de upload de arquivo."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Importar Arquivo")),
            dbc.ModalBody(
                [
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Fonte *", className="fw-medium"),
                            dcc.Dropdown(
                                id="importacao-modal-fonte",
                                options=[
                                    {"label": v, "value": v}
                                    for v in [
                                        "Nielsen Retail",
                                        "Nielsen Scantrack",
                                        "Precos ERP",
                                        "PL",
                                        "Cadastros",
                                        "DePara",
                                    ]
                                ],
                                placeholder="Selecione a fonte...",
                            ),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Observacao", className="fw-medium"),
                            dbc.Textarea(
                                id="importacao-modal-observacao",
                                placeholder="Observacao opcional sobre esta carga...",
                                rows=3,
                            ),
                        ]),
                    ], className="mb-3"),
                    dbc.Alert(id="importacao-modal-alerta", is_open=False, dismissable=True),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancelar",
                        id="importacao-btn-modal-cancelar",
                        color="secondary",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-cloud-upload me-1"), "Confirmar Importacao"],
                        id="importacao-btn-modal-confirmar",
                        color="primary",
                    ),
                ]
            ),
        ],
        id="importacao-modal-upload",
        is_open=False,
        size="lg",
    )
