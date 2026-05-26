from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QLabel,
    QDateEdit, QHeaderView, QSplitter,
)
from PySide6.QtCore import Qt, QDate

from app.views.components.page_header import PageHeader


class BalancoView(QWidget):

    _COLS = ["Código", "Conta", "Valor (R$)"]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = PageHeader(
            "Balanço Patrimonial",
            "Posição patrimonial e financeira na data-base",
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
        cl.addWidget(self._build_main_panels(), 1)

        root.addWidget(content)

    # ── montagem ──────────────────────────────────────────────────────────────

    def _build_filter_card(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        ly = QHBoxLayout(card)
        ly.setContentsMargins(18, 14, 18, 14)
        ly.setSpacing(10)

        lbl = QLabel("DATA-BASE")
        lbl.setObjectName("labelField")
        ly.addWidget(lbl)

        self._date_base = QDateEdit(QDate(QDate.currentDate().year(), 12, 31))
        self._date_base.setCalendarPopup(True)
        self._date_base.setFixedWidth(130)
        ly.addWidget(self._date_base)

        ly.addStretch()

        self._lbl_equacao = QLabel("")
        self._lbl_equacao.setVisible(False)
        ly.addWidget(self._lbl_equacao)

        self._btn_consultar = QPushButton("Gerar Balanço")
        self._btn_consultar.setFixedWidth(120)
        ly.addWidget(self._btn_consultar)

        return card

    def _build_summary_row(self) -> QWidget:
        row = QWidget()
        ly = QHBoxLayout(row)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(12)

        metrics = [
            ("Ativo Total",        "#34d399", "_lbl_ativo"),
            ("Passivo Total",      "#f87171", "_lbl_passivo"),
            ("Patrimônio Líquido", "#a78bfa", "_lbl_pl"),
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

    def _build_main_panels(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_ativo_panel())
        splitter.addWidget(self._build_passivo_pl_panel())
        splitter.setSizes([500, 500])
        return splitter

    def _build_ativo_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("card")
        ly = QVBoxLayout(panel)
        ly.setContentsMargins(16, 14, 16, 16)
        ly.setSpacing(10)

        lbl = QLabel("ATIVO")
        lbl.setStyleSheet(
            "color: #34d399; font-size: 13px; font-weight: 700; background: transparent;"
        )
        ly.addWidget(lbl)

        self._table_ativo = self._make_table()
        ly.addWidget(self._table_ativo, 1)

        ly.addWidget(self._build_total_row("TOTAL ATIVO", "#34d399", "_lbl_total_ativo"))

        return panel

    def _build_passivo_pl_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("card")
        ly = QVBoxLayout(panel)
        ly.setContentsMargins(16, 14, 16, 16)
        ly.setSpacing(10)

        lbl_passivo = QLabel("PASSIVO")
        lbl_passivo.setStyleSheet(
            "color: #f87171; font-size: 13px; font-weight: 700; background: transparent;"
        )
        ly.addWidget(lbl_passivo)

        self._table_passivo = self._make_table()
        ly.addWidget(self._table_passivo, 1)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #1a1a30; color: #1a1a30;")
        ly.addWidget(sep)

        lbl_pl = QLabel("PATRIMÔNIO LÍQUIDO")
        lbl_pl.setStyleSheet(
            "color: #a78bfa; font-size: 13px; font-weight: 700; background: transparent;"
        )
        ly.addWidget(lbl_pl)

        self._table_pl = self._make_table()
        ly.addWidget(self._table_pl, 1)

        ly.addWidget(
            self._build_total_row("TOTAL PASSIVO + PL", "#f87171", "_lbl_total_passivo_pl")
        )

        return panel

    def _build_total_row(self, label: str, cor: str, attr: str) -> QWidget:
        row = QWidget()
        ly = QHBoxLayout(row)
        ly.setContentsMargins(0, 4, 0, 0)
        ly.setSpacing(8)
        ly.addStretch()

        lbl_t = QLabel(label)
        lbl_t.setObjectName("labelField")
        ly.addWidget(lbl_t)

        lbl_val = QLabel("R$ 0,00")
        lbl_val.setStyleSheet(
            f"color: {cor}; font-size: 15px; font-weight: 700; background: transparent;"
        )
        setattr(self, attr, lbl_val)
        ly.addWidget(lbl_val)

        return row

    def _make_table(self) -> QTableWidget:
        table = QTableWidget(0, len(self._COLS))
        table.setHorizontalHeaderLabels(self._COLS)

        hdr = table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(2, 140)

        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setSortingEnabled(False)

        return table

    # ── helper estático ───────────────────────────────────────────────────────

    @staticmethod
    def _number_item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return item
