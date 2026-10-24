"""Read-only SerpApi Google Trends client. Values are estimates (CLAUDE.md rule 5)."""
from __future__ import annotations

import datetime as dt
import os
from typing import Any

from .base import HttpClient, require

BASE_URL = "https://serpapi.com"
TRENDING_HOURS = (4, 24, 48, 168)


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

    def trending_now(self, *, geo: str = "US", hours: int = 24, category_id: int | None = None) -> dict:
        """Google Trends "Trending Now" breakouts. Mostly news, sports and celebrities, so every
        query must pass the IP screen (docs/ip-screen.md) before it can seed a concept."""
        if hours not in TRENDING_HOURS:
            raise ValueError(f"hours must be one of {TRENDING_HOURS}")
        params = {"engine": "google_trends_trending_now", "geo": geo, "hours": hours, "api_key": self.api_key}
        if category_id is not None:
            params["category_id"] = category_id
        data = self.http.get_json("search.json", params=params)
        rows = [{"query": r.get("query"), "search_volume": r.get("search_volume"),
                 "increase_percentage": r.get("increase_percentage"), "active": r.get("active"),
                 "start_timestamp": r.get("start_timestamp"),
                 "categories": [c.get("name") for c in r.get("categories") or []],
                 "trend_breakdown": r.get("trend_breakdown") or []}
                for r in data.get("trending_searches") or []]
        return self._wrap(None, geo, f"past {hours}h", {"trending": rows},
                          source="serpapi_google_trends_trending_now")

    def autocomplete(self, q: str, *, gl: str = "us", hl: str = "en") -> dict:
        """Google search suggestions for a seed phrase (e.g. "funny plant mug")."""
        data = self.http.get_json("search.json", params={
            "engine": "google_autocomplete", "q": q, "gl": gl, "hl": hl, "api_key": self.api_key})
        rows = [{"value": r.get("value"), "relevance": r.get("relevance")}
                for r in data.get("suggestions") or [] if r.get("value")]
        return self._wrap(q, gl.upper(), None, {"suggestions": rows}, source="serpapi_google_autocomplete")

    @staticmethod
    def _wrap(q: str | None, geo: str, date: str | None, body: dict,
              source: str = "serpapi_google_trends") -> dict:
        return {"query": q, "geo": geo, "range": date, **body, "source": source,
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
