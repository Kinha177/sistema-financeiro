from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QComboBox, QDateEdit,
)
from PySide6.QtCore import Qt, QDate


class LivroRazaoView(QWidget):
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
        cl.addWidget(self._build_filter_bar())
        cl.addWidget(self._build_table())

        root.addWidget(content)

    def _build_header(self) -> QWidget:
        h = QWidget()
        h.setObjectName("pageHeader")
        ly = QVBoxLayout(h)
        ly.setAlignment(Qt.AlignVCenter)
        ly.addWidget(QLabel("Livro Razão", objectName="pageTitle"))
        ly.addWidget(QLabel("Movimentações agrupadas por conta contábil", objectName="pageSubtitle"))
        return h

    def _build_filter_bar(self) -> QWidget:
        bar = QWidget()
        ly = QHBoxLayout(bar)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(12)

        conta_cb = QComboBox()
        conta_cb.setPlaceholderText("Selecione a conta...")
        conta_cb.setMinimumWidth(260)
        ly.addWidget(conta_cb)

        ly.addWidget(QLabel("De:"))
        date_from = QDateEdit(QDate.currentDate().addMonths(-1))
        date_from.setCalendarPopup(True)
        ly.addWidget(date_from)

        ly.addWidget(QLabel("Até:"))
        date_to = QDateEdit(QDate.currentDate())
        date_to.setCalendarPopup(True)
        ly.addWidget(date_to)

        btn = QPushButton("Filtrar")
        btn.setFixedWidth(90)
        ly.addWidget(btn)

        ly.addStretch()
        return bar

    def _build_table(self) -> QTableWidget:
        cols = ["Data", "Histórico", "Débito (R$)", "Crédito (R$)", "Saldo (R$)"]
        tbl = QTableWidget(0, len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectRows)
        return tbl
