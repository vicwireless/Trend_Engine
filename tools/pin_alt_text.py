"""Alt text for Pinterest pin images (Day-21: pins were going out without it).

Template-built from the same strings that are drawn on the pin, so the alt text describes what is
actually in the image. No AI is used, so this adds no new AI-assisted text. Kept free of the PDF and
font dependencies in make_planner_family so CI can test it.
"""
from __future__ import annotations

from typing import Iterable

from src.compliance.blocklist import Blocklist

MAX_ALT_CHARS = 500  # Pinterest alt_text limit


def alt_text_cover(year: int, heading: str, subtitle: str, product: str) -> str:
    """Pin A: big year, heading, subtitle, one planner page, footer strip."""
    return (f'Pin graphic on a cream background: a large sage-green "{year}" above the heading "{heading}" '
            f'and the line "{subtitle}". Below is a preview of one page of the printable {product.lower()}. '
            "Footer text: Printable PDF, Letter and A4, instant download.")


def alt_text_inside(items: Iterable[str], product: str) -> str:
    """Pin B: "What's inside" checklist, one sample page, footer strip."""
    listed = "; ".join(items)
    return (f"Pin graphic on a cream background headed \"What's inside\", with a checklist: {listed}. "
            f"Below is a preview of a sample page from the printable {product.lower()}. "
            "Footer text: Print at home, for personal use.")


def check_alt_text(alt: str, blocklist: Blocklist) -> list[str]:
    """Fail-closed checks; an empty list means the alt text is usable."""
    errs = []
    if not alt or not alt.strip():
        errs.append("alt text is empty")
    if len(alt) > MAX_ALT_CHARS:
        errs.append(f"alt text is {len(alt)} chars (max {MAX_ALT_CHARS})")
    errs += [f"blocklist veto [{h.category}/{h.rule}] matched {h.match!r}" for h in blocklist.check(alt)]
    return errs
