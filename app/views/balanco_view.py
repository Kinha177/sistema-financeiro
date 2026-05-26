from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDateEdit, QSplitter,
)
from PySide6.QtCore import Qt, QDate


class BalancoView(QWidget):
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

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._build_side("ATIVO"))
        splitter.addWidget(self._build_side("PASSIVO + PL"))
        cl.addWidget(splitter)

        root.addWidget(content)

    def _build_header(self) -> QWidget:
        h = QWidget()
        h.setObjectName("pageHeader")
        ly = QVBoxLayout(h)
        ly.setAlignment(Qt.AlignVCenter)
        ly.addWidget(QLabel("Balanço Patrimonial", objectName="pageTitle"))
        ly.addWidget(QLabel("Posição patrimonial e financeira em uma data-base", objectName="pageSubtitle"))
        return h

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        ly = QHBoxLayout(bar)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(12)

        ly.addWidget(QLabel("Data-base:"))
        date_edit = QDateEdit(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        ly.addWidget(date_edit)

        ly.addWidget(QPushButton("Gerar Balanço"))

        btn_pdf = QPushButton("Exportar PDF")
        btn_pdf.setObjectName("btnSecondary")
        ly.addWidget(btn_pdf)

        ly.addStretch()
        return bar

    def _build_side(self, label: str) -> QWidget:
        panel = QWidget()
        panel.setObjectName("card")
        ly = QVBoxLayout(panel)

        title = QLabel(label)
        title.setObjectName("cardTitle")
        ly.addWidget(title)

        cols = ["Descrição", "Valor (R$)"]
        tbl = QTableWidget(0, len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        ly.addWidget(tbl)

        total = QLabel("TOTAL:  R$ 0,00")
        total.setObjectName("cardValue")
        total.setAlignment(Qt.AlignRight)
        ly.addWidget(total)

        return panel
