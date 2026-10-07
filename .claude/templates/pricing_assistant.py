"""Assistente local orientado a catálogo. Copiar para frontend/services/pricing_assistant.py.

O build gera o catálogo e os handlers específicos do roadmap. Este runtime não usa
LLM, rede, eval ou import dinâmico vindo de texto; executa somente funções registradas.
"""
from copy import deepcopy
import hashlib
import json
import logging
import unicodedata


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text).casefold())
    return " ".join("".join(c if c.isalnum() else " " for c in text if not unicodedata.combining(c)).split())


def context_fingerprint(context: dict) -> str:
    fields = ("page", "role", "filters", "product_id", "scenario_key", "scenario_view", "revision")
    payload = json.dumps({key: context.get(key) for key in fields}, sort_keys=True, allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def validate_catalog(catalog: dict, handlers: dict) -> None:
    seen = set()
    for analysis in catalog.get("analyses", []):
        identifier = analysis["id"]
        if identifier in seen:
            raise ValueError(f"Análise duplicada: {identifier}")
        seen.add(identifier)
        for field in ("title", "handler", "questions", "sources", "assumptions", "actions"):
            if field not in analysis:
                raise ValueError(f"{identifier}: falta {field}")
        if not analysis["questions"] or not analysis["sources"]:
            raise ValueError(f"{identifier}: perguntas/fontes vazias")
        if analysis["handler"] not in handlers or not callable(handlers[analysis["handler"]]):
            raise ValueError(f"{identifier}: handler não registrado")
        if any(action.get("kind") not in {"navigate", "simulate"} for action in analysis["actions"]):
            raise ValueError(f"{identifier}: ação não suportada")


def available(catalog: dict, context: dict) -> list[dict]:
    if catalog.get("enabled") is False:
        return []
    return [item for item in catalog.get("analyses", [])
            if (not item.get("pages") or context.get("page") in item["pages"])
            and (not item.get("roles") or context.get("role") in item["roles"])]


def answer(question: str, catalog: dict, handlers: dict, context: dict,
           analysis_id: str | None = None) -> dict:
    """Contexto explícito: página, filtros, produto selecionado e cenário/revisão.

    Matching conservador por perguntas/aliases. Texto livre desconhecido retorna
    sugestões em vez de escolher uma análise por similaridade fraca.
    """
    if catalog.get("enabled") is False:
        return {"status": "disabled", "message": "Assistente desabilitado neste projeto.", "actions": []}
    validate_catalog(catalog, handlers)
    analyses = available(catalog, context)
    options = [{"id": a["id"], "title": a["title"], "question": a["questions"][0]} for a in analyses]
    if analysis_id:
        matches = [a for a in analyses if a["id"] == analysis_id]
    else:
        query = normalize(question)
        matches = [a for a in analyses if query and query in
                   {normalize(q) for q in a["questions"] + a.get("aliases", [])}]
    if len(matches) != 1:
        return {"status": "choose_analysis", "message": "Escolha uma das análises disponíveis para esta tela.",
                "options": options, "actions": []}
    analysis = matches[0]
    missing = [key for key in analysis.get("required_context", []) if context.get(key) in (None, "", [], {})]
    if missing:
        return {"status": "needs_context", "analysis_id": analysis["id"],
                "message": "Selecione os dados necessários para continuar.", "missing": missing, "actions": []}
    try:
        result = handlers[analysis["handler"]](deepcopy(context))
        if not isinstance(result, dict) or not isinstance(result.get("message"), str):
            raise ValueError("Handler deve retornar mensagem e dados estruturados")
        json.dumps(result, allow_nan=False)
        action_ids = result.get("action_ids", [])
        allowed = {a["id"]: a for a in analysis["actions"]}
        if any(identifier not in allowed for identifier in action_ids):
            raise ValueError("Ação fora do catálogo")
    except Exception as exc:
        logging.getLogger(__name__).error("Análise %s indisponível (%s)", analysis["id"], type(exc).__name__)
        return {"status": "unavailable", "analysis_id": analysis["id"],
                "message": "Não foi possível calcular esta análise com os dados atuais. Revise os filtros e tente novamente.",
                "actions": []}
    return {"status": "ok", "analysis_id": analysis["id"], "message": result["message"],
            "data": result.get("data", {}), "assumptions": analysis["assumptions"],
            "sources": analysis["sources"], "revision": context.get("revision"),
            "context_fingerprint": context_fingerprint(context),
            "scenario_view": context.get("scenario_view", "applied"),
            "actions": [deepcopy(allowed[identifier]) for identifier in action_ids],
            "proposal": deepcopy(result.get("proposal"))}


def proposal_event(response: dict, context: dict, event_id: str, action_id: str) -> dict:
    """Intenção de rascunho para o dispatcher; jamais aplica o cenário."""
    if response.get("status") != "ok" or response.get("context_fingerprint") != context_fingerprint(context):
        raise ValueError("Contexto mudou; recalcule a análise")
    action = next((a for a in response.get("actions", []) if a["id"] == action_id and a["kind"] == "simulate"), None)
    proposal = response.get("proposal")
    if not event_id or not action or not isinstance(proposal, dict) or not isinstance(proposal.get("parameters"), dict):
        raise ValueError("Proposta de simulação inválida")
    if not action.get("scenario_key") or action["scenario_key"] != context.get("scenario_key") or context.get("revision") is None:
        raise ValueError("Selecione o cenário da proposta antes de simular")
    return {"id": event_id, "kind": "simulate", "scenario_key": action["scenario_key"],
            "expected_revision": context["revision"], "parameters": deepcopy(proposal["parameters"]),
            "scope": deepcopy(proposal.get("scope", context.get("filters") or {}))}


def append_history(history: list | None, question: str, response: dict, limit: int = 20) -> list:
    """Histórico retornado para dcc.Store(session), sem memória global compartilhada."""
    if limit < 1:
        raise ValueError("Limite de histórico deve ser positivo")
    return (deepcopy(history or []) + [{"question": question, "response": deepcopy(response)}])[-limit:]
