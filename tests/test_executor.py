import copy
import datetime as dt
import json
import re
import shutil
from pathlib import Path

import pytest
import responses
import yaml

from src.executor import run as runner
from src.executor.hashing import file_sha256, payload_sha256
from src.executor.ledger import Ledger
from src.executor.ops import ETSY_BASE, PINTEREST_BASE, PRINTIFY_BASE, Context
from tests.conftest import load

REPO = Path(__file__).resolve().parents[1]
TODAY = dt.date(2026, 10, 21)
NOW = dt.datetime(2026, 10, 21, 12, 0, tzinfo=dt.timezone.utc)
R = load("executor/responses.json")
SHOP, PSHOP = "77", "555"
PAYHIP = "https://payhip.test/api/v1"
DISCLOSURE = ("This design was created by the seller using AI image tools from the seller's original prompts "
              "and then edited; see shop policies.")
PARTNER = "Produced by a production partner; see partner disclosure."
TITLE = "Minimalist Pickleball Court Line Art Printable Wall Decor"
TAGS = ["pickleball", "pickleball gift", "court art", "line art", "printable", "wall decor", "sports print",
        "minimalist", "game room", "coach gift", "dink", "paddle sport", "digital download"]


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / "config").mkdir(parents=True)
    shutil.copy(REPO / "config" / "blocklist.yaml", root / "config" / "blocklist.yaml")
    config = yaml.safe_load((REPO / "config" / "engine.yaml").read_text())
    config["etsy"]["ai_disclosure_property"] = {"property_id": 900001, "value_ids": [1], "values": ["Yes"]}
    config["payhip"]["api_base_url"] = PAYHIP
    (root / "config" / "engine.yaml").write_text(yaml.safe_dump(config))

    costs = root / "data" / "costs"
    costs.mkdir(parents=True)
    fees = json.loads((REPO / "data" / "costs" / "2026-10-21-channel-fees.json").read_text())
    fees.update(as_of="2026-10-20", verified=True)
    fees["channels"]["payhip"]["verified"] = True
    (costs / "2026-10-20-channel-fees.json").write_text(json.dumps(fees))
    (costs / "2026-10-20-products.json").write_text(json.dumps({
        "as_of": "2026-10-20", "verified": True, "source": "test",
        "items": {"digital": {"unit_cost_usd": 0.0},
                  "tee-s": {"unit_cost_usd": 9.50, "shipping_usd": 4.75},
                  "tee-m": {"unit_cost_usd": 9.50, "shipping_usd": 4.75}}}))
    (costs / "2026-09-01-stale.json").write_text(json.dumps({
        "as_of": "2026-09-01", "verified": True, "items": {"digital": {"unit_cost_usd": 0.0}}}))

    (root / "assets" / "digital").mkdir(parents=True)
    (root / "assets" / "digital" / "court.pdf").write_bytes(b"%PDF-1.4 court")
    (root / "assets" / "digital" / "court.jpg").write_bytes(b"\xff\xd8 jpg")
    (root / "releases").mkdir()

    for k, v in {"ETSY_KEYSTRING": "k", "ETSY_SHARED_SECRET": "s", "ETSY_WRITE_TOKEN": "w", "ETSY_SHOP_ID": SHOP,
                 "PRINTIFY_WRITE_TOKEN": "p", "PRINTIFY_SHOP_ID": PSHOP,
                 "PINTEREST_TOKEN": "pin", "PAYHIP_API_KEY": "ph"}.items():
        monkeypatch.setenv(k, v)
    return root


def ctx_for(root):
    return Context(root, runner.load_config(root), http_kwargs={"sleep": lambda s: None})


def ledger_for(root):
    return Ledger(root / "data" / "ledger", now=lambda: NOW)


def write_manifest(root, ops, mid="2026-10-21-wk43", **overrides):
    manifest = {
        "manifest_id": mid, "created_at": "2026-10-21T10:00:00Z", "created_by": "claude",
        "summary": "test", "owner_minutes_estimate": 30,
        "ops": [{"op": name, "niche": niche, "payload": p, "payload_sha256": payload_sha256(p)}
                for name, niche, p in ops],
        **overrides,
    }
    path = root / "releases" / f"{mid}.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    return path


def execute(root, path, **kw):
    return runner.execute(path, ctx_for(root), ledger_for(root), today=TODAY, **kw)


def ledger_lines(root):
    return ledger_for(root).entries()


# ------------------------------------------------------------------ payloads

def create_payload(**kw):
    return {"title": TITLE, "description": f"Clean court lines for the pickleball fan.\n\n{DISCLOSURE}",
            "tags": TAGS, "taxonomy_id": 2078, "who_made": "i_did", "when_made": "made_to_order",
            "ai_assisted": True, "price_usd": 7.99, "cost_snapshot": "data/costs/2026-10-20-products.json",
            "cost_key": "digital", **kw}


def file_payload(root, ref="$ref:ops[0].listing_id"):
    return {"listing_id": ref, "path": "assets/digital/court.pdf", "name": "pickleball-court-8x10.pdf",
            "file_sha256": file_sha256(root / "assets/digital/court.pdf")}


def image_payload(root, ref="$ref:ops[0].listing_id"):
    return {"listing_id": ref, "path": "assets/digital/court.jpg", "rank": 1, "alt_text": "Court line art",
            "file_sha256": file_sha256(root / "assets/digital/court.jpg")}


def printify_payload(**kw):
    return {"title": "Retro Court Club Tee", "description": f"Soft tee.\n\n{DISCLOSURE}\n\n{PARTNER}", "tags": ["pickleball"],
            "blueprint_id": 6, "print_provider_id": 99, "ai_assisted": True,
            "variants": [{"id": 12100, "price_usd": 25.99, "cost_key": "tee-s"},
                         {"id": 12101, "price_usd": 25.99, "cost_key": "tee-m"}],
            "print_areas": [{"variant_ids": [12100, 12101], "placeholders": [{"position": "front", "images": []}]}],
            "cost_snapshot": "data/costs/2026-10-20-products.json", **kw}


# ------------------------------------------------------------------ mocks

def mock_digital_flow():
    responses.post(f"{ETSY_BASE}/shops/{SHOP}/listings", json=R["etsy_create_listing"])
    responses.put(f"{ETSY_BASE}/shops/{SHOP}/listings/2001/properties/900001", json=R["etsy_property"])
    responses.get(f"{ETSY_BASE}/listings/2001", json=R["etsy_listing_draft"])
    responses.post(f"{ETSY_BASE}/shops/{SHOP}/listings/2001/files", json=R["etsy_file"])
    responses.get(f"{ETSY_BASE}/shops/{SHOP}/listings/2001/files/3001", json=R["etsy_file"])
    responses.post(f"{ETSY_BASE}/shops/{SHOP}/listings/2001/images", json=R["etsy_image"])
    responses.get(f"{ETSY_BASE}/listings/2001/images/4001", json=R["etsy_image"])
    responses.patch(f"{ETSY_BASE}/shops/{SHOP}/listings/2001", json={})


def writes():
    return [c for c in responses.calls if c.request.method != "GET"]


# ------------------------------------------------------------------ full flow + replay

def digital_manifest(root):
    return write_manifest(root, [
        ("etsy_create_digital_listing", "pickleball", create_payload()),
        ("etsy_upload_file", "pickleball", file_payload(root)),
        ("etsy_upload_image", "pickleball", image_payload(root)),
        ("etsy_activate_listing", "pickleball", {"listing_id": "$ref:ops[0].listing_id"}),
    ])


@responses.activate
def test_digital_listing_flow_resolves_refs_and_reads_back(repo):
    mock_digital_flow()
    # activation read-back must see the active state
    responses.get(f"{ETSY_BASE}/listings/2001", json=R["etsy_listing_active"])
    summary = execute(repo, digital_manifest(repo))

    assert [o["status"] for o in summary["ops"]] == ["ok"] * 4
    assert summary["ops"][1]["result"] == {"listing_id": 2001, "listing_file_id": 3001}
    create = responses.calls[0].request
    assert create.headers["x-api-key"] == "k:s" and create.headers["Authorization"] == "Bearer w"
    assert "type=download" in create.body and "tags=pickleball%2Cpickleball+gift" in create.body
    assert any("/properties/900001" in c.request.url for c in responses.calls)  # AI disclosure attribute
    upload = next(c.request for c in responses.calls if c.request.url.endswith("/files") and c.request.method == "POST")
    assert b"Content-Type: application/pdf" in upload.body  # Etsy rejects typeless file parts
    lines = ledger_lines(repo)
    assert [e["status"] for e in lines] == ["pending", "ok"] * 4
    assert lines[1]["idempotency_key"] == "2026-10-21-wk43+0"
    assert (repo / "data/ledger/2026-10-21.jsonl").exists()


@responses.activate
def test_duplicate_manifest_replay_does_not_write_again(repo):
    mock_digital_flow()
    responses.get(f"{ETSY_BASE}/listings/2001", json=R["etsy_listing_active"])
    path = digital_manifest(repo)
    execute(repo, path)
    calls_after_first, lines_after_first = len(responses.calls), len(ledger_lines(repo))
    assert len(writes()) == 5  # create, property, file, image, activate

    summary = execute(repo, path)

    assert len(responses.calls) == calls_after_first  # no second write, no reads either
    assert [o["status"] for o in summary["ops"]] == ["skipped_duplicate"] * 4
    assert len(ledger_lines(repo)) == lines_after_first


@responses.activate
def test_partial_replay_resumes_after_last_ok_op(repo):
    mock_digital_flow()
    responses.replace(responses.GET, f"{ETSY_BASE}/listings/2001", json=R["etsy_listing_active"])
    path = digital_manifest(repo)
    ledger = ledger_for(repo)
    base = {"manifest_id": "2026-10-21-wk43", "niche": "pickleball", "payload_sha256": "x"}
    ledger.append({**base, "op_index": 0, "idempotency_key": "2026-10-21-wk43+0", "op": "etsy_create_digital_listing",
                   "status": "ok", "write_attempted": True, "result": {"listing_id": 2001}})

    summary = execute(repo, path)

    assert [o["status"] for o in summary["ops"]] == ["skipped_duplicate", "ok", "ok", "ok"]
    assert not any(c.request.url.endswith(f"/shops/{SHOP}/listings") and c.request.method == "POST"
                   for c in responses.calls)


@responses.activate
def test_pending_without_outcome_stops_without_writing(repo):
    path = write_manifest(repo, [("etsy_activate_listing", "pickleball", {"listing_id": 2001})])
    ledger_for(repo).append({"manifest_id": "2026-10-21-wk43", "op_index": 0, "idempotency_key": "2026-10-21-wk43+0",
                             "op": "etsy_activate_listing", "niche": "pickleball", "status": "pending",
                             "write_attempted": True})
    with pytest.raises(runner.UnknownState):
        execute(repo, path)
    assert len(responses.calls) == 0


@responses.activate
def test_failure_before_write_can_be_retried(repo):
    responses.patch(f"{ETSY_BASE}/shops/{SHOP}/listings/2001", json={})
    responses.get(f"{ETSY_BASE}/listings/2001", json=R["etsy_listing_active"])
    path = write_manifest(repo, [("etsy_activate_listing", "pickleball", {"listing_id": 2001})])
    ledger_for(repo).append({"manifest_id": "2026-10-21-wk43", "op_index": 0, "idempotency_key": "2026-10-21-wk43+0",
                             "op": "etsy_activate_listing", "niche": "pickleball", "status": "failed",
                             "write_attempted": False, "error": "ETSY_WRITE_TOKEN is not set"})
    assert execute(repo, path)["ops"][0]["status"] == "ok"


@responses.activate
def test_missing_credential_fails_without_write(repo, monkeypatch):
    monkeypatch.delenv("ETSY_WRITE_TOKEN")
    path = write_manifest(repo, [("etsy_activate_listing", "pickleball", {"listing_id": 2001})])
    with pytest.raises(runner.ExecutorError):
        execute(repo, path)
    assert len(responses.calls) == 0
    assert ledger_lines(repo)[-1]["write_attempted"] is False


@responses.activate
def test_429_replay_inside_op_creates_exactly_one_listing(repo):
    responses.post(f"{ETSY_BASE}/shops/{SHOP}/listings", status=429, headers={"Retry-After": "2"})
    responses.post(f"{ETSY_BASE}/shops/{SHOP}/listings", json=R["etsy_create_listing"])
    responses.put(f"{ETSY_BASE}/shops/{SHOP}/listings/2001/properties/900001", json=R["etsy_property"])
    responses.get(f"{ETSY_BASE}/listings/2001", json=R["etsy_listing_draft"])
    path = write_manifest(repo, [("etsy_create_digital_listing", "pickleball", create_payload())])

    summary = execute(repo, path)

    posts = [c for c in responses.calls if c.request.method == "POST"]
    assert [c.response.status_code for c in posts] == [429, 200]
    assert summary["ops"][0]["status"] == "ok"


@responses.activate
def test_server_error_after_write_attempt_blocks_rerun(repo):
    responses.patch(f"{ETSY_BASE}/shops/{SHOP}/listings/2001", status=500)
    path = write_manifest(repo, [("etsy_activate_listing", "pickleball", {"listing_id": 2001})])
    with pytest.raises(runner.ExecutorError):
        execute(repo, path)
    with pytest.raises(runner.UnknownState):
        execute(repo, path)
    assert len(responses.calls) == 1


@responses.activate
def test_readback_mismatch_stops_and_blocks_replay(repo):
    responses.patch(f"{ETSY_BASE}/shops/{SHOP}/listings/2001", json={})
    responses.get(f"{ETSY_BASE}/listings/2001", json=R["etsy_listing_draft"])  # still draft
    path = write_manifest(repo, [("etsy_activate_listing", "pickleball", {"listing_id": 2001})])
    with pytest.raises(runner.UnknownState):
        execute(repo, path)
    assert ledger_lines(repo)[-1]["status"] == "readback_failed"
    n = len(responses.calls)
    with pytest.raises(runner.UnknownState):
        execute(repo, path)
    assert len(responses.calls) == n


# ------------------------------------------------------------------ every other op

@responses.activate
def test_update_price(repo):
    responses.get(f"{ETSY_BASE}/listings/2001/inventory", json=R["etsy_inventory_before"])
    responses.put(f"{ETSY_BASE}/listings/2001/inventory", json={})
    responses.get(f"{ETSY_BASE}/listings/2001/inventory", json=R["etsy_inventory_after"])
    path = write_manifest(repo, [("etsy_update_price", "pickleball", {
        "listing_id": 2001, "offer_type": "digital", "price_usd": 8.75,
        "cost_snapshot": "data/costs/2026-10-20-products.json", "cost_key": "digital"})])
    out = execute(repo, path)["ops"][0]
    assert out["status"] == "ok" and out["readback"] == {"prices_usd": [8.75]}
    put = json.loads(next(c for c in responses.calls if c.request.method == "PUT").request.body)
    assert put["products"][0]["offerings"][0] == {"price": 8.75, "quantity": 999, "is_enabled": True}


@responses.activate
def test_update_price_over_10pct_step_refused_before_write(repo):
    responses.get(f"{ETSY_BASE}/listings/2001/inventory", json=R["etsy_inventory_before"])
    path = write_manifest(repo, [("etsy_update_price", "pickleball", {
        "listing_id": 2001, "offer_type": "digital", "price_usd": 8.99,
        "cost_snapshot": "data/costs/2026-10-20-products.json", "cost_key": "digital"})])
    with pytest.raises(runner.ExecutorError, match="price step"):
        execute(repo, path)
    assert all(c.request.method == "GET" for c in responses.calls)
    assert ledger_lines(repo)[-1]["write_attempted"] is False


@responses.activate
def test_update_price_cooldown_blocks_second_change(repo):
    responses.get(f"{ETSY_BASE}/listings/2001/inventory", json=R["etsy_inventory_before"])
    responses.put(f"{ETSY_BASE}/listings/2001/inventory", json={})
    responses.get(f"{ETSY_BASE}/listings/2001/inventory", json=R["etsy_inventory_after"])
    op = ("etsy_update_price", "pickleball", {"listing_id": 2001, "offer_type": "digital", "price_usd": 8.75,
          "cost_snapshot": "data/costs/2026-10-20-products.json", "cost_key": "digital"})
    execute(repo, write_manifest(repo, [op]))
    second = write_manifest(repo, [op], mid="2026-10-21-wk43b")
    with pytest.raises(runner.PreflightFailed, match="cool-down"):
        execute(repo, second)


@responses.activate
def test_deactivate(repo):
    responses.patch(f"{ETSY_BASE}/shops/{SHOP}/listings/2001", json={})
    responses.get(f"{ETSY_BASE}/listings/2001", json=R["etsy_listing_inactive"])
    path = write_manifest(repo, [("etsy_deactivate_listing", "pickleball", {"listing_id": 2001, "reason": "R-RETIRE"})])
    assert execute(repo, path)["ops"][0]["status"] == "ok"
    assert "state=inactive" in responses.calls[0].request.body


@responses.activate
def test_printify_create_and_publish(repo):
    responses.post(f"{PRINTIFY_BASE}/shops/{PSHOP}/products.json", json=R["printify_product_created"])
    responses.get(f"{PRINTIFY_BASE}/shops/{PSHOP}/products/pf_abc123.json", json=R["printify_product"])
    responses.post(f"{PRINTIFY_BASE}/shops/{PSHOP}/products/pf_abc123/publish.json", json={})
    responses.get(f"{PRINTIFY_BASE}/shops/{PSHOP}/products/pf_abc123.json", json=R["printify_product_locked"])
    path = write_manifest(repo, [
        ("printify_create_product", "pickleball", printify_payload()),
        ("printify_publish", "pickleball", {"product_id": "$ref:ops[0].product_id", "partner_checked": True}),
    ])
    summary = execute(repo, path)
    assert [o["status"] for o in summary["ops"]] == ["ok", "ok"]
    body = json.loads(responses.calls[0].request.body)
    assert body["variants"][0] == {"id": 12100, "price": 2599, "is_enabled": True}
    assert "/products/pf_abc123/publish.json" in responses.calls[2].request.url


def test_pod_publish_requires_partner_checked(repo):
    path = write_manifest(repo, [("printify_publish", "pickleball", {"product_id": "pf_abc123", "partner_checked": False})])
    with pytest.raises(runner.PreflightFailed, match="partner_checked"):
        execute(repo, path)


def test_pod_listing_requires_partner_sentence(repo):
    payload = printify_payload(description=f"Soft tee.\n\n{DISCLOSURE}")
    path = write_manifest(repo, [("printify_create_product", "pickleball", payload)])
    with pytest.raises(runner.PreflightFailed, match="production-partner sentence"):
        execute(repo, path)


def test_unverified_channel_fees_block_that_channel(repo):
    p = repo / "data" / "costs" / "2026-10-20-channel-fees.json"
    fees = json.loads(p.read_text())
    fees["channels"]["payhip"]["verified"] = False
    p.write_text(json.dumps(fees))
    path = write_manifest(repo, [("payhip_create_product", "pickleball", {
        "name": "Pickleball Court Printable", "description": f"Printable.\n\n{DISCLOSURE}", "price_usd": 7.99,
        "path": "assets/digital/court.pdf", "file_sha256": file_sha256(repo / "assets/digital/court.pdf"),
        "ai_assisted": True, "cost_snapshot": "data/costs/2026-10-20-products.json", "cost_key": "digital"})])
    with pytest.raises(runner.PreflightFailed, match="not verified"):
        execute(repo, path)


@responses.activate
def test_pinterest_create_pin(repo):
    responses.post(f"{PINTEREST_BASE}/pins", json=R["pinterest_pin"])
    responses.get(f"{PINTEREST_BASE}/pins/pin_777", json=R["pinterest_pin"])
    path = write_manifest(repo, [("pinterest_create_pin", "pickleball", {
        "board_id": "board_1", "title": "Pickleball court art", "link": "https://www.etsy.com/listing/2001",
        "image_url": "https://i.etsystatic.com/court.jpg"})])
    assert execute(repo, path)["ops"][0]["result"] == {"pin_id": "pin_777"}
    assert json.loads(responses.calls[0].request.body)["media_source"]["source_type"] == "image_url"


@responses.activate
def test_payhip_create_product(repo):
    responses.post(f"{PAYHIP}/products", json=R["payhip_product"])
    responses.get(f"{PAYHIP}/products/ph_42", json=R["payhip_product"])
    path = write_manifest(repo, [("payhip_create_product", "pickleball", {
        "name": "Pickleball Court Printable", "description": f"Printable.\n\n{DISCLOSURE}", "price_usd": 7.99,
        "path": "assets/digital/court.pdf", "file_sha256": file_sha256(repo / "assets/digital/court.pdf"),
        "ai_assisted": True, "cost_snapshot": "data/costs/2026-10-20-products.json", "cost_key": "digital"})])
    assert execute(repo, path)["ops"][0]["status"] == "ok"
    assert responses.calls[0].request.headers["payhip-api-key"] == "ph"


# ------------------------------------------------------------------ preflight: zero writes on any failure

def _set_config(root, **changes):
    p = root / "config" / "engine.yaml"
    c = yaml.safe_load(p.read_text())
    for k, v in changes.items():
        cur = c
        *parents, leaf = k.split(".")
        for part in parents:
            cur = cur[part]
        cur[leaf] = v
    p.write_text(yaml.safe_dump(c))


def _fill_week(root, op, n, niche="pickleball"):
    led = ledger_for(root)
    for i in range(n):
        led.append({"manifest_id": "old", "op_index": i, "idempotency_key": f"old+{i}", "op": op,
                    "niche": niche, "status": "ok", "write_attempted": True, "result": {}})


CASES = {
    "sha_mismatch": (lambda r: write_manifest(r, [("etsy_activate_listing", "n", {"listing_id": 1})]),
                     lambda p: p.write_text(p.read_text().replace("listing_id: 1", "listing_id: 2")),
                     "payload_sha256 mismatch"),
    "blocklist": (lambda r: write_manifest(r, [("etsy_create_digital_listing", "n",
                                                create_payload(title="Star Wars court print"))]), None, "blocklist veto"),
    "long_title": (lambda r: write_manifest(r, [("etsy_create_digital_listing", "n", create_payload(
        title="one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen"))]),
                   None, "words"),
    "missing_disclosure": (lambda r: write_manifest(r, [("etsy_create_digital_listing", "n",
                                                         create_payload(description="No disclosure"))]),
                           None, "AI disclosure sentence"),
    "below_floor": (lambda r: write_manifest(r, [("etsy_create_digital_listing", "n", create_payload(price_usd=1.0))]),
                    None, "below floor"),
    "pod_below_floor": (lambda r: write_manifest(r, [("printify_create_product", "n", printify_payload(
        variants=[{"id": 12100, "price_usd": 18.0, "cost_key": "tee-s"}]))]), None, "below floor 0.30"),
    "stale_costs": (lambda r: write_manifest(r, [("etsy_create_digital_listing", "n", create_payload(
        cost_snapshot="data/costs/2026-09-01-stale.json"))]), None, "re-fetch"),
    "bad_ref": (lambda r: write_manifest(r, [("etsy_activate_listing", "n", {"listing_id": "$ref:ops[0].listing_id"})]),
                None, "must point to an earlier op"),
    "file_hash": (lambda r: write_manifest(r, [("etsy_upload_file", "n", {**file_payload(r, 1), "file_sha256": "0" * 64})]),
                  None, "file_sha256 mismatch"),
    "unknown_op": (lambda r: write_manifest(r, [("etsy_delete_shop", "n", {})]), None, "is not one of"),
    "id_mismatch": (lambda r: write_manifest(r, [("etsy_activate_listing", "n", {"listing_id": 1})], mid="2026-10-21-other"),
                    lambda p: p.rename(p.with_name("2026-10-21-renamed.yaml")), "does not match filename"),
    "owner_hours": (lambda r: write_manifest(r, [("etsy_activate_listing", "n", {"listing_id": 1})],
                                             owner_minutes_estimate=7 * 24 * 60), None, "owner_minutes_estimate"),
    "ads_cap": (lambda r: write_manifest(r, [("etsy_activate_listing", "n", {"listing_id": 1})],
                                         ads={"daily_budget_usd": 5}), None, "exceeds cap"),
    "offsite_ads": (lambda r: write_manifest(r, [("etsy_activate_listing", "n", {"listing_id": 1})],
                                             ads={"offsite_ads_opted_in": True}), None, "offsite"),
    "too_many_niches": (lambda r: write_manifest(r, [("etsy_activate_listing", f"n{i}", {"listing_id": i})
                                                     for i in range(5)]), None, "active niches"),
}


@pytest.mark.parametrize("case", sorted(CASES))
@responses.activate
def test_preflight_failures_write_nothing(repo, case):
    make, mutate, expected = CASES[case]
    path = make(repo)
    if mutate:
        mutate(path)
        if not path.exists():
            path = next((repo / "releases").glob("*.yaml"))
    with pytest.raises(runner.PreflightFailed) as e:
        execute(repo, path)
    assert any(expected in err for err in e.value.errors), e.value.errors
    assert len(responses.calls) == 0
    assert ledger_lines(repo) == []


@responses.activate
def test_unverified_fee_snapshot_blocks_pricing(repo):
    p = repo / "data/costs/2026-10-20-channel-fees.json"
    p.write_text(json.dumps({**json.loads(p.read_text()), "verified": False}))
    path = write_manifest(repo, [("etsy_create_digital_listing", "n", create_payload())])
    with pytest.raises(runner.PreflightFailed, match="not marked verified"):
        execute(repo, path)


@responses.activate
def test_ai_disclosure_attribute_unconfigured_blocks(repo):
    _set_config(repo, **{"etsy.ai_disclosure_property": {"property_id": None, "value_ids": [], "values": []},
                         "etsy.ai_disclosure_owner_ticks": False})
    path = write_manifest(repo, [("etsy_create_digital_listing", "n", create_payload())])
    with pytest.raises(runner.PreflightFailed, match="AI disclosure attribute"):
        execute(repo, path)


@responses.activate
def test_owner_ticks_waives_attribute_but_not_sentence(repo):
    _set_config(repo, **{"etsy.ai_disclosure_property": {"property_id": None, "value_ids": [], "values": []},
                         "etsy.ai_disclosure_owner_ticks": True})
    path = write_manifest(repo, [("etsy_create_digital_listing", "n",
                                  create_payload(description="No disclosure"))])
    with pytest.raises(runner.PreflightFailed, match="AI disclosure sentence") as exc:
        execute(repo, path)
    assert "attribute is required" not in str(exc.value)


def test_extra_disclosure_sentence_is_accepted(repo):
    from src.executor import validate
    config = yaml.safe_load((repo / "config" / "engine.yaml").read_text())
    extra = config["compliance"]["ai_disclosure_sentences_extra"][0]
    payload = create_payload(description=f"A calendar. {extra}")
    errs = validate._check_text("etsy_create_digital_listing", payload, config,
                                validate.Blocklist.load(repo / "config" / "blocklist.yaml"), "op")
    assert errs == []


@responses.activate
def test_payhip_disabled_by_default(repo):
    _set_config(repo, **{"payhip.api_base_url": None})
    path = write_manifest(repo, [("payhip_create_product", "n", {
        "name": "x", "description": "x", "price_usd": 7.99, "path": "assets/digital/court.pdf",
        "file_sha256": file_sha256(repo / "assets/digital/court.pdf"), "ai_assisted": False,
        "cost_snapshot": "data/costs/2026-10-20-products.json", "cost_key": "digital"})])
    with pytest.raises(runner.PreflightFailed, match="payhip is disabled"):
        execute(repo, path)


@responses.activate
def test_weekly_listing_ceiling(repo):
    _fill_week(repo, "etsy_create_digital_listing", 60)
    path = write_manifest(repo, [("etsy_create_digital_listing", "pickleball", create_payload())])
    with pytest.raises(runner.PreflightFailed, match="new listings this week would be 61"):
        execute(repo, path)


@responses.activate
def test_weekly_pod_ceiling(repo):
    _fill_week(repo, "printify_create_product", 10)
    path = write_manifest(repo, [("printify_create_product", "pickleball", printify_payload())])
    with pytest.raises(runner.PreflightFailed, match="POD candidates this week would be 11"):
        execute(repo, path)


@responses.activate
def test_ceiling_ignores_ops_already_done_in_replay(repo):
    """A replay of an already-executed manifest must not trip the weekly ceiling on its own ops."""
    _fill_week(repo, "etsy_create_digital_listing", 59)
    responses.post(f"{ETSY_BASE}/shops/{SHOP}/listings", json=R["etsy_create_listing"])
    responses.put(f"{ETSY_BASE}/shops/{SHOP}/listings/2001/properties/900001", json=R["etsy_property"])
    responses.get(f"{ETSY_BASE}/listings/2001", json=R["etsy_listing_draft"])
    path = write_manifest(repo, [("etsy_create_digital_listing", "pickleball", create_payload())])
    execute(repo, path)
    assert execute(repo, path)["ops"][0]["status"] == "skipped_duplicate"


def test_dry_run_validates_without_writes(repo):
    path = write_manifest(repo, [("etsy_activate_listing", "pickleball", {"listing_id": 1})])
    with responses.RequestsMock() as rsps:
        out = execute(repo, path, dry_run=True)
        assert len(rsps.calls) == 0
    assert out["ops"][0]["status"] == "validated" and ledger_lines(repo) == []


@responses.activate
def test_ledger_lines_carry_the_approval_record(repo):
    mock_digital_flow()
    responses.get(f"{ETSY_BASE}/listings/2001", json=R["etsy_listing_active"])
    path = digital_manifest(repo)
    runner.execute(path, ctx_for(repo), ledger_for(repo), today=TODAY,
                   approval={"approver": "vicwireless", "merge_sha": "abc123"})
    assert all(l["approver"] == "vicwireless" and l["merge_sha"] == "abc123" for l in ledger_lines(repo))


def test_refuses_to_write_outside_github_actions(monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    assert runner.main(["releases/whatever.yaml"]) == 2
    assert "Refusing" in capsys.readouterr().err


def test_executor_workflow_triggers_only_on_release_manifests():
    wf = yaml.safe_load((REPO / ".github/workflows/executor.yml").read_text())
    on = wf[True] if True in wf else wf["on"]  # PyYAML parses `on:` as True
    assert set(on) == {"push"}
    assert on["push"] == {"branches": ["main"], "paths": ["releases/*.yaml"]}


def test_only_allowlisted_ops_exist():
    from src.executor.ops import OPS
    schema = json.loads((REPO / "schemas/release_manifest.json").read_text())
    enum = schema["properties"]["ops"]["items"]["properties"]["op"]["enum"]
    assert set(OPS) == set(enum) == {p.stem for p in (REPO / "schemas/ops").glob("*.json")}


# ---------------------------------------------------------------- monthly spend commitment cap
def _activate(root, **kw):
    return write_manifest(root, [("etsy_activate_listing", "n", {"listing_id": 1})], **kw)


def test_spend_cap_counts_subscriptions_ads_and_listing_fees(repo):
    from src.executor.validate import committed_monthly_spend
    (repo / "data" / "spend").mkdir(parents=True)
    (repo / "data" / "spend" / "subscriptions.csv").write_text(
        "vendor,plan,monthly_usd,status,started,source,notes\n"
        "Etsy Plus,Etsy Plus,10.00,active,2026-10-21,x,\n"
        "Etsy Ads,Etsy Ads,,active 2026-11-15,,x,\n"
        "Postiz,,,active (owner-reported),,x,\n"
        "SerpApi,Starter,75,approved 2026-10-24,,x,\n")
    manifest = yaml.safe_load(write_manifest(repo, [("etsy_create_digital_listing", "n", dict(
        title=TITLE, description="d " + DISCLOSURE, tags=TAGS, taxonomy_id=1, who_made="i_did",
        when_made="2020_2026", ai_assisted=True, price_usd=6.99,
        cost_snapshot="data/costs/2026-10-20-products.json", cost_key="digital"))]).read_text())
    lines = committed_monthly_spend(manifest, repo, runner.load_config(repo), ledger_for(repo), TODAY, set(),
                                    {"etsy": {"listing_fee_usd": 0.2}})
    # Etsy Plus counted; Etsy Ads row active -> 30 x the $3 cap; one new listing; unknown/approved-only rows ignored.
    assert lines == {"subscription:Etsy Plus": 10.0, "etsy_ads": 90.0, "listing_fees_30d": 0.2}


def test_spend_cap_refuses_manifest_over_cap(repo):
    path = _activate(repo, new_monthly_commitments_usd=100.01)
    with pytest.raises(runner.PreflightFailed) as e:
        execute(repo, path)
    assert "committed monthly spend would be $100.01" in str(e.value)
    assert "Only the owner can approve" in str(e.value)
    assert not (repo / "data" / "ledger").exists()  # nothing was written


@responses.activate
def test_spend_cap_allows_manifest_at_cap(repo):
    path = _activate(repo, new_monthly_commitments_usd=100)
    assert execute(repo, path, dry_run=True)["ops"][0]["status"] == "validated"


def test_spend_cap_missing_from_config_fails_closed(repo):
    cfg = yaml.safe_load((repo / "config" / "engine.yaml").read_text())
    del cfg["monthly_spend_commitment_cap_usd"]
    (repo / "config" / "engine.yaml").write_text(yaml.safe_dump(cfg))
    with pytest.raises(runner.PreflightFailed, match="monthly_spend_commitment_cap_usd is not set"):
        execute(repo, _activate(repo))


# ---------------------------------------------------------------- etsy_update_listing (in-place replace)
NEW_TITLE = "Christmas Trivia Game Printable, 40 Questions, Holiday Party Game"
METRICS_HEAD = ("date,listing_id,title,state,listing_type,price_usd,published_date,views_total,favorites_total,"
                "orders_total,units_total,revenue_usd_total\n")


def write_metrics(root, rows, date="2026-10-20"):
    d = root / "data" / "metrics"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{date}.csv").write_text(METRICS_HEAD + "".join(rows))


def metrics_row(lid=2001, state="active", orders=0, date="2026-10-20"):
    return f"{date},{lid},Old planner,{state},download,6.99,2026-10-01,0,0,{orders},{orders},0.0\n"


def update_payload(root, **kw):
    (root / "assets/digital/b.pdf").write_bytes(b"%PDF-1.4 b")
    files = [{"path": "assets/digital/court.pdf", "name": "trivia-letter.pdf",
              "file_sha256": file_sha256(root / "assets/digital/court.pdf")},
             {"path": "assets/digital/b.pdf", "name": "trivia-a4.pdf",
              "file_sha256": file_sha256(root / "assets/digital/b.pdf")}]
    images = [{"path": "assets/digital/court.jpg", "alt_text": f"Image {i}",
               "file_sha256": file_sha256(root / "assets/digital/court.jpg")} for i in range(1, 6)]
    return {"listing_id": 2001, "title": NEW_TITLE, "description": f"Forty questions.\n\n{DISCLOSURE}", "tags": TAGS,
            "ai_assisted": True, "price_usd": 4.99, "cost_snapshot": "data/costs/2026-10-20-products.json",
            "cost_key": "digital", "files": files, "images": images, **kw}


def mock_update_flow(old_files=(3001, 3002), old_images=(4001, 4002, 4003, 4004, 4005, 4006), state="active",
                     readback_title=NEW_TITLE):
    """A tiny in-memory Etsy listing so the test checks real end state, not just call order."""
    st = {"files": {i: f"old-{i}.pdf" for i in old_files}, "images": list(old_images), "min_files": len(old_files),
          "max_files": len(old_files), "next": 9000, "title": "Old planner", "price": 699, "tags": ["old"]}

    def listing(req):
        return 200, {}, json.dumps({"listing_id": 2001, "state": state, "listing_type": "download",
                                    "title": st["title"], "tags": st["tags"], "url": "https://www.etsy.com/listing/2001/x",
                                    "price": {"amount": st["price"], "divisor": 100, "currency_code": "USD"}})

    def files_list(req):
        return 200, {}, json.dumps({"count": len(st["files"]), "results": [
            {"listing_file_id": k, "filename": v} for k, v in st["files"].items()]})

    def file_post(req):
        st["next"] += 1
        body = req.body if isinstance(req.body, bytes) else req.body.read()
        name = re.search(rb'name="name"\r\n\r\n([^\r]+)', body).group(1).decode()
        st["files"][st["next"]] = name
        st["max_files"] = max(st["max_files"], len(st["files"]))
        return 201, {}, json.dumps({"listing_file_id": st["next"], "filename": name})

    def file_delete(req):
        st["files"].pop(int(req.url.rsplit("/", 1)[1]))
        st["min_files"] = min(st["min_files"], len(st["files"]))
        return 200, {}, "{}"

    def images_list(req):
        return 200, {}, json.dumps({"count": len(st["images"]), "results": [
            {"listing_image_id": i, "rank": n + 1} for n, i in enumerate(st["images"])]})

    def image_post(req):
        st["next"] += 1
        body = req.body if isinstance(req.body, bytes) else req.body.read()
        rank = int(re.search(rb'name="rank"\r\n\r\n(\d+)', body).group(1))
        assert b'name="overwrite"\r\n\r\ntrue' in body
        if rank <= len(st["images"]):
            st["images"][rank - 1] = st["next"]
        else:
            st["images"].append(st["next"])
        return 201, {}, json.dumps({"listing_image_id": st["next"], "rank": rank})

    def image_delete(req):
        st["images"].remove(int(req.url.rsplit("/", 1)[1]))
        return 200, {}, "{}"

    def patch(req):
        from urllib.parse import parse_qs
        form = parse_qs(req.body)
        st["title"] = readback_title.replace("&", "&amp;") if readback_title != NEW_TITLE else form["title"][0]
        st["tags"] = form["tags"][0].split(",")
        return 200, {}, "{}"

    def inv_put(req):
        st["price"] = int(round(json.loads(req.body)["products"][0]["offerings"][0]["price"] * 100))
        return 200, {}, "{}"

    base, shop = f"{ETSY_BASE}/listings/2001", f"{ETSY_BASE}/shops/{SHOP}/listings/2001"
    responses.add_callback(responses.GET, base, callback=listing)
    responses.add_callback(responses.GET, f"{shop}/files", callback=files_list)
    responses.add_callback(responses.POST, f"{shop}/files", callback=file_post)
    responses.add_callback(responses.DELETE, re.compile(re.escape(shop) + r"/files/\d+"), callback=file_delete)
    responses.add_callback(responses.GET, f"{base}/images", callback=images_list)
    responses.add_callback(responses.POST, f"{shop}/images", callback=image_post)
    responses.add_callback(responses.DELETE, re.compile(re.escape(shop) + r"/images/\d+"), callback=image_delete)
    responses.add_callback(responses.PATCH, shop, callback=patch)
    responses.get(f"{base}/inventory", json=R["etsy_inventory_before"])
    responses.add_callback(responses.PUT, f"{base}/inventory", callback=inv_put)
    return st


@responses.activate
def test_update_listing_replaces_everything_in_place_and_stays_active(repo):
    write_metrics(repo, [metrics_row()])
    st = mock_update_flow()
    out = execute(repo, write_manifest(repo, [("etsy_update_listing", "party-games", update_payload(repo))]))
    entry = out["ops"][0]
    assert entry["status"] == "ok"
    assert entry["readback"] == {"title": NEW_TITLE, "price_usd": 4.99, "state": "active", "state_before": "active",
                                 "listing_type": "download", "tags": 13, "image_count": 5,
                                 "files": ["trivia-a4.pdf", "trivia-letter.pdf"],
                                 "url": "https://www.etsy.com/listing/2001/x"}
    assert sorted(st["files"].values()) == ["trivia-a4.pdf", "trivia-letter.pdf"]   # old files gone
    assert len(st["images"]) == 5 and min(st["images"]) > 9000                      # old images gone
    assert st["min_files"] >= 1            # never zero files: Etsy would convert the listing to physical
    assert entry["result"]["listing_id"] == 2001 and len(entry["result"]["listing_image_ids"]) == 5
    # No state change was ever sent, and the listing was not re-created.
    assert not any(c.request.method == "POST" and c.request.url.endswith("/listings") for c in responses.calls)
    assert all("state" not in (c.request.body or "") for c in responses.calls if c.request.method == "PATCH")


@responses.activate
def test_update_listing_never_exceeds_five_files_or_drops_to_zero(repo):
    write_metrics(repo, [metrics_row()])
    st = mock_update_flow(old_files=(3001, 3002, 3003, 3004, 3005))
    out = execute(repo, write_manifest(repo, [("etsy_update_listing", "party-games", update_payload(repo))]))
    assert out["ops"][0]["status"] == "ok"
    assert st["max_files"] <= 5 and st["min_files"] >= 1
    assert sorted(st["files"].values()) == ["trivia-a4.pdf", "trivia-letter.pdf"]


@responses.activate
def test_update_listing_refuses_inactive_listing_before_any_write(repo):
    write_metrics(repo, [metrics_row()])
    mock_update_flow(state="inactive")
    with pytest.raises(runner.ExecutorError, match="expected 'active'"):
        execute(repo, write_manifest(repo, [("etsy_update_listing", "party-games", update_payload(repo))]))
    assert writes() == []
    last = ledger_for(repo).entries()[-1]
    assert last["status"] == "failed" and last["write_attempted"] is False


@responses.activate
def test_update_listing_readback_mismatch_is_not_ok(repo):
    write_metrics(repo, [metrics_row()])
    mock_update_flow(readback_title="Something else")
    with pytest.raises(runner.UnknownState, match="read-back"):
        execute(repo, write_manifest(repo, [("etsy_update_listing", "party-games", update_payload(repo))]))
    assert ledger_for(repo).entries()[-1]["status"] == "readback_failed"


@pytest.mark.parametrize("rows,date,kw,match", [
    ([], None, {}, "no metrics snapshot"),
    ([metrics_row(orders=1)], "2026-10-20", {}, "has orders"),
    ([metrics_row(lid=5)], "2026-10-20", {}, "is not in 2026-10-20.csv"),
    ([metrics_row(state="inactive")], "2026-10-20", {}, "was 'inactive'"),
    ([metrics_row()], "2026-10-10", {}, "days old"),
    ([metrics_row()], "2026-10-20", {"description": "No disclosure here."}, "AI disclosure sentence"),
    ([metrics_row()], "2026-10-20", {"title": "Grinch Trivia Game Printable"}, "blocklist veto"),
    ([metrics_row()], "2026-10-20", {"price_usd": 0.3}, "below floor"),
    ([metrics_row()], "2026-10-20", {"images": "one"}, "images"),
])
@responses.activate
def test_update_listing_preflight_rails(repo, rows, date, kw, match):
    if date:
        write_metrics(repo, rows, date)
    payload = update_payload(repo, **{k: v for k, v in kw.items() if k != "images"})
    if "images" in kw:
        payload["images"] = payload["images"][:1]
    with pytest.raises(runner.PreflightFailed, match=match):
        execute(repo, write_manifest(repo, [("etsy_update_listing", "party-games", payload)]))
    assert len(responses.calls) == 0


@responses.activate
def test_update_listing_file_hash_and_double_replace_are_refused(repo):
    write_metrics(repo, [metrics_row()])
    bad = update_payload(repo)
    bad["images"][2]["file_sha256"] = "0" * 64
    with pytest.raises(runner.PreflightFailed, match="file_sha256 mismatch"):
        execute(repo, write_manifest(repo, [("etsy_update_listing", "party-games", bad)]))
    twice = [("etsy_update_listing", "party-games", update_payload(repo))] * 2
    with pytest.raises(runner.PreflightFailed, match="replaced twice"):
        execute(repo, write_manifest(repo, twice))
