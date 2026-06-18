"""Layout da pagina de Lista de Precos Sell In."""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from frontend.pages.lista_preco.lista_preco_components import (
    build_bar_chart_familia,
    build_bar_chart_variacao,
    build_filtros,
    build_grid,
    build_kpis,
    build_modal_aprovacao,
)
from frontend.pages.lista_preco.lista_preco_queries import (
    carregar_canais_disponiveis,
    carregar_familias_disponiveis,
    carregar_lista_preco_itens,
)

dash.register_page(
    __name__,
    path="/lista-preco",
    title="Lista de Precos Sell In — KC Pricing",
    name="Lista de Precos Sell In",
)


def layout() -> html.Div:
    """Retorna o layout da pagina de Lista de Precos Sell In."""
    df = carregar_lista_preco_itens()
    familias = carregar_familias_disponiveis()
    canais = carregar_canais_disponiveis()

    return html.Div(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        html.H4(
                            [html.I(className="bi bi-tag me-2"), "Lista de Precos Sell In"],
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
                                        [html.I(className="bi bi-check-circle me-1"), "Aprovar Lista"],
                                        id="lista-preco-btn-aprovar",
                                        color="success",
                                        size="sm",
                                    ),
                                    width="auto",
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        [html.I(className="bi bi-x-circle me-1"), "Rejeitar Lista"],
                                        id="lista-preco-btn-rejeitar",
                                        color="danger",
                                        outline=True,
                                        size="sm",
                                    ),
                                    width="auto",
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        [html.I(className="bi bi-download me-1"), "Exportar Excel"],
                                        id="lista-preco-btn-exportar",
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
            build_filtros(familias, canais),

            # KPIs
            dcc.Loading(
                dbc.Row(
                    build_kpis(df),
                    id="lista-preco-kpis-row",
                    className="g-3 mb-3",
                ),
                type="circle",
                color="#1045C8",
            ),

            # Charts
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    [html.I(className="bi bi-bar-chart me-2"), "Preco Atual vs. Sell In NIV por Familia"],
                                    className="bg-white border-bottom fw-semibold",
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        html.Div(build_bar_chart_familia(df), id="lista-preco-chart-1-wrapper"),
                                        type="circle",
                                        color="#1045C8",
                                    )
                                ),
                            ],
                            className="shadow-sm border-0 mb-3",
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    [html.I(className="bi bi-bar-chart-steps me-2"), "Distribuicao de Variacao de Preco"],
                                    className="bg-white border-bottom fw-semibold",
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        html.Div(build_bar_chart_variacao(df), id="lista-preco-chart-2-wrapper"),
                                        type="circle",
                                        color="#1045C8",
                                    )
                                ),
                            ],
                            className="shadow-sm border-0 mb-3",
                        ),
                        md=6,
                    ),
                ],
                className="g-3",
            ),

            # Grid principal
            dbc.Card(
                [
                    dbc.CardHeader(
                        [html.I(className="bi bi-table me-2"), "Itens da Lista de Precos"],
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
            build_modal_aprovacao(),

            # Toast
            dbc.Toast(
                id="lista-preco-toast",
                header="Lista de Precos",
                is_open=False,
                dismissable=True,
                duration=4000,
                style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999},
            ),
        ],
        className="page-wrapper px-4 py-3",
        style={"background": "#f8fafc", "minHeight": "100vh"},
    )
