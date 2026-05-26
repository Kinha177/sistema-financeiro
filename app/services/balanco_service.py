from __future__ import annotations
from datetime import date
from decimal import Decimal


class BalancoService:
    """Regras de negócio do Balanço Patrimonial."""

    def apurar_balanco(self, data_base: date) -> dict:
        pass

    def calcular_ativo_circulante(self, data_base: date) -> Decimal:
        pass

    def calcular_ativo_nao_circulante(self, data_base: date) -> Decimal:
        pass

    def calcular_passivo_circulante(self, data_base: date) -> Decimal:
        pass

    def calcular_passivo_nao_circulante(self, data_base: date) -> Decimal:
        pass

    def calcular_patrimonio_liquido(self, data_base: date) -> Decimal:
        pass

    def verificar_equacao(self, data_base: date) -> bool:
        """Ativo = Passivo + PL."""
        pass
