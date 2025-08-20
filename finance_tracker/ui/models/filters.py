from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class TransactionFilters:
    account_id: Optional[str] = None
    category_id: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    type: Optional[str] = None  # "CREDIT" | "DEBIT" | None
    txt: Optional[str] = None
