from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.schemas.listas_preco_itens import ListaPrecoItemCreate, ListaPrecoItemResponse, ListaPrecoItemUpdate
from backend.services import listas_preco_itens as service

router = APIRouter(prefix="/listas-preco-itens", tags=["ListasPrecoItens"])


@router.get("/", response_model=list[ListaPrecoItemResponse])
def listar_itens(
    skip: int = 0,
    limit: int = 500,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ListaPrecoItemResponse]:
    return service.listar(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ListaPrecoItemResponse)
def obter_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ListaPrecoItemResponse:
    return service.obter(db, item_id)


@router.post("/", response_model=ListaPrecoItemResponse, status_code=status.HTTP_201_CREATED)
def criar_item(
    data: ListaPrecoItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ListaPrecoItemResponse:
    return service.criar(db, data)


@router.put("/{item_id}", response_model=ListaPrecoItemResponse)
def atualizar_item(
    item_id: int,
    data: ListaPrecoItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ListaPrecoItemResponse:
    return service.atualizar(db, item_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> None:
    service.deletar(db, item_id)
