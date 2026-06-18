from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.cenarios_simulacao import CenarioSimulacao
from backend.schemas.cenarios_simulacao import CenarioSimulacaoCreate, CenarioSimulacaoUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[CenarioSimulacao]:
    return db.query(CenarioSimulacao).offset(skip).limit(limit).all()


def get_by_id(db: Session, cenario_id: int) -> Optional[CenarioSimulacao]:
    return db.query(CenarioSimulacao).filter(CenarioSimulacao.id == cenario_id).first()


def create(db: Session, data: CenarioSimulacaoCreate) -> CenarioSimulacao:
    data_dict = data.model_dump()
    if data_dict.get("data_simulacao") is None:
        data_dict["data_simulacao"] = datetime.utcnow()
    db_obj = CenarioSimulacao(**data_dict)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, cenario_id: int, data: CenarioSimulacaoUpdate) -> Optional[CenarioSimulacao]:
    db_obj = get_by_id(db, cenario_id)
    if db_obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, cenario_id: int) -> bool:
    db_obj = get_by_id(db, cenario_id)
    if db_obj is None:
        return False
    db.delete(db_obj)
    db.commit()
    return True
