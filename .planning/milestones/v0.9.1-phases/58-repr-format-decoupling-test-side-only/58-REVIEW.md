---
phase: 58-repr-format-decoupling-test-side-only
reviewed: 2026-08-28T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - tests/_path_naming.py
  - tests/test_builder.py
  - tests/test_out02_escape_target_gate.py
  - tests/test_path_naming_predicate.py
  - tests/test_repr_census_guard.py
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: clean
---

# Phase 58: Code Review Report

**Reviewed:** 2026-08-28T00:00:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** clean

## Summary

Reviewed the test-side-only `repr()`/`!r` decoupling: the new leaf predicate module
`tests/_path_naming.py`, its durable meta-test suite `tests/test_path_naming_predicate.py`,
the AST-backed census guard `tests/test_repr_census_guard.py`, and the two rewritten
consumer sites in `tests/test_builder.py` and `tests/test_out02_escape_target_gate.py`.

Verification performed beyond static reading:
- Confirmed `git diff --name-only 3b0f2b93..HEAD -- typsphinx/` is empty — nothing under
  `typsphinx/` changed, matching the phase's test-side-only claim.
- Confirmed `tests/_path_naming.py` has zero `typsphinx` imports (grep) and is not
  duplicated inline elsewhere in `tests/` (grep for `def path_named_in`) or re-exposed via
  `tests/conftest.py` (D-04 satisfied on both counts).
- Traced `path_named_in`'s two-disjunct logic by hand against all seven scenarios exercised
  in `test_path_naming_predicate.py`, including the D-03 same-basename-sibling trap
  (`test_d03_fallback_trap_is_not_a_false_positive`) — the predicate takes the full value,
  never a basename, and correctly returns `False` when only a same-basename `fallback`
  field survives.
- Ran the full new suite (`pytest tests/test_repr_census_guard.py
  tests/test_path_naming_predicate.py -q`) — 16/16 pass.
- Falsified the census guard live: temporarily appended an `assert repr(x) in 'a'` to
  `tests/test_translator.py` and reran `test_repr_census_guard.py` — the allowlist-equality
  test correctly turned RED, naming the new site
  (`('test_translator.py', 3927)`) as "found but not allowlisted." Reverted via `git
  checkout` and confirmed `git status --short tests/` is clean afterward.
- Falsified the `.msg`-vs-`.test` exclusion live: appended
  `assert x == 'a', f'value was {x!r}'` (repr only in the failure message, not the test
  expression) — the guard correctly stayed GREEN, confirming diagnostic-only `!r`/`repr()`
  occurrences in `.msg` are excluded as designed. Reverted cleanly.
- Diffed `tests/test_builder.py` and `tests/test_out02_escape_target_gate.py` against their
  pre-phase versions: in both files only the pass criterion changed (the `repr(value) in
  message` assertion became `path_named_in(value, message)`); no pre-existing assertion was
  deleted or loosened. `test_out02_escape_target_gate.py`'s rewrite actually added a new,
  stricter check (de-duplicated single-distinct-warning-line assertion) alongside the
  format-agnostic predicate — a strengthening, not a weakening.
- Ran `black --check` on all five files — clean.
- Ran the affected consumer tests directly (`test_builder.py -k rehome_escape`,
  `test_out02_escape_target_gate.py`) — all pass.

No Critical or Warning findings. One Info-level documentation nit noted below.

## Info

### IN-01: Stale file-count comment in the non-vacuity floor's rationale

**File:** `tests/test_repr_census_guard.py:65-70`
**Issue:** The comment backing `MINIMUM_FILES_SWEPT = 100` states "324 `.py` files exist
under tests/ excluding `__pycache__`". A live count (`find tests -name "*.py" -not -path
"*/__pycache__/*" | wc -l`) now returns 327 — consistent with this phase adding three new
files (`_path_naming.py`, `test_path_naming_predicate.py`, `test_repr_census_guard.py`)
after the "324" figure was measured at plan time, but the comment itself was never updated
to reflect the phase's own file additions. This has no functional effect — `100` is
explicitly a floor with "wide headroom," not an exact assertion — but a future reader may
treat the "324" figure as a currently-accurate measurement rather than a stale planning-time
snapshot.
**Fix:** Either drop the specific count from the comment (keep only the qualitative
"wide headroom" rationale) or update it to the current count so it doesn't silently drift
again on the next file addition.

---

_Reviewed: 2026-08-28T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
