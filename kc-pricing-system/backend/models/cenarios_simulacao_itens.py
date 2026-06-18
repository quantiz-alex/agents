from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class CenarioSimulacaoItem(Base):
    __tablename__ = "cenarios_simulacao_itens"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    cenario_id = Column(BigInteger, ForeignKey("cenarios_simulacao.id"), nullable=False)
    produto_id = Column(BigInteger, ForeignKey("produtos.id"), nullable=False)
    volume_simulado = Column(Numeric(15, 2), nullable=True)
    receita_niv_simulada = Column(Numeric(15, 4), nullable=True)
    margem_industria = Column(Numeric(15, 4), nullable=True)
    margem_distribuidor = Column(Numeric(15, 4), nullable=True)
    margem_varejo = Column(Numeric(15, 4), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    cenario = relationship("CenarioSimulacao", foreign_keys=[cenario_id])
    produto = relationship("Produto", foreign_keys=[produto_id])

    __table_args__ = (
        Index("ix_cenarios_simulacao_itens_cenario_id", "cenario_id"),
        Index("ix_cenarios_simulacao_itens_produto_id", "produto_id"),
    )
