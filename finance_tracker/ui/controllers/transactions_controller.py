from __future__ import annotations
from typing import Optional
from decimal import Decimal

from PySide6.QtCore import QObject

from sqlalchemy.orm import Session, joinedload

from finance_tracker.ui.core.events import events
from finance_tracker.ui.models.transactions_table import TransactionsTableModel
from finance_tracker.ui.models.filters import TransactionFilters
from finance_tracker.ui.services import queries
from finance_tracker.ui.views.transactions.transactions import TransactionsView
from finance_tracker.ui.views.transactions.dialogs import TransactionDialog
from finance_tracker.ui.services.ledger import recompute_account_balance
from finance_tracker.models import Account, Category, Transaction, TransactionType


class TransactionsController(QObject):
    def __init__(self, session: Session, view: TransactionsView, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.session = session
        self.view = view
        self.model = TransactionsTableModel()

        # wire view to model
        self.view.set_model(self.model)

        # refresh hooks
        self.view.refreshRequested.connect(self.reload)
        events.refresh_requested.connect(self.reload)

        # CRUD actions
        self.view.addRequested.connect(self.on_add_clicked)
        self.view.editRequested.connect(self.on_edit_requested)
        self.view.deleteRequested.connect(self.on_delete_requested)

        self.reload_choices()
        self.reload()

    # data loading

    def reload_choices(self) -> None:
        accounts = queries.accounts_choices(self.session)
        categories = queries.categories_choices(self.session)
        self.view.set_choices(accounts, categories)

    def reload(self) -> None:
        flt: TransactionFilters = self.view.filters()

        q = (
            self.session.query(Transaction)
            .options(joinedload(Transaction.account), joinedload(Transaction.category))
        )
        if flt.account_id:
            q = q.filter(Transaction.account_id == flt.account_id)
        if flt.category_id:
            q = q.filter(Transaction.category_id == flt.category_id)
        if flt.date_from:
            q = q.filter(Transaction.date >= flt.date_from)
        if flt.date_to:
            q = q.filter(Transaction.date <= flt.date_to)
        if flt.type:
            tval = flt.type
            if isinstance(tval, str):
                tval = tval.lower()
                if tval in ("credit", "debit"):
                    tval = TransactionType.CREDIT if tval == "credit" else TransactionType.DEBIT
            q = q.filter(Transaction.type == tval)
        if flt.txt:
            like = f"%{flt.txt}%"
            q = q.filter(Transaction.description.ilike(like))

        rows = []
        for t in q.order_by(Transaction.date.desc(), Transaction.id.desc()).all():
            rows.append({
                "id": t.id,
                "date": t.date,
                "account": t.account.name if t.account else "",
                "category": t.category.name if t.category else "",
                "type": t.type.value if hasattr(t.type, "value") else str(t.type),
                "amount": t.amount,
                "description": t.description or "",
            })

        self.model.set_rows(rows)
        self.view.table.resizeColumnsToContents()

    def on_add_clicked(self) -> None:
        accounts = self.session.query(Account).order_by(Account.name).all()
        categories = self.session.query(Category).order_by(Category.name).all()

        dlg = TransactionDialog(accounts=accounts, categories=categories, parent=self.view)
        data = dlg.get_data()
        if not data:
            return

        tval = data["type"]
        if isinstance(tval, str):
            tval = tval.lower()
            data["type"] = TransactionType.CREDIT if tval == "credit" else TransactionType.DEBIT

        tx = Transaction(
            account_id=data["account_id"],
            category_id=data["category_id"],
            date=data["date"],
            type=data["type"],
            amount=data["amount"],
            description=data["description"],
        )
        self.session.add(tx)
        self.session.flush()

        acct = self.session.get(Account, data["account_id"])
        if acct:
            recompute_account_balance(self.session, acct)

        self.session.commit()
        self.reload()

    def on_edit_requested(self, tx_id: str) -> None:
        if not tx_id:
            return
        tx = self.session.get(Transaction, tx_id)
        if not tx:
            return

        accounts = self.session.query(Account).order_by(Account.name).all()
        categories = self.session.query(Category).order_by(Category.name).all()
        dlg = TransactionDialog(self.view, accounts=accounts, categories=categories)

        data = dlg.get_data()
        if not data:
            return

        old_account_id = tx.account_id

        tx.account_id = data["account_id"]
        tx.category_id = data["category_id"]
        tx.date = data["date"]
        tval = data["type"]
        if isinstance(tval, str):
            tval = tval.lower()
            tval = TransactionType.CREDIT if tval == "credit" else TransactionType.DEBIT
        tx.type = tval
        tx.amount = Decimal(data["amount"])
        tx.description = data["description"]

        # recompute balances if needed
        if old_account_id != tx.account_id:
            old_acct = self.session.get(Account, old_account_id)
            if old_acct:
                recompute_account_balance(self.session, old_acct)

        new_acct = self.session.get(Account, tx.account_id)
        if new_acct:
            recompute_account_balance(self.session, new_acct)

        self.session.commit()
        self.reload()

    def on_delete_requested(self, tx_id: str) -> None:
        if not tx_id:
            return
        tx = self.session.get(Transaction, tx_id)
        if not tx:
            return

        acct_id = tx.account_id
        self.session.delete(tx)
        self.session.flush()

        acct = self.session.get(Account, acct_id)
        if acct:
            recompute_account_balance(self.session, acct)

        self.session.commit()
        self.reload()
