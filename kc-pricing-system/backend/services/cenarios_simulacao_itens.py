from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.cenarios_simulacao_itens import CenarioSimulacaoItem
from backend.repositories import cenarios_simulacao_itens as repo
from backend.schemas.cenarios_simulacao_itens import CenarioSimulacaoItemCreate, CenarioSimulacaoItemUpdate


def listar(db: Session, skip: int = 0, limit: int = 500) -> list[CenarioSimulacaoItem]:
    return repo.get_all(db, skip=skip, limit=limit)


def obter(db: Session, item_id: int) -> CenarioSimulacaoItem:
    obj = repo.get_by_id(db, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Item de cenário de simulação não encontrado")
    return obj


def criar(db: Session, data: CenarioSimulacaoItemCreate) -> CenarioSimulacaoItem:
    return repo.create(db, data)


def atualizar(db: Session, item_id: int, data: CenarioSimulacaoItemUpdate) -> CenarioSimulacaoItem:
    obj = repo.update(db, item_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Item de cenário de simulação não encontrado")
    return obj


def deletar(db: Session, item_id: int) -> None:
    success = repo.delete(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item de cenário de simulação não encontrado")
