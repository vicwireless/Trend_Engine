"""Read-only SerpApi Google Trends client. Values are estimates (CLAUDE.md rule 5)."""
from __future__ import annotations

import datetime as dt
import os
from typing import Any

from .base import HttpClient, require

BASE_URL = "https://serpapi.com"


class SerpApiTrends:
    def __init__(self, api_key: str | None = None, **http_kwargs: Any):
        self.api_key = require(api_key or os.environ.get("SERPAPI_KEY"), "SERPAPI_KEY")
        self.http = HttpClient(BASE_URL, **http_kwargs)

    def _search(self, q: str, data_type: str, geo: str, date: str) -> dict:
        return self.http.get_json("search.json", params={
            "engine": "google_trends", "q": q, "data_type": data_type,
            "geo": geo, "date": date, "api_key": self.api_key})

    def interest_over_time(self, q: str, *, geo: str = "US", date: str = "today 12-m") -> dict:
        data = self._search(q, "TIMESERIES", geo, date)
        points = []
        for row in (data.get("interest_over_time") or {}).get("timeline_data", []):
            value = next((v.get("extracted_value") for v in row.get("values", [])), None)
            points.append({"date": row.get("date"), "timestamp": row.get("timestamp"), "value": value})
        return self._wrap(q, geo, date, {"points": points})

    def related_queries(self, q: str, *, geo: str = "US", date: str = "today 12-m") -> dict:
        data = self._search(q, "RELATED_QUERIES", geo, date)
        rq = data.get("related_queries") or {}
        slim = lambda rows: [{"query": r.get("query"), "value": r.get("extracted_value")} for r in rows or []]
        return self._wrap(q, geo, date, {"rising": slim(rq.get("rising")), "top": slim(rq.get("top"))})

    @staticmethod
    def _wrap(q: str, geo: str, date: str, body: dict) -> dict:
        return {"query": q, "geo": geo, "range": date, **body, "source": "serpapi_google_trends",
                "is_estimate": True,
                "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}


def momentum(points: list[dict], window: int = 12) -> float | None:
    """Mean of the last `window` points over the mean of the `window` before, minus 1."""
    values = [p["value"] for p in points if p.get("value") is not None]
    if len(values) < 2 * window:
        return None
    recent, prior = values[-window:], values[-2 * window:-window]
    base = sum(prior) / window
    return None if base == 0 else round(sum(recent) / window / base - 1, 4)
