from __future__ import annotations
from datetime import date
from decimal import Decimal
import enum

from sqlalchemy import String, Numeric, ForeignKey, Date, Enum as SAEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, uuid_pk


class TransactionType(enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id = uuid_pk()
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    budget_item_id: Mapped[str | None] = mapped_column(ForeignKey("budget_items.id"), nullable=True)

    date: Mapped[date] = mapped_column(Date, nullable=False)
    type: Mapped[TransactionType] = mapped_column(SAEnum(TransactionType, name="transactiontype"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(240), default="", nullable=False)
    external_ref: Mapped[str | None] = mapped_column(String(120))

    account = relationship("Account", back_populates="transactions", passive_deletes=True)
    category = relationship("Category", back_populates="transactions")
    budget_item = relationship("BudgetItem")

    __table_args__ = (
        Index("ix_transactions_date", "date"),
        Index("ix_transactions_account_date", "account_id", "date"),
        # These helper indexes were added in a later migration; keep them if present
        Index("ix_transactions_category_id", "category_id"),
        Index("ix_transactions_account_id", "account_id"),
    )