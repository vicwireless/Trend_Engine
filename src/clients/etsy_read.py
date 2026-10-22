"""Read-only Etsy Open API v3 client.

Numbers from here may be labelled "Etsy data" (CLAUDE.md rule 5). Receipts are stripped of buyer
identity before they leave this module (rule 4).
"""
from __future__ import annotations

import os
from typing import Any

from .base import HttpClient, require
from .etsy_auth import access_token, api_key

BASE_URL = "https://openapi.etsy.com/v3/application"

# Only these receipt / transaction fields survive. Everything else (name, address, email,
# buyer_user_id, messages) is dropped.
RECEIPT_FIELDS = ("receipt_id", "create_timestamp", "status", "is_paid", "is_shipped")
TRANSACTION_FIELDS = ("transaction_id", "listing_id", "product_id", "quantity", "sku", "is_digital")
PERSONALIZATION_KEYS = ("personalization", "personalisation")


def money(m: dict | None) -> float | None:
    if not m:
        return None
    return round(m["amount"] / m["divisor"], 2)


class EtsyRead:
    def __init__(self, keystring: str | None = None, read_token: str | None = None,
                 shared_secret: str | None = None, **http_kwargs: Any):
        headers = {"x-api-key": api_key(keystring, shared_secret)}
        token = read_token or access_token("ETSY_READ_TOKEN", "ETSY_REFRESH_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.http = HttpClient(BASE_URL, headers, **http_kwargs)
        self._has_token = bool(token)

    def find_active_listings(self, keywords: str, *, limit: int = 100, offset: int = 0,
                             sort_on: str = "score") -> dict:
        """findAllListingsActive. Returns total count and slim rows with price and favorites."""
        data = self.http.get_json("listings/active", params={
            "keywords": keywords, "limit": limit, "offset": offset, "sort_on": sort_on})
        rows = [{
            "listing_id": r["listing_id"],
            "title": r.get("title"),
            "price_usd": money(r.get("price")) if (r.get("price") or {}).get("currency_code", "USD") == "USD" else None,
            "currency_code": (r.get("price") or {}).get("currency_code"),
            "num_favorers": r.get("num_favorers"),
            "shop_id": r.get("shop_id"),
            "tags": r.get("tags", []),
            "type": r.get("type"),
            "created_timestamp": r.get("created_timestamp"),
        } for r in data.get("results", [])]
        return {"count": data.get("count", 0), "results": rows, "source": "etsy_open_api"}

    def get_shop_receipts(self, shop_id: int | str, *, limit: int = 100, offset: int = 0,
                          min_created: int | None = None) -> list[dict]:
        """getShopReceipts with buyer identity removed. Needs an OAuth token with transactions_r."""
        require("x" if self._has_token else None, "ETSY_READ_TOKEN")
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if min_created:
            params["min_created"] = min_created
        data = self.http.get_json(f"shops/{shop_id}/receipts", params=params)
        return [sanitize_receipt(r) for r in data.get("results", [])]

    def get_listing_stats(self, listing_id: int | str) -> dict:
        """getListing. Views are returned only when Etsy includes them; otherwise None."""
        r = self.http.get_json(f"listings/{listing_id}")
        return {
            "listing_id": r["listing_id"],
            "state": r.get("state"),
            "views": r.get("views"),
            "num_favorers": r.get("num_favorers"),
            "price_usd": money(r.get("price")),
            "source": "etsy_open_api",
        }


def sanitize_receipt(r: dict) -> dict:
    out = {k: r.get(k) for k in RECEIPT_FIELDS}
    out["grandtotal_usd"] = money(r.get("grandtotal"))
    out["subtotal_usd"] = money(r.get("subtotal"))
    out["total_shipping_cost_usd"] = money(r.get("total_shipping_cost"))
    out["discount_amt_usd"] = money(r.get("discount_amt"))
    txs = []
    for t in r.get("transactions", []):
        tx = {k: t.get(k) for k in TRANSACTION_FIELDS}
        tx["price_usd"] = money(t.get("price"))
        tx["shipping_cost_usd"] = money(t.get("shipping_cost"))
        tx["personalization_text"] = next(
            (v.get("formatted_value") for v in t.get("variations", [])
             if any(p in str(v.get("formatted_name", "")).lower() for p in PERSONALIZATION_KEYS)),
            None)
        txs.append(tx)
    out["transactions"] = txs
    return out
