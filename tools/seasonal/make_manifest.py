"""Write a release manifest that replaces planner listings in place with the seasonal products.

    python -m tools.seasonal.make_manifest --id 2026-11-15-seasonal-verify --keys christmas-trivia
    python -m tools.seasonal.make_manifest --id 2026-11-15-seasonal-games --skip christmas-trivia
"""
from __future__ import annotations

import argparse
import datetime as dt

import yaml

from src.executor.hashing import file_sha256, payload_sha256

from .build import ROOT
from .catalog import CATALOG, NICHE, description
from .listing import COLOR, IMAGES

ASSETS = "assets/digital/2026-11-15-seasonal"
COST_SNAPSHOT = "data/costs/2026-11-24-products.json"


def payload(key: str) -> dict:
    c = CATALOG[key]
    files = [{"path": f"{ASSETS}/{key}/{key}-{s}.pdf", "name": f"{key}-{s}.pdf"} for s in ("us-letter", "a4")]
    images = [{"path": f"{ASSETS}/{key}/images/{key}-{name}.jpg",
               "alt_text": alt.format(hero=c["hero"], color=COLOR[c["palette"]])[:250]} for name, _, alt in IMAGES]
    for item in files + images:
        item["file_sha256"] = file_sha256(ROOT / item["path"])
    return {"listing_id": c["listing_id"], "expect_state": "active", "title": c["title"], "description": description(key),
            "tags": c["tags"], "ai_assisted": True, "offer_type": "digital", "price_usd": c["price"],
            "cost_snapshot": COST_SNAPSHOT, "cost_key": "digital", "files": files, "images": images}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--keys", nargs="*")
    ap.add_argument("--skip", nargs="*", default=[])
    ap.add_argument("--summary", default="")
    args = ap.parse_args(argv)
    keys = args.keys or [k for k in CATALOG if k not in args.skip]
    ops = []
    for k in keys:
        p = payload(k)
        ops.append({"op": "etsy_update_listing", "niche": NICHE, "payload": p, "payload_sha256": payload_sha256(p)})
    manifest = {
        "manifest_id": args.id,
        "created_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": "claude",
        "summary": args.summary or f"Seasonal release: replace {len(keys)} zero-traction planner listings in place with holiday printables ({', '.join(keys)}).",
        "owner_minutes_estimate": 0,
        "ops": ops,
    }
    path = ROOT / "releases" / f"{args.id}.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    print(path.relative_to(ROOT), len(ops), "ops")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
