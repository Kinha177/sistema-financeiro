from __future__ import annotations
from datetime import date
from decimal import Decimal
import re


def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ usando o algoritmo oficial dos dígitos verificadores."""
    digits = re.sub(r"\D", "", cnpj)
    if len(digits) != 14 or len(set(digits)) == 1:
        return False

    def _digito(d: str, pesos: list[int]) -> int:
        resto = sum(int(c) * p for c, p in zip(d, pesos)) % 11
        return 0 if resto < 2 else 11 - resto

    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    p2 = [6] + p1
    return digits[12] == str(_digito(digits[:12], p1)) and \
           digits[13] == str(_digito(digits[:13], p2))


def validar_data_periodo(data_inicio: date, data_fim: date) -> bool:
    """Retorna True se data_inicio <= data_fim."""
    return data_inicio <= data_fim


def validar_valor_positivo(valor: Decimal | float) -> bool:
    """Retorna True se valor > 0."""
    return Decimal(str(valor)) > Decimal("0")


def validar_codigo_conta(codigo: str) -> bool:
    """Valida código de conta contábil (ex: '1', '1.1', '1.1.01')."""
    return bool(re.fullmatch(r"\d+(\.\d+)*", codigo.strip()))
