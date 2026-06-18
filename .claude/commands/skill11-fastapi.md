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

## Restrições

- Endpoints mínimos: GET (lista), GET (por ID), POST, PUT, DELETE.
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
