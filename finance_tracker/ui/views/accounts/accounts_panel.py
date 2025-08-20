from __future__ import annotations
from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QLabel, QHBoxLayout
)

from finance_tracker.models import Account


class AccountsPanel(QWidget):
    """
    Simple accounts list with a Refresh button.
    Exposes:
      - set_accounts(accounts: List[Account])
      - refreshRequested: Signal
    """
    refreshRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("Accounts"))
        self.refresh_btn = QPushButton("Refresh")
        header.addWidget(self.refresh_btn, alignment=Qt.AlignRight)
        layout.addLayout(header)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Account", "Balance"])
        layout.addWidget(self.tree)

        self.refresh_btn.clicked.connect(self.refreshRequested.emit)

    # API called by controller
    def set_accounts(self, accounts: List[Account]) -> None:
        self.tree.clear()
        for a in accounts:
            bal = getattr(a, "balance", None)
            bal_str = f"{bal:,.2f}" if bal is not None else ""
            QTreeWidgetItem(self.tree, [a.name, bal_str])
        self.tree.expandAll()

