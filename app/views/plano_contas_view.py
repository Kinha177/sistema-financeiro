from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QDialog, QFormLayout,
    QComboBox, QLabel, QDialogButtonBox, QMessageBox,
    QFrame, QMenu, QSizePolicy, QHeaderView,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

from app.controllers.conta_controller import ContaController
from app.exceptions import ValidacaoError
from app.models.conta import PlanoConta
from app.views.components.page_header import PageHeader

_TIPO_LABEL = {"ANALITICA": "Analítica", "SINTETICA": "Sintética"}
_NAT_LABEL  = {"DEVEDORA":  "Devedora",  "CREDORA":   "Credora"}


# ── Dialog ────────────────────────────────────────────────────────────────────

class ContaDialog(QDialog):
    """Formulário para criação e edição de uma PlanoConta."""

    def __init__(
        self,
        todas_contas: list[PlanoConta],
        conta: PlanoConta | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._conta   = conta
        self._contas  = todas_contas
        self._editing = conta is not None

        titulo = (
            f"Editar Conta: {conta.codigo} — {conta.nome}"
            if self._editing else "Nova Conta"
        )
        self.setWindowTitle(titulo)
        self.setMinimumWidth(520)
        self.setModal(True)

        self._build_ui()
        if self._editing:
            self._populate(conta)

    # ── build ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # cabeçalho do dialog
        header = QWidget()
        header.setObjectName("dialogHeader")
        hly = QVBoxLayout(header)
        hly.setContentsMargins(24, 20, 24, 16)
        hly.setSpacing(4)

        title_lbl = QLabel(self.windowTitle())
        title_lbl.setObjectName("dialogTitle")
        sub_lbl = QLabel("Campos marcados com * são obrigatórios.")
        sub_lbl.setObjectName("dialogSubtitle")
        hly.addWidget(title_lbl)
        hly.addWidget(sub_lbl)
        root.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("settingsDivider")
        root.addWidget(sep)

        # formulário
        form_container = QWidget()
        form_ly = QFormLayout(form_container)
        form_ly.setContentsMargins(24, 20, 24, 20)
        form_ly.setSpacing(14)
        form_ly.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_ly.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self._codigo_edit = QLineEdit()
        self._codigo_edit.setPlaceholderText("ex: 1.1.1")
        self._codigo_edit.setMaxLength(20)

        self._nome_edit = QLineEdit()
        self._nome_edit.setPlaceholderText("Nome da conta")
        self._nome_edit.setMaxLength(200)

        self._tipo_cb = QComboBox()
        for label, val in [("Analítica", "ANALITICA"), ("Sintética", "SINTETICA")]:
            self._tipo_cb.addItem(label, val)

        self._nat_cb = QComboBox()
        for label, val in [("Devedora", "DEVEDORA"), ("Credora", "CREDORA")]:
            self._nat_cb.addItem(label, val)

        self._pai_cb = QComboBox()
        self._pai_cb.addItem("— Nenhuma (conta raiz) —", None)
        for c in self._contas:
            if self._editing and c.id == self._conta.id:
                continue
            self._pai_cb.addItem(f"{c.codigo}  —  {c.nome}", c.id)

        form_ly.addRow(self._lbl("Código *"),     self._codigo_edit)
        form_ly.addRow(self._lbl("Nome *"),       self._nome_edit)
        form_ly.addRow(self._lbl("Tipo *"),       self._tipo_cb)
        form_ly.addRow(self._lbl("Natureza *"),   self._nat_cb)
        form_ly.addRow(self._lbl("Conta Pai"),    self._pai_cb)

        root.addWidget(form_container)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setObjectName("settingsDivider")
        root.addWidget(sep2)

        # botões
        btn_box = QDialogButtonBox()
        btn_box.setContentsMargins(24, 14, 24, 18)
        btn_cancel = btn_box.addButton("Cancelar", QDialogButtonBox.RejectRole)
        btn_save   = btn_box.addButton("Salvar",   QDialogButtonBox.AcceptRole)
        btn_cancel.setObjectName("btnSecondary")
        btn_save.setFixedWidth(100)

        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        root.addWidget(btn_box)

    def _lbl(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("labelField")
        return lbl

    def _populate(self, conta: PlanoConta) -> None:
        self._codigo_edit.setText(conta.codigo)
        self._nome_edit.setText(conta.nome)

        idx = self._tipo_cb.findData(conta.tipo)
        self._tipo_cb.setCurrentIndex(idx if idx >= 0 else 0)

        idx = self._nat_cb.findData(conta.natureza)
        self._nat_cb.setCurrentIndex(idx if idx >= 0 else 0)

        idx = self._pai_cb.findData(conta.conta_pai_id)
        self._pai_cb.setCurrentIndex(idx if idx >= 0 else 0)

    # ── slots ─────────────────────────────────────────────────────────────

    def _on_accept(self) -> None:
        codigo = self._codigo_edit.text().strip()
        nome   = self._nome_edit.text().strip()

        if not codigo:
            self._shake(self._codigo_edit, "Código é obrigatório.")
            return
        if not nome:
            self._shake(self._nome_edit, "Nome é obrigatório.")
            return

        self.accept()

    def _shake(self, widget: QWidget, msg: str) -> None:
        widget.setFocus()
        widget.setStyleSheet("border: 1px solid #f87171;")
        QTimer.singleShot(1500, lambda: widget.setStyleSheet(""))
        QMessageBox.warning(self, "Campo obrigatório", msg)

    # ── dados ─────────────────────────────────────────────────────────────

    def get_dados(self) -> dict:
        return {
            "codigo":       self._codigo_edit.text().strip(),
            "nome":         self._nome_edit.text().strip(),
            "tipo":         self._tipo_cb.currentData(),
            "natureza":     self._nat_cb.currentData(),
            "conta_pai_id": self._pai_cb.currentData(),
        }


# ── Main View ─────────────────────────────────────────────────────────────────

class PlanoContasView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._controller = ContaController()
        self._setup_ui()
        self._reload()

    # ── build ─────────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── cabeçalho ──
        header = PageHeader("Plano de Contas", "Estrutura hierárquica das contas contábeis")

        self._btn_new = QPushButton("+ Nova Conta")
        self._btn_new.setFixedWidth(130)
        self._btn_new.clicked.connect(self._on_new)

        self._btn_edit = QPushButton("Editar")
        self._btn_edit.setObjectName("btnSecondary")
        self._btn_edit.setFixedWidth(90)
        self._btn_edit.setEnabled(False)
        self._btn_edit.clicked.connect(self._on_edit)

        self._btn_del = QPushButton("Excluir")
        self._btn_del.setObjectName("btnDanger")
        self._btn_del.setFixedWidth(90)
        self._btn_del.setEnabled(False)
        self._btn_del.clicked.connect(self._on_delete)

        header.add_action(self._btn_new)
        header.add_action(self._btn_edit)
        header.add_action(self._btn_del)
        root.addWidget(header)

        # ── conteúdo ──
        content = QWidget()
        content.setObjectName("pageContent")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 20, 28, 28)
        cl.setSpacing(14)

        cl.addWidget(self._build_search_bar())
        cl.addWidget(self._build_tree())

        root.addWidget(content)

    def _build_search_bar(self) -> QWidget:
        bar = QWidget()
        ly = QHBoxLayout(bar)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(10)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Pesquisar por código ou nome…")
        self._search.setMaximumWidth(360)
        self._search.setClearButtonEnabled(True)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._apply_filter)
        self._search.textChanged.connect(lambda _: self._search_timer.start())

        ly.addWidget(self._search)

        self._count_lbl = QLabel()
        self._count_lbl.setObjectName("cardSubtext")
        ly.addWidget(self._count_lbl)

        ly.addStretch()
        return bar

    def _build_tree(self) -> QTreeWidget:
        self._tree = QTreeWidget()
        self._tree.setObjectName("accountTree")
        self._tree.setHeaderLabels(["Código", "Nome", "Tipo", "Natureza"])
        self._tree.setColumnWidth(0, 110)
        self._tree.setColumnWidth(2, 110)
        self._tree.setColumnWidth(3, 110)
        self._tree.header().setStretchLastSection(False)
        self._tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._tree.setAlternatingRowColors(True)
        self._tree.setRootIsDecorated(True)
        self._tree.setEditTriggers(QTreeWidget.NoEditTriggers)
        self._tree.setSelectionMode(QTreeWidget.SingleSelection)
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)
        self._tree.itemDoubleClicked.connect(lambda item, _: self._on_edit())
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)
        return self._tree

    # ── carregamento de dados ──────────────────────────────────────────────

    def _reload(self) -> None:
        try:
            contas = self._controller.listar_todas()
        except Exception as e:
            QMessageBox.critical(self, "Erro ao carregar", str(e))
            return

        self._tree.clear()
        self._update_count(contas)

        # índices
        by_id:     dict[int, QTreeWidgetItem] = {}
        by_parent: dict[int | None, list[PlanoConta]] = {}

        for c in contas:
            item = QTreeWidgetItem()
            item.setText(0, c.codigo)
            item.setText(1, c.nome)
            item.setText(2, _TIPO_LABEL.get(c.tipo, c.tipo))
            item.setText(3, _NAT_LABEL.get(c.natureza, c.natureza))
            item.setData(0, Qt.UserRole, c.id)
            by_id[c.id] = item
            by_parent.setdefault(c.conta_pai_id, []).append(c)

        # monta a árvore respeitando hierarquia
        def _add(parent_id: int | None, parent_widget) -> None:
            for c in by_parent.get(parent_id, []):
                item = by_id[c.id]
                if isinstance(parent_widget, QTreeWidget):
                    parent_widget.addTopLevelItem(item)
                else:
                    parent_widget.addChild(item)
                _add(c.id, item)

        _add(None, self._tree)
        self._tree.expandAll()
        self._on_selection_changed()

    def _update_count(self, contas: list) -> None:
        n = len(contas)
        self._count_lbl.setText(
            f"{n} conta" if n == 1 else f"{n} contas"
        )

    # ── pesquisa ──────────────────────────────────────────────────────────

    def _apply_filter(self) -> None:
        termo = self._search.text().strip()
        if not termo:
            self._show_all_items()
            return

        t = termo.lower()

        def _matches(item: QTreeWidgetItem) -> bool:
            return t in item.text(0).lower() or t in item.text(1).lower()

        def _hide_all(item: QTreeWidgetItem) -> None:
            item.setHidden(True)
            for i in range(item.childCount()):
                _hide_all(item.child(i))

        def _show_ancestors(item: QTreeWidgetItem) -> None:
            item.setHidden(False)
            p = item.parent()
            while p:
                p.setHidden(False)
                p = p.parent()

        def _check(item: QTreeWidgetItem) -> None:
            if _matches(item):
                _show_ancestors(item)
            for i in range(item.childCount()):
                _check(item.child(i))

        # esconde tudo, depois exibe os que batem
        for i in range(self._tree.topLevelItemCount()):
            _hide_all(self._tree.topLevelItem(i))
        for i in range(self._tree.topLevelItemCount()):
            _check(self._tree.topLevelItem(i))

    def _show_all_items(self) -> None:
        def _show(item: QTreeWidgetItem) -> None:
            item.setHidden(False)
            for i in range(item.childCount()):
                _show(item.child(i))
        for i in range(self._tree.topLevelItemCount()):
            _show(self._tree.topLevelItem(i))

    # ── seleção ───────────────────────────────────────────────────────────

    def _selected_item(self) -> QTreeWidgetItem | None:
        items = self._tree.selectedItems()
        return items[0] if items else None

    def _selected_id(self) -> int | None:
        item = self._selected_item()
        return item.data(0, Qt.UserRole) if item else None

    def _on_selection_changed(self) -> None:
        has_sel = self._selected_item() is not None
        self._btn_edit.setEnabled(has_sel)
        self._btn_del.setEnabled(has_sel)

    # ── context menu ──────────────────────────────────────────────────────

    def _show_context_menu(self, pos) -> None:
        item = self._tree.itemAt(pos)
        menu = QMenu(self)

        act_new = QAction("+ Nova Conta", self)
        act_new.triggered.connect(self._on_new)
        menu.addAction(act_new)

        if item:
            act_sub = QAction("+ Adicionar Subconta", self)
            act_sub.triggered.connect(lambda: self._on_new_subconta(item))
            menu.addAction(act_sub)
            menu.addSeparator()

            act_edit = QAction("Editar", self)
            act_edit.triggered.connect(self._on_edit)
            menu.addAction(act_edit)

            act_del = QAction("Excluir", self)
            act_del.triggered.connect(self._on_delete)
            menu.addAction(act_del)

        menu.exec(self._tree.viewport().mapToGlobal(pos))

    # ── CRUD ──────────────────────────────────────────────────────────────

    def _on_new(self) -> None:
        try:
            contas = self._controller.listar_todas()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
            return

        dialog = ContaDialog(contas, parent=self)
        if dialog.exec() != QDialog.Accepted:
            return

        try:
            self._controller.criar(dialog.get_dados())
            self._reload()
        except ValidacaoError as e:
            QMessageBox.warning(self, "Dado inválido", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erro inesperado", str(e))

    def _on_new_subconta(self, item: QTreeWidgetItem) -> None:
        """Abre dialog pré-selecionando o item como conta pai."""
        pai_id = item.data(0, Qt.UserRole)
        try:
            contas = self._controller.listar_todas()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
            return

        dialog = ContaDialog(contas, parent=self)
        # pré-seleciona o pai no combobox
        idx = dialog._pai_cb.findData(pai_id)
        if idx >= 0:
            dialog._pai_cb.setCurrentIndex(idx)

        if dialog.exec() != QDialog.Accepted:
            return

        try:
            self._controller.criar(dialog.get_dados())
            self._reload()
        except ValidacaoError as e:
            QMessageBox.warning(self, "Dado inválido", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erro inesperado", str(e))

    def _on_edit(self) -> None:
        conta_id = self._selected_id()
        if conta_id is None:
            return

        try:
            conta  = self._controller.buscar_por_id(conta_id)
            contas = self._controller.listar_todas()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
            return

        if conta is None:
            QMessageBox.warning(self, "Não encontrado", "Conta não encontrada.")
            return

        dialog = ContaDialog(contas, conta=conta, parent=self)
        if dialog.exec() != QDialog.Accepted:
            return

        try:
            self._controller.atualizar(conta_id, dialog.get_dados())
            self._reload()
        except ValidacaoError as e:
            QMessageBox.warning(self, "Dado inválido", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erro inesperado", str(e))

    def _on_delete(self) -> None:
        item = self._selected_item()
        if item is None:
            return

        conta_id = item.data(0, Qt.UserRole)
        nome     = item.text(1)

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Deseja excluir a conta:\n\n"
            f"  {item.text(0)}  —  {nome}\n\n"
            f"Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resposta != QMessageBox.Yes:
            return

        try:
            self._controller.excluir(conta_id)
            self._reload()
        except ValidacaoError as e:
            QMessageBox.warning(self, "Não é possível excluir", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erro inesperado", str(e))
