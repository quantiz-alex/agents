# Skill 04 — Mock Data Generation Skill (v4 — motor volumétrico)

Gera dados de demonstração **em volume e com forma realista** (sazonalidade, Pareto, FKs coerentes, catálogos pt-BR) a partir de `docs/data_model.yaml` + `docs/requirements.yaml → entities[].demo` + `docs/business_logic.yaml`.

> Em v3 o LLM escrevia 10–50 linhas por entidade à mão. Isso produzia "Top 10" com 8 barras, donuts de 3 fatias e grids de 1 página — a demo parecia brinquedo. Agora o LLM escreve **a especificação** (`docs/mock_spec.yaml`) e um **script** executa a geração (`scripts/generate_mock.py`) — milhares de linhas, reprodutíveis (seed), sem limite de tokens.

## Instruções

1. Ler `docs/data_model.yaml` (entidades com `table:`, campos, tipos, FKs, enums), `docs/requirements.yaml` (`entities[].role`, `entities[].demo.volume/distributions/example_row`, `demo_context`) e `docs/business_logic.yaml` (campos `derived_field`/`output_fields` com `persist: false` → **omitir do mock**).
2. Copiar `../.claude/templates/mock_generator.py` → `scripts/mock_generator.py` (se não existir).
3. Escrever `docs/mock_spec.yaml` — uma entrada por entidade, **traduzindo cada `distributions[].spec` do roadmap para o campo `gen`** (mesma sintaxe) e preenchendo o restante pelas regras de fallback abaixo.
4. Escrever `scripts/generate_mock.py`:
   ```python
   """Gera mock_data/ e database/seed.sql a partir de docs/mock_spec.yaml. Reprodutível (seed)."""
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent))
   from mock_generator import generate, load_spec, validate_outputs

   ROOT = Path(__file__).resolve().parents[1]
   spec = load_spec(ROOT / "docs" / "mock_spec.yaml")
   generate(spec, ROOT / "mock_data", ROOT / "database" / "seed.sql")
   problems = validate_outputs(spec, ROOT / "mock_data")
   if problems:
       print("\n".join(problems)); sys.exit(1)
   ```
5. **Executar** `python scripts/generate_mock.py` (exige `pandas`, `numpy`, `pyyaml`; `bcrypt` opcional para senha demo). Ler o output: contagens por entidade, avisos, resultado da validação.
6. Se a execução falhar → corrigir o spec (não o motor) e reexecutar. Erros típicos: FK para entidade inexistente, `derivado(...)` referenciando campo ainda não gerado (ordem é resolvida automaticamente, mas refs `pai.campo` exigem o campo `<pai>_id` na entidade), enum com valores fora do `data_model.yaml`.
7. Checklist final **no disco**: 2 arquivos por entidade, volume ≥ spec, FKs válidas (`python scripts/mock_generator.py docs/mock_spec.yaml --validate`).

## Regras de tradução roadmap → `gen`

| Situação | `gen` |
|---|---|
| `distributions[].spec` presente | copiar literalmente (`enum(...)`, `faixa(...)`, `normal(...)`, `pareto`, `sazonal(...) + tendencia(...)`, `derivado(...)`, `lista(BR:...)`) |
| `id` | `sequence` (sempre; adicionado automaticamente se omitido) |
| FK (`foreign_key` no data_model) | `fk(<entidade_pai>)`; se a entidade pai é dimensão de produto/cliente e esta é fato → `fk(<pai>, pareto)` (poucos itens concentram vendas) |
| enum do `data_model.yaml` sem pesos | `enum(A, B, C)` — mas prefira pesos plausíveis (status ativo 90%+, pendentes 20–30%) |
| campo de data em `role: fato` | `sazonal(mensal, pico: nov,dez) + tendencia(+6% ao ano)` (ajustar picos ao domínio: agro → safra; varejo → nov,dez; B2B → mar,jun,set,nov) |
| campo de data em dimensão (`vigencia`, `cadastro`) | `faixa(últimos 18 meses)` |
| `created_at` / `updated_at` | `audit` |
| moeda/custo/preço sem spec | `pareto(<min>, <max>)` com faixa coerente aos números-âncora (`demo_context.anchors`) |
| quantidade/volume | `normal(m, s, 1)` (fato) ou `pareto(min, max)` (dimensão) |
| percentual | `normal(m, s, min, max)` |
| `nome` de empresa/fornecedor/cliente | `lista(BR:empresas)`; pessoa → `lista(BR:nomes)`; produto → `lista(BR:produtos:<dominio>)` (`autopecas`, `agro`, `varejo`, `farma`, `industria`, `servicos`, `generico`) |
| `codigo`/`sku` | `codigo(<campo_categoria>:3)` ou `codigo(PRD)` |
| `cidade`/`uf`/`regiao` | `lista(BR:cidades)` / `lista(BR:uf)` / `lista(BR:regiao)` — nessa ordem de campos, para ficarem coerentes |
| `email` | `email(nome, <dominio do projeto>)` |
| `senha_hash` | `bcrypt(demo)` |
| campos de aprovação (`aprovado_por`, `aprovado_em`, `comentario_aprovacao`) | `se(status == 'Aprovado' or status == 'Rejeitado', <gen>, null)` |
| `parametros` (JSON) | `json(campo1, campo2)` |
| texto livre (descrição, comentário) | `texto(8)` |
| bit sem spec | `enum(1:90%, 0:10%)` |
| **campo `derived_field`/`output_field` com `persist: false`** | **NÃO incluir** — calculado em runtime (frontend `_queries.py` / backend service). Registrar aviso "campo <nome> é derivado — omitido do mock" |
| campo derivado **persistido** (ex.: `receita = quantidade * preco_unitario` numa fato) | `derivado(quantidade * preco_unitario)` — usar a mesma expressão de `business_logic.yaml` |
| pesos/frações (ex.: `volume_peso`, participação) | tipo `decimal` (soma por grupo = 1). Volumes derivados (total × peso) **não** são persistidos como inteiro por linha — calcular em runtime sem arredondar (`core.md` §3) |

## Volumetria (fallback quando o roadmap não informa)

| `role` | volume |
|---|---|
| `dimensao` | 100 (produto/SKU: 500; fornecedor/categoria: 30) |
| `fato` | 3.000 (ajustar para que os números-âncora batam: ex. receita anual ≈ Σ receita das linhas nos últimos 12 meses) |
| `apoio` | 12 (usuarios: garantir `fixed_rows` com `demo_context.credentials` → `{nome, email, role}`; `senha_hash: bcrypt(demo)`) |

**Garantias de demo** (checar após gerar; ajustar pesos se falhar):
- Fila de aprovação com ≥ 5 itens `Pendente Aprovação`.
- Toda dimensão usada em filtro `select` tem ≥ 4 valores distintos.
- Fato principal cobre todos os meses do `period_months` (nenhum mês vazio no gráfico de evolução).
- Top-N do gráfico de ranking tem N itens distintos.

## Spec — estrutura de `docs/mock_spec.yaml`

```yaml
seed: 42
period_months: 24            # de .build/project.json → demo.period_months
seed_cap: 2000               # linhas por tabela no seed.sql (CSV sempre completo)
entities:
  - name: produto            # = nome do arquivo em mock_data/
    table: produto           # = tabela (data_model.yaml)
    role: dimensao
    volume: 1200
    fixed_rows: []           # linhas garantidas (usuarios: credenciais de demo)
    fields:
      - {name: id, type: int, gen: sequence}
      - {name: familia, type: varchar(40), gen: "enum(Baterias:18%, Filtros:16%, ...)"}
      - {name: codigo, type: varchar(20), gen: "codigo(familia:3)"}
      - {name: nome, type: varchar(150), gen: "lista(BR:produtos:autopecas)"}
      - {name: fornecedor_id, type: int, gen: "fk(fornecedor, pareto)"}
      - {name: custo, type: decimal(15,2), gen: "pareto(15, 1800)"}
      - {name: preco_atual, type: decimal(15,2), gen: "derivado(custo * normal(1.38, 0.06))"}
      - {name: created_at, type: datetime2, gen: audit}
      - {name: updated_at, type: datetime2, gen: audit}
```

A referência completa de geradores está no docstring de `mock_generator.py`.

## Saída

```
mock_data/<entidade>.csv + .json   (todas as linhas)
database/seed.sql                  (gerado aqui — Step 5 apenas valida/ajusta)
docs/mock_spec.yaml, scripts/mock_generator.py, scripts/generate_mock.py
```

## Restrições

- O LLM **não escreve linhas de dados** — só o spec e o script. Exceção: `fixed_rows` (≤ 10 linhas, ex.: credenciais).
- Não usar dados sensíveis reais (CNPJ/e-mails são sintéticos por construção).
- Não alterar `mock_generator.py` no projeto — se faltar um gerador, registrar aviso sugerindo evolução do template.
- Contexto máximo: 8.000 tokens de saída para o spec; dividir por blocos de entidades se necessário.

## Pós-processamento

1. `python scripts/mock_generator.py docs/mock_spec.yaml --validate` → deve imprimir `[ok] mock_data valido`.
2. `/skill00-validator step4` (checa no disco 2 arquivos por entidade + volume + FKs).
3. Checkpoint `.build/checkpoints/step4.json` com contagens por entidade.

## Argumento opcional (entidade específica)

$ARGUMENTS — regenerar apenas a entidade indicada (o script aceita `--only <entidade>` quando implementado; senão, regenerar tudo — é reprodutível pelo seed).
