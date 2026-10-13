import pytest
from playwright.sync_api import expect

from data import PRODUCTS
from pages import CartPage, InventoryPage

pytestmark = pytest.mark.regression

BACKPACK = PRODUCTS["backpack"]["name"]
BIKE_LIGHT = PRODUCTS["bike_light"]["name"]


def test_cart_lists_exactly_the_added_products(inventory_page: InventoryPage, cart_page: CartPage):
    inventory_page.product(BACKPACK).add_to_cart()
    inventory_page.product(BIKE_LIGHT).add_to_cart()
    expect(inventory_page.header.cart_badge).to_have_text("2")

    inventory_page.header.open_cart()

    expect(cart_page.page).to_have_url(CartPage.URL)
    expect(cart_page.item_names).to_have_text([BACKPACK, BIKE_LIGHT])


def test_removing_product_from_cart_updates_badge(inventory_page: InventoryPage, cart_page: CartPage):
    inventory_page.product(BACKPACK).add_to_cart()
    inventory_page.product(BIKE_LIGHT).add_to_cart()
    inventory_page.header.open_cart()

    cart_page.item(BACKPACK).remove()

    expect(cart_page.item_names).to_have_text([BIKE_LIGHT])
    expect(cart_page.header.cart_badge).to_have_text("1")


def test_badge_disappears_when_cart_is_emptied(inventory_page: InventoryPage):
    backpack = inventory_page.product(BACKPACK)
    backpack.add_to_cart()

    backpack.remove()

    expect(backpack.add_button).to_be_visible()
    expect(inventory_page.header.cart_badge).not_to_be_visible()
