from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.listas_preco import ListaPreco
from backend.repositories import listas_preco as repo
from backend.schemas.listas_preco import ListaPrecoCreate, ListaPrecoUpdate


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[ListaPreco]:
    return repo.get_all(db, skip=skip, limit=limit)


def obter(db: Session, lista_id: int) -> ListaPreco:
    obj = repo.get_by_id(db, lista_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Lista de preço não encontrada")
    return obj


def criar(db: Session, data: ListaPrecoCreate) -> ListaPreco:
    return repo.create(db, data)


def atualizar(db: Session, lista_id: int, data: ListaPrecoUpdate) -> ListaPreco:
    obj = repo.update(db, lista_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Lista de preço não encontrada")
    return obj


def deletar(db: Session, lista_id: int) -> None:
    success = repo.delete(db, lista_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lista de preço não encontrada")
