from sqlalchemy import BigInteger, Boolean, Column, DateTime, Index, Numeric, String
from sqlalchemy.sql import func

from backend.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    sku = Column(String(50), nullable=False, unique=True)
    descricao = Column(String(200), nullable=False)
    familia = Column(String(100), nullable=False)
    embalagem = Column(String(100), nullable=True)
    classificacao = Column(String(20), nullable=True)
    canal = Column(String(100), nullable=True)
    regiao = Column(String(100), nullable=True)
    preco_atual = Column(Numeric(15, 4), nullable=True)
    ativo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_produtos_sku", "sku", unique=True),
        Index("ix_produtos_familia_canal", "familia", "canal"),
    )
