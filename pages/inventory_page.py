import re

from playwright.sync_api import Page

from pages.components import Header, ProductCard


class InventoryPage:
    """Product list at /inventory.html. Requires a logged-in session."""

    URL = re.compile(r"/inventory\.html$")

    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)
        self.title = page.get_by_text("Products", exact=True)
        # The sort <select> has no label; it is the only combobox on the page.
        self.sort_select = page.get_by_role("combobox")
        self.cards = page.get_by_test_id("inventory-item")
        self.names = page.get_by_test_id("inventory-item-name")
        self.prices = page.get_by_test_id("inventory-item-price")

    def open(self) -> None:
        self.page.goto("/inventory.html")

    def product(self, name: str) -> ProductCard:
        return ProductCard(self.cards.filter(has_text=name))

    def sort_by(self, option_label: str) -> None:
        self.sort_select.select_option(label=option_label)
