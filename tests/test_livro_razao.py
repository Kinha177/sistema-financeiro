from __future__ import annotations
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — registra todos os modelos no Base.metadata
from app.database.base import Base
from app.models.conta import PlanoConta
from app.models.lancamento import ItemLancamento, LancamentoContabil
from app.services.livro_razao_service import LivroRazaoService


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
    """Retorna (caixa, receita) — duas contas analíticas para os testes."""
    caixa   = PlanoConta(codigo="1.1.1", nome="Caixa",   tipo="ANALITICA", natureza="DEVEDORA")
    receita = PlanoConta(codigo="3.1.1", nome="Receita", tipo="ANALITICA", natureza="CREDORA")
    session.add_all([caixa, receita])
    session.flush()
    return caixa, receita


def _lancamento(session, data_, historico, debito_id, credito_id, valor):
    """Cria LancamentoContabil + ItemLancamento e persiste sem commit."""
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
    return lanc


# ── casos de teste ────────────────────────────────────────────────────────────

def test_lancamento_apenas_debito(session, contas):
    caixa, receita = contas
    _lancamento(session, date(2024, 1, 10), "Entrada de caixa",
                debito_id=caixa.id, credito_id=receita.id, valor="500.00")

    razao = LivroRazaoService(session).gerar_razao(caixa.id)

    assert len(razao) == 1
    linha = razao[0]
    assert linha["data"]      == date(2024, 1, 10)
    assert linha["historico"] == "Entrada de caixa"
    assert linha["debito"]    == Decimal("500.00")
    assert linha["credito"]   == Decimal("0")
    assert linha["saldo"]     == Decimal("500.00")


def test_lancamento_apenas_credito(session, contas):
    caixa, receita = contas
    _lancamento(session, date(2024, 1, 15), "Pagamento efetuado",
                debito_id=receita.id, credito_id=caixa.id, valor="200.00")

    razao = LivroRazaoService(session).gerar_razao(caixa.id)

    assert len(razao) == 1
    linha = razao[0]
    assert linha["debito"]  == Decimal("0")
    assert linha["credito"] == Decimal("200.00")
    assert linha["saldo"]   == Decimal("-200.00")


def test_multiplos_lancamentos_ordem_cronologica(session, contas):
    caixa, receita = contas
    # inseridos fora de ordem para garantir que o serviço ordena por data
    _lancamento(session, date(2024, 3, 1), "Março",   debito_id=caixa.id,   credito_id=receita.id, valor="300")
    _lancamento(session, date(2024, 1, 1), "Janeiro", debito_id=caixa.id,   credito_id=receita.id, valor="100")
    _lancamento(session, date(2024, 2, 1), "Fevereiro", debito_id=receita.id, credito_id=caixa.id, valor="50")

    razao = LivroRazaoService(session).gerar_razao(caixa.id)

    assert len(razao) == 3
    assert razao[0]["historico"] == "Janeiro"
    assert razao[1]["historico"] == "Fevereiro"
    assert razao[2]["historico"] == "Março"


def test_saldo_acumulado(session, contas):
    """Débito 100 → crédito 30 → débito 50 : saldos esperados 100, 70, 120."""
    caixa, receita = contas
    _lancamento(session, date(2024, 1, 1), "D1", debito_id=caixa.id,   credito_id=receita.id, valor="100")
    _lancamento(session, date(2024, 1, 2), "C1", debito_id=receita.id, credito_id=caixa.id,   valor="30")
    _lancamento(session, date(2024, 1, 3), "D2", debito_id=caixa.id,   credito_id=receita.id, valor="50")

    razao = LivroRazaoService(session).gerar_razao(caixa.id)

    assert razao[0]["saldo"] == Decimal("100")
    assert razao[1]["saldo"] == Decimal("70")
    assert razao[2]["saldo"] == Decimal("120")
