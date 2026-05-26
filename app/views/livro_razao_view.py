from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QDateEdit,
    QLabel, QHeaderView, QLineEdit,
)
from PySide6.QtCore import Qt, QDate

from app.views.components.page_header import PageHeader


class LivroRazaoView(QWidget):

    _COLS = ["Data", "Histórico", "Débito (R$)", "Crédito (R$)", "Saldo (R$)"]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    # ── montagem ──────────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = PageHeader(
            "Livro Razão",
            "Movimentações por conta contábil com saldo progressivo",
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
        cl.addWidget(self._build_table(), 1)
        cl.addWidget(self._build_totals_bar())

        root.addWidget(content)

    def _build_filter_card(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        outer = QVBoxLayout(card)
        outer.setContentsMargins(18, 14, 18, 14)
        outer.setSpacing(10)

        # ── linha 1: conta + período + botão ──────────────────────────────────
        row1 = QWidget()
        ly = QHBoxLayout(row1)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(10)

        lbl_conta = QLabel("CONTA")
        lbl_conta.setObjectName("labelField")
        ly.addWidget(lbl_conta)

        self._combo_conta = QComboBox()
        self._combo_conta.setPlaceholderText("Selecione a conta…")
        self._combo_conta.setMinimumWidth(280)
        ly.addWidget(self._combo_conta)

        sep = QWidget()
        sep.setFixedWidth(12)
        ly.addWidget(sep)

        lbl_de = QLabel("De:")
        lbl_de.setObjectName("labelField")
        ly.addWidget(lbl_de)

        self._date_from = QDateEdit(QDate.currentDate().addMonths(-1))
        self._date_from.setCalendarPopup(True)
        self._date_from.setFixedWidth(130)
        ly.addWidget(self._date_from)

        lbl_ate = QLabel("Até:")
        lbl_ate.setObjectName("labelField")
        ly.addWidget(lbl_ate)

        self._date_to = QDateEdit(QDate.currentDate())
        self._date_to.setCalendarPopup(True)
        self._date_to.setFixedWidth(130)
        ly.addWidget(self._date_to)

        ly.addStretch()

        self._btn_consultar = QPushButton("Consultar")
        self._btn_consultar.setFixedWidth(100)
        ly.addWidget(self._btn_consultar)

        outer.addWidget(row1)

        # ── linha 2: pesquisa ─────────────────────────────────────────────────
        self._edit_pesquisa = QLineEdit()
        self._edit_pesquisa.setPlaceholderText("Pesquisar no histórico…")
        self._edit_pesquisa.setClearButtonEnabled(True)
        outer.addWidget(self._edit_pesquisa)

        return card

    def _build_table(self) -> QTableWidget:
        self._table = QTableWidget(0, len(self._COLS))
        self._table.setHorizontalHeaderLabels(self._COLS)

        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in (2, 3, 4):
            hdr.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self._table.setColumnWidth(col, 140)

        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setSortingEnabled(True)

        return self._table

    def _build_totals_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("card")
        ly = QHBoxLayout(bar)
        ly.setContentsMargins(18, 12, 18, 12)
        ly.setSpacing(0)

        titulo = QLabel("TOTAIS")
        titulo.setObjectName("cardTitle")
        ly.addWidget(titulo)

        ly.addStretch()

        self._lbl_total_debito  = self.__total_lbl("Débito",  "#60a5fa")
        self._lbl_total_credito = self.__total_lbl("Crédito", "#f87171")
        self._lbl_saldo_final   = self.__total_lbl("Saldo",   "#a78bfa")

        for w in (self._lbl_total_debito, self._lbl_total_credito, self._lbl_saldo_final):
            ly.addWidget(w)

        return bar

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def __total_lbl(label: str, color: str) -> QLabel:
        lbl = QLabel(f"{label}:  R$ 0,00")
        lbl.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: 700;"
            f" padding: 0 24px 0 0; background: transparent;"
        )
        return lbl

    @staticmethod
    def _number_item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return item
