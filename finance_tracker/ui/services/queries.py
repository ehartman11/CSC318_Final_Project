from __future__ import annotations
from typing import Tuple, List, Dict, Optional, Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from finance_tracker.models import Account, Category, Transaction, TransactionType
from finance_tracker.ui.models.filters import TransactionFilters


def list_categories(session: Session) -> List[Tuple[str, str]]:
    return [(c.id, c.name) for c in session.query(Category).order_by(Category.name.asc()).all()]


def accounts_choices(session: Session) -> List[Dict[str, str]]:
    """Return [{'id': str, 'name': str}, ...] for account pickers."""
    rows = session.execute(select(Account).order_by(Account.name)).scalars().all()
    return [{"id": a.id, "name": a.name} for a in rows]


def categories_choices(session: Session) -> List[Dict[str, str]]:
    rows = session.execute(select(Category).order_by(Category.name)).scalars().all()
    return [{"id": c.id, "name": c.name} for c in rows]


def list_accounts(session: Session) -> List[Account]:
    return session.execute(select(Account).order_by(Account.name)).scalars().all()


def transactions_as_rows(session: Session, flt: Optional[TransactionFilters] = None) -> List[Dict[str, Any]]:
    """
    Return rows for the TransactionsTableModel:
      keys: 'Date','Account','Category','Amount','Type','Memo'
    """
    q = (
        session.query(Transaction)
        .options(joinedload(Transaction.account), joinedload(Transaction.category))
    )

    if flt:
        if flt.date_from:
            q = q.filter(Transaction.date >= flt.date_from)
        if flt.date_to:
            q = q.filter(Transaction.date <= flt.date_to)
        if flt.account_id:
            q = q.filter(Transaction.account_id == flt.account_id)
        if flt.category_id:
            q = q.filter(Transaction.category_id == flt.category_id)
        if flt.txt:
            like = f"%{flt.txt}%"
            q = q.filter(Transaction.description.ilike(like))
        if flt.type:
            if flt.type.upper() == "CREDIT":
                q = q.filter(Transaction.type == TransactionType.CREDIT)
            elif flt.type.upper() == "DEBIT":
                q = q.filter(Transaction.type == TransactionType.DEBIT)

    q = q.order_by(Transaction.date.desc(), Transaction.id)

    rows: List[Dict[str, Any]] = []
    for t in q.all():
        rows.append({
            "Date": t.date,
            "Account": t.account.name if t.account else "",
            "Category": t.category.name if t.category else "",
            "Amount": t.amount,
            "Type": t.type.name if hasattr(t.type, "name") else str(t.type),
            "Memo": t.description or "",
            "_id": t.id,
        })
    return rows
