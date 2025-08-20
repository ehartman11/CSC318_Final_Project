from sqlalchemy import select
from finance_tracker.db.base import SessionLocal
from finance_tracker.models import Account, Category, Transaction

with SessionLocal() as s:
    print("accounts:", [a.name for a in s.scalars(select(Account)).all()])
    print("categories:", [c.name for c in s.scalars(select(Category)).all()])
    tx = s.scalars(select(Transaction).order_by(Transaction.date).limit(5)).all()
    print("tx sample:", [(t.date, t.type.value, t.amount, t.description) for t in tx])