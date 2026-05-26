from __future__ import annotations
from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.exceptions import ValidacaoError
from app.models.movimento_estoque import MovimentacaoEstoque
from app.models.produto import Produto


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
        """Registra entrada de estoque e incrementa saldo do produto."""
        if quantidade <= Decimal("0"):
            raise ValidacaoError("Quantidade de entrada deve ser maior que zero.")

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
        """Registra saída de estoque. Lança ValidacaoError se estoque insuficiente."""
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
    ) -> list[dict]:
        """PEPS (FIFO): aloca a saída pelos lotes mais antigos primeiro.

        Retorna lista de dicts com os lotes consumidos:
            [{"data", "quantidade", "valor_unitario", "valor_total"}, ...]
        """
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

        # Fila de entradas em ordem cronológica (mais antigo primeiro)
        entradas = (
            self._db.query(MovimentacaoEstoque)
            .filter(
                MovimentacaoEstoque.produto_id == produto_id,
                MovimentacaoEstoque.tipo == "ENTRADA",
            )
            .order_by(MovimentacaoEstoque.data, MovimentacaoEstoque.id)
            .all()
        )

        # Total já consumido pelas saídas anteriores registradas
        total_saidas_anteriores = (
            self._db.query(func.sum(MovimentacaoEstoque.quantidade))
            .filter(
                MovimentacaoEstoque.produto_id == produto_id,
                MovimentacaoEstoque.tipo == "SAIDA",
            )
            .scalar()
        ) or Decimal("0")

        # Consome as saídas anteriores da frente da fila (PEPS sobre o histórico)
        ja_consumido = Decimal(str(total_saidas_anteriores))
        lotes: list[dict] = []
        for entrada in entradas:
            qtd = Decimal(str(entrada.quantidade))
            if ja_consumido >= qtd:
                ja_consumido -= qtd
                continue
            lotes.append({
                "data":                  entrada.data,
                "quantidade_disponivel": qtd - ja_consumido,
                "valor_unitario":        Decimal(str(entrada.valor)),
            })
            ja_consumido = Decimal("0")

        # Aloca a quantidade_saida pelos lotes disponíveis
        resultado: list[dict] = []
        restante = quantidade_saida
        for lote in lotes:
            if restante <= Decimal("0"):
                break
            consumido = min(lote["quantidade_disponivel"], restante)
            resultado.append({
                "data":           lote["data"],
                "quantidade":     consumido,
                "valor_unitario": lote["valor_unitario"],
                "valor_total":    consumido * lote["valor_unitario"],
            })
            restante -= consumido

        return resultado

    def saldo_estoque(self, produto_id: int) -> Decimal:
        """Retorna o saldo atual do produto."""
        produto = self._db.get(Produto, produto_id)
        if produto is None:
            raise ValidacaoError(f"Produto {produto_id} não encontrado.")
        return produto.estoque or Decimal("0")
