from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.cenarios_simulacao import CenarioSimulacao
from backend.repositories import cenarios_simulacao as repo
from backend.schemas.cenarios_simulacao import CenarioSimulacaoCreate, CenarioSimulacaoUpdate


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[CenarioSimulacao]:
    return repo.get_all(db, skip=skip, limit=limit)


def obter(db: Session, cenario_id: int) -> CenarioSimulacao:
    obj = repo.get_by_id(db, cenario_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Cenário de simulação não encontrado")
    return obj


def criar(db: Session, data: CenarioSimulacaoCreate) -> CenarioSimulacao:
    return repo.create(db, data)


def atualizar(db: Session, cenario_id: int, data: CenarioSimulacaoUpdate) -> CenarioSimulacao:
    obj = repo.update(db, cenario_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Cenário de simulação não encontrado")
    return obj


def deletar(db: Session, cenario_id: int) -> None:
    success = repo.delete(db, cenario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cenário de simulação não encontrado")
