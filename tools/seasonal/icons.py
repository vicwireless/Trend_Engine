"""Original flat cut-paper icons, drawn in code (100x100 viewBox). No third-party art.

Colors come from CSS variables so one icon works in every palette:
--a primary, --b secondary, --c accent, --d dark, --p paper.
"""
A, B, C, D, P = "var(--a)", "var(--b)", "var(--c)", "var(--d)", "var(--p)"


def _svg(body: str) -> str:
    return f'<svg class="ico" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


def _c(x, y, r, f):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{f}"/>'


def _r(x, y, w, h, f, rx=0, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}" {extra}/>'


def _p(d, f, extra=""):
    return f'<path d="{d}" fill="{f}" {extra}/>'


def _l(d, s, w=5, extra=""):
    return f'<path d="{d}" fill="none" stroke="{s}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def _star(cx, cy, r, f, pts=5, inner=0.45):
    import math
    out = []
    for i in range(pts * 2):
        rr = r if i % 2 == 0 else r * inner
        a = -math.pi / 2 + i * math.pi / pts
        out.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(out)}" fill="{f}"/>'


ICONS = {
    # ---------------- Christmas / winter
    "tree": _r(44, 78, 12, 14, D, 2) + _p("M50 8 L74 40 H62 L80 62 H66 L86 82 H14 L34 62 H20 L38 40 H26 Z", A) + _star(50, 12, 9, C),
    "star": _star(50, 52, 42, C),
    "gift": _r(16, 40, 68, 46, B, 4) + _r(12, 28, 76, 16, A, 4) + _r(44, 28, 12, 58, C) + _l("M50 28 C36 6 18 18 50 28 C82 18 64 6 50 28", C, 6),
    "bell": _p("M50 14 C28 14 26 44 22 62 L14 74 H86 L78 62 C74 44 72 14 50 14 Z", C) + _c(50, 82, 8, D) + _r(44, 6, 12, 10, D, 3),
    "candy cane": _l("M40 90 V36 C40 10 76 10 76 36 V44", B, 14) + _l("M40 78 l0.1 0 M40 56 l0.1 0 M44 30 l0.1 0 M62 18 l0.1 0 M76 38 l0.1 0", P, 7),
    "snowflake": _l("M50 8 V92 M14 29 L86 71 M14 71 L86 29 M50 22 l-9 -9 M50 22 l9 -9 M50 78 l-9 9 M50 78 l9 9 M26 36 l-12 3 M26 36 l-3 -12 M74 64 l12 -3 M74 64 l3 12 M26 64 l-12 -3 M26 64 l-3 12 M74 36 l12 3 M74 36 l3 -12", A, 5),
    "stocking": _p("M36 10 H66 V58 C66 66 62 70 58 74 L46 86 C36 96 14 86 24 70 L36 58 Z", B) + _r(32, 8, 38, 16, P, 4, f'stroke="{D}" stroke-width="3"') + _c(34, 80, 7, C),
    "mitten": _p("M30 40 C30 10 70 10 70 40 V72 H30 Z", A) + _p("M30 52 C14 44 8 62 22 70 L30 72 Z", A) + _r(26, 70, 48, 16, C, 5),
    "ornament": _c(50, 58, 32, B) + _r(42, 16, 16, 12, D, 3) + _l("M50 16 V6", D, 4) + _l("M20 52 Q50 66 80 52 M22 68 Q50 80 78 68", C, 5),
    "candle": _r(38, 40, 24, 46, P, 3, f'stroke="{D}" stroke-width="3"') + _p("M50 8 C62 22 58 34 50 36 C42 34 38 22 50 8 Z", C) + _r(26, 84, 48, 8, A, 4),
    "wreath": f'<circle cx="50" cy="52" r="30" fill="none" stroke="{A}" stroke-width="18"/>' + _c(30, 30, 5, B) + _c(72, 40, 5, B) + _c(62, 78, 5, B) + _c(26, 62, 5, B) + _p("M50 14 L34 4 V24 Z M50 14 L66 4 V24 Z", C) + _c(50, 14, 5, B),
    "holly": _p("M48 52 C30 40 20 44 8 34 C14 50 10 60 20 70 C32 72 40 66 48 52 Z", A) + _p("M52 52 C70 40 80 44 92 34 C86 50 90 60 80 70 C68 72 60 66 52 52 Z", A) + _c(42, 44, 8, B) + _c(58, 44, 8, B) + _c(50, 32, 8, B),
    "gingerbread": _c(50, 24, 16, D) + _p("M30 42 H70 L88 50 V60 L68 58 V72 L74 92 H58 L50 76 L42 92 H26 L32 72 V58 L12 60 V50 Z", D) + _c(44, 22, 2.5, P) + _c(56, 22, 2.5, P) + _l("M44 29 Q50 34 56 29", P, 2.5) + _c(50, 50, 3, C) + _c(50, 62, 3, C),
    "snowman": _c(50, 70, 24, P) + _c(50, 36, 17, P) + f'<circle cx="50" cy="70" r="24" fill="none" stroke="{D}" stroke-width="3"/><circle cx="50" cy="36" r="17" fill="none" stroke="{D}" stroke-width="3"/>' + _r(36, 6, 28, 16, D, 2) + _r(30, 20, 40, 5, D, 2) + _p("M50 36 L66 40 L50 43 Z", C) + _c(44, 32, 2.5, D) + _c(56, 32, 2.5, D) + _r(34, 50, 32, 7, B, 3),
    "santa hat": _p("M18 72 C22 30 50 12 78 30 C70 34 76 56 82 72 Z", B) + _r(10, 68, 80, 18, P, 9, f'stroke="{D}" stroke-width="3"') + _c(80, 28, 10, P) + f'<circle cx="80" cy="28" r="10" fill="none" stroke="{D}" stroke-width="3"/>',
    "cookie": _c(50, 50, 38, C) + _c(36, 38, 5, D) + _c(60, 34, 4, D) + _c(64, 58, 6, D) + _c(40, 64, 4, D) + _c(50, 50, 3.5, D),
    "cocoa": _p("M18 34 H70 V70 C70 84 58 90 44 90 C30 90 18 84 18 70 Z", B) + _l("M70 44 C90 44 90 70 70 68", B, 7) + _r(22, 30, 44, 10, P, 5) + _l("M34 22 C28 14 40 12 34 4 M52 22 C46 14 58 12 52 4", D, 4),
    "light bulb": _r(40, 12, 20, 18, D, 3) + _p("M50 28 C74 34 76 66 50 92 C24 66 26 34 50 28 Z", C) + _l("M10 14 Q50 2 90 14", D, 4),
    "sled": _r(16, 40, 62, 12, B, 4) + _l("M24 52 V68 M68 52 V68 M10 70 H80 C92 70 92 54 84 52", D, 6),
    "scarf": _p("M20 22 C40 34 60 34 80 22 V42 C60 54 40 54 20 42 Z", A) + _p("M56 44 L76 40 V86 H56 Z", A) + _l("M56 62 H76 M56 74 H76 M30 30 V46 M44 36 V52", C, 5),
    "snow globe": _c(50, 44, 34, P) + f'<circle cx="50" cy="44" r="34" fill="none" stroke="{D}" stroke-width="3.5"/>' + _p("M50 26 L64 52 H36 Z", A) + _r(47, 52, 6, 8, D) + _c(34, 34, 2.5, A) + _c(68, 30, 2.5, A) + _c(62, 60, 2.5, A) + _p("M22 74 H78 L84 92 H16 Z", B),
    "bow": _p("M50 44 L14 22 V70 Z", B) + _p("M50 44 L86 22 V70 Z", B) + _p("M44 50 L30 92 L46 82 Z M56 50 L70 92 L54 82 Z", B) + _c(50, 46, 10, C),
    "card": _r(10, 26, 80, 52, P, 4, f'stroke="{D}" stroke-width="3.5"') + _l("M12 30 L50 58 L88 30", D, 3.5) + _p("M50 52 C40 40 34 56 50 66 C66 56 60 40 50 52 Z", B),
    "pinecone": _p("M50 12 C74 26 80 62 50 92 C20 62 26 26 50 12 Z", D) + _l("M34 36 L50 46 L66 36 M30 52 L50 62 L70 52 M36 68 L50 76 L64 68", C, 4),
    "moon": _p("M64 10 C34 12 18 42 32 68 C44 90 74 94 90 74 C62 80 44 50 64 10 Z", C) + _star(74, 30, 8, C) + _star(84, 52, 5, C),
    "house": _p("M50 10 L90 46 H78 V88 H22 V46 H10 Z", B) + _r(42, 60, 16, 28, D, 2) + _r(28, 50, 12, 12, C) + _r(60, 50, 12, 12, C) + _p("M50 10 L90 46 H80 L50 20 L20 46 H10 Z", P),
    "heart": _p("M50 86 C10 58 8 22 32 18 C42 16 48 24 50 30 C52 24 58 16 68 18 C92 22 90 58 50 86 Z", B),
    "reindeer": _p("M30 44 C30 30 70 30 70 44 V62 C70 86 30 86 30 62 Z", D) + _l("M36 34 C30 22 22 22 18 10 M30 22 L20 26 M64 34 C70 22 78 22 82 10 M70 22 L80 26", D, 5) + _c(42, 52, 3.5, P) + _c(58, 52, 3.5, P) + f'<ellipse cx="50" cy="72" rx="9" ry="6" fill="{P}"/>',
    "sleigh": _p("M14 30 C14 50 26 60 44 60 H84 V36 C70 36 66 48 52 48 C36 48 32 30 14 30 Z", B) + _l("M22 62 V76 M70 62 V76 M10 78 H80 C92 78 92 64 86 62", C, 5),
    "drum": _r(18, 30, 64, 46, B, 6) + f'<ellipse cx="50" cy="30" rx="32" ry="10" fill="{P}" stroke="{D}" stroke-width="3"/>' + _l("M22 44 L36 70 L50 46 L64 70 L78 44", C, 4) + _l("M30 10 L48 28 M70 10 L52 28", D, 4),
    "boot": _p("M30 10 H58 V54 C74 56 86 62 86 78 V86 H30 Z", D) + _r(26, 8, 36, 14, P, 4, f'stroke="{D}" stroke-width="3"') + _r(28, 82, 60, 8, B, 3),
    "pie": _p("M10 44 H90 L78 76 H22 Z", C) + f'<ellipse cx="50" cy="44" rx="40" ry="12" fill="{B}"/>' + _l("M30 42 l6 4 M46 38 l6 4 M62 42 l6 4", P, 3.5),
    # ---------------- Thanksgiving / fall
    "turkey": _c(22, 40, 13, B) + _c(36, 26, 13, C) + _c(54, 20, 13, A) + _c(72, 28, 13, C) + _c(84, 42, 13, B) + _c(52, 60, 26, D) + _c(52, 42, 12, D) + _c(48, 40, 2.5, P) + _c(57, 40, 2.5, P) + _p("M52 44 L58 50 L46 50 Z", C) + _l("M44 86 V94 M60 86 V94", C, 4),
    "pumpkin": f'<ellipse cx="30" cy="58" rx="20" ry="28" fill="{C}"/><ellipse cx="70" cy="58" rx="20" ry="28" fill="{C}"/><ellipse cx="50" cy="58" rx="20" ry="30" fill="{B}"/>' + _l("M50 28 C50 18 56 14 62 12", A, 6),
    "leaf": _p("M50 6 C58 20 78 18 82 34 C92 40 82 56 74 60 C72 72 58 72 52 70 L50 94 L48 70 C42 72 28 72 26 60 C18 56 8 40 18 34 C22 18 42 20 50 6 Z", B) + _l("M50 22 V70 M50 44 L34 34 M50 44 L66 34 M50 58 L36 52 M50 58 L64 52", P, 2.5),
    "acorn": _p("M26 44 H74 C74 74 58 90 50 94 C42 90 26 74 26 44 Z", C) + _p("M18 44 C18 22 82 22 82 44 Z", D) + _l("M50 24 V10", D, 5),
    "corn": _p("M50 8 C66 24 66 64 50 84 C34 64 34 24 50 8 Z", C) + _p("M50 92 C30 84 22 60 28 40 C36 56 44 70 50 92 Z M50 92 C70 84 78 60 72 40 C64 56 56 70 50 92 Z", A) + _l("M42 28 H58 M40 42 H60 M40 56 H60", P, 2.5),
    "apple": _p("M50 30 C30 16 10 34 16 60 C22 88 42 92 50 84 C58 92 78 88 84 60 C90 34 70 16 50 30 Z", B) + _l("M50 30 C50 20 54 14 60 10", D, 5) + _p("M56 20 C66 10 78 14 80 22 C70 28 60 26 56 20 Z", A),
    # ---------------- New Year
    "glass": _p("M30 10 H70 L62 52 C60 62 40 62 38 52 Z", C) + _l("M50 60 V86 M34 88 H66", D, 5) + _c(44, 24, 3, P) + _c(56, 34, 3, P) + _c(48, 42, 2.5, P),
    "clock": _c(50, 50, 40, P) + f'<circle cx="50" cy="50" r="40" fill="none" stroke="{D}" stroke-width="6"/>' + _l("M50 50 V22 M50 50 L46 26", C, 5) + _c(50, 50, 4, D) + _l("M50 14 v4 M50 82 v4 M14 50 h4 M82 50 h4", D, 4),
    "firework": _l("M50 50 V10 M50 50 V90 M50 50 H10 M50 50 H90 M50 50 L22 22 M50 50 L78 22 M50 50 L22 78 M50 50 L78 78", C, 5) + _c(50, 10, 5, B) + _c(50, 90, 5, B) + _c(10, 50, 5, B) + _c(90, 50, 5, B) + _c(22, 22, 4, A) + _c(78, 22, 4, A) + _c(22, 78, 4, A) + _c(78, 78, 4, A),
    "balloon": f'<ellipse cx="50" cy="40" rx="28" ry="34" fill="{B}"/>' + _p("M50 74 L44 82 H56 Z", B) + _l("M50 82 C44 88 56 92 50 98", D, 3),
    "party hat": _p("M50 8 L82 84 H18 Z", A) + _l("M34 46 L60 34 M26 66 L70 52 M22 80 L78 70", C, 6) + _c(50, 10, 8, B),
    "confetti": _r(16, 20, 14, 8, B, 2, 'transform="rotate(20 23 24)"') + _r(64, 16, 14, 8, A, 2, 'transform="rotate(-30 71 20)"') + _c(44, 34, 6, C) + _r(28, 60, 14, 8, C, 2, 'transform="rotate(-15 35 64)"') + _c(74, 56, 6, B) + _r(56, 74, 14, 8, A, 2, 'transform="rotate(35 63 78)"') + _c(20, 84, 5, A) + _star(50, 54, 9, C),
}


def icon(name: str) -> str:
    return _svg(ICONS[name])


XMAS_BINGO = ["tree", "star", "gift", "bell", "candy cane", "snowflake", "stocking", "mitten", "ornament", "candle",
              "wreath", "holly", "gingerbread", "snowman", "santa hat", "cookie", "cocoa", "light bulb", "sled",
              "scarf", "snow globe", "bow", "card", "pinecone", "moon", "house", "heart", "reindeer", "sleigh",
              "drum", "boot", "pie"]
