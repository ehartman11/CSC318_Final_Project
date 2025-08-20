from __future__ import annotations
from typing import Any, Mapping, Sequence, List
from decimal import Decimal
from datetime import date

from PySide6 import QtCore


class TransactionsTableModel(QtCore.QAbstractTableModel):
    HEADERS: List[str] = ["Date", "Account", "Category", "Type", "Amount", "Description"]

    def __init__(self, rows: list[Any] | None = None, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._rows: list[Any] = rows or []

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self.HEADERS)

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if parent.isValid():
            return QtCore.QModelIndex()
        return self.createIndex(row, column)

    def parent(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        return QtCore.QModelIndex()

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        if role not in (QtCore.Qt.ItemDataRole.DisplayRole, QtCore.Qt.ItemDataRole.EditRole):
            return None

        row = self._rows[index.row()]
        header = self.HEADERS[index.column()]

        if isinstance(row, Mapping):
            value = row.get(header, "")
        elif isinstance(row, Sequence) and not isinstance(row, (str, bytes)):
            try:
                value = row[index.column()]
            except IndexError:
                value = ""
        else:
            value = ""

        if header == "Amount" and isinstance(value, (Decimal, float, int)):
            return f"{Decimal(value):,.2f}"
        if header == "Date" and isinstance(value, date):
            return value.strftime("%Y-%m-%d")
        return value

    def headerData(
            self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == QtCore.Qt.Orientation.Horizontal:
            try:
                return self.HEADERS[section]
            except IndexError:
                return ""
        return str(section + 1)

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        return QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable

    def set_rows(self, rows: list[Any]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def row_at(self, row: int) -> Any:
        return self._rows[row]
