import pytest
from playwright.sync_api import expect

from data import CUSTOMERS, PRODUCTS
from pages import (
    CartPage,
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
    InventoryPage,
)

pytestmark = pytest.mark.smoke


def test_standard_user_completes_checkout(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
    checkout_overview_page: CheckoutOverviewPage,
    checkout_complete_page: CheckoutCompletePage,
):
    customer = CUSTOMERS["default"]

    inventory_page.product(PRODUCTS["backpack"]["name"]).add_to_cart()
    inventory_page.header.open_cart()
    cart_page.checkout()
    checkout_info_page.submit(customer["first_name"], customer["last_name"], customer["postal_code"])
    checkout_overview_page.finish()

    expect(checkout_complete_page.page).to_have_url(CheckoutCompletePage.URL)
    expect(checkout_complete_page.confirmation).to_be_visible()
    expect(checkout_complete_page.header.cart_badge).not_to_be_visible()
