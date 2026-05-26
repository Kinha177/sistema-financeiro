from __future__ import annotations
from decimal import Decimal

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem

from app.controllers.conta_controller import ContaController
from app.database.connection import get_session
from app.services.livro_razao_service import LivroRazaoService
from app.views.livro_razao_view import LivroRazaoView


class _DateItem(QTableWidgetItem):
    """Item de data: exibe dd/mm/yyyy, ordena pelo valor ISO armazenado em UserRole."""

    def __lt__(self, other: QTableWidgetItem) -> bool:
        return (
            (self.data(Qt.ItemDataRole.UserRole) or "")
            < (other.data(Qt.ItemDataRole.UserRole) or "")
        )


def _fmt(valor: Decimal) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class LivroRazaoController:
    """Conecta LivroRazaoView ao LivroRazaoService."""

    def __init__(self, view: LivroRazaoView) -> None:
        self._view = view
        self._linhas_cache: list[dict] = []
        try:
            self._carregar_contas()
        except Exception as exc:
            QTimer.singleShot(
                0, lambda: QMessageBox.critical(view, "Erro ao carregar contas", str(exc))
            )
        view._combo_conta.currentIndexChanged.connect(self._consultar)
        view._btn_consultar.clicked.connect(self._consultar)
        view._edit_pesquisa.textChanged.connect(self._filtrar_local)

    # ── inicialização ─────────────────────────────────────────────────────────

    def _carregar_contas(self) -> None:
        contas = ContaController().listar_analiticas()
        self._view._combo_conta.blockSignals(True)
        for conta in contas:
            self._view._combo_conta.addItem(
                f"{conta.codigo} — {conta.nome}", conta.id
            )
        self._view._combo_conta.blockSignals(False)

    # ── consulta (DB) ─────────────────────────────────────────────────────────

    def _consultar(self, _=None) -> None:
        conta_id = self._view._combo_conta.currentData()
        if conta_id is None:
            return
        try:
            d_from = self._view._date_from.date().toPython()
            d_to   = self._view._date_to.date().toPython()
            session = get_session()
            try:
                self._linhas_cache = LivroRazaoService(session).gerar_razao(
                    conta_id, data_inicio=d_from, data_fim=d_to
                )
            finally:
                session.close()
            self._filtrar_local(self._view._edit_pesquisa.text())
        except Exception as exc:
            QMessageBox.critical(self._view, "Erro", str(exc))

    # ── filtro local (sem DB) ─────────────────────────────────────────────────

    def _filtrar_local(self, termo: str) -> None:
        termo = termo.strip().lower()
        if termo:
            linhas = [l for l in self._linhas_cache if termo in l["historico"].lower()]
        else:
            linhas = self._linhas_cache
        self._preencher_tabela(linhas)

    # ── preenchimento ─────────────────────────────────────────────────────────

    def _preencher_tabela(self, linhas: list[dict]) -> None:
        table = self._view._table
        table.setSortingEnabled(False)
        table.setRowCount(0)

        total_debito  = Decimal("0")
        total_credito = Decimal("0")

        for row, linha in enumerate(linhas):
            table.insertRow(row)

            data_item = _DateItem(linha["data"].strftime("%d/%m/%Y"))
            data_item.setData(Qt.ItemDataRole.UserRole, linha["data"].isoformat())
            table.setItem(row, 0, data_item)

            table.setItem(row, 1, QTableWidgetItem(linha["historico"]))
            table.setItem(row, 2, self._view._number_item(_fmt(linha["debito"])))
            table.setItem(row, 3, self._view._number_item(_fmt(linha["credito"])))
            table.setItem(row, 4, self._saldo_item(linha["saldo"]))

            total_debito  += linha["debito"]
            total_credito += linha["credito"]

        table.setSortingEnabled(True)
        self._atualizar_totais(total_debito, total_credito)

    def _saldo_item(self, saldo: Decimal) -> QTableWidgetItem:
        item = self._view._number_item(_fmt(saldo))
        if saldo < 0:
            item.setForeground(QColor("#f87171"))
        elif saldo > 0:
            item.setForeground(QColor("#86efac"))
        return item

    def _atualizar_totais(
        self, total_debito: Decimal, total_credito: Decimal
    ) -> None:
        # Saldo final = último saldo acumulado do período (não afetado pelo filtro de pesquisa)
        saldo_final = (
            self._linhas_cache[-1]["saldo"] if self._linhas_cache else Decimal("0")
        )

        self._view._lbl_total_debito.setText(f"Débito:  R$ {_fmt(total_debito)}")
        self._view._lbl_total_credito.setText(f"Crédito:  R$ {_fmt(total_credito)}")
        self._view._lbl_saldo_final.setText(f"Saldo:  R$ {_fmt(saldo_final)}")

        cor = "#f87171" if saldo_final < 0 else "#86efac" if saldo_final > 0 else "#a78bfa"
        self._view._lbl_saldo_final.setStyleSheet(
            f"color: {cor}; font-size: 12px; font-weight: 700;"
            f" padding: 0 24px 0 0; background: transparent;"
        )
