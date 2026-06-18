# Skill 10 — Plotly Generation Skill

Leia `docs/screens_definition.yaml` e gere componentes de gráficos para uma página.

## Argumento obrigatório

Nome da página e tipo de gráfico: $ARGUMENTS

Exemplo de uso: `/skill10-plotly aprovacao bar`

## Instruções

1. Leia `docs/screens_definition.yaml` — extraia os componentes do tipo `chart` e `kpi` da página.
2. Leia `docs/data_model.yaml` — entenda os campos disponíveis.
3. Gere ou atualize `frontend/pages/<pagina>/<pagina>_components.py` com as funções de gráfico.
4. Se o arquivo já existir, aplique patch incremental apenas nas funções de chart.

## Tipos Permitidos e Código Correspondente

### KPI

```python
import plotly.graph_objects as go
from dash import dcc
import dash_bootstrap_components as dbc

def build_kpi(title: str, value: str | int | float, delta: float | None = None) -> dbc.Card:
    fig = go.Figure(go.Indicator(
        mode="number+delta" if delta else "number",
        value=float(value),
        delta={"reference": float(value) - float(delta)} if delta else None,
        title={"text": title, "font": {"size": 14}},
        number={"font": {"size": 32}},
    ))
    fig.update_layout(height=120, margin=dict(l=10, r=10, t=30, b=10))
    return dbc.Card(dcc.Graph(figure=fig, config={"displayModeBar": False}))
```

### Barra

```python
import plotly.express as px

def build_bar_chart(df: pd.DataFrame, x: str, y: str, title: str) -> dcc.Graph:
    fig = px.bar(df, x=x, y=y, title=title, template="plotly_white")
    fig.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
    return dcc.Graph(id="<pagina>-chart-bar", figure=fig)
```

### Linha

```python
def build_line_chart(df: pd.DataFrame, x: str, y: str, title: str) -> dcc.Graph:
    fig = px.line(df, x=x, y=y, title=title, markers=True, template="plotly_white")
    fig.update_layout(height=350)
    return dcc.Graph(id="<pagina>-chart-line", figure=fig)
```

### Pizza

```python
def build_pie_chart(df: pd.DataFrame, names: str, values: str, title: str) -> dcc.Graph:
    fig = px.pie(df, names=names, values=values, title=title, template="plotly_white")
    fig.update_layout(height=350)
    return dcc.Graph(id="<pagina>-chart-pie", figure=fig)
```

### Scatter

```python
def build_scatter(df: pd.DataFrame, x: str, y: str, color: str | None, title: str) -> dcc.Graph:
    fig = px.scatter(df, x=x, y=y, color=color, title=title, template="plotly_white")
    fig.update_layout(height=350)
    return dcc.Graph(id="<pagina>-chart-scatter", figure=fig)
```

### Heatmap

```python
def build_heatmap(df: pd.DataFrame, x: str, y: str, values: str, title: str) -> dcc.Graph:
    pivot = df.pivot(index=y, columns=x, values=values)
    fig = go.Figure(go.Heatmap(z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist()))
    fig.update_layout(title=title, height=400, template="plotly_white")
    return dcc.Graph(id="<pagina>-chart-heatmap", figure=fig)
```

## Regras

- Sempre usar `template="plotly_white"`.
- Gráficos vazios (sem dados) devem retornar figura com mensagem `"Sem dados"`.
- Gráficos atualizados via callback em `_callbacks.py` — aqui apenas as funções construtoras.
- IDs seguem o padrão `<pagina>-chart-<tipo>`.
- Tipagem Python obrigatória.

## Restrições

- Usar APENAS `plotly.express` e `plotly.graph_objects`.
- Contexto máximo: **8.000 tokens** de saída (anteriormente 2.000).
- **Consultar `design-system.yaml`** para configurações de charts (template, colors, margins, etc.).

## Pós-processamento

1. Verificar que configurações seguem `design-system.yaml`
2. Verificar que gráficos usam `template="plotly_white"`
