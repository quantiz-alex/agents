# Skill — Business Logic Analysis

Leia `docs/requirements.yaml` e `docs/data_model.yaml` (e `roadmap.md` como fallback) e classifique CADA regra de negócio / feature em um tipo de lógica derivada, produzindo `docs/business_logic.yaml`.

## Quando usar

Invocada automaticamente pelo `data-engineer` como **Step 2.7**, entre `docs/api_contracts.yaml` (Step 2.6) e a geração de SQL (Step 3). Também pode ser chamada diretamente:

```
/skill-business-logic
```

## Por que esta skill existe

`business_rules` em `requirements.yaml` é hoje texto livre (`{id, description, module}`). Sem estrutura, cada skill downstream (screen-definition, simulation, callbacks, FastAPI) tem que reinterpretar esse texto sozinha — na prática, várias delas caem no mesmo placeholder genérico (`preco_simulado = custo/(1-margem/100)`) em vez da fórmula real do roadmap, e o cálculo às vezes nem chega a ser implementado (o frontend só exibe uma coluna pré-computada do mock). Esta skill resolve isso extraindo a fórmula UMA VEZ, de forma estruturada, para todas as demais consumirem.

## Instruções

1. Leia `docs/requirements.yaml` (`business_rules[]` global e `modules[].business_rules[]`, mais `modules[].features[]` — uma feature às vezes descreve o cálculo melhor que a regra formal) e `docs/data_model.yaml` (para resolver nomes de campos e tipos reais).
2. Se `roadmap.md` tiver a sub-seção estruturada opcional (Tipo/Fórmula/Variáveis/Campos de saída — ver `roadmap-template.md`), preferir esses campos a re-parsear o texto livre.
3. Para cada regra, tentar extrair `campo = expressão` ou uma condição de restrição a partir do texto. Heurísticas:
   - Presença de `=` ou "calculado como", "é igual a" → candidato a `derived_field` ou `interactive_formula`.
   - "não pode ser menor/maior que", "deve ser", "no mínimo/máximo" → `validation`.
   - "se o analista simular", "parâmetro", "%", "slider", módulo com `screen_type: simulation` → `interactive_formula`.
   - "aprovar", "rejeitar", "enviar para", "somente supervisor pode" → `workflow_rule`.
4. **Nunca inventar fórmula.** Se não conseguir extrair com confiança razoável, gerar a entrada com `parsed: false`, preencher `raw_description` com o texto original, e listar em `confidence_summary.needs_review`.
5. Vincular `entity` e cada variável/campo a nomes REAIS de `data_model.yaml` — nunca a nomes livres do roadmap.
6. Se `logic_type: interactive_formula`, preencher `interaction_hint` por variável: `slider` quando `min`/`max` são conhecidos ou inferíveis (ex.: "%" → 0–100), `input` quando não há faixa conhecida, `select` quando a variável é categórica.
7. Uma `formula` pode agregar múltiplas regras de texto (`source_rule_ids`) quando elas descrevem partes da mesma fórmula (ex.: RN-SIM-001 dá a fórmula de preço, RN-SIM-002 dá a fórmula de elasticidade — ambas compõem 1 `interactive_formula` da entidade de simulação).
8. Patch incremental — se `docs/business_logic.yaml` já existir, adicionar/atualizar apenas regras novas ou alteradas (comparar por `id`/`source_rule_ids`).

## Estrutura de Saída — `docs/business_logic.yaml`

```yaml
version: "1.0.0"

rules:
  - id: string                        # mesmo id da regra em requirements.yaml quando 1:1
    source_rule_ids: [string]         # RN-XXX que compõem esta lógica (pode ser >1)
    module: string
    entity: string                    # nome real em data_model.yaml
    logic_type: validation | derived_field | interactive_formula | workflow_rule
    parsed: bool                      # false = não foi possível extrair com confiança
    raw_description: string           # texto original das regras — sempre preenchido
    description: string               # descrição normalizada, curta

    # presente quando logic_type in (derived_field, interactive_formula)
    formula:
      expression: string              # ex.: "preco_novo = custo * (1 + markup_novo)"
      variables:
        - name: string                # nome usado na expressão
          source: input_param | entity_field | constant
          field: string                # se source=entity_field, campo real em data_model.yaml
          type: number | percent | currency | select
          unit: string                 # "%", "R$", "un."
          min: number
          max: number
          default: number
          interactive: bool            # true → precisa de slider/input editável na UI
          interaction_hint: slider | input | select
      output_fields:
        - name: string                # ex.: preco_novo, margem, faturamento_estimado
          type: number | currency | percent
          persist: bool                # true = grava na entidade; false = calculado on-the-fly, nunca no mock

    # presente quando logic_type == validation
    validation:
      field: string
      condition: string               # ex.: "preco >= custo * (1 + margem_minima)"
      error_message: string
      severity: block | warn          # block = HTTP 422; warn = aviso, não bloqueia

    # presente quando logic_type == workflow_rule
    workflow:
      trigger_action: string          # submit_approval | approve | reject | custom
      condition: string
      roles_allowed: [string]

    # como deve aparecer na UI (consumido por skill06/skill-simulation/skill09)
    ui:
      mode: interactive | passive      # interactive = slider/input; passive = badge/validação/coluna
      component_hint: slider | number_input | select | badge | computed_column
      screen_hint: simulation_panel | grid_column | form_field | approval_bar
      chart_hint: waterfall | elasticity_curve | scenario_comparison | none

confidence_summary:
  total_rules: int
  parsed: int
  needs_review: [string]              # ids com parsed:false — reportar ao usuário, nunca falhar silenciosamente
```

## Restrições

- NÃO gere código Python — apenas o YAML estruturado.
- NÃO invente fórmula/variáveis que não estejam implícitas no texto do roadmap/requirements — prefira `parsed: false` a uma suposição.
- `entity`/`field`/`variables[].field` devem referenciar `data_model.yaml` real (validado no pós-processamento).
- Contexto máximo: **8.000 tokens** de saída. Se exceder, dividir em chunks com continuação automática.

## Pós-processamento

1. Executar `/skill00-validator step2_7`.
2. Se `confidence_summary.needs_review` não estiver vazio → reportar ao usuário a lista de regras não-parseadas, sugerindo detalhar a sub-seção estruturada (Tipo/Fórmula/Variáveis) dessas regras em `roadmap.md`. Isso é um AVISO — não bloqueia o build.
3. Se validação estrutural falhar (YAML inválido, entidade/campo inexistente) → reportar erro e PARAR.
4. Se validação passar → criar checkpoint `.build/checkpoints/step2_7.json` e avançar.

## Argumento opcional

$ARGUMENTS
