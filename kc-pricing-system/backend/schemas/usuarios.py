from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioBase(BaseModel):
    nome: str = Field(..., max_length=100)
    email: EmailStr = Field(..., max_length=150)
    role: str = Field(..., max_length=30)
    ativo: bool = Field(default=True)


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = Field(default=None, max_length=150)
    role: Optional[str] = Field(default=None, max_length=30)
    ativo: Optional[bool] = None
    senha: Optional[str] = Field(default=None, min_length=6)


class UsuarioResponse(UsuarioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
