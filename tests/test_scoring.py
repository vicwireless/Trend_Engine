import pytest

from src.scoring.score import ScoreInputs, band, margin, score

FEES = {"listing_fee_usd": 0.20, "transaction_fee_rate": 0.065, "payment_processing_rate": 0.03,
        "payment_processing_fixed_usd": 0.25}


def inputs(**kw):
    base = dict(momentum=0.5, interest=60, active_listings=1000, median_favorites=100,
                median_price_usd=8.0, unit_cost_usd=0.0, owner_minutes_per_listing=5,
                sources=3, price_floor_margin=0.60)
    return ScoreInputs(**{**base, **kw})


def test_margin():
    assert margin(10.0, 0.0, FEES) == pytest.approx((10 - 0.20 - 0.65 - 0.30 - 0.25) / 10)


def test_strong_niche_builds():
    r = score(inputs(), FEES)
    assert r.band == "build" and 65 <= r.score <= 100
    assert set(r.components) == {"demand", "openness", "engagement", "price_headroom", "production_fit"}
    assert r.components["demand"] == pytest.approx(0.6 * 1 + 0.4 * 0.6, abs=1e-4)
    assert r.components["openness"] == pytest.approx(1 - 1 / 3, abs=1e-4)


def test_confidence_scales_score():
    assert score(inputs(sources=1), FEES).score == pytest.approx(score(inputs(), FEES).score * 0.70, abs=0.1)


@pytest.mark.parametrize("kw,reason", [
    ({"ip_veto": True}, "ip veto"),
    ({"momentum": None}, "missing inputs"),
    ({"median_price_usd": 1.0}, "below floor"),
])
def test_hard_zeroes(kw, reason):
    r = score(inputs(**kw), FEES)
    assert r.score == 0 and r.band == "park" and reason in r.zero_reason


def test_bands():
    assert band(65) == "build" and band(64.9) == "test" and band(50) == "test" and band(49.9) == "park"


def test_saturated_niche_scores_lower():
    assert score(inputs(active_listings=200_000), FEES).score < score(inputs(), FEES).score
