from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout,
)
from PySide6.QtCore import Qt


class _StatCard(QWidget):
    def __init__(self, title: str, value: str, subtext: str, accent: str = "#a78bfa") -> None:
        super().__init__()
        self.setObjectName("card")

        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("cardTitle")

        lbl_value = QLabel(value)
        lbl_value.setObjectName("cardValue")
        lbl_value.setStyleSheet(f"color: {accent};")

        lbl_sub = QLabel(subtext)
        lbl_sub.setObjectName("cardSubtext")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        layout.addWidget(lbl_sub)


class DashboardView(QWidget):
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
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(24)

        content_layout.addWidget(self._build_stat_row())
        content_layout.addWidget(self._build_placeholder_chart())
        content_layout.addStretch()

        root.addWidget(content)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("pageHeader")
        layout = QVBoxLayout(header)
        layout.setAlignment(Qt.AlignVCenter)

        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Visão geral do sistema financeiro")
        subtitle.setObjectName("pageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        return header

    def _build_stat_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        cards = [
            ("RECEITAS",          "R$ 0,00",  "Este mês",          "#34d399"),
            ("DESPESAS",          "R$ 0,00",  "Este mês",          "#f87171"),
            ("RESULTADO",         "R$ 0,00",  "Lucro / Prejuízo",  "#a78bfa"),
            ("ITENS EM ESTOQUE",  "0",        "Produtos cadastrados", "#60a5fa"),
        ]
        for title, value, sub, color in cards:
            layout.addWidget(_StatCard(title, value, sub, color))

        return row

    def _build_placeholder_chart(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        card.setMinimumHeight(200)

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("📊")
        icon.setObjectName("emptyStateIcon")
        icon.setAlignment(Qt.AlignCenter)

        text = QLabel("Gráficos serão exibidos aqui")
        text.setObjectName("emptyStateText")
        text.setAlignment(Qt.AlignCenter)

        sub = QLabel("Adicione lançamentos para visualizar o desempenho financeiro")
        sub.setObjectName("emptyStateSubtext")
        sub.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon)
        layout.addWidget(text)
        layout.addWidget(sub)
        return card
