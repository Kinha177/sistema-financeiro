from __future__ import annotations
from datetime import date


class BalancoController:
    def gerar(self, data_base: date) -> dict:
        pass

    def calcular_ativo(self, data_base: date) -> dict:
        pass

    def calcular_passivo(self, data_base: date) -> dict:
        pass

    def calcular_patrimonio_liquido(self, data_base: date) -> dict:
        pass

    def verificar_equacao_patrimonial(self, data_base: date) -> bool:
        pass
