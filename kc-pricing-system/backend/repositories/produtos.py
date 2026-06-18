from typing import Optional

from sqlalchemy.orm import Session

from backend.models.produtos import Produto
from backend.schemas.produtos import ProdutoCreate, ProdutoUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Produto]:
    return db.query(Produto).filter(Produto.ativo == True).offset(skip).limit(limit).all()


def get_by_id(db: Session, produto_id: int) -> Optional[Produto]:
    return db.query(Produto).filter(Produto.id == produto_id).first()


def get_by_sku(db: Session, sku: str) -> Optional[Produto]:
    return db.query(Produto).filter(Produto.sku == sku).first()


def create(db: Session, data: ProdutoCreate) -> Produto:
    db_obj = Produto(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, produto_id: int, data: ProdutoUpdate) -> Optional[Produto]:
    db_obj = get_by_id(db, produto_id)
    if db_obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, produto_id: int) -> bool:
    db_obj = get_by_id(db, produto_id)
    if db_obj is None:
        return False
    db_obj.ativo = False
    db.commit()
    return True
