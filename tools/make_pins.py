"""Make two Pinterest pin images (1000x1500) per planner-family listing, plus pins.md with the text.

    python tools/make_pins.py --assets assets/digital/2026-10-23-planner-family --out assets/pins/2026-10-23
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from tools.make_planner_family import PRODUCTS, YEAR, paste_shadow, pil_font, render_page, wrap

IDS = {"weekly-planner": 4601751471, "goal-planner": 4601781508, "habit-tracker": 4601756001}
PIN_TITLES = {
    "weekly-planner": ("2027 Weekly Planner Printable", "One calm page per week"),
    "goal-planner": ("2027 Goal Planner Printable", "Plan the year, check in monthly"),
    "habit-tracker": ("2027 Habit Tracker Printable", "One circle a day"),
}
BOARDS = {"weekly-planner": "2027 Planners", "goal-planner": "Goals and Habits", "habit-tracker": "Goals and Habits"}
PIN_TEXT = {
    "weekly-planner": [
        ("2027 weekly planner printable, minimal week-by-week pages",
         "A calm, minimal 2027 weekly planner to print at home. One page per week with seven day boxes, top 3 priorities and notes. US Letter and A4 PDFs, instant download. Great for a new year planner reset."),
        ("Printable 2027 planner: 53 weekly pages, Letter and A4",
         "Print only the weeks you need. Mostly white space, so it is light on ink. Weekly planner printable for 2027 with a how-to-print guide included."),
    ],
    "goal-planner": [
        ("2027 goal planner printable: yearly goals and monthly check-ins",
         "See the year, pick three big goals, plan each quarter and check in every month. A quiet, minimal goal planner PDF for 2027 in US Letter and A4. Instant download."),
        ("New year reset: printable goal planner for 2027",
         "19 pages: year in view, three big goals, four quarterly plans, twelve monthly check-ins and a year-end review. Print at home. Start any month."),
    ],
    "habit-tracker": [
        ("2027 habit tracker printable: 12 monthly pages",
         "Track up to 12 habits a month with one circle a day. Minimal 2027 habit tracker PDF in US Letter and A4 with a reflection box on every page. Instant download."),
        ("Printable monthly habit log for 2027",
         "A simple habit tracker you print at home: weekday letters above each date, 12 habit rows, one page per month. Reprint a month if you start late."),
    ],
}
BG, SAGE, INK, MUTED = "#F3EFE7", "#4F6F5B", "#2B2B2B", "#6B6B6B"


def pin_a(pdf: Path, key: str, out: Path) -> None:
    head, sub = PIN_TITLES[key]
    img = Image.new("RGB", (1000, 1500), BG)
    d = ImageDraw.Draw(img)
    d.text((70, 70), str(YEAR), font=pil_font("serif-b", 150), fill=SAGE)
    y = 250
    for ln in wrap(d, head.replace(f"{YEAR} ", ""), pil_font("serif-b", 84), 860):
        d.text((70, y), ln, font=pil_font("serif-b", 84), fill=INK)
        y += 100
    d.text((70, y + 10), sub, font=pil_font("serif", 46), fill=MUTED)
    pg = render_page(pdf, 0 if key != "weekly-planner" else 1, 620)
    paste_shadow(img, pg, (190, 560))
    d.text((70, 1420), "Printable PDF  |  Letter + A4  |  Instant download", font=pil_font("sans-b", 34), fill=INK)
    img.save(out)


def pin_b(pdf: Path, key: str, p: dict, out: Path) -> None:
    img = Image.new("RGB", (1000, 1500), BG)
    d = ImageDraw.Draw(img)
    d.text((70, 70), "What's inside", font=pil_font("serif-b", 96), fill=INK)
    y = 230
    for item in p["inside"][:4]:
        d.ellipse([75, y + 10, 103, y + 38], outline=SAGE, width=4)
        for ln in wrap(d, item, pil_font("sans", 40), 800):
            d.text((130, y), ln, font=pil_font("sans", 40), fill=INK)
            y += 54
        y += 24
    pg = render_page(pdf, p["samples"][-1], 560)
    paste_shadow(img, pg, (220, max(y + 40, 700)))
    d.text((70, 1420), "Print at home  |  For personal use", font=pil_font("sans-b", 34), fill=INK)
    img.save(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    assets, out = Path(a.assets), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    lines = ["# Pins to post by hand (2026-10-23)", "",
             "For each pin: upload the image, paste the title and description, set the board, and use the listing's "
             "**Share & Save link** as the destination (Shop Manager > Marketing > Share & Save), not the plain address. "
             "Post one or two a day. The 'AI-assisted' disclosure lives on the listing; Pinterest asks you to label "
             "AI-modified images, and these are code-drawn layouts with no photos.", ""]
    n = 0
    for key, p in PRODUCTS.items():
        pdf = assets / key / f"{YEAR}-{key}-letter.pdf"
        for i, (title, desc) in enumerate(PIN_TEXT[key]):
            n += 1
            f = out / f"pin-{n}-{key}-{'ab'[i]}.png"
            (pin_a(pdf, key, f) if i == 0 else pin_b(pdf, key, p, f))
            assert len(title) <= 100 and len(desc) <= 500
            lines += [f"## Pin {n}: {key}", f"- Image: `{f.name}`", f"- Board: {BOARDS[key]}", f"- Title: {title}",
                      f"- Description: {desc}", f"- Destination: https://www.etsy.com/listing/{IDS[key]} (swap in the Share & Save link)", ""]
    (out / "pins.md").write_text("\n".join(lines), encoding="utf-8")
    print(n, "pins")


if __name__ == "__main__":
    main()
