from __future__ import annotations
from datetime import date
from decimal import Decimal, InvalidOperation
import re


def _fmt_decimal(valor, decimais: int = 2) -> str:
    if valor is None:
        return "0," + "0" * decimais
    d = Decimal(str(valor))
    neg = d < 0
    d = abs(d)
    inteiro, dec = f"{d:.{decimais}f}".split(".")
    grupos: list[str] = []
    s = inteiro
    while len(s) > 3:
        grupos.insert(0, s[-3:])
        s = s[:-3]
    grupos.insert(0, s)
    result = ".".join(grupos) + "," + dec
    return f"-{result}" if neg else result


def formatar_moeda(valor: Decimal | float | None) -> str:
    """Retorna 'R$ 1.234,56'."""
    return f"R$ {_fmt_decimal(valor, 2)}"


def formatar_numero(valor: Decimal | float | None, decimais: int = 2) -> str:
    """Retorna '1.234,56' (sem prefixo R$)."""
    return _fmt_decimal(valor, decimais)


def formatar_data(data: date | None) -> str:
    """Retorna 'dd/mm/yyyy' ou string vazia."""
    return data.strftime("%d/%m/%Y") if data else ""


def formatar_cnpj(cnpj: str | None) -> str:
    """Retorna CNPJ no formato '00.000.000/0000-00'."""
    if not cnpj:
        return ""
    digits = re.sub(r"\D", "", cnpj)
    if len(digits) != 14:
        return cnpj
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def formatar_quantidade(qtd: Decimal | float | None, decimais: int = 4) -> str:
    """Retorna quantidade no formato '1.000,0000'."""
    return _fmt_decimal(qtd, decimais)


def moeda_para_decimal(texto: str) -> Decimal:
    """Converte 'R$ 1.234,56' ou '1.234,56' para Decimal."""
    if not texto:
        return Decimal("0")
    limpo = re.sub(r"[R$\s]", "", texto).replace(".", "").replace(",", ".")
    try:
        return Decimal(limpo)
    except InvalidOperation:
        return Decimal("0")
