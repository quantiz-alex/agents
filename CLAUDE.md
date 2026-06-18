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
│   │   ├── data-engineer.md   ← Fase 1: camada de dados
│   │   ├── frontend-builder.md ← Fase 2a: UI Dash (paralelo)
│   │   ├── backend-builder.md ← Fase 2b: API FastAPI (paralelo)
│   │   └── test-writer.md     ← STANDALONE: testes sob demanda
│   ├── commands/              ← slash commands disponíveis
│   │   ├── lighthouse.md      ← /lighthouse — orquestrador principal
│   │   ├── project-init.md    ← /project-init — criar novo projeto
│   │   ├── build.md           ← /build — pipeline sequencial legado
│   │   ├── build-parallel.md  ← /build-parallel — pipeline paralelo legado
│   │   └── skill*.md          ← especificações de referência (lidas pelos agentes)
│   ├── templates/
│   │   └── roadmap-template.md ← fonte única do template de roadmap
│   ├── skills/
│   │   └── ui-ux-pro-max/     ← guia de UI/UX para Dash
│   ├── design-system.yaml     ← tokens de design centralizados
│   └── PROJECTS.md            ← registro de todos os projetos gerados
│
└── <projeto-slug>/            ← projetos gerados (criados por /project-init)
    ├── roadmap.md             ← único arquivo escrito manualmente
    ├── docs/                  ← YAMLs gerados (requirements, data_model, screens)
    ├── database/              ← SQL gerado (schema, views, procedures, seed)
    ├── mock_data/             ← dados de teste (CSV + JSON por entidade)
    ├── frontend/              ← UI Dash completa
    ├── backend/               ← API FastAPI (5 camadas + auth JWT)
    └── tests/                 ← Pytest + Cypress
```

## Fluxo Rápido

```
/project-init Nome do Projeto    # cria estrutura + roadmap template
# editar <slug>/roadmap.md
cd <slug>
/lighthouse                      # build completo (dados → front+back em paralelo)
```

## Regras do Workspace

- **Stack 100% Python**: Dash 2.14+, FastAPI, SQLAlchemy, Pydantic v2, SQL Server
- **Projetos ficam DENTRO deste workspace**: cada projeto é um subdiretório
- **Nunca edite `.claude/` manualmente** exceto para melhorar este pipeline
- **test-writer é STANDALONE**: não roda automaticamente — solicitar explicitamente após validação com o cliente
