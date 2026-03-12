# Standard library
from collections.abc import Generator
from contextlib import contextmanager

# Third-party
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

# Local
from app.config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

_engine_kwargs: dict = {
    "pool_pre_ping": True,
}
if not _is_sqlite:
    _engine_kwargs["pool_size"] = 10
    _engine_kwargs["max_overflow"] = 20

engine = create_engine(
    settings.DATABASE_URL,
    **_engine_kwargs,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base for all ORM models.
    """

    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency implementing Unit of Work.

    Yields a session for the duration of the request.
    Commits on clean exit; rolls back on any exception.
    Guarantees the session is closed either way.
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()  # success — persist all
    except Exception:
        db.rollback()  # failure — undo all
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager version of get_db for use in
    Celery tasks and scripts outside of FastAPI.

    Usage:
        with get_db_context() as db:
            InvoiceService(db).create_invoice(...)
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
