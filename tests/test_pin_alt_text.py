import re
from pathlib import Path

from src.compliance.blocklist import Blocklist
from tools.pin_alt_text import MAX_ALT_CHARS, alt_text_cover, alt_text_inside, check_alt_text

ROOT = Path(__file__).resolve().parents[1]
PINS_MD = ROOT / "assets" / "pins" / "2026-10-23" / "pins.md"


def test_cover_alt_text_describes_pin():
    alt = alt_text_cover(2027, "Weekly Planner Printable", "One calm page per week", "Weekly Planner")
    assert '"2027"' in alt and "Weekly Planner Printable" in alt and "One calm page per week" in alt
    assert "weekly planner" in alt and check_alt_text(alt, Blocklist.load()) == []


def test_inside_alt_text_lists_items():
    alt = alt_text_inside(["12 monthly pages", "Reflection box"], "Habit Tracker")
    assert "12 monthly pages; Reflection box" in alt and "habit tracker" in alt
    assert check_alt_text(alt, Blocklist.load()) == []


def test_check_fails_closed():
    bl = Blocklist({"categories": {"brands": ["Acme"]}})
    assert check_alt_text("", bl) == ["alt text is empty"]
    assert any("max" in e for e in check_alt_text("x" * (MAX_ALT_CHARS + 1), bl))
    assert any("blocklist veto" in e for e in check_alt_text("An Acme planner", bl))


def test_committed_pins_all_have_alt_text():
    text = PINS_MD.read_text(encoding="utf-8")
    pins = re.split(r"^## Pin \d+:", text, flags=re.M)[1:]
    assert len(pins) == 6
    bl = Blocklist.load()
    for block in pins:
        m = re.search(r"^- Alt text: (.+)$", block, flags=re.M)
        assert m, f"pin without alt text: {block[:60]!r}"
        assert check_alt_text(m.group(1), bl) == []
    # AI-disclosure guidance stays in the posting instructions
    assert "AI-assisted" in text and "AI-modified" in text
