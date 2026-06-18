from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.listas_preco_itens import ListaPrecoItem
from backend.repositories import listas_preco_itens as repo
from backend.schemas.listas_preco_itens import ListaPrecoItemCreate, ListaPrecoItemUpdate


def listar(db: Session, skip: int = 0, limit: int = 500) -> list[ListaPrecoItem]:
    return repo.get_all(db, skip=skip, limit=limit)


def obter(db: Session, item_id: int) -> ListaPrecoItem:
    obj = repo.get_by_id(db, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Item de lista de preço não encontrado")
    return obj


def criar(db: Session, data: ListaPrecoItemCreate) -> ListaPrecoItem:
    return repo.create(db, data)


def atualizar(db: Session, item_id: int, data: ListaPrecoItemUpdate) -> ListaPrecoItem:
    obj = repo.update(db, item_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Item de lista de preço não encontrado")
    return obj


def deletar(db: Session, item_id: int) -> None:
    success = repo.delete(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item de lista de preço não encontrado")
