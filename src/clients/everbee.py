"""Read-only EverBee client.

Every number from here is an estimate (CLAUDE.md rule 5); results carry source and date.
Auth is the client_id / client_secret header pair. Quota headers (x-remaining-*) are tracked by
HttpClient: a per-second limit at 0 pauses, any other limit at 0 stops the run.

ASSUMPTION: EverBee's public API base URL and endpoint paths are not confirmed in this repo.
They are constructor arguments so they can be corrected without touching callers.
"""
from __future__ import annotations

import datetime as dt
import os
from typing import Any

from .base import HttpClient, require

DEFAULT_BASE_URL = "https://api.everbee.io"


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

    def keyword_research(self, keyword: str, path: str = "/v1/keyword_research") -> dict:
        return self.get(path, {"keyword": keyword})

    def product_analytics(self, keyword: str, path: str = "/v1/product_analytics") -> dict:
        return self.get(path, {"search_term": keyword})
