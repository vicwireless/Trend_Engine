"""Append one owner entry to the time log or the manual spend log, with validation.

    python tools/log_entry.py time  --minutes 25 --session "publish kidcore drafts" [--date 2026-10-26]
    python tools/log_entry.py spend --vendor SerpApi --category tools --amount 25.00 \
        --description "Starter, 1 month" --recurring monthly --source "SerpApi invoice" [--date ...]

Only the owner knows these numbers; nothing here estimates. See docs/spend-and-time.md.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics.spend import MANUAL_COLUMNS  # noqa: E402

TIME_LOG = ROOT / "data" / "time_log.csv"
TIME_COLUMNS = ["date", "session", "minutes", "notes"]
MANUAL = ROOT / "data" / "spend" / "manual.csv"


def _append(path: Path, columns: list[str], row: dict) -> None:
    new = not path.exists() or path.stat().st_size == 0
    path.parent.mkdir(parents=True, exist_ok=True)
    if not new:
        with path.open(newline="") as f:
            header = next(csv.reader(f), [])
        if header != columns:
            raise SystemExit(f"{path} header {header} != expected {columns}; fix the file first")
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        if new:
            w.writeheader()
        w.writerow(row)


def main(argv: list[str] | None = None, time_log: Path = TIME_LOG, manual: Path = MANUAL) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="kind", required=True)
    t = sub.add_parser("time")
    t.add_argument("--minutes", type=int, required=True)
    t.add_argument("--session", required=True)
    t.add_argument("--notes", default="")
    t.add_argument("--date", default=dt.date.today().isoformat())
    s = sub.add_parser("spend")
    s.add_argument("--vendor", required=True)
    s.add_argument("--category", required=True)
    s.add_argument("--amount", type=float, required=True)
    s.add_argument("--description", default="")
    s.add_argument("--recurring", default="no", choices=["no", "monthly", "yearly"])
    s.add_argument("--source", required=True, help="invoice, receipt or statement the amount came from")
    s.add_argument("--entered-by", default="owner")
    s.add_argument("--date", default=dt.date.today().isoformat())
    a = ap.parse_args(argv)
    dt.date.fromisoformat(a.date)  # raises on a bad date

    if a.kind == "time":
        if a.minutes <= 0:
            raise SystemExit("--minutes must be positive")
        _append(time_log, TIME_COLUMNS, {"date": a.date, "session": a.session, "minutes": a.minutes,
                                         "notes": a.notes})
        print(f"logged {a.minutes} min on {a.date} to {time_log}")
    else:
        _append(manual, MANUAL_COLUMNS, {
            "date": a.date, "vendor": a.vendor, "category": a.category, "description": a.description,
            "amount_usd": f"{a.amount:.2f}", "recurring": a.recurring, "source": a.source,
            "entered_by": a.entered_by})
        print(f"logged ${a.amount:.2f} {a.vendor} on {a.date} to {manual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
