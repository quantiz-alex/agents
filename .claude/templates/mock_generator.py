"""
mock_generator.py — Motor de dados de demonstração do pipeline Lighthouse (v4).
Copie para scripts/mock_generator.py no projeto. O data-engineer gera docs/mock_spec.yaml
(a partir de Volumetria/Distribuições do roadmap + data_model.yaml) e um scripts/generate_mock.py
que chama `generate(spec, out_dir, seed_sql)`.

Uso direto:
    python scripts/mock_generator.py docs/mock_spec.yaml --out mock_data --seed-sql database/seed.sql

Spec (YAML ou dict):
    seed: 42
    period_months: 24            # janela dos fatos com data (termina hoje)
    seed_cap: 2000               # máx. de linhas por tabela no seed.sql (CSV completo sempre)
    entities:
      - name: fornecedor          # = nome do arquivo (mock_data/fornecedor.csv)
        table: fornecedor         # = tabela no seed.sql
        role: dimensao | fato | apoio
        volume: 35
        fixed_rows: [{...}]       # linhas garantidas (ex.: credenciais de demo)
        fields:
          - {name: id, type: int, gen: sequence}
          - {name: nome, type: varchar(120), gen: "lista(BR:empresas)"}
          - {name: regiao, type: varchar(20), gen: "enum(Sudeste:45%, Sul:25%, Nordeste:20%, Centro-Oeste:10%)"}
          - {name: ativo, type: bit, gen: "enum(1:94%, 0:6%)"}
          - {name: created_at, type: datetime2, gen: audit}

Geradores (campo `gen`) — mesma sintaxe da seção "Distribuições" do roadmap:
    sequence                          ids 1..N
    enum(A:60%, B:30%, C:10%)         valores com pesos (sem % → uniforme; separador "/" também aceito)
    faixa(min–max)                    uniforme (int se ambos inteiros); para datas: faixa(últimos 6 meses)
    normal(media, desvio[, min[, max]])
    pareto([min, max])                80/20 — poucos itens concentram valor (lognormal)
    sazonal(mensal, pico: nov,dez) [+ tendencia(+8% ao ano)]   datas com sazonalidade/tendência
    tendencia(+8% ao ano)             só tendência
    fk(entidade[, pareto])            id de outra entidade (pareto → alguns pais muito mais frequentes)
    derivado(<expr>)                  expressão pandas sobre a MESMA linha; refs `pai.campo` via FK; funções normal(m,s), faixa(a,b), round(x,n), clip(x,a,b)
    se(<cond>, <gen>, <gen|null>)     condicional (cond em sintaxe pandas.eval)
    lista(BR:empresas|cidades|uf|nomes|emails|produtos[:dominio]|cnpj|cep)   catálogos pt-BR embutidos
    codigo(PREFIX[, N])               PREFIX-0001 ; codigo(campo:3) usa 3 letras do campo
    email(nome_campo[, dominio])      e-mail derivado do nome
    bcrypt(texto)                     hash bcrypt (passlib) — senha demo
    texto(N)                          frase pt-BR curta de ~N palavras
    json(campo1, campo2, ...)         JSON com valores de outros campos da linha
    audit                             created_at/updated_at coerentes
    null                              sempre nulo
    constante(valor)                  valor fixo
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# ============================================================================
# CATÁLOGOS pt-BR
# ============================================================================

_EMPRESAS_BASE = ["Horizonte", "Atlântica", "Nova Era", "Primavera", "Serra Azul", "Vale Verde", "Ipiranga", "Andrade", "Bandeirantes", "Continental",
                  "Meridional", "Planalto", "Litoral", "Aurora", "Pioneira", "Central", "Brasil Sul", "Norte Forte", "Estrela", "Real",
                  "Imperial", "Cruzeiro", "Tropical", "Guanabara", "Paulista", "Mineira", "Gaúcha", "Nordestina", "Pantanal", "Amazônia"]
_EMPRESAS_TIPO = ["Comércio", "Distribuidora", "Indústria", "Autopeças", "Logística", "Atacado", "Suprimentos", "Peças e Serviços", "Importadora", "Representações"]
_EMPRESAS_SUFIXO = ["Ltda", "S.A.", "ME", "EIRELI", "& Cia"]

_CIDADES = [("São Paulo", "SP"), ("Campinas", "SP"), ("Ribeirão Preto", "SP"), ("Sorocaba", "SP"), ("Santos", "SP"), ("São José dos Campos", "SP"),
            ("Rio de Janeiro", "RJ"), ("Niterói", "RJ"), ("Petrópolis", "RJ"), ("Belo Horizonte", "MG"), ("Uberlândia", "MG"), ("Juiz de Fora", "MG"),
            ("Curitiba", "PR"), ("Londrina", "PR"), ("Maringá", "PR"), ("Porto Alegre", "RS"), ("Caxias do Sul", "RS"), ("Pelotas", "RS"),
            ("Florianópolis", "SC"), ("Joinville", "SC"), ("Blumenau", "SC"), ("Salvador", "BA"), ("Feira de Santana", "BA"), ("Recife", "PE"),
            ("Caruaru", "PE"), ("Fortaleza", "CE"), ("Natal", "RN"), ("João Pessoa", "PB"), ("Maceió", "AL"), ("Aracaju", "SE"), ("São Luís", "MA"),
            ("Teresina", "PI"), ("Belém", "PA"), ("Manaus", "AM"), ("Goiânia", "GO"), ("Anápolis", "GO"), ("Brasília", "DF"), ("Cuiabá", "MT"),
            ("Campo Grande", "MS"), ("Vitória", "ES"), ("Vila Velha", "ES"), ("Palmas", "TO"), ("Porto Velho", "RO"), ("Macapá", "AP")]
_UF_REGIAO = {"SP": "Sudeste", "RJ": "Sudeste", "MG": "Sudeste", "ES": "Sudeste", "PR": "Sul", "RS": "Sul", "SC": "Sul",
              "BA": "Nordeste", "PE": "Nordeste", "CE": "Nordeste", "RN": "Nordeste", "PB": "Nordeste", "AL": "Nordeste", "SE": "Nordeste", "MA": "Nordeste", "PI": "Nordeste",
              "PA": "Norte", "AM": "Norte", "TO": "Norte", "RO": "Norte", "AP": "Norte", "AC": "Norte", "RR": "Norte", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste", "DF": "Centro-Oeste"}

_NOMES = ["Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela", "Henrique", "Isabela", "João", "Juliana", "Lucas", "Mariana", "Mateus",
          "Natália", "Otávio", "Paula", "Rafael", "Renata", "Rodrigo", "Sofia", "Thiago", "Vanessa", "Vinícius", "Beatriz", "Caio", "Camila", "Diego",
          "Fernanda", "Gustavo", "Helena", "Igor", "Larissa", "Leonardo", "Letícia", "Marcelo", "Patrícia", "Pedro", "Priscila", "Ricardo"]
_SOBRENOMES = ["Silva", "Souza", "Oliveira", "Santos", "Pereira", "Lima", "Carvalho", "Ferreira", "Rodrigues", "Almeida", "Costa", "Gomes", "Martins",
               "Araújo", "Melo", "Barbosa", "Ribeiro", "Alves", "Monteiro", "Cardoso", "Rocha", "Dias", "Nascimento", "Moreira", "Teixeira", "Correia",
               "Castro", "Campos", "Freitas", "Pinto", "Nunes", "Batista", "Vieira", "Mendes", "Ramos", "Azevedo", "Cavalcanti", "Duarte", "Fonseca", "Lopes"]

_PRODUTOS = {
    "generico": (["Kit", "Conjunto", "Unidade", "Módulo", "Pacote", "Linha", "Item"], ["Premium", "Standard", "Plus", "Pro", "Eco", "Max", "Compact"], ["A", "B", "C", "X", "S", "M", "L"]),
    "autopecas": (["Bateria 60Ah", "Bateria 70Ah", "Bateria 45Ah", "Filtro de Óleo", "Filtro de Ar", "Filtro de Combustível", "Pastilha de Freio", "Disco de Freio",
                   "Amortecedor Dianteiro", "Amortecedor Traseiro", "Mola Helicoidal", "Lâmpada H4", "Lâmpada LED", "Farol Auxiliar", "Óleo 5W30 1L", "Óleo 15W40 1L",
                   "Fluido de Freio", "Alternador", "Motor de Partida", "Bobina de Ignição", "Velas", "Correia Dentada", "Palheta Limpador", "Tapete", "Capa de Volante"],
                  ["Heavy Duty", "Standard", "Premium", "Original", "Reforçado", "Linha Leve", "Linha Pesada"], ["Gol", "Onix", "HB20", "Corolla", "Civic", "Strada", "Hilux", "Uno", "Palio", "Ka"]),
    "agro": (["Fertilizante NPK", "Herbicida", "Fungicida", "Inseticida", "Semente de Soja", "Semente de Milho", "Adjuvante", "Corretivo de Solo", "Inoculante", "Micronutriente"],
             ["Concentrado", "Granulado", "Líquido", "Premium", "Padrão"], ["20L", "5L", "1L", "25kg", "50kg", "saca 40kg"]),
    "varejo": (["Arroz", "Feijão", "Açúcar", "Café", "Óleo de Soja", "Leite", "Macarrão", "Farinha", "Refrigerante", "Sabão em Pó", "Detergente", "Papel Higiênico", "Biscoito", "Achocolatado"],
               ["Tipo 1", "Premium", "Tradicional", "Integral", "Light", "Família"], ["1kg", "5kg", "500g", "2L", "900ml", "12un"]),
    "farma": (["Analgésico", "Antitérmico", "Anti-inflamatório", "Antialérgico", "Vitamina C", "Vitamina D", "Protetor Solar", "Hidratante", "Xarope", "Pomada"],
              ["500mg", "750mg", "1g", "Infantil", "Adulto", "FPS 50", "FPS 30"], ["20 comp.", "10 comp.", "120ml", "200ml", "60g"]),
    "industria": (["Parafuso Sextavado", "Porca", "Arruela", "Rolamento", "Correia", "Mangueira Hidráulica", "Válvula", "Motor Elétrico", "Redutor", "Sensor Indutivo", "Chapa de Aço", "Tubo Galvanizado"],
                  ["M6", "M8", "M10", "M12", "1/2\"", "3/4\"", "Inox", "Galvanizado", "Aço Carbono"], ["100un", "50un", "1m", "6m", "cx"]),
    "servicos": (["Consultoria", "Manutenção", "Suporte", "Treinamento", "Implantação", "Licença", "Auditoria", "Assessoria"],
                 ["Básico", "Intermediário", "Avançado", "Enterprise"], ["mensal", "anual", "por hora", "por projeto"]),
}

_PALAVRAS = ["análise", "reajuste", "cenário", "margem", "cliente", "proposta", "revisão", "trimestre", "estratégia", "canal", "região", "meta",
             "aprovação", "ajuste", "impacto", "volume", "produto", "custo", "mercado", "concorrência", "elasticidade", "campanha", "família", "portfólio"]

_MESES = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}

# hash bcrypt de "demo" (fallback quando passlib não está instalado)
_BCRYPT_DEMO_FALLBACK = "$2b$12$6bK0mQ9uT6qkA9C6fY4y3eTqzZ7Yk4t0xY1nHfN6e3qq3q3q3q3q."

# ============================================================================
# PARSER DE SPEC DE GERADOR
# ============================================================================


def _split_args(s: str) -> list[str]:
    """Divide argumentos por vírgula respeitando parênteses/colchetes/aspas."""
    out, depth, cur, quote = [], 0, "", None
    for ch in s:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch; cur += ch; continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def _parse_gen(spec: str | None) -> list[tuple[str, str]]:
    """'sazonal(mensal, pico: nov,dez) + tendencia(+8% ao ano)' → [('sazonal','mensal, pico: nov,dez'), ('tendencia','+8% ao ano')]"""
    if spec is None:
        return [("null", "")]
    spec = str(spec).strip()
    if spec.lower() in ("null", "none", ""):
        return [("null", "")]
    parts, depth, cur = [], 0, ""
    for ch in spec:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "+" and depth == 0:
            parts.append(cur.strip()); cur = ""
        else:
            cur += ch
    parts.append(cur.strip())
    result = []
    for p in parts:
        m = re.match(r"^([a-zA-Z_]+)\s*(?:\((.*)\))?$", p, re.S)
        if not m:
            result.append(("constante", p))
        else:
            result.append((m.group(1).lower(), (m.group(2) or "").strip()))
    return result


def _num(s: str) -> float:
    s = s.strip().replace("%", "").replace("R$", "").replace(" ", "")
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    elif "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    return float(s)


def _is_int_type(t: str | None) -> bool:
    return bool(t) and t.lower().split("(")[0] in ("int", "bigint", "smallint", "tinyint")


def _is_decimal_type(t: str | None) -> bool:
    return bool(t) and t.lower().split("(")[0] in ("decimal", "numeric", "float", "money", "real")


def _decimals(t: str | None) -> int:
    m = re.search(r"\(\s*\d+\s*,\s*(\d+)\s*\)", t or "")
    return int(m.group(1)) if m else 2


def _is_date_type(t: str | None) -> bool:
    return bool(t) and t.lower().split("(")[0] in ("date", "datetime", "datetime2", "smalldatetime")


def _slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", ".", s.lower()).strip(".")


# ============================================================================
# GERADOR
# ============================================================================


class MockGenerator:
    def __init__(self, spec: dict[str, Any]):
        self.spec = spec
        self.rng = np.random.default_rng(int(spec.get("seed", 42)))
        self.period_months = int(spec.get("period_months", 24))
        self.end = pd.Timestamp(spec.get("end_date") or date.today()).normalize()
        self.start = (self.end - pd.DateOffset(months=self.period_months)).normalize()
        self.tables: dict[str, pd.DataFrame] = {}
        self.entities = {e["name"]: e for e in spec["entities"]}
        self.warnings: list[str] = []

    # ------------------------------------------------------------------ ordem
    def _deps(self, ent: dict) -> set[str]:
        deps = set()
        for f in ent.get("fields", []):
            for kind, args in _parse_gen(f.get("gen")):
                if kind == "fk":
                    deps.add(_split_args(args)[0].strip())
                if kind in ("derivado", "se", "json"):
                    for ref in re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.[a-zA-Z_]", args):
                        if ref in self.entities and ref != ent["name"]:
                            deps.add(ref)
        return deps

    def _order(self) -> list[dict]:
        done, order = set(), []
        pending = list(self.spec["entities"])
        while pending:
            progressed = False
            for e in list(pending):
                if self._deps(e) <= done:
                    order.append(e); done.add(e["name"]); pending.remove(e); progressed = True
            if not progressed:
                names = [e["name"] for e in pending]
                raise ValueError(f"Dependência circular/ausente entre entidades: {names}")
        return order

    # --------------------------------------------------------------- primitivos
    def _enum(self, args: str, n: int) -> np.ndarray:
        items = _split_args(args) if "," in args else [a.strip() for a in args.split("/")]
        vals, weights = [], []
        for it in items:
            if ":" in it and re.search(r":\s*[\d.,]+\s*%?\s*$", it):
                v, w = it.rsplit(":", 1)
                vals.append(v.strip().strip("'\"")); weights.append(_num(w))
            else:
                vals.append(it.strip().strip("'\"")); weights.append(1.0)
        w = np.array(weights, dtype=float); w = w / w.sum()
        return self.rng.choice(np.array(vals, dtype=object), size=n, p=w)

    def _faixa(self, args: str, n: int, ftype: str | None) -> np.ndarray:
        a = args.replace("–", "-").replace("—", "-")
        m = re.match(r"^\s*(-?[\d.,]+)\s*-\s*(-?[\d.,]+)\s*$", a)
        if m:
            lo, hi = _num(m.group(1)), _num(m.group(2))
            if _is_int_type(ftype) or (lo.is_integer() and hi.is_integer() and not _is_decimal_type(ftype)):
                return self.rng.integers(int(lo), int(hi) + 1, size=n)
            return self.rng.uniform(lo, hi, size=n)
        m = re.match(r"últimos?\s+(\d+)\s+(dias?|meses|semanas?|anos?)", a, re.I)
        if m:
            q, unit = int(m.group(1)), m.group(2).lower()
            days = q * {"d": 1, "s": 7, "m": 30, "a": 365}[unit[0]]
            offs = self.rng.integers(0, days + 1, size=n)
            return np.array([self.end - pd.Timedelta(days=int(d)) for d in offs], dtype=object)
        raise ValueError(f"faixa inválida: {args}")

    def _normal(self, args: str, n: int, ftype: str | None) -> np.ndarray:
        p = [_num(x) for x in _split_args(args)]
        mean, sd = p[0], p[1] if len(p) > 1 else abs(p[0]) * 0.2
        v = self.rng.normal(mean, sd, size=n)
        lo = p[2] if len(p) > 2 else (1 if _is_int_type(ftype) and mean > 0 else None)
        hi = p[3] if len(p) > 3 else None
        if lo is not None or hi is not None:
            v = np.clip(v, lo if lo is not None else -np.inf, hi if hi is not None else np.inf)
        return np.rint(v).astype(int) if _is_int_type(ftype) else v

    def _pareto(self, args: str, n: int, ftype: str | None) -> np.ndarray:
        p = [_num(x) for x in _split_args(args)] if args else []
        lo, hi = (p[0], p[1]) if len(p) >= 2 else (10.0, 5000.0)
        raw = self.rng.lognormal(mean=0.0, sigma=1.1, size=n)
        raw = (raw - raw.min()) / (raw.max() - raw.min() + 1e-9)
        v = lo + raw ** 1.6 * (hi - lo)
        return np.rint(v).astype(int) if _is_int_type(ftype) else v

    def _dates(self, gens: list[tuple[str, str]], n: int, ftype: str | None) -> np.ndarray:
        """sazonal + tendencia → amostra de datas no período, com pesos por mês e crescimento."""
        months = pd.period_range(self.start, self.end, freq="M")
        w = np.ones(len(months))
        for kind, args in gens:
            if kind == "sazonal":
                peaks = re.findall(r"pico\s*:\s*([a-zç,\s]+)", args, re.I)
                peak_months = set()
                for grp in peaks:
                    for tok in re.split(r"[,\s]+", grp.strip()):
                        if tok[:3].lower() in _MESES:
                            peak_months.add(_MESES[tok[:3].lower()])
                for i, m in enumerate(months):
                    if m.month in peak_months:
                        w[i] *= 1.7
                    elif (m.month - 1) % 12 + 1 in peak_months or (m.month + 1 - 1) % 12 + 1 in peak_months:
                        w[i] *= 1.2
            if kind == "tendencia":
                m = re.search(r"([+-]?\s*[\d.,]+)\s*%", args)
                yearly = _num(m.group(1)) / 100 if m else 0.08
                for i in range(len(months)):
                    w[i] *= (1 + yearly) ** (i / 12)
        w = w / w.sum()
        idx = self.rng.choice(len(months), size=n, p=w)
        out = []
        for i in idx:
            m = months[i]
            day_lo = m.start_time if m.start_time > self.start else self.start
            day_hi = m.end_time if m.end_time < self.end else self.end
            span = max(int((day_hi - day_lo).days), 0)
            d = day_lo + pd.Timedelta(days=int(self.rng.integers(0, span + 1)))
            if _is_date_type(ftype) and ftype.lower().startswith("datetime"):
                d = d + pd.Timedelta(hours=int(self.rng.integers(8, 19)), minutes=int(self.rng.integers(0, 60)))
            out.append(d.normalize() if not ftype or ftype.lower() == "date" else d)
        return np.array(out, dtype=object)

    def _fk(self, args: str, n: int) -> np.ndarray:
        a = _split_args(args)
        parent = a[0].strip()
        if parent not in self.tables:
            raise ValueError(f"fk({parent}) — entidade pai ainda não gerada")
        ids = self.tables[parent]["id"].to_numpy()
        if len(a) > 1 and a[1].strip().lower() == "pareto":
            w = self.rng.lognormal(0, 1.0, size=len(ids)); w = w / w.sum()
            return self.rng.choice(ids, size=n, p=w)
        return self.rng.choice(ids, size=n)

    def _lista(self, args: str, n: int, df: pd.DataFrame, field: str) -> np.ndarray:
        kind = args.strip().lower().replace("br:", "")
        if kind == "empresas":
            vals = [f"{self.rng.choice(_EMPRESAS_TIPO)} {self.rng.choice(_EMPRESAS_BASE)} {self.rng.choice(_EMPRESAS_SUFIXO)}" for _ in range(n)]
            return self._dedupe(vals)
        if kind == "cidades":
            idx = self.rng.integers(0, len(_CIDADES), size=n)
            return np.array([_CIDADES[i][0] for i in idx], dtype=object)
        if kind in ("uf", "estados"):
            if "cidade" in df.columns:
                lookup = {c: u for c, u in _CIDADES}
                return np.array([lookup.get(c, "SP") for c in df["cidade"]], dtype=object)
            return np.array([_CIDADES[i][1] for i in self.rng.integers(0, len(_CIDADES), size=n)], dtype=object)
        if kind in ("regiao", "regioes"):
            if "uf" in df.columns:
                return np.array([_UF_REGIAO.get(u, "Sudeste") for u in df["uf"]], dtype=object)
            return self._enum("Sudeste:45%, Sul:25%, Nordeste:20%, Centro-Oeste:10%", n)
        if kind == "nomes":
            return self._dedupe([f"{self.rng.choice(_NOMES)} {self.rng.choice(_SOBRENOMES)}" for _ in range(n)])
        if kind == "emails":
            base = df["nome"] if "nome" in df.columns else self._lista("nomes", n, df, field)
            return np.array([f"{_slug(str(nm))}@empresa.com.br" for nm in base], dtype=object)
        if kind.startswith("produtos"):
            dom = kind.split(":", 1)[1] if ":" in kind else "generico"
            base, var, sfx = _PRODUTOS.get(dom, _PRODUTOS["generico"])
            vals = [f"{self.rng.choice(base)} {self.rng.choice(var)} {self.rng.choice(sfx)}" for _ in range(n)]
            return self._dedupe(vals)
        if kind == "cnpj":
            return np.array([f"{self.rng.integers(10,99):02d}.{self.rng.integers(100,999):03d}.{self.rng.integers(100,999):03d}/0001-{self.rng.integers(10,99):02d}" for _ in range(n)], dtype=object)
        if kind == "cep":
            return np.array([f"{self.rng.integers(10000,99999):05d}-{self.rng.integers(100,999):03d}" for _ in range(n)], dtype=object)
        raise ValueError(f"lista desconhecida: {args}")

    def _dedupe(self, vals: list[str]) -> np.ndarray:
        seen: dict[str, int] = {}
        out = []
        for v in vals:
            if v in seen:
                seen[v] += 1; out.append(f"{v} {seen[v]}")
            else:
                seen[v] = 1; out.append(v)
        return np.array(out, dtype=object)

    def _codigo(self, args: str, n: int, df: pd.DataFrame) -> np.ndarray:
        a = _split_args(args)
        width = int(a[1]) if len(a) > 1 else 4
        if ":" in a[0]:
            fld, k = a[0].split(":"); k = int(k)
            counters: dict[str, int] = {}
            out = []
            for v in df[fld.strip()]:
                pref = _slug(str(v)).replace(".", "")[:k].upper()
                counters[pref] = counters.get(pref, 0) + 1
                out.append(f"{pref}-{counters[pref]:0{width}d}")
            return np.array(out, dtype=object)
        pref = a[0].strip().strip("'\"")
        return np.array([f"{pref}-{i:0{width}d}" for i in range(1, n + 1)], dtype=object)

    def _email(self, args: str, df: pd.DataFrame) -> np.ndarray:
        a = _split_args(args)
        dom = a[1].strip() if len(a) > 1 else "empresa.com.br"
        return np.array([f"{_slug(str(nm))}@{dom}" for nm in df[a[0].strip()]], dtype=object)

    def _bcrypt(self, args: str, n: int) -> np.ndarray:
        pwd = args.strip().strip("'\"") or "demo"
        h = None
        try:
            import bcrypt as _bcrypt  # type: ignore  — mesmo backend que o passlib usa no backend/auth.py
            h = _bcrypt.hashpw(pwd.encode("utf-8"), _bcrypt.gensalt(rounds=12)).decode("ascii")
        except Exception:  # noqa: BLE001
            try:
                import logging
                logging.getLogger("passlib").setLevel(logging.ERROR)
                from passlib.context import CryptContext  # type: ignore
                h = CryptContext(schemes=["bcrypt"]).hash(pwd)
            except Exception:  # noqa: BLE001
                h = _BCRYPT_DEMO_FALLBACK
                self.warnings.append("bcrypt/passlib indisponíveis — senha_hash usa hash fixo (instale passlib[bcrypt] e regere para login via API)")
        return np.array([h] * n, dtype=object)

    def _texto(self, args: str, n: int) -> np.ndarray:
        k = int(_num(args)) if args else 8
        out = []
        for _ in range(n):
            words = list(self.rng.choice(_PALAVRAS, size=max(k, 3), replace=True))
            out.append((" ".join(words)).capitalize() + ".")
        return np.array(out, dtype=object)

    def _json(self, args: str, df: pd.DataFrame) -> np.ndarray:
        cols = [c.strip() for c in _split_args(args)]
        return np.array([json.dumps({c: (None if pd.isna(r[c]) else (r[c].item() if hasattr(r[c], "item") else r[c])) for c in cols if c in df.columns}, ensure_ascii=False, default=str) for _, r in df.iterrows()], dtype=object)

    # ------------------------------------------------------------- derivados
    def _namespace(self, df: pd.DataFrame, ent: dict) -> dict[str, Any]:
        n = len(df)
        ns: dict[str, Any] = {c: df[c] for c in df.columns}
        ns.update({
            "normal": lambda m, s: pd.Series(self.rng.normal(m, s, size=n), index=df.index),
            "faixa": lambda a, b: pd.Series(self.rng.uniform(a, b, size=n), index=df.index),
            "round": lambda x, k=2: np.round(x, k),
            "clip": lambda x, a, b: np.clip(x, a, b),
            "abs": np.abs, "log": np.log, "exp": np.exp, "sqrt": np.sqrt, "where": np.where, "np": np, "pd": pd,
        })
        # refs pai.campo via FK: procura campo <pai>_id na entidade
        for parent in self.tables:
            fk_col = f"{parent}_id"
            if fk_col in df.columns:
                pdf = self.tables[parent].set_index("id")
                class _Ref:  # noqa: D401
                    def __init__(s, pdf, keys): s.pdf, s.keys = pdf, keys
                    def __getattr__(s, item): return s.pdf[item].reindex(s.keys).to_numpy()
                ns[parent] = _Ref(pdf, df[fk_col].to_numpy())
        return ns

    def _derivado(self, expr: str, df: pd.DataFrame, ent: dict) -> np.ndarray:
        ns = self._namespace(df, ent)
        # pai.campo → ns[pai].campo já resolve por __getattr__
        val = eval(expr, {"__builtins__": {}}, ns)  # noqa: S307 — spec controlada pelo pipeline
        return np.asarray(pd.Series(val, index=df.index) if np.ndim(val) else np.full(len(df), val))

    def _se(self, args: str, df: pd.DataFrame, ent: dict, ftype: str | None, field: str) -> np.ndarray:
        cond_s, gen_true, gen_false = (_split_args(args) + ["null", "null"])[:3]
        try:
            mask = np.asarray(df.eval(cond_s, engine="python"), dtype=bool)          # suporta `or`/`and`/`in`
        except Exception:  # noqa: BLE001 — condição com refs pai.campo → eval python com operadores vetoriais
            ns = self._namespace(df, ent)
            cond_py = re.sub(r"\s+or\s+", " | ", re.sub(r"\s+and\s+", " & ", cond_s))
            mask = np.asarray(eval(cond_py, {"__builtins__": {}}, ns), dtype=bool)  # noqa: S307
        vt = self._gen_field({"name": field, "type": ftype, "gen": gen_true}, df, ent)
        vf = self._gen_field({"name": field, "type": ftype, "gen": gen_false}, df, ent)
        out = np.array(vf, dtype=object); out[mask] = np.array(vt, dtype=object)[mask]
        return out

    # ------------------------------------------------------------- por campo
    def _gen_field(self, f: dict, df: pd.DataFrame, ent: dict) -> np.ndarray:
        n = len(df)
        ftype = f.get("type")
        gens = _parse_gen(f.get("gen"))
        kinds = [k for k, _ in gens]
        if "sazonal" in kinds or "tendencia" in kinds:
            return self._dates(gens, n, ftype or "date")
        kind, args = gens[0]
        if kind == "sequence":
            return np.arange(1, n + 1)
        if kind == "null":
            return np.full(n, None, dtype=object)
        if kind == "constante":
            v = args.strip().strip("'\"")
            return np.full(n, v, dtype=object)
        if kind == "enum":
            return self._enum(args, n)
        if kind == "faixa":
            return self._faixa(args, n, ftype)
        if kind == "normal":
            return self._normal(args, n, ftype)
        if kind == "pareto":
            return self._pareto(args, n, ftype)
        if kind == "fk":
            return self._fk(args, n)
        if kind == "lista":
            return self._lista(args, n, df, f["name"])
        if kind == "codigo":
            return self._codigo(args, n, df)
        if kind == "email":
            return self._email(args, df)
        if kind == "bcrypt":
            return self._bcrypt(args, n)
        if kind == "texto":
            return self._texto(args, n)
        if kind == "json":
            return self._json(args, df)
        if kind == "derivado":
            return self._derivado(args, df, ent)
        if kind == "se":
            return self._se(args, df, ent, ftype, f["name"])
        if kind == "audit":
            if "created_at" in df.columns and f["name"] == "updated_at":
                base = pd.to_datetime(df["created_at"], errors="coerce")
                return np.array([c + pd.Timedelta(days=int(d)) for c, d in zip(base, self.rng.integers(0, 40, size=n))], dtype=object)
            return self._dates([("tendencia", "+0%")], n, "datetime2")
        raise ValueError(f"gerador desconhecido '{kind}' no campo {ent['name']}.{f['name']}")

    def _cast(self, vals: np.ndarray, ftype: str | None) -> pd.Series:
        s = pd.Series(vals)
        if s.isna().all():
            return s
        if _is_int_type(ftype):
            return pd.to_numeric(s, errors="coerce").round().astype("Int64")
        if _is_decimal_type(ftype):
            return pd.to_numeric(s, errors="coerce").round(_decimals(ftype))
        if ftype and ftype.lower() == "bit":
            return s.map(lambda v: None if v is None or (isinstance(v, float) and math.isnan(v)) else int(str(v).strip().lower() in ("1", "true", "sim", "ativo"))).astype("Int64")
        if _is_date_type(ftype):
            dt = pd.to_datetime(s, errors="coerce")
            return dt.dt.strftime("%Y-%m-%d") if ftype.lower() == "date" else dt.dt.strftime("%Y-%m-%dT%H:%M:%S")
        return s

    # -------------------------------------------------------------- entidade
    def _generate_entity(self, ent: dict) -> pd.DataFrame:
        fixed = ent.get("fixed_rows") or []
        n = max(int(ent.get("volume", 50)), len(fixed))
        df = pd.DataFrame(index=range(n))
        fields = list(ent.get("fields", []))
        if not any(f["name"] == "id" for f in fields):
            fields.insert(0, {"name": "id", "type": "int", "gen": "sequence"})
        # ordem: campos sem dependência de outros campos primeiro (derivado/se/json/email/codigo(campo)/lista(uf/regiao/emails)/audit updated_at por último)
        late = {"derivado", "se", "json", "email"}
        def _rank(f: dict) -> int:
            k = _parse_gen(f.get("gen"))[0][0]
            if k == "sequence": return 0
            if k in late: return 3
            if k == "audit" and f["name"] == "updated_at": return 4
            if k == "codigo" and ":" in (f.get("gen") or ""): return 2
            if k == "lista" and any(t in (f.get("gen") or "").lower() for t in ("uf", "estados", "regiao", "emails")): return 2
            return 1
        for f in sorted(fields, key=_rank):
            vals = self._gen_field(f, df, ent)
            df[f["name"]] = self._cast(vals, f.get("type"))
        # linhas fixas sobrescrevem as primeiras
        for i, row in enumerate(fixed):
            for k, v in row.items():
                if k in df.columns:
                    df.at[i, k] = v
                else:
                    df[k] = None; df.at[i, k] = v
        df = df[[f["name"] for f in fields] + [c for c in df.columns if c not in {f["name"] for f in fields}]]
        return df

    def run(self) -> dict[str, pd.DataFrame]:
        for ent in self._order():
            self.tables[ent["name"]] = self._generate_entity(ent)
        return self.tables


# ============================================================================
# SAÍDA: CSV + JSON + seed.sql
# ============================================================================


def _to_json_records(df: pd.DataFrame, ent: dict) -> list[dict]:
    bit_cols = {f["name"] for f in ent.get("fields", []) if (f.get("type") or "").lower() == "bit"}
    recs = []
    for r in df.to_dict("records"):
        out = {}
        for k, v in r.items():
            if v is None or (isinstance(v, float) and math.isnan(v)) or v is pd.NA:
                out[k] = None
            elif k in bit_cols:
                out[k] = bool(int(v))
            elif hasattr(v, "item"):
                out[k] = v.item()
            else:
                out[k] = v
        recs.append(out)
    return recs


def _sql_literal(v: Any, ftype: str | None) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)) or v is pd.NA:
        return "NULL"
    if _is_int_type(ftype) or (ftype or "").lower() == "bit":
        return str(int(v))
    if _is_decimal_type(ftype):
        return f"{float(v):.{_decimals(ftype)}f}"
    s = str(v).replace("'", "''")
    return f"N'{s}'"


def write_outputs(gen: MockGenerator, out_dir: str | Path = "mock_data", seed_sql: str | Path | None = None) -> dict[str, int]:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    sql_parts: list[str] = []
    cap = int(gen.spec.get("seed_cap", 2000))
    for ent in gen._order():
        df = gen.tables[ent["name"]]
        df.to_csv(out / f"{ent['name']}.csv", index=False, encoding="utf-8")
        (out / f"{ent['name']}.json").write_text(json.dumps(_to_json_records(df, ent), ensure_ascii=False, indent=None, default=str), encoding="utf-8")
        counts[ent["name"]] = len(df)
        if seed_sql:
            table = ent.get("table", ent["name"])
            types = {f["name"]: f.get("type") for f in ent.get("fields", [])}
            cols = list(df.columns)
            sub = df.head(cap)
            sql_parts.append(f"-- {table}: {len(sub)} de {len(df)} linhas (cap={cap}; CSV completo em mock_data/{ent['name']}.csv)")
            sql_parts.append(f"SET IDENTITY_INSERT [dbo].[{table}] ON;")
            for start in range(0, len(sub), 500):
                chunk = sub.iloc[start:start + 500]
                lo, hi = int(chunk["id"].min()), int(chunk["id"].max())
                values = ",\n  ".join("(" + ", ".join(_sql_literal(r[c], types.get(c)) for c in cols) + ")" for _, r in chunk.iterrows())
                sql_parts.append(f"IF NOT EXISTS (SELECT 1 FROM [dbo].[{table}] WHERE id BETWEEN {lo} AND {hi})\nINSERT INTO [dbo].[{table}] ({', '.join(f'[{c}]' for c in cols)}) VALUES\n  {values};")
            sql_parts.append(f"SET IDENTITY_INSERT [dbo].[{table}] OFF;\nGO\n")
    if seed_sql:
        Path(seed_sql).parent.mkdir(parents=True, exist_ok=True)
        header = f"-- seed.sql gerado por mock_generator.py em {datetime.now():%Y-%m-%d %H:%M} (seed={gen.spec.get('seed', 42)})\n-- Idempotente por faixa de id. Ordem topológica de FKs.\n\n"
        Path(seed_sql).write_text(header + "\n".join(sql_parts), encoding="utf-8")
    return counts


def load_spec(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    if str(path).endswith((".yaml", ".yml")):
        try:
            import yaml  # type: ignore
            return yaml.safe_load(text)
        except ImportError as e:  # pragma: no cover
            raise SystemExit("pyyaml não instalado — use spec .json ou `pip install pyyaml`") from e
    return json.loads(text)


def generate(spec: dict[str, Any] | str | Path, out_dir: str | Path = "mock_data", seed_sql: str | Path | None = None, verbose: bool = True) -> dict[str, int]:
    """Ponto de entrada: gera todas as entidades, grava CSV/JSON (+ seed.sql) e retorna contagens."""
    if not isinstance(spec, dict):
        spec = load_spec(spec)
    gen = MockGenerator(spec)
    gen.run()
    counts = write_outputs(gen, out_dir, seed_sql)
    if verbose:
        for name, n in counts.items():
            print(f"[ok] {name:<32} {n:>6} linhas -> {out_dir}/{name}.csv + .json")
        for w in gen.warnings:
            print(f"[aviso] {w}")
        if seed_sql:
            print(f"[ok] seed.sql -> {seed_sql}")
    return counts


def validate_outputs(spec: dict[str, Any], out_dir: str | Path = "mock_data") -> list[str]:
    """Checa no disco: 2 arquivos por entidade, volume ≥ spec, FKs válidas. Retorna lista de problemas (vazia = ok)."""
    out = Path(out_dir); problems: list[str] = []
    tables: dict[str, pd.DataFrame] = {}
    for ent in spec["entities"]:
        csv, js = out / f"{ent['name']}.csv", out / f"{ent['name']}.json"
        if not csv.exists() or not js.exists():
            problems.append(f"{ent['name']}: faltam arquivos ({'csv ' if not csv.exists() else ''}{'json' if not js.exists() else ''})"); continue
        df = pd.read_csv(csv); tables[ent["name"]] = df
        if len(df) < int(ent.get("volume", 0)):
            problems.append(f"{ent['name']}: {len(df)} linhas < volume {ent.get('volume')}")
    for ent in spec["entities"]:
        df = tables.get(ent["name"])
        if df is None:
            continue
        for f in ent.get("fields", []):
            kind, args = _parse_gen(f.get("gen"))[0]
            if kind == "fk":
                parent = _split_args(args)[0].strip()
                if parent in tables and f["name"] in df.columns:
                    bad = ~df[f["name"]].dropna().isin(tables[parent]["id"])
                    if bad.any():
                        problems.append(f"{ent['name']}.{f['name']}: {int(bad.sum())} FKs inválidas para {parent}")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera mock data volumétrico a partir de docs/mock_spec.yaml")
    ap.add_argument("spec")
    ap.add_argument("--out", default="mock_data")
    ap.add_argument("--seed-sql", default=None)
    ap.add_argument("--validate", action="store_true", help="apenas valida os arquivos existentes")
    a = ap.parse_args()
    spec = load_spec(a.spec)
    if a.validate:
        probs = validate_outputs(spec, a.out)
        print("\n".join(probs) if probs else "[ok] mock_data valido")
        sys.exit(1 if probs else 0)
    generate(spec, a.out, a.seed_sql)


if __name__ == "__main__":
    main()
