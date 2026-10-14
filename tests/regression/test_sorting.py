import pytest
from playwright.sync_api import expect

from data import PRODUCTS, money
from pages import InventoryPage

pytestmark = pytest.mark.regression

ALL = list(PRODUCTS.values())

# The expected order is written out, not computed with sorted(). Python sorts by
# character code, the site sorts in the browser's locale order; they only agree on
# these names by chance. A test that re-implements the feature can share its bugs.
A_TO_Z = [
    PRODUCTS[key]["name"]
    for key in ["backpack", "bike_light", "bolt_tshirt", "fleece_jacket", "onesie", "red_tshirt"]
]


@pytest.mark.parametrize(
    ("start_option", "option", "expected_names"),
    [
        pytest.param("Name (Z to A)", "Name (A to Z)", A_TO_Z, id="a-to-z"),
        pytest.param("Name (A to Z)", "Name (Z to A)", A_TO_Z[::-1], id="z-to-a"),
    ],
)
def test_name_sort_orders_products_by_name(inventory_page: InventoryPage, start_option, option, expected_names):
    # The page opens sorted A to Z. Start from the opposite order, so choosing the
    # option has to change something: otherwise the a-to-z case passes even if sorting is broken.
    inventory_page.sort_by(start_option)
    expect(inventory_page.names).to_have_text(expected_names[::-1])

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
