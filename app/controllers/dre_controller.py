from __future__ import annotations
from decimal import Decimal

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem

from app.database.connection import get_session
from app.services.dre_service import DreService
from app.views.dre_view import DreView


def _fmt(valor: Decimal) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


_SECOES = [
    ("RECEITAS OPERACIONAIS", "receitas",  "total_receitas",  "#86efac", "Total Receitas"),
    ("(-) CUSTOS",            "custos",    "total_custos",    "#f87171", "Total Custos"),
    ("(-) DESPESAS",          "despesas",  "total_despesas",  "#fbbf24", "Total Despesas"),
]


class DreController:
    """Conecta DreView ao DreService."""

    def __init__(self, view: DreView) -> None:
        self._view = view

        view._btn_consultar.clicked.connect(self._consultar)
        view._date_from.dateChanged.connect(self._consultar)
        view._date_to.dateChanged.connect(self._consultar)

        QTimer.singleShot(0, self._consultar)

    # ── consulta (DB) ─────────────────────────────────────────────────────────

    def _consultar(self, _=None) -> None:
        try:
            d_from = self._view._date_from.date().toPython()
            d_to   = self._view._date_to.date().toPython()
            session = get_session()
            try:
                dados = DreService(session).gerar_dre(
                    data_inicio=d_from,
                    data_fim=d_to,
                )
            finally:
                session.close()
            self._preencher(dados)
        except Exception as exc:
            QMessageBox.critical(self._view, "Erro", str(exc))

    # ── preenchimento ─────────────────────────────────────────────────────────

    def _preencher(self, dados: dict) -> None:
        self._atualizar_cards(dados)
        self._preencher_tabela(dados)

    def _atualizar_cards(self, dados: dict) -> None:
        self._view._lbl_receitas.setText(f"R$ {_fmt(dados['total_receitas'])}")
        self._view._lbl_custos.setText(f"R$ {_fmt(dados['total_custos'])}")
        self._view._lbl_despesas.setText(f"R$ {_fmt(dados['total_despesas'])}")

        lucro = dados["lucro_liquido"]
        self._view._lbl_lucro.setText(f"R$ {_fmt(lucro)}")
        cor = "#f87171" if lucro < 0 else "#86efac" if lucro > 0 else "#a78bfa"
        self._view._lbl_lucro.setStyleSheet(
            f"color: {cor}; font-size: 20px; font-weight: 700; background: transparent;"
        )

    def _preencher_tabela(self, dados: dict) -> None:
        table = self._view._table
        table.setRowCount(0)

        for titulo, chave_itens, chave_total, cor, lbl_total in _SECOES:
            self._inserir_header(table, titulo, cor)
            for item in dados[chave_itens]:
                self._inserir_item(table, item["codigo"], item["nome"], item["valor"], cor)
            self._inserir_subtotal(table, lbl_total, dados[chave_total], cor)

        lucro = dados["lucro_liquido"]
        cor_lucro = "#f87171" if lucro < 0 else "#86efac" if lucro > 0 else "#a78bfa"
        self._inserir_resultado(table, lucro, cor_lucro)

    # ── helpers de linha ──────────────────────────────────────────────────────

    def _inserir_header(self, table, titulo: str, cor: str) -> None:
        row = table.rowCount()
        table.insertRow(row)
        item = QTableWidgetItem(titulo)
        item.setForeground(QColor(cor))
        item.setFont(_bold_font())
        item.setBackground(QColor("#0b0b18"))
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        table.setItem(row, 0, item)
        table.setSpan(row, 0, 1, 3)

    def _inserir_item(self, table, codigo: str, nome: str, valor: Decimal, cor: str) -> None:
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(codigo))
        table.setItem(row, 1, QTableWidgetItem(nome))
        val_item = self._view._number_item(f"R$ {_fmt(valor)}")
        val_item.setForeground(QColor(cor))
        table.setItem(row, 2, val_item)

    def _inserir_subtotal(self, table, label: str, total: Decimal, cor: str) -> None:
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(""))

        lbl_item = QTableWidgetItem(label)
        lbl_item.setForeground(QColor(cor))
        lbl_item.setFont(_bold_font())
        table.setItem(row, 1, lbl_item)

        val_item = self._view._number_item(f"R$ {_fmt(total)}")
        val_item.setForeground(QColor(cor))
        val_item.setFont(_bold_font())
        table.setItem(row, 2, val_item)

    def _inserir_resultado(self, table, lucro: Decimal, cor: str) -> None:
        row = table.rowCount()
        table.insertRow(row)

        lbl = QTableWidgetItem("LUCRO LÍQUIDO")
        lbl.setForeground(QColor(cor))
        lbl.setFont(_bold_font(12))
        lbl.setBackground(QColor("#0b0b18"))
        lbl.setFlags(Qt.ItemFlag.ItemIsEnabled)
        table.setItem(row, 0, lbl)
        table.setSpan(row, 0, 1, 2)

        val_item = self._view._number_item(f"R$ {_fmt(lucro)}")
        val_item.setForeground(QColor(cor))
        val_item.setFont(_bold_font(12))
        val_item.setBackground(QColor("#0b0b18"))
        val_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        table.setItem(row, 2, val_item)


def _bold_font(size: int = 11) -> QFont:
    f = QFont()
    f.setBold(True)
    f.setPointSize(size)
    return f
