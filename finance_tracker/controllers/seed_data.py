from __future__ import annotations
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from finance_tracker.db.base import SessionLocal
from finance_tracker.models import (
    User,
    Account, AccountType,
    Category, CategoryType,
    Budget, BudgetItem,
    Transaction, TransactionType,
    Goal, Alert, AlertKind,
    RecurringTransaction, Frequency,
)


def get_or_create(s: Session, model, defaults: dict | None = None, **kw):
    """filter_by(**kw) must use literals (e.g., user_id=..., not user=User(...))."""
    obj = s.execute(select(model).filter_by(**kw)).scalar_one_or_none()
    if obj:
        return obj, False
    obj = model(**kw, **(defaults or {}))
    s.add(obj)
    return obj, True


def seed() -> None:
    with SessionLocal() as s:
        # User (parent for accounts)
        demo_user, _ = get_or_create(
            s, User, username="demo",
            defaults=dict(password_hash="not-a-real-hash")
        )
        s.flush(); s.refresh(demo_user)
        assert demo_user.id, "User id missing after flush"

        # Helper for accounts to ensure both starting_balance and balance are set
        def account_defaults(kind: AccountType, start: Decimal):
            return {
                "type": kind,
                "currency": "USD",
                "starting_balance": start,
                "balance": start,
            }

        # Accounts (require user_id)
        checking, _ = get_or_create(
            s, Account,
            user_id=demo_user.id, name="Main Checking",
            defaults=account_defaults(AccountType.CHECKING, Decimal("1250.00")),
        )
        savings, _ = get_or_create(
            s, Account,
            user_id=demo_user.id, name="Emergency Fund",
            defaults=account_defaults(AccountType.SAVINGS, Decimal("5000.00")),
        )
        s.flush(); s.refresh(checking); s.refresh(savings)
        assert checking.id and savings.id, "Account ids missing after flush"

        # Categories
        salary, _    = get_or_create(s, Category, name="Salary",    defaults=dict(type=CategoryType.INCOME))
        groceries, _ = get_or_create(s, Category, name="Groceries", defaults=dict(type=CategoryType.EXPENSE))
        rent, _      = get_or_create(s, Category, name="Rent",      defaults=dict(type=CategoryType.EXPENSE))
        utilities, _ = get_or_create(s, Category, name="Utilities", defaults=dict(type=CategoryType.EXPENSE))
        s.flush()
        for c in (salary, groceries, rent, utilities):
            assert c.id, f"Category id missing for {c.name}"

        # Budget
        monthly_budget, _ = get_or_create(
            s, Budget, name="Default Monthly", defaults=dict(currency="USD")
        )
        s.flush(); s.refresh(monthly_budget)
        assert monthly_budget.id, "Budget id missing after flush"

        # Budget items (need budget_id + category_id)
        bi_groceries, _ = get_or_create(
            s, BudgetItem,
            budget_id=monthly_budget.id, category_id=groceries.id,
            defaults=dict(monthly_limit=Decimal("450.00")),
        )
        bi_util, _ = get_or_create(
            s, BudgetItem,
            budget_id=monthly_budget.id, category_id=utilities.id,
            defaults=dict(monthly_limit=Decimal("200.00")),
        )
        s.flush(); s.refresh(bi_groceries); s.refresh(bi_util)
        assert bi_groceries.id and bi_util.id, "BudgetItem ids missing after flush"

        # Transactions
        today = date.today()
        first_of_month = today.replace(day=1)

        tx_rows = [
            dict(account=checking, category=salary,    budget_item=None,
                 date=first_of_month,                   type=TransactionType.CREDIT, amount=Decimal("3500.00"),
                 description="Monthly salary"),
            dict(account=checking, category=rent,      budget_item=None,
                 date=first_of_month + timedelta(days=1), type=TransactionType.DEBIT,  amount=Decimal("-1500.00"),
                 description="Monthly rent"),
            dict(account=checking, category=groceries, budget_item=bi_groceries,
                 date=first_of_month + timedelta(days=3), type=TransactionType.DEBIT,  amount=Decimal("-86.43"),
                 description="Groceries – market"),
            dict(account=checking, category=utilities, budget_item=bi_util,
                 date=first_of_month + timedelta(days=10), type=TransactionType.DEBIT, amount=Decimal("-95.32"),
                 description="Electric bill"),
        ]

        for tx in tx_rows:
            s.add(Transaction(
                account_id=tx["account"].id,
                category_id=tx["category"].id if tx["category"] else None,
                budget_item_id=tx["budget_item"].id if tx["budget_item"] else None,
                date=tx["date"],
                type=tx["type"],
                amount=tx["amount"],
                description=tx["description"],
            ))
        s.flush()

        # Goal
        goal, _ = get_or_create(
            s, Goal, name="Emergency Fund 10k",
            defaults=dict(account_id=savings.id, target_amount=Decimal("10000.00"), target_date=None),
        )
        s.flush(); s.refresh(goal)
        assert goal.id, "Goal id missing after flush"

        # Alerts
        get_or_create(
            s, Alert,
            kind=AlertKind.BALANCE_BELOW, account_id=checking.id,
            defaults=dict(is_active=True, threshold_amount=Decimal("500.00"), note="Low balance warning"),
        )
        get_or_create(
            s, Alert,
            kind=AlertKind.CATEGORY_OVERSPEND, category_id=groceries.id,
            defaults=dict(is_active=True, threshold_amount=Decimal("400.00"), note="Groceries overspend"),
        )
        s.flush()

        # Recurring transaction
        get_or_create(
            s, RecurringTransaction,
            account_id=checking.id, category_id=utilities.id, amount=Decimal("-95.32"),
            defaults=dict(
                next_date=first_of_month + timedelta(days=35),
                frequency=Frequency.MONTHLY,
                description="Electric bill",
                active=True,
            ),
        )

        s.commit()
        print("Seed complete ✔")


if __name__ == "__main__":
    seed()
