import datetime as dt
import json
from pathlib import Path

import jsonschema

from src.compliance.blocklist import Blocklist
from src.sense.signals import from_autocomplete, from_trending_now, ingest_inbox, parse_inbox_csv

ROOT = Path(__file__).resolve().parents[1]
SIGNAL = jsonschema.Draft202012Validator(json.loads((ROOT / "schemas" / "signal.json").read_text()))
BL = Blocklist.load()
DAY = dt.date(2026, 10, 24)
NOW = "2026-10-24T12:00:00+00:00"


def assert_valid(sigs):
    for s in sigs:
        SIGNAL.validate(s)
        assert s["is_estimate"] is True
    assert len({s["signal_id"] for s in sigs}) == len(sigs)


def test_trending_now_signals_flag_blocklist():
    result = {"fetched_at": NOW, "range": "past 168h", "trending": [
        {"query": "friendsmas ideas", "increase_percentage": 500},
        {"query": "nfl scores", "increase_percentage": 1000},
        {"query": "no growth", "increase_percentage": None}]}
    sigs = from_trending_now(result, blocklist=BL)
    assert_valid(sigs)
    assert [s["keyword"] for s in sigs] == ["friendsmas ideas", "nfl scores"]
    assert sigs[0]["window_start"] == "2026-10-18" and "notes" not in sigs[0]
    assert "sports_leagues/nfl" in sigs[1]["notes"]


def test_autocomplete_signals_rank_in_order():
    result = {"fetched_at": NOW, "suggestions": [{"value": "funny plant mug"}, {"value": "plant mom mug"}]}
    sigs = from_autocomplete(result)
    assert_valid(sigs)
    assert [(s["keyword"], s["value"]) for s in sigs] == [("funny plant mug", 1.0), ("plant mom mug", 2.0)]


def test_pinterest_paste_with_growth_columns():
    text = "Trend\tWeekly change\tMonthly change\tYearly change\nfriendsmas\t+120%\t+300%\t+1,400%\ncozy reading nook\t-5%\t+40%\tn/a\n"
    sigs = parse_inbox_csv(text, source="pinterest_trends", day=DAY, fetched_at=NOW,
                           raw_ref="data/inbox/2026-10-24/pinterest_trends.csv", blocklist=BL)
    assert_valid(sigs)
    by = {(s["keyword"], s["metric"]): s for s in sigs}
    assert by[("friendsmas", "growth_wow")]["value"] == 1.2
    assert by[("friendsmas", "growth_yoy")]["value"] == 14.0
    assert by[("friendsmas", "growth_wow")]["window_start"] == "2026-10-17"
    assert by[("cozy reading nook", "trend_rank")]["value"] == 2.0
    assert ("cozy reading nook", "growth_yoy") not in by


def test_erank_csv_and_missing_keyword_column_fails_closed(tmp_path):
    inbox = tmp_path / "data" / "inbox" / "2026-10-24"
    inbox.mkdir(parents=True)
    (inbox / "erank_trendbuzz.csv").write_text("Keyword,Searches\nchristmas gift for friend,\"12,400\"\nstar wars mug,900\n")
    out = ingest_inbox(tmp_path, DAY, blocklist=BL, now=dt.datetime(2026, 10, 24, 12, tzinfo=dt.timezone.utc))
    sigs = json.loads(out["erank"].read_text())
    assert_valid(sigs)
    assert out["erank"] == tmp_path / "data" / "signals" / "2026-10-24" / "erank.json"
    vol = [s for s in sigs if s["metric"] == "search_volume"]
    assert vol[0]["value"] == 12400.0
    assert any("star wars" in s.get("notes", "") for s in sigs if s["keyword"] == "star wars mug")

    (inbox / "pinterest_trends.csv").write_text("Rank,Change\n1,+5%\n")
    try:
        ingest_inbox(tmp_path, DAY, blocklist=BL)
    except ValueError as e:
        assert "no keyword column" in str(e)
    else:
        raise AssertionError("expected ValueError")
