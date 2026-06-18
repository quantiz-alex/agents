from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.schemas.produtos import ProdutoCreate, ProdutoResponse, ProdutoUpdate
from backend.services import produtos as service

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("/", response_model=list[ProdutoResponse])
def listar_produtos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ProdutoResponse]:
    return service.listar(db, skip=skip, limit=limit)


@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProdutoResponse:
    return service.obter(db, produto_id)


@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(
    data: ProdutoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProdutoResponse:
    return service.criar(db, data)


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    data: ProdutoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProdutoResponse:
    return service.atualizar(db, produto_id, data)


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> None:
    service.deletar(db, produto_id)
