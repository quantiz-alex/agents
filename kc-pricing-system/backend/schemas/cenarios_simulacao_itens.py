from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CenarioSimulacaoItemBase(BaseModel):
    cenario_id: int
    produto_id: int
    volume_simulado: Optional[Decimal] = None
    receita_niv_simulada: Optional[Decimal] = None
    margem_industria: Optional[Decimal] = None
    margem_distribuidor: Optional[Decimal] = None
    margem_varejo: Optional[Decimal] = None


class CenarioSimulacaoItemCreate(CenarioSimulacaoItemBase):
    pass


class CenarioSimulacaoItemUpdate(BaseModel):
    cenario_id: Optional[int] = None
    produto_id: Optional[int] = None
    volume_simulado: Optional[Decimal] = None
    receita_niv_simulada: Optional[Decimal] = None
    margem_industria: Optional[Decimal] = None
    margem_distribuidor: Optional[Decimal] = None
    margem_varejo: Optional[Decimal] = None


class CenarioSimulacaoItemResponse(CenarioSimulacaoItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
