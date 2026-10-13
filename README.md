# Claude Code + Playwright Training

Hands-on modules for using Claude Code to write, review and structure Playwright (Python) tests against the live practice site https://www.saucedemo.com.

| Module | Goal | Guide |
|---|---|---|
| 1. Claude Code fundamentals | Operate Claude Code safely and control its context | [docs/modules/module-1.md](docs/modules/module-1.md) |
| 2. First Playwright tests with Claude | Generate and review tests instead of accepting them blindly | [docs/modules/module-2.md](docs/modules/module-2.md) |
| 3. Structuring the test repo and encoding standards | Make Claude produce consistent code | [docs/modules/module-3.md](docs/modules/module-3.md) |
| 4. Playwright MCP and browser-aware authoring | Have Claude inspect the real app instead of guessing selectors | [docs/modules/module-4.md](docs/modules/module-4.md) |
| 5. Inside the writer and reviewer subagents | Understand, calibrate and extend the subagents that write and review tests | [docs/modules/module-5.md](docs/modules/module-5.md) |
| 6. CI integration, guardrails, capstone | Run it in a pipeline and keep quality controlled | [docs/modules/module-6.md](docs/modules/module-6.md) |

## How to use this repo
This repo is the **reference result**: what a finished project looks like. There are two ways to use it.

**1. Work on top of it.** Clone the whole repo. The page objects, fixtures, test data, tests, `CLAUDE.md` and subagents are already there, and every exercise runs on top of them: you use them, take them apart to see why they're built that way, and extend them. Each module explains its part of the repo. Module 6 is the exception: the CI workflow, the deny rules and the "Fixing failing tests" section of `CLAUDE.md` are deliberately **not** in the repo, and you build them yourself.

**2. Build your own from scratch.** Start an empty folder with only this `README.md` and `CLAUDE.md` (add `docs/` too if you want the full exercises), open it in Claude Code, and ask Claude to help you build the project. `CLAUDE.md` tells Claude to build it in six stages that follow the modules, to stop after each stage so you can run and commit it, and to ask first who writes the tests.

The general use case is to begin with learning how to interact with Claude Code. Use Claude to build a similar repo to this one with the outlines listed above. You can make it your own! This is meant to be a guide only! Also keep in mind you can choose to allow Claude to build everything, or build alongside the AI with writing manual tests to further your code writing skills. Have fun with it!

Because you extend the repo as you go, your copy will end up different from `main`. That's expected. Work on your own branch for each module, so your exercise changes stay separate from the reference:
```powershell
git switch -c module-2       # start a module
git diff main                # see what you changed compared with the reference
git switch main              # back to the reference version
```

You will use Claude Code two ways:
- **Driving the browser live** through the Playwright MCP server (Claude clicks around the site and reads its accessibility tree).
- **Writing Python test files** with `pytest-playwright`, which you run and review.

## Project layout
```
CLAUDE.md                  Standards Claude follows in this repo (read it!)
.mcp.json                  Registers the Playwright MCP server
.claude/agents/            test-writer and test-reviewer subagents     (used from Module 2, explained in Module 5)
.claude/settings.json      Enables the MCP server, pre-approved commands
conftest.py                Registers fixtures/, sets data-test as the test-id attribute
pytest.ini                 base_url, browser, markers (smoke, regression)

tests/smoke/               Critical-path tests                         (Module 3)
tests/regression/          Edge cases and error handling               (Module 3)
pages/                     Page objects, one per URL                   (Module 3)
pages/components/          Shared UI pieces: Header, ProductCard       (Module 3)
fixtures/                  pytest fixtures: login, page objects        (Module 3)
data/                      Test data: users, products, customers       (Module 3)

tests/test_reference.py    Annotated beginner examples                 (Module 2)
tests/codegen/             Your codegen recordings                     (Module 2)
tests/claude/              Claude-written tests                        (Module 2)
exercises/bad_test.py      A passing-but-bad test to review            (Module 2)

docs/                      Module guides, cheat sheet, review checklist, POM guide
```

## Setup
### Before you start: install these
Do this before the session. Installs can take 20 to 30 minutes on a fresh machine.

| # | What | Why you need it | Get it | Notes |
|---|---|---|---|---|
| 1 | **VS Code** | Editor where you run Claude Code and read the tests | https://code.visualstudio.com | |
| 2 | **Claude Code extension** | The AI agent that writes and reviews tests and drives the browser | In VS Code: Extensions (`Ctrl+Shift+X`), search "Claude Code" (publisher: Anthropic) | Sign in with your Claude account when prompted. You need a paid plan (Pro, Max, Team or Enterprise) or an API key. |
| 3 | **Python 3.10 or newer** | Runs the Playwright tests (pytest) | https://www.python.org/downloads | **Windows: tick "Add python.exe to PATH"** on the first installer screen. |
| 4 | **Node.js LTS** (18 or newer) | Runs the Playwright MCP server that lets Claude control the browser | https://nodejs.org | Default installer options are fine. |
| 5 | **Google Chrome** | The browser the MCP server opens | https://www.google.com/chrome | Tests use their own bundled Chromium, installed in Setup below. |
| 6 | **Python extension for VS Code** (optional) | Syntax highlighting, and lets you run tests from the editor | Extensions, search "Python" (publisher: Microsoft) | |
| 7 | **Git** | Get the project with `git clone`, keep each module on its own branch, and push to GitHub in Module 6 | https://git-scm.com | |
| 8 | **GitHub account** (Module 6 only) | Runs the CI workflow | https://github.com | |
| 9 | **Anthropic API key** (Module 6 only) | Lets Claude run in CI to triage failures | https://console.anthropic.com | Stored as a GitHub repository secret, never in the repo. |

**Network:** you need access to `pypi.org`, `registry.npmjs.org`, the Playwright browser download servers and `saucedemo.com`. If you're on a corporate VPN or proxy and installs hang, try off-VPN or ask IT.

**No other credentials needed before Module 6.** The Playwright MCP server runs locally with no API key, and the practice site's logins are public (they're shown on its login page).

#### Check your installs
Close and reopen your terminal after installing, then run:
```powershell
code --version      # VS Code
python --version    # 3.10 or newer (macOS/Linux: python3 --version)
node --version      # v18 or newer
npx --version       # comes with Node
```
If a command says "not recognized" or "not found", that tool isn't installed or isn't on your PATH. Reinstall it (for Python, with "Add to PATH" ticked) and reopen the terminal.

### Install the project
> Building from scratch (option 2 above)? Skip this section. Claude sets the project up with you in stage 1.

Clone the repo (`git clone <repo-url>`), open the folder in VS Code (**File > Open Folder**), then open a terminal (**Terminal > New Terminal**) and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
pytest -n auto                        # 23 tests should pass
```

Then open the Claude Code panel in VS Code (with this folder open, so it loads `CLAUDE.md` and `.mcp.json`) and run `/mcp`. You should see `playwright` connected. On macOS/Linux, change `.mcp.json` to `"command": "npx", "args": ["-y", "@playwright/mcp@0.0.83"]`.

> Windows: if `Activate.ps1` is blocked, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.
> If `python -m venv` fails with "No module named 'encodings'", that Python install is broken. List others with `py -0p` and use one, e.g. `py -3.14 -m venv .venv`.

## Running tests
Activate the venv in each new terminal (`.\.venv\Scripts\Activate.ps1`), then:

| Command | Purpose |
|---|---|
| `pytest -n auto` | Everything, in parallel |
| `pytest -m smoke --headed` | Critical paths, watching the browser |
| `pytest -m regression -n auto` | Regression suite, in parallel |
| `pytest tests/test_reference.py -v` | Module 2 examples only |
| `pytest -k checkout -v` | Tests whose name contains "checkout" |
| `pytest --headed --slowmo 500` | Slow motion, to follow along |
| `pytest --tracing retain-on-failure` | Save a trace on failure; open with `playwright show-trace <zip>` |
| `pytest --tracing on` | Save a trace for every test, pass or fail |
| `pytest --screenshot only-on-failure` | Save a screenshot of the page when a test fails (in `test-results/`) |
| `pytest <file> --count 10 -n auto` | Run a test 10 times to check it is not flaky |
| `playwright codegen <url> --target python-pytest` | Record a test |

You can also ask Claude in the panel, e.g. "run the smoke tests headed".

## Reference
- [docs/playwright-basics.md](docs/playwright-basics.md): page, locators, auto-waiting, expect
- [docs/review-checklist.md](docs/review-checklist.md): what to check in any generated test
- [docs/pom-vs-components.md](docs/pom-vs-components.md): page objects vs. component helpers
