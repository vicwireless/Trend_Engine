import json

import pytest
import responses

from src.clients.base import MissingCredential
from src.clients.etsy_read import BASE_URL, EtsyRead
from tests.conftest import load


@responses.activate
def test_find_active_listings_returns_price_and_favorites():
    responses.get(f"{BASE_URL}/listings/active", json=load("etsy/listings_active.json"))
    out = EtsyRead("key", None).find_active_listings("pickleball print", limit=3)
    assert responses.calls[0].request.headers["x-api-key"] == "key"
    assert "keywords=pickleball+print" in responses.calls[0].request.url
    assert out["count"] == 18342
    assert out["source"] == "etsy_open_api"
    assert out["results"][0] == {**out["results"][0], "price_usd": 12.99, "num_favorers": 412}
    assert out["results"][2]["price_usd"] is None  # non-USD prices are not mixed in


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
