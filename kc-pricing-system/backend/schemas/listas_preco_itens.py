from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ListaPrecoItemBase(BaseModel):
    lista_preco_id: int
    produto_id: int
    ptc_sell_out: Decimal = Field(..., decimal_places=4)
    margem_cadeia_pct: Decimal = Field(..., decimal_places=4)
    sell_in_nf: Decimal = Field(..., decimal_places=4)
    sell_in_niv: Decimal = Field(..., decimal_places=4)
    custo_aquisicao: Optional[Decimal] = None
    markup: Optional[Decimal] = None
    cap_aplicado: bool
    variacao_pct: Optional[Decimal] = None


class ListaPrecoItemCreate(ListaPrecoItemBase):
    pass


class ListaPrecoItemUpdate(BaseModel):
    lista_preco_id: Optional[int] = None
    produto_id: Optional[int] = None
    ptc_sell_out: Optional[Decimal] = None
    margem_cadeia_pct: Optional[Decimal] = None
    sell_in_nf: Optional[Decimal] = None
    sell_in_niv: Optional[Decimal] = None
    custo_aquisicao: Optional[Decimal] = None
    markup: Optional[Decimal] = None
    cap_aplicado: Optional[bool] = None
    variacao_pct: Optional[Decimal] = None


class ListaPrecoItemResponse(ListaPrecoItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
