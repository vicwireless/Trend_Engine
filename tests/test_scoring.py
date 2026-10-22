import datetime as dt

import pytest

from src.scoring.score import (WEIGHTS, ScoreInputs, band, digital_share, gift_share, margin, score,
                               seasonality, weeks_to_next_peak)

FEES = {"listing_fee_usd": 0.20, "transaction_fee_rate": 0.065, "payment_processing_rate": 0.03,
        "payment_processing_fixed_usd": 0.25}


def inputs(**kw):
    base = dict(momentum=0.5, interest=60, active_listings=1000, median_favorites=100,
                median_price_usd=8.0, unit_cost_usd=0.0, owner_minutes_per_listing=5,
                gift_share=0.4, digital_share=0.8, sources=3, price_floor_margin=0.60,
                weeks_to_peak=9)
    return ScoreInputs(**{**base, **kw})


def test_weights_sum_to_one():
    assert sum(WEIGHTS.values()) == pytest.approx(1.0)
    assert len(WEIGHTS) == 8


def test_margin():
    assert margin(10.0, 0.0, FEES) == pytest.approx((10 - 0.20 - 0.65 - 0.30 - 0.25) / 10)


def test_strong_niche_builds():
    r = score(inputs(), FEES)
    assert r.band == "build" and 65 <= r.score <= 100
    assert set(r.components) == set(WEIGHTS)
    assert r.components["demand_momentum"] == pytest.approx(0.6 * 1 + 0.4 * 0.6, abs=1e-4)
    assert r.components["seasonality"] == 1.0
    assert r.components["our_evidence"] == 0.0


def test_everbee_delta_blends_into_demand():
    base = score(inputs(momentum=0.0), FEES).components["demand_momentum"]
    boosted = score(inputs(momentum=0.0, everbee_delta=0.5), FEES).components["demand_momentum"]
    assert boosted > base


def test_our_evidence_reaches_one_at_day45_gate():
    r = score(inputs(cohort_orders=10, cohort_contribution_per_100_visits=15), FEES)
    assert r.components["our_evidence"] == 1.0
    assert r.score > score(inputs(), FEES).score


def test_confidence_scales_score():
    assert score(inputs(sources=1), FEES).score == pytest.approx(score(inputs(), FEES).score * 0.70, abs=0.1)


@pytest.mark.parametrize("kw,reason", [
    ({"ip_veto": True}, "ip veto"),
    ({"momentum": None}, "missing inputs"),
    ({"gift_share": None}, "missing inputs"),
    ({"offer_type": "pod", "price_floor_margin": 0.30}, "pod_blueprints"),
    ({"offer_type": "sticker"}, "unknown offer_type"),
    ({"median_price_usd": 1.0}, "below floor"),
])
def test_hard_zeroes(kw, reason):
    r = score(inputs(**kw), FEES)
    assert r.score == 0 and r.band == "park" and reason in r.zero_reason


def test_pod_without_blueprints_scores_zero_pod_fit():
    r = score(inputs(offer_type="pod", pod_blueprints=0, price_floor_margin=0.30), FEES)
    assert r.components["pod_fit"] == 0.0


def test_bands():
    assert band(65) == "build" and band(64.9) == "test" and band(50) == "test" and band(49.9) == "park"


def test_saturated_niche_scores_lower():
    assert score(inputs(active_listings=200_000), FEES).score < score(inputs(), FEES).score


@pytest.mark.parametrize("weeks,expected", [(None, 0.5), (9, 1.0), (4, 0.5), (0, 0.0), (26, 0.3), (18, 0.5)])
def test_seasonality(weeks, expected):
    assert seasonality(weeks) == pytest.approx(expected)


def test_weeks_to_next_peak_rolls_past_peaks_forward():
    today = dt.date(2026, 10, 22)
    assert weeks_to_next_peak([dt.date(2027, 2, 14)], today) == pytest.approx(16.0 + 3 / 7, abs=0.01)
    assert weeks_to_next_peak([dt.date(2026, 2, 14)], today) == pytest.approx(16.0 + 3 / 7, abs=0.01)
    assert weeks_to_next_peak([], today) is None


def test_share_helpers():
    titles = ["Personalized teacher gift print", "Abstract wall art", "Birthday card printable", "Minimal poster"]
    assert gift_share(titles) == 0.5
    assert digital_share(["download", "physical", "both", "physical"]) == 0.5
    assert gift_share([]) is None and digital_share([]) is None
