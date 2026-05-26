import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.database.connection import init_db
from app.views.main_window import MainWindow

_STYLE_PATH = Path(__file__).parent / "assets" / "styles" / "dark_theme.qss"


def _load_stylesheet(app: QApplication) -> None:
    if _STYLE_PATH.exists():
        app.setStyleSheet(_STYLE_PATH.read_text(encoding="utf-8"))


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("SisGest Financeiro")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SisGest")

    _load_stylesheet(app)
    init_db()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
