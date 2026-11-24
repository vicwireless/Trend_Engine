"""Page templates for the seasonal printables. Each function returns the inner HTML of one or more
pages; build.py wraps them for US Letter and A4 and prints them with Chromium."""
from __future__ import annotations

import html
import random

from . import content as C
from .icons import XMAS_BINGO, icon

PALETTES = {
    "thanksgiving": {"a": "#566b3a", "b": "#b4532a", "c": "#d99a2b", "d": "#3a2c22", "p": "#fbf5e8", "label": "Thanksgiving"},
    "christmas": {"a": "#1f5a44", "b": "#b3312c", "c": "#d9a441", "d": "#2b2a28", "p": "#fbf6ea", "label": "Christmas"},
    "nye": {"a": "#1d2a4d", "b": "#a8405f", "c": "#c9982f", "d": "#1a1a24", "p": "#faf6ee", "label": "New Year's Eve"},
}
SHOP = "LMCGrows"
e = html.escape


def css(fonts_url: str) -> str:
    return f"""
@font-face {{ font-family: 'Fraunces'; src: url('{fonts_url}/fraunces-Fraunces.ttf'); font-weight: 100 900; }}
@font-face {{ font-family: 'DM Sans'; src: url('{fonts_url}/dmsans-DMSans.ttf'); font-weight: 100 1000; }}
@font-face {{ font-family: 'Caveat'; src: url('{fonts_url}/caveat-Caveat.ttf'); font-weight: 400 700; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: #fff; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font-family: 'DM Sans', sans-serif; color: var(--d); font-size: 11.5pt; line-height: 1.35; }}
.page {{ width: var(--pw); height: var(--ph); padding: 0.5in 0.55in 0.42in; position: relative; overflow: hidden;
  break-after: page; display: flex; flex-direction: column; background: #fff; }}
.frame {{ position: absolute; inset: 0.3in; border: 1.6pt solid var(--a); border-radius: 14pt; pointer-events: none; }}
.frame::after {{ content: ''; position: absolute; inset: 3.5pt; border: 0.6pt solid var(--c); border-radius: 11pt; }}
.inner {{ position: relative; flex: 1; display: flex; flex-direction: column; padding: 0.22in 0.22in 0.05in; min-height: 0; }}
.ico {{ width: 1em; height: 1em; display: inline-block; vertical-align: middle; }}
.kicker {{ font-size: 8.5pt; letter-spacing: 0.22em; text-transform: uppercase; color: var(--b); font-weight: 700; text-align: center; }}
h1 {{ font-family: 'Fraunces', serif; font-variation-settings: 'SOFT' 100, 'WONK' 1; font-weight: 800; color: var(--a);
  text-align: center; font-size: 30pt; line-height: 1.02; margin: 4pt 0 2pt; letter-spacing: -0.01em; }}
h2 {{ font-family: 'Fraunces', serif; font-weight: 700; color: var(--a); font-size: 15pt; margin: 6pt 0 3pt; }}
.sub {{ text-align: center; font-size: 11.5pt; color: var(--d); margin-bottom: 6pt; }}
.rowicons {{ text-align: center; font-size: 22pt; letter-spacing: 6pt; margin: 2pt 0 4pt; }}
.foot {{ position: relative; text-align: center; font-size: 7pt; letter-spacing: 0.12em; text-transform: uppercase; color: var(--d);
  padding-top: 3pt; }}
.body {{ flex: 1; min-height: 0; display: flex; flex-direction: column; }}
.hand {{ font-family: 'Caveat', cursive; font-weight: 700; color: var(--b); }}
/* cover */
.cover h1 {{ font-size: 46pt; margin-top: 12pt; }}
.cover ol.steps li {{ font-size: 12.5pt; padding: 4pt 0 4pt 28pt; }}
.cover ul.inside li {{ font-size: 11.5pt; padding: 3pt 0 3pt 16pt; }}
.card .lines {{ width: 100%; flex: 1; }}
.sign ol.steps {{ flex: 1; display: flex; flex-direction: column; justify-content: space-evenly; }}
.cover .big {{ text-align: center; font-size: 88pt; line-height: 1; margin: 12pt 0 8pt; letter-spacing: 10pt; }}
.cover .tag {{ text-align: center; font-family: 'Caveat', cursive; font-size: 30pt; color: var(--b); font-weight: 700; }}
.box {{ border: 1.2pt solid var(--a); border-radius: 10pt; padding: 12pt 16pt; margin: 9pt 0; background: var(--p); }}
.box h2 {{ margin-top: 0; }}
ol.steps {{ list-style: none; counter-reset: s; }}
ol.steps li {{ counter-increment: s; position: relative; padding: 5pt 0 5pt 28pt; font-size: 13.5pt; }}
ol.steps li::before {{ content: counter(s); position: absolute; left: 0; top: 2pt; width: 18pt; height: 18pt; border-radius: 50%;
  background: var(--a); color: #fff; font-weight: 700; font-size: 10pt; text-align: center; line-height: 18pt; }}
ul.inside {{ list-style: none; columns: 2; column-gap: 18pt; }}
ul.inside li {{ padding: 4pt 0 4pt 16pt; position: relative; font-size: 12.5pt; break-inside: avoid; }}
ul.inside li::before {{ content: ''; position: absolute; left: 2pt; top: 10pt; width: 7pt; height: 7pt; border-radius: 50%; background: var(--c); }}
/* quiz */
.quiz {{ flex: 1; display: grid; grid-auto-rows: 1fr; gap: 0; }}
.q {{ font-size: 12.5pt; display: flex; flex-direction: column; justify-content: center; border-bottom: 0.6pt dashed var(--a); padding: 2pt 2pt; }}
.q:last-child {{ border-bottom: 0; }}
.q b {{ color: var(--b); font-family: 'Fraunces', serif; font-size: 13pt; margin-right: 5pt; }}
.q .line {{ border-bottom: 0.8pt solid var(--d); height: 13pt; margin: 0 0 0 20pt; opacity: 0.55; }}
.names {{ display: flex; gap: 14pt; font-size: 10pt; margin: 2pt 0 4pt; }}
.names span {{ flex: 1; border-bottom: 0.8pt solid var(--d); padding-bottom: 1pt; }}
.answers {{ flex: 1; columns: 2; column-gap: 22pt; font-size: 12.5pt; }}
.answers p {{ break-inside: avoid; padding: 6pt 0; }}
.answers b {{ color: var(--b); }}
/* cards */
.cards {{ flex: 1; display: grid; grid-template-columns: 1fr 1fr; grid-auto-rows: 1fr; gap: 0; min-height: 0; }}
.card {{ border: 0.9pt dashed var(--d); display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; padding: 8pt 14pt; position: relative; }}
.card .lab {{ font-size: 8.5pt; letter-spacing: 0.2em; text-transform: uppercase; color: var(--b); font-weight: 700; margin-bottom: 4pt; }}
.card .txt {{ font-family: 'Fraunces', serif; font-weight: 600; font-size: 18pt; line-height: 1.15; color: var(--d); }}
.card .txt.small {{ font-size: 14.5pt; }}
.card .ci {{ font-size: 26pt; margin-bottom: 3pt; }}
.card .or {{ font-family: 'Caveat', cursive; color: var(--b); font-size: 15pt; font-weight: 700; line-height: 1; margin: 2pt 0; }}
.cutnote {{ text-align: center; font-size: 10pt; margin-bottom: 3pt; }}
/* pairs */
.pairs {{ flex: 1; display: grid; grid-auto-rows: 1fr; }}
.pair {{ display: grid; grid-template-columns: 1fr 14pt 28pt 14pt 1fr; align-items: center; gap: 6pt; border-bottom: 0.6pt dashed var(--a); font-size: 12pt; }}
.pair:last-child {{ border-bottom: 0; }}
.pair .l {{ text-align: right; font-weight: 600; }} .pair .r {{ font-weight: 600; }}
.pair i {{ width: 12pt; height: 12pt; border: 1.2pt solid var(--a); border-radius: 50%; display: block; }}
.pair em {{ font-family: 'Caveat', cursive; color: var(--b); font-size: 15pt; font-style: normal; text-align: center; font-weight: 700; }}
/* story */
.story p {{ font-size: 15.5pt; line-height: 1.62; margin-bottom: 12pt; }}
.story b {{ color: var(--b); font-weight: 800; letter-spacing: 0.03em; }}
/* sign */
.sign h1 {{ font-size: 50pt; }}
.sign ol.steps li {{ font-size: 20pt; line-height: 1.3; padding: 7pt 0 7pt 44pt; }}
.sign ol.steps li::before {{ width: 32pt; height: 32pt; line-height: 32pt; font-size: 17pt; top: 6pt; }}
/* number slips */
.nums {{ flex: 1; display: grid; grid-template-columns: repeat(4, 1fr); grid-auto-rows: 1fr; }}
.num {{ border: 0.9pt dashed var(--d); display: flex; align-items: center; justify-content: center; gap: 6pt;
  font-family: 'Fraunces', serif; font-weight: 800; font-size: 34pt; color: var(--a); }}
.num .ico {{ font-size: 16pt; }}
/* form */
.form {{ flex: 1; display: grid; grid-auto-rows: 1fr; }}
.field {{ display: flex; align-items: flex-end; gap: 6pt; font-size: 10.5pt; font-weight: 600; padding-bottom: 3pt; }}
.field span {{ flex: 1; border-bottom: 0.8pt solid var(--d); opacity: 0.6; height: 1pt; margin-bottom: 2pt; }}
.lines {{ flex: 1; display: grid; grid-auto-rows: 1fr; }}
.lines div {{ border-bottom: 0.8pt solid rgba(40,40,40,0.5); }}
/* bingo */
.bingo2 {{ flex: 1; display: flex; flex-direction: column; gap: 10pt; min-height: 0; }}
.bcard {{ flex: 1; min-height: 0; display: flex; flex-direction: column; border: 1.4pt solid var(--a); border-radius: 10pt; padding: 6pt 10pt 8pt; background: var(--p); }}
.bhead {{ display: grid; grid-template-columns: repeat(5, 1fr); text-align: center; font-family: 'Fraunces', serif; font-weight: 900;
  font-size: 24pt; color: var(--b); line-height: 1.1; }}
.bgrid {{ flex: 1; min-height: 0; display: grid; grid-template-columns: repeat(5, 1fr); grid-template-rows: repeat(5, 1fr); border: 1pt solid var(--d); background: #fff; }}
.bcell {{ border: 0.5pt solid var(--d); display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 6.6pt;
  text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; min-height: 0; }}
.bcell .ico {{ font-size: 38pt; margin-bottom: 2pt; }}
.bcell.free {{ background: var(--a); color: #fff; font-family: 'Fraunces', serif; font-size: 13pt; letter-spacing: 0.02em; }}
.bnum {{ text-align: right; font-size: 6.5pt; letter-spacing: 0.1em; margin-top: 2pt; }}
.calls {{ flex: 1; display: grid; grid-template-columns: repeat(4, 1fr); grid-auto-rows: 1fr; }}
.call {{ border: 0.9pt dashed var(--d); display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 10pt;
  text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em; }}
.call .ico {{ font-size: 58pt; margin-bottom: 5pt; }}
/* certificates */
.certs {{ flex: 1; display: grid; grid-template-rows: repeat(3, 1fr); gap: 9pt; min-height: 0; }}
.cert {{ border: 1.6pt solid var(--a); border-radius: 10pt; background: var(--p); position: relative; padding: 10pt 16pt; display: grid;
  grid-template-columns: 1fr 1.25fr; gap: 12pt; align-items: center; outline: 0.6pt solid var(--c); outline-offset: -5pt; }}
.cert .ct {{ font-family: 'Fraunces', serif; font-variation-settings: 'SOFT' 100, 'WONK' 1; font-weight: 800; font-size: 22pt; line-height: 1; color: var(--a); text-align: center; }}
.cert .ci {{ text-align: center; font-size: 30pt; letter-spacing: 4pt; margin-bottom: 4pt; }}
.cert .cf {{ display: grid; gap: 9pt; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700; }}
.cert .cf div {{ border-bottom: 0.8pt solid var(--d); padding-bottom: 10pt; }}
.coupons {{ flex: 1; display: grid; grid-template-columns: 1fr 1fr; grid-auto-rows: 1fr; gap: 0; }}
.coupon {{ border: 0.9pt dashed var(--d); padding: 8pt 12pt; display: flex; flex-direction: column; justify-content: center; text-align: center; }}
.coupon .k {{ font-size: 7.5pt; letter-spacing: 0.2em; text-transform: uppercase; color: var(--b); font-weight: 700; }}
.coupon .t {{ font-family: 'Fraunces', serif; font-weight: 700; font-size: 15pt; color: var(--a); line-height: 1.1; margin: 3pt 0; }}
.coupon .f {{ font-size: 8pt; display: flex; gap: 8pt; margin-top: 4pt; }} .coupon .f span {{ flex: 1; border-bottom: 0.7pt solid var(--d); text-align: left; padding-bottom: 8pt; }}
/* letters */
.letter {{ font-size: 13pt; line-height: 2.05; }}
.letter .blank {{ display: inline-block; border-bottom: 0.9pt solid var(--d); min-width: 1.6in; height: 14pt; vertical-align: baseline; }}
.letter .blank.w {{ min-width: 3.4in; }}
.reply p {{ font-family: 'Fraunces', serif; font-size: 17pt; line-height: 1.6; margin-bottom: 14pt; }}
.sig {{ font-family: 'Caveat', cursive; font-size: 40pt; color: var(--b); font-weight: 700; line-height: 1; }}
.stamp {{ width: 1.05in; height: 1.25in; border: 1.6pt dashed var(--b); border-radius: 6pt; display: flex; flex-direction: column; align-items: center;
  justify-content: center; font-size: 6.5pt; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 700; color: var(--b); }}
.stamp .ico {{ font-size: 32pt; }}
.seal {{ width: 1.5in; height: 1.5in; border-radius: 50%; border: 2pt solid var(--b); outline: 0.8pt solid var(--b); outline-offset: 3pt; display: flex; flex-direction: column;
  align-items: center; justify-content: center; text-align: center; font-size: 7pt; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 800; color: var(--b); }}
.seal .ico {{ font-size: 30pt; }}
.env {{ flex: 1; border: 1.4pt solid var(--a); border-radius: 10pt; background: var(--p); position: relative; padding: 16pt; display: flex; flex-direction: column; }}
.grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12pt; }}
.wsgrid {{ display: grid; margin: 4pt auto; border: 1.2pt solid var(--a); border-radius: 8pt; padding: 6pt; background: var(--p); }}
.wsgrid span {{ display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13pt; width: 0.36in; height: 0.36in; }}
.wordlist {{ columns: 3; font-size: 10.5pt; font-weight: 600; letter-spacing: 0.08em; margin-top: 6pt; }}
.drawbox {{ border: 1.2pt solid var(--a); border-radius: 10pt; flex: 1; position: relative; }}
.drawbox span {{ position: absolute; left: 8pt; top: 5pt; font-size: 9pt; font-weight: 700; color: var(--b); }}
.ttt {{ display: grid; grid-template-columns: repeat(3, 1fr); width: 1.8in; height: 1.8in; margin: 4pt auto; }}
.ttt i {{ border: 1.4pt solid var(--a); }}
.ttt i:nth-child(-n+3) {{ border-top: 0; }} .ttt i:nth-child(3n+1) {{ border-left: 0; }} .ttt i:nth-child(3n) {{ border-right: 0; }} .ttt i:nth-child(n+7) {{ border-bottom: 0; }}
"""


# ---------------------------------------------------------------- helpers
def page(inner: str, label: str, cls: str = "") -> str:
    return (f'<section class="page {cls}"><div class="frame"></div><div class="inner">{inner}</div>'
            f'<div class="foot">{e(label)} &nbsp;·&nbsp; {SHOP} &nbsp;·&nbsp; for personal use</div></section>')


def head(kicker: str, title: str, sub: str = "", icons: list[str] | None = None) -> str:
    ic = f'<div class="rowicons">{"".join(icon(i) for i in icons)}</div>' if icons else ""
    return (f'<div class="kicker">{e(kicker)}</div><h1>{e(title)}</h1>{ic}'
            + (f'<div class="sub">{e(sub)}</div>' if sub else ""))


def chunks(seq, n):
    return [seq[i:i + n] for i in range(0, len(seq), n)]


def cover(kicker, title, tagline, icons, steps, inside, label) -> str:
    return page(
        f'<div class="kicker" style="margin-top:6pt">{e(kicker)}</div><h1>{e(title)}</h1>'
        f'<div class="tag">{e(tagline)}</div><div class="big">{"".join(icon(i) for i in icons)}</div>'
        f'<div class="box"><h2>How to play</h2><ol class="steps">{"".join(f"<li>{e(s)}</li>" for s in steps)}</ol></div>'
        f'<div class="box"><h2>What\'s inside</h2><ul class="inside">{"".join(f"<li>{e(s)}</li>" for s in inside)}</ul></div>'
        f'<div style="flex:1"></div><div class="sub">Print on US Letter or A4. Cardstock works best for cards.</div>',
        label, "cover")


def quiz_pages(kicker, title, questions, per, label, icons) -> list[str]:
    out, n = [], 1
    for part in chunks(questions, per):
        rows = ""
        for q, _ in part:
            rows += f'<div class="q"><div><b>{n}.</b>{e(q)}</div><div class="line"></div></div>'
            n += 1
        out.append(page(head(kicker, title, "", icons)
                        + '<div class="names"><span>Name / team:</span><span>Score:</span></div>'
                        + f'<div class="quiz">{rows}</div>', label))
    return out


def answer_page(kicker, title, questions, label) -> str:
    rows = "".join(f"<p><b>{i}.</b> {e(a)}</p>" for i, (_, a) in enumerate(questions, 1))
    return page(head(kicker, title + " Answer Key", "One point for each correct answer. Highest score wins.")
                + f'<div class="answers">{rows}</div>', label)


def card_pages(kicker, title, items, label, lab="", icons=None, per=8, small=False, sub="Cut along the dashed lines.") -> list[str]:
    out = []
    for pi, part in enumerate(chunks(items, per)):
        cards = ""
        for i, it in enumerate(part):
            ic = f'<div class="ci">{icon(icons[(pi * per + i) % len(icons)])}</div>' if icons else ""
            if isinstance(it, tuple) and len(it) == 3:      # (label, text, _)
                l, t = it[0], e(it[1])
            elif isinstance(it, tuple):                      # either-or pair
                l, t = lab, f'{e(it[0])}<div class="or">or</div>{e(it[1])}'
            else:
                l, t = lab, e(it)
            cards += (f'<div class="card">{ic}' + (f'<div class="lab">{e(l)}</div>' if l else "")
                      + f'<div class="txt {"small" if small else ""}">{t}</div></div>')
        out.append(page(head(kicker, title) + f'<div class="cutnote">{e(sub)}</div><div class="cards">{cards}</div>', label))
    return out


def pairs_page(kicker, title, sub, pairs, label, icons=None) -> str:
    rows = "".join(f'<div class="pair"><span class="l">{e(a)}</span><i></i><em>or</em><i></i><span class="r">{e(b)}</span></div>'
                   for a, b in pairs)
    return page(head(kicker, title, sub, icons) + '<div class="names"><span>Name:</span></div>'
                + f'<div class="pairs">{rows}</div>', label)


def story_pages(kicker, title, sub, paras, label, icons) -> str:
    body = "".join("<p>" + e(p).replace("LEFT", "<b>LEFT</b>").replace("RIGHT", "<b>RIGHT</b>") + "</p>" for p in paras)
    return page(head(kicker, title, sub, icons) + f'<div class="body story">{body}</div>', label)


def number_pages(kicker, title, lo, hi, label, ic) -> list[str]:
    out = []
    for part in chunks(list(range(lo, hi + 1)), 20):
        out.append(page(head(kicker, title, "Cut apart, fold and draw from a bowl.")
                        + f'<div class="nums">{"".join(f"""<div class="num">{icon(ic)}{n}</div>""" for n in part)}</div>', label))
    return out


def lines(n: int) -> str:
    return f'<div class="lines">{"<div></div>" * n}</div>'


# ---------------------------------------------------------------- word search
def word_search(words: list[str], size: int = 14, seed: int = 2026) -> list[list[str]]:
    rng = random.Random(seed)
    grid = [[""] * size for _ in range(size)]
    for w in sorted(words, key=len, reverse=True):
        for _ in range(500):
            dx, dy = rng.choice([(1, 0), (0, 1), (1, 1)])
            x, y = rng.randrange(size - dx * (len(w) - 1)), rng.randrange(size - dy * (len(w) - 1))
            if all(grid[y + dy * i][x + dx * i] in ("", ch) for i, ch in enumerate(w)):
                for i, ch in enumerate(w):
                    grid[y + dy * i][x + dx * i] = ch
                break
        else:
            raise RuntimeError(f"could not place {w}")
    return [[c or rng.choice("ABCDEFGHIKLMNOPRSTUVWY") for c in row] for row in grid]


def scramble(word: str, seed: int) -> str:
    rng = random.Random(seed)
    letters = list(word)
    while "".join(letters) == word:
        rng.shuffle(letters)
    return "".join(letters)


# ---------------------------------------------------------------- bingo
def bingo_cards(n: int, seed: int = 1225) -> list[list[str]]:
    rng = random.Random(seed)
    seen, out = set(), []
    while len(out) < n:
        pick = tuple(rng.sample(XMAS_BINGO, 24))
        if pick not in seen:
            seen.add(pick)
            out.append(list(pick))
    return out


def bingo_pages(kicker, label) -> list[str]:
    out = []
    cards = bingo_cards(30)
    for pi, pair in enumerate(chunks(cards, 2)):
        html_cards = ""
        for ci, card in enumerate(pair):
            cells = card[:12] + ["FREE"] + card[12:]
            grid = "".join('<div class="bcell free">FREE</div>' if c == "FREE"
                           else f'<div class="bcell">{icon(c)}{e(c)}</div>' for c in cells)
            html_cards += (f'<div class="bcard"><div class="bhead"><span>B</span><span>I</span><span>N</span><span>G</span><span>O</span></div>'
                           f'<div class="bgrid">{grid}</div><div class="bnum">Card {pi * 2 + ci + 1} of 30</div></div>')
        out.append(page(f'<div class="kicker">{e(kicker)}</div><div class="bingo2" style="margin-top:4pt">{html_cards}</div>', label))
    return out


def calling_pages(kicker, label) -> list[str]:
    out = []
    for part in chunks(XMAS_BINGO, 16):
        out.append(page(head(kicker, "Calling Cards", "Cut apart, mix in a bowl and draw one at a time.")
                        + f'<div class="calls">{"".join(f"""<div class="call">{icon(c)}{e(c)}</div>""" for c in part)}</div>', label))
    return out


# ---------------------------------------------------------------- products
def thanksgiving_trivia():
    k, lab = "Thanksgiving Trivia", "Thanksgiving Trivia Game"
    ic = ["turkey", "pumpkin", "leaf", "pie", "acorn"]
    return [cover("Printable party game", "Thanksgiving Trivia", "30 questions for the whole table", ic[:3],
                  ["Hand a question sheet and a pen to every player or team.", "Read each question aloud, or let everyone work quietly.",
                   "Swap sheets and check them against the answer key.", "Most correct answers wins the wishbone (or first slice of pie)."],
                  ["3 question sheets (30 questions)", "Answer key", "30 cut-apart trivia cards", "Letter and A4 sizes"], lab),
            *quiz_pages(k, "Thanksgiving Trivia", C.THANKSGIVING_TRIVIA, 10, lab, ic),
            answer_page(k, "Thanksgiving Trivia", C.THANKSGIVING_TRIVIA, lab),
            *card_pages(k, "Trivia Cards", [(f"Question {i}", q, 0) for i, (q, _) in enumerate(C.THANKSGIVING_TRIVIA, 1)], lab,
                        small=True, sub="Cut apart and draw from a bowl. Answers are on the answer key.")]


def most_likely():
    k, lab = "Thanksgiving Party Game", "Who at This Table Thanksgiving Game"
    ic = ["pie", "leaf", "apple", "pumpkin", "acorn", "corn"]
    return [cover("Printable party game", "Who at This Table?", "The Thanksgiving dinner edition", ["pie", "turkey", "apple"],
                  ["Cut the cards apart and stack them face down.", "Draw a card and read it aloud: \"Who at this table would...\"",
                   "On three, everyone points at the person they'd pick.", "The person with the most fingers pointed at them keeps the card. Most cards wins."],
                  ["48 prompt cards", "Score sheet", "Blank cards for your own inside jokes", "Letter and A4 sizes"], lab),
            *card_pages(k, "Who at This Table?", C.MOST_LIKELY, lab, lab="Who at this table would", icons=ic),
            page(head(k, "Score Sheet", "Tally a point each time someone wins a card.")
                 + '<div class="form">' + "".join('<div class="field">Name<span></span>Points<span style="flex:0.4"></span></div>' for _ in range(14)) + "</div>", lab),
            *card_pages(k, "Write Your Own", [""] * 8, lab, lab="Who at this table would")]


def kids_table():
    k, lab = "Thanksgiving Kids Table", "Thanksgiving Kids Activity Pack"
    grid = word_search(C.KIDS_WORDS)
    ws = (f'<div class="wsgrid" style="grid-template-columns:repeat({len(grid)},auto)">'
          + "".join(f"<span>{c}</span>" for row in grid for c in row) + "</div>"
          + f'<div class="wordlist">{"".join(f"<div>{w}</div>" for w in sorted(C.KIDS_WORDS))}</div>')
    scr = "".join(f'<div class="field"><b style="letter-spacing:0.25em;min-width:1.7in">{scramble(w, i)}</b><span></span></div>'
                  for i, w in enumerate(C.KIDS_SCRAMBLE))
    az = "".join(f'<div class="field"><b style="color:var(--b);font-family:Fraunces;font-size:14pt;min-width:18pt">{ch}</b><span></span></div>'
                 for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    draw = "".join(f'<div class="drawbox"><span>Draw {e(d)}</span></div>' for d in C.KIDS_DRAW)
    return [cover("Printable kids activities", "Thanksgiving Kids Table", "Quiet fun while the turkey rests", ["turkey", "pumpkin", "corn"],
                  ["Print one set per child.", "Set out crayons or pencils at the kids' table.", "Let them puzzle, draw and giggle through dinner.",
                   "Read the Pick One cards aloud for the whole family."],
                  ["Word search (18 words)", "Word scramble with answer key", "Thankful A to Z", "Draw-it page", "Placemat with tic-tac-toe",
                   "10 Pick One cards", "Letter and A4 sizes"], lab),
            page(head(k, "Thanksgiving Word Search", "Words go across, down and diagonally.", ["turkey", "leaf", "pumpkin"]) + ws, lab),
            page(head(k, "Word Scramble", "Unscramble each Thanksgiving word.", ["acorn", "corn", "pie"]) + f'<div class="form">{scr}</div>', lab),
            page(head(k, "Thankful A to Z", "Write something you're thankful for that starts with each letter.")
                 + f'<div class="form" style="grid-template-columns:1fr 1fr;column-gap:18pt">{az}</div>', lab),
            page(head(k, "Draw It!", "Fill every box.") + f'<div class="body" style="display:grid;grid-template-columns:1fr 1fr;gap:8pt">{draw}</div>', lab),
            page(head(k, "My Placemat", "", ["turkey", "pumpkin", "leaf", "apple", "acorn"])
                 + '<div class="grid2"><div class="box"><h2>Tic-tac-toe</h2><div class="ttt">' + "<i></i>" * 9 + '</div><div class="ttt">' + "<i></i>" * 9 + '</div></div>'
                 + '<div class="box"><h2>Today I am thankful for</h2>' + "".join('<div class="field" style="height:26pt">&nbsp;<span></span></div>' for _ in range(7))
                 + '<h2 style="margin-top:10pt">My favorite food today</h2><div class="field" style="height:26pt">&nbsp;<span></span></div></div></div>'
                 + '<div class="drawbox" style="margin-top:8pt"><span>Draw your plate</span></div>', lab),
            *card_pages(k, "Pick One!", C.KIDS_WYR[:8], lab, lab="Which would you pick", small=True),
            *card_pages(k, "Pick One!", C.KIDS_WYR[8:] + [""] * 6, lab, lab="Which would you pick", small=True, sub="Two more, plus blanks to write your own."),
            page(head(k, "Word Scramble Answer Key") + '<div class="answers">'
                 + "".join(f"<p><b>{i}.</b> {scramble(w, i - 1)} = {w}</p>" for i, w in enumerate(C.KIDS_SCRAMBLE, 1)) + "</div>", lab)]


def christmas_trivia():
    k, lab = "Christmas Trivia", "Christmas Trivia Game"
    ic = ["tree", "candy cane", "gift", "bell", "holly"]
    return [cover("Printable party game", "Christmas Trivia", "40 questions for family, friends or the office", ic[:3],
                  ["Hand a question sheet and a pen to every player or team.", "Read each question aloud, or let everyone work quietly.",
                   "Swap sheets and check them against the answer key.", "Most correct answers wins. Tie? Closest guess to the number of ornaments on the tree."],
                  ["4 question sheets (40 questions)", "Answer key", "40 cut-apart trivia cards", "Letter and A4 sizes"], lab),
            *quiz_pages(k, "Christmas Trivia", C.CHRISTMAS_TRIVIA, 10, lab, ic),
            answer_page(k, "Christmas Trivia", C.CHRISTMAS_TRIVIA, lab),
            *card_pages(k, "Trivia Cards", [(f"Question {i}", q, 0) for i, (q, _) in enumerate(C.CHRISTMAS_TRIVIA, 1)], lab,
                        small=True, sub="Cut apart and draw from a bowl. Answers are on the answer key.")]


def left_right():
    k, lab = "Gift Exchange Game", "Christmas Left Right Game"
    return [cover("Printable gift exchange game", "The Left Right Game", "Pass the present, keep the giggles", ["gift", "bow", "stocking"],
                  ["Everyone sits in a circle holding one wrapped gift.", "One person reads the story aloud, nice and slowly.",
                   "Every time you hear LEFT, pass your gift left. Every time you hear RIGHT, pass it right.",
                   "When the story ends, the gift in your hands is yours to open."],
                  ["Family story (2 pages)", "Short story for little kids", "Rules sign for the table", "Letter and A4 sizes"], lab),
            story_pages(k, "The Night Before the Party", "Read aloud. Pass on every LEFT and RIGHT.", C.LEFT_RIGHT_STORY[:3], lab, ["gift", "tree", "cookie"]),
            story_pages(k, "The Night Before the Party", "Part two. Keep passing!", C.LEFT_RIGHT_STORY[3:], lab, ["star", "wreath", "bow"]),
            story_pages(k, "Snowy Goes to Town", "A short version for little ones.", C.LEFT_RIGHT_KIDS, lab, ["snowman", "scarf", "mitten"]),
            page(head(k, "How to Play", "", ["gift", "bow", "gift"]) + '<ol class="steps">'
                 + "".join(f"<li>{e(s)}</li>" for s in ["Sit in a circle. Everyone holds one wrapped gift.", "Listen to the story.",
                                                         "Hear LEFT? Pass your gift to the left.", "Hear RIGHT? Pass your gift to the right.",
                                                         "When the story ends, open the gift you're holding!"]) + "</ol>", lab, "sign")]


def white_elephant():
    k, lab = "Gift Exchange Kit", "White Elephant Gift Exchange Kit"
    twists = [(t, d, 0) for t, d in C.WHITE_ELEPHANT_TWISTS]
    return [cover("Printable gift exchange kit", "White Elephant", "Everything you need to run the swap", ["gift", "bow", "ornament"],
                  ["Ask every guest to bring one wrapped gift at the price you choose.", "Cut out the numbers and let everyone draw one.",
                   "Post the rules sign where everyone can see it.", "For extra chaos, shuffle in the twist cards and draw one each round."],
                  ["Rules sign", "Number slips 1 to 40", "12 twist cards", "Invitation note with price limit", "Steal tracker", "Letter and A4 sizes"], lab),
            page(head(k, "House Rules", "", ["gift", "bow", "gift"]) + '<ol class="steps">' + "".join(f"<li>{e(s)}</li>" for s in C.WHITE_ELEPHANT_RULES) + "</ol>", lab, "sign"),
            *number_pages(k, "Draw a Number", 1, 40, lab, "gift"),
            *card_pages(k, "Twist Cards", [(t, d, 0) for t, d, _ in twists[:8]], lab, small=True, icons=["gift", "bow", "star", "bell"], sub="Optional. Draw one at the start of each round."),
            *card_pages(k, "Twist Cards", [(t, d, 0) for t, d, _ in twists[8:]] + [("Your own twist", "", 0)] * 4, lab, small=True, icons=["gift", "bow", "star", "bell"], sub="Four more, plus blanks to write your own."),
            page(head(k, "You're Invited", "Fill in and hand out, or snap a photo and text it.")
                 + '<div class="certs">' + "".join(
                     '<div class="cert"><div><div class="ci">' + icon("gift") + icon("bow") + '</div><div class="ct">White Elephant Gift Swap</div></div>'
                     '<div class="cf"><div>When</div><div>Where</div><div>Bring one wrapped gift, about $</div></div></div>' for _ in range(3)) + "</div>", lab),
            page(head(k, "Steal Tracker", "A gift is frozen after its third steal. Tick a box for each steal.")
                 + '<div class="form">' + "".join('<div class="field">Gift<span></span>Steals &nbsp;☐ ☐ ☐&nbsp; Owner<span></span></div>' for _ in range(16)) + "</div>", lab)]


def secret_santa():
    k, lab = "Secret Santa Kit", "Secret Santa Kit"
    q = "".join(f'<div class="field">{e(x)}<span></span></div>' for x in C.SECRET_SANTA_QUESTIONS)
    slips = "".join('<div class="card"><div class="ci">' + icon("gift") + '</div><div class="lab">You are the Secret Santa for</div><div class="field" style="width:80%">&nbsp;<span></span></div>'
                    '<div class="lab" style="margin-top:6pt">Shh! Keep it secret.</div></div>' for _ in range(8))
    tags = "".join('<div class="card"><div class="ci">' + icon(i) + '</div><div class="lab">To</div><div class="field" style="width:80%">&nbsp;<span></span></div>'
                   '<div class="txt small" style="margin-top:6pt">From your Secret Santa</div></div>' for i in ["tree", "star", "candy cane", "bell", "holly", "stocking", "snowflake", "mitten"])
    return [cover("Printable gift exchange kit", "Secret Santa", "Sign-up to big reveal, all in one kit", ["santa hat", "gift", "star"],
                  ["Post the sign-up sheet and set a price limit and date.", "Have everyone fill in a wish-list questionnaire.",
                   "Write names on the draw slips and let each person pick one.", "Tag the gifts, then use the guess sheet for the big reveal."],
                  ["Sign-up sheet", "Wish-list questionnaire", "Name draw slips", "Gift tags", "Guess-the-giver reveal sheet", "Rules sign", "Letter and A4 sizes"], lab),
            page(head(k, "Secret Santa Sign-Up", "", ["santa hat", "gift", "santa hat"])
                 + '<div class="names"><span>Price limit: $</span><span>Exchange date:</span></div>'
                 + '<div class="form">' + "".join(f'<div class="field"><b style="color:var(--b);min-width:18pt">{i}.</b><span></span></div>' for i in range(1, 21)) + "</div>", lab),
            page(head(k, "My Wish List", "Help your Secret Santa out. Fill this in and hand it back.") + f'<div class="form">{q}</div>', lab),
            page(head(k, "Name Draw Slips") + f'<div class="cutnote">Write one name on each slip, fold, and draw.</div><div class="cards">{slips}</div>', lab),
            page(head(k, "Gift Tags") + f'<div class="cutnote">Cut out and tape to each gift.</div><div class="cards">{tags}</div>', lab),
            page(head(k, "Guess Your Secret Santa", "Before the reveal, everyone writes a guess. Most correct guesses wins.")
                 + '<div class="form">' + "".join('<div class="field">Gift for<span></span>I think it was<span></span></div>' for _ in range(16)) + "</div>", lab),
            page(head(k, "How It Works", "", ["gift", "star", "gift"]) + '<ol class="steps">'
                 + "".join(f"<li>{e(s)}</li>" for s in ["Draw a name. Keep it secret!", "Read their wish list.", "Buy or make one gift within the price limit.",
                                                         "Add a tag: To them, from their Secret Santa.", "At the party, guess which person had your name."]) + "</ol>", lab, "sign")]


def santa_letter():
    k, lab = "Letter to Santa Kit", "Letter to Santa Kit"
    return [cover("Printable kids kit", "Letter to Santa", "Write it, mail it, get a reply", ["card", "santa hat", "star"],
                  ["Help your child fill in the letter or write their own.", "Fold the envelope page, tuck the letter inside and 'mail' it.",
                   "Fill in the reply letter and the Nice List certificate after bedtime.", "Leave them by the tree or in the mailbox for a morning surprise."],
                  ["Fill-in letter to Santa", "Blank lined letter", "Wish list", "Envelope to cut and fold", "Reply letter from Santa", "Nice List certificate", "Letter and A4 sizes"], lab),
            page(head(k, "Dear Santa,", "", ["star", "tree", "star"]) + '<div class="body letter">'
                 'My name is <span class="blank w"></span> and I am <span class="blank" style="min-width:0.7in"></span> years old.<br>'
                 'This year I have been &nbsp;☐ very good &nbsp;☐ mostly good &nbsp;☐ trying my best.<br>'
                 'The kindest thing I did this year was <span class="blank w"></span><br><span class="blank w" style="min-width:6in"></span><br>'
                 'For Christmas I would really love <span class="blank w"></span><br><span class="blank w" style="min-width:6in"></span><br>'
                 'I would also like to give something to <span class="blank w"></span><br>'
                 'My question for you is <span class="blank w"></span><br><span class="blank w" style="min-width:6in"></span><br>'
                 'Please say hello to the reindeer!<br>Love, <span class="blank w"></span></div>', lab),
            page(head(k, "Dear Santa,", "", ["snowflake", "gift", "snowflake"]) + lines(16)
                 + '<div class="field" style="margin-top:12pt">Love,<span></span></div>', lab),
            page(head(k, "My Christmas Wish List", "", ["gift", "stocking", "gift"]) + '<div class="grid2">'
                 + "".join(f'<div class="box"><h2>{t}</h2>' + "".join('<div class="field" style="height:24pt">&nbsp;<span></span></div>' for _ in range(6)) + "</div>"
                           for t in ["Something I want", "Something I need", "Something to wear", "Something to read"])
                 + "</div><div class='box'><h2>Something I want to give</h2>" + "".join('<div class="field" style="height:24pt">&nbsp;<span></span></div>' for _ in range(3)) + "</div>", lab),
            page(head(k, "Envelope", "Cut out the panel, fold in thirds around your letter and seal with tape or a sticker.")
                 + '<div class="env"><div style="display:flex;justify-content:space-between"><div style="font-size:10pt"><b>From:</b><br><br>'
                 + '<div class="field" style="width:2.6in">&nbsp;<span></span></div><div class="field" style="width:2.6in;height:22pt">&nbsp;<span></span></div></div>'
                 + f'<div class="stamp">{icon("reindeer")}North Pole<br>Air Mail</div></div>'
                 + '<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center">'
                 + '<div class="hand" style="font-size:44pt;line-height:1">To: Santa Claus</div><div style="font-family:Fraunces;font-size:20pt;font-weight:600;margin-top:6pt">The Workshop, North Pole</div>'
                 + f'<div class="rowicons" style="font-size:30pt;margin-top:10pt">{icon("snowflake")}{icon("tree")}{icon("snowflake")}</div></div>'
                 + '<div style="text-align:center;font-size:8pt;letter-spacing:0.2em;text-transform:uppercase;font-weight:700;color:var(--b)">Special delivery · Do not open until Christmas</div></div>', lab),
            page('<div class="kicker">From the desk of Santa Claus · The Workshop, North Pole</div>'
                 + f'<div class="rowicons" style="font-size:30pt;margin-top:8pt">{icon("holly")}{icon("santa hat")}{icon("holly")}</div>'
                 + '<div class="body reply"><p style="margin-top:8pt">Dear <span class="blank" style="display:inline-block;border-bottom:0.9pt solid var(--d);min-width:3in;height:16pt"></span>,</p>'
                 + "".join(f"<p>{e(p)}</p>" for p in C.SANTA_REPLY)
                 + '<p>P.S. <span style="display:inline-block;border-bottom:0.9pt solid var(--d);min-width:5in;height:16pt"></span></p>'
                 + '<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:auto"><div><p style="margin:0">With love and jingle bells,</p><div class="sig">Santa</div></div>'
                 + f'<div class="seal">{icon("star")}Read at the<br>North Pole</div></div></div>', lab),
            page('<div class="kicker" style="margin-top:14pt">Official Certificate</div><h1 style="font-size:54pt;margin-top:8pt">The Nice List</h1>'
                 + f'<div class="rowicons" style="font-size:44pt;margin:10pt 0">{icon("star")}{icon("tree")}{icon("star")}</div>'
                 + '<div class="sub" style="font-size:14pt">This certifies that</div><div class="field" style="height:50pt;margin:0 0.6in">&nbsp;<span></span></div>'
                 + '<div class="sub" style="font-size:14pt;margin-top:14pt">has been kind, helpful and full of good cheer,<br>and is officially on the Nice List for Christmas</div>'
                 + '<div class="field" style="height:40pt;margin:0 2.4in">&nbsp;<span></span></div><div class="sub">Year</div>'
                 + '<div style="flex:1"></div><div style="display:flex;justify-content:space-between;align-items:flex-end;padding:0 0.3in 0.2in"><div><div class="sig">Santa</div><div style="font-size:8pt;letter-spacing:0.16em;text-transform:uppercase;font-weight:700">Santa Claus, North Pole</div></div>'
                 + f'<div class="seal">{icon("reindeer")}Checked<br>twice</div></div>', lab)]


def gift_certificates():
    k, lab = "Gift Certificates", "Printable Christmas Gift Certificates"
    sets = [["tree", "star"], ["gift", "bow"], ["candy cane", "holly"], ["snowflake", "mitten"], ["bell", "wreath"], ["cocoa", "cookie"]]
    def certs(titles, icons3):
        return '<div class="certs">' + "".join(
            f'<div class="cert"><div><div class="ci">{icon(ic[0])}{icon(ic[1])}</div><div class="ct">{e(t)}</div></div>'
            '<div class="cf"><div>To</div><div>From</div><div>Good for</div></div></div>' for t, ic in zip(titles, icons3)) + "</div>"
    T = C.GIFT_CERT_TYPES
    coupons = "".join(f'<div class="coupon"><div class="k">This coupon is good for</div><div class="t">{e(t)}</div>'
                      '<div class="f"><span>To</span><span>From</span></div></div>' for t in C.COUPONS)
    blank = "".join('<div class="coupon"><div class="k">This coupon is good for</div><div class="field" style="height:26pt">&nbsp;<span></span></div>'
                    '<div class="f"><span>To</span><span>From</span></div></div>' for _ in range(12))
    return [cover("Printable last-minute gift", "Gift Certificates", "Fill in, cut out, give", ["gift", "star", "bow"],
                  ["Print the page you like on cardstock.", "Write in who it's for and what it's good for: a dinner, a day trip, lessons, anything.",
                   "Cut along the edges.", "Slip it in a card, a stocking or under the tree."],
                  ["18 gift certificates in 6 styles", "12 ready-made 'good for' coupons", "12 blank coupons", "Letter and A4 sizes"], lab),
            page(head(k, "Gift Certificates") + certs(T[:3], sets[:3]), lab),
            page(head(k, "Gift Certificates") + certs(T[3:], sets[3:]), lab),
            page(head(k, "Gift Certificates") + certs(["Merry Christmas", "Merry Christmas", "Merry Christmas"], [sets[0], sets[2], sets[4]]), lab),
            page(head(k, "Gift Certificates") + certs(["Happy Holidays", "Happy Holidays", "Happy Holidays"], [sets[3], sets[1], sets[5]]), lab),
            page(head(k, "Gift Certificates") + certs(["With love", "Just for you", "Thank you"], [sets[1], sets[0], sets[3]]), lab),
            page(head(k, "Gift Certificates") + certs(["For Mom", "For Dad", "For my favorite person"], [sets[5], sets[4], sets[2]]), lab),
            page(head(k, "Coupon Book") + f'<div class="cutnote">Cut apart and staple into a booklet.</div><div class="coupons">{coupons}</div>', lab),
            page(head(k, "Blank Coupons") + f'<div class="cutnote">Write your own.</div><div class="coupons">{blank}</div>', lab)]


def bingo():
    k, lab = "Christmas Bingo", "Christmas Bingo, 30 Cards"
    return [cover("Printable party game", "Christmas Bingo", "30 different picture cards", ["tree", "star", "candy cane"],
                  ["Give every player a bingo card and some markers: candies, buttons or coins.", "Cut out the calling cards and mix them in a bowl.",
                   "Draw a calling card and show the picture. Players cover it if they have it.", "First to cover five in a row shouts BINGO!"],
                  ["30 unique picture bingo cards", "32 calling cards", "Works for ages 3 and up (no reading needed)", "Letter and A4 sizes"], lab),
            *bingo_pages(k, lab), *calling_pages(k, lab)]


def charades():
    k, lab = "Christmas Charades", "Christmas Charades Game"
    items = [(lvl, t, 0) for lvl, ts in C.CHARADES.items() for t in ts]
    return [cover("Printable party game", "Christmas Charades", "72 cards to act out, no talking!", ["snowman", "gingerbread", "bell"],
                  ["Cut the cards apart and put them in a bowl or stocking.", "Split into two teams. One player draws a card and acts it out without a sound.",
                   "Their team has one minute to guess. One point for each correct guess.", "Easy cards are great for kids. Tricky cards are worth two points."],
                  ["72 charades cards", "3 levels: easy, medium, tricky", "Score sheet", "Letter and A4 sizes"], lab),
            *card_pages(k, "Charades Cards", items, lab, icons=["snowman", "tree", "gift", "bell", "mitten", "cookie", "sled", "star"]),
            page(head(k, "Score Sheet", "One point per guess. Tricky cards score two.")
                 + '<div class="grid2" style="flex:1">' + "".join(f'<div class="box" style="display:flex;flex-direction:column"><h2>Team {t}</h2>{lines(14)}<div class="field" style="margin-top:8pt">Total<span></span></div></div>' for t in "AB") + "</div>", lab)]


def nye_games():
    k, lab = "New Year's Eve Games", "New Years Eve Party Games"
    ic = ["glass", "clock", "firework", "balloon", "party hat"]
    slips = "".join(f'<div class="card"><div class="lab">{e(p)}</div>{lines(3)}<div class="lab" style="margin-top:4pt">Don\'t sign it!</div></div>'
                    for p in (C.RESOLUTION_PROMPTS + C.RESOLUTION_PROMPTS[:3]))
    pred = "".join(f'<div class="field" style="height:46pt">{e(p)}<span></span></div>' for p in C.NYE_PREDICTIONS)
    return [cover("Printable party games", "New Year's Eve Games", "Five games to fill the hours until midnight", ["glass", "clock", "firework"],
                  ["Pick a game for each hour before midnight.", "Trivia and This or That work for any size group.",
                   "For Whose Resolution, collect the unsigned slips and work out the writer of each one.", "Seal the predictions page in an envelope and open it next New Year's Eve."],
                  ["New Year trivia (20 questions) with answer key", "Whose Resolution? slips", "16 year-in-review conversation cards",
                   "This or That", "Predictions time capsule", "Letter and A4 sizes"], lab),
            *quiz_pages(k, "New Year Trivia", C.NYE_TRIVIA, 10, lab, ic),
            answer_page(k, "New Year Trivia", C.NYE_TRIVIA, lab),
            page(head(k, "Whose Resolution?") + f'<div class="cutnote">Everyone fills in a slip. Read them aloud and name the writer of each one.</div><div class="cards">{slips}</div>', lab),
            *card_pages(k, "Year in Review", C.YEAR_REVIEW, lab, lab="Take turns answering", icons=ic, small=True),
            pairs_page(k, "This or That", "Circle one in each row, then compare with the room.", C.NYE_THIS_OR_THAT, lab, ic[:3]),
            page(head(k, "My Predictions", "Fill in, seal in an envelope, and open next New Year's Eve.", ["clock", "confetti", "clock"])
                 + '<div class="names"><span>Name:</span><span>Date:</span></div>' + f'<div class="form">{pred}</div>', lab)]


# ---------------------------------------------------------------- bundle bonus games
def bonus_thanksgiving():
    k, lab = "Thanksgiving Bonus Games", "Thanksgiving Games Bundle"
    return [pairs_page(k, "This or That", "Circle one in each row, then compare with the table.", C.THIS_OR_THAT_THANKSGIVING, lab, ["turkey", "pie", "pumpkin"]),
            *card_pages(k, "Conversation Cards", C.TABLE_TALK, lab, lab="Take turns answering", icons=["leaf", "acorn", "apple", "corn"], small=True)]


def bonus_christmas():
    k, lab = "Christmas Bonus Games", "Christmas Games Bundle"
    clues = [(f"Clue {i}", c, 0) for i, (c, _) in enumerate(C.SCAVENGER_CLUES, 1)]
    return [*card_pages(k, "Which Would You Choose?", C.WOULD_YOU_RATHER_XMAS, lab, lab="Which would you choose", small=True),
            page(head(k, "Indoor Scavenger Hunt", "A rhyming clue hunt that ends at the tree.", ["gift", "star", "gift"]) + '<ol class="steps">'
                 + "".join(f"<li>{e(s)}</li>" for s in ["Cut the clue cards apart.", "Keep Clue 1 to hand to the kids.",
                                                         "Hide each next clue in the spot the clue before it describes (see the hiding guide).",
                                                         "Put a small prize under the tree for the finish."]) + '</ol><div class="box"><h2>Hiding guide</h2><div class="answers" style="columns:2">'
                 + "".join(f"<p><b>Clue {i}</b> leads to: {e(a)}</p>" for i, (_, a) in enumerate(C.SCAVENGER_CLUES, 1)) + "</div></div>", lab),
            *card_pages(k, "Scavenger Hunt Clues", clues[:8], lab, small=True, icons=["gift", "star", "bell", "tree"]),
            *card_pages(k, "Scavenger Hunt Clues", clues[8:], lab, small=True, icons=["gift", "star", "bell", "tree"], per=4)]


def bundle_cover(kicker, title, tagline, icons, games, label):
    return page(f'<div class="kicker" style="margin-top:6pt">{e(kicker)}</div><h1>{e(title)}</h1><div class="tag">{e(tagline)}</div>'
                f'<div class="big">{"".join(icon(i) for i in icons)}</div>'
                f'<div class="box"><h2>Games in this bundle</h2><ol class="steps">{"".join(f"<li>{e(g)}</li>" for g in games)}</ol></div>'
                '<div style="flex:1"></div><div class="sub">Each game starts with its own how-to-play page. Print only the pages you need.</div>', label, "cover")


# ---------------------------------------------------------------- 2026-11-24 add-ons
def ws_solved(words: list[str], size: int, seed: int):
    """Like word_search, but also returns the set of cells that belong to a word (for the answer key)."""
    rng = random.Random(seed)
    grid = [[""] * size for _ in range(size)]
    used = set()
    for w in sorted(words, key=len, reverse=True):
        for _ in range(800):
            dx, dy = rng.choice([(1, 0), (0, 1), (1, 1)])
            x, y = rng.randrange(size - dx * (len(w) - 1)), rng.randrange(size - dy * (len(w) - 1))
            if all(grid[y + dy * i][x + dx * i] in ("", ch) for i, ch in enumerate(w)):
                for i, ch in enumerate(w):
                    grid[y + dy * i][x + dx * i] = ch
                    used.add((x + dx * i, y + dy * i))
                break
        else:
            raise RuntimeError(f"could not place {w}")
    return [[c or rng.choice("ABCDEFGHIKLMNOPRSTUVWY") for c in row] for row in grid], used


def ws_html(grid, used=None, cell="0.36in", fs="13pt") -> str:
    cells = ""
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            hit = used is not None and (x, y) in used
            style = f"width:{cell};height:{cell};font-size:{fs};" + ("background:var(--c);border-radius:50%;" if hit else
                                                                     ("opacity:0.45;" if used is not None else ""))
            cells += f'<span style="{style}">{c}</span>'
    return f'<div class="wsgrid" style="grid-template-columns:repeat({len(grid)},auto)">{cells}</div>'


def wordlist(words) -> str:
    return f'<div class="wordlist">{"".join(f"<div>{w}</div>" for w in sorted(words))}</div>'


def christmas_word_games():
    k, lab = "Christmas Word Games", "Christmas Word Games for Kids"
    easy, eu = ws_solved(C.XMAS_WORDS_EASY, 11, 1224)
    hard, hu = ws_solved(C.XMAS_WORDS_HARD, 15, 1225)
    scr = "".join(f'<div class="field"><b style="letter-spacing:0.25em;min-width:1.9in">{scramble(w, 40 + i)}</b><span></span></div>'
                  for i, w in enumerate(C.XMAS_SCRAMBLE))
    az = "".join(f'<div class="field"><b style="color:var(--b);font-family:Fraunces;font-size:14pt;min-width:18pt">{ch}</b><span></span></div>'
                 for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return [cover("Printable kids activities", "Christmas Word Games", "Puzzles for the class party or the car ride", ["tree", "snowman", "gift"],
                  ["Print one set per child.", "Start with the easy word search, then try the big one.", "Unscramble the words and fill in the A to Z page.",
                   "Check your work with the answer keys."],
                  ["Easy word search (12 words)", "Big word search (18 words)", "Word scramble (12 words)", "Christmas A to Z",
                   "Answer keys for all three puzzles", "Letter and A4 sizes"], lab),
            page(head(k, "Christmas Word Search", "Easy: words go across, down and diagonally.", ["tree", "star", "bell"])
                 + ws_html(easy, cell="0.5in", fs="18pt") + wordlist(C.XMAS_WORDS_EASY), lab),
            page(head(k, "Big Christmas Word Search", "Find all 18 words.", ["snowflake", "wreath", "candle"])
                 + ws_html(hard, cell="0.38in", fs="13.5pt") + wordlist(C.XMAS_WORDS_HARD), lab),
            page(head(k, "Christmas Word Scramble", "Unscramble each Christmas word.", ["gift", "stocking", "cookie"]) + f'<div class="form">{scr}</div>', lab),
            page(head(k, "Christmas A to Z", "Write something Christmassy that starts with each letter.")
                 + f'<div class="form" style="grid-template-columns:1fr 1fr;column-gap:18pt">{az}</div>', lab),
            page(head(k, "Answer Key: Easy Word Search") + ws_html(easy, eu, cell="0.5in", fs="18pt"), lab),
            page(head(k, "Answer Key: Big Word Search") + ws_html(hard, hu, cell="0.38in", fs="13.5pt"), lab),
            page(head(k, "Answer Key: Word Scramble") + '<div class="answers">'
                 + "".join(f"<p><b>{i}.</b> {scramble(w, 39 + i)} = {w}</p>" for i, w in enumerate(C.XMAS_SCRAMBLE, 1)) + "</div>", lab)]


def gift_tags():
    k, lab = "Christmas Gift Tags", "Printable Christmas Gift Tags"
    sets = [["tree", "star", "gift", "bell", "candy cane", "snowflake", "stocking", "mitten", "ornament", "wreath", "holly", "snowman"],
            ["gingerbread", "santa hat", "cookie", "cocoa", "sled", "bow", "reindeer", "pinecone", "candle", "house", "heart", "snow globe"]]
    greet = ["Merry Christmas", "Happy Holidays", "Just for you", "With love", "Open me first", "Do not open until Dec 25"]

    def tags(icons, texts, cols=3, big=False):
        out = ""
        for i, ic in enumerate(icons):
            out += (f'<div class="card" style="padding:6pt 10pt"><div class="ci" style="font-size:{46 if big else 34}pt">{icon(ic)}</div>'
                    f'<div class="txt small" style="color:var(--a);font-size:{17 if big else 13}pt">{e(texts[i % len(texts)])}</div>'
                    '<div class="field" style="width:86%;margin-top:6pt">To<span></span></div><div class="field" style="width:86%">From<span></span></div></div>')
        return f'<div class="cards" style="grid-template-columns:repeat({cols},1fr)">{out}</div>'

    return [cover("Printable gift wrap helper", "Christmas Gift Tags", "Print, cut, tie on", ["gift", "bow", "star"],
                  ["Print on cardstock, or on sticker paper for stick-on labels.", "Cut along the dashed lines.",
                   "Punch a hole and tie on with ribbon or string, or tape flat.", "Write the names. Done!"],
                  ["48 small tags in 24 designs", "12 large tags", "8 blank write-your-own tags", "Letter and A4 sizes"], lab),
            page(head(k, "Gift Tags") + '<div class="cutnote">Cut along the dashed lines.</div>' + tags(sets[0], greet[:1]), lab),
            page(head(k, "Gift Tags") + '<div class="cutnote">Cut along the dashed lines.</div>' + tags(sets[1], greet[:1]), lab),
            page(head(k, "Gift Tags") + '<div class="cutnote">Cut along the dashed lines.</div>' + tags(sets[0], greet[1:4]), lab),
            page(head(k, "Gift Tags") + '<div class="cutnote">Cut along the dashed lines.</div>' + tags(sets[1], greet[1:4]), lab),
            page(head(k, "Large Gift Tags") + '<div class="cutnote">For big boxes and gift bags.</div>' + tags(sets[0][:6], greet, cols=2, big=True), lab),
            page(head(k, "Large Gift Tags") + '<div class="cutnote">For big boxes and gift bags.</div>' + tags(sets[1][:6], greet[::-1], cols=2, big=True), lab),
            page(head(k, "Write Your Own") + '<div class="cutnote">Blank tags for your own message.</div>'
                 + '<div class="cards">' + "".join(f'<div class="card"><div class="ci">{icon(ic)}</div>{lines(2)}'
                                                     '<div class="field" style="width:86%;margin-top:6pt">To<span></span></div><div class="field" style="width:86%">From<span></span></div></div>'
                                                     for ic in ["star", "tree", "gift", "bell", "holly", "bow", "snowflake", "heart"]) + "</div>", lab)]


def christmas_table_games():
    k, lab = "Christmas Table Games", "Christmas Dinner Table Games"
    awards = "".join(f'<div class="field" style="font-size:12pt">{e(a)}<span></span></div>' for a in C.XMAS_AWARDS)
    return [cover("Printable party games", "Christmas Table Games", "Three easy games for the dinner table", ["candle", "holly", "cocoa"],
                  ["Put a This or That sheet and a pen at every place setting.", "Stack the conversation cards in the middle and take turns drawing.",
                   "After dessert, everyone fills in an awards ballot in secret.", "Count the votes and announce the winners!"],
                  ["This or That, Christmas edition (20 pairs)", "24 conversation cards", "Family awards ballot (12 awards)", "Tally sheet", "Letter and A4 sizes"], lab),
            pairs_page(k, "This or That", "Circle one in each row, then compare with the table.", C.XMAS_THIS_OR_THAT, lab, ["tree", "gift", "cocoa"]),
            *card_pages(k, "Conversation Cards", C.XMAS_TABLE_TALK, lab, lab="Take turns answering", icons=["candle", "holly", "star", "bell"], small=True),
            page(head(k, "Family Awards Ballot", "Write one name on each line. No voting for yourself!", ["star", "bow", "star"])
                 + '<div class="names"><span>Voter (optional):</span></div>' + f'<div class="form">{awards}</div>', lab),
            page(head(k, "Awards Tally", "Count the ballots and write in each winner.")
                 + '<div class="form">' + "".join(f'<div class="field" style="font-size:12pt">{e(a)}<span></span>Votes<span style="flex:0.3"></span></div>' for a in C.XMAS_AWARDS) + "</div>", lab)]


def nye_kids():
    k, lab = "New Year's Eve for Kids", "New Years Eve Kids Countdown Pack"
    ic = ["balloon", "party hat", "clock", "confetti", "firework"]
    grid, used = ws_solved(C.NYE_KIDS_WORDS, 13, 2027)
    bags = "".join(f'<div class="card"><div class="ci">{icon(ic[i % 5])}</div><div class="lab">{e(t)}</div>'
                   '<div class="field" style="width:80%;font-size:10pt">Open at<span></span>o\'clock</div>'
                   f'<div class="txt small" style="margin-top:6pt">{e(a)}</div></div>' for i, (t, a) in enumerate(C.NYE_KIDS_HOURS))
    blank = "".join(f'<div class="card"><div class="ci">{icon(ic[i % 5])}</div><div class="lab">Bag</div>'
                    f'<div class="field" style="width:80%;font-size:10pt">Open at<span></span>o\'clock</div>{lines(2)}</div>' for i in range(8))
    review = "".join(f'<div class="field" style="height:44pt">{e(p)}<span></span></div>' for p in C.NYE_KIDS_REVIEW)
    goals = "".join(f'<div class="field" style="height:50pt">{e(p)}<span></span></div>' for p in C.NYE_KIDS_GOALS)
    return [cover("Printable kids party pack", "New Year's Eve for Kids", "A countdown party, one bag at a time", ["balloon", "party hat", "clock"],
                  ["Cut out the countdown tags and tape one to each paper bag or envelope.", "Write a time on every tag. Early bedtime? Count down to noon or 8 pm instead.",
                   "Tuck in what the activity needs: paper for hats, a balloon, a snack.", "Open one bag each hour and finish with the big countdown!"],
                  ["8 countdown bag tags with activities", "8 blank tags for your own ideas", "My Year in Review page", "Wishes for next year page",
                   "Pick One game", "Word search with answer key", "Letter and A4 sizes"], lab),
            page(head(k, "Countdown Bag Tags") + f'<div class="cutnote">Cut apart and tape one to each bag.</div><div class="cards">{bags}</div>', lab),
            page(head(k, "Make Your Own Tags") + f'<div class="cutnote">Write your own activities.</div><div class="cards">{blank}</div>', lab),
            page(head(k, "My Year in Review", "", ic[:3]) + '<div class="names"><span>Name:</span><span>Age:</span></div>' + f'<div class="form">{review}</div>', lab),
            page(head(k, "My Wishes for Next Year", "", ["firework", "clock", "firework"]) + '<div class="names"><span>Name:</span></div>' + f'<div class="form">{goals}</div>', lab),
            pairs_page(k, "Pick One!", "Circle the one you would pick in each row.", C.NYE_KIDS_PICK, lab, ic[:3]),
            page(head(k, "New Year Word Search", "Words go across, down and diagonally.", ["balloon", "confetti", "party hat"])
                 + ws_html(grid, cell="0.44in", fs="16pt") + wordlist(C.NYE_KIDS_WORDS), lab),
            page(head(k, "Answer Key: Word Search") + ws_html(grid, used, cell="0.44in", fs="16pt"), lab)]
