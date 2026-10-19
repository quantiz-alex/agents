"""Ferramentas de DETALHE do Assistente — analisam o item aberto no "Detalhar" de qualquer tela.

Regra de ouro: cada ferramenta chama AS MESMAS funções de consulta que a tela usa para montar o detalhe, com o mesmo estado
(cenário aplicado + preços aprovados + decisões da sessão). Assim o número do assistente é o mesmo número da tela.
O item em foco chega em ctx["entity"] = {"type", "id", "label", "snapshot"?}, gravado pela própria tela ao abrir o Detalhar.
"""
from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd

from frontend.services import assistant_data as ad


def _clean(v: Any) -> Any:
    """JSON-seguro: NaN → None, numpy → python, datas → texto."""
    if isinstance(v, dict):
        return {str(k): _clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_clean(x) for x in v]
    if isinstance(v, (pd.Timestamp, datetime, date)):
        return v.strftime("%d/%m/%Y")
    if isinstance(v, np.generic):
        v = v.item()
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


def _records(df: pd.DataFrame, n: int = 10) -> list[dict]:
    out = df.head(n).copy()
    num = out.select_dtypes("number").columns
    out[num] = out[num].round(2)
    return _clean(out.to_dict("records"))


def _entity(ctx: dict, tipo: str) -> dict | None:
    e = ctx.get("entity") or {}
    return e if e.get("type") == tipo and e.get("id") not in (None, "") else None


def _num(v: Any) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


def _brl(v: Any) -> str:
    f = _num(v)
    return "—" if f is None else ad.brl(f)


def _pct(v: Any, sign: bool = False) -> str:
    f = _num(v)
    return "—" if f is None else ad.pct(f, sign)


def _dec(v: Any) -> str:
    f = _num(v)
    return "—" if f is None else f"{f:.2f}".replace(".", ",")


def _sem_foco(o_que: str) -> dict:
    return {"message": f"Abra o Detalhar de um {o_que} nesta tela para eu analisar.", "data": {}, "action_ids": []}


# ----------------------------------------------------------------------------- produto (Tabela Vigente / Centro de Comando / Estratégia / Simulador)

def detalhe_produto(ctx: dict) -> dict:
    """EXEMPLO (tela-tabela por produto). Mesmas consultas da Tabela Vigente: base (cenário aplicado + aprovados) → recalcular → por_produto/variacoes."""
    from frontend.pages.tabela_vigente import tabela_vigente_queries as tq

    e = _entity(ctx, "produto")
    pid = (e or {}).get("id") or ctx.get("product_id")
    if pid in (None, ""):
        return _sem_foco("produto")
    base = tq.base(ctx.get("scenario_state"), ctx.get("session"))
    combos = base[base["produto_id"] == int(pid)]
    if combos.empty:
        return {"message": "Não encontrei esse produto na lista de preços vigente.", "data": {}, "action_ids": []}
    d = tq.recalcular(combos, {})
    p = tq.por_produto(d).iloc[0]
    canais = (d.groupby("canal").agg(preco_min=("sell_in", "min"), preco_max=("sell_in", "max"), receita=("receita_atual", "sum"),
                                     volume=("volume_atual", "sum")).reset_index().sort_values("receita", ascending=False))
    fora = tq.fora_guardrail(d)
    minimo = max(float(p["custo"]), float(p["min_price_guardrail"]))
    msg = (f"{p['sku']} · {p['produto']} ({p['categoria']}): preço base {ad.brl(float(p['preco_base']))} (referência Varejo · Sudeste · Standard), "
           f"faixa nas {int(p['combinacoes'])} combinações {p['faixa']}. Custo {ad.brl(float(p['custo']))}, margem na referência "
           f"{_pct(p['margem_bruta_pct'])} vs meta {_pct(p['margem_alvo'])}. Guardrails {ad.brl(minimo)} – {ad.brl(float(p['max_price_guardrail']))}"
           f"{f' ({fora} combinação(ões) fora)' if fora else ''}. Receita somada {_brl(p['receita_atual'])}, volume {round(float(p['volume_atual']))}, "
           f"elasticidade {_dec(p['elasticidade'])}, concorrente {_brl(p['preco_concorrente'])}.")
    acoes = ["abrir_tabela_produto"] if ctx.get("page") != "tabela-vigente" else []
    return {"message": msg, "data": {"itens": _records(canais, 10),
                                     "produto": _clean({k: p[k] for k in ("sku", "produto", "preco_base", "faixa", "custo", "margem_bruta_pct",
                                                                          "margem_alvo", "receita_atual", "volume_atual", "elasticidade")}),
                                     "nav_context": {"sku": str(p["sku"])}}, "action_ids": acoes}


# ----------------------------------------------------------------------------- combinação na Configuração de Preços (simulação na tela)

def detalhe_combinacao(ctx: dict) -> dict:
    """A simulação da Configuração usa parâmetros ainda não salvos (controles da tela). Por isso a tela grava no foco o retrato
    exato da linha (snapshot) e esta ferramenta devolve esse retrato — sem recalcular, sem divergir."""
    e = _entity(ctx, "combinacao")
    if not e or not e.get("snapshot"):
        return _sem_foco("item da simulação")
    s = e["snapshot"]
    msg = (f"{s.get('sku')} · {s.get('produto')} em {s.get('canal')} · {s.get('regiao')} · {s.get('segmento')} (simulação da tela): sell in "
           f"{_brl(s.get('sell_in_atual'))} → {_brl(s.get('sell_in_simulado'))} ({_pct(s.get('variacao_pct'), True)}), margem {_pct(s.get('margem_atual'))} → "
           f"{_pct(s.get('margem_simulado'))}, volume {int(_num(s.get('volume_atual')) or 0)} → {int(_num(s.get('volume_simulado')) or 0)} "
           f"(elasticidade {_dec(s.get('elasticidade'))}, RN-012). Custo {_brl(s.get('custo'))}.")
    return {"message": msg, "data": {"combinacao": _clean(s)}, "action_ids": []}


# >>> Gerar uma ferramenta por tipo de item que o projeto publica no Detalhar (pedido, lote, cliente, promoção...), sempre chamando
#     as MESMAS funções *_queries.py que o callback de detalhe da tela usa. Os dois handlers acima são EXEMPLOS do padrão.
DETAIL_HANDLERS = {"detalhe_produto": detalhe_produto, "detalhe_combinacao": detalhe_combinacao}
