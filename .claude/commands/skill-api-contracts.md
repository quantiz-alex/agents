# Skill — API Contracts Generator

Leia `docs/requirements.yaml` e `docs/data_model.yaml` para gerar `docs/api_contracts.yaml` com os contratos completos de todos os endpoints REST antes da geração do backend.

## Quando Usar

- Após a Etapa 2 (Data Model) e antes da Etapa 9 (Backend FastAPI)
- Para documentar contratos de API que serão usados por `skill11-fastapi.md`
- Como referência de integração entre frontend (queries) e backend (endpoints)

## Argumento opcional

`$ARGUMENTS` — entidade específica (ex.: `clientes`). Se vazio, gera contratos para todas as entidades.

---

## Instruções

1. Leia `docs/requirements.yaml` para obter módulos e regras de negócio.
2. Leia `docs/data_model.yaml` para obter entidades, campos, tipos e relacionamentos.
3. Gere `docs/api_contracts.yaml` com contratos completos para cada entidade.
4. Se o arquivo já existir, aplique patch incremental para entidades novas/alteradas.
5. **Se `docs/business_logic.yaml` já existir** (gerado no Step 2.7 — pode não existir ainda na primeira passada, já que a ordem padrão do pipeline é 2.6 antes de 2.7; nesse caso, esta skill roda de novo em modo patch incremental após o Step 2.7 completar): para cada entidade com regra `logic_type: interactive_formula` vinculada, adicionar o contrato `POST /<entidade>/simular` (ver estrutura abaixo); para cada regra `logic_type: validation` com `severity: block`, documentar `422` em `POST`/`PUT` com o `error_message` literal da regra.

---

## Estrutura de Saída

```yaml
# docs/api_contracts.yaml

meta:
  version: "1.0.0"
  base_url: "/api/v1"
  auth_required: true          # todos os endpoints protegidos por JWT (exceto /auth)
  content_type: "application/json"

endpoints:
  auth:
    POST /auth/login:
      description: "Autenticação — retorna access token JWT"
      auth_required: false
      request:
        body:
          email: {type: string, format: email, required: true}
          password: {type: string, min_length: 6, required: true}
      response:
        200:
          access_token: {type: string}
          token_type:   {type: string, example: "bearer"}
          expires_in:   {type: integer, example: 28800}
        401:
          detail: "Credenciais inválidas"

    POST /auth/refresh:
      description: "Renova o access token"
      auth_required: true
      response:
        200:
          access_token: {type: string}
        401:
          detail: "Token expirado ou inválido"

  <entidade>:
    GET /<entidade>:
      description: "Lista todos os registros com paginação e filtros opcionais"
      auth_required: true
      query_params:
        skip:    {type: integer, default: 0}
        limit:   {type: integer, default: 100, max: 1000}
        # campos filtráveis conforme data_model.yaml
      response:
        200:
          type: array
          items: <Entidade>Response
        401: "Não autenticado"
        403: "Sem permissão"

    GET /<entidade>/{id}:
      description: "Retorna um registro pelo ID"
      auth_required: true
      path_params:
        id: {type: integer, required: true}
      response:
        200: <Entidade>Response
        404: "Registro não encontrado"

    POST /<entidade>:
      description: "Cria um novo registro"
      auth_required: true
      request:
        body: <Entidade>Create
      response:
        201: <Entidade>Response
        422: "Dados inválidos (detalhes dos campos com erro) — inclui error_message de regras logic_type:validation vinculadas, se houver"

    PUT /<entidade>/{id}:
      description: "Atualiza um registro existente"
      auth_required: true
      path_params:
        id: {type: integer, required: true}
      request:
        body: <Entidade>Update
      response:
        200: <Entidade>Response
        404: "Registro não encontrado"
        422: "Dados inválidos"

    DELETE /<entidade>/{id}:
      description: "Soft delete — marca como inativo (ativo=false)"
      auth_required: true
      path_params:
        id: {type: integer, required: true}
      response:
        204: "Deletado com sucesso"
        404: "Registro não encontrado"

    # Presente SOMENTE se houver regra logic_type:interactive_formula vinculada em business_logic.yaml
    POST /<entidade>/simular:
      description: "Calcula o cenário de simulação sem persistir — request body = formula.variables[interactive=true]"
      auth_required: true
      request:
        body: SimulacaoRequest   # campos 1:1 com formula.variables[] da regra vinculada
      response:
        200: SimulacaoResponse   # kpis/comparativo/resumo = formula.output_fields[]
        422: "Parâmetros de simulação inválidos"

schemas:
  <Entidade>Base:
    # campos editáveis (excluir id, created_at, updated_at, ativo)
    campo1: {type: string, max_length: 255, required: true}
    campo2: {type: integer, required: false}

  <Entidade>Create:
    extends: <Entidade>Base
    # campos obrigatórios na criação

  <Entidade>Update:
    extends: <Entidade>Base
    # todos os campos opcionais (partial update)

  <Entidade>Response:
    extends: <Entidade>Base
    id:         {type: integer}
    ativo:      {type: boolean}
    created_at: {type: string, format: datetime}
    updated_at: {type: string, format: datetime}

error_responses:
  400:
    detail: string     # mensagem de erro
  401:
    detail: "Não autenticado — forneça um Bearer token válido"
  403:
    detail: "Sem permissão para esta operação"
  404:
    detail: "Registro não encontrado"
  422:
    detail: array      # lista de erros de validação Pydantic
  500:
    detail: "Erro interno do servidor"

pagination:
  strategy: offset_limit
  default_limit: 100
  max_limit: 1000
  response_headers:
    X-Total-Count: integer
    X-Page-Size:   integer

versioning:
  strategy: url_prefix    # /api/v1/
  current: "v1"
```

---

## Regras de Geração

- Toda entidade com campo `ativo` usa **soft delete** — o `DELETE` não remove o registro, apenas seta `ativo=false`.
- Entidades com FK (relacionamentos) incluem os campos de FK em `<Entidade>Create` como obrigatórios.
- Campos `created_at` e `updated_at` aparecem apenas em `<Entidade>Response` — nunca em Create/Update.
- Filtros de query disponíveis em `GET /` correspondem aos campos indexados no `data_model.yaml`.
- O endpoint `/auth/login` e `/auth/refresh` são os únicos com `auth_required: false`.

## Restrições

- NÃO gere código Python — apenas o YAML de contratos.
- Contexto máximo: **8.000 tokens** de saída.
- Se exceder, dividir em múltiplos arquivos por módulo: `docs/api_contracts_<modulo>.yaml`.

## Pós-processamento

1. Verificar que toda entidade do `data_model.yaml` tem contrato gerado
2. Verificar que schemas de request/response são consistentes com os campos do data model
3. Criar checkpoint `step_api_contracts.json`
4. Registrar em `.build/build.log`

## Modo de Uso

```
/skill-api-contracts
/skill-api-contracts clientes
```
