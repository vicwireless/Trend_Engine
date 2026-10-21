"""Read-only EverBee client.

Every number from here is an estimate (CLAUDE.md rule 5); results carry source and date.
Auth is the client_id / client_secret header pair. Quota headers (x-remaining-*) are tracked by
HttpClient: a per-second limit at 0 pauses, any other limit at 0 stops the run.

Base URL, auth headers and paths are from the EverBee Research Open API guide and OpenAPI
document (https://research-open-api.everbee.com/docs/research-open-api-guide.html, read
2026-10-21). Limits: 10 QPS and 50,000 queries per rolling 24 h per client_id; quota headers are
x-remaining-this-second and x-remaining-today. Response field names are not pinned yet; callers
should read data defensively until a live response is captured as a fixture.
"""
from __future__ import annotations

import datetime as dt
import os
from typing import Any
from urllib.parse import quote

from .base import HttpClient, require

DEFAULT_BASE_URL = "https://research-open-api.everbee.com"


class EverBee:
    def __init__(self, client_id: str | None = None, client_secret: str | None = None, *,
                 base_url: str | None = None, backoff_base: float = 2.0, **http_kwargs: Any):
        cid = require(client_id or os.environ.get("EVERBEE_CLIENT_ID"), "EVERBEE_CLIENT_ID")
        secret = require(client_secret or os.environ.get("EVERBEE_CLIENT_SECRET"), "EVERBEE_CLIENT_SECRET")
        self.http = HttpClient(base_url or os.environ.get("EVERBEE_BASE_URL") or DEFAULT_BASE_URL,
                               {"client_id": cid, "client_secret": secret},
                               backoff_base=backoff_base, **http_kwargs)

    def get(self, path: str, params: dict | None = None) -> dict:
        data = self.http.get_json(path, params=params or {})
        return {
            "data": data,
            "source": "everbee",
            "is_estimate": True,
            "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "remaining": dict(self.http.remaining),
        }

    def keyword_research(self, keyword: str, **params: Any) -> dict:
        """GET /api/v1/keywords/{keyword}: suggestions and analytics for one keyword."""
        return self.get(f"/api/v1/keywords/{quote(keyword, safe='')}", params)

    def trending_keywords(self, **params: Any) -> dict:
        """GET /api/v1/keywords: default or trending keyword suggestions."""
        return self.get("/api/v1/keywords", params)

    def product_analytics(self, keyword: str, **params: Any) -> dict:
        """GET /api/v1/listings filtered by title_include: top-listing sales estimates."""
        return self.get("/api/v1/listings", {"title_include": keyword, **params})
