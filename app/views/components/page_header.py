from __future__ import annotations
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class PageHeader(QWidget):
    """Cabeçalho padrão de página com título, subtítulo e área de ações."""

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("pageHeader")

        self._outer = QHBoxLayout(self)
        self._outer.setContentsMargins(28, 0, 28, 0)
        self._outer.setSpacing(0)
        self._outer.setAlignment(Qt.AlignVCenter)

        text_area = QWidget()
        text_ly = QVBoxLayout(text_area)
        text_ly.setContentsMargins(0, 0, 0, 0)
        text_ly.setSpacing(2)

        self._title_lbl = QLabel(title)
        self._title_lbl.setObjectName("pageTitle")

        self._subtitle_lbl = QLabel(subtitle)
        self._subtitle_lbl.setObjectName("pageSubtitle")

        text_ly.addWidget(self._title_lbl)
        text_ly.addWidget(self._subtitle_lbl)

        self._outer.addWidget(text_area)
        self._outer.addStretch()

        self._actions = QWidget()
        self._actions_ly = QHBoxLayout(self._actions)
        self._actions_ly.setContentsMargins(0, 0, 0, 0)
        self._actions_ly.setSpacing(8)
        self._outer.addWidget(self._actions)

    def add_action(self, widget: QWidget) -> None:
        self._actions_ly.addWidget(widget)
