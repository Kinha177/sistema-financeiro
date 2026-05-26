from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame,
)
from PySide6.QtCore import Qt


class _ReportCard(QWidget):
    def __init__(self, icon: str, title: str, description: str) -> None:
        super().__init__()
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)

        ly = QVBoxLayout(self)
        ly.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("emptyStateIcon")
        icon_lbl.setStyleSheet("font-size: 32px;")

        title_lbl = QLabel(title)
        title_lbl.setObjectName("cardTitle")

        desc_lbl = QLabel(description)
        desc_lbl.setObjectName("cardSubtext")
        desc_lbl.setWordWrap(True)

        btn = QPushButton("Gerar PDF")
        btn.setObjectName("btnSecondary")
        btn.setFixedWidth(110)

        ly.addWidget(icon_lbl)
        ly.addWidget(title_lbl)
        ly.addWidget(desc_lbl)
        ly.addStretch()
        ly.addWidget(btn)


class RelatoriosView(QWidget):
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
        cl.setSpacing(24)
        cl.addWidget(self._build_grid())
        cl.addStretch()

        root.addWidget(content)

    def _build_header(self) -> QWidget:
        h = QWidget()
        h.setObjectName("pageHeader")
        ly = QVBoxLayout(h)
        ly.setAlignment(Qt.AlignVCenter)
        ly.addWidget(QLabel("Relatórios PDF", objectName="pageTitle"))
        ly.addWidget(QLabel("Exportação de demonstrações contábeis e financeiras", objectName="pageSubtitle"))
        return h

    def _build_grid(self) -> QWidget:
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(16)

        reports = [
            ("📋", "Plano de Contas",        "Lista estruturada de todas as contas"),
            ("📖", "Livro Diário",            "Registro cronológico dos lançamentos"),
            ("📚", "Livro Razão",             "Movimentação por conta contábil"),
            ("⊕",  "Razonetes",              "Representação em T das contas"),
            ("📊", "DRE",                     "Demonstração do Resultado do Exercício"),
            ("⚖",  "Balanço Patrimonial",    "Posição patrimonial em data-base"),
            ("📦", "Relatório de Estoque",    "Posição atual dos produtos"),
            ("📄", "Ficha PEPS / UEPS",       "Custeio detalhado por produto"),
        ]

        for idx, (icon, title, desc) in enumerate(reports):
            row, col = divmod(idx, 4)
            grid.addWidget(_ReportCard(icon, title, desc), row, col)

        return container
