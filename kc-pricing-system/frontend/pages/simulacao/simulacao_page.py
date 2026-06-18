"""Layout da pagina de Simulacao de Impactos."""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from frontend.pages.simulacao.simulacao_components import (
    build_chart_margem_cadeia,
    build_chart_receita_familia,
    build_filtros,
    build_grid,
    build_kpis,
)
from frontend.pages.simulacao.simulacao_queries import (
    carregar_cenarios,
    carregar_cenarios_itens,
)

dash.register_page(
    __name__,
    path="/simulacao",
    title="Simulacao de Impactos — KC Pricing",
    name="Simulacao de Impactos",
)


def layout() -> html.Div:
    """Retorna o layout da pagina de Simulacao de Impactos."""
    df_cenarios = carregar_cenarios()
    df_itens = carregar_cenarios_itens()

    return html.Div(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        html.H4(
                            [html.I(className="bi bi-sliders me-2"), "Simulacao de Impactos"],
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
                                        [html.I(className="bi bi-download me-1"), "Exportar Excel"],
                                        id="simulacao-btn-exportar",
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
                    build_kpis(df_cenarios, df_itens),
                    id="simulacao-kpis-row",
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
                                    [html.I(className="bi bi-bar-chart me-2"), "Impacto em Margem por Elo da Cadeia"],
                                    className="bg-white border-bottom fw-semibold",
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        html.Div(build_chart_margem_cadeia(df_itens), id="simulacao-chart-1-wrapper"),
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
                                    [html.I(className="bi bi-bar-chart-line me-2"), "Receita NIV Simulada por Familia"],
                                    className="bg-white border-bottom fw-semibold",
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        html.Div(build_chart_receita_familia(df_itens), id="simulacao-chart-2-wrapper"),
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

            # Grid
            dbc.Card(
                [
                    dbc.CardHeader(
                        [html.I(className="bi bi-table me-2"), "Resultados por SKU"],
                        className="bg-white border-bottom fw-semibold",
                    ),
                    dbc.CardBody(
                        dcc.Loading(
                            build_grid(df_itens),
                            type="circle",
                            color="#1045C8",
                        )
                    ),
                ],
                className="shadow-sm border-0 mb-3",
            ),

            # Toast
            dbc.Toast(
                id="simulacao-toast",
                header="Simulacao de Impactos",
                is_open=False,
                dismissable=True,
                duration=4000,
                style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999},
            ),
        ],
        className="page-wrapper px-4 py-3",
        style={"background": "#f8fafc", "minHeight": "100vh"},
    )
