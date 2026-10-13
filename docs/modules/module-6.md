# Module 6: CI Integration, Guardrails, Capstone

**Goal:** run the suite in a pipeline and keep quality under control.

> **Stuck?** The `finished-example` branch has the finished workflow, deny rules and "Fixing failing tests" section. See only what this module adds with `git diff main origin/finished-example`. Build your own first, then compare.

Until now everything ran on your machine, with you watching. In CI nobody is watching: tests run on every pull request, and Claude can be called automatically when they fail. That's useful, and it's exactly where the guardrails matter most. This module puts the suite in GitHub Actions, adds a Claude triage step that proposes a fix as a pull request a human must approve, and sets the rules that stop Claude from "fixing" a test by making it weaker.

**You need for this module:** a GitHub account, Git, your copy of this repo pushed to a GitHub repository you own, and an Anthropic API key stored as a repository secret named `ANTHROPIC_API_KEY` (**Settings > Secrets and variables > Actions**).

## Topics
| Topic | What to know |
|---|---|
| GitHub Actions | Run pytest-playwright on every PR; upload traces, screenshots and the test report as artifacts |
| Claude in CI | On failure, run headless Claude (`claude -p`) to read the trace and propose a fix as a **draft PR**. A human approves or rejects it. |
| Guardrails | Deny rules for destructive commands and secret files; never weaken an assertion to make a test pass; fix flaky tests at the root cause, not with retries |
| Metrics | Flake rate, time to author a test, review rejection rate |

---

## Exercise 1: Run the suite in GitHub Actions (30 min)
Create `.github/workflows/playwright.yml`:
```yaml
name: playwright

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: playwright install --with-deps chromium
      - run: >
          pytest -n auto
          --tracing retain-on-failure
          --screenshot only-on-failure
          --junitxml=reports/junit.xml
      - name: Upload traces, screenshots and report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-results
          path: |
            test-results/
            reports/
          retention-days: 14
```
Push a branch and open a PR. Then:
1. Check the run passes and the `playwright-results` artifact contains `reports/junit.xml`.
2. Push a commit that breaks one test (change an expected value, as in Module 4, Exercise 4). Download the artifact and open the trace locally: `playwright show-trace test-results/<test-folder>/trace.zip`.
3. Revert the broken commit.

Questions:
- Why `if: always()` on the upload step? (Without it, the artifacts are skipped exactly when you need them: when tests fail.)
- Traces contain cookies and page content. Who can download artifacts from your repo? How long should they be kept?

## Exercise 2: Deny rules (15 min)
`allow` rules in [.claude/settings.json](../../.claude/settings.json) skip the permission prompt. `deny` rules block a tool call outright, in every mode, even if something else allows it. Add a `deny` list next to the existing `allow` list:
```json
"deny": [
  "Bash(rm -rf:*)",
  "PowerShell(Remove-Item -Recurse:*)",
  "Bash(git push --force:*)",
  "Bash(git reset --hard:*)",
  "Read(./.env)",
  "Read(./.env.*)",
  "Read(./**/*.pem)",
  "Edit(./.github/workflows/**)"
]
```
Start a new session and test it: ask Claude to read `.env` (create a dummy one first) and to edit the workflow file. Both should be refused without a prompt.

Discuss: why deny edits to the workflow? (A pipeline that Claude can rewrite is a pipeline Claude can switch off.) What else in this repo should Claude never touch?

## Exercise 3: Never weaken the assertion (20 min)
The most common bad "fix" is to change the test until it agrees with the bug. See it happen first:

1. Break the app's expected behavior in a copy of a test: in `tests/smoke/test_cart_broken.py`, change the expected badge text from `"1"` to `"2"`.
2. Ask Claude, with no other guidance: `tests/smoke/test_cart_broken.py is failing. Make it pass.`
3. Look at the diff. Did it change `"2"` back to `"1"` (correct here, because the test was wrong) or did it reason about **which side is wrong**? Now imagine the app had the bug. The same edit would hide it.

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
Start a new session and repeat step 2. What changed in Claude's answer? Run the test-reviewer agent on whatever it proposes. Delete the broken copy afterwards.

**Flaky tests get the same rule.** A test that fails 1 run in 10 has a cause: an assertion before the page settles, shared state between tests, or order-dependent data. Adding `pytest-rerunfailures` or a longer timeout hides the cause and makes the suite slower. When you review a flaky-test fix, the PR must name the cause, and `pytest <file> --count 10 -n auto` must pass 10/10 after it.

## Exercise 4: Claude triages failures in CI (30 min)
Add a second job to the workflow. It runs only when tests fail on a PR from this repo, asks headless Claude to find the cause and propose a fix, and opens a **draft** PR with the result. Claude never pushes or merges: the workflow does the git work, and a human decides.

```yaml
  triage:
    needs: test
    if: failure() && github.event_name == 'pull_request' && github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}
      - uses: actions/download-artifact@v4
        with:
          name: playwright-results
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt && playwright install --with-deps chromium
      - run: npm install -g @anthropic-ai/claude-code
      - name: Claude triage
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: >
          claude -p "Tests failed in CI. Read reports/junit.xml and the traces and
          screenshots in test-results/. For each failure decide: test bug, app bug,
          or flaky, with evidence. Follow the 'Fixing failing tests' rules in
          CLAUDE.md. Only for a test bug, edit the test or page object to fix it
          and run pytest on that file. Write your findings to triage.md."
          --strict-mcp-config
          --allowedTools "Read,Grep,Glob,Edit,Write,Bash(pytest:*)"
          --output-format json > triage.json
      - name: Open a draft PR with the proposed fix
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          if git diff --quiet; then exit 0; fi
          branch="claude/triage-${{ github.run_id }}"
          git config user.name "claude-triage"
          git config user.email "claude-triage@users.noreply.github.com"
          git switch -c "$branch"
          git add -A -- . ':!triage.json' ':!triage.md' ':!test-results' ':!reports'
          git commit -m "Proposed fix from CI triage"
          git push origin "$branch"
          gh pr create --draft --base "${{ github.head_ref }}" \
            --title "Proposed fix: CI triage for #${{ github.event.pull_request.number }}" \
            --body-file triage.md
```
Notes on the guardrails built into this job:
- `--allowedTools` gives Claude no `git` or `gh`. It can only read, edit and run pytest. The workflow, not Claude, creates the branch and PR.
- `--strict-mcp-config` with no `--mcp-config` starts Claude without MCP servers. CI has the trace, it doesn't need a live browser, and this repo's `.mcp.json` uses a Windows-only command.
- The PR is a **draft** against the failing branch. Protect `main` with a required review (**Settings > Branches**) so nothing merges without a human.
- The `if:` skips PRs from forks: they would run your API key against code you haven't reviewed.
- PRs opened with `GITHUB_TOKEN` don't trigger new workflow runs. Pull the branch and run the tests yourself, or re-run them from the PR.

Test it: push a branch with a broken test and open a PR. Review the draft PR Claude proposes **as you would any PR**: does `triage.md` name the cause with evidence? Did it weaken anything? Run the test-reviewer agent on the changed files.

## Exercise 5: Measure it (10 min)
Pick three numbers to track for the capstone and beyond:

| Metric | Definition | How to get it here |
|---|---|---|
| **Flake rate** | Runs that fail and then pass on unchanged code, divided by total runs | `pytest --count 10 -n auto` per new test; failures in CI that pass on re-run |
| **Time to author** | From first prompt to a test the reviewer ACCEPTs and that passes 10/10 | Note the start and end time for each test you write |
| **Review rejection rate** | REJECT or ACCEPT WITH CHANGES verdicts, divided by all reviews | Count the test-reviewer verdicts |

Discuss: which of these would you show a client? Which would go up if Claude got worse, and which would go up if your reviewer got stricter?

---

## Capstone
Pick an app (not saucedemo) and deliver all of the following in one repository.

| Deliverable | Done when |
|---|---|
| **A tested `CLAUDE.md`** | You ran the same prompt with and without it (Module 3, Exercise 3) and can show the difference |
| **10 or more tests** | Smoke and regression markers; every test passes `--count 10 -n auto` |
| **Two subagents** | In `.claude/agents/`, each with one job and a deliberately limited `tools` list (e.g. a writer and a reviewer, or a reviewer and a failure-triager). The reviewer is calibrated against known good and bad examples (Module 5, Exercise 2). |
| **Deny rules** | In `.claude/settings.json`, blocking destructive commands, secret files and edits to the CI workflow, and tested in a new session (Exercise 2) |
| **A CI workflow with a failure-triage step** | Runs on every PR, uploads artifacts, and triages failures into a draft PR a human must approve |
| **A short writeup** | One page: where Claude's output needed correction, what you changed (prompt, CLAUDE.md, agent, guardrail) so it didn't happen again, and your three metrics |

Use a demo or staging environment you are allowed to test, never production (Module 4, Exercise 5).

---

## Checklist: CI and guardrails
- [ ] Tests run on every PR, and traces and reports are uploaded even when tests fail
- [ ] Deny rules block destructive commands, secret files, and edits to the workflow
- [ ] `CLAUDE.md` forbids weakening assertions, skipping tests, retries and longer timeouts as fixes
- [ ] CI triage proposes a draft PR; Claude has no git or GitHub permissions; a human merges
- [ ] Flaky-test fixes name the root cause and pass 10/10
- [ ] You track flake rate, time to author and review rejection rate
