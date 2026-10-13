# Page Objects vs. Component Helpers

Both move locators out of tests so a UI change is fixed in one place. They differ in **what they wrap**.

| | Page object | Component helper |
|---|---|---|
| Wraps | A whole page / URL | A piece of UI with no URL |
| Constructed from | `Page` | `Page` (one per page) or a root `Locator` (many per page) |
| Lives in | `pages/<name>_page.py` | `pages/components/<name>.py` |
| Examples here | `LoginPage`, `CartPage`, `CheckoutInfoPage` | `Header`, `ProductCard` |
| Rule of thumb | "Where am I?" | "What am I looking at?" |

## Why components matter
Without a component, every page that shows the cart badge defines it again:
```python
class InventoryPage:  self.cart_badge = page.get_by_test_id("shopping-cart-badge")
class CartPage:       self.cart_badge = page.get_by_test_id("shopping-cart-badge")
class CheckoutCompletePage: ...                         # and again
```
With one, each page composes it: `self.header = Header(page)`, and tests read `inventory_page.header.cart_badge`.

## Root-locator components solve "which one?"
The inventory page has six "Add to cart" buttons. A `ProductCard` built from one product's root locator scopes every child locator to that product:
```python
card = ProductCard(page.get_by_test_id("inventory-item").filter(has_text="Sauce Labs Backpack"))
card.add_to_cart()              # only the Backpack's button
expect(card.remove_button).to_be_visible()
```
The same class works for cart rows, because the cart reuses the same markup. No `nth(0)`, no index.

## Decision guide
1. Does it have its own URL? **Page object.**
2. Does it appear on several pages, or repeat several times on one page? **Component.**
3. Used once, on one page? Just an attribute on that page object.
4. Is it a multi-page *flow* (add item, open cart, check out)? Neither: make it a **fixture** (see `at_checkout_info` in `tests/regression/test_checkout.py`).

## Rules we follow (also in CLAUDE.md)
- Locators are attributes set in `__init__`. Actions are methods named for what the user does.
- No assertions inside page objects or components. Tests own the "what proves success" decision.
- Action methods return `None`. Tests get page objects from fixtures, not from method return values. (Returning the next page object is also a common style. We pick one and stay consistent.)
- Lookup methods that pick one of many items return a component: `inventory_page.product(name)` and `cart_page.item(name)` return a `ProductCard`. They find something; they don't do anything.
