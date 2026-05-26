from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTabWidget,
)
from PySide6.QtCore import Qt


class EstoqueView(QWidget):
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

        tabs = QTabWidget()
        tabs.addTab(self._build_produtos_tab(), "Produtos")
        tabs.addTab(self._build_movimentos_tab(), "Movimentações")
        tabs.addTab(self._build_peps_tab(), "PEPS")
        tabs.addTab(self._build_ueps_tab(), "UEPS")
        cl.addWidget(tabs)

        root.addWidget(content)

    def _build_header(self) -> QWidget:
        h = QWidget()
        h.setObjectName("pageHeader")
        ly = QVBoxLayout(h)
        ly.setAlignment(Qt.AlignVCenter)
        ly.addWidget(QLabel("Controle de Estoque", objectName="pageTitle"))
        ly.addWidget(QLabel("Gerenciamento de produtos — PEPS e UEPS", objectName="pageSubtitle"))
        return h

    def _build_produtos_tab(self) -> QWidget:
        tab = QWidget()
        ly = QVBoxLayout(tab)
        ly.setContentsMargins(0, 12, 0, 0)
        ly.setSpacing(12)

        bar = QWidget()
        bly = QHBoxLayout(bar)
        bly.setContentsMargins(0, 0, 0, 0)
        bly.addWidget(QPushButton("+ Novo Produto"))
        bly.addStretch()
        ly.addWidget(bar)

        cols = ["Código", "Nome", "Unidade", "Qtd. Atual", "Custo Médio", "Vlr. Total", "Estoque Mín."]
        tbl = QTableWidget(0, len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        ly.addWidget(tbl)
        return tab

    def _build_movimentos_tab(self) -> QWidget:
        tab = QWidget()
        ly = QVBoxLayout(tab)
        ly.setContentsMargins(0, 12, 0, 0)
        ly.setSpacing(12)

        bar = QWidget()
        bly = QHBoxLayout(bar)
        bly.setContentsMargins(0, 0, 0, 0)
        bly.addWidget(QPushButton("+ Registrar Entrada"))

        btn_saida = QPushButton("+ Registrar Saída")
        btn_saida.setObjectName("btnSecondary")
        bly.addWidget(btn_saida)
        bly.addStretch()
        ly.addWidget(bar)

        cols = ["Data", "Produto", "Tipo", "Quantidade", "Vlr. Unitário", "Método", "N° Doc."]
        tbl = QTableWidget(0, len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        ly.addWidget(tbl)
        return tab

    def _build_peps_tab(self) -> QWidget:
        return self._build_custeio_placeholder("PEPS — Primeiro que Entra, Primeiro que Sai")

    def _build_ueps_tab(self) -> QWidget:
        return self._build_custeio_placeholder("UEPS — Último que Entra, Primeiro que Sai")

    def _build_custeio_placeholder(self, titulo: str) -> QWidget:
        tab = QWidget()
        ly = QVBoxLayout(tab)
        ly.setContentsMargins(0, 12, 0, 0)
        ly.setAlignment(Qt.AlignTop)

        lbl = QLabel(titulo)
        lbl.setObjectName("emptyStateText")
        ly.addWidget(lbl)

        cols = ["Data", "Entrada Qtd.", "Entrada R$", "Saída Qtd.", "Saída R$", "Saldo Qtd.", "Saldo R$"]
        tbl = QTableWidget(0, len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        ly.addWidget(tbl)
        return tab
