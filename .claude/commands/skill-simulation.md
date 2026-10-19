# Skill — Simulação de cenários e tabela de preços consumidora (v5)

Aplicar quando `screen_type: simulation`, `has_simulation: true` ou quando a tela consome o cenário compartilhado (tabela de preços vigentes). Regras gerais em `$LH/rules/core.md`. Para parâmetros que afetam outras telas, o contrato de estado é `skill-demo-scenario.md`.

## Contrato
- **Fórmula = `business_logic.yaml`.** Use a regra `logic_type: interactive_formula` da tela (`simulation_panel.config.business_logic_rule_id`).
  - Os parâmetros de cálculo são **exatamente** `formula.variables[interactive: true]`.
  - O corpo implementa `formula.expression`.
  - Os KPIs e resultados são `formula.output_fields[]`.
  - Não invente "Receita Atual/Simulada" se a fórmula produz outras grandezas.
  - Sem `business_logic.yaml`, registre aviso e implemente só o que o roadmap descrever.
- **Regra compartilhada** por várias telas vai em `frontend/services/scenario_engine.py` (motor puro). O `_queries.py` só carrega, resolve o cenário e chama o motor. Nunca duplicar fórmula.
- **Simular nunca persiste.** Salvar cenário guarda um snapshot **na sessão** (`demo-session`/store da página), **nunca em CSV**. Aplicar altera só o estado de demo da sessão.
- **Elasticidade:** `volume_novo = volume × (1 + elasticidade × (preço_novo/preço_atual − 1))`, com `max(0, …)` e **sem `round` por linha**. Arredondar só na exibição de totais, para preservar o efeito em volumes pequenos por combinação.
- **Funções públicas reutilizáveis** em `_queries.py`: o Assistente de Pricing chama as mesmas, com os mesmos argumentos.

## Componentes (biblioteca — ver `LIBRARY_INDEX.md`)
| Peça | Como |
|---|---|
| Parâmetros | `card("Parâmetros do cenário", dbc.Row([param_slider(...) …]), right=dbc.Switch(id="<p>-auto", value=True, label="Ao vivo"))`. `param_slider` quando há min/max; `filter_select` para categóricas; `dbc.Input(type="number")` só sem faixa |
| Resultado | `kpi_row([kpi_card(label, atual, simulado, …)])` Atual × Simulado; gráfico `grouped_bars`/`waterfall`/`elasticity_curve` (rótulos não se sobrepõem quando atual ≈ simulado); `data_table` comparativo |
| Cenários salvos | `data_table` com os snapshots da sessão; ação "simulate" carrega o cenário nos controles |
| Feedback | `toast("<p>-toast")` + `notify()`; `confirm_modal` antes de Aplicar/Descartar |

## Callbacks
- **`recalc_mode: live`** → Padrão 9 do skill08: sliders como Input, a tela abre já calculada, `step ≥ 0,5`.
- **`recalc_mode: button`** → Padrão 2.
- **Salvar cenário:** evento para o dono de `demo-session` (`{"type":"demo-session-event","page":SLUG}`).
- **Enviar para aprovação:** Padrão 3, quando `has_approval_flow`.
- **Publicar** os parâmetros da tela para o Assistente (skill08, Padrão 15). Na Configuração com controles não salvos, o Detalhar publica `assistant_focus(..., snapshot=<linha exibida>)`.

## Tabela de preços vigentes (consumidor do cenário) — padrão por produto
Quando o preço existe por combinação (produto × canal × região × segmento):
- **Grid = uma linha por produto.**
  - Preço base = combinação de referência (`grid.reference_combination`, ex.: Varejo · Sudeste · Standard; sem ela, a combinação de maior volume).
  - Colunas: preço base, novo preço base (editável), variação, **faixa nas combinações** (mín–máx), e totais somados nas combinações (receita, margem R$, volume).
- **Edições guardadas por combinação** (`{item_id: novo_preco}`). Assim o recálculo linha a linha, os KPIs, o lote de aprovação e o rascunho vindo da Configuração continuam iguais.
- **Editar o preço base** (inline, simulador do Detalhar ou ajuste em massa) aplica **o mesmo fator** a todas as combinações do produto (`expandir`). Voltar ao valor vigente remove as edições do produto.
- **Guardrails:** RN de guardrail validada no preço base, com **aviso** de combinações fora da faixa (não bloqueia).
- **Detalhar** (modal xl) contém:
  - a ficha do produto;
  - a faixa por canal;
  - a tabela das combinações (diferença vs base, preço atual/novo, margem, volume com 1 casa);
  - o histórico;
  - o simulador do preço base ("Aplicar a todas as combinações").

  É **uma ação só**: sem "Simular" duplicado.
- **Filtros:** categoria, subcategoria, status e busca. As dimensões da combinação ficam no Detalhar.
- **Exportar:** `send_excel_multi({"Por produto": …, "Combinações": …})`.
- **Funções de referência** em `_queries.py`: `base`, `recalcular`, `ref_rows`, `por_produto`, `expandir`, `variacoes`, `fora_guardrail`, `ajuste_massa`, `kpis`, `itens_lote`. O projeto de referência `qwizer-pricing-vibe-code/frontend/pages/tabela_vigente/` implementa exatamente isso.

## Restrições
- Tipagem obrigatória. No máximo cerca de 8.000 tokens por arquivo.
- Sem `html.Div` raiz manual nem hex: a página usa `app_shell(...)`.
