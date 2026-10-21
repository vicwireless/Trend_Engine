import hashlib
import io
import json

import responses
from PIL import Image

from src.clients.image_gen import ImageGen
from tests.conftest import load

URL = "https://images.test/v1/generate"


@responses.activate
def test_generate_base64_writes_provenance(tmp_path):
    responses.post(URL, json=load("image_gen/response_b64.json"))
    gen = ImageGen("key", api_url=URL, model="m1", provider="p1")
    out = gen.generate("textured autumn pickleball court, gouache", seed=42, width=8, height=8,
                       out_path=tmp_path / "con-1" / "draft.png", concept_id="con-1")
    sent = json.loads(responses.calls[0].request.body)
    assert sent == {"prompt": "textured autumn pickleball court, gouache", "seed": 42, "width": 8, "height": 8, "model": "m1"}
    img_path = tmp_path / "con-1" / "draft.png"
    assert Image.open(img_path).size == (8, 8)
    prov = json.loads((tmp_path / "con-1" / "draft.prompt.json").read_text())
    assert prov["seed"] == 42 and prov["prompt"].startswith("textured") and prov["ai_assisted"] is True
    assert prov["size"] == {"width": 8, "height": 8} and prov["provider"] == "p1" and prov["model"] == "m1"
    assert prov["sha256"] == hashlib.sha256(img_path.read_bytes()).hexdigest()
    assert out["provenance_path"].endswith("draft.prompt.json")


@responses.activate
def test_generate_raw_bytes(tmp_path):
    buf = io.BytesIO()
    Image.new("RGB", (4, 4)).save(buf, "PNG")
    responses.post(URL, body=buf.getvalue(), content_type="image/png")
    ImageGen("key", api_url=URL).generate("p", seed=1, width=4, height=4, out_path=tmp_path / "a.png")
    assert (tmp_path / "a.png").read_bytes() == buf.getvalue()
    assert (tmp_path / "a.prompt.json").exists()
