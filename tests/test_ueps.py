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
    p = Produto(nome="Produto UEPS", estoque=Decimal("0"))
    session.add(p)
    session.flush()
    return p


# ── casos de teste ────────────────────────────────────────────────────────────

def test_lote_unico(session, produto):
    """Saída menor que o lote único: retorna um único registro com o custo do lote."""
    svc = EstoqueService(session)
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("10.00"), date(2024, 1, 1))

    lotes = svc.calcular_ueps(produto.id, Decimal("40"))

    assert len(lotes) == 1
    assert lotes[0]["quantidade"]     == Decimal("40")
    assert lotes[0]["valor_unitario"] == Decimal("10.00")
    assert lotes[0]["valor_total"]    == Decimal("400.00")


def test_multiplos_lotes(session, produto):
    """Saída que cruza dois lotes: aloca primeiro o lote mais recente (R$12) depois o mais antigo (R$10)."""
    svc = EstoqueService(session)
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("10.00"), date(2024, 1, 1))
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("12.00"), date(2024, 1, 2))

    lotes = svc.calcular_ueps(produto.id, Decimal("150"))

    assert len(lotes) == 2
    assert lotes[0]["quantidade"]     == Decimal("100")
    assert lotes[0]["valor_unitario"] == Decimal("12.00")
    assert lotes[0]["valor_total"]    == Decimal("1200.00")
    assert lotes[1]["quantidade"]     == Decimal("50")
    assert lotes[1]["valor_unitario"] == Decimal("10.00")
    assert lotes[1]["valor_total"]    == Decimal("500.00")


def test_saida_parcial(session, produto):
    """Saída anterior esgota o lote mais recente parcialmente; novo UEPS começa pelo saldo restante."""
    svc = EstoqueService(session)
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("10.00"), date(2024, 1, 1))
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("12.00"), date(2024, 1, 2))

    # Saída de 80 consome do lote R$12 (mais recente); restam 20 de R$12 + 100 de R$10
    svc.saida_produto(produto.id, Decimal("80"), Decimal("12.00"), date(2024, 1, 3))

    lotes = svc.calcular_ueps(produto.id, Decimal("60"))

    assert len(lotes) == 2
    assert lotes[0]["quantidade"]     == Decimal("20")
    assert lotes[0]["valor_unitario"] == Decimal("12.00")
    assert lotes[1]["quantidade"]     == Decimal("40")
    assert lotes[1]["valor_unitario"] == Decimal("10.00")


def test_saida_total(session, produto):
    """Saída exatamente igual ao estoque total: todos os lotes são consumidos na ordem UEPS."""
    svc = EstoqueService(session)
    svc.entrada_produto(produto.id, Decimal("50"), Decimal("8.00"),  date(2024, 2, 1))
    svc.entrada_produto(produto.id, Decimal("50"), Decimal("9.00"),  date(2024, 2, 2))
    svc.entrada_produto(produto.id, Decimal("50"), Decimal("10.00"), date(2024, 2, 3))

    lotes = svc.calcular_ueps(produto.id, Decimal("150"))

    assert len(lotes) == 3
    # Ordem UEPS: R$10 → R$9 → R$8
    assert lotes[0]["valor_unitario"] == Decimal("10.00")
    assert lotes[1]["valor_unitario"] == Decimal("9.00")
    assert lotes[2]["valor_unitario"] == Decimal("8.00")
    assert all(l["quantidade"] == Decimal("50") for l in lotes)

    valor_total = sum(l["valor_total"] for l in lotes)
    assert valor_total == Decimal("50") * Decimal("8.00") \
                        + Decimal("50") * Decimal("9.00") \
                        + Decimal("50") * Decimal("10.00")


def test_entrada_apos_saida(session, produto):
    """Saída anterior só pode consumir lotes que existiam no momento — não lotes futuros.

    Bug fixado: o algoritmo antigo aplicava total_saidas ao lote mais recente
    (Entrada 2), mesmo que a saída tivesse ocorrido antes de Entrada 2 existir.
    """
    svc = EstoqueService(session)
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("10.00"), date(2024, 1, 1))
    # Saída antes da segunda entrada: só o lote R$10 existia neste momento
    svc.saida_produto(produto.id, Decimal("30"), Decimal("10.00"), date(2024, 1, 2))
    svc.entrada_produto(produto.id, Decimal("100"), Decimal("12.00"), date(2024, 1, 3))

    # Estado correto: 70 @ R$10 + 100 @ R$12 (LIFO: topo = R$12)
    lotes = svc.calcular_ueps(produto.id, Decimal("100"))

    assert len(lotes) == 1
    assert lotes[0]["quantidade"]     == Decimal("100")
    assert lotes[0]["valor_unitario"] == Decimal("12.00")
    assert lotes[0]["valor_total"]    == Decimal("1200.00")
