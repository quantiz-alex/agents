"""Callbacks globais do Assistente de Pricing — registrados UMA vez pelo app.py.

Donos únicos: assistant-history (perguntas/limpar/logout/troca de usuário/reset), assistant-action-event (intenção de navegação → guard_routes),
{"type":"demo-scenario-event","page":"assistant"} (proposta → dispatcher do cenário no shell). Toast de ação expirada usa shell-toast (allow_duplicate).
Seleção de produto das páginas chega por {"type":"assistant-select","page":ALL} (lista vazia quando ausente).
Motor: Claude (services/assistant_llm) para texto livre quando configurado; senão, ou em falha da API, motor local (services/pricing_assistant).
"""
from __future__ import annotations

import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dash import ALL, Input, Output, State, callback, ctx, no_update

from frontend.components.pricing_assistant_components import focus_chip, render_messages, suggestion_buttons
from frontend.components.ui_components import notify
from frontend.services import assistant_data as ad
from frontend.services import assistant_llm
from frontend.services import pricing_assistant as pa
from frontend.services.assistant_analyses import ANALYSIS_HANDLERS

_CATALOG = Path(__file__).resolve().parents[1] / "docs" / "assistant_catalog.yaml"
# >>> PARAMETRIZAR: telas que consomem o cenário compartilhado (skill-demo-scenario); {} se o projeto não tem cenário.
SCENARIO_PAGES = {"configuracao-precos", "tabela-vigente", "estrategia-capitaes", "pedidos"}
_PAGE_LABELS = {"home": "Início"}


@lru_cache(maxsize=1)
def catalog() -> dict:
    c = yaml.safe_load(_CATALOG.read_text(encoding="utf-8"))
    pa.validate_catalog(c, ANALYSIS_HANDLERS)
    return c


def _page(pathname: str | None) -> str:
    return (pathname or "/home").strip("/") or "home"


def page_label(page: str) -> str:
    if page in _PAGE_LABELS:
        return _PAGE_LABELS[page]
    try:
        from frontend.services.access import page as page_def

        return page_def(page).get("title") or page
    except KeyError:
        return page.replace("-", " ").capitalize()


_ENTITY_NAMES = {"produto": "Produto", "pedido": "Pedido", "lote": "Lote", "cliente": "Cliente", "promocao": "Promoção", "combinacao": "Item simulado"}


def focus_label(context: dict) -> str | None:
    """Rótulo do item aberto no Detalhar (ex.: "Pedido PED-0001 · Mercado X")."""
    e = context.get("entity") or {}
    if not e.get("type"):
        return None
    return f"{_ENTITY_NAMES.get(e['type'], e['type'].capitalize())} {e.get('label') or e.get('id')}"


def product_label(context: dict) -> str | None:
    try:
        pr = ad.produto(context)
    except (ValueError, TypeError):
        return None
    return str(pr["sku"]) if pr else None


def _da_tela(page: str, valores: list | None, ids: list | None) -> dict:
    """Valor do store pattern-matching da tela atual (assistant-select / assistant-params)."""
    for i, data in zip(ids or [], valores or []):
        if i.get("page") == page and data:
            return data
    return {}


def build_context(pathname: str | None, user: dict | None, scenario: dict | None, session: dict | None, selects: list | None,
                  select_ids: list | None, params: list | None = None, params_ids: list | None = None) -> dict:
    """Contexto do assistente: tela, usuário, item em foco (assistant-select) e estado da tela (assistant-params: filtros/parâmetros)."""
    page = _page(pathname)
    sel = _da_tela(page, selects, select_ids)
    st = scenario or {}
    return {"page": page, "role": (user or {}).get("role"), "email": (user or {}).get("email"), "filters": sel.get("filters") or {},
            "product_id": sel.get("product_id"), "scenario_key": "configuracao-precos" if page in SCENARIO_PAGES else None,
            "scenario_view": "draft" if page == "configuracao-precos" else "applied", "revision": st.get("revision"),
            "scenario_state": st, "session": session, "entity": sel.get("entity") or None, "params": _da_tela(page, params, params_ids) or None}


@lru_cache(maxsize=1)
def scope_vocab() -> frozenset:
    """Termos do domínio: glossário + catálogo + nomes reais de categorias, produtos, SKUs, canais, regiões e segmentos."""
    from frontend.services.data import names, produtos

    extra = [*produtos()["nome"].astype(str), *produtos()["sku"].astype(str)]
    for t in ("categoria", "subcategoria", "canal", "regiao", "segmento"):
        try:
            extra += list(names(t).values())
        except (KeyError, FileNotFoundError):
            continue
    return frozenset(pa.scope_vocabulary(catalog(), extra))


def responder(pergunta: str, analysis_id: str | None, context: dict, history: list | None) -> dict:
    """Sugestão/opção clicada → análise direta. Texto livre: trava de escopo (sem custo) → Claude (se ativo), com queda para o motor local."""
    cat = catalog()
    if not analysis_id and not pa.in_scope(pergunta, scope_vocab(), has_history=bool(history)):
        return pa.out_of_scope_response(cat, context)
    if analysis_id or not assistant_llm.enabled():
        return pa.answer(pergunta, cat, ANALYSIS_HANDLERS, context, analysis_id)
    try:
        return assistant_llm.answer(pergunta, cat, ANALYSIS_HANDLERS, context, history,
                                    page_label=page_label(context["page"]), product_label=focus_label(context) or product_label(context))
    except assistant_llm.LLMUnavailable:
        return {**pa.answer(pergunta, cat, ANALYSIS_HANDLERS, context), "note": "IA indisponível no momento — resposta do modo local."}


SELECT = [State({"type": "assistant-select", "page": ALL}, "data"), State({"type": "assistant-select", "page": ALL}, "id"),
          State({"type": "assistant-params", "page": ALL}, "data"), State({"type": "assistant-params", "page": ALL}, "id")]


def register_assistant_callbacks() -> None:
    @callback(Output("assistant-shell", "style"), Output("assistant-suggestions", "children"), Output("assistant-focus", "children"),
              Input("url", "pathname"), Input("current-user", "data"), Input({"type": "assistant-select", "page": ALL}, "data"),
              State({"type": "assistant-select", "page": ALL}, "id"))
    def visibilidade(pathname: str | None, user: dict | None, selects: list, select_ids: list) -> tuple:
        """Sugestões da tela + do item aberto no Detalhar (que vem primeiro); o chip "Em foco" mostra o que o assistente vai analisar."""
        if not user or pathname in ("/login", "/", None):
            return {"display": "none"}, [], None
        ctxt = build_context(pathname, user, None, None, selects, select_ids)
        return {}, suggestion_buttons(pa.available(catalog(), ctxt)), focus_chip(focus_label(ctxt))

    @callback(Output("assistant-panel", "is_open", allow_duplicate=True), Input({"type": "assistant-ask", "source": ALL}, "n_clicks"),
              prevent_initial_call=True)
    def perguntar_sobre_item(clicks: list) -> Any:
        """Botão "Perguntar ao Assistente" dentro de um Detalhar: abre o assistente por cima, com o item já em foco."""
        return True if ctx.triggered and ctx.triggered[0].get("value") else no_update

    @callback(Output("assistant-panel", "is_open"), Input("assistant-open", "n_clicks"), State("assistant-panel", "is_open"), prevent_initial_call=True)
    def abrir(n: int | None, aberto: bool) -> bool:
        return not aberto if n else no_update

    @callback(Output("assistant-history", "data"), Output("assistant-question", "value"),
              Input("assistant-send", "n_clicks"), Input("assistant-question", "n_submit"), Input({"type": "assistant-suggestion", "analysis": ALL}, "n_clicks"),
              Input({"type": "assistant-option", "analysis": ALL, "turn": ALL}, "n_clicks"),
              Input("assistant-clear", "n_clicks"), Input("current-user", "data"), Input("demo-active", "data"),
              State("assistant-question", "value"), State("url", "pathname"), State("demo-scenario", "data"), State("demo-session", "data"),
              State("assistant-history", "data"), *SELECT, prevent_initial_call=True,
              running=[(Output("assistant-send", "disabled"), True, False), (Output("assistant-question", "disabled"), True, False)])
    def perguntar(n_send: int | None, n_sub: int | None, sugest: list, opcoes: list, n_clear: int | None, user: dict | None, active: dict | None,
                  pergunta: str | None, pathname: str | None, scenario: dict | None, session: dict | None, history: list | None,
                  *sel: list) -> tuple:
        trig = ctx.triggered_id
        if trig == "assistant-clear" or (trig == "current-user" and not user) or (trig == "demo-active" and (active or {}).get("reset")):
            return [], ""
        if trig == "current-user":   # outro usuário entrou sem passar pelo logout: não herda a conversa
            email = (user or {}).get("email")
            return ([], "") if any(t.get("user") not in (None, email) for t in history or []) else (no_update, no_update)
        if trig == "demo-active" or not user:
            return no_update, no_update
        analysis_id = None
        if isinstance(trig, dict):
            if not (ctx.triggered and ctx.triggered[0].get("value")):   # botão recém-criado (n_clicks=0), não um clique
                return no_update, no_update
            analysis_id = trig["analysis"]
            item = next((a for a in catalog()["analyses"] if a["id"] == analysis_id), None)
            pergunta = item["questions"][0] if item else ""
        elif not (pergunta or "").strip():
            return no_update, no_update
        context = build_context(pathname, user, scenario, session, *sel)
        resp = responder((pergunta or "").strip(), analysis_id, context, history)
        meta = {"page": context["page"], "page_label": page_label(context["page"]), "product_label": focus_label(context) or product_label(context),
                "engine": resp.get("engine", "local"), "user": user.get("email")}
        return pa.append_history(history, (pergunta or "").strip(), resp, meta), ""

    @callback(Output("assistant-messages", "children"), Input("assistant-history", "data"), Input("url", "pathname"), Input("demo-active", "data"),
              Input("demo-scenario", "data"), Input({"type": "assistant-select", "page": ALL}, "data"),
              Input({"type": "assistant-params", "page": ALL}, "data"),
              State("current-user", "data"), State("demo-session", "data"), State({"type": "assistant-select", "page": ALL}, "id"),
              State({"type": "assistant-params", "page": ALL}, "id"))
    def mensagens(history: list | None, pathname: str | None, _a: Any, scenario: dict | None, selects: list, params: list, user: dict | None,
                  session: dict | None, select_ids: list, params_ids: list) -> list:
        """Re-renderiza também quando a seleção, os parâmetros da tela ou o cenário mudam, para desabilitar na hora as ações que expiraram."""
        fp = pa.context_fingerprint(build_context(pathname, user, scenario, session, selects, select_ids, params, params_ids)) if user else None
        return render_messages(history or [], fp)

    @callback(Output("assistant-action-event", "data"), Output({"type": "demo-scenario-event", "page": "assistant"}, "data"),
              Output("assistant-panel", "is_open", allow_duplicate=True),
              Output("shell-toast", "is_open", allow_duplicate=True), Output("shell-toast", "children", allow_duplicate=True),
              Output("shell-toast", "icon", allow_duplicate=True),
              Input({"type": "assistant-action", "action": ALL, "turn": ALL}, "n_clicks"), State("assistant-history", "data"), State("url", "pathname"),
              State("current-user", "data"), State("demo-scenario", "data"), State("demo-session", "data"), *SELECT, prevent_initial_call=True)
    def acao(clicks: list, history: list | None, pathname: str | None, user: dict | None, scenario: dict | None, session: dict | None,
             *sel: list) -> tuple:
        nada = (no_update,) * 6
        trig = ctx.triggered_id
        if not isinstance(trig, dict) or not any(clicks or []) or not history:
            return nada
        resp = (history[-1] or {}).get("response") or {}
        context = build_context(pathname, user, scenario, session, *sel)
        action = next((a for a in resp.get("actions") or [] if a["id"] == trig["action"]), None)
        if not action:
            return nada
        if resp.get("context_fingerprint") != pa.context_fingerprint(context):
            return no_update, no_update, no_update, *notify("O contexto mudou desde a resposta (tela, produto ou cenário). Pergunte de novo para recalcular.", "warning")
        if action["kind"] == "simulate":
            try:
                ev = pa.proposal_event(resp, context, uuid.uuid4().hex, action["id"])
            except ValueError as exc:
                return no_update, no_update, no_update, *notify(str(exc), "warning")
            nav = {"id": uuid.uuid4().hex, "target": "configuracao-precos", "context": {"scenario_view": "draft", "origem": "assistente"}}
            return nav, ev, False, no_update, no_update, no_update
        nav_ctx = dict((resp.get("data") or {}).get("nav_context") or {})
        if action["id"] == "ver_tabela_rascunho":
            nav_ctx = {"scenario_key": "configuracao-precos", "scenario_view": "draft", "revision": context.get("revision"), "scope": {}}
        return {"id": uuid.uuid4().hex, "target": action["target"], "context": nav_ctx}, no_update, False, no_update, no_update, no_update
