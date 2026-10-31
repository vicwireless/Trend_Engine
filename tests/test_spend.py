import csv
import datetime as dt
import importlib.util
from pathlib import Path

import pytest
import responses

from src.clients.base import ClientError
from src.clients.etsy_read import BASE_URL, EtsyRead
from src.metrics import collect as C
from src.metrics import spend as S
from src.metrics import weekly as W

TS = 1792700000  # 2026-10-23 UTC

ENTRIES = [
    {"entry_id": 1, "ledger_type": "tier_2_subscription", "amount": -1000, "created_timestamp": TS,
     "reference_type": "shop", "reference_id": 77},
    {"entry_id": 2, "ledger_type": "seller_onboarding_fee", "amount": -2900, "created_timestamp": TS,
     "reference_type": "shop", "reference_id": 77},
    {"entry_id": 3, "ledger_type": "seller_onboarding_fee_payment", "amount": 2900, "created_timestamp": TS,
     "reference_type": "seller_onboarding_fee", "reference_id": 9},
    {"entry_id": 4, "ledger_type": "listing", "amount": -20, "created_timestamp": TS,
     "reference_type": "listing", "reference_id": 4601},
    {"entry_id": 5, "ledger_type": "etsy_plus_credit", "amount": 20, "created_timestamp": TS,
     "reference_type": "etsy", "reference_id": 5},
    {"entry_id": 6, "ledger_type": "sale", "amount": 699, "created_timestamp": TS,
     "reference_type": "receipt", "reference_id": 123456},
    {"entry_id": 7, "ledger_type": "transaction", "amount": -45, "created_timestamp": TS,
     "reference_type": "receipt", "reference_id": 123456},
    {"entry_id": 8, "ledger_type": "disbursement", "amount": -500, "created_timestamp": TS,
     "reference_type": "payment_account", "reference_id": 1},
    {"entry_id": 9, "ledger_type": "brand_new_fee", "amount": -100, "created_timestamp": TS,
     "reference_type": "shop", "reference_id": 77},
]


def test_ledger_rows_keeps_fees_and_credits_only():
    rows = S.ledger_rows(ENTRIES)
    ids = [r["entry_id"] for r in rows]
    assert ids == [1, 2, 4, 5, 7, 9]  # payment(3), sale(6), payout(8) dropped
    by_id = {r["entry_id"]: r for r in rows}
    assert by_id[5]["amount_usd"] == "-0.20"            # credit reduces spend
    assert by_id[9]["category"] == "etsy_other"          # unknown fee kept visible
    assert by_id[7]["reference_id"] == ""                # receipt ids not stored
    assert by_id[4]["reference_id"] == 4601
    assert sum(float(r["amount_usd"]) for r in rows) == pytest.approx(10 + 29 + 0.20 - 0.20 + 0.45 + 1.00)


@responses.activate
def test_fetch_ledger_is_get_only_and_paginates(monkeypatch):
    monkeypatch.setenv("ETSY_SHARED_SECRET", "sec")
    http = EtsyRead("key", "tok", session=C.ReadOnlySession()).http
    url = f"{BASE_URL}/shops/77/payment-account/ledger-entries"
    responses.get(url, json={"results": [dict(ENTRIES[0], entry_id=i) for i in range(100)]})
    responses.get(url, json={"results": ENTRIES[:2]})
    got = S.fetch_ledger(http, "77", dt.date(2026, 10, 15), dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc))
    assert len(got) == 102
    assert "offset=100" in responses.calls[1].request.url
    with pytest.raises(ClientError):
        C.ReadOnlySession().post(url)


def _write(path: Path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def test_summarize_counts_only_confirmed_amounts(tmp_path):
    S.write_ledger(S.ledger_rows(ENTRIES[:5]), tmp_path)
    _write(tmp_path / "manual.csv", S.MANUAL_COLUMNS, [
        {"date": "2026-10-24", "vendor": "SerpApi", "category": "tools", "amount_usd": "25.00",
         "recurring": "monthly", "source": "invoice", "entered_by": "owner"},
        {"date": "2026-10-24", "vendor": "Mystery", "category": "tools", "amount_usd": "",
         "recurring": "no", "source": "", "entered_by": "owner"},
    ])
    _write(tmp_path / "subscriptions.csv", S.SUBSCRIPTION_COLUMNS, [
        {"vendor": "Etsy Plus", "monthly_usd": "10.00", "status": "active"},
        {"vendor": "Postiz", "monthly_usd": "", "status": "active (owner-reported)"},
        {"vendor": "Old tool", "monthly_usd": "", "status": "cancelled"},
    ])
    s = S.summarize(dt.date(2026, 10, 31), tmp_path)
    assert s["total_to_date"] == pytest.approx(39.00 + 25.00)
    assert s["recurring_confirmed_monthly"] == 10.0
    assert s["recurring_unconfirmed"] == ["Postiz"]
    assert s["unparsed_rows"] == 1
    text = "\n".join(S.report_lines(s))
    assert "Postiz" in text and "$64.00" in text


def test_summarize_empty_dir(tmp_path):
    s = S.summarize(dt.date(2026, 10, 31), tmp_path)
    assert s["total_to_date"] == 0 and s["etsy_ledger_through"] is None
    assert "never fetched" in "\n".join(S.report_lines(s))


def test_time_lines_flags_stale_log(tmp_path):
    log = tmp_path / "time_log.csv"
    _write(log, ["date", "session", "minutes", "notes"],
           [{"date": "2026-10-23", "session": "setup", "minutes": "360", "notes": ""}])
    text = "\n".join(W.time_lines(dt.date(2026, 10, 31), log))
    assert "Stale" in text and "360 min" in text
    _write(log, ["date", "session", "minutes", "notes"],
           [{"date": "2026-10-30", "session": "publish", "minutes": "30", "notes": ""}])
    text = "\n".join(W.time_lines(dt.date(2026, 10, 31), log))
    assert "Stale" not in text and "last 7 days 30 min" in text


def _log_entry():
    path = Path(__file__).resolve().parents[1] / "tools" / "log_entry.py"
    spec = importlib.util.spec_from_file_location("log_entry", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_log_entry_appends_and_validates(tmp_path):
    L = _log_entry()
    tl, man = tmp_path / "time_log.csv", tmp_path / "spend" / "manual.csv"
    L.main(["time", "--minutes", "25", "--session", "publish", "--date", "2026-10-26"], tl, man)
    L.main(["spend", "--vendor", "SerpApi", "--category", "tools", "--amount", "25",
            "--source", "invoice", "--date", "2026-10-24"], tl, man)
    assert list(csv.DictReader(tl.open()))[0]["minutes"] == "25"
    assert list(csv.DictReader(man.open()))[0]["amount_usd"] == "25.00"
    with pytest.raises(SystemExit):
        L.main(["time", "--minutes", "0", "--session", "x"], tl, man)
    tl.write_text("wrong,header\n")
    with pytest.raises(SystemExit):
        L.main(["time", "--minutes", "5", "--session", "x"], tl, man)
