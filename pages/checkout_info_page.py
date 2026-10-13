import re

from playwright.sync_api import Page


class CheckoutInfoPage:
    """Checkout step one at /checkout-step-one.html: customer details form."""

    URL = re.compile(r"/checkout-step-one\.html$")

    def __init__(self, page: Page):
        self.page = page
        self.first_name = page.get_by_placeholder("First Name")
        self.last_name = page.get_by_placeholder("Last Name")
        self.postal_code = page.get_by_placeholder("Zip/Postal Code")
        self.continue_button = page.get_by_role("button", name="Continue")
        self.error = page.get_by_role("alert")

    def fill(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.postal_code.fill(postal_code)

    def submit(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.fill(first_name, last_name, postal_code)
        self.continue_button.click()
