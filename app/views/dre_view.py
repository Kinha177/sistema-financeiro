from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDateEdit,
)
from PySide6.QtCore import Qt, QDate


class DREView(QWidget):
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
        ly.addWidget(QLabel("DRE — Demonstração do Resultado do Exercício", objectName="pageTitle"))
        ly.addWidget(QLabel("Apuração do lucro ou prejuízo do período", objectName="pageSubtitle"))
        return h

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        ly = QHBoxLayout(bar)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(12)

        ly.addWidget(QLabel("Exercício de:"))
        date_from = QDateEdit(QDate(QDate.currentDate().year(), 1, 1))
        date_from.setCalendarPopup(True)
        ly.addWidget(date_from)

        ly.addWidget(QLabel("até:"))
        date_to = QDateEdit(QDate(QDate.currentDate().year(), 12, 31))
        date_to.setCalendarPopup(True)
        ly.addWidget(date_to)

        ly.addWidget(QPushButton("Gerar DRE"))

        btn_pdf = QPushButton("Exportar PDF")
        btn_pdf.setObjectName("btnSecondary")
        ly.addWidget(btn_pdf)

        ly.addStretch()
        return bar

    def _build_table(self) -> QTableWidget:
        cols = ["Código", "Descrição", "Valor (R$)"]
        rows = [
            "Receita Bruta de Vendas",
            "(-) Deduções",
            "= Receita Líquida",
            "(-) Custo das Mercadorias",
            "= Lucro Bruto",
            "(-) Despesas Operacionais",
            "= Resultado Operacional",
            "(-) IR / CSLL",
            "= Lucro / Prejuízo Líquido",
        ]

        tbl = QTableWidget(len(rows), len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)

        for i, row_text in enumerate(rows):
            tbl.setItem(i, 1, QTableWidgetItem(row_text))
            tbl.setItem(i, 2, QTableWidgetItem("—"))

        return tbl
