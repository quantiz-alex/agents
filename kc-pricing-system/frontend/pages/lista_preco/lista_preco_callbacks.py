"""Callbacks da pagina de Lista de Precos Sell In."""

from typing import Any, Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html, no_update

from frontend.pages.lista_preco.lista_preco_components import (
    build_bar_chart_familia,
    build_bar_chart_variacao,
    build_grid,
    build_kpis,
)
from frontend.pages.lista_preco.lista_preco_queries import carregar_lista_preco_itens


def register_callbacks() -> None:
    """Registra todos os callbacks da pagina de lista de precos."""

    @callback(
        Output("lista-preco-grid", "rowData"),
        Output("lista-preco-kpis-row", "children"),
        Output("lista-preco-chart-1-wrapper", "children"),
        Output("lista-preco-chart-2-wrapper", "children"),
        Input("lista-preco-btn-filtrar", "n_clicks"),
        State("lista-preco-filtro-familia", "value"),
        State("lista-preco-filtro-canal", "value"),
        State("lista-preco-filtro-cap", "value"),
        State("lista-preco-filtro-aprovacao", "value"),
        prevent_initial_call=False,
    )
    def filtrar(
        n_clicks: Optional[int],
        familia: Optional[str],
        canal: Optional[str],
        status_cap: Optional[str],
        status_aprovacao: Optional[str],
    ) -> tuple[list[dict], list, Any, Any]:
        df = carregar_lista_preco_itens(
            familia=familia,
            canal=canal,
            status_cap=status_cap,
            status_aprovacao=status_aprovacao,
        )
        return (
            df.to_dict("records"),
            build_kpis(df),
            build_bar_chart_familia(df),
            build_bar_chart_variacao(df),
        )

    @callback(
        Output("lista-preco-modal-aprovacao", "is_open"),
        Input("lista-preco-btn-aprovar", "n_clicks"),
        Input("lista-preco-btn-rejeitar", "n_clicks"),
        Input("lista-preco-btn-modal-cancelar", "n_clicks"),
        Input("lista-preco-btn-modal-confirmar", "n_clicks"),
        State("lista-preco-modal-aprovacao", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_modal(
        n_aprovar: Optional[int],
        n_rejeitar: Optional[int],
        n_cancelar: Optional[int],
        n_confirmar: Optional[int],
        is_open: bool,
    ) -> bool:
        return not is_open

    @callback(
        Output("lista-preco-toast", "is_open"),
        Output("lista-preco-toast", "children"),
        Output("lista-preco-toast", "icon"),
        Input("lista-preco-btn-modal-confirmar", "n_clicks"),
        prevent_initial_call=True,
    )
    def confirmar_acao(n_clicks: Optional[int]) -> tuple[bool, str, str]:
        return True, "Acao registrada com sucesso (modo mock).", "success"

    @callback(
        Output("lista-preco-btn-exportar", "disabled"),
        Input("lista-preco-grid", "rowData"),
        prevent_initial_call=False,
    )
    def toggle_exportar(row_data: Optional[list]) -> bool:
        return not bool(row_data)
