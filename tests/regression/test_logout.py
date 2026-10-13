import pytest
from playwright.sync_api import Page, expect

from pages import InventoryPage, LoginPage

pytestmark = pytest.mark.regression


def test_logout_returns_to_login(page: Page, inventory_page: InventoryPage):
    inventory_page.header.logout()

    expect(LoginPage(page).submit).to_be_visible()


def test_inventory_is_blocked_after_logout(page: Page, inventory_page: InventoryPage):
    inventory_page.header.logout()

    inventory_page.open()

    login = LoginPage(page)
    expect(login.error).to_contain_text("You can only access '/inventory.html' when you are logged in")
