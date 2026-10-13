import pytest
from playwright.sync_api import Page, expect

from data import USERS
from pages import InventoryPage, LoginPage

pytestmark = pytest.mark.regression


@pytest.mark.parametrize(
    ("username", "password", "message"),
    [
        pytest.param(
            USERS["locked_out"]["username"],
            USERS["locked_out"]["password"],
            "Sorry, this user has been locked out.",
            id="locked-out-user",
        ),
        pytest.param(
            USERS["wrong_password"]["username"],
            USERS["wrong_password"]["password"],
            "Username and password do not match any user in this service",
            id="wrong-password",
        ),
        pytest.param("", USERS["standard"]["password"], "Username is required", id="missing-username"),
        pytest.param(USERS["standard"]["username"], "", "Password is required", id="missing-password"),
    ],
)
def test_invalid_login_shows_error(page: Page, login_page: LoginPage, username, password, message):
    login_page.login(username, password)

    expect(login_page.error).to_contain_text(message)
    expect(page).not_to_have_url(InventoryPage.URL)
