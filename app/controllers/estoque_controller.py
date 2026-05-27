from __future__ import annotations
from collections import deque
from datetime import date
from decimal import Decimal

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFormLayout, QLineEdit, QMessageBox,
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
)
from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_session
from app.exceptions import ValidacaoError
from app.models.movimento_estoque import MovimentacaoEstoque
from app.models.produto import Produto
from app.services.estoque_service import EstoqueService, LoteConsumo
from app.views.components.page_header import PageHeader
from app.views.custos_view import CustosView
from app.views.estoque_view import EstoqueView


class EstoqueController:

    def __init__(
        self,
        estoque_view: EstoqueView,
        custos_view: CustosView,
        session: Session | None = None,
    ) -> None:
        self._view    = estoque_view
        self._custos  = custos_view
        self._session = session or get_session()
        self._svc     = EstoqueService(self._session)
        self._produto_ids: list[int] = []
        self._produto_selecionado_id: int | None = None

        self._find_estoque_widgets()
        self._connect_estoque_view()
        self._connect_custos_view()
        self._load_produtos()
        self._load_movimentos()
        self._load_custos_produtos()

    # ── localização de widgets (EstoqueView tem widgets como variáveis locais) ──

    def _find_estoque_widgets(self) -> None:
        header = self._view.findChild(PageHeader)
        btns   = header.findChildren(QPushButton) if header else []
        self._btn_entrada   = btns[0] if len(btns) > 0 else None
        self._btn_saida     = btns[1] if len(btns) > 1 else None

        tabs: QTabWidget | None = self._view.findChild(QTabWidget)
        self._tabs = tabs
        if tabs is None:
            self._tbl_produtos = self._search = self._btn_novo_prod = None
            self._tbl_movimentos = self._tbl_peps = self._tbl_ueps = None
            return

        def _tab(n: int) -> QWidget | None:
            w = tabs.widget(n)
            return w if w is not None else None

        prod_tab = _tab(0)
        if prod_tab is not None:
            self._tbl_produtos  = prod_tab.findChild(QTableWidget)
            self._search        = prod_tab.findChild(QLineEdit)
            novo_btns           = prod_tab.findChildren(QPushButton)
            self._btn_novo_prod = novo_btns[0] if novo_btns else None
        else:
            self._tbl_produtos = self._search = self._btn_novo_prod = None

        mov_tab  = _tab(1)
        peps_tab = _tab(2)
        ueps_tab = _tab(3)
        self._tbl_movimentos = mov_tab.findChild(QTableWidget)  if mov_tab  else None
        self._tbl_peps       = peps_tab.findChild(QTableWidget) if peps_tab else None
        self._tbl_ueps       = ueps_tab.findChild(QTableWidget) if ueps_tab else None

    # ── conexão de sinais ──────────────────────────────────────────────────────

    def _connect_estoque_view(self) -> None:
        if self._btn_entrada:
            self._btn_entrada.clicked.connect(self._abrir_dialog_entrada)
        if self._btn_saida:
            self._btn_saida.clicked.connect(self._abrir_dialog_saida)
        if self._btn_novo_prod:
            self._btn_novo_prod.clicked.connect(self._abrir_dialog_novo_produto)
        if self._search:
            self._search.textChanged.connect(self._filtrar_produtos)
        if self._tbl_produtos:
            self._tbl_produtos.currentRowChanged.connect(self._on_produto_selecionado)
        if self._tabs:
            self._tabs.currentChanged.connect(self._on_tab_changed)

    def _connect_custos_view(self) -> None:
        self._custos._btn_calcular.clicked.connect(self._calcular_custeio)

    # ── carregamento de dados ──────────────────────────────────────────────────

    def _load_produtos(self, filtro: str = "") -> None:
        if not self._tbl_produtos:
            return
        produtos = (
            self._session.query(Produto)
            .filter(Produto.nome.ilike(f"%{filtro}%"))
            .order_by(Produto.nome)
            .all()
        )
        self._produto_ids = [p.id for p in produtos]
        tbl = self._tbl_produtos
        tbl.setRowCount(len(produtos))
        for row, p in enumerate(produtos):
            tbl.setItem(row, 0, QTableWidgetItem(p.nome))
            tbl.setItem(row, 1, self._right_item(str(p.estoque or Decimal("0"))))
            tbl.setItem(row, 2, QTableWidgetItem(""))

    def _load_movimentos(self) -> None:
        if not self._tbl_movimentos:
            return
        movs = (
            self._session.query(MovimentacaoEstoque)
            .options(joinedload(MovimentacaoEstoque.produto))
            .order_by(MovimentacaoEstoque.data.desc(), MovimentacaoEstoque.id.desc())
            .all()
        )
        tbl = self._tbl_movimentos
        tbl.setRowCount(len(movs))
        for row, m in enumerate(movs):
            total = Decimal(str(m.quantidade)) * Decimal(str(m.valor))
            tbl.setItem(row, 0, QTableWidgetItem(str(m.data)))
            tbl.setItem(row, 1, QTableWidgetItem(m.produto.nome))
            tbl.setItem(row, 2, QTableWidgetItem(m.tipo))
            tbl.setItem(row, 3, self._right_item(str(m.quantidade)))
            tbl.setItem(row, 4, self._right_item(f"R$ {m.valor:,.2f}"))
            tbl.setItem(row, 5, self._right_item(f"R$ {total:,.2f}"))

    def _load_custos_produtos(self) -> None:
        self._custos._combo_produto.clear()
        for p in self._session.query(Produto).order_by(Produto.nome).all():
            self._custos._combo_produto.addItem(p.nome, p.id)

    def _load_ficha(self, produto_id: int, metodo: str) -> None:
        """Ficha de estoque PEPS ou UEPS com saldo corrente por movimento."""
        tbl = self._tbl_peps if metodo == "PEPS" else self._tbl_ueps
        if not tbl:
            return

        movs = (
            self._session.query(MovimentacaoEstoque)
            .filter(MovimentacaoEstoque.produto_id == produto_id)
            .order_by(MovimentacaoEstoque.data, MovimentacaoEstoque.id)
            .all()
        )

        lotes: deque[list[Decimal]] = deque()   # cada item: [qty_disponivel, valor_unit]
        saldo_qty   = Decimal("0")
        saldo_valor = Decimal("0")

        tbl.setRowCount(len(movs))
        for row, m in enumerate(movs):
            qty = Decimal(str(m.quantidade))
            vlr = Decimal(str(m.valor))

            if m.tipo == "ENTRADA":
                lotes.append([qty, vlr])
                saldo_qty   += qty
                saldo_valor += qty * vlr
                tbl.setItem(row, 0, QTableWidgetItem(str(m.data)))
                tbl.setItem(row, 1, self._right_item(str(qty)))
                tbl.setItem(row, 2, self._right_item(f"R$ {vlr:,.2f}"))
                tbl.setItem(row, 3, QTableWidgetItem(""))
                tbl.setItem(row, 4, QTableWidgetItem(""))
            else:
                custo_total = self._consumir_lotes(lotes, qty, metodo)
                custo_unit  = custo_total / qty if qty else Decimal("0")
                saldo_qty   -= qty
                saldo_valor -= custo_total
                tbl.setItem(row, 0, QTableWidgetItem(str(m.data)))
                tbl.setItem(row, 1, QTableWidgetItem(""))
                tbl.setItem(row, 2, QTableWidgetItem(""))
                tbl.setItem(row, 3, self._right_item(str(qty)))
                tbl.setItem(row, 4, self._right_item(f"R$ {custo_unit:,.2f}"))

            tbl.setItem(row, 5, self._right_item(str(saldo_qty)))
            tbl.setItem(row, 6, self._right_item(f"R$ {saldo_valor:,.2f}"))

    # ── helpers ────────────────────────────────────────────────────────────────

    def _consumir_lotes(
        self, lotes: deque[list[Decimal]], qty: Decimal, metodo: str
    ) -> Decimal:
        """Consome qty da fila (FIFO=PEPS, LIFO=UEPS). Retorna custo total consumido."""
        custo    = Decimal("0")
        restante = qty
        while restante > 0 and lotes:
            lote      = lotes[0] if metodo == "PEPS" else lotes[-1]
            consumido = min(lote[0], restante)
            custo    += consumido * lote[1]
            lote[0]  -= consumido
            restante -= consumido
            if lote[0] == Decimal("0"):
                if metodo == "PEPS":
                    lotes.popleft()
                else:
                    lotes.pop()
        return custo

    @staticmethod
    def _right_item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return item

    # ── slots — EstoqueView ────────────────────────────────────────────────────

    def _filtrar_produtos(self, texto: str) -> None:
        self._load_produtos(texto)

    def _on_produto_selecionado(self, row: int) -> None:
        if 0 <= row < len(self._produto_ids):
            self._produto_selecionado_id = self._produto_ids[row]
            self._refresh_custeio_tabs()

    def _on_tab_changed(self, index: int) -> None:
        if index in (2, 3) and self._produto_selecionado_id is not None:
            metodo = "PEPS" if index == 2 else "UEPS"
            self._load_ficha(self._produto_selecionado_id, metodo)

    def _refresh_custeio_tabs(self) -> None:
        if self._tabs is None or self._produto_selecionado_id is None:
            return
        idx = self._tabs.currentIndex()
        if idx == 2:
            self._load_ficha(self._produto_selecionado_id, "PEPS")
        elif idx == 3:
            self._load_ficha(self._produto_selecionado_id, "UEPS")

    def _abrir_dialog_novo_produto(self) -> None:
        dlg = QDialog(self._view)
        dlg.setWindowTitle("Novo Produto")
        dlg.setMinimumWidth(320)
        form = QFormLayout(dlg)

        nome_edit = QLineEdit()
        nome_edit.setPlaceholderText("Nome do produto…")
        form.addRow("Nome:", nome_edit)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        form.addRow(btns)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        nome = nome_edit.text().strip()
        if not nome:
            QMessageBox.warning(self._view, "Atenção", "Informe o nome do produto.")
            return
        p = Produto(nome=nome, estoque=Decimal("0"))
        self._session.add(p)
        self._session.commit()
        self._load_produtos()
        self._load_custos_produtos()

    def _abrir_dialog_entrada(self) -> None:
        dlg, combo_prod, spin_qty, spin_vlr, date_edit = self._build_mov_dialog(
            "Registrar Entrada"
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        produto_id: int | None = combo_prod.currentData()
        if produto_id is None:
            return
        try:
            self._svc.entrada_produto(
                produto_id=produto_id,
                quantidade=Decimal(str(spin_qty.value())),
                valor=Decimal(str(spin_vlr.value())),
                data=date(
                    date_edit.date().year(),
                    date_edit.date().month(),
                    date_edit.date().day(),
                ),
            )
            self._session.commit()
            self._refresh_all()
        except ValidacaoError as exc:
            QMessageBox.warning(self._view, "Erro de validação", str(exc))

    def _abrir_dialog_saida(self) -> None:
        dlg, combo_prod, spin_qty, spin_vlr, date_edit = self._build_mov_dialog(
            "Registrar Saída"
        )
        spin_vlr.setEnabled(False)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        produto_id: int | None = combo_prod.currentData()
        if produto_id is None:
            return
        try:
            qty = Decimal(str(spin_qty.value()))
            # custo unitário calculado via PEPS para registro da saída
            lotes_custo = self._svc.calcular_peps(produto_id, qty)
            custo_total = sum(l["valor_total"] for l in lotes_custo)
            custo_unit  = custo_total / qty if qty else Decimal("0")
            self._svc.saida_produto(
                produto_id=produto_id,
                quantidade=qty,
                valor=custo_unit,
                data=date(
                    date_edit.date().year(),
                    date_edit.date().month(),
                    date_edit.date().day(),
                ),
            )
            self._session.commit()
            self._refresh_all()
        except ValidacaoError as exc:
            QMessageBox.warning(self._view, "Erro de validação", str(exc))

    def _build_mov_dialog(
        self, titulo: str
    ) -> tuple[QDialog, QComboBox, QDoubleSpinBox, QDoubleSpinBox, QDateEdit]:
        dlg = QDialog(self._view)
        dlg.setWindowTitle(titulo)
        dlg.setMinimumWidth(360)
        form = QFormLayout(dlg)

        combo_prod = QComboBox()
        for p in self._session.query(Produto).order_by(Produto.nome).all():
            combo_prod.addItem(p.nome, p.id)
        form.addRow("Produto:", combo_prod)

        spin_qty = QDoubleSpinBox()
        spin_qty.setRange(0.0001, 999_999)
        spin_qty.setDecimals(4)
        spin_qty.setValue(1)
        form.addRow("Quantidade:", spin_qty)

        spin_vlr = QDoubleSpinBox()
        spin_vlr.setRange(0, 999_999)
        spin_vlr.setDecimals(2)
        spin_vlr.setPrefix("R$ ")
        form.addRow("Valor Unit.:", spin_vlr)

        date_edit = QDateEdit(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        form.addRow("Data:", date_edit)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        form.addRow(btns)

        return dlg, combo_prod, spin_qty, spin_vlr, date_edit

    def _refresh_all(self) -> None:
        self._load_produtos()
        self._load_movimentos()
        self._load_custos_produtos()
        self._refresh_custeio_tabs()

    # ── slots — CustosView ─────────────────────────────────────────────────────

    def _calcular_custeio(self) -> None:
        produto_id: int | None = self._custos._combo_produto.currentData()
        if produto_id is None:
            QMessageBox.warning(self._custos, "Atenção", "Selecione um produto.")
            return

        qty    = Decimal(str(self._custos._spin_quantidade.value()))
        metodo = "PEPS" if "PEPS" in self._custos._combo_metodo.currentText() else "UEPS"

        try:
            lotes = (
                self._svc.calcular_peps(produto_id, qty)
                if metodo == "PEPS"
                else self._svc.calcular_ueps(produto_id, qty)
            )
        except ValidacaoError as exc:
            QMessageBox.warning(self._custos, "Erro", str(exc))
            return

        total_qty   = sum(l["quantidade"]  for l in lotes)
        total_valor = sum(l["valor_total"] for l in lotes)

        self._custos._lbl_metodo_badge.setText(metodo)
        self._custos._card_metodo.set_value(metodo)
        self._custos._card_lotes.set_value(str(len(lotes)))
        self._custos._card_qtd.set_value(str(total_qty))
        self._custos._card_total.set_value(f"R$ {total_valor:,.2f}")
        self._custos._lbl_total_footer.setText(f"Total: R$ {total_valor:,.2f}")

        tbl = self._custos._table
        tbl.setRowCount(len(lotes))
        for row, lote in enumerate(lotes):
            tbl.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            tbl.setItem(row, 1, QTableWidgetItem(str(lote["data"])))
            tbl.setItem(row, 2, self._right_item(str(lote["quantidade"])))
            tbl.setItem(row, 3, self._right_item(f"R$ {lote['valor_unitario']:,.2f}"))
            tbl.setItem(row, 4, self._right_item(f"R$ {lote['valor_total']:,.2f}"))

    # ── interface pública ──────────────────────────────────────────────────────

    def listar_produtos(self) -> list[Produto]:
        return self._session.query(Produto).order_by(Produto.nome).all()

    def buscar_produto(self, produto_id: int) -> Produto | None:
        return self._session.get(Produto, produto_id)

    def criar_produto(self, dados: dict) -> Produto:
        p = Produto(nome=dados["nome"], estoque=Decimal("0"))
        self._session.add(p)
        self._session.commit()
        return p

    def atualizar_produto(self, produto_id: int, dados: dict) -> Produto | None:
        p = self._session.get(Produto, produto_id)
        if p is None:
            return None
        p.nome = dados.get("nome", p.nome)
        self._session.commit()
        return p

    def registrar_entrada(self, dados: dict) -> MovimentacaoEstoque:
        mov = self._svc.entrada_produto(
            produto_id=dados["produto_id"],
            quantidade=Decimal(str(dados["quantidade"])),
            valor=Decimal(str(dados["valor"])),
            data=dados["data"],
        )
        self._session.commit()
        return mov

    def registrar_saida(self, dados: dict) -> MovimentacaoEstoque:
        mov = self._svc.saida_produto(
            produto_id=dados["produto_id"],
            quantidade=Decimal(str(dados["quantidade"])),
            valor=Decimal(str(dados["valor"])),
            data=dados["data"],
        )
        self._session.commit()
        return mov

    def listar_movimentos(
        self, produto_id: int | None = None
    ) -> list[MovimentacaoEstoque]:
        q = self._session.query(MovimentacaoEstoque)
        if produto_id is not None:
            q = q.filter(MovimentacaoEstoque.produto_id == produto_id)
        return q.order_by(MovimentacaoEstoque.data.desc()).all()

    def calcular_peps(
        self, produto_id: int, quantidade_saida: Decimal
    ) -> list[LoteConsumo]:
        return self._svc.calcular_peps(produto_id, quantidade_saida)

    def calcular_ueps(
        self, produto_id: int, quantidade_saida: Decimal
    ) -> list[LoteConsumo]:
        return self._svc.calcular_ueps(produto_id, quantidade_saida)
