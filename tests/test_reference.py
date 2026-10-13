"""Reference tests: beginner Playwright style (Module 2).

Read this file top to bottom before the exercises. Each comment points at one
Playwright basic: page, locators, auto-waiting, expect.

The locators and test data are written inline here, which keeps the basics in
one place. CLAUDE.md does not allow that in the rest of tests/: locators belong
in pages/ and data in data/. Module 3, Exercise 4 refactors this file to the
repo standard.
"""
import re

from playwright.sync_api import Page, expect


def test_standard_user_can_log_in(page: Page):
    # `page` is a fresh browser tab provided by pytest-playwright.
    # "/" resolves against --base-url in pytest.ini.
    page.goto("/")

    # Locators describe HOW to find an element; nothing is searched yet.
    # The login inputs have no <label>, so get_by_label won't work here.
    # Placeholder is the next most user-facing option.
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")

    # Actions auto-wait: click() waits until the button is visible, enabled and stable.
    page.get_by_role("button", name="Login").click()

    # expect() retries until the condition is true or the timeout (5s) expires.
    # That is why we never need time.sleep().
    expect(page).to_have_url(re.compile(r"/inventory\.html$"))
    expect(page.get_by_text("Products", exact=True)).to_be_visible()


def test_locked_out_user_sees_error(page: Page):
    page.goto("/")
    page.get_by_placeholder("Username").fill("locked_out_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()

    # Assert the outcome a real user would see, and that we did NOT navigate.
    # The error box exposes role="alert" in the accessibility tree.
    expect(page.get_by_role("alert")).to_contain_text("locked out")
    expect(page).not_to_have_url(re.compile(r"/inventory\.html$"))


def test_add_backpack_to_cart(logged_in_page: Page):
    page = logged_in_page  # fixture from fixtures/auth.py (registered in conftest.py), already logged in

    # Scope first, then find: "the Add to cart button INSIDE the Backpack card".
    # There are six "Add to cart" buttons, so an unscoped role locator would be ambiguous.
    backpack = page.get_by_test_id("inventory-item").filter(has_text="Sauce Labs Backpack")
    backpack.get_by_role("button", name="Add to cart").click()

    expect(backpack.get_by_role("button", name="Remove")).to_be_visible()
    # The cart badge has no role or label, so test-id is the most stable option.
    expect(page.get_by_test_id("shopping-cart-badge")).to_have_text("1")
