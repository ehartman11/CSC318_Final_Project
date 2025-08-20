from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Iterable, Optional

from sqlalchemy import func, select, and_, or_, case
from sqlalchemy.orm import Session

from ..db.base import SessionLocal
from ..models.account import Account
from ..models.category import Category, CategoryType
from ..models.transaction import Transaction
from ..models.budget import Budget, BudgetItem


# Helpers
def month_bounds(year: int, month: int) -> tuple[date, date]:
    from calendar import monthrange
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    return start, end


# DTOs
@dataclass(frozen=True)
class BalanceRow:
    account_id: str
    account_name: str
    balance: Decimal


@dataclass(frozen=True)
class CategorySpendRow:
    category_id: str
    category_name: str
    spend: Decimal  # positive number representing money out


@dataclass(frozen=True)
class Cashflow:
    income: Decimal
    expenses: Decimal  # positive number representing money out
    net: Decimal       # income - expenses


@dataclass(frozen=True)
class BudgetUtilizationRow:
    budget_id: str
    budget_name: str
    category_id: str
    category_name: str
    monthly_limit: Decimal
    spent: Decimal
    utilization: Optional[Decimal]


# Reports
def account_balances(s: Session, as_of: Optional[date] = None) -> list[BalanceRow]:
    """Compute balance per account as starting_balance + sum(transactions.amount up to as_of)."""
    tx_filter = []
    if as_of is not None:
        tx_filter.append(Transaction.date <= as_of)

    tx_sum = func.coalesce(func.sum(Transaction.amount), 0)

    # left join so accounts without tx still show up
    stmt = (
        select(
            Account.id,
            Account.name,
            (Account.starting_balance + tx_sum).label("balance"),
        )
        .join(Transaction, Transaction.account_id == Account.id, isouter=True)
        .where(and_(*tx_filter) if tx_filter else True)
        .group_by(Account.id, Account.name, Account.starting_balance)
        .order_by(Account.name)
    )
    rows = s.execute(stmt).all()
    return [BalanceRow(r[0], r[1], Decimal(str(r[2]))) for r in rows]


def monthly_spend_by_category(s: Session, year: int, month: int) -> list[CategorySpendRow]:
    start, end = month_bounds(year, month)

    # Only expenses; treat spend as positive number = -sum(negative amounts)
    spend_expr = -func.coalesce(func.sum(
        case((Transaction.amount < 0, Transaction.amount), else_=0)
    ), 0)

    stmt = (
        select(
            Category.id,
            Category.name,
            spend_expr.label("spend")
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            and_(
                Category.type == CategoryType.EXPENSE,
                Transaction.date >= start,
                Transaction.date <= end,
                )
        )
        .group_by(Category.id, Category.name)
        .having(spend_expr > 0)
        .order_by(spend_expr.desc(), Category.name)
    )
    rows = s.execute(stmt).all()
    return [CategorySpendRow(r[0], r[1], Decimal(str(r[2]))) for r in rows]


def cashflow(s: Session, start: date, end: date) -> Cashflow:
    # Income = sum of positive amounts; Expenses = -sum of negative amounts
    income_expr = func.coalesce(func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)), 0)
    out_expr = -func.coalesce(func.sum(case((Transaction.amount < 0, Transaction.amount), else_=0)), 0)

    stmt = (
        select(income_expr.label("income"), out_expr.label("expenses"))
        .where(and_(Transaction.date >= start, Transaction.date <= end))
    )
    income, expenses = s.execute(stmt).one()
    income = Decimal(str(income))
    expenses = Decimal(str(expenses))
    return Cashflow(income=income, expenses=expenses, net=income - expenses)


def budget_utilization(s: Session, year: int, month: int) -> list[BudgetUtilizationRow]:
    start, end = month_bounds(year, month)

    # Sum of negative amounts in the month for each category under each budget item
    spend_expr = -func.coalesce(func.sum(
        case((Transaction.amount < 0, Transaction.amount), else_=0)
    ), 0)

    stmt = (
        select(
            Budget.id.label("budget_id"),
            Budget.name.label("budget_name"),
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            BudgetItem.monthly_limit.label("monthly_limit"),
            spend_expr.label("spent"),
        )
        .join(BudgetItem, BudgetItem.budget_id == Budget.id)
        .join(Category, Category.id == BudgetItem.category_id)
        .join(Transaction, Transaction.category_id == Category.id, isouter=True)
        .where(
            and_(
                or_(Transaction.id.is_(None), and_(Transaction.date >= start, Transaction.date <= end)),
                Category.type == CategoryType.EXPENSE,
                )
        )
        .group_by(
            Budget.id, Budget.name,
            Category.id, Category.name,
            BudgetItem.monthly_limit
        )
        .order_by(Budget.name, Category.name)
    )

    rows = s.execute(stmt).all()
    out: list[BudgetUtilizationRow] = []
    for b_id, b_name, c_id, c_name, limit, spent in rows:
        limit_d = Decimal(str(limit)) if limit is not None else Decimal("0")
        spent_d = Decimal(str(spent))
        util = (spent_d / limit_d) if limit_d and spent_d is not None else None
        out.append(BudgetUtilizationRow(
            budget_id=b_id,
            budget_name=b_name,
            category_id=c_id,
            category_name=c_name,
            monthly_limit=limit_d,
            spent=spent_d,
            utilization=util,
        ))
    return out


# Convenience runner (optional)
def demo_print(year: int, month: int) -> None:
    with SessionLocal() as s:
        print("Balances:")
        for row in account_balances(s):
            print(f"  {row.account_name}: {row.balance}")

        print("\nMonthly spend by category:")
        for row in monthly_spend_by_category(s, year, month):
            print(f"  {row.category_name}: {row.spend}")

        start, end = month_bounds(year, month)
        cf = cashflow(s, start, end)
        print(f"\nCashflow {start}..{end}: income={cf.income} expenses={cf.expenses} net={cf.net}")

        print("\nBudget utilization:")
        for row in budget_utilization(s, year, month):
            util_str = f"{(row.utilization*100):.1f}%" if row.utilization is not None else "—"
            print(f"  [{row.budget_name}] {row.category_name}: {row.spent}/{row.monthly_limit} ({util_str})")