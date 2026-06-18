from typing import Optional

from sqlalchemy.orm import Session

from backend.models.cenarios_simulacao_itens import CenarioSimulacaoItem
from backend.schemas.cenarios_simulacao_itens import CenarioSimulacaoItemCreate, CenarioSimulacaoItemUpdate


def get_all(db: Session, skip: int = 0, limit: int = 500) -> list[CenarioSimulacaoItem]:
    return db.query(CenarioSimulacaoItem).offset(skip).limit(limit).all()


def get_by_id(db: Session, item_id: int) -> Optional[CenarioSimulacaoItem]:
    return db.query(CenarioSimulacaoItem).filter(CenarioSimulacaoItem.id == item_id).first()


def create(db: Session, data: CenarioSimulacaoItemCreate) -> CenarioSimulacaoItem:
    db_obj = CenarioSimulacaoItem(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, item_id: int, data: CenarioSimulacaoItemUpdate) -> Optional[CenarioSimulacaoItem]:
    db_obj = get_by_id(db, item_id)
    if db_obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, item_id: int) -> bool:
    db_obj = get_by_id(db, item_id)
    if db_obj is None:
        return False
    db.delete(db_obj)
    db.commit()
    return True
