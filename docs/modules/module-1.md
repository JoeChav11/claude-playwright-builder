# Module 1: Claude Code Fundamentals

**Goal:** operate Claude Code safely and control its context.

Before Claude writes any tests, you need to know how to start it, how much it is allowed to do without asking, what it can "see" at any moment, and how to check its changes before they land. Everything in Modules 2 and 3 builds on these habits.

## Topics
| Topic | What to know |
|---|---|
| Running Claude | Terminal (`claude` in the VS Code integrated terminal) and the VS Code extension (Claude Code panel) |
| Permission modes | default, accept edits, plan mode |
| Context management | `/clear`, `/compact`, `/context`, referencing files with `@` |
| Slash commands | built-in commands, `/init`, how `CLAUDE.md` is loaded |
| Reviewing diffs | read every change before accepting it |

---

## Exercise 1: Two ways to run Claude (10 min)
1. Open this repo in VS Code. Open the integrated terminal (**Ctrl+`**), activate the venv, and run:
   ```powershell
   claude
   ```
   Ask: `What does this repo test, and how do I run the smoke tests?` Exit with `/exit` (or Ctrl+C twice).
2. Open the **Claude Code panel** from the extension (Spark icon in the editor toolbar or the Activity Bar). Ask the same question.

Notice: both read the same `CLAUDE.md` and give the same run command. The extension adds editor integration: it sees your open file and selection, and shows proposed edits as diffs in the editor.

## Exercise 2: Permission modes (15 min)
Claude asks before it acts. The mode decides how often.

| Mode | Edits files | Runs commands | Use it for |
|---|---|---|---|
| **Default** | asks each time | asks each time | learning, unfamiliar repos |
| **Accept edits** | without asking | asks each time | a task you have already planned and trust |
| **Plan** | no (read-only) | read-only only | multi-file changes; Claude proposes, you approve |

Switch modes with **Shift+Tab** (terminal and panel), or the mode selector under the panel's prompt box.

Setup: create a throwaway file `scratch/greet.py` (the `scratch/` folder is for this module only; delete it when you finish):
```python
def greet(name):
    return f"Hello, {name}!"
```

1. In **default** mode, ask: `Add a docstring to scratch/greet.py explaining what the function does.` Look at the permission prompt. Reject it.
2. Switch to **plan** mode and ask the same thing. Note that Claude only describes the change.
3. Switch to **accept edits** and ask again. The edit lands without a prompt. Ask Claude to revert it.

Discuss: which mode would you use on a client repo on day one? Which is safe for a 10-file refactor? (Module 3 uses plan mode for exactly this.)

## Exercise 3: Control the context (15 min)
Claude only knows what is in its context window: the conversation, `CLAUDE.md`, and files it has read. Context is limited, and a long session gets slower and less accurate.

1. Run `/context`. Note how much is already used before you have typed anything (system prompt, tools, `CLAUDE.md`).
2. Reference files directly with `@`:
   ```
   Explain the difference between @pages/components/header.py and @pages/components/product_card.py
   ```
   In the extension, select lines in the editor and press **Alt+K** to insert an `@` reference to that selection.
3. Run `/context` again. What grew?
4. Run `/compact`. Claude summarizes the conversation and keeps going with less context. You can steer it: `/compact keep only the decisions about components`.
5. Run `/clear`. The conversation is gone; `CLAUDE.md` is loaded fresh. Ask `What did we just discuss?` to confirm.

Rule of thumb: `/clear` when you switch tasks, `/compact` when one task runs long.

## Exercise 4: Slash commands and how CLAUDE.md is loaded (10 min)
1. Type `/` to list commands. Find `/help`, `/init`, `/memory`, `/context` and `/agents`. Run `/agents`: this repo ships two subagents, `test-writer` and `test-reviewer`, which you use from Module 2 onwards.
2. Run `/memory` to see which memory files are loaded.

How `CLAUDE.md` is loaded:
- **At session start:** your user file (`~/.claude/CLAUDE.md`), the project's `CLAUDE.md`, and any `CLAUDE.md` in parent folders.
- **On demand:** a `CLAUDE.md` in a subfolder loads when Claude reads files in that folder.
- **Not mid-session:** edits to `CLAUDE.md` apply reliably only after `/clear` or a new session. (Module 3, Exercise 3 relies on this.)

## Exercise 5: Review diffs before accepting (10 min)
Setup: create a throwaway test file `scratch/test_scratch.py` with a badly named test:
```python
from scratch.greet import greet


def test_1():
    assert greet("Ada") == "Hello, Ada!"
```
Ask Claude, in default mode:
```
In scratch/test_scratch.py, rename the test to describe its behavior.
```
Before accepting, check the diff:
- [ ] Is only the requested change there? (No unrelated reformatting or "while I was here" edits.)
- [ ] Does it follow `CLAUDE.md` naming (`test_<who/what>_<does>_<outcome>`)?
- [ ] Would anything else break (other references to the name)?

Reject it once with feedback ("use a shorter name"), then accept the revised version. Run the file: `pytest scratch/test_scratch.py -v`. When you are done with the module, delete the `scratch/` folder.

## Exercise 6: Scaffold an empty repo and run /init (15 min)
Outside this repo:
```powershell
mkdir $HOME\claude-init-demo
cd $HOME\claude-init-demo
git init
claude
```
1. Run `/init`. Claude scans the folder and writes a `CLAUDE.md`.
2. Open the generated `CLAUDE.md` and explain, in your own words:
   - What sections it created and why
   - What it could and could not infer from an empty repo
   - When Claude will read this file
3. Add a little code (e.g. ask Claude for a `requirements.txt` with `pytest` and one passing test), `/clear`, and run `/init` again. What changed?
4. Compare the result with this repo's [CLAUDE.md](../../CLAUDE.md). Which rules here could `/init` never have guessed?

Takeaway: `/init` gives you a starting point from what is in the repo. The team's standards (banned patterns, locator priority, where code goes) still have to be written by people. That is Module 3.

---

## Checklist: ready for Module 2?
- [ ] You can start Claude in the terminal and in the extension
- [ ] You can switch permission modes and know when to use each
- [ ] You use `@` to point Claude at files instead of pasting code
- [ ] You know when to `/clear` and when to `/compact`
- [ ] You can explain when `CLAUDE.md` is loaded
- [ ] You never accept a diff you have not read
- [ ] Clean up: the `scratch/` folder is deleted
