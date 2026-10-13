import pytest
from playwright.sync_api import expect

from data import PRODUCTS, money
from pages import InventoryPage

pytestmark = pytest.mark.regression

ALL = list(PRODUCTS.values())


@pytest.mark.parametrize(
    ("option", "expected_names"),
    [
        pytest.param("Name (A to Z)", sorted(p["name"] for p in ALL), id="a-to-z"),
        pytest.param("Name (Z to A)", sorted((p["name"] for p in ALL), reverse=True), id="z-to-a"),
    ],
)
def test_name_sort_orders_products_by_name(inventory_page: InventoryPage, option, expected_names):
    inventory_page.sort_by(option)

    # to_have_text with a list checks every item, in order, and retries until it matches.
    expect(inventory_page.names).to_have_text(expected_names)


@pytest.mark.parametrize(
    ("option", "descending"),
    [
        pytest.param("Price (low to high)", False, id="low-to-high"),
        pytest.param("Price (high to low)", True, id="high-to-low"),
    ],
)
def test_price_sort_orders_products_by_price(inventory_page: InventoryPage, option, descending):
    # Compare prices, not names: two products share a price, so name order among them is not defined.
    expected_prices = [money(p) for p in sorted((p["price"] for p in ALL), reverse=descending)]

    inventory_page.sort_by(option)

    expect(inventory_page.prices).to_have_text(expected_prices)
