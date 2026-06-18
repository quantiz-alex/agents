from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.importacoes_base import ImportacaoBase
from backend.repositories import importacoes_base as repo
from backend.schemas.importacoes_base import ImportacaoBaseCreate, ImportacaoBaseUpdate


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[ImportacaoBase]:
    return repo.get_all(db, skip=skip, limit=limit)


def obter(db: Session, importacao_id: int) -> ImportacaoBase:
    obj = repo.get_by_id(db, importacao_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Importação não encontrada")
    return obj


def criar(db: Session, data: ImportacaoBaseCreate) -> ImportacaoBase:
    return repo.create(db, data)


def atualizar(db: Session, importacao_id: int, data: ImportacaoBaseUpdate) -> ImportacaoBase:
    obj = repo.update(db, importacao_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Importação não encontrada")
    return obj


def deletar(db: Session, importacao_id: int) -> None:
    success = repo.delete(db, importacao_id)
    if not success:
        raise HTTPException(status_code=404, detail="Importação não encontrada")
