from __future__ import annotations
from collections import deque
from datetime import date
from decimal import Decimal
from typing import TypedDict

from sqlalchemy.orm import Session

from app.exceptions import ValidacaoError
from app.models.movimento_estoque import MovimentacaoEstoque
from app.models.produto import Produto


class LoteConsumo(TypedDict):
    data: date
    quantidade: Decimal
    valor_unitario: Decimal
    valor_total: Decimal


class EstoqueService:

    def __init__(self, session: Session) -> None:
        self._db = session

    def entrada_produto(
        self,
        produto_id: int,
        quantidade: Decimal,
        valor: Decimal,
        data: date,
    ) -> MovimentacaoEstoque:
        if quantidade <= Decimal("0"):
            raise ValidacaoError("Quantidade de entrada deve ser maior que zero.")
        if valor < Decimal("0"):
            raise ValidacaoError("Valor unitário não pode ser negativo.")

        produto = self._db.get(Produto, produto_id)
        if produto is None:
            raise ValidacaoError(f"Produto {produto_id} não encontrado.")

        mov = MovimentacaoEstoque(
            produto_id=produto_id,
            tipo="ENTRADA",
            quantidade=quantidade,
            valor=valor,
            data=data,
        )
        self._db.add(mov)
        produto.estoque = (produto.estoque or Decimal("0")) + quantidade
        self._db.flush()
        return mov

    def saida_produto(
        self,
        produto_id: int,
        quantidade: Decimal,
        valor: Decimal,
        data: date,
    ) -> MovimentacaoEstoque:
        if quantidade <= Decimal("0"):
            raise ValidacaoError("Quantidade de saída deve ser maior que zero.")

        produto = self._db.get(Produto, produto_id)
        if produto is None:
            raise ValidacaoError(f"Produto {produto_id} não encontrado.")

        saldo_atual = produto.estoque or Decimal("0")
        if saldo_atual < quantidade:
            raise ValidacaoError(
                f"Estoque insuficiente. Disponível: {saldo_atual}, solicitado: {quantidade}."
            )

        mov = MovimentacaoEstoque(
            produto_id=produto_id,
            tipo="SAIDA",
            quantidade=quantidade,
            valor=valor,
            data=data,
        )
        self._db.add(mov)
        produto.estoque = saldo_atual - quantidade
        self._db.flush()
        return mov

    def calcular_peps(
        self,
        produto_id: int,
        quantidade_saida: Decimal,
    ) -> list[LoteConsumo]:
        """PEPS (FIFO): aloca a saída pelos lotes mais antigos primeiro."""
        return self._calcular_custeio(produto_id, quantidade_saida, lifo=False)

    def calcular_ueps(
        self,
        produto_id: int,
        quantidade_saida: Decimal,
    ) -> list[LoteConsumo]:
        """UEPS (LIFO): aloca a saída pelos lotes mais recentes primeiro."""
        return self._calcular_custeio(produto_id, quantidade_saida, lifo=True)

    def _calcular_custeio(
        self,
        produto_id: int,
        quantidade_saida: Decimal,
        lifo: bool,
    ) -> list[LoteConsumo]:
        if quantidade_saida <= Decimal("0"):
            raise ValidacaoError("Quantidade de saída deve ser maior que zero.")

        produto = self._db.get(Produto, produto_id)
        if produto is None:
            raise ValidacaoError(f"Produto {produto_id} não encontrado.")

        saldo = produto.estoque or Decimal("0")
        if saldo < quantidade_saida:
            raise ValidacaoError(
                f"Estoque insuficiente. Disponível: {saldo}, solicitado: {quantidade_saida}."
            )

        # Query única: todos os movimentos em ordem cronológica
        movimentos = (
            self._db.query(MovimentacaoEstoque)
            .filter(MovimentacaoEstoque.produto_id == produto_id)
            .order_by(MovimentacaoEstoque.data, MovimentacaoEstoque.id)
            .all()
        )

        # Reconstrói o estado corrente dos lotes replaying cada movimento.
        # Cada item: [qty_disponivel, valor_unitario, data_entrada]
        lotes: deque[list] = deque()
        for m in movimentos:
            qty = Decimal(str(m.quantidade))
            vlr = Decimal(str(m.valor))
            if m.tipo == "ENTRADA":
                lotes.append([qty, vlr, m.data])
            else:
                restante = qty
                while restante > 0 and lotes:
                    lote = lotes[-1] if lifo else lotes[0]
                    consumido = min(lote[0], restante)
                    lote[0] -= consumido
                    restante -= consumido
                    if lote[0] == Decimal("0"):
                        if lifo:
                            lotes.pop()
                        else:
                            lotes.popleft()

        # Aloca quantidade_saida pelos lotes disponíveis na ordem do método
        resultado: list[LoteConsumo] = []
        restante = quantidade_saida
        lotes_iter = reversed(lotes) if lifo else iter(lotes)
        for lote in lotes_iter:
            if restante <= Decimal("0"):
                break
            consumido = min(lote[0], restante)
            resultado.append({
                "data":           lote[2],
                "quantidade":     consumido,
                "valor_unitario": lote[1],
                "valor_total":    consumido * lote[1],
            })
            restante -= consumido

        return resultado

    def saldo_estoque(self, produto_id: int) -> Decimal:
        produto = self._db.get(Produto, produto_id)
        if produto is None:
            raise ValidacaoError(f"Produto {produto_id} não encontrado.")
        return produto.estoque or Decimal("0")
