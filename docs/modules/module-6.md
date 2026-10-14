# Module 6: Capstone

**Goal:** apply everything from Modules 1 to 5 to an app of your own choice, without a reference repo to lean on.

Until now you had saucedemo and this course as a guide: either the finished project was already there and the exercises took it apart and extended it, or you built it stage by stage with `CLAUDE.md` telling Claude what each stage needed. In the capstone you start from an empty folder and an app you haven't tested before, and you build the same kind of project yourself, with Claude. The hard part isn't the tests. It's writing standards and agents that make Claude produce good tests for an app neither of you knows yet, and noticing when it doesn't.

---

## Before you start
Settle these first, before Claude opens a single page:
- **Permission to test.** Use a demo or staging environment you are allowed to test, never production (Module 4, Exercise 4). If you don't have one, ask your instructor for a practice site.
- **Secrets.** Test logins come from environment variables or a secrets manager, never from prompts, `data/` or `CLAUDE.md`. Real secrets don't go in the project folder at all: deny rules are a seatbelt, not a sandbox (Module 5, Exercise 6).
- **Baseline permissions.** Decide which browser tools and commands you pre-approve in `.claude/settings.json`, and which still ask (Module 4, Exercise 4).

## Deliverables
Deliver all of the following in one repository.

| Deliverable | Done when |
|---|---|
| **A tested `CLAUDE.md`** | You ran the same prompt with and without it, in two clean copies (Module 3, Exercise 3), and can show the difference, or explain why there wasn't much of one. It includes a "Fixing failing tests" section (Module 4, Exercise 3). |
| **A coverage map** | A short table: each main user flow, whether it's smoke or regression, and which tests cover it. Flows you chose not to test are listed too, with why. |
| **10 or more tests** | Smoke and regression markers; every test passes `--count 10 -n auto` (report it as run: "10/10, `-n auto`") |
| **One bug caught** | Show one test failing for a real reason: an app bug, a broken user like saucedemo's `problem_user`, or a change you made on purpose and then reverted. Include the failure output. A test that has never failed hasn't shown it can. |
| **Two subagents** | In `.claude/agents/`, each with one job. A reviewer or triager gets a deliberately limited `tools` list. A writer may need editing tools; if it inherits all tools like this repo's, say why that's acceptable. The reviewer is calibrated against known good and bad examples (Module 5, Exercise 2). |
| **Deny rules** | In `.claude/settings.json`, blocking destructive commands, reading secret files and edits to your agents, tested in a new session (Module 5, Exercise 6). The writeup names what they don't stop. |
| **A short writeup** | One page: where Claude's output needed correction, what you changed (prompt, `CLAUDE.md`, agent, deny rule) so it didn't happen again, and your three metrics (Module 5, Exercise 7) |

## Suggested order
| Step | Do | Covered in |
|---|---|---|
| 1 | Settle "Before you start". Set up the project: venv, `requirements.txt`, `pytest.ini`, `conftest.py`, `.mcp.json`, `.claude/settings.json` with your pre-approvals and deny rules (all except the one for `.claude/agents/`, which comes in step 5). Test the deny rules in a new session. | Modules 1, 4 and 5 |
| 2 | Have Claude explore the app with MCP and list its main user flows. Draft the coverage map: which are smoke, which are regression. | Modules 2 and 4 |
| 3 | Run `/init`, then rewrite the `CLAUDE.md` it generates using this repo's as a model. Include "Fixing failing tests" from the start. | Modules 1, 3 and 4 |
| 4 | Write two or three tests with Claude, in plan mode, and review them by hand. Fix what you don't like in `CLAUDE.md`, not just in the code. | Modules 2 and 3 |
| 5 | Add the writer and reviewer agents. Calibrate the reviewer before you trust it. Then add the deny rule for `.claude/agents/` and test it in a new session (from then on, edit the agents by hand). | Module 5 |
| 6 | Write the rest of the tests through the writer → reviewer loop. Record your metrics as you go. | Module 5 |
| 7 | Show one bug caught. Run the with/without `CLAUDE.md` comparison. Write the one-page writeup. | Modules 2, 3 and 5 |

Commit after each step, so you can show how the project and its standards changed.

---

## Rubric
Each row is scored by a reviewer (instructor or peer) reading the repo and the writeup.

| | Meets | Needs work |
|---|---|---|
| **Assertions** | Every test ends with an `expect` on something the act step changed, and would fail if the feature broke | Tests check things that were already true, or only that a page loaded |
| **Independence** | Tests pass in any order and with `-n auto`; no test relies on another's state | Tests share state, or only pass serially |
| **Coverage** | The map covers the app's main flows; choices to skip are explained | Many tests of one easy page; key flows missing |
| **Evidence** | Failures are classified (app bug, test bug, flaky) with output, traces or screenshots | "Fixed" by changing the test, with no evidence |
| **Consistency** | Tests, page objects and agents follow `CLAUDE.md`; exceptions are commented | Rules in `CLAUDE.md` that the code ignores |
| **Tool access** | Each agent's tools match its job, and the writeup says what each one could still do (e.g. `Bash` can edit) | Agents with all tools and no reason given |

## Final checklist
- [ ] `CLAUDE.md` was compared with and without, and says how to fix a failing test without weakening it
- [ ] The coverage map lists every main flow and the tests that cover it
- [ ] Every locator came from a snapshot of the real page, and the committed tests run without MCP
- [ ] Every test passes `--count 10 -n auto`, and one test has been shown to fail for a real reason
- [ ] Two agents, each with tool access you can justify; the reviewer rejects a known-bad test and accepts a known-good one
- [ ] Deny rules block destructive commands, reading secret files and edits to the agents, tested in a new session; you know their gaps
- [ ] No real credentials anywhere in the repo or the prompts
- [ ] The writeup names what Claude got wrong, what you changed so it didn't recur, and your three metrics
