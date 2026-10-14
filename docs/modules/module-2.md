# Module 2: First Playwright Tests with Claude

**Goal:** generate and review tests instead of accepting them blindly.

You will use Claude Code two ways:
- **Driving the browser live** through the Playwright MCP server (Claude clicks around https://www.saucedemo.com and reads the page's accessibility tree).
- **Writing Python test files** with `pytest-playwright`, which you run and review.

Files for this module: `tests/test_reference.py` (annotated examples, start here), `tests/codegen/`, `tests/claude/`, `exercises/bad_test.py`, [playwright-basics.md](../playwright-basics.md), [review-checklist.md](../review-checklist.md).

This repo ships two subagents in `.claude/agents/`: **test-writer** writes tests, **test-reviewer** reviews them and is told never to edit (it has no editing tools). You use both from this module on; Module 5 looks at how they work.

## Topics
| Topic | What to know |
|---|---|
| What MCP is | Model Context Protocol: a standard way to give Claude extra tools. The Playwright server adds browser tools (`browser_navigate`, `browser_snapshot`, `browser_click`, ...) |
| Managing servers | `claude mcp list`, `claude mcp get <name>`, `/mcp` inside a session |
| Live inspection | Claude navigates, snapshots the accessibility tree, and derives locators from it |
| Locators and `expect` | [playwright-basics.md](../playwright-basics.md): role locators first, web-first assertions that retry |
| Prompt pattern | flow + assertions that prove success + constraints |
| Reviewing | every generated test gets the [review checklist](../review-checklist.md), whoever wrote it |

---

## Exercise 1: What MCP is and which servers are loaded (10 min)
1. Open [.mcp.json](../../.mcp.json). This file registers the `playwright` server for everyone who opens the repo. [.claude/settings.json](../../.claude/settings.json) enables it and pre-approves its browsing tools by name (`mcp__playwright__browser_navigate`, ...). Module 4, Exercise 4 looks at the ones it leaves out.
2. In a terminal (outside Claude), run:
   ```powershell
   claude mcp list
   claude mcp get playwright
   ```
   Note the **scope** of each server: *project* (from `.mcp.json`, shared with the team), *local* or *user* (only on your machine).
3. Inside a Claude session, run `/mcp`. Confirm `playwright` is connected and open it to see its tool list.

Discuss: the server is just a program (`npx @playwright/mcp`) that Claude can call. What can it do on your machine? Who decided it was safe to pre-approve?

## Exercise 2: Let Claude drive (15 min)
Goal: see the page the way Playwright sees it.

Prompt Claude:
> Use the playwright MCP tools to open saucedemo.com, log in as standard_user, and add the Bike Light to the cart. After each step, take a snapshot and list the interactive elements with their role and accessible name. Then open the menu (top left), take a snapshot, and give me each menu item's role, accessible name, and the Playwright Python locator you would use. Don't write any code.

Notice: the snapshot is the accessibility tree. The roles and names there are exactly what `get_by_role("button", name="...")` matches against. This is why role locators come first.

Check its menu answer against the locators this repo already uses, in [pages/components/header.py](../../pages/components/header.py):
- Does the snapshot agree that Logout is a `button`, even though it is an `<a>` tag?
- Which items have a role and name, and which would fall back to `get_by_test_id`?

This is the habit `CLAUDE.md` asks for: "Check roles against the real accessibility tree, not the HTML tag."

## Exercise 3: Record with codegen (10 min)
```powershell
playwright codegen https://www.saucedemo.com --target python-pytest -o tests/codegen/test_recorded.py
```
Log in as `standard_user`, add any item, go to the cart, check out, finish. Close the browser to save. Run it: `pytest tests/codegen -v`.

Open the file and note: Which locator types did codegen pick? Are there any assertions? (Codegen records actions; it only adds assertions if you use its "Assert" toolbar buttons.)

## Exercise 4: Have Claude write the same flow (15 min)
Use the **prompt pattern**: flow + assertions that prove success + constraints. Send it to the test-writer agent:

```
Use the test-writer agent:
FLOW: a logged-in standard user adds the Backpack and the Bike Light to the cart,
opens the cart, checks out as the default customer, and finishes.
ASSERT: cart badge shows 2 before checkout; cart page lists exactly those 2 items;
overview's item total is the sum of their two prices; final page shows
"Thank you for your order!".
CONSTRAINTS: no sleeps, no XPath, no CSS unless nothing else works. Use the
existing page object fixtures and take products and the customer from data/,
no literal names, prices or customer details. One test function, saved in
tests/claude/.
```
The prompt describes the flow in a user's words and points to where the data lives, instead of pasting names and prices into it. A prompt full of literals invites a test full of literals, which this repo's `CLAUDE.md` forbids. You don't need to understand page objects, fixtures or `data/` yet; Module 3 covers them.

Then send a weak prompt to the same agent and compare:
```
Use the test-writer agent: write a playwright test for checkout on saucedemo
```
Did it stop and ask what proves success, or did it assume? (Its instructions say to ask. Check that it does.)

> **This isn't a fair fight, and that's the lesson.** Codegen sees only the clicks you made. The test-writer sees the whole repo: `CLAUDE.md`, the page objects, the fixtures and `data/`. So you're not comparing "codegen vs. Claude"; you're comparing **a recorder vs. Claude working inside a repo with standards**. Expect Claude's test to use page object fixtures (`inventory_page`, `cart_page`, ...) instead of raw locators. What Claude knows about your repo is most of what makes its output good. Module 3 looks at that structure, and Module 3, Exercise 3 shows how much of it comes from `CLAUDE.md`.

## Exercise 5: Review, don't accept (15 min)
1. Read `exercises/bad_test.py` yourself first. Find as many problems as you can using the [review checklist](../review-checklist.md).
2. Run it: `pytest exercises/bad_test.py -v`. **It passes.** That's the point.
3. Ask: `Use the test-reviewer agent on exercises/bad_test.py`. Compare its list to yours.
4. Run the test-reviewer agent on your **codegen** file and on the test-writer's file from Exercise 4. Does it judge them equally, or does Claude-written code get an easier ride?

## Exercise 6: Prove the test catches bugs (stretch)
saucedemo has built-in broken users: `problem_user` and `error_user` see bugs in the cart and checkout. Run your Exercise 4 test as each of them.

Your test never types a username. It gets a logged-in tab from a fixture, and that fixture picks the user from a fixture called `user_key` (default: `"standard"`, the keys are in `data/users.json`). To switch users, add this line directly above the test function:
```python
@pytest.mark.parametrize("user_key", ["problem", "error"])
```
That runs the test once per user; `pytest tests/claude -v` shows one result for each. (Module 3 explains fixtures; for now, this one line is all you need.)
- Does your test fail for both? It should, if it checks what the user sees: these users can't add some products, or can't finish checkout.
- Now `exercises/bad_test.py`: it logs in by typing a username, so change `"standard_user"` to `"problem_user"` in it and run it. Does it fail? If a test can't catch a real bug, it isn't protecting you. Undo the change afterwards (`git restore exercises/bad_test.py`).

## Comparison worksheet
If the weak prompt got a question back instead of a test, write what it asked in the first row and leave the rest of that column empty: asking is the right result. For "Fails for `problem_user`?", the codegen test types its username like `bad_test.py`, so change the string in it, run it, then change it back.

| | Codegen | Claude (strong prompt) | Claude (weak prompt) |
|---|---|---|---|
| Wrote a test, or asked first? (what?) | wrote | | |
| Locator types used | | | |
| Number of `expect` assertions | | | |
| Sleeps / hard waits | | | |
| Fails for `problem_user`? | | | |
| Would you merge it? | | | |

## Clean up
- [ ] `exercises/bad_test.py` is back to `standard_user` (`git restore exercises/bad_test.py`)
- [ ] Your codegen and Claude-written tests are committed on `module-2`
