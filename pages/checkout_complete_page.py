import re

from playwright.sync_api import Page

from pages.components import Header


class CheckoutCompletePage:
    """Order confirmation at /checkout-complete.html."""

    URL = re.compile(r"/checkout-complete\.html$")

    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)
        self.confirmation = page.get_by_role("heading", name="Thank you for your order!")
        self.back_home_button = page.get_by_role("button", name="Back Home")
