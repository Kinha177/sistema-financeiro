from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QTableWidget,
    QHeaderView, QSizePolicy,
)
from PySide6.QtCore import Qt

from app.views.components.page_header import PageHeader
from app.views.components.stat_card import StatCard
from app.views.components.empty_state import EmptyState


# ── Quick Action Card ─────────────────────────────────────────────────────────

class _QuickActionCard(QWidget):
    def __init__(self, icon: str, title: str, desc: str, accent: str = "#a78bfa") -> None:
        super().__init__()
        self.setObjectName("quickActionCard")
        self.setCursor(Qt.PointingHandCursor)

        ly = QHBoxLayout(self)
        ly.setContentsMargins(16, 14, 16, 14)
        ly.setSpacing(14)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            f"background:{accent}25; border-radius:9px; font-size:17px;"
        )
        ly.addWidget(icon_lbl)

        text_area = QWidget()
        text_ly = QVBoxLayout(text_area)
        text_ly.setContentsMargins(0, 0, 0, 0)
        text_ly.setSpacing(2)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("quickActionTitle")

        desc_lbl = QLabel(desc)
        desc_lbl.setObjectName("quickActionDesc")

        text_ly.addWidget(title_lbl)
        text_ly.addWidget(desc_lbl)
        ly.addWidget(text_area, 1)

        arrow = QLabel("›")
        arrow.setObjectName("quickActionArrow")
        ly.addWidget(arrow)


# ── Dashboard View ────────────────────────────────────────────────────────────

class DashboardView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = PageHeader("Dashboard", "Visão geral do sistema financeiro")
        root.addWidget(header)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("pageContent")
        content_ly = QVBoxLayout(content)
        content_ly.setSpacing(24)
        content_ly.setContentsMargins(28, 24, 28, 28)

        content_ly.addWidget(self._build_stat_row())
        content_ly.addWidget(self._build_middle_row())
        content_ly.addWidget(self._build_chart_placeholder())
        content_ly.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll)

    # ── sections ──────────────────────────────────────────────────────────

    def _build_stat_row(self) -> QWidget:
        row = QWidget()
        ly = QHBoxLayout(row)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(16)

        cards = [
            ("📈", "Receitas",     "R$ 0,00", "Este mês",           "#34d399"),
            ("📉", "Despesas",     "R$ 0,00", "Este mês",           "#f87171"),
            ("💰", "Resultado",    "R$ 0,00", "Lucro / Prejuízo",   "#a78bfa"),
            ("📦", "Em Estoque",   "0",        "Produtos ativos",    "#60a5fa"),
        ]
        for icon, title, value, sub, color in cards:
            card = StatCard(icon, title, value, sub, color)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            ly.addWidget(card)

        return row

    def _build_middle_row(self) -> QWidget:
        row = QWidget()
        ly = QHBoxLayout(row)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(16)

        ly.addWidget(self._build_recent_activity(), 3)
        ly.addWidget(self._build_quick_actions(), 2)
        return row

    def _build_recent_activity(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        ly = QVBoxLayout(card)
        ly.setSpacing(14)

        # Cabeçalho do card
        header_row = QHBoxLayout()
        title = QLabel("Atividade Recente")
        title.setObjectName("cardSectionTitle")
        header_row.addWidget(title)
        header_row.addStretch()
        see_all = QPushButton("Ver tudo")
        see_all.setObjectName("btnLink")
        header_row.addWidget(see_all)
        ly.addLayout(header_row)

        # Tabela de lançamentos recentes
        cols = ["Data", "Histórico", "Conta Déb.", "Conta Cred.", "Valor"]
        tbl = QTableWidget(0, len(cols))
        tbl.setObjectName("activityTable")
        tbl.setHorizontalHeaderLabels(cols)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectRows)
        tbl.setMinimumHeight(220)
        tbl.verticalHeader().setVisible(False)
        ly.addWidget(tbl)

        return card

    def _build_quick_actions(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        ly = QVBoxLayout(card)
        ly.setSpacing(10)

        title = QLabel("Ações Rápidas")
        title.setObjectName("cardSectionTitle")
        ly.addWidget(title)

        actions = [
            ("📝", "Novo Lançamento",    "Registrar partida dobrada",   "#a78bfa"),
            ("📋", "Nova Conta",         "Adicionar ao plano de contas", "#60a5fa"),
            ("📦", "Entrada de Estoque", "Registrar recebimento",        "#34d399"),
            ("📈", "Gerar DRE",          "Apurar resultado do período",  "#f59e0b"),
            ("📄", "Exportar Relatório", "Gerar PDF dos relatórios",      "#f87171"),
        ]
        for icon, title_text, desc, accent in actions:
            ly.addWidget(_QuickActionCard(icon, title_text, desc, accent))

        ly.addStretch()
        return card

    def _build_chart_placeholder(self) -> EmptyState:
        placeholder = EmptyState(
            "📊",
            "Gráfico de Desempenho",
            "Adicione lançamentos contábeis para visualizar\n"
            "o desempenho financeiro ao longo do tempo.",
        )
        placeholder.setMinimumHeight(180)
        return placeholder
