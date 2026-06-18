"""Aplicacao principal do KC Pricing System — Dash Frontend."""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html, no_update

from frontend.components.sidebar import (
    CONTENT_FULL_STYLE,
    CONTENT_STYLE,
    build_sidebar,
    register_sidebar_callbacks,
)

# 1. Instanciar app PRIMEIRO — obrigatorio antes dos imports de paginas
app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
    ],
    suppress_callback_exceptions=True,
    title="KC Pricing System",
)
server = app.server

# 2. Importar layouts APOS app (aciona dash.register_page() em cada modulo)
from frontend.pages.login.login_page import layout as login_layout  # noqa: E402
from frontend.pages.importacao.importacao_page import layout as importacao_layout  # noqa: E402
from frontend.pages.tributario.tributario_page import layout as tributario_layout  # noqa: E402
from frontend.pages.pricing.pricing_page import layout as pricing_layout  # noqa: E402
from frontend.pages.lista_preco.lista_preco_page import layout as lista_preco_layout  # noqa: E402
from frontend.pages.simulacao.simulacao_page import layout as simulacao_layout  # noqa: E402
from frontend.pages.administracao.administracao_page import layout as administracao_layout  # noqa: E402

_PAGE_LAYOUTS: dict = {
    "/": login_layout,
    "/login": login_layout,
    "/importacao": importacao_layout,
    "/tributario": tributario_layout,
    "/pricing": pricing_layout,
    "/lista-preco": lista_preco_layout,
    "/simulacao": simulacao_layout,
    "/administracao": administracao_layout,
}

_ROTAS_PROTEGIDAS: list[str] = [
    "/importacao",
    "/tributario",
    "/pricing",
    "/lista-preco",
    "/simulacao",
    "/administracao",
]

# 3. Importar callbacks APOS app
from frontend.pages.login.login_callbacks import register_callbacks as login_register  # noqa: E402
from frontend.pages.importacao.importacao_callbacks import register_callbacks as importacao_register  # noqa: E402
from frontend.pages.tributario.tributario_callbacks import register_callbacks as tributario_register  # noqa: E402
from frontend.pages.pricing.pricing_callbacks import register_callbacks as pricing_register  # noqa: E402
from frontend.pages.lista_preco.lista_preco_callbacks import register_callbacks as lista_preco_register  # noqa: E402
from frontend.pages.simulacao.simulacao_callbacks import register_callbacks as simulacao_register  # noqa: E402
from frontend.pages.administracao.administracao_callbacks import register_callbacks as administracao_register  # noqa: E402

# 4. Layout principal — SEM dash.page_container
app.layout = html.Div(
    [
        dcc.Store(id="current-user", storage_type="session"),
        dcc.Location(id="url", refresh=False),
        html.Div(id="sidebar-wrapper"),
        html.Div(
            html.Div(id="page-content"),
            id="main-content",
        ),
    ]
)

# 5. Registrar callbacks de todas as paginas
login_register()
importacao_register()
tributario_register()
pricing_register()
lista_preco_register()
simulacao_register()
administracao_register()
register_sidebar_callbacks()


# 6. Render de pagina — substitui dash.page_container
@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    prevent_initial_call=False,
)
def render_page_content(pathname: str):
    """Renderiza o layout correspondente ao pathname atual."""
    layout_fn = _PAGE_LAYOUTS.get(pathname)
    if layout_fn is None:
        return dbc.Alert(
            [
                html.H5("Pagina nao encontrada", className="fw-semibold"),
                html.P(f"A rota '{pathname}' nao existe nesta aplicacao."),
            ],
            color="warning",
            className="m-4",
        )
    return layout_fn() if callable(layout_fn) else layout_fn


# 7. Guard routes — UNICO callback que escreve em url.pathname
@callback(
    Output("url", "pathname"),
    Input("url", "pathname"),
    Input("current-user", "data"),
    prevent_initial_call=False,
)
def guard_routes(pathname: str, user_data: dict):
    """Controla acesso autenticado: redireciona para login se nao autenticado."""
    if pathname in ("/", None):
        return "/importacao" if user_data else "/login"
    if pathname == "/login":
        return "/importacao" if user_data else no_update
    if pathname in _ROTAS_PROTEGIDAS:
        return no_update if user_data else "/login"
    return no_update


# 8. Toggle sidebar — exibe/oculta conforme autenticacao e passa pathname
@callback(
    Output("sidebar-wrapper", "children"),
    Output("main-content", "style"),
    Input("url", "pathname"),
    Input("current-user", "data"),
    prevent_initial_call=False,
)
def toggle_sidebar(pathname: str, user_data: dict):
    """Exibe sidebar apenas em rotas autenticadas."""
    if pathname in ("/login", "/", None) or not user_data:
        return [], CONTENT_FULL_STYLE
    return build_sidebar(pathname), CONTENT_STYLE


if __name__ == "__main__":
    app.run(debug=True, port=8050)
