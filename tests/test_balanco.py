from __future__ import annotations
from decimal import Decimal
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — registra todos os modelos no Base.metadata
from app.database.base import Base
from app.models.conta import PlanoConta
from app.models.lancamento import ItemLancamento, LancamentoContabil
from app.services.balanco_service import BalancoService


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    s = Session()
    yield s
    s.close()


@pytest.fixture
def contas(session):
    # 1=Ativo, 2=Passivo, 6=PL, 3=Receita (contrapartida DRE, ignorada pelo balanço)
    caixa    = PlanoConta(codigo="1.1.1", nome="Caixa",              tipo="ANALITICA", natureza="DEVEDORA")
    emprest  = PlanoConta(codigo="2.1.1", nome="Empréstimos a Pagar",tipo="ANALITICA", natureza="CREDORA")
    capital  = PlanoConta(codigo="6.1.1", nome="Capital Social",     tipo="ANALITICA", natureza="CREDORA")
    receita  = PlanoConta(codigo="3.1.1", nome="Receita de Vendas",  tipo="ANALITICA", natureza="CREDORA")
    session.add_all([caixa, emprest, capital, receita])
    session.flush()
    return caixa, emprest, capital, receita


def _lancamento(session, data_, historico, debito_id, credito_id, valor):
    lanc = LancamentoContabil(data=data_, historico=historico)
    session.add(lanc)
    session.flush()
    item = ItemLancamento(
        lancamento_id=lanc.id,
        conta_debito_id=debito_id,
        conta_credito_id=credito_id,
        valor=Decimal(str(valor)),
    )
    session.add(item)
    session.flush()


# ── casos de teste ────────────────────────────────────────────────────────────

def test_apenas_ativo(session, contas):
    """Venda à vista: débito Caixa (Ativo), crédito Receita (ignorada pelo balanço)."""
    caixa, emprest, capital, receita = contas
    _lancamento(session, date(2024, 1, 5), "Venda", debito_id=caixa.id, credito_id=receita.id, valor="500")

    resultado = BalancoService(session).gerar_balanco()

    assert len(resultado["ativo"])   == 1
    assert len(resultado["passivo"]) == 0
    assert len(resultado["pl"])      == 0
    assert resultado["total_ativo"]  == Decimal("500")
    assert resultado["equacao_valida"] is False


def test_ativo_e_passivo(session, contas):
    """Empréstimo recebido: débito Caixa, crédito Empréstimos — Ativo = Passivo."""
    caixa, emprest, capital, receita = contas
    _lancamento(session, date(2024, 2, 10), "Empréstimo", debito_id=caixa.id, credito_id=emprest.id, valor="800")

    resultado = BalancoService(session).gerar_balanco()

    assert resultado["total_ativo"]    == Decimal("800")
    assert resultado["total_passivo"]  == Decimal("800")
    assert resultado["total_pl"]       == Decimal("0")
    assert resultado["equacao_valida"] is True


def test_ativo_e_pl(session, contas):
    """Integralização de capital: débito Caixa, crédito Capital Social — Ativo = PL."""
    caixa, emprest, capital, receita = contas
    _lancamento(session, date(2024, 3, 1), "Capital", debito_id=caixa.id, credito_id=capital.id, valor="1000")

    resultado = BalancoService(session).gerar_balanco()

    assert resultado["total_ativo"]    == Decimal("1000")
    assert resultado["total_passivo"]  == Decimal("0")
    assert resultado["total_pl"]       == Decimal("1000")
    assert resultado["equacao_valida"] is True


def test_equacao_com_tres_grupos(session, contas):
    """Ativo 1500 = Passivo 500 + PL 1000."""
    caixa, emprest, capital, receita = contas
    _lancamento(session, date(2024, 4,  1), "Capital",    debito_id=caixa.id, credito_id=capital.id, valor="1000")
    _lancamento(session, date(2024, 4, 10), "Empréstimo", debito_id=caixa.id, credito_id=emprest.id,  valor="500")

    resultado = BalancoService(session).gerar_balanco()

    assert resultado["total_ativo"]       == Decimal("1500")
    assert resultado["total_passivo"]     == Decimal("500")
    assert resultado["total_pl"]          == Decimal("1000")
    assert resultado["total_passivo_pl"]  == Decimal("1500")
    assert resultado["equacao_valida"]    is True


def test_sem_movimentacoes(session, contas):
    resultado = BalancoService(session).gerar_balanco()

    assert resultado["ativo"]          == []
    assert resultado["passivo"]        == []
    assert resultado["pl"]             == []
    assert resultado["total_ativo"]    == Decimal("0")
    assert resultado["total_passivo"]  == Decimal("0")
    assert resultado["total_pl"]       == Decimal("0")
    assert resultado["equacao_valida"] is True
