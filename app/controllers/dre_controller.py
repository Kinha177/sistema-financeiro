from __future__ import annotations
from datetime import date


class DREController:
    def gerar(self, data_inicio: date, data_fim: date) -> dict:
        pass

    def calcular_receita_bruta(self, data_inicio: date, data_fim: date) -> float:
        pass

    def calcular_deducoes(self, data_inicio: date, data_fim: date) -> float:
        pass

    def calcular_custo_mercadorias(self, data_inicio: date, data_fim: date) -> float:
        pass

    def calcular_despesas_operacionais(self, data_inicio: date, data_fim: date) -> float:
        pass

    def calcular_resultado_liquido(self, data_inicio: date, data_fim: date) -> float:
        pass
