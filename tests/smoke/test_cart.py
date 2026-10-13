import pytest
from playwright.sync_api import expect

from data import PRODUCTS
from pages import InventoryPage

pytestmark = pytest.mark.smoke


def test_adding_product_updates_cart_badge(inventory_page: InventoryPage):
    backpack = inventory_page.product(PRODUCTS["backpack"]["name"])

    backpack.add_to_cart()

    expect(backpack.remove_button).to_be_visible()
    expect(inventory_page.header.cart_badge).to_have_text("1")
