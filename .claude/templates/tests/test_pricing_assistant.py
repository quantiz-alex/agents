"""Assistente de Pricing — testes GENÉRICOS do motor (copiar para tests/frontend/; valem para qualquer projeto).

Cobrem: catálogo válido, todo handler roda e é JSON-safe nas suas telas, ferramentas de foco restritas por tela, trava de escopo,
fallback local e loop do Claude com cliente falso (sem rede). Não há testes de paridade número-a-número: cada projeto tem suas regras.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from frontend.assistant_callbacks import SCENARIO_PAGES, catalog, responder, scope_vocab
from frontend.services import assistant_llm
from frontend.services import pricing_assistant as pa
from frontend.services.assistant_analyses import ANALYSIS_HANDLERS

USER = {"role": "admin", "email": "admin@demo.com"}


def make_ctx(page: str, entity: dict | None = None, params: dict | None = None) -> dict:
    """Contexto mínimo. Projetos com cenário compartilhado: preencha scenario_state com o estado inicial do demo (skill-demo-scenario)."""
    return {"page": page, "role": USER["role"], "email": USER["email"], "filters": {}, "product_id": (entity or {}).get("id"),
            "scenario_key": next(iter(SCENARIO_PAGES), None) if page in SCENARIO_PAGES else None, "scenario_view": "applied",
            "revision": 0, "scenario_state": {}, "session": None, "entity": entity, "params": params}


ANALISES_TELA = [(a, p) for a in catalog()["analyses"] if not a.get("entity") and not a.get("required_context") for p in a["pages"]]


# ---------------------------------------------------------------- catálogo
def test_catalogo_valido():
    c = catalog()                                     # valida na carga (textos, handlers, ações)
    ids = [a["id"] for a in c["analyses"]]
    assert len(ids) == len(set(ids))
    assert all(a["handler"] in ANALYSIS_HANDLERS for a in c["analyses"])


def test_ferramentas_de_foco_tem_telas_explicitas():
    """entity sem pages faria a ferramenta aparecer em telas de outro propósito (ex.: 'melhor preço' no simulador tributário)."""
    assert all(a.get("pages") for a in catalog()["analyses"] if a.get("entity"))


def test_textos_do_catalogo_sao_strings():
    for a in catalog()["analyses"]:
        for k in ("questions", "aliases", "sources", "assumptions"):
            assert all(isinstance(v, str) for v in a.get(k, [])), (a["id"], k)


# ---------------------------------------------------------------- handlers
@pytest.mark.parametrize("analysis,page", ANALISES_TELA, ids=lambda x: x["id"] if isinstance(x, dict) else x)
def test_handlers_da_tela_rodam_e_serializam(analysis, page):
    r = pa.run_analysis(catalog(), ANALYSIS_HANDLERS, analysis, make_ctx(page))
    assert r["status"] in ("ok", "needs_context"), r["message"]
    json.dumps(r, allow_nan=False)


# ---------------------------------------------------------------- trava de escopo
@pytest.mark.parametrize("pergunta", ["Quantos graus vai fazer hoje?", "quem ganhou o jogo ontem?", "escreva um código em python"])
def test_trava_de_escopo_bloqueia(pergunta):
    assert not pa.in_scope(pergunta, scope_vocab(), has_history=True)


def test_fora_do_escopo_nao_chama_claude(monkeypatch):
    monkeypatch.setattr(assistant_llm, "enabled", lambda: True)
    monkeypatch.setattr(assistant_llm, "answer", lambda *a, **k: (_ for _ in ()).throw(AssertionError("não deveria chamar")))
    page = next(p for a, p in ANALISES_TELA)
    assert responder("Quantos graus vai fazer hoje?", None, make_ctx(page), [])["status"] == "out_of_scope"


# ---------------------------------------------------------------- motor Claude (cliente falso)
def _b(**kw):
    return SimpleNamespace(**kw)


class FakeClient:
    def __init__(self, responses=None, error=None):
        self.calls, self._r, self._e = [], list(responses or []), error
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kw):
        self.calls.append(kw)
        if self._e:
            raise self._e
        return self._r.pop(0)


def test_claude_chama_ferramenta_com_contexto_do_servidor():
    analysis, page = ANALISES_TELA[0]
    client = FakeClient([_b(stop_reason="tool_use", content=[_b(type="tool_use", id="t1", name=analysis["id"], input={})]),
                         _b(stop_reason="end_turn", content=[_b(type="text", text="Resposta.")])])
    r = assistant_llm.answer("pergunta", catalog(), ANALYSIS_HANDLERS, make_ctx(page), [], client=client)
    assert r["engine"] == "claude" and r["message"] == "Resposta."
    assert all(t["input_schema"]["properties"] == {} for t in client.calls[0]["tools"])   # contexto nunca vem do modelo


def test_falha_da_api_cai_no_modo_local(monkeypatch):
    monkeypatch.setattr(assistant_llm, "enabled", lambda: True)

    def boom(*a, **k):
        raise assistant_llm.LLMUnavailable("off")

    monkeypatch.setattr(assistant_llm, "answer", boom)
    analysis, page = ANALISES_TELA[0]
    r = responder(analysis["questions"][0], None, make_ctx(page), [])
    assert r["engine"] == "local" and "IA indisponível" in r.get("note", "")
