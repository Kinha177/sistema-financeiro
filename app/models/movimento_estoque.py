from __future__ import annotations
from datetime import date
from decimal import Decimal
from sqlalchemy import String, Text, Date, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class MovimentoEstoque(Base):
    """Registro de entradas e saídas de estoque (suporta PEPS e UEPS)."""

    __tablename__ = "movimentos_estoque"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    # ENTRADA, SAIDA, AJUSTE
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    quantidade: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    valor_unitario: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    # PEPS, UEPS, MEDIO
    metodo_custeio: Mapped[str] = mapped_column(String(10), default="MEDIO")
    numero_documento: Mapped[str | None] = mapped_column(String(50))
    observacao: Mapped[str | None] = mapped_column(Text)

    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    produto: Mapped["Produto"] = relationship("Produto", back_populates="movimentos")  # noqa: F821

    def __repr__(self) -> str:
        return f"<MovimentoEstoque id={self.id} tipo={self.tipo} qtd={self.quantidade}>"
