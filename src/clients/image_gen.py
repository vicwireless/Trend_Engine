"""Image generation client with prompt provenance.

Every output is written with a sibling `<name>.prompt.json` recording prompt, seed, size, provider,
model and the output hash, and is flagged ai_assisted=true (CLAUDE.md rule 2).

ASSUMPTION: the image provider is not chosen yet. The client posts JSON
{prompt, seed, width, height, model} to IMAGE_API_URL and accepts either raw image bytes or JSON
with base64 at `image_base64` or `data[0].b64_json`. Adjust `_extract` once a provider is picked.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .base import ClientError, HttpClient, require


class ImageGen:
    def __init__(self, api_key: str | None = None, *, api_url: str | None = None,
                 model: str | None = None, provider: str | None = None, **http_kwargs: Any):
        key = require(api_key or os.environ.get("IMAGE_API_KEY"), "IMAGE_API_KEY")
        self.api_url = require(api_url or os.environ.get("IMAGE_API_URL"), "IMAGE_API_URL")
        self.model = model or os.environ.get("IMAGE_MODEL", "default")
        self.provider = provider or os.environ.get("IMAGE_PROVIDER", "unspecified")
        self.http = HttpClient(self.api_url, {"Authorization": f"Bearer {key}"}, **http_kwargs)

    def generate(self, prompt: str, *, seed: int, width: int, height: int, out_path: str | Path,
                 negative_prompt: str | None = None, concept_id: str | None = None) -> dict:
        body = {"prompt": prompt, "seed": seed, "width": width, "height": height, "model": self.model}
        if negative_prompt:
            body["negative_prompt"] = negative_prompt
        resp = self.http.request("POST", self.api_url, json=body)
        image = self._extract(resp)

        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(image)
        provenance = {
            "output": out_path.name,
            "sha256": hashlib.sha256(image).hexdigest(),
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "size": {"width": width, "height": height},
            "provider": self.provider,
            "model": self.model,
            "concept_id": concept_id,
            "ai_assisted": True,
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        }
        prov_path = provenance_path(out_path)
        prov_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
        return {"path": str(out_path), "provenance_path": str(prov_path), **provenance}

    @staticmethod
    def _extract(resp) -> bytes:
        if resp.headers.get("Content-Type", "").startswith("image/"):
            return resp.content
        data = resp.json()
        b64 = data.get("image_base64") or ((data.get("data") or [{}])[0]).get("b64_json")
        if not b64:
            raise ClientError("image response had no image data")
        return base64.b64decode(b64)


def provenance_path(out_path: Path) -> Path:
    return out_path.with_name(out_path.stem + ".prompt.json")
