# Changelog

## v5.0.0 — 2026-10-19 — Paridade com o projeto de referência (Qwizer) + economia de tokens

**Plano e decisões:** `docs/PLANO_MELHORIA_V5.md`.

### Comportamento gerado (portado do Qwizer)
- **Detalhar:**
  - vira **modal central** (`detail_offcanvas(..., extra=)`), com título por `Output(id-title, children)` e botão "Perguntar ao Assistente";
  - conteúdo fixo só via `extra=` (nunca `oc.children=[...]`).
- **KPIs numa linha** (`kpi_row` com larguras iguais + valor com `clamp`/ellipsis). Células do AG Grid com ellipsis.
- **`elasticity_curve`:** rótulos não se sobrepõem ("Atual = Simulado" quando coincidem).
- **Tabela de preços por produto:**
  - preço base = combinação de referência;
  - edições por combinação com propagação proporcional (`expandir`);
  - variações por canal × região × segmento no Detalhar;
  - uma só ação de linha;
  - exportação com duas abas.
- **Volume:** nunca arredondado por linha (preserva a elasticidade; as frações somam o total do produto).
- **Navegação:**
  - `guard_routes` é dono de `url` + `workflow-context` e **limpa o contexto de atalho ao trocar de tela**;
  - banner "Limpar filtro" (skill08, Padrão 14).
- **Assistente de Pricing v2** em todo projeto:
  - modo híbrido: Claude via `ANTHROPIC_API_KEY`, motor local como fallback;
  - análises **por tela**, chamando as mesmas `*_queries.py`;
  - item em foco do Detalhar (`assistant_focus`);
  - parâmetros da tela (`screen_params`, Padrão 15);
  - trava de escopo, catálogo v2 (`pages` explícito, `entity` + `pages`, textos entre aspas) e log de custo.
- **Templates novos:** `assistant_llm.py`, `assistant_detail.py`, `assistant_pages.py`, `assistant_callbacks.py`, `page_common.py`, `tests/`.
- **Templates substituídos:** `pricing_assistant.py` e `pricing_assistant_components.py`.
- **Dependências:** `openpyxl` (Excel), `anthropic` e `pyyaml`. Variáveis do assistente no `.env.example`.
- **Testes:**
  - pytest do frontend em `tests/frontend/`, Cypress em `tests/e2e/`;
  - conftest raiz só com `sys.path`; fixtures de API em `tests/backend/conftest.py`;
  - sem testes de paridade número a número.

### Economia de tokens
- **`rules/core.md`:** fonte única de regras e decisões. Resolve 8 contradições antigas (roteamento, rota pós-login, sidebar, credenciais `demo`, estado na sessão em vez de CSV, mock volumétrico).
- **Cópias de template** sempre com `cp`.
- **Leitura por resumo e índice:**
  - `templates/LIBRARY_INDEX.md` (gerado por `build_library_index.py`) substitui a leitura de cerca de 150 KB de código das bibliotecas;
  - `docs/handoff.md` (data-engineer → frontend/backend) e recortes `docs/screens/<slug>.yaml` (`split_screens.py`) substituem a releitura de cerca de 255 KB de YAMLs por página.
- **frontend-builder com leitura sob demanda** por passo e por tipo de tela.
- **Modelo por agente:** Sonnet no data-engineer, backend-builder, ui-reviewer, test-writer e frontend-fixer; Opus no frontend-builder.
- **`frontend-fixer` (novo):** correções pontuais sem reler as especificações. ui-reviewer sem Write/Edit.
- **`validate_project.py`:** validação determinística (telas, páginas, app, assistente) no lugar do skill00 executado pelo modelo. seed.sql auditado por grep. Loop do mock limitado a 3 tentativas.
- **`skill-simulation.md` reescrito como contrato enxuto** (23 KB → cerca de 6 KB), sem o anti-exemplo nem gravação em CSV.
- **Pipelines arquivados:** `/build`, `/build-parallel` e `/skill-design-system` foram para `.claude/archive/`.

## Não lançado — 2026-10-07

- Assistente de Pricing local gerado automaticamente do roadmap: catálogo de capacidades, handlers calculados, perguntas contextuais e propostas de simulação sem API de IA.
- Runtime conservador por catálogo, histórico por sessão e rejeição de ações de respostas antigas por cenário/filtros/produto; verificações em `check_pricing_assistant.py`.

- Cenários mock conectados: estado puro por sessão com baseline/aplicado/rascunho, simulação atômica, aplicação explícita, descarte e reset.
- Mapeamento declarativo de parâmetros, regras e telas consumidoras; motor compartilhado para comparativo inline, detalhe e dashboards.
- Contrato Dash para eventos locais e stores globais sem dependências de páginas desmontadas; revisão invalida simulações antigas.
- Regressões executáveis sem Dash/banco em `check_demo_scenario.py`. Validação visual do app gerado continua necessária.
- Branding unificado no roadmap, com cor `auto` aceita pelo validador.

## v4.0.0 — 2025-01

### Destaque

Pipeline reformulado para gerar aplicações com **fator "wow"** em demos de cliente: mock data volumétrico (milhares de linhas, sazonalidade, Pareto), app shell completo (login/logout/perfil/breadcrumb), interatividade real (drill-downs, recálculo live, role-aware UI), fidelidade ao roadmap (schema rico + análise de regras de negócio) e verificação de UI em runtime (Playwright).

### Breaking changes

- `roadmap.md` agora segue schema rico (v4) — `roadmap-template.md` e `roadmap-example.md` atualizados. Roadmaps v3 ainda funcionam (fallbacks aplicados), mas a qualidade da geração cai.
- `mock_data/` agora é gerado por `scripts/mock_generator.py` a partir de `docs/mock_spec.yaml` — não mais escrito à mão pelo LLM. Step 4 do data-engineer delega a `skill04-mock-data.md`.
- `database/seed.sql` agora é gerado pelo `mock_generator.py` no Step 4 — Step 5 apenas valida/ajusta (`skill05-sql-seed.md`).
- `frontend/pages/<page>/_queries.py` agora lê via `api_client.py` com flag `USE_API` (mock/live) — não lê CSV diretamente.
- `skill07-dash-page.md` reescrito para usar `app_shell_with_workflow` — não renderiza sidebar/login manualmente.

### Novos agentes

- **`ui-reviewer`** (Fase 3, sob demanda): roda smoke test Playwright contra o frontend em execução. Captura Traceback no DOM, callbacks que estouram, componentes ausentes, sidebar sem badge, role restriction não aplicada. Reporta arquivos a investigar (não corrige).

### Novas skills/commands

- `skill-shell.md` — shell global (sidebar, login, breadcrumb, user_badge, offcanvas)
- `skill-analytics.md` — agregações/KPIs/charts para telas analytics
- `skill-auth.md` — auth JWT completa (registro, password reset, role-based access)
- `skill-workflow-definition.md` — workflows multi-step com navegação contextual
- `skill-api-contracts.md` — contratos de API declarativos
- `skill-business-logic.md` — análise de regras de negócio (validation/derived_field/interactive_formula/workflow_rule)
- `skill04-mock-data.md` — geração volumétrica de mock data (motor + spec)
- `roadmap-import.md` — importar roadmap rico a partir de briefing

### Novos templates

- `mock_generator.py` — motor volumétrico (pandas/numpy): enum/faixa/normal/pareto/sazonal+tendencia/derivado/lista(BR:...)/fk/bcrypt/audit/json/codigo/email/texto. Gera CSV+JSON por entidade + `seed.sql` em ordem topológica de FKs. Validador integrado (`--validate`).
- `api_client.py` — cliente API com flag `USE_API` (mock/live) e cache opcional.
- `workflow_components.py` — componentes de workflow multi-step (stepper, contextual nav).
- `scripts/ui_smoke.py` — smoke test Playwright (login, descoberta de páginas, checks por página, sidebar badge, role restriction).

### Skills atualizadas

- `skill00-validator.md` — Etapa 0 (roadmap rico), Etapa 4 (volume + garantias de demo), Etapa 5 (seed gerado pelo motor), Etapa 7 (fórmulas interativas + campos derivados).
- `skill01-requirements.md` — schema alinhado ao roadmap v4 (entities[].demo.distributions, modules[].layout, drilldowns, simulation_params, sidebar_badge, recalc_mode, empty_state).
- `skill06-screen-definition.md` — schema único de screens, novos screen_types (analytics, simulation, approval_queue, master_detail).
- `skill07-dash-page.md` — usa `app_shell_with_workflow`, não renderiza sidebar/login manualmente.
- `skill08-dash-callback.md` — padrões 8-13 (drill-down, live recalc, role-aware UI, workflow nav, offcanvas, confirm dialog, empty state, sidebar badge).
- `skill11-fastapi.md` — endpoints de agregação (KPIs, séries temporais, rankings, distribuições).

### Agentes atualizados

- `data-engineer.md` — Step 0 (validação roadmap rico), Step 1 (requirements com demo.distributions), Step 2.6 (api_contracts), Step 2.7 (business_logic), Step 4 (motor volumétrico), Step 5 (validação/ajuste do seed).
- `frontend-builder.md` — reescrito como índice operacional (aponta para skills especializadas).
- `backend-builder.md` — novos pré-requisitos (api_contracts, business_logic) + step de analytics.
- `lighthouse.md` — Fase 3 (ui-reviewer sob demanda), Passo 5, atualização do relatório final.

### Design system

- `design-system.yaml` — novos tokens (offcanvas, confirm dialog, breadcrumb, user_badge, empty_state, workflow stepper).
- `theme.css` — variáveis CSS para novos componentes.
- `components-library.py` — novos componentes: `kpi_card`, `data_table`, `empty_state`, `offcanvas`, `confirm_dialog`, `user_badge`, `breadcrumb`, `app_shell_with_workflow`.
- `charts-library.py` — novos charts: `heatmap`, `treemap`, `combo`, `sparkline`, `funnel`, `gauge`. Styling consistente via `_base_layout`.
- `GUIA-VISUAL-PMZ.md` / `SKILL.md` (ui-ux-pro-max) — regras para novos componentes e charts.

### Outros

- `project-init.md` — cria `scripts/` e `tests/frontend_unit/` na estrutura inicial.
- `PROJECTS.md` — sem mudança de schema (continua rastreando status por projeto).
- `CLAUDE.md` — estrutura e regras atualizadas para v4.

### Dependências dev-only (não vão para produção)

- `playwright` + `playwright install chromium` — para `ui_smoke.py` (Fase 3).
- `bcrypt` (opcional) — para `mock_generator.py` gerar `senha_hash` realista (fallback: hash fixo de demo).
