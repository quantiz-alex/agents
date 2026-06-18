from typing import Optional

from sqlalchemy.orm import Session

from backend.models.margens_cadeia import MargemCadeia
from backend.schemas.margens_cadeia import MargemCadeiaCreate, MargemCadeiaUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[MargemCadeia]:
    return db.query(MargemCadeia).offset(skip).limit(limit).all()


def get_by_id(db: Session, margem_id: int) -> Optional[MargemCadeia]:
    return db.query(MargemCadeia).filter(MargemCadeia.id == margem_id).first()


def create(db: Session, data: MargemCadeiaCreate) -> MargemCadeia:
    db_obj = MargemCadeia(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, margem_id: int, data: MargemCadeiaUpdate) -> Optional[MargemCadeia]:
    db_obj = get_by_id(db, margem_id)
    if db_obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, margem_id: int) -> bool:
    db_obj = get_by_id(db, margem_id)
    if db_obj is None:
        return False
    db.delete(db_obj)
    db.commit()
    return True
