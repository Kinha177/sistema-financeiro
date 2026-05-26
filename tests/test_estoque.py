from __future__ import annotations
from decimal import Decimal
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — registra todos os modelos no Base.metadata
from app.database.base import Base
from app.exceptions import ValidacaoError
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
    p = Produto(nome="Produto Teste", estoque=Decimal("0"))
    session.add(p)
    session.flush()
    return p


# ── casos de teste ────────────────────────────────────────────────────────────

def test_entrada_produto(session, produto):
    svc = EstoqueService(session)
    mov = svc.entrada_produto(produto.id, Decimal("10"), Decimal("5.00"), date(2024, 1, 1))

    assert mov.tipo       == "ENTRADA"
    assert mov.quantidade == Decimal("10")
    assert mov.produto_id == produto.id
    assert svc.saldo_estoque(produto.id) == Decimal("10")


def test_saida_valida(session, produto):
    svc = EstoqueService(session)
    svc.entrada_produto(produto.id, Decimal("20"), Decimal("5.00"), date(2024, 1, 1))

    mov = svc.saida_produto(produto.id, Decimal("8"), Decimal("5.00"), date(2024, 1, 2))

    assert mov.tipo       == "SAIDA"
    assert mov.quantidade == Decimal("8")
    assert svc.saldo_estoque(produto.id) == Decimal("12")


def test_saida_maior_que_estoque(session, produto):
    svc = EstoqueService(session)
    svc.entrada_produto(produto.id, Decimal("5"), Decimal("5.00"), date(2024, 1, 1))

    with pytest.raises(ValidacaoError, match="insuficiente"):
        svc.saida_produto(produto.id, Decimal("10"), Decimal("5.00"), date(2024, 1, 2))

    assert svc.saldo_estoque(produto.id) == Decimal("5")


def test_saldo_atualizado(session, produto):
    svc = EstoqueService(session)

    svc.entrada_produto(produto.id, Decimal("100"), Decimal("2.00"), date(2024, 1,  1))
    svc.entrada_produto(produto.id, Decimal("50"),  Decimal("2.50"), date(2024, 1,  5))
    svc.saida_produto(  produto.id, Decimal("30"),  Decimal("2.00"), date(2024, 1, 10))
    svc.saida_produto(  produto.id, Decimal("20"),  Decimal("2.00"), date(2024, 1, 15))

    assert svc.saldo_estoque(produto.id) == Decimal("100")
