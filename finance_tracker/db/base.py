from __future__ import annotations
from datetime import datetime
import uuid
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from sqlalchemy import create_engine, String, DateTime, text
from ..config.loader import db_url, db_echo


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"), nullable=False
    )


# Cross‑DB UUID primary key helper (works on SQLite and Postgres)
def uuid_pk():
    return mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


# Engine & Session
engine = create_engine(db_url(), echo=db_echo(), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)