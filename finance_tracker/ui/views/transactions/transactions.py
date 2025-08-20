from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Iterable, Tuple

from PySide6 import QtCore, QtWidgets

from finance_tracker.ui.models.transactions_table import TransactionsTableModel
from finance_tracker.ui.models.filters import TransactionFilters


@dataclass(frozen=True)
class _DateRange:
    start: Optional[date]
    end: Optional[date]


class TransactionsView(QtWidgets.QWidget):
    addRequested = QtCore.Signal()
    editRequested = QtCore.Signal(str)
    deleteRequested = QtCore.Signal(str)
    refreshRequested = QtCore.Signal()
    filtersChanged = QtCore.Signal(TransactionFilters)

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._model: Optional[TransactionsTableModel] = None
        self._build_ui()
        self._wire_signals()

    def set_model(self, model: TransactionsTableModel) -> None:
        """Attach the table model."""
        self._model = model
        self.table.setModel(model)
        self.table.resizeColumnsToContents()

    def set_choices(
            self,
            accounts: Iterable[Tuple[str, str]],
            categories: Iterable[Tuple[str, str]],
            types: Iterable[Tuple[str, object]] | None = None,
    ) -> None:
        """
        Populate the comboboxes.

        accounts/categories/types must be iterables of (id, label). For 'All ...'
        we keep a None item at index 0.
        """
        def _reload(cb: QtWidgets.QComboBox, items: Iterable[Tuple[str, str]]):
            current = cb.currentData()
            cb.blockSignals(True)
            try:
                cb.clear()
                cb.addItem("All", userData=None)
                for _id, label in items:
                    cb.addItem(label, userData=_id)
                if current is not None:
                    idx = cb.findData(current)
                    if idx >= 0:
                        cb.setCurrentIndex(idx)
            finally:
                cb.blockSignals(False)

        _reload(self.account_cb, accounts)
        _reload(self.category_cb, categories)

        self.type_cb.blockSignals(True)
        try:
            self.type_cb.clear()
            self.type_cb.addItem("All Types", userData=None)
            if types:
                for _id, label in types:
                    self.type_cb.addItem(label, userData=_id)
        finally:
            self.type_cb.blockSignals(False)

    def selected_tx_id(self) -> Optional[str]:
        """Return the selected transaction id via Qt.UserRole."""
        if not self._model:
            return None
        sel = self.table.selectionModel()
        if not sel or not sel.hasSelection():
            return None
        row_index = sel.selectedRows(0)[0]
        idx = self._model.index(row_index.row(), 0)
        tx_id = self._model.data(idx, QtCore.Qt.ItemDataRole.UserRole)
        return str(tx_id) if tx_id else None

    def filters(self) -> TransactionFilters:
        """Build ONLY the fields that actually exist in TransactionFilters."""
        return TransactionFilters(
            account_id=self.account_cb.currentData(),
            category_id=self.category_cb.currentData(),
            date_from=self._qtdate_to_py(self.from_date.date()) if self.from_date.date().isValid() else None,
            date_to=self._qtdate_to_py(self.to_date.date()) if self.to_date.date().isValid() else None,
        )

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        filters_layout = QtWidgets.QGridLayout()
        filters_layout.setHorizontalSpacing(8)
        filters_layout.setVerticalSpacing(4)

        row = 0

        self.account_cb = QtWidgets.QComboBox()
        self.account_cb.setEditable(False)
        self.account_cb.addItem("All", userData=None)

        self.category_cb = QtWidgets.QComboBox()
        self.category_cb.setEditable(False)
        self.category_cb.addItem("All", userData=None)

        self.type_cb = QtWidgets.QComboBox()
        self.type_cb.setEditable(False)
        self.type_cb.addItem("All Types", userData=None)

        self.from_date = QtWidgets.QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat("yyyy-MM-dd")
        self.from_date.setDate(QtCore.QDate())

        self.to_date = QtWidgets.QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDisplayFormat("yyyy-MM-dd")
        self.to_date.setDate(QtCore.QDate())

        filters_layout.addWidget(QtWidgets.QLabel("Account"), row, 0)
        filters_layout.addWidget(self.account_cb, row, 1)
        filters_layout.addWidget(QtWidgets.QLabel("Category"), row, 2)
        filters_layout.addWidget(self.category_cb, row, 3)
        filters_layout.addWidget(QtWidgets.QLabel("Type"), row, 4)
        filters_layout.addWidget(self.type_cb, row, 5)

        row += 1
        filters_layout.addWidget(QtWidgets.QLabel("From"), row, 0)
        filters_layout.addWidget(self.from_date, row, 1)
        filters_layout.addWidget(QtWidgets.QLabel("To"), row, 2)
        filters_layout.addWidget(self.to_date, row, 3)

        layout.addLayout(filters_layout)

        # -- toolbar row (Add/Edit/Delete/Refresh)
        tb_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add…")
        self.edit_btn = QtWidgets.QPushButton("Edit…")
        self.delete_btn = QtWidgets.QPushButton("Delete")
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        tb_layout.addWidget(self.add_btn)
        tb_layout.addWidget(self.edit_btn)
        tb_layout.addWidget(self.delete_btn)
        tb_layout.addStretch(1)
        tb_layout.addWidget(self.refresh_btn)
        layout.addLayout(tb_layout)

        self.table = QtWidgets.QTableView()
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)

    def _wire_signals(self) -> None:
        # Buttons
        self.add_btn.clicked.connect(self.addRequested.emit)
        self.edit_btn.clicked.connect(self._emit_edit_for_selection)
        self.delete_btn.clicked.connect(self._emit_delete_for_selection)
        self.refresh_btn.clicked.connect(self.refreshRequested.emit)

        # Filters
        self.account_cb.currentIndexChanged.connect(self._emit_filters_changed)
        self.category_cb.currentIndexChanged.connect(self._emit_filters_changed)
        self.type_cb.currentIndexChanged.connect(self._emit_filters_changed)  # harmless even if controller ignores type
        self.from_date.dateChanged.connect(self._emit_filters_changed)
        self.to_date.dateChanged.connect(self._emit_filters_changed)

    # helpers
    def _emit_edit_for_selection(self) -> None:
        tx_id = self.selected_tx_id()
        if tx_id:
            self.editRequested.emit(tx_id)

    def _emit_delete_for_selection(self) -> None:
        tx_id = self.selected_tx_id()
        if tx_id:
            self.deleteRequested.emit(tx_id)

    def _emit_filters_changed(self, *args) -> None:
        self.filtersChanged.emit(self.filters())

    @staticmethod
    def _qtdate_to_py(qd: QtCore.QDate) -> date:
        return date(qd.year(), qd.month(), qd.day())
