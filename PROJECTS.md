# Projetos

Registro de todos os projetos gerenciados pelo pipeline Delegated Lighthouse.

## Como Usar

```bash
# Criar novo projeto
/project-init Nome do Projeto

# Navegar e iniciar o build delegado
cd ../nome-do-projeto
/lighthouse

# Ou executar um agente específico em linguagem natural:
# "gere a camada de dados", "regenere o frontend",
# "adicione a entidade produto no backend", "crie os testes"
```

---

## Projetos Ativos

| Projeto | Slug | Status | Última Atividade |
|---------|------|--------|-----------------|
| _(nenhum projeto ainda — use `/project-init` para criar)_ | — | — | — |

---

## Status Legend

| Ícone | Significado |
|-------|-------------|
| 🟡 | Aguardando preenchimento do roadmap.md |
| 🔵 | Build em andamento |
| 🟢 | Build concluído com sucesso |
| 🔴 | Build com erros — verificar relatórios dos agentes |
| ⏸ | Em pausa — retomar com `/lighthouse` |

---

## Arquitetura do Pipeline

```
.claude/
├── agents/                    ← Subagents (contexto isolado, paralelizáveis)
│   ├── data-engineer.md       ← Fase 1: roadmap → requirements → data model → SQL → mock → seed
│   ├── frontend-builder.md    ← Fase 2a: design system → screens → páginas Dash → app ┐ paralelo
│   ├── backend-builder.md     ← Fase 2b: FastAPI 5 camadas → auth JWT → README       ┘
│   └── test-writer.md         ← STANDALONE (fora do fluxo): pytest + cypress, cobertura ≥85%
│                                 rodar sob demanda, após validação com o cliente
├── commands/
│   ├── lighthouse.md          ← Orquestrador: delega via Agent tool
│   ├── project-init.md        ← Cria novo projeto a partir do template
│   ├── build.md               ← Pipeline sequencial legado (fallback)
│   ├── build-parallel.md      ← Pipeline paralelo legado (fallback)
│   └── skill*.md              ← Especificações de referência (lidas pelos agentes)
├── templates/
│   └── roadmap-template.md    ← Fonte única do template de roadmap
├── design-system.yaml
└── PROJECTS.md                ← este arquivo
```

## Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `/project-init <nome>` | Cria novo projeto com estrutura completa e roadmap template |
| `/lighthouse` | Orquestrador: Fase 1 (dados) → Fase 2 (front+back em paralelo). NÃO inclui testes |
| `/lighthouse data\|frontend\|backend` | Executa apenas uma fase específica |
| "gere os testes do projeto" | test-writer standalone: pytest + cypress, cobertura ≥85% (após validação com cliente) |
| "teste a página `<page>`" | test-writer com escopo de uma página (após refatoração/aprovação) |
| `/build` | Pipeline sequencial legado (sem delegação) |
| `/build-parallel` | Pipeline paralelo legado (sem delegação) |
