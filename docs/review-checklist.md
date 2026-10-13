# Test Review Checklist

Use this on every generated test, whether it came from codegen or Claude.

## Locators
- [ ] Uses `get_by_role` with a `name` wherever the element has a role
- [ ] Falls back in order: label, placeholder/text, test-id, then CSS as a last resort. No XPath.
- [ ] No positional selectors (`nth-child`, `.first`, `.nth(0)`) unless position is the thing being tested
- [ ] No styling classes (`.btn_medium`) or deep DOM paths (`/div/div[2]/...`)
- [ ] Repeated elements are scoped (`card.filter(has_text=...).get_by_role(...)`)

## Waiting
- [ ] No `time.sleep()` or `page.wait_for_timeout()`
- [ ] No manual `is_visible()` polling loops

## Assertions
- [ ] Ends with `expect(...)` that proves the **user-visible** outcome
- [ ] Uses web-first assertions (`expect(...).to_be_visible()`), not `assert locator.is_visible()` (which checks once, with no retry)
- [ ] Asserts the right thing: e.g. order confirmation text, not just "a page loaded"
- [ ] Negative cases assert what should NOT happen too

## Structure
- [ ] One flow per test, descriptive name (`test_locked_out_user_sees_error`)
- [ ] Uses `page.goto("/")` with `base_url`, no hard-coded host
- [ ] Shared setup (login) lives in a fixture, not copy-pasted
- [ ] Passes when run alone and in any order

## Repo standards (Module 3)
- [ ] In `tests/smoke/` or `tests/regression/` with a matching `pytestmark`
- [ ] No locators in the test file; they live in `pages/` or `pages/components/`
- [ ] No literal usernames, product names, prices or customer details; uses `data/`
- [ ] Reuses existing page objects, components and fixtures instead of near-duplicates
- [ ] Page objects contain no assertions
- [ ] Similar cases use `parametrize` with readable ids, not copy-paste
- [ ] Safe to run in parallel (`pytest -n auto`)

## The "would it catch a bug?" check
Ask: if the feature broke, would this test fail? A test that clicks through checkout but never checks the result passes on a broken site.
