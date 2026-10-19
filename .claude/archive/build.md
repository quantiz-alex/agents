# /build — Pipeline Orquestrado

Execute o pipeline completo de geração do projeto, passo a passo, de forma automática.

Assistente local faz parte do build: após screens/workflows/business_logic e antes de concluir frontend, executar `skill-pricing-assistant.md` (default habilitado). Gerar catálogo/handlers/painel/callbacks específicos do roadmap e integrar no shell. Cenários compartilhados seguem `skill-demo-scenario.md`. Não exige comando extra ou API de IA. Retomada verifica hashes/artefatos do assistente, não apenas app.py existente.

## Argumento opcional

`$ARGUMENTS` — etapa inicial (ex.: `skill03` para retomar a partir do SQL). Se vazio, começa do início ou retoma de onde parou.

---

## Protocolo de Economia de Tokens e Extended Thinking

CRÍTICO — siga rigorosamente:

1. **Extended Thinking**: Antes de cada etapa, use `<thinking>` para:
   - Analisar dependências entre entidades/componentes
   - Calcular ordem de geração (topological sort para FKs)
   - Estimar tokens necessários para a saída
   - Planejar chunking se necessário (>8.000 tokens)
   - Identificar oportunidades de paralelização

2. Leia APENAS o arquivo de entrada da etapa atual.
3. Gere a saída de forma compacta (sem comentários desnecessários, sem exemplos extras).
4. Após escrever cada arquivo de saída, **descarte mentalmente** o conteúdo do arquivo de entrada — não o reutilize na próxima etapa.
5. Nunca regenere um arquivo que já existe e está correto — pule a etapa.
6. Ao final de cada etapa, imprima apenas: `✓ [etapa] → [arquivo gerado]` e avance imediatamente.

### Limite de Tokens Aumentado
- Contexto máximo por skill: **8.000 tokens** (anteriormente 2.000)
- Se uma entidade/página exceder 8.000 tokens, dividir em chunks com continuação automática
- Usar prompt caching para YAMLs de configuração reutilizados

---

## Estado do Build e Sistema de Checkpoints

Antes de iniciar, verifique a existência dos arquivos abaixo para determinar quais etapas já estão concluídas:

```
.build/project.json          → etapa 0 concluída (projeto validado, project.name extraído)
docs/requirements.yaml       → etapa 1 concluída
docs/design-system.yaml      → etapa 1.5 concluída
docs/data_model.yaml         → etapa 2 concluída
backend/config.py            → etapa 2.5 concluída
docs/api_contracts.yaml      → etapa 2.6 concluída
docs/business_logic.yaml     → etapa 2.7 concluída
database/schema.sql          → etapa 3 concluída
mock_data/                   → etapa 4 INCOMPLETA — verificar se CADA entidade de data_model.yaml tem AMBOS .csv E .json em mock_data/. Se faltar qualquer um dos dois para qualquer entidade, retomar a geração apenas das entidades faltantes.
database/seed.sql            → etapa 5 concluída
docs/screens_definition.yaml → etapa 6 concluída
frontend/app.py              → etapas 7-8 concluídas
backend/main.py              → etapa 9 INCOMPLETA — verificar se CADA entidade de data_model.yaml tem os 5 arquivos (model, schema, repository, service, route). Se qualquer arquivo faltar, retomar apenas as entidades incompletas.
backend/auth.py              → etapa 9.5 concluída
requirements.txt             → etapa 10 concluída (verificar se README.md também existe)
tests/backend/               → etapa 11 INCOMPLETA — verificar se CADA entidade de data_model.yaml tem test_<entidade>.py em tests/backend/. Se faltar qualquer arquivo, rodar skill12 apenas para as entidades faltantes.
tests/frontend/cypress.config.js → etapa 12 concluída (verificar se existe um .cy.js por página em screens_definition.yaml)
```

Pule as etapas já concluídas. Inicie na primeira etapa pendente.

### Sistema de Checkpoints

Após cada etapa bem-sucedida:

1. **Criar checkpoint**: Salvar hash SHA256 dos arquivos gerados em `.build/checkpoints/step{N}.json`
2. **Validar**: Executar `/skill00-validator step{N}` automaticamente
3. **Registrar**: Adicionar entrada em `.build/build.log` com timestamp e status

```json
// .build/checkpoints/step2.json
{
  "step": 2,
  "timestamp": "2024-06-03T15:30:00Z",
  "files": {
    "docs/data_model.yaml": "a3f5b9c..."
  },
  "validation": "passed",
  "duration_seconds": 12
}
```

### Rollback

Para reverter para uma etapa anterior:
```
/build --rollback step-3
```

Isso restaura os arquivos do checkpoint da etapa 3 e reinicia a partir da etapa 4.

---

## Etapa 0 — Validação Pré-Build

**Input:** `roadmap.md`
**Output:** `validation_reports/step0_prebuild.yaml`, `.build/project.json`

**Ações:**
1. Executar `/skill-roadmap-template` para validar `roadmap.md` e extrair `project.name`
2. Se `roadmap.md` não existir → gerar template preenchível e **PARAR** aguardando preenchimento
3. Se `roadmap.md` inválido → exibir erros do validator e **PARAR**
4. Ler `.build/project.json` — confirmar que `name`, `name_slug`, `name_class` foram gerados
5. Criar estrutura de diretórios se não existir:
   ```
   docs/
   database/
   mock_data/
   frontend/pages/
   frontend/components/
   backend/models/
   backend/schemas/
   backend/repositories/
   backend/services/
   backend/api/routes/
   tests/backend/
   tests/frontend/
   tests/integration/
   validation_reports/
   .build/checkpoints/
   ```
6. Executar `/skill00-validator step0`
7. Se validação falhar → PARAR e reportar erros
8. Se validação passar → Criar checkpoint inicial e avançar

---

## Etapa 1 — Requirement Extraction

**Input:** `roadmap.md`
**Output:** `docs/requirements.yaml`

**Thinking Required:**
```
<thinking>
- Quantos módulos existem no roadmap?
- Quantas entidades foram identificadas?
- Há dependências entre módulos?
- Estimativa de tokens para o YAML: ~X tokens
</thinking>
```

Leia `roadmap.md`. Extraia todos os requisitos funcionais, entidades, regras de negócio e requisitos não-funcionais. Gere `docs/requirements.yaml` com estrutura:

```yaml
project:
  name: string
  description: string

modules:
  - name: string
    description: string
    priority: high|medium|low
    features:
      - id: string
        title: string
        description: string
        acceptance_criteria: [string]

entities:
  - name: string
    description: string
    module: string

business_rules:
  - id: string
    description: string

non_functional:
  security: string
  performance: string
  scalability: string
```

**Pós-processamento:**
1. Executar `/skill00-validator step1`
2. Se validação falhar → PARAR, reportar erros, sugerir correções
3. Se validação passar → Criar checkpoint step1 e avançar
4. **Descarte** o conteúdo de `roadmap.md` da memória

Avance para Etapa 1.5.

---

## Etapa 1.5 — Design System

**Input:** `docs/requirements.yaml`
**Output:** `docs/design-system.yaml`

Executar `/skill-design-system`. Gera todos os tokens de cor, configurações de AG Grid, Plotly, tipografia e convenções de IDs que serão usados pelas etapas 7-10.

**Pós-processamento:**
1. Verificar que `docs/design-system.yaml` é YAML válido
2. Criar checkpoint step1_5 e avançar
3. **Descarte** `requirements.yaml` da memória

Avance para Etapa 2.

---

## Etapa 2 — Data Model Generation

**Input:** `docs/requirements.yaml`
**Output:** `docs/data_model.yaml`

Leia APENAS `docs/requirements.yaml`. Para cada item em `entities`, crie a definição completa de campos, tipos SQL Server, constraints e relacionamentos.

```yaml
entities:
  <nome>:
    table: string
    fields:
      - name: string
        type: string   # int, varchar(N), decimal(P,S), datetime2, bit
        nullable: bool
        primary_key: bool
        foreign_key: {table: string, field: string}
    indexes:
      - fields: [string]
        unique: bool

relationships:
  - from: string
    to: string
    type: one_to_one|one_to_many|many_to_many

enums:
  <nome>:
    values: [string]
```

Campos obrigatórios em toda entidade: `id` (PK, int identity), `created_at`, `updated_at`.
**Pós-processamento:**
1. Executar `/skill00-validator step2`
2. Verificar ciclos de dependência em FKs
3. Se validação falhar → PARAR e reportar
4. Se validação passar → Criar checkpoint step2 e avançar
5. **Descarte** `requirements.yaml` da memória

Avance para Etapa 2.5.

---

## Etapa 2.5 — Environment & Database Configuration

**Input:** `docs/data_model.yaml`, `.build/project.json`
**Output:** `backend/config.py`, `backend/database.py`, `.env.example`, `.gitignore` (atualizado)

Executar `/skill-env`. Gera a configuração de ambiente com pydantic-settings, a conexão SQLAlchemy com fallback SQLite e o `.env.example` com todas as variáveis necessárias.

**Pós-processamento:**
1. Verificar que `backend/config.py` e `backend/database.py` são Python válidos
2. Verificar que `.gitignore` contém `.env`
3. Criar checkpoint step2_5 e avançar

Avance para Etapa 2.6.

---

## Etapa 2.6 — API Contracts

**Input:** `docs/requirements.yaml`, `docs/data_model.yaml`
**Output:** `docs/api_contracts.yaml`

Executar `/skill-api-contracts`. Gera os contratos de todos os endpoints REST (request/response schemas, status codes, regras de autenticação) antes de gerar o backend.

**Pós-processamento:**
1. Verificar que `docs/api_contracts.yaml` é YAML válido
2. Verificar que toda entidade do data model tem contrato
3. Criar checkpoint step2_6 e avançar
4. **Descarte** `data_model.yaml` da memória

Avance para Etapa 2.7.

---

## Etapa 2.7 — Business Logic Analysis

**Input:** `docs/requirements.yaml`, `docs/data_model.yaml` (+ `roadmap.md` como fallback)
**Output:** `docs/business_logic.yaml`

Executar `/skill-business-logic`. Classifica cada `business_rule`/feature em `validation | derived_field | interactive_formula | workflow_rule`, extraindo fórmula/variáveis/campos de saída de forma estruturada — em vez de deixar as etapas 6, 7, 9 reinterpretarem o texto livre cada uma por conta própria (o que hoje faz várias delas caírem no mesmo cálculo-placeholder genérico em vez da fórmula real do roadmap).

**Pós-processamento:**
1. Executar `/skill00-validator step2_7`
2. Se `confidence_summary.needs_review` não vier vazio → reportar ao usuário quais regras não puderam ser extraídas com confiança (aviso — não bloqueia)
3. Se validação estrutural falhar → PARAR e reportar
4. Se validação passar → Criar checkpoint step2_7 e avançar

Avance para Etapa 3.

---

## Etapa 3 — SQL Generation

**Input:** `docs/data_model.yaml`
**Output:** `database/schema.sql`, `database/views.sql`, `database/procedures.sql`

Leia APENAS `docs/data_model.yaml`. Gere os três arquivos sequencialmente:

1. `schema.sql` — `CREATE TABLE` com `IF NOT EXISTS`, compatível com SQL Server e Fabric.
2. `views.sql` — `CREATE OR ALTER VIEW vw_<entity>` com JOINs das entidades relacionadas.
3. `procedures.sql` — procedures `usp_<entity>_get_all`, `usp_<entity>_get_by_id`, `usp_<entity>_insert`, `usp_<entity>_update`, `usp_<entity>_delete`.

**Pós-processamento:**
1. Executar `/skill00-validator step3`
2. Verificar ordem de criação de tabelas (topological sort)
3. Se validação falhar → PARAR e reportar
4. Se validação passar → Criar checkpoint step3 e avançar
5. **Descarte** `data_model.yaml` da memória

Avance para Etapa 4.

---

## Etapa 4 — Mock Data Generation

**Input:** `docs/data_model.yaml`
**Output:** `mock_data/<entity>.csv` e `mock_data/<entity>.json` para cada entidade

Leia `docs/data_model.yaml`. Extraia a lista completa de entidades (apenas as que têm `table:`, ignorar enums).

**ANTES de gerar qualquer arquivo**, monte um checklist explícito no formato:
```
[ ] entidade1 → mock_data/entidade1.csv + mock_data/entidade1.json
[ ] entidade2 → mock_data/entidade2.csv + mock_data/entidade2.json
...
```

Verifique quais entidades JÁ têm AMBOS os arquivos no disco — marque essas como `[x]`. Gere APENAS as que ainda estão `[ ]`.

Para cada entidade pendente, na ordem do checklist:
1. Gere o CSV completo e escreva em `mock_data/<entidade>.csv`
2. Gere o JSON completo e escreva em `mock_data/<entidade>.json`
3. Marque `[x]` no checklist e exiba: `✓ <entidade> → CSV (N rows) + JSON (N rows)`
4. Só avance para a próxima entidade após confirmar que AMBOS os arquivos foram escritos

Regras de dados:
- Gere entre 10 e 50 registros por entidade (realistas, em português brasileiro)
- Respeite FKs (IDs válidos nas entidades referenciadas)
- IDs inteiros sequenciais a partir de 1, datas ISO 8601, decimais com ponto
- Booleanos: `true`/`false` (JSON) e `1`/`0` (CSV)
- Enums: usar apenas valores definidos em `enums` do data_model.yaml

**NUNCA** escreva texto com vírgula não-escapada em campos CSV sem envolver o campo em aspas duplas.

**Pós-processamento:**
1. Ao finalizar todas as entidades, listar o checklist completo mostrando todos os `[x]`
2. Executar `/skill00-validator step4` — ele verifica o disco, não a memória
3. Se validação falhar → PARAR e reportar qual entidade/arquivo está faltando
4. Se validação passar → Criar checkpoint step4 listando AMBOS csv e json por entidade e avançar

Avance para Etapa 5.

---

## Etapa 5 — SQL Seed Generation

**Input:** `docs/data_model.yaml` + arquivos `mock_data/*.json`
**Output:** `database/seed.sql`

Leia `data_model.yaml` para ordem de inserção (respeitar FKs). Para cada entidade, leia o `.json` correspondente e gere os INSERTs com `SET IDENTITY_INSERT ON/OFF`. Use insert condicional (`IF NOT EXISTS`) para idempotência. Processe uma entidade por vez.

**Pós-processamento:**
1. Executar `/skill00-validator step5`
2. Se validação falhar → PARAR e reportar
3. Se validação passar → Criar checkpoint step5 e avançar

Avance para Etapa 6.

---

## Etapa 6 — Screen Definition

**Input:** `docs/requirements.yaml`
**Output:** `docs/screens_definition.yaml`

Leia APENAS `docs/requirements.yaml`. Defina uma tela por módulo/feature principal. Para cada tela especifique: `title`, `route`, `data_sources`, `components` (tipo: filter, grid, chart, modal, form, kpi), `actions` e `filters`.

**Pós-processamento:**
1. Executar `/skill00-validator step6`
2. Verificar que todas as rotas são únicas
3. Se validação falhar → PARAR e reportar
4. Se validação passar → Criar checkpoint step6 e avançar

Avance para Etapa 7.

---

## Etapa 7 — Frontend Pages

**Input:** `docs/screens_definition.yaml` + `docs/data_model.yaml`
**Output:** para cada página em `screens_definition.yaml`:

```
frontend/pages/<page>/<page>_page.py
frontend/pages/<page>/<page>_components.py
frontend/pages/<page>/<page>_queries.py
frontend/pages/<page>/<page>_callbacks.py
```

Processe UMA página por vez. Para cada página:

**`_queries.py`** — funções que leem `mock_data/` via `pd.read_csv()` e filtros. NÃO conectar ao banco.

**`_components.py`** — componentes visuais com o design system abaixo. Grids com `dash_ag_grid`, gráficos com `plotly.express`. Filtros em card compacto. KPIs com borda lateral colorida.

**`_page.py`** — `register_page()` + `layout()` retorna `html.Div` com `className="page-wrapper px-4 py-3"` e `style={"background": "#f8fafc", "minHeight": "100vh"}`. NUNCA use `dbc.Container` como raiz.

**`_callbacks.py`** — `register_callbacks()` com todos os `@callback`. Usa `_queries.py` para dados.

### Design System Obrigatório

| Elemento       | Regra                                                           |
| -------------- | --------------------------------------------------------------- |
| Fundo da página | `#f8fafc` via style inline no `html.Div` raiz                 |
| Cards          | `dbc.Card` com `className="shadow-sm border-0 mb-3"`            |
| Header do card | `dbc.CardHeader` com `className="bg-white border-bottom fw-semibold"` |
| KPI card       | `border-start border-4 border-{color}` sem shadow lateral extra |
| Filtros        | Card com `CardBody className="py-2"` e `Row className="g-2 align-items-end"` |
| AG Grid        | `ag-theme-alpine`, `floatingFilter: True`, `suppressMenu: True`, `rowHeight: 44` |
| Plotly         | `template="plotly_white"`, `paper_bgcolor="rgba(0,0,0,0)"`, `height=300` |
| Botão filtrar  | `color="primary"`, `className="w-100"`                          |
| Status badges  | `dbc.Badge` com cores semânticas (success/warning/danger)       |

IDs no padrão `<page>-<component>`. Tipagem Python obrigatória. Após cada página, avance para a próxima.

---

## Etapa 8 — App Principal + Sidebar

**Output:** `frontend/components/sidebar.py` e `frontend/app.py`

### `frontend/components/sidebar.py`

Sidebar fixa à esquerda com largura 240px. Links para todas as páginas geradas na Etapa 7.

```python
import dash_bootstrap_components as dbc
from dash import html, page_registry

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "240px",
    "padding": "0",
    "background": "#1e293b",
    "zIndex": 100,
    "display": "flex",
    "flexDirection": "column",
}

CONTENT_STYLE = {
    "marginLeft": "240px",
    "minHeight": "100vh",
    "background": "#f8fafc",
}

CONTENT_FULL_STYLE = {
    "marginLeft": "0",
    "minHeight": "100vh",
    "background": "#f8fafc",
}

def build_sidebar() -> html.Div:
    nav_items = [
        # Um NavLink por página, com ícone Bootstrap (bi bi-*)
        # Ex.: {"href": "/", "label": "Dashboard", "icon": "bi-speedometer2"}
        # Listar todas as páginas geradas
    ]
    return html.Div([

        # ── Topo: logo/nome do projeto ────────────────────────────────────
        html.Div([
            html.Span("●", style={"color": "#1045C8", "fontSize": "1.2rem"}),
            html.Span(f" {project_name}", style={"color": "white", "fontWeight": "700", "fontSize": "1rem"}),  # project_name lido de .build/project.json
        ], style={"padding": "20px 16px 16px", "borderBottom": "1px solid #334155", "flexShrink": "0"}),

        # ── Meio: links de navegação (cresce e rola se necessário) ────────
        html.Nav([
            dbc.NavLink(
                [html.I(className=f"bi {item['icon']} me-2"), item["label"]],
                href=item["href"],
                active="exact",
                style={"color": "#cbd5e1", "padding": "10px 16px", "display": "flex", "alignItems": "center", "borderRadius": "6px", "margin": "2px 8px"},
                className="sidebar-link",
            )
            for item in nav_items
        ], style={"padding": "8px 0", "flexGrow": "1", "overflowY": "auto"}),

        # ── Rodapé: crédito fixo na base da sidebar ───────────────────────
        html.Div([
            html.P("Desenvolvido por", style={
                "margin": "0",
                "fontSize": "0.68rem",
                "color": "#475569",
                "lineHeight": "1.3",
            }),
            html.P("Quantiz Pricing Solution", style={
                "margin": "0",
                "fontSize": "0.68rem",
                "color": "#64748b",
                "fontWeight": "500",
                "lineHeight": "1.3",
            }),
        ], style={
            "padding": "12px 16px",
            "borderTop": "1px solid #334155",
            "flexShrink": "0",
        }),

    ], style=SIDEBAR_STYLE)
```

### `frontend/pages/login/login_page.py`

Página de login fullscreen. Fundo degradê escuro (`#1e293b → #0f172a`). Card centralizado com:
- Logo da aplicação
- Input de e-mail (com `n_submit`)
- Input de senha (com `n_submit`)
- Botão "Entrar"
- `dbc.Alert(id="login-alert")` para erros
- Texto de dica do modo desenvolvimento

NÃO usa sidebar. `layout()` retorna `html.Div` que preenche a tela inteira.

### `frontend/pages/login/login_callbacks.py`

**Regra:** `Output("url", "pathname")` existe APENAS em `guard_routes` (app.py). Nunca duplicar.

```python
def register_callbacks() -> None:
    @callback(
        Output("current-user", "data"),    # ← único output de routing é guard_routes
        Output("login-alert", "children"),
        Output("login-alert", "is_open"),
        Input("login-btn", "n_clicks"),
        Input("login-email", "n_submit"),
        Input("login-senha", "n_submit"),
        State("login-email", "value"),
        State("login-senha", "value"),
    )
    def fazer_login(n_clicks, n_email, n_senha, email, senha):
        # Valida e-mail contra mock_data/usuarios.csv
        # Modo mock: qualquer senha é aceita se o e-mail existir
        # Sucesso → (usuario_dict, "", False) — guard_routes redireciona automaticamente
        # Falha   → (no_update, msg_erro, True)
```

### `frontend/app.py`

**NÃO usar `dash.page_container`** — usar render callback explícito:

```python
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html, no_update
from frontend.components.sidebar import (
    CONTENT_FULL_STYLE, CONTENT_STYLE, build_sidebar, register_sidebar_callbacks,
)

# 1. Instanciar app PRIMEIRO
app = dash.Dash(__name__, use_pages=True, pages_folder="pages",
    external_stylesheets=[dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"],
    suppress_callback_exceptions=True, title="<nome>")
server = app.server

# 2. Importar layouts APÓS app (aciona dash.register_page())
from frontend.pages.login.login_page import layout as login_layout          # noqa: E402
from frontend.pages.<page>.<page>_page import layout as <page>_layout       # noqa: E402
# ... uma linha por página

_PAGE_LAYOUTS: dict = {
    "/": login_layout, "/login": login_layout,
    "/<page>": <page>_layout,  # ... uma entrada por rota
}

# 3. Imports de callbacks
from frontend.pages.login.login_callbacks import register_callbacks as login_register  # noqa: E402
from frontend.pages.<page>.<page>_callbacks import register_callbacks as <page>_register  # noqa: E402

# 4. Layout — html.Div(id="page-content") no lugar de dash.page_container
app.layout = html.Div([
    dcc.Store(id="current-user", storage_type="session"),
    dcc.Location(id="url", refresh=False),
    html.Div(id="sidebar-wrapper"),
    html.Div(html.Div(id="page-content"), id="main-content"),
])

# 5. Registrar todos os callbacks
login_register(); <page>_register(); register_sidebar_callbacks()

# 6. Render de página
@callback(Output("page-content", "children"), Input("url", "pathname"),
          prevent_initial_call=False)
def render_page_content(pathname: str):
    layout_fn = _PAGE_LAYOUTS.get(pathname)
    if layout_fn is None:
        return dbc.Alert(f"Página não encontrada: {pathname}", color="warning", className="m-4")
    return layout_fn() if callable(layout_fn) else layout_fn

# 7. Guard routes — ÚNICO callback com Output("url","pathname")
# Input("current-user","data") é obrigatório para disparar redirect pós-login
@callback(Output("url", "pathname"),
          Input("url", "pathname"), Input("current-user", "data"),
          prevent_initial_call=False)
def guard_routes(pathname: str, user_data):
    _PROTEGIDAS = ["/<page1>", "/<page2>"]  # todas as rotas autenticadas
    if pathname in ("/", None): return "/dashboard" if user_data else "/login"
    if pathname == "/login": return "/dashboard" if user_data else no_update
    if pathname in _PROTEGIDAS: return no_update if user_data else "/login"
    return no_update

# 8. Toggle sidebar — Input("current-user","data") para atualizar após login
@callback(Output("sidebar-wrapper", "children"), Output("main-content", "style"),
          Input("url", "pathname"), Input("current-user", "data"),
          prevent_initial_call=False)
def toggle_sidebar(pathname: str, user_data):
    if pathname in ("/login", "/") or not user_data: return [], CONTENT_FULL_STYLE
    return build_sidebar(), CONTENT_STYLE

if __name__ == "__main__":
    app.run(debug=True, port=1050)
```

**Regras críticas:**
- `dash.page_container` **PROIBIDO** — substituído por `render_page_content`
- Layouts importados APÓS `app = dash.Dash(...)` (`register_page` exige app instanciado)
- `guard_routes` e `toggle_sidebar` usam `Input("current-user","data")` para disparar ao fazer login
- `Output("url","pathname")` SOMENTE em `guard_routes`, nunca em `login_callbacks`
- Executar com `python -m frontend.app` (não `python frontend/app.py`)

---

## Etapa 9 — Backend FastAPI

**Input:** `docs/data_model.yaml`
**Output:** para cada entidade:

```
backend/models/<entity>.py
backend/schemas/<entity>.py
backend/repositories/<entity>.py
backend/services/<entity>.py
backend/api/routes/<entity>.py
```

**ANTES de gerar qualquer arquivo**, monte um checklist das entidades (apenas as com `table:`, ignorar enums):
```
[ ] entidade1  →  model ✗  schema ✗  repository ✗  service ✗  route ✗
[ ] entidade2  →  model ✗  schema ✗  repository ✗  service ✗  route ✗
...
```

Verifique quais entidades JÁ têm os 5 arquivos no disco — marque `[x]` e pule-as. Gere apenas as pendentes.

Para cada entidade `[ ]`:
1. Gere os 5 arquivos sequencialmente
2. Marque `[x]` e exiba: `✓ entidade → 5 arquivos gerados`
3. Só avance para a próxima entidade após confirmar gravação de todos os 5

Após todas as entidades, gere **`backend/main.py`**:
```python
from fastapi import FastAPI
from backend.api.routes import <entity1>, <entity2>

app = FastAPI(title=f"{project_name} API")  # project_name lido de .build/project.json
app.include_router(<entity1>.router)
app.include_router(<entity2>.router)
```

**Pós-processamento:**
1. Exibir checklist completo com todos os `[x]`
2. Executar `/skill00-validator step9`
3. Se validação falhar → identificar entidade/arquivo faltante, regerar apenas ela
4. Se validação passar → criar checkpoint step9 listando os 5 arquivos por entidade e avançar

---

## Etapa 9.5 — Camada de Autenticação

**Input:** `backend/config.py`, `docs/data_model.yaml` (entidade de usuários)
**Output:** `backend/auth.py`, `backend/schemas/token.py`, `backend/api/routes/auth.py`

Executar `/skill-auth`. Gera JWT com python-jose + bcrypt, o endpoint `/api/v1/auth/login`, a dependência `get_current_user` e a atualização do `login_callbacks.py` para chamada real à API.

**Ações adicionais:**
1. Adicionar `CORSMiddleware` ao `backend/main.py` com `settings.cors_origins`
2. Adicionar `app.include_router(auth.router, prefix="/api/v1")` ao `backend/main.py`
3. Adicionar `Depends(get_current_user)` em todos os routers de entidades
4. Desabilitar `/docs` e `/redoc` quando `settings.is_production == True`

**Pós-processamento:**
1. Executar `/skill00-validator step9` novamente para re-validar backend com auth
2. Verificar que `SECRET_KEY` não aparece como literal string no código
3. Criar checkpoint step9_5 e avançar

Avance para Etapa 10.

---

## Etapa 10 — Arquivos de Configuração e README

Gere os arquivos abaixo de forma compacta:

**`requirements.txt`** — liste apenas as dependências reais usadas no código gerado:
```
dash>=2.14.0
dash-bootstrap-components>=1.5.0
dash-ag-grid>=31.0.0
plotly>=5.18.0
pandas>=2.0.0
numpy>=1.24.0
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
pyodbc>=5.0.0
python-dotenv>=1.0.0
pytest>=7.4.0
httpx>=0.26.0
requests>=2.31.0
```

**`frontend/components/sidebar.py`** — sidebar fixa à esquerda com links para todas as páginas geradas (gerada na Etapa 8 — pular se já existir).

**`README.md`** — documentação do projeto com as seções:
- Nome e descrição do projeto
- Stack tecnológico (tabela)
- Estrutura de pastas
- Como rodar (frontend e backend)
- Fluxo de desenvolvimento vs integração
- Páginas disponíveis (com rota e descrição)
- Como executar os testes (seção obrigatória, ver detalhes abaixo)
- Próximos passos (integração com banco)

**Seção obrigatória no README — Como executar os testes:**

```markdown
## Testes

### Testes Unitários de Backend (Pytest)

Rodam em memória (SQLite), sem necessidade de banco ou servidor.

\`\`\`bash
pip install -r requirements.txt
pytest tests/backend/ -v
\`\`\`

Para rodar uma entidade específica:

\`\`\`bash
pytest tests/backend/test_cenarios_precificacao.py -v
\`\`\`

### Testes E2E de Frontend (Cypress)

Requerem o app rodando em `http://localhost:1050`.

\`\`\`bash
# 1. Iniciar o backend e o frontend
uvicorn backend.main:app --reload &
python -m frontend.app &

# 2. Instalar dependências do Cypress (apenas na primeira vez)
cd tests/frontend
npm install

# 3. Abrir o Cypress interativo
npm run cy:open

# 4. Ou rodar todos os specs headless (modo CI)
npm run cy:run
\`\`\`

Para rodar um spec específico:

\`\`\`bash
npx cypress run --spec "cypress/e2e/cenarios.cy.js"
\`\`\`

> **Credenciais de teste:** `ana.silva@diageo.com` / `senha123` (mock — ver `cypress/fixtures/usuario.json`)
```

---

## Etapa 11 — Testes Unitários de Backend (Pytest)

**Input:** arquivos gerados em `backend/` na Etapa 9
**Output:** `tests/conftest.py` + `tests/backend/test_<entidade>.py` para cada entidade

Monte checklist de entidades (mesmo da Etapa 9). Verifique quais já têm arquivo de teste no disco — pule-as.

Para cada entidade pendente, execute `/skill12-tests <entidade>`:
- Exiba: `✓ test_<entidade>.py gerado`

Gere `tests/conftest.py` se não existir (fixtures de `client` e `test_db` com SQLite em memória).

**Pós-processamento:**
1. Verificar que `tests/backend/` contém um arquivo por entidade
2. Verificar que `tests/conftest.py` existe
3. Criar checkpoint step11 e avançar

---

## Etapa 12 — Testes E2E (Cypress)

**Input:** `docs/screens_definition.yaml`, `docs/design-system.yaml`, `mock_data/usuarios.csv`
**Output:** suite Cypress completa em `tests/frontend/`

Execute `/skill13-integration-tests` (sem argumento) para gerar o setup completo + todos os specs.

Isso gera:
- `tests/frontend/package.json` — dependência Cypress
- `tests/frontend/cypress.config.js` — config com `baseUrl: http://localhost:1050`
- `tests/frontend/cypress/fixtures/usuario.json` — e-mail real de `mock_data/usuarios.csv`
- `tests/frontend/cypress/support/commands.js` — `cy.login()` com `cy.session()`
- `tests/frontend/cypress/support/e2e.js`
- `tests/frontend/cypress/e2e/login.cy.js`
- `tests/frontend/cypress/e2e/<pagina>.cy.js` — um spec por página em `screens_definition.yaml`

**Pós-processamento:**
1. Verificar que `package.json` e `cypress.config.js` existem em `tests/frontend/`
2. Verificar que existe um spec `.cy.js` para cada página listada em `screens_definition.yaml`
3. Criar checkpoint step12 e avançar

---

## Relatório Final

Após concluir todas as etapas, exiba:

```
=== BUILD COMPLETO ===

✓ Etapa 0   — .build/project.json (project.name extraído)
✓ Etapa 1   — docs/requirements.yaml
✓ Etapa 1.5 — docs/design-system.yaml
✓ Etapa 2   — docs/data_model.yaml
✓ Etapa 2.5 — backend/config.py + backend/database.py + .env.example
✓ Etapa 2.6 — docs/api_contracts.yaml
✓ Etapa 2.7 — docs/business_logic.yaml (<N> regras: <N> validação, <N> campo derivado, <N> fórmula interativa, <N> workflow)
✓ Etapa 3   — database/ (schema, views, procedures)
✓ Etapa 4   — mock_data/ (<N> entidades)
✓ Etapa 5   — database/seed.sql
✓ Etapa 6   — docs/screens_definition.yaml
✓ Etapa 7   — frontend/pages/ (<N> páginas)
✓ Etapa 8   — frontend/app.py + sidebar + login
✓ Etapa 9   — backend/ (<N> entidades) — skill11-fastapi
✓ Etapa 9.5 — backend/auth.py + JWT + CORS configurados
✓ Etapa 10  — requirements.txt, README.md
✓ Etapa 11  — tests/backend/ (<N> entidades) — skill12-tests
✓ Etapa 12  — tests/integration/ (smoke + data consistency)

Próximos passos:
  1. cp .env.example .env  →  preencher credenciais
  2. pip install -r requirements.txt
  3. uvicorn backend.main:app --reload  →  API em http://localhost:8000
  4. python -m frontend.app             →  UI em http://localhost:1050
```
