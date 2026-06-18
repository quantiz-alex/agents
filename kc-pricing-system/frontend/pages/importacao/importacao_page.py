"""Layout da pagina de Importacao de Bases."""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from frontend.pages.importacao.importacao_components import (
    build_filtros,
    build_grid,
    build_kpis,
    build_modal_upload,
)
from frontend.pages.importacao.importacao_queries import carregar_importacoes

dash.register_page(
    __name__,
    path="/importacao",
    title="Importacao de Bases — KC Pricing",
    name="Importacao de Bases",
)


def layout() -> html.Div:
    """Retorna o layout da pagina de Importacao de Bases."""
    df = carregar_importacoes()

    return html.Div(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        html.H4(
                            [
                                html.I(className="bi bi-cloud-upload me-2"),
                                "Importacao de Bases",
                            ],
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
                                        [html.I(className="bi bi-cloud-upload me-1"), "Importar Arquivo"],
                                        id="importacao-btn-abrir-modal",
                                        color="primary",
                                        size="sm",
                                    ),
                                    width="auto",
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        [html.I(className="bi bi-download me-1"), "Exportar Historico"],
                                        id="importacao-btn-exportar",
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
                    id="importacao-kpis-row",
                    className="g-3 mb-3",
                ),
                type="circle",
                color="#1045C8",
            ),

            # Grid principal
            dbc.Card(
                [
                    dbc.CardHeader(
                        [html.I(className="bi bi-table me-2"), "Historico de Importacoes"],
                        className="bg-white border-bottom fw-semibold",
                    ),
                    dbc.CardBody(
                        dcc.Loading(
                            build_grid(df),
                            id="importacao-grid-loading",
                            type="circle",
                            color="#1045C8",
                        )
                    ),
                ],
                className="shadow-sm border-0 mb-3",
            ),

            # Modal de upload
            build_modal_upload(),

            # Toast de feedback
            dbc.Toast(
                id="importacao-toast",
                header="Importacao",
                is_open=False,
                dismissable=True,
                duration=4000,
                icon="success",
                style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999},
            ),
        ],
        className="page-wrapper px-4 py-3",
        style={"background": "#f8fafc", "minHeight": "100vh"},
    )
