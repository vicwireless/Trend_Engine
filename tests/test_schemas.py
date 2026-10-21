import json
import re
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
RECORDS = ["signal", "concept", "asset", "listing", "cohort", "order", "release_manifest"]


def doc_fields(record: str) -> set[str]:
    text = (ROOT / "docs" / "data-model.md").read_text()
    section = re.search(rf"^## {record}\n(.*?)(?=^## |\Z)", text, re.S | re.M).group(1)
    fields = set()
    for row in re.findall(r"^\| (`[^|]+) \|", section, re.M):
        fields.update(re.findall(r"`([a-z_0-9]+)`", row))
    return fields


@pytest.mark.parametrize("path", sorted(SCHEMAS.rglob("*.json")), ids=lambda p: p.stem)
def test_schema_is_valid(path):
    jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text()))


@pytest.mark.parametrize("record", RECORDS)
def test_schema_mirrors_data_model(record):
    props = set(json.loads((SCHEMAS / f"{record}.json").read_text())["properties"])
    assert doc_fields(record) == props


def test_order_schema_forbids_pii():
    schema = json.loads((SCHEMAS / "order.json").read_text())
    v = jsonschema.Draft202012Validator(schema)
    order = {"order_id": "1", "channel": "etsy", "created_at": "2026-10-21T00:00:00Z", "listing_id": None,
             "external_listing_id": "1001", "quantity": 1, "item_price_usd": 12.99, "shipping_usd": 0,
             "discount_usd": 0, "cogs_usd": None, "personalization_text": None, "cohort_id": None}
    assert v.is_valid(order)
    assert not v.is_valid({**order, "buyer_email": "a@b.c"})
