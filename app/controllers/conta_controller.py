from __future__ import annotations
from app.database.connection import get_session
from app.models.conta import Conta


class ContaController:
    def listar_todas(self) -> list[Conta]:
        pass

    def listar_por_grupo(self, grupo: str) -> list[Conta]:
        pass

    def buscar_por_id(self, conta_id: int) -> Conta | None:
        pass

    def buscar_por_codigo(self, codigo: str) -> Conta | None:
        pass

    def criar(self, dados: dict) -> Conta:
        pass

    def atualizar(self, conta_id: int, dados: dict) -> Conta | None:
        pass

    def excluir(self, conta_id: int) -> bool:
        pass

    def listar_analiticas(self) -> list[Conta]:
        pass
