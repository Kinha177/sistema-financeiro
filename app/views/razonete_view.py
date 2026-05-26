from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt


class _RazoneteCard(QFrame):
    """Representação visual em T de uma conta (placeholder)."""

    def __init__(self, conta_nome: str = "—") -> None:
        super().__init__()
        self.setObjectName("card")
        self.setMinimumSize(220, 160)

        ly = QVBoxLayout(self)
        ly.setSpacing(4)

        title = QLabel(conta_nome)
        title.setObjectName("cardTitle")
        title.setAlignment(Qt.AlignCenter)
        ly.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("sidebarSeparator")
        ly.addWidget(sep)

        cols = QWidget()
        cl = QHBoxLayout(cols)
        cl.setContentsMargins(0, 0, 0, 0)

        deb_lbl = QLabel("DÉBITO")
        deb_lbl.setObjectName("labelField")
        deb_lbl.setAlignment(Qt.AlignCenter)

        vsep = QFrame()
        vsep.setFrameShape(QFrame.VLine)
        vsep.setObjectName("sidebarSeparator")

        cred_lbl = QLabel("CRÉDITO")
        cred_lbl.setObjectName("labelField")
        cred_lbl.setAlignment(Qt.AlignCenter)

        cl.addWidget(deb_lbl)
        cl.addWidget(vsep)
        cl.addWidget(cred_lbl)
        ly.addWidget(cols)
        ly.addStretch()


class RazoneteView(QWidget):
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
        cl.addWidget(self._build_filter_bar())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        canvas = QWidget()
        canvas_ly = QHBoxLayout(canvas)
        canvas_ly.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        canvas_ly.setSpacing(16)

        # Placeholder cards
        for i in range(3):
            canvas_ly.addWidget(_RazoneteCard("Conta Exemplo"))
        canvas_ly.addStretch()

        scroll.setWidget(canvas)
        cl.addWidget(scroll)

        root.addWidget(content)

    def _build_header(self) -> QWidget:
        h = QWidget()
        h.setObjectName("pageHeader")
        ly = QVBoxLayout(h)
        ly.setAlignment(Qt.AlignVCenter)
        ly.addWidget(QLabel("Razonete", objectName="pageTitle"))
        ly.addWidget(QLabel("Representação em T das contas contábeis", objectName="pageSubtitle"))
        return h

    def _build_filter_bar(self) -> QWidget:
        bar = QWidget()
        ly = QHBoxLayout(bar)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(12)

        cb = QComboBox()
        cb.setPlaceholderText("Filtrar por grupo de contas...")
        cb.setMinimumWidth(240)
        ly.addWidget(cb)

        ly.addWidget(QPushButton("Gerar"))
        ly.addStretch()
        return bar
