from finance_tracker.db.base import engine


def test_db_connects():
    with engine.connect() as conn:
        assert conn.closed is False