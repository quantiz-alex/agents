from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ImportacaoBaseBase(BaseModel):
    fonte: str = Field(..., max_length=50)
    nome_arquivo: str = Field(..., max_length=255)
    data_importacao: datetime
    usuario_id: int
    total_linhas: Optional[int] = None
    status: str = Field(default="Processando", max_length=20)
    hash_arquivo: str = Field(..., max_length=64)
    observacao: Optional[str] = Field(default=None, max_length=500)


class ImportacaoBaseCreate(ImportacaoBaseBase):
    pass


class ImportacaoBaseUpdate(BaseModel):
    fonte: Optional[str] = Field(default=None, max_length=50)
    nome_arquivo: Optional[str] = Field(default=None, max_length=255)
    data_importacao: Optional[datetime] = None
    usuario_id: Optional[int] = None
    total_linhas: Optional[int] = None
    status: Optional[str] = Field(default=None, max_length=20)
    hash_arquivo: Optional[str] = Field(default=None, max_length=64)
    observacao: Optional[str] = Field(default=None, max_length=500)


class ImportacaoBaseResponse(ImportacaoBaseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
