"""SQLAlchemy engine and session factory.

Uses DATABASE_URL (Postgres) when set; otherwise the existing SQLite DATABASE_PATH
so Render / local keep working without a separate database.
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.base import Base

logger = logging.getLogger(__name__)

_engine = None
SessionLocal: sessionmaker[Session] | None = None


def sqlalchemy_url() -> str:
    """Return the SQLAlchemy URL for the mandi cache."""
    settings = get_settings()
    url = (settings.database_url or "").strip()
    if url:
        return url
    path = Path(settings.database_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path.as_posix()}"


def get_engine():
    """Lazily create a singleton engine."""
    global _engine
    if _engine is None:
        url = sqlalchemy_url()
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        _engine = create_engine(url, future=True, pool_pre_ping=True, connect_args=connect_args)
        logger.info("SQLAlchemy engine ready url=%s", url.split("@")[-1])
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Return the sessionmaker, creating it if needed."""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)
    return SessionLocal


def get_session() -> Generator[Session, None, None]:
    """Yield a short-lived session (caller must not keep it open)."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_sqlalchemy() -> None:
    """Create mandi_prices (and any other SQLAlchemy tables) if missing."""
    # Import models so metadata is populated.
    import app.models.mandi_price  # noqa: F401

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("SQLAlchemy tables ensured (mandi_prices)")
