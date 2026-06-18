from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    sku: str = Field(..., max_length=50)
    descricao: str = Field(..., max_length=200)
    familia: str = Field(..., max_length=100)
    embalagem: Optional[str] = Field(default=None, max_length=100)
    classificacao: Optional[str] = Field(default=None, max_length=20)
    canal: Optional[str] = Field(default=None, max_length=100)
    regiao: Optional[str] = Field(default=None, max_length=100)
    preco_atual: Optional[Decimal] = None
    ativo: bool = Field(default=True)


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    sku: Optional[str] = Field(default=None, max_length=50)
    descricao: Optional[str] = Field(default=None, max_length=200)
    familia: Optional[str] = Field(default=None, max_length=100)
    embalagem: Optional[str] = Field(default=None, max_length=100)
    classificacao: Optional[str] = Field(default=None, max_length=20)
    canal: Optional[str] = Field(default=None, max_length=100)
    regiao: Optional[str] = Field(default=None, max_length=100)
    preco_atual: Optional[Decimal] = None
    ativo: Optional[bool] = None


class ProdutoResponse(ProdutoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
