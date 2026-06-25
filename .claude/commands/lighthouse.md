# /lighthouse — Orquestrador Delegado (Subagents)

Orquestra o build do projeto delegando para subagents especializados via Agent tool. Cada agente roda em **contexto isolado**; frontend e backend rodam **em paralelo**.

## Argumento opcional

`$ARGUMENTS` — fase inicial para retomar: `data`, `frontend`, `backend`. Se vazio, detecta automaticamente o estado e inicia na primeira fase incompleta.

---

## Arquitetura

```
/lighthouse (você, orquestrador — contexto principal)
   │
   ├── FASE 1: Agent(data-engineer)        ← roadmap → requirements → data model → SQL → mock → seed
   │
   └── FASE 2: Agent(frontend-builder) ┐
               Agent(backend-builder)  ┘   ← EM PARALELO (mesma mensagem, 2 tool calls)

   FORA DO FLUXO (sob demanda, não acionar automaticamente):
   ── Agent(test-writer)                   ← pytest + cypress, cobertura ≥85%
```

Os subagents estão definidos em `.claude/agents/`. Cada um conhece suas regras, detecta o próprio estado no disco e retorna um relatório estruturado com `STATUS:`.

> **test-writer é standalone.** Ele NÃO faz parte do build automático. É invocado separadamente, em geral após a validação do processo com o cliente ou após refatoração/aprovação de telas, para verificar se o projeto está correto — com meta de cobertura ≥85% de linhas. Acione-o apenas quando o usuário pedir explicitamente (ex.: "rode os testes", "gere testes para a página X", "valide o projeto").

---

## Protocolo do Orquestrador

Você (contexto principal) NÃO gera código do projeto — apenas valida, delega, verifica relatórios e consolida. Mantenha seu contexto leve.

### Passo 1 — Pré-validação (antes de delegar)

1. Verificar que `roadmap.md` existe no diretório atual.
   - Se NÃO existir → copiar `../.claude/templates/roadmap-template.md` para `./roadmap.md`, informar o usuário que precisa preenchê-lo e **PARAR**.
   - Se existir mas contiver `TODO:` em seções obrigatórias → avisar e perguntar se deve prosseguir mesmo assim.
2. Detectar estado das fases (cheque rápido, sem ler conteúdo):
   ```
   Fase 1 (data)     completa → docs/data_model.yaml + database/seed.sql existem
                                E mock_data/ tem .csv+.json por entidade
   Fase 2 (frontend) completa → frontend/app.py existe
   Fase 2 (backend)  completa → backend/main.py + backend/auth.py existem
   ```
3. Informar ao usuário quais fases serão executadas e quais serão puladas.

### Passo 2 — Fase 1: data-engineer

Lançar via Agent tool com `subagent_type: "data-engineer"`. Prompt mínimo:

> Execute o pipeline de dados no diretório atual. Detecte o estado dos steps no disco e gere apenas o que falta. Ao final, retorne o relatório estruturado com STATUS.

Aguardar conclusão. Ler o `STATUS:` do relatório:
- `success` → avançar para Fase 2
- `partial` ou `failed` → exibir os erros ao usuário e **PARAR** (não delegar fases dependentes sobre uma base quebrada)
- Se o agente parou aguardando preenchimento do roadmap → repassar instruções ao usuário e PARAR

### Passo 3 — Fase 2: frontend-builder + backend-builder EM PARALELO

**CRÍTICO:** lançar os DOIS Agent calls na MESMA mensagem para execução concorrente.

- `subagent_type: "frontend-builder"` — prompt: "Execute o pipeline de frontend no diretório atual. Detecte o estado no disco e gere apenas o que falta. Retorne o relatório estruturado com STATUS."
- `subagent_type: "backend-builder"` — prompt: "Execute o pipeline de backend no diretório atual. Detecte o estado no disco e gere apenas o que falta. Retorne o relatório estruturado com STATUS."

Eles não conflitam: frontend escreve em `frontend/` e `docs/{design-system,screens_definition}.yaml`; backend escreve em `backend/`, `requirements.txt` e `README.md`. A única exceção (atualização do `login_callbacks.py` pelo backend no step 9.5) é um bloco comentado adicionado ao final — sem conflito real.

Aguardar AMBOS. Se qualquer um retornar `failed`/`blocked` → reportar os erros ao usuário.

**NÃO acione o test-writer aqui.** Os testes são uma etapa separada, executada sob demanda após a validação com o cliente (ver seção "Testes Sob Demanda" abaixo).

### Passo 4 — Consolidação

1. Atualizar a linha do projeto em `../.claude/PROJECTS.md`:
   - Todas as fases `success` → status `🟢 Build concluído` + data atual
   - Alguma falha → status `🔴 Build com erros` + data atual
2. Exibir relatório final consolidado:

```
══════════════════════════════════════════
  LIGHTHOUSE — BUILD CONCLUÍDO
══════════════════════════════════════════

  Fase 1  data-engineer     ✅ <resumo do relatório>
  Fase 2  frontend-builder  ✅ <N> páginas
          backend-builder   ✅ <N> entidades + auth JWT

  Fases puladas (já completas): <lista>
  Avisos: <consolidar avisos dos relatórios>

  Próximos passos:
    1. cp .env.example .env          → preencher credenciais
    2. pip install -r requirements.txt
    3. uvicorn backend.main:app --reload   → API :8000
    4. python frontend/app.py              → UI  :1050
    5. Validar o sistema com o cliente
    6. Após aprovação → pedir "gere os testes do projeto"
       (test-writer: pytest + cypress, cobertura ≥85%)
══════════════════════════════════════════
```

---

## Regras do Orquestrador

- **Stack fixo, 100% Python**: Dash 2.14+ / Dash Bootstrap Components / Dash AG Grid / Plotly / Pandas / NumPy no frontend; FastAPI / SQLAlchemy / Pydantic no backend. NUNCA aceite ou repasse pedidos que introduzam outra tecnologia (React, Streamlit, Node.js, etc.) — se o usuário pedir, explique que o stack do pipeline é fixo e ofereça a alternativa equivalente em Dash/Python.
- NUNCA gere arquivos do projeto diretamente — sempre delegue ao subagent responsável.
- NUNCA lance a Fase 2 antes da Fase 1 reportar `success` (frontend/backend dependem dos YAMLs de dados).
- NUNCA lance frontend e backend em mensagens separadas — sempre juntos para paralelismo.
- Se o usuário pediu apenas uma fase (`$ARGUMENTS`), execute só ela (verificando pré-requisitos) e atualize PROJECTS.md.
- NUNCA acione o test-writer como parte do build — apenas quando o usuário pedir explicitamente.

## Testes Sob Demanda (test-writer — fora do fluxo)

O test-writer é acionado separadamente, em momentos como:
- Após validação do processo/sistema com o cliente
- Após refatoração de uma tela (aprovada ou reprovada pelo cliente) — para verificar se continua correta
- Auditoria de qualidade pontual

Exemplos de invocação (lançar `subagent_type: "test-writer"` com prompt focado):
- "gere os testes do projeto" → escopo: projeto inteiro, cobertura ≥85%
- "teste a página aprovacao" → escopo: `frontend/pages/aprovacao/` + spec Cypress
- "teste a entidade produto" → escopo: 5 camadas da entidade no backend

Ele gera testes unitários Pytest (backend + páginas/callbacks/queries do frontend) e E2E Cypress, mede cobertura com pytest-cov e itera até atingir ≥85% de linhas no escopo. Repasse ao usuário os `BUGS ENCONTRADOS` que ele reportar — ele não corrige código de produção.

## Execução Direta de Agentes (sem lighthouse)

O usuário também pode pedir um agente avulso em linguagem natural ("regenere o frontend", "adicione a entidade produto no backend") — nesse caso, lance apenas o subagent correspondente com um prompt focado no pedido.

## Pipelines Legados (fallback)

`/build` e `/build-parallel` continuam disponíveis e inalterados — executam tudo no contexto principal, sem delegação.
