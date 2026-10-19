# Lighthouse Pipeline — Workspace (v5)

Este workspace é o **pipeline de geração automática de aplicações Full-Stack** (Dash + FastAPI + SQL Server) da Quantiz Pricing Solution. Projeto de referência: `qwizer-pricing-vibe-code`.

## Estrutura

```
agent-vibe-code-pricing/       ← workspace raiz (abrir aqui no Claude Code)
├── CLAUDE.md                  ← este arquivo
├── README.md                  ← documentação completa do pipeline
├── docs/PLANO_MELHORIA_V5.md  ← plano e decisões da v5
│
├── .claude/
│   ├── rules/core.md          ← REGRAS CENTRAIS (fonte única) — todo agente lê primeiro
│   ├── agents/                ← subagents (modelo definido no frontmatter)
│   │   ├── data-engineer.md   ← Fase 1 (Sonnet): roadmap → mock volumétrico → docs/handoff.md
│   │   ├── frontend-builder.md ← Fase 2a (Opus): UI Dash + Assistente de Pricing (paralelo)
│   │   ├── backend-builder.md ← Fase 2b (Sonnet): API FastAPI (paralelo)
│   │   ├── ui-reviewer.md     ← Fase 3 (Sonnet, sob demanda): smoke Playwright — só reporta
│   │   ├── frontend-fixer.md  ← Fase 3 (Sonnet, sob demanda): corrige só os arquivos apontados
│   │   └── test-writer.md     ← STANDALONE (Sonnet): testes pytest + cypress sob demanda
│   ├── commands/              ← /lighthouse, /project-init, /roadmap-import + skills de referência
│   ├── templates/             ← copiados com `cp` para os projetos
│   │   ├── LIBRARY_INDEX.md   ← índice das bibliotecas (ler ISTO, não o código-fonte)
│   │   ├── components-library.py, charts-library.py, workflow_components.py, page_common.py, api_client.py
│   │   ├── pricing_assistant.py, assistant_llm.py, assistant_detail.py, assistant_pages.py,
│   │   │   assistant_callbacks.py, pricing_assistant_components.py   ← Assistente híbrido (todo projeto)
│   │   ├── tests/             ← conftest + teste genérico do assistente
│   │   └── scripts/           ← validate_project.py, split_screens.py, build_library_index.py, check_*.py, ui_smoke.py
│   ├── skills/ui-ux-pro-max/  ← guia de UI/UX (consultar só o checklist §8 do GUIA)
│   ├── archive/               ← pipelines antigos (/build, /build-parallel) — não usar
│   ├── design-system.yaml     ← tokens de design
│   └── PROJECTS.md            ← registro dos projetos gerados
│
└── <projeto-slug>/            ← projetos gerados (aqui ou em pasta irmã: `.build/project.json → lighthouse_home`)
```

## Fluxo rápido

```
/project-init Nome do Projeto    # cria estrutura + roadmap template + registra lighthouse_home
# editar <slug>/roadmap.md       # preencher TODOs (ou /roadmap-import)
cd <slug>
/lighthouse                      # dados → front + back em paralelo
# (opcional) "revise a UI" → ui-reviewer; falhas → frontend-fixer
# (opcional) após validação com o cliente → "gere os testes" → test-writer
```

## Regras do workspace
- **Regras e decisões padronizadas:** `.claude/rules/core.md`. Se outro arquivo contradisser, vale o core.
- **Economia de tokens:**
  - Templates sempre copiados com `cp`.
  - Agentes leem o índice da biblioteca, o `docs/handoff.md` e o recorte `docs/screens/<slug>.yaml`, nunca os YAMLs inteiros por tela.
  - Validações rodam por script.
- **Após mudar qualquer template:** `python .claude/templates/scripts/build_library_index.py`.
- **Execução sob demanda:**
  - test-writer é standalone.
  - ui-reviewer exige o frontend rodando.
  - Correções pontuais ficam com o frontend-fixer, não com o frontend-builder.
- **Playwright** é dev-only (`requirements-dev.txt`).
