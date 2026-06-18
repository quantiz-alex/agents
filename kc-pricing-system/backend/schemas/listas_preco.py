from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ListaPrecoBase(BaseModel):
    descricao: str = Field(..., max_length=200)
    data_geracao: datetime
    usuario_id: int
    parametro_tributario_id: int
    status: str = Field(default="Gerada", max_length=30)
    total_skus: Optional[int] = None
    pct_dentro_cap: Optional[Decimal] = None
    aprovado_por: Optional[int] = None
    data_aprovacao: Optional[datetime] = None


class ListaPrecoCreate(BaseModel):
    descricao: str = Field(..., max_length=200)
    parametro_tributario_id: int
    usuario_id: int
    data_geracao: Optional[datetime] = None
    status: str = Field(default="Gerada", max_length=30)
    total_skus: Optional[int] = None
    pct_dentro_cap: Optional[Decimal] = None


class ListaPrecoUpdate(BaseModel):
    descricao: Optional[str] = Field(default=None, max_length=200)
    status: Optional[str] = Field(default=None, max_length=30)
    total_skus: Optional[int] = None
    pct_dentro_cap: Optional[Decimal] = None
    aprovado_por: Optional[int] = None
    data_aprovacao: Optional[datetime] = None
    parametro_tributario_id: Optional[int] = None


class ListaPrecoResponse(ListaPrecoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
