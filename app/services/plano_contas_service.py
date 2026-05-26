from __future__ import annotations
import re
from sqlalchemy.orm import Session
from app.models.conta import PlanoConta
from app.exceptions import ValidacaoError

_TIPOS     = ("ANALITICA", "SINTETICA")
_NATUREZAS = ("DEVEDORA", "CREDORA")
_COD_RE    = re.compile(r'^\d+(\.\d+)*$')


class PlanoContasService:
    """Regras de negócio do Plano de Contas."""

    def __init__(self, session: Session) -> None:
        self._db = session

    # ── consultas ─────────────────────────────────────────────────────────

    def listar_todas(self) -> list[PlanoConta]:
        return (
            self._db.query(PlanoConta)
            .order_by(PlanoConta.codigo)
            .all()
        )

    def listar_analiticas(self) -> list[PlanoConta]:
        return (
            self._db.query(PlanoConta)
            .filter(PlanoConta.tipo == "ANALITICA")
            .order_by(PlanoConta.codigo)
            .all()
        )

    def buscar_por_id(self, conta_id: int) -> PlanoConta | None:
        return self._db.get(PlanoConta, conta_id)

    def buscar_por_codigo(self, codigo: str) -> PlanoConta | None:
        return (
            self._db.query(PlanoConta)
            .filter(PlanoConta.codigo == codigo.strip())
            .first()
        )

    def pesquisar(self, termo: str) -> list[PlanoConta]:
        t = f"%{termo}%"
        return (
            self._db.query(PlanoConta)
            .filter(
                PlanoConta.codigo.ilike(t) | PlanoConta.nome.ilike(t)
            )
            .order_by(PlanoConta.codigo)
            .all()
        )

    # ── escrita ───────────────────────────────────────────────────────────

    def criar(self, dados: dict) -> PlanoConta:
        self._validar(dados, exclude_id=None)
        conta = PlanoConta(
            codigo=dados["codigo"].strip(),
            nome=dados["nome"].strip(),
            tipo=dados["tipo"],
            natureza=dados["natureza"],
            conta_pai_id=dados.get("conta_pai_id"),
        )
        self._db.add(conta)
        self._db.flush()
        return conta

    def atualizar(self, conta_id: int, dados: dict) -> PlanoConta:
        conta = self.buscar_por_id(conta_id)
        if conta is None:
            raise ValidacaoError("Conta não encontrada.")

        self._validar(dados, exclude_id=conta_id)

        novo_pai_id = dados.get("conta_pai_id")
        if novo_pai_id is not None:
            self._verificar_hierarquia_circular(conta_id, novo_pai_id)

        conta.codigo       = dados["codigo"].strip()
        conta.nome         = dados["nome"].strip()
        conta.tipo         = dados["tipo"]
        conta.natureza     = dados["natureza"]
        conta.conta_pai_id = novo_pai_id
        self._db.flush()
        return conta

    def excluir(self, conta_id: int) -> None:
        conta = self.buscar_por_id(conta_id)
        if conta is None:
            raise ValidacaoError("Conta não encontrada.")

        n_subcontas = (
            self._db.query(PlanoConta)
            .filter(PlanoConta.conta_pai_id == conta_id)
            .count()
        )
        if n_subcontas > 0:
            raise ValidacaoError(
                f"Não é possível excluir: a conta possui {n_subcontas} "
                f"subconta(s). Exclua-as primeiro."
            )

        from app.models.lancamento import ItemLancamento
        em_uso = (
            self._db.query(ItemLancamento)
            .filter(
                (ItemLancamento.conta_debito_id  == conta_id) |
                (ItemLancamento.conta_credito_id == conta_id)
            )
            .first()
        )
        if em_uso:
            raise ValidacaoError(
                "Não é possível excluir: a conta está referenciada "
                "em lançamentos contábeis."
            )

        self._db.delete(conta)
        self._db.flush()

    # ── validação ─────────────────────────────────────────────────────────

    def _validar(self, dados: dict, *, exclude_id: int | None) -> None:
        codigo   = (dados.get("codigo") or "").strip()
        nome     = (dados.get("nome")   or "").strip()
        tipo     = dados.get("tipo",     "")
        natureza = dados.get("natureza", "")

        if not codigo:
            raise ValidacaoError("Código é obrigatório.")
        if not _COD_RE.match(codigo):
            raise ValidacaoError(
                "Código inválido. Use somente números separados por pontos "
                "(ex: 1, 1.1, 1.1.01)."
            )
        if len(codigo) > 20:
            raise ValidacaoError("Código deve ter no máximo 20 caracteres.")
        if not nome:
            raise ValidacaoError("Nome é obrigatório.")
        if len(nome) > 200:
            raise ValidacaoError("Nome deve ter no máximo 200 caracteres.")
        if tipo not in _TIPOS:
            raise ValidacaoError(
                f"Tipo inválido. Valores aceitos: {', '.join(_TIPOS)}."
            )
        if natureza not in _NATUREZAS:
            raise ValidacaoError(
                f"Natureza inválida. Valores aceitos: {', '.join(_NATUREZAS)}."
            )

        existente = self.buscar_por_codigo(codigo)
        if existente and existente.id != exclude_id:
            raise ValidacaoError(f"O código '{codigo}' já está em uso.")

    def _verificar_hierarquia_circular(
        self, conta_id: int, pai_id: int
    ) -> None:
        visited: set[int] = set()
        cur = pai_id
        while cur is not None:
            if cur == conta_id:
                raise ValidacaoError(
                    "Hierarquia circular: a conta pai não pode ser "
                    "descendente da própria conta."
                )
            if cur in visited:
                break
            visited.add(cur)
            pai = self.buscar_por_id(cur)
            cur = pai.conta_pai_id if pai else None
