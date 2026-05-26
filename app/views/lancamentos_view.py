from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
)
from PySide6.QtCore import Qt


class LancamentosView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        content = QWidget()
        content.setObjectName("pageContent")
        cl = QVBoxLayout(content)
        cl.setSpacing(16)
        cl.addWidget(self._build_toolbar())
        cl.addWidget(self._build_table())

        root.addWidget(content)

    def _build_header(self) -> QWidget:
        h = QWidget()
        h.setObjectName("pageHeader")
        ly = QVBoxLayout(h)
        ly.setAlignment(Qt.AlignVCenter)
        ly.addWidget(QLabel("Lançamentos", objectName="pageTitle"))
        ly.addWidget(QLabel("Registro de partidas dobradas", objectName="pageSubtitle"))
        return h

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        ly = QHBoxLayout(bar)
        ly.setContentsMargins(0, 0, 0, 0)

        ly.addWidget(QPushButton("+ Novo Lançamento"))
        btn_del = QPushButton("Excluir")
        btn_del.setObjectName("btnDanger")
        ly.addWidget(btn_del)
        ly.addStretch()
        return bar

    def _build_table(self) -> QTableWidget:
        cols = ["Data", "Histórico", "Conta Débito", "Conta Crédito", "Valor", "N° Doc.", "Origem"]
        tbl = QTableWidget(0, len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectRows)
        return tbl
