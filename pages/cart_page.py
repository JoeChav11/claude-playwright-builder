import re

from playwright.sync_api import Page

from pages.components import Header, ProductCard


class CartPage:
    """Cart at /cart.html."""

    URL = re.compile(r"/cart\.html$")

    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.checkout_button = page.get_by_role("button", name="Checkout")
        self.continue_shopping_button = page.get_by_role("button", name="Continue Shopping")

    def item(self, name: str) -> ProductCard:
        return ProductCard(self.items.filter(has_text=name))

    def checkout(self) -> None:
        self.checkout_button.click()
