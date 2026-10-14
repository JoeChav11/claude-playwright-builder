# Module 4: Explore, Debug and Fix Failing Tests

**Goal:** have Claude work from the real app, and from real evidence when tests fail, instead of guessing.

In Module 2 you used the Playwright MCP server to look at pages. Here you turn that into a repeatable workflow: Claude explores a feature live, then codifies it into a deterministic pytest file. Then you deal with what happens next: tests fail. You debug failures with real evidence, set the rule that stops Claude "fixing" a test by making it weaker, and check what the browser tools can see and do.

Start a new branch from `main` for this module (`git switch main`, then `git switch -c module-4`), so Exercise 1 starts from the original `Header`.

## Topics
| Topic | What to know |
|---|---|
| Explore, then codify | MCP exploration is for learning the page; the deliverable is a pytest file that runs without MCP |
| Debugging | failure output, trace viewer, screenshots, console logs |
| Fixing failing tests | never make a test pass by weakening it; decide whether the test or the app is wrong first |
| Security | non-production targets only, no real credentials |

---

## Exercise 1: Explore, then codify (25 min)
This is the main exercise. Give the test-writer agent **a feature description only**: no selectors, no steps, no instructions to use MCP. It should explore the app via MCP, then write tests that run without MCP. Then you run them 10 times to check they are stable.

Send only:
```
Use the test-writer agent: Feature: "Reset App State" in the side menu clears the
user's cart. Add tests for it.
```
The menu item has no locator yet, so the writer should explore, then stop and reply with the files it would change. Check its reply before approving:
- [ ] It explored with MCP **before** proposing code. (Nothing in your prompt asked for it. Its instructions and `CLAUDE.md` both did.)
- [ ] New locators came from a snapshot, not from memory
- [ ] If it asked what proves success instead, that's correct too: "clears the cart" doesn't say what the user should see. Answer it and send the task again.

Then approve: `Use the test-writer agent: <same feature>. The files you listed are approved.`

Review the code before accepting:
- [ ] The new locator lives in `Header` (it's in the menu on every page), not in the test
- [ ] The test file has no MCP calls; it is plain pytest-playwright and runs without MCP
- [ ] Assertions use `expect(...)`, products come from `data/`
- [ ] `pytest -n auto` still passes (CLAUDE.md requires this after changing `pages/`)
- [ ] The test-reviewer agent accepts it. Run it on the new file.

> Watch for: what did the snapshot show for the product buttons after the reset? If the app behaves differently from what the feature description says, a good answer reports it to you instead of quietly writing a test that matches either version.

**Check stability: run the new tests 10 times yourself.** The writer reports a 10-run result, but check it rather than trust it. A test that passes once can still be flaky. `pytest-repeat` (in `requirements.txt`) runs each test 10 times; `-n auto` spreads the runs across workers. Replace the file name with the one Claude created:
```powershell
pytest tests/regression/test_reset_app_state.py --count 10 -n auto
```
- Every run must pass (10 per test). **Any failure blocks acceptance until you've classified it.** A test that fails every time is a real app bug or a test bug (Exercises 2 and 3). One that fails some of the time on unchanged code is flaky.
- If a run fails, give Claude the failure output and ask for the cause, not a retry or a longer timeout. Typical causes of flakiness: asserting before the menu finishes animating, or depending on cart state from another test. If the failure only shows up with `-n auto`, run it without `-n auto` too: shared state or resource limits are likely.
- Re-run all 10 after any fix, and write down what you ran ("10/10 with `-n auto`"), not just "stable".
- 10/10 is this course's acceptance gate, not proof. A test that fails 1 run in 50 can pass 10 in a row.

## Exercise 2: Debug with real evidence (20 min)
Break a test on purpose so there is something to debug. In a copy of [tests/smoke/test_cart.py](../../tests/smoke/test_cart.py) saved as `tests/smoke/test_cart_broken.py`, change the expected badge text from `"1"` to `"2"`. Delete the copy when you finish.

1. **Failure output.** Run it and paste the full output to Claude:
   ```powershell
   pytest tests/smoke/test_cart_broken.py
   ```
   Ask: `Why did this fail? Is the bug in the test or in the app?`
2. **Trace viewer.** Record a trace for every test, pass or fail:
   ```powershell
   pytest tests/smoke/test_cart_broken.py --tracing on
   playwright show-trace test-results\<test-folder>\trace.zip
   ```
   Step through the actions, the DOM snapshot at each step, and the network tab. (`--tracing retain-on-failure` keeps traces only for failures; use that day to day.)
3. **Screenshots.** Run with `--screenshot only-on-failure` and open the PNG in `test-results/`. Give it to Claude with `@test-results/...` and ask what the page shows.
4. **Console logs.** Ask Claude to reproduce the flow with MCP and read the browser console:
   > Use the playwright MCP tools to log in as error_user, add the Backpack to the cart, and show me the browser console messages.

   Compare with `standard_user`. Console errors are often the first clue that a failure is the app's fault, not the test's.

Rule: give Claude evidence (output, trace, screenshot, console), not "the test is broken, fix it". Without evidence it will change the assertion to make the test pass.

## Exercise 3: Never weaken the assertion (20 min)
In Exercise 2 the test was wrong, so editing it was the right fix. This time the **app** is wrong. The most common bad "fix" is to change the test until it agrees with the bug. See it happen first.

1. Save this as `tests/smoke/test_cart_problem.py`. It's the cart smoke test with a different product, run as `problem_user` (the `user_key` line from Module 2, Exercise 6):
   ```python
   import pytest
   from playwright.sync_api import expect

   from data import PRODUCTS
   from pages import InventoryPage

   pytestmark = pytest.mark.smoke


   @pytest.mark.parametrize("user_key", ["problem"])
   def test_problem_user_adding_jacket_updates_cart_badge(inventory_page: InventoryPage):
       jacket = inventory_page.product(PRODUCTS["fleece_jacket"]["name"])

       jacket.add_to_cart()

       expect(jacket.remove_button).to_be_visible()
       expect(inventory_page.header.cart_badge).to_have_text("1")
   ```
   Commit it on your module branch, so you have a clean version to go back to:
   ```powershell
   git add tests/smoke/test_cart_problem.py
   git commit -m "Add problem_user cart test (Module 4, Exercise 3)"
   ```
2. Run it. It fails: the Remove button never appears. `problem_user` can't add the Fleece Jacket. That's a real bug in the app, and the test is right to fail.
3. Start a new session and ask Claude, with no other guidance: `tests/smoke/test_cart_problem.py is failing. Make it pass.`
4. Look at the diff. Every edit that makes this test pass hides the bug: switching to a product that works (the Backpack does), switching to `standard_user`, deleting the Remove-button `expect`, adding `xfail` or a longer timeout. Did Claude do one of these, or did it say the app is wrong?

Add a guardrail to `CLAUDE.md`:
```markdown
## Fixing failing tests
- First decide whether the test or the app is wrong, and say which, with evidence
  (failure output, trace, screenshot).
- If the test is wrong (it expects something the app was never meant to do), fix
  it and show the evidence that the old expectation was wrong.
- If the app is wrong, don't edit the test: report the bug. Never change a correct
  expected value, remove an `expect`, loosen a matcher (`to_have_text` to
  `to_contain_text`), add `skip`/`xfail`, add retries or raise a timeout to make
  it pass.
```
That's why Exercise 2's fix was fine: the evidence showed the test expected the wrong badge. Here the evidence points at the app.

Undo whatever Claude changed: run `git status`, then `git restore <file>` for every file it lists (the committed version of `test_cart_problem.py` comes back). Start a new session and repeat step 3. A good answer now calls it an app bug, points to the evidence (the Remove button never appears; compare `standard_user`), and leaves the test alone. If Claude still proposes an edit, run the test-reviewer agent on it. Should it be accepted?

Discuss: a test that correctly catches a known app bug fails on every run. Who decides what happens to it (mark it, ticket it, leave it red), and why shouldn't that be Claude? Remove it afterwards: `git rm tests/smoke/test_cart_problem.py`, then `git commit -m "Remove Module 4 exercise test"`.

**Flaky tests get the same rule.** A test that fails 1 run in 10 has a cause: an assertion before the page settles, shared state between tests, or order-dependent data. Adding `pytest-rerunfailures` or a longer timeout hides the cause and makes the suite slower. When you review a flaky-test fix, it must name the cause, and `pytest <file> --count 10 -n auto` must pass 10/10 after it. Report the run as you made it ("10/10, `-n auto`").

> **Stuck?** The `finished-example` branch has this section in its `CLAUDE.md`: `git diff main origin/finished-example -- CLAUDE.md`. Write your own first, then compare.

## Exercise 4: Security review (10 min)
The MCP browser sees everything you could see in that browser, and every snapshot is sent to the model as context.

Discuss as a group, then check this repo against the list:
- [ ] MCP only points at **non-production** environments. saucedemo.com is a public demo, which is why it's used here.
- [ ] No real credentials in prompts, `data/*.json`, `.mcp.json`, or `CLAUDE.md`. The saucedemo logins are public.
- [ ] Logins for real test environments come from environment variables or a secrets manager, not from the chat.
- [ ] You know which MCP tools are pre-approved in `.claude/settings.json`, and why. This repo pre-approves the browsing tools by name. It leaves out `browser_evaluate` and `browser_run_code_unsafe` (they run any code Claude writes inside the page) and `browser_file_upload` (it sends files from your machine to the site), so those still ask first. Approving the whole server (`"mcp__playwright"`) would approve those too.
- [ ] MCP output folders (`.playwright-mcp/`) and test artifacts (`test-results/`) are git-ignored. Traces and screenshots can contain session tokens and personal data.
- [ ] The MCP server version is pinned (this repo pins it in `.mcp.json`; `@latest` would change between sessions without anyone reviewing it).

What would you change before using this setup on a client's staging environment?

---

## Checklist: exploring, debugging and fixing
- [ ] New locators come from a snapshot, not from memory
- [ ] MCP is for exploring; the committed test is plain pytest that runs without it
- [ ] A new test passes 10 runs in a row before you accept it
- [ ] When a test fails, you give Claude the output, trace, screenshot or console log
- [ ] Claude never makes a test pass by weakening it; `CLAUDE.md` says so
- [ ] `tests/smoke/test_cart_broken.py` and `tests/smoke/test_cart_problem.py` are deleted
- [ ] You never point MCP at production or share real credentials with it
