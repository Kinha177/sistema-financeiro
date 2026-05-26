from __future__ import annotations
from datetime import date
from decimal import Decimal


class DREService:
    """Regras de negócio da Demonstração do Resultado do Exercício."""

    def apurar_resultado(self, data_inicio: date, data_fim: date) -> dict:
        pass

    def calcular_receita_bruta(self, data_inicio: date, data_fim: date) -> Decimal:
        pass

    def calcular_receita_liquida(self, data_inicio: date, data_fim: date) -> Decimal:
        pass

    def calcular_lucro_bruto(self, data_inicio: date, data_fim: date) -> Decimal:
        pass

    def calcular_lucro_operacional(self, data_inicio: date, data_fim: date) -> Decimal:
        pass

    def calcular_lucro_liquido(self, data_inicio: date, data_fim: date) -> Decimal:
        pass
