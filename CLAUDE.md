# Lighthouse Pipeline — Workspace

Este workspace é o **pipeline de geração automática de aplicações Full-Stack** (Dash + FastAPI + SQL Server) da Quantiz Pricing Solution.

## Estrutura

```
agent-vibe-code-pricing/       ← workspace raiz (abrir aqui no Claude Code)
├── CLAUDE.md                  ← este arquivo
├── README.md                  ← documentação completa do pipeline
├── skills-lock.json           ← dependências de skills instaladas
│
├── .claude/
│   ├── agents/                ← subagents (descobertos automaticamente pelo Claude Code)
│   │   ├── data-engineer.md   ← Fase 1: camada de dados (roadmap → mock volumétrico)
│   │   ├── frontend-builder.md ← Fase 2a: UI Dash (paralelo)
│   │   ├── backend-builder.md ← Fase 2b: API FastAPI (paralelo)
│   │   ├── ui-reviewer.md     ← Fase 3: smoke Playwright em runtime (sob demanda)
│   │   └── test-writer.md     ← STANDALONE: testes pytest+cypress sob demanda
│   ├── commands/              ← slash commands disponíveis
│   │   ├── lighthouse.md      ← /lighthouse — orquestrador (3 fases)
│   │   ├── project-init.md    ← /project-init — criar novo projeto
│   │   ├── roadmap-import.md  ← /roadmap-import — importar roadmap rico
│   │   ├── skill-shell.md     ← shell global (sidebar/login/breadcrumb)
│   │   ├── skill-analytics.md ← agregações/KPIs/charts de analytics
│   │   ├── skill-auth.md      ← auth JWT completa (registro, reset, roles)
│   │   ├── skill-workflow-definition.md ← workflows multi-step com navegação contextual
│   │   ├── skill-api-contracts.md      ← contratos de API
│   │   ├── skill-business-logic.md     ← análise de regras de negócio
│   │   ├── build.md           ← /build — pipeline sequencial legado
│   │   ├── build-parallel.md  ← /build-parallel — pipeline paralelo legado
│   │   └── skill0*.md         ← especificações de referência (lidas pelos agentes)
│   ├── templates/
│   │   ├── roadmap-template.md ← fonte única do template de roadmap
│   │   ├── roadmap-example.md  ← exemplo de roadmap preenchido
│   │   ├── components-library.py ← componentes Dash (kpi/data_table/offcanvas/...)
│   │   ├── charts-library.py    ← gráficos Plotly (heatmap/treemap/combo/...)
│   │   ├── mock_generator.py    ← motor volumétrico de mock data
│   │   ├── api_client.py        ← cliente API com flag USE_API (mock/live)
│   │   ├── workflow_components.py ← componentes de workflow multi-step
│   │   └── scripts/
│   │       └── ui_smoke.py      ← smoke test Playwright (dev-only)
│   ├── skills/
│   │   └── ui-ux-pro-max/     ← guia de UI/UX para Dash (SKILL.md + GUIA-VISUAL-PMZ.md)
│   ├── design-system.yaml     ← tokens de design centralizados
│   └── PROJECTS.md            ← registro de todos os projetos gerados
│
└── <projeto-slug>/            ← projetos gerados (criados por /project-init)
    ├── roadmap.md             ← único arquivo escrito manualmente
    ├── docs/                  ← YAMLs gerados (requirements, data_model, mock_spec, screens, business_logic, api_contracts)
    ├── database/              ← SQL gerado (schema, views, procedures, seed)
    ├── mock_data/             ← dados volumétricos (CSV + JSON por entidade, milhares de linhas)
    ├── scripts/               ← mock_generator.py, generate_mock.py, ui_smoke.py
    ├── frontend/              ← UI Dash completa (app shell + páginas + callbacks + queries)
    ├── backend/               ← API FastAPI (5 camadas + auth JWT + agregações)
    └── tests/                 ← Pytest (unit + integration) + Cypress (E2E)
```

## Fluxo Rápido

```
/project-init Nome do Projeto    # cria estrutura + roadmap template
# editar <slug>/roadmap.md       # preencher TODOs (ou /roadmap-import para estrutura rica)
cd <slug>
/lighthouse                      # build completo (dados → front+back em paralelo)
# (opcional) inicie o frontend e peça "revise a UI" → Fase 3 (ui-reviewer + Playwright)
# (opcional) após validação com cliente → peça "gere os testes" → test-writer
```

## Regras do Workspace

- **Stack 100% Python**: Dash 2.14+, FastAPI, SQLAlchemy, Pydantic v2, SQL Server
- **Projetos ficam DENTRO deste workspace**: cada projeto é um subdiretório
- **Nunca edite `.claude/` manualmente** exceto para melhorar este pipeline
- **test-writer é STANDALONE**: não roda automaticamente — solicitar explicitamente após validação com o cliente
- **ui-reviewer é SOB DEMANDA**: exige frontend rodando (`python -m frontend.app`) — não roda automaticamente após Fase 2
- **Playwright é dev-only**: NÃO adicionar a `requirements.txt` de produção — apenas `requirements-dev.txt`
