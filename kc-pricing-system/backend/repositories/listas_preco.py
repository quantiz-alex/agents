from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.listas_preco import ListaPreco
from backend.schemas.listas_preco import ListaPrecoCreate, ListaPrecoUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[ListaPreco]:
    return db.query(ListaPreco).offset(skip).limit(limit).all()


def get_by_id(db: Session, lista_id: int) -> Optional[ListaPreco]:
    return db.query(ListaPreco).filter(ListaPreco.id == lista_id).first()


def create(db: Session, data: ListaPrecoCreate) -> ListaPreco:
    data_dict = data.model_dump()
    if data_dict.get("data_geracao") is None:
        data_dict["data_geracao"] = datetime.utcnow()
    db_obj = ListaPreco(**data_dict)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, lista_id: int, data: ListaPrecoUpdate) -> Optional[ListaPreco]:
    db_obj = get_by_id(db, lista_id)
    if db_obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, lista_id: int) -> bool:
    db_obj = get_by_id(db, lista_id)
    if db_obj is None:
        return False
    db_obj.status = "Arquivada"
    db.commit()
    return True
