from playwright.sync_api import Locator


class ProductCard:
    """One product: a tile on the inventory page or a row in the cart.

    Takes a root Locator instead of a Page, so every locator below is scoped to
    this one product. That is what makes "the Add to cart button for the
    Backpack" unambiguous when the page has six of them.
    """

    def __init__(self, root: Locator):
        self.root = root
        self.name = root.get_by_test_id("inventory-item-name")
        self.price = root.get_by_test_id("inventory-item-price")
        self.add_button = root.get_by_role("button", name="Add to cart")
        self.remove_button = root.get_by_role("button", name="Remove")

    def add_to_cart(self) -> None:
        self.add_button.click()

    def remove(self) -> None:
        self.remove_button.click()
