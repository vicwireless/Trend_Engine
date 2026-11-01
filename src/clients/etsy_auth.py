"""Etsy OAuth for the engine and executor: API key header and access-token refresh.

Etsy access tokens last 1 hour and refresh tokens 90 days, so secrets hold the refresh token and
each run trades it for an access token. Re-run tools/etsy_oauth.py before the 90 days are up.
Docs: https://developer.etsy.com/documentation/essentials/authentication/
"""
from __future__ import annotations

import os

import requests

from .base import AuthError, ClientError, require

TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"


def api_key(keystring: str | None = None, shared_secret: str | None = None) -> str:
    """Etsy wants `x-api-key: <keystring>:<shared secret>` on every request."""
    k = require(keystring or os.environ.get("ETSY_KEYSTRING"), "ETSY_KEYSTRING")
    s = require(shared_secret or os.environ.get("ETSY_SHARED_SECRET"), "ETSY_SHARED_SECRET")
    return f"{k}:{s}"


def refresh_tokens(keystring: str, refresh_token: str, *, session: requests.Session | None = None,
                   timeout: float = 30) -> tuple[str, str | None]:
    """(access_token, new_refresh_token). Etsy rotates the refresh token on every refresh and revokes
    a reused old one (observed 2026-11-01), so callers that run again later must keep the new one."""
    resp = (session or requests).post(TOKEN_URL, data={
        "grant_type": "refresh_token", "client_id": keystring, "refresh_token": refresh_token}, timeout=timeout)
    if resp.status_code in (400, 401, 403):
        try:  # Etsy's reason, e.g. "invalid_grant: refresh_token is revoked". Never echoes the token.
            body = resp.json()
            reason = f" ({body.get('error')}: {body.get('error_description')})"
        except ValueError:
            reason = ""
        raise AuthError(f"Etsy token refresh -> {resp.status_code}{reason}; re-run tools/etsy_oauth.py")
    if not resp.ok:
        raise ClientError(f"Etsy token refresh -> {resp.status_code}")
    body = resp.json()
    token = body.get("access_token")
    if not token:
        raise AuthError("Etsy token refresh returned no access_token")
    return token, body.get("refresh_token")


def refresh_access_token(keystring: str, refresh_token: str, *, session: requests.Session | None = None,
                         timeout: float = 30) -> str:
    return refresh_tokens(keystring, refresh_token, session=session, timeout=timeout)[0]


ROTATED_FILE_VAR = "ETSY_ROTATED_REFRESH_FILE"


def access_token(token_var: str, refresh_var: str) -> str | None:
    """An access token from `token_var`, else one refreshed from `refresh_var`, else None.

    If ETSY_ROTATED_REFRESH_FILE is set (the metrics workflow sets it), the refresh token is read from
    that file when it exists and the rotated one Etsy returns is written back to it (mode 0600), so a
    second process in the same run uses the new token and the workflow can save it to the secret.
    The rotated token also replaces `refresh_var` in this process's environment.
    """
    if os.environ.get(token_var):
        return os.environ[token_var]
    rotated = os.environ.get(ROTATED_FILE_VAR)
    refresh = None
    if rotated and os.path.exists(rotated):
        with open(rotated, encoding="utf-8") as f:
            refresh = f.read().strip() or None
    refresh = refresh or (os.environ.get(refresh_var) or "").strip() or None
    if not refresh:
        return None
    token, new_refresh = refresh_tokens(require(os.environ.get("ETSY_KEYSTRING"), "ETSY_KEYSTRING"), refresh)
    if new_refresh and new_refresh != refresh:
        os.environ[refresh_var] = new_refresh
        if rotated:
            fd = os.open(rotated, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(new_refresh)
    return token


# --- One-time sign-in (tools/etsy_oauth.py). Authorization code flow with PKCE (S256). ---
AUTHORIZE_URL = "https://www.etsy.com/oauth/connect"
SCOPES = {
    "read": ["shops_r", "listings_r", "transactions_r"],
    "write": ["shops_r", "listings_r", "listings_w"],
}


def new_pkce() -> tuple[str, str]:
    """(verifier, challenge): 43–128 chars from [A-Za-z0-9._~-], challenge = base64url(sha256)."""
    import base64
    import hashlib
    import secrets
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


def authorize_url(keystring: str, redirect_uri: str, scopes: list[str], state: str, challenge: str) -> str:
    from urllib.parse import quote, urlencode
    if not redirect_uri.startswith("https://"):
        raise ClientError("Etsy requires an https:// redirect URI")
    return AUTHORIZE_URL + "?" + urlencode({
        "response_type": "code", "client_id": keystring, "redirect_uri": redirect_uri,
        "scope": " ".join(scopes), "state": state, "code_challenge": challenge,
        "code_challenge_method": "S256"}, quote_via=quote)


def parse_redirect(pasted: str, expected_state: str) -> str:
    """The `code` from the URL the browser landed on after approval. Fails closed on a state mismatch."""
    from urllib.parse import parse_qs, urlparse
    query = parse_qs(urlparse(pasted.strip()).query)
    if "error" in query:
        raise AuthError(f"Etsy returned an error: {query['error'][0]}")
    if query.get("state", [None])[0] != expected_state:
        raise AuthError("state does not match this sign-in; start again")
    code = query.get("code", [None])[0]
    if not code:
        raise AuthError("no code in the pasted URL")
    return code


def exchange_code(keystring: str, redirect_uri: str, code: str, verifier: str, *,
                  session: requests.Session | None = None, timeout: float = 30) -> dict:
    resp = (session or requests).post(TOKEN_URL, data={
        "grant_type": "authorization_code", "client_id": keystring, "redirect_uri": redirect_uri,
        "code": code, "code_verifier": verifier}, timeout=timeout)
    if not resp.ok:
        raise AuthError(f"Etsy code exchange -> {resp.status_code}: {resp.text[:200]}")
    body = resp.json()
    if not body.get("access_token") or not body.get("refresh_token"):
        raise AuthError("Etsy code exchange returned no tokens")
    return body
