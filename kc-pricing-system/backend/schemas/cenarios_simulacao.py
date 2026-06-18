from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CenarioSimulacaoBase(BaseModel):
    descricao: str = Field(..., max_length=200)
    tipo_cenario: str = Field(..., max_length=20)
    lista_preco_id: int
    parametro_tributario_id: int
    data_simulacao: datetime
    usuario_id: int
    delta_volume_pct: Optional[Decimal] = None
    delta_receita_niv: Optional[Decimal] = None
    delta_margem_industria: Optional[Decimal] = None


class CenarioSimulacaoCreate(BaseModel):
    descricao: str = Field(..., max_length=200)
    tipo_cenario: str = Field(..., max_length=20)
    lista_preco_id: int
    parametro_tributario_id: int
    usuario_id: int
    data_simulacao: Optional[datetime] = None
    delta_volume_pct: Optional[Decimal] = None
    delta_receita_niv: Optional[Decimal] = None
    delta_margem_industria: Optional[Decimal] = None


class CenarioSimulacaoUpdate(BaseModel):
    descricao: Optional[str] = Field(default=None, max_length=200)
    tipo_cenario: Optional[str] = Field(default=None, max_length=20)
    lista_preco_id: Optional[int] = None
    parametro_tributario_id: Optional[int] = None
    data_simulacao: Optional[datetime] = None
    usuario_id: Optional[int] = None
    delta_volume_pct: Optional[Decimal] = None
    delta_receita_niv: Optional[Decimal] = None
    delta_margem_industria: Optional[Decimal] = None


class CenarioSimulacaoResponse(CenarioSimulacaoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
