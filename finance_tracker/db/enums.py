from enum import StrEnum


class AccountType(StrEnum):
    CHECKING = "checking"
    SAVINGS  = "savings"
    INVESTMENT = "investment"
    RETIREMENT = "retirement"
    OTHER = "other"


class TxType(StrEnum):
    INCOME  = "income"
    EXPENSE = "expense"


class AlertType(StrEnum):
    OVERSPEND = "overspend"
    BILL_DUE  = "bill_due"
    GOAL      = "goal"
