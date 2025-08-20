from __future__ import annotations
from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy.orm import Session, sessionmaker
from finance_tracker.db.base import SessionLocal, engine

_session_factory: Optional[sessionmaker] = None


def make_session_factory() -> sessionmaker:
    global _session_factory
    if _session_factory is None:
        _session_factory = SessionLocal
    return _session_factory


@contextmanager
def session_scope() -> Iterator[Session]:
    """Context-managed session, commits on success, rollbacks on error."""
    factory = make_session_factory()
    session: Session = factory()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def ensure_db() -> None:
    """
    Light-weight sanity check that the DB is reachable.
    Alembic handles migrations; this just opens a connection.
    """
    with engine.connect():
        pass


@contextmanager
def get_session() -> Iterator[Session]:
    """
    Yield a SQLAlchemy Session with commit/rollback semantics.
    Usage:
        with get_session() as s:
            ...
    """
    s: Session = SessionLocal()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()