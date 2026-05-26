from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QLineEdit, QDateEdit, QLabel,
)
from PySide6.QtCore import Qt, QDate

from app.views.components.page_header import PageHeader


class LancamentosView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = PageHeader("Lançamentos Contábeis", "Registro de partidas dobradas")
        btn_new = QPushButton("+ Novo Lançamento")
        btn_new.setFixedWidth(155)
        header.add_action(btn_new)
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

        ly.addWidget(QLabel("De:"))
        date_from = QDateEdit(QDate.currentDate().addMonths(-1))
        date_from.setCalendarPopup(True)
        date_from.setFixedWidth(130)
        ly.addWidget(date_from)

        ly.addWidget(QLabel("Até:"))
        date_to = QDateEdit(QDate.currentDate())
        date_to.setCalendarPopup(True)
        date_to.setFixedWidth(130)
        ly.addWidget(date_to)

        search = QLineEdit()
        search.setPlaceholderText("Filtrar por histórico…")
        search.setMaximumWidth(260)
        ly.addWidget(search)

        btn_filter = QPushButton("Filtrar")
        btn_filter.setFixedWidth(80)
        ly.addWidget(btn_filter)

        ly.addStretch()

        btn_del = QPushButton("Excluir Selecionado")
        btn_del.setObjectName("btnDanger")
        btn_del.setFixedWidth(160)
        ly.addWidget(btn_del)

        return bar

    def _build_table(self) -> QTableWidget:
        cols = ["Data", "Histórico", "Conta Débito", "Conta Crédito", "Valor", "N° Doc."]
        tbl = QTableWidget(0, len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectRows)
        tbl.verticalHeader().setVisible(False)
        return tbl
