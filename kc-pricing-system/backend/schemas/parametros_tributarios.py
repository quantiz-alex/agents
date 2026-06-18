from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ParametroTributarioBase(BaseModel):
    ano_vigencia: int
    regime: str = Field(..., max_length=20)
    aliquota_ibs: Decimal = Field(..., decimal_places=4)
    aliquota_cbs: Decimal = Field(..., decimal_places=4)
    aliquota_icms: Decimal = Field(..., decimal_places=4)
    aliquota_pis: Decimal = Field(..., decimal_places=4)
    aliquota_cofins: Decimal = Field(..., decimal_places=4)
    aliquota_is: Decimal = Field(..., decimal_places=4)
    credito_pis_cofins: Optional[Decimal] = None
    debito_icms: Optional[Decimal] = None
    ativo: bool = Field(default=False)
    usuario_id: int


class ParametroTributarioCreate(ParametroTributarioBase):
    pass


class ParametroTributarioUpdate(BaseModel):
    ano_vigencia: Optional[int] = None
    regime: Optional[str] = Field(default=None, max_length=20)
    aliquota_ibs: Optional[Decimal] = None
    aliquota_cbs: Optional[Decimal] = None
    aliquota_icms: Optional[Decimal] = None
    aliquota_pis: Optional[Decimal] = None
    aliquota_cofins: Optional[Decimal] = None
    aliquota_is: Optional[Decimal] = None
    credito_pis_cofins: Optional[Decimal] = None
    debito_icms: Optional[Decimal] = None
    ativo: Optional[bool] = None
    usuario_id: Optional[int] = None


class ParametroTributarioResponse(ParametroTributarioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
