from sqlalchemy import inspect
from finance_tracker.db.base import engine

if __name__ == "__main__":
    i = inspect(engine)
    print("tables:", sorted(i.get_table_names()))
    for t in ("accounts", "categories", "transactions", "budgets", "budget_items", "goals", "alerts", "recurring_transactions"):
        try:
            print(t, "cols:", [c["name"] for c in i.get_columns(t)])
        except Exception as e:
            print(t, "error:", e)