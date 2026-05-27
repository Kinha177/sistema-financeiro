from __future__ import annotations
from decimal import Decimal

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

from app.controllers.conta_controller import ContaController
from app.database.connection import get_session
from app.services.razonete_service import RazoneteService
from app.utils.formatters import formatar_numero as _fmt
from app.views.razonete_view import RazoneteView


class RazoneteController:
    """Conecta RazoneteView ao RazoneteService."""

    def __init__(self, view: RazoneteView) -> None:
        self._view      = view
        self._cache:    dict = {}        # resultado bruto do service
        self._sort_asc: bool = True      # True = crescente, False = decrescente

        try:
            self._carregar_contas()
        except Exception as exc:
            QTimer.singleShot(
                0, lambda: QMessageBox.critical(view, "Erro ao carregar contas", str(exc))
            )

        view._combo_conta.currentIndexChanged.connect(self._consultar)
        view._btn_consultar.clicked.connect(self._consultar)
        view._edit_pesquisa.textChanged.connect(self._filtrar_local)
        view._btn_ordenar.clicked.connect(self._toggle_ordem)

    # ── inicialização ─────────────────────────────────────────────────────────

    def _carregar_contas(self) -> None:
        contas = ContaController().listar_analiticas()
        self._view._combo_conta.blockSignals(True)
        for conta in contas:
            self._view._combo_conta.addItem(
                f"{conta.codigo} — {conta.nome}",
                (conta.id, conta.codigo, conta.nome),
            )
        self._view._combo_conta.blockSignals(False)

    # ── consulta (DB) ─────────────────────────────────────────────────────────

    def _consultar(self, _=None) -> None:
        data = self._view._combo_conta.currentData()
        if data is None:
            return
        conta_id, codigo, nome = data
        try:
            session = get_session()
            try:
                self._cache = RazoneteService(session).gerar_razonete(conta_id)
            finally:
                session.close()
            self._cache["_codigo"] = codigo
            self._cache["_nome"]   = nome
            self._filtrar_local(self._view._edit_pesquisa.text())
        except Exception as exc:
            QMessageBox.critical(self._view, "Erro", str(exc))

    # ── ordenação ─────────────────────────────────────────────────────────────

    def _toggle_ordem(self, _=None) -> None:
        self._sort_asc = not self._sort_asc
        self._view._btn_ordenar.setText("↑ Data" if self._sort_asc else "↓ Data")
        if self._cache:
            try:
                self._filtrar_local(self._view._edit_pesquisa.text())
            except Exception as exc:
                QMessageBox.critical(self._view, "Erro", str(exc))

    # ── filtro local (sem DB) ─────────────────────────────────────────────────

    def _filtrar_local(self, termo: str) -> None:
        if not self._cache:
            return

        termo = termo.strip().lower()

        def _filtrar(lista: list[dict]) -> list[dict]:
            result = [e for e in lista if termo in e["historico"].lower()] if termo else lista
            return sorted(result, key=lambda e: e["data"], reverse=not self._sort_asc)

        lado_deb  = _filtrar(self._cache["lado_debito"])
        lado_cred = _filtrar(self._cache["lado_credito"])

        self._popular_card(
            self._cache["_codigo"],
            self._cache["_nome"],
            lado_deb,
            lado_cred,
        )

    # ── preenchimento ─────────────────────────────────────────────────────────

    def _popular_card(
        self,
        codigo: str,
        nome: str,
        lado_deb: list[dict],
        lado_cred: list[dict],
    ) -> None:
        card = self._view._card
        card.limpar()
        card.set_conta(codigo, nome)

        total_deb  = Decimal("0")
        total_cred = Decimal("0")

        for i, entrada in enumerate(lado_deb):
            card.adicionar_debito(
                entrada["data"].strftime("%d/%m"),
                entrada["historico"],
                f"R$ {_fmt(entrada['valor'])}",
                par=(i % 2 == 1),
            )
            total_deb += entrada["valor"]

        for i, entrada in enumerate(lado_cred):
            card.adicionar_credito(
                entrada["data"].strftime("%d/%m"),
                entrada["historico"],
                f"R$ {_fmt(entrada['valor'])}",
                par=(i % 2 == 1),
            )
            total_cred += entrada["valor"]

        # saldo calculado sobre as entradas visíveis — mantém consistência com
        # os totais da linha quando filtro de pesquisa estiver ativo
        saldo = total_deb - total_cred
        card.set_totais(
            f"R$ {_fmt(total_deb)}",
            f"R$ {_fmt(total_cred)}",
            f"R$ {_fmt(saldo)}",
            saldo_negativo=saldo < Decimal("0"),
        )
