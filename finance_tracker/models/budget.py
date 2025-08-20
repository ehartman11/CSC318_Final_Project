from __future__ import annotations
from decimal import Decimal

from sqlalchemy import String, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, uuid_pk


class Budget(Base, TimestampMixin):
    __tablename__ = "budgets"

    id = uuid_pk()
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    items = relationship(
        "BudgetItem",
        back_populates="budget",
        cascade="all, delete-orphan",
        single_parent=True,
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint("name"),
    )


class BudgetItem(Base, TimestampMixin):
    __tablename__ = "budget_items"

    id = uuid_pk()
    budget_id: Mapped[str] = mapped_column(
        ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[str] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    monthly_limit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    budget = relationship("Budget", back_populates="items", passive_deletes=True)
    category = relationship("Category", back_populates="budget_items")

    __table_args__ = (
        UniqueConstraint("budget_id", "category_id", name="uq_budgetitem_budget_category"),
    )