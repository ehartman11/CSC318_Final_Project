from __future__ import annotations
from datetime import date

from PySide6.QtCore import QObject

from finance_tracker.ui.core.events import events
from finance_tracker.ui.services.ledger import month_to_date_spend_by_category
from finance_tracker.ui.views.dashboard.dashboard import Dashboard


class DashboardController(QObject):
    def __init__(self, session, view: Dashboard, parent=None):
        super().__init__(parent)
        self.session = session
        self.view = view

        self.view.refreshRequested.connect(self.refresh)
        events.refresh_requested.connect(self.refresh)

        self.refresh()

    def refresh(self) -> None:
        items = month_to_date_spend_by_category(self.session, date.today())
        self.view.set_spend_data(items)
