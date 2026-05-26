from __future__ import annotations
from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.conta import PlanoConta
from app.models.lancamento import ItemLancamento, LancamentoContabil


class DreService:

    def __init__(self, session: Session) -> None:
        self._db = session

    def gerar_dre(
        self,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> dict:
        """Retorna estrutura da DRE agrupada em receitas, custos e despesas.

        Prefixos considerados: 3=Receitas, 4=Custos, 5=Despesas.
        Saldo: CREDORA → cred − deb; DEVEDORA → deb − cred.
        """
        sub_deb = (
            self._db.query(
                ItemLancamento.conta_debito_id.label("conta_id"),
                func.sum(ItemLancamento.valor).label("total"),
            )
            .join(ItemLancamento.lancamento)
        )
        sub_cred = (
            self._db.query(
                ItemLancamento.conta_credito_id.label("conta_id"),
                func.sum(ItemLancamento.valor).label("total"),
            )
            .join(ItemLancamento.lancamento)
        )

        if data_inicio is not None:
            sub_deb  = sub_deb.filter(LancamentoContabil.data  >= data_inicio)
            sub_cred = sub_cred.filter(LancamentoContabil.data >= data_inicio)
        if data_fim is not None:
            sub_deb  = sub_deb.filter(LancamentoContabil.data  <= data_fim)
            sub_cred = sub_cred.filter(LancamentoContabil.data <= data_fim)

        sub_deb  = sub_deb.group_by(ItemLancamento.conta_debito_id).subquery()
        sub_cred = sub_cred.group_by(ItemLancamento.conta_credito_id).subquery()

        rows = (
            self._db.query(
                PlanoConta,
                func.coalesce(sub_deb.c.total,  Decimal("0")).label("total_deb"),
                func.coalesce(sub_cred.c.total, Decimal("0")).label("total_cred"),
            )
            .outerjoin(sub_deb,  PlanoConta.id == sub_deb.c.conta_id)
            .outerjoin(sub_cred, PlanoConta.id == sub_cred.c.conta_id)
            .filter(
                PlanoConta.tipo == "ANALITICA",
                PlanoConta.codigo.like("3%")
                | PlanoConta.codigo.like("4%")
                | PlanoConta.codigo.like("5%"),
            )
            .order_by(PlanoConta.codigo)
            .all()
        )

        receitas:  list[dict] = []
        custos:    list[dict] = []
        despesas:  list[dict] = []

        for conta, total_deb, total_cred in rows:
            deb  = Decimal(str(total_deb))
            cred = Decimal(str(total_cred))
            saldo = (cred - deb) if conta.natureza == "CREDORA" else (deb - cred)
            if saldo == Decimal("0"):
                continue
            entrada = {"codigo": conta.codigo, "nome": conta.nome, "valor": saldo}
            if conta.codigo.startswith("3"):
                receitas.append(entrada)
            elif conta.codigo.startswith("4"):
                custos.append(entrada)
            else:
                despesas.append(entrada)

        total_receitas  = sum((e["valor"] for e in receitas),  Decimal("0"))
        total_custos    = sum((e["valor"] for e in custos),    Decimal("0"))
        total_despesas  = sum((e["valor"] for e in despesas),  Decimal("0"))
        lucro_liquido   = total_receitas - total_custos - total_despesas

        return {
            "receitas":        receitas,
            "custos":          custos,
            "despesas":        despesas,
            "total_receitas":  total_receitas,
            "total_custos":    total_custos,
            "total_despesas":  total_despesas,
            "lucro_liquido":   lucro_liquido,
        }
