from __future__ import annotations

from PySide6.QtCore import QObject

from finance_tracker.ui.core.events import events
from finance_tracker.ui.services import queries, ledger
from finance_tracker.ui.views.accounts.accounts_panel import AccountsPanel


class AccountsController(QObject):
    def __init__(self, session, view: AccountsPanel, parent=None):
        super().__init__(parent)
        self.session = session
        self.view = view

        self.view.refreshRequested.connect(self.reload)
        events.refresh_requested.connect(self.reload)

        self.reload()

    def reload(self) -> None:
        accounts = queries.list_accounts(self.session)
        for a in accounts:
            try:
                ledger.recompute_account_balance(self.session, a)
            except Exception:
                pass
        self.session.commit()
        self.view.set_accounts(accounts)
