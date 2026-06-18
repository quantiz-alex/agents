"""Callbacks da pagina de Importacao de Bases."""

from typing import Any, Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, no_update

from frontend.pages.importacao.importacao_components import build_grid, build_kpis
from frontend.pages.importacao.importacao_queries import carregar_importacoes


def register_callbacks() -> None:
    """Registra todos os callbacks da pagina de importacao."""

    @callback(
        Output("importacao-grid", "rowData"),
        Output("importacao-kpis-row", "children"),
        Input("importacao-btn-filtrar", "n_clicks"),
        State("importacao-filtro-fonte", "value"),
        State("importacao-filtro-data", "start_date"),
        State("importacao-filtro-data", "end_date"),
        State("importacao-filtro-status", "value"),
        prevent_initial_call=False,
    )
    def filtrar(
        n_clicks: Optional[int],
        fonte: Optional[str],
        data_inicio: Optional[str],
        data_fim: Optional[str],
        status: Optional[str],
    ) -> tuple[list[dict], list]:
        df = carregar_importacoes(
            fonte=fonte,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
        )
        return df.to_dict("records"), build_kpis(df)

    @callback(
        Output("importacao-modal-upload", "is_open"),
        Input("importacao-btn-abrir-modal", "n_clicks"),
        Input("importacao-btn-modal-cancelar", "n_clicks"),
        Input("importacao-btn-modal-confirmar", "n_clicks"),
        State("importacao-modal-upload", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_modal(
        n_abrir: Optional[int],
        n_cancelar: Optional[int],
        n_confirmar: Optional[int],
        is_open: bool,
    ) -> bool:
        return not is_open

    @callback(
        Output("importacao-toast", "is_open"),
        Output("importacao-toast", "children"),
        Output("importacao-toast", "icon"),
        Input("importacao-btn-modal-confirmar", "n_clicks"),
        State("importacao-modal-fonte", "value"),
        prevent_initial_call=True,
    )
    def confirmar_importacao(
        n_clicks: Optional[int],
        fonte: Optional[str],
    ) -> tuple[bool, str, str]:
        if not fonte:
            return True, "Selecione uma fonte antes de confirmar.", "danger"
        return True, f"Importacao de '{fonte}' registrada com sucesso (modo mock).", "success"

    @callback(
        Output("importacao-btn-exportar", "disabled"),
        Input("importacao-grid", "rowData"),
        prevent_initial_call=False,
    )
    def toggle_exportar(row_data: Optional[list]) -> bool:
        return not bool(row_data)
