"""Painel global do assistente local; copiar para frontend/components/."""
from dash import dcc, html
import dash_bootstrap_components as dbc


def assistant_panel() -> html.Div:
    """Montar uma vez no shell; callbacks registrados uma vez pelo frontend-builder."""
    return html.Div([
        dcc.Store(id="assistant-history", storage_type="session", data=[]),
        dcc.Store(id="assistant-response", storage_type="memory"),
        dcc.Store(id="assistant-context", storage_type="memory", data={}),
        dcc.Store(id="assistant-action-event", storage_type="memory"),
        dbc.Button("Assistente de Pricing", id="assistant-open", color="primary", n_clicks=0),
        dbc.Offcanvas([
            html.P("Explore os dados e simule oportunidades nesta demonstração.", className="text-muted small"),
            html.Div(id="assistant-suggestions", className="d-flex flex-wrap gap-2 mb-3"),
            html.Div(id="assistant-messages", role="log", **{"aria-live": "polite"}),
            html.Div(id="assistant-results"),
            dbc.Label("Sua pergunta", html_for="assistant-question"),
            dbc.Input(id="assistant-question", type="text", maxLength=500, n_submit=0),
            dbc.Button("Analisar", id="assistant-send", n_clicks=0, color="primary", className="mt-2"),
            dbc.Button("Limpar conversa", id="assistant-clear", n_clicks=0, outline=True,
                       color="secondary", className="mt-2 ms-2"),
        ], id="assistant-panel", title="Assistente de Pricing", is_open=False, placement="end"),
    ], id="assistant-shell", style={"display": "none"})
