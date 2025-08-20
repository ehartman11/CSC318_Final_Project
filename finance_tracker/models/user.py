from __future__ import annotations
from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base, uuid_pk


class User(Base):
    __tablename__ = "users"

    id = uuid_pk()
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_users_username", "username", unique=True),)
