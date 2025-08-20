from __future__ import annotations
import sys

from PySide6.QtWidgets import QApplication

from finance_tracker.ui.main_window import MainWindow
from finance_tracker.ui.services.db import ensure_db, get_session


def run() -> None:
    app = QApplication(sys.argv)
    ensure_db()
    with get_session() as session:
        w = MainWindow(session=session)
        w.resize(1000, 700)
        w.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    run()
