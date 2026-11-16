"""Print-on-demand design masters for the holiday POD test (mugs, ornaments, tees).

    python -m tools.seasonal.pod --out assets/pod/masters/2026-11-16-holiday --work <dir>

Transparent 300 ppi PNGs drawn from the same original icon set as the printables. Pixel sizes are the
commonly published print areas for these product types and MUST be checked against the chosen
Printify blueprint's placeholder before upload (the catalog API was not reachable on 2026-11-16).
Each file is run through src/qa/print_qa.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageCms

from src.qa.print_qa import PrintSpec, run

from . import pages as P
from .build import ROOT, render
from .icons import XMAS_BINGO, icon
from .pages import bingo_cards

SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
FONTS = (ROOT / "assets" / "fonts").as_uri()
BASE = f"""
@font-face {{ font-family: 'Fraunces'; src: url('{FONTS}/fraunces-Fraunces.ttf'); font-weight: 100 900; }}
@font-face {{ font-family: 'Caveat'; src: url('{FONTS}/caveat-Caveat.ttf'); font-weight: 400 700; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: transparent; width: 100vw; height: 100vh; overflow: hidden; }}
body {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
.ico {{ width: 1em; height: 1em; display: inline-block; vertical-align: middle; }}
h1 {{ font-family: 'Fraunces', serif; font-variation-settings: 'SOFT' 100, 'WONK' 1; font-weight: 800; line-height: 0.95; letter-spacing: -0.01em; color: var(--a); }}
.hand {{ font-family: 'Caveat', cursive; font-weight: 700; color: var(--b); }}
"""


def doc(body: str, palette: str, extra: str = "") -> str:
    pal = P.PALETTES[palette]
    vars_ = ";".join(f"--{k}:{pal[k]}" for k in "abcdp")
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{BASE}{extra}</style></head><body style="{vars_}">{body}</body></html>'


def row(names, size):
    return f'<div style="font-size:{size}px;letter-spacing:{size // 5}px;line-height:1.25">{"".join(icon(n) for n in names)}</div>'


def designs() -> dict:
    card = bingo_cards(1, seed=77)[0]
    cells = card[:12] + ["FREE"] + card[12:]
    grid = "".join('<div style="background:var(--a);color:#fff;font-family:Fraunces;font-weight:800;font-size:30px;display:flex;align-items:center;justify-content:center">FREE</div>'
                   if c == "FREE" else f'<div style="display:flex;align-items:center;justify-content:center;font-size:78px;border:3px solid var(--d)">{icon(c)}</div>' for c in cells)
    pat = XMAS_BINGO
    return {
        # key: (viewport w, h, scale, palette, html, print size in inches, product, note)
        "mug-christmas-icons": (825, 385, 3, "christmas",
                                doc(row(pat[0:10], 58) + row(pat[10:20], 58) + row(pat[20:30], 58), "christmas"),
                                (8.25, 3.85), "11 oz ceramic mug, full wrap", "Icon pattern, no text."),
        "mug-merry-christmas": (825, 385, 3, "christmas",
                                doc('<div style="display:flex;width:100%;justify-content:space-around;align-items:center">'
                                    + "".join(f'<div>{row(ic, 44)}<h1 style="font-size:74px;margin:8px 0 2px">Merry<br>Christmas</h1><div class="hand" style="font-size:34px">warm wishes, hot cocoa</div></div>'
                                              for ic in (["tree", "star", "gift"], ["cocoa", "cookie", "candy cane"])) + "</div>", "christmas"),
                                (8.25, 3.85), "11 oz ceramic mug, front and back", "Generic greeting, original lettering layout."),
        "ornament-tree-2026": (500, 500, 4, "christmas",
                               doc(f'<div style="font-size:250px;line-height:1">{icon("tree")}</div><h1 style="font-size:92px;color:var(--b)">2026</h1>' + row(["star", "star", "star"], 36), "christmas"),
                               (2.75, 2.75), "Round ceramic ornament", "Year ornament."),
        "ornament-snowflake": (500, 500, 4, "christmas",
                               doc(f'<div style="font-size:210px;line-height:1.05">{icon("snowflake")}</div><h1 style="font-size:54px">Merry Christmas</h1><div class="hand" style="font-size:54px;line-height:1">2026</div>', "christmas"),
                               (2.75, 2.75), "Round ceramic ornament", "Generic greeting."),
        "tee-christmas-bingo": (900, 1080, 5, "christmas",
                                doc('<h1 style="font-size:104px;color:var(--b);letter-spacing:0.02em">CHRISTMAS<br>BINGO</h1>'
                                    f'<div style="display:grid;grid-template-columns:repeat(5,128px);grid-template-rows:repeat(5,128px);border:6px solid var(--d);margin-top:36px;background:var(--p)">{grid}</div>'
                                    '<div class="hand" style="font-size:58px;margin-top:18px">free space is for snacks</div>', "christmas"),
                                (15, 18), "Unisex tee, front print", "Matches the Christmas Bingo printable."),
        "tee-happy-new-year-2027": (900, 1080, 5, "nye",
                                    doc(row(["firework", "glass", "firework"], 170) + '<h1 style="font-size:150px;margin-top:30px">Happy<br>New Year</h1>'
                                        '<h1 style="font-size:230px;color:var(--c);margin-top:10px">2027</h1>' + row(["confetti", "clock", "confetti"], 110), "nye"),
                                    (15, 18), "Unisex tee, front print", "Generic greeting with the year."),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    out, work = ROOT / args.out, Path(args.work)
    out.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    jobs, d = [], designs()
    for key, (w, h, scale, _pal, html, *_rest) in d.items():
        hp = work / f"pod-{key}.html"
        hp.write_text(html, encoding="utf-8")
        jobs.append({"html": str(hp), "image": str(out / f"{key}.png"), "w": w, "h": h, "scale": scale, "transparent": True})
    render(jobs, work)
    report = []
    for key, (w, h, scale, _pal, _html, (win, hin), product, note) in d.items():
        path = out / f"{key}.png"
        with Image.open(path) as im:
            im.convert("RGBA").save(path, icc_profile=SRGB, optimize=True)
        r = run(path, PrintSpec(width_in=win, height_in=hin, ppi=300, require_transparency=True, max_file_mb=20))
        report.append({"design": key, "file": f"{args.out}/{key}.png", "px": [w * scale, h * scale], "print_in": [win, hin],
                       "product": product, "note": note, "print_qa_passed": r.passed,
                       "failed": [f"{c.name}: {c.detail}" for c in r.checks if not c.passed]})
        print(key, "PASS" if r.passed else "FAIL", [c.detail for c in r.checks if not c.passed])
    (out / "print-qa.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0 if all(x["print_qa_passed"] for x in report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
