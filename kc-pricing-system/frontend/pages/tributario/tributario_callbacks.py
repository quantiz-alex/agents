"""Callbacks da pagina de Parametrizacao Tributaria."""

from typing import Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, no_update

from frontend.pages.tributario.tributario_components import build_grid, build_kpis
from frontend.pages.tributario.tributario_queries import carregar_parametros_tributarios


def register_callbacks() -> None:
    """Registra todos os callbacks da pagina de tributario."""

    @callback(
        Output("tributario-grid", "rowData"),
        Output("tributario-kpis-row", "children"),
        Input("tributario-btn-filtrar", "n_clicks"),
        State("tributario-filtro-ano", "value"),
        State("tributario-filtro-regime", "value"),
        prevent_initial_call=False,
    )
    def filtrar(
        n_clicks: Optional[int],
        ano: Optional[str],
        regime: Optional[str],
    ) -> tuple[list[dict], list]:
        df = carregar_parametros_tributarios(ano_vigencia=ano, regime=regime)
        return df.to_dict("records"), build_kpis(df)

    @callback(
        Output("tributario-modal-form", "is_open"),
        Input("tributario-btn-novo", "n_clicks"),
        Input("tributario-btn-modal-cancelar", "n_clicks"),
        Input("tributario-btn-modal-confirmar", "n_clicks"),
        State("tributario-modal-form", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_modal(
        n_novo: Optional[int],
        n_cancelar: Optional[int],
        n_confirmar: Optional[int],
        is_open: bool,
    ) -> bool:
        return not is_open

    @callback(
        Output("tributario-toast", "is_open"),
        Output("tributario-toast", "children"),
        Output("tributario-toast", "icon"),
        Input("tributario-btn-modal-confirmar", "n_clicks"),
        State("tributario-modal-ano", "value"),
        State("tributario-modal-regime", "value"),
        prevent_initial_call=True,
    )
    def confirmar_parametro(
        n_clicks: Optional[int],
        ano: Optional[str],
        regime: Optional[str],
    ) -> tuple[bool, str, str]:
        if not ano or not regime:
            return True, "Preencha os campos obrigatorios (Ano e Regime).", "danger"
        return True, f"Parametro para {ano} / {regime} salvo com sucesso (modo mock).", "success"

    @callback(
        Output("tributario-btn-exportar", "disabled"),
        Input("tributario-grid", "rowData"),
        prevent_initial_call=False,
    )
    def toggle_exportar(row_data: Optional[list]) -> bool:
        return not bool(row_data)
