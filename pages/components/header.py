from playwright.sync_api import Page


class Header:
    """Top bar shown on every page after login: menu and cart icon.

    A component helper, not a page: it has no URL of its own, so every page
    object that shows the header composes one instead of repeating these locators.
    """

    def __init__(self, page: Page):
        self.page = page
        self.menu_button = page.get_by_role("button", name="Open Menu")
        # An <a> tag, but it declares role="button", and role locators follow the accessibility tree.
        self.logout_button = page.get_by_role("button", name="Logout")
        # The cart icon and badge have no accessible name or role; test-id is the stable option.
        self.cart_link = page.get_by_test_id("shopping-cart-link")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")

    def open_cart(self) -> None:
        self.cart_link.click()

    def logout(self) -> None:
        self.menu_button.click()
        self.logout_button.click()
