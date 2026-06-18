from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Index, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class ListaPrecoItem(Base):
    __tablename__ = "listas_preco_itens"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    lista_preco_id = Column(BigInteger, ForeignKey("listas_preco.id"), nullable=False)
    produto_id = Column(BigInteger, ForeignKey("produtos.id"), nullable=False)
    ptc_sell_out = Column(Numeric(15, 4), nullable=False)
    margem_cadeia_pct = Column(Numeric(5, 4), nullable=False)
    sell_in_nf = Column(Numeric(15, 4), nullable=False)
    sell_in_niv = Column(Numeric(15, 4), nullable=False)
    custo_aquisicao = Column(Numeric(15, 4), nullable=True)
    markup = Column(Numeric(5, 4), nullable=True)
    cap_aplicado = Column(Boolean, nullable=False, default=False)
    variacao_pct = Column(Numeric(8, 4), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    lista_preco = relationship("ListaPreco", foreign_keys=[lista_preco_id])
    produto = relationship("Produto", foreign_keys=[produto_id])

    __table_args__ = (
        Index("ix_listas_preco_itens_lista_preco_id", "lista_preco_id"),
        Index("ix_listas_preco_itens_produto_id", "produto_id"),
        Index("ix_listas_preco_itens_lista_produto", "lista_preco_id", "produto_id"),
    )
