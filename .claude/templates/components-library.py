"""
components-library.py — Biblioteca de componentes reutilizáveis padrão PMZ.
Copie este arquivo para frontend/components/ui_components.py em novos projetos.
Toda página deve ser montada com app_shell(...) e usar kpi_card(...)/data_table(...).
Requer: dash>=2.14, dash-bootstrap-components, dash-ag-grid, pandas.

NOVO: Componentes de workflow disponíveis em workflow_components.py:
- workflow_breadcrumb() — Breadcrumb de progresso no fluxo
- workflow_context_actions() — Botões de próximos passos contextuais
- workflow_status_card() — Card com status do workflow ativo
"""
from typing import Any

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import html, dcc


# ============================================================================
# TOKENS — Fonte única de verdade
# ============================================================================

COLORS = {
    # Superfícies e bordas
    "app_bg": "#f8fafc",
    "surface": "#ffffff",
    "border": "#e2e8f0",
    "row_border": "#eef2f7",
    "thead_bg": "#f8fafc",
    "sidebar": "#ffffff",
    "sidebar_border": "#e2e8f0",
    # Texto
    "text_strong": "#1e293b",
    "text": "#374151",
    "text_muted": "#64748b",
    "text_faint": "#94a3b8",
    # Semântico (texto, fundo)
    "pos": ("#166534", "#dcfce7"),  # melhora / Aprovado / Ativo
    "neg": ("#991b1b", "#fee2e2"),  # piora / Rejeitado
    "warn": ("#92400e", "#fef3c7"),  # Pendente / revisar
    "info": ("#1e40af", "#dbeafe"),  # Simulado / tag neutra
}

# Paleta categórica para gráficos (ordem fixa) - será sobrescrita com primary do projeto
CHART_COLORWAY = ["#1045C8", "#10b981", "#f59e0b", "#ef4444", "#06b6d4"]

FONT_UI = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
FONT_NUM = "monospace"  # sempre com font-variant-numeric: tabular-nums

RADIUS = {"card": "0.375rem", "control": "0.375rem", "pill": "20px", "chip": "6px"}
SPACE = {"page_x": "1.5rem", "page_y": "1rem", "card": "1rem", "gap": "0.75rem"}


def status_badge_style(kind: str) -> dict[str, Any]:
    """kind: 'pos' | 'neg' | 'warn' | 'info' -> style de pill."""
    fg, bg = COLORS[kind]
    return {
        "display": "inline-block",
        "padding": "3px 11px",
        "borderRadius": RADIUS["pill"],
        "fontSize": "0.7rem",
        "fontWeight": 700,
        "color": fg,
        "backgroundColor": bg,
    }


# Mapa status textual -> tipo semântico (use em tabelas/callbacks)
STATUS_KIND = {
    "Aprovado": "pos",
    "Ativo": "pos",
    "Vigente": "pos",
    "Rejeitado": "neg",
    "Inativo": "neg",
    "Pendente": "warn",
    "Pendente Aprovação": "warn",
    "Simulado": "info",
}


# ============================================================================
# COMPONENTES BÁSICOS
# ============================================================================


def icon(icon_name: str, size: str = "1rem") -> html.I:
    """Ícone Bootstrap Icons."""
    return html.I(className=f"bi bi-{icon_name}", style={"fontSize": size})


def button(
    label: str, primary: bool = True, icon_key: str | None = None, **kwargs
) -> dbc.Button:
    """Botão padrão com ícone opcional."""
    children = []
    if icon_key:
        children.append(icon(icon_key, "0.875rem"))
        children.append(" ")
    children.append(label)

    color = "primary" if primary else "secondary"
    outline = not primary

    return dbc.Button(
        children, color=color, outline=outline, className="fw-bold", **kwargs
    )


# ============================================================================
# CABEÇALHO DE PÁGINA
# ============================================================================


def page_header(
    icon_key: str, title: str, subtitle: str, actions: list | None = None
) -> html.Div:
    """Cabeçalho padrão de página com ícone + título + subtítulo + ações."""
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            icon(icon_key, "1.5rem"),
                            html.H4(
                                title,
                                className="mb-0 fw-semibold",
                                style={"letterSpacing": "-0.02em"},
                            ),
                        ],
                        className="d-flex align-items-center gap-2",
                    ),
                    html.P(
                        subtitle,
                        className="text-muted mb-0 mt-2",
                        style={"fontSize": "0.875rem", "maxWidth": "640px"},
                    ),
                ]
            ),
            html.Div(
                actions or [], className="d-flex gap-2", style={"flexShrink": 0}
            ),
        ],
        className="d-flex align-items-start justify-content-between gap-3 mb-3",
    )


# ============================================================================
# KPI CARD
# ============================================================================


def _fmt_pct(v: float) -> str:
    """Formata percentual com sinal."""
    s = f"{v:+.1f}".replace(".", ",")
    return s + "%"


def kpi_card(
    label: str,
    atual: str,
    simulado: str,
    delta_pct: float,
    better: str = "up",
) -> dbc.Card:
    """
    KPI com comparação atual × simulado + delta colorido.
    
    Args:
        label: Rótulo do KPI
        atual: Valor atual (formatado como string)
        simulado: Valor simulado (formatado como string)
        delta_pct: Delta percentual (ex: 3.7 para +3.7%)
        better: 'up' (subir é bom), 'down' (subir é ruim), 'neutral'
    """
    if better == "neutral":
        kind = "warn"
    else:
        good = (delta_pct >= 0) if better == "up" else (delta_pct <= 0)
        kind = "pos" if good else "neg"

    fg, bg = COLORS[kind]
    arrow = "▲" if delta_pct > 0 else ("▼" if delta_pct < 0 else "•")

    border_color = "success" if kind == "pos" else ("danger" if kind == "neg" else "warning")

    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    label,
                    className="text-muted text-uppercase small fw-bold",
                    style={
                        "fontSize": "0.7rem",
                        "letterSpacing": "0.05em",
                        "lineHeight": 1.35,
                        "minHeight": "28px",
                    },
                ),
                html.Div(
                    simulado,
                    style={
                        "fontFamily": FONT_NUM,
                        "fontVariantNumeric": "tabular-nums",
                        "fontSize": "1.5rem",
                        "fontWeight": 700,
                        "color": COLORS["text_strong"],
                        "marginTop": "0.75rem",
                    },
                ),
                html.Div(
                    f"de {atual}",
                    style={
                        "fontFamily": FONT_NUM,
                        "fontSize": "0.7rem",
                        "color": COLORS["text_faint"],
                        "marginTop": "0.25rem",
                    },
                ),
                html.Div(
                    [html.Span(arrow), " ", _fmt_pct(delta_pct)],
                    style={
                        "display": "inline-flex",
                        "alignItems": "center",
                        "gap": "0.25rem",
                        "marginTop": "0.75rem",
                        "padding": "3px 9px",
                        "borderRadius": "7px",
                        "fontSize": "0.75rem",
                        "fontWeight": 700,
                        "fontFamily": FONT_NUM,
                        "color": fg,
                        "backgroundColor": bg,
                    },
                ),
            ]
        ),
        className=f"shadow-sm border-0 border-start border-4 border-{border_color} mb-3 h-100",
    )


def kpi_row(cards: list) -> dbc.Row:
    """Row de KPI cards com colunas iguais."""
    cols = [dbc.Col(card, md=12 // len(cards)) for card in cards]
    return dbc.Row(cols, className="mb-3")


def app_shell_with_workflow(
    active_key: str,
    icon_key: str,
    title: str,
    subtitle: str,
    content: list,
    actions: list | None = None,
    workflow_context: dict | None = None,
) -> html.Div:
    """
    App shell com suporte a workflow e navegação contextual.
    
    Args:
        active_key: chave da página ativa na sidebar
        icon_key: ícone Bootstrap Icons
        title: título da página
        subtitle: subtítulo/descrição
        content: lista de componentes do conteúdo
        actions: lista de botões de ação (opcional)
        workflow_context: dict com workflow_id, step_id, context_data (opcional)
    
    Se workflow_context for fornecido, adiciona:
    - Breadcrumb de progresso no workflow
    - Botões de próximos passos contextuais
    
    Exemplo de workflow_context:
    {
        "workflow_id": "pricing_simulation_flow",
        "step_id": "simulate_scenario",
        "context_data": {"arquitetura_id": 123, "regras_margem": {...}},
        "user_role": "analista"
    }
    """
    # Importar componentes de workflow se necessário
    workflow_breadcrumb_component = None
    workflow_actions = []
    
    if workflow_context:
        try:
            from frontend.components.workflow_components import (
                workflow_breadcrumb,
                workflow_context_actions,
            )
            
            workflow_breadcrumb_component = workflow_breadcrumb(
                workflow_context["workflow_id"],
                workflow_context["step_id"],
                workflow_context.get("context_data", {}),
            )
            
            workflow_actions = workflow_context_actions(
                workflow_context["workflow_id"],
                workflow_context["step_id"],
                workflow_context.get("context_data", {}),
                workflow_context.get("user_role"),
            )
        except ImportError:
            # workflow_components.py não disponível - ignorar
            pass
    
    # Combinar ações padrão com ações de workflow
    all_actions = (actions or []) + workflow_actions
    
    # Montar conteúdo com breadcrumb se disponível
    page_content = []
    if workflow_breadcrumb_component:
        page_content.append(workflow_breadcrumb_component)
    
    page_content.extend(content)
    
    # Usar app_shell padrão
    return app_shell(active_key, icon_key, title, subtitle, page_content, all_actions)


# ============================================================================
# CARD GENÉRICO
# ============================================================================


def card(title: str, body: Any, right: str | None = None) -> dbc.Card:
    """Card genérico com header e body."""
    header_content = [
        html.Span(title, className="fw-semibold", style={"fontSize": "0.875rem"}),
    ]
    if right:
        header_content.append(
            html.Span(right, className="text-muted small", style={"fontSize": "0.75rem"})
        )

    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    header_content,
                    className="d-flex align-items-center justify-content-between",
                ),
                className="bg-white border-bottom",
            ),
            dbc.CardBody(body),
        ],
        className="shadow-sm border-0 mb-3",
    )


# ============================================================================
# DATA TABLE (AG GRID)
# ============================================================================


def data_table(
    df: Any,  # pd.DataFrame
    id: str,
    numeric_cols: list[str] | None = None,
    status_col: str | None = None,
    page_size: int = 20,
) -> dag.AgGrid:
    """
    AG Grid já estilizada com badges automáticos e mono tabular.
    
    Args:
        df: DataFrame com os dados
        id: ID do componente
        numeric_cols: Lista de colunas numéricas (alinhamento direita + mono)
        status_col: Coluna de status para badges coloridos
        page_size: Itens por página
    """
    numeric_cols = numeric_cols or []

    # Column definitions
    column_defs = []
    for col in df.columns:
        col_def = {
            "field": col,
            "headerName": col,
            "sortable": True,
            "filter": True,
            "resizable": True,
        }

        # Colunas numéricas
        if col in numeric_cols:
            col_def["type"] = "numericColumn"
            col_def["cellStyle"] = {
                "fontFamily": FONT_NUM,
                "fontVariantNumeric": "tabular-nums",
            }

        # Coluna de status
        if col == status_col:
            col_def["cellStyle"] = {"textAlign": "center"}
            # Badges serão aplicados via cellClassRules ou cellRenderer customizado
            # Por simplicidade, deixamos o AG Grid renderizar o texto

        column_defs.append(col_def)

    return dag.AgGrid(
        id=id,
        rowData=df.to_dict("records"),
        columnDefs=column_defs,
        defaultColDef={
            "sortable": True,
            "filter": True,
            "resizable": True,
            "floatingFilter": True,
            "suppressMenu": True,
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": page_size,
            "paginationPageSizeSelector": [10, 20, 50, 100],
            "animateRows": True,
            "rowHeight": 44,
            "headerHeight": 44,
        },
        className="ag-theme-alpine",
        style={"height": "500px"},
    )


# ============================================================================
# APP SHELL
# ============================================================================


def app_shell(
    active_key: str,
    icon_key: str,
    title: str,
    subtitle: str,
    content: list,
    actions: list | None = None,
) -> html.Div:
    """
    Shell completo da aplicação (usado em conjunto com sidebar separada).
    
    Args:
        active_key: Chave da página ativa (para sidebar)
        icon_key: Ícone da página
        title: Título da página
        subtitle: Subtítulo da página
        content: Lista de componentes do conteúdo
        actions: Lista de botões de ação (opcional)
    """
    return html.Div(
        [
            page_header(icon_key, title, subtitle, actions),
            *content,
        ],
        className="page-wrapper px-4 py-3",
        style={"background": COLORS["app_bg"], "minHeight": "100vh"},
    )


# ============================================================================
# FILTROS
# ============================================================================


def filter_card(filters: list, button_id: str = "btn-filtrar") -> dbc.Card:
    """
    Card de filtros compacto com botão Filtrar.
    
    Args:
        filters: Lista de componentes de filtro (cada um em um dbc.Col)
        button_id: ID do botão de filtrar
    """
    # Adiciona botão Filtrar ao final
    filters_with_button = filters + [
        dbc.Col(
            button("Filtrar", primary=True, id=button_id, className="w-100"),
            md=1,
            className="d-grid",
        )
    ]

    return dbc.Card(
        dbc.CardBody(
            dbc.Row(filters_with_button, className="g-2 align-items-end"),
            className="py-2",
        ),
        className="shadow-sm border-0 mb-3",
    )


# ============================================================================
# HELPERS DE FORMATAÇÃO
# ============================================================================


def format_currency(value: float, decimals: int = 0) -> str:
    """Formata moeda brasileira."""
    if decimals == 0:
        return f"R$ {value:,.0f}".replace(",", ".")
    else:
        return f"R$ {value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percent(value: float, decimals: int = 1, with_sign: bool = True) -> str:
    """Formata percentual."""
    if with_sign:
        return f"{value:+.{decimals}f}%".replace(".", ",")
    else:
        return f"{value:.{decimals}f}%".replace(".", ",")


def format_number(value: float, decimals: int = 0) -> str:
    """Formata número com separador de milhares."""
    if decimals == 0:
        return f"{value:,.0f}".replace(",", ".")
    else:
        return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
