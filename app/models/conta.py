from __future__ import annotations
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Conta(Base):
    """Plano de Contas — nó da árvore de contas contábeis."""

    __tablename__ = "contas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    # Grupos: ATIVO, PASSIVO, PATRIMÔNIO_LÍQUIDO, RECEITA, DESPESA, CUSTO
    grupo: Mapped[str] = mapped_column(String(30), nullable=False)
    # Natureza: DEVEDORA, CREDORA
    natureza: Mapped[str] = mapped_column(String(10), nullable=False)
    # ANALÍTICA (aceita lançamentos) ou SINTÉTICA (apenas agrupamento)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False, default="ANALITICA")
    ativa: Mapped[bool] = mapped_column(default=True)

    conta_pai_id: Mapped[int | None] = mapped_column(ForeignKey("contas.id"))
    conta_pai: Mapped[Conta | None] = relationship("Conta", remote_side="Conta.id", back_populates="subcontas")
    subcontas: Mapped[list[Conta]] = relationship("Conta", back_populates="conta_pai")

    def __repr__(self) -> str:
        return f"<Conta {self.codigo} — {self.nome}>"
