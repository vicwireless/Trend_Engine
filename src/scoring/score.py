"""Niche / offer score. Implements docs/scoring.md (scoring-v0.2)."""
from __future__ import annotations

import datetime as dt
import math
import re
from dataclasses import asdict, dataclass

SCORE_VERSION = "scoring-v0.2"
# Playbook SP-03 inputs. Weights accepted by the owner 2026-10-22 (proposed defaults).
WEIGHTS = {"demand_momentum": 0.25, "competition_gap": 0.20, "gift_intent": 0.10, "digital_fit": 0.10,
           "pod_fit": 0.10, "seasonality": 0.10, "our_evidence": 0.10, "production_fit": 0.05}
BANDS = ((65.0, "build"), (50.0, "test"), (0.0, "park"))
GIFT_WORDS = re.compile(
    r"\b(gift|gifts|personali[sz]ed|custom|birthday|christmas|hanukkah|valentine'?s?|mother'?s day|"
    r"father'?s day|wedding|anniversary|graduation|teacher|bridesmaid|baby shower|housewarming|"
    r"retirement|for (him|her|mom|dad))\b", re.I)
EVERGREEN_SEASONALITY = 0.5


@dataclass
class ScoreInputs:
    momentum: float | None
    interest: float | None
    active_listings: int | None
    median_favorites: float | None
    median_price_usd: float | None
    unit_cost_usd: float | None
    owner_minutes_per_listing: float | None
    gift_share: float | None          # share of top-25 Etsy titles with gift/occasion words
    digital_share: float | None       # share of top-25 Etsy results that are downloads
    sources: int
    price_floor_margin: float
    offer_type: str = "digital"       # "digital" | "pod"
    everbee_delta: float | None = None   # EverBee search-volume change (estimate), optional
    pod_blueprints: int | None = None    # matching Printify blueprints; required for pod offers
    weeks_to_peak: float | None = None   # None = evergreen
    cohort_orders: int = 0
    cohort_contribution_per_100_visits: float = 0.0
    ip_veto: bool = False


@dataclass
class ScoreResult:
    score: float
    band: str
    components: dict
    confidence: float
    margin_at_median: float | None
    zero_reason: str | None
    version: str = SCORE_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def etsy_fees(price: float, fees: dict) -> float:
    """Per-sale Etsy fees on a single item. `fees` comes from the dated fee snapshot."""
    return (fees["listing_fee_usd"]
            + price * fees["transaction_fee_rate"]
            + price * fees["payment_processing_rate"]
            + fees["payment_processing_fixed_usd"])


def margin(price: float, unit_cost: float, fees: dict) -> float:
    return (price - etsy_fees(price, fees) - unit_cost) / price


def confidence(sources: int) -> float:
    return 1.0 if sources >= 3 else 0.85 if sources == 2 else 0.70 if sources == 1 else 0.0


def gift_share(titles: list[str]) -> float | None:
    """Share of titles (top 25 Etsy results) with gift or occasion words."""
    titles = titles[:25]
    return sum(bool(GIFT_WORDS.search(t)) for t in titles) / len(titles) if titles else None


def digital_share(listing_types: list[str]) -> float | None:
    """Share of the top 25 Etsy results whose `listing_type` is "download" or "both"."""
    types = listing_types[:25]
    return sum(t in ("download", "both") for t in types) / len(types) if types else None


def weeks_to_next_peak(peak_dates: list[dt.date], today: dt.date) -> float | None:
    """Weeks to the nearest upcoming peak in data/calendar.yaml (a past peak counts next year)."""
    upcoming = []
    for p in peak_dates:
        while p < today:
            p = p.replace(year=p.year + 1)
        upcoming.append(p)
    return min((p - today).days / 7 for p in upcoming) if upcoming else None


def seasonality(weeks: float | None) -> float:
    """1.0 inside the 8–10 week launch window; too late falls to 0, too early decays to 0.3."""
    if weeks is None:
        return EVERGREEN_SEASONALITY
    if 8 <= weeks <= 10:
        return 1.0
    if weeks < 8:
        return clamp(weeks / 8)
    return max(0.3, 1 - (weeks - 10) / 16)


def score(inp: ScoreInputs, fees: dict) -> ScoreResult:
    required = ["momentum", "interest", "active_listings", "median_favorites", "median_price_usd",
                "unit_cost_usd", "owner_minutes_per_listing", "gift_share", "digital_share"]
    if inp.offer_type == "pod":
        required.append("pod_blueprints")
    missing = [k for k in required if getattr(inp, k) is None]
    if inp.offer_type not in ("digital", "pod"):
        return _zero(f"unknown offer_type {inp.offer_type!r}")
    if missing:
        return _zero(f"missing inputs: {', '.join(missing)}")
    if inp.ip_veto:
        return _zero("ip veto")
    if inp.median_price_usd <= 0:
        return _zero("no market price")

    m = margin(inp.median_price_usd, inp.unit_cost_usd, fees)
    if m < inp.price_floor_margin:
        return _zero(f"margin {m:.2f} below floor {inp.price_floor_margin:.2f}", m)

    trends = 0.6 * clamp((inp.momentum + 0.2) / 0.7) + 0.4 * clamp(inp.interest / 100)
    demand = trends if inp.everbee_delta is None else 0.7 * trends + 0.3 * clamp((inp.everbee_delta + 0.2) / 0.7)
    openness = 1 - clamp((math.log10(max(inp.active_listings, 1)) - 2) / 3)
    engagement = clamp(math.log10(1 + inp.median_favorites) / math.log10(501))
    headroom = clamp((m - inp.price_floor_margin) / 0.30)
    blueprint_fit = 1.0 if inp.offer_type == "digital" else clamp(inp.pod_blueprints / 3)
    evidence = 0.5 * clamp(inp.cohort_orders / 10) + 0.5 * clamp(inp.cohort_contribution_per_100_visits / 15)

    comps = {
        "demand_momentum": demand,
        "competition_gap": 0.6 * openness + 0.4 * engagement,
        "gift_intent": clamp(inp.gift_share / 0.5),
        "digital_fit": clamp(inp.digital_share / 0.6),
        "pod_fit": headroom * blueprint_fit,
        "seasonality": seasonality(inp.weeks_to_peak),
        "our_evidence": evidence,
        "production_fit": clamp(1 - (inp.owner_minutes_per_listing - 2) / 28),
    }
    k = confidence(inp.sources)
    value = round(100 * k * sum(WEIGHTS[n] * v for n, v in comps.items()), 1)
    return ScoreResult(value, band(value), {n: round(v, 4) for n, v in comps.items()}, k, round(m, 4), None)


def band(value: float) -> str:
    return next(name for floor, name in BANDS if value >= floor)


def _zero(reason: str, m: float | None = None) -> ScoreResult:
    return ScoreResult(0.0, "park", {}, 0.0, None if m is None else round(m, 4), reason)
