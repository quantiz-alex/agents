from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.margens_cadeia import MargemCadeia
from backend.repositories import margens_cadeia as repo
from backend.schemas.margens_cadeia import MargemCadeiaCreate, MargemCadeiaUpdate


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[MargemCadeia]:
    return repo.get_all(db, skip=skip, limit=limit)


def obter(db: Session, margem_id: int) -> MargemCadeia:
    obj = repo.get_by_id(db, margem_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Margem da cadeia não encontrada")
    return obj


def criar(db: Session, data: MargemCadeiaCreate) -> MargemCadeia:
    return repo.create(db, data)


def atualizar(db: Session, margem_id: int, data: MargemCadeiaUpdate) -> MargemCadeia:
    obj = repo.update(db, margem_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Margem da cadeia não encontrada")
    return obj


def deletar(db: Session, margem_id: int) -> None:
    success = repo.delete(db, margem_id)
    if not success:
        raise HTTPException(status_code=404, detail="Margem da cadeia não encontrada")
