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
