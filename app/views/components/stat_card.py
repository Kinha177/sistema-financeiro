from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class StatCard(QWidget):
    """Card de estatística com ícone, título, valor e variação."""

    def __init__(
        self,
        icon: str,
        title: str,
        value: str,
        subtext: str,
        accent: str = "#a78bfa",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("statCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        # topo: ícone + label
        top = QHBoxLayout()
        top.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(38, 38)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            f"background:{accent}25; border-radius:10px; font-size:18px;"
        )
        top.addWidget(icon_lbl)

        title_lbl = QLabel(title.upper())
        title_lbl.setObjectName("cardTitle")
        top.addWidget(title_lbl, 1)

        layout.addLayout(top)

        # valor
        self._value_lbl = QLabel(value)
        self._value_lbl.setObjectName("cardValue")
        self._value_lbl.setStyleSheet(f"color:{accent};")
        layout.addWidget(self._value_lbl)

        # subtexto
        sub_lbl = QLabel(subtext)
        sub_lbl.setObjectName("cardSubtext")
        layout.addWidget(sub_lbl)

    def set_value(self, value: str) -> None:
        self._value_lbl.setText(value)
