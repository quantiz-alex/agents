# Skill 00 — Validation & Consistency Check

Valida a consistência e integridade entre todos os artefatos gerados antes de prosseguir para a próxima etapa do pipeline.

## Quando Usar

- Antes de cada etapa do `/build` para garantir que os artefatos de entrada estão corretos
- Após modificações manuais em YAMLs para verificar impactos
- Como diagnóstico quando o build falha

## Argumento Opcional

`$ARGUMENTS` — etapa a validar (ex.: `step2` para validar após data_model.yaml). Se vazio, valida tudo.

---

## Validações por Etapa

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

### Etapa 4 — Validação de Mock Data

**Input:** `docs/data_model.yaml`  
**Output:** `mock_data/<entity>.csv` e `mock_data/<entity>.json`

**IMPORTANTE:** Esta validação deve ser feita lendo os arquivos do DISCO, não com base no que foi gerado na sessão atual. Não confie na memória — verifique cada arquivo explicitamente.

**Procedimento obrigatório antes de qualquer check:**
1. Ler `docs/data_model.yaml` e extrair a lista de entidades com `table:` (ignorar enums)
2. Para cada entidade, verificar se `mock_data/<entidade>.csv` existe E se `mock_data/<entidade>.json` existe
3. Exibir resultado por entidade: `✓ entidade (csv ✓ json ✓)` ou `✗ entidade (csv ✗ json ✓)` etc.
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

**Output:** `validation_reports/step4_mock_data.yaml`

---

### Etapa 5 — Validação de SQL Seed

**Input:** `docs/data_model.yaml`, `mock_data/*.json`  
**Output:** `database/seed.sql`

**Checks:**
1. ✓ Arquivo `seed.sql` existe e não está vazio
2. ✓ Todas as entidades têm bloco de INSERT
3. ✓ Ordem de INSERT respeita dependências de FK
4. ✓ Uso de `SET IDENTITY_INSERT ON/OFF`
5. ✓ IDs nos INSERTs correspondem aos IDs do mock_data
6. ✓ Sintaxe SQL é válida
7. ✓ Strings com aspas simples escapadas corretamente

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
