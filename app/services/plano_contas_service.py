from __future__ import annotations
from app.models.conta import Conta


class PlanoContasService:
    """Regras de negócio do Plano de Contas."""

    def montar_arvore(self, contas: list[Conta]) -> list[dict]:
        pass

    def validar_codigo(self, codigo: str) -> bool:
        pass

    def codigo_disponivel(self, codigo: str) -> bool:
        pass

    def pode_excluir(self, conta: Conta) -> bool:
        pass

    def importar_plano_padrao(self) -> list[Conta]:
        pass
