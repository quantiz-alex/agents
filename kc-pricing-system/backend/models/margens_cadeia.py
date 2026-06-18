from sqlalchemy import BigInteger, Column, Date, DateTime, Index, Numeric, String
from sqlalchemy.sql import func

from backend.database import Base


class MargemCadeia(Base):
    __tablename__ = "margens_cadeia"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    familia = Column(String(100), nullable=False)
    canal = Column(String(100), nullable=False)
    margem_industria = Column(Numeric(5, 4), nullable=False)
    margem_distribuidor = Column(Numeric(5, 4), nullable=False)
    margem_varejo = Column(Numeric(5, 4), nullable=False)
    price_index = Column(Numeric(10, 4), nullable=False)
    relatividade = Column(Numeric(10, 4), nullable=False)
    vigencia_inicio = Column(Date, nullable=False)
    vigencia_fim = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_margens_cadeia_familia_canal", "familia", "canal"),
    )
