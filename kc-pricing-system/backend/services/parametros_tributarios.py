from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.parametros_tributarios import ParametroTributario
from backend.repositories import parametros_tributarios as repo
from backend.schemas.parametros_tributarios import ParametroTributarioCreate, ParametroTributarioUpdate


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[ParametroTributario]:
    return repo.get_all_including_inactive(db, skip=skip, limit=limit)


def obter(db: Session, parametro_id: int) -> ParametroTributario:
    obj = repo.get_by_id(db, parametro_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Parâmetro tributário não encontrado")
    return obj


def criar(db: Session, data: ParametroTributarioCreate) -> ParametroTributario:
    return repo.create(db, data)


def atualizar(db: Session, parametro_id: int, data: ParametroTributarioUpdate) -> ParametroTributario:
    obj = repo.update(db, parametro_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Parâmetro tributário não encontrado")
    return obj


def deletar(db: Session, parametro_id: int) -> None:
    success = repo.delete(db, parametro_id)
    if not success:
        raise HTTPException(status_code=404, detail="Parâmetro tributário não encontrado")
