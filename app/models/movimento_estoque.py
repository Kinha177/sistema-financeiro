from __future__ import annotations
from datetime import date
from decimal import Decimal
from sqlalchemy import String, Date, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    # ENTRADA, SAIDA, AJUSTE
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    quantidade: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)

    produto: Mapped["Produto"] = relationship("Produto", back_populates="movimentacoes")  # noqa: F821

    def __repr__(self) -> str:
        return f"<MovimentacaoEstoque id={self.id} tipo={self.tipo}>"
