"""Layout da pagina de Parametrizacao de Pricing."""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from frontend.pages.pricing.pricing_components import (
    build_filtros,
    build_grid_margens,
    build_grid_produtos,
    build_kpis,
    build_modal_margem,
    build_modal_produto,
)
from frontend.pages.pricing.pricing_queries import (
    carregar_margens_cadeia,
    carregar_produtos,
)

dash.register_page(
    __name__,
    path="/pricing",
    title="Parametrizacao de Pricing — KC Pricing",
    name="Parametrizacao de Pricing",
)


def layout() -> html.Div:
    """Retorna o layout da pagina de Parametrizacao de Pricing."""
    df_produtos = carregar_produtos()
    df_margens = carregar_margens_cadeia()

    return html.Div(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        html.H4(
                            [html.I(className="bi bi-gear me-2"), "Parametrizacao de Pricing"],
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
                                        [html.I(className="bi bi-download me-1"), "Exportar"],
                                        id="pricing-btn-exportar",
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
                    build_kpis(df_produtos, df_margens),
                    id="pricing-kpis-row",
                    className="g-3 mb-3",
                ),
                type="circle",
                color="#1045C8",
            ),

            # Tabs: Produtos / Margens da Cadeia
            dbc.Card(
                [
                    dbc.CardHeader(
                        dbc.Tabs(
                            [
                                dbc.Tab(label="Produtos / Capitaes", tab_id="tab-produtos"),
                                dbc.Tab(label="Margens da Cadeia", tab_id="tab-margens"),
                            ],
                            id="pricing-tabs",
                            active_tab="tab-produtos",
                        ),
                        className="bg-white border-bottom",
                    ),
                    dbc.CardBody(
                        dcc.Loading(
                            html.Div(id="pricing-tabs-content"),
                            type="circle",
                            color="#1045C8",
                        )
                    ),
                ],
                className="shadow-sm border-0 mb-3",
            ),

            # Modais
            build_modal_produto(),
            build_modal_margem(),

            # Toast
            dbc.Toast(
                id="pricing-toast",
                header="Parametrizacao de Pricing",
                is_open=False,
                dismissable=True,
                duration=4000,
                style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999},
            ),
        ],
        className="page-wrapper px-4 py-3",
        style={"background": "#f8fafc", "minHeight": "100vh"},
    )
