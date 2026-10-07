"""Estado de cenário mock por sessão. Copiar para frontend/components/demo_scenario.py.

Funções puras: nenhum CSV, banco ou variável global é alterado.
Resultados devem ser JSON compacto (resumos), nunca DataFrames completos.
"""
from copy import deepcopy
from collections.abc import Callable
import hashlib
import json


def fingerprint(params: dict, scope: dict) -> str:
    payload = json.dumps([params, scope], sort_keys=True, allow_nan=False, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def new_session(parameters: dict, scope: dict | None = None) -> dict:
    baseline = {"parameters": deepcopy(parameters), "scope": deepcopy(scope or {})}
    return {"baseline": baseline, "applied": deepcopy(baseline), "draft": deepcopy(baseline),
            "revision": 0, "applied_revision": 0, "preview": None, "last_event_id": None}


def transition(state: dict, event: dict) -> dict:
    """Eventos serializados por um único callback do shell.

    event = {id, kind, expected_revision, ...}. Rejeita eventos atrasados.
    edit traz parameters completos e scope; preview traz fingerprint e results;
    apply só aceita preview da revisão atual; reset restaura baseline.
    """
    if not event.get("id"):
        raise ValueError("Evento precisa de id")
    if event["id"] == state.get("last_event_id"):
        return deepcopy(state)
    if event.get("expected_revision") != state["revision"]:
        raise ValueError("Cenário mudou; atualize a revisão antes de continuar")
    result = deepcopy(state)
    kind = event.get("kind")
    if kind == "edit":
        result["draft"] = {"parameters": deepcopy(event["parameters"]),
                           "scope": deepcopy(event.get("scope", state["draft"]["scope"]))}
        result["preview"] = None
    elif kind == "simulate":
        draft = {"parameters": deepcopy(event["parameters"]),
                 "scope": deepcopy(event.get("scope", state["draft"]["scope"]))}
        signature = fingerprint(draft["parameters"], draft["scope"])
        if event.get("fingerprint") != signature:
            raise ValueError("Resultado pertence a parâmetros ou filtros antigos")
        json.dumps(event["results"], allow_nan=False)
        result["draft"] = draft
        result["preview"] = {"fingerprint": signature, "results": deepcopy(event["results"])}
    elif kind == "preview":
        draft = state["draft"]
        signature = fingerprint(draft["parameters"], draft["scope"])
        if event.get("fingerprint") != signature:
            raise ValueError("Resultado pertence a parâmetros ou filtros antigos")
        json.dumps(event["results"], allow_nan=False)
        result["preview"] = {"fingerprint": signature, "results": deepcopy(event["results"])}
    elif kind == "apply":
        draft = state["draft"]
        preview = state.get("preview")
        if not preview or preview["fingerprint"] != fingerprint(draft["parameters"], draft["scope"]):
            raise ValueError("Simule os parâmetros atuais antes de aplicar")
        result["applied"] = deepcopy(draft)
        result["applied_revision"] += 1
        result["preview"] = None
    elif kind == "discard":
        result["draft"] = deepcopy(state["applied"])
        result["preview"] = None
    elif kind == "reset":
        result["applied"] = deepcopy(state["baseline"])
        result["draft"] = deepcopy(state["baseline"])
        result["preview"] = None
        result["applied_revision"] += 1
    else:
        raise ValueError(f"Evento desconhecido: {kind}")
    result["revision"] += 1
    result["last_event_id"] = event["id"]
    return result


def scenario_for_view(state: dict, view: str = "applied") -> dict:
    """Comparativo de simulação usa draft; telas comuns usam applied."""
    if view not in ("applied", "draft", "baseline"):
        raise ValueError("Visão de cenário inválida")
    return deepcopy(state[view])


def dispatch(state: dict, event: dict, calculate: Callable[[dict, dict], dict]) -> dict:
    """Entrada do shell: recalcula preview com motor real, ignorando resultados do cliente."""
    if event.get("id") and event["id"] == state.get("last_event_id"):
        return deepcopy(state)
    prepared = deepcopy(event)
    if prepared.get("kind") in ("simulate", "preview"):
        if prepared.get("expected_revision") != state["revision"]:
            raise ValueError("Cenário mudou; simule novamente")
        draft = ({"parameters": prepared["parameters"],
                  "scope": prepared.get("scope", state["draft"]["scope"])}
                 if prepared["kind"] == "simulate" else state["draft"])
        prepared["results"] = calculate(deepcopy(draft["parameters"]), deepcopy(draft["scope"]))
        prepared["fingerprint"] = fingerprint(draft["parameters"], draft["scope"])
    return transition(state, prepared)
