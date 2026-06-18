from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class CenarioSimulacao(Base):
    __tablename__ = "cenarios_simulacao"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    descricao = Column(String(200), nullable=False)
    tipo_cenario = Column(String(20), nullable=False)
    lista_preco_id = Column(BigInteger, ForeignKey("listas_preco.id"), nullable=False)
    parametro_tributario_id = Column(BigInteger, ForeignKey("parametros_tributarios.id"), nullable=False)
    data_simulacao = Column(DateTime, nullable=False, server_default=func.now())
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"), nullable=False)
    delta_volume_pct = Column(Numeric(8, 4), nullable=True)
    delta_receita_niv = Column(Numeric(15, 2), nullable=True)
    delta_margem_industria = Column(Numeric(15, 2), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    lista_preco = relationship("ListaPreco", foreign_keys=[lista_preco_id])
    parametro_tributario = relationship("ParametroTributario", foreign_keys=[parametro_tributario_id])
    usuario = relationship("Usuario", foreign_keys=[usuario_id])

    __table_args__ = (
        Index("ix_cenarios_simulacao_lista_preco_id", "lista_preco_id"),
        Index("ix_cenarios_simulacao_parametro_tributario_id", "parametro_tributario_id"),
        Index("ix_cenarios_simulacao_usuario_id", "usuario_id"),
    )
