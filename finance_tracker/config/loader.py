from __future__ import annotations
from pathlib import Path
from functools import lru_cache
from dataclasses import dataclass
import os

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# ----- Typed config containers -----
@dataclass(frozen=True)
class DatabaseCfg:
    url: str
    echo: bool = False


@dataclass(frozen=True)
class AppCfg:
    env: str = "dev"


@dataclass(frozen=True)
class LoggingCfg:
    level: str = "INFO"
    file: str | None = None  # fine thanks to __future__ annotations


@dataclass(frozen=True)
class Cfg:
    app: AppCfg
    database: DatabaseCfg
    logging: LoggingCfg


def _project_root() -> Path:
    """
    Anchor to the repo root regardless of CWD:
    finance_tracker/config/loader.py -> .. (config) -> .. (finance_tracker) -> project root
    """
    cfg_py = Path(__file__).resolve()
    return cfg_py.parents[2]


def _abs_sqlite_url(url: str) -> str:
    """
    If the URL is sqlite and relative (e.g. sqlite:///./finance.db or sqlite:///finance.db),
    convert it to an absolute path rooted at the project root so launching from any CWD/IDE works.
    """
    if not url.startswith("sqlite:///"):
        return url

    path_part = url[len("sqlite:///"):]
    if Path(path_part).is_absolute():
        return url

    abs_path = (_project_root() / path_part).resolve()
    return f"sqlite:///{abs_path.as_posix()}"


@lru_cache
def get_config() -> Cfg:
    # Load TOML from the same dir as this file
    cfg_path = Path(__file__).with_name("config.toml")
    data = {}
    if cfg_path.exists():
        with cfg_path.open("rb") as f:
            data = tomllib.load(f)

    app = data.get("app", {})
    db = data.get("database", {})
    lg = data.get("logging", {})

    # Allow an env override for the DB URL for testing
    raw_db_url = os.getenv("FINANCE_DB_URL", db.get("url", "sqlite:///./finance.db"))

    return Cfg(
        app=AppCfg(env=app.get("env", "dev")),
        database=DatabaseCfg(
            url=_abs_sqlite_url(raw_db_url),
            echo=bool(db.get("echo", False)),
        ),
        logging=LoggingCfg(
            level=lg.get("level", "INFO"),
            file=lg.get("file"),
        ),
    )


# ----- Backwards-compatible helpers -----
def db_url() -> str:
    return get_config().database.url


def db_echo() -> bool:
    return get_config().database.echo


def log_level() -> str:
    return get_config().logging.level
