from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MargemCadeiaBase(BaseModel):
    familia: str = Field(..., max_length=100)
    canal: str = Field(..., max_length=100)
    margem_industria: Decimal = Field(..., decimal_places=4)
    margem_distribuidor: Decimal = Field(..., decimal_places=4)
    margem_varejo: Decimal = Field(..., decimal_places=4)
    price_index: Decimal = Field(..., decimal_places=4)
    relatividade: Decimal = Field(..., decimal_places=4)
    vigencia_inicio: date
    vigencia_fim: Optional[date] = None


class MargemCadeiaCreate(MargemCadeiaBase):
    pass


class MargemCadeiaUpdate(BaseModel):
    familia: Optional[str] = Field(default=None, max_length=100)
    canal: Optional[str] = Field(default=None, max_length=100)
    margem_industria: Optional[Decimal] = None
    margem_distribuidor: Optional[Decimal] = None
    margem_varejo: Optional[Decimal] = None
    price_index: Optional[Decimal] = None
    relatividade: Optional[Decimal] = None
    vigencia_inicio: Optional[date] = None
    vigencia_fim: Optional[date] = None


class MargemCadeiaResponse(MargemCadeiaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
