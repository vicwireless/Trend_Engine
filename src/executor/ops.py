"""Allowlisted write operations. Nothing outside OPS can be executed.

Each op takes (payload, ctx) with $refs already resolved, performs one external write, reads the
resource back, and returns {"result": {...ids...}, "readback_ok": bool, "readback": {...}}.
Credentials come only from the process environment, which the executor workflow fills from
GitHub Actions secrets.
"""
from __future__ import annotations

import mimetypes
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from src.clients import etsy_auth
from src.clients.base import HttpClient, require

ETSY_BASE = "https://openapi.etsy.com/v3/application"
PRINTIFY_BASE = "https://api.printify.com/v1"
PINTEREST_BASE = "https://api.pinterest.com/v5"


class OpDisabled(RuntimeError):
    pass


class PreconditionFailed(RuntimeError):
    """Raised before any write when live state makes the op unsafe. Nothing was written."""


@dataclass
class Context:
    root: Path
    config: dict
    http_kwargs: dict = field(default_factory=dict)
    _clients: dict = field(default_factory=dict)

    def _client(self, name: str, factory: Callable[[], HttpClient]) -> HttpClient:
        if name not in self._clients:
            self._clients[name] = factory()
        return self._clients[name]

    @property
    def etsy(self) -> HttpClient:
        return self._client("etsy", lambda: HttpClient(ETSY_BASE, {
            "x-api-key": etsy_auth.api_key(),
            "Authorization": "Bearer " + require(
                etsy_auth.access_token("ETSY_WRITE_TOKEN", "ETSY_WRITE_REFRESH_TOKEN"), "ETSY_WRITE_TOKEN"),
        }, **self.http_kwargs))

    @property
    def etsy_shop(self) -> str:
        return require(os.environ.get("ETSY_SHOP_ID"), "ETSY_SHOP_ID")

    @property
    def printify(self) -> HttpClient:
        return self._client("printify", lambda: HttpClient(PRINTIFY_BASE, {
            "Authorization": "Bearer " + require(os.environ.get("PRINTIFY_WRITE_TOKEN"), "PRINTIFY_WRITE_TOKEN"),
        }, **self.http_kwargs))

    @property
    def printify_shop(self) -> str:
        return require(os.environ.get("PRINTIFY_SHOP_ID"), "PRINTIFY_SHOP_ID")

    @property
    def pinterest(self) -> HttpClient:
        return self._client("pinterest", lambda: HttpClient(PINTEREST_BASE, {
            "Authorization": "Bearer " + require(os.environ.get("PINTEREST_TOKEN"), "PINTEREST_TOKEN"),
        }, **self.http_kwargs))

    @property
    def payhip(self) -> HttpClient:
        base = (self.config.get("payhip") or {}).get("api_base_url")
        if not base:
            raise OpDisabled("payhip.api_base_url is not configured")
        return self._client("payhip", lambda: HttpClient(base, {
            "payhip-api-key": require(os.environ.get("PAYHIP_API_KEY"), "PAYHIP_API_KEY"),
        }, **self.http_kwargs))

    def file(self, rel: str) -> Path:
        path = (self.root / rel).resolve()
        if not path.is_relative_to(self.root.resolve()):
            raise ValueError(f"{rel} is outside the repo")
        return path


def _cents(usd: float) -> int:
    return int(round(usd * 100))


def _etsy_price(listing: dict) -> float | None:
    p = listing.get("price")
    return None if not p else round(p["amount"] / p["divisor"], 2)


# ---------------------------------------------------------------- Etsy

def etsy_create_digital_listing(p: dict, ctx: Context) -> dict:
    data = {
        "quantity": p.get("quantity", 999),
        "title": p["title"],
        "description": p["description"],
        "price": p["price_usd"],
        "who_made": p["who_made"],
        "when_made": p["when_made"],
        "taxonomy_id": p["taxonomy_id"],
        "type": "download",
        "is_supply": "false",
        "tags": ",".join(p["tags"]),
    }
    created = ctx.etsy.request("POST", f"shops/{ctx.etsy_shop}/listings", data=data).json()
    listing_id = created["listing_id"]

    prop = (ctx.config.get("etsy") or {}).get("ai_disclosure_property") or {}
    if p["ai_assisted"] and prop.get("property_id"):
        ctx.etsy.request("PUT", f"shops/{ctx.etsy_shop}/listings/{listing_id}/properties/{prop['property_id']}",
                         data={"value_ids": ",".join(map(str, prop.get("value_ids", []))),
                               "values": ",".join(prop.get("values", []))})

    rb = ctx.etsy.get_json(f"listings/{listing_id}")
    ok = rb.get("title") == p["title"] and _etsy_price(rb) == round(p["price_usd"], 2) and rb.get("state") == "draft"
    return {"result": {"listing_id": listing_id}, "readback_ok": ok,
            "readback": {"title": rb.get("title"), "price_usd": _etsy_price(rb), "state": rb.get("state")}}


def _content_type(path) -> str:
    return mimetypes.guess_type(str(path))[0] or "application/octet-stream"


def etsy_upload_file(p: dict, ctx: Context) -> dict:
    lid = p["listing_id"]
    path = ctx.file(p["path"])
    with open(path, "rb") as f:
        created = ctx.etsy.request("POST", f"shops/{ctx.etsy_shop}/listings/{lid}/files",
                                   data={"name": p["name"]},
                                   files={"file": (p["name"], f, _content_type(path))}).json()
    fid = created["listing_file_id"]
    rb = ctx.etsy.get_json(f"shops/{ctx.etsy_shop}/listings/{lid}/files/{fid}")
    ok = rb.get("listing_file_id") == fid and rb.get("filename") == p["name"]
    return {"result": {"listing_id": lid, "listing_file_id": fid}, "readback_ok": ok,
            "readback": {"filename": rb.get("filename"), "filesize": rb.get("filesize")}}


def etsy_upload_image(p: dict, ctx: Context) -> dict:
    lid = p["listing_id"]
    path = ctx.file(p["path"])
    data = {"rank": p["rank"]}
    if p.get("alt_text"):
        data["alt_text"] = p["alt_text"]
    with open(path, "rb") as f:
        created = ctx.etsy.request("POST", f"shops/{ctx.etsy_shop}/listings/{lid}/images",
                                   data=data, files={"image": (path.name, f)}).json()
    iid = created["listing_image_id"]
    rb = ctx.etsy.get_json(f"listings/{lid}/images/{iid}")
    ok = rb.get("listing_image_id") == iid and rb.get("rank") == p["rank"]
    return {"result": {"listing_id": lid, "listing_image_id": iid}, "readback_ok": ok,
            "readback": {"rank": rb.get("rank")}}


def _set_state(p: dict, ctx: Context, state: str) -> dict:
    lid = p["listing_id"]
    ctx.etsy.request("PATCH", f"shops/{ctx.etsy_shop}/listings/{lid}", data={"state": state})
    rb = ctx.etsy.get_json(f"listings/{lid}")
    return {"result": {"listing_id": lid}, "readback_ok": rb.get("state") == state,
            "readback": {"state": rb.get("state")}}


def etsy_activate_listing(p: dict, ctx: Context) -> dict:
    return _set_state(p, ctx, "active")


def etsy_deactivate_listing(p: dict, ctx: Context) -> dict:
    return _set_state(p, ctx, "inactive")


def etsy_update_price(p: dict, ctx: Context) -> dict:
    lid = p["listing_id"]
    inv = ctx.etsy.get_json(f"listings/{lid}/inventory")
    max_pct = ctx.config.get("price_change_max_pct", 0.10)
    for current in {_etsy_price(o) for prod in inv.get("products", []) for o in prod.get("offerings", [])}:
        if current and abs(p["price_usd"] / current - 1) > max_pct + 1e-9:
            raise PreconditionFailed(f"listing {lid}: ${current:.2f} -> ${p['price_usd']:.2f} exceeds "
                                     f"the ±{max_pct:.0%} price step")
    body = {
        "products": [{
            "sku": prod.get("sku", ""),
            "property_values": [{k: pv.get(k) for k in ("property_id", "value_ids", "scale_id", "property_name", "values")}
                                for pv in prod.get("property_values", [])],
            "offerings": [{"price": p["price_usd"], "quantity": o["quantity"], "is_enabled": o["is_enabled"]}
                          for o in prod.get("offerings", [])],
        } for prod in inv.get("products", [])],
        "price_on_property": inv.get("price_on_property", []),
        "quantity_on_property": inv.get("quantity_on_property", []),
        "sku_on_property": inv.get("sku_on_property", []),
    }
    ctx.etsy.request("PUT", f"listings/{lid}/inventory", json=body)
    rb = ctx.etsy.get_json(f"listings/{lid}/inventory")
    prices = {_etsy_price(o) for prod in rb.get("products", []) for o in prod.get("offerings", [])}
    return {"result": {"listing_id": lid}, "readback_ok": prices == {round(p["price_usd"], 2)},
            "readback": {"prices_usd": sorted(x for x in prices if x is not None)}}


# ---------------------------------------------------------------- Printify

def printify_create_product(p: dict, ctx: Context) -> dict:
    body = {
        "title": p["title"],
        "description": p["description"],
        "tags": p.get("tags", []),
        "blueprint_id": p["blueprint_id"],
        "print_provider_id": p["print_provider_id"],
        "variants": [{"id": v["id"], "price": _cents(v["price_usd"]), "is_enabled": v.get("is_enabled", True)}
                     for v in p["variants"]],
        "print_areas": p["print_areas"],
    }
    created = ctx.printify.request("POST", f"shops/{ctx.printify_shop}/products.json", json=body).json()
    pid = created["id"]
    rb = ctx.printify.get_json(f"shops/{ctx.printify_shop}/products/{pid}.json")
    want = {v["id"]: _cents(v["price_usd"]) for v in p["variants"]}
    got = {v["id"]: v.get("price") for v in rb.get("variants", []) if v["id"] in want}
    ok = rb.get("title") == p["title"] and got == want
    return {"result": {"product_id": pid}, "readback_ok": ok,
            "readback": {"title": rb.get("title"), "variant_prices_cents": got}}


def printify_publish(p: dict, ctx: Context) -> dict:
    pid = p["product_id"]
    flags = {k: p.get(k, True) for k in ("title", "description", "images", "variants", "tags")}
    flags.update({"keyFeatures": True, "shipping_template": True})
    ctx.printify.request("POST", f"shops/{ctx.printify_shop}/products/{pid}/publish.json", json=flags)
    rb = ctx.printify.get_json(f"shops/{ctx.printify_shop}/products/{pid}.json")
    # Publishing is asynchronous: a locked product or an external id means it was accepted.
    ok = bool(rb.get("is_locked") or rb.get("external"))
    return {"result": {"product_id": pid, "external": rb.get("external")}, "readback_ok": ok,
            "readback": {"is_locked": rb.get("is_locked"), "external": rb.get("external")}}


# ---------------------------------------------------------------- Pinterest

def pinterest_create_pin(p: dict, ctx: Context) -> dict:
    body = {
        "board_id": p["board_id"],
        "title": p["title"],
        "description": p.get("description", ""),
        "link": p["link"],
        "media_source": {"source_type": "image_url", "url": p["image_url"]},
    }
    if p.get("alt_text"):
        body["alt_text"] = p["alt_text"]
    created = ctx.pinterest.request("POST", "pins", json=body).json()
    pin_id = created["id"]
    rb = ctx.pinterest.get_json(f"pins/{pin_id}")
    ok = rb.get("link") == p["link"] and rb.get("board_id") == p["board_id"]
    return {"result": {"pin_id": pin_id}, "readback_ok": ok,
            "readback": {"link": rb.get("link"), "board_id": rb.get("board_id")}}


# ---------------------------------------------------------------- Payhip

def payhip_create_product(p: dict, ctx: Context) -> dict:
    """ASSUMPTION: Payhip's product-create API is unconfirmed. Disabled until configured."""
    client = ctx.payhip
    path = ctx.file(p["path"])
    with open(path, "rb") as f:
        created = client.request("POST", "products", data={
            "name": p["name"], "description": p["description"], "price": p["price_usd"]},
            files={"file": (path.name, f)}).json()
    pid = str(created["id"])
    rb = client.get_json(f"products/{pid}")
    ok = rb.get("name") == p["name"]
    return {"result": {"product_id": pid}, "readback_ok": ok, "readback": {"name": rb.get("name")}}


OPS: dict[str, Callable[[dict, Context], dict]] = {
    "etsy_create_digital_listing": etsy_create_digital_listing,
    "etsy_upload_file": etsy_upload_file,
    "etsy_upload_image": etsy_upload_image,
    "etsy_activate_listing": etsy_activate_listing,
    "etsy_update_price": etsy_update_price,
    "etsy_deactivate_listing": etsy_deactivate_listing,
    "printify_create_product": printify_create_product,
    "printify_publish": printify_publish,
    "pinterest_create_pin": pinterest_create_pin,
    "payhip_create_product": payhip_create_product,
}

# Ops that put a new sellable listing in front of buyers (counted against max_new_listings_per_week).
NEW_LISTING_OPS = {"etsy_create_digital_listing", "printify_publish", "payhip_create_product"}
# Ops that create a POD candidate (counted against max_pod_candidates_per_week).
POD_CANDIDATE_OPS = {"printify_create_product"}
