"""Generate the kidcore wall art test set (scan 2026-10-26: kidcore wall art scored 51.5, band test).

    PYTHONPATH=. python tools/make_kidcore_designs.py --out assets/digital/2026-10-26-kidcore

Original code-drawn art only: hand-wobbled shapes, puffed bubble lettering built from Liberation Sans
Bold, and a low-frequency crayon/paper grain. No characters, faces, mascots or lookalikes
(Lisa Frank, Care Bears and smiley faces are deliberately absent; see docs/ip-screen.md).

Per design: five print-ready JPGs (2x3, 3x4, 4x5, 11x14, ISO A) at 300 ppi, and five 2400x1800
listing images. The set listing is five zips, one per ratio.
"""
from __future__ import annotations

import argparse
import math
import random
import zipfile
import zlib
from pathlib import Path

import io
import json
import shutil

from PIL import Image, ImageChops, ImageCms, ImageDraw, ImageFilter, ImageFont

from src.qa.print_qa import PrintSpec, run as print_qa

Image.MAX_IMAGE_PIXELS = 400_000_000
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

CREAM, INK = "#FFF4DE", "#24203F"
RED, YEL, BLUE, GRN, ORG, PINK, GRAPE = "#E8412F", "#FFC52E", "#2E86DE", "#38AE5B", "#FF8A1E", "#FF7DB4", "#7B52D3"

SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
# Largest print size each file covers at 300 ppi (print QA checks against it).
QA_SIZE_IN = {"2x3": (20, 30), "3x4": (18, 24), "4x5": (16, 20), "11x14": (11, 14), "iso": (420 / 25.4, 594 / 25.4)}

# (key, label, width_px, height_px, print note)
RATIOS = [
    ("2x3", "2:3 ratio", 6000, 9000, "4x6, 8x12, 12x18, 16x24, 20x30 in"),
    ("3x4", "3:4 ratio", 5400, 7200, "6x8, 9x12, 12x16, 18x24 in"),
    ("4x5", "4:5 ratio", 4800, 6000, "4x5, 8x10, 16x20 in"),
    ("11x14", "11x14 in", 3300, 4200, "11x14 in"),
    ("iso", "ISO A size", 4961, 7016, "A5, A4, A3, A2"),
]


# ---------------------------------------------------------------- primitives
def wobble(points, amp, seed, closed=True):
    """Hand-drawn edge: subdivide each segment and push points off the line with smooth noise."""
    rnd = random.Random(seed)
    out = []
    n = len(points)
    for i in range(n if closed else n - 1):
        (x0, y0), (x1, y1) = points[i], points[(i + 1) % n]
        seg = max(2, int(math.hypot(x1 - x0, y1 - y0) / max(amp * 6, 1)))
        for k in range(seg):
            t = k / seg
            out.append((x0 + (x1 - x0) * t + rnd.uniform(-amp, amp), y0 + (y1 - y0) * t + rnd.uniform(-amp, amp)))
    return out


def circle_pts(cx, cy, r, n=90):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def star_pts(cx, cy, r, inner=0.48, rot=-90):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 36)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def blob(d, pts, fill, outline=INK, width=0, amp=0, seed=0):
    p = wobble(pts, amp, seed) if amp else pts
    d.polygon(p, fill=fill)
    if width:
        d.line(p + [p[0]], fill=outline, width=width, joint="curve")


def squiggle(d, x, y, length, amp, waves, color, width, angle=0.0):
    pts = []
    for i in range(60):
        t = i / 59
        px, py = t * length, math.sin(t * waves * 2 * math.pi) * amp
        ca, sa = math.cos(angle), math.sin(angle)
        pts.append((x + px * ca - py * sa, y + px * sa + py * ca))
    d.line(pts, fill=color, width=width, joint="curve")
    r = width / 2
    for px, py in (pts[0], pts[-1]):
        d.ellipse([px - r, py - r, px + r, py + r], fill=color)


def checker_band(d, x0, y0, x1, y1, cell, a, b):
    cols = int((x1 - x0) // cell) + 1
    rows = max(1, int(round((y1 - y0) / cell)))
    for r in range(rows):
        for c in range(cols):
            d.rectangle([x0 + c * cell, y0 + r * cell, x0 + (c + 1) * cell, y0 + (r + 1) * cell],
                        fill=a if (r + c) % 2 == 0 else b)


def daisy(d, cx, cy, r, petal, center, seed):
    rnd = random.Random(seed)
    for i in range(8):
        a = 2 * math.pi * i / 8 + rnd.uniform(-0.08, 0.08)
        px, py = cx + r * 0.62 * math.cos(a), cy + r * 0.62 * math.sin(a)
        blob(d, circle_pts(px, py, r * 0.42, 40), petal, amp=r * 0.02, seed=seed + i)
    blob(d, circle_pts(cx, cy, r * 0.38, 50), center, amp=r * 0.02, seed=seed + 99)


def rainbow(d, cx, cy, r, band, colors):
    for i, col in enumerate(colors):
        rr = r - i * band
        d.pieslice([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360, fill=col)
    rr = r - len(colors) * band
    return rr


def puff_text(img, text, cx, cy, max_w, max_h, fill, outline=INK, shadow=None, seed=0, tilt=0.0):
    """Bubble letters: render, dilate and round the glyph mask at 1/4 scale, upscale, re-threshold."""
    lines = text.split("\n")
    s = 4
    size = 400
    font = ImageFont.truetype(FONT, size)
    tmp = ImageDraw.Draw(Image.new("L", (10, 10)))
    widths = [tmp.textlength(ln, font=font) * 1.03 + size * 0.02 * len(ln) for ln in lines]
    lh = size * 1.02
    tw, th = max(widths), lh * len(lines)
    scale = min(max_w / (tw + size * 0.5), max_h / (th + size * 0.5))
    W, H = int((tw + size * 0.6) * scale / s), int((th + size * 0.6) * scale / s)
    fsz = max(8, int(size * scale / s))
    f = ImageFont.truetype(FONT, fsz)
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    y = (H - fsz * 1.02 * len(lines)) / 2
    rnd = random.Random(seed)
    for ln in lines:
        x = (W - md.textlength(ln, font=f)) / 2
        for ch in ln:
            dy = rnd.uniform(-0.04, 0.04) * fsz
            md.text((x, y + dy), ch, font=f, fill=255)
            x += md.textlength(ch, font=f) * 1.03 + fsz * 0.02
        y += fsz * 1.02
    if tilt:
        m = m.rotate(tilt, resample=Image.BICUBIC, expand=False)
    rad = max(1, fsz // 26)

    def rounded(mask, grow):
        g = mask.filter(ImageFilter.MaxFilter(2 * grow + 1)) if grow else mask
        return g.filter(ImageFilter.GaussianBlur(max(1, grow * 0.9)))

    body = rounded(m, rad)
    edge = rounded(m, rad * 2 + max(1, fsz // 40))
    up = lambda im: im.resize((W * s, H * s), Image.LANCZOS).point(lambda v: 255 if v > 118 else 0)
    body, edge = up(body), up(edge)
    ox, oy = int(cx - W * s / 2), int(cy - H * s / 2)
    if shadow:
        off = int(fsz * s * 0.07)
        img.paste(shadow, (ox + off, oy + off), edge)
    img.paste(outline, (ox, oy), edge)
    img.paste(fill, (ox, oy), body)
    # shine: a thin highlight offset up-left inside each letter
    hi = ImageChops.subtract(body, ImageChops.offset(body, int(fsz * s * 0.03), int(fsz * s * 0.03)))
    hi = hi.filter(ImageFilter.GaussianBlur(fsz * s * 0.004))
    img.paste("#FFFFFF", (ox, oy), hi.point(lambda v: int(v * 0.55)))


def grain(img, seed, strength=16):
    """Crayon/paper grain: low-frequency noise upscaled, so JPGs stay small."""
    w, h = img.size
    rnd = random.Random(seed)
    sw, sh = max(8, w // 6), max(8, h // 6)
    n = Image.new("L", (sw, sh))
    n.putdata([128 + int(rnd.gauss(0, 40)) for _ in range(sw * sh)])
    n = n.filter(ImageFilter.GaussianBlur(0.6)).resize((w, h), Image.BILINEAR)
    dark = Image.new("RGB", (w, h), "#000000")
    light = Image.new("RGB", (w, h), "#FFFFFF")
    img.paste(dark, (0, 0), n.point(lambda v: max(0, 128 - v) * strength // 64))
    img.paste(light, (0, 0), n.point(lambda v: max(0, v - 128) * strength // 80))
    return img


# ---------------------------------------------------------------- designs (draw on W x H, portrait)
def scatter_stars(d, W, H, n, colors, seed, avoid=None, rmin=0.018, rmax=0.04):
    rnd = random.Random(seed)
    placed = 0
    tries = 0
    while placed < n and tries < n * 40:
        tries += 1
        x, y = rnd.uniform(0.06, 0.94) * W, rnd.uniform(0.05, 0.95) * H
        if avoid and any(a[0] < x / W < a[2] and a[1] < y / H < a[3] for a in avoid):
            continue
        r = rnd.uniform(rmin, rmax) * W
        blob(d, star_pts(x, y, r, rot=rnd.uniform(-110, -70)), rnd.choice(colors), INK, int(W * 0.004),
             amp=r * 0.03, seed=seed + tries)
        placed += 1


def d_recess(W, H, seed=11):
    img = Image.new("RGB", (W, H), YEL)
    d = ImageDraw.Draw(img)
    cell = W / 12
    checker_band(d, 0, 0, W, cell * 2, cell, RED, CREAM)
    checker_band(d, 0, H - cell * 2, W, H, cell, BLUE, CREAM)
    for i, (y, col) in enumerate([(0.24, PINK), (0.78, GRN), (0.84, GRAPE)]):
        squiggle(d, W * 0.1, H * y, W * 0.8, H * 0.012, 5 + i, col, int(W * 0.018))
    scatter_stars(d, W, H, 12, [ORG, PINK, BLUE, GRN, CREAM], seed, avoid=[(0.05, 0.3, 0.95, 0.74)])
    puff_text(img, "RECESS\nFOREVER", W / 2, H * 0.51, W * 0.84, H * 0.44, RED, INK, shadow=BLUE, seed=seed, tilt=4)
    return img


def d_gold_star(W, H, seed=23):
    img = Image.new("RGB", (W, H), BLUE)
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H * 0.42
    for i in range(24):
        a0, a1 = 360 / 24 * i, 360 / 24 * (i + 0.5)
        R = math.hypot(W, H)
        d.pieslice([cx - R, cy - R, cx + R, cy + R], a0, a1, fill="#4A9BE8")
    blob(d, star_pts(cx + W * 0.015, cy + W * 0.02, W * 0.36), INK, amp=W * 0.004, seed=seed)
    blob(d, star_pts(cx, cy, W * 0.36), YEL, INK, int(W * 0.012), amp=W * 0.004, seed=seed)
    blob(d, star_pts(cx - W * 0.05, cy - W * 0.06, W * 0.1, inner=0.5), "#FFE27A", amp=W * 0.003, seed=seed + 1)
    for i, (x, y) in enumerate([(0.15, 0.1), (0.85, 0.13), (0.1, 0.62), (0.9, 0.6), (0.2, 0.92), (0.8, 0.93)]):
        blob(d, star_pts(W * x, H * y, W * 0.035), [PINK, CREAM, ORG, GRN, CREAM, PINK][i], INK, int(W * 0.004),
             amp=W * 0.002, seed=seed + 10 + i)
    puff_text(img, "YOU\nDID IT!", W / 2, H * 0.79, W * 0.86, H * 0.22, CREAM, INK, shadow=RED, seed=seed, tilt=-3)
    return img


def d_messy(W, H, seed=37):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for i in range(16):
        x, y = rnd.uniform(0.05, 0.95) * W, rnd.uniform(0.04, 0.96) * H
        if 0.3 < y / H < 0.72 and 0.1 < x / W < 0.9:
            continue
        r = rnd.uniform(0.05, 0.11) * W
        pts = [(x + r * (0.7 + 0.5 * rnd.random()) * math.cos(a), y + r * (0.7 + 0.5 * rnd.random()) * math.sin(a))
               for a in [2 * math.pi * k / 14 for k in range(14)]]
        col = rnd.choice([RED, YEL, BLUE, GRN, ORG, PINK, GRAPE])
        blob(d, pts, col, amp=r * 0.06, seed=seed + i)
        for k in range(3):
            a = rnd.uniform(0, 2 * math.pi)
            dr = r * rnd.uniform(1.2, 1.6)
            sr = r * rnd.uniform(0.1, 0.18)
            d.ellipse([x + dr * math.cos(a) - sr, y + dr * math.sin(a) - sr, x + dr * math.cos(a) + sr, y + dr * math.sin(a) + sr], fill=col)
    for i in range(5):
        squiggle(d, W * rnd.uniform(0.05, 0.4), H * rnd.choice([0.08, 0.2, 0.8, 0.9, 0.95]), W * rnd.uniform(0.3, 0.5),
                 H * 0.01, rnd.randint(3, 6), rnd.choice([INK, GRAPE, BLUE]), int(W * 0.012), angle=rnd.uniform(-0.3, 0.3))
    puff_text(img, "MAKE\nSOMETHING\nMESSY", W / 2, H * 0.51, W * 0.86, H * 0.42, GRAPE, INK, shadow=YEL, seed=seed, tilt=-2)
    return img


def d_shapes(W, H, seed=41):
    img = Image.new("RGB", (W, H), PINK)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    step = W / 9
    for r in range(int(H / step) + 1):
        for c in range(10):
            x, y = c * step + (step / 2 if r % 2 else 0), r * step
            d.ellipse([x - W * 0.012, y - W * 0.012, x + W * 0.012, y + W * 0.012], fill="#FF9CC6")
    ow = int(W * 0.011)
    base = H * 0.86
    s = W * 0.5
    d.rectangle([W * 0.08, base, W * 0.92, base + H * 0.03], fill=INK)
    blob(d, [(W / 2 - s / 2, base), (W / 2 + s / 2, base), (W / 2 + s / 2, base - s * 0.72), (W / 2 - s / 2, base - s * 0.72)],
         BLUE, INK, ow, amp=W * 0.003, seed=seed)
    y = base - s * 0.72
    blob(d, [(W / 2 - s * 0.45, y), (W / 2 + s * 0.45, y), (W / 2, y - s * 0.72)], YEL, INK, ow, amp=W * 0.003, seed=seed + 1)
    blob(d, circle_pts(W / 2, y - s * 0.72 - s * 0.2, s * 0.2), RED, INK, ow, amp=W * 0.003, seed=seed + 2)
    blob(d, [(W * 0.09, base), (W * 0.24, base), (W * 0.24, base - s * 0.3), (W * 0.09, base - s * 0.3)], GRN, INK, ow,
         amp=W * 0.003, seed=seed + 3)
    arc = [(W * 0.77 + s * 0.15 * math.cos(math.pi * k / 40), base - s * 0.15 * math.sin(math.pi * k / 40)) for k in range(41)]
    blob(d, arc, ORG, INK, ow, amp=W * 0.002, seed=seed + 4)
    for i in range(7):
        x, y2 = rnd.uniform(0.1, 0.9) * W, rnd.uniform(0.06, 0.32) * H
        blob(d, star_pts(x, y2, W * rnd.uniform(0.02, 0.035)), rnd.choice([CREAM, YEL, BLUE]), INK, int(W * 0.004),
             amp=W * 0.002, seed=seed + 20 + i)
    return img


def d_daisy_check(W, H, seed=53):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    cell = W / 8
    for r in range(int(H / cell) + 2):
        for c in range(9):
            if (r + c) % 2 == 0:
                x0, y0 = c * cell, r * cell
                pts = [(x0, y0), (x0 + cell, y0), (x0 + cell, y0 + cell), (x0, y0 + cell)]
                warped = [(px + math.sin(py / H * 6) * cell * 0.18, py + math.sin(px / W * 5) * cell * 0.12) for px, py in pts]
                d.polygon(warped, fill=GRN)
    cx, cy, R = W / 2, H * 0.62, W * 0.42
    band = R * 0.13
    d.pieslice([cx - R - W * 0.012, cy - R - W * 0.012, cx + R + W * 0.012, cy + R + W * 0.012], 180, 360, fill=INK)
    inner = rainbow(d, cx, cy, R, band, [RED, ORG, YEL, GRN, BLUE, GRAPE])
    d.pieslice([cx - inner + W * 0.012, cy - inner + W * 0.012, cx + inner - W * 0.012, cy + inner - W * 0.012], 180, 360, fill=CREAM)
    checker_band(d, cx - R - W * 0.012, cy, cx + R + W * 0.012, cy + band * 1.2, band * 0.6, PINK, CREAM)
    d.rectangle([cx - R - W * 0.012, cy - W * 0.004, cx + R + W * 0.012, cy + W * 0.004], fill=INK)
    rnd = random.Random(seed)
    for i, (x, y) in enumerate([(0.16, 0.14), (0.84, 0.12), (0.5, 0.07), (0.14, 0.86), (0.5, 0.84), (0.86, 0.88), (0.32, 0.95), (0.68, 0.96)]):
        daisy(d, W * x, H * y, W * rnd.uniform(0.07, 0.1), "#FFFFFF", YEL, seed + i * 7)
    return img


DESIGNS = [
    ("recess-forever", "Recess Forever", d_recess),
    ("you-did-it", "You Did It", d_gold_star),
    ("make-something-messy", "Make Something Messy", d_messy),
    ("happy-shapes", "Happy Shapes", d_shapes),
    ("rainbow-daisy-check", "Rainbow Daisy Checkerboard", d_daisy_check),
]


# ---------------------------------------------------------------- listing images (2400x1800)
def card(bg="#F6EFE4"):
    img = Image.new("RGB", (2400, 1800), bg)
    return img, ImageDraw.Draw(img)


def framed(art, h):
    a = art.resize((int(art.width * h / art.height), h), Image.LANCZOS)
    pad = int(h * 0.05)
    f = Image.new("RGB", (a.width + 2 * pad, a.height + 2 * pad), "#FFFFFF")
    f.paste(a, (pad, pad))
    out = Image.new("RGB", (f.width + 40, f.height + 40), "#2B2622")
    out.paste(f, (20, 20))
    return out


def shadow_paste(img, piece, xy):
    sh = Image.new("L", (piece.width + 80, piece.height + 80), 0)
    ImageDraw.Draw(sh).rectangle([40, 40, piece.width + 40, piece.height + 40], fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    img.paste("#5A4E44", (xy[0] - 20, xy[1] + 10), sh)
    img.paste(piece, xy)


def font(size, bold=True):
    return ImageFont.truetype(FONT if bold else FONT_REG, size)


def listing_images(out, key, title, preview):
    out.mkdir(parents=True, exist_ok=True)
    # 1 wall mockup
    img, d = card("#EDE3D3")
    d.rectangle([0, 1380, 2400, 1800], fill="#C9A27E")
    shadow_paste(img, framed(preview, 1100), (2400 // 2 - framed(preview, 1100).width // 2, 110))
    img.save(out / f"{key}-1-cover.jpg", quality=90)
    # 2 detail crop
    img, d = card()
    w = preview.width
    crop = preview.crop((int(w * 0.1), int(preview.height * 0.3), int(w * 0.9), int(preview.height * 0.3 + w * 0.6)))
    img.paste(crop.resize((2400, 1800), Image.LANCZOS))
    img.save(out / f"{key}-2-detail.jpg", quality=90)
    # 3 the print, flat
    img, d = card()
    a = preview.resize((int(preview.width * 1600 / preview.height), 1600), Image.LANCZOS)
    shadow_paste(img, a, (160, 100))
    d.text((1400, 300), title, font=font(96), fill=INK)
    for i, ln in enumerate(["Printable wall art", "Instant digital download", "5 print-ready JPGs, 300 ppi", "Original design"]):
        d.text((1400, 520 + i * 120), ln, font=font(64, False), fill="#4A4560")
    img.save(out / f"{key}-3-print.jpg", quality=90)
    # 4 sizes
    img, d = card()
    d.text((140, 120), "Five files, every common size", font=font(100), fill=INK)
    y = 330
    for _, label, pw, ph, note in RATIOS:
        d.text((160, y), label, font=font(66), fill=RED)
        d.text((760, y + 6), note, font=font(58, False), fill=INK)
        d.text((760, y + 86), f"{pw} x {ph} px, 300 ppi JPG", font=font(44, False), fill="#6B6680")
        y += 250
    img.save(out / f"{key}-4-sizes.jpg", quality=90)
    # 5 how it works
    img, d = card()
    d.text((140, 140), "How it works", font=font(110), fill=INK)
    steps = ["Buy and download the JPG files from your Etsy account.",
             "Print at home, at a local print shop or with an online printer.",
             "Pick the file whose ratio matches your frame. Frame not included."]
    y = 420
    for i, s in enumerate(steps, 1):
        d.ellipse([160, y - 10, 290, y + 120], fill=[YEL, PINK, BLUE][i - 1])
        d.text((205, y + 14), str(i), font=font(80), fill=INK)
        d.text((350, y + 22), s, font=font(60, False), fill=INK)
        y += 300
    d.text((160, 1600), "Digital download. Nothing is shipped. For personal use.", font=font(46, False), fill="#6B6680")
    img.save(out / f"{key}-5-how.jpg", quality=90)


def set_cover(out, previews):
    img, d = card("#EDE3D3")
    d.rectangle([0, 1440, 2400, 1800], fill="#C9A27E")
    h = 560
    pieces = [framed(p, h) for p in previews]
    xs = [180, 980, 1700]
    for i, (p, x) in enumerate(zip(pieces[:3], xs)):
        shadow_paste(img, p, (x, 90))
    for p, x in zip(pieces[3:], [580, 1340]):
        shadow_paste(img, p, (x, 790))
    img.save(out / "kidcore-set-of-5-1-cover.jpg", quality=90)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/digital/2026-10-26-kidcore")
    ap.add_argument("--quality", type=int, default=82)
    args = ap.parse_args()
    root = Path(args.out)
    previews, qa = [], []
    for key, title, fn in DESIGNS:
        dd = root / key
        dd.mkdir(parents=True, exist_ok=True)
        for rk, _, w, h, _ in RATIOS:
            img = grain(fn(w, h), seed=zlib.crc32(key.encode()) % 1000)
            path = dd / f"{key}-{rk}.jpg"
            img.save(path, quality=args.quality, dpi=(300, 300), optimize=True, subsampling=0, icc_profile=SRGB)
            rep = print_qa(path, PrintSpec(*QA_SIZE_IN[rk]))
            qa.append(rep.to_dict())
            if not rep.passed:
                raise SystemExit(f"print QA failed: {path}: {[c for c in rep.to_dict()['checks'] if not c['passed']]}")
        prev = Image.open(dd / f"{key}-2x3.jpg").resize((1200, 1800), Image.LANCZOS)
        previews.append(prev)
        listing_images(dd / "images", key, title, prev)
        print(key, "done")
    sd = root / "kidcore-set-of-5"
    (sd / "images").mkdir(parents=True, exist_ok=True)
    for rk, label, *_ in RATIOS:
        with zipfile.ZipFile(sd / f"kidcore-set-of-5-{rk}.zip", "w", zipfile.ZIP_STORED) as z:
            for key, _, _ in DESIGNS:
                z.write(root / key / f"{key}-{rk}.jpg", f"{key}-{rk}.jpg")
    set_cover(sd / "images", previews)
    first = DESIGNS[0][0]
    for src, dst in (("4-sizes", "2-sizes"), ("5-how", "3-how")):
        shutil.copy(root / first / "images" / f"{first}-{src}.jpg", sd / "images" / f"kidcore-set-of-5-{dst}.jpg")
    (root / "print-qa.json").write_text(json.dumps(qa, indent=1) + "\n", encoding="utf-8")
    print("set done; print QA passed for", len(qa), "files")


if __name__ == "__main__":
    main()
