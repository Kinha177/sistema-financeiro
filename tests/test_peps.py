from __future__ import annotations
from decimal import Decimal
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.database.base import Base
from app.models.produto import Produto
from app.services.estoque_service import EstoqueService


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
def produto(session):
    p = Produto(nome="Produto PEPS", estoque=Decimal("0"))
    session.add(p)
    session.flush()
    return p


# ── casos de teste ────────────────────────────────────────────────────────────

def test_lote_unico(session, produto):
    """Saída menor que o lote único: retorna um único registro com o custo do lote."""
    svc = EstoqueService(session)
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("10.00"), date(2024, 1, 1))

    lotes = svc.calcular_peps(produto.id, Decimal("40"))

    assert len(lotes) == 1
    assert lotes[0]["quantidade"]     == Decimal("40")
    assert lotes[0]["valor_unitario"] == Decimal("10.00")
    assert lotes[0]["valor_total"]    == Decimal("400.00")


def test_multiplos_lotes(session, produto):
    """Saída que cruza dois lotes: aloca primeiro o lote mais antigo (R$10) depois o mais novo (R$12)."""
    svc = EstoqueService(session)
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("10.00"), date(2024, 1, 1))
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("12.00"), date(2024, 1, 2))

    lotes = svc.calcular_peps(produto.id, Decimal("150"))

    assert len(lotes) == 2
    assert lotes[0]["quantidade"]     == Decimal("100")
    assert lotes[0]["valor_unitario"] == Decimal("10.00")
    assert lotes[0]["valor_total"]    == Decimal("1000.00")
    assert lotes[1]["quantidade"]     == Decimal("50")
    assert lotes[1]["valor_unitario"] == Decimal("12.00")
    assert lotes[1]["valor_total"]    == Decimal("600.00")


def test_consumo_parcial(session, produto):
    """Saída anterior esgota o primeiro lote parcialmente; novo PEPS começa pelo saldo restante."""
    svc = EstoqueService(session)
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("10.00"), date(2024, 1, 1))
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("12.00"), date(2024, 1, 2))

    # Saída registrada de 80 consome do lote R$10; restam 20 de R$10 + 100 de R$12
    svc.saida_produto(produto.id, Decimal("80"), Decimal("10.00"), date(2024, 1, 3))

    lotes = svc.calcular_peps(produto.id, Decimal("60"))

    assert len(lotes) == 2
    assert lotes[0]["quantidade"]     == Decimal("20")
    assert lotes[0]["valor_unitario"] == Decimal("10.00")
    assert lotes[1]["quantidade"]     == Decimal("40")
    assert lotes[1]["valor_unitario"] == Decimal("12.00")


def test_consumo_total(session, produto):
    """Saída exatamente igual ao estoque total: todos os lotes são consumidos integralmente."""
    svc = EstoqueService(session)
    svc.entrada_produto(produto.id, Decimal("50"), Decimal("8.00"),  date(2024, 2, 1))
    svc.entrada_produto(produto.id, Decimal("50"), Decimal("9.00"),  date(2024, 2, 2))
    svc.entrada_produto(produto.id, Decimal("50"), Decimal("10.00"), date(2024, 2, 3))

    lotes = svc.calcular_peps(produto.id, Decimal("150"))

    assert len(lotes) == 3
    assert lotes[0]["quantidade"] == Decimal("50")
    assert lotes[1]["quantidade"] == Decimal("50")
    assert lotes[2]["quantidade"] == Decimal("50")

    valor_total = sum(l["valor_total"] for l in lotes)
    assert valor_total == Decimal("50") * Decimal("8.00") \
                        + Decimal("50") * Decimal("9.00") \
                        + Decimal("50") * Decimal("10.00")
