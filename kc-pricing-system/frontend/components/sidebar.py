"""Sidebar fixa do KC Pricing System."""

import os

import dash_bootstrap_components as dbc
from dash import html

_PRIMARY = "#1045C8"
_LOGO_PATH = "logo.png"
_DISPLAY_NAME = "KC Pricing"

_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
_LOGO_EXISTS = os.path.isfile(os.path.join(_ASSETS_DIR, _LOGO_PATH))

_NAV_PAGES = [
    ("/importacao",   "cloud-upload", "Importacao de Bases"),
    ("/tributario",   "calculator",   "Param. Tributaria"),
    ("/pricing",      "gear",         "Param. de Pricing"),
    ("/lista-preco",  "tag",          "Lista de Precos"),
    ("/simulacao",    "sliders",      "Simulacao de Impactos"),
    ("/administracao","people",       "Administracao"),
]

CONTENT_STYLE: dict = {"marginLeft": "240px"}
CONTENT_FULL_STYLE: dict = {"marginLeft": "0"}


def build_sidebar(pathname: str = "/") -> html.Div:
    """Constroi a sidebar fixa com navegacao estilo pill."""

    nav_links = [
        dbc.NavLink(
            [html.I(className=f"bi bi-{icon}"), label],
            href=href,
            active="exact",
            className="nav-link",
        )
        for href, icon, label in _NAV_PAGES
    ]

    logo_mark = (
        html.Img(
            src=f"/assets/{_LOGO_PATH}",
            height=30,
            style={"objectFit": "contain", "maxWidth": "110px"},
        )
        if _LOGO_EXISTS
        else html.Div(
            _DISPLAY_NAME[:2].upper(),
            style={
                "width": "30px",
                "height": "30px",
                "borderRadius": "8px",
                "background": _PRIMARY,
                "color": "#ffffff",
                "fontSize": "0.75rem",
                "fontWeight": "800",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "flexShrink": "0",
            },
        )
    )

    return html.Div(
        [
            # Topo: logo mark + nome
            html.Div(
                [
                    logo_mark,
                    html.Span(
                        _DISPLAY_NAME,
                        style={
                            "marginLeft": "0.625rem",
                            "fontWeight": "700",
                            "fontSize": "1rem",
                            "color": "#0f172a",
                            "letterSpacing": "-0.02em",
                        },
                    ),
                ],
                style={
                    "padding": "1.25rem 1.25rem 1rem",
                    "display": "flex",
                    "alignItems": "center",
                },
            ),

            # Separador sutil
            html.Hr(style={"margin": "0 0.75rem 0.5rem", "borderColor": "#e2e8f0", "opacity": "1"}),

            # Navegacao
            html.Nav(
                nav_links,
                className="sidebar-nav flex-grow-1 py-2",
            ),

            # Rodape
            html.Div(
                [
                    html.Span("Desenvolvido por", style={"display": "block"}),
                    html.Span("Quantiz Pricing Solution", style={"display": "block", "fontWeight": "500"}),
                ],
                style={
                    "color": "#94a3b8",
                    "fontSize": "0.72rem",
                    "padding": "0.875rem 1.25rem",
                    "borderTop": "1px solid #e2e8f0",
                    "lineHeight": "1.6",
                },
            ),
        ],
        style={
            "width": "240px",
            "position": "fixed",
            "top": 0,
            "left": 0,
            "height": "100vh",
            "background": "#ffffff",
            "borderRight": "1px solid #e2e8f0",
            "boxShadow": "2px 0 8px rgba(0,0,0,0.04)",
            "display": "flex",
            "flexDirection": "column",
            "overflowY": "auto",
            "zIndex": 100,
        },
    )


def register_sidebar_callbacks() -> None:
    pass
