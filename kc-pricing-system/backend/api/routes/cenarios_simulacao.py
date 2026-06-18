from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.schemas.cenarios_simulacao import (
    CenarioSimulacaoCreate,
    CenarioSimulacaoResponse,
    CenarioSimulacaoUpdate,
)
from backend.services import cenarios_simulacao as service

router = APIRouter(prefix="/cenarios-simulacao", tags=["CenariosSimulacao"])


@router.get("/", response_model=list[CenarioSimulacaoResponse])
def listar_cenarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[CenarioSimulacaoResponse]:
    return service.listar(db, skip=skip, limit=limit)


@router.get("/{cenario_id}", response_model=CenarioSimulacaoResponse)
def obter_cenario(
    cenario_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> CenarioSimulacaoResponse:
    return service.obter(db, cenario_id)


@router.post("/", response_model=CenarioSimulacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_cenario(
    data: CenarioSimulacaoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> CenarioSimulacaoResponse:
    return service.criar(db, data)


@router.put("/{cenario_id}", response_model=CenarioSimulacaoResponse)
def atualizar_cenario(
    cenario_id: int,
    data: CenarioSimulacaoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> CenarioSimulacaoResponse:
    return service.atualizar(db, cenario_id, data)


@router.delete("/{cenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cenario(
    cenario_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> None:
    service.deletar(db, cenario_id)
