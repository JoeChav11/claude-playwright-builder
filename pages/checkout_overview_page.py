import re

from playwright.sync_api import Page


class CheckoutOverviewPage:
    """Checkout step two at /checkout-step-two.html: order summary."""

    URL = re.compile(r"/checkout-step-two\.html$")

    def __init__(self, page: Page):
        self.page = page
        self.item_names = page.get_by_test_id("inventory-item-name")
        # Summary totals are plain text with no role; test-id keeps them distinct.
        self.item_total = page.get_by_test_id("subtotal-label")
        self.finish_button = page.get_by_role("button", name="Finish")

    def finish(self) -> None:
        self.finish_button.click()
