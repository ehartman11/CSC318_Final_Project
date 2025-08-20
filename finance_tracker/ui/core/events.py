from __future__ import annotations
from PySide6.QtCore import QObject, Signal


class AppEvents(QObject):
    """Global app events to decouple controllers."""
    transactions_changed = Signal()        # fire after add/edit/delete
    accounts_changed = Signal()            # fire when balances / accounts list changes
    budgets_changed = Signal()

    refresh_requested = Signal()

events = AppEvents()
