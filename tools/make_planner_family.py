"""Generate the 2027 planner-family printables (code-drawn layouts, no raster art) and their listing images.

    python tools/make_planner_family.py --out assets/digital/2026-10-23-planner-family

Writes, per product: US Letter and A4 PDFs, a one-page print guide, and five 2400x1800 listing images.
Fonts are Liberation Serif/Sans (SIL OFL). Everything is original geometry and text.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
pdfmetrics.registerFont(TTFont("Serif", FONT_DIR / "LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Bold", FONT_DIR / "LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Italic", FONT_DIR / "LiberationSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Sans", FONT_DIR / "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", FONT_DIR / "LiberationSans-Bold.ttf"))

INK, MUTED, RULE, SAGE, PAPER = HexColor("#2B2B2B"), HexColor("#6B6B6B"), HexColor("#C9C4BA"), HexColor("#4F6F5B"), HexColor("#FAF8F4")
YEAR = 2027
MONTHS = [calendar.month_name[m] for m in range(1, 13)]
SIZES = {"letter": letter, "a4": A4}
MARGIN = 40  # points


def week_start(size: str) -> int:
    return calendar.SUNDAY if size == "letter" else calendar.MONDAY


def day_names(size: str) -> list[str]:
    first = week_start(size)
    return [calendar.day_abbr[(first + i) % 7] for i in range(7)]


def header(c, w, h, title, sub=None):
    c.setFillColor(INK)
    c.setFont("Serif-Bold", 26)
    c.drawString(MARGIN, h - MARGIN - 22, title)
    if sub:
        c.setFont("Sans", 9.5)
        c.setFillColor(MUTED)
        c.drawString(MARGIN, h - MARGIN - 38, sub)
    c.setStrokeColor(SAGE)
    c.setLineWidth(1.2)
    c.line(MARGIN, h - MARGIN - 46, w - MARGIN, h - MARGIN - 46)
    return h - MARGIN - 58


def footer(c, w, label):
    c.setFont("Sans", 7.5)
    c.setFillColor(MUTED)
    c.drawCentredString(w / 2, 22, f"{label}  |  for personal use")


def lined(c, x, y_top, width, n, gap):
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    for i in range(1, n + 1):
        c.line(x, y_top - i * gap, x + width, y_top - i * gap)


def box(c, x, y, w_, h_, title=None):
    c.setStrokeColor(RULE)
    c.setLineWidth(0.7)
    c.rect(x, y, w_, h_, stroke=1, fill=0)
    if title:
        c.setFont("Sans-Bold", 8)
        c.setFillColor(SAGE)
        c.drawString(x + 6, y + h_ - 12, title.upper())


# ---------- Product 1: weekly planner ----------
def weekly(path: Path, size: str):
    w, h = SIZES[size]
    c = canvas.Canvas(str(path), pagesize=SIZES[size])
    c.setTitle(f"{YEAR} Weekly Planner")
    first = week_start(size)
    d = dt.date(YEAR, 1, 1)
    while d.weekday() != (first if first == 0 else 6):  # step back to the week start
        d -= dt.timedelta(days=1)
    n = 0
    while d.year <= YEAR and not (d.year == YEAR + 1 and d.day > 7):
        end = d + dt.timedelta(days=6)
        if d.year > YEAR:
            break
        n += 1
        label = f"{d:%b} {d.day} - {end:%b} {end.day}" if d.month != end.month else f"{d:%B} {d.day} - {end.day}"
        y = header(c, w, h, f"Week {n}", f"{label}, {end.year if end.year == YEAR else d.year}")
        top = y - 6
        left_w = (w - 2 * MARGIN) * 0.64
        right_x = MARGIN + left_w + 14
        right_w = w - MARGIN - right_x
        row_h = (top - 60) / 7
        for i in range(7):
            day = d + dt.timedelta(days=i)
            ry = top - (i + 1) * row_h
            box(c, MARGIN, ry, left_w, row_h)
            c.setFont("Serif-Bold", 12)
            c.setFillColor(INK)
            c.drawString(MARGIN + 8, ry + row_h - 17, f"{calendar.day_abbr[day.weekday()]}")
            c.setFont("Sans", 9)
            c.setFillColor(MUTED)
            c.drawString(MARGIN + 8, ry + row_h - 30, f"{day:%b} {day.day}")
            lined(c, MARGIN + 54, ry + row_h - 8, left_w - 64, int((row_h - 12) // 16), 16)
        ph = (top - 60) * 0.34
        box(c, right_x, top - ph, right_w, ph, "Top 3 priorities")
        lined(c, right_x + 8, top - 14, right_w - 16, int((ph - 18) // 22), 22)
        nh = (top - 60) - ph - 12
        box(c, right_x, 60, right_w, nh, "Notes")
        lined(c, right_x + 8, 60 + nh - 14, right_w - 16, int((nh - 18) // 22), 22)
        footer(c, w, f"{YEAR} Weekly Planner")
        c.showPage()
        d += dt.timedelta(days=7)
        if d > dt.date(YEAR, 12, 31):
            break
    c.save()


# ---------- Product 2: goal planner ----------
def goals(path: Path, size: str):
    w, h = SIZES[size]
    c = canvas.Canvas(str(path), pagesize=SIZES[size])
    c.setTitle(f"{YEAR} Goal Planner")
    cw = w - 2 * MARGIN

    y = header(c, w, h, f"{YEAR}: A Year in View", "Write it down, then make it small enough to start.")
    for i, (t, hh) in enumerate([("My word for the year", 70), ("Where I want to be by December", 170),
                                 ("What I am leaving behind", 120), ("What I will protect (time, energy, people)", 140)]):
        box(c, MARGIN, y - sum(x[1] for x in [("", 70), ("", 170), ("", 120), ("", 140)][:i + 1]) - 14 * (i + 1) + 14,
            cw, hh, t)
    footer(c, w, f"{YEAR} Goal Planner")
    c.showPage()

    y = header(c, w, h, "Three Big Goals", "For each: why it matters, the first step, and how you will know.")
    gh = (y - 70) / 3
    for i in range(3):
        top = y - i * gh
        box(c, MARGIN, top - gh + 10, cw, gh - 10, f"Goal {i + 1}")
        for j, lab in enumerate(["The goal", "Why it matters", "First step (this week)", "I will know it worked when"]):
            ly = top - 34 - j * ((gh - 56) / 4)
            c.setFont("Sans", 8.5)
            c.setFillColor(MUTED)
            c.drawString(MARGIN + 10, ly + 3, lab)
            c.setStrokeColor(RULE)
            c.line(MARGIN + 150, ly, MARGIN + cw - 10, ly)
    footer(c, w, f"{YEAR} Goal Planner")
    c.showPage()

    for q in range(4):
        months = ", ".join(MONTHS[q * 3:q * 3 + 3])
        y = header(c, w, h, f"Quarter {q + 1}", months)
        bh = (y - 70) / 4
        for i, t in enumerate(["Focus for this quarter", "Milestones", "Habits that support it", "Review at quarter end"]):
            top = y - i * bh
            box(c, MARGIN, top - bh + 10, cw, bh - 10, t)
            lined(c, MARGIN + 10, top - 14, cw - 20, int((bh - 34) // 20), 20)
        footer(c, w, f"{YEAR} Goal Planner")
        c.showPage()

    for m in range(12):
        y = header(c, w, h, MONTHS[m], f"{YEAR} monthly check-in")
        half = (cw - 14) / 2
        hh = (y - 70) / 3
        pairs = [("This month's focus", "Wins"), ("Next actions", "What got in the way"), ("Adjust for next month", "Gratitude")]
        for i, (a, b) in enumerate(pairs):
            top = y - i * hh
            box(c, MARGIN, top - hh + 10, half, hh - 10, a)
            lined(c, MARGIN + 8, top - 14, half - 16, int((hh - 34) // 20), 20)
            box(c, MARGIN + half + 14, top - hh + 10, half, hh - 10, b)
            lined(c, MARGIN + half + 22, top - 14, half - 16, int((hh - 34) // 20), 20)
        footer(c, w, f"{YEAR} Goal Planner")
        c.showPage()

    y = header(c, w, h, f"{YEAR} Year-End Review", "Come back here in December.")
    bh = (y - 70) / 4
    for i, t in enumerate(["What I finished", "What I learned", "What I will carry into next year", "A note to myself"]):
        top = y - i * bh
        box(c, MARGIN, top - bh + 10, cw, bh - 10, t)
        lined(c, MARGIN + 10, top - 14, cw - 20, int((bh - 34) // 20), 20)
    footer(c, w, f"{YEAR} Goal Planner")
    c.showPage()
    c.save()


# ---------- Product 3: habit tracker ----------
def habits(path: Path, size: str):
    w, h = SIZES[size]
    c = canvas.Canvas(str(path), pagesize=SIZES[size])
    c.setTitle(f"{YEAR} Habit Tracker")
    for m in range(1, 13):
        ndays = calendar.monthrange(YEAR, m)[1]
        y = header(c, w, h, MONTHS[m - 1], f"{YEAR} habit tracker. Fill a circle each day you do it.")
        label_w = 120
        cell = (w - 2 * MARGIN - label_w) / 31
        rows = 12
        row_h = min(34, (y - 130) / rows)
        c.setFont("Sans", 6.5)
        c.setFillColor(MUTED)
        for d in range(1, 32):
            cx = MARGIN + label_w + (d - 0.5) * cell
            c.drawCentredString(cx, y - 18, str(d))
            if d <= ndays:
                wd = dt.date(YEAR, m, d).weekday()
                c.setFont("Sans", 5.5)
                c.drawCentredString(cx, y - 8, "MTWTFSS"[wd])
                c.setFont("Sans", 6.5)
        for r in range(rows):
            ry = y - 28 - (r + 1) * row_h
            c.setStrokeColor(RULE)
            c.setLineWidth(0.5)
            c.line(MARGIN, ry, w - MARGIN, ry)
            c.setFont("Sans", 7)
            c.setFillColor(MUTED)
            c.drawString(MARGIN + 2, ry + row_h / 2 - 2, f"{r + 1}.")
            c.line(MARGIN + 14, ry + 6, MARGIN + label_w - 8, ry + 6)
            for d in range(1, ndays + 1):
                cx = MARGIN + label_w + (d - 0.5) * cell
                c.setStrokeColor(RULE)
                c.circle(cx, ry + row_h / 2, min(cell, row_h) * 0.3, stroke=1, fill=0)
        by = y - 28 - rows * row_h - 20
        box(c, MARGIN, 44, (w - 2 * MARGIN), by - 44, "Reflection: what is working, what to change")
        lined(c, MARGIN + 8, by - 8, w - 2 * MARGIN - 16, int((by - 44 - 20) // 20), 20)
        footer(c, w, f"{YEAR} Habit Tracker")
        c.showPage()
    c.save()


# ---------- print guide (shared text, per product) ----------
def guide(path: Path, product: str, pages: str):
    w, h = letter
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setTitle(f"How to print: {product}")
    y = header(c, w, h, "How to Print", product)
    lines = [
        ("Files", f"You will find two PDFs: US Letter (8.5 x 11 in) and A4 (210 x 297 mm). {pages}"),
        ("Pick your size", "Use Letter in the US and Canada. Use A4 almost everywhere else. Planners with a Sunday week start are in the Letter file; the A4 file starts weeks on Monday."),
        ("Print settings", "Choose Actual size or 100% (not 'fit to page'). Print single-sided or double-sided as you prefer. Leave margins at default."),
        ("Paper", "Standard 20 lb paper works. Matte cardstock (65-110 lb) is nicer for writing on. The pages are mostly white space, so they are light on ink."),
        ("Binding", "Punch holes for a 6-ring or 3-ring binder, use a clipboard, or take the file to a copy shop for coil binding."),
        ("Reprint", "Print as many copies as you like for yourself. Please do not resell or share the files."),
    ]
    for head, body in lines:
        c.setFont("Sans-Bold", 11)
        c.setFillColor(SAGE)
        c.drawString(MARGIN, y - 20, head)
        c.setFont("Sans", 10)
        c.setFillColor(INK)
        words, line, ly = body.split(), "", y - 36
        for wd in words:
            if pdfmetrics.stringWidth(line + " " + wd, "Sans", 10) > w - 2 * MARGIN:
                c.drawString(MARGIN, ly, line.strip())
                line, ly = wd, ly - 14
            else:
                line += " " + wd
        c.drawString(MARGIN, ly, line.strip())
        y = ly - 14
    footer(c, w, "How to print")
    c.save()


# ---------- listing images ----------
def render_page(pdf: Path, index: int, width: int) -> Image.Image:
    doc = pdfium.PdfDocument(str(pdf))
    page = doc[index]
    scale = width / page.get_width()
    img = page.render(scale=scale).to_pil().convert("RGB")
    doc.close()
    return img


def pil_font(name: str, size: int):
    paths = {"serif-b": FONT_DIR / "LiberationSerif-Bold.ttf", "serif": FONT_DIR / "LiberationSerif-Regular.ttf",
             "sans": FONT_DIR / "LiberationSans-Regular.ttf", "sans-b": FONT_DIR / "LiberationSans-Bold.ttf"}
    return ImageFont.truetype(str(paths[name]), size)


def wrap(draw, text, font, width):
    out, line = [], ""
    for wd in text.split():
        t = f"{line} {wd}".strip()
        if draw.textlength(t, font=font) > width and line:
            out.append(line)
            line = wd
        else:
            line = t
    out.append(line)
    return out


def card(size=(2400, 1800)):
    img = Image.new("RGB", size, "#F3EFE7")
    return img, ImageDraw.Draw(img)


def paste_shadow(base, page, xy):
    sh = Image.new("RGBA", (page.width + 40, page.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([20, 24, page.width + 20, page.height + 24], fill=(0, 0, 0, 38))
    base.paste(sh, (xy[0] - 20, xy[1] - 20), sh)
    base.paste(page, xy)
    ImageDraw.Draw(base).rectangle([xy[0], xy[1], xy[0] + page.width, xy[1] + page.height], outline="#C9C4BA", width=2)


def text_block(d, x, y, lines, font, fill="#2B2B2B", gap=1.35):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += int(font.size * gap)
    return y


def images(out: Path, stem: str, title: str, tagline: str, inside: list[str], sample_pages: list[int], pdf: Path, details: list[str]):
    # 1 cover
    img, d = card()
    for i, idx in enumerate(sample_pages[:2]):
        pg = render_page(pdf, idx, 900)
        paste_shadow(img, pg, (1180 + i * 360, 160 + i * 140))
    d.text((140, 200), str(YEAR), font=pil_font("serif-b", 260), fill="#4F6F5B")
    y = text_block(d, 140, 520, wrap(d, title, pil_font("serif-b", 120), 1050), pil_font("serif-b", 120), gap=1.15)
    text_block(d, 140, y + 30, wrap(d, tagline, pil_font("serif", 56), 1050), pil_font("serif", 56), fill="#6B6B6B")
    d.text((140, 1560), "Printable PDF  |  US Letter + A4  |  Instant download", font=pil_font("sans-b", 44), fill="#2B2B2B")
    img.save(out / f"{stem}-1-cover.png")
    # 2 what is inside
    img, d = card()
    d.text((140, 140), "What's inside", font=pil_font("serif-b", 110), fill="#2B2B2B")
    y = 340
    for item in inside:
        d.ellipse([150, y + 18, 182, y + 50], outline="#4F6F5B", width=5)
        for ln in wrap(d, item, pil_font("sans", 58), 1000):
            d.text((220, y), ln, font=pil_font("sans", 58), fill="#2B2B2B")
            y += 80
        y += 30
    pg = render_page(pdf, sample_pages[0], 1000)
    paste_shadow(img, pg, (1260, 200))
    img.save(out / f"{stem}-2-inside.png")
    # 3 page previews
    img, d = card()
    d.text((140, 100), "A look at the pages", font=pil_font("serif-b", 100), fill="#2B2B2B")
    n = min(3, len(sample_pages))
    pw = 660
    for i, idx in enumerate(sample_pages[:3][:n]):
        pg = render_page(pdf, idx, pw)
        paste_shadow(img, pg, (140 + i * (pw + 130), 300))
    img.save(out / f"{stem}-3-pages.png")
    # 4 sizes
    img, d = card()
    d.text((140, 140), "Two sizes included", font=pil_font("serif-b", 110), fill="#2B2B2B")
    rows = ["US Letter  8.5 x 11 in  (weeks start Sunday)", "A4  210 x 297 mm  (weeks start Monday)", *details]
    y = 380
    for r in rows:
        for ln in wrap(d, r, pil_font("sans", 62), 2000):
            d.text((160, y), ln, font=pil_font("sans", 62), fill="#2B2B2B")
            y += 88
        y += 34
    img.save(out / f"{stem}-4-sizes.png")
    # 5 how to print
    img, d = card()
    d.text((140, 140), "Print at home in 3 steps", font=pil_font("serif-b", 110), fill="#2B2B2B")
    steps = [("1", "Download your PDF from your Etsy account after purchase."),
             ("2", "Print at 100% / 'Actual size' on matte paper or cardstock."),
             ("3", "Punch, bind or clip it. Print again whenever you need a fresh copy.")]
    y = 420
    for num, s in steps:
        d.ellipse([160, y - 10, 290, y + 120], outline="#4F6F5B", width=6)
        d.text((197, y + 14), num, font=pil_font("serif-b", 80), fill="#4F6F5B")
        for ln in wrap(d, s, pil_font("sans", 60), 1700):
            d.text((350, y + 10), ln, font=pil_font("sans", 60), fill="#2B2B2B")
            y += 82
        y += 120
    d.text((160, 1560), "Digital download. Nothing is shipped. For personal use.", font=pil_font("sans", 46), fill="#6B6B6B")
    img.save(out / f"{stem}-5-print.png")


PRODUCTS = {
    "weekly-planner": dict(
        fn=weekly, title="Weekly Planner Printable", tagline="One calm page per week, with room for priorities and notes.",
        inside=["53 weekly pages covering all of 2027", "Seven day boxes with writing lines", "Top 3 priorities and a notes panel on every page",
                "How-to-print guide"],
        pages="53 weekly pages.", samples=[0, 1, 25],
        details=["53 pages in each size", "Print only the weeks you need", "Black ink with one sage accent line"]),
    "goal-planner": dict(
        fn=goals, title="Goal Planner Printable", tagline="A year in view, three big goals, and a check-in every month.",
        inside=["Year-in-view and three big goals pages", "Four quarterly plans", "Twelve monthly check-ins",
                "Year-end review", "How-to-print guide"],
        pages="19 pages.", samples=[0, 1, 2],
        details=["19 pages in each size", "Start any month, not only January", "Black ink with one sage accent line"]),
    "habit-tracker": dict(
        fn=habits, title="Habit Tracker Printable", tagline="Twelve monthly pages, twelve habits, one circle a day.",
        inside=["12 monthly pages for 2027", "Track up to 12 habits per month", "Weekday letters above each date",
                "Reflection box on every page", "How-to-print guide"],
        pages="12 monthly pages.", samples=[0, 1, 5],
        details=["12 pages in each size", "Reprint a month if you start late", "Black ink with one sage accent line"]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = Path(ap.parse_args().out)
    for key, p in PRODUCTS.items():
        d = out / key
        (d / "images").mkdir(parents=True, exist_ok=True)
        files = {}
        for size in ("letter", "a4"):
            f = d / f"{YEAR}-{key}-{size}.pdf"
            p["fn"](f, size)
            files[size] = f
        guide(d / f"{YEAR}-{key}-how-to-print.pdf", f"{YEAR} {p['title']}", p["pages"])
        images(d / "images", key, p["title"], p["tagline"], p["inside"], p["samples"], files["letter"], p["details"])
        print(key, "ok")


if __name__ == "__main__":
    main()
