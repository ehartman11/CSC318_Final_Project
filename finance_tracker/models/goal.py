from __future__ import annotations
from datetime import date
from decimal import Decimal

from sqlalchemy import String, Numeric, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, uuid_pk


class Goal(Base, TimestampMixin):
    __tablename__ = "goals"

    id = uuid_pk()
    account_id: Mapped[str | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    account = relationship(
        "Account",
        back_populates="goals",
        passive_deletes=True,
    )