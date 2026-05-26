from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QDateEdit, QLabel, QHeaderView,
)
from PySide6.QtCore import Qt, QDate

from app.views.components.page_header import PageHeader


class LivroDiarioView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = PageHeader("Livro Diário", "Registro cronológico de todos os lançamentos")
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

        cl.addWidget(self._build_filter_bar())
        cl.addWidget(self._build_table())

        root.addWidget(content)

    def _build_filter_bar(self) -> QWidget:
        bar = QWidget()
        ly = QHBoxLayout(bar)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(10)

        ly.addWidget(QLabel("Período:"))

        date_from = QDateEdit(QDate.currentDate().addMonths(-1))
        date_from.setCalendarPopup(True)
        date_from.setFixedWidth(130)
        ly.addWidget(date_from)

        ly.addWidget(QLabel("até"))

        date_to = QDateEdit(QDate.currentDate())
        date_to.setCalendarPopup(True)
        date_to.setFixedWidth(130)
        ly.addWidget(date_to)

        btn = QPushButton("Filtrar")
        btn.setFixedWidth(80)
        ly.addWidget(btn)

        ly.addStretch()
        return bar

    def _build_table(self) -> QTableWidget:
        cols = ["Data", "Lançamento N°", "Histórico", "Conta Débito", "Conta Crédito", "Valor (R$)"]
        tbl = QTableWidget(0, len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectRows)
        tbl.verticalHeader().setVisible(False)
        return tbl
