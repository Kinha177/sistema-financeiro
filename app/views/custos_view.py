from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QLabel,
    QComboBox, QSpinBox, QHeaderView, QSizePolicy,
)
from PySide6.QtCore import Qt

from app.views.components.page_header import PageHeader
from app.views.components.stat_card import StatCard


class CustosView(QWidget):

    _COLS = ["Lote", "Data", "Quantidade", "Valor Unitário (R$)", "Valor Total (R$)"]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = PageHeader(
            "Custeio de Estoque",
            "Análise detalhada de lotes consumidos — PEPS e UEPS",
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
        cl.setSpacing(16)

        cl.addWidget(self._build_filter_card())
        cl.addWidget(self._build_summary_row())
        cl.addWidget(self._build_table(), 1)

        root.addWidget(content)

    # ── seções ────────────────────────────────────────────────────────────────

    def _build_filter_card(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        ly = QHBoxLayout(card)
        ly.setContentsMargins(18, 14, 18, 14)
        ly.setSpacing(12)

        lbl_metodo = QLabel("MÉTODO")
        lbl_metodo.setObjectName("labelField")
        ly.addWidget(lbl_metodo)

        self._combo_metodo = QComboBox()
        self._combo_metodo.addItems(["PEPS — Primeiro a Entrar, Primeiro a Sair",
                                     "UEPS — Último a Entrar, Primeiro a Sair"])
        self._combo_metodo.setFixedWidth(320)
        ly.addWidget(self._combo_metodo)

        lbl_produto = QLabel("PRODUTO")
        lbl_produto.setObjectName("labelField")
        ly.addWidget(lbl_produto)

        self._combo_produto = QComboBox()
        self._combo_produto.setPlaceholderText("Selecione um produto…")
        self._combo_produto.setFixedWidth(220)
        ly.addWidget(self._combo_produto)

        lbl_qty = QLabel("QTDE SAÍDA")
        lbl_qty.setObjectName("labelField")
        ly.addWidget(lbl_qty)

        self._spin_quantidade = QSpinBox()
        self._spin_quantidade.setMinimum(1)
        self._spin_quantidade.setMaximum(999_999)
        self._spin_quantidade.setValue(1)
        self._spin_quantidade.setFixedWidth(90)
        ly.addWidget(self._spin_quantidade)

        ly.addStretch()

        self._btn_calcular = QPushButton("Calcular")
        self._btn_calcular.setFixedWidth(100)
        ly.addWidget(self._btn_calcular)

        return card

    def _build_summary_row(self) -> QWidget:
        row = QWidget()
        ly = QHBoxLayout(row)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(14)

        self._card_metodo = StatCard("📋", "Método Utilizado", "—",         "Aguardando cálculo",  "#a78bfa")
        self._card_lotes  = StatCard("📦", "Lotes Consumidos", "0",          "Partidas alocadas",   "#60a5fa")
        self._card_qtd    = StatCard("🔢", "Qtde Total",        "0",          "Unidades alocadas",   "#34d399")
        self._card_total  = StatCard("💰", "Custo Total",       "R$ 0,00",   "Valor dos lotes",     "#f59e0b")

        for card in (self._card_metodo, self._card_lotes, self._card_qtd, self._card_total):
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            ly.addWidget(card)

        return row

    def _build_table(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(18, 14, 18, 18)
        fl.setSpacing(12)

        header_row = QHBoxLayout()
        title = QLabel("Lotes Consumidos")
        title.setObjectName("cardSectionTitle")
        header_row.addWidget(title)
        header_row.addStretch()

        self._lbl_metodo_badge = QLabel("—")
        self._lbl_metodo_badge.setObjectName("badgeNeutral")
        self._lbl_metodo_badge.setStyleSheet(
            "background:#a78bfa22; color:#a78bfa; border-radius:8px;"
            " padding:3px 10px; font-weight:600; font-size:12px;"
        )
        header_row.addWidget(self._lbl_metodo_badge)
        fl.addLayout(header_row)

        self._table = QTableWidget(0, len(self._COLS))
        self._table.setHorizontalHeaderLabels(self._COLS)

        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self._table.setColumnWidth(2, 120)
        self._table.setColumnWidth(3, 170)

        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setMinimumHeight(260)
        fl.addWidget(self._table)

        # rodapé com totalizador
        footer = QHBoxLayout()
        footer.addStretch()
        self._lbl_total_footer = QLabel("Total: R$ 0,00")
        self._lbl_total_footer.setStyleSheet(
            "color:#f59e0b; font-size:15px; font-weight:700; background:transparent;"
        )
        footer.addWidget(self._lbl_total_footer)
        fl.addLayout(footer)

        return frame

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _number_item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return item
