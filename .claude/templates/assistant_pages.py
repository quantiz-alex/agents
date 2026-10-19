"""Análises do Assistente POR TELA — cada handler chama as mesmas funções `*_queries.py` da tela, com o estado atual dela.

O estado (filtros, período, ano, sliders, faixas em edição…) chega em ctx["params"], publicado pela própria tela no store
{"type": "assistant-params", "page": SLUG}. Sem params (ex.: tela recém-aberta), vale o padrão que a tela usa ao carregar.
Todo resultado devolve `data.parametros_tela` para o assistente citar o recorte usado.
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from frontend.services import assistant_data as ad
from frontend.services.assistant_detail import _clean, _num, _pct, _records


def _p(ctx: dict) -> dict:
    return dict(ctx.get("params") or {})


def _v(x: Any) -> Any:
    """Valor de controle → None quando vazio/"Todos" (mesmo critério de pages._common.opt_value)."""
    return None if x in (None, "", [], "Todos") else x


def _ok(msg: str, data: dict | None = None, params: dict | None = None, action_ids: list | None = None) -> dict:
    out = dict(data or {})
    if params:
        out["parametros_tela"] = _clean({k: v for k, v in params.items() if v not in (None, "", [], {})})
    return {"message": msg, "data": out, "action_ids": action_ids or []}


def _x(v: float) -> str:
    return f"{v:.2f}x".replace(".", ",")


# ============================================================================ EXEMPLO 1 — tela analítica com período e filtros (botão Filtrar)

def _dash(ctx: dict) -> tuple:
    from frontend.pages.dashboard import dashboard_queries as dq

    p = _p(ctx)
    ini0, fim0 = dq.periodo_padrao()
    ini, fim = p.get("inicio") or ini0, p.get("fim") or fim0
    filt = [_v(p.get(k)) for k in ("ambiente_id", "canal_id", "regiao_id", "segmento_id", "categoria_id")]
    df = dq.carregar_vendas(ini, fim, *filt)
    ant = dq.carregar_vendas(*dq.periodo_anterior(ini, fim), *filt)
    params = {"periodo": f"{pd.Timestamp(ini):%d/%m/%Y} a {pd.Timestamp(fim):%d/%m/%Y}",
              **{k: p.get(k + "_label") or p.get(k) for k in ("ambiente_id", "canal_id", "regiao_id", "segmento_id", "categoria_id") if _v(p.get(k))}}
    return dq, df, ant, params


def dash_resumo(ctx: dict) -> dict:
    """KPIs do Dashboard: dashboard_queries.calcular_kpis(período e filtros da tela)."""
    dq, df, ant, params = _dash(ctx)
    if df.empty:
        return _ok("Sem vendas no período/filtros da tela.", params=params)
    k = dq.calcular_kpis(df, ant)
    vr = (k["receita"] / k["receita_ant"] - 1) * 100 if k["receita_ant"] else None
    vv = (k["volume"] / k["volume_ant"] - 1) * 100 if k["volume_ant"] else None
    msg = (f"Período {params['periodo']}: receita {ad.brl(k['receita'])} ({_pct(vr, True)} vs período anterior), volume "
           f"{k['volume']:,.0f}".replace(",", ".") + f" ({_pct(vv, True)}), margem ponderada {_pct(k['margem'])} vs alvo {_pct(k['margem_alvo'])} (RN-001). "
           f"{k['skus']} SKUs, {k['clientes']} clientes; {k['abaixo_alvo']} produtos abaixo da margem alvo.")
    return _ok(msg, {k2: k[k2] for k2 in ("receita", "receita_ant", "volume", "margem", "margem_alvo", "skus", "clientes", "abaixo_alvo")}, params)


def dash_categorias(ctx: dict) -> dict:
    """Gráfico receita × margem por categoria: dashboard_queries.agregar_categoria."""
    dq, df, _ant, params = _dash(ctx)
    g = dq.agregar_categoria(df).dropna(subset=["margem"])
    if g.empty:
        return _ok("Sem vendas no período/filtros da tela.", params=params)
    best, worst = g.sort_values("margem").iloc[-1], g.sort_values("margem").iloc[0]
    top = g.iloc[0]
    msg = (f"Período {params['periodo']}: maior receita em {top['categoria']} ({ad.brl(top['receita'])}, margem {_pct(top['margem'])}). "
           f"Melhor margem: {best['categoria']} ({_pct(best['margem'])}); pior margem: {worst['categoria']} ({_pct(worst['margem'])}).")
    return _ok(msg, {"itens": _records(g[["categoria", "receita", "margem"]], 12)}, params)


def dash_top_clientes(ctx: dict) -> dict:
    """Top clientes do Dashboard: dashboard_queries.agregar_top_clientes."""
    dq, df, _ant, params = _dash(ctx)
    g = dq.agregar_top_clientes(df, 8)
    if g.empty:
        return _ok("Sem vendas no período/filtros da tela.", params=params)
    tot = float(df["receita"].sum())
    share = float(g["receita"].sum()) / tot * 100 if tot else 0
    msg = (f"Período {params['periodo']}: os 8 maiores clientes somam {ad.brl(float(g['receita'].sum()))} ({_pct(share)} da receita). "
           f"Maior: {g.iloc[0]['cliente']} ({ad.brl(g.iloc[0]['receita'])}).")
    return _ok(msg, {"itens": _records(g[["cliente", "receita"]], 8)}, params)


def dash_mix_canal(ctx: dict) -> dict:
    """Mix por canal do Dashboard: dashboard_queries.agregar_mix_canal (receita)."""
    dq, df, _ant, params = _dash(ctx)
    g = dq.agregar_mix_canal(df, "receita")
    if g.empty:
        return _ok("Sem vendas no período/filtros da tela.", params=params)
    tot = float(g["valor"].sum())
    g = g.assign(participacao_pct=g["valor"] / tot * 100 if tot else 0.0)
    partes = "; ".join(f"{r.canal} {_pct(r.participacao_pct)}" for r in g.itertuples())
    msg = f"Período {params['periodo']}: receita por canal — {partes}."
    return _ok(msg, {"itens": _records(g[["canal", "valor", "participacao_pct"]].rename(columns={"valor": "receita"}), 10)}, params)


# ============================================================================ EXEMPLO 2 — simulador com sliders ao vivo (produto da tela)

def _sim(ctx: dict):
    from frontend.pages.simulador_tributario import simulador_tributario_queries as sq

    p = _p(ctx)
    e = ctx.get("entity") or {}
    pid = p.get("produto_id") or (e.get("id") if e.get("type") == "produto" else None) or ctx.get("product_id") or sq.produto_padrao()
    d = sq.defaults(pid)
    vals = {k: float(p[k]) if _num(p.get(k)) is not None else float(d[k]) for k in sq.PARAMS}
    ano = int(p.get("ano") or 2033)
    pr = sq.produto(pid)
    params = {"produto": f"{pr['sku']} · {pr['nome']}", "ano": ano, **vals}
    return sq, pid, ano, vals, pr, sq.simular(pid, ano, vals), params


def reforma_produto(ctx: dict) -> dict:
    """KPIs do Simulador Tributário: simular(produto, ano e sliders da tela)."""
    _sq, _pid, ano, vals, pr, r, params = _sim(ctx)
    msg = (f"{pr['sku']} em {ano}, com os parâmetros da tela (margens indústria {_pct(vals['margem_industria'])}, distribuidor "
           f"{_pct(vals['margem_distribuidor'])}, varejo {_pct(vals['margem_varejo'])}): PPC legado {ad.brl(r['ppc_legado'])} → reforma "
           f"{ad.brl(r['ppc_reforma'])} ({_pct(r['impacto_ppc_pct'], True)}); alíquota efetiva {_pct(r['aliquota_efetiva'])} (RN-033/RN-034).")
    return _ok(msg, {"ppc_legado": r["ppc_legado"], "ppc_reforma": r["ppc_reforma"], "impacto_ppc_pct": r["impacto_ppc_pct"],
                     "itens": _records(pd.DataFrame(r["timeline"]), 10)}, params)


def reforma_transicao(ctx: dict) -> dict:
    """Linha do tempo 2026–2033 do Simulador: maior salto anual de PPC e de alíquota efetiva."""
    _sq, _pid, ano, _vals, pr, r, params = _sim(ctx)
    t = pd.DataFrame(r["timeline"]).sort_values("ano")
    t["salto_ppc_pct"] = t["ppc"].pct_change() * 100
    t["salto_aliquota_pp"] = t["aliquota_efetiva"].diff()
    s = t.iloc[t["salto_ppc_pct"].abs().fillna(-1).argmax()]
    msg = (f"{pr['sku']}: na transição 2026–2033, o maior salto anual do PPC é em {int(s['ano'])} ({_pct(s['salto_ppc_pct'], True)}; alíquota efetiva "
           f"{_pct(s['aliquota_efetiva'])}, {s['salto_aliquota_pp']:+.1f} p.p.".replace(".", ",") + f"). Em 2033 o impacto acumulado no PPC é "
           f"{_pct(float(t.iloc[-1]['impacto_pct']), True)}.")
    return _ok(msg, {"itens": _records(t[["ano", "ppc", "impacto_pct", "aliquota_efetiva", "salto_ppc_pct", "salto_aliquota_pp"]], 10)}, params)


# ============================================================================ EXEMPLO 3 — edição em grid simulada por botão (faixas em edição)

def _politica(ctx: dict):
    from frontend.pages.politica_descontos import politica_descontos_queries as pq

    vig = pq.faixas_vigentes(ctx.get("session"))
    ed = _p(ctx).get("faixas")
    faixas = {t: pq.normalizar(t, list((ed or {}).get(t) or vig[t])) for t in pq.TIPOS} if ed else {t: pq.normalizar(t, vig[t]) for t in pq.TIPOS}
    editado = faixas != {t: pq.normalizar(t, vig[t]) for t in pq.TIPOS}
    return pq, faixas, vig, editado


def faixas_desconto(ctx: dict) -> dict:
    """KPIs da Política de Descontos: kpis(simular(faixas em edição na tela, vigentes))."""
    pq, faixas, vig, editado = _politica(ctx)
    erro = pq.validar(faixas)
    if erro:
        return _ok(f"As faixas em edição estão inválidas: {erro}. Corrija para simular.")
    r = pq.simular(faixas, vig)
    k = pq.kpis(r)
    origem = "faixas em edição (não aplicadas)" if editado else "política vigente"
    msg = (f"Simulação com as {origem} sobre {k['n']} pedidos reais: impacto em desconto {ad.brl(k['impacto'])} vs vigente, "
           f"{k['n_cobertos']} pedidos com algum desconto ({_pct(k['cobertos'])}), ticket médio {ad.brl(k['ticket'])}. Descontos compostos (RN-029).")
    return _ok(msg, {**k}, {"faixas": "em edição" if editado else "vigentes"})


def politica_segmento(ctx: dict) -> dict:
    """Gráfico de impacto por segmento: impacto_segmento(simular(...))."""
    pq, faixas, vig, editado = _politica(ctx)
    if pq.validar(faixas):
        return _ok("As faixas em edição estão inválidas; corrija para simular.")
    g = pq.impacto_segmento(pq.simular(faixas, vig)["sim"])
    if not editado or g["variacao_pct"].abs().max() < 1e-9:
        return _ok("As faixas na tela são iguais às vigentes — nenhum segmento muda. Edite as faixas para comparar.", {"itens": _records(g, 5)})
    msg = "Variação da receita líquida por segmento com as faixas em edição: " + "; ".join(f"{r.segmento} {_pct(r.variacao_pct, True)}" for r in g.itertuples()) + "."
    return _ok(msg, {"itens": _records(g.rename(columns={"t": "receita_simulada", "a": "receita_atual"}), 5)}, {"faixas": "em edição"})


def politica_distribuicao(ctx: dict) -> dict:
    """Gráfico de distribuição por faixa (Volume, Mix, Fidelidade): distribuicao(simular(...)["sim"], tipo)."""
    pq, faixas, vig, editado = _politica(ctx)
    if pq.validar(faixas):
        return _ok("As faixas em edição estão inválidas; corrija para simular.")
    sim = pq.simular(faixas, vig)["sim"]
    partes, linhas = [], []
    for t in pq.TIPOS:
        dist = pq.distribuicao(sim, t)
        sem = int(dist.loc[dist["faixa"] == "Sem faixa", "n_pedidos"].sum())
        partes.append(f"{t}: {len(sim) - sem} de {len(sim)} pedidos em alguma faixa")
        linhas += [{"tipo": t, **r} for r in dist.to_dict("records")]
    return _ok("; ".join(partes) + ".", {"itens": _records(pd.DataFrame(linhas), 20)}, {"faixas": "em edição" if editado else "vigentes"})


# >>> Gerar 2–5 handlers por tela do projeto seguindo os exemplos: chamar as funções *_queries.py da tela com _p(ctx) (params publicados pela
#     tela via screen_params) e devolver _ok(msg, data, params). Registrar todos aqui (ids = ids do catálogo).
PAGE_HANDLERS = {
    "dash_resumo": dash_resumo, "dash_categorias": dash_categorias, "dash_top_clientes": dash_top_clientes, "dash_mix_canal": dash_mix_canal,
    "reforma_produto": reforma_produto, "reforma_transicao": reforma_transicao,
    "faixas_desconto": faixas_desconto, "politica_segmento": politica_segmento, "politica_distribuicao": politica_distribuicao,
}
