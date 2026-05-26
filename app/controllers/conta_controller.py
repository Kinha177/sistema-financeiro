from __future__ import annotations
from app.database.connection import get_session
from app.models.conta import PlanoConta
from app.services.plano_contas_service import PlanoContasService


class ContaController:
    """Camada de apresentação para Plano de Contas.

    Cada método abre uma sessão, executa a operação no service,
    faz commit e fecha a sessão. Erros de validação propagam para a view.
    """

    def _run(self, fn):
        session = get_session()
        try:
            svc    = PlanoContasService(session)
            result = fn(svc)
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ── consultas ─────────────────────────────────────────────────────────

    def listar_todas(self) -> list[PlanoConta]:
        return self._run(lambda svc: svc.listar_todas())

    def listar_analiticas(self) -> list[PlanoConta]:
        return self._run(lambda svc: svc.listar_analiticas())

    def buscar_por_id(self, conta_id: int) -> PlanoConta | None:
        return self._run(lambda svc: svc.buscar_por_id(conta_id))

    def pesquisar(self, termo: str) -> list[PlanoConta]:
        return self._run(lambda svc: svc.pesquisar(termo))

    # ── escrita ───────────────────────────────────────────────────────────

    def criar(self, dados: dict) -> PlanoConta:
        return self._run(lambda svc: svc.criar(dados))

    def atualizar(self, conta_id: int, dados: dict) -> PlanoConta:
        return self._run(lambda svc: svc.atualizar(conta_id, dados))

    def excluir(self, conta_id: int) -> None:
        return self._run(lambda svc: svc.excluir(conta_id))
