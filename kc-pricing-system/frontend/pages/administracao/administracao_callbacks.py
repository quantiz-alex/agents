"""Callbacks da pagina de Administracao."""

from typing import Optional

from dash import Input, Output, State, callback, no_update

from frontend.pages.administracao.administracao_components import build_grid, build_kpis
from frontend.pages.administracao.administracao_queries import carregar_usuarios


def register_callbacks() -> None:
    """Registra todos os callbacks da pagina de administracao."""

    @callback(
        Output("administracao-grid", "rowData"),
        Output("administracao-kpis-row", "children"),
        Input("administracao-btn-filtrar", "n_clicks"),
        State("administracao-filtro-role", "value"),
        State("administracao-filtro-ativo", "value"),
        prevent_initial_call=False,
    )
    def filtrar(
        n_clicks: Optional[int],
        role: Optional[str],
        ativo: Optional[str],
    ) -> tuple[list[dict], list]:
        df = carregar_usuarios(role=role, ativo=ativo)
        return df.to_dict("records"), build_kpis(df)

    @callback(
        Output("administracao-modal-usuario", "is_open"),
        Input("administracao-btn-novo", "n_clicks"),
        Input("administracao-btn-modal-cancelar", "n_clicks"),
        Input("administracao-btn-modal-confirmar", "n_clicks"),
        State("administracao-modal-usuario", "is_open"),
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
        Output("administracao-toast", "is_open"),
        Output("administracao-toast", "children"),
        Output("administracao-toast", "icon"),
        Input("administracao-btn-modal-confirmar", "n_clicks"),
        State("administracao-modal-nome", "value"),
        State("administracao-modal-email", "value"),
        State("administracao-modal-role", "value"),
        prevent_initial_call=True,
    )
    def confirmar_usuario(
        n_clicks: Optional[int],
        nome: Optional[str],
        email: Optional[str],
        role: Optional[str],
    ) -> tuple[bool, str, str]:
        if not nome or not email or not role:
            return True, "Preencha todos os campos obrigatorios (Nome, Email e Perfil).", "danger"
        return True, f"Usuario '{nome}' criado com sucesso (modo mock).", "success"

    @callback(
        Output("administracao-btn-exportar", "disabled"),
        Input("administracao-grid", "rowData"),
        prevent_initial_call=False,
    )
    def toggle_exportar(row_data: Optional[list]) -> bool:
        return not bool(row_data)
