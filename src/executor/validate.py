"""Preflight checks for a release manifest. Runs before any write; any error means zero writes."""
from __future__ import annotations

import datetime as dt
import json
import re
from functools import lru_cache
from pathlib import Path

import jsonschema

from src.compliance.blocklist import Blocklist
from src.scoring.score import margin

from . import costs
from .hashing import file_sha256, payload_sha256
from .ledger import Ledger, idempotency_key
from .ops import NEW_LISTING_OPS, OPS, POD_CANDIDATE_OPS

SCHEMAS = Path(__file__).resolve().parents[2] / "schemas"
REF_RE = re.compile(r"^\$ref:ops\[(\d+)\]\.([a-z_]+)$")
LISTING_TEXT_OPS = {"etsy_create_digital_listing", "printify_create_product", "payhip_create_product"}
MAX_TITLE_WORDS = 15


@lru_cache(maxsize=None)
def _schema(rel: str) -> dict:
    return json.loads((SCHEMAS / rel).read_text(encoding="utf-8"))


def _schema_errors(instance, rel: str, where: str) -> list[str]:
    v = jsonschema.Draft202012Validator(_schema(rel))
    return [f"{where}: {'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}" for e in v.iter_errors(instance)]


def iso_week(d: dt.date) -> tuple[int, int]:
    y, w, _ = d.isocalendar()
    return y, w


def preflight(manifest: dict, manifest_path: Path, root: Path, config: dict, ledger: Ledger,
              today: dt.date, blocklist: Blocklist | None = None) -> list[str]:
    errors = _schema_errors(manifest, "release_manifest.json", "manifest")
    if errors:
        return errors

    mid = manifest["manifest_id"]
    if manifest_path.stem != mid:
        errors.append(f"manifest_id {mid!r} does not match filename {manifest_path.name!r}")

    blocklist = blocklist or Blocklist.load(root / "config" / "blocklist.yaml")
    max_age = config.get("cost_snapshot_max_age_days", 14)
    floors = config["price_floor_margin"]
    done = {k for k, e in ledger.latest().items() if e["status"] == "ok"}

    fees = None
    try:
        fees = costs.latest_channel_fees(root, today, max_age)
    except costs.CostError as e:
        if any(op["op"] in _PRICED_OPS for op in manifest["ops"]):
            errors.append(f"channel fees: {e}")

    for i, op in enumerate(manifest["ops"]):
        name, p, where = op["op"], op["payload"], f"ops[{i}] {op['op']}"
        errors += _schema_errors(p, f"ops/{name}.json", where)
        if payload_sha256(p) != op["payload_sha256"]:
            errors.append(f"{where}: payload_sha256 mismatch")
        errors += _check_refs(p, i, where)
        errors += _check_files(p, root, where)
        if name in LISTING_TEXT_OPS or name == "pinterest_create_pin":
            errors += _check_text(name, p, config, blocklist, where)
        if name == "payhip_create_product" and not (config.get("payhip") or {}).get("api_base_url"):
            errors.append(f"{where}: payhip is disabled until payhip.api_base_url is configured")
        if fees and name in _PRICED_OPS:
            errors += _check_price(name, p, root, today, max_age, floors, fees, where)
        if name == "etsy_update_price":
            errors += _check_price_cooldown(p, config, ledger, today, where)
        if name == "printify_publish" and p.get("partner_checked") is not True:
            errors.append(f"{where}: POD publish requires partner_checked: true (owner attaches the production "
                          "partner in Etsy and ticks the PR checklist)")

    errors += _check_ceilings(manifest, config, ledger, today, done)
    return errors


_NON_ACTIVATING_OPS = {"etsy_deactivate_listing"}
_PRICED_OPS = {"etsy_create_digital_listing", "etsy_update_price", "printify_create_product", "payhip_create_product"}


def _check_refs(p: dict, i: int, where: str) -> list[str]:
    errs = []
    for k, v in p.items():
        if isinstance(v, str) and v.startswith("$ref:"):
            m = REF_RE.match(v)
            if not m or int(m.group(1)) >= i:
                errs.append(f"{where}: {k} reference {v!r} must point to an earlier op")
    return errs


def _check_files(p: dict, root: Path, where: str) -> list[str]:
    if "path" not in p or "file_sha256" not in p:
        return []
    path = (root / p["path"]).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        return [f"{where}: file {p['path']} not found in repo"]
    if file_sha256(path) != p["file_sha256"]:
        return [f"{where}: file_sha256 mismatch for {p['path']}"]
    return []


def _check_text(name: str, p: dict, config: dict, blocklist: Blocklist, where: str) -> list[str]:
    errs = []
    title = p.get("title") or p.get("name") or ""
    hits = blocklist.check(title, p.get("description"), p.get("tags"), p.get("alt_text"))
    errs += [f"{where}: blocklist veto [{h.category}/{h.rule}] matched {h.match!r}" for h in hits]
    if name in LISTING_TEXT_OPS:
        if len(title.split()) > MAX_TITLE_WORDS:
            errs.append(f"{where}: title has {len(title.split())} words (max {MAX_TITLE_WORDS})")
        if p.get("ai_assisted"):
            comp = config["compliance"]
            sentences = [comp["ai_disclosure_sentence"], *comp.get("ai_disclosure_sentences_extra", [])]
            desc = " ".join(p["description"].split())
            if not any(" ".join(s.split()) in desc for s in sentences):
                errs.append(f"{where}: ai_assisted listing is missing the AI disclosure sentence")
            etsy = config.get("etsy") or {}
            if (name == "etsy_create_digital_listing" and etsy.get("require_ai_disclosure_attribute", True)
                    and not (etsy.get("ai_disclosure_property") or {}).get("property_id")
                    and not etsy.get("ai_disclosure_owner_ticks")):
                errs.append(f"{where}: AI disclosure attribute is required but etsy.ai_disclosure_property "
                            "is not configured")
        if name == "printify_create_product":
            partner = " ".join(config["compliance"]["pod_partner_sentence"].split())
            if partner not in " ".join(p["description"].split()):
                errs.append(f"{where}: POD listing is missing the production-partner sentence")
    return errs


def _check_price_cooldown(p: dict, config: dict, ledger: Ledger, today: dt.date, where: str) -> list[str]:
    days = config.get("price_change_cooldown_days", 28)
    since = today - dt.timedelta(days=days)
    for e in ledger.entries():
        if (e.get("op") == "etsy_update_price" and e.get("status") == "ok"
                and str((e.get("result") or {}).get("listing_id")) == str(p["listing_id"])
                and dt.date.fromisoformat(e["ts"][:10]) > since):
            return [f"{where}: listing {p['listing_id']} was repriced on {e['ts'][:10]}; "
                    f"cool-down is {days} days"]
    return []


def _check_price(name, p, root, today, max_age, floors, fees, where) -> list[str]:
    try:
        snap = costs.load_snapshot(root, p["cost_snapshot"], today, max_age)
        if name == "printify_create_product":
            checks = [(v["price_usd"], costs.item_cost(snap, v["cost_key"]), floors["pod"], fees["etsy"], f"variant {v['id']}")
                      for v in p["variants"]]
        elif name == "payhip_create_product":
            checks = [(p["price_usd"], costs.item_cost(snap, p["cost_key"]), floors["digital"], fees["payhip"], "")]
        else:
            kind = p.get("offer_type", "digital")
            checks = [(p["price_usd"], costs.item_cost(snap, p["cost_key"]), floors[kind], fees["etsy"], "")]
    except (costs.CostError, KeyError, ValueError) as e:
        return [f"{where}: {e}"]
    errs = []
    for price, cost, floor, channel_fees, label in checks:
        if channel_fees.get("verified") is False:
            errs.append(f"{where}: channel fees for this channel are not verified in the fee snapshot")
            continue
        m = margin(price, cost, channel_fees)
        if m < floor:
            errs.append(f"{where}: {label + ' ' if label else ''}margin {m:.2f} at ${price:.2f} is below floor {floor:.2f}")
    return errs


def _check_ceilings(manifest: dict, config: dict, ledger: Ledger, today: dt.date, done: set[str]) -> list[str]:
    errs = []
    mid = manifest["manifest_id"]
    pending = [(i, op) for i, op in enumerate(manifest["ops"]) if idempotency_key(mid, i) not in done]

    cap_min = config["owner_hours_cap_per_week"] * 60
    if manifest["owner_minutes_estimate"] > cap_min:
        errs.append(f"owner_minutes_estimate {manifest['owner_minutes_estimate']} exceeds {cap_min:.0f}")

    ads = manifest.get("ads") or {}
    if ads.get("daily_budget_usd", 0) > config["etsy_ads_daily_cap_usd"]:
        errs.append(f"ads daily budget {ads['daily_budget_usd']} exceeds cap {config['etsy_ads_daily_cap_usd']}")
    if ads.get("offsite_ads_opted_in", False) and not config["offsite_ads_opted_in"]:
        errs.append("manifest declares offsite ads opt-in but config has offsite_ads_opted_in: false")

    week = iso_week(today)
    window_start = today - dt.timedelta(days=config.get("niche_active_window_days", 28))
    week_new = week_pod = 0
    active_niches = set()
    for e in ledger.entries():
        if e.get("status") != "ok":
            continue
        d = dt.date.fromisoformat(e["ts"][:10])
        if iso_week(d) == week:
            week_new += e["op"] in NEW_LISTING_OPS
            week_pod += e["op"] in POD_CANDIDATE_OPS
        if d >= window_start and e.get("niche") and e["op"] not in _NON_ACTIVATING_OPS:
            active_niches.add(e["niche"])

    new = sum(op["op"] in NEW_LISTING_OPS for _, op in pending)
    pod = sum(op["op"] in POD_CANDIDATE_OPS for _, op in pending)
    if week_new + new > config["max_new_listings_per_week"]:
        errs.append(f"new listings this week would be {week_new + new} (max {config['max_new_listings_per_week']})")
    if week_pod + pod > config["max_pod_candidates_per_week"]:
        errs.append(f"POD candidates this week would be {week_pod + pod} (max {config['max_pod_candidates_per_week']})")
    niches = active_niches | {op["niche"] for _, op in pending if op["op"] not in _NON_ACTIVATING_OPS}
    if len(niches) > config["niches_active_max"]:
        errs.append(f"active niches would be {len(niches)}: {sorted(niches)} (max {config['niches_active_max']})")
    return errs
