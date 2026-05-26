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
from app.services.dre_service import DreService


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
    caixa   = PlanoConta(codigo="1.1.1", nome="Caixa",                tipo="ANALITICA", natureza="DEVEDORA")
    receita = PlanoConta(codigo="3.1.1", nome="Receita de Vendas",    tipo="ANALITICA", natureza="CREDORA")
    custo   = PlanoConta(codigo="4.1.1", nome="Custo de Mercadorias", tipo="ANALITICA", natureza="DEVEDORA")
    despesa = PlanoConta(codigo="5.1.1", nome="Despesas Gerais",      tipo="ANALITICA", natureza="DEVEDORA")
    session.add_all([caixa, receita, custo, despesa])
    session.flush()
    return caixa, receita, custo, despesa


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

def test_apenas_receitas(session, contas):
    caixa, receita, custo, despesa = contas
    _lancamento(session, date(2024, 1, 10), "Venda", debito_id=caixa.id, credito_id=receita.id, valor="1000")

    resultado = DreService(session).gerar_dre()

    assert len(resultado["receitas"]) == 1
    assert len(resultado["custos"])   == 0
    assert len(resultado["despesas"]) == 0
    assert resultado["receitas"][0]["valor"] == Decimal("1000")
    assert resultado["total_receitas"]       == Decimal("1000")
    assert resultado["lucro_liquido"]        == Decimal("1000")


def test_receitas_e_custos(session, contas):
    caixa, receita, custo, despesa = contas
    _lancamento(session, date(2024, 2,  1), "Venda", debito_id=caixa.id, credito_id=receita.id, valor="1000")
    _lancamento(session, date(2024, 2,  5), "CMV",   debito_id=custo.id, credito_id=caixa.id,   valor="300")

    resultado = DreService(session).gerar_dre()

    assert resultado["total_receitas"] == Decimal("1000")
    assert resultado["total_custos"]   == Decimal("300")
    assert resultado["total_despesas"] == Decimal("0")
    assert resultado["lucro_liquido"]  == Decimal("700")


def test_receitas_e_despesas(session, contas):
    caixa, receita, custo, despesa = contas
    _lancamento(session, date(2024, 3,  1), "Venda",   debito_id=caixa.id,   credito_id=receita.id, valor="800")
    _lancamento(session, date(2024, 3, 10), "Despesa", debito_id=despesa.id, credito_id=caixa.id,   valor="200")

    resultado = DreService(session).gerar_dre()

    assert resultado["total_receitas"]  == Decimal("800")
    assert resultado["total_custos"]    == Decimal("0")
    assert resultado["total_despesas"]  == Decimal("200")
    assert resultado["lucro_liquido"]   == Decimal("600")


def test_calculo_lucro_liquido(session, contas):
    """Receitas 2000 - Custos 500 - Despesas 300 = Lucro 1200."""
    caixa, receita, custo, despesa = contas
    _lancamento(session, date(2024, 4,  1), "Venda",   debito_id=caixa.id,   credito_id=receita.id, valor="2000")
    _lancamento(session, date(2024, 4,  5), "CMV",     debito_id=custo.id,   credito_id=caixa.id,   valor="500")
    _lancamento(session, date(2024, 4, 10), "Despesa", debito_id=despesa.id, credito_id=caixa.id,   valor="300")

    resultado = DreService(session).gerar_dre()

    assert resultado["total_receitas"]  == Decimal("2000")
    assert resultado["total_custos"]    == Decimal("500")
    assert resultado["total_despesas"]  == Decimal("300")
    assert resultado["lucro_liquido"]   == Decimal("1200")


def test_sem_movimentacoes(session, contas):
    resultado = DreService(session).gerar_dre()

    assert resultado["receitas"]        == []
    assert resultado["custos"]          == []
    assert resultado["despesas"]        == []
    assert resultado["total_receitas"]  == Decimal("0")
    assert resultado["total_custos"]    == Decimal("0")
    assert resultado["total_despesas"]  == Decimal("0")
    assert resultado["lucro_liquido"]   == Decimal("0")
