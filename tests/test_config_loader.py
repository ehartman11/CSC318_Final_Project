from finance_tracker.config.loader import get_config, db_url


def test_config_loads():
    cfg = get_config()
    assert "database" in cfg
    assert db_url()