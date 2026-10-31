"""Weekly metrics summary and gate status from data/metrics snapshots. No network calls.

Writes reports/weekly/<week-start>-metrics.md (week starts Monday, UTC). Re-running it during the
week overwrites the same file, so the rolling metrics PR always carries the latest numbers.

    python -m src.metrics.weekly [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from pathlib import Path

from src.metrics import spend as SP

METRICS = Path("data/metrics")
LEDGER = Path("data/ledger")
PINS_LOG = Path("data/marketing/pins_posted.csv")
REPORTS = Path("reports/weekly")
TIME_LOG = Path("data/time_log.csv")
OWNER_CAP_MIN_PER_WEEK = 90  # config/engine.yaml owner_hours_cap_per_week: 1.5

DAY7 = {"deadline": "2026-10-30", "min_live": 20}

CANNOT = [
    "Daily views or visits as Etsy reports them (only lifetime `views` per listing; daily = snapshot delta)",
    "Traffic sources, search terms, Pinterest referrals, conversion rate (Shop Stats only)",
    "Etsy Ads spend, impressions, clicks, ROAS (no Ads API)",
    "Whether the owner ticked the AI-generator field in the listing editor (not in the API; the "
    "description sentence is checked instead)",
    "Pins posted or pin clicks (no Pinterest token; Pinterest hosts are blocked in the cloud env)",
    "Fees and net payout per listing (the payment ledger is shop-level; shop fees are in the Spend section)",
]


def time_lines(today: dt.date, log: Path = TIME_LOG) -> list[str]:
    """Owner minutes from data/time_log.csv. Logged minutes only; a missing week shows as stale."""
    rows = load_rows(log) if log.exists() else []
    mins = [(r.get("date", ""), _num(r.get("minutes"), int)) for r in rows]
    week_ago = (today - dt.timedelta(days=7)).isoformat()
    last7 = sum(m for d, m in mins if d > week_ago)
    last = max((d for d, _ in mins), default=None)
    stale = last is None or last <= week_ago
    return [
        "## Owner time (logged only)",
        "",
        f"Source: `{log}`. Total logged {sum(m for _, m in mins):,} min in {len(mins)} entries; "
        f"last 7 days {last7} min (cap {OWNER_CAP_MIN_PER_WEEK} min/week); last entry {last or 'never'}."
        + (" **Stale: no entry in the last 7 days, so owner yield ($/hr) cannot be computed.** "
           "Log with `python tools/log_entry.py time --minutes N --session \"...\"`." if stale else ""),
    ]


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def snapshots(metrics: Path = METRICS) -> list[Path]:
    return sorted(metrics.glob("????-??-??.csv"))


def week_bounds(day: dt.date) -> tuple[dt.date, dt.date]:
    start = day - dt.timedelta(days=day.weekday())
    return start, start + dt.timedelta(days=6)


def _num(v, cast=float):
    try:
        return cast(v) if v not in (None, "") else 0
    except ValueError:
        return 0


def ledger_status(ledger: Path = LEDGER) -> dict:
    """Clean = the last line for every idempotency key is ok. A failure that was reconciled has a
    later ok line for the same key."""
    last: dict[str, dict] = {}
    for f in sorted(ledger.glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                d = json.loads(line)
                last[d["idempotency_key"]] = d
    bad = [k for k, d in last.items() if d.get("status") != "ok"]
    return {"ops": len(last), "not_ok": bad, "clean": not bad and bool(last)}


def pins_status(log: Path = PINS_LOG, today: dt.date | None = None) -> dict:
    if not log.exists():
        return {"status": "UNVERIFIED", "detail": f"no {log}; the API cannot see pins, owner to confirm"}
    rows = load_rows(log)
    dates = sorted(r.get("date", "") for r in rows if r.get("date"))
    recent = [d for d in dates if today and d >= (today - dt.timedelta(days=7)).isoformat()]
    return {"status": "MET" if recent else "NOT MET",
            "detail": f"{len(rows)} pins logged, {len(recent)} in the last 7 days, last {dates[-1] if dates else 'never'}"}


def day7_gate(snaps: list[Path], today: dt.date, ledger: Path = LEDGER, pins_log: Path = PINS_LOG,
              open_ledger_prs: int | None = None) -> dict:
    latest = load_rows(snaps[-1]) if snaps else []
    active = [r for r in latest if r["state"] == "active"]
    live_by_deadline = [r for r in active if (r.get("published_date") or "9999") <= DAY7["deadline"]]
    disclosed = [r for r in active if r.get("has_disclosure_sentence") == "True"]
    led = ledger_status(ledger)
    pins = pins_status(pins_log, today)
    checks = {
        "live_listings": {
            "status": "MET" if len(live_by_deadline) >= DAY7["min_live"] else "NOT MET",
            "detail": f"{len(active)} active now; {len(live_by_deadline)} still active that were created by {DAY7['deadline']} (need {DAY7['min_live']})"},
        "disclosure_sentence": {
            "status": "MET" if active and len(disclosed) == len(active) else "NOT MET",
            "detail": f"{len(disclosed)}/{len(active)} active descriptions carry an accepted disclosure sentence; editor AI field not API-visible"},
        "ledger_clean": {
            "status": "MET" if led["clean"] and not open_ledger_prs else "NOT MET",
            "detail": f"{led['ops']} ops, last status not ok: {led['not_ok'][:5] or 'none'}; open ledger PRs: "
                      f"{'not checked' if open_ledger_prs is None else open_ledger_prs}"},
        "pins_posting": pins,
    }
    states = {c["status"] for c in checks.values()}
    overall = "NOT MET" if "NOT MET" in states else ("MET (pending owner confirmation)" if "UNVERIFIED" in states else "MET")
    return {"gate": "Day 7", "deadline": DAY7["deadline"], "overall": overall, "checks": checks,
            "snapshot": snaps[-1].stem if snaps else None}


def summarize(day: dt.date, metrics: Path = METRICS, ledger: Path = LEDGER, pins_log: Path = PINS_LOG,
              open_ledger_prs: int | None = None, spend_dir: Path = SP.SPEND_DIR,
              time_log: Path = TIME_LOG) -> str:
    snaps = snapshots(metrics)
    if not snaps:
        raise SystemExit("no snapshots in data/metrics; run python -m src.metrics.collect first")
    start, end = week_bounds(day)
    in_week = [p for p in snaps if start.isoformat() <= p.stem <= end.isoformat()]
    before = [p for p in snaps if p.stem < start.isoformat()]
    last = in_week[-1] if in_week else snaps[-1]
    base = before[-1] if before else (in_week[0] if in_week else None)
    now_rows = {r["listing_id"]: r for r in load_rows(last)}
    base_rows = {r["listing_id"]: r for r in load_rows(base)} if base and base != last else {}
    base_label = base.stem if base_rows else "none (first snapshot; week deltas start next run)"

    keys = [("views_total", int), ("favorites_total", int), ("orders_total", int), ("revenue_usd_total", float)]
    table = []
    for lid, r in now_rows.items():
        b = base_rows.get(lid)
        d = {k: (_num(r[k], c) - _num(b[k], c)) if b else None for k, c in keys}
        table.append((lid, r, d))
    tot_now = {k: sum(_num(r[k], c) for r in now_rows.values()) for k, c in keys}
    tot_wk = {k: (sum(d[k] for _, _, d in table if d[k] is not None) if base_rows else None) for k, _ in keys}
    table.sort(key=lambda t: (-(t[2]["revenue_usd_total"] or 0), -(t[2]["views_total"] or 0), -_num(t[1]["views_total"], int)))

    shop_json = last.with_suffix(".shop.json")
    shop = json.loads(shop_json.read_text()) if shop_json.exists() else {}
    gate = day7_gate(snaps, day, ledger, pins_log, open_ledger_prs)

    def fmt(v, money=False):
        if v is None:
            return "n/a"
        return f"${v:,.2f}" if money else f"{int(v):,}"

    views_wk, orders_wk = tot_wk["views_total"], tot_wk["orders_total"]
    conv = f"{orders_wk / views_wk:.1%}" if views_wk else "n/a"
    out = [
        f"# Weekly metrics, week of {start.isoformat()} to {end.isoformat()}",
        "",
        f"Source: Etsy Open API v3 (Etsy data), snapshots in `data/metrics/`. Latest snapshot **{last.stem}**; "
        f"week baseline **{base_label}**. Generated by `python -m src.metrics.weekly` (no network).",
        "",
        "## Summary",
        "",
        "| Metric | This week | Lifetime |",
        "|---|---|---|",
        f"| Active listings | | {shop.get('active_rows', sum(1 for r in now_rows.values() if r['state'] == 'active'))} |",
        f"| Views | {fmt(views_wk)} | {fmt(tot_now['views_total'])} |",
        f"| Favorites | {fmt(tot_wk['favorites_total'])} | {fmt(tot_now['favorites_total'])} |",
        f"| Orders | {fmt(orders_wk)} | {fmt(tot_now['orders_total'])} |",
        f"| Gross item revenue | {fmt(tot_wk['revenue_usd_total'], True)} | {fmt(tot_now['revenue_usd_total'], True)} |",
        f"| Orders per view | {conv} | |",
        f"| Shop favorers / reviews | | {shop.get('shop_favorers', 'n/a')} / {shop.get('review_count', 'n/a')} |",
        "",
        "Revenue is item price x quantity before discounts, excluding shipping, tax and Etsy fees; "
        "canceled and fully refunded receipts are excluded. Listings are never judged on views "
        "alone (CLAUDE.md rule 7, docs/redefine.md).",
        "",
        f"## Gate status: {gate['gate']} (deadline {gate['deadline']}): **{gate['overall']}**",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for name, c in gate["checks"].items():
        out.append(f"| {name.replace('_', ' ')} | {c['status']} | {c['detail']} |")
    out += [
        "",
        "## Per listing",
        "",
        "| Listing | Title | State | Price | Views wk / life | Favs wk / life | Orders wk / life | Revenue wk / life |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for lid, r, d in table:
        title = (r.get("title") or "")[:48].replace("|", "/")
        out.append(
            f"| {lid} | {title} | {r['state']} | {fmt(_num(r['price_usd']), True)} | "
            f"{fmt(d['views_total'])} / {fmt(_num(r['views_total'], int))} | "
            f"{fmt(d['favorites_total'])} / {fmt(_num(r['favorites_total'], int))} | "
            f"{fmt(d['orders_total'])} / {fmt(_num(r['orders_total'], int))} | "
            f"{fmt(d['revenue_usd_total'], True)} / {fmt(_num(r['revenue_usd_total']), True)} |")
    out += [""] + SP.report_lines(SP.summarize(day, spend_dir))
    out += [""] + time_lines(day, time_log)
    out += ["", "## What the Etsy API cannot provide", ""] + [f"- {c}" for c in CANNOT]
    out += ["", "Use the weekly Shop Stats CSV export (`data/stats_exports/`) for visits, sources and ads.", ""]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=dt.datetime.now(dt.timezone.utc).date().isoformat())
    ap.add_argument("--out", type=Path, default=REPORTS)
    ap.add_argument("--open-ledger-prs", type=int, default=None,
                    help="count of open 'ledger:' PRs (the workflow passes it; omitted = not checked)")
    a = ap.parse_args(argv)
    day = dt.date.fromisoformat(a.date)
    text = summarize(day, open_ledger_prs=a.open_ledger_prs)
    a.out.mkdir(parents=True, exist_ok=True)
    path = a.out / f"{week_bounds(day)[0].isoformat()}-metrics.md"
    path.write_text(text)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
