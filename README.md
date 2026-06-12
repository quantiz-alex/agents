# Sistema Lighthouse — Geração Automática de Aplicações Full-Stack

Pipeline orquestrado por **subagents especializados** que gera aplicações completas (Dash + FastAPI + SQL Server) a partir de um único arquivo `roadmap.md`.

---

## 🚀 Como Iniciar um Novo Projeto (passo a passo)

### Passo 1 — Criar o projeto

No Claude Code, a partir de qualquer diretório dentro de `projetos/`:

```
/project-init Sistema de Gestão Comercial
```

Isso cria `../sistema-de-gestao-comercial/` com toda a estrutura de pastas e um `roadmap.md` template, e registra o projeto em `PROJECTS.md`.

### Passo 2 — Preencher o roadmap.md

Abra `../sistema-de-gestao-comercial/roadmap.md` e substitua todos os `TODO:`:
- **Descrição** — o que o sistema faz, qual problema resolve, quem usa
- **Módulos** — cada módulo com prioridade, funcionalidades `[F-NNN]` e regras de negócio `[RN-NNN]`
- **Entidades de Dados** — uma linha por entidade com descrição e módulo
- **Requisitos Não-Funcionais** — performance, segurança, escalabilidade

> 💡 Este é o **único arquivo que você escreve**. Todo o resto é gerado. Quanto mais detalhado o roadmap, melhor o resultado.

### Passo 3 — Rodar o build delegado

Navegue para o diretório do projeto e execute:

```
cd ../sistema-de-gestao-comercial
/lighthouse
```

O orquestrador executa:

```
FASE 1  data-engineer       roadmap → requirements → data model → env →
                            api contracts → SQL → mock data → seed
           ↓ (só avança com STATUS: success)
FASE 2  frontend-builder ┐  design system → telas → páginas Dash → app + sidebar + login
        backend-builder  ┘  EM PARALELO: 5 camadas por entidade → auth JWT → README
```

### Passo 4 — Rodar e validar com o cliente

```bash
cp .env.example .env                  # preencher credenciais (ou manter USE_SQLITE=true p/ dev)
pip install -r requirements.txt
uvicorn backend.main:app --reload     # API  → http://localhost:8000
python frontend/app.py                # UI   → http://localhost:8050
```

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
│   │   ├── data-engineer.md       ← Fase 1: camada de dados completa
│   │   ├── frontend-builder.md    ← Fase 2a: UI Dash               ┐ rodam em
│   │   ├── backend-builder.md     ← Fase 2b: API FastAPI + JWT     ┘ PARALELO
│   │   └── test-writer.md         ← STANDALONE: testes sob demanda, cobertura ≥85%
│   ├── commands/
│   │   ├── lighthouse.md          ← orquestrador (delega via Agent tool)
│   │   ├── project-init.md        ← cria novo projeto
│   │   ├── build.md               ← pipeline sequencial legado (fallback)
│   │   ├── build-parallel.md      ← pipeline paralelo legado (fallback)
│   │   └── skill*.md              ← especificações de referência (lidas pelos agentes)
│   ├── templates/
│   │   └── roadmap-template.md    ← fonte única do template de roadmap
│   ├── design-system.yaml         ← tokens de design centralizados
│   ├── PROJECTS.md                ← registro de todos os projetos
│   └── README.md                  ← este arquivo
│
├── <projeto-a>/                   ← cada projeto é um diretório irmão
│   ├── roadmap.md                 ← ÚNICO arquivo escrito manualmente
│   ├── .build/checkpoints/        ← estado e retomada do build
│   ├── docs/                      ← requirements, data_model, screens, contracts (YAML)
│   ├── database/                  ← schema, views, procedures, seed (SQL)
│   ├── mock_data/                 ← <entidade>.csv + .json
│   ├── frontend/                  ← app Dash (pages/, components/)
│   ├── backend/                   ← API FastAPI (5 camadas por entidade + auth)
│   └── tests/                     ← pytest (backend/, frontend_unit/) + cypress (frontend/)
└── <projeto-b>/
```

### Responsabilidades dos agentes

| Agente | Quando roda | Gera | Não toca em |
|--------|-------------|------|-------------|
| **data-engineer** | Fase 1 do `/lighthouse` | requirements, data model, config/env, api contracts, SQL, mock data, seed | frontend/, rotas backend, testes |
| **frontend-builder** | Fase 2 (paralelo) | design system, screens, 4 arquivos por página, app, sidebar, login | backend/, SQL, testes |
| **backend-builder** | Fase 2 (paralelo) | 5 camadas por entidade, main.py, auth JWT, requirements.txt, README do projeto | frontend/* (exceto bloco comentado no login), SQL, testes |
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

*\*Cypress (JavaScript) é a única exceção ao Python no projeto — usado apenas para testes E2E, nunca para código de produção.*

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
| `/lighthouse` parou na Fase 1 com roadmap inválido | Verificar seções obrigatórias: título `#`, `## Módulos` (≥1 feature), `## Entidades de Dados` (≥1 entidade) |
| Agente reportou `STATUS: blocked` | Pré-requisito faltando — rodar a fase anterior indicada na mensagem |
| Mock data incompleto (falta .csv ou .json) | Rodar `/lighthouse data` — o agente regenera apenas as entidades faltantes |
| Testes com 401 em tudo | O conftest precisa de override do `get_current_user` — o test-writer já trata; se persistir, pedir "corrija o conftest de auth" |
| Cobertura abaixo de 85% | Ver no relatório do test-writer quais linhas ficaram descobertas e o motivo |
| Subagents não aparecem | A sessão do Claude Code deve ser iniciada dentro de `projetos/` ou de um projeto (o `.claude/agents/` é descoberto no diretório pai) |

---

## 📝 Changelog

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

**Versão**: 3.0.0
**Última atualização**: 2026-06-12
**Mantido por**: Quantiz Pricing Solution
