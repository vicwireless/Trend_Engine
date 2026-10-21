"""Niche / offer score. Implements docs/scoring.md (scoring-v0.1)."""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

SCORE_VERSION = "scoring-v0.1"
WEIGHTS = {"demand": 0.30, "openness": 0.20, "engagement": 0.15, "price_headroom": 0.20, "production_fit": 0.15}
BANDS = ((65.0, "build"), (50.0, "test"), (0.0, "park"))


@dataclass
class ScoreInputs:
    momentum: float | None
    interest: float | None
    active_listings: int | None
    median_favorites: float | None
    median_price_usd: float | None
    unit_cost_usd: float | None
    owner_minutes_per_listing: float | None
    sources: int
    price_floor_margin: float
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


def score(inp: ScoreInputs, fees: dict) -> ScoreResult:
    required = ("momentum", "interest", "active_listings", "median_favorites",
                "median_price_usd", "unit_cost_usd", "owner_minutes_per_listing")
    missing = [k for k in required if getattr(inp, k) is None]
    if missing:
        return _zero(f"missing inputs: {', '.join(missing)}")
    if inp.ip_veto:
        return _zero("ip veto")
    if inp.median_price_usd <= 0:
        return _zero("no market price")

    m = margin(inp.median_price_usd, inp.unit_cost_usd, fees)
    if m < inp.price_floor_margin:
        return _zero(f"margin {m:.2f} below floor {inp.price_floor_margin:.2f}", m)

    comps = {
        "demand": 0.6 * clamp((inp.momentum + 0.2) / 0.7) + 0.4 * clamp(inp.interest / 100),
        "openness": 1 - clamp((math.log10(max(inp.active_listings, 1)) - 2) / 3),
        "engagement": clamp(math.log10(1 + inp.median_favorites) / math.log10(501)),
        "price_headroom": clamp((m - inp.price_floor_margin) / 0.30),
        "production_fit": clamp(1 - (inp.owner_minutes_per_listing - 2) / 28),
    }
    k = confidence(inp.sources)
    value = round(100 * k * sum(WEIGHTS[n] * v for n, v in comps.items()), 1)
    return ScoreResult(value, band(value), {n: round(v, 4) for n, v in comps.items()}, k, round(m, 4), None)


def band(value: float) -> str:
    return next(name for floor, name in BANDS if value >= floor)


def _zero(reason: str, m: float | None = None) -> ScoreResult:
    return ScoreResult(0.0, "park", {}, 0.0, None if m is None else round(m, 4), reason)
