from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class ImportacaoBase(Base):
    __tablename__ = "importacoes_base"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    fonte = Column(String(50), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    data_importacao = Column(DateTime, nullable=False, server_default=func.now())
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"), nullable=False)
    total_linhas = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="Processando")
    hash_arquivo = Column(String(64), nullable=False)
    observacao = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", foreign_keys=[usuario_id])

    __table_args__ = (
        Index("ix_importacoes_base_usuario_id", "usuario_id"),
        Index("ix_importacoes_base_fonte_data", "fonte", "data_importacao"),
    )
