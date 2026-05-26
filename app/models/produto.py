from __future__ import annotations
from decimal import Decimal
from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    estoque: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    movimentacoes: Mapped[list] = relationship("MovimentacaoEstoque", back_populates="produto")

    def __repr__(self) -> str:
        return f"<Produto id={self.id} nome={self.nome}>"
