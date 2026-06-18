from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.usuarios import Usuario
from backend.repositories import usuarios as repo
from backend.schemas.usuarios import UsuarioCreate, UsuarioUpdate


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    return repo.get_all(db, skip=skip, limit=limit)


def obter(db: Session, usuario_id: int) -> Usuario:
    obj = repo.get_by_id(db, usuario_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return obj


def criar(db: Session, data: UsuarioCreate) -> Usuario:
    from backend.auth import hash_password

    existing = repo.get_by_email(db, data.email)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email já cadastrado")
    senha_hash = hash_password(data.senha)
    return repo.create(db, data, senha_hash)


def atualizar(db: Session, usuario_id: int, data: UsuarioUpdate) -> Usuario:
    from backend.auth import hash_password

    senha_hash = None
    if data.senha is not None:
        senha_hash = hash_password(data.senha)
    obj = repo.update(db, usuario_id, data, senha_hash=senha_hash)
    if obj is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return obj


def deletar(db: Session, usuario_id: int) -> None:
    success = repo.delete(db, usuario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
