import pytest
import responses

from src.clients.serpapi_trends import BASE_URL, SerpApiTrends, momentum
from tests.conftest import load


@responses.activate
def test_interest_over_time():
    responses.get(f"{BASE_URL}/search.json", json=load("serpapi/interest_over_time.json"))
    out = SerpApiTrends("k").interest_over_time("pickleball gift")
    url = responses.calls[0].request.url
    assert "engine=google_trends" in url and "data_type=TIMESERIES" in url
    assert out["is_estimate"] is True and out["source"] == "serpapi_google_trends"
    assert len(out["points"]) == 24 and out["points"][-1]["value"] == 60
    assert momentum(out["points"]) == 0.5


@responses.activate
def test_related_queries():
    responses.get(f"{BASE_URL}/search.json", json=load("serpapi/related_queries.json"))
    out = SerpApiTrends("k").related_queries("pickleball gift")
    assert "data_type=RELATED_QUERIES" in responses.calls[0].request.url
    assert out["rising"] == [{"query": "pickleball gifts for men", "value": 250}]
    assert out["top"][0] == {"query": "pickleball paddle", "value": 100}


def test_momentum_needs_enough_points():
    assert momentum([{"value": 1}] * 10) is None


@responses.activate
def test_trending_now():
    responses.get(f"{BASE_URL}/search.json", json=load("serpapi/trending_now.json"))
    out = SerpApiTrends("k").trending_now(hours=168)
    url = responses.calls[0].request.url
    assert "engine=google_trends_trending_now" in url and "hours=168" in url
    assert out["source"] == "serpapi_google_trends_trending_now" and out["is_estimate"] is True
    assert out["trending"][0]["query"] == "friendsmas ideas"
    assert out["trending"][0]["categories"] == ["Shopping"]
    assert out["trending"][1]["active"] is False


def test_trending_now_rejects_bad_hours():
    with pytest.raises(ValueError):
        SerpApiTrends("k").trending_now(hours=12)


@responses.activate
def test_autocomplete():
    responses.get(f"{BASE_URL}/search.json", json=load("serpapi/autocomplete.json"))
    out = SerpApiTrends("k").autocomplete("funny plant mug")
    url = responses.calls[0].request.url
    assert "engine=google_autocomplete" in url and "q=funny+plant+mug" in url
    assert out["source"] == "serpapi_google_autocomplete"
    assert [s["value"] for s in out["suggestions"]] == ["funny plant mug", "funny plant mug for her"]
