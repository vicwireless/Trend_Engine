"""Listing images (5 per product, 2400x1800) and pins (2 per product, 1000x1500) for the seasonal
release, plus pins.md and data/marketing/pin_queue.csv.

    python -m tools.seasonal.listing --assets assets/digital/2026-11-15-seasonal --pins assets/pins/2026-11-15 --work <build dir>

Run tools.seasonal.build first: it leaves page previews in <work>/prev/<key>/.
"""
from __future__ import annotations

import argparse
import csv
import glob
import html
from pathlib import Path

from . import pages as P
from .build import ROOT, render
from .catalog import CATALOG
from .icons import icon

e = html.escape
RAW = "https://raw.githubusercontent.com/vicwireless/Trend_Engine/main/"
GRAIN = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.55 0'/></filter>"
         "<rect width='300' height='300' filter='url(%23n)'/></svg>\")")
ICONSETS = {"thanksgiving": ["turkey", "pumpkin", "leaf", "pie", "acorn", "corn"],
            "christmas": ["tree", "gift", "candy cane", "star", "bell", "holly"],
            "nye": ["glass", "clock", "firework", "balloon", "party hat", "confetti"]}


def css() -> str:
    fonts = (ROOT / "assets" / "fonts").as_uri()
    return f"""
@font-face {{ font-family: 'Fraunces'; src: url('{fonts}/fraunces-Fraunces.ttf'); font-weight: 100 900; }}
@font-face {{ font-family: 'DM Sans'; src: url('{fonts}/dmsans-DMSans.ttf'); font-weight: 100 1000; }}
@font-face {{ font-family: 'Caveat'; src: url('{fonts}/caveat-Caveat.ttf'); font-weight: 400 700; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ width: 100vw; height: 100vh; overflow: hidden; font-family: 'DM Sans', sans-serif; color: var(--d); position: relative; }}
body::after {{ content: ''; position: absolute; inset: 0; background-image: {GRAIN}; opacity: 0.16; mix-blend-mode: multiply; pointer-events: none; }}
.ico {{ width: 1em; height: 1em; display: inline-block; vertical-align: middle; }}
.dark {{ background: var(--a); color: var(--p); }} .cream {{ background: var(--p); }} .warm {{ background: var(--b); color: var(--p); }}
h1 {{ font-family: 'Fraunces', serif; font-variation-settings: 'SOFT' 100, 'WONK' 1; font-weight: 800; line-height: 0.98; letter-spacing: -0.015em; }}
.pill {{ display: inline-block; font-size: 15px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 800; padding: 9px 18px; border-radius: 99px;
  background: var(--c); color: var(--d); }}
.pg {{ position: absolute; background: #fff; box-shadow: 0 18px 40px rgba(0,0,0,0.32), 0 2px 6px rgba(0,0,0,0.25); border-radius: 4px; }}
.pg img {{ width: 100%; height: 100%; display: block; border-radius: 4px; }}
.hand {{ font-family: 'Caveat', cursive; font-weight: 700; }}
ul.ck {{ list-style: none; }} ul.ck li {{ position: relative; padding: 0 0 0 44px; }}
ul.ck li::before {{ content: '✓'; position: absolute; left: 0; top: 0.05em; width: 30px; height: 30px; border-radius: 50%; background: var(--c); color: var(--d);
  font-weight: 900; font-size: 20px; text-align: center; line-height: 30px; }}
.strip {{ position: absolute; left: 0; right: 0; bottom: 0; padding: 16px 0; text-align: center; font-weight: 800; letter-spacing: 0.18em; text-transform: uppercase; font-size: 17px; }}
"""


def doc(body: str, palette: str, cls: str) -> str:
    pal = P.PALETTES[palette]
    vars_ = ";".join(f"--{k}:{pal[k]}" for k in "abcdp")
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head><body class="{cls}" style="{vars_}">{body}</body></html>'


def pg(src: str, x: int, y: int, h: int, rot: float = 0) -> str:
    w = round(h * 8.5 / 11)
    return f'<div class="pg" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rot}deg)"><img src="{src}"></div>'


def previews(work: Path, key: str) -> list[str]:
    return [Path(p).as_uri() for p in sorted(glob.glob(str(work / "prev" / key / "p-*.png")))]


def title_size(text: str, base: int) -> int:
    longest = max(len(w) for w in text.split())
    return min(base, int(base * 9 / max(longest, 9)) + 6, int(base * 22 / max(len(text), 22)) + 14)


# ---------------------------------------------------------------- listing images (1200x900 @2x)
def img_hero(c, pv):
    a, b, d = (pv[i - 1] for i in c["show"])
    kind = "Printable bundle" if c.get("bundle") else "Printable game" if "kit" not in c["hero"].lower() else "Printable kit"
    fs = title_size(c["hero"], 104)
    return doc(
        f'<div style="position:absolute;left:64px;top:70px;width:560px">'
        f'<span class="pill">{kind} · Instant download</span>'
        f'<h1 style="font-size:{fs}px;margin-top:30px;color:var(--p)">{e(c["hero"])}</h1>'
        f'<div class="hand" style="font-size:54px;color:var(--c);margin-top:18px;line-height:1.05">{e(c["sub"])}</div></div>'
        f'<div style="position:absolute;left:64px;bottom:60px;font-size:24px;font-weight:700;letter-spacing:0.04em">'
        f'<span style="display:inline-block;font-size:58px;letter-spacing:10px;background:var(--p);border-radius:18px;padding:10px 12px 10px 22px">{"".join(icon(i) for i in ICONSETS[c["palette"]][:4])}</span>'
        f'<div style="margin-top:16px;opacity:0.95">US Letter + A4 PDF · Print at home</div></div>'
        + pg(d, 890, 150, 560, 9) + pg(b, 770, 120, 600, 3) + pg(a, 640, 130, 640, -5), c["palette"], "dark")


def img_inside(c, pv):
    n = len(pv)
    pick = pv if n <= 10 else [pv[round(i * (n - 1) / 9)] for i in range(10)]
    thumbs = "".join(pg(p, 592 + (i % 5) * 100, 130 + (i // 5) * 310 + (i % 2) * 14, 250, (-2, 1.5, -1, 2, -1.5)[i % 5]) for i, p in enumerate(pick))
    items = "".join(f'<li style="margin-bottom:17px">{e(g)}</li>' for g in c["gets"][:7])
    return doc(
        f'<div style="position:absolute;left:60px;top:60px;width:520px"><span class="pill">What you get</span>'
        f'<h1 style="font-size:60px;color:var(--a);margin:22px 0 26px">{n} pages, ready to print</h1>'
        f'<ul class="ck" style="font-size:{24 if len(c["gets"]) > 5 else 27}px;font-weight:600;line-height:1.22">{items}</ul></div>{thumbs}'
        f'<div class="strip" style="background:var(--a);color:var(--p)">2 PDF files · US Letter and A4 · {n} pages each</div>', c["palette"], "cream")


def img_close(c, pv):
    a, b = (pv[i - 1] for i in c["close"])
    return doc(
        pg(a, 70, 110, 730, -4) + pg(b, 600, 150, 700, 5)
        + '<div style="position:absolute;left:0;right:0;top:26px;text-align:center"><span class="hand" style="font-size:58px;color:var(--p)">Print as many copies as your party needs</span></div>',
        c["palette"], "warm")


def img_how(c, pv):
    steps = [("card", "1. Download", "Get your PDFs from Etsy right after purchase."),
             ("house", "2. Print", "At home or a copy shop, on Letter or A4 paper."),
             (ICONSETS[c["palette"]][1], "3. Play", "Cut where it's dashed, gather everyone and go.")]
    cols = "".join(f'<div style="flex:1;text-align:center;padding:0 22px"><div style="font-size:150px;line-height:1">{icon(i)}</div>'
                   f'<h1 style="font-size:56px;color:var(--a);margin:24px 0 12px">{t}</h1><div style="font-size:27px;font-weight:500;line-height:1.3">{s}</div></div>'
                   for i, t, s in steps)
    return doc(
        '<div style="position:absolute;left:0;right:0;top:64px;text-align:center"><span class="pill">How it works</span>'
        f'<h1 style="font-size:76px;color:var(--b);margin-top:22px">Ready in minutes</h1></div>'
        f'<div style="position:absolute;left:50px;right:50px;top:300px;display:flex">{cols}</div>'
        '<div class="strip" style="background:var(--b);color:var(--p)">Digital download · Nothing is shipped</div>', c["palette"], "cream")


def img_details(c, pv):
    n = len(pv)
    rows = [f"{n} pages in each size", "2 PDF files: US Letter + A4", "Instant download, nothing ships", "Print as often as you like for your own party",
            "Original design by LMCGrows"]
    items = "".join(f'<li style="margin-bottom:24px">{e(r)}</li>' for r in rows)
    return doc(
        f'<div style="position:absolute;left:70px;top:76px;width:620px"><span class="pill">The details</span>'
        f'<h1 style="font-size:{title_size(c["hero"], 78)}px;margin:24px 0 34px;color:var(--p)">{e(c["hero"])}</h1>'
        f'<ul class="ck" style="font-size:31px;font-weight:600;line-height:1.2">{items}</ul></div>'
        + pg(pv[c["close"][1] - 1], 800, 170, 520, 6) + pg(pv[0], 700, 210, 560, -4), c["palette"], "dark")


IMAGES = [("01-hero", img_hero, "{hero} printable, cover and sample pages fanned out on a {color} background"),
          ("02-whats-inside", img_inside, "What you get with the {hero} printable: page previews and a checklist of contents"),
          ("03-close-up", img_close, "Close-up of two sample pages from the {hero} printable"),
          ("04-how-it-works", img_how, "How it works: download the PDFs, print on Letter or A4, then play"),
          ("05-details", img_details, "Details for the {hero} printable: page count, two PDF sizes, instant download")]
COLOR = {"thanksgiving": "olive green", "christmas": "deep green", "nye": "navy"}


# ---------------------------------------------------------------- pins (500x750 @2x)
def pin_a(c, pv):
    a, b = pv[c["show"][0] - 1], pv[c["show"][1] - 1]
    fs = title_size(c["hero"], 74)
    return doc(
        f'<div style="position:absolute;left:0;right:0;top:34px;text-align:center;padding:0 26px"><span class="pill" style="font-size:12px">Printable · Instant download</span>'
        f'<h1 style="font-size:{fs}px;margin-top:16px;color:var(--p)">{e(c["hero"])}</h1>'
        f'<div class="hand" style="font-size:34px;color:var(--c);margin-top:6px;line-height:1">{e(c["sub"])}</div></div>'
        + pg(b, 215, 300, 400, 6) + pg(a, 40, 290, 420, -5)
        + '<div class="strip" style="background:var(--c);color:var(--d);font-size:13px;padding:12px 0">LMCGrows on Etsy · Letter + A4</div>', c["palette"], "dark")


def pin_b(c, pv):
    items = "".join(f'<li style="margin-bottom:9px">{e(g)}</li>' for g in c["gets"][:5])
    fs = title_size(c["hero"], 62)
    return doc(
        f'<div style="position:absolute;left:30px;right:30px;top:30px"><div style="font-size:54px;letter-spacing:8px;text-align:center">{"".join(icon(i) for i in ICONSETS[c["palette"]][:4])}</div>'
        f'<h1 style="font-size:{fs}px;color:var(--a);text-align:center;margin:12px 0 4px">{e(c["hero"])}</h1>'
        f'<div class="hand" style="font-size:30px;color:var(--b);text-align:center;margin-bottom:14px">print today, play tonight</div>'
        f'<ul class="ck" style="font-size:17px;font-weight:600;line-height:1.25;width:250px">{items}</ul></div>'
        + pg(pv[c["close"][0] - 1], 286, 330, 330, 5)
        + '<div class="strip" style="background:var(--b);color:var(--p);font-size:13px;padding:12px 0">Instant download · LMCGrows on Etsy</div>', c["palette"], "cream")


def pin_copy(key: str, c: dict, v: int) -> dict:
    hero = c["hero"]
    occasion = {"thanksgiving": "Thanksgiving dinner", "christmas": "Christmas party", "nye": "New Year's Eve party"}[c["palette"]]
    if v == 0:
        title = f"{hero}: printable for your {occasion}"
        desc = (f"{c['intro']} Instant download in US Letter and A4, so you can print it today. "
                f"Includes: {'; '.join(c['gets'][:3])}.")
        alt = f"Pin showing the cover and a sample page of the {hero} printable on a {COLOR[c['palette']]} background with the words {hero} and {c['sub']}."
    else:
        title = f"Print today, play tonight: {hero} (instant download)"
        desc = (f"Need a last-minute idea for your {occasion}? {hero} is a print-at-home PDF: {c['sub']}. "
                f"What you get: {'; '.join(c['gets'][:4])}. US Letter and A4 included.")
        alt = f"Pin on a cream background with holiday icons, the title {hero}, a checklist of what is included and one sample page."
    return {"title": title[:100], "description": desc[:500], "alt_text": alt[:500]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", required=True)
    ap.add_argument("--pins", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--only", nargs="*", help="render just these products and merge their pins into the existing files")
    ap.add_argument("--queue", default="data/marketing/pin_queue.csv")
    args = ap.parse_args(argv)
    work = Path(args.work)
    jobs, rows, md = [], [], ["# Pins for the 2026-11-15 seasonal release\n",
                              "Two pins per listing, 1000x1500. Not posted by the engine; the desktop session schedules them through Postiz "
                              "from `data/marketing/pin_queue.csv`.\n"]
    (ROOT / args.pins).mkdir(parents=True, exist_ok=True)
    for key, c in CATALOG.items():
        if args.only and key not in args.only:
            continue
        pv = previews(work, key)
        d = ROOT / args.assets / key / "images"
        d.mkdir(parents=True, exist_ok=True)
        for name, fn, _ in IMAGES:
            h = work / f"img-{key}-{name}.html"
            h.write_text(fn(c, pv), encoding="utf-8")
            jobs.append({"html": str(h), "image": str(d / f"{key}-{name}.jpg"), "w": 1200, "h": 900, "scale": 2, "quality": 88})
        link = f"https://www.etsy.com/listing/{c['listing_id']}"
        for v, fn in enumerate((pin_a, pin_b)):
            h = work / f"pin-{key}-{v + 1}.html"
            h.write_text(fn(c, pv), encoding="utf-8")
            rel = f"{args.pins}/{key}-pin-{v + 1}.jpg"
            jobs.append({"html": str(h), "image": str(ROOT / rel), "w": 500, "h": 750, "scale": 2, "quality": 90})
            copy = pin_copy(key, c, v)
            rows.append({"listing_id": c["listing_id"], "image_path": rel, "image_raw_url": RAW + rel, **copy, "link": link, "board": c["board"]})
            md.append(f"## {key} pin {v + 1}\n- Image: `{Path(rel).name}`\n- Board: {c['board']}\n- Title: {copy['title']}\n- Description: {copy['description']}\n"
                      f"- Alt text: {copy['alt_text']}\n- Destination: {link}\n")
    render(jobs, work)
    fields = ["listing_id", "image_path", "image_raw_url", "title", "description", "alt_text", "link", "board"]
    md_path, q = ROOT / args.pins / "pins.md", ROOT / args.queue
    if args.only:   # merge: keep rows whose image still exists and is not being re-rendered
        new_paths = {r["image_path"] for r in rows}
        old = []
        if q.exists():
            with open(q, newline="", encoding="utf-8") as f:
                old = [r for r in csv.DictReader(f) if r["image_path"] not in new_paths and (ROOT / r["image_path"]).is_file()]
        rows = old + rows
        md = ["# Pins for the 2026 seasonal releases\n",
              "Two pins per listing, 1000x1500. Not posted by the engine; the desktop session schedules them through Postiz.\n"]
        for r in rows:
            md.append(f"## {Path(r['image_path']).stem}\n- Image: `{Path(r['image_path']).name}`\n- Board: {r['board']}\n- Title: {r['title']}\n"
                      f"- Description: {r['description']}\n- Alt text: {r['alt_text']}\n- Destination: {r['link']}\n")
    md_path.write_text("\n".join(md), encoding="utf-8")
    with open(q, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(jobs)} images rendered; {len(rows)} pins queued in {q.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
