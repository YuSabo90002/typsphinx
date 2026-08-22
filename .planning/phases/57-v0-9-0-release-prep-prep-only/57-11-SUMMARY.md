---
phase: 57-v0-9-0-release-prep-prep-only
plan: 11
subsystem: builder
tags: [python, sphinx, typst, windows-compat, repr-escaping, release-prep]

# Dependency graph
requires:
  - phase: 57-v0-9-0-release-prep-prep-only (plans 57-05, 57-10)
    provides: "the two CI matrix dispatches (31956166848, 31959060298) that proved the
      Windows-only defect, and 57-10's separator-portable test assertion that this plan's
      fix makes actually pass on Windows"
provides:
  - "Non-escaping path quoting at typsphinx/builder.py's three pre-write template-path
    refusal sites (srcdir-ancestor, templates_path collision, bundle-destination collision)"
  - "A locally-runnable Windows-shape regression guard (TestWindowsPathEscapingRegressionGuard)"
  - "An AMENDED decision block in 57-CONTEXT.md scoping the owner-approved prep-only fence
    exception for 57-08 and the phase verifier to read"
  - "A CHANGELOG.md ### Fixed bullet for the Windows message change"
  - "WINDOWS.md entries 9 and 10 transitioned (not closed) to record the real fix landing"
  - "A deferred todo cataloguing the remaining path-valued !r sites left unchanged"
affects: [57-08, phase-verifier, release-v0.9.0]

# Actuals (#2632)
actuals:
  tokens: 11925
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Message-construction helper functions (_conf17_violation_message,
      _templates_path_collision_message, _bundle_destination_collision_message) as the
      one place a refusal sentence is built, both for cross-call-site consistency and to
      make the message directly unit-testable without duplicating its f-string"
    - "Explicit '{value}' quoting instead of {value!r} for path-valued interpolations in
      user-facing refusal messages, reserving !r for identifier-valued interpolations
      (registry keys, docnames, config tuples) that cannot contain a path separator"

key-files:
  created:
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-MESSAGE-FIX-EVIDENCE.md
    - .planning/todos/pending/2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md
  modified:
    - typsphinx/builder.py
    - tests/test_templates_path_collision_gate.py
    - CHANGELOG.md
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-CONTEXT.md
    - .planning/WINDOWS.md

key-decisions:
  - "Fixed the product message rather than normalizing the test's expectation (owner
    decision, 2026-08-17), knowingly breaking Phase 57's prep-only fence as the one
    intended exception"
  - "Extracted the two remaining inline refusal f-strings into named module-level functions
    (mirroring the pre-existing _conf17_violation_message) so task 2's regression guard
    could call real product code directly instead of duplicating a format string"
  - "Left every path-valued !r site outside the three named refusal sites untouched and
    filed them as a single deferred todo, rather than widening the fix during release prep"

requirements-completed: [REL-08]

coverage:
  - id: D1
    description: "The three pre-write template-path refusal messages in typsphinx/builder.py
      quote path values without repr() escaping, so a Windows backslash is not doubled"
    requirement: "REL-08"
    verification:
      - kind: unit
        ref: "tests/test_templates_path_collision_gate.py::TestWindowsPathEscapingRegressionGuard::test_conf17_violation_message_does_not_double_backslashes"
        status: pass
      - kind: unit
        ref: "tests/test_templates_path_collision_gate.py::TestWindowsPathEscapingRegressionGuard::test_templates_path_collision_message_does_not_double_backslashes"
        status: pass
      - kind: unit
        ref: "tests/test_templates_path_collision_gate.py::TestWindowsPathEscapingRegressionGuard::test_bundle_destination_collision_message_does_not_double_backslashes"
        status: pass
      - kind: integration
        ref: "uv run python -m pytest -q (1421 passed, 5 skipped, zero test file edits in task 1's commit)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The Windows-only regression is now locally detectable (no CI dispatch
      needed) via a real revert-and-restore RED/GREEN demonstration"
    verification:
      - kind: unit
        ref: "manual revert of _conf17_violation_message to !r -> RED, restore -> GREEN
          (transcript in 57-MESSAGE-FIX-EVIDENCE.md section 6)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The AMENDED fence-exception block, CHANGELOG bullet, WINDOWS.md
      transition, and deferred todo are all recorded per task 3"
    requirement: "REL-08"
    verification:
      - kind: other
        ref: "grep -q AMENDED 57-CONTEXT.md && grep -q 57-11 WINDOWS.md && test -f todo &&
          test -f 57-MESSAGE-FIX-EVIDENCE.md && pytest tests/test_changelog_page_gate.py -q"
        status: pass
    human_judgment: true
    rationale: "Whether the AMENDED block's wording actually satisfies 57-08 and the
      phase verifier as intended readers is a judgment call about future-plan legibility,
      not something a unit test can confirm."

# Metrics
duration: 55min
completed: 2026-08-22
status: complete
---

# Phase 57 Plan 11: Fix the repr-escaped path in the refusal message Summary

**Unescaped path quoting at three `typsphinx/builder.py` refusal sites closes the Windows-only backslash-doubling defect that burned two full CI matrix dispatches, with the fence-break recorded as an owner-approved exception.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-08-22T06:21:00Z (approx.)
- **Completed:** 2026-08-22T06:27:02Z
- **Tasks:** 3
- **Files modified:** 7 (2 created, 5 modified)

## Accomplishments

- Fixed the actual root cause — `repr()` escaping filesystem-path values — at the three named
  pre-write template-path refusal sites in `typsphinx/builder.py`, replacing `{value!r}` with
  explicit non-escaping `'{value}'` quoting for path values only; every identifier-valued `!r`
  (registry keys) is untouched.
- Extracted the two previously-inline refusal messages into their own named functions
  (`_templates_path_collision_message`, `_bundle_destination_collision_message`), matching the
  existing `_conf17_violation_message` pattern, so a unit test can call the real product code
  directly instead of duplicating its f-string.
- Added `TestWindowsPathEscapingRegressionGuard` (4 tests) that drives all three real
  message-construction functions with a hand-built Windows-shaped path and asserts no doubled
  backslash survives — demonstrated to actually catch a regression via a manual revert/restore
  RED/GREEN transcript.
- Confirmed the full local suite passes with **zero test file edits** in task 1's own commit
  (1417 passed, 5 skipped), proving POSIX output is byte-identical before and after the fix, and
  confirmed plan 57-10's already-merged `str(Path("_templates") / "nested")` assertion now
  matches what the fixed message produces on Windows (was not reverted or re-edited).
- Recorded the fence exception: an AMENDED block in `57-CONTEXT.md` naming SC#4, both failing CI
  runs, the owner's decision, and the two downstream readers (`57-08`, the phase verifier) who
  must evaluate the fence against the amendment; a `CHANGELOG.md` `### Fixed` bullet in user
  terms (the `**Breaking` count stays exactly four); `WINDOWS.md` entries 9 and 10 transitioned
  but left open pending a Windows-lane CI confirmation this plan did not observe; and a deferred
  todo cataloguing every other path-valued `!r` site the census found outside the three fixed
  sites.

## Task Commits

Each task was committed atomically:

1. **Task 1: Census every `!r`, classify it, and unescape the path values in the pre-write refusal family** - `699d4c0e` (fix)
2. **Task 2: Make the Windows-only escaping regression detectable on this POSIX host** - `6cfdde70` (test)
3. **Task 3: Record the fence exception, the CHANGELOG entry, the ledger transition, and the deferred class** - `965395cf` (docs)

**Plan metadata:** committed as part of this worktree's task 3 commit above (worktree mode — orchestrator merges and records final STATE.md/ROADMAP.md updates centrally).

## Files Created/Modified

- `typsphinx/builder.py` - Unescaped path quoting at the three refusal sites; extracted two message-builder functions
- `tests/test_templates_path_collision_gate.py` - Added `TestWindowsPathEscapingRegressionGuard` (4 tests)
- `CHANGELOG.md` - `### Fixed` bullet under `## [0.9.0]` for the Windows message change
- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-CONTEXT.md` - AMENDED 2026-08-17 fence-exception block
- `.planning/WINDOWS.md` - Entries 9 and 10 annotated with an UPDATE note, both left `open`
- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-MESSAGE-FIX-EVIDENCE.md` - Created: census, before/after reproduction, RED/GREEN transcript
- `.planning/todos/pending/2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md` - Created: deferred path-valued `!r` sites

## Decisions Made

- Fixed the product message rather than normalizing the test's expectation, per explicit owner
  decision taken 2026-08-17 with the fence-break cost stated up front.
- Extracted `_templates_path_collision_message()` and `_bundle_destination_collision_message()`
  as pure refactors (byte-identical output, confirmed by the full suite passing unchanged) so
  task 2's regression guard could exercise real product code rather than a re-pasted format
  string — this is a different, and I believe better, design than what a prior interrupted
  attempt at this same plan left behind (two unwired helper functions); these are fully wired at
  their original call sites.
- Scoped the fix to exactly the three named refusal sites in `typsphinx/builder.py`; every other
  path-valued `!r` site the census found (the v0.8.0-era output-path collision family, bundle-copy
  I/O failure messages, several warning/debug logs, and `template_registry.py`'s declared-template
  validation) is filed as a single deferred todo rather than fixed here.

## Deviations from Plan

None — plan executed exactly as written. Task 2's extraction of the two message-builder helper
functions is within the plan's own latitude ("keep it small and honest... unless the existing
module's structure makes [inventing a new module] unnatural" and "you are free to reach a
different and better design" per the prior-attempt note in this plan's dispatch), not a deviation
from a specified design.

## Issues Encountered

- The freshly-provisioned worktree `.venv/bin/ruff` is a generic-linux ELF the NixOS sandbox
  cannot execute (a known, previously-documented environmental hazard unrelated to this plan's
  change). Worked around with `nix-shell -p ruff --run "ruff check ."` (ruff 0.15.14 from
  nixpkgs), which produced a clean result identical in kind to `uv run ruff`. `black` and `mypy`
  ran fine directly through `uv run`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The Windows-only escaping defect that blocked `57-05`'s post-bump authority CI dispatch on
  both `windows-latest` lanes across two separate runs is fixed and locally proven, but **not yet
  confirmed on an actual Windows CI lane** — that confirmation is `57-08`'s (or a re-dispatched
  `57-05`'s) job, reading `WINDOWS.md` entries 9 and 10 (still `open`) and `57-CONTEXT.md`'s new
  AMENDED block (which scopes the fence exception this plan takes).
- `57-08`'s SC#4 sweep must allow exactly this plan's `typsphinx/builder.py` diff as the one
  intended exception and flag anything else under `typsphinx/` as before — the AMENDED block
  names `57-08` explicitly for this reason.
- No irreversible action was taken: `git tag -l v0.9.0` and `git ls-remote --tags origin v0.9.0`
  both remain empty.

---
*Phase: 57-v0-9-0-release-prep-prep-only*
*Completed: 2026-08-22*
