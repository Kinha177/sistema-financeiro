from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(18), unique=True)
    endereco: Mapped[str | None] = mapped_column(Text)
    telefone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(200))
    regime_tributario: Mapped[str | None] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"<Empresa id={self.id} nome={self.nome!r}>"
