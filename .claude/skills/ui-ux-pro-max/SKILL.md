---
name: ui-ux-pro-max
description: "UI/UX design intelligence for Dash/Python business applications. Guides the frontend-builder agent during all UI phases of the Lighthouse pipeline: design system validation, screen definition, page generation, and pre-delivery review. Stack: Dash 2.14+, Dash Bootstrap Components, Dash AG Grid, Plotly. Actions: plan, design, review, validate, check. Pages: dashboard, admin panel, data table, form, report, KPI. Topics: color systems, accessibility, layout, typography, spacing, interaction states, chart type selection, AG Grid configuration, Plotly templates, callback patterns."
---

# UI/UX Pro Max — Design Intelligence (Dash/Python Edition)

Guia de design e UX para aplicações business em **Dash/Python puro**. Usado pelos agentes do pipeline Lighthouse para garantir qualidade visual, usabilidade e consistência em todas as telas geradas.

> **Stack inegociável:** Dash 2.14+ · Dash Bootstrap Components (dbc) · Dash AG Grid · Plotly · Pandas/NumPy. Nenhuma regra deste guia deve introduzir React, Vue, HTML/CSS/JS separados ou qualquer tecnologia fora deste stack.

> **Guia Visual Complementar:** Para princípios de UX, tokens detalhados, estrutura de página e exemplos de código, consulte `GUIA-VISUAL-PMZ.md` nesta mesma pasta. Este documento (SKILL.md) foca em regras técnicas categorizadas; o GUIA-VISUAL-PMZ.md foca em princípios e padrões visuais.

---

## Princípios de UX (do GUIA-VISUAL-PMZ.md)

Estes princípios devem guiar TODAS as decisões de design:

1. **O dado é o herói** — Layout, cor e tipografia existem para tornar números legíveis e comparáveis, nunca para decorar
2. **Uma tela = um objetivo** — Cabeçalho diz o que é e o que fazer; o resto sustenta isso
3. **Comparação em vez de valor solto** — Sempre mostrar baseline + delta % com cor semântica
4. **Cor com significado** — Verde=positivo, vermelho=negativo, âmbar=atenção, azul=info
5. **Densidade para uso profissional** — Tabelas compactas, KPIs generosos
6. **Sem tela vazia e sem tela sufocada** — Respiro consistente
7. **Estado sempre visível** — Badges coloridos, não texto simples

---

## Integração no Pipeline Lighthouse

O agente **frontend-builder** deve consultar este guia nos seguintes momentos:

| Step | Momento | O que usar neste guia |
|------|----------|----------------------|
| **1.5 — Design System** | Antes de gerar `docs/design-system.yaml` | §4 Seleção de Estilo, §6 Tipografia & Cor, `design-system.yaml` existente como fonte de verdade |
| **6 — Screen Definition** | Ao definir `components[]` de cada tela | §10 Charts & Data (tipo de gráfico), §5 Layout & Dashboard (hierarquia), §9 Navegação |
| **7 — Frontend Pages** | Durante geração dos 4 arquivos por página | §8 Forms & Feedback (formulários DBC), §7 Loading & Transições, §1 Acessibilidade |
| **8 — App + Sidebar** | Ao montar sidebar e guard_routes | §9 Padrões de Navegação (Dash routing, dcc.Location) |
| **Pré-entrega** | Antes de reportar `STATUS: success` | Checklist Pré-Entrega (seção final) |

---

## Quando Aplicar

### Obrigatório

- Definindo componentes de tela (`components[]` no `screens_definition.yaml`)
- Escolhendo tipo de gráfico Plotly para um conjunto de dados
- Gerando páginas com formulários, filtros ou tabelas AG Grid
- Revisando UI para consistência visual ou problemas de usabilidade
- Implementando navegação (sidebar, login, guard_routes)

### Recomendado

- UI parece "não profissional" sem causa clara
- Feedback do cliente sobre usabilidade
- Otimização de qualidade pré-apresentação

### Pular

- Lógica de backend puro (FastAPI, SQLAlchemy)
- Design do modelo de dados ou SQL
- Configuração de infraestrutura

---

## Bibliotecas de Componentes Reutilizáveis

**REGRA CRÍTICA:** NUNCA recriar componentes que já existem nas bibliotecas. SEMPRE importar e usar.

### Disponíveis em `.claude/templates/`:

**`components-library.py`** → copiar para `frontend/components/ui_components.py`
- `app_shell(active_key, icon_key, title, subtitle, content, actions)` — Shell completo
- `kpi_card(label, atual, simulado, delta_pct, better)` — KPI com comparação + delta
- `kpi_row(cards)` — Row de KPI cards
- `data_table(df, id, numeric_cols, status_col, page_size)` — AG Grid estilizada
- `page_header(icon_key, title, subtitle, actions)` — Cabeçalho padrão
- `card(title, body, right)` — Card genérico
- `button(label, primary, icon_key)` — Botão padrão
- `filter_card(filters, button_id)` — Card de filtros compacto
- Helpers: `format_currency()`, `format_percent()`, `format_number()`, `status_badge_style()`

**`charts-library.py`** → copiar para `frontend/components/charts.py`
- `bar_ranking()`, `bar_vertical()`, `variation_bars()` — Barras
- `donut()`, `pie()` — Pizza/rosca
- `line_chart()`, `multi_line_chart()`, `area_chart()` — Linhas
- `scatter_chart()`, `histogram()` — Outros
- Helper: `set_primary_color(color)`, `get_empty_state_message()`

### Exemplo de uso:

```python
from frontend.components.ui_components import app_shell, kpi_card, kpi_row, data_table
from frontend.components.charts import bar_ranking

def layout():
    kpis = [
        kpi_card("Faturamento", "R$ 1.899.674", "R$ 1.969.961", +3.7, "up"),
        kpi_card("Custo", "R$ 1.181.668", "R$ 1.335.509", +13.0, "down"),
    ]
    
    return app_shell(
        active_key="dashboard",
        icon_key="speedometer2",
        title="Dashboard",
        subtitle="Visão executiva",
        content=[kpi_row(kpis), dcc.Graph(figure=bar_ranking([...], [...]))]
    )
```

---

## Categorias de Regras por Prioridade

| Prioridade | Categoria | Impacto | Verificações Obrigatórias | Anti-Padrões |
|-----------|----------|---------|--------------------------|--------------|
| 1 | Acessibilidade | CRÍTICO | Contraste 4.5:1, Labels em inputs, Tab order | Remover focus rings, inputs sem label |
| 2 | Interação Web | CRÍTICO | Feedback de click, Loading em callbacks async, Cursor pointer | Elementos clicáveis sem feedback visual, Botão ativo durante loading |
| 3 | Performance Dash | ALTO | n_clicks/State sem trigger desnecessário, Callbacks mínimos, Dados via CSV | Callbacks em cadeia longa, Layout em callback |
| 4 | Seleção de Estilo | ALTO | Consistência DBC, design-system.yaml como fonte | Inline styles para cores, misturar temas |
| 5 | Layout & Dashboard | ALTO | Hierarquia visual, Sidebar 240px, page-wrapper raiz | dbc.Container como raiz, Layout sem hierarquia |
| 6 | Tipografia & Cor | MÉDIO | Tokens semânticos, Contraste legível, Scale consistente | Hex raw em componentes, Texto < 12px |
| 7 | Loading & Transições | MÉDIO | dcc.Loading em callbacks > 300ms, Empty states, Toast 3-5s | Spinner eterno, Ausência de feedback de estado |
| 8 | Forms & Feedback | MÉDIO | Labels visíveis, Erro próximo ao campo, Confirmação destrutiva | Placeholder como único label, Erro genérico |
| 9 | Navegação | ALTO | Rotas únicas, Back consistente, Guard de autenticação | Rota duplicada, Nav sem estado ativo |
| 10 | Gráficos & Dados | ALTO | Tipo correto para dado, Tooltip, Legenda, Estado vazio | Gráfico de pizza com >5 categorias |

---

## Quick Reference

### 1. Acessibilidade (CRÍTICO)

- `color-contrast` — Mínimo 4.5:1 para texto normal; use tokens do `design-system.yaml` (heading `#1e293b` sobre branco = ✓)
- `focus-states` — Não remover `outline` padrão do Bootstrap; inputs DBC já têm focus ring
- `form-labels` — Todo `dcc.Input`, `dcc.Dropdown`, `dcc.DatePickerRange` deve ter um `html.Label` ou `dbc.Label` associado
- `aria-labels` — Botões só com ícone (`html.I`) precisam de `title=` ou texto oculto: `dbc.Button([html.I(className="bi bi-download"), " Exportar"])`
- `keyboard-nav` — Tab order segue a ordem de declaração Python; declare componentes na ordem lógica
- `heading-hierarchy` — Use `html.H4` para título de página, `html.H5` para seções, nunca pular nível
- `color-not-only` — Status nunca só por cor: use `dbc.Badge` com texto ("Ativo", "Pendente") + cor semântica
- `error-clarity` — Mensagens de erro explicam causa + correção; não apenas "Erro ao salvar"

### 2. Interação Web (CRÍTICO)

- `click-feedback` — `dbc.Button` deve mostrar spinner ou mudar texto durante operação async: `[dbc.Spinner(size="sm"), " Salvando..."]`
- `loading-states` — Envolva outputs de callbacks lentos (> 300ms) em `dcc.Loading(type="circle")`
- `disabled-during-load` — `disabled=True` no botão enquanto callback está rodando (via `prevent_initial_call` + Output disabled)
- `cursor-pointer` — Elementos clicáveis que não são `dbc.Button` precisam de `style={"cursor": "pointer"}`
- `hover-not-only` — Ações primárias devem ser clicáveis; não dependa de hover para revelar controles principais
- `error-feedback` — Erros de formulário próximos ao campo, em vermelho semântico (`color="danger"`)
- `empty-state-action` — Estado vazio de grid deve ter mensagem + ação sugerida; não apenas grid vazio

### 3. Performance Dash (ALTO)

- `minimal-callbacks` — Prefira um callback com múltiplos Outputs a vários callbacks com saída individual no mesmo trigger
- `prevent-initial-call` — Use `prevent_initial_call=True` apenas quando necessário; callbacks de filtro precisam rodar na carga (`False`)
- `data-via-csv` — Páginas lêem `mock_data/<entidade>.csv` via `pd.read_csv()`; nunca consultar banco no frontend
- `no-layout-in-callback` — Layouts são funções puras Python; não regenere componentes inteiros em callbacks (exceto modais condicionais)
- `state-not-input` — Use `State` para valores de filtro lidos só no clique; `Input` apenas para o botão de filtrar
- `debounce-input` — `dcc.Input(debounce=True)` para inputs de busca; evita callback a cada keystroke
- `pagination-ag-grid` — AG Grid com `paginationPageSize=20`; nunca carregue todos os dados numa grid sem paginação
- `mock-data-filter` — Filtragem acontece no `_queries.py` antes de passar o DataFrame para o componente; não passe DataFrames inteiros sem filtrar

### 4. Seleção de Estilo (ALTO)

- `design-system-source` — O `design-system.yaml` em `.claude/` é a fonte de verdade; nunca sobrescrever valores de cor, spacing ou componentes definidos lá
- `dbc-theme` — Use `dbc.themes.BOOTSTRAP` como tema base; não importar outros temas Bootstrap
- `consistency` — Mesmo padrão de card, filtro, grid e KPI em todas as páginas; copie o padrão do `design-system.yaml`
- `no-inline-colors` — Nunca `style={"color": "#1045C8"}`; use `className="text-primary"` ou tokens do design system
- `semantic-colors` — Sempre use cores semânticas: `color="primary"`, `color="success"`, `color="danger"`; não valores hex
- `icon-set` — Use exclusivamente Bootstrap Icons (`bi bi-*`); não misturar com FontAwesome ou emojis como ícone estrutural
- `card-pattern` — Todo card: `dbc.Card(className="shadow-sm border-0 mb-3")`; CardHeader: `className="bg-white border-bottom fw-semibold"`
- `kpi-pattern` — KPI cards com borda lateral: `className="shadow-sm border-0 border-start border-4 border-{color} mb-3 h-100"`

### 5. Layout & Dashboard (ALTO)

- `use-app-shell` — **OBRIGATÓRIO:** Toda página deve usar `app_shell(active_key, icon_key, title, subtitle, content, actions)` da biblioteca. NUNCA montar estrutura manualmente.
- `page-wrapper-root` — Raiz de toda página (quando não usar app_shell): `html.Div(className="page-wrapper px-4 py-3", style={"background": "#f8fafc", "minHeight": "100vh"})`
- `no-container-root` — **NUNCA** usar `dbc.Container` como raiz do `layout()`
- `sidebar-fixed` — Sidebar é fixa em 240px; `CONTENT_STYLE = {"marginLeft": "240px"}`; login usa `CONTENT_FULL_STYLE = {"marginLeft": "0"}`
- `visual-hierarchy` — Ordem vertical de seções: Header (H4 + botões) → Filtros (card compacto) → KPIs (Row) → Grid/Chart (card principal)
- `filter-at-top` — Filtros sempre usando `filter_card(filters, button_id)` da biblioteca
- `kpi-row` — KPIs usando `kpi_row([kpi_card(...), kpi_card(...)])` da biblioteca
- `grid-in-card` — AG Grid sempre usando `data_table(df, id, numeric_cols, status_col)` da biblioteca dentro de `card(title, body)`
- `column-sizing` — Filtros: `dbc.Col(md=2)` a `md=4` conforme o tipo; botão filtrar: `dbc.Col(md=1)` com `className="d-grid"`
- `z-index-layers` — Modais (`z=1050`), Sidebar (`z=100`), conteúdo (`z=0`); nunca conflitar camadas

### 6. Tipografia & Cor (MÉDIO)

- `font-family` — `system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif` do `design-system.yaml`; não importar Google Fonts adicionais
- `heading-sizes` — H4 para título de página (`1.25rem` / `fw-semibold`), H5 para seções, `small` para labels de filtro
- `body-text` — Cor `#374151` (body_text do design system); `font-size: 0.875rem` para conteúdo de card
- `muted-text` — `className="text-muted small"` para metadados e labels de filtro; nunca usar `color="#6b7280"` inline
- `contrast-heading` — `#1e293b` sobre `#ffffff` = 16:1 ✓ | `#374151` sobre `#f8fafc` = 10:1 ✓
- `semantic-badge-text` — Sempre inclua texto no badge de status; `dbc.Badge("Ativo", color="success")`
- `weight-hierarchy` — Headers `fw-semibold` (600), corpo `fw-normal` (400), labels `fw-medium` (500)
- `no-raw-hex` — Nunca usar hex diretamente em `className` ou `style`; usar tokens do `design-system.yaml`

### 7. Loading & Transições de Estado (MÉDIO)

- `dcc-loading-wrapper` — Envolva grid, charts e conteúdo dinâmico em `dcc.Loading(type="circle", color="#1045C8")`
- `loading-threshold` — Callbacks que podem demorar > 300ms precisam de loading state; filtros simples em CSV local não precisam
- `button-loading-text` — Durante loading: `dbc.Button([dbc.Spinner(size="sm", className="me-2"), "Carregando..."], disabled=True)`
- `empty-state` — Grid sem dados: `dbc.Alert("Nenhum registro encontrado. Ajuste os filtros.", color="info")` dentro do card
- `toast-duration` — `dbc.Toast` com `duration=4000` (4s); sempre com `is_open=True` após ação
- `toast-placement` — `dbc.Toast` posicionado em `position="top-right"` ou `position="bottom-right"`; nunca no centro
- `alert-dismissible` — `dbc.Alert(dismissable=True)` para mensagens não críticas; `is_open` controlado por callback
- `modal-confirm` — Ações destrutivas (deletar, limpar) sempre com `dbc.Modal` de confirmação antes de executar

### 8. Forms & Feedback (MÉDIO)

- `visible-labels` — Todo campo de formulário tem `dbc.Label` acima do input; nunca usar placeholder como único identificador
- `error-placement` — Erro abaixo do campo em `dbc.FormText(color="danger")` ou `dbc.Alert(color="danger")`
- `required-indicator` — Campos obrigatórios com `" *"` no label ou `html.Span("*", className="text-danger")`
- `submit-feedback` — Botão de envio: loading → sucesso/erro via `dbc.Alert` ou `dbc.Toast`
- `filter-button-full` — Botão "Filtrar" usa `className="w-100"` dentro de `dbc.Col(className="d-grid")`
- `date-range-clear` — `dcc.DatePickerRange` com `clearable=True` e `placeholder` explicativo
- `dropdown-search` — `dcc.Dropdown` com `searchable=True` quando lista > 10 itens
- `confirmation-modal` — Ações irreversíveis sempre com modal de confirmação; não confiar em `n_clicks` diretamente
- `empty-export` — Botão exportar desabilitado quando grid está vazio; valide no callback com `if df.empty: no_update`
- `inline-validation` — Valide após submit, não a cada keystroke; mostre todos os erros de uma vez

### 9. Navegação Dash (ALTO)

- `unique-routes` — Toda rota em `dash.register_page(__name__, path="/<slug>")` deve ser única no projeto; valide em `screens_definition.yaml`
- `dcc-location` — Use `dcc.Location(id="url", refresh=False)` no `app.py`; único ponto de controle de URL
- `guard-routes` — `guard_routes` callback em `app.py` redireciona para `/login` se sem auth, para `/` se autenticado tentando acessar `/login`
- `sidebar-active` — `dbc.NavLink(active="exact")` para highlight automático de rota ativa
- `nav-icon-label` — Cada item de sidebar tem ícone Bootstrap Icons + label textual; nunca só ícone
- `login-fullscreen` — Página de login sem sidebar; usa `CONTENT_FULL_STYLE` com `marginLeft: 0`
- `page-title-register` — `dash.register_page(__name__, path, title, name)` — `title` aparece na aba do browser
- `no-output-url-login` — `Output("url", "pathname")` existe APENAS no `guard_routes`; callbacks de login NUNCA escrevem nesta Output
- `sidebar-footer` — Footer da sidebar: "Desenvolvido por / Quantiz Pricing Solution" fixo no bottom
- `nav-state-active` — Item de navegação da rota atual deve estar visualmente destacado (dbc `active="exact"` já trata)

### 10. Gráficos & Dados com Plotly (ALTO)

**Tipo de gráfico → dado:**

| Dado | Gráfico Plotly | Função |
|------|---------------|--------|
| Tendência no tempo | Linha | `px.line` |
| Comparação entre categorias | Barra vertical | `px.bar` |
| Ranking / top-N | Barra horizontal | `px.bar(orientation="h")` |
| Proporção (≤5 categorias) | Pizza/Donut | `px.pie(hole=0.4)` |
| Proporção (>5 categorias) | Barra empilhada | `px.bar(barmode="stack")` |
| Distribuição | Histograma | `px.histogram` |
| Relação entre duas variáveis | Dispersão | `px.scatter` |
| KPI único | `dbc.Card` com número grande | — |
| Funil de processo | Funil | `px.funnel` |

- `plotly-template` — Sempre `template="plotly_white"` e `paper_bgcolor="rgba(0,0,0,0)"`, `plot_bgcolor="rgba(0,0,0,0)"`
- `plotly-height` — Default `height=300`; gráficos de destaque podem usar `height=400`
- `plotly-margin` — `margin=dict(l=20, r=20, t=40, b=20)` padrão; título curto no `title=`
- `plotly-font` — `font=dict(family="system-ui, sans-serif", size=12, color="#374151")`
- `plotly-config` — `config={"displayModeBar": False}` na maioria das telas; `True` apenas em relatórios analíticos
- `chart-legend` — Sempre mostrar legenda para gráficos com múltiplas séries; `legend=dict(orientation="h", yanchor="bottom", y=1.02)`
- `chart-tooltip` — Plotly já fornece tooltip por padrão; garanta `hover_data=` com campos relevantes
- `empty-chart-state` — Quando DataFrame está vazio, não renderize o gráfico; retorne `dbc.Alert("Sem dados para o período.", color="info")`
- `chart-color-palette` — Use `color_discrete_sequence=["#1045C8", "#10b981", "#f59e0b", "#ef4444", "#06b6d4"]` (design system)
- `no-pie-overuse` — Evite pizza com > 5 categorias; use barra horizontal para clareza
- `ag-grid-column-types` — Colunas numéricas: `type="numericColumn"`, `valueFormatter: {"function": "d3.format(',.2f')(params.value)"}`
- `ag-grid-date-format` — Datas: `valueFormatter: {"function": "params.value ? new Date(params.value).toLocaleDateString('pt-BR') : ''"}`
- `ag-grid-status-badge` — Coluna de status: `cellRenderer: "agTextCellRenderer"` com CSS do Bootstrap Badge via `cellClass`
- `ag-grid-export` — Botão exportar CSV usando `grid.exportDataAsCsv()` via `rowData` + `pd.DataFrame.to_csv()`

---

## Referência do Stack Dash

### Componentes e Equivalentes

| Necessidade | Componente Correto | Proibido |
|-------------|-------------------|---------|
| Raiz da página | `html.Div(className="page-wrapper")` | `dbc.Container` como raiz |
| Card de conteúdo | `dbc.Card + dbc.CardBody` | `html.Div` com border manual |
| Tabela de dados | `dash_ag_grid.AgGrid` | `dbc.Table`, `html.Table`, `DataTable` |
| Gráfico | `plotly.express.*` ou `go.Figure` | `matplotlib`, `seaborn`, `bokeh` |
| Input texto | `dbc.Input` | `html.Input` raw |
| Dropdown | `dcc.Dropdown` | `dbc.Select` para > 5 opções |
| Data | `dcc.DatePickerSingle` / `dcc.DatePickerRange` | `html.Input(type="date")` |
| Modal | `dbc.Modal` | `html.Dialog` |
| Toast | `dbc.Toast` | `dbc.Alert` flutuante manual |
| Badge | `dbc.Badge` | `html.Span` com style manual |
| Loading | `dcc.Loading` | Spinner CSS manual |
| Alerta | `dbc.Alert` | `html.Div` com style de cor |
| Tabs | `dbc.Tabs + dbc.Tab` | `dcc.Tabs` (menos estilizado) |
| Ícone | `html.I(className="bi bi-*")` | Emojis como ícone estrutural |

### Padrão de IDs

```
<page>-grid               → AG Grid principal
<page>-btn-filtrar        → Botão de aplicar filtros
<page>-filtro-<campo>     → Inputs de filtro individuais
<page>-chart-<tipo>       → Cada gráfico (bar, line, pie)
<page>-kpis-row           → Row dos KPI cards
<page>-btn-<acao>         → Outros botões de ação
<page>-modal-<nome>       → Modais
<page>-toast-<nome>       → Toasts/alertas
```

### Estrutura de Callback Padrão

```python
@callback(
    Output("<page>-grid", "rowData"),
    Output("<page>-kpis-row", "children"),
    Input("<page>-btn-filtrar", "n_clicks"),
    State("<page>-filtro-campo1", "value"),
    State("<page>-filtro-campo2", "value"),
    prevent_initial_call=False,
)
def filtrar(n_clicks, campo1, campo2):
    df = carregar_entidade(campo1=campo1, campo2=campo2)
    return df.to_dict("records"), build_kpis(df)
```

---

## Checklist Pré-Entrega

Execute antes de reportar `STATUS: success`.

### Estrutura e Layout
- [ ] Toda página usa `html.Div(className="page-wrapper px-4 py-3", style={"background": "#f8fafc", "minHeight": "100vh"})` como raiz
- [ ] Nenhuma página usa `dbc.Container` como raiz de `layout()`
- [ ] Hierarquia de seções: Header → Filtros → KPIs → Grid/Chart
- [ ] Sidebar com `width: 240px` e `CONTENT_STYLE` com `marginLeft: 240px`
- [ ] Login com `CONTENT_FULL_STYLE` sem sidebar

### Estilo e Tokens
- [ ] Nenhuma cor hex inline em componentes (usar tokens do `design-system.yaml` ou `className`)
- [ ] Todos os cards com `className="shadow-sm border-0 mb-3"`
- [ ] KPI cards com `border-start border-4 border-{color}`
- [ ] Ícones exclusivamente Bootstrap Icons (`bi bi-*`); sem emoji como ícone estrutural
- [ ] Badges de status com texto + cor semântica

### Interação e Feedback
- [ ] Callbacks lentos (> 300ms) envolvidos em `dcc.Loading`
- [ ] Botão "Filtrar" desabilitado e com spinner durante execução
- [ ] Estado vazio de grid com `dbc.Alert` explicativo (não grid em branco)
- [ ] Ações destrutivas com `dbc.Modal` de confirmação
- [ ] Toasts de sucesso/erro após ações de formulário

### Formulários
- [ ] Todo `dcc.Input` / `dcc.Dropdown` / `dcc.DatePickerRange` tem `dbc.Label` visível acima
- [ ] Campos obrigatórios sinalizados com `*` no label
- [ ] Erros exibidos abaixo do campo em vermelho semântico
- [ ] Botão de submit mostra loading state

### Navegação e Rotas
- [ ] Sem rotas duplicadas em `screens_definition.yaml`
- [ ] `guard_routes` implementado em `app.py` com redirecionamento correto
- [ ] Nenhum callback de login escreve em `Output("url", "pathname")`
- [ ] Todos os `dbc.NavLink` com `active="exact"`
- [ ] Footer da sidebar com "Desenvolvido por / Quantiz Pricing Solution"

### Gráficos Plotly
- [ ] Todo gráfico com `template="plotly_white"` e fundos transparentes
- [ ] Tipo de gráfico adequado ao dado (tabela §10 acima)
- [ ] Gráfico de pizza com no máximo 5 categorias
- [ ] Estado vazio retorna `dbc.Alert`, não figura vazia
- [ ] Paleta de cores alinhada ao design system

### AG Grid
- [ ] Tema `ag-theme-alpine` em todas as grids
- [ ] `floatingFilter=True`, `suppressMenu=True`, `rowHeight=44`
- [ ] Paginação com `paginationPageSize=20`
- [ ] Colunas numéricas com `valueFormatter` formatado (`d3.format`)
- [ ] Datas com `valueFormatter` em `pt-BR`

### Acessibilidade
- [ ] Contraste de texto ≥ 4.5:1 (use tokens do design system, já validados)
- [ ] Tab order segue ordem lógica de declaração
- [ ] Botões com apenas ícone têm `title=` ou texto auxiliar
- [ ] Status nunca comunicado só por cor (usar Badge com texto)

### Python
- [ ] Tipagem Python em todas as funções (`def carregar_entidade(campo: str | None = None) -> pd.DataFrame:`)
- [ ] Cada arquivo passa `python -m py_compile <arquivo>`
- [ ] Nenhum import de biblioteca fora do stack (sem `matplotlib`, `flask`, `streamlit`, etc.)

### Uso de Bibliotecas (CRÍTICO)
- [ ] Todas as páginas usam `app_shell()` da biblioteca (não montam estrutura manualmente)
- [ ] KPIs usam `kpi_card()` com comparação atual×simulado (não valores soltos)
- [ ] Tabelas usam `data_table()` da biblioteca (não AG Grid manual)
- [ ] Gráficos usam helpers de `charts.py` (não Plotly manual)
- [ ] Filtros usam `filter_card()` da biblioteca
- [ ] Nenhum componente recriado que já existe na biblioteca

---

## Anti-Padrões Críticos (NUNCA FAZER)

❌ **Valor solto sem comparação** — sempre usar `kpi_card(label, atual, simulado, delta_pct, better)`  
❌ **Estrutura manual de página** — sempre usar `app_shell()`  
❌ **Hex/style inline** — usar tokens e className  
❌ **Status como texto** — usar badge colorido  
❌ **Gráfico monocromático** — usar paleta categórica  
❌ **Coluna truncada** — dar largura adequada ou scroll  
❌ **dbc.Container como raiz** — usar html.Div com page-wrapper  
❌ **Números sem mono tabular** — sempre usar font mono para números  
❌ **Filtro sem botão** — sempre ter botão "Filtrar" explícito  
❌ **Grid sem paginação** — sempre paginar com 20 itens  
❌ **Callback sem loading** — envolver em dcc.Loading se > 300ms  
❌ **Recriar componente da biblioteca** — sempre importar e usar
