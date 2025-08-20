from __future__ import annotations
import sys

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QTabWidget

from finance_tracker.ui.core.events import events
from finance_tracker.ui.views.accounts.accounts_panel import AccountsPanel
from finance_tracker.ui.views.dashboard.dashboard import Dashboard
from finance_tracker.ui.views.transactions.transactions import TransactionsView

from finance_tracker.ui.controllers.accounts_controller import AccountsController
from finance_tracker.ui.controllers.dashboard_controller import DashboardController
from finance_tracker.ui.controllers.transactions_controller import TransactionsController


class MainWindow(QMainWindow):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Finance Tracker")

        self.session = session

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Views
        self.accounts_view = AccountsPanel()
        self.dashboard_view = Dashboard()
        self.transactions_view = TransactionsView()

        # Controllers
        self.accounts_controller = AccountsController(session=self.session, view=self.accounts_view, parent=self)
        self.dashboard_controller = DashboardController(session=self.session, view=self.dashboard_view, parent=self)
        self.transactions_controller = TransactionsController(session=self.session, view=self.transactions_view, parent=self)

        # Tabs
        self.tabs.addTab(self.dashboard_view, "Dashboard")
        self.tabs.addTab(self.accounts_view, "Accounts")
        self.tabs.addTab(self.transactions_view, "Transactions")

        # Menu / toolbar actions
        self._build_menu()

    def _build_menu(self) -> None:
        refresh_act = QAction("Refresh", self)
        refresh_act.setShortcut("F5")
        refresh_act.triggered.connect(events.refresh_requested.emit)

        bar = self.menuBar().addMenu("&View")
        bar.addAction(refresh_act)
