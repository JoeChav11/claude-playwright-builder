import pytest
from playwright.sync_api import Page, expect

from data import USERS
from pages import InventoryPage, LoginPage


@pytest.fixture
def user_key() -> str:
    """Which entry in data/users.json logged_in_page uses.

    Override per test with @pytest.mark.parametrize("user_key", ["problem"]).
    """
    return "standard"


@pytest.fixture
def logged_in_page(page: Page, user_key: str) -> Page:
    """A page logged in as USERS[user_key], sitting on the inventory page."""
    user = USERS[user_key]
    login = LoginPage(page)
    login.open()
    login.login(user["username"], user["password"])
    expect(page).to_have_url(InventoryPage.URL)
    return page
