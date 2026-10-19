# Skill — Assistente de Pricing (v2: híbrido Claude + local, análises por tela)

Todo projeto tem o assistente. Ele é gerado pelo frontend-builder no **Step 6.6** e integrado nas páginas (Step 7) e no shell (Step 8). O projeto de referência é o `qwizer-pricing-vibe-code`, que pode ser consultado por Grep quando houver dúvida de implementação.

## Princípios
1. **Os números vêm sempre das consultas da tela.**
   - Cada análise chama as **mesmas funções `*_queries.py`** que a tela usa, com o **mesmo estado**: cenário aplicado, aprovações da sessão, filtros e parâmetros aplicados.
   - Nada é recalculado "do zero" no assistente.
2. **Modo híbrido.**
   - Com `ANTHROPIC_API_KEY`, o Claude entende a pergunta livre e chama as análises como **ferramentas sem parâmetros**. O contexto (tela, item em foco, filtros) é injetado pelo servidor, e o modelo não consegue alterá-lo.
   - Sem chave, ou se a API falhar, entra o motor local: busca aproximada por pergunta, alias ou título, com opções clicáveis.
3. **Análises por tela.**
   - Cada tela tem 2–5 análises próprias, alinhadas ao propósito dela.
   - Uma análise nunca aparece em tela de outro propósito. Exemplo: "melhor preço" fica na tela de preços, nunca no simulador tributário.
4. **Item em foco.**
   - Todo Detalhar publica o item aberto (`assistant_focus`).
   - As ferramentas `detalhe_*` analisam esse item e só aparecem nas telas listadas em `pages`.
5. **Trava de escopo.** Pergunta fora de pricing recebe uma resposta padrão com sugestões, sem chamar a API.
6. **Ações limitadas.** Só "Abrir" (navegação com contexto) e "Simular proposta" (rascunho). Nunca aplica nem aprova.

## Arquivos (copiar com `cp` e depois parametrizar ou gerar)
| Template (`$LH/templates/`) | Destino | O que fazer |
|---|---|---|
| `pricing_assistant.py` | `frontend/services/` | Ajustar `DOMAIN_GLOSSARY` (termos do domínio do cliente) e `_MISSING_HINTS` (slugs de onde se seleciona o item) |
| `assistant_llm.py` | `frontend/services/` | Preencher `APP_NAME`, `DOMAIN_SCOPE`, `SCREEN_ROUTING` (assunto → tela) e `EXTRA_RULES`. Manter o texto estável (cache de prompt) |
| `assistant_detail.py` | `frontend/services/` | Manter os helpers. Gerar **uma ferramenta por tipo de item** que o projeto publica no Detalhar (os 2 handlers do template são exemplos) |
| `assistant_pages.py` | `frontend/services/` | Manter `_p` / `_v` / `_ok`. Gerar 2–5 handlers por tela seguindo os 3 exemplos (analítica com período, simulador ao vivo, grid editável) |
| `assistant_callbacks.py` | `frontend/` | Ajustar `SCENARIO_PAGES`. O resto é genérico |
| `pricing_assistant_components.py` | `frontend/components/` | Nada (genérico) |
| `page_common.py` | `frontend/pages/_common.py` | Nada. Acrescentar `shell()` e outros helpers do projeto se precisar |
| `tests/conftest.py`, `tests/test_pricing_assistant.py` | `tests/`, `tests/frontend/` | Nada (testes genéricos do motor) |

**Gerar também:**
- `frontend/services/assistant_data.py`: lookups usados pelos handlers, como `produto(ctx)` e `brl`/`pct` em pt-BR.
- `frontend/services/assistant_analyses.py`:
  - handlers globais: alertas, pendências etc.;
  - registry `ANALYSIS_HANDLERS = {..., **DETAIL_HANDLERS, **PAGE_HANDLERS}`.
- `docs/assistant_catalog.yaml`.

## Catálogo v2 (`docs/assistant_catalog.yaml`)
```yaml
version: 2
enabled: true
mode: hybrid
analyses:
  - id: dash_resumo                       # = chave em ANALYSIS_HANDLERS
    title: Resumo do período (receita, volume e margem vs período anterior)
    handler: dash_resumo
    pages: [dashboard]                    # SEMPRE explícito
    roles: []
    questions: ["Como foi o período filtrado?"]            # 1ª = sugestão exibida
    aliases: ["Resumo do dashboard", "Comparar com o período anterior"]
    required_context: []                  # ex.: [product_id]
    sources: ["dashboard_queries.calcular_kpis", "RN-001"]
    rule_ids: [RN-001]
    assumptions: ["Período e filtros atuais da tela"]
    outputs: [receita, volume, margem]
    actions: []                           # {id, kind: navigate|simulate, target|scenario_key}
  - id: detalhe_pedido                    # ferramenta de FOCO
    entity: pedido                        # exige item em foco desse tipo...
    pages: [pedidos]                      # ...E uma destas telas
    # (demais campos iguais)
```

**Regras do catálogo:**
- **Todo texto entre aspas.** `"× 0,75"` sem aspas vira número na lista.
- **`entity` sempre com `pages`.**
- **IDs únicos**, um handler para cada ID.
- **Perguntas:** a primeira é curta e é a sugestão exibida. Os aliases cobrem formas comuns de perguntar.
- **Administração e telas de cadastro puro:** sem análises (a trava de escopo responde).

## Como escolher as análises de cada tela
Use o propósito da tela (`user_goal`, KPIs, gráficos, regras de negócio) e reaproveite as funções que a própria tela chama:

| Tipo de tela | Análises típicas |
|---|---|
| Analítica (dashboard) | Resumo do período vs anterior · ranking/top N · mix por dimensão · melhor/pior por margem |
| Diagnóstico (alertas) | Alertas críticos · abaixo da meta · oportunidades · onde está o risco (por categoria) · diagnóstico do item em foco |
| Tabela de preços | Abaixo da meta no preço vigente · fora dos guardrails · impacto do rascunho · análise do produto em foco · melhor preço testado (sensibilidade) |
| Configuração / cenário | Impacto do rascunho · otimizador · dimensão mais impactada · melhor cenário salvo · item simulado em foco (snapshot) |
| Simulador | Impacto com os parâmetros da tela · evolução/linha do tempo |
| Grid editável simulado | Impacto do que está em edição vs vigente · impacto por segmento · distribuição |
| Fila/lista (pedidos, aprovações, clientes) | Resumo com os filtros da tela · itens prioritários · item em foco |

## Integração nas páginas (Step 7)
- **Item em foco:** o callback do Detalhar devolve `assistant_focus(tipo, id, label, product_id=..., categoria_id=..., snapshot=...)` no Output `{"type":"assistant-select","page":SLUG}` (`allow_duplicate=True`). O layout tem esse store.
  - Use `snapshot` quando o número exibido depende de controles não salvos.
- **Parâmetros da tela:** `assistant_params_store(SLUG)` no layout, mais o callback `publicar_params` (skill08, Padrão 15) com o **mesmo gatilho** que aplica os filtros na tela.
- **Handlers:**
  - leem `ctx["params"]` via `_p(ctx)`, com fallback no padrão que a tela usa ao abrir;
  - devolvem `_ok(msg, data, params)`, onde `params` vira `parametros_tela` e o assistente cita o recorte.

## Integração no shell (Step 8)
- `assistant_panel()` montado uma vez no layout do app, oculto no login.
- `register_assistant_callbacks()` chamado uma vez.
- `requirements.txt` com `anthropic` e `.env.example` com `ANTHROPIC_API_KEY`, `ASSISTANT_MODEL` e `ASSISTANT_AI`, conforme `skill-env.md`.

## Validação
1. `python "$LH/templates/scripts/check_pricing_assistant.py"`, que cobre os invariantes do motor.
2. `python "$LH/templates/scripts/validate_project.py" assistant`:
   - catálogo (aspas, `entity` + `pages`, IDs);
   - telas sem análise;
   - `assistant_llm.py` parametrizado.
3. `pytest tests/frontend -q` com o teste genérico copiado. **Não** gerar testes de paridade número a número: cada projeto tem suas regras.

## Relatório (no relatório do frontend-builder)
`ASSISTENTE: <N> análises em <N> telas · <N> ferramentas de foco · telas com params: <lista> · capacidades excluídas: <lista com motivo>`
