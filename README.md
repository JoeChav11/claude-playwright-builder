# Claude Code + Playwright Training

Hands-on modules for using Claude Code to write, review and structure Playwright (Python) tests against the live practice site https://www.saucedemo.com.

| Module | Goal | Guide |
|---|---|---|
| 1. Claude Code fundamentals | Operate Claude Code safely and control its context | [docs/modules/module-1.md](docs/modules/module-1.md) |
| 2. First Playwright tests with Claude | Generate and review tests instead of accepting them blindly | [docs/modules/module-2.md](docs/modules/module-2.md) |
| 3. Structuring the test repo and encoding standards | Make Claude produce consistent code | [docs/modules/module-3.md](docs/modules/module-3.md) |
| 4. Explore, debug and fix failing tests | Have Claude work from the real app and from real evidence, instead of guessing | [docs/modules/module-4.md](docs/modules/module-4.md) |
| 5. Inside the writer and reviewer subagents | Understand, calibrate and extend the subagents that write and review tests | [docs/modules/module-5.md](docs/modules/module-5.md) |
| 6. Capstone | Apply everything to an app of your own choice | [docs/modules/module-6.md](docs/modules/module-6.md) |

## How to use this repo
This repo is the **reference result**: what a finished project looks like. There are two ways to use it.

**1. Work on top of it.** Clone the whole repo. The page objects, fixtures, test data, tests, `CLAUDE.md` and subagents are already there, and every exercise runs on top of them: you use them, take them apart to see why they're built that way, and extend them. Each module explains its part of the repo. The guardrails are the exception: the "Fixing failing tests" section of `CLAUDE.md` (Module 4) and the deny rules in `.claude/settings.json` (Module 5) are deliberately **not** on `main`, and you build them yourself. If you get stuck, compare with the `finished-example` branch, which has both: `git diff main origin/finished-example`. Module 6 is a capstone: you build a project like this one for an app of your own.

**2. Build your own from scratch.** Make a new empty folder (not inside a clone of this repo) and copy in only this `README.md` and `CLAUDE.md`, from a clone or downloaded from GitHub. Add `docs/` too if you want the full exercises. Do Module 1 first if you're new to Claude Code: most of it doesn't need the project, and it teaches plan mode, which every stage uses. Then open the folder in Claude Code and ask Claude to help you build the project. `CLAUDE.md` tells Claude to build it in five stages that follow Modules 1 to 5, to stop after each stage so you can run and commit it, and to ask first who writes the tests. The module exercises are written for the cloned repo; the stage table in `CLAUDE.md` says which ones work after each stage and what to change (until stage 5 there are no subagents, so those steps go to the main session).

No `CLAUDE.md`? Start from [docs/curriculum.md](docs/curriculum.md) instead: its last section has the prompt to have Claude draft one, and what it must contain.

Either way, you choose how much Claude writes. Claude can write the tests while you review them, or you can write them yourself, with Claude reviewing, to build your own Playwright skills. The repo is a guide, not a template: make your project your own.

Because you extend the repo as you go, your copy will end up different from `main`. That's expected. Work on your own branch for each module, so your exercise changes stay separate from the reference. Some modules start fresh from the reference; others build on your previous module:

| Module | Start its branch from | Why |
|---|---|---|
| 1 | no branch needed | Exercises use a throwaway `scratch/` folder and a separate demo folder |
| 2 | `main` | Uses the reference as shipped |
| 3 | `main` | Exercise 4 refactors the original `tests/test_reference.py` |
| 4 | `main` | Exercise 1 needs the original `Header`, without your Module 3 changes |
| 5 | your `module-4` branch | Keeps the "Fixing failing tests" section you wrote in Module 4 |
| 6 | a new repository | The capstone is a new project for your own app |

```powershell
git switch main
git switch -c module-4            # start a module from main...
git switch -c module-5 module-4   # ...or from your previous module
git diff main                     # see what you changed compared with the reference
```
Each module's checklist ends with what to clean up, so failing exercise files don't follow you into the next module.

Building from scratch (option 2)? Each stage's branch starts from the previous stage's branch, so your work carries forward.

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
requirements.txt           Packages the project needs
constraints.txt            Exact versions the course was tested with (pip install ... -c constraints.txt)

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

docs/                      Curriculum overview, module guides, cheat sheet, review checklist, POM guide
```

## Setup
### Before you start: install these
Do this before the session. Installs can take 20 to 30 minutes on a fresh machine.

| # | What | Why you need it | Get it | Notes |
|---|---|---|---|---|
| 1 | **VS Code** | Editor where you run Claude Code and read the tests | https://code.visualstudio.com | |
| 2 | **Claude Code extension** | The AI agent that writes and reviews tests and drives the browser | In VS Code: Extensions (`Ctrl+Shift+X`), search "Claude Code" (publisher: Anthropic) | Sign in with your Claude account when prompted. You need a paid plan (Pro, Max, Team or Enterprise) or an API key. |
| 3 | **Claude Code CLI** (required) | Runs `claude` in a terminal. Modules 1 and 2 use it (`claude`, `claude mcp list`) | Windows PowerShell: `irm https://claude.ai/install.ps1 \| iex`. macOS/Linux: `curl -fsSL https://claude.ai/install.sh \| bash` | Same sign-in as the extension. |
| 4 | **Python 3.10 or newer** | Runs the Playwright tests (pytest) | https://www.python.org/downloads | **Windows: tick "Add python.exe to PATH"** on the first installer screen. |
| 5 | **Node.js LTS** (18 or newer) | Runs the Playwright MCP server that lets Claude control the browser | https://nodejs.org | Default installer options are fine. |
| 6 | **Google Chrome** | The browser the MCP server opens | https://www.google.com/chrome | Tests use their own bundled Chromium, installed in Setup below. |
| 7 | **Python extension for VS Code** (optional) | Syntax highlighting, and lets you run tests from the editor | Extensions, search "Python" (publisher: Microsoft) | |
| 8 | **Git** | Get the project with `git clone`, and keep each module on its own branch | https://git-scm.com | |

**Network:** you need access to `pypi.org`, `registry.npmjs.org`, the Playwright browser download servers and `saucedemo.com`. If you're on a corporate VPN or proxy and installs hang, try off-VPN or ask IT.

**No other credentials needed.** The Playwright MCP server runs locally with no API key, and the practice site's logins are public (they're shown on its login page).

#### Check your installs
Close and reopen your terminal after installing, then run:
```powershell
code --version      # VS Code
python --version    # 3.10 or newer (macOS/Linux: python3 --version)
node --version      # v18 or newer
npx --version       # comes with Node
claude --version    # Claude Code CLI
git --version
```
If a command says "not recognized" or "not found", that tool isn't installed or isn't on your PATH. Reinstall it (for Python, with "Add to PATH" ticked) and reopen the terminal.

### Install the project
> Building from scratch (option 2 above)? Skip this section. Claude sets the project up with you in stage 1.

Clone the repo (`git clone https://github.com/JoeChav11/claude-playwright-builder.git`), open the `claude-playwright-builder` folder in VS Code (**File > Open Folder**), then open a terminal (**Terminal > New Terminal**) and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt -c constraints.txt   # constraints.txt pins the tested versions
playwright install chromium
pytest -n auto                        # 23 tests should pass
```

Then open the Claude Code panel in VS Code (with this folder open, so it loads `CLAUDE.md` and `.mcp.json`) and run `/mcp`. You should see `playwright` connected.

#### Windows vs macOS/Linux
The course is written for Windows PowerShell. On macOS/Linux, change these:

| | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| Python command | `python` | `python3` (outside the venv) |
| Activate the venv | `.\.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |
| `.mcp.json` | `"command": "cmd", "args": ["/c", "npx", "-y", "@playwright/mcp@0.0.83"]` (as shipped) | `"command": "npx", "args": ["-y", "@playwright/mcp@0.0.83"]` |
| Install the CLI | `irm https://claude.ai/install.ps1 \| iex` | `curl -fsSL https://claude.ai/install.sh \| bash` |
| Paths in commands | `test-results\<folder>\trace.zip` | `test-results/<folder>/trace.zip` |
| Delete a file | `Remove-Item <file>` | `rm <file>` |

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
- [docs/curriculum.md](docs/curriculum.md): course overview, install checklist, and how to draft a CLAUDE.md from scratch
- [docs/playwright-basics.md](docs/playwright-basics.md): page, locators, auto-waiting, expect
- [docs/review-checklist.md](docs/review-checklist.md): what to check in any generated test
- [docs/pom-vs-components.md](docs/pom-vs-components.md): page objects vs. component helpers
