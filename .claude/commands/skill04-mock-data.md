# Skill 04 — Mock Data Generation Skill

Leia `docs/data_model.yaml` e gere dados fictícios realistas para todas as entidades.

## Instruções

1. Leia `docs/data_model.yaml` (e `docs/business_logic.yaml`, se existir).
2. Extraia todas as entidades que possuem `table:` (ignorar enums).
3. **ANTES de gerar qualquer dado**, monte e exiba um checklist das entidades:
   ```
   Entidades a gerar (N total):
   [ ] entidade1  →  mock_data/entidade1.csv  +  mock_data/entidade1.json
   [ ] entidade2  →  mock_data/entidade2.csv  +  mock_data/entidade2.json
   ...
   ```
4. Verifique quais entidades JÁ possuem AMBOS os arquivos no disco — marque `[x]` e pule-as.
5. Para cada entidade `[ ]`, na sequência do checklist:
   a. Gere os dados (entre 10 e 50 registros realistas)
   b. Escreva o CSV → confirme gravação
   c. Escreva o JSON → confirme gravação
   d. Marque `[x]` e exiba: `✓ entidade → CSV (N linhas) + JSON (N registros)`
   e. Só avance para a próxima entidade após os dois arquivos estarem gravados
6. Ao concluir, exiba o checklist completo com todos os `[x]`.

## Estrutura de Saída

```
mock_data/
├── <entidade>.csv
├── <entidade>.json
├── ...
```

## Regras de Geração

- IDs: inteiros sequenciais iniciando em 1.
- Textos: português brasileiro, realistas para o domínio do negócio.
- Datas: formato ISO 8601 (`YYYY-MM-DD` ou `YYYY-MM-DDTHH:MM:SS`).
- Decimais: usar ponto como separador decimal nos arquivos.
- Campos de FK: usar IDs que existam na entidade referenciada.
- Campos booleanos: `true`/`false` (JSON) e `1`/`0` (CSV).
- Enums: usar apenas valores definidos em `enums` do data_model.yaml.
- **NUNCA gere no mock um campo marcado `logic_type: derived_field` em `docs/business_logic.yaml`** (ex.: `margem`, `preco_novo`, qualquer `output_field` de uma regra `derived_field`/`interactive_formula` com `persist: false`). Gerar esse valor pronto no CSV/JSON esconderia a ausência do cálculo real no frontend/backend — o campo deve ser SEMPRE calculado em runtime (pandas em `_queries.py`, serviço em `services/<entidade>.py`), nunca lido de um dado pré-computado. Se a entidade tiver esses campos listados em `data_model.yaml`, omita-os do mock e registre um aviso: "campo <nome> é derivado — não incluído no mock, calculado em runtime".

## Formato CSV

```
id,campo1,campo2,...
1,valor1,valor2,...
```

## Formato JSON

```json
[
  {"id": 1, "campo1": "valor1", "campo2": "valor2"},
  ...
]
```

## Restrições

- NÃO gere código Python — apenas os arquivos de dados.
- NÃO use dados sensíveis reais (CPF, CNPJ, e-mails reais).
- Use dados fictícios mas plausíveis.
- **Campos de texto que contenham vírgula DEVEM ser envolvidos em aspas duplas no CSV.**
- Contexto máximo: **8.000 tokens** de saída por entidade.
- Se uma entidade exceder 8.000 tokens, divida em chunks gerando parte dos registros por vez, mas finalize AMBOS os arquivos antes de avançar.

## Pós-processamento

1. Após gerar todas as entidades, executar `/skill00-validator step4`
2. O validator verifica no **disco** (não na memória) se cada entidade tem ambos os arquivos
3. Se validação falhar → identificar a entidade/arquivo faltante, regerar apenas ela
4. Se validação passar → criar checkpoint listando csv+json por entidade e avançar

## Argumento opcional (entidade específica)

$ARGUMENTS
