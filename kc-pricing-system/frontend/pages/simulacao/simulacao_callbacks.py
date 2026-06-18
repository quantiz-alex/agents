"""Callbacks da pagina de Simulacao de Impactos."""

from typing import Any, Optional

from dash import Input, Output, State, callback, no_update

from frontend.pages.simulacao.simulacao_components import (
    build_chart_margem_cadeia,
    build_chart_receita_familia,
    build_grid,
    build_kpis,
)
from frontend.pages.simulacao.simulacao_queries import (
    carregar_cenarios,
    carregar_cenarios_itens,
)


def register_callbacks() -> None:
    """Registra todos os callbacks da pagina de simulacao."""

    @callback(
        Output("simulacao-grid", "rowData"),
        Output("simulacao-kpis-row", "children"),
        Output("simulacao-chart-1-wrapper", "children"),
        Output("simulacao-chart-2-wrapper", "children"),
        Input("simulacao-btn-filtrar", "n_clicks"),
        State("simulacao-filtro-cenario", "value"),
        State("simulacao-filtro-familia", "value"),
        State("simulacao-filtro-canal", "value"),
        State("simulacao-filtro-regiao", "value"),
        State("simulacao-filtro-ano", "value"),
        prevent_initial_call=False,
    )
    def filtrar(
        n_clicks: Optional[int],
        cenario: Optional[str],
        familia: Optional[str],
        canal: Optional[str],
        regiao: Optional[str],
        ano: Optional[str],
    ) -> tuple[list[dict], list, Any, Any]:
        df_cenarios = carregar_cenarios(tipo_cenario=cenario)
        df_itens = carregar_cenarios_itens(
            familia=familia or None,
            canal=canal or None,
            regiao=regiao or None,
            tipo_cenario=cenario,
        )

        return (
            df_itens.to_dict("records"),
            build_kpis(df_cenarios, df_itens),
            build_chart_margem_cadeia(df_itens),
            build_chart_receita_familia(df_itens),
        )

    @callback(
        Output("simulacao-btn-exportar", "disabled"),
        Input("simulacao-grid", "rowData"),
        prevent_initial_call=False,
    )
    def toggle_exportar(row_data: Optional[list]) -> bool:
        return not bool(row_data)
