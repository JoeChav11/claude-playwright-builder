# Module 6: Capstone

**Goal:** apply everything from Modules 1 to 5 to an app of your own choice, without a reference repo to lean on.

Until now you worked on top of a finished project: the page objects, fixtures, `CLAUDE.md` and agents were already there, and the exercises took them apart and extended them. In the capstone you start from an empty folder and an app you haven't tested before, and you build the same kind of project yourself, with Claude. The hard part isn't the tests. It's writing standards and agents that make Claude produce good tests for an app neither of you knows yet, and noticing when it doesn't.

Use a demo or staging environment you are allowed to test, never production (Module 4, Exercise 4). If you don't have one, ask your instructor for a practice site.

---

## Deliverables
Deliver all of the following in one repository.

| Deliverable | Done when |
|---|---|
| **A tested `CLAUDE.md`** | You ran the same prompt with and without it (Module 3, Exercise 3) and can show the difference. It includes a "Fixing failing tests" section (Module 4, Exercise 3). |
| **10 or more tests** | Smoke and regression markers; every test passes `--count 10 -n auto` |
| **Two subagents** | In `.claude/agents/`, each with one job and a deliberately limited `tools` list (e.g. a writer and a reviewer, or a reviewer and a failure-triager). The reviewer is calibrated against known good and bad examples (Module 5, Exercise 2). |
| **Deny rules** | In `.claude/settings.json`, blocking destructive commands, reading secret files and edits to your agents, tested in a new session (Module 5, Exercise 6). The writeup names what they don't stop. |
| **A short writeup** | One page: where Claude's output needed correction, what you changed (prompt, `CLAUDE.md`, agent, deny rule) so it didn't happen again, and your three metrics (Module 5, Exercise 7) |

## Suggested order
| Step | Do | Covered in |
|---|---|---|
| 1 | Pick the app. Have Claude explore it with MCP and list its main user flows. Choose which are smoke and which are regression. | Modules 2 and 4 |
| 2 | Set up the project: venv, `requirements.txt`, `pytest.ini`, `conftest.py`, `.mcp.json`. Run `/init`, then rewrite the `CLAUDE.md` it generates using this repo's as a model. | Modules 1 and 3 |
| 3 | Write two or three tests with Claude, in plan mode, and review them by hand. Fix what you don't like in `CLAUDE.md`, not just in the code. | Modules 2 and 3 |
| 4 | Add the writer and reviewer agents. Calibrate the reviewer before you trust it. | Module 5 |
| 5 | Write the rest of the tests through the writer → reviewer loop. Record your metrics as you go. | Module 5 |
| 6 | Add the "Fixing failing tests" section and the deny rules, and test both in a new session. | Modules 4 and 5 |
| 7 | Write the one-page writeup. | |

Commit after each step, so you can show how the project and its standards changed.

---

## Final checklist
- [ ] `CLAUDE.md` makes a visible difference, and says how to fix a failing test without weakening it
- [ ] Every locator came from a snapshot of the real page, and the committed tests run without MCP
- [ ] Every test passes `--count 10 -n auto`
- [ ] Two agents with limited tools; the reviewer rejects a known-bad test and accepts a known-good one
- [ ] Deny rules block destructive commands, reading secret files and edits to the agents, tested in a new session; you know their gaps
- [ ] No real credentials anywhere in the repo or the prompts
- [ ] The writeup names what Claude got wrong, what you changed so it didn't recur, and your three metrics
