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
from app.services.razonete_service import RazoneteService


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
    caixa   = PlanoConta(codigo="1.1.1", nome="Caixa",   tipo="ANALITICA", natureza="DEVEDORA")
    receita = PlanoConta(codigo="3.1.1", nome="Receita", tipo="ANALITICA", natureza="CREDORA")
    session.add_all([caixa, receita])
    session.flush()
    return caixa, receita


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

def test_apenas_debitos(session, contas):
    caixa, receita = contas
    _lancamento(session, date(2024, 1, 10), "Venda à vista",  debito_id=caixa.id, credito_id=receita.id, valor="300")
    _lancamento(session, date(2024, 1, 15), "Venda a prazo",  debito_id=caixa.id, credito_id=receita.id, valor="200")

    resultado = RazoneteService(session).gerar_razonete(caixa.id)

    assert len(resultado["lado_debito"])  == 2
    assert len(resultado["lado_credito"]) == 0
    assert resultado["lado_debito"][0]["valor"] == Decimal("300")
    assert resultado["lado_debito"][1]["valor"] == Decimal("200")


def test_apenas_creditos(session, contas):
    caixa, receita = contas
    _lancamento(session, date(2024, 2, 5), "Devolução",       debito_id=receita.id, credito_id=caixa.id, valor="150")
    _lancamento(session, date(2024, 2, 8), "Estorno",         debito_id=receita.id, credito_id=caixa.id, valor="50")

    resultado = RazoneteService(session).gerar_razonete(caixa.id)

    assert len(resultado["lado_debito"])  == 0
    assert len(resultado["lado_credito"]) == 2
    assert resultado["lado_credito"][0]["valor"] == Decimal("150")
    assert resultado["lado_credito"][1]["valor"] == Decimal("50")


def test_debitos_e_creditos_misturados(session, contas):
    caixa, receita = contas
    _lancamento(session, date(2024, 3, 1), "Entrada D",  debito_id=caixa.id,   credito_id=receita.id, valor="500")
    _lancamento(session, date(2024, 3, 5), "Saída C",    debito_id=receita.id, credito_id=caixa.id,   valor="100")
    _lancamento(session, date(2024, 3, 10), "Entrada D", debito_id=caixa.id,   credito_id=receita.id, valor="200")

    resultado = RazoneteService(session).gerar_razonete(caixa.id)

    assert len(resultado["lado_debito"])  == 2
    assert len(resultado["lado_credito"]) == 1

    historicos_debito  = [e["historico"] for e in resultado["lado_debito"]]
    historicos_credito = [e["historico"] for e in resultado["lado_credito"]]
    assert "Entrada D" in historicos_debito
    assert "Saída C"   in historicos_credito


def test_saldo_final_correto(session, contas):
    """Débitos 400 + 100 = 500; Créditos 80 + 20 = 100; Saldo = 400."""
    caixa, receita = contas
    _lancamento(session, date(2024, 4, 1), "D1", debito_id=caixa.id,   credito_id=receita.id, valor="400")
    _lancamento(session, date(2024, 4, 2), "D2", debito_id=caixa.id,   credito_id=receita.id, valor="100")
    _lancamento(session, date(2024, 4, 3), "C1", debito_id=receita.id, credito_id=caixa.id,   valor="80")
    _lancamento(session, date(2024, 4, 4), "C2", debito_id=receita.id, credito_id=caixa.id,   valor="20")

    resultado = RazoneteService(session).gerar_razonete(caixa.id)

    assert resultado["saldo_final"] == Decimal("400")
