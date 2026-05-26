from __future__ import annotations
from decimal import Decimal
from sqlalchemy import String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Produto(Base):
    """Cadastro de produtos para controle de estoque."""

    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    unidade: Mapped[str] = mapped_column(String(10), default="UN")
    quantidade_atual: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    custo_medio: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    estoque_minimo: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    ativo: Mapped[bool] = mapped_column(default=True)

    movimentos: Mapped[list] = relationship("MovimentoEstoque", back_populates="produto")

    def __repr__(self) -> str:
        return f"<Produto {self.codigo} — {self.nome}>"
