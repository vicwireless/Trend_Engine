#!/usr/bin/env python3
"""One-time Etsy sign-in. Run on your own computer; nothing is sent anywhere but Etsy.

    python tools/etsy_oauth.py --mode read     # engine: shops_r listings_r transactions_r
    python tools/etsy_oauth.py --mode write    # executor: shops_r listings_r listings_w

Needs ETSY_KEYSTRING and ETSY_SHARED_SECRET in the environment (or a .env file) and a callback URL
registered on your Etsy app that exactly matches --redirect-uri. The page the browser lands on after
approval may fail to load; that is fine. Copy its full address from the address bar and paste it here.

Tokens are written to .etsy_tokens_<mode>.json (gitignored, owner-only). They are never printed.
Etsy refresh tokens last 90 days: run this again before then.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.clients import etsy_auth  # noqa: E402
from src.clients.base import ClientError  # noqa: E402


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=sorted(etsy_auth.SCOPES), required=True)
    ap.add_argument("--redirect-uri", default=os.environ.get("ETSY_REDIRECT_URI", "https://localhost/callback"))
    args = ap.parse_args(argv)

    load_dotenv(ROOT / ".env")
    keystring = os.environ.get("ETSY_KEYSTRING")
    if not keystring:
        print("ETSY_KEYSTRING is not set (put it in .env, which git ignores).", file=sys.stderr)
        return 1

    verifier, challenge = etsy_auth.new_pkce()
    state = secrets.token_urlsafe(16)
    scopes = etsy_auth.SCOPES[args.mode]
    url = etsy_auth.authorize_url(keystring, args.redirect_uri, scopes, state, challenge)
    print(f"\nMode: {args.mode}. Scopes: {', '.join(scopes)}\n")
    print("1. Open this address in the browser where you're signed in to Etsy and click Allow access:\n")
    print(url + "\n")
    print("2. The next page may not load. Copy the FULL address from the address bar and paste it below.\n")
    try:
        code = etsy_auth.parse_redirect(input("Pasted address: "), state)
        tokens = etsy_auth.exchange_code(keystring, args.redirect_uri, code, verifier)
    except ClientError as e:
        print(f"\nStopped: {e}", file=sys.stderr)
        return 1

    user_id = tokens["access_token"].split(".")[0]
    shop_id = None
    try:
        key = etsy_auth.api_key(keystring, os.environ.get("ETSY_SHARED_SECRET"))
        r = requests.get(f"https://openapi.etsy.com/v3/application/users/{user_id}/shops",
                         headers={"x-api-key": key, "Authorization": f"Bearer {tokens['access_token']}"}, timeout=30)
        if r.ok:
            shop_id = r.json().get("shop_id")
            print(f"Signed in. Shop: {r.json().get('shop_name')} (id {shop_id}).")
        else:
            print(f"Signed in, but the shop lookup returned {r.status_code}; the tokens are still saved.")
    except ClientError as e:
        print(f"Signed in. Shop lookup skipped: {e}")

    out = ROOT / f".etsy_tokens_{args.mode}.json"
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"mode": args.mode, "scopes": scopes, "refresh_token": tokens["refresh_token"],
                   "access_token_1h": tokens["access_token"], "shop_id": shop_id,
                   "refresh_valid_days": 90}, f, indent=2)
    secret = "ETSY_REFRESH_TOKEN" if args.mode == "read" else "ETSY_WRITE_REFRESH_TOKEN"
    print(f"\nSaved to {out.name}. Copy the refresh_token value into the GitHub secret {secret}"
          + (" and shop_id into ETSY_SHOP_ID" if args.mode == "write" else "")
          + ", then delete the file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
