"""Assistente orientado a catálogo — motor local (sem rede).

Executa somente funções registradas em ANALYSIS_HANDLERS. O motor com Claude (services/assistant_llm.py) reutiliza
`run_analysis`, então os números sempre vêm destes handlers; o LLM só escolhe a análise e redige a resposta.
"""
from copy import deepcopy
from datetime import datetime
from difflib import SequenceMatcher
import hashlib
import json
import logging
import math

import unicodedata

HISTORY_LIMIT = 20
ROWS_PER_TURN = 10
MATCH_ACCEPT = 0.75      # score mínimo para executar direto
MATCH_SUGGEST = 0.45     # score mínimo para entrar na lista de candidatos
_STOPWORDS = {"que", "qual", "quais", "como", "estao", "esta", "sao", "com", "sem", "por", "para", "dos", "das", "nos", "nas", "uma", "uns",
              "umas", "meu", "minha", "meus", "minhas", "onde", "quando", "mais", "menos", "tem", "ter", "isso", "esse", "essa", "este",
              "deste", "desse", "neste", "nesse", "dele", "dela", "aqui", "hoje", "agora", "mostre", "mostrar", "me", "ver", "quero", "saber", "existe", "existem", "ha"}

# >>> PARAMETRIZAR POR PROJETO: dica por tela de onde o usuário seleciona o item exigido (slugs das telas do projeto).
_MISSING_HINTS = {
    "product_id": {
        "tabela-vigente": "Selecione um produto clicando em Detalhar na tabela.",
        "centro-comando": "Clique num produto da lista ou do gráfico para selecioná-lo.",
        "estrategia-capitaes": "Clique num capitão na matriz ou em Detalhar.",
        "simulador-tributario": "Selecione um produto no Simulador Tributário.",
        None: "Selecione um produto nesta tela.",
    },
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text).casefold())
    return " ".join("".join(c if c.isalnum() else " " for c in text if not unicodedata.combining(c)).split())


def _tokens(text: str) -> set[str]:
    return {t[:6] for t in normalize(text).split() if len(t) > 2 and t not in _STOPWORDS}  # prefixo = stem grosseiro (otimizar ≈ otimizador)


def context_fingerprint(context: dict) -> str:
    """Revisão/visão do cenário só contam em telas de cenário; fora delas não invalidam ações."""
    fields = ["page", "role", "filters", "product_id"]
    if context.get("scenario_key"):
        fields += ["scenario_key", "scenario_view", "revision"]
    data = {key: context.get(key) for key in fields}
    foco = context.get("entity") or {}
    data["entity"] = [foco.get("type"), foco.get("id")] if foco else None       # trocar o item do Detalhar expira as ações
    data["params"] = context.get("params") or None                               # mudar filtro/parâmetro da tela também
    payload = json.dumps(data, sort_keys=True, allow_nan=False, default=str)
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
        for field in ("questions", "aliases", "sources", "assumptions"):
            if any(not isinstance(v, str) for v in analysis.get(field, [])):
                raise ValueError(f"{identifier}: {field} deve conter apenas textos (use aspas no YAML)")
        if analysis["handler"] not in handlers or not callable(handlers[analysis["handler"]]):
            raise ValueError(f"{identifier}: handler não registrado")
        if any(action.get("kind") not in {"navigate", "simulate"} for action in analysis["actions"]):
            raise ValueError(f"{identifier}: ação não suportada")


def entity_type(context: dict) -> str | None:
    return (context.get("entity") or {}).get("type")


def available(catalog: dict, context: dict) -> list[dict]:
    """Análises da tela atual (`pages`). As de item em foco (`entity`) exigem também o foco desse tipo — e só valem nas telas listadas,
    para que, por exemplo, "melhor preço" (Tabela Vigente) não apareça no Simulador Tributário. Elas vêm primeiro."""
    if catalog.get("enabled") is False:
        return []
    foco = entity_type(context)
    out = [item for item in catalog.get("analyses", [])
           if (not item.get("pages") or context.get("page") in item["pages"])
           and (not item.get("roles") or context.get("role") in item["roles"])
           and (not item.get("entity") or item["entity"] == foco)]
    return sorted(out, key=lambda a: 0 if a.get("entity") else 1)


def options_for(analyses: list[dict]) -> list[dict]:
    return [{"id": a["id"], "title": a["title"], "question": a["questions"][0]} for a in analyses]


def _pool(analysis: dict) -> set[str]:
    return set().union(*(_tokens(p) for p in [*analysis["questions"], *analysis.get("aliases", []), analysis["title"]]))


def _scores(question: str, analyses: list[dict]) -> list[tuple[float, dict]]:
    """Sobreposição de palavras ponderada pela raridade entre as análises (termos genéricos como "produto" pesam pouco;
    palavras desconhecidas pesam como raras e derrubam o score) + similaridade de texto para erros de digitação."""
    q, qt = normalize(question), _tokens(question)
    pools = [_pool(a) for a in analyses]
    n = len(analyses)
    idf = {t: math.log((n + 1) / (1 + sum(t in p for p in pools))) + 1 for t in qt}
    total = sum(idf.values())
    out = []
    for a, pool in zip(analyses, pools):
        phrases = [normalize(p) for p in [*a["questions"], *a.get("aliases", []), a["title"]]]
        if q in phrases:
            out.append((1.0, a))
            continue
        overlap = sum(idf[t] for t in qt & pool) / total if total else 0.0
        ratio = max(SequenceMatcher(None, q, p).ratio() for p in phrases)
        out.append((max(overlap * 0.95, ratio * 0.85), a))
    return sorted(out, key=lambda x: x[0], reverse=True)


def match(question: str, analyses: list[dict]) -> tuple[dict | None, list[dict]]:
    """(análise escolhida | None, candidatos ordenados). Escolhe só com score alto e sem empate próximo."""
    if not normalize(question) or not analyses:
        return None, []
    ranked = _scores(question, analyses)
    top_score, top = ranked[0]
    second = ranked[1][0] if len(ranked) > 1 else 0.0
    if (top_score >= MATCH_ACCEPT and ((top_score == 1.0 and second < 1.0) or top_score - second >= 0.08)) or (top_score >= 0.6 and top_score - second >= 0.2):
        return top, []
    return None, [a for s, a in ranked if s >= MATCH_SUGGEST][:4]


# >>> PARAMETRIZAR POR PROJETO: acrescente termos do domínio do cliente (o catálogo e os nomes de produtos/dimensões já entram via
#     scope_vocabulary(extra_terms) em assistant_callbacks.scope_vocab). Remova termos de módulos que o projeto não tem.
# Vocabulário do domínio (pricing e processos da aplicação). Somado aos termos do catálogo e aos nomes de produtos/categorias/canais.
DOMAIN_GLOSSARY = """
preço preços precificação precificar tabela lista vigente reajuste reajustar aumento redução margem margens markup custo custos lucro
lucratividade rentabilidade receita faturamento venda vendas vender volume demanda elasticidade elástico concorrente concorrência
mercado posicionamento gap sell in sell out ppc consumidor desconto descontos faixa faixas política promoção promoções promocional
verba roi canibalização incremental imposto impostos tributo tributos tributária tributário reforma icms pis cofins ibs cbs alíquota
crédito cenário cenários simulação simular simulado rascunho aplicado aplicar proposta otimizar otimização arquitetura índice índices
atributo meta metas alvo alerta alertas crítico críticos oportunidade oportunidades risco aprovação aprovações aprovar rejeitar lote
lotes pendência pendências pedido pedidos cliente clientes canal canais região regiões segmento segmentos varejo atacado distribuidor
categoria categorias subcategoria produto produtos sku skus item itens portfólio mix capitão capitães estratégia estratégias guardrail
mínimo máximo dashboard indicador indicadores kpi resumo impacto variação comparativo histórico tendência regra regras qwizer pricing
"""


_SCOPE_IGNORE = {"quanto", "quantos", "quanta", "quantas", "qual", "quais", "vai", "fazer", "faz", "dia", "dias", "ano", "anos", "devo", "deveria", "quem", "onde", "quando", "porque", "pode", "posso", "tem", "temos"}


def _scope_tokens(text: str) -> set[str]:
    """Prefixo de 7 letras: mais estrito que o matching (evita capital ≈ capitão), ainda junta reajuste/reajustar."""
    return {t[:7] for t in normalize(text).split() if len(t) > 2 and t not in _STOPWORDS and t not in _SCOPE_IGNORE}


# Palavras de continuação aceitas só quando já há conversa ("por que caiu?", "me explica esse resultado", "e o pior?").
FOLLOWUP_TERMS = """
explica explicar explique detalha detalhe detalhes resultado resultados motivo motivos causa causou caiu cair caindo subiu subir subindo
melhor melhores pior piores maior maiores menor menores primeiro primeiros último próximo passo passos devo deveria fazer recomenda
recomendação recomendações sugere sugestão sugestões ação ações compara comparar comparação diferença resume resumir exemplo exemplos
mostra mostrar lista listar outro outros outra outras mais menos top aumentar diminuir reduzir cresceu continua continuar entendi
significa sentido certo correto confirma número números valor valores total
"""


def scope_vocabulary(catalog: dict, extra_terms: list[str] | None = None) -> set[str]:
    vocab = _scope_tokens(DOMAIN_GLOSSARY)
    for a in catalog.get("analyses", []):
        for phrase in [*a["questions"], *a.get("aliases", []), a["title"]]:
            vocab |= _scope_tokens(phrase)
    for term in extra_terms or []:
        vocab |= _scope_tokens(term)
    return vocab


def in_scope(question: str, vocab: set[str], has_history: bool = False) -> bool:
    """Trava barata (sem API): fora do escopo só quando a pergunta não tem NENHUM termo do domínio.
    Seguimentos curtos ("e por quê?", "e no sul?") passam quando já há conversa — o Claude ainda aplica a regra de escopo."""
    tokens = _scope_tokens(question)
    if tokens & vocab:
        return True
    return has_history and tokens <= _FOLLOWUP


def out_of_scope_response(catalog: dict, context: dict) -> dict:
    return {"status": "out_of_scope", "engine": "local",
            "message": ("Sou o assistente de pricing do Qwizer e respondo apenas sobre os processos desta aplicação: preços, margens, "
                        "custos, alertas, cenários, promoções, descontos, aprovações e impactos tributários. Experimente uma destas:"),
            "options": options_for(available(catalog, context))[:4], "actions": []}


def missing_message(missing: list[str], page: str | None) -> str:
    hints = [(_MISSING_HINTS.get(k) or {}).get(page) or (_MISSING_HINTS.get(k) or {}).get(None) or f"Informe {k}." for k in missing]
    return " ".join(dict.fromkeys(hints))


def run_analysis(catalog: dict, handlers: dict, analysis: dict, context: dict) -> dict:
    """Executa UMA análise do catálogo com o contexto do servidor e devolve a resposta padronizada."""
    missing = [key for key in analysis.get("required_context", []) if context.get(key) in (None, "", [], {})]
    if missing:
        return {"status": "needs_context", "analysis_id": analysis["id"], "title": analysis["title"],
                "message": missing_message(missing, context.get("page")), "missing": missing, "actions": []}
    allowed = {a["id"]: a for a in analysis["actions"]}
    try:
        result = handlers[analysis["handler"]](deepcopy(context))
        if not isinstance(result, dict) or not isinstance(result.get("message"), str):
            raise ValueError("Handler deve retornar mensagem e dados estruturados")
        json.dumps(result, allow_nan=False)
        action_ids = result.get("action_ids", [])
        if any(identifier not in allowed for identifier in action_ids):
            raise ValueError("Ação fora do catálogo")
    except Exception as exc:
        logging.getLogger(__name__).error("Análise %s indisponível (%s: %s)", analysis["id"], type(exc).__name__, exc)
        return {"status": "unavailable", "analysis_id": analysis["id"], "title": analysis["title"],
                "message": "Não foi possível calcular esta análise com os dados atuais. Revise os filtros e tente novamente.",
                "actions": []}
    return {"status": "ok", "analysis_id": analysis["id"], "title": analysis["title"], "message": result["message"],
            "data": result.get("data", {}), "assumptions": list(analysis["assumptions"]),
            "sources": list(analysis["sources"]), "revision": context.get("revision"),
            "context_fingerprint": context_fingerprint(context),
            "scenario_view": context.get("scenario_view", "applied"),
            "actions": [deepcopy(allowed[identifier]) for identifier in action_ids],
            "proposal": deepcopy(result.get("proposal"))}


def answer(question: str, catalog: dict, handlers: dict, context: dict,
           analysis_id: str | None = None) -> dict:
    """Motor local: id explícito (sugestão clicada) ou pergunta casada por similaridade com perguntas/aliases/título."""
    if catalog.get("enabled") is False:
        return {"status": "disabled", "message": "Assistente desabilitado neste projeto.", "actions": [], "engine": "local"}
    analyses = available(catalog, context)
    if analysis_id:
        chosen = next((a for a in analyses if a["id"] == analysis_id), None)
        candidates = []
    else:
        chosen, candidates = match(question, analyses)
    if not chosen:
        if candidates:
            msg = "Não tenho certeza de qual análise você quer. Alguma destas?"
        else:
            msg = "Não encontrei uma análise para essa pergunta nesta tela. Estas são as disponíveis:"
        return {"status": "choose_analysis", "message": msg, "options": options_for(candidates or analyses), "actions": [], "engine": "local"}
    return {**run_analysis(catalog, handlers, chosen, context), "engine": "local"}


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


def _compact(response: dict, keep_proposal: bool) -> dict:
    r = deepcopy(response)
    data = r.get("data")
    if isinstance(data, dict):
        r["data"] = {k: (v[:ROWS_PER_TURN] if isinstance(v, list) else v) for k, v in data.items()}
    if not keep_proposal:
        r.pop("proposal", None)
    return r


def append_history(history: list | None, question: str, response: dict, meta: dict | None = None,
                   limit: int = HISTORY_LIMIT) -> list:
    """Histórico para dcc.Store(session). Cada turno guarda tela/produto/motor; só o último mantém a proposta completa."""
    if limit < 1:
        raise ValueError("Limite de histórico deve ser positivo")
    old = [{**t, "response": _compact(t.get("response") or {}, keep_proposal=False)} for t in deepcopy(history or [])]
    turn = {"question": question, "response": _compact(response, keep_proposal=True),
            "ts": datetime.now().strftime("%H:%M"), **(meta or {})}
    return (old + [turn])[-limit:]


_FOLLOWUP = frozenset(_scope_tokens(FOLLOWUP_TERMS) | {t[:7] for t in normalize(FOLLOWUP_TERMS).split()})
