from __future__ import annotations
from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.conta import PlanoConta
from app.models.lancamento import ItemLancamento, LancamentoContabil

# Convenção de prefixos: 1=Ativo, 2=Passivo, 6=Patrimônio Líquido
# (3=Receitas / 4=Custos / 5=Despesas são exclusivos da DRE)


class BalancoService:

    def __init__(self, session: Session) -> None:
        self._db = session

    def gerar_balanco(self, data_base: date | None = None) -> dict:
        """Retorna Ativo, Passivo e PL até data_base (inclusive).

        Saldo: DEVEDORA (Ativo) → deb − cred; CREDORA (Passivo/PL) → cred − deb.
        Valida equação: Ativo = Passivo + PL.
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

        if data_base is not None:
            sub_deb  = sub_deb.filter(LancamentoContabil.data  <= data_base)
            sub_cred = sub_cred.filter(LancamentoContabil.data <= data_base)

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
                PlanoConta.codigo.like("1%")
                | PlanoConta.codigo.like("2%")
                | PlanoConta.codigo.like("6%"),
            )
            .order_by(PlanoConta.codigo)
            .all()
        )

        ativo:   list[dict] = []
        passivo: list[dict] = []
        pl:      list[dict] = []

        for conta, total_deb, total_cred in rows:
            deb   = Decimal(str(total_deb))
            cred  = Decimal(str(total_cred))
            saldo = (deb - cred) if conta.natureza == "DEVEDORA" else (cred - deb)
            if saldo == Decimal("0"):
                continue
            entrada = {"codigo": conta.codigo, "nome": conta.nome, "valor": saldo}
            if conta.codigo.startswith("1"):
                ativo.append(entrada)
            elif conta.codigo.startswith("2"):
                passivo.append(entrada)
            else:
                pl.append(entrada)

        total_ativo   = sum((e["valor"] for e in ativo),   Decimal("0"))
        total_passivo = sum((e["valor"] for e in passivo), Decimal("0"))
        total_pl      = sum((e["valor"] for e in pl),      Decimal("0"))
        total_p_pl    = total_passivo + total_pl

        return {
            "ativo":            ativo,
            "passivo":          passivo,
            "pl":               pl,
            "total_ativo":      total_ativo,
            "total_passivo":    total_passivo,
            "total_pl":         total_pl,
            "total_passivo_pl": total_p_pl,
            "equacao_valida":   total_ativo == total_p_pl,
        }
