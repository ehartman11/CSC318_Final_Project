from __future__ import annotations
from typing import List, Tuple
from decimal import Decimal

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QListWidget, QListWidgetItem


class Dashboard(QWidget):
    """
    Displays month-to-date spend by category (simple list for now).
    Exposes:
      - set_spend_data([(category, amount), ...])
      - refreshRequested: Signal
    """
    refreshRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("Dashboard"))
        self.refresh_btn = QPushButton("Refresh")
        header.addWidget(self.refresh_btn, alignment=Qt.AlignRight)
        layout.addLayout(header)

        self.list = QListWidget()
        layout.addWidget(self.list)

        self.refresh_btn.clicked.connect(self.refreshRequested.emit)

    def set_spend_data(self, items: List[Tuple[str, Decimal]]) -> None:
        self.list.clear()
        for name, amt in items:
            QListWidgetItem(f"{name}: {amt:,.2f}", self.list)
