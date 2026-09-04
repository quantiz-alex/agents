"""Smoke temporÃ¡rio: instancia todos os componentes e grÃ¡ficos das bibliotecas."""
import importlib.util
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent


def load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ui = load("ui_components", "components-library.py")
ch = load("charts", "charts-library.py")

df = pd.DataFrame(
    {
        "id": [1, 2, 3],
        "produto": ["A", "B", "C"],
        "preco": [10.5, 20.0, 30.25],
        "variacao_pct": [1.5, -2.0, 0.0],
        "status": ["Aprovado", "Pendente AprovaÃ§Ã£o", "Rejeitado"],
        "data": ["2026-01-01", "2026-02-01", "2026-03-01"],
        "ativo": [1, 0, 1],
    }
)

comps = [
    ui.kpi_card("Receita", "R$ 1", "R$ 2", 3.7, "up"),
    ui.kpi_simple("Pendentes", "5", delta_pct=-2.0, trend=[1, 2, 3, 2], hint="mÃªs"),
    ui.kpi_row([ui.kpi_simple("A", "1"), ui.kpi_simple("B", "2")], row_id="x-kpis"),
    ui.data_table(df, "x-grid", column_types={"preco": "currency", "variacao_pct": "pct_delta", "status": "badge", "data": "date", "ativo": "bool"},
                  row_actions=["detalhar", "editar"], default_sort=("preco", "desc"), hide_cols=["id"], selectable=True),
    ui.data_table(df, "x-grid2", numeric_cols=["preco"], status_col="status"),
    ui.quick_filter_input("x-grid"),
    ui.filter_card([ui.filter_select("f1", "FamÃ­lia", ["A", "B"]), ui.filter_date_range("f2", "PerÃ­odo"), ui.filter_text("f3", "Busca")], "x-btn", right=ui.chips_row("x-chips", [ui.chip("FamÃ­lia", "A", {"type": "x-chip", "field": "familia"})])),
    ui.param_slider("x-p", "Markup", "%", -20, 40, 1, 0, hint="ajuste"),
    ui.empty_state(action=ui.button("Limpar", primary=False)),
    ui.loading(ui.card("T", "b", right="r", icon_key="table")),
    ui.toast("x-toast"),
    ui.confirm_modal("x-confirm", danger=True, with_comment=True, comment_required=True),
    ui.detail_offcanvas("x-detail"),
    ui.detail_field("Nome", "Bateria", mono=False),
    ui.user_badge("Ana Souza", "gerente", "ana@x.com"),
    ui.status_badge("Ativo"),
    ui.stat_pill("dados atÃ© 31/08", "info", "calendar3"),
    ui.section_title("SeÃ§Ã£o", right=ui.button("x", primary=False), icon_key="graph-up"),
    ui.home_shortcut_card("calculator", "SimulaÃ§Ã£o", "desc", "/simulacao", badge="5 pendÃªncias"),
    ui.app_shell("k", "speedometer2", "T", "S", [ui.section_title("a")], actions=[ui.button("Exportar", primary=False, icon_key="download")], breadcrumb_items=[("Pricing", "/home"), "Tela"], meta=[ui.stat_pill("x")]),
    ui.app_shell_with_workflow("k", "i", "T", "S", [], workflow_context={"workflow_id": "w", "step_id": "s"}),
]
print("ui components:", len(comps), "ok")
assert ui.notify("ok")[0] is True
assert ui.format_currency(1234567.891, 2) == "R$ 1.234.567,89"
assert ui.format_compact(1_260_000) == "R$ 1,3M"
assert ui.format_percent(3.7) == "+3,7%"
assert ui.format_date("2026-03-01T10:00:00") == "01/03/2026"
pal = ui.derive_palette("#0F766E")
assert set(pal) >= {"primary", "primary_hover", "primary_soft", "primary_dark", "secondary"}

figs = [
    ch.bar_ranking(["a", "b"], [2, 1], title="t"),
    ch.bar_vertical(["a"], [1]),
    ch.variation_bars(["a", "b"], [1.5, -2]),
    ch.donut(["a", "b"], [1, 2]),
    ch.pie(["a"], [1]),
    ch.line_chart([1, 2], [3, 4], title="t"),
    ch.multi_line_chart([1, 2], {"s1": [1, 2], "s2": [2, 1]}),
    ch.area_chart([1, 2], [1, 2]),
    ch.scatter_chart([1], [1]),
    ch.histogram([1, 2, 2, 3]),
    ch.waterfall_chart(["Atual", "PreÃ§o", "Volume", "Simulado"], [100, 10, -5, 105]),
    ch.elasticity_curve([1, 2, 3], [30, 20, 10], 2, 2.5),
    ch.scenario_comparison_chart([{"nome": "A", "r": 1}, {"nome": "B", "r": 2}], "r"),
    ch.heatmap(["Loja", "Web"], ["Bat", "Filt"], [[1, 2], [3, None]], title="h"),
    ch.treemap(["Bat", "Filt", "F1"], ["", "", "Bat"], [10, 5, 4], title="t"),
    ch.combo_bar_line(["jan", "fev"], [10, 12], [100, 130], title="c"),
    ch.stacked_bars(["jan"], {"Loja": [1], "Web": [2]}, percent=True),
    ch.stacked_bars(["jan"], {"Loja": [1]}, horizontal=True),
    ch.grouped_bars(["a", "b"], {"Atual": [1, 2], "Simulado": [2, 3]}),
    ch.funnel(["A", "B", "C"], [10, 6, 2]),
    ch.gauge(27.5, target=30, title="Margem"),
    ch.sparkline([1, 3, 2, 4]),
]
ch.with_selection(figs[0], "a")
for f in figs:
    f.to_json()
ch.set_primary_color("#0F766E", "#F59E0B")
print("charts:", len(figs), "ok")

