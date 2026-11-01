import csv
import datetime as dt
import json
from pathlib import Path

import pytest
import responses
import yaml

from src.clients.base import ClientError
from src.clients.etsy_read import BASE_URL, EtsyRead
from src.metrics import collect as C
from src.metrics import weekly as W

SENT = "Designed by the seller with AI-assisted tools (code-generated layout); see shop policies."


def listing(lid, views, favs, desc=SENT, created=1793000000):
    return {"listing_id": lid, "title": f"Listing {lid}", "state": "active", "listing_type": "download",
            "price": {"amount": 499, "divisor": 100, "currency_code": "USD"}, "views": views,
            "num_favorers": favs, "description": desc, "original_creation_timestamp": created}


RECEIPTS = {"count": 3, "results": [
    {"receipt_id": 1, "status": "Paid", "name": "Jane Buyer", "buyer_email": "jane@example.com",
     "transactions": [{"listing_id": 11, "quantity": 2, "price": {"amount": 499, "divisor": 100}},
                      {"listing_id": 11, "quantity": 1, "price": {"amount": 499, "divisor": 100}}]},
    {"receipt_id": 2, "status": "Completed", "transactions": [{"listing_id": 12, "quantity": 1, "price": {"amount": 899, "divisor": 100}}]},
    {"receipt_id": 3, "status": "Canceled", "transactions": [{"listing_id": 12, "quantity": 1, "price": {"amount": 899, "divisor": 100}}]},
]}


@pytest.fixture
def etsy(monkeypatch):
    monkeypatch.setenv("ETSY_SHARED_SECRET", "sec")
    return EtsyRead("key", "tok", session=C.ReadOnlySession())


def mock_api(listings, receipts=RECEIPTS):
    responses.get(f"{BASE_URL}/shops/77", json={"listing_active_count": len(listings), "num_favorers": 0})
    responses.get(f"{BASE_URL}/shops/77/listings", json={"count": len(listings), "results": listings})
    responses.get(f"{BASE_URL}/shops/77/receipts", json=receipts)


@responses.activate
def test_collect_writes_csv_and_aggregates_sales(tmp_path, etsy):
    mock_api([listing(11, 5, 1), listing(12, 3, 0, desc="no disclosure here")])
    res = C.collect("2026-11-01", etsy=etsy, shop_id="77", out_dir=tmp_path, sentences=[SENT])
    rows = {r["listing_id"]: r for r in res["rows"]}
    assert rows[11]["orders_total"] == 1 and rows[11]["units_total"] == 3 and rows[11]["revenue_usd_total"] == 14.97
    assert rows[12]["orders_total"] == 1 and rows[12]["revenue_usd_total"] == 8.99  # canceled excluded
    assert rows[11]["views_1d"] == ""  # no baseline: never present lifetime as daily
    assert rows[11]["has_disclosure_sentence"] is True and rows[12]["has_disclosure_sentence"] is False
    assert res["shop"]["receipts_excluded"] == 1 and res["shop"]["gross_item_revenue_usd_total"] == 23.96
    assert (tmp_path / "2026-11-01.csv").exists() and (tmp_path / "2026-11-01.shop.json").exists()
    for call in responses.calls:
        assert call.request.method == "GET"


@responses.activate
def test_no_buyer_data_written(tmp_path, etsy):
    mock_api([listing(11, 5, 1)])
    C.collect("2026-11-01", etsy=etsy, shop_id="77", out_dir=tmp_path, sentences=[SENT])
    blob = "".join(p.read_text() for p in tmp_path.iterdir())
    for pii in ("Jane", "jane@example.com", "receipt_id"):
        assert pii not in blob


@responses.activate
def test_daily_deltas_and_missing_listing_carried(tmp_path, etsy):
    mock_api([listing(11, 5, 1), listing(12, 3, 0)])
    C.collect("2026-11-01", etsy=etsy, shop_id="77", out_dir=tmp_path, sentences=[SENT])
    responses.reset()
    mock_api([listing(11, 9, 2)])
    responses.get(f"{BASE_URL}/listings/12", json={**listing(12, 4, 0), "state": "inactive"})
    res = C.collect("2026-11-02", etsy=etsy, shop_id="77", out_dir=tmp_path, sentences=[SENT])
    rows = {r["listing_id"]: r for r in res["rows"]}
    assert rows[11]["views_1d"] == 4 and rows[11]["favorites_1d"] == 1 and rows[11]["orders_1d"] == 0
    assert rows[12]["state"] == "inactive" and rows[12]["views_1d"] == 1


def test_read_only_session_refuses_writes():
    with pytest.raises(ClientError):
        C.ReadOnlySession().request("POST", "https://openapi.etsy.com/v3/application/listings")


def test_disclosure_handles_html_escaping():
    sent = "This design was created by the seller using AI image tools from the seller's original prompts and then edited; see shop policies."
    assert C.has_disclosure("Intro.  This design was created by the seller using AI image tools from the seller&#39;s original\nprompts and then edited; see shop policies.", [sent])


def test_engine_config_sentences_load():
    assert len(C.disclosure_sentences()) >= 2


def write_snap(d: Path, date: str, rows: list[dict]):
    d.mkdir(parents=True, exist_ok=True)
    with (d / f"{date}.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=C.COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in C.COLUMNS})


def snap_row(lid, views, orders=0, rev=0.0, pub="2026-10-23", disc="True"):
    return {"listing_id": lid, "title": f"L{lid}", "state": "active", "price_usd": 4.99, "published_date": pub,
            "views_total": views, "favorites_total": 0, "orders_total": orders, "revenue_usd_total": rev,
            "has_disclosure_sentence": disc}


def ledger(d: Path, lines):
    d.mkdir(parents=True, exist_ok=True)
    (d / "2026-10-23.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))


def test_weekly_summary_and_gate(tmp_path):
    m = tmp_path / "metrics"
    write_snap(m, "2026-11-01", [snap_row(i, 1) for i in range(20)])  # previous week (Sunday)
    write_snap(m, "2026-11-04", [snap_row(i, 3, orders=1 if i == 0 else 0, rev=4.99 if i == 0 else 0) for i in range(20)])
    led = tmp_path / "ledger"
    ledger(led, [{"idempotency_key": "a+0", "status": "pending"}, {"idempotency_key": "a+0", "status": "ok"}])
    text = W.summarize(dt.date(2026, 11, 4), m, led, tmp_path / "none.csv", open_ledger_prs=0)
    assert "week of 2026-11-02" in text and "baseline **2026-11-01**" in text
    assert "| Views | 40 | 60 |" in text and "| Orders | 1 | 1 |" in text
    assert "MET (pending owner confirmation)" in text and "UNVERIFIED" in text
    assert "What the Etsy API cannot provide" in text


def test_gate_not_met_cases(tmp_path):
    m = tmp_path / "metrics"
    write_snap(m, "2026-10-31", [snap_row(i, 0, pub="2026-10-31" if i < 2 else "2026-10-23") for i in range(20)])
    led = tmp_path / "ledger"
    ledger(led, [{"idempotency_key": "a+0", "status": "failed"}])
    pins = tmp_path / "pins.csv"
    pins.write_text("date,pin,url\n2026-10-24,pin-1,https://example.invalid\n")
    g = W.day7_gate(W.snapshots(m), dt.date(2026, 10, 31), led, pins, open_ledger_prs=1)
    assert g["checks"]["live_listings"]["status"] == "NOT MET"  # 18 created by the deadline
    assert g["checks"]["ledger_clean"]["status"] == "NOT MET"
    assert g["checks"]["pins_posting"]["status"] == "MET"
    assert g["overall"] == "NOT MET"


def test_metrics_workflow_has_no_write_secrets():
    wf = Path(".github/workflows/metrics.yml").read_text()
    for s in ("ETSY_WRITE_REFRESH_TOKEN", "PRINTIFY_WRITE_TOKEN", "PINTEREST_TOKEN", "PAYHIP_API_KEY"):
        assert s not in wf
    on = yaml.safe_load(wf)[True]  # PyYAML parses the bare key `on` as True
    assert set(on) == {"schedule", "workflow_dispatch"}


# --- Refresh-token rotation (2026-11-01: Etsy revoked a reused refresh token) ---
from src.clients import etsy_auth as A


@responses.activate
def test_access_token_persists_rotated_refresh_token(tmp_path, monkeypatch):
    f = tmp_path / "rot"
    monkeypatch.setenv("ETSY_KEYSTRING", "key")
    monkeypatch.setenv("ETSY_REFRESH_TOKEN", "r0")
    monkeypatch.delenv("ETSY_READ_TOKEN", raising=False)
    monkeypatch.setenv(A.ROTATED_FILE_VAR, str(f))
    responses.post(A.TOKEN_URL, json={"access_token": "a1", "refresh_token": "r1"})
    responses.post(A.TOKEN_URL, json={"access_token": "a2", "refresh_token": "r2"})
    assert A.access_token("ETSY_READ_TOKEN", "ETSY_REFRESH_TOKEN") == "a1"
    assert f.read_text() == "r1" and (f.stat().st_mode & 0o777) == 0o600
    # A second process in the same run starts from the original env value but must use the file.
    monkeypatch.setenv("ETSY_REFRESH_TOKEN", "r0")
    assert A.access_token("ETSY_READ_TOKEN", "ETSY_REFRESH_TOKEN") == "a2"
    assert "refresh_token=r1" in responses.calls[1].request.body
    assert f.read_text() == "r2"


@responses.activate
def test_refresh_error_reports_etsy_reason_without_token(monkeypatch):
    monkeypatch.setenv("ETSY_KEYSTRING", "key")
    monkeypatch.setenv("ETSY_REFRESH_TOKEN", "secret-refresh")
    monkeypatch.delenv("ETSY_READ_TOKEN", raising=False)
    monkeypatch.delenv(A.ROTATED_FILE_VAR, raising=False)
    responses.post(A.TOKEN_URL, status=400, json={"error": "invalid_grant", "error_description": "refresh_token is revoked"})
    with pytest.raises(A.AuthError) as e:
        A.access_token("ETSY_READ_TOKEN", "ETSY_REFRESH_TOKEN")
    assert "refresh_token is revoked" in str(e.value) and "secret-refresh" not in str(e.value)


def test_metrics_workflow_saves_rotated_token():
    wf = yaml.safe_load(Path(".github/workflows/metrics.yml").read_text())
    steps = wf["jobs"]["measure"]["steps"]
    last = steps[-1]
    assert last["if"] == "always()" and "gh secret set ETSY_REFRESH_TOKEN" in last["run"]
    collect = next(s for s in steps if s.get("name", "").startswith("Collect"))
    assert "ETSY_ROTATED_REFRESH_FILE" in collect["env"]
