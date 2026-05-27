from __future__ import annotations
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parents[2]


_PROJECT_ROOT = _base_dir()
_DB_PATH = _PROJECT_ROOT / "data" / "sisgest.db"
_ENGINE = create_engine(f"sqlite:///{_DB_PATH}", echo=False)
_SessionFactory = sessionmaker(bind=_ENGINE, expire_on_commit=False)


def init_db() -> None:
    """Cria/migra o schema do banco de dados.

    Em desenvolvimento aplica as migrations Alembic; no executável
    distribuído (frozen) usa create_all para evitar dependência do
    diretório de scripts Alembic.
    """
    import app.models  # noqa: F401 — registra todos os models no metadata

    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if getattr(sys, "frozen", False):
        from app.database.base import Base
        Base.metadata.create_all(_ENGINE)
    else:
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config(str(_PROJECT_ROOT / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{_DB_PATH}")
        command.upgrade(alembic_cfg, "head")


def get_session() -> Session:
    return _SessionFactory()
