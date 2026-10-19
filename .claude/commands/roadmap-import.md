# /roadmap-import — Gerador de Roadmap a partir de Documento do Cliente

Analisa qualquer documento de entrada (roadmap técnico, proposta comercial, especificação funcional, briefing) e gera o `roadmap.md` do pipeline preenchido com as informações extraídas. Campos que não puderem ser inferidos com confiança recebem marcação `TODO:` para revisão manual.

## Argumento obrigatório

`$ARGUMENTS` — caminho do documento de origem (relativo ao diretório atual ou absoluto).

Se vazio → exibir instruções e exemplos, depois **PARAR**.

---

## Passo 1 — Ler o documento de origem

Ler o arquivo em `$ARGUMENTS`. Se não existir → PARAR com mensagem de erro.

Identificar o tipo do documento:
- Roadmap técnico / estimativa de prazo
- Proposta comercial
- Especificação funcional (FRD/PRD)
- Briefing / apresentação convertida
- Outro

---

## Passo 2 — Extração estruturada

Analisar o documento e extrair os seguintes campos. Para cada campo, registrar internamente: **[ENCONTRADO]**, **[INFERIDO]** (deduziu a partir do contexto) ou **[AUSENTE]** (não encontrado).

### 2.1 Projeto
- `nome`: título do projeto — remover subtítulos após ":"
- `descricao`: o que o sistema faz, qual problema resolve, quem usa — máx. 3 frases

### 2.2 Perfis de Acesso
Identificar grupos de usuários mencionados (ex.: "time de Pricing", "área fiscal", "admin", "gestor") e mapear para roles:
- Nomes em snake_case, sem espaços
- Inferir permissões a partir do verbo + substantivo ("visualizar resultados" → [visualizar], "parametrizar regras" → [criar, editar])
- Sempre incluir `admin` com permissões `full`
- Marcar como `TODO:` quando as permissões não puderem ser inferidas com confiança

### 2.3 Módulos
Para cada bloco funcional identificado (sprint, fase, entregável, requisito funcional agrupado):

**Prioridade:** inferir de sinais como "MVP", "v0", "Sprint 1" → `high`; "v1", "Sprint 2", "roadmap futuro" → `medium`/`low`.

**Tipo de tela** — mapear por palavras-chave do escopo:
| Palavras-chave no texto | Tipo |
|---|---|
| importar, upload, ingestão, carga, formulário, cadastrar, configurar, parametrizar | `form` |
| listar, grid, tabela, CRUD, gerenciar, buscar | `grid` |
| listar + detalhar item, ficha, "ao clicar abre" | `master_detail` |
| dashboard, painel, visão geral, KPI, métricas, indicadores | `dashboard` |
| análise, analítico, evolução, matriz, múltiplos gráficos, drill-down | `analytics` |
| relatório, exportar, auditoria, rastreabilidade, histórico | `report` |
| simular, cenário, "e se", impacto de parâmetro, elasticidade | `simulation` |
| aprovar, rejeitar, fila, pendências, workflow de aprovação | `approval_queue` |
| combinação sem predominância | `mixed` |

> Lista canônica de `Tipo de tela` (única aceita pelo validador): `dashboard | analytics | grid | master_detail | form | report | mixed | simulation | approval_queue` — igual à do `roadmap-template.md`.

**Ícone Bootstrap** — sugestão por tipo de módulo (alinhado ao template):
| Tema | Ícone |
|---|---|
| Preços / pricing | `tag` |
| Dashboard / visão geral | `speedometer2` |
| Análise / analytics | `bar-chart-line` |
| Simulação / cenários | `calculator` |
| Relatório | `file-earmark-bar-graph` |
| Importação / upload | `cloud-upload` |
| Tributário / fiscal | `receipt` |
| Usuários / acesso | `people` |
| Configuração / parametrização | `gear` |
| Produtos / portfólio | `box-seam` |
| Clientes | `person-badge` |
| Aprovação / workflow | `check2-circle` |

**Grupo de menu**: agrupar módulos por afinidade (ex.: `Visão Geral`, `Pricing`, `Operação`, `Administração`). Se o documento não sugerir, usar: dashboards/analytics → `Visão Geral`; simulação/preços/aprovação → `Pricing`; cadastros → `Cadastros`; usuários/config → `Administração`.

**Objetivo do usuário** (1 frase, obrigatório): "Como <role>, quero <ação> para <decisão>". Inferir do contexto; marcar `TODO:` se não houver base.

**KPIs** (para `dashboard`, `analytics`, `mixed`, `simulation`): extrair métricas mencionadas explicitamente (ex.: "Volume, Receita NIV, Margem"). Colocar `TODO:` se não mencionado. Indicar se o KPI é `comparação` (atual × simulado/anterior) ou `simples`.

**Gráficos**: inferir tipo a partir do dado — evolutivo/temporal → `line` (ou `combo` se volume + valor), comparação entre categorias → `bar`, ranking → `bar` horizontal, proporção ≤5 → `donut`, matriz 2 dimensões → `heatmap`, hierarquia/participação → `treemap`, etapas → `funnel`, meta × realizado → `gauge`, sensibilidade preço × volume → `elasticity_curve`, ponte de impacto → `waterfall`.

**Layout**: sugerir a DSL do template (`kpis:4 | charts:2col | grid`) a partir dos componentes identificados; se houver mais de 4 gráficos, usar `charts:3col` + `charts:2col`.

**Drill-down**: quando o texto disser "ao clicar em X, ver Y" ou "detalhar por" → `gráfico <X> → filtra grid por <campo>`.

**Volumetria e distribuições** (§ Entidades): extrair números do documento ("1.200 SKUs", "35 fornecedores", "24 meses de histórico", "80% da receita em 20% dos produtos" → `pareto`). Se ausente, deixar `TODO:` — o pipeline assume padrão (dimensão 50–300, fato 2.000–5.000 linhas).

**Contexto de Demonstração** (§ nova seção): persona da demo, cenário narrativo, números-âncora, período de dados. Inferir do público-alvo do documento; marcar `TODO:` o que não houver base.

**Filtros**: inferir a partir de dimensões mencionadas (canal, região, período, produto, status).

**Funcionalidades / Features**: cada requisito funcional `[RFxx]` ou item de escopo vira uma feature `[F-NNN]`. Preservar os IDs originais se existirem (RF01 → F-001).

**Ações disponíveis**: inferir do verbo:
- "importar", "upload", "ingestão" → `importar-csv`
- "exportar", "download" → `exportar-excel`
- "gerar lista", "calcular", "processar" → `visualizar` + botão de ação
- "criar", "cadastrar", "novo" → `criar`
- "editar", "parametrizar", "configurar" → `editar`
- "excluir", "deletar" → `excluir`
- "aprovar", "validar" → `approve`; "rejeitar", "devolver" → `reject`
- "enviar para aprovação", "submeter" → `submit_approval`
- "simular", "comparar cenários" → `simulate` (+ `criar` para salvar cenário)
- "detalhar", "abrir ficha", "ver detalhes" → `detalhar` (modal de detalhe — Detalhar)

**Regras de negócio**: extrair restrições e invariantes mencionados. Preservar IDs se existirem.

### 2.4 Entidades de Dados
Identificar entidades a partir de:
- Substantivos principais do domínio (ex: "Produto", "CenarioSimulacao", "RegrasTributaria")
- Tabelas ou bases de dados mencionadas (ex: "Nielsen", "Preços ERP", "P&L SAP")
- Relacionamentos implícitos ("um cenário tem muitos produtos")

Para cada entidade inferida:
- Sugerir campos principais a partir do contexto — marcar com `TODO:` se não houver detalhes suficientes
- Indicar o módulo de origem

**SEMPRE incluir a entidade `Usuarios`** com campos padrão do pipeline.

### 2.5 Branding
- Se cores forem mencionadas → usar; senão → `TODO: #1045C8`
- Logo → sempre `TODO:` (é um arquivo, não pode ser inferido de texto)
- Nome na sidebar → usar a abreviação do projeto se disponível (ex: "KC Pricing")

### 2.6 Requisitos Não-Funcionais
Extrair diretamente do documento. Traduzir para o formato do template.

### 2.7 Integrações Externas
Identificar sistemas externos mencionados (ERP, SAP, Nielsen, APIs, banco externo).

---

## Passo 3 — Verificar divergências de stack

Comparar o stack mencionado no documento com o stack fixo do pipeline:

| Divergência possível | Ação |
|---|---|
| PostgreSQL / MySQL / outros bancos | Usar SQL Server (stack do pipeline). Adicionar nota `<!-- Banco original: PostgreSQL — adaptado para SQL Server -->` |
| React / Vue / Angular | Ignorar — o pipeline gera Dash. Adicionar nota |
| Flask / Django / Node | Ignorar — o pipeline gera FastAPI. Adicionar nota |
| Pandas / NumPy | Compatível ✓ |
| Plotly / Dash | Compatível ✓ |

---

## Passo 4 — Escopo de versão

Se o documento tiver múltiplas versões/sprints (v0, v1, MVP, Fase 2...), **focar na versão mais imediata (MVP / v0 / Sprint 1)** para o `roadmap.md` e adicionar ao final uma seção `## Escopo Futuro (fora do MVP)` com os itens de versões posteriores, como referência.

---

## Passo 5 — Gerar `roadmap.md`

Ler o template de `../.claude/templates/roadmap-template.md`. Substituir todos os campos com os valores extraídos. Manter a estrutura e os comentários do template.

**Convenções de marcação no output:**
- Valor extraído com alta confiança → escrever direto (sem `TODO:`)
- Valor inferido com confiança média → escrever + comentário `<!-- inferido: revisar -->`
- Valor ausente → manter `TODO:` do template
- Divergência de stack → comentário `<!-- nota: ... -->`

Escrever em `./roadmap.md` (diretório atual).

Se `roadmap.md` já existir → perguntar ao usuário antes de sobrescrever. Se confirmar, criar backup `roadmap.md.bak`.

---

## Passo 6 — Relatório de extração

Exibir ao final:

```
══════════════════════════════════════════
  ROADMAP-IMPORT — RELATÓRIO
══════════════════════════════════════════

  Fonte: <nome do arquivo>
  Projeto: <nome extraído>
  Tipo de documento: <tipo identificado>

  EXTRAÍDO COM CONFIANÇA:
    ✅ Nome e descrição do projeto
    ✅ <N> módulos identificados (<lista>)
    ✅ <N> features mapeadas ([F-001]...[F-NNN])
    ✅ <N> entidades inferidas
    ✅ Requisitos não-funcionais

  REQUER REVISÃO MANUAL (marcado com TODO:):
    ⚠ Perfis de acesso — permissões por role
    ⚠ Campos detalhados das entidades
    ⚠ Branding (cores, logo)
    ⚠ <outros campos ausentes>

  DIVERGÊNCIAS DE STACK:
    📌 <lista de divergências encontradas e como foram tratadas>

  ESCOPO EXCLUÍDO (versões futuras):
    📋 <módulos/features de v1 ou posteriores movidos para ## Escopo Futuro>

  Próximos passos:
    1. Revisar ./roadmap.md — preencher os TODO:
    2. /lighthouse   ← iniciar o build quando o roadmap estiver completo
══════════════════════════════════════════
```

---

## Uso

```
/roadmap-import roadmap_estimativas.md
/roadmap-import ../docs/briefing_cliente.md
/roadmap-import C:/propostas/sistema_gestao_comercial.md
```

## Notas

- Funciona com qualquer formato de documento textual convertido para `.md` (Word → MD, PDF → MD, etc.)
- A qualidade do output depende da riqueza do documento de entrada — quanto mais detalhado, menos `TODO:`
- Para documentos muito longos (>500 linhas), o agente foca nos primeiros dois terços (geralmente onde está o escopo funcional) e menciona o que ignorou
- Não modifica o documento de origem
