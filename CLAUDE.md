# Test repo: saucedemo.com (Playwright + pytest)

End-to-end tests for https://www.saucedemo.com, written in Playwright **Python** with pytest. Follow this file exactly; consistency matters more than cleverness.

## About this repo
This is the **reference result and starting point** of a six-module training course on Claude Code + Playwright (`docs/modules/module-1.md` to `module-6.md`; index in `README.md`). Students clone it and work through the modules in order, one git branch per module. The exercises use, inspect and extend what is already here; only the guardrails (Modules 4 and 5) are built from scratch, and Module 6 is a capstone on the student's own app. Students' branches are expected to drift from `main`. **If `pages/` and `tests/` don't exist, skip to "Building from scratch" below.**
- Everything here is teaching material: keep it exemplary, consistent with the module docs, and commented where a comment teaches something.
- **This is the `finished-example` branch**: `main` plus the guardrails students build themselves ("Fixing failing tests" below, from Module 4, and `deny` rules in `.claude/settings.json`, from Module 5). Keep it in sync by merging `main` into it; don't rebase.
- When you change course material, keep the module docs, `docs/curriculum.md`, `README.md` and this file in sync. Exercises quote file paths, test counts (23) and commands; update them if those change.
- When a student is working through a module of the cloned repo, help them do the exercise themselves on their branch, rather than copying a finished answer.

## Building from scratch
**Applies when `pages/` and `tests/` don't exist**: a student has started an empty folder with this file and `README.md` and wants to build the project. Then:
- Everything in this file that says files "already exist" (the layout, "Reuse existing...", "23 tests") describes the **target**, not the current state. The rules below "Commands" are the standard for the code you write.
- **First, ask who writes the tests:** Claude writes them and the student reviews, or the student writes them and Claude reviews. Don't write code until they answer (skip the question if their message already says). Then follow their choice for the rest of the build.
- **Build one stage at a time, in order.** Plan only the current stage, in plan mode, listing every file. After it's built and its check passes, **stop**: ask the student to run the check, commit it (stage 1 on `main`, then a branch per stage, each from the previous stage's branch: `git switch -c module-N`), and say when to start the next stage. Never plan or build two stages at once, even if asked to "build everything": explain why, and offer to go stage by stage quickly.
- Build each stage from the list below. The module docs' exercises (`docs/modules/`, if the student copied them) are written for the cloned repo: the **Exercises** column says which ones work after each stage, and what to change. Until stage 5, steps that use the test-writer or test-reviewer agent go to the main session instead ("review it against docs/review-checklist.md").

| Stage (module) | Builds | Check | Exercises |
|---|---|---|---|
| 1. Setup (Module 1) | `git init`, `.gitignore`, `requirements.txt` (pytest, pytest-playwright, pytest-xdist, pytest-repeat), `pytest.ini` (base_url, chromium, strict `smoke`/`regression` markers), `conftest.py` (`data-test` test-id attribute), `.mcp.json` (Playwright MCP pinned to `@playwright/mcp@0.0.83`; Windows: `"command": "cmd", "args": ["/c", "npx", "-y", ...]`, macOS/Linux: `"command": "npx"`), `.claude/settings.json` (`"enabledMcpjsonServers": ["playwright"]`, allow `pytest` and the Playwright browsing tools by name, not `browser_evaluate`, `browser_run_code_unsafe` or `browser_file_upload`). Then: venv, `pip install -r requirements.txt` (with `-c constraints.txt` if the student has it), `playwright install chromium`. `conftest.py` registers `fixtures/` only from stage 2, once it exists. | `pytest` starts, imports `conftest.py` without errors and reports "no tests ran" (exit code 5: expected, there are no tests yet); after reloading Claude Code, `/mcp` shows `playwright` connected | Module 1, all. Ex 3: `@` two files of your own. Ex 4: `/agents` lists none yet |
| 2. First tests (Module 2) | `tests/test_reference.py`: 3 annotated beginner tests (login, locked-out error, add to cart) with inline locators. `fixtures/auth.py` with `logged_in_page` and the `user_key` fixture it reads (default `"standard"`, overridable with `parametrize`), registered in `conftest.py`. Empty `tests/codegen/` and `tests/claude/` folders (with a README) for recorded and Claude-written tests. `exercises/bad_test.py`: a checkout test that passes but uses sleeps, XPath, styling classes and `assert ... is_visible()` | `pytest tests/test_reference.py` passes, and so does `pytest exercises/bad_test.py` (that's the point) | Module 2, all. Ex 2: compare the menu with your own notes (no `header.py` yet). Ex 4: main session, using `logged_in_page` and inline locators (no page objects or `data/` yet). Ex 5: main session reviews |
| 3. Structure (Module 3) | `data/*.json` + `data/__init__.py` (`USERS`, `PRODUCTS`, `CUSTOMERS`, `money()`); page objects for login, inventory, cart, checkout info / overview / complete; `Header` and `ProductCard` components; `fixtures/pages.py`; smoke tests (login, cart, checkout) and regression tests (cart, checkout, login errors, logout, sorting). Locators from MCP snapshots. | `pytest -n auto` passes | Module 3, all. Ex 4 refactors `tests/test_reference.py` into the page objects you just built. Ex 5: main session writes and reviews |
| 4. MCP-driven tests (Module 4) | One new feature tested from a description only, explored with MCP first (e.g. "Reset App State" in the menu clears the cart). Then the student writes a "Fixing failing tests" section here; guide, don't write it. | New test passes `--count 10 -n auto`; in a new session, Claude won't "fix" a failing test by changing what it expects | Module 4, all. Ex 1 is this stage's build (main session, not the test-writer). Ex 3: use your own product key and page object names |
| 5. Subagents (Module 5) | `.claude/agents/test-writer.md` (all tools) and `test-reviewer.md` (`Read, Grep, Glob, Bash` only; no editing tools, told never to edit and to use Bash only for pytest), both `model: sonnet` to keep costs down. Then the student adds `deny` rules to `.claude/settings.json`; guide, don't write them. | In a new session, the reviewer rejects `exercises/bad_test.py` and accepts a smoke test, and reading `.env` or editing `.claude/agents/` is refused | Module 5, all, as written |
| 6. Capstone (Module 6) | Nothing in this repo: the student builds a new project for their own app | See `docs/modules/module-6.md` | Module 6 |

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
`tests/test_reference.py`, `tests/claude/`, `tests/codegen/` and `exercises/` are Module 2 training material. Don't refactor them unless asked. They live outside `tests/smoke/` and `tests/regression/` and may use inline locators; every other rule still applies when they're reviewed.

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
| `nth-child`, `.first`, `.nth(i)` to pick an item | Scope with `.filter(has_text=...)` or a component. Exception: when position is the requirement ("the first product shown"), put the positional lookup in the page object with a comment saying so |
| Styling classes (`.btn_primary`, `.btn_medium`) | Role or test-id |
| `assert locator.is_visible()` / `assert ... in locator.inner_text()` | `expect(locator).to_be_visible()` / `.to_have_text()` (these retry) |
| Hard-coded `https://www.saucedemo.com/...` | `page.goto("/")`; base URL is in `pytest.ini` |
| Literal test data in tests | `data/*.json` |
| Logging in inside a test body | `logged_in_page` / page object fixtures. Exception: tests of login itself (`test_login.py`, `test_login_errors.py`) log in through `login_page` |

## Fixing failing tests
- Never change an expected value, remove an `expect`, loosen a matcher
  (`to_have_text` to `to_contain_text`), add `skip`/`xfail`, add retries or
  raise a timeout to make a test pass.
- First decide whether the test or the app is wrong, and say which, with evidence
  (failure output, trace, screenshot). If the app is wrong, don't edit the test:
  report the bug.
- Flaky tests: name the cause (assertion before the page settles, shared state,
  order-dependent data) and fix it; the fix must pass `pytest <file> --count 10 -n auto`.

## Working style
- **Multi-file changes** (new page object + fixture + tests, renaming a locator used in many places, refactors): use **plan mode** first. List every file you will touch and what changes, and wait for approval.
- Before adding a page object or locator, open the page with the Playwright MCP tools and take a `browser_snapshot`. Build locators from what the snapshot shows.
- Reuse existing page objects, components and fixtures. Read `pages/` and `fixtures/` before creating anything new.
