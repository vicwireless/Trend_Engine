"""Turn raw trend observations into signal records (docs/data-model.md, signal).

Everything here is an estimate (CLAUDE.md rule 5): none of these sources is Etsy Marketplace
Insights or the Etsy Open API. Blocklist hits are noted on the signal, not dropped, so the
weekly brief can show what was seen and why it was skipped; the IP screen vetoes later.
"""
from __future__ import annotations

import csv
import datetime as dt
import io
import json
import re
from pathlib import Path
from typing import Iterable

from src.compliance.blocklist import Blocklist

UNASSIGNED_NICHE = "unassigned"


def slug(text: str, max_len: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len].rstrip("-") or "x"


def make_signal(*, source: str, keyword: str, metric: str, value: float, unit: str,
                window_start: dt.date, window_end: dt.date, fetched_at: str, n: int,
                blocklist: Blocklist | None = None, raw_ref: str | None = None,
                license: str | None = None, niche: str = UNASSIGNED_NICHE) -> dict:
    sig = {
        "signal_id": f"sig-{window_end:%Y%m%d}-{slug(source, 16)}-{slug(metric, 16)}-{n:03d}-{slug(keyword, 24)}",
        "source": source, "is_estimate": True, "keyword": keyword, "niche": niche, "metric": metric,
        "value": value, "unit": unit, "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(), "fetched_at": fetched_at, "raw_ref": raw_ref,
        "license": license,
    }
    if blocklist is not None:
        hits = blocklist.check(keyword)
        if hits:
            sig["notes"] = "blocklist hit: " + ", ".join(sorted({f"{h.category}/{h.rule}" for h in hits}))
    return sig


# --- SerpApi -----------------------------------------------------------------------------------

def from_trending_now(result: dict, *, blocklist: Blocklist | None = None) -> list[dict]:
    """Signals from SerpApiTrends.trending_now(): one `increase_pct` per breakout query."""
    fetched = result["fetched_at"]
    end = dt.date.fromisoformat(fetched[:10])
    hours = int(re.search(r"(\d+)", result.get("range") or "24").group(1))
    start = end - dt.timedelta(days=max(0, hours // 24 - 1))
    out = []
    for n, row in enumerate(result.get("trending") or [], 1):
        if not row.get("query") or row.get("increase_percentage") is None:
            continue
        out.append(make_signal(source="serpapi_google_trends_trending_now", keyword=row["query"],
                               metric="increase_pct", value=float(row["increase_percentage"]), unit="percent",
                               window_start=start, window_end=end, fetched_at=fetched, n=n,
                               blocklist=blocklist, license="SerpApi ToS"))
    return out


def from_autocomplete(result: dict, *, blocklist: Blocklist | None = None) -> list[dict]:
    """Signals from SerpApiTrends.autocomplete(): suggestion rank (1 = first) per suggestion."""
    fetched = result["fetched_at"]
    day = dt.date.fromisoformat(fetched[:10])
    return [make_signal(source="serpapi_google_autocomplete", keyword=row["value"], metric="suggestion_rank",
                        value=float(n), unit="rank", window_start=day, window_end=day, fetched_at=fetched, n=n,
                        blocklist=blocklist, license="SerpApi ToS")
            for n, row in enumerate(result.get("suggestions") or [], 1)]


# --- Owner inbox (manual exports, no API) ------------------------------------------------------

KEYWORD_COLS = ("keyword", "keywords", "term", "search term", "search terms", "trend", "query")
GROWTH_COLS = {  # header alias -> (metric, window days)
    "weekly change": ("growth_wow", 7), "wow": ("growth_wow", 7), "week over week": ("growth_wow", 7),
    "monthly change": ("growth_mom", 30), "mom": ("growth_mom", 30), "month over month": ("growth_mom", 30),
    "yearly change": ("growth_yoy", 365), "yoy": ("growth_yoy", 365), "year over year": ("growth_yoy", 365),
}
VOLUME_COLS = ("searches", "avg searches", "search volume", "volume", "etsy searches")


def _rows(text: str) -> tuple[list[str], list[list[str]]]:
    text = text.lstrip("﻿")
    dialect = "excel-tab" if text.split("\n", 1)[0].count("\t") > text.split("\n", 1)[0].count(",") else "excel"
    rows = [r for r in csv.reader(io.StringIO(text), dialect=dialect) if any(c.strip() for c in r)]
    if not rows:
        return [], []
    return [h.strip().lower() for h in rows[0]], rows[1:]


def _number(cell: str) -> float | None:
    cell = cell.strip().replace(",", "").replace("+", "")
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*(%?)", cell)
    if not m:
        return None
    v = float(m.group(1))
    return v / 100 if m.group(2) else v


def parse_inbox_csv(text: str, *, source: str, day: dt.date, fetched_at: str, raw_ref: str,
                    blocklist: Blocklist | None = None) -> list[dict]:
    """Parse an owner-pasted table (CSV or tab-separated, first row = header).

    Needs a keyword column (any of KEYWORD_COLS). Row order becomes `trend_rank`; growth columns
    (weekly/monthly/yearly change, "+120%" -> 1.2) and a search-volume column are added when present.
    Fails closed: a table without a keyword column raises ValueError.
    """
    header, rows = _rows(text)
    kcol = next((i for i, h in enumerate(header) if h in KEYWORD_COLS), None)
    if kcol is None:
        raise ValueError(f"{raw_ref}: no keyword column; expected one of {KEYWORD_COLS}, got {header}")
    growth = [(i, *GROWTH_COLS[h]) for i, h in enumerate(header) if h in GROWTH_COLS]
    vcol = next((i for i, h in enumerate(header) if h in VOLUME_COLS), None)
    out: list[dict] = []
    kw = dict(source=source, fetched_at=fetched_at, raw_ref=raw_ref, blocklist=blocklist,
              license="owner export, internal use")
    for n, row in enumerate(rows, 1):
        if kcol >= len(row) or not row[kcol].strip():
            continue
        keyword = row[kcol].strip()
        out.append(make_signal(keyword=keyword, metric="trend_rank", value=float(n), unit="rank",
                               window_start=day, window_end=day, n=n, **kw))
        for i, metric, days in growth:
            v = _number(row[i]) if i < len(row) else None
            if v is not None:
                out.append(make_signal(keyword=keyword, metric=metric, value=v, unit="ratio",
                                       window_start=day - dt.timedelta(days=days), window_end=day, n=n, **kw))
        if vcol is not None and vcol < len(row):
            v = _number(row[vcol])
            if v is not None:
                out.append(make_signal(keyword=keyword, metric="search_volume", value=v, unit="count",
                                       window_start=day - dt.timedelta(days=30), window_end=day, n=n, **kw))
    return out


INBOX_FILES = {"erank_trendbuzz.csv": "erank", "pinterest_trends.csv": "pinterest_trends"}


def ingest_inbox(root: Path, day: dt.date, *, blocklist: Blocklist | None = None,
                 now: dt.datetime | None = None) -> dict[str, Path]:
    """Read data/inbox/YYYY-MM-DD/<known file> and write data/signals/YYYY-MM-DD/<source>.json."""
    inbox = root / "data" / "inbox" / day.isoformat()
    out_dir = root / "data" / "signals" / day.isoformat()
    fetched = (now or dt.datetime.now(dt.timezone.utc)).isoformat(timespec="seconds")
    written: dict[str, Path] = {}
    for name, source in INBOX_FILES.items():
        path = inbox / name
        if not path.exists():
            continue
        sigs = parse_inbox_csv(path.read_text(encoding="utf-8"), source=source, day=day, fetched_at=fetched,
                               raw_ref=str(path.relative_to(root)), blocklist=blocklist)
        written[source] = write_signals(out_dir / f"{source}.json", sigs)
    return written


def write_signals(path: Path, signals: Iterable[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(list(signals), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":  # pragma: no cover
    import argparse

    ap = argparse.ArgumentParser(description="Ingest owner inbox exports into data/signals/")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    for src, p in ingest_inbox(root, dt.date.fromisoformat(args.date), blocklist=Blocklist.load()).items():
        print(f"{src}: {p.relative_to(root)}")
