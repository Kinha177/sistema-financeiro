from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem,
)
from PySide6.QtCore import Qt


class PlanoContasView(QWidget):
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
        content_layout.setSpacing(16)

        content_layout.addWidget(self._build_toolbar())
        content_layout.addWidget(self._build_tree())

        root.addWidget(content)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("pageHeader")
        layout = QVBoxLayout(header)
        layout.setAlignment(Qt.AlignVCenter)

        QLabel("Plano de Contas", header).setObjectName("pageTitle")
        title = header.findChild(QLabel)
        title.setObjectName("pageTitle")

        layout.addWidget(QLabel("Plano de Contas", objectName="pageTitle"))
        layout.addWidget(QLabel("Estrutura hierárquica das contas contábeis", objectName="pageSubtitle"))
        return header

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)

        btn_new = QPushButton("+ Nova Conta")
        btn_new.setFixedWidth(140)

        btn_import = QPushButton("Importar")
        btn_import.setObjectName("btnSecondary")
        btn_import.setFixedWidth(100)

        layout.addWidget(btn_new)
        layout.addWidget(btn_import)
        layout.addStretch()
        return bar

    def _build_tree(self) -> QTreeWidget:
        tree = QTreeWidget()
        tree.setHeaderLabels(["Código", "Nome", "Grupo", "Natureza", "Tipo"])
        tree.setColumnWidth(0, 100)
        tree.setColumnWidth(1, 300)
        tree.setColumnWidth(2, 160)
        tree.setColumnWidth(3, 100)
        tree.setAlternatingRowColors(True)

        placeholder = QTreeWidgetItem(tree, ["—", "Nenhuma conta cadastrada", "", "", ""])
        return tree
