from __future__ import annotations
from decimal import Decimal
from app.models.produto import Produto
from app.models.movimento_estoque import MovimentoEstoque


class EstoqueService:
    """Regras de negócio do controle de estoque."""

    def calcular_custo_medio(self, produto_id: int) -> Decimal:
        pass

    def calcular_peps(self, produto_id: int) -> list[dict]:
        """Primeiro a Entrar, Primeiro a Sair."""
        pass

    def calcular_ueps(self, produto_id: int) -> list[dict]:
        """Último a Entrar, Primeiro a Sair."""
        pass

    def atualizar_saldo(self, produto: Produto, quantidade: Decimal, tipo: str) -> None:
        pass

    def verificar_estoque_minimo(self) -> list[Produto]:
        pass

    def valorar_estoque_total(self, metodo: str = "MEDIO") -> Decimal:
        pass
