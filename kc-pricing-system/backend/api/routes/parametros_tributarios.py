from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.schemas.parametros_tributarios import (
    ParametroTributarioCreate,
    ParametroTributarioResponse,
    ParametroTributarioUpdate,
)
from backend.services import parametros_tributarios as service

router = APIRouter(prefix="/parametros-tributarios", tags=["ParametrosTributarios"])


@router.get("/", response_model=list[ParametroTributarioResponse])
def listar_parametros(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ParametroTributarioResponse]:
    return service.listar(db, skip=skip, limit=limit)


@router.get("/{parametro_id}", response_model=ParametroTributarioResponse)
def obter_parametro(
    parametro_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ParametroTributarioResponse:
    return service.obter(db, parametro_id)


@router.post("/", response_model=ParametroTributarioResponse, status_code=status.HTTP_201_CREATED)
def criar_parametro(
    data: ParametroTributarioCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ParametroTributarioResponse:
    return service.criar(db, data)


@router.put("/{parametro_id}", response_model=ParametroTributarioResponse)
def atualizar_parametro(
    parametro_id: int,
    data: ParametroTributarioUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ParametroTributarioResponse:
    return service.atualizar(db, parametro_id, data)


@router.delete("/{parametro_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_parametro(
    parametro_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> None:
    service.deletar(db, parametro_id)
