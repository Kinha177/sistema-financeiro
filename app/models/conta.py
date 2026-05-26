from __future__ import annotations
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class PlanoConta(Base):
    __tablename__ = "plano_contas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    # ANALITICA ou SINTETICA
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    # DEVEDORA ou CREDORA
    natureza: Mapped[str] = mapped_column(String(10), nullable=False)

    conta_pai_id: Mapped[int | None] = mapped_column(ForeignKey("plano_contas.id"))
    conta_pai: Mapped[PlanoConta | None] = relationship(
        "PlanoConta", remote_side="PlanoConta.id", back_populates="subcontas"
    )
    subcontas: Mapped[list[PlanoConta]] = relationship("PlanoConta", back_populates="conta_pai")

    def __repr__(self) -> str:
        return f"<PlanoConta {self.codigo} — {self.nome}>"
