"""Painel global do Assistente de Pricing (montado uma vez no shell; oculto no login).

Histórico global da sessão: cada turno mostra a tela/produto em que foi feito; turnos antigos ficam recolhidos e só o
último exibe tabela e ações (Abrir / Simular proposta). Motor: Claude (se configurado) ou local — ver services/assistant_llm.py.
"""
from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html

from frontend.components.ui_components import data_table, status_badge

_ROW_KEYS = ("itens", "resultados", "cenarios", "categorias", "timeline")
_SMALL = {"fontSize": "0.7rem"}


def assistant_panel(ai_enabled: bool | None = None) -> html.Div:
    """Montar uma vez no shell; callbacks registrados uma vez em frontend/assistant_callbacks.py."""
    if ai_enabled is None:
        from frontend.services import assistant_llm

        ai_enabled = assistant_llm.enabled()
    if ai_enabled:
        modo = [status_badge("IA (Claude)", "info"),
                html.Span(" · entende perguntas livres; números sempre calculados pelas análises sobre os dados da demonstração.",
                          className="text-muted", style={"fontSize": "0.72rem"})]
    else:
        modo = [status_badge("Modo local", "neutral"),
                html.Span(" · análises calculadas sobre os dados da demonstração; sem IA generativa nem internet.",
                          className="text-muted", style={"fontSize": "0.72rem"})]
    return html.Div([
        dcc.Store(id="assistant-history", storage_type="session", data=[]),
        dcc.Store(id="assistant-action-event", storage_type="memory"),
        dcc.Store(id={"type": "demo-scenario-event", "page": "assistant"}, storage_type="memory"),
        dbc.Button([html.I(className="bi bi-stars me-2"), "Assistente de Pricing"], id="assistant-open", color="primary", n_clicks=0,
                   className="shadow fw-semibold"),
        dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Assistente de Pricing")), dbc.ModalBody([
            html.P("Explore os dados e simule oportunidades nesta demonstração.", className="text-muted small mb-1"),
            html.Div(modo, className="mb-3"),
            html.Div(id="assistant-focus", className="mb-2"),
            html.Div("Perguntas sugeridas para esta tela", className="small fw-semibold mb-1"),
            html.Div(id="assistant-suggestions", className="d-flex flex-wrap gap-2 mb-3"),
            dcc.Loading(html.Div(id="assistant-messages", role="log", **{"aria-live": "polite"}), type="dot", color="#2563eb"),
            dbc.Label("Sua pergunta", html_for="assistant-question", className="small fw-semibold mt-2"),
            dbc.Input(id="assistant-question", type="text", maxLength=500, n_submit=0,
                      placeholder="Pergunte sobre margens, alertas, cenários..." if ai_enabled else "Use uma das perguntas sugeridas ou escreva a sua..."),
            html.Div([dbc.Button("Analisar", id="assistant-send", n_clicks=0, color="primary", size="sm", className="mt-2 fw-semibold"),
                      dbc.Button("Limpar conversa", id="assistant-clear", n_clicks=0, outline=True, color="secondary", size="sm", className="mt-2 ms-2")]),
        ])], id="assistant-panel", is_open=False, centered=True, scrollable=True, size="xl", zindex=1070),   # acima do Detalhar aberto
    ], id="assistant-shell", style={"display": "none"})


def focus_chip(label: str | None) -> Any:
    """Item aberto no Detalhar que o assistente está considerando."""
    if not label:
        return html.Div("Dica: abra o Detalhar de um item para o assistente analisá-lo.", className="text-muted", style={"fontSize": "0.72rem"})
    return html.Div([html.I(className="bi bi-bullseye me-1"), html.Span("Em foco: ", className="fw-semibold"), label],
                    className="assistant-focus-chip")


def suggestion_buttons(items: list[dict]) -> list:
    if not items:
        return [html.Span("Nenhuma análise disponível nesta tela.", className="text-muted small")]
    return [dbc.Button(a["questions"][0], id={"type": "assistant-suggestion", "analysis": a["id"]}, n_clicks=0, size="sm", color="primary", outline=True,
                       className="text-start") for a in items]


def _tabela(rows: list[dict], idx: int) -> Any:
    df = pd.DataFrame(rows)
    if df.empty:
        return None
    return data_table(df, f"assistant-table-{idx}", height=f"{min(260, 50 + 42 * len(df))}px", page_size=10)


def _chips(turn: dict) -> html.Div:
    r = turn.get("response") or {}
    chips = []
    if turn.get("page_label") or turn.get("page"):
        chips.append(html.Span([html.I(className="bi bi-window me-1"), turn.get("page_label") or turn.get("page")], className="assistant-chip"))
    if turn.get("product_label"):
        chips.append(html.Span([html.I(className="bi bi-box me-1"), turn["product_label"]], className="assistant-chip"))
    engine = turn.get("engine") or r.get("engine")
    if engine:
        chips.append(html.Span("Claude" if engine == "claude" else "Local", className="assistant-chip assistant-chip-engine"))
    if turn.get("ts"):
        chips.append(html.Span(turn["ts"], className="text-muted", style=_SMALL))
    return html.Div(chips, className="d-flex flex-wrap align-items-center gap-1")


def _message(r: dict) -> Any:
    msg = r.get("message", "")
    if r.get("engine") == "claude":
        return dcc.Markdown(msg, className="small assistant-md mb-1")
    return html.Div(msg, className="small")


def _turn_body(turn: dict, i: int, is_last: bool, atual: bool) -> list:
    r = turn.get("response") or {}
    out: list = [_message(r)]
    if r.get("note"):
        out.append(html.Div(r["note"], className="text-muted fst-italic", style=_SMALL))
    if not is_last:
        return out
    if r.get("status") == "ok":
        data = r.get("data") or {}
        rows = next((data[k] for k in _ROW_KEYS if data.get(k)), None)
        if rows:
            out.append(_tabela(rows[:10], i))
        if r.get("analyses_used"):
            out.append(html.Div("Análises usadas: " + "; ".join(map(str, r["analyses_used"])), className="text-muted", style=_SMALL))
        if r.get("assumptions"):
            out.append(html.Div("Hipóteses: " + "; ".join(map(str, r["assumptions"])), className="text-muted", style=_SMALL))
        if r.get("sources"):
            out.append(html.Div("Fontes: " + ", ".join(map(str, r["sources"][:6])), className="text-muted", style=_SMALL))
        acts = [dbc.Button(("Simular proposta" if a["kind"] == "simulate" else f"Abrir {a.get('target', '')}".replace("-", " ")),
                           id={"type": "assistant-action", "action": a["id"], "turn": i}, n_clicks=0, size="sm",
                           color="primary" if a["kind"] == "simulate" else "secondary", outline=a["kind"] != "simulate", className="me-2 mt-1",
                           disabled=not atual) for a in r.get("actions") or []]
        if acts:
            out.append(html.Div(acts))
        if not atual and r.get("actions"):
            out.append(html.Div("Contexto mudou (tela, filtros, produto ou revisão) — pergunte de novo para recalcular.", className="text-warning small"))
    elif r.get("status") == "answer" and r.get("analyses_used"):
        out.append(html.Div("Análises usadas: " + "; ".join(map(str, r["analyses_used"])), className="text-muted", style=_SMALL))
    elif r.get("options"):
        out.append(html.Div([dbc.Button(o["question"], id={"type": "assistant-option", "analysis": o["id"], "turn": i}, n_clicks=0, size="sm",
                                        color="primary", outline=True, className="text-start") for o in r["options"]],
                            className="d-flex flex-wrap gap-2 mt-1"))
    return out


def render_messages(history: list[dict], current_fp: str | None) -> list:
    """Turnos antigos recolhidos (pergunta + tela); o último aberto com tabela/ações. Ações só ativas se o contexto não mudou."""
    out = []
    n = len(history or [])
    for i, turn in enumerate(history or []):
        r = turn.get("response") or {}
        is_last = i == n - 1
        atual = is_last and r.get("context_fingerprint") == current_fp
        head = html.Div([html.Div(turn.get("question"), className="small fw-semibold text-primary"), _chips(turn)],
                        className="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-1")
        if is_last:
            out.append(html.Div([head, *_turn_body(turn, i, True, atual)], className="p-2 rounded border bg-white"))
        else:
            out.append(html.Details([html.Summary(head, className="assistant-summary"), *_turn_body(turn, i, False, False)],
                                    className="p-2 rounded border bg-white assistant-old"))
    return out
