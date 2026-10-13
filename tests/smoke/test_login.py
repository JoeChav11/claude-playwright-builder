import pytest
from playwright.sync_api import Page, expect

from data import USERS
from pages import InventoryPage, LoginPage

pytestmark = pytest.mark.smoke


def test_standard_user_lands_on_inventory(page: Page, login_page: LoginPage):
    user = USERS["standard"]

    login_page.login(user["username"], user["password"])

    inventory = InventoryPage(page)
    expect(page).to_have_url(InventoryPage.URL)
    expect(inventory.title).to_be_visible()
    expect(inventory.cards).to_have_count(6)
