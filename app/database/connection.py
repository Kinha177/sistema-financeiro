from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DB_PATH = _PROJECT_ROOT / "data" / "sisgest.db"
_ENGINE = create_engine(f"sqlite:///{_DB_PATH}", echo=False)
_SessionFactory = sessionmaker(bind=_ENGINE, expire_on_commit=False)


def init_db() -> None:
    """Aplica todas as migrations pendentes (cria o schema na primeira execução)."""
    import app.models  # noqa: F401
    from alembic.config import Config
    from alembic import command

    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    alembic_cfg = Config(str(_PROJECT_ROOT / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{_DB_PATH}")
    command.upgrade(alembic_cfg, "head")


def get_session() -> Session:
    return _SessionFactory()
