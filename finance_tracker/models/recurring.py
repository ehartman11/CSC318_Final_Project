from __future__ import annotations
from datetime import date
from decimal import Decimal
import enum

from sqlalchemy import String, Numeric, ForeignKey, Date, Enum as SAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, uuid_pk


class Frequency(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class RecurringTransaction(Base, TimestampMixin):
    __tablename__ = "recurring_transactions"

    id = uuid_pk()
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"))
    next_date: Mapped[date] = mapped_column(Date, nullable=False)
    frequency: Mapped[Frequency] = mapped_column(SAEnum(Frequency, name="frequency"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(240), default="", nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    account = relationship("Account", passive_deletes=True)
    category = relationship("Category")