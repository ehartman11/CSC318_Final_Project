from __future__ import annotations
import enum

from sqlalchemy import String, Enum as SAEnum, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, uuid_pk


class CategoryType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id = uuid_pk()
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    type: Mapped[CategoryType] = mapped_column(SAEnum(CategoryType, name="categorytype"), nullable=False)

    transactions = relationship("Transaction", back_populates="category")
    budget_items = relationship("BudgetItem", back_populates="category")

    __table_args__ = (
        Index("ix_categories_name", "name"),
        UniqueConstraint("name"),
    )