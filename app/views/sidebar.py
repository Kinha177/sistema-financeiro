from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QFont


_NAV_ITEMS: list[tuple[str, str, str, str]] = [
    # (chave, rótulo, ícone, grupo)
    ("dashboard",     "Dashboard",         "📊", "VISÃO GERAL"),
    ("plano_contas",  "Plano de Contas",   "📋", "CONTABILIDADE"),
    ("livro_diario",  "Livro Diário",      "📓", "CONTABILIDADE"),
    ("livro_razao",   "Livro Razão",       "📒", "CONTABILIDADE"),
    ("razonete",      "Razonetes",         "🔢", "CONTABILIDADE"),
    ("dre",           "DRE",               "📈", "RELATÓRIOS"),
    ("balanco",       "Balanço",           "⚖",  "RELATÓRIOS"),
    ("estoque",       "Estoque",           "📦", "OPERACIONAL"),
    ("relatorios",    "Relatórios",        "🖨",  "OPERACIONAL"),
    ("configuracoes", "Configurações",     "⚙",  "SISTEMA"),
]

_W_EXPANDED  = 240
_W_COLLAPSED = 64


class Sidebar(QWidget):
    navigation_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._collapsed = False
        self._active_btn: QPushButton | None = None
        self._buttons: dict[str, QPushButton] = {}
        self._section_labels: list[QLabel] = []
        self._anim: QVariantAnimation | None = None
        self._setup_ui()
        self.setFixedWidth(_W_EXPANDED)

    # ── build ─────────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_divider())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("navScroll")

        nav_container = QWidget()
        nav_container.setObjectName("navContainer")
        self._nav_vbox = QVBoxLayout(nav_container)
        self._nav_vbox.setContentsMargins(0, 8, 0, 8)
        self._nav_vbox.setSpacing(0)

        current_group = ""
        for key, label, icon, group in _NAV_ITEMS:
            if group != current_group:
                current_group = group
                self._nav_vbox.addSpacing(6)
                lbl = self._build_section_label(group)
                self._nav_vbox.addWidget(lbl)
                self._section_labels.append(lbl)

            btn = self._build_nav_btn(key, label, icon)
            self._nav_vbox.addWidget(btn)
            self._buttons[key] = btn

        self._nav_vbox.addStretch()
        scroll.setWidget(nav_container)
        root.addWidget(scroll, 1)

        root.addWidget(self._build_divider())
        root.addWidget(self._build_footer())

        self._navigate("dashboard")

    def _build_header(self) -> QWidget:
        w = QWidget()
        w.setObjectName("sidebarHeader")
        w.setFixedHeight(72)

        outer = QHBoxLayout(w)
        outer.setContentsMargins(0, 0, 8, 0)
        outer.setSpacing(0)

        logo_area = QWidget()
        logo_area.setObjectName("logoArea")
        logo_ly = QVBoxLayout(logo_area)
        logo_ly.setContentsMargins(0, 0, 0, 0)
        logo_ly.setSpacing(2)
        logo_ly.setAlignment(Qt.AlignCenter)

        self._logo_title = QLabel("SisGest")
        self._logo_title.setObjectName("logoTitle")
        self._logo_title.setAlignment(Qt.AlignCenter)
        self._logo_title.setFont(QFont("Segoe UI", 20, QFont.Bold))

        self._logo_sub = QLabel("GESTÃO FINANCEIRA")
        self._logo_sub.setObjectName("logoSubtitle")
        self._logo_sub.setAlignment(Qt.AlignCenter)

        logo_ly.addWidget(self._logo_title)
        logo_ly.addWidget(self._logo_sub)
        outer.addWidget(logo_area, 1)

        self._toggle_btn = QPushButton("◀")
        self._toggle_btn.setObjectName("sidebarToggle")
        self._toggle_btn.setFixedSize(26, 26)
        self._toggle_btn.setCursor(Qt.PointingHandCursor)
        self._toggle_btn.clicked.connect(self.toggle)
        outer.addWidget(self._toggle_btn)

        return w

    def _build_divider(self) -> QFrame:
        f = QFrame()
        f.setObjectName("sidebarSeparator")
        f.setFrameShape(QFrame.HLine)
        f.setFixedHeight(1)
        return f

    def _build_section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("sidebarSectionLabel")
        return lbl

    def _build_nav_btn(self, key: str, label: str, icon: str) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("navButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("navIcon", icon)
        btn.setProperty("navLabel", label)
        self._apply_btn_style(btn, expanded=True)
        btn.clicked.connect(lambda _, k=key: self._navigate(k))
        return btn

    def _build_footer(self) -> QWidget:
        w = QWidget()
        w.setObjectName("sidebarFooter")
        ly = QVBoxLayout(w)
        ly.setContentsMargins(0, 10, 0, 10)
        ly.setAlignment(Qt.AlignCenter)

        self._version_lbl = QLabel("v1.0.0  —  SisGest")
        self._version_lbl.setObjectName("versionLabel")
        self._version_lbl.setAlignment(Qt.AlignCenter)
        ly.addWidget(self._version_lbl)
        return w

    # ── helpers ───────────────────────────────────────────────────────────

    def _apply_btn_style(self, btn: QPushButton, *, expanded: bool) -> None:
        icon  = btn.property("navIcon")
        label = btn.property("navLabel")
        if expanded:
            btn.setText(f"   {icon}   {label}")
            btn.setToolTip("")
            btn.setStyleSheet("")
        else:
            btn.setText(icon)
            btn.setToolTip(label)
            btn.setStyleSheet(
                "QPushButton { text-align: center; padding-left: 0; "
                "padding-right: 0; font-size: 18px; }"
                "QPushButton:checked { text-align: center; padding-left: 0; "
                "padding-right: 0; font-size: 18px; }"
                "QPushButton:hover { text-align: center; padding-left: 0; "
                "padding-right: 0; font-size: 18px; }"
            )

    # ── collapse ──────────────────────────────────────────────────────────

    def toggle(self) -> None:
        self._collapsed = not self._collapsed
        target_w = _W_COLLAPSED if self._collapsed else _W_EXPANDED

        if self._anim:
            self._anim.stop()

        self._anim = QVariantAnimation(self)
        self._anim.setStartValue(self.width())
        self._anim.setEndValue(target_w)
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self.setFixedWidth)
        self._anim.start(QVariantAnimation.DeleteWhenStopped)

        expanded = not self._collapsed
        for btn in self._buttons.values():
            self._apply_btn_style(btn, expanded=expanded)

        for lbl in self._section_labels:
            lbl.setVisible(expanded)

        if self._collapsed:
            self._logo_title.setText("SG")
            self._logo_sub.hide()
            self._toggle_btn.setText("▶")
        else:
            self._logo_title.setText("SisGest")
            self._logo_sub.show()
            self._toggle_btn.setText("◀")

        self._version_lbl.setVisible(expanded)

    # ── navigation ────────────────────────────────────────────────────────

    def _navigate(self, key: str) -> None:
        if self._active_btn:
            self._active_btn.setChecked(False)
        btn = self._buttons.get(key)
        if btn:
            btn.setChecked(True)
            self._active_btn = btn
        self.navigation_changed.emit(key)
