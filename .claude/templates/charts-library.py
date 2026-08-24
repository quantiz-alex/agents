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

# Layout base para todos os gráficos
_LAYOUT = dict(
    colorway=CHART_COLORWAY,
    font=dict(family=FONT_UI, size=12, color=TEXT_COLOR),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    template="plotly_white",
)


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
# HELPERS DE CONFIGURAÇÃO
# ============================================================================


def set_primary_color(color: str) -> None:
    """
    Define a cor primária do projeto para usar nos gráficos.
    Chame esta função no início do app com a cor do branding.
    
    Args:
        color: Cor hexadecimal (ex: "#1045C8")
    """
    global CHART_COLORWAY
    CHART_COLORWAY[0] = color


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
