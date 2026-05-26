from __future__ import annotations
from datetime import date
from decimal import Decimal
from sqlalchemy import String, Text, Date, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.conta import Conta


class Lancamento(Base):
    """Partida dobrada — cada registro representa um lançamento contábil."""

    __tablename__ = "lancamentos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    historico: Mapped[str] = mapped_column(Text, nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    numero_documento: Mapped[str | None] = mapped_column(String(50))
    # MANUAL, IMPORTADO, AJUSTE
    origem: Mapped[str] = mapped_column(String(20), default="MANUAL")

    conta_debito_id: Mapped[int] = mapped_column(ForeignKey("contas.id"), nullable=False)
    conta_credito_id: Mapped[int] = mapped_column(ForeignKey("contas.id"), nullable=False)

    conta_debito: Mapped[Conta] = relationship("Conta", foreign_keys=[conta_debito_id])
    conta_credito: Mapped[Conta] = relationship("Conta", foreign_keys=[conta_credito_id])

    def __repr__(self) -> str:
        return f"<Lancamento id={self.id} data={self.data} valor={self.valor}>"
