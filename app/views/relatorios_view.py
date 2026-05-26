from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt

from app.views.components.page_header import PageHeader


class _ReportCard(QWidget):
    def __init__(self, icon: str, title: str, description: str, accent: str = "#a78bfa") -> None:
        super().__init__()
        self.setObjectName("reportCard")

        ly = QVBoxLayout(self)
        ly.setContentsMargins(20, 18, 20, 18)
        ly.setSpacing(10)

        # ícone
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(44, 44)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            f"background:{accent}20; border-radius:12px; font-size:22px;"
        )
        ly.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("reportCardTitle")
        ly.addWidget(title_lbl)

        desc_lbl = QLabel(description)
        desc_lbl.setObjectName("cardSubtext")
        desc_lbl.setWordWrap(True)
        ly.addWidget(desc_lbl)

        ly.addStretch()

        btn = QPushButton("Gerar PDF")
        btn.setObjectName("btnSecondary")
        btn.setFixedWidth(100)
        btn.setCursor(Qt.PointingHandCursor)
        ly.addWidget(btn)


class RelatoriosView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = PageHeader(
            "Relatórios",
            "Exportação de demonstrações contábeis e financeiras em PDF",
        )
        root.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("pageContent")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 24, 28, 28)
        cl.setSpacing(16)

        cl.addWidget(self._build_grid())
        cl.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll)

    def _build_grid(self) -> QWidget:
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(16)

        reports = [
            ("📋", "Plano de Contas",      "Lista estruturada de todas as contas",       "#a78bfa"),
            ("📓", "Livro Diário",          "Registro cronológico dos lançamentos",        "#60a5fa"),
            ("📒", "Livro Razão",           "Movimentação por conta contábil",             "#34d399"),
            ("🔢", "Razonetes",             "Representação em T das contas",               "#f59e0b"),
            ("📈", "DRE",                   "Demonstração do Resultado do Exercício",      "#a78bfa"),
            ("⚖",  "Balanço Patrimonial",  "Posição patrimonial em data-base",            "#60a5fa"),
            ("📦", "Relatório de Estoque",  "Posição atual e valoração dos produtos",      "#34d399"),
            ("📄", "Ficha PEPS / UEPS",     "Custeio detalhado por produto",               "#f87171"),
        ]

        for idx, (icon, title, desc, accent) in enumerate(reports):
            row, col = divmod(idx, 4)
            grid.addWidget(_ReportCard(icon, title, desc, accent), row, col)

        return container
