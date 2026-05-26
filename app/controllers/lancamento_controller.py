from __future__ import annotations
from datetime import date
from app.models.lancamento import Lancamento


class LancamentoController:
    def listar_todos(self) -> list[Lancamento]:
        pass

    def listar_por_periodo(self, data_inicio: date, data_fim: date) -> list[Lancamento]:
        pass

    def listar_por_conta(self, conta_id: int, data_inicio: date, data_fim: date) -> list[Lancamento]:
        pass

    def buscar_por_id(self, lancamento_id: int) -> Lancamento | None:
        pass

    def criar(self, dados: dict) -> Lancamento:
        pass

    def atualizar(self, lancamento_id: int, dados: dict) -> Lancamento | None:
        pass

    def excluir(self, lancamento_id: int) -> bool:
        pass
