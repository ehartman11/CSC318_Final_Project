from __future__ import annotations
import argparse
from datetime import date

from ..services import reports


def main() -> None:
    parser = argparse.ArgumentParser(description="Finance Tracker Reports")
    parser.add_argument("year", type=int, nargs="?", default=date.today().year)
    parser.add_argument("month", type=int, nargs="?", default=date.today().month)
    args = parser.parse_args()

    reports.demo_print(args.year, args.month)


if __name__ == "__main__":
    main()