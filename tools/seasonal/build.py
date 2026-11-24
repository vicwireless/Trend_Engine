"""Build the 2026 seasonal printables: Letter and A4 PDFs per product, bundles, page previews.

    python -m tools.seasonal.build --out assets/digital/2026-11-15-seasonal --work /tmp/seasonal-build

Original code-drawn layouts and icons (tools/seasonal/), open-licensed fonts (assets/fonts/, SIL OFL).
Needs Node with Playwright/Chromium (render.js) and poppler's pdftoppm for previews.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from . import pages as P

ROOT = Path(__file__).resolve().parents[2]
SIZES = {"letter": ("8.5in", "11in"), "a4": ("210mm", "297mm")}

# key -> (palette, builder)
SINGLES = {
    "thanksgiving-trivia": ("thanksgiving", P.thanksgiving_trivia),
    "thanksgiving-who-at-this-table": ("thanksgiving", P.most_likely),
    "thanksgiving-kids-table": ("thanksgiving", P.kids_table),
    "christmas-trivia": ("christmas", P.christmas_trivia),
    "christmas-left-right-game": ("christmas", P.left_right),
    "white-elephant-kit": ("christmas", P.white_elephant),
    "secret-santa-kit": ("christmas", P.secret_santa),
    "letter-to-santa-kit": ("christmas", P.santa_letter),
    "christmas-gift-certificates": ("christmas", P.gift_certificates),
    "christmas-bingo": ("christmas", P.bingo),
    "christmas-charades": ("christmas", P.charades),
    "new-years-eve-games": ("nye", P.nye_games),
    # 2026-11-24 add-ons
    "christmas-word-games": ("christmas", P.christmas_word_games),
    "christmas-gift-tags": ("christmas", P.gift_tags),
    "christmas-table-games": ("christmas", P.christmas_table_games),
    "new-years-eve-kids-pack": ("nye", P.nye_kids),
}
BUNDLES = {
    "thanksgiving-games-bundle": {
        "palette": "thanksgiving", "members": ["thanksgiving-trivia", "thanksgiving-who-at-this-table", "thanksgiving-kids-table"],
        "bonus": P.bonus_thanksgiving,
        "cover": lambda: P.bundle_cover("Printable party games", "Thanksgiving Games Bundle", "Five games for the whole table",
                                        ["turkey", "pie", "pumpkin"],
                                        ["Thanksgiving Trivia (30 questions)", "Who at This Table? dinner party game (48 cards)",
                                         "Thanksgiving Kids Table activity pack", "Bonus: This or That", "Bonus: conversation cards (24)"],
                                        "Thanksgiving Games Bundle"),
    },
    "christmas-games-bundle": {
        "palette": "christmas", "members": ["christmas-trivia", "christmas-left-right-game", "christmas-bingo", "christmas-charades", "white-elephant-kit"],
        "bonus": P.bonus_christmas,
        "cover": lambda: P.bundle_cover("Printable party games", "Christmas Games Bundle", "Seven games for family, friends and the office",
                                        ["tree", "gift", "candy cane"],
                                        ["Christmas Trivia (40 questions)", "The Left Right gift-passing game", "Christmas Bingo (30 picture cards)",
                                         "Christmas Charades (72 cards)", "White Elephant gift exchange kit", "Bonus: Which Would You Choose? (32 cards)",
                                         "Bonus: Indoor scavenger hunt (12 rhyming clues)"],
                                        "Christmas Games Bundle"),
    },
}


def document(pages: list[str], palette: str, size: str) -> str:
    pal = P.PALETTES[palette]
    w, h = SIZES[size]
    vars_ = ";".join(f"--{k}:{pal[k]}" for k in "abcdp") + f";--pw:{w};--ph:{h}"
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><style>@page{{size:{w} {h};margin:0}}'
            f'{P.css((ROOT / "assets" / "fonts").as_uri())}</style></head><body style="{vars_}">{"".join(pages)}</body></html>')


def render(jobs: list[dict], work: Path) -> None:
    jf = work / "jobs.json"
    jf.write_text(json.dumps(jobs))
    env = {**os.environ, "NODE_PATH": os.environ.get("NODE_PATH", "/opt/node-tools/node_modules")}
    subprocess.run(["node", str(ROOT / "tools/seasonal/render.js"), str(jf)], check=True, env=env)


def merge(parts: list[Path], out: Path, title: str) -> int:
    w = PdfWriter()
    for part in parts:
        for pg in PdfReader(part).pages:
            w.add_page(pg)
    w.add_metadata({"/Title": title, "/Author": "LMCGrows"})
    w.compress_identical_objects()
    with open(out, "wb") as f:
        w.write(f)
    return len(w.pages)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args(argv)
    out, work = (ROOT / args.out), Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    jobs, index = [], {}

    def add(key, palette, pages, tag=""):
        for size, (w, h) in SIZES.items():
            html = work / f"{key}{tag}-{size}.html"
            html.write_text(document(pages, palette, size), encoding="utf-8")
            pdf = work / f"{key}{tag}-{size}.pdf"
            jobs.append({"html": str(html), "pdf": str(pdf), "width": w, "height": h})

    keys = args.only or list(SINGLES) + list(BUNDLES)
    for key in keys:
        if key in SINGLES:
            palette, fn = SINGLES[key]
            add(key, palette, fn())
        else:
            b = BUNDLES[key]
            add(key, b["palette"], [b["cover"]()], "-cover")
            add(key, b["palette"], b["bonus"](), "-bonus")
            for m in b["members"]:
                if not (work / f"{m}-letter.html").exists() or m not in keys:
                    add(m, SINGLES[m][0], SINGLES[m][1]())
    seen = set()
    jobs = [j for j in jobs if not (j["pdf"] in seen or seen.add(j["pdf"]))]
    render(jobs, work)

    for key in keys:
        d = out / key
        d.mkdir(parents=True, exist_ok=True)
        for size in SIZES:
            name = f"{key}-{'us-letter' if size == 'letter' else 'a4'}.pdf"
            if key in SINGLES:
                parts, title = [work / f"{key}-{size}.pdf"], key.replace("-", " ").title()
            else:
                b = BUNDLES[key]
                parts = ([work / f"{key}-cover-{size}.pdf"] + [work / f"{m}-{size}.pdf" for m in b["members"]]
                         + [work / f"{key}-bonus-{size}.pdf"])
                title = key.replace("-", " ").title()
            n = merge(parts, d / name, title)
            index.setdefault(key, {})[size] = {"file": f"{args.out}/{key}/{name}", "pages": n,
                                               "mb": round((d / name).stat().st_size / 1e6, 2)}
        # page previews for listing images and review (work dir only, not committed)
        prev = work / "prev" / key
        prev.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdftoppm", "-r", "140", "-png", str(d / f"{key}-us-letter.pdf"), str(prev / "p")], check=True)
    (work / "index.json").write_text(json.dumps(index, indent=2))
    print(json.dumps(index, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
