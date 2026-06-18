from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class ListaPreco(Base):
    __tablename__ = "listas_preco"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    descricao = Column(String(200), nullable=False)
    data_geracao = Column(DateTime, nullable=False, server_default=func.now())
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"), nullable=False)
    parametro_tributario_id = Column(BigInteger, ForeignKey("parametros_tributarios.id"), nullable=False)
    status = Column(String(30), nullable=False, default="Gerada")
    total_skus = Column(Integer, nullable=True)
    pct_dentro_cap = Column(Numeric(5, 2), nullable=True)
    aprovado_por = Column(BigInteger, ForeignKey("usuarios.id"), nullable=True)
    data_aprovacao = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    parametro_tributario = relationship("ParametroTributario", foreign_keys=[parametro_tributario_id])
    aprovador = relationship("Usuario", foreign_keys=[aprovado_por])

    __table_args__ = (
        Index("ix_listas_preco_usuario_id", "usuario_id"),
        Index("ix_listas_preco_parametro_tributario_id", "parametro_tributario_id"),
        Index("ix_listas_preco_status", "status"),
    )
