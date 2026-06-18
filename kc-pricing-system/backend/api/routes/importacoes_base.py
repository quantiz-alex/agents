from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.schemas.importacoes_base import ImportacaoBaseCreate, ImportacaoBaseResponse, ImportacaoBaseUpdate
from backend.services import importacoes_base as service

router = APIRouter(prefix="/importacoes-base", tags=["ImportacoesBase"])


@router.get("/", response_model=list[ImportacaoBaseResponse])
def listar_importacoes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ImportacaoBaseResponse]:
    return service.listar(db, skip=skip, limit=limit)


@router.get("/{importacao_id}", response_model=ImportacaoBaseResponse)
def obter_importacao(
    importacao_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ImportacaoBaseResponse:
    return service.obter(db, importacao_id)


@router.post("/", response_model=ImportacaoBaseResponse, status_code=status.HTTP_201_CREATED)
def criar_importacao(
    data: ImportacaoBaseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ImportacaoBaseResponse:
    return service.criar(db, data)


@router.put("/{importacao_id}", response_model=ImportacaoBaseResponse)
def atualizar_importacao(
    importacao_id: int,
    data: ImportacaoBaseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ImportacaoBaseResponse:
    return service.atualizar(db, importacao_id, data)


@router.delete("/{importacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_importacao(
    importacao_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> None:
    service.deletar(db, importacao_id)
