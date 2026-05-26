from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QLabel,
    QDateEdit, QHeaderView,
)
from PySide6.QtCore import Qt, QDate

from app.views.components.page_header import PageHeader


class DreView(QWidget):

    _COLS = ["Código", "Conta / Grupo", "Valor (R$)"]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = PageHeader(
            "DRE",
            "Demonstração do Resultado do Exercício",
        )
        btn_pdf = QPushButton("Exportar PDF")
        btn_pdf.setObjectName("btnSecondary")
        btn_pdf.setFixedWidth(120)
        header.add_action(btn_pdf)
        root.addWidget(header)

        content = QWidget()
        content.setObjectName("pageContent")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 20, 28, 28)
        cl.setSpacing(14)

        cl.addWidget(self._build_filter_card())
        cl.addWidget(self._build_summary_row())
        cl.addWidget(self._build_table(), 1)

        root.addWidget(content)

    # ── montagem ──────────────────────────────────────────────────────────────

    def _build_filter_card(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        ly = QHBoxLayout(card)
        ly.setContentsMargins(18, 14, 18, 14)
        ly.setSpacing(10)

        lbl = QLabel("PERÍODO")
        lbl.setObjectName("labelField")
        ly.addWidget(lbl)

        lbl_de = QLabel("De:")
        lbl_de.setObjectName("labelField")
        ly.addWidget(lbl_de)

        self._date_from = QDateEdit(QDate(QDate.currentDate().year(), 1, 1))
        self._date_from.setCalendarPopup(True)
        self._date_from.setFixedWidth(130)
        ly.addWidget(self._date_from)

        lbl_ate = QLabel("Até:")
        lbl_ate.setObjectName("labelField")
        ly.addWidget(lbl_ate)

        self._date_to = QDateEdit(QDate(QDate.currentDate().year(), 12, 31))
        self._date_to.setCalendarPopup(True)
        self._date_to.setFixedWidth(130)
        ly.addWidget(self._date_to)

        ly.addStretch()

        self._btn_consultar = QPushButton("Gerar DRE")
        self._btn_consultar.setFixedWidth(110)
        ly.addWidget(self._btn_consultar)

        return card

    def _build_summary_row(self) -> QWidget:
        row = QWidget()
        ly = QHBoxLayout(row)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(12)

        metrics = [
            ("Receitas Operacionais", "#86efac", "_lbl_receitas"),
            ("(-) Custos",            "#f87171", "_lbl_custos"),
            ("(-) Despesas",          "#fbbf24", "_lbl_despesas"),
            ("Lucro Líquido",         "#a78bfa", "_lbl_lucro"),
        ]
        for titulo, cor, attr in metrics:
            card, lbl = self._build_metric_card(titulo, cor)
            setattr(self, attr, lbl)
            ly.addWidget(card, 1)

        return row

    def _build_metric_card(self, titulo: str, cor: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setObjectName("card")
        ly = QVBoxLayout(card)
        ly.setContentsMargins(16, 14, 16, 16)
        ly.setSpacing(6)

        lbl_titulo = QLabel(titulo.upper())
        lbl_titulo.setObjectName("cardTitle")

        lbl_valor = QLabel("R$ 0,00")
        lbl_valor.setStyleSheet(
            f"color: {cor}; font-size: 20px; font-weight: 700; background: transparent;"
        )

        ly.addWidget(lbl_titulo)
        ly.addWidget(lbl_valor)

        return card, lbl_valor

    def _build_table(self) -> QTableWidget:
        self._table = QTableWidget(0, len(self._COLS))
        self._table.setHorizontalHeaderLabels(self._COLS)

        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(2, 160)

        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setSortingEnabled(False)

        return self._table

    # ── helper estático ───────────────────────────────────────────────────────

    @staticmethod
    def _number_item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return item
