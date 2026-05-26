from __future__ import annotations
from datetime import date
from decimal import Decimal


def formatar_moeda(valor: Decimal | float | None) -> str:
    pass


def formatar_data(data: date | None) -> str:
    pass


def formatar_cnpj(cnpj: str | None) -> str:
    pass


def formatar_quantidade(qtd: Decimal | float | None, decimais: int = 4) -> str:
    pass


def moeda_para_decimal(texto: str) -> Decimal:
    pass
