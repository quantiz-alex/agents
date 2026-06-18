from typing import Optional

from sqlalchemy.orm import Session

from backend.models.parametros_tributarios import ParametroTributario
from backend.schemas.parametros_tributarios import ParametroTributarioCreate, ParametroTributarioUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[ParametroTributario]:
    return (
        db.query(ParametroTributario)
        .filter(ParametroTributario.ativo == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_including_inactive(db: Session, skip: int = 0, limit: int = 100) -> list[ParametroTributario]:
    return db.query(ParametroTributario).offset(skip).limit(limit).all()


def get_by_id(db: Session, parametro_id: int) -> Optional[ParametroTributario]:
    return db.query(ParametroTributario).filter(ParametroTributario.id == parametro_id).first()


def create(db: Session, data: ParametroTributarioCreate) -> ParametroTributario:
    db_obj = ParametroTributario(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, parametro_id: int, data: ParametroTributarioUpdate) -> Optional[ParametroTributario]:
    db_obj = get_by_id(db, parametro_id)
    if db_obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, parametro_id: int) -> bool:
    db_obj = get_by_id(db, parametro_id)
    if db_obj is None:
        return False
    db_obj.ativo = False
    db.commit()
    return True
