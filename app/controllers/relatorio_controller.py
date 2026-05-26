from __future__ import annotations
from datetime import date
from pathlib import Path


class RelatorioController:
    def exportar_plano_contas(self, destino: Path) -> Path:
        pass

    def exportar_livro_diario(self, data_inicio: date, data_fim: date, destino: Path) -> Path:
        pass

    def exportar_livro_razao(self, conta_id: int, data_inicio: date, data_fim: date, destino: Path) -> Path:
        pass

    def exportar_razonetes(self, data_base: date, destino: Path) -> Path:
        pass

    def exportar_dre(self, data_inicio: date, data_fim: date, destino: Path) -> Path:
        pass

    def exportar_balanco(self, data_base: date, destino: Path) -> Path:
        pass

    def exportar_estoque(self, destino: Path) -> Path:
        pass

    def exportar_ficha_peps(self, produto_id: int, destino: Path) -> Path:
        pass

    def exportar_ficha_ueps(self, produto_id: int, destino: Path) -> Path:
        pass
