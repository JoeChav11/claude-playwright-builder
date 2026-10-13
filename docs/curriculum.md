# Claude Code for Playwright Test Automation (Python)

**Audience:** QA and automation engineers. Some Python helps; no prior Claude Code experience needed.
**Duration:** 5 modules of about 2 hours each (timed exercises take 65 to 115 minutes per module; the rest is teaching and discussion), then a capstone project in Module 6.
**Practice target:** https://www.saucedemo.com, or a demo/staging app you are allowed to test. Never production.

This is the course overview. The full exercises are in [modules/](modules/), and the finished reference repo is this one. To build your own project from scratch without the repo's `CLAUDE.md`, see [Starting without a CLAUDE.md](#starting-without-a-claudemd) at the end.

## Installation checklist

| Tool | Purpose | Command / source |
|---|---|---|
| VS Code | Editor | code.visualstudio.com |
| Claude Code VS Code extension | The agent: chat panel, inline diffs, permission modes | VS Code Marketplace, "Claude Code" (publisher: Anthropic). Needs a paid Claude plan or an API key. |
| Claude Code CLI (optional) | Run `claude` in a terminal; used for `claude mcp list` and headless `claude -p` | `irm https://claude.ai/install.ps1 \| iex` (Windows PowerShell), `curl -fsSL https://claude.ai/install.sh \| bash` (macOS/Linux) |
| Python 3.10+ | Language | python.org (Windows: tick "Add python.exe to PATH"), then create a venv |
| Node.js LTS (18+) | Runs the Playwright MCP server via `npx` | nodejs.org |
| Google Chrome | The browser the MCP server opens | google.com/chrome |
| Git | Clone, one branch per module | git-scm.com |
| Python extension for VS Code (optional) | Highlighting, run tests from the editor | Marketplace, "Python" (Microsoft) |
| Playwright for Python | Test framework | `pip install -r requirements.txt` (pytest, pytest-playwright, pytest-xdist, pytest-repeat), then `playwright install chromium` |
| Playwright MCP | Lets Claude drive a browser | Checked into the repo as `.mcp.json`, pinned to `@playwright/mcp@0.0.83` (Windows wraps `npx` in `cmd /c`). Check with `/mcp`. |

Install commands change. Verify against the Claude Code docs before the session.

## Module 1: Claude Code fundamentals
**Goals:** Operate Claude Code safely and control its context.
- Run `claude` in the VS Code terminal and via the extension
- Permission modes: default, accept edits, plan mode (Shift+Tab)
- Context management: `/clear`, `/compact`, `/context`, referencing files with `@`
- Built-in slash commands, `/init`, and how `CLAUDE.md` is loaded
- Reviewing diffs before accepting, and undoing with `/rewind`

**Exercise:** Scaffold an empty repo, run `/init`, and explain what the generated `CLAUDE.md` does and what it couldn't infer.

## Module 2: First Playwright tests with Claude
**Goals:** Generate and review tests instead of accepting them blindly.
- What MCP is, and managing servers with `claude mcp list` and `/mcp`
- Let Claude drive the browser with MCP, snapshot the accessibility tree, and derive locators from the live page
- Playwright Python basics: `page`, locators, auto-waiting, `expect`
- Locator priority: role, label, placeholder/text, then test-id (`data-test`), with CSS last and XPath never
- Compare `playwright codegen` output to Claude-written tests
- Prompt pattern: state the user flow, the assertions that prove success, and the constraints (no `sleep`, no brittle selectors)
- The repo ships two subagents from here on: **test-writer** writes tests, **test-reviewer** reviews them and never edits

**Exercise:** Check which MCP servers are loaded, and have Claude drive the site and report roles and names. Have the test-writer write a checkout test from a strong prompt and a weak one. Review a passing-but-bad test (`exercises/bad_test.py`) by hand, then with the test-reviewer. Check whether your tests fail for `problem_user`.

## Module 3: Structuring the test repo and encoding standards
**Goals:** Make Claude produce consistent code.
- Layout: `tests/smoke/`, `tests/regression/`, `pages/`, `pages/components/`, `conftest.py`, `fixtures/`, `data/`
- Page Object Model vs. component helpers
- pytest fixtures, strict markers (`smoke`, `regression`), `pytest-xdist` parallelism
- A `CLAUDE.md` for the test repo covering:
  - Run commands (`pytest -m smoke --headed`)
  - Where new pages, components, fixtures and data go
  - Naming and locator rules
  - Banned patterns (`time.sleep`, XPath, `.first`/`.nth()`, `assert ... is_visible()`)
  - Where test data lives
- Use plan mode for multi-file refactors

**Exercise:** Run the same prompt with and without `CLAUDE.md` and compare. Refactor the Module 2 tests into page objects in plan mode. Add one rule of your own and check Claude follows it.

## Module 4: Explore, debug and fix failing tests
**Goals:** Have Claude work from the real app, and from real evidence when tests fail, instead of guessing.
- Explore-then-codify workflow: Claude explores the flow via MCP, then writes a deterministic pytest file
- Debugging: feed Claude the failure output, traces (`--tracing retain-on-failure`), screenshots and console logs
- Fixing failing tests: a "Fixing failing tests" section in `CLAUDE.md` so Claude never "fixes" a test by weakening the assertion, and flaky-test fixes name the root cause instead of adding retries or longer timeouts
- Security: only point MCP at non-production environments, never expose real credentials, and know which browser tools are pre-approved

**Exercise:** Give the test-writer a feature description only (e.g. "Reset App State" clears the cart). It explores with MCP, then writes tests. Run them 10 times (`--count 10 -n auto`) to check stability. Debug a broken test with its output, trace and screenshot. Then ask Claude to "make it pass" when the app is the one that's wrong, add the "Fixing failing tests" rule, and compare.

## Module 5: Inside the writer and reviewer subagents
**Goals:** Understand, calibrate and extend the subagents that write and review tests.
- What a subagent is: its own context, its own `tools` list, its own `model`, started by name or by matching its `description`
- Why the reviewer has no `Edit`/`Write`, and why the writer returns a file list instead of waiting for approval
- Both agents run on `model: sonnet` to keep costs down; choosing a model per job
- Calibrating a reviewer against known good and bad tests
- The writer → reviewer loop, and whether a reviewer is harder on code than its author
- Deny rules in `.claude/settings.json`: block destructive commands, reading secret files and edits to the agents, for every session. A seatbelt, not a sandbox: each rule matches one tool and pattern
- Metrics: flake rate, time to author a test, review rejection rate

**Exercise:** Calibrate the test-reviewer (it must reject `bad_test.py` and accept a smoke test), run a writer → reviewer loop, then build a third agent yourself: a read-only `failure-triager` that returns test bug, app bug or flaky with evidence. Add deny rules and test them in a new session.

The "Fixing failing tests" section (Module 4) and the deny rules (Module 5) are deliberately not on `main`: students build them. The `finished-example` branch has both to compare against.

## Module 6: Capstone
**Goals:** Apply Modules 1 to 5 to an app of your own choice.

For a chosen app (not saucedemo), deliver:
1. A tested `CLAUDE.md` (shown to make a difference, as in Module 3), with a "Fixing failing tests" section
2. 10 or more UI tests with smoke and regression markers, each passing `--count 10 -n auto`
3. Two subagents with limited `tools` lists, the reviewer calibrated
4. Deny rules, tested in a new session
5. A short writeup of where Claude's output needed correction, what you changed so it didn't recur, and your three metrics

## Common pitfalls to teach
- Tests that pass but assert nothing meaningful
- Selector guesses without checking the live accessibility tree
- Context bloat in long sessions (use `/clear` and `/compact`)
- Auto-accepting edits without reading diffs
- Retries and longer timeouts masking real flakiness
- "Fixing" a failing test by changing what it expects

## Starting without a CLAUDE.md
If you're building your own project in an empty folder and don't have the repo's `CLAUDE.md`, put this file in the folder, open it in Claude Code, and ask:

```
Read curriculum.md. Draft a CLAUDE.md for this project that covers everything in
the list under "What the CLAUDE.md must contain". Don't create any other files yet.
```

Read the draft before you accept it, then start a new session so Claude loads it.

### What the CLAUDE.md must contain
- **How to build:** first ask who writes the tests (Claude writes and the student reviews, or the reverse). Build one stage per module, in order, planning each stage in plan mode. After each stage, stop so the student can run its check and commit it (stage 1 on `main`, then `git switch -c module-N`). Never build two stages at once. The module exercises are written for the cloned repo; the table says which ones work after each stage. Until stage 5, steps that use an agent go to the main session.
- **Stages and checks:**

  | Stage | Builds | Check | Exercises that work |
  |---|---|---|---|
  | 1. Setup | `git init`, `.gitignore`, `requirements.txt`, `pytest.ini` (base_url, chromium, strict `smoke`/`regression` markers), `conftest.py` (`data-test` as the test-id attribute), `.mcp.json` (Playwright MCP pinned to `@playwright/mcp@0.0.83`), `.claude/settings.json` (enable the MCP server, allow `pytest` and the browsing tools by name), venv, `playwright install chromium` | `pytest` runs; `/mcp` shows `playwright` connected | Module 1 (no agents in `/agents` yet) |
  | 2. First tests | A few annotated beginner tests, a `logged_in_page` fixture with a `user_key` override, a passing-but-bad test to review | Tests pass | Module 2, writing and reviewing in the main session, with inline locators |
  | 3. Structure | `data/*.json`, page objects, components, page fixtures, smoke and regression tests | `pytest -n auto` passes | Module 3, Ex 5 in the main session |
  | 4. MCP-driven tests | One feature tested from a description only, explored with MCP first. Then the student writes a "Fixing failing tests" section in `CLAUDE.md`; Claude guides | Passes `--count 10 -n auto`; Claude won't weaken a failing test | Module 4; Ex 1 is the build |
  | 5. Subagents | `.claude/agents/test-writer.md` (all tools) and `test-reviewer.md` (`Read, Grep, Glob, Bash`; never edits), both `model: sonnet`. Then the student adds deny rules; Claude guides | The reviewer rejects the bad test and accepts a good one; deny rules refuse in a new session | Module 5, as written |
  | 6. Capstone | Nothing in this project: a new project for the student's own app | See Module 6 | Module 6 |

- **Run commands:** smoke headed, parallel runs (`-n auto`), one test, debugging with traces and screenshots, the 10-run stability check.
- **Standards:** the layout and where new code goes, page object rules (locators in `__init__`, no assertions), test rules (markers, naming, arrange/act/assert, `parametrize`, independent tests), the locator priority, and the banned patterns with what to do instead.
- **Working style:** plan mode for multi-file changes; take a `browser_snapshot` with the Playwright MCP before writing locators; reuse existing page objects and fixtures; run each test and confirm it passes before reporting done.
