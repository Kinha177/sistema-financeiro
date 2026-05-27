from __future__ import annotations
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.database.connection import init_db
from app.views.main_window import MainWindow


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("SisGest Financeiro")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SisGest")

    style_path = _base_dir() / "assets" / "styles" / "dark_theme.qss"
    if style_path.exists():
        app.setStyleSheet(style_path.read_text(encoding="utf-8"))

    init_db()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
