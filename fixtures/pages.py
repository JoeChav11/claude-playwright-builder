"""Page object fixtures.

login_page opens the login screen. Every other fixture wraps the same logged-in
browser tab (via logged_in_page) and does NOT navigate: the test drives the flow.
Requesting several of them in one test shares one tab and one login.
"""
import pytest
from playwright.sync_api import Page

from pages import (
    CartPage,
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
    InventoryPage,
    LoginPage,
)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    login = LoginPage(page)
    login.open()
    return login


@pytest.fixture
def inventory_page(logged_in_page: Page) -> InventoryPage:
    return InventoryPage(logged_in_page)


@pytest.fixture
def cart_page(logged_in_page: Page) -> CartPage:
    return CartPage(logged_in_page)


@pytest.fixture
def checkout_info_page(logged_in_page: Page) -> CheckoutInfoPage:
    return CheckoutInfoPage(logged_in_page)


@pytest.fixture
def checkout_overview_page(logged_in_page: Page) -> CheckoutOverviewPage:
    return CheckoutOverviewPage(logged_in_page)


@pytest.fixture
def checkout_complete_page(logged_in_page: Page) -> CheckoutCompletePage:
    return CheckoutCompletePage(logged_in_page)
