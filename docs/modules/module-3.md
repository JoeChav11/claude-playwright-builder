# Module 3: Structuring the Test Repo and Encoding Standards

**Goal:** make Claude produce consistent code.

In Module 2 your strong prompt had to restate the rules ("no sleeps, use role locators..."), and you may have noticed Claude following rules you never gave it. That's because this repo already keeps its rules in the repo itself: a folder layout, shared page objects and fixtures, and a `CLAUDE.md` that Claude reads at the start of every session. In this module you take that structure apart, prove `CLAUDE.md` is doing the work, and extend it.

## What's in the repo
You've been using these since Module 2. This is what each part does:
```
tests/smoke/           3 critical-path tests          @pytest.mark.smoke
tests/regression/      17 edge-case tests            @pytest.mark.regression
pages/                 page objects, one per URL
pages/components/      Header, ProductCard (shared UI pieces)
fixtures/auth.py       logged_in_page, user_key
fixtures/pages.py      login_page, inventory_page, cart_page, checkout_*_page
data/*.json            users, products, customers
conftest.py            registers fixtures/ via pytest_plugins
pytest.ini             markers (strict), base_url, import mode
CLAUDE.md              the standards Claude follows
```
Read [pom-vs-components.md](../pom-vs-components.md) before the exercises.

Start a new branch from `main` for this module (`git switch main`, then `git switch -c module-3`), so the refactor in Exercise 4 starts from the original files.

---

## Exercise 1: Tour the structure (10 min)
1. Open `tests/regression/test_cart.py`. Count the locators in it. (Answer: zero. Every locator lives in `pages/`.)
2. Follow `inventory_page.header.cart_badge` from the test into `fixtures/pages.py`, `pages/inventory_page.py`, and `pages/components/header.py`.
3. Ask Claude:
   > Explain how a test in tests/smoke/test_checkout.py gets a logged-in browser. Trace every fixture involved.

   Check its answer against `fixtures/auth.py` and `fixtures/pages.py`.

## Exercise 2: Markers and parallelism (10 min)
```powershell
pytest -m smoke --headed           # watch the 3 critical paths
pytest -m regression               # serial: note the time
pytest -m regression -n auto       # parallel: note the time
pytest -m "not smoke" --collect-only -q
```
Questions:
- How much faster was `-n auto`? Why don't more workers always help? (Hint: CPU cores, and the site's response time.)
- Try `pytest -m smoek`. Why does it select nothing silently, while `@pytest.mark.smoek` on a test fails? (Look at `--strict-markers` in `pytest.ini`.)
- Parallel runs only work because tests are independent. What would break if one test relied on another test's cart?

## Exercise 3: Prove CLAUDE.md is doing the work (20 min)
Ask Claude for the same test twice, once with the standards and once without. Keep everything else the same, so the only difference is `CLAUDE.md`:
- **A new session for each run.** CLAUDE.md is read at session start, and a session that has already seen one answer will copy it.
- **No subagents.** The test-writer's instructions repeat several CLAUDE.md rules, so they would hide the difference. The prompt says so explicitly, because Claude may otherwise hand the task to the agent on its own.
- **Run A's test out of the way before Run B.** Otherwise Run B can simply copy it.

**Run A (with CLAUDE.md):** start a new session and send:
```
Without using any subagent, add a regression test: after sorting by "Price (high to
low)", adding the first product shown puts the Fleece Jacket in the cart.
```
Then move the test it wrote out of the repo, for example to your desktop.

**Run B (without):** rename `CLAUDE.md` to `CLAUDE.md.off`, start a **new** session and send the same prompt. Rename it back afterwards, and put Run A's test back.

Compare: Where did each test go? Did it use page objects and `data/`? Did it get a marker? Any `nth(0)` or `.first`? Then, with `CLAUDE.md` renamed back, run the test-reviewer agent on both files.

Expect Run B to be better than you'd guess. Without `CLAUDE.md`, Claude still reads `pages/`, `fixtures/` and the existing tests, and copies their patterns: **existing code is a standard too**. So ask which differences came from `CLAUDE.md`, and which the code alone would have taught. The rules that only `CLAUDE.md` carries (banned patterns, "run it 10 times", what not to do) are the ones it's worth writing down. In a new project with no code yet, `CLAUDE.md` is the only standard there is (Module 6).

> Notice the trap in the prompt: "the first product shown" invites `.first`. A good answer uses the page object and asserts by name from `data/products.json`, or asks you whether position is really what you want to test.

## Exercise 4: Plan mode for a multi-file refactor (20 min)
Multi-file changes are where Claude is most likely to drift: one file gets the new pattern, another keeps the old one. Plan mode makes Claude propose every change before touching anything.

**Turn on plan mode:** in the Claude Code panel, press **Shift+Tab** until the mode shows **Plan** (or pick it from the mode selector under the prompt box). In the terminal CLI, Shift+Tab also cycles modes.

Prompt:
```
Refactor tests/test_reference.py to follow CLAUDE.md: move it into the right
folder(s) with markers, use the page object fixtures and data/, and delete anything
that duplicates an existing test. Keep every behavior it currently checks.
```
Review the plan **before** approving. Check that:
- [ ] It lists every file it will create, change, or delete
- [ ] Every assertion in the old file still exists somewhere (or the plan says which existing test already covers it)
- [ ] No new locators were invented when a page object already has one
- [ ] It says it will run the suite at the end

Reject the plan and tell Claude what to fix at least once, even if it looks good. Practise steering, not just approving.

Afterwards: `pytest -n auto` must still pass.

## Exercise 5: Extend the standards (15 min)
Add a feature end to end with the test-writer agent and let CLAUDE.md drive the shape:
```
Use the test-writer agent: add coverage for the product detail page (click a product
name on the inventory page). Smoke: the detail page shows the right name and price.
Regression: "Back to products" returns to the inventory, and adding to cart from the
detail page updates the badge.
```
This needs a new page object, so the writer should stop and reply with the files it would add or change instead of writing them. That list is its plan. A good one creates `pages/product_detail_page.py`, exports it from `pages/__init__.py`, adds a fixture in `fixtures/pages.py`, and puts tests in both folders with the right markers. Fix anything missing, then approve:
```
Use the test-writer agent: <same feature>. The files you listed are approved.
```
When it's done, run the test-reviewer agent on the new test files.

Then **add one rule of your own** to CLAUDE.md (e.g. "every page object docstring states its URL", or "regression tests for errors must use parametrize"). Start a new session, ask the test-writer agent for another test, and check that it follows your new rule without being told.

## Exercise 6: Standards for problem users (stretch)
`user_key` can be overridden per test:
```python
@pytest.mark.parametrize("user_key", ["standard", "problem", "error"])
def test_...(inventory_page): ...
```
Ask Claude to run the whole smoke suite as each broken user and write up which tests fail and why. Should these be marked `xfail`, a new marker, or left out? Decide with Claude, then put the decision in CLAUDE.md.

---

## Checklist: is the repo "Claude-ready"?
- [ ] Someone new (or a new Claude session) can find the run commands in under 30 seconds
- [ ] Every rule in CLAUDE.md is something you'd actually reject a PR for
- [ ] Banned patterns are listed with what to do instead
- [ ] It's clear where new pages, components, fixtures, and data go
- [ ] It's short. Claude reads CLAUDE.md every session; it costs context each time, so prune rules that never matter.
