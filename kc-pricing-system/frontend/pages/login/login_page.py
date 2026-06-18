"""Layout da pagina de Login do KC Pricing System."""

import dash
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(
    __name__,
    path="/login",
    title="Login — KC Pricing",
    name="Login",
)

_PRIMARY = "#1045C8"


def layout() -> html.Div:
    """Retorna o layout fullscreen da pagina de login."""
    return html.Div(
        [
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                # Logo / titulo
                                html.Div(
                                    [
                                        html.Img(
                                            src="/assets/logo.png",
                                            height=48,
                                            style={"objectFit": "contain", "maxWidth": "160px", "marginBottom": "0.5rem"},
                                        ),
                                        html.H4(
                                            "KC Pricing System",
                                            className="fw-bold mb-1",
                                            style={"color": "#1e293b"},
                                        ),
                                        html.P(
                                            "Formacao de Precos Sell In",
                                            className="text-muted small mb-4",
                                        ),
                                    ],
                                    className="text-center",
                                ),

                                # Email
                                html.Div(
                                    [
                                        dbc.Label("Email", html_for="login-email", className="fw-medium"),
                                        dbc.Input(
                                            id="login-email",
                                            type="email",
                                            placeholder="seu@email.com",
                                            className="mb-3",
                                            n_submit=0,
                                            autofocus=True,
                                        ),
                                    ]
                                ),

                                # Senha
                                html.Div(
                                    [
                                        dbc.Label("Senha", html_for="login-senha", className="fw-medium"),
                                        dbc.Input(
                                            id="login-senha",
                                            type="password",
                                            placeholder="Sua senha",
                                            className="mb-3",
                                            n_submit=0,
                                        ),
                                    ]
                                ),

                                # Botao Entrar
                                dbc.Button(
                                    "Entrar",
                                    id="login-btn",
                                    color="primary",
                                    className="w-100 mb-3",
                                    style={"backgroundColor": _PRIMARY, "borderColor": _PRIMARY},
                                    n_clicks=0,
                                ),

                                # Alerta de erro
                                dbc.Alert(
                                    id="login-alert",
                                    is_open=False,
                                    dismissable=True,
                                    color="danger",
                                    className="mb-2",
                                ),

                                # Dica modo dev
                                dbc.Alert(
                                    [
                                        html.Strong("Modo Mock: "),
                                        "Use qualquer email do arquivo usuarios.csv. Qualquer senha e aceita.",
                                    ],
                                    color="info",
                                    className="small mb-0",
                                ),
                            ],
                            className="p-4",
                        ),
                        className="shadow border-0",
                        style={"maxWidth": "400px", "width": "100%"},
                    ),
                    width="auto",
                    className="d-flex align-items-center justify-content-center",
                    style={"minHeight": "100vh"},
                ),
                justify="center",
                align="center",
                className="m-0",
                style={"minHeight": "100vh"},
            )
        ],
        style={
            "background": "linear-gradient(135deg, #1e293b, #0f172a)",
            "minHeight": "100vh",
        },
    )
