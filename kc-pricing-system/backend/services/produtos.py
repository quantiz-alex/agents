from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.produtos import Produto
from backend.repositories import produtos as repo
from backend.schemas.produtos import ProdutoCreate, ProdutoUpdate


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Produto]:
    return repo.get_all(db, skip=skip, limit=limit)


def obter(db: Session, produto_id: int) -> Produto:
    obj = repo.get_by_id(db, produto_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return obj


def criar(db: Session, data: ProdutoCreate) -> Produto:
    existing = repo.get_by_sku(db, data.sku)
    if existing is not None:
        raise HTTPException(status_code=409, detail="SKU já cadastrado")
    return repo.create(db, data)


def atualizar(db: Session, produto_id: int, data: ProdutoUpdate) -> Produto:
    obj = repo.update(db, produto_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return obj


def deletar(db: Session, produto_id: int) -> None:
    success = repo.delete(db, produto_id)
    if not success:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
