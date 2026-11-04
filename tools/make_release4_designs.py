"""Generate Release 4 printables (2026-11-04): kidcore vol. 2, kidcore Christmas and Hanukkah wall art,
kids Christmas coloring pages and bingo, the kids Christmas activity pack and a Secret Santa kit.

    PYTHONPATH=. python tools/make_release4_designs.py --out assets/digital/2026-11-04-release-4

Original code-drawn art only, reusing the kidcore primitives (tools/make_kidcore_designs.py): wobbled
shapes, crayon grain, no characters, no faces, no mascots, no lookalikes. Wall art carries NO design
text. Printables (PDF) carry only plain descriptive labels written for this release.

Wall art: five print-ready JPGs per design (same ratios and print QA as release 3) plus five 2400x1800
listing images. Sets: one zip per ratio. Printables: US Letter and A4 PDFs at 200 ppi plus listing images.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import zipfile
import zlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.qa.print_qa import PrintSpec, run as print_qa
from tools.make_kidcore_designs import (BLUE, CREAM, FONT, FONT_REG, GRAPE, GRN, INK, ORG, PINK, QA_SIZE_IN, RATIOS, RED,
                                        SRGB, YEL, blob, card, checker_band, circle_pts, daisy, framed, grain,
                                        listing_images, rainbow, scatter_stars, shadow_paste, squiggle, star_pts)

MINT, SKY, PLUM = "#7FD6B2", "#9CD3FF", "#3B2E6E"
XRED, XGRN, GOLD, SNOW = "#D7332B", "#1F8A4C", "#F2B632", "#FFFDF7"


def font(size, bold=True):
    return ImageFont.truetype(FONT if bold else FONT_REG, size)


# ================================================================ wall art (portrait W x H, text-free)
def d_checker_hearts(W, H, seed=61):
    img = Image.new("RGB", (W, H), PINK)
    d = ImageDraw.Draw(img)
    cell = W / 7
    for r in range(int(H / cell) + 2):
        for c in range(8):
            if (r + c) % 2 == 0:
                x0, y0 = c * cell, r * cell
                pts = [(x0, y0), (x0 + cell, y0), (x0 + cell, y0 + cell), (x0, y0 + cell)]
                d.polygon([(px + math.sin(py / H * 7) * cell * 0.2, py + math.sin(px / W * 6) * cell * 0.1)
                           for px, py in pts], fill="#FFB3D3")
    rnd = random.Random(seed)

    def heart(cx, cy, s):
        pts = []
        for k in range(120):
            t = 2 * math.pi * k / 120
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append((cx + x * s / 17, cy + y * s / 17))
        return pts
    big = W * 0.34
    blob(d, [(x + W * 0.02, y + W * 0.025) for x, y in heart(W / 2, H * 0.47, big)], INK, amp=W * 0.003, seed=seed)
    blob(d, heart(W / 2, H * 0.47, big), RED, INK, int(W * 0.012), amp=W * 0.003, seed=seed)
    blob(d, heart(W / 2 - big * 0.38, H * 0.47 - big * 0.42, big * 0.16), "#FF8A80", amp=W * 0.002, seed=seed + 1)
    for i in range(16):
        x, y = rnd.uniform(0.08, 0.92) * W, rnd.uniform(0.05, 0.95) * H
        if 0.12 < x / W < 0.88 and 0.22 < y / H < 0.74:
            continue
        s = W * rnd.uniform(0.045, 0.08)
        blob(d, heart(x, y, s), rnd.choice([RED, YEL, CREAM, GRAPE, ORG]), INK, int(W * 0.005), amp=W * 0.002, seed=seed + i)
    for y in (0.08, 0.92):
        squiggle(d, W * 0.12, H * y, W * 0.76, H * 0.01, 6, CREAM, int(W * 0.014))
    return img


def d_rocket(W, H, seed=67):
    img = Image.new("RGB", (W, H), PLUM)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(140):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), W * rnd.uniform(0.002, 0.005)
        d.ellipse([x - r, y - r, x + r, y + r], fill=CREAM)
    ow = int(W * 0.011)
    # planets
    blob(d, circle_pts(W * 0.2, H * 0.17, W * 0.11), ORG, INK, ow, amp=W * 0.003, seed=seed)
    d.arc([W * 0.04, H * 0.17 - W * 0.05, W * 0.36, H * 0.17 + W * 0.05], 160, 380, fill=YEL, width=int(W * 0.018))
    blob(d, circle_pts(W * 0.83, H * 0.8, W * 0.09), MINT, INK, ow, amp=W * 0.003, seed=seed + 1)
    blob(d, circle_pts(W * 0.82, H * 0.12, W * 0.05), PINK, INK, ow, amp=W * 0.002, seed=seed + 2)
    # rocket (generic: cone, body, two fins, round window; no logo)
    cx, top, bw, bh = W * 0.5, H * 0.2, W * 0.24, H * 0.42
    body = [(cx - bw / 2, top + bh * 0.3), (cx - bw / 2, top + bh), (cx + bw / 2, top + bh), (cx + bw / 2, top + bh * 0.3)]
    blob(d, [(cx - bw / 2 - W * 0.12, top + bh * 1.02), (cx - bw / 2, top + bh * 0.62), (cx - bw / 2, top + bh * 1.02)],
         RED, INK, ow, amp=W * 0.002, seed=seed + 3)
    blob(d, [(cx + bw / 2 + W * 0.12, top + bh * 1.02), (cx + bw / 2, top + bh * 0.62), (cx + bw / 2, top + bh * 1.02)],
         RED, INK, ow, amp=W * 0.002, seed=seed + 4)
    blob(d, body, CREAM, INK, ow, amp=W * 0.002, seed=seed + 5)
    blob(d, [(cx - bw / 2, top + bh * 0.3), (cx, top - bh * 0.08), (cx + bw / 2, top + bh * 0.3)], RED, INK, ow,
         amp=W * 0.002, seed=seed + 6)
    blob(d, circle_pts(cx, top + bh * 0.5, bw * 0.24), SKY, INK, ow, amp=W * 0.002, seed=seed + 7)
    checker_band(d, cx - bw / 2 + ow, top + bh * 0.78, cx + bw / 2 - ow, top + bh * 0.86, bw / 8, BLUE, CREAM)
    # flame
    fy = top + bh
    blob(d, [(cx - bw * 0.35, fy), (cx, fy + H * 0.2), (cx + bw * 0.35, fy)], ORG, INK, ow, amp=W * 0.004, seed=seed + 8)
    blob(d, [(cx - bw * 0.18, fy), (cx, fy + H * 0.11), (cx + bw * 0.18, fy)], YEL, amp=W * 0.003, seed=seed + 9)
    scatter_stars(d, W, H, 9, [YEL, CREAM, PINK], seed, avoid=[(0.2, 0.12, 0.8, 0.86)])
    return img


def d_flower_burst(W, H, seed=71):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    spots = [(0.5, 0.45, 0.26), (0.22, 0.18, 0.15), (0.8, 0.2, 0.13), (0.18, 0.72, 0.14), (0.82, 0.72, 0.16),
             (0.5, 0.88, 0.12), (0.5, 0.1, 0.08), (0.08, 0.45, 0.07), (0.93, 0.46, 0.07)]
    cols = [(RED, YEL), (BLUE, ORG), (GRN, PINK), (GRAPE, YEL), (ORG, BLUE), (PINK, GRN), (YEL, RED), (MINT, GRAPE),
            (SKY, RED)]
    for i, (x, y, r) in enumerate(spots):
        cx, cy, R = W * x, H * y, W * r
        petal, center = cols[i]
        n = 6
        for k in range(n):
            a = 2 * math.pi * k / n + rnd.uniform(-0.05, 0.05)
            blob(d, circle_pts(cx + R * 0.58 * math.cos(a), cy + R * 0.58 * math.sin(a), R * 0.46, 50), petal, INK,
                 int(W * 0.006), amp=R * 0.02, seed=seed + i * 10 + k)
        blob(d, circle_pts(cx, cy, R * 0.4, 50), center, INK, int(W * 0.006), amp=R * 0.02, seed=seed + i)
    return img


def d_rainbow_stack(W, H, seed=79):
    img = Image.new("RGB", (W, H), SKY)
    d = ImageDraw.Draw(img)
    palettes = [[RED, ORG, YEL, GRN], [PINK, GRAPE, BLUE, MINT], [ORG, YEL, GRN, BLUE], [GRAPE, PINK, RED, ORG]]
    rows, cols = 4, 2
    cw, rh = W / cols, H / rows
    for r in range(rows):
        for c in range(cols):
            cx, cy = cw * (c + 0.5), rh * r + rh * 0.78
            R = cw * 0.4
            pal = palettes[(r + c) % 4]
            d.pieslice([cx - R - W * 0.008, cy - R - W * 0.008, cx + R + W * 0.008, cy + R + W * 0.008], 180, 360, fill=INK)
            inner = rainbow(d, cx, cy, R, R * 0.17, pal)
            d.pieslice([cx - inner + W * 0.008, cy - inner + W * 0.008, cx + inner - W * 0.008, cy + inner - W * 0.008],
                       180, 360, fill=SKY)
            for side in (-1, 1):
                blob(d, circle_pts(cx + side * R * 0.83, cy + W * 0.005, R * 0.2), SNOW, INK, int(W * 0.005),
                     amp=W * 0.002, seed=seed + r * 7 + c * 3 + side)
    return img


def d_sunny(W, H, seed=83):
    img = Image.new("RGB", (W, H), "#FFE7A8")
    d = ImageDraw.Draw(img)
    cx, cy, R = W / 2, H * 0.42, W * 0.22
    for k in range(14):
        a = 2 * math.pi * k / 14
        pts = []
        for t in range(30):
            rr = R * 1.2 + t / 29 * R * 0.75
            off = math.sin(t / 29 * math.pi * 3) * R * 0.08
            pts.append((cx + rr * math.cos(a) - off * math.sin(a), cy + rr * math.sin(a) + off * math.cos(a)))
        d.line(pts, fill=ORG if k % 2 else RED, width=int(W * 0.03), joint="curve")
    blob(d, circle_pts(cx, cy, R), YEL, INK, int(W * 0.012), amp=W * 0.004, seed=seed)
    blob(d, circle_pts(cx - R * 0.35, cy - R * 0.35, R * 0.22), "#FFF1A6", amp=W * 0.003, seed=seed + 1)
    for i, (x, y, s) in enumerate([(0.24, 0.78, 0.2), (0.72, 0.84, 0.24), (0.5, 0.94, 0.16)]):
        cxp, cyp, cs = W * x, H * y, W * s
        puffs = [(-0.55, 0.05, 0.38), (-0.15, -0.18, 0.5), (0.3, -0.08, 0.44), (0.65, 0.08, 0.32)]
        for dx, dy, r in puffs:  # outline pass, then fill pass, so the cloud reads as one shape
            rr = r * cs + W * 0.008
            d.ellipse([cxp + dx * cs - rr, cyp + dy * cs - rr, cxp + dx * cs + rr, cyp + dy * cs + rr], fill=INK)
        d.rectangle([cxp - 0.85 * cs, cyp, cxp + 0.95 * cs, cyp + 0.3 * cs + W * 0.008], fill=INK)
        for dx, dy, r in puffs:
            rr = r * cs
            d.ellipse([cxp + dx * cs - rr, cyp + dy * cs - rr, cxp + dx * cs + rr, cyp + dy * cs + rr], fill=SNOW)
        d.rectangle([cxp - 0.85 * cs + W * 0.008, cyp, cxp + 0.95 * cs - W * 0.008, cyp + 0.3 * cs], fill=SNOW)
    for i in range(4):
        squiggle(d, W * 0.08, H * (0.07 + i * 0.025), W * 0.84, H * 0.006, 7, [GRAPE, BLUE, GRN, PINK][i], int(W * 0.009))
    return img


def d_xmas_tree(W, H, seed=89):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    cell = W / 10
    checker_band(d, 0, H * 0.82, W, H, cell, XRED, CREAM)
    ow = int(W * 0.011)
    cx = W / 2
    layers = [(0.18, 0.36, 0.2), (0.3, 0.52, 0.28), (0.44, 0.7, 0.36)]
    for i, (yt, yb, half) in enumerate(layers):
        blob(d, [(cx, H * yt), (cx + W * half, H * yb), (cx - W * half, H * yb)], [GRN, XGRN, GRN][i], INK, ow,
             amp=W * 0.004, seed=seed + i)
    d.rectangle([cx - W * 0.06, H * 0.7, cx + W * 0.06, H * 0.8], fill="#8A5A3B", outline=INK, width=ow)
    rnd = random.Random(seed)
    for k in range(18):
        t = rnd.random()
        li = rnd.randrange(3)
        yt, yb, half = layers[li]
        y = H * (yt + (yb - yt) * (0.35 + 0.6 * t))
        span = W * half * (0.35 + 0.6 * t) * 0.8
        x = cx + rnd.uniform(-span, span)
        r = W * 0.025
        blob(d, circle_pts(x, y, r, 30), rnd.choice([RED, YEL, BLUE, PINK, ORG, GRAPE]), INK, int(W * 0.004), seed=seed + k)
    blob(d, star_pts(cx, H * 0.17, W * 0.08), YEL, INK, ow, amp=W * 0.002, seed=seed + 50)
    for i, (x, y) in enumerate([(0.12, 0.1), (0.88, 0.14), (0.1, 0.55), (0.9, 0.5), (0.15, 0.32), (0.86, 0.33)]):
        blob(d, star_pts(W * x, H * y, W * 0.03), [PINK, BLUE, GRN, ORG, GOLD, GRAPE][i], INK, int(W * 0.004),
             amp=W * 0.002, seed=seed + 60 + i)
    return img


def ornament(d, x, y, r, col, band, seed, ow):
    d.rectangle([x - r * 0.25, y - r * 1.18, x + r * 0.25, y - r * 0.92], fill=GOLD, outline=INK, width=ow)
    d.arc([x - r * 0.15, y - r * 1.42, x + r * 0.15, y - r * 1.12], 180, 360, fill=INK, width=ow)
    blob(d, circle_pts(x, y, r, 60), col, INK, ow, amp=r * 0.01, seed=seed)
    d.rectangle([x - r * 0.97, y - r * 0.14, x + r * 0.97, y + r * 0.14], fill=band)
    for k in range(5):
        px = x - r * 0.6 + k * r * 0.3
        d.ellipse([px - r * 0.06, y - r * 0.06, px + r * 0.06, y + r * 0.06], fill=INK)
    d.ellipse([x - r * 0.62, y - r * 0.68, x - r * 0.34, y - r * 0.4], fill="#FFFFFF")


def d_ornaments(W, H, seed=97):
    img = Image.new("RGB", (W, H), XGRN)
    d = ImageDraw.Draw(img)
    for i in range(0, int(H), int(W / 9)):
        squiggle(d, -W * 0.05, i, W * 1.1, W * 0.008, 8, "#2BA35E", int(W * 0.006))
    cols = [RED, YEL, BLUE, PINK, ORG, GRAPE, MINT, RED, YEL]
    bands = [CREAM, RED, YEL, BLUE, CREAM, YEL, PINK, GRN, PINK]
    k = 0
    for r in range(4):
        for c in range(3):
            if k >= 12:
                break
            x = W * (0.2 + 0.3 * c) + (W * 0.05 if r % 2 else 0)
            y = H * (0.14 + 0.23 * r)
            d.line([(x, 0 if r == 0 else y - H * 0.12), (x, y - W * 0.13)], fill=CREAM, width=int(W * 0.004))
            ornament(d, x, y, W * 0.1, cols[k % 9], bands[k % 9], seed + k, int(W * 0.007))
            k += 1
    return img


def d_candy_stars(W, H, seed=101):
    img = Image.new("RGB", (W, H), SNOW)
    d = ImageDraw.Draw(img)
    stripe = W / 7
    for i in range(-12, 20):
        x0 = i * stripe
        d.polygon([(x0, 0), (x0 + stripe / 2, 0), (x0 + stripe / 2 + H * 0.6, H), (x0 + H * 0.6, H)],
                  fill=XRED if i % 2 else "#FFD1D1")
    rnd = random.Random(seed)
    for i, (x, y, r) in enumerate([(0.5, 0.46, 0.3), (0.2, 0.15, 0.1), (0.82, 0.18, 0.12), (0.18, 0.82, 0.12),
                                   (0.8, 0.84, 0.1), (0.5, 0.92, 0.06), (0.1, 0.48, 0.06), (0.9, 0.5, 0.06)]):
        col = [GOLD, GRN, YEL, BLUE, GRN, YEL, CREAM, CREAM][i]
        blob(d, star_pts(W * x + W * 0.012, H * y + W * 0.016, W * r), INK, amp=W * 0.002, seed=seed + i)
        blob(d, star_pts(W * x, H * y, W * r, rot=rnd.uniform(-100, -80)), col, INK, int(W * 0.01), amp=W * 0.002,
             seed=seed + i)
    return img


def d_ginger_house(W, H, seed=107):
    img = Image.new("RGB", (W, H), SKY)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(90):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H * 0.78), W * rnd.uniform(0.004, 0.01)
        d.ellipse([x - r, y - r, x + r, y + r], fill=SNOW)
    d.rectangle([0, H * 0.8, W, H], fill=SNOW)
    squiggle(d, 0, H * 0.8, W, H * 0.008, 6, SNOW, int(W * 0.03))
    ow = int(W * 0.011)
    cx, base, hw = W / 2, H * 0.8, W * 0.3
    wall_top = base - H * 0.26
    blob(d, [(cx - hw, base), (cx + hw, base), (cx + hw, wall_top), (cx - hw, wall_top)], "#C07A45", INK, ow,
         amp=W * 0.003, seed=seed)
    blob(d, [(cx - hw * 1.18, wall_top + W * 0.02), (cx, wall_top - H * 0.22), (cx + hw * 1.18, wall_top + W * 0.02)],
         "#9C5A2F", INK, ow, amp=W * 0.003, seed=seed + 1)
    # icing scallops along the roof edges
    for side in (-1, 1):
        for k in range(10):
            t = (k + 0.5) / 10
            x = cx + side * hw * 1.18 * (1 - t)
            y = wall_top + W * 0.02 - (H * 0.22 + W * 0.02) * t
            d.ellipse([x - W * 0.028, y - W * 0.012, x + W * 0.028, y + W * 0.03], fill=SNOW, outline=INK, width=int(W * 0.004))
    d.rectangle([cx - W * 0.07, base - H * 0.14, cx + W * 0.07, base], fill=XRED, outline=INK, width=ow)
    d.ellipse([cx + W * 0.03, base - H * 0.075, cx + W * 0.05, base - H * 0.065], fill=GOLD)
    for wx in (cx - hw * 0.62, cx + hw * 0.62):
        d.rectangle([wx - W * 0.06, wall_top + H * 0.05, wx + W * 0.06, wall_top + H * 0.13], fill=YEL, outline=INK, width=ow)
        d.line([(wx, wall_top + H * 0.05), (wx, wall_top + H * 0.13)], fill=INK, width=int(W * 0.005))
    for k in range(8):
        x = cx - hw + (k + 0.5) * hw * 2 / 8
        blob(d, circle_pts(x, wall_top + H * 0.018, W * 0.018, 24), [RED, GRN, YEL, PINK, BLUE, ORG, GRAPE, MINT][k],
             INK, int(W * 0.003), seed=seed + 10 + k)
    blob(d, circle_pts(cx, wall_top - H * 0.1, W * 0.04), PINK, INK, int(W * 0.005), seed=seed + 30)
    return img


def d_hanukkah(W, H, seed=113):
    img = Image.new("RGB", (W, H), "#1E4FA8")
    d = ImageDraw.Draw(img)
    cell = W / 10
    checker_band(d, 0, H * 0.84, W, H, cell, SNOW, SKY)
    rnd = random.Random(seed)
    for _ in range(70):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H * 0.8), W * rnd.uniform(0.003, 0.008)
        d.ellipse([x - r, y - r, x + r, y + r], fill=SKY)
    ow = int(W * 0.01)
    cx, base = W / 2, H * 0.74
    # nine-branch Hanukkah lamp: eight candles in a row, the helper candle (shamash) raised in the middle
    d.rectangle([cx - W * 0.2, base, cx + W * 0.2, base + H * 0.04], fill=GOLD, outline=INK, width=ow)
    d.rectangle([cx - W * 0.03, base - H * 0.12, cx + W * 0.03, base], fill=GOLD, outline=INK, width=ow)
    d.rectangle([cx - W * 0.42, base - H * 0.15, cx + W * 0.42, base - H * 0.12], fill=GOLD, outline=INK, width=ow)
    cols = [SNOW, SKY, PINK, MINT, YEL, SNOW, SKY, PINK, MINT]
    xs = [cx - W * 0.4 + i * W * 0.1 for i in range(9)]
    for i, x in enumerate(xs):
        raised = i == 4
        top = base - H * (0.36 if raised else 0.3)
        bottom = base - H * 0.15
        d.rectangle([x - W * 0.025, top, x + W * 0.025, bottom], fill=cols[i], outline=INK, width=int(W * 0.006))
        blob(d, [(x - W * 0.025, top), (x, top - H * 0.06), (x + W * 0.025, top)], ORG, INK, int(W * 0.004),
             amp=W * 0.002, seed=seed + i)
        blob(d, [(x - W * 0.012, top), (x, top - H * 0.035), (x + W * 0.012, top)], YEL, amp=W * 0.001, seed=seed + 20 + i)
    for i in range(3):
        squiggle(d, W * 0.1, H * (0.08 + i * 0.03), W * 0.8, H * 0.006, 7, [SNOW, GOLD, SKY][i], int(W * 0.008))
    return img


SINGLES = [  # key, title, fn, group
    ("checker-hearts", "Checker Hearts", d_checker_hearts, "vol2"),
    ("retro-rocket", "Retro Rocket", d_rocket, "vol2"),
    ("flower-burst", "Flower Burst", d_flower_burst, "vol2"),
    ("rainbow-stack", "Rainbow Stack", d_rainbow_stack, "vol2"),
    ("sunny-day", "Sunny Day", d_sunny, "vol2"),
    ("checker-christmas-tree", "Checker Christmas Tree", d_xmas_tree, "xmas"),
    ("ornament-parade", "Ornament Parade", d_ornaments, "xmas"),
    ("candy-stripe-stars", "Candy Stripe Stars", d_candy_stars, "xmas"),
    ("gingerbread-house", "Gingerbread House", d_ginger_house, "xmas"),
    ("hanukkah-lights", "Hanukkah Lights", d_hanukkah, "hanukkah"),
]
SETS = [("kidcore-vol-2-set-of-5", "vol2"), ("kidcore-christmas-set-of-4", "xmas")]


def set_cover(path, previews):
    img, d = card("#EDE3D3")
    d.rectangle([0, 1440, 2400, 1800], fill="#C9A27E")
    n = len(previews)
    h = 560 if n > 4 else 640
    pieces = [framed(p, h) for p in previews]
    if n == 5:
        spots = [(180, 90), (980, 90), (1700, 90), (580, 790), (1340, 790)]
    else:  # one row
        gap = (2400 - sum(p.width for p in pieces)) / (n + 1)
        x, spots = gap, []
        for p in pieces:
            spots.append((int(x), 420))
            x += p.width + gap
    for p, xy in zip(pieces, spots):
        shadow_paste(img, p, xy)
    img.save(path, quality=90)


# ================================================================ PDF printables (PIL pages at 200 ppi)
PAGE = {"letter": (1700, 2200), "a4": (1654, 2339)}
PPI = 200


def outline(d, pts, w, fill=SNOW):
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=INK, width=w, joint="curve")


# Line-art motifs: fn(d, cx, cy, s, w, fill) draws within roughly a 2s x 2s box. `fill` lets bingo color them.
def m_tree(d, cx, cy, s, w, f=SNOW):
    for i, (t, b, h) in enumerate([(-1.0, -0.35, 0.5), (-0.6, 0.15, 0.7), (-0.2, 0.7, 0.92)]):
        outline(d, wobble_safe([(cx, cy + t * s), (cx + h * s, cy + b * s), (cx - h * s, cy + b * s)]), w,
                f if f == SNOW else GRN)
    d.rectangle([cx - 0.15 * s, cy + 0.7 * s, cx + 0.15 * s, cy + s], fill=f if f == SNOW else "#8A5A3B", outline=INK, width=w)


def m_star(d, cx, cy, s, w, f=SNOW):
    outline(d, star_pts(cx, cy, s * 0.95), w, f if f == SNOW else GOLD)


def m_ornament(d, cx, cy, s, w, f=SNOW):
    d.rectangle([cx - 0.22 * s, cy - 0.95 * s, cx + 0.22 * s, cy - 0.72 * s], fill=f if f == SNOW else GOLD, outline=INK, width=w)
    d.ellipse([cx - 0.75 * s, cy - 0.75 * s, cx + 0.75 * s, cy + 0.75 * s], fill=f if f == SNOW else RED, outline=INK, width=w)
    d.arc([cx - 0.75 * s, cy - 0.3 * s, cx + 0.75 * s, cy + 0.3 * s], 0, 180, fill=INK, width=w)
    d.arc([cx - 0.75 * s, cy - 0.05 * s, cx + 0.75 * s, cy + 0.55 * s], 0, 180, fill=INK, width=w)


def m_stocking(d, cx, cy, s, w, f=SNOW):
    pts = [(cx - 0.35 * s, cy - 0.7 * s), (cx + 0.3 * s, cy - 0.7 * s), (cx + 0.3 * s, cy + 0.25 * s),
           (cx + 0.15 * s, cy + 0.75 * s), (cx - 0.65 * s, cy + 0.85 * s), (cx - 0.8 * s, cy + 0.5 * s),
           (cx - 0.35 * s, cy + 0.25 * s)]
    outline(d, pts, w, f if f == SNOW else RED)
    d.rectangle([cx - 0.45 * s, cy - 0.95 * s, cx + 0.4 * s, cy - 0.65 * s], fill=SNOW, outline=INK, width=w)


def m_present(d, cx, cy, s, w, f=SNOW):
    d.rectangle([cx - 0.75 * s, cy - 0.4 * s, cx + 0.75 * s, cy + 0.85 * s], fill=f if f == SNOW else BLUE, outline=INK, width=w)
    d.rectangle([cx - 0.85 * s, cy - 0.65 * s, cx + 0.85 * s, cy - 0.4 * s], fill=f if f == SNOW else BLUE, outline=INK, width=w)
    d.rectangle([cx - 0.12 * s, cy - 0.65 * s, cx + 0.12 * s, cy + 0.85 * s], fill=f if f == SNOW else YEL, outline=INK, width=w)
    d.ellipse([cx - 0.6 * s, cy - 1.0 * s, cx - 0.02 * s, cy - 0.65 * s], fill=f if f == SNOW else YEL, outline=INK, width=w)
    d.ellipse([cx + 0.02 * s, cy - 1.0 * s, cx + 0.6 * s, cy - 0.65 * s], fill=f if f == SNOW else YEL, outline=INK, width=w)


def m_candy_cane(d, cx, cy, s, w, f=SNOW):
    hx, hy, hr = cx - 0.1 * s, cy - 0.55 * s, 0.38 * s  # hook center and radius
    path = [(hx + hr, cy + 0.95 * s), (hx + hr, hy)]
    path += [(hx + hr * math.cos(math.pi * k / 24), hy - hr * math.sin(math.pi * k / 24)) for k in range(25)]
    path += [(hx - hr, hy + 0.15 * s)]
    thick = int(0.3 * s)
    d.line(path, fill=INK, width=thick + 2 * w, joint="curve")
    for px, py in (path[0], path[-1]):
        r = (thick + 2 * w) / 2
        d.ellipse([px - r, py - r, px + r, py + r], fill=INK)
    inner = SNOW if f == SNOW else RED
    d.line(path, fill=inner, width=thick, joint="curve")
    for px, py in (path[0], path[-1]):
        d.ellipse([px - thick / 2, py - thick / 2, px + thick / 2, py + thick / 2], fill=inner)
    for k in range(5):
        y = cy + 0.85 * s - k * 0.3 * s
        d.line([(hx + hr - thick / 2, y), (hx + hr + thick / 2, y - 0.14 * s)], fill=INK, width=max(2, w))


def m_bell(d, cx, cy, s, w, f=SNOW):
    pts = [(cx - 0.3 * s, cy - 0.8 * s), (cx + 0.3 * s, cy - 0.8 * s), (cx + 0.45 * s, cy - 0.2 * s),
           (cx + 0.8 * s, cy + 0.55 * s), (cx - 0.8 * s, cy + 0.55 * s), (cx - 0.45 * s, cy - 0.2 * s)]
    outline(d, pts, w, f if f == SNOW else GOLD)
    d.ellipse([cx - 0.18 * s, cy + 0.5 * s, cx + 0.18 * s, cy + 0.86 * s], fill=f if f == SNOW else ORG, outline=INK, width=w)
    d.arc([cx - 0.15 * s, cy - s, cx + 0.15 * s, cy - 0.7 * s], 180, 360, fill=INK, width=w)


def m_mitten(d, cx, cy, s, w, f=SNOW):
    pts = circle_pts(cx + 0.05 * s, cy - 0.2 * s, 0.55 * s, 40)[20:] + circle_pts(cx + 0.05 * s, cy - 0.2 * s, 0.55 * s, 40)[:1]
    body = [(cx - 0.5 * s, cy - 0.2 * s)] + pts + [(cx + 0.6 * s, cy + 0.55 * s), (cx - 0.5 * s, cy + 0.55 * s)]
    outline(d, body, w, f if f == SNOW else PINK)
    d.ellipse([cx - 0.85 * s, cy - 0.2 * s, cx - 0.35 * s, cy + 0.25 * s], fill=f if f == SNOW else PINK, outline=INK, width=w)
    d.rectangle([cx - 0.55 * s, cy + 0.55 * s, cx + 0.65 * s, cy + 0.9 * s], fill=SNOW, outline=INK, width=w)


def m_snowflake(d, cx, cy, s, w, f=SNOW):
    col = INK if f == SNOW else BLUE
    for k in range(6):
        a = math.pi / 3 * k
        ex, ey = cx + 0.9 * s * math.cos(a), cy + 0.9 * s * math.sin(a)
        d.line([(cx, cy), (ex, ey)], fill=col, width=w * 2)
        for t in (0.5, 0.75):
            bx, by = cx + t * 0.9 * s * math.cos(a), cy + t * 0.9 * s * math.sin(a)
            for da in (0.6, -0.6):
                d.line([(bx, by), (bx + 0.25 * s * math.cos(a + da), by + 0.25 * s * math.sin(a + da))], fill=col, width=w * 2)


def m_house(d, cx, cy, s, w, f=SNOW):
    d.rectangle([cx - 0.7 * s, cy - 0.1 * s, cx + 0.7 * s, cy + 0.85 * s], fill=f if f == SNOW else "#C07A45", outline=INK, width=w)
    outline(d, [(cx - 0.9 * s, cy), (cx, cy - 0.9 * s), (cx + 0.9 * s, cy)], w, f if f == SNOW else "#9C5A2F")
    d.rectangle([cx - 0.18 * s, cy + 0.35 * s, cx + 0.18 * s, cy + 0.85 * s], fill=f if f == SNOW else RED, outline=INK, width=w)
    for x in (cx - 0.45 * s, cx + 0.45 * s):
        d.rectangle([x - 0.13 * s, cy + 0.1 * s, x + 0.13 * s, cy + 0.36 * s], fill=f if f == SNOW else YEL, outline=INK, width=w)


def m_holly(d, cx, cy, s, w, f=SNOW):
    for side in (-1, 1):
        pts = []
        for k in range(9):
            t = k / 8
            x = cx + side * (0.1 + 0.8 * t) * s
            pts.append((x, cy - 0.15 * s - (0.25 * s if k % 2 else 0) * (1 if k not in (0, 8) else 0) - math.sin(t * math.pi) * 0.25 * s))
        for k in range(8, -1, -1):
            t = k / 8
            x = cx + side * (0.1 + 0.8 * t) * s
            pts.append((x, cy + 0.1 * s + (0.2 * s if k % 2 else 0) - math.sin(t * math.pi) * 0.1 * s))
        outline(d, pts, w, f if f == SNOW else GRN)
    for dx, dy in ((-0.15, 0.25), (0.15, 0.25), (0, 0.5)):
        d.ellipse([cx + dx * s - 0.17 * s, cy + dy * s - 0.17 * s, cx + dx * s + 0.17 * s, cy + dy * s + 0.17 * s],
                  fill=f if f == SNOW else RED, outline=INK, width=w)


def m_mug(d, cx, cy, s, w, f=SNOW):
    d.rectangle([cx - 0.6 * s, cy - 0.35 * s, cx + 0.45 * s, cy + 0.85 * s], fill=f if f == SNOW else RED, outline=INK, width=w)
    d.arc([cx + 0.2 * s, cy - 0.1 * s, cx + 0.85 * s, cy + 0.55 * s], 270, 90, fill=INK, width=w * 2)
    for k, x in enumerate((-0.3, 0.0, 0.25)):
        squiggle(d, cx + x * s, cy - 0.45 * s, 0.5 * s, 0.06 * s, 1.5, INK, w, angle=-math.pi / 2)


def m_cookie(d, cx, cy, s, w, f=SNOW):
    d.ellipse([cx - 0.85 * s, cy - 0.85 * s, cx + 0.85 * s, cy + 0.85 * s], fill=f if f == SNOW else "#D9A066", outline=INK, width=w)
    rnd = random.Random(int(cx * 7 + cy))
    for _ in range(7):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0.1, 0.6) * s
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([x - 0.09 * s, y - 0.09 * s, x + 0.09 * s, y + 0.09 * s], fill=INK)


def m_wreath(d, cx, cy, s, w, f=SNOW):
    d.ellipse([cx - 0.9 * s, cy - 0.9 * s, cx + 0.9 * s, cy + 0.9 * s], fill=f if f == SNOW else GRN, outline=INK, width=w)
    d.ellipse([cx - 0.45 * s, cy - 0.45 * s, cx + 0.45 * s, cy + 0.45 * s], fill=SNOW, outline=INK, width=w)
    for k in range(10):
        a = 2 * math.pi * k / 10
        x, y = cx + 0.68 * s * math.cos(a), cy + 0.68 * s * math.sin(a)
        d.ellipse([x - 0.07 * s, y - 0.07 * s, x + 0.07 * s, y + 0.07 * s], fill=INK if f == SNOW else RED)
    outline(d, [(cx - 0.35 * s, cy + 0.65 * s), (cx, cy + 0.85 * s), (cx + 0.35 * s, cy + 0.65 * s), (cx, cy + 1.0 * s)], w,
            f if f == SNOW else RED)


def m_sled(d, cx, cy, s, w, f=SNOW):
    d.rectangle([cx - 0.8 * s, cy - 0.3 * s, cx + 0.7 * s, cy + 0.1 * s], fill=f if f == SNOW else RED, outline=INK, width=w)
    d.line([(cx - 0.6 * s, cy + 0.1 * s), (cx - 0.6 * s, cy + 0.45 * s)], fill=INK, width=w)
    d.line([(cx + 0.5 * s, cy + 0.1 * s), (cx + 0.5 * s, cy + 0.45 * s)], fill=INK, width=w)
    d.line([(cx - 0.95 * s, cy + 0.45 * s), (cx + 0.75 * s, cy + 0.45 * s)], fill=INK, width=w * 2)
    d.arc([cx + 0.55 * s, cy + 0.05 * s, cx + 0.95 * s, cy + 0.45 * s], 270, 90, fill=INK, width=w * 2)


def m_hat(d, cx, cy, s, w, f=SNOW):
    outline(d, circle_pts(cx, cy + 0.2 * s, 0.75 * s, 40)[20:] + [(cx + 0.75 * s, cy + 0.2 * s)], w, f if f == SNOW else BLUE)
    d.rectangle([cx - 0.85 * s, cy + 0.2 * s, cx + 0.85 * s, cy + 0.55 * s], fill=SNOW, outline=INK, width=w)
    d.ellipse([cx - 0.22 * s, cy - 0.95 * s, cx + 0.22 * s, cy - 0.5 * s], fill=SNOW, outline=INK, width=w)


def m_snowman(d, cx, cy, s, w, f=SNOW):  # faceless on purpose (no character, no lookalike)
    d.ellipse([cx - 0.62 * s, cy + 0.05 * s, cx + 0.62 * s, cy + 1.0 * s], fill=SNOW, outline=INK, width=w)
    d.ellipse([cx - 0.42 * s, cy - 0.6 * s, cx + 0.42 * s, cy + 0.15 * s], fill=SNOW, outline=INK, width=w)
    d.rectangle([cx - 0.3 * s, cy - 1.0 * s, cx + 0.3 * s, cy - 0.62 * s], fill=INK)
    d.rectangle([cx - 0.45 * s, cy - 0.66 * s, cx + 0.45 * s, cy - 0.56 * s], fill=INK)
    d.rectangle([cx - 0.45 * s, cy - 0.02 * s, cx + 0.45 * s, cy + 0.1 * s], fill=SNOW if f == SNOW else RED, outline=INK, width=w)
    for y in (0.35, 0.6, 0.85):
        d.ellipse([cx - 0.06 * s, cy + y * s - 0.06 * s, cx + 0.06 * s, cy + y * s + 0.06 * s], fill=INK)


def m_candle(d, cx, cy, s, w, f=SNOW):
    d.rectangle([cx - 0.25 * s, cy - 0.35 * s, cx + 0.25 * s, cy + 0.85 * s], fill=f if f == SNOW else RED, outline=INK, width=w)
    outline(d, [(cx - 0.2 * s, cy - 0.45 * s), (cx, cy - 1.0 * s), (cx + 0.2 * s, cy - 0.45 * s)], w, f if f == SNOW else YEL)
    d.ellipse([cx - 0.6 * s, cy + 0.75 * s, cx + 0.6 * s, cy + 0.98 * s], fill=f if f == SNOW else GRN, outline=INK, width=w)


def m_lights(d, cx, cy, s, w, f=SNOW):
    pts = [(cx - s + 2 * s * t / 40, cy - 0.3 * s + math.sin(t / 40 * math.pi) * 0.4 * s) for t in range(41)]
    d.line(pts, fill=INK, width=w)
    cols = [RED, YEL, BLUE, GRN, PINK]
    for k in range(5):
        x, y = pts[4 + k * 8]
        d.rectangle([x - 0.08 * s, y, x + 0.08 * s, y + 0.12 * s], fill=INK)
        d.ellipse([x - 0.16 * s, y + 0.1 * s, x + 0.16 * s, y + 0.55 * s], fill=f if f == SNOW else cols[k], outline=INK, width=w)


def wobble_safe(pts):
    return pts


MOTIFS = [  # key, label, fn  (20 = bingo pool)
    ("tree", "Tree", m_tree), ("star", "Star", m_star), ("ornament", "Ornament", m_ornament),
    ("stocking", "Stocking", m_stocking), ("present", "Present", m_present), ("candy-cane", "Candy Cane", m_candy_cane),
    ("bell", "Bell", m_bell), ("mitten", "Mitten", m_mitten), ("snowflake", "Snowflake", m_snowflake),
    ("gingerbread-house", "Gingerbread House", m_house), ("holly", "Holly", m_holly), ("cocoa", "Cocoa", m_mug),
    ("cookie", "Cookie", m_cookie), ("wreath", "Wreath", m_wreath), ("sled", "Sled", m_sled),
    ("winter-hat", "Winter Hat", m_hat), ("snowman", "Snowman", m_snowman), ("candle", "Candle", m_candle),
    ("lights", "Lights", m_lights), ("placeholder", "", None),
]


def m_snow_globe(d, cx, cy, s, w, f=SNOW):
    d.ellipse([cx - 0.75 * s, cy - 0.95 * s, cx + 0.75 * s, cy + 0.55 * s], fill=SNOW if f == SNOW else SKY, outline=INK, width=w)
    d.polygon([(cx - 0.8 * s, cy + 0.95 * s), (cx + 0.8 * s, cy + 0.95 * s), (cx + 0.55 * s, cy + 0.45 * s),
               (cx - 0.55 * s, cy + 0.45 * s)], fill=SNOW if f == SNOW else RED, outline=INK)
    d.line([(cx - 0.8 * s, cy + 0.95 * s), (cx + 0.8 * s, cy + 0.95 * s), (cx + 0.55 * s, cy + 0.45 * s),
            (cx - 0.55 * s, cy + 0.45 * s), (cx - 0.8 * s, cy + 0.95 * s)], fill=INK, width=w)
    d.polygon([(cx, cy - 0.55 * s), (cx + 0.3 * s, cy + 0.2 * s), (cx - 0.3 * s, cy + 0.2 * s)],
              fill=SNOW if f == SNOW else GRN, outline=INK)
    for dx, dy in ((-0.4, -0.4), (0.35, -0.55), (0.45, -0.1), (-0.45, 0.05), (0.1, -0.75)):
        d.ellipse([cx + dx * s - 0.05 * s, cy + dy * s - 0.05 * s, cx + dx * s + 0.05 * s, cy + dy * s + 0.05 * s], fill=INK)


MOTIFS[-1] = ("snow-globe", "Snow Globe", m_snow_globe)
COLORING = ["tree", "ornament", "gingerbread-house", "stocking", "present", "snowman", "wreath", "candy-cane",
            "mitten", "cocoa", "sled", "snowflake"]


def page(size):
    w, h = PAGE[size]
    img = Image.new("RGB", (w, h), "#FFFFFF")
    return img, ImageDraw.Draw(img), w, h


def page_footer(d, w, h, text="Original design. For personal and classroom use."):
    f = font(26, False)
    d.text(((w - d.textlength(text, font=f)) / 2, h - 80), text, font=f, fill="#8A8597")


def coloring_page(key, size):
    img, d, w, h = page(size)
    fn = dict((k, f) for k, _, f in MOTIFS)[key]
    s = w * 0.3
    fn(d, w / 2, h * 0.47, s, 10)
    rnd = random.Random(zlib.crc32(key.encode()))
    for _ in range(9):
        x, y = rnd.uniform(0.08, 0.92) * w, rnd.choice([rnd.uniform(0.06, 0.16), rnd.uniform(0.8, 0.9)]) * h
        outline(d, star_pts(x, y, w * rnd.uniform(0.025, 0.04)), 6)
    border = 40
    d.rounded_rectangle([border, border, w - border, h - border], radius=40, outline=INK, width=6)
    page_footer(d, w, h)
    return img


def bingo_card(n, size, cards_seed=2026):
    img, d, w, h = page(size)
    rnd = random.Random(cards_seed * 100 + n)
    pool = MOTIFS[:]
    picks = rnd.sample(pool, 16)
    title = "Christmas Bingo"
    tf = font(110)
    d.text(((w - d.textlength(title, font=tf)) / 2, 90), title, font=tf, fill=XRED)
    sub = f"Card {n}"
    sf = font(44, False)
    d.text(((w - d.textlength(sub, font=sf)) / 2, 230), sub, font=sf, fill=INK)
    gx0, gy0 = 110, 330
    gw = w - 220
    cell = gw / 4
    colors = [RED, YEL, BLUE, GRN, PINK, ORG]
    for i, (k, lab, fn) in enumerate(picks):
        r, c = divmod(i, 4)
        x0, y0 = gx0 + c * cell, gy0 + r * cell
        d.rectangle([x0, y0, x0 + cell, y0 + cell], fill="#FFF7EC" if (r + c) % 2 == 0 else "#FFFFFF", outline=INK, width=6)
        fn(d, x0 + cell / 2, y0 + cell * 0.43, cell * 0.27, 5, colors[(i + n) % 6])
        lf = font(30)
        d.text((x0 + (cell - d.textlength(lab, font=lf)) / 2, y0 + cell * 0.8), lab, font=lf, fill=INK)
    page_footer(d, w, h)
    return img


def calling_cards(size):
    img, d, w, h = page(size)
    tf = font(70)
    t = "Bingo calling cards: cut out and draw one at a time"
    d.text(((w - d.textlength(t, font=font(46))) / 2, 90), t, font=font(46), fill=INK)
    cols, rows = 4, 5
    cw, ch = (w - 160) / cols, (h - 300) / rows
    for i, (k, lab, fn) in enumerate(MOTIFS):
        r, c = divmod(i, cols)
        x0, y0 = 80 + c * cw, 200 + r * ch
        for xx in range(int(x0), int(x0 + cw), 24):
            d.line([(xx, y0), (xx + 12, y0)], fill="#9C97AA", width=3)
        for yy in range(int(y0), int(y0 + ch), 24):
            d.line([(x0, yy), (x0, yy + 12)], fill="#9C97AA", width=3)
        fn(d, x0 + cw / 2, y0 + ch * 0.42, min(cw, ch) * 0.27, 5, [RED, YEL, BLUE, GRN, PINK][i % 5])
        lf = font(30)
        d.text((x0 + (cw - d.textlength(lab, font=lf)) / 2, y0 + ch * 0.8), lab, font=lf, fill=INK)
    page_footer(d, w, h)
    return img


def lines_block(d, x0, y0, x1, n, gap, color="#B8B3C6"):
    for i in range(n):
        y = y0 + (i + 1) * gap
        d.line([(x0, y), (x1, y)], fill=color, width=3)
    return y0 + n * gap


def headline(d, w, y, text, size=96, color=XRED):
    f = font(size)
    d.text(((w - d.textlength(text, font=f)) / 2, y), text, font=f, fill=color)


def wish_list_page(size):
    img, d, w, h = page(size)
    d.rounded_rectangle([40, 40, w - 40, h - 40], radius=40, outline=XGRN, width=10)
    headline(d, w, 110, "My Christmas Wish List")
    f = font(40, False)
    d.text((140, 270), "Name:", font=f, fill=INK)
    d.line([(300, 310), (w - 140, 310)], fill="#B8B3C6", width=3)
    y = 360
    for i in range(10):
        y += 140
        m_star(d, 175, y - 30, 32, 4, [RED, YEL, BLUE, GRN, PINK][i % 5])
        d.line([(240, y), (w - 140, y)], fill="#B8B3C6", width=3)
    for i, fn in enumerate([m_present, m_ornament, m_candy_cane]):
        fn(d, w * (0.25 + 0.25 * i), h - 200, 60, 4, [BLUE, RED, RED][i])
    page_footer(d, w, h)
    return img


def letter_page(size):
    img, d, w, h = page(size)
    d.rounded_rectangle([40, 40, w - 40, h - 40], radius=40, outline=XRED, width=10)
    headline(d, w, 110, "Dear Santa,", 110, XGRN)
    f = font(40, False)
    prompts = ["This year I am proud that I", "Something kind I did was", "I would love", "For my family I wish",
               "Love from"]
    y = 300
    for p in prompts:
        d.text((130, y), p, font=f, fill=INK)
        y = lines_block(d, 130, y + 20, w - 130, 2 if p != "Love from" else 1, 110) + 50
    for i, fn in enumerate([m_snowflake, m_stocking, m_bell]):
        fn(d, w * (0.25 + 0.25 * i), h - 190, 60, 4, [BLUE, RED, GOLD][i])
    page_footer(d, w, h)
    return img


def countdown_page(size):
    img, d, w, h = page(size)
    headline(d, w, 90, "Countdown to Christmas", 88)
    f = font(32, False)
    t = "Color one shape each day from December 1."
    d.text(((w - d.textlength(t, font=f)) / 2, 210), t, font=f, fill=INK)
    cols, rows = 4, 6
    cw, ch = (w - 160) / cols, (h - 420) / rows
    fns = [m_star, m_ornament, m_present, m_tree, m_bell, m_mitten, m_stocking, m_snowflake]
    for i in range(24):
        r, c = divmod(i, cols)
        x0, y0 = 80 + c * cw, 290 + r * ch
        fns[i % len(fns)](d, x0 + cw / 2, y0 + ch * 0.45, min(cw, ch) * 0.3, 5)
        nf = font(38)
        num = str(i + 1)
        d.text((x0 + 18, y0 + 10), num, font=nf, fill=XRED)
    page_footer(d, w, h)
    return img


def santa_kit_pages(size):
    pages = []
    img, d, w, h = page(size)
    d.rounded_rectangle([40, 40, w - 40, h - 40], radius=40, outline=XGRN, width=10)
    headline(d, w, 100, "Secret Santa: All About Me", 80)
    f = font(36, False)
    qs = ["Name", "Favorite color", "Favorite snack or treat", "Favorite drink", "Hobbies I love", "Scent I like",
          "Something I collect", "Please no (allergies or dislikes)", "Small gifts I'd enjoy", "Wish list item"]
    y = 270
    for q in qs:
        d.text((120, y), q, font=f, fill=INK)
        d.line([(120, y + 120), (w - 120, y + 120)], fill="#B8B3C6", width=3)
        y += 175
    page_footer(d, w, h, "Original design. For personal and workplace use.")
    pages.append(img)
    img, d, w, h = page(size)
    headline(d, w, 90, "Gift exchange details", 80)
    f = font(38, False)
    rows = ["Group", "Exchange date", "Time and place", "Spending limit", "Organizer", "Wrap gifts by", "Theme (optional)"]
    y = 260
    for r in rows:
        d.text((130, y), r, font=f, fill=INK)
        d.line([(560, y + 40), (w - 130, y + 40)], fill="#B8B3C6", width=3)
        y += 120
    headline(d, w, y + 40, "Name slips", 60, XGRN)
    cols, rws = 3, 5
    cw, ch = (w - 200) / cols, (h - y - 300) / rws
    for i in range(cols * rws):
        r, c = divmod(i, cols)
        x0, y0 = 100 + c * cw, y + 150 + r * ch
        d.rectangle([x0, y0, x0 + cw - 20, y0 + ch - 20], outline="#9C97AA", width=3)
        m_star(d, x0 + 50, y0 + (ch - 20) / 2, 22, 3, [RED, GOLD, GRN][i % 3])
    page_footer(d, w, h, "Original design. For personal and workplace use.")
    pages.append(img)
    img, d, w, h = page(size)
    headline(d, w, 90, "Gift tags", 80)
    cols, rws = 3, 4
    cw, ch = (w - 200) / cols, (h - 360) / rws
    fns = [m_tree, m_ornament, m_present, m_star, m_holly, m_snowflake]
    for i in range(cols * rws):
        r, c = divmod(i, cols)
        x0, y0 = 100 + c * cw, 230 + r * ch
        d.rounded_rectangle([x0, y0, x0 + cw - 30, y0 + ch - 30], radius=30, outline=INK, width=5)
        fns[i % 6](d, x0 + (cw - 30) / 2, y0 + ch * 0.28, ch * 0.13, 4, [RED, GRN, BLUE, GOLD, GRN, BLUE][i % 6])
        tf = font(30)
        d.text((x0 + 30, y0 + ch * 0.5), "To:", font=tf, fill=INK)
        d.line([(x0 + 100, y0 + ch * 0.5 + 34), (x0 + cw - 70, y0 + ch * 0.5 + 34)], fill="#B8B3C6", width=3)
        d.text((x0 + 30, y0 + ch * 0.66), "From:", font=tf, fill=INK)
        d.text((x0 + 120, y0 + ch * 0.66), "your Secret Santa", font=font(30, False), fill=XRED)
    page_footer(d, w, h, "Original design. For personal and workplace use.")
    pages.append(img)
    return pages


def save_pdf(path, pages):
    path.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(path, "PDF", resolution=PPI, save_all=True, append_images=pages[1:])


PRINTABLES = {
    # key: (title, page builder per size, list of (file suffix, builder)) ; each product gets letter + a4 PDFs
    "christmas-coloring-pages": ("Christmas Coloring Pages", lambda s: [coloring_page(k, s) for k in COLORING]),
    "christmas-bingo": ("Christmas Picture Bingo", lambda s: [bingo_card(n, s) for n in range(1, 11)] + [calling_cards(s)]),
    "secret-santa-kit": ("Secret Santa Kit", santa_kit_pages),
    # activity-pack members built separately below
}


# ================================================================ listing images for printables
def pdf_cover(path, title, sub, pages, bg="#F3EADB", accent=XRED):
    img, d = card(bg)
    previews = [p.resize((int(p.width * 1250 / p.height), 1250), Image.LANCZOS) for p in pages[:3]]
    xs = [180, 640, 1100][:len(previews)]
    for i, (p, x) in enumerate(zip(previews, xs)):
        shadow_paste(img, p, (x, 360 + i * 30 - 60))
    tf = font(110)
    d.text((140, 80), title, font=tf, fill=accent)
    d.text((140, 220), sub, font=font(56, False), fill=INK)
    img.save(path, quality=90)


def pdf_grid(path, pages, title):
    img, d = card("#FFFFFF")
    n = min(len(pages), 8)
    cols = 4 if n > 4 else n
    rows = math.ceil(n / cols)
    th = 1500 // rows - 40
    for i, p in enumerate(pages[:n]):
        r, c = divmod(i, cols)
        pv = p.resize((int(p.width * th / p.height), th), Image.LANCZOS)
        shadow_paste(img, pv, (100 + c * 570, 220 + r * (th + 40)))
    d.text((100, 70), title, font=font(84), fill=INK)
    img.save(path, quality=90)


def pdf_detail(path, page_img):
    img, d = card()
    w = page_img.width
    crop = page_img.crop((int(w * 0.05), int(page_img.height * 0.12), int(w * 0.95), int(page_img.height * 0.12 + w * 0.675)))
    img.paste(crop.resize((2400, 1800), Image.LANCZOS))
    img.save(path, quality=90)


def pdf_sizes(path, lines):
    img, d = card()
    d.text((140, 120), "What you get", font=font(110), fill=INK)
    y = 360
    for ln in lines:
        d.ellipse([150, y + 10, 200, y + 60], fill=YEL)
        d.text((240, y), ln, font=font(60, False), fill=INK)
        y += 170
    d.text((150, 1600), "Digital download. Nothing is shipped. US Letter and A4 PDFs.", font=font(46, False), fill="#6B6680")
    img.save(path, quality=90)


def pdf_how(path):
    img, d = card()
    d.text((140, 140), "How it works", font=font(110), fill=INK)
    steps = ["Buy and download the PDFs from your Etsy account.",
             "Print at home on plain paper or card stock.",
             "Print as many copies as you need for your family or class."]
    y = 420
    for i, s in enumerate(steps, 1):
        d.ellipse([160, y - 10, 290, y + 120], fill=[YEL, PINK, BLUE][i - 1])
        d.text((205, y + 14), str(i), font=font(80), fill=INK)
        d.text((350, y + 22), s, font=font(60, False), fill=INK)
        y += 300
    d.text((160, 1600), "Digital download. Nothing is shipped. For personal and classroom use.", font=font(46, False),
           fill="#6B6680")
    img.save(path, quality=90)


def printable_images(out, key, title, sub, pages, what):
    out.mkdir(parents=True, exist_ok=True)
    pdf_cover(out / f"{key}-1-cover.jpg", title, sub, pages)
    pdf_grid(out / f"{key}-2-pages.jpg", pages, "Every page included" if len(pages) <= 8 else "A look inside")
    pdf_detail(out / f"{key}-3-detail.jpg", pages[0])
    pdf_sizes(out / f"{key}-4-included.jpg", what)
    pdf_how(out / f"{key}-5-how.jpg")


# ================================================================ main
def build_wall_art(root, qa_out, quality):
    previews = {}
    for key, title, fn, group in SINGLES:
        dd = root / key
        dd.mkdir(parents=True, exist_ok=True)
        for rk, _, w, h, _ in RATIOS:
            img = grain(fn(w, h), seed=zlib.crc32(key.encode()) % 1000)
            path = dd / f"{key}-{rk}.jpg"
            img.save(path, quality=quality, dpi=(300, 300), optimize=True, subsampling=0, icc_profile=SRGB)
            rep = print_qa(path, PrintSpec(*QA_SIZE_IN[rk]))
            qa_out.append(rep.to_dict())
            if not rep.passed:
                raise SystemExit(f"print QA failed: {path}: {[c for c in rep.to_dict()['checks'] if not c['passed']]}")
        prev = Image.open(dd / f"{key}-2x3.jpg").resize((1200, 1800), Image.LANCZOS)
        previews[key] = prev
        listing_images(dd / "images", key, title, prev)
        print(key, "done", flush=True)
    for set_key, group in SETS:
        members = [k for k, _, _, g in SINGLES if g == group]
        sd = root / set_key
        (sd / "images").mkdir(parents=True, exist_ok=True)
        for rk, *_ in RATIOS:
            with zipfile.ZipFile(sd / f"{set_key}-{rk}.zip", "w", zipfile.ZIP_STORED) as z:
                for k in members:
                    z.write(root / k / f"{k}-{rk}.jpg", f"{k}-{rk}.jpg")
        set_cover(sd / "images" / f"{set_key}-1-cover.jpg", [previews[k] for k in members])
        first = members[0]
        for src, dst in (("4-sizes", "2-sizes"), ("5-how", "3-how")):
            shutil.copy(root / first / "images" / f"{first}-{src}.jpg", sd / "images" / f"{set_key}-{dst}.jpg")
        print(set_key, "done", flush=True)


def build_printables(root):
    built = {}
    for key, (title, builder) in PRINTABLES.items():
        for size in ("letter", "a4"):
            pages = builder(size)
            save_pdf(root / key / f"{key}-{size}.pdf", pages)
            if size == "letter":
                built[key] = pages
        print(key, "done", flush=True)
    ap_members = {"wish-list": lambda s: [wish_list_page(s), letter_page(s)], "countdown": lambda s: [countdown_page(s)]}
    pack = root / "kids-christmas-activity-pack"
    for size in ("letter", "a4"):
        for m, b in ap_members.items():
            save_pdf(pack / f"{m}-{size}.pdf", b(size))
    # The pack: coloring + bingo PDFs (shared files) + wish list/letter + countdown, one zip per paper size
    for size in ("letter", "a4"):
        with zipfile.ZipFile(pack / f"kids-christmas-activity-pack-{size}.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for src in (root / "christmas-coloring-pages" / f"christmas-coloring-pages-{size}.pdf",
                        root / "christmas-bingo" / f"christmas-bingo-{size}.pdf",
                        pack / f"wish-list-{size}.pdf", pack / f"countdown-{size}.pdf"):
                z.write(src, src.name)
    for size in ("letter", "a4"):
        for m in ap_members:
            (pack / f"{m}-{size}.pdf").unlink()
    pack_pages = [wish_list_page("letter"), letter_page("letter"), countdown_page("letter"),
                  built["christmas-coloring-pages"][0], built["christmas-bingo"][0], built["christmas-bingo"][-1]]
    return built, pack_pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/digital/2026-11-04-release-4")
    ap.add_argument("--quality", type=int, default=82)
    ap.add_argument("--only", choices=["wall", "printables", "all"], default="all")
    args = ap.parse_args()
    root = Path(args.out)
    if args.only in ("wall", "all"):
        qa = []
        build_wall_art(root, qa, args.quality)
        (root / "print-qa.json").write_text(json.dumps(qa, indent=1) + "\n", encoding="utf-8")
        print("print QA passed for", len(qa), "files")
    if args.only in ("printables", "all"):
        built, pack_pages = build_printables(root)
        printable_images(root / "christmas-coloring-pages" / "images", "christmas-coloring-pages",
                         "Christmas Coloring Pages", "12 big, simple pages for kids", built["christmas-coloring-pages"],
                         ["12 coloring pages, one big picture each", "US Letter and A4 PDFs", "Thick, easy lines for little hands",
                          "Print as many times as you like"])
        printable_images(root / "christmas-bingo" / "images", "christmas-bingo", "Christmas Picture Bingo",
                         "10 cards for kids who can't read yet", built["christmas-bingo"],
                         ["10 different picture bingo cards", "20 calling cards to cut out", "US Letter and A4 PDFs",
                          "Great for class parties and family night"])
        printable_images(root / "secret-santa-kit" / "images", "secret-santa-kit", "Secret Santa Kit",
                         "Questionnaire, name slips and gift tags", built["secret-santa-kit"],
                         ["All About Me questionnaire", "Exchange details and 15 name slips", "12 gift tags",
                          "US Letter and A4 PDFs"])
        printable_images(root / "kids-christmas-activity-pack" / "images", "kids-christmas-activity-pack",
                         "Kids Christmas Activity Pack", "Coloring, bingo, wish list and countdown", pack_pages,
                         ["12 coloring pages", "Picture bingo: 10 cards + calling cards", "Wish list and letter to Santa",
                          "Countdown to Christmas chart"])


if __name__ == "__main__":
    main()
