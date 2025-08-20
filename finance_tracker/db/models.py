from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    String, Date, DateTime, Enum, ForeignKey, Numeric, UniqueConstraint,
    CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import AccountType, TxType, AlertType

NUM = Numeric(18, 2)  # money scale


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID string
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))

    accounts: Mapped[list["Account"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    budgets:  Mapped[list["Budget"]]  = relationship(back_populates="user", cascade="all, delete-orphan")
    goals:    Mapped[list["Goal"]]    = relationship(back_populates="user", cascade="all, delete-orphan")
    alerts:   Mapped[list["Alert"]]   = relationship(back_populates="user", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    type: Mapped[AccountType] = mapped_column(Enum(AccountType))
    balance: Mapped[Decimal] = mapped_column(NUM, default=Decimal("0.00"))

    user: Mapped["User"] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_account_user_name"),)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    kind: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_category_user_name"),)


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(NUM)  # positive; sign derives from type
    type: Mapped[TxType] = mapped_column(Enum(TxType))
    note: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    category_id: Mapped[Optional[str]] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)

    account: Mapped["Account"] = relationship(back_populates="transactions")

    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_tx_amount_nonnegative"),
        Index("ix_tx_user_date", "date"),
    )


class Budget(Base):
    __tablename__ = "budgets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    period: Mapped[str] = mapped_column(String(7))   # e.g., "2025-08"
    limit: Mapped[Decimal] = mapped_column(NUM)
    spent: Mapped[Decimal] = mapped_column(NUM, default=Decimal("0.00"))

    user: Mapped["User"] = relationship(back_populates="budgets")

    __table_args__ = (UniqueConstraint("user_id", "category_id", "period", name="uq_budget_ucp"),)


class Goal(Base):
    __tablename__ = "goals"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    target_amount: Mapped[Decimal] = mapped_column(NUM)
    deadline: Mapped[date] = mapped_column(Date)
    current: Mapped[Decimal] = mapped_column(NUM, default=Decimal("0.00"))

    user: Mapped["User"] = relationship(back_populates="goals")


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    message: Mapped[str] = mapped_column(String(160))
    kind: Mapped[AlertType] = mapped_column(Enum(AlertType))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    read: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="alerts")
