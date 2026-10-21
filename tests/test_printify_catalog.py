import pytest
import responses

from src.clients.printify_catalog import BASE_URL, PrintifyCatalog
from tests.conftest import load


@pytest.fixture
def pf():
    return PrintifyCatalog("tok")


@responses.activate
def test_blueprints_and_providers(pf):
    responses.get(f"{BASE_URL}/catalog/blueprints.json", json=load("printify/blueprints.json"))
    responses.get(f"{BASE_URL}/catalog/blueprints/6/print_providers.json", json=load("printify/print_providers.json"))
    assert [b["id"] for b in pf.blueprints()] == [6, 68]
    assert pf.print_providers(6)[0]["id"] == 99
    assert responses.calls[0].request.headers["Authorization"] == "Bearer tok"


@responses.activate
def test_variants(pf):
    responses.get(f"{BASE_URL}/catalog/blueprints/6/print_providers/99/variants.json", json=load("printify/variants.json"))
    assert [v["id"] for v in pf.variants(6, 99)] == [12100, 12101]


@responses.activate
def test_shipping_cost_for_variant(pf):
    responses.get(f"{BASE_URL}/catalog/blueprints/6/print_providers/99/shipping.json", json=load("printify/shipping.json"))
    assert pf.shipping_cost_usd(6, 99, 12101) == {"first_item_usd": 4.75, "additional_items_usd": 2.40}


@responses.activate
def test_shipping_unknown_variant_fails_closed(pf):
    responses.get(f"{BASE_URL}/catalog/blueprints/6/print_providers/99/shipping.json", json=load("printify/shipping.json"))
    with pytest.raises(LookupError):
        pf.shipping_cost_usd(6, 99, 1)
