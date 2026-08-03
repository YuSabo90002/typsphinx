---
created: 2026-08-01T00:00:00+09:00
title: "`EXPECTED_PAGE_COUNT_PRE_PHASE` in `test_signature_page_boundary_render_gate.py` now holds a post-phase value"
area: tests
resolves_phase: 38
source: .planning/phases/37-signature-typography-the-desc-family/37-08-PLAN.md Task 2 (§5.2 of 37-GATE-EVIDENCE.md)
files:
  - tests/test_signature_page_boundary_render_gate.py (the `EXPECTED_PAGE_COUNT_PRE_PHASE` constant and its consumer, `test_page_count_does_not_inflate`)
---

## Problem

Plan `37-09` (Phase 37's Wave 5 gap-closure plan) re-pinned this constant from `6` to `7` after
discovering, investigating, and confirming a legitimate consequence of restoring correct
`desc_signature` vertical spacing on this fixture's deliberately tight page geometry (full reasoning
in `37-GATE-EVIDENCE-09.md` §3.3 and `37-GATE-EVIDENCE.md` §5.2).

The re-pin itself is correct and fully justified — but the constant's own name,
`EXPECTED_PAGE_COUNT_PRE_PHASE`, now describes the wrong thing: it no longer holds a *pre*-phase
value, it holds the value measured **after** Phase 37's `37-09` fix landed. The comment directly
above the constant records the full history (why 6 was originally measured pre-phase, why it moved
to 7 post-`37-09`), so the *value* is not undocumented — only the *identifier* no longer matches its
own contents.

## Solution

Rename the constant to something that describes what it actually holds post-`37-09` (e.g.
`EXPECTED_PAGE_COUNT` or `EXPECTED_PAGE_COUNT_POST_PHASE_37`), update its sole consumer
(`test_page_count_does_not_inflate`), and confirm
`uv run pytest tests/test_signature_page_boundary_render_gate.py -v` stays green. Low priority — pure
naming hygiene, no behavior change; the existing comment already prevents actual confusion about the
value's provenance.

## Resolved

Filed to `completed/` by Phase 41 (`.planning/phases/41-v0-7-0-release-automation-release-prep/`,
2026-08-03). Phase 41 files this record; the fix itself landed in an earlier phase (Phase 38, per
`resolves_phase: 38` above), not in Phase 41.

Re-verified in this worktree by grep against `tests/test_signature_page_boundary_render_gate.py`:

```
147:EXPECTED_PAGE_COUNT_CEILING = 7
```

The constant is named `EXPECTED_PAGE_COUNT_CEILING` (not the todo's suggested
`EXPECTED_PAGE_COUNT`/`EXPECTED_PAGE_COUNT_POST_PHASE_37`, but the same rename intent: a name that
no longer claims to be a pre-phase value), and its value is `7` — matching the post-`37-09`
re-pin this todo describes. `grep -rn "EXPECTED_PAGE_COUNT_PRE_PHASE" tests/` under this worktree
returns only two comment-line mentions (lines 112 and 305) that narrate the historical rename;
the old name does not appear as a live Python identifier anywhere under `tests/`. The fix is in
place; no code change was made by Phase 41 for this item.
