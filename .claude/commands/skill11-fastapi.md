# Skill 11 — FastAPI Generation Skill

Leia `docs/data_model.yaml` e `docs/api_contracts.yaml` para gerar o backend FastAPI.

## Argumento obrigatório

Nome da entidade: $ARGUMENTS

Exemplo de uso: `/skill11-fastapi clientes`

## Pré-requisitos

Antes de gerar qualquer arquivo, verificar que existem:
- `backend/config.py` — gerado pela Etapa 2.5 (`/skill-env`)
- `backend/database.py` — gerado pela Etapa 2.5 (`/skill-env`)

Se não existirem → **PARAR** e executar `/skill-env` primeiro.

## Instruções

1. Leia `docs/data_model.yaml` — extraia a entidade solicitada.
2. Leia `docs/api_contracts.yaml` se existir — extraia os contratos e schemas da entidade.
3. Gere os arquivos abaixo para a entidade solicitada.
4. Se os arquivos já existirem, aplique patch incremental.

## Arquivos Gerados

```
backend/
├── models/<entidade>.py       ← SQLAlchemy model
├── schemas/<entidade>.py      ← Pydantic schemas
├── repositories/<entidade>.py ← lógica de acesso a dados
├── api/routes/<entidade>.py   ← endpoints FastAPI
└── services/<entidade>.py     ← regras de negócio
```

### `models/<entidade>.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, func
from backend.database import Base

class <Entidade>(Base):
    __tablename__ = "<table>"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # campos conforme data_model.yaml
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### `schemas/<entidade>.py`

```python
from pydantic import BaseModel
from datetime import datetime

class <Entidade>Base(BaseModel):
    # campos editáveis

class <Entidade>Create(<Entidade>Base):
    pass

class <Entidade>Update(<Entidade>Base):
    pass

class <Entidade>Response(<Entidade>Base):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### `repositories/<entidade>.py`

```python
from sqlalchemy.orm import Session
from backend.models.<entidade> import <Entidade>
from backend.schemas.<entidade> import <Entidade>Create, <Entidade>Update

class <Entidade>Repository:
    def get_all(self, db: Session) -> list[<Entidade>]: ...
    def get_by_id(self, db: Session, id: int) -> <Entidade> | None: ...
    def create(self, db: Session, data: <Entidade>Create) -> <Entidade>: ...
    def update(self, db: Session, id: int, data: <Entidade>Update) -> <Entidade> | None: ...
    def delete(self, db: Session, id: int) -> bool: ...
```

### `api/routes/<entidade>.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.<entidade> import <Entidade>Create, <Entidade>Update, <Entidade>Response
from backend.services.<entidade> import <Entidade>Service

# get_current_user é adicionado pela Etapa 9.5 (/skill-auth)
# Após rodar /skill-auth, cada endpoint receberá: current_user = Depends(get_current_user)
router = APIRouter(prefix="/<entidade>s", tags=["<entidade>s"])
service = <Entidade>Service()

@router.get("/", response_model=list[<Entidade>Response])
def get_all(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[<Entidade>Response]:
    return service.get_all(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=<Entidade>Response)
def get_by_id(id: int, db: Session = Depends(get_db)) -> <Entidade>Response:
    item = service.get_by_id(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return item

@router.post("/", response_model=<Entidade>Response, status_code=status.HTTP_201_CREATED)
def create(data: <Entidade>Create, db: Session = Depends(get_db)) -> <Entidade>Response:
    return service.create(db, data)

@router.put("/{id}", response_model=<Entidade>Response)
def update(id: int, data: <Entidade>Update, db: Session = Depends(get_db)) -> <Entidade>Response:
    item = service.update(db, id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return item

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int, db: Session = Depends(get_db)) -> None:
    if not service.delete(db, id):
        raise HTTPException(status_code=404, detail="Registro não encontrado")
```

### `backend/main.py` (gerado após todas as entidades)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_settings
from backend.database import create_tables, health_check
from backend.api.routes import auth, <entity1>, <entity2>  # listar todas

settings = get_settings()

app = FastAPI(
    title=f"{settings.app_name if hasattr(settings, 'app_name') else 'API'}",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(<entity1>.router, prefix="/api/v1")
app.include_router(<entity2>.router, prefix="/api/v1")


@app.on_event("startup")
async def startup() -> None:
    create_tables()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "db": health_check()}
```

## Endpoints especializados — Simulação, Validação e Aprovação

Além do CRUD básico, verificar em `docs/api_contracts.yaml`, `docs/requirements.yaml` e **`docs/business_logic.yaml`** se a entidade requer:
- `has_simulation: true` (ou ≥1 regra `logic_type: interactive_formula` vinculada) → gerar bloco de simulação
- ≥1 regra `logic_type: validation` vinculada → gerar bloco de validação
- `has_approval_flow: true` → gerar bloco de aprovação

### Bloco de Simulação

Quando houver uma regra `logic_type: interactive_formula` vinculada à entidade, adicionar ao `schemas/<entidade>.py`. **Os campos de `SimulacaoRequest` NÃO são fixos** — `margem_desejada`/`desconto_maximo` abaixo é só a FORMA do modelo Pydantic; os campos reais são gerados 1:1 a partir de `formula.variables[]` onde `interactive: true` (mesmo nome, mesmo `min`/`max` da regra em `business_logic.yaml`) — a MESMA fórmula e os MESMOS parâmetros que `skill-simulation.md` usa no frontend (paridade front/back):

```python
from pydantic import BaseModel, Field
from typing import Any

class SimulacaoRequest(BaseModel):
    """Parâmetros de entrada do cenário de simulação — um campo por formula.variables[interactive=true]."""
    margem_desejada:  float | None = Field(None, ge=0, le=100, description="Margem desejada em %")
    desconto_maximo:  float | None = Field(None, ge=0, le=100, description="Desconto máximo em %")
    # demais parâmetros conforme business_logic.yaml (fallback acima apenas se business_logic.yaml não existir)

class SimulacaoKpi(BaseModel):
    label: str
    valor: str

class SimulacaoResponse(BaseModel):
    """Resultado do cálculo de simulação — sem persistência."""
    kpis:        list[SimulacaoKpi]
    comparativo: list[dict[str, Any]]
    resumo:      dict[str, float]
```

Adicionar ao `services/<entidade>.py`:

```python
def simular(
    self,
    db: Session,
    params: SimulacaoRequest,
) -> SimulacaoResponse:
    """
    Executa o cálculo do cenário sem persistir.
    Implementa formula.expression da regra logic_type:interactive_formula
    vinculada em docs/business_logic.yaml — a mesma fórmula do frontend.
    """
    registros = self.repo.get_all(db, skip=0, limit=10000)

    # --- Lógica de cálculo (substituir pela formula.expression real de business_logic.yaml) ---
    comparativo = []
    receita_atual = receita_simulada = 0.0

    for item in registros:
        preco_sim = item.preco_atual
        if params.margem_desejada is not None:
            preco_sim = item.custo / (1 - params.margem_desejada / 100)
        if params.desconto_maximo is not None:
            preco_sim *= (1 - params.desconto_maximo / 100)

        var_pct = ((preco_sim - item.preco_atual) / item.preco_atual * 100) if item.preco_atual else 0
        receita_atual    += item.preco_atual * getattr(item, "volume", 1)
        receita_simulada += preco_sim        * getattr(item, "volume", 1)

        comparativo.append({
            "id":             item.id,
            "produto":        getattr(item, "nome", str(item.id)),
            "preco_atual":    round(item.preco_atual, 2),
            "preco_simulado": round(preco_sim, 2),
            "variacao_pct":   round(var_pct, 2),
        })

    variacao_total = ((receita_simulada / receita_atual) - 1) * 100 if receita_atual else 0

    return SimulacaoResponse(
        kpis=[
            SimulacaoKpi(label="Receita Atual",    valor=f"R$ {receita_atual:,.2f}"),
            SimulacaoKpi(label="Receita Simulada", valor=f"R$ {receita_simulada:,.2f}"),
            SimulacaoKpi(label="Variação Total",   valor=f"{variacao_total:+.1f}%"),
            SimulacaoKpi(label="Itens Afetados",   valor=str(len(comparativo))),
        ],
        comparativo=comparativo,
        resumo={
            "receita_atual":    round(receita_atual, 2),
            "receita_simulada": round(receita_simulada, 2),
            "variacao_pct":     round(variacao_total, 2),
        },
    )
```

Adicionar ao `api/routes/<entidade>.py`:

```python
@router.post("/simular", response_model=SimulacaoResponse)
def simular_cenario(
    params: SimulacaoRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> SimulacaoResponse:
    """Calcula o resultado do cenário sem persistir. Disponível para analista+."""
    return service.simular(db, params)
```

---

### Bloco de Validação de Regra de Negócio

Para cada regra `logic_type: validation` em `docs/business_logic.yaml` vinculada à entidade, adicionar ao `schemas/<entidade>.py` (em `<Entidade>Create`/`<Entidade>Update`) um validador Pydantic v2 implementando `validation.condition` literalmente:

```python
from pydantic import BaseModel, field_validator, model_validator

class ProdutoCreate(BaseModel):
    preco: float
    custo: float
    # ... demais campos

    @model_validator(mode="after")
    def validar_preco_minimo(self) -> "ProdutoCreate":
        """RN-XXX: <validation.error_message literal de business_logic.yaml>."""
        # condição = validation.condition da regra (ex.: preco >= custo * (1 + margem_minima))
        if self.preco < self.custo * 1.10:
            raise ValueError("<validation.error_message>")
        return self
```

- `severity: block` → `raise ValueError(...)` (o FastAPI converte automaticamente em `422 Unprocessable Entity` na resposta do `POST`/`PUT`).
- `severity: warn` → NÃO levantar erro; em vez disso, o `service.criar`/`service.atualizar` calcula a condição e retorna um `avisos: list[str]` adicional na resposta (não bloqueia a escrita).
- Nunca reescrever a mensagem — usar `validation.error_message` literal do roadmap, para o erro exibido ao usuário final ser exatamente o que o cliente definiu como regra de negócio.

---

### Bloco de Aprovação

Quando `has_approval_flow: true`, adicionar ao `schemas/<entidade>.py`:

```python
from enum import Enum

class StatusAprovacaoEnum(str, Enum):
    rascunho            = "Rascunho"
    pendente_aprovacao  = "Pendente Aprovação"
    aprovado            = "Aprovado"
    rejeitado           = "Rejeitado"

class EnviarAprovacaoRequest(BaseModel):
    pass   # sem campos adicionais; o id vem na URL

class AprovarRequest(BaseModel):
    comentario: str | None = Field(None, max_length=1000)

class RejeitarRequest(BaseModel):
    comentario: str = Field(..., min_length=5, max_length=1000,
                             description="Motivo da rejeição — obrigatório")
```

Adicionar ao `services/<entidade>.py`:

```python
from datetime import datetime, timezone

def enviar_para_aprovacao(self, db: Session, id: int, solicitante: str) -> <Entidade>:
    item = self.repo.get_by_id(db, id)
    if not item:
        raise HTTPException(404, "Registro não encontrado")
    if item.status not in (StatusAprovacaoEnum.rascunho, StatusAprovacaoEnum.rejeitado):
        raise HTTPException(409, f"Registro com status '{item.status}' não pode ser enviado para aprovação")
    return self.repo.update(db, id, {"status": StatusAprovacaoEnum.pendente_aprovacao})


def aprovar(self, db: Session, id: int, aprovador: str, comentario: str | None) -> <Entidade>:
    item = self.repo.get_by_id(db, id)
    if not item:
        raise HTTPException(404, "Registro não encontrado")
    if item.status != StatusAprovacaoEnum.pendente_aprovacao:
        raise HTTPException(409, "Apenas registros com status 'Pendente Aprovação' podem ser aprovados")
    return self.repo.update(db, id, {
        "status":               StatusAprovacaoEnum.aprovado,
        "aprovado_por":         aprovador,
        "aprovado_em":          datetime.now(timezone.utc),
        "comentario_aprovacao": comentario,
    })


def rejeitar(self, db: Session, id: int, aprovador: str, comentario: str) -> <Entidade>:
    item = self.repo.get_by_id(db, id)
    if not item:
        raise HTTPException(404, "Registro não encontrado")
    if item.status != StatusAprovacaoEnum.pendente_aprovacao:
        raise HTTPException(409, "Apenas registros com status 'Pendente Aprovação' podem ser rejeitados")
    return self.repo.update(db, id, {
        "status":               StatusAprovacaoEnum.rejeitado,
        "aprovado_por":         aprovador,
        "aprovado_em":          datetime.now(timezone.utc),
        "comentario_aprovacao": comentario,
    })
```

Adicionar ao `api/routes/<entidade>.py`:

```python
from backend.auth import get_current_user

@router.post("/{id}/enviar-aprovacao", response_model=<Entidade>Response)
def enviar_para_aprovacao(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> <Entidade>Response:
    """Envia para aprovação. Disponível para role analista."""
    if current_user.role not in ("analista", "supervisor", "admin"):
        raise HTTPException(403, "Permissão insuficiente")
    return service.enviar_para_aprovacao(db, id, solicitante=current_user.nome)


@router.post("/{id}/aprovar", response_model=<Entidade>Response)
def aprovar(
    id: int,
    body: AprovarRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> <Entidade>Response:
    """Aprova o registro. Apenas supervisor e admin."""
    if current_user.role not in ("supervisor", "admin"):
        raise HTTPException(403, "Apenas supervisores e administradores podem aprovar")
    return service.aprovar(db, id, aprovador=current_user.nome, comentario=body.comentario)


@router.post("/{id}/rejeitar", response_model=<Entidade>Response)
def rejeitar(
    id: int,
    body: RejeitarRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> <Entidade>Response:
    """Rejeita o registro com comentário obrigatório. Apenas supervisor e admin."""
    if current_user.role not in ("supervisor", "admin"):
        raise HTTPException(403, "Apenas supervisores e administradores podem rejeitar")
    return service.rejeitar(db, id, aprovador=current_user.nome, comentario=body.comentario)
```

---

## Bloco de Analytics — KPIs e gráficos por tela (v4)

**Quando:** para cada `pages.<pagina>` em `docs/screens_definition.yaml` com `screen_type ∈ {dashboard, analytics, report, master_detail}` ou com `kpis[]`/`charts[]` não vazios. Gera **um módulo de agregação por tela**, espelhando as funções de `frontend/pages/<pagina>/<pagina>_queries.py` (mesmos nomes, mesmas fórmulas de `business_logic.yaml`) — é o que permite ao frontend trocar CSV por API com `USE_API=true` sem mudar nenhuma tela.

**Arquivos:**
- `backend/services/analytics_<pagina>.py`
- `backend/api/routes/analytics_<pagina>.py` → `APIRouter(prefix="/analytics/<pagina>", tags=["Analytics · <Título>"])`

**Padrão do service** (pandas sobre SQLAlchemy — mesma lógica vetorizada do frontend):

```python
"""analytics_<pagina>.py — agregações da tela <Título> (paridade com frontend/pages/<pagina>/<pagina>_queries.py)."""
from __future__ import annotations
from datetime import date
import pandas as pd
from sqlalchemy.orm import Session
from backend.models.<fato> import <Fato>
from backend.models.<dimensao> import <Dimensao>

def _base(db: Session, inicio: date | None, fim: date | None, **filtros: str | None) -> pd.DataFrame:
    q = db.query(<Fato>, <Dimensao>.nome.label("<dimensao>")).join(<Dimensao>, <Fato>.<dimensao>_id == <Dimensao>.id)
    if inicio: q = q.filter(<Fato>.data >= inicio)
    if fim:    q = q.filter(<Fato>.data <= fim)
    for campo, valor in filtros.items():
        if valor: q = q.filter(getattr(<Fato>, campo) == valor)
    df = pd.read_sql(q.statement, db.bind)
    # campos derivados — MESMA expressão de business_logic.yaml usada no frontend
    df["margem_pct"] = (df["receita"] - df["custo_total"]) / df["receita"] * 100
    return df

def kpis(db: Session, inicio, fim, **filtros) -> dict:            # 1:1 com pages.<pagina>.kpis[]
    df = _base(db, inicio, fim, **filtros)
    ant = _base(db, <inicio - delta>, <fim - delta>, **filtros)     # baseline p/ kind: comparação
    return {"receita": {"valor": float(df.receita.sum()), "anterior": float(ant.receita.sum())}, ...}

def chart_<id>(db: Session, inicio, fim, **filtros) -> list[dict]:  # 1:1 com pages.<pagina>.charts[]
    df = _base(db, inicio, fim, **filtros)
    return df.groupby("<x_field>", as_index=False)["<y_field>"].sum().sort_values("<y_field>", ascending=False).head(<top_n>).to_dict("records")

def grid(db: Session, inicio, fim, skip: int = 0, limit: int = 500, **filtros) -> list[dict]:
    df = _base(db, inicio, fim, **filtros)
    return df.iloc[skip: skip + limit].to_dict("records")
```

**Padrão das rotas:**

```python
router = APIRouter(prefix="/analytics/<pagina>", tags=["Analytics · <Título>"])

@router.get("/kpis")
def get_kpis(inicio: date | None = None, fim: date | None = None, <filtro>: str | None = None,
             db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    return service.kpis(db, inicio, fim, <filtro>=<filtro>)

@router.get("/charts/<id>")
def get_chart_<id>(...) -> list[dict]: ...      # um por charts[]

@router.get("/grid")
def get_grid(...) -> list[dict]: ...
```

Regras: filtros dos endpoints = `pages.<pagina>.filters[]` (+ `drilldowns[].target_field` como query param opcional); nomes de campos retornados = os mesmos que o CSV/`_queries.py` produz (o frontend faz `pd.DataFrame(api_get(...))` e segue igual); incluir os routers em `main.py`; validar `python -c "import backend.services.analytics_<pagina>"`.

---

## Restrições

- Endpoints mínimos: GET (lista), GET (por ID), POST, PUT, DELETE.
- Endpoints de analytics (`/analytics/<pagina>/kpis|charts/<id>|grid`): obrigatórios para toda tela com `kpis[]`/`charts[]` em `screens_definition.yaml`.
- Endpoints de simulação e aprovação: apenas quando sinalizados em `api_contracts.yaml` ou `requirements.yaml`.
- `simular` nunca persiste — apenas calcula e retorna.
- Aprovação exige role check explícito no route — não delegar somente ao JWT.
- `RejeitarRequest.comentario` é obrigatório (validação Pydantic via `Field(...)`).
- Tipagem Python obrigatória em todos os parâmetros e retornos.
- Tratamento de erro com `HTTPException` e status codes corretos.
- Separação obrigatória: route → service → repository.
- Rotas com prefixo `/api/v1/<entidade>s` (plural).
- `backend/database.py` e `backend/config.py` devem existir antes desta skill.
- Contexto máximo: **8.000 tokens** de saída por arquivo.
- Se exceder 8.000 tokens, dividir em chunks com continuação automática.

## Pós-processamento

1. Executar `/skill00-validator step9 --entity <entity>` automaticamente
2. Verificar que todos os arquivos Python são válidos (parse)
3. Verificar que tipagem está presente
4. Se validação falhar → reportar erros e sugestões
5. Se validação passar → criar checkpoint parcial e avançar
