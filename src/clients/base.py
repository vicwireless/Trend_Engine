"""Shared HTTP behaviour for every client.

Fail closed (CLAUDE.md rule 8): 401/403 raise immediately, 429 retries with backoff that honors
Retry-After (rule 9) and raises once retries run out, any other non-2xx raises.
"""
from __future__ import annotations

import random
import time
from typing import Any, Callable, Mapping

import requests

DEFAULT_TIMEOUT = 30
USER_AGENT = "trend-engine/0.0.1"


class ClientError(RuntimeError):
    """Any failure the caller must stop on and report."""


class AuthError(ClientError):
    pass


class RateLimited(ClientError):
    pass


class QuotaExhausted(ClientError):
    pass


class MissingCredential(ClientError):
    pass


def require(value: str | None, name: str) -> str:
    if not value:
        raise MissingCredential(f"{name} is not set")
    return value


class HttpClient:
    """Thin wrapper over requests.Session with retry, backoff and quota tracking."""

    def __init__(
        self,
        base_url: str,
        headers: Mapping[str, str] | None = None,
        *,
        max_retries: int = 4,
        backoff_base: float = 1.0,
        max_wait: float = 120.0,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, **(headers or {})})
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.max_wait = max_wait
        self.sleep = sleep
        self.timeout = timeout
        self.remaining: dict[str, int] = {}

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        self._check_quota()
        url = path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)
        for attempt in range(self.max_retries + 1):
            resp = self.session.request(method, url, **kwargs)
            self._record_remaining(resp)
            if resp.status_code in (401, 403):
                raise AuthError(f"{method} {path} -> {resp.status_code}")
            if resp.status_code == 429:
                if attempt == self.max_retries:
                    raise RateLimited(f"{method} {path} -> 429 after {attempt + 1} attempts")
                self.sleep(self._wait_for(resp, attempt))
                continue
            if not resp.ok:
                raise ClientError(f"{method} {path} -> {resp.status_code}: {resp.text[:300]}")
            return resp
        raise RateLimited(f"{method} {path} exhausted retries")  # pragma: no cover

    def get_json(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", path, **kwargs).json()

    def _wait_for(self, resp: requests.Response, attempt: int) -> float:
        retry_after = resp.headers.get("Retry-After")
        if retry_after is not None:
            try:
                wait = float(retry_after)
            except ValueError:
                wait = self.backoff_base * 2**attempt
        else:
            wait = self.backoff_base * 2**attempt + random.uniform(0, self.backoff_base)
        if wait > self.max_wait:
            raise RateLimited(f"Retry-After {wait}s exceeds max wait {self.max_wait}s")
        return wait

    def _record_remaining(self, resp: requests.Response) -> None:
        for name, value in resp.headers.items():
            if name.lower().startswith("x-remaining-"):
                try:
                    self.remaining[name.lower()] = int(value)
                except ValueError:
                    continue

    def _check_quota(self) -> None:
        for name, value in self.remaining.items():
            if value > 0:
                continue
            if "second" in name:
                self.sleep(1.0)
                self.remaining[name] = 1
            else:
                raise QuotaExhausted(f"{name} is 0; stopping until it resets")
