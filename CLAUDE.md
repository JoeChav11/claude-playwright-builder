# Test repo: saucedemo.com (Playwright + pytest)

End-to-end tests for https://www.saucedemo.com, written in Playwright **Python** with pytest. Follow this file exactly; consistency matters more than cleverness.

## About this repo
This is the **reference result and starting point** of a six-module training course on Claude Code + Playwright (`docs/modules/module-1.md` to `module-6.md`; index in `README.md`). Students clone it and work through the modules in order, one git branch per module. The exercises use, inspect and extend what is already here; only the Module 6 pieces are built from scratch. Students' branches are expected to drift from `main`.
- Everything here is teaching material: keep it exemplary, consistent with the module docs, and commented where a comment teaches something.
- **Deliberately absent** (students build them in Module 6): `.github/workflows/`, `deny` rules in `.claude/settings.json`, and a "Fixing failing tests" section in this file. Don't add them unless asked.
- When you change course material, keep the module docs, `README.md` and this file in sync. Exercises quote file paths, test counts (23) and commands; update them if those change.
- When a student is working through a module, help them do the exercise themselves on their branch, rather than copying a finished answer.

## Commands
Activate the venv first: `.\.venv\Scripts\Activate.ps1` (macOS/Linux: `source .venv/bin/activate`).

| Task | Command |
|---|---|
| Smoke tests, watch the browser | `pytest -m smoke --headed` |
| Smoke tests, fast | `pytest -m smoke` |
| Regression in parallel | `pytest -m regression -n auto` |
| Everything in parallel | `pytest -n auto` |
| One file / one test | `pytest tests/regression/test_cart.py -k badge -v` |
| Debug a failure | `pytest <file> --headed --slowmo 500 --tracing retain-on-failure --screenshot only-on-failure` |
| Check a new test is stable | `pytest <file> --count 10 -n auto` (must pass 10/10) |

After writing or changing a test, run it and confirm it passes before reporting done. Run the full suite with `-n auto` after changing anything in `pages/`, `fixtures/` or `data/`.

## Layout
```
tests/smoke/        critical paths, marked smoke
tests/regression/   edge cases and errors, marked regression
pages/              one page object per URL
pages/components/   UI pieces shared across pages (Header, ProductCard)
fixtures/           pytest fixtures, registered in conftest.py
data/               test data as JSON, loaded by data/__init__.py
conftest.py         registers fixtures/, sets data-test as the test-id attribute
.claude/agents/     test-writer and test-reviewer subagents (used from Module 2)
docs/modules/       the course, one file per module
```
`tests/test_reference.py`, `tests/claude/`, `tests/codegen/` and `exercises/` are Module 2 training material. Don't refactor them unless asked.

## Where code goes
- **New page (has its own URL):** `pages/<name>_page.py`, class `<Name>Page`, export it from `pages/__init__.py`, add a fixture in `fixtures/pages.py`.
- **Repeated UI piece (no URL, appears on several pages, or repeats within a page):** `pages/components/<name>.py`. Components take a `Page` if there is one per page (Header), or a root `Locator` if there are many (ProductCard).
- **Setup reused across files:** a fixture in `fixtures/`. Setup used by one file only: a fixture in that test file.
- **Test data:** `data/*.json`. Tests import `USERS`, `PRODUCTS`, `CUSTOMERS` and `money()` from `data`. Never hard-code usernames, passwords, product names, prices or customer details in tests or page objects. Expected UI messages (error text) may live in the test.

## Page object rules
- Locators are attributes set in `__init__`; actions are methods named for what the user does (`login`, `add_to_cart`, `checkout`).
- Each page object has a `URL` regex class attribute for `expect(page).to_have_url(...)`.
- Page objects contain **no assertions**. Assertions belong in tests.
- Action methods (`login`, `checkout`) return `None`. Lookup methods that pick one of many items (`product(name)`, `item(name)`) return a component. Tests use page object fixtures; fixtures share one logged-in tab.

## Test rules
- Every test file sets `pytestmark = pytest.mark.smoke` or `pytest.mark.regression`. Markers are strict: unknown markers fail.
- File names: `test_<feature>.py`. Test names describe the behavior: `test_<who/what>_<does>_<outcome>`, e.g. `test_locked_out_user_sees_error`.
- Use page object fixtures (`login_page`, `inventory_page`, `cart_page`, ...). For a non-standard user, `@pytest.mark.parametrize("user_key", ["problem"])`.
- Arrange / act / assert, separated by blank lines. End with at least one `expect(...)` on a user-visible outcome.
- Use `pytest.mark.parametrize` with `pytest.param(..., id="readable-id")` instead of copy-pasted tests.
- Tests must be independent: they run in parallel in random worker order.

## Locator rules
Priority order. Only move down when the option above does not work, and leave a one-line comment saying why:
1. `get_by_role(role, name=...)`
2. `get_by_label(...)`
3. `get_by_placeholder(...)` / `get_by_text(...)`
4. `get_by_test_id(...)` (reads `data-test`)
5. CSS: last resort. XPath: not allowed.

Check roles against the real accessibility tree (Playwright MCP `browser_snapshot`), not the HTML tag. On this site the Logout `<a>` is a `button` and the login error is an `alert`.

## Banned patterns
| Don't | Do instead |
|---|---|
| `time.sleep()`, `page.wait_for_timeout()` | Actions auto-wait; use `expect(...)` for state |
| XPath, especially indexed (`//div[2]/form/input`) | Role/label/test-id locators |
| `nth-child`, `.first`, `.nth(i)` to pick an item | Scope with `.filter(has_text=...)` or a component |
| Styling classes (`.btn_primary`, `.btn_medium`) | Role or test-id |
| `assert locator.is_visible()` / `assert ... in locator.inner_text()` | `expect(locator).to_be_visible()` / `.to_have_text()` (these retry) |
| Hard-coded `https://www.saucedemo.com/...` | `page.goto("/")`; base URL is in `pytest.ini` |
| Literal test data in tests | `data/*.json` |
| Logging in inside a test body | `logged_in_page` / page object fixtures |

## Working style
- **Multi-file changes** (new page object + fixture + tests, renaming a locator used in many places, refactors): use **plan mode** first. List every file you will touch and what changes, and wait for approval.
- Before adding a page object or locator, open the page with the Playwright MCP tools and take a `browser_snapshot`. Build locators from what the snapshot shows.
- Reuse existing page objects, components and fixtures. Read `pages/` and `fixtures/` before creating anything new.
