import logging
from . import __name__ as pkg_name
from .config.loader import log_level


def get_logger(name: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name or pkg_name)
    if not logger.handlers:
        logger.setLevel(log_level())
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        logger.addHandler(ch)
    return logger
