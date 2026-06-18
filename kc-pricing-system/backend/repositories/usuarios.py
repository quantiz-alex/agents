from typing import Optional

from sqlalchemy.orm import Session

from backend.models.usuarios import Usuario
from backend.schemas.usuarios import UsuarioCreate, UsuarioUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    return db.query(Usuario).filter(Usuario.ativo == True).offset(skip).limit(limit).all()


def get_by_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def get_by_email(db: Session, email: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.email == email).first()


def create(db: Session, data: UsuarioCreate, senha_hash: str) -> Usuario:
    db_obj = Usuario(
        nome=data.nome,
        email=data.email,
        senha_hash=senha_hash,
        role=data.role,
        ativo=data.ativo,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, usuario_id: int, data: UsuarioUpdate, senha_hash: Optional[str] = None) -> Optional[Usuario]:
    db_obj = get_by_id(db, usuario_id)
    if db_obj is None:
        return None
    update_data = data.model_dump(exclude_unset=True, exclude={"senha"})
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    if senha_hash is not None:
        db_obj.senha_hash = senha_hash
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, usuario_id: int) -> bool:
    db_obj = get_by_id(db, usuario_id)
    if db_obj is None:
        return False
    db_obj.ativo = False
    db.commit()
    return True
