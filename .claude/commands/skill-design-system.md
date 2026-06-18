# Skill — Design System Generator

Leia `docs/requirements.yaml` e gere `docs/design-system.yaml` com todos os tokens de design, configurações de componentes e convenções visuais do projeto.

## Quando Usar

- Após a Etapa 1 (Requirements) e antes da Etapa 7 (Frontend Pages)
- Quando precisar padronizar o visual de um projeto existente
- Para customizar temas, cores e espaçamentos

## Argumento opcional

`$ARGUMENTS` — tema de cor base (ex.: `blue`, `purple`, `green`). Padrão: `blue`.

---

## Instruções

1. Leia `docs/requirements.yaml` para obter `project.name` e contexto do domínio.
2. Leia `.build/project.json` para obter `name` e `name_slug`.
3. Gere `docs/design-system.yaml` com a estrutura completa abaixo.
4. Se o arquivo já existir, aplique patch incremental apenas nas seções modificadas.

---

## Estrutura de Saída

```yaml
# docs/design-system.yaml

meta:
  project: string          # nome do projeto
  version: "1.0.0"
  generated_at: datetime

colors:
  # Paleta primária (sidebar, botões, destaques)
  primary:
    50:  "#eff6ff"
    100: "#dbeafe"
    200: "#bfdbfe"
    300: "#93c5fd"
    400: "#60a5fa"
    500: "#1045C8"   # padrão — usar em botões, links, destaques
    600: "#2563eb"
    700: "#1d4ed8"
    800: "#1e40af"
    900: "#1e3a8a"

  # Cores neutras (textos, fundos, bordas)
  slate:
    50:  "#f8fafc"    # fundo de páginas
    100: "#f1f5f9"
    200: "#e2e8f0"    # bordas de cards
    300: "#cbd5e1"    # texto sidebar
    400: "#94a3b8"
    500: "#64748b"
    600: "#475569"
    700: "#334155"    # sidebar hover
    800: "#1e293b"    # sidebar background
    900: "#0f172a"

  # Semânticas
  success: "#22c55e"
  warning: "#f59e0b"
  danger:  "#ef4444"
  info:    "#06b6d4"
  muted:   "#6b7280"

  # Aliases de uso direto
  sidebar_bg:        "#1e293b"
  sidebar_hover:     "#334155"
  sidebar_text:      "#cbd5e1"
  sidebar_highlight: "#1045C8"
  sidebar_border:    "#334155"
  page_bg:           "#f8fafc"
  card_bg:           "#ffffff"
  card_border:       "#e2e8f0"
  heading_color:     "#1e293b"
  body_text:         "#374151"
  muted_text:        "#6b7280"

typography:
  font_family: "system-ui, -apple-system, 'Segoe UI', sans-serif"
  font_size_base: "14px"
  font_size_sm:   "12px"
  font_size_xs:   "11px"
  font_size_lg:   "16px"
  font_size_xl:   "20px"
  font_weight_normal:   400
  font_weight_semibold: 600
  font_weight_bold:     700
  line_height:    1.5

spacing:
  xs:  "4px"
  sm:  "8px"
  md:  "12px"
  lg:  "16px"
  xl:  "24px"
  xxl: "32px"
  page_padding_x: "24px"   # px-4 Bootstrap
  page_padding_y: "12px"   # py-3 Bootstrap
  card_padding:   "16px"

borders:
  radius_sm:  "4px"
  radius_md:  "8px"
  radius_lg:  "12px"
  border_color: "#e2e8f0"
  border_width: "1px"

shadows:
  sm:   "0 1px 2px 0 rgb(0 0 0 / 0.05)"
  md:   "0 4px 6px -1px rgb(0 0 0 / 0.1)"
  lg:   "0 10px 15px -3px rgb(0 0 0 / 0.1)"
  card: "0 1px 3px 0 rgb(0 0 0 / 0.1)"   # shadow-sm Bootstrap

layout:
  sidebar_width:       "240px"
  sidebar_collapsed:   "64px"
  content_margin_left: "240px"
  header_height:       "60px"
  page_max_width:      "100%"

components:
  card:
    class_name:        "shadow-sm border-0 mb-3"
    header_class:      "bg-white border-bottom fw-semibold"
    body_padding:      "16px"

  kpi_card:
    class_prefix:      "border-start border-4 border-"
    available_colors:  ["primary", "success", "warning", "danger", "info"]
    body_class:        "py-3"

  filter_panel:
    class_name:        "shadow-sm border-0 mb-3"
    body_class:        "py-2"
    row_class:         "g-2 align-items-end"

  button:
    primary_color:     "primary"
    class_name:        ""
    size:              "sm"

  badge:
    status_map:
      ativo:     "success"
      inativo:   "secondary"
      pendente:  "warning"
      aprovado:  "success"
      reprovado: "danger"
      cancelado: "danger"
      concluido: "success"
      aberto:    "info"

ag_grid:
  theme:               "ag-theme-alpine"
  row_height:          44
  header_height:       44
  pagination_size:     20
  pagination_options:  [10, 20, 50, 100]
  floating_filter:     true
  suppress_menu:       true
  animate_rows:        true
  default_col_def:
    resizable: true
    sortable:  true
    filter:    true
    floatingFilter: true
    suppressMenu:   true

plotly:
  template:            "plotly_white"
  paper_bgcolor:       "rgba(0,0,0,0)"
  plot_bgcolor:        "rgba(0,0,0,0)"
  default_height:      300
  chart_height:        350
  font_family:         "system-ui, sans-serif"
  font_size:           12
  font_color:          "#374151"
  margin:
    l: 20
    r: 20
    t: 40
    b: 20
  color_sequence:      ["#1045C8", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4", "#8b5cf6"]

login_page:
  bg_gradient_start:   "#1e293b"
  bg_gradient_end:     "#0f172a"
  card_width:          "400px"
  card_border_radius:  "12px"

id_conventions:
  grid:            "<page>-grid"
  btn_filter:      "<page>-btn-filtrar"
  btn_export:      "<page>-btn-export"
  btn_new:         "<page>-btn-novo"
  filter_dropdown: "<page>-filtro-<field>"
  filter_period:   "<page>-filtro-periodo"
  chart:           "<page>-chart-<type>"
  kpi_row:         "<page>-kpis-row"
  modal:           "<page>-modal-<action>"
  form_field:      "<page>-form-<field>"

branding:
  footer_line1:    "Desenvolvido por"
  footer_line2:    "Quantiz Pricing Solution"
  footer_color1:   "#475569"    # slate-600 — texto auxiliar
  footer_color2:   "#64748b"    # slate-500 — nome da empresa
  footer_size:     "0.68rem"
  footer_weight2:  500          # ligeiramente mais pesado que o texto auxiliar
  footer_border:   "#334155"    # slate-700 — separador sutil
  sidebar_logo_color: "#1045C8" # cor do ícone/bullet do logo
```

---

## Restrições

- NÃO gere código Python ou JavaScript — apenas o YAML.
- Se `$ARGUMENTS` especificar uma cor base diferente de `blue`, ajuste toda a paleta `primary` e os aliases de cor correspondentes.
- `color_sequence` do Plotly deve usar a cor `primary.500` como primeiro elemento.
- Contexto máximo: **4.000 tokens** de saída.

## Pós-processamento

1. Validar que YAML é sintaxicamente correto
2. Verificar que todos os `color_sequence` são hex válidos
3. Criar checkpoint `step_design_system.json`
4. Registrar em `.build/build.log`

## Modo de Uso

```
/skill-design-system
/skill-design-system purple
```
