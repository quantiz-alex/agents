from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.schemas.cenarios_simulacao_itens import (
    CenarioSimulacaoItemCreate,
    CenarioSimulacaoItemResponse,
    CenarioSimulacaoItemUpdate,
)
from backend.services import cenarios_simulacao_itens as service

router = APIRouter(prefix="/cenarios-simulacao-itens", tags=["CenariosSimulacaoItens"])


@router.get("/", response_model=list[CenarioSimulacaoItemResponse])
def listar_itens(
    skip: int = 0,
    limit: int = 500,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[CenarioSimulacaoItemResponse]:
    return service.listar(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=CenarioSimulacaoItemResponse)
def obter_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> CenarioSimulacaoItemResponse:
    return service.obter(db, item_id)


@router.post("/", response_model=CenarioSimulacaoItemResponse, status_code=status.HTTP_201_CREATED)
def criar_item(
    data: CenarioSimulacaoItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> CenarioSimulacaoItemResponse:
    return service.criar(db, data)


@router.put("/{item_id}", response_model=CenarioSimulacaoItemResponse)
def atualizar_item(
    item_id: int,
    data: CenarioSimulacaoItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> CenarioSimulacaoItemResponse:
    return service.atualizar(db, item_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> None:
    service.deletar(db, item_id)
