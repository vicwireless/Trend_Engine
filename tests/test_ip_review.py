import datetime as dt
import json
from pathlib import Path

import jsonschema
import pytest

from src.compliance.blocklist import Blocklist
from src.compliance.ip_review import CheckResult, Subject, is_veto, missing_checks, review

ROOT = Path(__file__).resolve().parents[1]
IP_REVIEW = jsonschema.Draft202012Validator(
    json.loads((ROOT / "schemas" / "concept.json").read_text())["properties"]["ip_review"])
BL = Blocklist.load()
NOW = dt.datetime(2026, 10, 24, 12, tzinfo=dt.timezone.utc)
T = "2026-10-24T11:00:00+00:00"


def passing(**over):
    checks = {
        "origin": CheckResult("pass", "web + KYM search: no single source", T),
        "trademark": CheckResult("pass", "tmsearch 'plant whisperer in training': 0 live/pending", T, ("025", "021")),
        "etsy_marketplace": CheckResult("pass", "findAllListingsActive: 40 generic results, no licensed", T),
        "text_copyright": CheckResult("pass", "original short phrase", T),
        "image_provenance": CheckResult("pass", "own typography, no images", T),
    }
    checks.update(over)
    return checks


def subject(fmt="tshirt", **kw):
    return Subject(phrase="plant whisperer in training", product_format=fmt, **kw)


def test_all_checks_pass():
    out = review(subject(), passing(), blocklist=BL, now=NOW)
    IP_REVIEW.validate(out)
    assert out["status"] == "pass" and out["reasons"] == [] and not is_veto(out)
    assert list(missing_checks(out)) == []


def test_missing_check_is_veto():
    checks = passing()
    del checks["origin"]
    out = review(subject(), checks, blocklist=BL, now=NOW)
    IP_REVIEW.validate(out)
    assert is_veto(out) and "origin: not checked" in out["reasons"]
    assert list(missing_checks(out)) == ["origin"]


@pytest.mark.parametrize("result", ["unknown", "hit"])
def test_unknown_or_hit_is_veto(result):
    out = review(subject(), passing(trademark=CheckResult(result, "pending app 98xxxxxx", T, ("025",))),
                 blocklist=BL, now=NOW)
    assert is_veto(out) and any(r.startswith("trademark:") for r in out["reasons"])


def test_blocklist_runs_on_tags_and_design_text():
    out = review(subject(tags=["grumpy cat shirt"]), passing(), blocklist=BL, now=NOW)
    assert is_veto(out) and "meme_owned/grumpy cat" in out["reasons"][0]
    out = review(subject(design_text=["as seen on TikTok"]), passing(), blocklist=BL, now=NOW)
    assert is_veto(out)


def test_trademark_must_cover_product_classes():
    out = review(subject("mug"), passing(trademark=CheckResult("pass", "tmsearch", T, ("025",))),
                 blocklist=BL, now=NOW)
    assert "trademark: classes ['021'] not searched" in out["reasons"]


def test_unknown_format_and_empty_evidence_are_veto():
    out = review(subject("phone_case"), passing(), blocklist=BL, now=NOW)
    assert any("unknown product_format" in r for r in out["reasons"])
    out = review(subject(), passing(origin=CheckResult("pass", " ", T)), blocklist=BL, now=NOW)
    assert "origin: pass without evidence" in out["reasons"]


def test_no_review_is_veto():
    assert is_veto(None) and is_veto({"status": "veto"})
