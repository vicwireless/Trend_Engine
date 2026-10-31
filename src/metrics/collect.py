"""Daily per-listing metrics snapshot from the Etsy Open API v3. READ-ONLY.

Writes data/metrics/<date>.csv (one row per listing) and data/metrics/<date>.shop.json (shop totals
and the inputs the gate check needs). Every number here is "Etsy data" (CLAUDE.md rule 5) because it
comes from the Etsy Open API.

What the API gives (verified 2026-10-31, docs/metrics.md): lifetime `views` and `num_favorers` per
listing, receipts + transactions (orders, units, item revenue). What it does NOT give: daily views,
visits, traffic sources, search terms, conversion rate, Etsy Ads spend/clicks, Pinterest clicks.
Daily views/favorites/orders here are DELTAS between consecutive snapshots.

Rule 4: receipts pass through EtsyRead.sanitize_receipt and only per-listing aggregates are written.
No receipt, buyer, or personalization field is ever stored by this module.

    python -m src.metrics.collect [--date YYYY-MM-DD] [--out data/metrics]
"""
from __future__ import annotations

import argparse
import csv
import html
import html
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any, Iterable

import requests

from src.clients.base import ClientError, require
from src.clients.etsy_read import EtsyRead, money, sanitize_receipt

OUT_DIR = Path("data/metrics")
PAGE = 100
# Receipt statuses that do not count as revenue.
EXCLUDED_STATUSES = {"canceled", "cancelled", "fully refunded"}

COLUMNS = [
    "date", "listing_id", "title", "state", "listing_type", "price_usd", "published_date",
    "views_total", "favorites_total", "orders_total", "units_total", "revenue_usd_total",
    "views_1d", "favorites_1d", "orders_1d", "units_1d", "revenue_usd_1d",
    "has_disclosure_sentence", "source",
]


class ReadOnlySession(requests.Session):
    """A requests session that refuses anything but GET/HEAD (CLAUDE.md rule 1, scheduled task)."""

    def request(self, method, url, *args, **kwargs):  # type: ignore[override]
        if method.upper() not in ("GET", "HEAD"):
            raise ClientError(f"metrics job is read-only; refused {method} {url}")
        return super().request(method, url, *args, **kwargs)


def _paginate(http, path: str, params: dict[str, Any] | None = None) -> Iterable[dict]:
    offset = 0
    while True:
        data = http.get_json(path, params={**(params or {}), "limit": PAGE, "offset": offset})
        rows = data.get("results", [])
        yield from rows
        offset += len(rows)
        if not rows or offset >= data.get("count", 0):
            return


def _date(ts: int | None) -> str | None:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).date().isoformat() if ts else None


def disclosure_sentences(config_path: Path = Path("config/engine.yaml")) -> list[str]:
    import yaml
    comp = (yaml.safe_load(config_path.read_text()) or {}).get("compliance", {})
    return [s for s in [comp.get("ai_disclosure_sentence"), *comp.get("ai_disclosure_sentences_extra", [])] if s]


def _norm(s: str) -> str:
    # Etsy returns descriptions HTML-escaped (&#39; for an apostrophe).
    return " ".join(html.unescape(str(s)).replace("’", "'").split()).lower()


def has_disclosure(description: str | None, sentences: list[str]) -> bool:
    d = _norm(description or "")
    return any(_norm(s) in d for s in sentences)


def sales_by_listing(receipts: Iterable[dict]) -> dict[int, dict[str, float]]:
    """Aggregate sanitized receipts to {listing_id: orders, units, revenue_usd}. Item revenue only
    (price x quantity, before discounts, excluding shipping and tax); canceled/refunded excluded."""
    out: dict[int, dict[str, float]] = {}
    for r in receipts:
        if str(r.get("status") or "").lower() in EXCLUDED_STATUSES:
            continue
        seen: set[int] = set()
        for tx in r.get("transactions", []):
            lid = tx.get("listing_id")
            if lid is None:
                continue
            agg = out.setdefault(int(lid), {"orders": 0, "units": 0, "revenue_usd": 0.0})
            qty = int(tx.get("quantity") or 0)
            agg["units"] += qty
            agg["revenue_usd"] = round(agg["revenue_usd"] + (tx.get("price_usd") or 0) * qty, 2)
            if lid not in seen:
                agg["orders"] += 1
                seen.add(lid)
    return out


def previous_snapshot(out_dir: Path, date: str) -> dict[str, dict]:
    """Rows of the latest data/metrics/<d>.csv strictly before `date`, keyed by listing_id."""
    prior = sorted(p for p in out_dir.glob("????-??-??.csv") if p.stem < date)
    if not prior:
        return {}
    with prior[-1].open(newline="") as f:
        return {row["listing_id"]: row for row in csv.DictReader(f)}


def _delta(now: Any, before: dict | None, key: str) -> Any:
    if before is None or before.get(key) in (None, ""):
        return ""  # no baseline yet; never pretend a lifetime total is a daily number
    try:
        d = float(now or 0) - float(before[key])
    except ValueError:
        return ""
    return round(d, 2) if "revenue" in key else int(d)


def collect(date: str, *, etsy: EtsyRead | None = None, shop_id: str | None = None,
            out_dir: Path = OUT_DIR, sentences: list[str] | None = None) -> dict:
    shop_id = require(shop_id or os.environ.get("ETSY_SHOP_ID"), "ETSY_SHOP_ID")
    if etsy is None:
        etsy = EtsyRead(session=ReadOnlySession())
    http = etsy.http
    sentences = disclosure_sentences() if sentences is None else sentences

    shop = http.get_json(f"shops/{shop_id}")
    listings = {int(l["listing_id"]): l for l in _paginate(http, f"shops/{shop_id}/listings", {"state": "active"})}
    prev = previous_snapshot(out_dir, date)
    # Listings we tracked before that are no longer active: read their current state so the row
    # (and its cumulative numbers) carries on instead of silently disappearing.
    for lid in sorted({int(k) for k in prev} - set(listings)):
        try:
            listings[lid] = http.get_json(f"listings/{lid}")
        except ClientError as e:
            listings[lid] = {"listing_id": lid, "state": f"unreadable: {str(e)[:60]}",
                             "title": prev[str(lid)].get("title")}

    receipts = [sanitize_receipt(r) for r in _paginate(http, f"shops/{shop_id}/receipts")]
    sales = sales_by_listing(receipts)

    rows = []
    for lid, l in sorted(listings.items(), key=lambda kv: kv[0]):
        s = sales.get(lid, {"orders": 0, "units": 0, "revenue_usd": 0.0})
        before = prev.get(str(lid))
        row = {
            "date": date, "listing_id": lid, "title": l.get("title"), "state": l.get("state"),
            "listing_type": l.get("listing_type"), "price_usd": money(l.get("price")),
            "published_date": _date(l.get("original_creation_timestamp") or l.get("created_timestamp")),
            "views_total": l.get("views"), "favorites_total": l.get("num_favorers"),
            "orders_total": s["orders"], "units_total": s["units"], "revenue_usd_total": s["revenue_usd"],
            "has_disclosure_sentence": has_disclosure(l.get("description"), sentences) if "description" in l else "",
            "source": "etsy_open_api",
        }
        for k_now, k in (("views_total", "views_1d"), ("favorites_total", "favorites_1d"),
                         ("orders_total", "orders_1d"), ("units_total", "units_1d"),
                         ("revenue_usd_total", "revenue_usd_1d")):
            row[k] = _delta(row[k_now], before, k_now)
        rows.append(row)

    gross = round(sum(r["revenue_usd_total"] for r in rows), 2)
    shop_summary = {
        "date": date,
        "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source": "etsy_open_api",
        "shop_id": int(shop_id),
        "listing_active_count": shop.get("listing_active_count"),
        "digital_listing_count": shop.get("digital_listing_count"),
        "transaction_sold_count": shop.get("transaction_sold_count"),
        "shop_favorers": shop.get("num_favorers"),
        "review_count": shop.get("review_count"),
        "review_average": shop.get("review_average"),
        "is_vacation": shop.get("is_vacation"),
        "active_rows": sum(1 for r in rows if r["state"] == "active"),
        "active_with_disclosure_sentence": sum(1 for r in rows if r["state"] == "active" and r["has_disclosure_sentence"] is True),
        "receipts_counted": sum(1 for r in receipts if str(r.get("status") or "").lower() not in EXCLUDED_STATUSES),
        "receipts_excluded": sum(1 for r in receipts if str(r.get("status") or "").lower() in EXCLUDED_STATUSES),
        "views_total": sum(int(r["views_total"] or 0) for r in rows),
        "favorites_total": sum(int(r["favorites_total"] or 0) for r in rows),
        "orders_total": sum(r["orders_total"] for r in rows),
        "gross_item_revenue_usd_total": gross,
        "baseline_date": next(iter(prev.values()))["date"] if prev else None,
        "api_remaining_today": http.remaining.get("x-remaining-today"),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / f"{date}.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    (out_dir / f"{date}.shop.json").write_text(json.dumps(shop_summary, indent=2) + "\n")
    return {"rows": rows, "shop": shop_summary}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=dt.datetime.now(dt.timezone.utc).date().isoformat())
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    a = ap.parse_args(argv)
    res = collect(a.date, out_dir=a.out)
    s = res["shop"]
    print(f"{a.date}: {s['active_rows']} active listings, {s['views_total']} views, "
          f"{s['favorites_total']} favorites, {s['orders_total']} orders, ${s['gross_item_revenue_usd_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
