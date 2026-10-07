# Skill 00 — Validation & Consistency Check

Valida a consistência e integridade entre todos os artefatos gerados antes de prosseguir para a próxima etapa do pipeline.

## Quando Usar

- Antes de cada etapa do `/build` para garantir que os artefatos de entrada estão corretos
- Após modificações manuais em YAMLs para verificar impactos
- Como diagnóstico quando o build falha

## Argumento Opcional

`$ARGUMENTS` — etapa a validar (ex.: `step2` para validar após data_model.yaml). Se vazio, valida tudo.

---

## Listas Canônicas (fonte única — usadas pelas etapas 0, 1 e 6)

```yaml
screen_types: [dashboard, analytics, grid, master_detail, form, report, mixed, simulation, approval_queue]
chart_types:  [bar, line, area, pie, donut, scatter, histogram, heatmap, treemap, combo, funnel, gauge, sparkline, waterfall, elasticity_curve, scenario_comparison]
kpi_kinds:    [comparação, simples]
kpi_formats:  [currency, percent, number, text]
layout_tokens: ["kpis:N", "charts:1col", "charts:2col", "charts:3col", "grid", "split:A/B", "tabs:...", "params", "detail"]
entity_roles: [dimensao, fato, apoio]
distributions: ["enum(A:x%, B:y%)", "faixa(min–max)", "normal(media, desvio)", "pareto", "sazonal(mensal, pico: ...)", "tendencia(±X% ao ano)", "derivado(<expr>)", "lista(BR:...)"]
action_types: [visualizar, criar, editar, excluir, desativar, exportar-excel, exportar-pdf, importar-csv, drill-down, detalhar, simulate, apply, discard, reset_demo, submit_approval, approve, reject]
```

Se algum desses conjuntos precisar crescer, altere AQUI e em `roadmap-template.md` — nunca em apenas um lugar.

## Validações por Etapa

### Etapa 0 — Validação do Roadmap (antes de qualquer geração)

**Input:** `roadmap.md`
**Output:** `.build/project.json` + `validation_reports/step0_roadmap.yaml`

**Checks (erro = PARAR):**
1. ✓ Título `#` na linha 1; seções `## Módulos` (≥1 módulo com ≥1 feature) e `## Entidades de Dados` (≥1 entidade) presentes
2. ✓ Cada módulo tem `**Tipo de tela**` ∈ `screen_types` (valor fora da lista → erro listando os aceitos)
3. ✓ Tipos de gráfico mencionados em `**Gráfico...**`/`**Gráficos:**` ∈ `chart_types`
4. ✓ `**Layout**`, se presente, usa apenas `layout_tokens` separados por `|`
5. ✓ `**Papel**` das entidades, se presente, ∈ `entity_roles`
6. ✓ Cor primária em `## Branding` é hex válido (`#RRGGBB`) ou `auto`; auto deve produzir cor resolvida e primary_source no design system antes da geração visual
7. ✓ Nenhum `TODO:` em campos obrigatórios: Descrição, Tipo de tela, ≥1 feature por módulo, Campos principais de cada entidade

**Checks (aviso = continuar, reportar):**
8. ⚠ Módulo sem `**Objetivo do usuário**` (o subtítulo da tela ficará genérico)
9. ⚠ Módulo sem `**Layout**` (será inferido do tipo de tela)
10. ⚠ Módulo `dashboard|analytics|report` sem `**Drill-down**` (tela ficará estática)
11. ⚠ Módulo sem `**Estado vazio**` (usará texto padrão)
12. ⚠ Entidade sem `**Volumetria de demo**` (dimensão → 100, fato → 3.000 linhas) ou sem `**Distribuições**` (valores uniformes — parecem menos reais)
13. ⚠ `## Contexto de Demonstração` ausente ou com `TODO:` (Home e mock terão narrativa genérica)
14. ⚠ Entidade com `**Papel**: fato` sem campo de data (sazonalidade não poderá ser aplicada)
15. ⚠ Módulo `approval_queue` sem `**Badge na sidebar**` (contador de pendências não será gerado)

---

### Etapa 1 — Validação de Requirements

**Input:** `roadmap.md`  
**Output:** `docs/requirements.yaml`

**Checks:**
1. ✓ Arquivo `roadmap.md` existe e não está vazio
2. ✓ YAML gerado é válido (parse sem erros)
3. ✓ Campos obrigatórios presentes: `project.name`, `modules`, `entities`
4. ✓ Todos os módulos têm pelo menos 1 feature
5. ✓ Todas as entidades têm `name`, `description`, `module`
6. ✓ Referências de módulos nas entidades existem
7. ✓ IDs de features e business_rules são únicos
8. ✓ `modules[].screen_type` ∈ `screen_types`; `modules[].charts[].type` ∈ `chart_types`; `modules[].kpis[].kind` ∈ `kpi_kinds`
9. ✓ `modules[].layout` (lista de faixas) usa apenas `layout_tokens`; se ausente no roadmap, foi preenchido pelo fallback por `screen_type`
10. ✓ `modules[].drilldowns[].source_chart` referencia um `charts[].id` do mesmo módulo e `target_field` existe na entidade do grid
11. ✓ `entities[].demo.volume` é inteiro > 0; `entities[].demo.distributions[].field` existe em `fields[]`
12. ✓ `demo_context.credentials[]` cobre todos os `roles[]`

**Output:** `validation_reports/step1_requirements.yaml`

---

### Etapa 2 — Validação de Data Model

**Input:** `docs/requirements.yaml`  
**Output:** `docs/data_model.yaml`

**Checks:**
1. ✓ Todas as entidades de `requirements.yaml` estão presentes
2. ✓ Campos obrigatórios em toda entidade: `id`, `created_at`, `updated_at`
3. ✓ Tipos SQL são válidos para SQL Server (int, varchar, decimal, datetime2, bit, etc.)
4. ✓ Foreign keys referenciam tabelas existentes
5. ✓ Foreign keys referenciam campos que existem na tabela alvo
6. ✓ Campos de FK têm tipo compatível com o campo referenciado
7. ✓ Nomes de tabelas seguem snake_case
8. ✓ Não há ciclos de dependência em FKs (detectar com DFS)
9. ✓ Enums têm pelo menos 1 valor
10. ✓ Relacionamentos referenciam entidades existentes

**Output:** `validation_reports/step2_data_model.yaml`

---

### Etapa 2.7 — Validação de Business Logic

**Input:** `docs/requirements.yaml`, `docs/data_model.yaml`
**Output:** `docs/business_logic.yaml`

**Checks:**
1. ✓ YAML válido
2. ✓ Toda regra tem `logic_type` em `validation | derived_field | interactive_formula | workflow_rule`
3. ✓ Toda regra `logic_type: interactive_formula` tem `formula.expression` E ≥1 `formula.variables[]` com `interactive: true`
4. ✓ Toda regra `logic_type: validation` tem `validation.condition` E `validation.error_message`
5. ✓ `entity` e `variables[].field`/`output_fields[].name` referenciam campos reais de `data_model.yaml`
6. ⚠ Se `confidence_summary.needs_review` não estiver vazio → warning (reportar ao usuário, não bloqueia)

**Output:** `validation_reports/step2_7_business_logic.yaml`

---

### Etapa 3 — Validação de SQL

**Input:** `docs/data_model.yaml`  
**Output:** `database/schema.sql`, `database/views.sql`, `database/procedures.sql`

**Checks:**
1. ✓ Arquivos SQL existem e não estão vazios
2. ✓ Todas as entidades têm CREATE TABLE em `schema.sql`
3. ✓ Ordem de criação respeita dependências de FK
4. ✓ Sintaxe SQL é válida (parse básico)
5. ✓ Views referenciam apenas tabelas criadas
6. ✓ Procedures seguem padrão: `usp_<entity>_get_all`, `_get_by_id`, `_insert`, `_update`, `_delete`
7. ✓ Procedures usam campos que existem na tabela
8. ✓ Uso de `IF NOT EXISTS` / `CREATE OR ALTER` para idempotência

**Output:** `validation_reports/step3_sql.yaml`

---

### Etapa 4 — Validação de Mock Data (motor volumétrico)

**Input:** `docs/data_model.yaml`, `docs/mock_spec.yaml` (se existir)
**Output:** `mock_data/<entity>.csv` e `mock_data/<entity>.json`, `database/seed.sql`

**IMPORTANTE:** Esta validação deve ser feita lendo os arquivos do DISCO, não com base no que foi gerado na sessão atual. Não confie na memória — verifique cada arquivo explicitamente.

**Procedimento obrigatório antes de qualquer check:**
1. Ler `docs/data_model.yaml` e extrair a lista de entidades com `table:` (ignorar enums)
2. Para cada entidade, verificar se `mock_data/<entidade>.csv` existe E se `mock_data/<entidade>.json` existe
3. Exibir resultado por entidade: `✓ entidade (csv ✓ json ✓, N rows)` ou `✗ entidade (csv ✗ json ✓)` etc.
4. Se qualquer arquivo estiver faltando → marcar validação como FAILED antes de verificar conteúdo

**Checks de conteúdo (somente para arquivos que existem):**
1. ✓ Para cada entidade: AMBOS `.csv` E `.json` existem no disco
2. ✓ CSV não está vazio (tem header + pelo menos 1 linha de dados)
3. ✓ JSON é válido (parse sem erros) e tem pelo menos 1 objeto
4. ✓ Headers do CSV correspondem aos campos da entidade no data_model
5. ✓ Todos os registros têm campo `id` único dentro do arquivo
6. ✓ Foreign keys apontam para IDs que existem nos arquivos das entidades referenciadas
7. ✓ Campos de texto com vírgula estão entre aspas duplas no CSV
8. ✓ Valores de enum estão na lista permitida
9. ✓ **Volume ≥ `mock_spec.yaml → entities[].volume`** (se o spec existir) — demo com volume realista, não brinquedo
10. ✓ **`database/seed.sql` existe** (gerado pelo motor no Step 4) e tem bloco por entidade
11. ✓ **Garantias de demo** (se aplicável):
    - Se houver tela `approval_queue`: ≥ 5 linhas com status `Pendente Aprovação` (ou equivalente) na entidade de aprovação
    - Toda dimensão usada em filtro `select` (lendo `requirements.yaml → modules[].filters[]`) tem ≥ 4 valores distintos no mock
    - Fato principal (entidade `role: fato` com campo de data) cobre todos os meses do `demo.period_months` — nenhum mês vazio
    - Top-N do gráfico de ranking (lendo `requirements.yaml → modules[].charts[]` com type `bar`/`treemap`) tem N itens distintos

**Output:** `validation_reports/step4_mock_data.yaml`

---

### Etapa 5 — Validação de SQL Seed (gerado pelo motor)

**Input:** `docs/data_model.yaml`, `database/seed.sql` (gerado pelo Step 4)
**Output:** `validation_reports/step5_seed.yaml`

**Checks:**
1. ✓ Arquivo `seed.sql` existe e não está vazio
2. ✓ Todas as entidades do `data_model.yaml` têm bloco de INSERT (cabeçalho `-- SEED: <entidade>`)
3. ✓ Ordem de INSERT respeita dependências de FK (ordem topológica)
4. ✓ Uso de `SET IDENTITY_INSERT ON/OFF` com `GO` entre blocos
5. ✓ Idempotência: cada bloco usa `IF NOT EXISTS` ou `MERGE` (não duplica em reexecução)
6. ✓ Sintaxe SQL Server/Fabric válida: aspas escapadas (`''`), datas ISO, decimais com ponto, bits como `1`/`0`
7. ✓ Nenhum `TRUNCATE`/`DELETE` (compatível com ambiente compartilhado)
8. ✓ Volume por tabela ≤ `seed_cap` (default 2000) — CSV em `mock_data/` mantém volume completo

**Output:** `validation_reports/step5_seed.yaml`

---

### Etapa 6 — Validação de Screen Definition

**Input:** `docs/requirements.yaml`  
**Output:** `docs/screens_definition.yaml`

**Checks:**
1. ✓ YAML é válido
2. ✓ Todas as páginas têm: `title`, `route`, `module`, `components`
3. ✓ Rotas começam com `/` e são únicas
4. ✓ Data sources referenciam entidades existentes em `data_model.yaml`
5. ✓ Componentes têm `id`, `type`, `config`
6. ✓ Tipos de componente são válidos: filter, grid, modal, form, card, chart, kpi, button, tabs
7. ✓ Grids referenciam entidades existentes
8. ✓ Colunas de grid referenciam campos existentes na entidade
9. ✓ Charts têm campos x/y válidos
10. ✓ Filtros referenciam campos existentes
11. ✓ Toda página `screen_type: simulation` (ou `has_simulation: true`) tem ≥1 regra em `docs/business_logic.yaml` com `logic_type: interactive_formula` vinculada ao seu módulo — se não houver, ERRO: "tela de simulação sem fórmula real declarada — provável fallback ao placeholder genérico"
12. ✓ `simulation_panel.config.params` corresponde 1:1 a `formula.variables[].name` onde `interactive: true` da regra vinculada (mesmos nomes, mesma quantidade)
13. ✓ Colunas de grid marcadas `type: computed` referenciam uma regra `logic_type: derived_field` existente em `business_logic.yaml`
14. ✓ Se houver cenário compartilhado: `scenario_dependencies.yaml` mapeia parâmetros reais para RN, outputs e consumidores existentes; default_view e escopo explícitos, aprovação somente quando declarada. Contrato e critérios de jornada em `skill-demo-scenario.md`; não declarar propagação validada apenas por existência de arquivos.
15. ✓ Assistente habilitado (default): catálogo de análises específico do roadmap, handlers registrados, fontes/campos/regras existentes, exclusões justificadas e ações de navegação/simulação válidas. Perguntas sem regra de demanda não geram ganho de volume. Executar validate_catalog e fixtures do projeto; integração/aceite em skill-pricing-assistant.md.

**Output:** `validation_reports/step6_screens.yaml`

---

### Etapa 7 — Validação de Frontend Pages

**Input:** `docs/screens_definition.yaml`, `docs/data_model.yaml`  
**Output:** `frontend/pages/<page>/*.py`

**Checks:**
1. ✓ Para cada página existem 4 arquivos: `_page.py`, `_components.py`, `_queries.py`, `_callbacks.py`
2. ✓ Arquivos Python são válidos (parse sem erros de sintaxe)
3. ✓ `_page.py` tem `register_page()` e `layout()`
4. ✓ `_callbacks.py` tem `register_callbacks()`
5. ✓ IDs seguem padrão `<page>-<component>`
6. ✓ Imports estão corretos (não há imports de módulos inexistentes)
7. ✓ `_queries.py` lê de `mock_data/` (não conecta ao banco)
8. ✓ Design system está aplicado (className corretas)
9. ✓ Tipagem Python presente em todas as funções
10. ✓ Não usa `dbc.Container` como raiz do layout
11. ✓ Para páginas vinculadas a uma regra `interactive_formula` em `business_logic.yaml`: `<pagina>_page.py` ou `<pagina>_components.py` contém um `dcc.Slider`/`param_slider(...)`/`dbc.Input(type="number")` com `id` casando `<pagina>-param-<variable.name>` para CADA `formula.variables[].interactive: true` — senão ERRO: "parâmetro interativo declarado sem controle de UI correspondente"
12. ✓ `<pagina>_queries.py` contém uma função cujo corpo referencia (grep textual) os nomes de `formula.variables[]`/`output_fields[]` combinados por um operador (não apenas retorna uma coluna já existente do CSV sem transformação) — heurística "fórmula é calculada, não copiada"
13. ✓ `<pagina>_callbacks.py` chama essa função dentro de um `@callback` disparado por `Input("<pagina>-btn-simular", "n_clicks")` (ou id equivalente) — a função de cálculo é EXECUTADA por uma ação do usuário, não apenas definida
14. ✓ Para entidades com regra `derived_field` exibida em grid/relatório da página: `<pagina>_queries.py` calcula o campo via pandas ao carregar os dados (grep de atribuição `df["<output_field>"] = ...`) — não apenas lê a coluna do `mock_data/*.csv` como se já viesse pronta

**Output:** `validation_reports/step7_frontend.yaml`

---

### Etapa 8 — Validação de App Principal

**Input:** Todas as páginas geradas  
**Output:** `frontend/app.py`, `frontend/components/sidebar.py`

**Checks:**
1. ✓ `app.py` existe e é válido
2. ✓ `sidebar.py` existe e é válido
3. ✓ Todas as páginas têm link na sidebar
4. ✓ `guard_routes` callback existe e é único
5. ✓ Todos os `register_callbacks()` são importados e chamados
6. ✓ `dcc.Store(id="current-user")` existe
7. ✓ Página de login existe em `frontend/pages/login/`
8. ✓ Não há duplicação de `Output("url", "pathname")`

**Output:** `validation_reports/step8_app.yaml`

---

### Etapa 9 — Validação de Backend

**Input:** `docs/data_model.yaml`  
**Output:** `backend/models/`, `backend/schemas/`, `backend/repositories/`, `backend/services/`, `backend/api/routes/`

**Checks:**
1. ✓ Para cada entidade existem 5 arquivos (model, schema, repository, service, route)
2. ✓ Arquivos Python são válidos
3. ✓ Models SQLAlchemy têm campos correspondentes ao data_model
4. ✓ Schemas Pydantic têm Create, Update, Response
5. ✓ Repositories têm métodos CRUD completos
6. ✓ Routes têm endpoints GET, GET BY ID, POST, PUT, DELETE
7. ✓ Tipagem Python presente
8. ✓ `main.py` importa e registra todos os routers
9. ✓ Tratamento de erros com HTTPException
10. ✓ Para entidades com regra `interactive_formula` em `business_logic.yaml`: existe rota `POST /<entidade>s/simular` (ou `/calcular`) em `backend/api/routes/<entidade>.py`
11. ✓ Essa rota chama uma função de `backend/services/<entidade>.py` que implementa a fórmula — E essa função é de fato referenciada em algum lugar do projeto (grep: toda função `def calcular_*`/`def simular*` definida em `services/` deve ter ≥1 chamada correspondente fora da própria definição, seja em `api/routes/` ou nos scripts de mock). Se a função existir mas nenhuma chamada for encontrada → ERRO CRÍTICO: "função de cálculo definida em services/<entidade>.py nunca é chamada — código morto, fórmula não está em uso"
12. ✓ Para entidades com regra `validation` (`severity: block`): `backend/schemas/<entidade>.py` tem um `@field_validator`/`@model_validator` implementando `validation.condition` e levantando erro com `validation.error_message`

**Output:** `validation_reports/step9_backend.yaml`

---

### Etapa 10 — Validação de Configuração

**Output:** `requirements.txt`, `README.md`

**Checks:**
1. ✓ `requirements.txt` existe com todas as dependências
2. ✓ Versões de pacotes são compatíveis
3. ✓ `README.md` existe com seções obrigatórias
4. ✓ Estrutura de pastas documentada
5. ✓ Comandos de execução presentes

**Output:** `validation_reports/step10_config.yaml`

---

## Estrutura do Relatório de Validação

```yaml
validation:
  step: string
  timestamp: datetime
  status: success | warning | error
  
checks:
  - id: string
    description: string
    status: pass | fail | warning
    details: string
    
errors:
  - severity: critical | high | medium | low
    message: string
    file: string
    line: int
    suggestion: string
    
warnings:
  - message: string
    file: string
    suggestion: string
    
summary:
  total_checks: int
  passed: int
  failed: int
  warnings: int
  
recommendations:
  - action: string
    priority: high | medium | low
```

---

## Modo de Uso

### Validação Completa
```
/skill00-validator
```

### Validação de Etapa Específica
```
/skill00-validator step2
```

### Validação com Auto-fix (futuro)
```
/skill00-validator --fix
```

---

## Regras de Validação

1. **Fail Fast**: Parar na primeira validação crítica que falhar
2. **Warnings não bloqueiam**: Avisos são reportados mas não impedem o build
3. **Sugestões de correção**: Cada erro deve ter uma sugestão de como corrigir
4. **Idempotência**: Executar validação múltiplas vezes não altera estado
5. **Performance**: Validações devem ser rápidas (<5s por etapa)

---

## Integração com Build

O `build.md` deve chamar esta skill automaticamente:

```markdown
## Antes de cada etapa
1. Executar `/skill00-validator step{N-1}`
2. Se status = error → PARAR e reportar
3. Se status = warning → CONTINUAR mas logar
4. Se status = success → PROSSEGUIR
```

---

## Saída em Caso de Erro

```
❌ VALIDAÇÃO FALHOU — Etapa 2 (Data Model)

Erros Críticos (2):
  1. [CRITICAL] Foreign key 'pedidos.cliente_id' referencia tabela inexistente 'clientes'
     → Arquivo: docs/data_model.yaml:45
     → Sugestão: Adicionar entidade 'clientes' ou corrigir nome da FK
     
  2. [HIGH] Campo 'created_at' ausente na entidade 'produtos'
     → Arquivo: docs/data_model.yaml:78
     → Sugestão: Adicionar campo obrigatório 'created_at: datetime2'

Avisos (1):
  1. [MEDIUM] Entidade 'logs' não tem índices definidos
     → Pode impactar performance em consultas

Recomendações:
  - Corrigir erros críticos antes de prosseguir
  - Executar: /skill02-data-model --fix-entity produtos

Build INTERROMPIDO na Etapa 2.
```

---

## Restrições

- Validação é **read-only** — não modifica arquivos
- Não executa SQL ou conecta ao banco
- Não executa código Python (apenas parse estático)
- Contexto máximo: 4.000 tokens de saída por relatório
