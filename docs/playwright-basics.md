# Playwright Python Basics (one page)

| Concept | What it is | Example |
|---|---|---|
| `page` | A browser tab. pytest-playwright gives you a fresh one per test. | `def test_x(page: Page):` |
| Locator | A *recipe* for finding an element. Lazy: evaluated each time you act on it. | `page.get_by_role("button", name="Login")` |
| Action | Something a user does. Auto-waits for the element to be visible, enabled, stable. | `.click()`, `.fill("x")`, `.check()` |
| `expect` | Assertion that **retries** until true or timeout (default 5s). | `expect(loc).to_have_text("1")` |

## Why no `sleep`
Actions and `expect` already wait for the condition you care about. A sleep waits for a guess: too short and the test flakes, too long and the suite is slow.

## Locator priority
```python
page.get_by_role("button", name="Login")      # 1. how users and screen readers see it
page.get_by_label("Email")                    # 2. form fields with a <label>
page.get_by_placeholder("Username")           # 3. inputs without a label
page.get_by_text("Thank you for your order!") # 3. non-interactive text
page.get_by_test_id("shopping-cart-badge")    # 4. stable hook added by developers
page.locator("#user-name")                    # 5. CSS: last resort (XPath: not allowed)
```
Roles and names come from the accessibility tree. To see it: `playwright codegen` (hover an element), or ask Claude to take a `browser_snapshot` with the MCP server.

## Common assertions
```python
expect(page).to_have_url(re.compile(r"/cart\.html$"))
expect(locator).to_be_visible()
expect(locator).to_have_text("Products")
expect(locator).to_have_count(3)
expect(locator).not_to_be_visible()
```

## Handling repeated elements
```python
card = page.get_by_test_id("inventory-item").filter(has_text="Sauce Labs Backpack")
card.get_by_role("button", name="Add to cart").click()
```
