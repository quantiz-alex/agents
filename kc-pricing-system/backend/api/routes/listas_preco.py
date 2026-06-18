from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.schemas.listas_preco import ListaPrecoCreate, ListaPrecoResponse, ListaPrecoUpdate
from backend.services import listas_preco as service

router = APIRouter(prefix="/listas-preco", tags=["ListasPreco"])


@router.get("/", response_model=list[ListaPrecoResponse])
def listar_listas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ListaPrecoResponse]:
    return service.listar(db, skip=skip, limit=limit)


@router.get("/{lista_id}", response_model=ListaPrecoResponse)
def obter_lista(
    lista_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ListaPrecoResponse:
    return service.obter(db, lista_id)


@router.post("/", response_model=ListaPrecoResponse, status_code=status.HTTP_201_CREATED)
def criar_lista(
    data: ListaPrecoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ListaPrecoResponse:
    return service.criar(db, data)


@router.put("/{lista_id}", response_model=ListaPrecoResponse)
def atualizar_lista(
    lista_id: int,
    data: ListaPrecoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ListaPrecoResponse:
    return service.atualizar(db, lista_id, data)


@router.delete("/{lista_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_lista(
    lista_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> None:
    service.deletar(db, lista_id)
