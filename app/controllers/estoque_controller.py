from __future__ import annotations
from app.models.produto import Produto
from app.models.movimento_estoque import MovimentoEstoque


class EstoqueController:
    def listar_produtos(self) -> list[Produto]:
        pass

    def buscar_produto(self, produto_id: int) -> Produto | None:
        pass

    def criar_produto(self, dados: dict) -> Produto:
        pass

    def atualizar_produto(self, produto_id: int, dados: dict) -> Produto | None:
        pass

    def registrar_entrada(self, dados: dict) -> MovimentoEstoque:
        pass

    def registrar_saida(self, dados: dict) -> MovimentoEstoque:
        pass

    def listar_movimentos(self, produto_id: int | None = None) -> list[MovimentoEstoque]:
        pass

    def calcular_peps(self, produto_id: int) -> list[dict]:
        pass

    def calcular_ueps(self, produto_id: int) -> list[dict]:
        pass
