"""Spend log: Etsy fees from the payment ledger (read-only) plus owner-entered spend. No estimates.

Three files in data/spend/ (docs/spend-and-time.md):

- etsy_ledger.csv   written here from `shops/{id}/payment-account/ledger-entries` (Etsy data).
                    One row per fee or credit entry; payouts, sales and fee payments are left out.
- manual.csv        owner-entered spend outside Etsy (subscriptions, samples, tools), with a source.
- subscriptions.csv register of recurring tools. `monthly_usd` stays BLANK until the owner confirms
                    the amount, so the burn total never contains a guessed number.

The weekly report reads these through `summarize()` and prints only verified totals; anything
without a confirmed amount is listed by name as "amount not confirmed".

    python -m src.metrics.spend [--since 2026-10-15] [--out data/spend]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
from pathlib import Path
from typing import Iterable

from src.clients.base import require

SPEND_DIR = Path("data/spend")
LEDGER_COLUMNS = ["date", "entry_id", "ledger_type", "category", "amount_usd", "reference_type",
                  "reference_id", "source"]
MANUAL_COLUMNS = ["date", "vendor", "category", "description", "amount_usd", "recurring", "source",
                  "entered_by"]
SUBSCRIPTION_COLUMNS = ["vendor", "plan", "monthly_usd", "status", "started", "source", "notes"]

# Positive entries that are money moving, not a reduction in cost (a card payment that settles a
# fee, a sale, a refund to the buyer side). Spend = fee charges minus Etsy-issued credits.
CREDIT_TYPES = {"etsy_plus_credit"}
PAYOUT_MARKERS = ("disburse", "deposit", "payout")
CATEGORY = {
    "listing": "etsy_listing_fees",
    "renew_sold": "etsy_listing_fees",
    "renew_expired": "etsy_listing_fees",
    "etsy_plus_credit": "etsy_listing_fees",
    "tier_2_subscription": "etsy_plus",
    "seller_onboarding_fee": "etsy_setup",
    "transaction": "etsy_sales_fees",
    "transaction_quantity": "etsy_sales_fees",
    "processing_fee": "etsy_sales_fees",
    "offsite_ads_fee": "etsy_offsite_ads",
    "prolist": "etsy_ads",
    "marketing": "etsy_ads",
}


def _category(ledger_type: str) -> str:
    return CATEGORY.get(ledger_type, "etsy_other")


def ledger_rows(entries: Iterable[dict]) -> list[dict]:
    """Etsy ledger entries -> spend rows. Keeps fee charges (negative amounts) and Etsy credits;
    drops sales, fee payments and payouts. Unknown negative types are kept as etsy_other so they
    show up instead of vanishing."""
    rows = []
    for e in entries:
        t = str(e.get("ledger_type") or "")
        amount = int(e.get("amount") or 0)
        if any(m in t.lower() for m in PAYOUT_MARKERS):
            continue
        if amount < 0:
            cost = -amount
        elif t in CREDIT_TYPES:
            cost = -amount
        else:
            continue
        ref_type = e.get("reference_type") or ""
        rows.append({
            "date": dt.datetime.fromtimestamp(int(e["created_timestamp"]), dt.timezone.utc).date().isoformat(),
            "entry_id": e.get("entry_id"),
            "ledger_type": t,
            "category": _category(t),
            "amount_usd": f"{cost / 100:.2f}",
            "reference_type": ref_type,
            # Listing and shop ids only; receipt ids are not needed for spend (rule 4 minimalism).
            "reference_id": e.get("reference_id") if ref_type in ("listing", "shop") else "",
            "source": "etsy_payment_ledger",
        })
    rows.sort(key=lambda r: (r["date"], str(r["entry_id"])))
    return rows


def fetch_ledger(http, shop_id: str, since: dt.date, until: dt.datetime | None = None) -> list[dict]:
    until = until or dt.datetime.now(dt.timezone.utc)
    start = int(dt.datetime(since.year, since.month, since.day, tzinfo=dt.timezone.utc).timestamp())
    entries, offset = [], 0
    while True:
        data = http.get_json(f"shops/{shop_id}/payment-account/ledger-entries",
                             params={"min_created": start, "max_created": int(until.timestamp()),
                                     "limit": 100, "offset": offset})
        page = data.get("results", [])
        entries += page
        if len(page) < 100:
            return entries
        offset += 100


def write_ledger(rows: list[dict], out_dir: Path = SPEND_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "etsy_ledger.csv"
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return path


def _read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _amount(v) -> float | None:
    try:
        return float(v) if str(v).strip() != "" else None
    except ValueError:
        return None


def summarize(today: dt.date, spend_dir: Path = SPEND_DIR) -> dict:
    """Verified spend only. Rows without a parseable amount are reported, never counted."""
    etsy = _read(spend_dir / "etsy_ledger.csv")
    manual = _read(spend_dir / "manual.csv")
    subs = _read(spend_dir / "subscriptions.csv")
    since30 = (today - dt.timedelta(days=30)).isoformat()

    by_cat: dict[str, float] = {}
    last30 = 0.0
    total = 0.0
    bad = []
    for r in etsy + manual:
        a = _amount(r.get("amount_usd"))
        if a is None:
            bad.append(r)
            continue
        cat = r.get("category") or "other"
        by_cat[cat] = round(by_cat.get(cat, 0.0) + a, 2)
        total += a
        if r.get("date", "") >= since30:
            last30 += a
    confirmed = [s for s in subs if _amount(s.get("monthly_usd")) is not None
                 and (s.get("status") or "").lower().startswith("active")]
    unconfirmed = [s for s in subs if _amount(s.get("monthly_usd")) is None
                   and not (s.get("status") or "").lower().startswith(("cancel", "not "))]
    return {
        "total_to_date": round(total, 2),
        "last_30_days": round(last30, 2),
        "by_category": dict(sorted(by_cat.items())),
        "recurring_confirmed_monthly": round(sum(_amount(s["monthly_usd"]) for s in confirmed), 2),
        "recurring_confirmed": [s["vendor"] for s in confirmed],
        "recurring_unconfirmed": [s["vendor"] for s in unconfirmed],
        "unparsed_rows": len(bad),
        "etsy_ledger_through": etsy[-1]["date"] if etsy else None,
    }


def report_lines(s: dict) -> list[str]:
    out = [
        "## Spend (verified entries only)",
        "",
        "Source: `data/spend/` (Etsy payment ledger + owner entries). Nothing here is estimated; a "
        "tool without a confirmed amount is named, not counted.",
        "",
        "| Line | USD |",
        "|---|---|",
    ]
    for cat, amt in s["by_category"].items():
        out.append(f"| {cat} | ${amt:,.2f} |")
    out += [
        f"| **Total to date** | **${s['total_to_date']:,.2f}** |",
        f"| Last 30 days | ${s['last_30_days']:,.2f} |",
        f"| Confirmed recurring per month | ${s['recurring_confirmed_monthly']:,.2f} "
        f"({', '.join(s['recurring_confirmed']) or 'none'}) |",
        "",
        f"Amount not confirmed (owner to fill `monthly_usd` in `data/spend/subscriptions.csv`): "
        f"{', '.join(s['recurring_unconfirmed']) or 'none'}. Etsy ledger through "
        f"{s['etsy_ledger_through'] or 'never fetched'}."
        + (f" {s['unparsed_rows']} row(s) skipped for a missing amount." if s["unparsed_rows"] else ""),
    ]
    return out


def main(argv: list[str] | None = None) -> int:
    from src.clients.etsy_read import EtsyRead
    from src.metrics.collect import ReadOnlySession

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", default="2026-10-15", help="first day to read (shop opened 2026-10-21)")
    ap.add_argument("--out", type=Path, default=SPEND_DIR)
    a = ap.parse_args(argv)
    shop_id = require(os.environ.get("ETSY_SHOP_ID"), "ETSY_SHOP_ID")
    http = EtsyRead(session=ReadOnlySession()).http
    rows = ledger_rows(fetch_ledger(http, shop_id, dt.date.fromisoformat(a.since)))
    path = write_ledger(rows, a.out)
    print(f"{path}: {len(rows)} fee/credit rows, ${sum(float(r['amount_usd']) for r in rows):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
