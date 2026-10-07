# Skill — App Shell (Step 0 + Step 8 do frontend-builder)

Especificação autoritativa do **shell do produto**: bibliotecas, tema, sidebar com usuário/grupos/badges, Home, login split-screen e `app.py`. É o que faz o app gerado parecer um produto e não um protótipo.

**Inputs:** `.build/project.json` (branding + demo), `docs/design-system.yaml`, `docs/screens_definition.yaml`, `docs/requirements.yaml`
**Outputs:** `frontend/components/{ui_components,charts,workflow_components,sidebar}.py`, `assets/{theme,sidebar}.css`, `frontend/pages/home/*`, `frontend/pages/login/*`, `frontend/app.py`

---

## Step 0 — Bibliotecas + tema (uma vez por projeto)

Copiar arquivos faltantes; em projeto existente, aplicar patches incrementais preservando customizações. Não pular atualização de branding ou cenário apenas porque ui_components.py existe.

1. Copiar `../.claude/templates/components-library.py` → `frontend/components/ui_components.py`
2. Copiar `../.claude/templates/charts-library.py` → `frontend/components/charts.py`
3. Copiar `../.claude/templates/workflow_components.py` → `frontend/components/workflow_components.py`
4. Copiar `../.claude/templates/dash-starter/assets/theme.css` → `assets/theme.css`
5. Copiar `../.claude/templates/api_client.py` → `frontend/api_client.py`
   - Assistente habilitado por padrão: copiar pricing_assistant.py para services/ e pricing_assistant_components.py para components/; gerar catálogo/handlers/callbacks conforme skill-pricing-assistant.md. Montar assistant_panel uma vez no shell, oculto no login. Não alterar o fluxo de login para esta integração.
   - Se houver arquitetura/simulação compartilhada, copiar `../.claude/templates/demo_scenario.py` → `frontend/components/demo_scenario.py` e seguir `skill-demo-scenario.md` para stores, motor e dispatcher. Em modo mock, operar sem API.
6. Criar `frontend/__init__.py`, `frontend/components/__init__.py`, `frontend/pages/__init__.py` (vazios) e `assets/icons/`
7. **Aplicar o branding** (ler `.build/project.json → branding`):
   - Resolver a cor primária antes de derivar a paleta: valor explicitamente informado no roadmap/configuração > cor estimada do logo > fallback `#1045C8`. Não considerar o default copiado de design-system.yaml como escolha explícita do cliente.
   - Detectar `assets/logo.png` mesmo com `branding.logo` vazio. Copiar `templates/scripts/brand_palette.py` para `scripts/` e executar com Pillow no ambiente de build se não houver cor explícita. Registrar `primary_source: explicit|logo|fallback` e a cor resolvida em `.build/project.json` e `docs/design-system.yaml`; se logo neutro/ausente, registrar fallback e motivo. Não inventar a cor oficial da empresa. Rodar novamente o Step 0 após adicionar/trocar logo para atualizar a paleta.
   - Sincronizar CSS, `ui_components.PRIMARY`, ambos os `CHART_COLORWAY`, cores de foco e botões. Conferir contraste do texto branco nos botões/painel; escurecer o tom de superfície quando necessário, preservando a cor original como referência da marca. Não recolorir o arquivo de logo; usar `logo_dark` (variante para fundo escuro) quando fornecido.
   - Calcular a paleta com a MESMA lógica de `derive_palette(primary, secondary)` de `ui_components.py` (execute `python -c "from frontend.components.ui_components import derive_palette; print(derive_palette('<primary>', <secondary|None>))"`).
   - Em `assets/theme.css`, substituir os valores de `--pmz-primary`, `--pmz-primary-hover`, `--pmz-primary-soft`, `--pmz-primary-soft-border`, `--pmz-primary-dark`, `--pmz-secondary` no bloco `:root`.
   - Em `ui_components.py` e `charts.py`, substituir `"#1045C8"` (primeiro item de `CHART_COLORWAY`) pela cor primária; se houver secundária, substituir o terceiro item (`"#f59e0b"`) por ela.
   - Se `branding.font == "inter"`: acrescentar em `theme.css` `@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');` e `--pmz-font-ui: 'Inter', system-ui, sans-serif;` (única exceção permitida a fontes externas).
   - Se `branding.favicon` existir em disco: garantir que está em `assets/favicon.ico` (Dash serve automaticamente).
8. Checkpoint `✓ Step 0 → bibliotecas + tema (primary <cor>)`.

---

## Step 8 — Sidebar, Home, Login, app.py

### 8.1 `frontend/components/sidebar.py`

Toda a estilização está em `assets/theme.css` (classes `.sidebar*`, `.user-avatar`, `.nav-badge`). **`html.Style()` não existe em Dash** — nunca gerar CSS inline em Python além do que já vem da biblioteca.

Estrutura (de cima para baixo):

```
┌──────────────────────────────┐
│ [logo | iniciais]  Nome      │  .sidebar-brand  (tagline em linha menor, opcional)
│                    tagline   │
├──────────────────────────────┤
│ VISÃO GERAL                  │  .sidebar-group  (um por menu_group, na ordem do roadmap)
│  ⌂ Início                    │  sempre primeiro item do primeiro grupo → /home
│  ◔ Dashboard Executivo       │
│  ▥ Análise de Vendas         │
│ PRICING                      │
│  ▤ Tabela de Preços          │
│  ⚙ Simulação          [ 5 ]  │  .nav-badge quando screens[].sidebar_badge existir
│  ✓ Fila de Aprovações [ 5 ]  │
│ ADMINISTRAÇÃO                │
│  ☺ Usuários                  │  só aparece para roles com access à tela
├──────────────────────────────┤
│ (AS) Ana Souza       [Sair]  │  .sidebar-user → user_badge(nome, role, email) + botão id={"type": "btn-logout", "index": "sidebar"}
│      gerente · ana@…         │
│ Desenvolvido por             │  .sidebar-footer — 2 linhas + "v{version}"
│ Quantiz Pricing Solution     │
└──────────────────────────────┘
```

Regras:
- `build_sidebar(pathname: str, user: dict | None, badges: dict[str, int] | None = None) -> html.Div` — `user` vem do `dcc.Store("current-user")` (`{nome, email, role}`); itens cuja tela não dá `access` ao `role` são **omitidos** (não desabilitados).
- Itens: `dbc.NavLink([html.I(className=f"bi bi-{icon}"), html.Span(label), html.Span(str(n), className="nav-badge") if n else None], href=route, active="exact", className="nav-link")`. Ordem e agrupamento vêm de `screens_definition.yaml → pages[].menu_group` (fallback: ordem dos módulos, grupo "Geral").
- Logo: `os.path.isfile(<assets>/<branding.logo>)` avaliado no import → `html.Img(src=f"/assets/{logo}", height=30)`; senão `html.Div(display_name[:2].upper(), className="brand-mark")`.
- Contadores (`badges`): calculados em `app.py` por callback global (Padrão 12 de `skill08-dash-callback.md`) lendo a query indicada em `pages[].sidebar_badge` — a sidebar só renderiza o número recebido.
- Exportar `build_sidebar`, `CONTENT_STYLE = {"marginLeft": "240px"}`, `CONTENT_FULL_STYLE = {"marginLeft": "0"}`, `register_sidebar_callbacks()` (hoje vazio, reservado).
- **Nenhum CSS em `assets/sidebar.css`** — tudo já está em `theme.css`. Se o projeto antigo tiver `sidebar.css`, remova para evitar conflito.

### 8.2 `frontend/pages/home/` (sempre gerada)

Rota `/home` — destino após login. 4 arquivos como qualquer página (`home_page.py`, `home_components.py`, `home_queries.py`, `home_callbacks.py`).

Conteúdo, nesta ordem, usando `app_shell(active_key="home", icon_key="house", title=f"Olá, {primeiro_nome}", subtitle=<demo.story resumido ou descrição do projeto>, breadcrumb_items=None)`:
1. **Números-âncora** — `kpi_row` com 3–4 `kpi_simple` calculados dos mocks (ex.: receita últimos 12 meses `format_compact`, itens ativos, pendências, margem média). Escolha a partir de `demo_context.anchors` + KPIs do dashboard principal; cada um com `trend=` (últimos 12 meses) quando houver fato com data.
2. **Atalhos** — `dbc.Row` de `home_shortcut_card(icon, title, user_goal, route, badge)` para cada tela que o `role` acessa (exceto Home e Administração para não-admin); `badge` = contagem de pendências quando `sidebar_badge` existir.
3. **Para você** — `card("Pendências para você")` com `data_table` (máx. 10 linhas, sem paginação) dos itens que exigem ação do role logado (aprovador → pendentes de aprovação; analista → rascunhos/rejeitados dele). Se vazio → `empty_state("Nenhuma pendência", "Tudo em dia!", icon_key="check2-circle", compact=True)`.
4. **Como funciona** (opcional, quando há workflow) — `card` com o `workflow_breadcrumb` do Workflow Principal em modo passivo.

O `layout()` da Home lê `current-user` via callback (`Output("home-content","children") ← Input("current-user","data")`) para personalizar nome/role.

### 8.3 `frontend/pages/login/`

`login_page.py` — **split-screen**, sem sidebar, classes de `theme.css`:

```python
html.Div([
    # Painel de marca (esquerda) — some em telas < 992px
    html.Div([
        html.Div([
            login_brand_logo(_ASSETS, display_name, branding.get("logo_dark") or branding.get("logo")),
            html.Div([
            html.H1(branding.tagline),
            html.P(<descrição do projeto — 1ª frase>, className="lead"),
            *[html.Div([html.I(className="bi bi-check-circle-fill"), html.Span(b)], className="bullet") for b in <3 bullets>],
            ]),
        ], className="login-brand-content"),
        html.Div("Quantiz Pricing Solution", style={"opacity": 0.7, "fontSize": "0.8rem"}),
    ], className="login-brand"),
    # Formulário (direita)
    html.Div(dbc.Card(dbc.CardBody([
        html.H4("Entrar", className="fw-semibold mb-1"), html.P("Acesse com seu e-mail corporativo", className="text-muted small mb-4"),
        dbc.Label("E-mail", className="small fw-semibold"), dbc.Input(id="login-email", type="email", n_submit=0, className="mb-3", autoFocus=True),
        dbc.Label("Senha", className="small fw-semibold"), dbc.Input(id="login-senha", type="password", n_submit=0, className="mb-3"),
        dbc.Button("Entrar", id="login-btn", color="primary", className="w-100 fw-semibold", n_clicks=0),
        dbc.Alert(id="login-alert", is_open=False, color="danger", dismissable=True, className="mt-3 small"),
        html.Hr(),
        html.Div("Acesso de demonstração", className="text-muted text-uppercase fw-bold", style={"fontSize": "0.65rem", "letterSpacing": "0.06em"}),
        html.Div([<demo-chip por credencial>], className="d-flex flex-column gap-2 mt-2"),
    ]), className="login-card shadow-sm border-0"), className="login-form"),
], className="login-wrap")
```

- Importar `login_brand_logo` de `ui_components.py`. Ele usa o arquivo configurado ou `assets/logo.png` e preserva proporções, grande e centralizado no painel. Sem arquivo, exibir nome centralizado. Não substituir logo por iniciais pequenas. Detectar o arquivo ao construir o layout para reconhecer logo adicionado depois do build.
- **3 bullets** do painel: derivar dos `user_goal` dos 3 módulos `priority: high` (encurtar para ≤ 60 caracteres).
- **Demo chips**: um por `demo_context.credentials[]` → `html.Div([user_badge(nome, role, compact=True), html.Div([html.Div(nome, className="fw-semibold"), html.Div(email, className="text-muted")]), html.Span("usar", className="ms-auto text-primary fw-semibold")], id={"type": "login-demo-chip", "email": email}, className="demo-chip", n_clicks=0)`. Callback com pattern-matching preenche `login-email` e `login-senha` ("demo") e dispara o login.
- Sem "dica de modo dev" em texto corrido — os chips substituem.

`login_callbacks.py`:
- Callback de login: Outputs `current-user.data`, `login-alert.children`, `login-alert.is_open`; Inputs `login-btn.n_clicks`, `login-email.n_submit`, `login-senha.n_submit`, `{"type":"login-demo-chip","email":ALL}.n_clicks`; States dos valores. Se disparado por chip → usa o e-mail do chip. Valida contra `mock_data/usuarios.csv` (case-insensitive, `ativo == 1`); qualquer senha aceita em modo mock; grava `{"id","nome","email","role"}` no store. Erro → `"E-mail não encontrado. Use um dos acessos de demonstração abaixo."`.
- Bloco comentado `# MODO API:` chamando `api_client.login(email, senha)` (o backend-builder completa).
- **NUNCA** `Output("url","pathname")` aqui.

### 8.4 `frontend/app.py`

```python
import os, json
import dash, dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback, dcc, html, no_update
from frontend.components.sidebar import CONTENT_FULL_STYLE, CONTENT_STYLE, build_sidebar, register_sidebar_callbacks

_ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
with open(os.path.join(os.path.dirname(__file__), "..", ".build", "project.json"), encoding="utf-8") as f:
    PROJECT = json.load(f)

app = dash.Dash(__name__, use_pages=False, assets_folder=_ASSETS,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"],
    suppress_callback_exceptions=True, title=PROJECT["branding"]["display_name"],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
server = app.server

# imports canônicos de layouts APÓS app; sem register_page no roteamento explícito
from frontend.pages.login.login_page import layout as login_layout          # noqa: E402
from frontend.pages.home.home_page import layout as home_layout             # noqa: E402
# ... uma linha por página
_PAGE_LAYOUTS = {"/login": login_layout, "/home": home_layout, "/<page>": <page>_layout, ...}
_ROUTE_ROLES = {"/<page>": ["admin", "gerente", ...], ...}   # de screens_definition.pages[].access

from frontend.pages.login.login_callbacks import register_callbacks as login_register  # noqa: E402
# ... um por página (+ home)

app.layout = html.Div([
    dcc.Store(id="current-user", storage_type="session"),
    dcc.Store(id="workflow-context", storage_type="session"),
    # Quando houver cenários: demo-scenario (session), demo-active (memory), conforme skill-demo-scenario.md.
    dcc.Store(id="sidebar-badges", storage_type="memory"),
    dcc.Location(id="url", refresh=False),
    html.Div(id="sidebar-wrapper"),
    html.Div(html.Div(id="page-content"), id="main-content", className="main-content"),
])

login_register(); home_register(); <page>_register(); ...; register_sidebar_callbacks()

@callback(Output("page-content", "children"), Input("url", "pathname"), Input("current-user", "data"), State("workflow-context", "data"))
def render_page_content(pathname, user, workflow_context):
    if not user and pathname != "/login":
        return login_layout()
    layout_fn = _PAGE_LAYOUTS.get(pathname)
    if layout_fn is None:
        return <empty_state("Página não encontrada", f"A rota {pathname} não existe.", icon_key="signpost-split", action=dcc.Link(button("Ir para o início", primary=True), href="/home"))>
    if user and pathname in _ROUTE_ROLES and user.get("role") not in _ROUTE_ROLES[pathname]:
        return <empty_state("Sem permissão", "Seu perfil não tem acesso a esta tela.", icon_key="shield-lock")>
    context = workflow_context if (workflow_context or {}).get("target") == pathname.lstrip("/") else None
    return layout_fn(workflow_context=context) if callable(layout_fn) else layout_fn

# ÚNICO callback que escreve em url.pathname (inclui logout)
@callback(Output("url", "pathname"), Output("current-user", "data", allow_duplicate=True),
          Input("url", "pathname"), Input("current-user", "data"), Input({"type": "btn-logout", "index": ALL}, "n_clicks"),
          prevent_initial_call="initial_duplicate")
def guard_routes(pathname, user, logout_clicks):
    if isinstance(dash.ctx.triggered_id, dict) and dash.ctx.triggered_id.get("type") == "btn-logout" and any(logout_clicks or []):
        return "/login", None
    if pathname in ("/", None):
        return ("/home" if user else "/login"), no_update
    if pathname == "/login":
        return ("/home" if user else no_update), no_update
    if pathname in _PAGE_LAYOUTS and not user:
        return "/login", no_update
    return no_update, no_update

@callback(Output("sidebar-wrapper", "children"), Output("main-content", "className"),
          Input("url", "pathname"), Input("current-user", "data"), Input("sidebar-badges", "data"))
def toggle_sidebar(pathname, user, badges):
    if pathname in ("/login", "/") or not user:
        return [], "main-content full"
    return build_sidebar(pathname, user, badges or {}), "main-content"

# Padrão 12 (skill08): contadores de pendência para a sidebar
@callback(Output("sidebar-badges", "data"), Input("url", "pathname"), Input("current-user", "data"))
def compute_badges(pathname, user): ...

if __name__ == "__main__":
    app.run(debug=True, port=1050)
```

Regras críticas:
- `dash.page_container` **PROIBIDO**; layouts importados **após** `app = dash.Dash(...)`; rodar com `python -m frontend.app`.
- Logout dinâmico: usar ID `{"type": "btn-logout", "index": "sidebar"}` e Input com `ALL` (lista vazia quando ausente), conforme o callback acima. Não confiar em `suppress_callback_exceptions` para dependências ausentes em runtime.
- Roteamento explícito exige `use_pages=False`, sem `register_page` nem descoberta automática. Importar por `frontend.pages.*` e registrar cada conjunto de callbacks exatamente uma vez, fora de `layout()`.
- Projetos com cenários seguem `skill-demo-scenario.md`: roteador recebe demo-active como Input e demo-scenario como State, passando `scenario_state` ao layout. Editar não remonta a página; aplicar/reset atualizam consumidores. Login/logout limpam estado da persona anterior. Botão Restaurar demonstração fica disponível na área autenticada, com confirmação.
- Todo `layout(workflow_context=None)` aceita contexto e passa valores iniciais aos builders dos filtros/stores. Não gerar callback de montagem com `Input("<pagina>-drill", "id")` ou `Input("<pagina>-filtro-*", "id")`, nem Outputs locais disparados por Inputs globais. O contexto entra pelo roteador e não precisa ser apagado por cada página.
- Escritas em `workflow-context.data` devem ter um único dono no shell: eventos de navegação com IDs de dicionário e `ALL`, incluindo um nonce/context_id por evento. O mesmo callback navega e publica o contexto; combinar essa responsabilidade com o dono de `url.pathname` (guard_routes), sem criar outro writer de URL. Não usar callbacks concorrentes para consumir/apagar contexto. Autorização de rota continua obrigatória.
- `validation_layout` serve para validação estática, não monta componentes no navegador. `prevent_initial_call` e `allow_duplicate` não corrigem IDs ausentes. Callbacks exclusivamente locais só devem depender de componentes locais presentes juntos; globais usam pattern matching `ALL` quando o alvo é dinâmico.
- `main-content` usa **className** (`main-content` / `main-content full`) — o CSS responsivo em `theme.css` cuida do `margin-left`; `CONTENT_STYLE` é mantido só por compatibilidade.
- Pós-login sempre `/home` (não mais direto para o dashboard).

---

## Checklist do shell (pré-entrega)

- [ ] Sidebar mostra grupos, ícone + label, badge de pendências, bloco do usuário com **Sair** funcional
- [ ] Itens da sidebar filtrados por role; Home lista só atalhos acessíveis
- [ ] Login split-screen com tagline, 3 bullets e chips de demo clicáveis que logam
- [ ] `/` → `/home` autenticado; `/login` → `/home` se já logado; rota protegida → `/login`
- [ ] Rota inexistente e sem-permissão renderizam `empty_state` (não `dbc.Alert` cru)
- [ ] `theme.css` com `--pmz-primary` igual ao branding; nenhum `sidebar.css` residual
- [ ] Título da aba = `display_name`; favicon presente se informado
- [ ] Sidebar colapsa para ícones em < 992px
