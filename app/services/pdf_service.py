from __future__ import annotations
from pathlib import Path
from datetime import date


class PDFService:
    """Geração de relatórios em PDF via ReportLab."""

    def __init__(self, empresa_nome: str = "Empresa") -> None:
        self.empresa_nome = empresa_nome

    def gerar_plano_contas(self, dados: list[dict], destino: Path) -> Path:
        pass

    def gerar_livro_diario(self, dados: list[dict], data_inicio: date, data_fim: date, destino: Path) -> Path:
        pass

    def gerar_livro_razao(self, dados: list[dict], conta_nome: str, destino: Path) -> Path:
        pass

    def gerar_razonetes(self, dados: list[dict], destino: Path) -> Path:
        pass

    def gerar_dre(self, dados: dict, data_inicio: date, data_fim: date, destino: Path) -> Path:
        pass

    def gerar_balanco(self, dados: dict, data_base: date, destino: Path) -> Path:
        pass

    def gerar_relatorio_estoque(self, dados: list[dict], destino: Path) -> Path:
        pass

    def gerar_ficha_peps_ueps(self, dados: list[dict], produto_nome: str, metodo: str, destino: Path) -> Path:
        pass

    def _cabecalho(self, canvas, doc) -> None:
        pass

    def _rodape(self, canvas, doc) -> None:
        pass
