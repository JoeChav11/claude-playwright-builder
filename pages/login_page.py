import re

from playwright.sync_api import Page


class LoginPage:
    """Login screen at "/"."""

    # The site root: the host followed by a single "/", whatever --base-url points at.
    URL = re.compile(r"://[^/]+/$")

    def __init__(self, page: Page):
        self.page = page
        # The inputs have no <label>, so placeholder is the most user-facing hook.
        self.username = page.get_by_placeholder("Username")
        self.password = page.get_by_placeholder("Password")
        self.submit = page.get_by_role("button", name="Login")
        self.error = page.get_by_role("alert")

    def open(self) -> None:
        self.page.goto("/")

    def login(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()
