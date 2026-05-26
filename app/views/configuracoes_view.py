from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QScrollArea,
    QFrame, QGroupBox, QFormLayout,
)
from PySide6.QtCore import Qt

from app.views.components.page_header import PageHeader


# ── Section Card ──────────────────────────────────────────────────────────────

class _SectionCard(QWidget):
    def __init__(self, title: str, icon: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")

        self._root_ly = QVBoxLayout(self)
        self._root_ly.setSpacing(16)

        # título
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(32, 32)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size:16px;")
        title_row.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("settingsSectionTitle")
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        self._root_ly.addLayout(title_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("settingsDivider")
        self._root_ly.addWidget(sep)

        self._form_ly = QFormLayout()
        self._form_ly.setSpacing(12)
        self._form_ly.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._form_ly.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self._root_ly.addLayout(self._form_ly)

    def add_field(self, label: str, widget: QWidget) -> None:
        lbl = QLabel(label)
        lbl.setObjectName("labelField")
        self._form_ly.addRow(lbl, widget)

    def add_footer(self) -> None:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("settingsDivider")
        self._root_ly.addWidget(sep)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("Salvar Alterações")
        save_btn.setFixedWidth(160)
        btn_row.addWidget(save_btn)
        self._root_ly.addLayout(btn_row)


# ── ConfiguracoesView ─────────────────────────────────────────────────────────

class ConfiguracoesView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = PageHeader("Configurações", "Preferências e dados do sistema")
        root.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("pageContent")
        content_ly = QVBoxLayout(content)
        content_ly.setContentsMargins(28, 24, 28, 28)
        content_ly.setSpacing(20)

        content_ly.addWidget(self._build_empresa_section())
        content_ly.addWidget(self._build_aparencia_section())
        content_ly.addWidget(self._build_banco_section())
        content_ly.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll)

    # ── sections ──────────────────────────────────────────────────────────

    def _build_empresa_section(self) -> QWidget:
        card = _SectionCard("Dados da Empresa", "🏢")

        card.add_field("Razão Social", QLineEdit(placeholderText="Nome completo da empresa"))
        card.add_field("CNPJ",         QLineEdit(placeholderText="00.000.000/0000-00"))
        card.add_field("E-mail",       QLineEdit(placeholderText="contato@empresa.com.br"))
        card.add_field("Telefone",     QLineEdit(placeholderText="(00) 00000-0000"))

        regime_cb = QComboBox()
        regime_cb.addItems(["Simples Nacional", "Lucro Presumido", "Lucro Real"])
        card.add_field("Regime Tributário", regime_cb)

        card.add_footer()
        return card

    def _build_aparencia_section(self) -> QWidget:
        card = _SectionCard("Aparência", "🎨")

        tema_cb = QComboBox()
        tema_cb.addItems(["Escuro (padrão)", "Claro"])
        card.add_field("Tema", tema_cb)

        idioma_cb = QComboBox()
        idioma_cb.addItems(["Português (Brasil)", "English"])
        card.add_field("Idioma", idioma_cb)

        moeda_cb = QComboBox()
        moeda_cb.addItems(["Real (BRL)", "Dólar (USD)", "Euro (EUR)"])
        card.add_field("Moeda Padrão", moeda_cb)

        card.add_footer()
        return card

    def _build_banco_section(self) -> QWidget:
        card = _SectionCard("Banco de Dados", "🗄")

        db_path = QLineEdit()
        db_path.setPlaceholderText("data/sisgest.db")
        db_path.setReadOnly(True)
        card.add_field("Localização", db_path)

        btn_row = QWidget()
        btn_ly = QHBoxLayout(btn_row)
        btn_ly.setContentsMargins(0, 0, 0, 0)
        btn_ly.setSpacing(8)
        backup_btn = QPushButton("Fazer Backup")
        restore_btn = QPushButton("Restaurar Backup")
        restore_btn.setObjectName("btnSecondary")
        btn_ly.addWidget(backup_btn)
        btn_ly.addWidget(restore_btn)
        btn_ly.addStretch()
        card.add_field("Backup", btn_row)

        card.add_footer()
        return card
