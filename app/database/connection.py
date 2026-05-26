from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database.base import Base

_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "sisgest.db"
_ENGINE = create_engine(f"sqlite:///{_DB_PATH}", echo=False)
_SessionFactory = sessionmaker(bind=_ENGINE)


def init_db() -> None:
    import app.models  # noqa: F401 — registers all models with Base
    Base.metadata.create_all(_ENGINE)


def get_session() -> Session:
    return _SessionFactory()
