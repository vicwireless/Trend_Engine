"""Read-only Printify catalog client: blueprints, print providers, variants, shipping."""
from __future__ import annotations

import os
from typing import Any

from .base import HttpClient, require

BASE_URL = "https://api.printify.com/v1"


class PrintifyCatalog:
    def __init__(self, token: str | None = None, **http_kwargs: Any):
        token = require(token or os.environ.get("PRINTIFY_READ_TOKEN"), "PRINTIFY_READ_TOKEN")
        self.http = HttpClient(BASE_URL, {"Authorization": f"Bearer {token}"}, **http_kwargs)

    def blueprints(self) -> list[dict]:
        return self.http.get_json("catalog/blueprints.json")

    def blueprint(self, blueprint_id: int) -> dict:
        return self.http.get_json(f"catalog/blueprints/{blueprint_id}.json")

    def print_providers(self, blueprint_id: int) -> list[dict]:
        return self.http.get_json(f"catalog/blueprints/{blueprint_id}/print_providers.json")

    def variants(self, blueprint_id: int, print_provider_id: int, *, show_out_of_stock: bool = False) -> list[dict]:
        data = self.http.get_json(
            f"catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json",
            params={"show-out-of-stock": int(show_out_of_stock)})
        return data.get("variants", [])

    def shipping(self, blueprint_id: int, print_provider_id: int) -> dict:
        return self.http.get_json(
            f"catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping.json")

    def shipping_cost_usd(self, blueprint_id: int, print_provider_id: int, variant_id: int,
                          country: str = "US") -> dict:
        """First-item and additional-item shipping for one variant, in USD."""
        for profile in self.shipping(blueprint_id, print_provider_id).get("profiles", []):
            if variant_id in profile.get("variant_ids", []) and country in profile.get("countries", []):
                return {
                    "first_item_usd": profile["first_item"]["cost"] / 100,
                    "additional_items_usd": profile["additional_items"]["cost"] / 100,
                }
        raise LookupError(f"No shipping profile for variant {variant_id} to {country}")
