# Module 5: Inside the Writer and Reviewer Subagents

**Goal:** understand, calibrate and extend the subagents that write and review your tests.

Since Module 2 you've been handing work to two subagents that ship with this repo: **test-writer** and **test-reviewer**. In this module you open them up: what a subagent is, why each one is built the way it is, how to check the reviewer is actually right, how to chain the two, and how to build a third one yourself. Then you set limits for every session, not just the agents (deny rules), and pick the numbers that tell you whether all of this is working.

## What a subagent is
A subagent is a separate Claude defined in a Markdown file in `.claude/agents/`. When your main session hands it a task, it:
- starts with a **fresh context**: it sees its own instructions, `CLAUDE.md`, and the task, not your conversation
- uses only the **tools** listed in its file
- returns **only its final answer** to your session, so its snapshots, file reads and test runs don't fill your context

| | Main session | Subagent |
|---|---|---|
| Sees your conversation | yes | no, only the task you give it |
| Tools | everything your session has | only what its file lists |
| Context | grows with every file read and test run | its own; you get back a summary |
| Started by | you | you ("Use the test-reviewer agent...") or Claude, when a task matches its `description` |

A subagent file looks like this:
```markdown
---
name: <lowercase-with-dashes>
description: <when to use it; Claude reads this to decide when to delegate>
tools: <comma-separated list; leave the line out to inherit all tools>
model: <sonnet, haiku, opus or inherit; leave the line out to use your session's model>
---
<the subagent's instructions>
```
Run `/agents` in a session to list, create and edit subagents. Files in `.claude/agents/` are shared with everyone who opens the repo. Subagents are loaded at session start, so start a new session after you edit one.

---

## Exercise 1: Read the two agents (15 min)
Open [.claude/agents/test-writer.md](../../.claude/agents/test-writer.md) and [.claude/agents/test-reviewer.md](../../.claude/agents/test-reviewer.md). Answer:

1. **Tools.** The reviewer lists `Read, Grep, Glob, Bash`. The writer has no `tools` line. What can each one do that the other can't? Why must the reviewer not have `Edit` or `Write`? (A reviewer that can edit will "fix" a test until it passes review.)
2. **Approval.** CLAUDE.md says multi-file changes need your approval first. A subagent can't stop mid-task and ask you. How does the writer handle this instead? (Step 4: it stops and returns a file list. You saw this in Modules 3 and 4.)
3. **Success criteria.** Which step makes the writer refuse a prompt like "write a test for checkout"? Why is refusing better than guessing?
4. **Model.** Both agents set `model: sonnet`, so they don't run on the frontier model even if your session does. Which job could a cheaper model handle (`haiku`), and which would suffer? Exercise 2's calibration is how you'd find out.
5. **Overlap with CLAUDE.md.** Both agents say "follow CLAUDE.md", and the writer repeats some of its rules. What goes wrong if the two drift apart? Which file should own each rule?

## Exercise 2: Calibrate the reviewer (20 min)
A reviewer is only useful if its verdicts are right. Test it against files where you already know the answer:

| Ask Claude | Expected verdict |
|---|---|
| `Use the test-reviewer agent on exercises/bad_test.py` | REJECT. It passes, which is the point of Module 2. |
| `Use the test-reviewer agent on tests/smoke/test_cart.py` | ACCEPT |
| `Use the test-reviewer agent on tests/claude/test_weak.py` (below) | REJECT: the only assertion is on the page title |

Create `tests/claude/test_weak.py` for the third row and delete it afterwards:
```python
import pytest
from playwright.sync_api import expect

from data import PRODUCTS

pytestmark = pytest.mark.regression


def test_adding_backpack_works(inventory_page):
    inventory_page.product(PRODUCTS["backpack"]["name"]).add_to_cart()

    expect(inventory_page.title).to_be_visible()
```
It passes, follows the folder and data rules, and proves nothing: the title is visible whether or not "Add to cart" works.

If a verdict is wrong, edit `test-reviewer.md`, start a new session and run all three again. Changing one rule can break another verdict, so always re-run the full set. Tuning until all three are right is the exercise.

## Exercise 3: Writer, then reviewer (20 min)
Subagents can't call each other. Your main session coordinates: it sends the task to the writer, passes the result to the reviewer, and sends the reviewer's findings back to the writer.

Ask Claude:
```
Feature: "Continue Shopping" on the cart page returns to the products page, and
the cart badge still shows the same count.

1. Use the test-writer agent to write regression tests for it.
2. Use the test-reviewer agent to review what it wrote.
3. If the verdict is REJECT or ACCEPT WITH CHANGES, send the reviewer's findings
   back to the test-writer agent and review again. Stop after 2 rounds.
4. Give me both verdicts and the final file.
```
While it runs, check `/context` in your main session. The agents' snapshots and test runs are not in it.

Review:
- [ ] The writer explored with MCP before writing (look for snapshots in its summary)
- [ ] The reviewer ran the test 10 times and reported the count
- [ ] Reviewer findings went back to the writer, not fixed by the main session
- [ ] The final test ends with an assertion that would fail if "Continue Shopping" were broken
- [ ] `pytest -n auto` still passes

## Exercise 4: Is the reviewer harder than the author? (10 min)
Compare two reviews of the same file:
1. In a session where Claude wrote a test **without** an agent, ask that same session: `Review the test you just wrote against docs/review-checklist.md.`
2. Run the test-reviewer agent on the same file.

Which found more problems? The main session already "knows" why every line was written. The subagent sees only the file and its instructions, like a colleague reviewing a PR.

## Exercise 5: Build a third agent (20 min)
Build a `failure-triager` yourself, using `/agents` to create it (or write the file by hand). Its job: given a failing test, find out why, without changing anything.

Decide for yourself, then compare with a neighbour:
- **Tools.** It needs to run pytest and reproduce the flow in a browser (Playwright MCP), but must not edit files. Which tools does it get?
- **Evidence.** Which evidence should it collect? (Module 4, Exercise 4: failure output, trace, screenshot, browser console.)
- **Verdict.** What should it return? (Suggested: test bug, app bug, or flaky, with the evidence for it.)
- **Description.** When should Claude delegate to it without being asked?

Test it: break a test as in Module 4, Exercise 4 (`tests/smoke/test_cart_broken.py`), and ask `Use the failure-triager agent on tests/smoke/test_cart_broken.py`. It should call it a test bug. Then recreate `tests/smoke/test_cart_problem.py` from Module 4, Exercise 5 and run the triager on it: it should call it an app bug. Delete both files afterwards.

## Exercise 6: Deny rules for every session (20 min)
An agent's `tools` list limits that agent. Deny rules limit **every** session in the repo, including the agents. `allow` rules in [.claude/settings.json](../../.claude/settings.json) skip the permission prompt; `deny` rules block a tool call outright, in every mode, even if something else allows it. Add a `deny` list next to the existing `allow` list:
```json
"deny": [
  "Bash(rm -rf:*)",
  "PowerShell(Remove-Item -Recurse:*)",
  "Bash(git push --force:*)",
  "Bash(git reset --hard:*)",
  "Read(./.env)",
  "Read(./.env.*)",
  "Read(./**/*.pem)",
  "Edit(./.claude/agents/**)"
]
```
Start a new session and test it: ask Claude to read `.env` (create a dummy one first) and to edit `.claude/agents/test-reviewer.md`. Both should be refused without a prompt.

**Now find the gap.** In the same session, ask: `Show me what's in .env using a shell command.` Claude can't use the Read tool, but `Get-Content .env` (or `cat .env`) is a different tool, so it isn't denied. It isn't on the `allow` list either, so you get a permission prompt. Decline it. Delete the dummy `.env` afterwards.

What deny rules do and don't do:
- Each rule matches one tool and one pattern. `Read(./.env)` stops the Read tool, not a shell command, a Python script or an MCP tool that reads the same file.
- `Bash(...)` rules match how a command starts. `Bash(rm -rf:*)` blocks `rm -rf build`, but not `rm -r -f build`.
- They are a seatbelt against mistakes, not a sandbox. Anything that must stay secret shouldn't be in a folder Claude works in. Keep it in environment variables or a secrets manager, and keep the permission prompt on for commands you haven't allowed.

Discuss: why deny edits to the agents? (A Claude that can rewrite the reviewer can make it lenient enough to pass its own tests.) You can still edit the agent files yourself; deny rules only bind Claude. What else in this repo should Claude never touch?

> **Stuck?** The `finished-example` branch has this deny list: `git diff main origin/finished-example -- .claude/settings.json`.

## Exercise 7: Measure it (10 min)
Pick three numbers to track for the capstone and beyond:

| Metric | Definition | How to get it here |
|---|---|---|
| **Flake rate** | Runs that fail and then pass on unchanged code, divided by total runs | `pytest --count 10 -n auto` per new test |
| **Time to author** | From first prompt to a test the reviewer ACCEPTs and that passes 10/10 | Note the start and end time for each test you write |
| **Review rejection rate** | REJECT or ACCEPT WITH CHANGES verdicts, divided by all reviews | Count the test-reviewer verdicts |

Discuss: which of these would you show a client? Which would go up if Claude got worse, and which would go up if your reviewer got stricter?

## Exercise 8: Let Claude delegate on its own (stretch)
You've been naming the agent in each prompt. Claude can also delegate on its own when a task matches an agent's `description`. In a new session, without naming any agent, ask:
```
Add a test that the cart badge disappears after checkout is finished, and make
sure it gets reviewed.
```
Did Claude use both agents without being told? If not, make the `description` lines more specific (e.g. "Use proactively after any test file changes") and try again. Is automatic delegation what you want on a team, or should people name the agent?

---

## Checklist: writer and reviewer
- [ ] You can explain why the reviewer has no `Edit` or `Write` tool
- [ ] The reviewer rejects `bad_test.py` and the title-only test, and accepts the smoke tests
- [ ] Reviewer findings go back to the writer; you don't fix them in the main session
- [ ] Your `failure-triager` can't edit files and returns a verdict with evidence
- [ ] Agent files live in `.claude/agents/`, so the whole team uses the same ones
- [ ] Deny rules block destructive commands, reading secret files and edits to the agents, tested in a new session, and you can name one thing they don't stop
- [ ] You track flake rate, time to author and review rejection rate
- [ ] `tests/claude/test_weak.py` and `tests/smoke/test_cart_broken.py` are deleted
