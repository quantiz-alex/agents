"""
components-library.py — Biblioteca de componentes reutilizáveis padrão PMZ (v4).
Copie este arquivo para frontend/components/ui_components.py em novos projetos.

Toda página é montada com app_shell(...) e usa exclusivamente os componentes daqui:
  Estrutura .... app_shell, app_shell_with_workflow, page_header, breadcrumb, section_title
  KPIs ......... kpi_card (comparação atual × referência), kpi_simple (valor + tendência), kpi_row
  Dados ........ data_table (AG Grid c/ badges reais, formatos pt-BR, ações por linha), quick_filter_input
  Filtros ...... filter_card, chips_row, chip, param_slider
  Feedback ..... empty_state, loading, toast, notify, confirm_modal, detail_offcanvas
  Identidade ... user_badge, status_badge, stat_pill, home_shortcut_card, icon, button, card
  Formatação ... format_currency, format_percent, format_number, format_date, format_compact
  Tema ......... COLORS, CHART_COLORWAY, derive_palette

Requer: dash>=2.14, dash-bootstrap-components>=1.5, dash-ag-grid>=31, pandas.
Componentes de workflow (breadcrumb de jornada, próximos passos) vivem em workflow_components.py.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import dcc, html

# ============================================================================
# TOKENS — Fonte única de verdade
# ============================================================================

COLORS: dict[str, Any] = {
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
    "neutral": ("#334155", "#f1f5f9"),  # Rascunho / sem semântica
}

# Paleta categórica para gráficos (ordem fixa). CHART_COLORWAY[0] é substituído
# pela cor primária do projeto no Step 0 do frontend-builder.
CHART_COLORWAY = ["#1045C8", "#10b981", "#f59e0b", "#ef4444", "#06b6d4", "#8b5cf6", "#ec4899"]
PRIMARY = CHART_COLORWAY[0]

FONT_UI = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
FONT_NUM = "'JetBrains Mono', 'SFMono-Regular', Consolas, monospace"  # sempre com tabular-nums

RADIUS = {"card": "0.5rem", "control": "0.375rem", "pill": "20px", "chip": "6px"}
SPACE = {"page_x": "1.5rem", "page_y": "1rem", "card": "1rem", "gap": "0.75rem"}

# Mapa status textual -> tipo semântico (use em tabelas/callbacks/badges)
STATUS_KIND: dict[str, str] = {
    "Aprovado": "pos",
    "Ativo": "pos",
    "Vigente": "pos",
    "Publicado": "pos",
    "Concluído": "pos",
    "Sim": "pos",
    "Rejeitado": "neg",
    "Inativo": "neg",
    "Cancelado": "neg",
    "Bloqueado": "neg",
    "Não": "neg",
    "Pendente": "warn",
    "Pendente Aprovação": "warn",
    "Em análise": "warn",
    "Atrasado": "warn",
    "Simulado": "info",
    "Novo": "info",
    "Rascunho": "neutral",
    "admin": "info",
    "supervisor": "warn",
    "gerente": "warn",
    "analista": "neutral",
}


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _mix(hex_color: str, target: tuple[int, int, int], ratio: float) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    tr, tg, tb = target
    mixed = (
        round(r + (tr - r) * ratio),
        round(g + (tg - g) * ratio),
        round(b + (tb - b) * ratio),
    )
    return "#{:02x}{:02x}{:02x}".format(*mixed)


def derive_palette(primary: str, secondary: str | None = None) -> dict[str, str]:
    """
    Deriva a paleta do projeto a partir da cor primária (e secundária opcional).
    Usada pelo frontend-builder para gerar assets/theme.css (CSS vars) e o colorway.
    """
    return {
        "primary": primary,
        "primary_hover": _mix(primary, (0, 0, 0), 0.15),
        "primary_soft": _mix(primary, (255, 255, 255), 0.90),
        "primary_soft_border": _mix(primary, (255, 255, 255), 0.75),
        "primary_dark": _mix(primary, (15, 23, 42), 0.55),
        "secondary": secondary or _mix(primary, (245, 158, 11), 0.75),
    }


def set_primary_color(primary: str, secondary: str | None = None) -> None:
    """Aplica a cor primária do projeto aos tokens em runtime (opcional — o Step 0 já substitui no arquivo)."""
    global PRIMARY
    PRIMARY = primary
    CHART_COLORWAY[0] = primary
    if secondary:
        CHART_COLORWAY[2] = secondary


# ============================================================================
# HELPERS DE FORMATAÇÃO (pt-BR)
# ============================================================================


def _br(number: str) -> str:
    return number.replace(",", "X").replace(".", ",").replace("X", ".")


def format_currency(value: float | None, decimals: int = 0) -> str:
    """Moeda brasileira: R$ 1.234.567 (decimals=0) ou R$ 1.234,56 (decimals=2)."""
    if value is None:
        return "—"
    return "R$ " + _br(f"{value:,.{decimals}f}")


def format_percent(value: float | None, decimals: int = 1, with_sign: bool = True) -> str:
    """Percentual com vírgula decimal e sinal opcional: +3,7%."""
    if value is None:
        return "—"
    s = f"{value:+.{decimals}f}" if with_sign else f"{value:.{decimals}f}"
    return s.replace(".", ",") + "%"


def format_number(value: float | None, decimals: int = 0) -> str:
    """Número com separador de milhares pt-BR."""
    if value is None:
        return "—"
    return _br(f"{value:,.{decimals}f}")


def format_compact(value: float | None, prefix: str = "R$ ") -> str:
    """Formato compacto para KPIs executivos: R$ 1,2M · R$ 48,3K · R$ 950."""
    if value is None:
        return "—"
    abs_v = abs(value)
    if abs_v >= 1_000_000_000:
        s, suf = value / 1_000_000_000, "B"
    elif abs_v >= 1_000_000:
        s, suf = value / 1_000_000, "M"
    elif abs_v >= 1_000:
        s, suf = value / 1_000, "K"
    else:
        return prefix + _br(f"{value:,.0f}")
    return prefix + f"{s:.1f}".replace(".", ",") + suf


def format_date(value: str | date | datetime | None) -> str:
    """dd/mm/aaaa a partir de ISO string, date ou datetime."""
    if value is None or value == "":
        return "—"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value[:19])
        except ValueError:
            return value
    return value.strftime("%d/%m/%Y")


# ============================================================================
# COMPONENTES BÁSICOS
# ============================================================================


def icon(icon_name: str, size: str = "1rem", className: str = "") -> html.I:
    """Ícone Bootstrap Icons."""
    return html.I(className=f"bi bi-{icon_name} {className}".strip(), style={"fontSize": size})


def button(
    label: str,
    primary: bool = True,
    icon_key: str | None = None,
    danger: bool = False,
    size: str | None = "sm",
    **kwargs: Any,
) -> dbc.Button:
    """Botão padrão: primário cheio, ghost (outline) para secundários, vermelho outline para destrutivos."""
    children: list = []
    if icon_key:
        children += [icon(icon_key, "0.875rem"), " "]
    children.append(label)
    if danger:
        color, outline = "danger", True
    else:
        color, outline = ("primary", False) if primary else ("secondary", True)
    cls = ("fw-semibold " + kwargs.pop("className", "")).strip()
    return dbc.Button(children, color=color, outline=outline, size=size, className=cls, **kwargs)


def status_badge(value: str, kind: str | None = None) -> html.Span:
    """Pill de status com cor semântica (kind inferido de STATUS_KIND se omitido)."""
    kind = kind or STATUS_KIND.get(str(value), "neutral")
    fg, bg = COLORS[kind]
    return html.Span(
        str(value),
        className="status-pill",
        style={"color": fg, "backgroundColor": bg},
    )


def status_badge_style(kind: str) -> dict[str, Any]:
    """kind: 'pos' | 'neg' | 'warn' | 'info' | 'neutral' -> style de pill (compat v3)."""
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


def stat_pill(text: str, kind: str = "info", icon_key: str | None = None) -> html.Span:
    """Chip informativo pequeno (ex.: 'dados até 31/08/2026', '1.284 itens afetados')."""
    fg, bg = COLORS[kind]
    children: list = [icon(icon_key, "0.75rem", "me-1")] if icon_key else []
    children.append(text)
    return html.Span(
        children,
        className="stat-pill",
        style={"color": fg, "backgroundColor": bg},
    )


def section_title(text: str, right: Any | None = None, icon_key: str | None = None) -> html.Div:
    """Título de seção dentro da página (H5) com conteúdo opcional à direita."""
    left: list = [icon(icon_key, "1rem", "text-primary me-2")] if icon_key else []
    left.append(html.H5(text, className="mb-0 fw-semibold", style={"fontSize": "1rem"}))
    return html.Div(
        [html.Div(left, className="d-flex align-items-center"), html.Div(right if right is not None else [])],
        className="d-flex align-items-center justify-content-between mt-2 mb-2",
    )


def user_badge(name: str, role: str, email: str | None = None, compact: bool = False) -> html.Div:
    """Bloco do usuário logado: avatar com iniciais + nome + badge de role (usado na sidebar/Home)."""
    initials = "".join(p[0] for p in str(name).split()[:2]).upper() or "?"
    avatar = html.Div(
        initials,
        className="user-avatar",
        style={"background": PRIMARY},
    )
    if compact:
        return html.Div([avatar], className="d-flex align-items-center")
    return html.Div(
        [
            avatar,
            html.Div(
                [
                    html.Div(name, className="fw-semibold text-truncate", style={"fontSize": "0.85rem", "color": COLORS["text_strong"]}),
                    html.Div(
                        [status_badge(role), html.Span(email or "", className="text-muted ms-2 text-truncate", style={"fontSize": "0.7rem"})],
                        className="d-flex align-items-center",
                    ),
                ],
                className="ms-2 overflow-hidden flex-grow-1",
            ),
        ],
        className="d-flex align-items-center",
    )


# ============================================================================
# CABEÇALHO DE PÁGINA / SHELL
# ============================================================================


def breadcrumb(items: list[str | tuple[str, str]]) -> html.Nav:
    """
    Breadcrumb 'Grupo › Tela'. Cada item é str (texto) ou (texto, href).
    O último item é o atual (sem link).
    """
    crumbs: list = []
    for i, it in enumerate(items):
        text, href = (it, None) if isinstance(it, str) else it
        is_last = i == len(items) - 1
        if href and not is_last:
            crumbs.append(dcc.Link(text, href=href, className="crumb"))
        else:
            crumbs.append(html.Span(text, className="crumb crumb-current" if is_last else "crumb"))
        if not is_last:
            crumbs.append(html.Span("›", className="crumb-sep"))
    return html.Nav(crumbs, className="breadcrumb-pmz", **{"aria-label": "breadcrumb"})


def page_header(
    icon_key: str,
    title: str,
    subtitle: str,
    actions: list | None = None,
    breadcrumb_items: list | None = None,
    meta: list | None = None,
) -> html.Div:
    """
    Cabeçalho padrão: [breadcrumb] · ícone + H4 + subtítulo (objetivo do usuário) · ações à direita.
    meta: lista de stat_pill/chips exibidos abaixo do subtítulo (ex.: 'dados até 31/08').
    """
    left: list = []
    if breadcrumb_items:
        left.append(breadcrumb(breadcrumb_items))
    left.append(
        html.Div(
            [
                html.Div(icon(icon_key, "1.25rem"), className="page-icon"),
                html.H4(title, className="mb-0 fw-semibold", style={"letterSpacing": "-0.02em"}),
            ],
            className="d-flex align-items-center gap-2",
        )
    )
    if subtitle:
        left.append(html.P(subtitle, className="text-muted mb-0 mt-1", style={"fontSize": "0.875rem", "maxWidth": "720px"}))
    if meta:
        left.append(html.Div(meta, className="d-flex flex-wrap gap-2 mt-2"))
    return html.Div(
        [
            html.Div(left, className="min-w-0"),
            html.Div(actions or [], className="d-flex flex-wrap gap-2 page-actions", style={"flexShrink": 0}),
        ],
        className="page-header d-flex align-items-start justify-content-between gap-3 mb-3",
    )


def app_shell(
    active_key: str,
    icon_key: str,
    title: str,
    subtitle: str,
    content: list,
    actions: list | None = None,
    breadcrumb_items: list | None = None,
    meta: list | None = None,
) -> html.Div:
    """
    Shell completo da área de conteúdo (a sidebar é renderizada por app.py).
    breadcrumb_items: ex. ["Pricing", "Simulação de Reajuste"] (grupo de menu + tela).
    """
    return html.Div(
        [page_header(icon_key, title, subtitle, actions, breadcrumb_items, meta), *content],
        className="page-wrapper px-4 py-3",
        style={"background": COLORS["app_bg"], "minHeight": "100vh"},
    )


def app_shell_with_workflow(
    active_key: str,
    icon_key: str,
    title: str,
    subtitle: str,
    content: list,
    actions: list | None = None,
    workflow_context: dict | None = None,
    breadcrumb_items: list | None = None,
    meta: list | None = None,
) -> html.Div:
    """
    app_shell + breadcrumb de jornada e próximos passos quando a tela participa de um workflow.
    workflow_context: {"workflow_id", "step_id", "context_data", "user_role"} (ver workflow_components.py).
    """
    wf_breadcrumb = None
    wf_actions: list = []
    if workflow_context:
        try:
            from frontend.components.workflow_components import (  # type: ignore
                workflow_breadcrumb,
                workflow_context_actions,
            )

            wf_breadcrumb = workflow_breadcrumb(
                workflow_context["workflow_id"],
                workflow_context["step_id"],
                workflow_context.get("context_data", {}),
            )
            wf_actions = workflow_context_actions(
                workflow_context["workflow_id"],
                workflow_context["step_id"],
                workflow_context.get("context_data", {}),
                workflow_context.get("user_role"),
            )
        except ImportError:
            pass
    page_content: list = ([wf_breadcrumb] if wf_breadcrumb else []) + list(content)
    return app_shell(
        active_key, icon_key, title, subtitle, page_content,
        (actions or []) + wf_actions, breadcrumb_items, meta,
    )


# ============================================================================
# KPI CARDS
# ============================================================================


def _fmt_pct(v: float) -> str:
    return f"{v:+.1f}".replace(".", ",") + "%"


def _delta_kind(delta_pct: float, better: str) -> str:
    if better == "neutral" or delta_pct == 0:
        return "neutral"
    good = (delta_pct > 0) if better == "up" else (delta_pct < 0)
    return "pos" if good else "neg"


def _delta_badge(delta_pct: float, kind: str, suffix: str = "") -> html.Div:
    fg, bg = COLORS[kind]
    arrow = "▲" if delta_pct > 0 else ("▼" if delta_pct < 0 else "•")
    return html.Div(
        [html.Span(arrow), " ", _fmt_pct(delta_pct), html.Span(suffix, className="ms-1 fw-normal") if suffix else None],
        className="kpi-delta",
        style={"color": fg, "backgroundColor": bg, "fontFamily": FONT_NUM},
    )


def _kpi_label(label: str, icon_key: str | None) -> html.Div:
    children: list = [html.Span(label)]
    if icon_key:
        children.append(icon(icon_key, "0.9rem", "text-muted"))
    return html.Div(
        children,
        className="kpi-label d-flex justify-content-between align-items-start text-muted text-uppercase fw-bold",
    )


def kpi_card(
    label: str,
    atual: str,
    simulado: str,
    delta_pct: float,
    better: str = "up",
    compare_label: str = "de",
    icon_key: str | None = None,
) -> dbc.Card:
    """
    KPI de COMPARAÇÃO: valor de referência (simulado/atual) em destaque, baseline ('de {atual}')
    e delta % colorido. Use para atual × simulado, mês × mês anterior, realizado × meta.

    Args:
        label: rótulo (eyebrow)
        atual: baseline formatado (ex.: mês anterior / cenário atual)
        simulado: valor em destaque formatado (ex.: mês atual / cenário simulado)
        delta_pct: variação percentual (3.7 → +3,7%)
        better: 'up' (subir é bom) | 'down' (subir é ruim) | 'neutral'
        compare_label: texto antes do baseline — 'de', 'vs', 'meta'
    """
    kind = _delta_kind(delta_pct, better)
    border = {"pos": "success", "neg": "danger", "warn": "warning"}.get(kind, "secondary")
    return dbc.Card(
        dbc.CardBody(
            [
                _kpi_label(label, icon_key),
                html.Div(simulado, className="kpi-value", style={"fontFamily": FONT_NUM, "color": COLORS["text_strong"]}),
                html.Div(f"{compare_label} {atual}", className="kpi-baseline", style={"fontFamily": FONT_NUM, "color": COLORS["text_faint"]}),
                _delta_badge(delta_pct, kind),
            ]
        ),
        className=f"kpi-card shadow-sm border-0 border-start border-4 border-{border} mb-3 h-100",
    )


def kpi_simple(
    label: str,
    value: str,
    delta_pct: float | None = None,
    better: str = "up",
    trend: list[float] | None = None,
    icon_key: str | None = None,
    hint: str | None = None,
    color: str = "primary",
) -> dbc.Card:
    """
    KPI SIMPLES: um valor em destaque, opcionalmente com delta % e/ou sparkline de tendência.
    Use quando NÃO há baseline natural (ex.: 'Pendentes', 'SKUs ativos', 'Ticket médio').

    Args:
        value: valor formatado
        delta_pct: variação opcional (ex.: vs período anterior)
        trend: lista de valores para sparkline (últimos N períodos)
        hint: texto pequeno abaixo do valor (ex.: 'últimos 12 meses')
        color: cor da borda lateral quando não há delta (primary|info|secondary)
    """
    kind = _delta_kind(delta_pct, better) if delta_pct is not None else None
    border = {"pos": "success", "neg": "danger"}.get(kind or "", color)
    body: list = [
        _kpi_label(label, icon_key),
        html.Div(value, className="kpi-value", style={"fontFamily": FONT_NUM, "color": COLORS["text_strong"]}),
    ]
    footer: list = []
    if delta_pct is not None:
        footer.append(_delta_badge(delta_pct, kind or "neutral"))
    if hint:
        footer.append(html.Span(hint, className="text-muted", style={"fontSize": "0.72rem"}))
    if trend:
        try:
            from frontend.components.charts import sparkline  # type: ignore

            footer.append(
                dcc.Graph(
                    figure=sparkline(trend, color=COLORS["pos"][0] if (kind in (None, "pos")) else COLORS["neg"][0]),
                    config={"displayModeBar": False, "staticPlot": True},
                    style={"height": "36px", "width": "110px"},
                    className="ms-auto",
                )
            )
        except ImportError:
            pass
    if footer:
        body.append(html.Div(footer, className="d-flex align-items-center gap-2 mt-2"))
    return dbc.Card(
        dbc.CardBody(body),
        className=f"kpi-card shadow-sm border-0 border-start border-4 border-{border} mb-3 h-100",
    )


def kpi_row(cards: list, row_id: str | None = None) -> dbc.Row:
    """Row responsiva de KPIs: 1 col no mobile, 2 em tablets, N em desktop (mín. 3 cols)."""
    n = max(len(cards), 1)
    md = max(12 // n, 3)
    cols = [dbc.Col(c, xs=12, sm=6, md=md) for c in cards]
    kwargs: dict[str, Any] = {"id": row_id} if row_id else {}
    return dbc.Row(cols, className="g-3 mb-1 kpi-row", **kwargs)


# ============================================================================
# CARD GENÉRICO
# ============================================================================


def card(
    title: str,
    body: Any,
    right: Any | None = None,
    icon_key: str | None = None,
    body_class: str = "",
    card_id: str | None = None,
) -> dbc.Card:
    """Card com header (título + conteúdo opcional à direita) e body."""
    header_left: list = [icon(icon_key, "0.9rem", "text-primary me-2")] if icon_key else []
    header_left.append(html.Span(title, className="fw-semibold", style={"fontSize": "0.875rem"}))
    right_el = html.Span(right, className="text-muted small") if isinstance(right, str) else (right if right is not None else [])
    kwargs: dict[str, Any] = {"id": card_id} if card_id else {}
    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    [html.Div(header_left, className="d-flex align-items-center"), html.Div(right_el)],
                    className="d-flex align-items-center justify-content-between",
                ),
                className="bg-white border-bottom",
            ),
            dbc.CardBody(body, className=body_class),
        ],
        className="shadow-sm border-0 mb-3",
        **kwargs,
    )


def home_shortcut_card(icon_key: str, title: str, description: str, href: str, badge: str | None = None) -> dcc.Link:
    """Card-atalho da Home: ícone, título, descrição e badge opcional (ex.: '5 pendências')."""
    return dcc.Link(
        dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.Div(icon(icon_key, "1.25rem"), className="page-icon"),
                            stat_pill(badge, "warn") if badge else None,
                        ],
                        className="d-flex justify-content-between align-items-start mb-2",
                    ),
                    html.Div(title, className="fw-semibold", style={"color": COLORS["text_strong"]}),
                    html.Div(description, className="text-muted", style={"fontSize": "0.8rem"}),
                ]
            ),
            className="shadow-sm border-0 h-100 shortcut-card",
        ),
        href=href,
        className="text-decoration-none",
    )


# ============================================================================
# FEEDBACK: EMPTY STATE, LOADING, TOAST, MODAL, OFFCANVAS
# ============================================================================


def empty_state(
    title: str = "Nenhum registro encontrado",
    hint: str = "Ajuste os filtros ou amplie o período.",
    icon_key: str = "inbox",
    action: Any | None = None,
    compact: bool = False,
) -> html.Div:
    """Estado vazio explicativo — SEMPRE usar no lugar de grid/gráfico vazio."""
    return html.Div(
        [
            html.Div(icon(icon_key, "1.75rem" if compact else "2.25rem"), className="empty-icon"),
            html.Div(title, className="fw-semibold mt-2", style={"color": COLORS["text_strong"]}),
            html.Div(hint, className="text-muted", style={"fontSize": "0.85rem", "maxWidth": "360px"}),
            html.Div(action, className="mt-3") if action is not None else None,
        ],
        className="empty-state text-center d-flex flex-column align-items-center " + ("py-3" if compact else "py-5"),
    )


def loading(children: Any, id: str | None = None, overlay: bool = True) -> dcc.Loading:
    """dcc.Loading padronizado (spinner na cor primária, overlay leve). Envolva grids/gráficos atualizados por callback."""
    kwargs: dict[str, Any] = {"id": id} if id else {}
    return dcc.Loading(children, type="circle", color=PRIMARY, className="pmz-loading" if overlay else "", **kwargs)


def toast(id: str, header: str = "Notificação") -> dbc.Toast:
    """Toast fixo no canto superior direito. Controle com notify() → (is_open, children, icon)."""
    return dbc.Toast(
        id=id,
        header=header,
        is_open=False,
        dismissable=True,
        duration=4000,
        icon="primary",
        style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999, "width": 360},
    )


def notify(message: str, kind: str = "success") -> tuple[bool, Any, str]:
    """
    Retorna a tupla para os 3 Outputs padrão do toast: (is_open, children, icon).
    kind: success | danger | warning | info
    """
    icons = {"success": "check-circle-fill", "danger": "x-circle-fill", "warning": "exclamation-triangle-fill", "info": "info-circle-fill"}
    children = html.Div([icon(icons.get(kind, "info-circle-fill"), "1rem", f"text-{kind} me-2"), message], className="d-flex align-items-center")
    return True, children, kind


def confirm_modal(
    id: str,
    title: str = "Confirmar ação",
    body: Any = "Tem certeza? Esta ação não pode ser desfeita.",
    confirm_label: str = "Confirmar",
    danger: bool = False,
    with_comment: bool = False,
    comment_label: str = "Comentário",
    comment_required: bool = False,
) -> dbc.Modal:
    """
    Modal de confirmação. IDs gerados: {id} (modal), {id}-confirm, {id}-cancel, {id}-comment (se with_comment).
    Use SEMPRE antes de ações destrutivas (excluir/desativar) e de decisões (aprovar/rejeitar).
    """
    body_children: list = [html.Div(body, id=f"{id}-body")]
    if with_comment:
        body_children += [
            dbc.Label([comment_label, html.Span(" *", className="text-danger") if comment_required else None], className="small fw-semibold mt-3"),
            dbc.Textarea(id=f"{id}-comment", rows=3, placeholder="Descreva o motivo..."),
        ]
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title, className="fs-6 fw-semibold")),
            dbc.ModalBody(body_children),
            dbc.ModalFooter(
                [
                    dbc.Button("Cancelar", id=f"{id}-cancel", color="secondary", outline=True, size="sm"),
                    dbc.Button(confirm_label, id=f"{id}-confirm", color="danger" if danger else "primary", size="sm", className="fw-semibold"),
                ]
            ),
        ],
        id=id,
        is_open=False,
        centered=True,
    )


def detail_offcanvas(id: str, title: str = "Detalhe", width: int = 520, placement: str = "end") -> dbc.Offcanvas:
    """
    Painel lateral de detalhe (master_detail / approval_queue / clique em linha).
    IDs gerados: {id} (offcanvas), {id}-body. No callback: Output(id, "is_open"), Output(id, "title"), Output(f"{id}-body", "children").
    """
    return dbc.Offcanvas(
        html.Div(id=f"{id}-body"),
        id=id,
        title=title,
        is_open=False,
        placement=placement,
        scrollable=True,
        backdrop=True,
        style={"width": f"{width}px"},
        className="detail-offcanvas",
    )


def detail_field(label: str, value: Any, mono: bool = False) -> html.Div:
    """Par rótulo/valor para uso dentro do detail_offcanvas."""
    return html.Div(
        [
            html.Div(label, className="text-muted text-uppercase fw-bold", style={"fontSize": "0.65rem", "letterSpacing": "0.05em"}),
            html.Div(value, className="fw-semibold", style={"fontFamily": FONT_NUM if mono else FONT_UI, "fontSize": "0.9rem", "color": COLORS["text_strong"]}),
        ],
        className="mb-3",
    )


# ============================================================================
# FILTROS
# ============================================================================


def filter_card(
    filters: list,
    button_id: str = "btn-filtrar",
    show_button: bool = True,
    right: Any | None = None,
    card_id: str | None = None,
) -> dbc.Card:
    """
    Card de filtros compacto no topo da página.
    filters: lista de dbc.Col (cada um com dbc.Label + input).
    show_button=False para filtros 'ao vivo' (callbacks disparam na mudança dos inputs).
    right: conteúdo extra à direita do botão (ex.: chips_row de filtros ativos).
    """
    cols = list(filters)
    if show_button:
        cols.append(
            dbc.Col(
                button("Filtrar", primary=True, icon_key="funnel", id=button_id, className="w-100", size=None),
                xs=12, md=2, lg=1,
                className="d-grid",
            )
        )
    kwargs: dict[str, Any] = {"id": card_id} if card_id else {}
    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(cols, className="g-2 align-items-end"),
                html.Div(right, className="mt-2") if right is not None else None,
            ],
            className="py-2",
        ),
        className="shadow-sm border-0 mb-3 filter-card",
        **kwargs,
    )


def filter_select(id: str, label: str, options: list, value: Any = None, all_label: str | None = "Todos", md: int = 3) -> dbc.Col:
    """Filtro select padrão em dbc.Col com label. options: lista de str ou {label, value}."""
    opts = [{"label": o, "value": o} if isinstance(o, str) else o for o in options]
    if all_label is not None:
        opts = [{"label": all_label, "value": ""}] + opts
        value = value if value is not None else ""
    return dbc.Col(
        [dbc.Label(label, className="small fw-semibold"), dbc.Select(id=id, options=opts, value=value)],
        xs=12, sm=6, md=md,
    )


def filter_date_range(id: str, label: str, start: Any = None, end: Any = None, md: int = 3) -> dbc.Col:
    """Filtro de período (dcc.DatePickerRange) padronizado."""
    return dbc.Col(
        [
            dbc.Label(label, className="small fw-semibold"),
            dcc.DatePickerRange(
                id=id, start_date=start, end_date=end, display_format="DD/MM/YYYY",
                clearable=True, className="w-100", start_date_placeholder_text="Início", end_date_placeholder_text="Fim",
            ),
        ],
        xs=12, sm=6, md=md,
    )


def filter_text(id: str, label: str, placeholder: str = "Buscar...", md: int = 3) -> dbc.Col:
    """Filtro texto com debounce (não dispara a cada tecla)."""
    return dbc.Col(
        [dbc.Label(label, className="small fw-semibold"), dbc.Input(id=id, type="text", placeholder=placeholder, debounce=True)],
        xs=12, sm=6, md=md,
    )


def chip(label: str, value: str, chip_id: dict | str, removable: bool = True) -> html.Span:
    """Chip de filtro ativo (ex.: 'Família: Baterias ✕'). chip_id pattern-matching: {"type": "<page>-chip", "field": ...}."""
    children: list = [html.Span(f"{label}: ", className="text-muted"), html.Span(value, className="fw-semibold")]
    if removable:
        children.append(html.Span("✕", id=chip_id, className="chip-remove", n_clicks=0))
    return html.Span(children, className="filter-chip")


def chips_row(id: str, chips: list | None = None) -> html.Div:
    """Container de chips de filtros ativos (drill-down). Preenchido por callback via children."""
    return html.Div(chips or [], id=id, className="d-flex flex-wrap gap-2 chips-row")


def param_slider(
    id: str,
    label: str,
    unit: str = "",
    min: float = 0,
    max: float = 100,
    step: float = 1,
    default: float = 0,
    md: int = 3,
    hint: str | None = None,
) -> dbc.Col:
    """
    Slider de parâmetro para painéis de simulação. Tooltip mostra o valor ao vivo.
    Use SEMPRE que a variável (business_logic.yaml → formula.variables[]) tiver min/max.
    Para recálculo ao vivo, declare o slider como Input (skill08 → Padrão 9).
    """
    marks = {min: f"{min:g}{unit}", default: f"{default:g}{unit}", max: f"{max:g}{unit}"}
    return dbc.Col(
        [
            html.Div(
                [dbc.Label(f"{label} ({unit})" if unit else label, className="small fw-semibold mb-0"), html.Span(hint or "", className="text-muted", style={"fontSize": "0.7rem"})],
                className="d-flex justify-content-between align-items-baseline",
            ),
            dcc.Slider(
                id=id, min=min, max=max, step=step, value=default, marks=marks,
                tooltip={"placement": "top", "always_visible": True},
                className="pt-1 param-slider",
            ),
        ],
        xs=12, md=md,
    )


# ============================================================================
# DATA TABLE (AG GRID)
# ============================================================================

_JS_FMT = {
    "currency": "params.value == null ? '' : 'R$ ' + Number(params.value).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})",
    "currency0": "params.value == null ? '' : 'R$ ' + Number(params.value).toLocaleString('pt-BR', {maximumFractionDigits: 0})",
    "number": "params.value == null ? '' : Number(params.value).toLocaleString('pt-BR', {maximumFractionDigits: 0})",
    "decimal": "params.value == null ? '' : Number(params.value).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})",
    "percent": "params.value == null ? '' : Number(params.value).toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + '%'",
    "pct_delta": "params.value == null ? '' : (params.value > 0 ? '+' : '') + Number(params.value).toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + '%'",
    "date": "params.value ? new Date(String(params.value).slice(0,10) + 'T00:00:00').toLocaleDateString('pt-BR') : ''",
    "datetime": "params.value ? new Date(params.value).toLocaleString('pt-BR', {dateStyle: 'short', timeStyle: 'short'}) : ''",
    "bool": "params.value == null ? '' : ((params.value === true || params.value === 1 || params.value === '1' || params.value === 'true') ? 'Sim' : 'Não')",
}

_NUMERIC_FORMATS = {"currency", "currency0", "number", "decimal", "percent", "pct_delta"}

_BADGE_RULES = {
    "badge-pos": "['Aprovado','Ativo','Vigente','Publicado','Concluído','Sim','true',true,1].includes(params.value)",
    "badge-neg": "['Rejeitado','Inativo','Cancelado','Bloqueado','Não','false',false,0].includes(params.value)",
    "badge-warn": "['Pendente','Pendente Aprovação','Em análise','Atrasado','supervisor','gerente'].includes(params.value)",
    "badge-info": "['Simulado','Novo','admin'].includes(params.value)",
    "badge-neutral": "['Rascunho','analista'].includes(params.value)",
}

_ACTION_LABELS = {
    "detalhar": "Detalhar", "editar": "Editar", "excluir": "Excluir", "desativar": "Desativar",
    "approve": "Aprovar", "reject": "Rejeitar", "visualizar": "Ver", "duplicar": "Duplicar",
}


def _humanize(col: str) -> str:
    return col.replace("_", " ").strip().capitalize()


def data_table(
    df: Any,  # pd.DataFrame
    id: str,
    column_types: dict[str, str] | None = None,
    numeric_cols: list[str] | None = None,
    status_col: str | None = None,
    page_size: int = 20,
    headers: dict[str, str] | None = None,
    row_actions: list[str] | None = None,
    default_sort: tuple[str, str] | None = None,
    hide_cols: list[str] | None = None,
    height: str = "520px",
    empty_message: str = "Nenhum registro encontrado. Ajuste os filtros.",
    selectable: bool = False,
    pending_values: tuple[str, ...] = ("Pendente", "Pendente Aprovação"),
) -> dag.AgGrid:
    """
    AG Grid padrão PMZ — formatos pt-BR, badges reais, ações por linha, linha pendente destacada.

    Args:
        column_types: {coluna: tipo} com tipo ∈ text|currency|currency0|number|decimal|percent|pct_delta|date|datetime|bool|badge
                      (pct_delta colore +verde/−vermelho; badge aplica pill semântica por valor)
        numeric_cols: compat v3 — equivale a column_types={c: "decimal"}
        status_col:   compat v3 — equivale a column_types={status_col: "badge"}
        headers:      {coluna: 'Cabeçalho'} — default: nome humanizado
        row_actions:  ['detalhar','editar','desativar'] → colunas clicáveis; trate cellClicked com colId 'acao_<nome>'
        default_sort: ('coluna', 'asc'|'desc')
        hide_cols:    colunas presentes no df mas ocultas (ex.: 'id' usado só para lookup)
        selectable:   checkbox de seleção múltipla (aprovação em lote)
    """
    column_types = dict(column_types or {})
    for c in numeric_cols or []:
        column_types.setdefault(c, "decimal")
    if status_col:
        column_types.setdefault(status_col, "badge")
    headers = headers or {}
    hide_cols = set(hide_cols or [])

    column_defs: list[dict[str, Any]] = []
    for i, col in enumerate(df.columns):
        ctype = column_types.get(col, "text")
        cdef: dict[str, Any] = {"field": col, "headerName": headers.get(col, _humanize(col)), "hide": col in hide_cols}
        if selectable and i == 0:
            cdef.update({"checkboxSelection": True, "headerCheckboxSelection": True, "minWidth": 160})
        if ctype in _NUMERIC_FORMATS:
            cdef.update({"type": "numericColumn", "cellClass": "cell-num", "valueFormatter": {"function": _JS_FMT[ctype]}, "filter": "agNumberColumnFilter"})
            if ctype == "pct_delta":
                cdef["cellClassRules"] = {"delta-pos": "params.value > 0", "delta-neg": "params.value < 0"}
        elif ctype in ("date", "datetime"):
            cdef.update({"cellClass": "cell-num", "valueFormatter": {"function": _JS_FMT[ctype]}, "filter": "agDateColumnFilter"})
        elif ctype == "bool":
            cdef.update({"cellClass": "cell-badge", "valueFormatter": {"function": _JS_FMT["bool"]}, "cellClassRules": {"badge-pos": _BADGE_RULES["badge-pos"], "badge-neg": _BADGE_RULES["badge-neg"]}})
        elif ctype == "badge":
            cdef.update({"cellClass": "cell-badge", "cellClassRules": dict(_BADGE_RULES), "maxWidth": 190})
        if default_sort and default_sort[0] == col:
            cdef["sort"] = default_sort[1]
        column_defs.append(cdef)

    for action in row_actions or []:
        label = _ACTION_LABELS.get(action, action.capitalize())
        column_defs.append(
            {
                "colId": f"acao_{action}",
                "headerName": "" if len(row_actions or []) > 1 else "Ações",
                "valueGetter": {"function": f"'{label}'"},
                "cellClass": "cell-action" + (" cell-action-danger" if action in ("excluir", "desativar", "reject") else ""),
                "sortable": False, "filter": False, "resizable": False, "suppressMenu": True,
                "width": 96, "pinned": "right",
            }
        )

    grid_options: dict[str, Any] = {
        "pagination": True,
        "paginationPageSize": page_size,
        "paginationPageSizeSelector": [10, 20, 50, 100],
        "animateRows": True,
        "rowHeight": 42,
        "headerHeight": 40,
        "domLayout": "normal",
        "suppressCellFocus": True,
        "enableCellTextSelection": True,
        "overlayNoRowsTemplate": f"<div class='ag-empty'><i class='bi bi-inbox'></i><div>{empty_message}</div></div>",
        "localeText": {
            "page": "Página", "to": "a", "of": "de", "more": "mais", "next": "Próxima", "last": "Última", "first": "Primeira", "previous": "Anterior",
            "pageSize": "Por página", "filterOoo": "Filtrar...", "noRowsToShow": empty_message,
            "equals": "Igual", "notEqual": "Diferente", "contains": "Contém", "notContains": "Não contém", "startsWith": "Começa com", "endsWith": "Termina com",
            "lessThan": "Menor que", "greaterThan": "Maior que", "inRange": "Entre", "blank": "Vazio", "notBlank": "Preenchido",
        },
    }
    if selectable:
        grid_options.update({"rowSelection": "multiple", "suppressRowClickSelection": True})
    if status_col or any(t == "badge" for t in column_types.values()):
        badge_col = status_col or next(c for c, t in column_types.items() if t == "badge")
        vals = ", ".join(f"'{v}'" for v in pending_values)
        grid_options["rowClassRules"] = {"row-pending": f"[{vals}].includes(params.data && params.data['{badge_col}'])"}

    return dag.AgGrid(
        id=id,
        rowData=df.to_dict("records"),
        columnDefs=column_defs,
        defaultColDef={"sortable": True, "filter": True, "resizable": True, "floatingFilter": True, "suppressMenu": True, "flex": 1, "minWidth": 110},
        dashGridOptions=grid_options,
        columnSize="responsiveSizeToFit",
        className="ag-theme-alpine pmz-grid",
        style={"height": height},
        csvExportParams={"fileName": f"{id}.csv"},
    )


def quick_filter_input(grid_id: str, placeholder: str = "Busca rápida na tabela...") -> dbc.Input:
    """
    Campo de busca rápida para um data_table. ID: {grid_id}-quick.
    Callback (skill08): Output(grid_id, "dashGridOptions") ← Input(f"{grid_id}-quick", "value") → {"quickFilterText": value}
    """
    return dbc.Input(id=f"{grid_id}-quick", type="search", placeholder=placeholder, debounce=True, size="sm", style={"maxWidth": "280px"})


def with_empty_state(component: Any, empty: Any, is_empty: bool) -> html.Div:
    """
    Mantém `component` (grid/gráfico) SEMPRE no layout e alterna com `empty_state`.
    Necessário quando o componente é Input/State de callbacks (cellClicked, clickData, dashGridOptions):
    o dash-renderer falha callbacks com dependências parcialmente ausentes.
    """
    return html.Div(
        [
            html.Div(empty, style={} if is_empty else {"display": "none"}),
            html.Div(component, style={"display": "none"} if is_empty else {}),
        ]
    )
