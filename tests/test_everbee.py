import pytest
import responses

from src.clients.base import QuotaExhausted, RateLimited
from src.clients.everbee import EverBee
from tests.conftest import load

URL = "https://everbee.test"


def eb(sleeps):
    return EverBee("cid", "secret", base_url=URL, sleep=sleeps.append)


@responses.activate
def test_headers_and_estimate_label():
    responses.get(f"{URL}/api/v1/keywords/pickleball%20gift", json=load("everbee/keyword_research.json"),
                  headers={"x-remaining-today": "42"})
    out = eb([]).keyword_research("pickleball gift")
    req = responses.calls[0].request
    assert req.headers["client_id"] == "cid" and req.headers["client_secret"] == "secret"
    assert out["is_estimate"] is True and out["source"] == "everbee"
    assert out["remaining"] == {"x-remaining-today": 42}
    assert out["data"]["search_volume"] == 14800


@responses.activate
def test_429_replay_backs_off_then_succeeds():
    responses.get(f"{URL}/api/v1/keywords/pickleball%20gift", status=429, headers={"Retry-After": "5"})
    responses.get(f"{URL}/api/v1/keywords/pickleball%20gift", json=load("everbee/keyword_research.json"))
    sleeps = []
    out = eb(sleeps).keyword_research("pickleball gift")
    assert sleeps == [5.0]
    assert out["data"]["keyword"] == "pickleball gift"


@responses.activate
def test_429_persisting_fails_closed():
    for _ in range(5):
        responses.get(f"{URL}/api/v1/keywords/x", status=429)
    with pytest.raises(RateLimited):
        eb([]).keyword_research("x")


@responses.activate
def test_remaining_zero_blocks_next_call():
    responses.get(f"{URL}/api/v1/keywords/a", json={}, headers={"x-remaining-today": "0"})
    client = eb([])
    client.keyword_research("a")
    with pytest.raises(QuotaExhausted):
        client.keyword_research("b")
    assert len(responses.calls) == 1


@responses.activate
def test_product_analytics_uses_listings_endpoint_with_title_filter():
    responses.get(f"{URL}/api/v1/listings", json={"listings": []})
    eb([]).product_analytics("pickleball gift", per_page=25)
    req = responses.calls[0].request
    assert "title_include=pickleball+gift" in req.url and "per_page=25" in req.url
