import pytest
import responses

from src.clients.base import AuthError, ClientError, HttpClient, QuotaExhausted, RateLimited

URL = "https://api.example.test"


def client(sleeps, **kw):
    return HttpClient(URL, sleep=sleeps.append, **kw)


@responses.activate
def test_429_replay_honors_retry_after_then_succeeds():
    responses.get(f"{URL}/x", status=429, headers={"Retry-After": "3"})
    responses.get(f"{URL}/x", status=429)
    responses.get(f"{URL}/x", json={"ok": True})
    sleeps = []
    assert client(sleeps, backoff_base=1.0).get_json("x") == {"ok": True}
    assert len(responses.calls) == 3
    assert sleeps[0] == 3.0          # Retry-After honored
    assert 2.0 <= sleeps[1] <= 3.0   # exponential backoff with jitter (attempt 1)


@responses.activate
def test_429_exhausted_fails_closed():
    for _ in range(3):
        responses.get(f"{URL}/x", status=429, headers={"Retry-After": "1"})
    with pytest.raises(RateLimited):
        client([], max_retries=2).get_json("x")
    assert len(responses.calls) == 3


@responses.activate
def test_retry_after_longer_than_max_wait_fails_closed():
    responses.get(f"{URL}/x", status=429, headers={"Retry-After": "3600"})
    with pytest.raises(RateLimited):
        client([], max_wait=60).get_json("x")
    assert len(responses.calls) == 1


@pytest.mark.parametrize("status", [401, 403])
@responses.activate
def test_auth_errors_do_not_retry(status):
    responses.get(f"{URL}/x", status=status)
    with pytest.raises(AuthError):
        client([]).get_json("x")
    assert len(responses.calls) == 1


@responses.activate
def test_other_errors_raise():
    responses.get(f"{URL}/x", status=500, body="boom")
    with pytest.raises(ClientError):
        client([]).get_json("x")


@responses.activate
def test_daily_quota_zero_stops_before_next_call():
    responses.get(f"{URL}/x", json={}, headers={"x-remaining-today": "0"})
    c = client([])
    c.get_json("x")
    with pytest.raises(QuotaExhausted):
        c.get_json("x")
    assert len(responses.calls) == 1


@responses.activate
def test_per_second_quota_zero_pauses():
    responses.get(f"{URL}/x", json={}, headers={"x-remaining-this-second": "0"})
    sleeps = []
    c = client(sleeps)
    c.get_json("x")
    c.get_json("x")
    assert sleeps == [1.0]
