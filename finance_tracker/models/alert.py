from __future__ import annotations
from decimal import Decimal
import enum

from sqlalchemy import String, ForeignKey, Enum as SAEnum, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, uuid_pk


class AlertKind(enum.Enum):
    BALANCE_BELOW = "balance_below"
    CATEGORY_OVERSPEND = "category_overspend"
    GOAL_PROGRESS = "goal_progress"


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id = uuid_pk()
    kind: Mapped[AlertKind] = mapped_column(SAEnum(AlertKind, name="alertkind"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    goal_id: Mapped[str | None] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"))

    threshold_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    note: Mapped[str] = mapped_column(String(240), default="", nullable=False)

    account = relationship("Account", passive_deletes=True)
    category = relationship("Category", passive_deletes=True)
    goal = relationship("Goal", passive_deletes=True)