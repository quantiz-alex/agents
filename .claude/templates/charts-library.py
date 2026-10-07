"""
charts-library.py — Helpers de gráfico no padrão PMZ (Plotly).
Copie este arquivo para frontend/components/charts.py em novos projetos.
Legenda fora das fatias, paleta categórica fixa, margens enxutas.
Requer: plotly
"""
import plotly.graph_objects as go
import plotly.express as px


# ============================================================================
# CONFIGURAÇÃO BASE
# ============================================================================

# Paleta categórica (será sobrescrita com primary do projeto)
CHART_COLORWAY = ["#1045C8", "#10b981", "#f59e0b", "#ef4444", "#06b6d4"]

# Cores semânticas para variações
COLOR_POSITIVE = "#166534"  # verde
COLOR_NEGATIVE = "#991b1b"  # vermelho
COLOR_NEUTRAL = "#64748b"   # cinza

FONT_UI = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
TEXT_COLOR = "#374151"

# Layout base para todos os gráficos (pt-BR: vírgula decimal e ponto de milhar via `separators`)
_LAYOUT = dict(
    colorway=CHART_COLORWAY,
    font=dict(family=FONT_UI, size=12, color=TEXT_COLOR),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    template="plotly_white",
    separators=",.",
    hoverlabel=dict(bgcolor="#1e293b", font=dict(family=FONT_UI, size=12, color="#ffffff"), bordercolor="#1e293b"),
    title_font=dict(size=13, color="#1e293b"),
    title_x=0,
    title_xanchor="left",
)

GRID_COLOR = "#eef2f7"

# Hovertemplates prontos (usar com customdata quando necessário)
HOVER_CURRENCY = "%{x}<br>R$ %{y:,.2f}<extra></extra>"
HOVER_CURRENCY_H = "%{y}<br>R$ %{x:,.2f}<extra></extra>"
HOVER_NUMBER = "%{x}<br>%{y:,.0f}<extra></extra>"
HOVER_PERCENT = "%{x}<br>%{y:.1f}%<extra></extra>"


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}, {alpha})"


# ============================================================================
# GRÁFICOS DE BARRAS
# ============================================================================


def bar_ranking(
    labels: list[str],
    values: list[float],
    value_fmt=None,
    title: str = "",
    height: int = 300,
) -> go.Figure:
    """
    Barras horizontais para ranking (ex.: Top fornecedores).
    Maior valor no topo.
    
    Args:
        labels: Rótulos das categorias
        values: Valores numéricos
        value_fmt: Função de formatação (default: lambda v: f"{v:,.0f}")
        title: Título do gráfico
        height: Altura em pixels
    """
    if value_fmt is None:
        value_fmt = lambda v: f"{v:,.0f}".replace(",", ".")

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=CHART_COLORWAY[0], line=dict(width=0)),
            text=[value_fmt(v) for v in values],
            textposition="outside",
        )
    )

    fig.update_layout(**_LAYOUT, title=title, height=height)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7", zeroline=False)

    return fig


def bar_vertical(
    labels: list[str],
    values: list[float],
    title: str = "",
    height: int = 300,
) -> go.Figure:
    """
    Barras verticais para comparação entre categorias.
    
    Args:
        labels: Rótulos das categorias
        values: Valores numéricos
        title: Título do gráfico
        height: Altura em pixels
    """
    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(color=CHART_COLORWAY[0], line=dict(width=0)),
            text=[f"{v:,.0f}".replace(",", ".") for v in values],
            textposition="outside",
        )
    )

    fig.update_layout(**_LAYOUT, title=title, height=height)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7", zeroline=False)

    return fig


def variation_bars(
    labels: list[str],
    pcts: list[float],
    title: str = "",
    height: int = 300,
) -> go.Figure:
    """
    Barras +/- a partir do zero: verde positivo, vermelho negativo.
    Ideal para mostrar variações percentuais.
    
    Args:
        labels: Rótulos das categorias
        pcts: Percentuais de variação (ex: 3.7 para +3.7%)
        title: Título do gráfico
        height: Altura em pixels
    """
    colors = [COLOR_POSITIVE if p >= 0 else COLOR_NEGATIVE for p in pcts]

    fig = go.Figure(
        go.Bar(
            x=pcts,
            y=labels,
            orientation="h",
            marker=dict(color=colors),
            text=[f"{p:+.1f}%".replace(".", ",") for p in pcts],
            textposition="outside",
        )
    )

    fig.update_layout(**_LAYOUT, title=title, height=height)
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#eef2f7",
        zeroline=True,
        zerolinecolor="#cbd5e1",
        zerolinewidth=2,
    )

    return fig


# ============================================================================
# GRÁFICOS DE PIZZA/DONUT
# ============================================================================


def donut(
    labels: list[str],
    values: list[float],
    title: str = "",
    height: int = 300,
    hole: float = 0.62,
) -> go.Figure:
    """
    Rosca (donut) com legenda externa; sem rótulo sobre as fatias.
    Use apenas para ≤5 categorias.
    
    Args:
        labels: Rótulos das categorias
        values: Valores numéricos
        title: Título do gráfico
        height: Altura em pixels
        hole: Tamanho do buraco central (0-1)
    """
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=hole,
            textinfo="none",
            sort=False,
            marker=dict(colors=CHART_COLORWAY),
        )
    )

    fig.update_layout(**_LAYOUT, title=title, height=height)

    return fig


def pie(
    labels: list[str],
    values: list[float],
    title: str = "",
    height: int = 300,
) -> go.Figure:
    """
    Pizza simples com legenda externa.
    Use apenas para ≤5 categorias.
    
    Args:
        labels: Rótulos das categorias
        values: Valores numéricos
        title: Título do gráfico
        height: Altura em pixels
    """
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            textinfo="percent",
            sort=False,
            marker=dict(colors=CHART_COLORWAY),
        )
    )

    fig.update_layout(**_LAYOUT, title=title, height=height)

    return fig


# ============================================================================
# GRÁFICOS DE LINHA
# ============================================================================


def line_chart(
    x: list,
    y: list,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    height: int = 300,
) -> go.Figure:
    """
    Gráfico de linha para tendências no tempo.
    
    Args:
        x: Valores do eixo X (geralmente datas)
        y: Valores do eixo Y
        title: Título do gráfico
        x_label: Rótulo do eixo X
        y_label: Rótulo do eixo Y
        height: Altura em pixels
    """
    fig = go.Figure(
        go.Scatter(
            x=x,
            y=y,
            mode="lines+markers",
            line=dict(color=CHART_COLORWAY[0], width=2),
            marker=dict(size=6),
        )
    )

    fig.update_layout(
        **_LAYOUT,
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=height,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7")
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7")

    return fig


def multi_line_chart(
    x: list,
    series: dict[str, list],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    height: int = 300,
) -> go.Figure:
    """
    Gráfico de múltiplas linhas para comparação de séries.
    
    Args:
        x: Valores do eixo X (geralmente datas)
        series: Dicionário {nome_série: valores_y}
        title: Título do gráfico
        x_label: Rótulo do eixo X
        y_label: Rótulo do eixo Y
        height: Altura em pixels
    """
    fig = go.Figure()

    for i, (name, y_values) in enumerate(series.items()):
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y_values,
                mode="lines+markers",
                name=name,
                line=dict(color=CHART_COLORWAY[i % len(CHART_COLORWAY)], width=2),
                marker=dict(size=6),
            )
        )

    fig.update_layout(
        **_LAYOUT,
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=height,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7")
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7")

    return fig


# ============================================================================
# GRÁFICOS DE ÁREA
# ============================================================================


def area_chart(
    x: list,
    y: list,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    height: int = 300,
) -> go.Figure:
    """
    Gráfico de área para tendências com volume.
    
    Args:
        x: Valores do eixo X (geralmente datas)
        y: Valores do eixo Y
        title: Título do gráfico
        x_label: Rótulo do eixo X
        y_label: Rótulo do eixo Y
        height: Altura em pixels
    """
    fig = go.Figure(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            fill="tozeroy",
            line=dict(color=CHART_COLORWAY[0], width=2),
            fillcolor=f"rgba({int(CHART_COLORWAY[0][1:3], 16)}, {int(CHART_COLORWAY[0][3:5], 16)}, {int(CHART_COLORWAY[0][5:7], 16)}, 0.2)",
        )
    )

    fig.update_layout(
        **_LAYOUT,
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=height,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7")
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7")

    return fig


# ============================================================================
# OUTROS GRÁFICOS
# ============================================================================


def scatter_chart(
    x: list,
    y: list,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    height: int = 300,
) -> go.Figure:
    """
    Gráfico de dispersão para relação entre duas variáveis.
    
    Args:
        x: Valores do eixo X
        y: Valores do eixo Y
        title: Título do gráfico
        x_label: Rótulo do eixo X
        y_label: Rótulo do eixo Y
        height: Altura em pixels
    """
    fig = go.Figure(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=dict(color=CHART_COLORWAY[0], size=8),
        )
    )

    fig.update_layout(
        **_LAYOUT,
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=height,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7")
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7")

    return fig


def histogram(
    values: list[float],
    title: str = "",
    x_label: str = "",
    y_label: str = "Frequência",
    height: int = 300,
    nbins: int = 20,
) -> go.Figure:
    """
    Histograma para distribuição de valores.
    
    Args:
        values: Valores para distribuição
        title: Título do gráfico
        x_label: Rótulo do eixo X
        y_label: Rótulo do eixo Y
        height: Altura em pixels
        nbins: Número de bins
    """
    fig = go.Figure(
        go.Histogram(
            x=values,
            nbinsx=nbins,
            marker=dict(color=CHART_COLORWAY[0], line=dict(color="#ffffff", width=1)),
        )
    )

    fig.update_layout(
        **_LAYOUT,
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=height,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7")
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7")

    return fig


def waterfall_chart(
    labels: list[str],
    values: list[float],
    measure: list[str] | None = None,
    value_fmt=None,
    title: str = "",
    height: int = 320,
) -> go.Figure:
    """
    Gráfico de ponte (waterfall) — mostra a composição de uma variação em etapas
    (ex.: Preço Atual -> +Δmarkup -> +Δelasticidade -> Preço/Receita Simulada).
    Use para telas de simulação/interactive_formula (business_logic.yaml) quando
    ui.chart_hint == "waterfall".

    Args:
        labels: Rótulo de cada barra/etapa (primeiro e último geralmente são totais)
        values: Valor de cada etapa (positivo = alta, negativo = queda; totais = valor absoluto)
        measure: "absolute"|"relative"|"total" por etapa (default: absolute no 1º e último, relative no meio)
        value_fmt: Função de formatação (default: R$ com separador brasileiro)
        title: Título do gráfico
        height: Altura em pixels
    """
    if value_fmt is None:
        value_fmt = lambda v: f"R$ {v:,.0f}".replace(",", ".")
    if measure is None:
        measure = ["absolute"] + ["relative"] * (len(labels) - 2) + ["total"]

    fig = go.Figure(
        go.Waterfall(
            x=labels,
            y=values,
            measure=measure,
            text=[value_fmt(v) for v in values],
            textposition="outside",
            connector=dict(line=dict(color="#cbd5e1", width=1)),
            increasing=dict(marker=dict(color=COLOR_POSITIVE)),
            decreasing=dict(marker=dict(color=COLOR_NEGATIVE)),
            totals=dict(marker=dict(color=CHART_COLORWAY[0])),
        )
    )

    fig.update_layout(**_LAYOUT, title=title, height=height, showlegend=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7", zeroline=False)

    return fig


def elasticity_curve(
    preco_range: list[float],
    volume_estimado: list[float],
    preco_atual: float | None = None,
    preco_simulado: float | None = None,
    title: str = "",
    x_label: str = "Preço",
    y_label: str = "Volume/Receita estimado",
    height: int = 320,
) -> go.Figure:
    """
    Curva de sensibilidade preço x volume/receita (elasticidade de demanda) —
    para telas de simulação com ui.chart_hint == "elasticity_curve" em business_logic.yaml.
    Marca verticalmente o preço atual e/ou o preço simulado sobre a curva.

    Args:
        preco_range: Sequência de preços testados (eixo X)
        volume_estimado: Volume/receita projetado para cada preço (eixo Y)
        preco_atual: Preço vigente — desenha linha vertical de referência
        preco_simulado: Preço do cenário simulado — desenha linha vertical destacada
        title: Título do gráfico
        x_label: Rótulo do eixo X
        y_label: Rótulo do eixo Y
        height: Altura em pixels
    """
    fig = go.Figure(
        go.Scatter(
            x=preco_range,
            y=volume_estimado,
            mode="lines",
            line=dict(color=CHART_COLORWAY[0], width=2),
        )
    )

    if preco_atual is not None:
        fig.add_vline(x=preco_atual, line=dict(color=COLOR_NEUTRAL, width=1, dash="dot"),
                       annotation_text="Atual", annotation_position="top")
    if preco_simulado is not None:
        fig.add_vline(x=preco_simulado, line=dict(color=CHART_COLORWAY[1], width=2, dash="dash"),
                       annotation_text="Simulado", annotation_position="top")

    fig.update_layout(
        **_LAYOUT, title=title, xaxis_title=x_label, yaxis_title=y_label, height=height,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7")
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7")

    return fig


def scenario_comparison_chart(
    cenarios: list[dict],
    metric_field: str,
    label_field: str = "nome",
    value_fmt=None,
    title: str = "",
    height: int = 320,
) -> go.Figure:
    """
    Barras agrupadas comparando N cenários salvos lado a lado (ui.chart_hint ==
    "scenario_comparison" em business_logic.yaml) — ex.: comparar receita simulada
    de vários cenários de precificação salvos pelo analista.

    Args:
        cenarios: Lista de dicts, um por cenário salvo (ex.: listar_cenarios_salvos())
        metric_field: Chave numérica de cada dict a comparar (ex.: "receita_simulada")
        label_field: Chave usada como rótulo de cada barra (default: "nome")
        value_fmt: Função de formatação (default: número com separador brasileiro)
        title: Título do gráfico
        height: Altura em pixels
    """
    if value_fmt is None:
        value_fmt = lambda v: f"{v:,.0f}".replace(",", ".")

    labels = [c.get(label_field, "") for c in cenarios]
    values = [c.get(metric_field, 0) for c in cenarios]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(color=CHART_COLORWAY[: len(labels)] or CHART_COLORWAY[0]),
            text=[value_fmt(v) for v in values],
            textposition="outside",
        )
    )

    fig.update_layout(**_LAYOUT, title=title, height=height, showlegend=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7", zeroline=False)

    return fig


# ============================================================================
# GRÁFICOS ANALÍTICOS (v4) — heatmap, treemap, combo, funil, gauge, sparkline
# ============================================================================


def heatmap(
    x_labels: list[str],
    y_labels: list[str],
    values: list[list[float]],
    title: str = "",
    value_fmt: str = ",.0f",
    height: int = 340,
    colorscale: list | None = None,
) -> go.Figure:
    """
    Matriz de calor para 2 dimensões × 1 métrica (ex.: receita por família × canal).
    values[i][j] corresponde a y_labels[i] × x_labels[j]. Clique na célula → drill-down (skill08 Padrão 8:
    clickData['points'][0]['x'] e ['y'] identificam a célula).
    """
    if colorscale is None:
        colorscale = [[0, "#f8fafc"], [0.5, _rgba(CHART_COLORWAY[0], 0.55)], [1, CHART_COLORWAY[0]]]
    fig = go.Figure(
        go.Heatmap(
            x=x_labels,
            y=y_labels,
            z=values,
            colorscale=colorscale,
            text=[[f"{v:{value_fmt}}".replace(",", "X").replace(".", ",").replace("X", ".") if v is not None else "" for v in row] for row in values],
            texttemplate="%{text}",
            textfont=dict(size=11),
            hovertemplate="%{y} × %{x}<br><b>%{text}</b><extra></extra>",
            xgap=3,
            ygap=3,
            showscale=False,
        )
    )
    fig.update_layout(**{**_LAYOUT, "margin": dict(l=20, r=20, t=40, b=20)}, title=title, height=height)
    fig.update_xaxes(showgrid=False, side="top")
    fig.update_yaxes(showgrid=False, autorange="reversed")
    return fig


def treemap(
    labels: list[str],
    parents: list[str],
    values: list[float],
    title: str = "",
    height: int = 340,
    value_prefix: str = "R$ ",
) -> go.Figure:
    """
    Treemap para participação hierárquica (ex.: família > fornecedor por receita).
    Raízes têm parents="" . Clique → drill-down por clickData['points'][0]['label'].
    """
    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=CHART_COLORWAY * (len(labels) // len(CHART_COLORWAY) + 1), line=dict(width=2, color="#ffffff")),
            textinfo="label+percent parent",
            texttemplate="<b>%{label}</b><br>%{percentParent:.1%}",
            hovertemplate="%{label}<br>" + value_prefix + "%{value:,.0f}<br>%{percentRoot:.1%} do total<extra></extra>",
            pathbar=dict(visible=True, thickness=22),
            tiling=dict(pad=2),
        )
    )
    fig.update_layout(**{**_LAYOUT, "margin": dict(l=8, r=8, t=40, b=8)}, title=title, height=height)
    return fig


def combo_bar_line(
    x: list,
    bars: list[float],
    line: list[float],
    bar_name: str = "Volume",
    line_name: str = "Receita",
    title: str = "",
    height: int = 320,
    bar_fmt: str = ",.0f",
    line_fmt: str = ",.0f",
    line_prefix: str = "R$ ",
) -> go.Figure:
    """
    Barras (eixo esquerdo) + linha (eixo direito) — ex.: volume × receita por mês.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=x, y=bars, name=bar_name,
            marker=dict(color=_rgba(CHART_COLORWAY[0], 0.35), line=dict(width=0)),
            hovertemplate="%{x}<br>" + bar_name + ": %{y:" + bar_fmt + "}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x, y=line, name=line_name, mode="lines+markers", yaxis="y2",
            line=dict(color=CHART_COLORWAY[0], width=2.5), marker=dict(size=6),
            hovertemplate="%{x}<br>" + line_name + ": " + line_prefix + "%{y:" + line_fmt + "}<extra></extra>",
        )
    )
    fig.update_layout(
        **_LAYOUT, title=title, height=height, barmode="overlay",
        yaxis=dict(title=bar_name, showgrid=True, gridcolor=GRID_COLOR, zeroline=False),
        yaxis2=dict(title=line_name, overlaying="y", side="right", showgrid=False, zeroline=False),
    )
    fig.update_xaxes(showgrid=False)
    return fig


def stacked_bars(
    x: list,
    series: dict[str, list[float]],
    title: str = "",
    height: int = 320,
    horizontal: bool = False,
    percent: bool = False,
) -> go.Figure:
    """Barras empilhadas por série (ex.: receita por mês × canal). percent=True normaliza para 100%."""
    fig = go.Figure()
    for i, (name, vals) in enumerate(series.items()):
        kw = dict(y=x, x=vals, orientation="h") if horizontal else dict(x=x, y=vals)
        fig.add_trace(go.Bar(name=name, marker=dict(color=CHART_COLORWAY[i % len(CHART_COLORWAY)], line=dict(width=0)), **kw))
    fig.update_layout(**_LAYOUT, title=title, height=height, barmode="stack", barnorm="percent" if percent else None)
    if horizontal:
        fig.update_yaxes(showgrid=False, autorange="reversed")
        fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False)
    else:
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False)
    return fig


def grouped_bars(
    x: list,
    series: dict[str, list[float]],
    title: str = "",
    height: int = 320,
    value_fmt: str = ",.0f",
) -> go.Figure:
    """Barras agrupadas — comparação atual × simulado (ou período × período) por categoria."""
    fig = go.Figure()
    palette = ["#94a3b8", CHART_COLORWAY[0]] if len(series) == 2 else CHART_COLORWAY
    for i, (name, vals) in enumerate(series.items()):
        fig.add_trace(
            go.Bar(
                x=x, y=vals, name=name,
                marker=dict(color=palette[i % len(palette)], line=dict(width=0)),
                hovertemplate="%{x}<br>" + name + ": %{y:" + value_fmt + "}<extra></extra>",
            )
        )
    fig.update_layout(**_LAYOUT, title=title, height=height, barmode="group", bargroupgap=0.08)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False)
    return fig


def funnel(
    stages: list[str],
    values: list[float],
    title: str = "",
    height: int = 320,
) -> go.Figure:
    """Funil de etapas (ex.: cenários criados → enviados → aprovados → publicados)."""
    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker=dict(color=[_rgba(CHART_COLORWAY[0], 1 - i * 0.15) for i in range(len(stages))]),
            connector=dict(line=dict(color="#e2e8f0", width=1)),
        )
    )
    fig.update_layout(**_LAYOUT, title=title, height=height, showlegend=False)
    return fig


def gauge(
    value: float,
    target: float | None = None,
    min_value: float = 0,
    max_value: float = 100,
    title: str = "",
    suffix: str = "%",
    height: int = 220,
    better: str = "up",
) -> go.Figure:
    """
    Indicador tipo velocímetro — realizado × meta (ex.: margem % vs meta).
    Cor da barra: verde se atingiu a meta (conforme `better`), âmbar se perto (≥90%), vermelho caso contrário.
    """
    color = CHART_COLORWAY[0]
    if target is not None:
        ok = value >= target if better == "up" else value <= target
        near = (value >= target * 0.9) if better == "up" else (value <= target * 1.1)
        color = COLOR_POSITIVE if ok else ("#f59e0b" if near else COLOR_NEGATIVE)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number" + ("+delta" if target is not None else ""),
            value=value,
            number=dict(suffix=suffix, font=dict(size=28, family="'JetBrains Mono', Consolas, monospace")),
            delta=dict(reference=target, suffix=suffix, increasing=dict(color=COLOR_POSITIVE), decreasing=dict(color=COLOR_NEGATIVE)) if target is not None else None,
            gauge=dict(
                axis=dict(range=[min_value, max_value], tickwidth=1, tickcolor="#cbd5e1"),
                bar=dict(color=color, thickness=0.7),
                bgcolor="#f1f5f9",
                borderwidth=0,
                threshold=dict(line=dict(color="#1e293b", width=3), thickness=0.85, value=target) if target is not None else None,
            ),
        )
    )
    fig.update_layout(**{**_LAYOUT, "margin": dict(l=20, r=20, t=40, b=10)}, title=title, height=height)
    return fig


def sparkline(values: list[float], color: str | None = None, height: int = 36, fill: bool = True) -> go.Figure:
    """Mini-gráfico de tendência sem eixos (para kpi_simple e painel de detalhe)."""
    color = color or CHART_COLORWAY[0]
    fig = go.Figure(
        go.Scatter(
            y=values, mode="lines", line=dict(color=color, width=2),
            fill="tozeroy" if fill else None, fillcolor=_rgba(color, 0.15), hoverinfo="skip",
        )
    )
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=2, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, fixedrange=True), yaxis=dict(visible=False, fixedrange=True), showlegend=False,
    )
    return fig


def with_selection(fig: go.Figure, selected_label: str | None) -> go.Figure:
    """
    Destaca o item clicado (drill-down) em gráficos de barra: esmaece os demais.
    Chame no callback após filtrar; selected_label=None remove o destaque.
    """
    if selected_label is None:
        return fig
    for tr in fig.data:
        if tr.type == "bar":
            cats = list(tr.y if getattr(tr, "orientation", None) == "h" else tr.x)
            base = tr.marker.color if isinstance(tr.marker.color, str) else CHART_COLORWAY[0]
            tr.marker.color = [base if str(c) == str(selected_label) else _rgba(base if base.startswith("#") else CHART_COLORWAY[0], 0.25) for c in cats]
    return fig


# ============================================================================
# HELPERS DE CONFIGURAÇÃO
# ============================================================================


def diverging_bars(
    labels: list[str],
    values: list[float],
    value_fmt=None,
    title: str = "",
    height: int = 240,
) -> go.Figure:
    """
    Barras horizontais divergentes a partir do zero com cor semântica (verde > 0, vermelho < 0)
    e rótulo livre — ex.: drivers SHAP (feature × impacto). Ordem de entrada preservada (topo = 1º).
    """
    if value_fmt is None:
        value_fmt = lambda v: f"{v:+,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")
    colors = [COLOR_POSITIVE if v >= 0 else COLOR_NEGATIVE for v in values]
    fig = go.Figure(
        go.Bar(
            x=values, y=labels, orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=[value_fmt(v) for v in values], textposition="outside", cliponaxis=False,
            hovertemplate="%{y}<br>Impacto: %{x:+.3f}<extra></extra>",
        )
    )
    fig.update_layout(**{**_LAYOUT, "margin": dict(l=10, r=40, t=30 if title else 10, b=10)}, title=title, height=height, showlegend=False)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=True, zerolinecolor="#cbd5e1", zerolinewidth=2)
    return fig


def scatter_by_series(
    series: dict[str, tuple[list, list]],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    height: int = 320,
    x_suffix: str = "",
    y_prefix: str = "",
    colors: dict[str, str] | None = None,
) -> go.Figure:
    """Dispersão com uma cor por série (ex.: Expansão × Substituição). series = {nome: (x, y)}."""
    fig = go.Figure()
    for i, (name, (xs, ys)) in enumerate(series.items()):
        color = (colors or {}).get(name, CHART_COLORWAY[i % len(CHART_COLORWAY)])
        fig.add_trace(
            go.Scattergl(
                x=xs, y=ys, mode="markers", name=name,
                marker=dict(color=_rgba(color, 0.55), size=6, line=dict(width=0)),
                hovertemplate=name + "<br>%{x:.1f}" + x_suffix + " · " + y_prefix + "%{y:,.0f}<extra></extra>",
            )
        )
    fig.update_layout(**_LAYOUT, title=title, xaxis_title=x_label, yaxis_title=y_label, height=height)
    fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False)
    return fig



def set_primary_color(color: str, secondary: str | None = None) -> None:
    """
    Define a cor primária (e secundária opcional) do projeto para usar nos gráficos.
    Chame no início do app com a cor do branding (ou deixe o Step 0 substituir no arquivo).
    """
    CHART_COLORWAY[0] = color
    if secondary:
        CHART_COLORWAY[2] = secondary


def get_empty_state_message(chart_type: str = "gráfico") -> dict:
    """
    Retorna um dbc.Alert para estado vazio de gráfico.
    
    Args:
        chart_type: Tipo do gráfico (para mensagem personalizada)
    """
    import dash_bootstrap_components as dbc

    return dbc.Alert(
        f"Sem dados para exibir o {chart_type}. Ajuste os filtros.",
        color="info",
        className="text-center",
    )
