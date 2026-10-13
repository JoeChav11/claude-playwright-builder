import pytest
from playwright.sync_api import expect

from data import CUSTOMERS, PRODUCTS, money
from pages import CartPage, CheckoutInfoPage, CheckoutOverviewPage, InventoryPage

pytestmark = pytest.mark.regression

CUSTOMER = CUSTOMERS["default"]


@pytest.fixture
def at_checkout_info(inventory_page: InventoryPage, cart_page: CartPage) -> None:
    """Backpack and Bike Light in the cart, sitting on checkout step one."""
    inventory_page.product(PRODUCTS["backpack"]["name"]).add_to_cart()
    inventory_page.product(PRODUCTS["bike_light"]["name"]).add_to_cart()
    inventory_page.header.open_cart()
    cart_page.checkout()


@pytest.mark.usefixtures("at_checkout_info")
def test_overview_shows_item_total(
    checkout_info_page: CheckoutInfoPage, checkout_overview_page: CheckoutOverviewPage
):
    expected_total = money(PRODUCTS["backpack"]["price"] + PRODUCTS["bike_light"]["price"])

    checkout_info_page.submit(CUSTOMER["first_name"], CUSTOMER["last_name"], CUSTOMER["postal_code"])

    expect(checkout_overview_page.page).to_have_url(CheckoutOverviewPage.URL)
    expect(checkout_overview_page.item_names).to_have_text(
        [PRODUCTS["backpack"]["name"], PRODUCTS["bike_light"]["name"]]
    )
    expect(checkout_overview_page.item_total).to_have_text(f"Item total: {expected_total}")


@pytest.mark.usefixtures("at_checkout_info")
@pytest.mark.parametrize(
    ("first_name", "last_name", "postal_code", "message"),
    [
        pytest.param("", CUSTOMER["last_name"], CUSTOMER["postal_code"], "First Name is required", id="no-first-name"),
        pytest.param(CUSTOMER["first_name"], "", CUSTOMER["postal_code"], "Last Name is required", id="no-last-name"),
        pytest.param(CUSTOMER["first_name"], CUSTOMER["last_name"], "", "Postal Code is required", id="no-postal-code"),
    ],
)
def test_checkout_info_requires_all_fields(
    checkout_info_page: CheckoutInfoPage, first_name, last_name, postal_code, message
):
    checkout_info_page.submit(first_name, last_name, postal_code)

    expect(checkout_info_page.error).to_contain_text(message)
    expect(checkout_info_page.page).to_have_url(CheckoutInfoPage.URL)
