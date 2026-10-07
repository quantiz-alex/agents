# Sistema Lighthouse — Geração Automática de Aplicações Full-Stack

O build também gera automaticamente um **Assistente de Pricing local**, adaptado ao roadmap de cada projeto: catálogo de análises, cálculos Python sobre dados mock, perguntas sugeridas e ações para abrir detalhes ou simular propostas. Não exige API de IA nem comando adicional. As análises usam apenas campos/fórmulas disponíveis; limitações são registradas. O cenário só muda após aplicação explícita. Configuração opcional em `## Assistente de Pricing` do roadmap; geração descrita em `.claude/commands/skill-pricing-assistant.md`.

Pipeline orquestrado por **subagents especializados** que gera aplicações completas (Dash + FastAPI + SQL Server) a partir de um único arquivo `roadmap.md`. **v4.0.0** — mock data volumétrico, app shell completo, interatividade real, fidelidade ao roadmap e verificação de UI em runtime.

---

## 🚀 Como Iniciar um Novo Projeto (passo a passo)

### Passo 1 — Criar o projeto

No Claude Code, a partir de qualquer diretório dentro de `projetos/`:

```
/project-init Sistema de Gestão Comercial
```

Isso cria `../sistema-de-gestao-comercial/` com toda a estrutura de pastas, bibliotecas UI/UX copiadas e um `roadmap.md` template, e registra o projeto em `PROJECTS.md`.

### Passo 2 — Preencher o roadmap.md

Abra `../sistema-de-gestao-comercial/roadmap.md` e substitua todos os `TODO:`:
- **Descrição** — o que o sistema faz, qual problema resolve, quem usa
- **Branding** — cores, logo, nome na sidebar, tagline
- **Contexto de Demonstração** — persona, story, números-âncora, período, credenciais de demo
- **Perfis de Acesso** — roles e permissões
- **Módulos** — cada módulo com prioridade, tipo de tela, layout, KPIs, gráficos, filtros, drill-downs, features `[F-NNN]` e regras de negócio `[RN-NNN]` (com tipo/fórmula/variáveis/campos de saída)
- **Entidades de Dados** — papel (dimensão/fato/apoio), volumetria de demo, distribuições por campo, exemplo de linha
- **Requisitos Não-Funcionais** — performance, segurança, escalabilidade

> 💡 Este é o **único arquivo que você escreve**. Todo o resto é gerado. Quanto mais detalhado o roadmap (especialmente `distributions` e `business_rules` estruturadas), melhor o resultado. Veja `../.claude/templates/roadmap-example.md` para um exemplo preenchido.
> 💡 Alternativa: `/roadmap-import` a partir de um briefing em texto livre — gera a estrutura rica do roadmap automaticamente.

### Passo 3 — Rodar o build delegado

Navegue para o diretório do projeto e execute:

```
cd ../sistema-de-gestao-comercial
/lighthouse
```

O orquestrador executa:

```
FASE 1  data-engineer       roadmap → requirements → data model → env →
                            api contracts → business logic → SQL →
                            mock data VOLUMÉTRICO (motor) → seed
           ↓ (só avança com STATUS: success)
FASE 2  frontend-builder ┐  design system → screens → páginas Dash →
        backend-builder  ┘  EM PARALELO: app shell + sidebar + login + callbacks
                            5 camadas por entidade → auth JWT → agregações → README
```

### Passo 4 — Rodar e validar com o cliente

```bash
cp .env.example .env                  # preencher credenciais (ou manter USE_SQLITE=true p/ dev)
pip install -r requirements.txt
uvicorn backend.main:app --reload     # API  → http://localhost:8000
python -m frontend.app                # UI   → http://localhost:1050
```

**(Opcional) Validar a UI em runtime** — captura bugs que a validação estática não vê:

```bash
pip install playwright && playwright install chromium   # dev-only
# em outro terminal, com o frontend rodando:
"revise a UI"          # → ui-reviewer roda smoke Playwright
```

O **ui-reviewer** (Fase 3, sob demanda) verifica em runtime: login flui, cada página carrega sem Traceback no DOM, componentes esperados presentes (grid/KPIs/charts/filtros), callbacks não estouram no console, sidebar badge de approval_queue mostra número, role restriction aplicada. Reporta arquivos a investigar (não corrige).

Apresente o sistema ao cliente. Ajustes de tela? Peça em linguagem natural:
- *"regenere a página aprovacao com filtro por data"* → frontend-builder
- *"adicione a entidade descontos no backend"* → backend-builder

### Passo 5 — Gerar os testes (após aprovação do cliente)

Os testes **NÃO** rodam no build automático — são uma etapa separada, acionada quando o processo foi validado:

```
"gere os testes do projeto"        → projeto inteiro, cobertura ≥85%
"teste a página aprovacao"         → escopo de uma página (após refatoração)
"teste a entidade produto"         → escopo de uma entidade
```

O **test-writer** lê o código gerado, cria testes unitários Pytest (backend + páginas/callbacks/queries do frontend) e specs E2E Cypress, mede a cobertura com `pytest-cov` e itera até atingir **≥85% de linhas** no escopo — ou reporta exatamente o que ficou descoberto e por quê.

```bash
pytest tests/ --cov=backend --cov=frontend --cov-report=html -v
cd tests/frontend && npm install && npm run cy:run
```

---

## 🏗 Arquitetura

```
projetos/
├── .claude/                       ← config compartilhada (este diretório)
│   ├── agents/                    ← SUBAGENTS (contexto isolado, paralelizáveis)
│   │   ├── data-engineer.md       ← Fase 1: camada de dados (roadmap → mock volumétrico)
│   │   ├── frontend-builder.md    ← Fase 2a: UI Dash + app shell         ┐ rodam em
│   │   ├── backend-builder.md     ← Fase 2b: API FastAPI + JWT + agg     ┘ PARALELO
│   │   ├── ui-reviewer.md         ← Fase 3: smoke Playwright em runtime (sob demanda)
│   │   └── test-writer.md         ← STANDALONE: testes sob demanda, cobertura ≥85%
│   ├── commands/
│   │   ├── lighthouse.md          ← orquestrador (delega via Agent tool, 3 fases)
│   │   ├── project-init.md        ← cria novo projeto
│   │   ├── roadmap-import.md      ← importar roadmap rico de briefing
│   │   ├── skill-shell.md         ← shell global (sidebar/login/breadcrumb)
│   │   ├── skill-analytics.md     ← agregações/KPIs/charts de analytics
│   │   ├── skill-auth.md          ← auth JWT completa (registro, reset, roles)
│   │   ├── skill-workflow-definition.md ← workflows multi-step
│   │   ├── skill-api-contracts.md ← contratos de API
│   │   ├── skill-business-logic.md ← análise de regras de negócio
│   │   ├── build.md               ← pipeline sequencial legado (fallback)
│   │   ├── build-parallel.md      ← pipeline paralelo legado (fallback)
│   │   └── skill0*.md             ← especificações de referência (lidas pelos agentes)
│   ├── templates/
│   │   ├── roadmap-template.md    ← fonte única do template de roadmap (schema v4)
│   │   ├── roadmap-example.md     ← exemplo preenchido
│   │   ├── components-library.py  ← componentes Dash (kpi/data_table/offcanvas/...)
│   │   ├── charts-library.py      ← gráficos Plotly (heatmap/treemap/combo/...)
│   │   ├── mock_generator.py      ← motor volumétrico de mock data
│   │   ├── api_client.py          ← cliente API com flag USE_API (mock/live)
│   │   ├── workflow_components.py ← componentes de workflow multi-step
│   │   └── scripts/ui_smoke.py    ← smoke test Playwright (dev-only)
│   ├── skills/
│   │   └── ui-ux-pro-max/         ← guia de UI/UX para Dash (SKILL.md + GUIA-VISUAL-PMZ.md)
│   ├── design-system.yaml         ← tokens de design centralizados
│   └── PROJECTS.md                ← registro de todos os projetos
│
├── <projeto-a>/                   ← cada projeto é um diretório irmão
│   ├── roadmap.md                 ← ÚNICO arquivo escrito manualmente
│   ├── .build/checkpoints/        ← estado e retomada do build
│   ├── docs/                      ← requirements, data_model, mock_spec, screens, business_logic, api_contracts (YAML)
│   ├── database/                  ← schema, views, procedures, seed (SQL)
│   ├── mock_data/                 ← <entidade>.csv + .json (volumétrico, milhares de linhas)
│   ├── scripts/                   ← mock_generator.py, generate_mock.py, ui_smoke.py
│   ├── frontend/                  ← app Dash (app shell + pages/ + components/)
│   ├── backend/                   ← API FastAPI (5 camadas + auth + agregações)
│   └── tests/                     ← pytest (backend/, frontend_unit/) + cypress (frontend/)
└── <projeto-b>/
```

### Responsabilidades dos agentes

| Agente | Quando roda | Gera | Não toca em |
|--------|-------------|------|-------------|
| **data-engineer** | Fase 1 do `/lighthouse` | requirements, data model, config/env, api contracts, business logic, SQL, **mock data volumétrico** (motor), seed | frontend/, rotas backend, testes |
| **frontend-builder** | Fase 2 (paralelo) | design system, screens, 4 arquivos por página, **app shell** (sidebar/login/breadcrumb/user_badge), callbacks (drill-down/live recalc/role-aware) | backend/, SQL, testes |
| **backend-builder** | Fase 2 (paralelo) | 5 camadas por entidade, **agregações** (KPIs/séries/rankings), main.py, auth JWT completa, requirements.txt, README do projeto | frontend/* (exceto bloco comentado no login), SQL, testes |
| **ui-reviewer** | **Fase 3 (sob demanda)** | relatório de smoke Playwright em runtime (Traceback no DOM, callbacks que estouram, componentes ausentes, sidebar badge, role restriction) | código de produção (falhas são reportadas, não corrigidas) |
| **test-writer** | **Sob demanda** (fora do fluxo) | pytest unitários (backend + frontend), Cypress E2E, relatório de cobertura | código de produção (bugs são reportados, não corrigidos) |

### Contrato entre orquestrador e agentes

Cada agente detecta o próprio estado no disco (nunca regenera o que já existe), cria checkpoints em `.build/checkpoints/` e termina retornando um relatório com `STATUS: success | partial | failed | blocked`. O `/lighthouse` só avança de fase com `success`.

---

## 📋 Stack Tecnológico — FIXO E INEGOCIÁVEL

> ⚠️ **Todo projeto gerado é 100% Python.** O stack abaixo é fixo — os agentes estão instruídos a NUNCA introduzir outra tecnologia (React, Vue, Streamlit, Node.js, Django, Flask, etc.). Se um requisito parecer exigir algo fora do stack, o agente implementa a alternativa mais próxima em Dash/Python e registra um aviso.

### Frontend (exclusivamente)

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Framework | **Dash** | 2.14+ |
| UI Components | **Dash Bootstrap Components** | — |
| Tabelas | **Dash AG Grid** | — |
| Gráficos | **Plotly** | — |
| Processamento de Dados | **Pandas, NumPy** | — |

Toda a UI é declarada em Python via componentes Dash — sem arquivos `.html`, `.css` ou `.js` customizados, sem frameworks JavaScript.

### Backend e Infraestrutura

| Camada | Tecnologia |
|--------|-----------|
| API | FastAPI + SQLAlchemy + Pydantic v2 |
| Banco de Dados | SQL Server / Microsoft Fabric (fallback SQLite em dev) |
| Autenticação | JWT (python-jose + bcrypt) |
| Testes | Pytest + pytest-cov (≥85% linhas) + Cypress E2E* |
| Design System | Centralizado em YAML |
| UI Runtime Verification | Playwright (dev-only, Fase 3) |

*\*Cypress (JavaScript) e Playwright (Python via bindings) são as únicas exceções ao Python no projeto — usados apenas para testes, nunca para código de produção.*

---

## 🔄 Fluxos Alternativos

### Retomar um build interrompido
```
cd ../<projeto>
/lighthouse              # detecta o estado no disco e continua de onde parou
```

### Rodar apenas uma fase
```
/lighthouse data         # só camada de dados
/lighthouse frontend     # só UI
/lighthouse backend      # só API
```

### Pedir um agente em linguagem natural (sem lighthouse)
```
"gere a camada de dados"
"regenere o frontend"
"adicione a entidade produto no backend"
"revise a UI"            # → ui-reviewer (exige frontend rodando)
"teste a página dashboard"
```

### Pipelines legados (sem delegação — tudo no contexto principal)
```
/build                   # sequencial, 13 etapas com validação e checkpoints
/build-parallel          # paralelo por DAG de dependências
/build --rollback step-3 # reverter para checkpoint
/skill00-validator step2 # validar uma etapa específica
```

Os comandos legados permanecem 100% funcionais e compatíveis — os checkpoints são o mesmo formato, então é possível começar com `/build` e retomar com `/lighthouse` (e vice-versa).

---

## 🔧 Troubleshooting

| Problema | Solução |
|----------|---------|
| `/lighthouse` parou na Fase 1 com roadmap inválido | Verificar seções obrigatórias: título `#`, `## Módulos` (≥1 feature), `## Entidades de Dados` (≥1 entidade). Rodar `/skill00-validator step0` para diagnóstico. |
| Agente reportou `STATUS: blocked` | Pré-requisito faltando — rodar a fase anterior indicada na mensagem |
| Mock data incompleto (falta .csv ou .json) | Rodar `/lighthouse data` — o agente regenera apenas as entidades faltantes via `scripts/generate_mock.py` |
| Mock data "parece brinquedo" (poucas linhas, Top 10 com 8 barras) | Verificar `docs/mock_spec.yaml` — aumentar `volume` e ajustar `distributions` (Pareto/sazonal). Regenerar com `python scripts/generate_mock.py` |
| UI com Traceback no DOM | Rodar Fase 3: inicie o frontend (`python -m frontend.app`) e peça "revise a UI" — o ui-reviewer aponta o arquivo e a linha |
| Testes com 401 em tudo | O conftest precisa de override do `get_current_user` — o test-writer já trata; se persistir, pedir "corrija o conftest de auth" |
| Cobertura abaixo de 85% | Ver no relatório do test-writer quais linhas ficaram descobertas e o motivo |
| Subagents não aparecem | A sessão do Claude Code deve ser iniciada dentro de `projetos/` ou de um projeto (o `.claude/agents/` é descoberto no diretório pai) |

---

## 📝 Changelog

### v4.0.0 (2025-01) — Wow Factor para Demos de Cliente
- ✨ **Mock data volumétrico**: motor `mock_generator.py` gera milhares de linhas com sazonalidade, Pareto, FKs coerentes, catálogos pt-BR — a partir de `docs/mock_spec.yaml` declarativo (não mais escrito à mão pelo LLM)
- ✨ **App shell completo**: sidebar, login/logout, perfil, breadcrumb, user_badge, offcanvas, confirm dialog — via `skill-shell.md` e `app_shell_with_workflow`
- ✨ **Interatividade real**: drill-downs gráficos, recálculo live (simulation), role-aware UI, workflows multi-step com navegação contextual — padrões 8-13 em `skill08-dash-callback.md`
- ✨ **Fidelidade ao roadmap**: schema rico (v4) com `distributions`, `business_rules` estruturadas (tipo/fórmula/variáveis/campos de saída), `layout`, `drilldowns`, `simulation_params`, `sidebar_badge` — análise dedicada em `skill-business-logic.md`
- ✨ **Verificação de UI em runtime**: agente `ui-reviewer` (Fase 3) roda smoke Playwright contra o frontend em execução — captura Traceback no DOM, callbacks que estouram, componentes ausentes, sidebar sem badge, role restriction não aplicada
- ✨ **Novas skills**: skill-shell, skill-analytics, skill-auth, skill-workflow-definition, skill-api-contracts, skill-business-logic, skill04-mock-data (motor)
- ✨ **Novos templates**: mock_generator.py, api_client.py (flag USE_API), workflow_components.py, scripts/ui_smoke.py
- ✨ **Novos componentes**: kpi_card, data_table, empty_state, offcanvas, confirm_dialog, user_badge, breadcrumb, app_shell_with_workflow
- ✨ **Novos charts**: heatmap, treemap, combo, sparkline, funnel, gauge
- ✨ **Backend com agregações**: endpoints de KPIs, séries temporais, rankings, distribuições
- ✨ **Auth JWT completa**: registro, password reset, role-based access
- ♻️ skill07 reescrito (usa app_shell_with_workflow), skill06 (schema único de screens), skill11 (analytics), frontend-builder (índice operacional), backend-builder (pré-requisitos + analytics)
- Veja `CHANGELOG.md` para detalhes completos.

### v3.0.0 (2026-06-12) — Arquitetura Delegated Lighthouse
- ✨ Subagents nativos em `.claude/agents/` (data-engineer, frontend-builder, backend-builder, test-writer) — contexto isolado por agente
- ✨ `/lighthouse` — orquestrador que delega via Agent tool; frontend + backend em **paralelo real**
- ✨ `/project-init` — criação de projetos com estrutura completa + registro em `PROJECTS.md`
- ✨ test-writer **standalone** (fora do fluxo de build): roda sob demanda após validação com o cliente, com meta de **cobertura ≥85%** (pytest-cov, loop iterativo) e testes unitários também para o frontend (queries, components, callbacks)
- ✨ `templates/roadmap-template.md` — fonte única do template (deduplicado de 3 arquivos)
- ✨ `PROJECTS.md` — gestão centralizada de projetos
- ♻️ `/build` e `/build-parallel` mantidos como fallback, inalterados

### v2.0.0 (2024-06-03) — Melhorias Críticas
- ✨ skill00-validator, build-parallel (3x mais rápido), skill13-integration-tests
- ✨ Design system centralizado, checkpoints/rollback, extended thinking
- ⚡ Limite de tokens 2.000 → 8.000 por skill

### v1.0.0 — Versão Original
- ✅ Pipeline sequencial básico com 12 skills

---

**Versão**: 4.0.0
**Última atualização**: 2025-01
**Mantido por**: Quantiz Pricing Solution
