"""Layout da pagina de Parametrizacao Tributaria."""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from frontend.pages.tributario.tributario_components import (
    build_filtros,
    build_grid,
    build_kpis,
    build_modal_parametro,
)
from frontend.pages.tributario.tributario_queries import carregar_parametros_tributarios

dash.register_page(
    __name__,
    path="/tributario",
    title="Parametrizacao Tributaria — KC Pricing",
    name="Parametrizacao Tributaria",
)


def layout() -> html.Div:
    """Retorna o layout da pagina de Parametrizacao Tributaria."""
    df = carregar_parametros_tributarios()

    return html.Div(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        html.H4(
                            [html.I(className="bi bi-calculator me-2"), "Parametrizacao Tributaria"],
                            className="fw-semibold mb-0",
                            style={"color": "#1e293b"},
                        ),
                        className="align-self-center",
                    ),
                    dbc.Col(
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Button(
                                        [html.I(className="bi bi-plus-circle me-1"), "Novo Parametro"],
                                        id="tributario-btn-novo",
                                        color="primary",
                                        size="sm",
                                    ),
                                    width="auto",
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        [html.I(className="bi bi-download me-1"), "Exportar"],
                                        id="tributario-btn-exportar",
                                        color="secondary",
                                        outline=True,
                                        size="sm",
                                    ),
                                    width="auto",
                                ),
                            ],
                            className="g-2 justify-content-end",
                        ),
                        className="text-end",
                    ),
                ],
                className="mb-3 align-items-center",
            ),

            # Filtros
            build_filtros(),

            # KPIs
            dcc.Loading(
                dbc.Row(
                    build_kpis(df),
                    id="tributario-kpis-row",
                    className="g-3 mb-3",
                ),
                type="circle",
                color="#1045C8",
            ),

            # Grid principal
            dbc.Card(
                [
                    dbc.CardHeader(
                        [html.I(className="bi bi-table me-2"), "Parametros Tributarios"],
                        className="bg-white border-bottom fw-semibold",
                    ),
                    dbc.CardBody(
                        dcc.Loading(
                            build_grid(df),
                            type="circle",
                            color="#1045C8",
                        )
                    ),
                ],
                className="shadow-sm border-0 mb-3",
            ),

            # Modal
            build_modal_parametro(),

            # Toast
            dbc.Toast(
                id="tributario-toast",
                header="Parametrizacao Tributaria",
                is_open=False,
                dismissable=True,
                duration=4000,
                style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999},
            ),
        ],
        className="page-wrapper px-4 py-3",
        style={"background": "#f8fafc", "minHeight": "100vh"},
    )
