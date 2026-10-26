"""Kidcore test release: concept records with the IP screen, then the release manifest.

    PYTHONPATH=. python tools/make_kidcore_release.py

Writes data/scores/2026-10-26/kidcore-concepts.json every run. Writes releases/2026-10-26-kidcore.yaml
only when every concept's IP screen passes (docs/ip-screen.md); otherwise it lists what is missing
and exits non-zero. Trademark results come from data/ip/2026-10-26-kidcore-trademark.yaml, filled
from a USPTO search (the cloud environment cannot reach USPTO today).
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import yaml

from src.compliance.blocklist import Blocklist
from src.compliance.ip_review import CheckResult, Subject, review
from src.executor.hashing import file_sha256, payload_sha256
from tools.make_kidcore_designs import DESIGNS, RATIOS
from tools.make_release_manifest import COMMON, SNAPSHOT

ROOT = Path(__file__).resolve().parents[1]
ASSETS = "assets/digital/2026-10-26-kidcore"
MANIFEST_ID = "2026-10-26-kidcore"
NICHE = "kidcore-wall-art"
TAXONOMY_DIGITAL_PRINTS = 2078  # Art & Collectibles > Prints > Digital Prints (seller-taxonomy/nodes, 2026-10-26)
TRADEMARK_FILE = ROOT / "data" / "ip" / "2026-10-26-kidcore-trademark.yaml"
SCAN_SCORE = 51.5  # data/scores/2026-10-26/erank-shortlist-scan.json, kidcore_wall_art
SIGNALS = ["sig-20261026-erank-trend-rank-088-kidcore", "sig-20261026-erank-search-volume-088-kidcore",
           "sig-20261026-erank-competing-listin-088-kidcore"]
CHECKED = "2026-10-26T13:40:00+00:00"

ETSY_EVIDENCE = {  # findAllListingsActive, 2026-10-26 (Etsy data)
    "recess-forever": '"recess forever": 109 results, generic teacher-retirement shirts and mugs from many shops; none licensed',
    "you-did-it": '"you did it" is a stock encouragement phrase; results are generic graduation and congrats items',
    "make-something-messy": '"make something messy": 0 results',
    "happy-shapes": "no design text; toy-block shapes are generic",
    "rainbow-daisy-check": "no design text; rainbow, daisy and checkerboard are generic motifs",
    "kidcore-set-of-5": "set of the five designs above",
}
ORIGIN_EVIDENCE = {
    "recess-forever": "web search 2026-10-26: no single source; used by many sellers as a teacher-retirement line. "
                      "Not the 1997 Disney series title",
    "you-did-it": "common phrase, no single source. Replaced 'Gold Star Day', which is also the name of "
                  "Gold Star Mother's and Family's Day (families of fallen service members)",
    "make-something-messy": "web search 2026-10-26: no brand or campaign uses the phrase",
    "happy-shapes": "original code-drawn composition, no text",
    "rainbow-daisy-check": "original code-drawn composition, no text",
    "kidcore-set-of-5": "set of the five designs above",
}

G = ["kidcore wall art", "printable wall art", "colorful wall art", "dopamine decor"]
LISTINGS = {
    "recess-forever": dict(
        price=4.99, phrase="Recess Forever",
        title="Recess Forever Kidcore Wall Art Printable, Retro Playroom Poster, Teacher Gift Digital Download",
        tags=[*G, "kidcore poster", "playroom decor", "retro kids art", "recess forever", "teacher gift",
              "classroom decor", "bubble letter art", "kids room print", "teacher retirement"],
        intro="Chunky bubble letters, a red and blue checkerboard and a sky full of stars. A bright, nostalgic print "
              "for a playroom, a classroom or a teacher who is finally retiring.",
        alt="Kidcore print with puffy red Recess Forever lettering on yellow with checkerboard bands"),
    "you-did-it": dict(
        price=4.99, phrase="You Did It!",
        title="You Did It Gold Star Print, Kidcore Wall Art Printable, Encouraging Playroom Poster Download",
        tags=[*G, "gold star print", "encouragement art", "playroom decor", "kids room print", "kidcore poster",
              "classroom decor", "star wall art", "positive kids art", "graduation gift"],
        intro="A big hand-drawn gold star on a sunburst with a cheerful You Did It! An encouraging print for a kid's "
              "room, a classroom or a friend's big win.",
        alt="Kidcore print with a large gold star on a blue sunburst and puffy You Did It lettering"),
    "make-something-messy": dict(
        price=4.99, phrase="Make Something Messy",
        title="Make Something Messy Print, Kidcore Art Studio Poster, Craft Room Wall Art Printable",
        tags=[*G, "craft room decor", "art studio print", "kidcore poster", "playroom decor", "art teacher gift",
              "classroom decor", "kids art room", "paint splatter art", "creative wall art"],
        intro="Paint splats, squiggles and puffy purple letters. A playful print for a craft room, an art class or "
              "anyone who needs permission to make a mess.",
        alt="Kidcore print with puffy purple Make Something Messy lettering and colorful paint splats"),
    "happy-shapes": dict(
        price=4.99, phrase="",
        title="Happy Shapes Kidcore Wall Art Printable, Primary Color Toy Blocks Poster, Playroom Print",
        tags=[*G, "primary colors art", "toy blocks print", "playroom decor", "kids room print", "kidcore poster",
              "geometric kids art", "nursery wall art", "shapes poster", "pink nursery art"],
        intro="A wobbly tower of toy-block shapes in primary colors on a pink polka-dot ground. A simple, happy print "
              "for a nursery or playroom.",
        alt="Kidcore print of stacked toy-block shapes in red, yellow, blue, green and orange on pink"),
    "rainbow-daisy-check": dict(
        price=4.99, phrase="",
        title="Rainbow Daisy Checkerboard Print, Kidcore Wall Art Printable, Retro Green Checkered Poster",
        tags=[*G, "checkerboard print", "rainbow wall art", "daisy print", "retro wall art", "kidcore poster",
              "playroom decor", "groovy wall art", "y2k room decor", "kids room print"],
        intro="A six-color rainbow over a wavy green checkerboard, scattered with white daisies. A retro, sunny print "
              "for a bedroom, dorm or playroom.",
        alt="Kidcore print of a rainbow over a wavy green and cream checkerboard with white daisies"),
    "kidcore-set-of-5": dict(
        price=13.99, phrase="Recess Forever / You Did It! / Make Something Messy",
        title="Kidcore Wall Art Set of 5 Printable, Colorful Playroom Gallery Wall, Retro Kids Posters",
        tags=[*G, "wall art set of 5", "gallery wall set", "kidcore decor", "playroom decor", "kids room print",
              "classroom decor", "retro kids art", "kidcore poster", "bubble letter art"],
        intro="All five kidcore prints in one download for a ready-made gallery wall: Recess Forever, You Did It!, "
              "Make Something Messy, Happy Shapes and Rainbow Daisy Checkerboard.",
        alt="Five framed kidcore prints arranged as a gallery wall"),
}


def trademark_results() -> dict:
    if not TRADEMARK_FILE.exists():
        return {}
    data = yaml.safe_load(TRADEMARK_FILE.read_text(encoding="utf-8")) or {}
    return data.get("results") or {}


def concepts(bl: Blocklist, tm: dict) -> list[dict]:
    out = []
    for key, p in LISTINGS.items():
        t = tm.get(key)
        trademark = (CheckResult(t["result"], t["evidence"], t["checked_at"], tuple(t.get("classes", [])))
                     if t else CheckResult("unknown", "USPTO search not run yet (tmsearch.uspto.gov blocked from the "
                                           "cloud environment)", CHECKED, ()))
        checks = {
            "origin": CheckResult("pass", ORIGIN_EVIDENCE[key], CHECKED),
            "trademark": trademark,
            "etsy_marketplace": CheckResult("pass", ETSY_EVIDENCE[key], CHECKED),
            "text_copyright": CheckResult("pass", "short original phrase or no text; no lyrics or quotes", CHECKED),
            "image_provenance": CheckResult("pass", f"code-drawn by tools/make_kidcore_designs.py; no images from "
                                            f"third parties, no characters or faces", CHECKED),
        }
        subj = Subject(phrase=p["phrase"] or p["title"], product_format="printable_wall_art", title=p["title"],
                       tags=p["tags"], design_text=[p["phrase"]] if p["phrase"] else [])
        ip = review(subj, checks, blocklist=bl, now=dt.datetime.fromisoformat(CHECKED))
        out.append({
            "concept_id": f"con-20261026-{key}", "niche": NICHE, "working_title": p["title"].split(",")[0],
            "offer_type": "digital", "product_format": "printable_wall_art",
            "target_buyer": "adults decorating a playroom, classroom, dorm or nostalgic kidcore room",
            "gift_occasion": "teacher gift" if key == "recess-forever" else None,
            "differentiation": "Original code-drawn kidcore art with puffed bubble lettering and crayon grain; five "
                               "ratios per design; no characters or lookalikes",
            "signal_ids": SIGNALS, "score": SCAN_SCORE, "score_version": "scoring-v0.2", "ip_review": ip,
            "status": "proposed" if ip["status"] == "pass" else "vetoed", "ai_assisted": True,
            "created_at": CHECKED})
    return out


def description(key, p):
    if key == "kidcore-set-of-5":
        get = [f"5 zip files, one per size ratio, each with all five prints ({', '.join(r[1] for r in RATIOS)})"]
    else:
        get = [f"{label}: {note}" for _, label, _, _, note in RATIOS]
    lines = [p["intro"], "", "WHAT YOU GET"] + [f"• {g}" for g in get]
    lines += ["• 300 ppi JPG files, sRGB", "", "Print at home, at a local print shop or with an online printer. "
              "Frame not included.", "", COMMON]
    return "\n".join(lines)


def op(name, payload):
    return {"op": name, "niche": NICHE, "payload": payload, "payload_sha256": payload_sha256(payload)}


def manifest() -> dict:
    ops = []
    for key, p in LISTINGS.items():
        assert len(p["tags"]) == 13 and len(set(p["tags"])) == 13 and all(len(t) <= 20 for t in p["tags"]), key
        assert len(p["title"].split()) <= 15, (key, len(p["title"].split()))
        base = f"{ASSETS}/{key}"
        idx = len(ops)
        ops.append(op("etsy_create_digital_listing", {
            "title": p["title"], "description": description(key, p), "tags": p["tags"],
            "taxonomy_id": TAXONOMY_DIGITAL_PRINTS, "who_made": "i_did", "when_made": "2020_2026", "ai_assisted": True,
            "price_usd": p["price"], "cost_snapshot": SNAPSHOT, "cost_key": "digital"}))
        ref = f"$ref:ops[{idx}].listing_id"
        ext = "zip" if key == "kidcore-set-of-5" else "jpg"
        for rk, *_ in RATIOS:
            name = f"{key}-{rk}.{ext}"
            ops.append(op("etsy_upload_file", {"listing_id": ref, "path": f"{base}/{name}",
                                               "file_sha256": file_sha256(ROOT / base / name), "name": name}))
        imgs = sorted((ROOT / base / "images").glob("*.jpg"))
        for rank, path in enumerate(imgs, start=1):
            rel = str(path.relative_to(ROOT))
            ops.append(op("etsy_upload_image", {"listing_id": ref, "path": rel, "file_sha256": file_sha256(path),
                                                "rank": rank, "alt_text": p["alt"] if rank == 1 else
                                                f"{p['title'].split(',')[0]}: {path.stem.split('-', 2)[-1].split('-', 1)[-1]} image"}))
    return {"manifest_id": MANIFEST_ID, "created_at": "2026-10-26T14:00:00Z", "created_by": "claude",
            "summary": "Release 3: kidcore wall art test (scan 2026-10-26, score 51.5, band test). 5 printable singles "
                       "at $4.99 and a set of 5 at $13.99, drafts only; owner ticks the AI field and publishes each.",
            "owner_minutes_estimate": 40, "ops": ops}


def main() -> int:
    bl = Blocklist.load()
    cs = concepts(bl, trademark_results())
    out = ROOT / "data" / "scores" / "2026-10-26" / "kidcore-concepts.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cs, indent=1) + "\n", encoding="utf-8")
    vetoed = {c["concept_id"]: c["ip_review"]["reasons"] for c in cs if c["ip_review"]["status"] != "pass"}
    if vetoed:
        print("IP screen not passed; manifest not written:")
        for cid, reasons in vetoed.items():
            print(f"  {cid}: {'; '.join(reasons)}")
        return 1
    m = manifest()
    path = ROOT / "releases" / f"{MANIFEST_ID}.yaml"
    path.write_text(yaml.safe_dump(m, sort_keys=False, width=120, allow_unicode=True), encoding="utf-8")
    print(path, len(m["ops"]), "ops")
    return 0


if __name__ == "__main__":
    sys.exit(main())
