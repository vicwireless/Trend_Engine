"""Release 4 (2026-11-04): concept records with the IP screen, then the release manifest.

    PYTHONPATH=. python tools/make_release4.py

Owner approved the scope on 2026-11-04 ("Release 4 at 15 to 20 listings = YES"). Evidence: the 2026-11-04
SerpApi + Etsy scan (data/signals/2026-11-04/). Writes data/scores/2026-11-04/release4-concepts.json every
run. Writes releases/2026-11-04-release-4.yaml only when every concept's IP screen passes
(docs/ip-screen.md); otherwise lists what is missing and exits non-zero. Trademark results come from
data/ip/2026-11-04-release-4-trademark.yaml (USPTO is not reachable from the cloud environment).
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
from tools.make_kidcore_designs import RATIOS
from tools.make_release_manifest import COMMON

ROOT = Path(__file__).resolve().parents[1]
ASSETS = "assets/digital/2026-11-04-release-4"
MANIFEST_ID = "2026-11-04-release-4"
SNAPSHOT = "data/costs/2026-11-04-products.json"
TRADEMARK_FILE = ROOT / "data" / "ip" / "2026-11-04-release-4-trademark.yaml"
CHECKED = "2026-11-04T02:00:00+00:00"
SCAN = "data/signals/2026-11-04/release4-scan.json"
IPSCAN = "data/signals/2026-11-04/release4-etsy-ip-check.json"

TAX_DIGITAL_PRINTS = 2078   # Art & Collectibles > Prints > Digital Prints
TAX_COLORING = 339          # Books, Movies & Music > Books > Coloring Books
TAX_PARTY_GAMES = 1350      # Paper & Party Supplies > Party Supplies > Party Favors & Games > Party Games
# (seller-taxonomy/nodes, read 2026-11-04)

K = ["kidcore wall art", "printable wall art", "colorful wall art"]
X = ["kidcore christmas", "christmas wall art", "retro christmas"]

LISTINGS = {
    # ---------------------------------------------------------------- kidcore vol. 2 (text-free)
    "checker-hearts": dict(
        niche="kidcore-wall-art", kind="wall", price=6.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Checker Hearts Kidcore Wall Art Printable, Pink Checkerboard Heart Poster, Playroom Print",
        tags=[*K, "heart wall art", "pink checkerboard", "playroom decor", "kids room print", "dopamine decor",
              "girls room decor", "retro kids art", "valentine wall art", "nursery wall art", "kidcore poster"],
        intro="A big puffy red heart on a wavy pink checkerboard, with little hearts all around. A sweet, bright print "
              "for a kid's room, a nursery or a playful grown-up space.",
        alt="Kidcore print of a large red heart on a wavy pink checkerboard with small colorful hearts"),
    "retro-rocket": dict(
        niche="kidcore-wall-art", kind="wall", price=6.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Retro Rocket Kidcore Wall Art Printable, Space Playroom Poster, Kids Room Rocket Print",
        tags=[*K, "rocket print", "space wall art", "outer space decor", "playroom decor", "kids room print",
              "boys room decor", "planet wall art", "retro kids art", "nursery wall art", "kidcore poster"],
        intro="A chunky red and cream rocket blasting past planets and stars on a deep purple sky. A bold space print "
              "for a playroom, a nursery or a little astronaut's room.",
        alt="Kidcore print of a red and cream rocket with an orange flame among planets on a purple starry sky"),
    "flower-burst": dict(
        niche="kidcore-wall-art", kind="wall", price=6.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Flower Burst Kidcore Wall Art Printable, Retro Flower Poster, Colorful Playroom Print",
        tags=[*K, "retro flower print", "flower wall art", "groovy wall art", "playroom decor", "kids room print",
              "dopamine decor", "y2k room decor", "nursery wall art", "70s flower art", "kidcore poster"],
        intro="Nine chunky six-petal flowers in every color of the crayon box on a warm cream ground. A cheerful, "
              "retro print for a bedroom, dorm, nursery or playroom.",
        alt="Kidcore print of colorful six-petal retro flowers scattered on a cream background"),
    "rainbow-stack": dict(
        niche="kidcore-wall-art", kind="wall", price=6.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Rainbow Stack Kidcore Wall Art Printable, Eight Rainbows Poster, Bright Playroom Print",
        tags=[*K, "rainbow wall art", "rainbow print", "playroom decor", "kids room print", "dopamine decor",
              "nursery wall art", "retro kids art", "classroom decor", "cloud wall art", "kidcore poster"],
        intro="Eight little rainbows, each with two puffy clouds, lined up on a sky-blue ground. A happy pattern print "
              "for a playroom, classroom or nursery.",
        alt="Kidcore print of eight small rainbows with white clouds in a grid on light blue"),
    "sunny-day": dict(
        niche="kidcore-wall-art", kind="wall", price=6.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Sunny Day Kidcore Wall Art Printable, Retro Sun and Clouds Poster, Playroom Print",
        tags=[*K, "sun wall art", "sunshine print", "playroom decor", "kids room print", "dopamine decor",
              "nursery wall art", "retro kids art", "cloud wall art", "sunshine decor", "kidcore poster"],
        intro="A big yellow sun with wiggly red and orange rays over three puffy clouds. A warm, sunny print for a "
              "nursery, playroom or any room that needs a lift.",
        alt="Kidcore print of a yellow sun with wavy red and orange rays above white clouds on pale yellow"),
    "kidcore-vol-2-set-of-5": dict(
        niche="kidcore-wall-art", kind="set", price=14.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Kidcore Wall Art Set of 5 Printable, Hearts Rocket Flowers Rainbows Sun, Playroom Gallery",
        tags=[*K, "wall art set of 5", "gallery wall set", "kidcore decor", "playroom decor", "kids room print",
              "nursery wall art", "retro kids art", "dopamine decor", "rainbow wall art", "kidcore poster"],
        intro="Five kidcore prints in one download for a ready-made gallery wall: Checker Hearts, Retro Rocket, "
              "Flower Burst, Rainbow Stack and Sunny Day.",
        alt="Five framed kidcore prints arranged as a gallery wall"),
    # ---------------------------------------------------------------- kidcore Christmas + Hanukkah (text-free)
    "checker-christmas-tree": dict(
        niche="kidcore-wall-art", kind="wall", price=6.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Checker Christmas Tree Print, Kidcore Christmas Wall Art Printable, Retro Holiday Poster",
        tags=[*X, "christmas tree print", "holiday wall art", "christmas printable", "kids christmas decor",
              "playroom decor", "checkerboard print", "colorful christmas", "holiday decor", "kidcore wall art",
              "xmas wall art"],
        intro="A three-tier tree covered in candy-colored ornaments, topped with a gold star, over a red checkerboard. "
              "A bright, nostalgic print to swap in for the holidays.",
        alt="Kidcore print of a green Christmas tree with colorful ornaments and a gold star over a red checkerboard"),
    "ornament-parade": dict(
        niche="kidcore-wall-art", kind="wall", price=6.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Ornament Parade Print, Kidcore Christmas Wall Art Printable, Colorful Holiday Poster",
        tags=[*X, "ornament print", "holiday wall art", "christmas printable", "kids christmas decor",
              "playroom decor", "colorful christmas", "holiday decor", "kidcore wall art", "xmas wall art",
              "christmas baubles"],
        intro="Twelve round ornaments in red, yellow, blue, pink and purple hanging on a deep green ground. A cheerful "
              "holiday print for a hallway, kitchen or kid's room.",
        alt="Kidcore print of twelve colorful round Christmas ornaments hanging on green"),
    "candy-stripe-stars": dict(
        niche="kidcore-wall-art", kind="wall", price=6.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Candy Stripe Stars Print, Kidcore Christmas Wall Art Printable, Red Stripe Holiday Poster",
        tags=[*X, "candy stripe print", "holiday wall art", "christmas printable", "kids christmas decor",
              "star wall art", "colorful christmas", "holiday decor", "kidcore wall art", "xmas wall art",
              "red stripe art"],
        intro="A big gold star and a handful of little ones on bold red and pink candy stripes. A festive, graphic "
              "print that brightens any wall for the season.",
        alt="Kidcore print of a large gold star and small stars on diagonal red and pink candy stripes"),
    "gingerbread-house": dict(
        niche="kidcore-wall-art", kind="wall", price=6.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Gingerbread House Print, Kidcore Christmas Wall Art Printable, Snowy Holiday Poster",
        tags=[*X, "gingerbread print", "holiday wall art", "christmas printable", "kids christmas decor",
              "kitchen christmas", "colorful christmas", "holiday decor", "kidcore wall art", "xmas wall art",
              "snowy house print"],
        intro="A little gingerbread house with icing trim and a row of candy lights, in falling snow. A cozy, "
              "sweet print for a kitchen, playroom or holiday corner.",
        alt="Kidcore print of a gingerbread house with white icing and candy lights in falling snow"),
    "kidcore-christmas-set-of-4": dict(
        niche="kidcore-wall-art", kind="set", price=14.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Kidcore Christmas Wall Art Set of 4 Printable, Retro Holiday Gallery Wall Prints",
        tags=[*X, "christmas print set", "gallery wall set", "holiday wall art", "christmas printable",
              "kids christmas decor", "playroom decor", "colorful christmas", "holiday decor", "kidcore wall art",
              "xmas wall art"],
        intro="All four kidcore Christmas prints in one download: Checker Christmas Tree, Ornament Parade, "
              "Candy Stripe Stars and Gingerbread House.",
        alt="Four framed kidcore Christmas prints in a row on a wall"),
    "hanukkah-lights": dict(
        niche="kidcore-wall-art", kind="wall", price=6.99, phrase="", tax=TAX_DIGITAL_PRINTS,
        title="Hanukkah Lights Print, Colorful Menorah Wall Art Printable, Kids Hanukkah Decor",
        tags=["hanukkah wall art", "hanukkah print", "menorah print", "hanukkah decor", "chanukah decor",
              "kids hanukkah", "festival of lights", "holiday wall art", "colorful menorah", "kidcore wall art",
              "printable wall art", "jewish holiday art", "hanukkah printable"],
        intro="A nine-branch Hanukkah lamp with eight colorful candles and the helper candle raised in the middle, "
              "glowing on a deep blue sky over a light blue checkerboard. A bright print for the festival of lights.",
        alt="Kidcore print of a gold nine-branch menorah with colorful lit candles on deep blue"),
    # ---------------------------------------------------------------- printables (PDF)
    "christmas-coloring-pages": dict(
        niche="holiday-planners", kind="pdf", price=6.99, phrase="", tax=TAX_COLORING,
        files=["christmas-coloring-pages-letter.pdf", "christmas-coloring-pages-a4.pdf"],
        title="Christmas Coloring Pages for Kids, 12 Printable Pages, Toddler and Preschool Coloring PDF",
        tags=["christmas coloring", "coloring pages", "kids coloring pages", "christmas printable", "toddler coloring",
              "preschool activity", "holiday activity", "kids christmas", "classroom activity", "printable for kids",
              "christmas craft", "easy coloring pages", "christmas party"],
        intro="Twelve big, simple Christmas pictures with thick lines that little hands can color: a tree, ornament, "
              "gingerbread house, stocking, present, snowman, wreath, candy cane, mitten, cocoa, sled and snowflake.",
        get=["12 coloring pages", "US Letter PDF (8.5 x 11 in)", "A4 PDF (210 x 297 mm)"],
        alt="Three Christmas coloring pages with simple outlines of a tree, ornament and gingerbread house"),
    "christmas-bingo": dict(
        niche="holiday-planners", kind="pdf", price=6.99, phrase="Christmas Bingo", tax=TAX_PARTY_GAMES,
        files=["christmas-bingo-letter.pdf", "christmas-bingo-a4.pdf"],
        title="Christmas Picture Bingo Printable for Kids, 10 Cards, Classroom Holiday Party Game",
        tags=["christmas bingo", "picture bingo", "kids bingo game", "christmas party game", "classroom party",
              "holiday game", "christmas printable", "family game night", "preschool game", "kids christmas",
              "printable game", "school party game", "holiday activity"],
        intro="Picture bingo for kids who can't read yet: ten different 4 x 4 cards with colorful Christmas pictures "
              "and a word under each, plus a sheet of 20 calling cards to cut out.",
        get=["10 different bingo cards", "20 calling cards to cut out", "US Letter PDF (8.5 x 11 in)",
             "A4 PDF (210 x 297 mm)"],
        alt="Christmas picture bingo card with a 4 by 4 grid of colorful holiday pictures"),
    "secret-santa-kit": dict(
        niche="holiday-planners", kind="pdf", price=6.99, phrase="Secret Santa", tax=TAX_PARTY_GAMES,
        files=["secret-santa-kit-letter.pdf", "secret-santa-kit-a4.pdf"],
        title="Secret Santa Kit Printable, Gift Exchange Questionnaire, Name Slips and Gift Tags",
        tags=["secret santa", "gift exchange", "secret santa form", "office christmas", "christmas printable",
              "holiday party game", "gift tags", "name slips", "work party", "santa questionnaire",
              "white elephant", "family gift swap", "holiday printable"],
        intro="Everything for an easy gift exchange at work, school or home: an All About Me questionnaire, an "
              "exchange details sheet with 15 name slips, and 12 matching gift tags.",
        get=["All About Me questionnaire", "Exchange details + 15 name slips", "12 gift tags",
             "US Letter PDF (8.5 x 11 in)", "A4 PDF (210 x 297 mm)"],
        alt="Secret Santa questionnaire, name slips and gift tags printable pages"),
    "kids-christmas-activity-pack": dict(
        niche="holiday-planners", kind="pdf", price=11.99,
        phrase="My Christmas Wish List / Dear Santa / Countdown to Christmas", tax=TAX_PARTY_GAMES,
        files=["kids-christmas-activity-pack-letter.zip", "kids-christmas-activity-pack-a4.zip"],
        title="Kids Christmas Activity Pack Printable, Coloring Pages, Bingo, Wish List, Countdown",
        tags=["kids christmas", "christmas activity", "christmas printable", "coloring pages", "christmas bingo",
              "wish list printable", "letter to santa", "advent countdown", "classroom activity", "holiday activity",
              "busy book pages", "preschool activity", "family activities"],
        intro="A whole stack of Christmas fun for kids in one download: 12 coloring pages, picture bingo with 10 "
              "cards and calling cards, a wish list, a letter to Santa and a color-in countdown from December 1.",
        get=["12 coloring pages", "Picture bingo: 10 cards + 20 calling cards", "Wish list and letter to Santa",
             "Countdown to Christmas chart", "One zip per paper size: US Letter and A4 PDFs"],
        alt="Kids Christmas wish list, letter to Santa and countdown chart printable pages"),
}
XMAS_ART = {"checker-christmas-tree", "ornament-parade", "candy-stripe-stars", "gingerbread-house",
            "kidcore-christmas-set-of-4", "hanukkah-lights"}


def group(key):
    """Concept group (evidence and buyer). Niches stay within the 3-niche ceiling: the Christmas and Hanukkah
    prints ship under kidcore-wall-art, the kids printables under holiday-planners."""
    if key in XMAS_ART:
        return "kidcore-christmas"
    return "kidcore-wall-art" if LISTINGS[key]["niche"] == "kidcore-wall-art" else "kids-christmas-printables"


SET_MEMBERS = {"kidcore-vol-2-set-of-5": ["checker-hearts", "retro-rocket", "flower-burst", "rainbow-stack", "sunny-day"],
               "kidcore-christmas-set-of-4": ["checker-christmas-tree", "ornament-parade", "candy-stripe-stars",
                                              "gingerbread-house"]}

SIGNALS = {
    "kidcore-wall-art": ["sig-20261026-erank-trend-rank-088-kidcore", "release4-scan:etsy:kidcore wall art"],
    "kidcore-christmas": ["release4-scan:etsy:retro christmas printable", "release4-scan:trends:christmas wall art printable"],
    "kids-christmas-printables": ["release4-scan:trends:christmas coloring pages printable",
                                  "release4-scan:trends:secret santa printable",
                                  "release4-scan:etsy:christmas bingo printable"],
}


def etsy_evidence(key):
    scan = json.loads((ROOT / IPSCAN).read_text(encoding="utf-8"))
    q = {"christmas-bingo": "christmas picture bingo", "secret-santa-kit": "secret santa questionnaire",
         "kids-christmas-activity-pack": "christmas wish list printable",
         "christmas-coloring-pages": "christmas coloring pages kids", "hanukkah-lights": "hanukkah wall art printable"}
    k = q.get(key, "kidcore christmas" if group(key) == "kidcore-christmas" else None)
    if not k:
        return "kidcore printable: 232 results, many shops, none licensed (Etsy data, 2026-11-04 scan)"
    r = scan[k]
    return (f'"{k}": {r["count"]} results; top 25 from {r["distinct_shops_top25"]} different shops; '
            f'no "licensed" or "official" titles (Etsy data, {IPSCAN})')


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
                     if t else CheckResult("unknown", "USPTO search not run yet (tmsearch.uspto.gov is blocked from "
                                           "the cloud environment)", CHECKED, ()))
        origin = ("original code-drawn art with no design text" if not p["phrase"] else
                  "plain descriptive holiday wording (bingo, wish list, letter to Santa, countdown, Secret Santa); "
                  "folk tradition and generic game names, not tied to a person, show, brand or meme")
        checks = {
            "origin": CheckResult("pass", origin, CHECKED),
            "trademark": trademark,
            "etsy_marketplace": CheckResult("pass", etsy_evidence(key), CHECKED),
            "text_copyright": CheckResult("pass", "no text or short original labels; no lyrics, poems or quotes",
                                          CHECKED),
            "image_provenance": CheckResult("pass", "code-drawn by tools/make_release4_designs.py; no third-party "
                                            "images, no characters, no faces", CHECKED),
        }
        fmt = "printable_wall_art" if p["kind"] in ("wall", "set") else "printable"
        subj = Subject(phrase=p["phrase"] or p["title"], product_format=fmt, title=p["title"], tags=p["tags"],
                       design_text=[s.strip() for s in p["phrase"].split("/")] if p["phrase"] else [])
        ip = review(subj, checks, blocklist=bl, now=dt.datetime.fromisoformat(CHECKED))
        out.append({
            "concept_id": f"con-20261104-{key}", "niche": p["niche"], "working_title": p["title"].split(",")[0],
            "offer_type": "digital", "product_format": fmt,
            "target_buyer": {"kidcore-wall-art": "adults decorating a playroom, nursery, classroom or kidcore room",
                             "kidcore-christmas": "families decorating for the holidays with a bright, retro look",
                             "kids-christmas-printables": "parents, teachers and office organizers planning December "
                                                          "activities"}[group(key)],
            "gift_occasion": "christmas" if group(key) != "kidcore-wall-art" else None,
            "differentiation": "Original code-drawn kidcore art and crayon grain; no characters or lookalikes",
            "signal_ids": SIGNALS[group(key)], "score": None, "score_version": "scan-2026-11-04 (owner-approved scope)",
            "ip_review": ip, "status": "proposed" if ip["status"] == "pass" else "vetoed", "ai_assisted": True,
            "created_at": CHECKED})
    return out


def description(key, p):
    if p["kind"] == "set":
        n = len(SET_MEMBERS[key])
        get = [f"5 zip files, one per size ratio, each with all {n} prints "
               f"({', '.join(r[1] for r in RATIOS)})"]
        tail = "Print at home, at a local print shop or with an online printer. Frame not included."
    elif p["kind"] == "wall":
        get = [f"{label}: {note}" for _, label, _, _, note in RATIOS] + ["300 ppi JPG files, sRGB"]
        tail = "Print at home, at a local print shop or with an online printer. Frame not included."
    else:
        get = p["get"]
        tail = "Print at home on plain paper or card stock, as many copies as you need for your family or class."
    lines = [p["intro"], "", "WHAT YOU GET"] + [f"• {g}" for g in get] + ["", tail, "", COMMON]
    return "\n".join(lines)


def op(name, niche, payload):
    return {"op": name, "niche": niche, "payload": payload, "payload_sha256": payload_sha256(payload)}


def manifest() -> dict:
    ops = []
    for key, p in LISTINGS.items():
        assert len(p["tags"]) == 13 and len(set(p["tags"])) == 13 and all(len(t) <= 20 for t in p["tags"]), key
        assert len(p["title"].split()) <= 15, (key, len(p["title"].split()))
        base = f"{ASSETS}/{key}"
        idx = len(ops)
        ops.append(op("etsy_create_digital_listing", p["niche"], {
            "title": p["title"], "description": description(key, p), "tags": p["tags"], "taxonomy_id": p["tax"],
            "who_made": "i_did", "when_made": "2020_2026", "ai_assisted": True, "price_usd": p["price"],
            "cost_snapshot": SNAPSHOT, "cost_key": "digital"}))
        ref = f"$ref:ops[{idx}].listing_id"
        if p["kind"] == "pdf":
            names = p["files"]
        else:
            ext = "zip" if p["kind"] == "set" else "jpg"
            names = [f"{key}-{rk}.{ext}" for rk, *_ in RATIOS]
        for name in names:
            ops.append(op("etsy_upload_file", p["niche"], {"listing_id": ref, "path": f"{base}/{name}",
                                                          "file_sha256": file_sha256(ROOT / base / name), "name": name}))
        imgs = sorted((ROOT / base / "images").glob("*.jpg"))
        for rank, path in enumerate(imgs, start=1):
            rel = str(path.relative_to(ROOT))
            ops.append(op("etsy_upload_image", p["niche"], {
                "listing_id": ref, "path": rel, "file_sha256": file_sha256(path), "rank": rank,
                "alt_text": p["alt"] if rank == 1 else
                f"{p['title'].split(',')[0]}: {path.stem.split('-')[-1]} image"}))
    return {"manifest_id": MANIFEST_ID, "created_at": "2026-11-04T02:00:00Z", "created_by": "claude",
            "summary": "Release 4: 16 digital listings, drafts only. Kidcore vol. 2 (5 prints + set of 5), kidcore "
                       "Christmas (4 prints + set of 4) and a Hanukkah print, Christmas coloring pages, picture bingo, "
                       "Secret Santa kit and a kids activity pack. Evidence: 2026-11-04 SerpApi + Etsy scan. Owner "
                       "ticks the AI field and publishes each.",
            "owner_minutes_estimate": 100, "ops": ops}


def main() -> int:
    bl = Blocklist.load()
    cs = concepts(bl, trademark_results())
    out = ROOT / "data" / "scores" / "2026-11-04" / "release4-concepts.json"
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
