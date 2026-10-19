# Plano de melhoria — Lighthouse v5

> **Origem:** as melhorias feitas à mão no projeto gerado `qwizer-pricing-vibe-code` (out/2026) e uma análise do consumo de tokens do pipeline atual (`/lighthouse`).
> **Objetivo:** (1) os agentes passarem a gerar o app **como ele está hoje no Qwizer**; (2) reduzir de forma relevante os tokens gastos por build.

---

## 1. Diagnóstico

### 1.1 Consumo de tokens (estimativa a partir dos tamanhos dos arquivos, build do porte do Qwizer: 28 entidades e cerca de 16 telas)

| Fase | Lido + escrito | Observação |
|---|---|---|
| data-engineer | ~165 KB lidos + 545 KB escritos ≈ **180K tokens** | Perto do limite da janela |
| frontend-builder | ~920 KB lidos + 675 KB escritos ≈ **400K tokens** | **Estoura a janela**: 1–2 compactações, e cada compactação obriga a reler tudo |
| backend-builder | ~450 KB lidos + 480 KB escritos ≈ **230K tokens** | |
| **Total único** | **≈ 800K tokens** | A cobrança real de entrada é maior, porque o contexto é reenviado a cada turno (~150 chamadas × ~120K) |

**Onde vai o grosso:**

1. **Releitura por página:**
   - O `skill07:11` e o `skill08:13-14` mandam reler `screens_definition` (119 KB), `design-system`, `business_logic` (57 KB) e `data_model` (60 KB) **a cada tela**. São cerca de 255 KB por tela; se seguido à risca, ×16 telas ≈ **1M tokens**.
2. **Lista "leia antes de gerar" do frontend-builder** (`frontend-builder.md:23-38`):
   - São cerca de **320 KB**: 12 skills, o guia visual, o `SKILL.md` de 28 KB e **106 KB de código-fonte das bibliotecas**.
   - Isso é lido mesmo quando a tela não usa simulação, aprovação ou workflow.
3. **YAMLs grandes do projeto relidos por três agentes:**
   - `requirements.yaml` (140 KB), `screens_definition` (119 KB), `api_contracts` (103 KB), `roadmap.md` (86 KB).
   - Cada agente relê tudo; nada é passado como resumo ou recorte.
4. **"Copiar" sem `cp`** (project-init, skill-shell, skill04, ui-reviewer):
   - Se o agente copia com Read + Write, gasta cerca de 175 KB lidos e 175 KB escritos (≈ 90K tokens).
   - As bibliotecas ainda são copiadas **duas vezes**: no project-init e de novo no passo 0 do frontend.
5. **Todos os agentes herdam o modelo da sessão** (sem `model:` no frontmatter), com `effortLevel: high`. Tarefas mecânicas, como copiar, rodar validações e o smoke test, usam o modelo mais caro.
6. **Duplicação e contradições:**
   - O mesmo parágrafo do assistente aparece em 10 arquivos.
   - As regras do cenário demo aparecem em mais de 12 lugares.
   - O mesmo checklist aparece 4 vezes, e os tokens de design em 7 lugares.
   - Há **8 contradições** (register_page, rota pós-login, cor da sidebar, credenciais demo, CSV vs sessão…). Elas geram retrabalho e releituras.
7. **Código dentro das instruções:**
   - `skill-approval-flow` tem 86% de código, `skill-simulation` 79% e `skill-auth` 79%.
   - O `skill-simulation.md:33` traz um exemplo de cerca de 18 KB que ele mesmo diz "NUNCA" usar.
8. **Material legado:** o `build.md` (33 KB) e o `build-parallel.md` (11 KB) estão marcados como legado, mas continuam no repositório e são referenciados.

### 1.2 Defasagem em relação ao Qwizer
Em 6 de 8 frentes o framework **ainda manda gerar o comportamento antigo**. Nas outras duas ele é omisso ou ambíguo. Detalhe na seção 3.

---

## 2. Estratégia

A ordem segue o maior impacto com o menor risco:

1. **Primeiro reduzir tokens** (Fase 1), porque isso barateia todos os builds seguintes, inclusive os de teste desta própria melhoria.
2. **Depois portar as melhorias do Qwizer** (Fase 2), já no formato enxuto.
3. **Por fim alinhar regras e validar** (Fase 3), com um build de referência comparado ao Qwizer.

Princípio geral: **template pronto (copiado com `cp`) + instrução curta que aponta para ele**, em vez de código explicado dentro do `.md`. O agente só lê o código quando precisa mudar algo específico.

---

## 3. Fase 2 — Portar as melhorias do Qwizer (o que muda, onde)

> As evidências e linhas exatas no app estão em `qwizer-pricing-vibe-code`. **FW** = `agent-vibe-code-pricing/.claude`.

### 3.1 Detalhar = modal central (não lateral)
- **`FW/templates/components-library.py:705-720`:** trocar `detail_offcanvas` (Offcanvas) pela versão do app:
  - `dbc.Modal` centralizado, rolável, com tamanho `lg`/`xl` conforme `width`;
  - `ModalTitle(id=f"{id}-title")`;
  - parâmetro **`extra=`** para conteúdo fixo (botões, simulador);
  - rodapé com `assistant_ask_button`.
- **Regra nova (skill08, Padrão 10):**
  - o título é atualizado por `Output(f"{id}-title", "children")`;
  - o conteúdo fixo entra por `extra=`;
  - **nunca** fazer `oc.children = [...]`. Isso quebrava o React ("Objects are not valid as a React child").
- **Corrigir as menções a "offcanvas"** em:
  - `skill08:37,441-472,545`
  - `skill07:36,57,144`
  - `frontend-builder.md:102,130,149`
  - `design-system.yaml:365`
  - `skill06:39,46`
  - `roadmap-template.md:42`
  - `roadmap-import.md:107`
  - `GUIA-VISUAL-PMZ.md:226`
  - `SKILL.md:79`
- **CSS:** trocar `.detail-offcanvas` por `.detail-modal` em `templates/dash-starter/assets/theme.css:197-205`.

### 3.2 KPIs numa linha só
- **`components-library.py:548-552`:** `kpi_row` com colunas de largura igual a partir de lg (`lg=True`, `md = 12//n if n<=4 else 4`).
- **`theme.css`:**
  - `.kpi-value` com `clamp()`, `nowrap` e `ellipsis`;
  - `.kpi-row > .kpi-col { min-width: 0 }`.

### 3.3 Gráfico de elasticidade sem rótulos sobrepostos
- **`charts-library.py:553-558`:**
  - quando os dois preços são próximos, um rótulo só: "Atual = Simulado";
  - quando são diferentes, rótulos para lados opostos.

### 3.4 Tabela Vigente por produto
- **`skill06-screen-definition.md`, bloco `grid`:**
  - novos campos: `grain: produto`, `reference_combination` (Varejo/Sudeste/Standard), `variations_in: detail`, `edit_propagation: proportional`;
  - regra: **não** gerar a ação "Simular" quando o "Detalhar" já contém o simulador;
  - regra: dimensões que vão para o Detalhar não viram filtro do grid.
- **`skill-simulation.md`:** nova seção "Consumidor: Tabela Vigente" com o padrão do app:
  - `ref_rows` / `por_produto` / `expandir` / `variacoes` / `ajuste_massa`;
  - edições guardadas por combinação;
  - exportação com duas abas.
- **`roadmap-template.md:103-109`:** linha "Granularidade do grid / combinação de referência".

### 3.5 Volume sem arredondar por linha (elasticidade preservada)
- **`skill-simulation.md` e `skill-demo-scenario.md:31`:**
  - regra explícita: **nunca arredondar o volume por linha**; arredondar só na exibição;
  - as frações por combinação somam o total do produto (RN-015).
- **`skill04-mock-data.md:54-55`:** campos de peso/fração são `decimal`, e o volume derivado não é gravado como inteiro.
- **Exibição:** volume por combinação com 1 casa decimal no Detalhar.

### 3.6 Navegação e filtro herdado
- **`skill-shell.md:180-193`:** substituir o exemplo de `guard_routes` pelo do app (`app.py:124-147`):
  - publica `workflow-context` com `nonce`;
  - **limpa o contexto quando a URL muda para outra tela**.
- **Ajustar** o `data_structure` de `workflow-context` em `design-system.yaml:505-515` para `{target, context, workflow_id, nonce}`.
- **Novo padrão "banner de contexto herdado + Limpar filtro":** helper `context_banner()` em `workflow_components.py`, com a regra correspondente em `skill08`.

### 3.7 Assistente de Pricing (maior bloco)
**Novos templates**, copiados do app e parametrizados por projeto:

| Template novo / atualizado | Origem no app | Parametrizar |
|---|---|---|
| `templates/pricing_assistant.py` (substitui) | `frontend/services/pricing_assistant.py` | `DOMAIN_GLOSSARY`, `_MISSING_HINTS` |
| `templates/assistant_llm.py` (novo) | `frontend/services/assistant_llm.py` | Domínio e mapa "pergunta → tela" no prompt; `PRICES` |
| `templates/assistant_detail.py` (novo) | `frontend/services/assistant_detail.py` | Helpers + padrão `DETAIL_HANDLERS` |
| `templates/assistant_pages.py` (novo, esqueleto) | `frontend/services/assistant_pages.py` | `_p` / `_v` / `_ok(parametros_tela)` + exemplo por tipo de tela |
| `templates/assistant_callbacks.py` (novo) | `frontend/assistant_callbacks.py` | `SCENARIO_PAGES` |
| `templates/pricing_assistant_components.py` (substitui) | `frontend/components/pricing_assistant_components.py` | — |
| `templates/page_common.py` (novo) | `frontend/pages/_common.py` | — (`assistant_focus`, `screen_params`, `assistant_params_store`, `event_stores`, `nav_event`, `send_excel`, `opt_value`) |
| `templates/tests/` (novo) | `tests/conftest.py`, `test_pricing_assistant.py`, `test_assistant_detail.py`, `test_assistant_pages.py` | Ids de análises |

**Reescrever `skill-pricing-assistant.md`** (hoje contradiz o app em cerca de 10 pontos). Contrato novo, curto:

1. **Modo híbrido:**
   - sem `ANTHROPIC_API_KEY`, o assistente funciona no modo local (busca aproximada + trava de escopo);
   - com a chave, o Claude chama as análises como ferramentas **sem parâmetros**, e o contexto é injetado pelo servidor;
   - qualquer falha da API cai no modo local.
2. **Análises por tela:** 2–5 por tela, cada uma chamando **as mesmas funções `*_queries.py` da tela**. Nenhuma recalcula por conta própria.
3. **Item em foco:**
   - todo Detalhar publica `assistant_focus(tipo, id, label)` no store `assistant-select`;
   - as ferramentas `detalhe_*` têm `entity` **e** `pages` explícitos;
   - exemplo: "melhor preço" só na Tabela Vigente, nunca no Simulador Tributário.
4. **Estado da tela:**
   - telas com filtros ou parâmetros publicam `screen_params(...)` no store `assistant-params`, com o mesmo gatilho que aplica os filtros na tela (botão Filtrar/Simular, ou ao vivo);
   - as respostas citam `parametros_tela`.
5. **Trava de escopo:** perguntas fora de pricing não chamam a API.
6. **Catálogo v2:**
   - `pages` explícito;
   - `entity` para as ferramentas de foco;
   - **todos os textos entre aspas** (o "× 0,75" virava número);
   - `validate_catalog` recusa valores que não sejam texto.
7. **Paridade é critério de aceite:** um teste por análise confirmando "número do assistente = número da tela, com os mesmos parâmetros".

**Também:**
- **`check_pricing_assistant.py`:** cobrir escopo, `entity`/`pages`, params e o motor Claude com cliente falso. Ajustar o teste de empate, que hoje espera `choose_analysis`.
- **Dependências:** `anthropic` e `openpyxl` em `dash-starter/requirements.txt`, `build.md` e `backend-builder.md:88`.
- **`.env.example`:** `ANTHROPIC_API_KEY`, `ASSISTANT_MODEL`, `ASSISTANT_AI`.
- **CSS do assistente:** z-index 1060/1070, chips, histórico recolhido, Markdown.

### 3.8 Testes
- **`test-writer.md:86,112-121` e `skill12:161`:** os testes pytest do frontend vão para `tests/frontend/`.
  - Hoje essa pasta está reservada para Cypress, o que conflita com o app.
  - Mover Cypress para `tests/e2e/`.
- **`conftest`:** separar em dois.
  - Raiz: só o `sys.path`.
  - `tests/backend/conftest.py`: importa o FastAPI e o SQLAlchemy. Hoje esse import no topo quebra os testes que rodam só o frontend.

### 3.9 Outras melhorias do app a promover
- **`data_table`:**
  - formatação de data sem deslocamento de fuso;
  - tooltip em colunas de texto;
  - larguras mínimas;
  - coluna de ação com largura fixa;
  - sem `responsiveSizeToFit`.
- **Helpers:** `chart_block` / `grid_block` / `kpi_from_spec` e `bar_colored` / `bubble_by_series` / `add_reference_lines` / `empty_figure` passam a valer para todo projeto.

---

## 4. Fase 1 — Redução de tokens

| # | Ação | Onde | Economia estimada |
|---|---|---|---|
| T1 | **Recorte por tela.** A fase de definição grava `docs/screens/<slug>.yaml` (só a tela) e `docs/digest.yaml` (entidades, RNs e campos usados por tela, cerca de 10–15 KB). skill07 e skill08 passam a ler **só o recorte da tela + o digest**, sem os 4 YAMLs inteiros | `skill06`, `skill07:11`, `skill08:13-14`, `frontend-builder` | **Até cerca de 900K tokens** por build (de ~255 KB para ~20 KB por tela) |
| T2 | **Leitura sob demanda.** O frontend-builder lê no início só um **índice** (~8 KB): função → assinatura → quando usar, gerado de `design-system.yaml:339-415`. Skills de simulação, aprovação, workflow e assistente só são lidas se a tela tiver aquele `screen_type`. O código das bibliotecas não é lido, só copiado | `frontend-builder.md:23-38` | De ~95K para ~25K tokens no início do frontend |
| T3 | **Toda cópia com `cp`** via Bash, nunca Read + Write. Remover a cópia duplicada no project-init ou no passo 0 do frontend | `project-init:71-73`, `skill-shell:14-20`, `skill04:10`, `ui-reviewer:17`, `frontend-builder` passo 0 | ~90K tokens |
| T4 | **Modelo por agente** no frontmatter: `model: sonnet` para ui-reviewer, test-writer e tarefas mecânicas (cópia, validação, mock). Opus só no frontend, nos passos de tela e assistente. Recomendar `effortLevel: medium` para builds | `agents/*.md`, README | 40–60% do custo das fases mecânicas |
| T5 | **Ferramentas mínimas:** ui-reviewer sem Write/Edit (só reporta) | `ui-reviewer.md`, `test-writer.md` | Menos ações acidentais e menos retrabalho |
| T6 | **Fonte única:** um `rules/core.md` curto (~6 KB) com stack, cenário demo, assistente, rotas, cores e credenciais. Os outros arquivos referenciam com 1 linha em vez de colar o parágrafo (assistente em 10 arquivos, demo em 12+, checklist ×4, tokens de design ×7) | todos | ~60–80 KB a menos nas instruções lidas |
| T7 | **Código fora do `.md`:** os blocos de código de skill-approval-flow, skill-simulation, skill-auth, skill11, skill13 e skill08 viram templates `.py` (copiados) mais um resumo de 10–20 linhas. Remover o anti-exemplo de 18 KB do skill-simulation | `commands/skill-*.md` | ~100 KB a menos nas skills |
| T8 | **Arquivar o legado:** `build.md`, `build-parallel.md`, `skill-design-system.md` (substituído pela cópia do template), changelog dentro do README, notas "em v3…" e "anteriormente…" | mover para `.claude/archive/` | Menos ruído; evita o agente seguir regras velhas |
| T9 | **Validador enxuto no `/lighthouse`:** o `skill00` vira **script** (`scripts/validate_project.py`, checagens determinísticas de YAML, ids e referências) em vez de 20 KB de instrução lida pelo modelo. O validador por tela (`skill07:180`) passa a ser esse script | `skill00`, `skill07` | ~20 KB por chamada, mais o risco de ler 17 MB de mock |
| T10 | **Resumo entre agentes:** o data-engineer grava `docs/handoff.md` (~5 KB: entidades, telas, RNs-chave). Frontend e backend começam por ele e só abrem os YAMLs grandes no trecho necessário (Grep por chave em vez de Read inteiro) | `data-engineer`, `lighthouse.md:62,73` | ~50–100K tokens |
| T11 | **Correções em loop curtas:** quando o ui_smoke encontra falhas, criar um **fixer** dedicado (Sonnet, só os arquivos apontados), e não um frontend-builder novo que relê ~380 KB | `ui-reviewer`, `lighthouse` fase 3 | ~100K tokens por rodada de correção |
| T12 | **Limite no loop do mock:** no máximo 3 tentativas, com o erro resumido | `data-engineer.md:229` | Evita loops longos |
| T13 | **Caminho dos templates:** resolver `../.claude/` para projetos irmãos (variável `LIGHTHOUSE_HOME` no `project.json`) | agentes | Evita Glob/Grep "procurando" as specs |

**Meta:** de ~800K para **~300–350K tokens únicos por build**, com o frontend cabendo numa janela só (sem compactação), o que corta também os reenvios de contexto.

---

## 5. Fase 3 — Consistência e validação

1. **Resolver as 8 contradições**, com a decisão registrada no `rules/core.md`:
   - **App e roteamento:**
     - `register_page` × `use_pages=False`: fica `use_pages=False` + `guard_routes`;
     - rota pós-login: `/home`.
   - **Visual:**
     - sidebar: branca;
     - raiz da página: `app_shell`, nunca `html.Div` com hex.
   - **Dados e acesso:**
     - credenciais demo: `<role>@<empresa>.com` / `demo`;
     - CSV × sessão: cenário e aprovações vivem na sessão, nunca em CSV;
     - mock: sempre pelo motor volumétrico.
2. **Corrigir os docs desatualizados do Qwizer** (`screens_definition.yaml` da Tabela Vigente, `business_logic.yaml:166,233,283` ainda com `round`, `roadmap.md:305`). Ele vira o **projeto de referência**.
3. **Build de referência:**
   - rodar `/lighthouse` num roadmap pequeno (3–4 telas) e no do Qwizer;
   - comparar com o app atual: telas, assistente e testes de paridade passando;
   - medir os tokens reais com `/cost` ou o painel de uso, antes e depois.
4. **Smoke de regressão do framework:** `scripts/check_framework.py` confere que:
   - nenhum `.md` cita `Offcanvas` para Detalhar;
   - `Output(id,"title")` não aparece;
   - não há `round(` em volume;
   - os templates importam;
   - o catálogo de exemplo valida.

---

## 6. Ordem de execução sugerida

| Etapa | Conteúdo | Esforço |
|---|---|---|
| 1 | T3, T4, T5, T8, T12, T13 (rápidos e sem risco) | Baixo |
| 2 | T1, T2, T10 (recortes, índice, handoff): maior economia | Médio |
| 3 | 3.1–3.6 e 3.8–3.9 (bibliotecas, CSS, regras de tela/navegação/testes) | Médio |
| 4 | 3.7 Assistente (templates novos + skill reescrita + checks) | Alto |
| 5 | T6, T7, T9 (fonte única, código para templates, validador em script) | Médio/alto |
| 6 | Fase 3 (contradições, docs do Qwizer, build de referência, medição) | Médio |

## 7. Decisões (19/10/2026)
1. **Modelos:** Sonnet em data-engineer, backend-builder, ui-reviewer, test-writer e frontend-fixer. Opus só no frontend-builder.
2. **Legado:** `/build`, `/build-parallel` e `/skill-design-system` foram arquivados em `.claude/archive/` (nenhum agente os usava).
3. **Assistente:** todo projeto tem o assistente (modo híbrido; o local é o fallback).
4. **Referência:** o Qwizer é o projeto de referência oficial. **Sem testes de paridade** número a número, porque cada projeto tem suas particularidades. Ficam só os testes genéricos do motor do assistente.

## 8. Status da execução (19/10/2026)
| Item | Status |
|---|---|
| **T1** recortes por tela | ✅ `scripts/split_screens.py` (Qwizer: 25–43 KB por tela vs ~255 KB) + skill07/08 leem só o recorte |
| **T2** leitura sob demanda + índice | ✅ `frontend-builder` reescrito; `LIBRARY_INDEX.md` (21 KB vs ~150 KB de código) |
| **T3** cópias com `cp` | ✅ project-init (sem cópia dupla), skill-shell, skill04, ui-reviewer, data-engineer |
| **T4** modelo por agente | ✅ frontmatter |
| **T5** ui-reviewer sem Write/Edit | ✅ |
| **T6** fonte única | ✅ `rules/core.md` (8 contradições resolvidas); referências nos agentes |
| **T7** código fora do `.md` | ✅ `skill-simulation` (23 → ~6 KB)<br>⏳ `skill-approval-flow`: só nota v5 que prevalece sobre o código. A reescrita fica para uma próxima rodada |
| **T8** legado arquivado | ✅ |
| **T9** validador por script | ✅ `scripts/validate_project.py` (screens / pages / app / assistant) |
| **T10** handoff | ✅ Step 6 do data-engineer, `docs/handoff.md` |
| **T11** frontend-fixer | ✅ agente novo + /lighthouse Fase 3 |
| **T12** limite do loop do mock | ✅ 3 tentativas; seed.sql auditado por grep |
| **T13** caminho `$LH` | ✅ `core.md` §1 + `lighthouse_home` no `project.json` |
| **3.1–3.6, 3.8** paridade de comportamento | ✅ bibliotecas, CSS, skill06/07/08, skill-shell, skill-simulation, skill-demo-scenario, skill04, design-system, testes |
| **3.7** assistente | ✅ 6 templates novos/substituídos + `page_common.py` + `tests/`<br>✅ skill reescrita<br>✅ check atualizado (empate de pergunta → opções) |
| **Fase 3.2** docs do Qwizer | ✅ `business_logic` (sem `round` em volume), `screens_definition` (Tabela Vigente por produto), `roadmap` |
| **Fase 3.3** build de referência medido | ⏳ próximo passo: rodar `/lighthouse` num roadmap pequeno e medir os tokens |

**Verificações feitas:**
- Templates compilam.
- `check_pricing_assistant.py` e `check_demo_scenario.py` passam.
- O teste genérico do assistente passou contra o Qwizer (52 testes).
- `validate_project.py` roda no Qwizer sem erros.
- Os 175 testes do Qwizer passam.
