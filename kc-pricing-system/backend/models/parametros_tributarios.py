from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class ParametroTributario(Base):
    __tablename__ = "parametros_tributarios"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    ano_vigencia = Column(Integer, nullable=False)
    regime = Column(String(20), nullable=False)
    aliquota_ibs = Column(Numeric(5, 4), nullable=False)
    aliquota_cbs = Column(Numeric(5, 4), nullable=False)
    aliquota_icms = Column(Numeric(5, 4), nullable=False)
    aliquota_pis = Column(Numeric(5, 4), nullable=False)
    aliquota_cofins = Column(Numeric(5, 4), nullable=False)
    aliquota_is = Column(Numeric(5, 4), nullable=False)
    credito_pis_cofins = Column(Numeric(5, 4), nullable=True)
    debito_icms = Column(Numeric(5, 4), nullable=True)
    ativo = Column(Boolean, nullable=False, default=False)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", foreign_keys=[usuario_id])

    __table_args__ = (
        Index("ix_param_trib_ano_regime", "ano_vigencia", "regime"),
        Index("ix_param_trib_ativo", "ativo"),
    )
