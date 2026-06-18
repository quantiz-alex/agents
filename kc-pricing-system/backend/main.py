from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import create_tables
from backend.api.routes import (
    auth,
    usuarios,
    produtos,
    parametros_tributarios,
    margens_cadeia,
    importacoes_base,
    listas_preco,
    listas_preco_itens,
    cenarios_simulacao,
    cenarios_simulacao_itens,
)

app = FastAPI(
    title="KC Pricing System API",
    version="0.1.0",
    description="API de gestão de preços e simulação tributária — KC Pricing System",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth router
app.include_router(auth.router, prefix="/api/v1")

# Entity routers
app.include_router(usuarios.router, prefix="/api/v1")
app.include_router(produtos.router, prefix="/api/v1")
app.include_router(parametros_tributarios.router, prefix="/api/v1")
app.include_router(margens_cadeia.router, prefix="/api/v1")
app.include_router(importacoes_base.router, prefix="/api/v1")
app.include_router(listas_preco.router, prefix="/api/v1")
app.include_router(listas_preco_itens.router, prefix="/api/v1")
app.include_router(cenarios_simulacao.router, prefix="/api/v1")
app.include_router(cenarios_simulacao_itens.router, prefix="/api/v1")


@app.on_event("startup")
def on_startup() -> None:
    create_tables()


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "ok", "service": "KC Pricing System API"}
