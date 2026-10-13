# Module 4: Playwright MCP and Browser-Aware Authoring

**Goal:** have Claude inspect the real app instead of guessing selectors.

Without a browser, Claude writes locators from memory of what pages "usually" look like. With the Playwright MCP server, it opens the real page, reads the accessibility tree, and builds locators from what is actually there. In this module you turn that into a repeatable workflow: explore live, then codify into a deterministic pytest file, then debug it with real evidence instead of guesses.

## Topics
| Topic | What to know |
|---|---|
| What MCP is | Model Context Protocol: a standard way to give Claude extra tools. The Playwright server adds browser tools (`browser_navigate`, `browser_snapshot`, `browser_click`, ...) |
| Managing servers | `claude mcp list`, `claude mcp get <name>`, `/mcp` inside a session |
| Live inspection | Claude navigates, snapshots the accessibility tree, and derives locators from it |
| Explore, then codify | MCP exploration is for learning the page; the deliverable is a pytest file that runs without MCP |
| Debugging | failure output, trace viewer, screenshots, console logs |
| Fixing failing tests | never make a test pass by weakening it; decide whether the test or the app is wrong first |
| Security | non-production targets only, no real credentials |

---

## Exercise 1: What MCP is and which servers are loaded (10 min)
1. Open [.mcp.json](../../.mcp.json). This file registers the `playwright` server for everyone who opens the repo. [.claude/settings.json](../../.claude/settings.json) enables it and pre-approves its tools (`mcp__playwright`).
2. In a terminal (outside Claude), run:
   ```powershell
   claude mcp list
   claude mcp get playwright
   ```
   Note the **scope** of each server: *project* (from `.mcp.json`, shared with the team), *local* or *user* (only on your machine).
3. Inside a Claude session, run `/mcp`. Confirm `playwright` is connected and open it to see its tool list.

Discuss: the server is just a program (`npx @playwright/mcp`) that Claude can call. What can it do on your machine? Who decided it was safe to pre-approve?

## Exercise 2: Snapshot the real page (10 min)
Prompt Claude:
> Use the playwright MCP tools to open saucedemo.com, log in as standard_user, and open the menu (top left). Take a snapshot. For each menu item, give me its role, accessible name, and the Playwright Python locator you would use. Don't write any code.

Check its answer against [pages/components/header.py](../../pages/components/header.py):
- Does the snapshot agree that Logout is a `button`, even though it is an `<a>` tag?
- Which items have a role and name, and which would fall back to `get_by_test_id`?

This is the habit `CLAUDE.md` asks for: "Check roles against the real accessibility tree, not the HTML tag."

## Exercise 3: Explore, then codify (25 min)
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
- Every run must pass (10 per test). One failure means the test is flaky. Don't accept it yet.
- If a run fails, give Claude the failure output and ask for the cause, not a retry or a longer timeout. Typical causes: asserting before the menu finishes animating, or depending on cart state from another test.
- Re-run all 10 after any fix.

## Exercise 4: Debug with real evidence (20 min)
Break a test on purpose so there is something to debug. In a copy of [tests/smoke/test_cart.py](../../tests/smoke/test_cart.py) saved as `tests/smoke/test_cart_broken.py`, change the expected badge text from `"1"` to `"2"`. Keep the copy for Exercise 5, and delete it after that.

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

## Exercise 5: Never weaken the assertion (20 min)
The most common bad "fix" is to change the test until it agrees with the bug. See it happen first, with the broken copy from Exercise 4:

1. Start a new session and ask Claude, with no other guidance: `tests/smoke/test_cart_broken.py is failing. Make it pass.`
2. Look at the diff. Did it change `"2"` back to `"1"` (correct here, because the test was wrong) or did it reason about **which side is wrong**? Now imagine the app had the bug. The same edit would hide it.

Add a guardrail to `CLAUDE.md`:
```markdown
## Fixing failing tests
- Never change an expected value, remove an `expect`, loosen a matcher
  (`to_have_text` to `to_contain_text`), add `skip`/`xfail`, add retries or
  raise a timeout to make a test pass.
- First decide whether the test or the app is wrong, and say which, with evidence
  (failure output, trace, screenshot). If the app is wrong, don't edit the test:
  report the bug.
```
Start a new session and repeat step 1. What changed in Claude's answer? Run the test-reviewer agent on whatever it proposes. Delete `tests/smoke/test_cart_broken.py` afterwards.

**Flaky tests get the same rule.** A test that fails 1 run in 10 has a cause: an assertion before the page settles, shared state between tests, or order-dependent data. Adding `pytest-rerunfailures` or a longer timeout hides the cause and makes the suite slower. When you review a flaky-test fix, it must name the cause, and `pytest <file> --count 10 -n auto` must pass 10/10 after it.

> **Stuck?** The `finished-example` branch has this section in its `CLAUDE.md`: `git diff main origin/finished-example -- CLAUDE.md`. Write your own first, then compare.

## Exercise 6: Security review (10 min)
The MCP browser sees everything you could see in that browser, and every snapshot is sent to the model as context.

Discuss as a group, then check this repo against the list:
- [ ] MCP only points at **non-production** environments. saucedemo.com is a public demo, which is why it's used here.
- [ ] No real credentials in prompts, `data/*.json`, `.mcp.json`, or `CLAUDE.md`. The saucedemo logins are public.
- [ ] Logins for real test environments come from environment variables or a secrets manager, not from the chat.
- [ ] You know which MCP tools are pre-approved in `.claude/settings.json`, and why.
- [ ] MCP output folders (`.playwright-mcp/`) and test artifacts (`test-results/`) are git-ignored. Traces and screenshots can contain session tokens and personal data.
- [ ] The MCP server version is pinned (this repo pins it in `.mcp.json`; `@latest` would change between sessions without anyone reviewing it).

What would you change before using this setup on a client's staging environment?

---

## Checklist: browser-aware authoring
- [ ] You can list, inspect and check the status of MCP servers
- [ ] New locators come from a snapshot, not from memory
- [ ] MCP is for exploring; the committed test is plain pytest that runs without it
- [ ] A new test passes 10 runs in a row before you accept it
- [ ] When a test fails, you give Claude the output, trace, screenshot or console log
- [ ] Claude never makes a test pass by weakening it; `CLAUDE.md` says so
- [ ] `tests/smoke/test_cart_broken.py` is deleted
- [ ] You never point MCP at production or share real credentials with it
