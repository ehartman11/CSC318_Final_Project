from __future__ import annotations
from decimal import Decimal
from datetime import date
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session
from finance_tracker.models import Account, Transaction, TransactionType


def recompute_account_balance(session: Session, account: Account) -> None:
    """
    Recompute: balance = starting_balance + sum(all transaction amounts).
    Note: your Transaction amounts are already signed (+credit / -debit).
    """
    total = (
        session.query(Transaction.amount)
        .filter(Transaction.account_id == account.id)
        .all()
    )
    sum_amount = sum((row[0] or Decimal("0") for row in total), Decimal("0"))
    account.balance = (account.starting_balance or Decimal("0")) + sum_amount
    session.add(account)


def month_to_date_spend_by_category(session: Session, today: date) -> List[Tuple[str, Decimal]]:
    """
    Returns [(category_name, abs(total_debit_this_month)), ...] sorted desc.
    Debits are summed (negative amounts); we return positive magnitudes for display.
    """
    start = date(today.year, today.month, 1)
    txs = (
        session.query(Transaction)
        .filter(Transaction.date >= start)
        .all()
    )
    agg: Dict[str, Decimal] = {}
    for t in txs:
        if t.type == TransactionType.DEBIT:
            name = t.category.name if t.category else "(Uncategorized)"
            amt = t.amount or Decimal("0")
            agg[name] = agg.get(name, Decimal("0")) + amt

    return sorted(((k, abs(v)) for k, v in agg.items()), key=lambda x: x[1], reverse=True)
