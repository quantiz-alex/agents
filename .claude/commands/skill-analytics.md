# Skill Analytics — Agregações para Telas Analytics/Dashboard (v4)

Define como o `<pagina>_queries.py` calcula KPIs, séries temporais, rankings e distribuições a partir dos dados mock/API. É o espelho frontend do `backend/services/analytics_<pagina>.py` (ver `skill11-fastapi.md` Step 9) — mesmos nomes de função, mesmas fórmulas de `business_logic.yaml`, para que a flag `USE_API` em `api_client.py` funcione sem mudar a tela.

> Em v3 cada página recriava a lógica de agregação do zero, levando a KPIs inconsistentes entre o mock e a API. Agora esta skill é a fonte canônica — o backend espelha exatamente as mesmas funções.

## Quando aplicar

Para toda página em `docs/screens_definition.yaml` com `screen_type ∈ {dashboard, analytics, report, master_detail}` ou com `kpis[]`/`charts[]` não vazios.

## Estrutura de `<pagina>_queries.py`

```python
"""<pagina>_queries.py — agregações da tela <Título>.

Paridade com backend/services/analytics_<pagina>.py (mesmos nomes, mesmas fórmulas).
USE_API em api_client.py troca a fonte sem mudar a tela.
"""
import pandas as pd
from frontend.api_client import api_get, USE_API

_PAGE = "<pagina>"  # prefixo dos endpoints: /analytics/<pagina>/...


def _load_df(filters: dict | None = None) -> pd.DataFrame:
    """Carrega a entidade principal da tela, aplicando filtros."""
    if USE_API:
        return pd.DataFrame(api_get(f"/{_PAGE}/grid", params=filters or {}))
    # mock: lê CSV e aplica filtros em pandas
    df = pd.read_csv("mock_data/<entidade>.csv", parse_dates=["data"])
    if filters:
        for k, v in filters.items():
            if v and v != "all" and k in df.columns:
                df = df[df[k] == v]
    return df


def carregar_kpis(filters: dict | None = None) -> dict:
    """Retorna dict {kpi_id: {value, format, compare_to, delta_pct}}.
    Alinhado com screens_definition.yaml → pages.<pagina>.kpis[]."""
    ...


def carregar_chart(chart_id: str, filters: dict | None = None) -> pd.DataFrame:
    """Retorna DataFrame agregado para o gráfico <chart_id>.
    Alinhado com screens_definition.yaml → pages.<pagina>.charts[]."""
    ...


def carregar_grid(filters: dict | None = None) -> pd.DataFrame:
    """Retorna DataFrame para o AG Grid (com campos derivados calculados)."""
    ...
```

## Padrões de agregação por tipo de KPI

| `kpis[].kind` | `format` | Cálculo |
|---|---|---|
| `simples` + `currency` | `R$ 1.234,56` | `df[col].sum()` |
| `simples` + `percent` | `12,3%` | `df[col].mean()` ou `df[flag].mean() * 100` |
| `simples` + `number` | `1.234` | `df[col].sum()` ou `len(df)` |
| `comparação` + `currency` | `R$ 1.234,56 (▲ 5,2%)` | atual = `df[col].sum()`; anterior = `df[df.data < hoje-30d][col].sum()`; delta_pct = `(atual-anterior)/anterior*100` |
| `comparação` + `percent` | `12,3% (▼ 1,2pp)` | atual = `mean()`; anterior = `mean(janela anterior)`; delta em p.p. |

**Regras:**
- `better: up` → delta positivo é verde (▲); `better: down` → delta negativo é verde (▼); `neutral` → cinza.
- `compare_to` define a janela: `"mês anterior"` → 30d; `"ano anterior"` → 365d; `"simulado"` → vem do `calcular_simulacao()`.
- Formatação pt-BR via `format_brl()` / `format_pct()` / `format_int()` de `components-library.py`.

## Padrões de agregação por tipo de chart

| `charts[].type` | Agregação | Exemplo |
|---|---|---|
| `bar` (ranking) | `df.groupby(x_field)[y_field].sum().sort_values(ascending=False).head(N)` | Top 10 produtos por receita |
| `bar` (evolução) | `df.groupby(df.data.dt.to_period("M"))[y_field].sum()` | Receita mensal (24 meses) |
| `line` (evolução) | `df.groupby(df.data.dt.to_period("M"))[y_field].mean()` | Ticket médio mensal |
| `line` (comparação) | pivot por `series_field` + groupby período | Receita por região ao longo do tempo |
| `pie` / `donut` | `df.groupby(x_field)[y_field].sum()` | Distribuição por categoria |
| `heatmap` | `df.pivot_table(index=x, columns=y, values=z, aggfunc="sum")` | Receita por região × mês |
| `treemap` | `df.groupby([x_field, y_field])[value].sum()` | Receita por categoria → subcategoria |
| `combo` | bar = `groupby(x).sum()`, line = `groupby(x).mean()` no mesmo eixo x | Volume (bar) + margem % (line) |
| `funnel` | `df.groupby(x_field)[y_field].sum()` em ordem de estágio | Funil de vendas por estágio |
| `gauge` | `df[col].mean() / meta * 100` | % da meta atingida |
| `sparkline` | `df.groupby(period)[y].sum()` (sem eixo, inline em KPI) | Mini-evolução no card de KPI |

**Regras:**
- Período padrão = `demo.period_months` (de `.build/project.json`). Sempre agrupar por mês (ou dia se `period_months ≤ 3`).
- `series_field` presente → pivot/stack para multi-série.
- Drill-down: `carregar_chart(chart_id, filters={**filters, target_field: value})` → re-agrega filtrando pelo campo de drill.

## Campos derivados (de `business_logic.yaml`)

Para cada regra `logic_type: derived_field` com `persist: false` vinculada a um campo exibido na tela:

```python
# em _load_df(), após carregar o DataFrame:
df["margem_percent"] = (df["receita"] - df["custo"]) / df["receita"] * 100
df["margem_reais"] = df["receita"] - df["custo"]
```

Usar a **mesma fórmula** de `business_logic.yaml → rules[].formula` — não reinventar. Se a fórmula referencia variáveis de `variables[]`, usar os valores default (para mock) ou os parâmetros interativos (para simulation).

## Filtros

`carregar_kpis(filters)`, `carregar_chart(chart_id, filters)`, `carregar_grid(filters)` aceitam o mesmo dict de filtros:

```python
filters = {
    "familia": "Baterias",        # select
    "data_inicio": "2025-01-01",  # date_range
    "data_fim": "2025-12-31",
    "busca": "filtro",            # text (busca livre)
}
```

Filtros vêm dos IDs `<pagina>-filtro-<field>` (Pattern 1 de `skill08-dash-callback.md`). Valores `"all"` ou `None` → ignorar (não filtrar).

## Performance

- Vetorizado em pandas — nunca `iterrows()`.
- Cache opcional via `api_client.py` (TTL 60s para agregações).
- Meta: `< 300ms` para ≤ 5.000 linhas (mock) ou ≤ 50.000 linhas (API com índice).

## Paridade com backend

Cada função aqui tem uma correspondente em `backend/services/analytics_<pagina>.py` com o **mesmo nome** e **mesmo retorno** (dict para KPIs, DataFrame/records para charts/grid). O `api_client.py` com `USE_API=true` chama `GET /analytics/<pagina>/kpis|charts/<id>|grid` e o frontend faz `pd.DataFrame(api_get(...))` — a tela não muda.

**Checklist de paridade** (validar ao final):
- [ ] `carregar_kpis` retorna mesmo dict shape (keys = `kpis[].id`)
- [ ] `carregar_chart` retorna mesmo DataFrame shape (colunas = `x_field`, `y_field`, `series_field`)
- [ ] `carregar_grid` retorna mesmas colunas (incluindo derivados)
- [ ] Filtros aceitos são os mesmos (`screens_definition.yaml → pages.<pagina>.filters[]`)

## Saída

```
frontend/pages/<pagina>/<pagina>_queries.py
```

## Restrições

- NÃO persistir dados — apenas calcular em memória.
- NÃO ler CSV diretamente fora de `_load_df()` — toda função recebe `df` ou chama `_load_df()`.
- NÃO usar `iterrows()` — vetorizar com pandas.
- Se uma fórmula de `business_logic.yaml` não puder ser calculada (campo ausente no mock), registrar aviso e retornar `0`/`None` — não quebrar a tela.
