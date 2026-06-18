from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import (
    create_access_token,
    get_current_user,
    verify_password,
)
from backend.config import settings
from backend.database import get_db
from backend.repositories.usuarios import get_by_email
from backend.schemas.token import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    usuario = get_by_email(db, data.email)
    if usuario is None or not verify_password(data.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo",
        )
    access_token = create_access_token(
        data={"sub": str(usuario.id), "email": usuario.email}
    )
    expires_in = settings.access_token_expire_minutes * 60
    return TokenResponse(access_token=access_token, token_type="bearer", expires_in=expires_in)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(current_user=Depends(get_current_user)) -> TokenResponse:
    access_token = create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email}
    )
    expires_in = settings.access_token_expire_minutes * 60
    return TokenResponse(access_token=access_token, token_type="bearer", expires_in=expires_in)
