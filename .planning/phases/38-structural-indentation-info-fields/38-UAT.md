---
status: testing
phase: 38-structural-indentation-info-fields
source: [38-VERIFICATION.md]
started: 2026-08-01T15:10:10Z
updated: 2026-08-01T15:10:10Z
---

## Current Test

number: 1
name: Decide whether SC#4 / IND-04's "drives ... block quotes" prose is stale documentation or an unmet criterion
expected: |
  A human decision on whether the ROADMAP/REQUIREMENTS prose should be corrected to match D-04's
  narrower, deliberately-scoped reading (SHARED_INDENT_STEP drives desc_content and field_list
  only; block_quote is an intentional non-consumer using Typst's own quote() default spacing),
  or whether the prose's literal claim that the constant "drives ... block quotes" was meant to
  hold and the implementation is out of compliance with the roadmap's own wording.
awaiting: user response

## Tests

### 1. Decide whether SC#4 / IND-04's "drives ... block quotes" prose is stale documentation or an unmet criterion

Read side by side:

- `ROADMAP.md` Phase 38 Success Criterion #4 — "One named indent constant drives desc nesting,
  field lists, and block quotes — a repo-wide grep over `typsphinx/` finds no second independent
  indent literal at those sites"
- `REQUIREMENTS.md` IND-04 — "One shared indent constant drives every indent context — desc
  nesting, field lists, and block quotes — rather than independent magic numbers per node type"
- `38-CONTEXT.md` D-04 — the locked decision that deliberately excludes `block_quote`
- The shipped code — `visit_block_quote` / `depart_block_quote` in `typsphinx/translator.py`, and
  the regression test `test_ind04_d04_block_quote_not_converted` that enforces the exclusion

expected: A human decision on whether the ROADMAP/REQUIREMENTS prose should be corrected to match
D-04's narrower, deliberately-scoped reading (`SHARED_INDENT_STEP` drives `desc_content` and
`field_list` only; `block_quote` is an intentional non-consumer using Typst's own `quote()` default
spacing), or whether the prose's literal claim that the constant "drives ... block quotes" was meant
to hold and the implementation is out of compliance with the roadmap's own wording.

why_human: This is a values/scope judgment already made once by the project owner during
context-gathering — D-04 records it as deliberate and says "so verify-time does not re-open it" —
but the ROADMAP.md and REQUIREMENTS.md prose was never edited to reflect the narrower scope, the way
FLD-02's REQUIREMENTS.md parenthetical was corrected in this same phase. A grep-only check cannot
decide whether "drives ... block quotes" is now stale documentation or an unmet criterion; that is a
call about what the roadmap author intended, not something derivable from the codebase alone. The
mechanical, grep-checkable half of SC#4/IND-04 ("no second independent indent literal") IS satisfied.

result: [pending]

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
