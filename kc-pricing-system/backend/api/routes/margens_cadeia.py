from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.schemas.margens_cadeia import MargemCadeiaCreate, MargemCadeiaResponse, MargemCadeiaUpdate
from backend.services import margens_cadeia as service

router = APIRouter(prefix="/margens-cadeia", tags=["MargensCadeia"])


@router.get("/", response_model=list[MargemCadeiaResponse])
def listar_margens(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[MargemCadeiaResponse]:
    return service.listar(db, skip=skip, limit=limit)


@router.get("/{margem_id}", response_model=MargemCadeiaResponse)
def obter_margem(
    margem_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> MargemCadeiaResponse:
    return service.obter(db, margem_id)


@router.post("/", response_model=MargemCadeiaResponse, status_code=status.HTTP_201_CREATED)
def criar_margem(
    data: MargemCadeiaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> MargemCadeiaResponse:
    return service.criar(db, data)


@router.put("/{margem_id}", response_model=MargemCadeiaResponse)
def atualizar_margem(
    margem_id: int,
    data: MargemCadeiaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> MargemCadeiaResponse:
    return service.atualizar(db, margem_id, data)


@router.delete("/{margem_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_margem(
    margem_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> None:
    service.deletar(db, margem_id)
