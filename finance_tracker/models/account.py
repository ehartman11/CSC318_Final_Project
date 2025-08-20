from __future__ import annotations
from decimal import Decimal
from sqlalchemy import String, Numeric, Enum, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base, TimestampMixin, uuid_pk
import enum


class AccountType(enum.Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    CASH = "cash"
    BROKERAGE = "brokerage"


class Account(Base, TimestampMixin):
    __tablename__ = "accounts"

    id = uuid_pk()

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="accounts")

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    type: Mapped[AccountType] = mapped_column(Enum(AccountType, name="accounttype"), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    starting_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)

    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)

    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan", single_parent=True)
    goals = relationship("Goal", back_populates="account", cascade="all", passive_deletes=True)

    __table_args__ = (Index("ix_accounts_name", "name"),)
