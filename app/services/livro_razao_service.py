from __future__ import annotations
from datetime import date
from decimal import Decimal
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from app.models.lancamento import ItemLancamento, LancamentoContabil


class LivroRazaoService:

    def __init__(self, session: Session) -> None:
        self._db = session

    def gerar_razao(
        self,
        conta_id: int,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> list[dict]:
        """Retorna movimentos da conta em ordem cronológica com saldo progressivo.

        Saldo: saldo_anterior + débito − crédito
        """
        q = (
            self._db.query(ItemLancamento)
            .join(ItemLancamento.lancamento)
            .options(joinedload(ItemLancamento.lancamento))
            .filter(
                or_(
                    ItemLancamento.conta_debito_id == conta_id,
                    ItemLancamento.conta_credito_id == conta_id,
                )
            )
        )
        if data_inicio is not None:
            q = q.filter(LancamentoContabil.data >= data_inicio)
        if data_fim is not None:
            q = q.filter(LancamentoContabil.data <= data_fim)

        itens = q.order_by(LancamentoContabil.data, LancamentoContabil.id).all()

        saldo = Decimal("0")
        resultado: list[dict] = []

        for item in itens:
            debito  = item.valor if item.conta_debito_id  == conta_id else Decimal("0")
            credito = item.valor if item.conta_credito_id == conta_id else Decimal("0")
            saldo   = saldo + debito - credito

            resultado.append({
                "data":      item.lancamento.data,
                "historico": item.lancamento.historico,
                "debito":    debito,
                "credito":   credito,
                "saldo":     saldo,
            })

        return resultado
