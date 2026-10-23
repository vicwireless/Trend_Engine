import json

import pytest
import responses

from src.clients.base import MissingCredential
from src.clients.etsy_read import BASE_URL, EtsyRead
from tests.conftest import load


@pytest.fixture(autouse=True)
def etsy_env(monkeypatch):
    monkeypatch.setenv("ETSY_SHARED_SECRET", "sec")
    for k in ("ETSY_READ_TOKEN", "ETSY_REFRESH_TOKEN"):
        monkeypatch.delenv(k, raising=False)


@responses.activate
def test_find_active_listings_returns_price_and_favorites():
    responses.get(f"{BASE_URL}/listings/active", json=load("etsy/listings_active.json"))
    out = EtsyRead("key", None).find_active_listings("pickleball print", limit=3)
    assert responses.calls[0].request.headers["x-api-key"] == "key:sec"
    assert "keywords=pickleball+print" in responses.calls[0].request.url
    assert out["count"] == 18342
    assert out["source"] == "etsy_open_api"
    assert out["results"][0] == {**out["results"][0], "price_usd": 12.99, "num_favorers": 412}
    assert out["results"][2]["price_usd"] is None  # non-USD prices are not mixed in
    assert out["results"][0]["listing_type"] == "download"  # Etsy's field is listing_type, not type


@responses.activate
def test_receipts_strip_buyer_identity():
    responses.get(f"{BASE_URL}/shops/77/receipts", json=load("etsy/shop_receipts.json"))
    receipts = EtsyRead("key", "tok").get_shop_receipts(77)
    assert responses.calls[0].request.headers["Authorization"] == "Bearer tok"
    blob = json.dumps(receipts)
    for pii in ("Jane", "Elm Street", "jane.buyer@example.com", "62701", "31337", "sister Ann", "seller@example.com"):
        assert pii not in blob
    r = receipts[0]
    assert r["grandtotal_usd"] == 25.98
    tx = r["transactions"][0]
    assert tx["listing_id"] == 1001 and tx["quantity"] == 2 and tx["price_usd"] == 12.99
    assert tx["personalization_text"] == "Team Dink 2026"
    assert "buyer_user_id" not in tx


def test_receipts_require_oauth_token(monkeypatch):
    monkeypatch.delenv("ETSY_READ_TOKEN", raising=False)
    with pytest.raises(MissingCredential):
        EtsyRead("key", None).get_shop_receipts(77)


@responses.activate
def test_listing_stats():
    responses.get(f"{BASE_URL}/listings/1001", json=load("etsy/listing.json"))
    s = EtsyRead("key").get_listing_stats(1001)
    assert s == {"listing_id": 1001, "state": "active", "views": 2310, "num_favorers": 412,
                 "price_usd": 12.99, "source": "etsy_open_api"}


@responses.activate
def test_listing_stats_without_views():
    body = load("etsy/listing.json")
    del body["views"]
    responses.get(f"{BASE_URL}/listings/1001", json=body)
    assert EtsyRead("key").get_listing_stats(1001)["views"] is None


def test_missing_keystring_fails_closed(monkeypatch):
    monkeypatch.delenv("ETSY_KEYSTRING", raising=False)
    with pytest.raises(MissingCredential):
        EtsyRead()


def test_missing_shared_secret_fails_closed(monkeypatch):
    monkeypatch.delenv("ETSY_SHARED_SECRET")
    with pytest.raises(MissingCredential, match="ETSY_SHARED_SECRET"):
        EtsyRead("key", None)


@responses.activate
def test_refresh_token_is_traded_for_an_access_token(monkeypatch):
    from src.clients.etsy_auth import TOKEN_URL
    monkeypatch.setenv("ETSY_KEYSTRING", "key")
    monkeypatch.setenv("ETSY_REFRESH_TOKEN", "123.refresh")
    responses.post(TOKEN_URL, json={"access_token": "123.access", "refresh_token": "123.refresh2", "expires_in": 3600})
    responses.get(f"{BASE_URL}/shops/77/receipts", json=load("etsy/shop_receipts.json"))
    EtsyRead().get_shop_receipts(77)
    assert "grant_type=refresh_token" in responses.calls[0].request.body
    assert responses.calls[1].request.headers["Authorization"] == "Bearer 123.access"


@responses.activate
def test_rejected_refresh_token_fails_closed(monkeypatch):
    from src.clients.base import AuthError
    from src.clients.etsy_auth import TOKEN_URL
    monkeypatch.setenv("ETSY_KEYSTRING", "key")
    monkeypatch.setenv("ETSY_REFRESH_TOKEN", "expired")
    responses.post(TOKEN_URL, status=400, json={"error": "invalid_grant"})
    with pytest.raises(AuthError, match="re-run tools/etsy_oauth.py"):
        EtsyRead("key", None)


def test_authorize_url_has_pkce_and_exact_scopes():
    from urllib.parse import parse_qs, urlparse
    from src.clients import etsy_auth as ea
    verifier, challenge = ea.new_pkce()
    assert 43 <= len(verifier) <= 128 and "=" not in challenge
    q = parse_qs(urlparse(ea.authorize_url("key", "https://localhost/callback", ea.SCOPES["read"], "st", challenge)).query)
    assert q["scope"] == ["shops_r listings_r transactions_r"] and q["code_challenge_method"] == ["S256"]
    assert q["client_id"] == ["key"] and q["state"] == ["st"]
    assert "listings_w" not in ea.SCOPES["read"]


def test_authorize_url_requires_https():
    from src.clients import etsy_auth as ea
    from src.clients.base import ClientError
    with pytest.raises(ClientError):
        ea.authorize_url("key", "http://localhost/cb", ["shops_r"], "st", "c")


def test_parse_redirect_checks_state():
    from src.clients import etsy_auth as ea
    from src.clients.base import AuthError
    assert ea.parse_redirect("https://localhost/callback?code=abc&state=st", "st") == "abc"
    with pytest.raises(AuthError, match="state"):
        ea.parse_redirect("https://localhost/callback?code=abc&state=other", "st")
    with pytest.raises(AuthError, match="access_denied"):
        ea.parse_redirect("https://localhost/callback?error=access_denied&state=st", "st")
    with pytest.raises(AuthError, match="no code"):
        ea.parse_redirect("https://localhost/callback?state=st", "st")


@responses.activate
def test_exchange_code_sends_verifier():
    from src.clients import etsy_auth as ea
    responses.post(ea.TOKEN_URL, json={"access_token": "1.a", "refresh_token": "1.r", "expires_in": 3600})
    out = ea.exchange_code("key", "https://localhost/callback", "abc", "ver")
    body = responses.calls[0].request.body
    assert "grant_type=authorization_code" in body and "code_verifier=ver" in body and out["refresh_token"] == "1.r"
