from __future__ import annotations
from decimal import Decimal
from datetime import date

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QDateEdit,
    QLabel, QPushButton
)
from PySide6.QtCore import QDate

from finance_tracker.models import Account, Category, TransactionType


class TransactionDialog(QDialog):
    """
    Manual-entry dialog used by the Transactions view/controller.
    Use .get_data() for a one-call modal, or access the properties after exec().
    """
    def __init__(self, accounts: list[Account], categories: list[Category], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Transaction")

        self.account_cb = QComboBox()
        for acc in sorted(accounts, key=lambda a: a.name.lower()):
            self.account_cb.addItem(acc.name, acc.id)

        self.category_cb = QComboBox()
        self.category_cb.addItem("(Uncategorized)", None)
        for cat in sorted(categories, key=lambda c: c.name.lower()):
            self.category_cb.addItem(cat.name, cat.id)

        self.type_cb = QComboBox()
        self.type_cb.addItem("Credit", TransactionType.CREDIT.value)
        self.type_cb.addItem("Debit", TransactionType.DEBIT.value)

        self.amount_edit = QLineEdit()
        self.desc_edit = QLineEdit()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        form = QVBoxLayout()

        def row(label: str, w):
            lay = QHBoxLayout()
            lay.addWidget(QLabel(label))
            lay.addWidget(w)
            form.addLayout(lay)

        row("Account", self.account_cb)
        row("Category", self.category_cb)
        row("Type", self.type_cb)
        row("Amount", self.amount_edit)
        row("Description", self.desc_edit)
        row("Date", self.date_edit)

        btns = QHBoxLayout()
        ok = QPushButton("Add")
        cancel = QPushButton("Cancel")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(btns)

    def get_data(self) -> dict | None:
        """Show the dialog and return a dict of values or None if cancelled."""
        if self.exec() != QDialog.accepted:
            return None

        try:
            amt = Decimal((self.amount_edit.text() or "0").strip())
        except Exception:
            return None

        qd = self.date_edit.date()
        py_date = qd.toPython() if hasattr(qd, "toPython") else date(qd.year(), qd.month(), qd.day())

        tx_type_value = self.type_cb.currentData()
        tx_type = TransactionType(tx_type_value)

        return {
            "account_id": self.account_id,
            "category_id": self.category_id,
            "type": tx_type,
            "date": py_date,
            "amount": amt,
            "description": self.description,
        }

    @property
    def account_id(self) -> str:
        return self.account_cb.currentData()

    @property
    def category_id(self) -> str | None:
        return self.category_cb.currentData()

    @property
    def amount_decimal(self) -> Decimal:
        return Decimal((self.amount_edit.text() or "0").strip())

    @property
    def description(self) -> str:
        return (self.desc_edit.text() or "").strip()

    @property
    def qdate(self) -> QDate:
        return self.date_edit.date()
