"""Callbacks da pagina de Parametrizacao de Pricing."""

from typing import Any, Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html, no_update

from frontend.pages.pricing.pricing_components import (
    build_grid_margens,
    build_grid_produtos,
    build_kpis,
)
from frontend.pages.pricing.pricing_queries import (
    carregar_margens_cadeia,
    carregar_produtos,
)


def register_callbacks() -> None:
    """Registra todos os callbacks da pagina de pricing."""

    @callback(
        Output("pricing-tabs-content", "children"),
        Output("pricing-kpis-row", "children"),
        Input("pricing-tabs", "active_tab"),
        Input("pricing-btn-filtrar", "n_clicks"),
        State("pricing-filtro-canal", "value"),
        State("pricing-filtro-regiao", "value"),
        State("pricing-filtro-familia", "value"),
        State("pricing-filtro-classificacao", "value"),
        prevent_initial_call=False,
    )
    def atualizar_conteudo(
        active_tab: str,
        n_clicks: Optional[int],
        canal: Optional[str],
        regiao: Optional[str],
        familia: Optional[str],
        classificacao: Optional[str],
    ) -> tuple[Any, list]:
        df_produtos = carregar_produtos(canal=canal or None, regiao=regiao or None, familia=familia or None, classificacao=classificacao)
        df_margens = carregar_margens_cadeia(canal=canal or None, familia=familia or None)
        kpis = build_kpis(df_produtos, df_margens)

        if active_tab == "tab-margens":
            grid = build_grid_margens(df_margens)
            content: Any = [
                dbc.Row(
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-pencil me-1"), "Nova Margem"],
                            id="pricing-btn-nova-margem",
                            color="primary",
                            size="sm",
                            className="mb-3",
                        ),
                    )
                ),
                grid,
            ]
        else:
            grid = build_grid_produtos(df_produtos)
            content = [
                dbc.Row(
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-pencil me-1"), "Editar Produto"],
                            id="pricing-btn-editar-produto",
                            color="primary",
                            size="sm",
                            className="mb-3",
                        ),
                    )
                ),
                grid,
            ]

        return content, kpis

    @callback(
        Output("pricing-modal-produto", "is_open"),
        Input("pricing-btn-modal-produto-cancelar", "n_clicks"),
        Input("pricing-btn-modal-produto-confirmar", "n_clicks"),
        State("pricing-modal-produto", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_modal_produto(
        n_cancelar: Optional[int],
        n_confirmar: Optional[int],
        is_open: bool,
    ) -> bool:
        return not is_open

    @callback(
        Output("pricing-modal-margem", "is_open"),
        Input("pricing-btn-modal-margem-cancelar", "n_clicks"),
        Input("pricing-btn-modal-margem-confirmar", "n_clicks"),
        State("pricing-modal-margem", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_modal_margem(
        n_cancelar: Optional[int],
        n_confirmar: Optional[int],
        is_open: bool,
    ) -> bool:
        return not is_open

    @callback(
        Output("pricing-toast", "is_open"),
        Output("pricing-toast", "children"),
        Output("pricing-toast", "icon"),
        Input("pricing-btn-modal-produto-confirmar", "n_clicks"),
        Input("pricing-btn-modal-margem-confirmar", "n_clicks"),
        prevent_initial_call=True,
    )
    def toast_confirmacao(
        n_produto: Optional[int],
        n_margem: Optional[int],
    ) -> tuple[bool, str, str]:
        return True, "Registro salvo com sucesso (modo mock).", "success"

    @callback(
        Output("pricing-btn-exportar", "disabled"),
        Input("pricing-tabs", "active_tab"),
        prevent_initial_call=False,
    )
    def toggle_exportar(active_tab: str) -> bool:
        return False
