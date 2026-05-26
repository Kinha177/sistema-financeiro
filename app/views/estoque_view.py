from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTabWidget, QLineEdit, QHeaderView,
)
from PySide6.QtCore import Qt

from app.views.components.page_header import PageHeader


class EstoqueView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = PageHeader("Controle de Estoque", "Gerenciamento de produtos — PEPS e UEPS")
        btn_entrada = QPushButton("+ Entrada")
        btn_entrada.setFixedWidth(100)
        btn_saida = QPushButton("+ Saída")
        btn_saida.setObjectName("btnSecondary")
        btn_saida.setFixedWidth(100)
        header.add_action(btn_entrada)
        header.add_action(btn_saida)
        root.addWidget(header)

        content = QWidget()
        content.setObjectName("pageContent")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 20, 28, 28)
        cl.setSpacing(0)

        tabs = QTabWidget()
        tabs.addTab(self._build_produtos_tab(),    "📦  Produtos")
        tabs.addTab(self._build_movimentos_tab(),  "🔄  Movimentações")
        tabs.addTab(self._build_custeio_tab("PEPS — Primeiro que Entra, Primeiro que Sai"), "📊  PEPS")
        tabs.addTab(self._build_custeio_tab("UEPS — Último que Entra, Primeiro que Sai"),  "📊  UEPS")
        cl.addWidget(tabs)

        root.addWidget(content)

    # ── abas ──────────────────────────────────────────────────────────────

    def _build_produtos_tab(self) -> QWidget:
        tab = QWidget()
        ly = QVBoxLayout(tab)
        ly.setContentsMargins(0, 14, 0, 0)
        ly.setSpacing(12)

        bar = QWidget()
        bar_ly = QHBoxLayout(bar)
        bar_ly.setContentsMargins(0, 0, 0, 0)
        bar_ly.setSpacing(10)

        btn = QPushButton("+ Novo Produto")
        btn.setFixedWidth(140)
        bar_ly.addWidget(btn)

        search = QLineEdit()
        search.setPlaceholderText("Buscar produto…")
        search.setMaximumWidth(280)
        bar_ly.addWidget(search)
        bar_ly.addStretch()
        ly.addWidget(bar)

        cols = ["Nome", "Estoque Atual", "Ações"]
        tbl = QTableWidget(0, len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.verticalHeader().setVisible(False)
        ly.addWidget(tbl)
        return tab

    def _build_movimentos_tab(self) -> QWidget:
        tab = QWidget()
        ly = QVBoxLayout(tab)
        ly.setContentsMargins(0, 14, 0, 0)
        ly.setSpacing(12)

        cols = ["Data", "Produto", "Tipo", "Quantidade", "Valor Unit.", "Total"]
        tbl = QTableWidget(0, len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.verticalHeader().setVisible(False)
        ly.addWidget(tbl)
        return tab

    def _build_custeio_tab(self, titulo: str) -> QWidget:
        tab = QWidget()
        ly = QVBoxLayout(tab)
        ly.setContentsMargins(0, 14, 0, 0)
        ly.setSpacing(12)

        cols = ["Data", "Qtd. Entrada", "Vlr. Entrada", "Qtd. Saída", "Vlr. Saída", "Saldo Qtd.", "Saldo R$"]
        tbl = QTableWidget(0, len(cols))
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.verticalHeader().setVisible(False)
        ly.addWidget(tbl)
        return tab
