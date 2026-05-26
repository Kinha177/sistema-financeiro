from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

_NAV_ITEMS: list[tuple[str, str, str]] = [
    # (chave, rótulo, grupo)
    ("dashboard",    "  Dashboard",           "VISÃO GERAL"),
    ("plano_contas", "  Plano de Contas",      "CONTABILIDADE"),
    ("lancamentos",  "  Lançamentos",          "CONTABILIDADE"),
    ("livro_diario", "  Livro Diário",         "CONTABILIDADE"),
    ("livro_razao",  "  Livro Razão",          "CONTABILIDADE"),
    ("razonete",     "  Razonete",             "CONTABILIDADE"),
    ("dre",          "  DRE",                  "RELATÓRIOS"),
    ("balanco",      "  Balanço Patrimonial",  "RELATÓRIOS"),
    ("estoque",      "  Estoque",              "OPERACIONAL"),
    ("relatorios",   "  Exportar PDF",         "OPERACIONAL"),
]


class Sidebar(QWidget):
    navigation_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._active_button: QPushButton | None = None
        self._buttons: dict[str, QPushButton] = {}
        self._setup_ui()

    # ── build ─────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(0)

        layout.addWidget(self._build_logo())
        layout.addWidget(self._build_separator())
        layout.addSpacing(8)

        current_group = ""
        for key, label, group in _NAV_ITEMS:
            if group != current_group:
                current_group = group
                layout.addSpacing(4)
                layout.addWidget(self._build_section_label(group))

            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _checked=False, k=key: self._navigate(k))
            layout.addWidget(btn)
            self._buttons[key] = btn

        layout.addStretch()
        layout.addWidget(self._build_version())

        self._navigate("dashboard")

    def _build_logo(self) -> QWidget:
        area = QWidget()
        area.setObjectName("logoArea")
        area.setFixedHeight(72)

        inner = QVBoxLayout(area)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(2)
        inner.setAlignment(Qt.AlignCenter)

        title = QLabel("SisGest")
        title.setObjectName("logoTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))

        subtitle = QLabel("GESTÃO FINANCEIRA")
        subtitle.setObjectName("logoSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        inner.addWidget(title)
        inner.addWidget(subtitle)
        return area

    def _build_separator(self) -> QFrame:
        sep = QFrame()
        sep.setObjectName("sidebarSeparator")
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        return sep

    def _build_section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("sidebarSectionLabel")
        return lbl

    def _build_version(self) -> QLabel:
        lbl = QLabel("v1.0.0  —  SisGest Financeiro")
        lbl.setObjectName("versionLabel")
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    # ── navigation ────────────────────────────────────

    def _navigate(self, key: str) -> None:
        if self._active_button:
            self._active_button.setChecked(False)

        btn = self._buttons.get(key)
        if btn:
            btn.setChecked(True)
            self._active_button = btn

        self.navigation_changed.emit(key)
