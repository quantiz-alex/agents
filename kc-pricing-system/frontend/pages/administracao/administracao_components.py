"""Componentes visuais para a pagina de Administracao."""

from typing import Any

import dash_ag_grid
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html

_PRIMARY = "#1045C8"


def build_grid(df: pd.DataFrame) -> Any:
    """Monta o AG Grid de usuarios."""
    column_defs = [
        {"field": "id", "headerName": "ID", "width": 80, "type": "numericColumn"},
        {"field": "nome", "headerName": "Nome", "minWidth": 180},
        {"field": "email", "headerName": "Email", "minWidth": 220},
        {
            "field": "role",
            "headerName": "Perfil",
            "width": 160,
            "cellStyle": {
                "function": (
                    "params.value === 'admin' ? {'color': '#1045C8', 'fontWeight': '600'} : "
                    "params.value === 'gestor_pricing' ? {'color': '#f59e0b', 'fontWeight': '600'} : "
                    "{'color': '#374151'}"
                )
            },
        },
        {
            "field": "ativo",
            "headerName": "Status",
            "width": 110,
            "valueFormatter": {"function": "params.value === 1 ? 'Ativo' : 'Inativo'"},
            "cellStyle": {
                "function": "params.value === 1 ? {'color': '#10b981', 'fontWeight': '600'} : {'color': '#ef4444', 'fontWeight': '600'}"
            },
        },
        {
            "field": "created_at",
            "headerName": "Criado em",
            "minWidth": 160,
            "valueFormatter": {
                "function": "params.value ? new Date(params.value).toLocaleDateString('pt-BR') : ''"
            },
        },
    ]

    return dash_ag_grid.AgGrid(
        id="administracao-grid",
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
    """Monta cards de KPI de administracao."""
    from frontend.pages.administracao.administracao_queries import calcular_kpis_administracao

    kpis = calcular_kpis_administracao(df)

    return [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Total de Usuarios", className="text-muted small mb-1"),
                    html.H4(str(kpis["total"]), className="fw-bold mb-0", style={"color": _PRIMARY}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": _PRIMARY + " !important"},
            ),
            md=2,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Usuarios Ativos", className="text-muted small mb-1"),
                    html.H4(str(kpis["ativos"]), className="fw-bold mb-0", style={"color": "#10b981"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#10b981 !important"},
            ),
            md=2,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Admins", className="text-muted small mb-1"),
                    html.H4(str(kpis["admins"]), className="fw-bold mb-0", style={"color": _PRIMARY}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#06b6d4 !important"},
            ),
            md=2,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Gestores de Pricing", className="text-muted small mb-1"),
                    html.H4(str(kpis["gestores"]), className="fw-bold mb-0", style={"color": "#f59e0b"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#f59e0b !important"},
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Analistas de Pricing", className="text-muted small mb-1"),
                    html.H4(str(kpis["analistas"]), className="fw-bold mb-0", style={"color": "#8b5cf6"}),
                ]),
                className="shadow-sm border-0 border-start border-4 mb-3 h-100",
                style={"borderColor": "#8b5cf6 !important"},
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
                            dbc.Label("Perfil", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="administracao-filtro-role",
                                options=[
                                    {"label": "Admin", "value": "admin"},
                                    {"label": "Gestor de Pricing", "value": "gestor_pricing"},
                                    {"label": "Analista de Pricing", "value": "analista_pricing"},
                                ],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Status", className="text-muted small fw-medium mb-1"),
                            dcc.Dropdown(
                                id="administracao-filtro-ativo",
                                options=[{"label": v, "value": v} for v in ["Sim", "Nao"]],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-search me-1"), "Filtrar"],
                            id="administracao-btn-filtrar",
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


def build_modal_usuario() -> dbc.Modal:
    """Modal de cadastro de novo usuario."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Novo Usuario")),
            dbc.ModalBody(
                [
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Nome Completo *", className="fw-medium"),
                            dbc.Input(id="administracao-modal-nome", placeholder="Nome completo do usuario"),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Email *", className="fw-medium"),
                            dbc.Input(id="administracao-modal-email", type="email", placeholder="email@empresa.com"),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Perfil *", className="fw-medium"),
                            dcc.Dropdown(
                                id="administracao-modal-role",
                                options=[
                                    {"label": "Admin", "value": "admin"},
                                    {"label": "Gestor de Pricing", "value": "gestor_pricing"},
                                    {"label": "Analista de Pricing", "value": "analista_pricing"},
                                ],
                                placeholder="Selecione o perfil...",
                            ),
                        ]),
                    ], className="mb-3"),
                    dbc.Alert(
                        "Em modo mock, uma senha temporaria e gerada automaticamente.",
                        color="info",
                        className="small",
                    ),
                    dbc.Alert(id="administracao-modal-alerta", is_open=False, dismissable=True),
                ]
            ),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="administracao-btn-modal-cancelar", color="secondary", outline=True, className="me-2"),
                dbc.Button([html.I(className="bi bi-person-plus me-1"), "Criar Usuario"], id="administracao-btn-modal-confirmar", color="primary"),
            ]),
        ],
        id="administracao-modal-usuario",
        is_open=False,
        size="lg",
    )
