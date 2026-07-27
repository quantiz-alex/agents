# Dash Starter — Padrão PMZ

Kit pronto para os agentes gerarem telas já no padrão. Fonte única de estilo em bibliotecas;
toda página é montada com `app_shell(...)` e usa `kpi_card` / `data_table` / `charts`.

## Estrutura

```
dash-starter/
├── README.md                    # este arquivo
├── requirements.txt             # dependências Python
├── assets/
│   ├── theme.css               # CSS global (fontes, reset, scrollbar)
│   └── icons/                  # ícones Bootstrap Icons (opcional)
└── components/
    ├── ui_components.py        # componentes reutilizáveis
    └── charts.py               # gráficos Plotly padronizados
```

## Como usar

### 1. Copiar para novo projeto

```bash
# No início de um novo projeto, copie os arquivos:
cp -r .claude/templates/dash-starter/components frontend/
cp -r .claude/templates/dash-starter/assets .
cp .claude/templates/dash-starter/requirements.txt .
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Criar uma página

```python
from frontend.components.ui_components import app_shell, kpi_card, kpi_row, button
from frontend.components.charts import bar_ranking

def layout():
    kpis = [
        kpi_card("Faturamento atual × simulado", "R$ 1.899.674", "R$ 1.969.961", +3.7, "up"),
        kpi_card("Custo atual × simulado", "R$ 1.181.668", "R$ 1.335.509", +13.0, "down"),
    ]
    
    chart = bar_ranking(
        ["Bosch", "Freedom", "Fulgor"],
        [612, 548, 447]
    )
    
    return app_shell(
        active_key="dashboard",
        icon_key="speedometer2",
        title="Dashboard de Precificação",
        subtitle="Visão executiva comparando o cenário atual com o simulado ativo.",
        actions=[button("Exportar", primary=False, icon_key="download")],
        content=[kpi_row(kpis), dcc.Graph(figure=chart)]
    )
```

## Componentes Disponíveis

### UI Components (`ui_components.py`)

- **`app_shell(active_key, icon_key, title, subtitle, content, actions)`** — Shell completo da página
- **`kpi_card(label, atual, simulado, delta_pct, better)`** — KPI com comparação + delta colorido
- **`kpi_row(cards)`** — Row de KPI cards
- **`data_table(df, id, numeric_cols, status_col, page_size)`** — AG Grid estilizada
- **`page_header(icon_key, title, subtitle, actions)`** — Cabeçalho de página
- **`card(title, body, right)`** — Card genérico
- **`button(label, primary, icon_key)`** — Botão padrão
- **`filter_card(filters, button_id)`** — Card de filtros compacto
- **`icon(icon_name, size)`** — Ícone Bootstrap Icons

### Charts (`charts.py`)

- **`bar_ranking(labels, values, value_fmt, title, height)`** — Barras horizontais para ranking
- **`bar_vertical(labels, values, title, height)`** — Barras verticais
- **`variation_bars(labels, pcts, title, height)`** — Barras +/- com cores semânticas
- **`donut(labels, values, title, height, hole)`** — Rosca com legenda externa
- **`pie(labels, values, title, height)`** — Pizza simples
- **`line_chart(x, y, title, x_label, y_label, height)`** — Linha para tendências
- **`multi_line_chart(x, series, title, x_label, y_label, height)`** — Múltiplas linhas
- **`area_chart(x, y, title, x_label, y_label, height)`** — Área
- **`scatter_chart(x, y, title, x_label, y_label, height)`** — Dispersão
- **`histogram(values, title, x_label, y_label, height, nbins)`** — Histograma

### Helpers

- **`format_currency(value, decimals)`** — Formata moeda brasileira
- **`format_percent(value, decimals, with_sign)`** — Formata percentual
- **`format_number(value, decimals)`** — Formata número com separador
- **`status_badge_style(kind)`** — Retorna style para badge semântico
- **`set_primary_color(color)`** — Define cor primária para gráficos

## Tokens

Todos os valores de cor, tipografia e espaçamento estão centralizados em `ui_components.py`:

```python
COLORS = {
    "app_bg": "#f8fafc",
    "surface": "#ffffff",
    "border": "#e2e8f0",
    "text_strong": "#1e293b",
    "text": "#374151",
    "text_muted": "#64748b",
    "pos": ("#166534", "#dcfce7"),  # verde
    "neg": ("#991b1b", "#fee2e2"),  # vermelho
    "warn": ("#92400e", "#fef3c7"),  # âmbar
    "info": ("#1e40af", "#dbeafe"),  # azul
}

FONT_UI = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
FONT_NUM = "monospace"  # sempre com tabular-nums

RADIUS = {"card": "0.375rem", "control": "0.375rem", "pill": "20px", "chip": "6px"}
SPACE = {"page_x": "1.5rem", "page_y": "1rem", "card": "1rem", "gap": "0.75rem"}
```

**Regra:** Nunca escrever hex/valores soltos no código. Sempre usar os tokens.

## Princípios de UX

1. **O dado é o herói** — Layout existe para tornar números legíveis
2. **Uma tela = um objetivo** — Cabeçalho diz o que é e o que fazer
3. **Comparação em vez de valor solto** — Sempre mostrar baseline + delta
4. **Cor com significado** — Verde=positivo, vermelho=negativo, âmbar=atenção
5. **Densidade para uso profissional** — Tabelas compactas, KPIs generosos
6. **Sem tela vazia e sem tela sufocada** — Respiro consistente
7. **Estado sempre visível** — Badges coloridos, não texto simples

## Checklist antes de publicar

- [ ] Usa `app_shell()` para estrutura de página
- [ ] KPIs mostram comparação atual × simulado + delta colorido
- [ ] Números em mono tabular (colunas numéricas, KPIs, preços)
- [ ] Status como badges coloridos (não texto simples)
- [ ] Gráficos com paleta categórica e fundos transparentes
- [ ] Nenhum hex/valor solto no código (usar tokens)
- [ ] Filtros em card compacto com botão `className="w-100"`
- [ ] AG Grid com `floatingFilter=True`, paginação 20
- [ ] Raiz da página: `html.Div(className="page-wrapper px-4 py-3")`
- [ ] Nenhum `dbc.Container` como raiz de página

## Referências

- **Guia Visual Completo:** `.claude/skills/ui-ux-pro-max/GUIA-VISUAL-PMZ.md`
- **Design System:** `.claude/design-system.yaml`
- **Skill UI/UX:** `.claude/skills/ui-ux-pro-max/SKILL.md`
