from __future__ import annotations
from decimal import Decimal

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMessageBox, QTableWidget, QTableWidgetItem

from app.database.connection import get_session
from app.services.balanco_service import BalancoService
from app.views.balanco_view import BalancoView


def _fmt(valor: Decimal) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class BalancoController:
    """Conecta BalancoView ao BalancoService."""

    def __init__(self, view: BalancoView) -> None:
        self._view = view

        view._btn_consultar.clicked.connect(self._consultar)
        view._date_base.dateChanged.connect(self._consultar)

        QTimer.singleShot(0, self._consultar)

    # ── consulta (DB) ─────────────────────────────────────────────────────────

    def _consultar(self, _=None) -> None:
        try:
            data_base = self._view._date_base.date().toPython()
            session = get_session()
            try:
                dados = BalancoService(session).gerar_balanco(data_base=data_base)
            finally:
                session.close()
            self._preencher(dados)
        except Exception as exc:
            QMessageBox.critical(self._view, "Erro", str(exc))

    # ── preenchimento ─────────────────────────────────────────────────────────

    def _preencher(self, dados: dict) -> None:
        self._atualizar_cards(dados)
        self._preencher_tabela(self._view._table_ativo,   dados["ativo"],   "#34d399")
        self._preencher_tabela(self._view._table_passivo, dados["passivo"], "#f87171")
        self._preencher_tabela(self._view._table_pl,      dados["pl"],      "#a78bfa")
        self._atualizar_totais(dados)
        self._atualizar_equacao(dados["equacao_valida"])

    def _atualizar_cards(self, dados: dict) -> None:
        self._view._lbl_ativo.setText(f"R$ {_fmt(dados['total_ativo'])}")
        self._view._lbl_passivo.setText(f"R$ {_fmt(dados['total_passivo'])}")
        self._view._lbl_pl.setText(f"R$ {_fmt(dados['total_pl'])}")

    def _preencher_tabela(
        self, table: QTableWidget, itens: list[dict], cor: str
    ) -> None:
        table.setRowCount(0)
        for row, item in enumerate(itens):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(item["codigo"]))
            table.setItem(row, 1, QTableWidgetItem(item["nome"]))
            val_item = self._view._number_item(f"R$ {_fmt(item['valor'])}")
            val_item.setForeground(QColor(cor))
            table.setItem(row, 2, val_item)

    def _atualizar_totais(self, dados: dict) -> None:
        self._view._lbl_total_ativo.setText(f"R$ {_fmt(dados['total_ativo'])}")
        self._view._lbl_total_passivo_pl.setText(f"R$ {_fmt(dados['total_passivo_pl'])}")

    def _atualizar_equacao(self, valida: bool) -> None:
        lbl = self._view._lbl_equacao
        if valida:
            lbl.setText("  Equação Patrimonial: VÁLIDA  ")
            lbl.setStyleSheet(
                "color: #86efac; font-size: 11px; font-weight: 700;"
                " background-color: #14532d; border-radius: 8px; padding: 3px 0;"
            )
        else:
            lbl.setText("  Equação Patrimonial: INVÁLIDA  ")
            lbl.setStyleSheet(
                "color: #f87171; font-size: 11px; font-weight: 700;"
                " background-color: #7f1d1d; border-radius: 8px; padding: 3px 0;"
            )
        lbl.setVisible(True)
