"""IP screen for a concept (docs/ip-screen.md). Produces the concept's `ip_review` record.

Seven checks; the blocklist runs here, the rest are recorded results from the reviewer (Claude in
the define step, or the owner). Fail closed (CLAUDE.md rules 3 and 8): a missing check, an
`unknown` result, or a `hit` is a veto. The trademark check must also cover the USPTO classes of
the product being made.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Iterable

from .blocklist import Blocklist

# Checks the reviewer records. "blocklist" is computed, so it is not in this list.
RECORDED_CHECKS = ("origin", "trademark", "etsy_marketplace", "text_copyright", "image_provenance")
ALL_CHECKS = ("blocklist",) + RECORDED_CHECKS
RESULTS = ("pass", "hit", "unknown")

# Nice classes a USPTO search must cover, by product_format (docs/data-model.md, concept).
# 025 clothing, 021 mugs/drinkware, 016 paper goods/stickers/prints, 009 downloadable files,
# 024 textiles (tote bags are 018). Unknown formats fail closed.
CLASSES_BY_FORMAT = {
    "tshirt": {"025"}, "sweatshirt": {"025"}, "hoodie": {"025"}, "hat": {"025"},
    "mug": {"021"}, "tumbler": {"021"},
    "sticker": {"016"}, "poster": {"016"}, "art_print": {"016"}, "card": {"016"},
    "tote_bag": {"018"}, "pillow": {"024"}, "blanket": {"024"},
    "printable_wall_art": {"009", "016"}, "planner": {"009", "016"}, "printable": {"009", "016"},
}


@dataclass(frozen=True)
class CheckResult:
    result: str                      # "pass" | "hit" | "unknown"
    evidence: str                    # what was searched / seen, enough to repeat it
    checked_at: str                  # ISO 8601 UTC
    classes: tuple[str, ...] = ()    # trademark only: Nice classes searched

    def to_dict(self, name: str) -> dict:
        d = {"check": name, "result": self.result, "evidence": self.evidence, "checked_at": self.checked_at}
        if name == "trademark":
            d["classes"] = sorted(self.classes)
        return d


@dataclass
class Subject:
    """What is being screened: every customer-visible text plus the product format."""
    phrase: str
    product_format: str
    title: str = ""
    tags: list[str] = field(default_factory=list)
    design_text: list[str] = field(default_factory=list)

    def texts(self) -> list[str]:
        return [self.phrase, self.title, *self.tags, *self.design_text]


def review(subject: Subject, checks: dict[str, CheckResult], *, blocklist: Blocklist,
           now: dt.datetime | None = None) -> dict:
    """Return an `ip_review` record: status pass only if every check passes."""
    now_s = (now or dt.datetime.now(dt.timezone.utc)).isoformat(timespec="seconds")
    reasons: list[str] = []
    records: list[dict] = []

    hits = blocklist.check(subject.texts())
    bl = CheckResult("hit" if hits else "pass",
                     "; ".join(sorted({f"{h.category}/{h.rule}: {h.match!r}" for h in hits})) or "no hits", now_s)
    records.append(bl.to_dict("blocklist"))
    if hits:
        reasons.append(f"blocklist: {bl.evidence}")

    for name in RECORDED_CHECKS:
        c = checks.get(name)
        if c is None:
            reasons.append(f"{name}: not checked")
            continue
        records.append(c.to_dict(name))
        if c.result not in RESULTS:
            reasons.append(f"{name}: invalid result {c.result!r}")
        elif c.result != "pass":
            reasons.append(f"{name}: {c.result} ({c.evidence})")
        elif not c.evidence.strip():
            reasons.append(f"{name}: pass without evidence")

    tm = checks.get("trademark")
    needed = CLASSES_BY_FORMAT.get(subject.product_format)
    if needed is None:
        reasons.append(f"trademark: unknown product_format {subject.product_format!r}")
    elif tm is not None and not needed <= set(tm.classes):
        reasons.append(f"trademark: classes {sorted(needed - set(tm.classes))} not searched")

    return {"status": "veto" if reasons else "pass", "reasons": reasons, "reviewed_at": now_s,
            "checks": records}


def is_veto(ip_review: dict | None) -> bool:
    """Scoring input `ip_veto`: anything but an explicit pass is a veto."""
    return not ip_review or ip_review.get("status") != "pass"


def missing_checks(ip_review: dict) -> Iterable[str]:
    seen = {c["check"] for c in ip_review.get("checks", [])}
    return [c for c in ALL_CHECKS if c not in seen]
