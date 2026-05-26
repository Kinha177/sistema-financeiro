from __future__ import annotations
from decimal import Decimal
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from app.models.lancamento import ItemLancamento, LancamentoContabil


class RazoneteService:

    def __init__(self, session: Session) -> None:
        self._db = session

    def gerar_razonete(self, conta_id: int) -> dict:
        """Retorna os lados débito/crédito do razonete e o saldo final.

        lado_debito  → movimentações em que a conta foi debitada  (lado esquerdo)
        lado_credito → movimentações em que a conta foi creditada (lado direito)
        saldo_final  → Σ débitos − Σ créditos
        """
        itens = (
            self._db.query(ItemLancamento)
            .join(ItemLancamento.lancamento)
            .options(joinedload(ItemLancamento.lancamento))
            .filter(
                or_(
                    ItemLancamento.conta_debito_id == conta_id,
                    ItemLancamento.conta_credito_id == conta_id,
                )
            )
            .order_by(LancamentoContabil.data, LancamentoContabil.id)
            .all()
        )

        lado_debito:  list[dict] = []
        lado_credito: list[dict] = []

        for item in itens:
            entrada = {
                "data":      item.lancamento.data,
                "historico": item.lancamento.historico,
                "valor":     item.valor,
            }
            # if/if (não if/elif): um item pode debitar e creditar a mesma conta
            if item.conta_debito_id == conta_id:
                lado_debito.append(entrada)
            if item.conta_credito_id == conta_id:
                lado_credito.append(entrada)

        total_debito  = sum((e["valor"] for e in lado_debito),  Decimal("0"))
        total_credito = sum((e["valor"] for e in lado_credito), Decimal("0"))

        return {
            "lado_debito":  lado_debito,
            "lado_credito": lado_credito,
            "saldo_final":  total_debito - total_credito,
        }
