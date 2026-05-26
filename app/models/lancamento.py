from __future__ import annotations
from datetime import date
from decimal import Decimal
from sqlalchemy import Text, Date, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class LancamentoContabil(Base):
    __tablename__ = "lancamentos_contabeis"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    historico: Mapped[str] = mapped_column(Text, nullable=False)

    itens: Mapped[list[ItemLancamento]] = relationship(
        "ItemLancamento", back_populates="lancamento", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<LancamentoContabil id={self.id} data={self.data}>"


class ItemLancamento(Base):
    __tablename__ = "itens_lancamento"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lancamento_id: Mapped[int] = mapped_column(
        ForeignKey("lancamentos_contabeis.id"), nullable=False
    )
    conta_debito_id: Mapped[int] = mapped_column(ForeignKey("plano_contas.id"), nullable=False)
    conta_credito_id: Mapped[int] = mapped_column(ForeignKey("plano_contas.id"), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    lancamento: Mapped[LancamentoContabil] = relationship(
        "LancamentoContabil", back_populates="itens"
    )
    conta_debito: Mapped["PlanoConta"] = relationship(  # noqa: F821
        "PlanoConta", foreign_keys=[conta_debito_id]
    )
    conta_credito: Mapped["PlanoConta"] = relationship(  # noqa: F821
        "PlanoConta", foreign_keys=[conta_credito_id]
    )

    def __repr__(self) -> str:
        return f"<ItemLancamento id={self.id} valor={self.valor}>"
