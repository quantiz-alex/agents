from typing import Optional

from sqlalchemy.orm import Session

from backend.models.importacoes_base import ImportacaoBase
from backend.schemas.importacoes_base import ImportacaoBaseCreate, ImportacaoBaseUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[ImportacaoBase]:
    return db.query(ImportacaoBase).offset(skip).limit(limit).all()


def get_by_id(db: Session, importacao_id: int) -> Optional[ImportacaoBase]:
    return db.query(ImportacaoBase).filter(ImportacaoBase.id == importacao_id).first()


def create(db: Session, data: ImportacaoBaseCreate) -> ImportacaoBase:
    db_obj = ImportacaoBase(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, importacao_id: int, data: ImportacaoBaseUpdate) -> Optional[ImportacaoBase]:
    db_obj = get_by_id(db, importacao_id)
    if db_obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, importacao_id: int) -> bool:
    db_obj = get_by_id(db, importacao_id)
    if db_obj is None:
        return False
    db.delete(db_obj)
    db.commit()
    return True
