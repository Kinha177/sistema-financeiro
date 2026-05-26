from __future__ import annotations
from datetime import date
from decimal import Decimal
from app.models.lancamento import Lancamento
from app.models.conta import Conta


class LancamentoService:
    """Regras de negócio dos lançamentos contábeis."""

    def validar_partida_dobrada(self, debito: Conta, credito: Conta, valor: Decimal) -> bool:
        pass

    def calcular_saldo_conta(self, conta_id: int, data_inicio: date, data_fim: date) -> Decimal:
        pass

    def gerar_livro_diario(self, data_inicio: date, data_fim: date) -> list[Lancamento]:
        pass

    def gerar_livro_razao(self, conta_id: int, data_inicio: date, data_fim: date) -> list[dict]:
        pass

    def gerar_razonete(self, conta_id: int, data_inicio: date, data_fim: date) -> dict:
        pass
