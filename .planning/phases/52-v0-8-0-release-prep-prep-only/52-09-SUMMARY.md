---
phase: 52-v0-8-0-release-prep-prep-only
plan: 09
subsystem: testing
tags: [pytest, ci, windows, python3.13, ntpath]

# Dependency graph
requires:
  - phase: 52-08
    provides: three CI defects fixed (locale, repr-escaping, ruff I001), taking CI from 8 failures to 1
provides:
  - Drive-qualified rehome-escape test fixture, genuinely absolute on Windows under CPython 3.13
  - Filed todo naming the outstanding product-side _track_image() isabs inconsistency
  - Third, all-green ci.yml authority run (12/12 jobs success) discharging Phase 52 SC#3's toolchain half
  - Broken Windows ledger closed to open_count: 0
affects: [complete-milestone, ship]

# Actuals (#2632)
actuals:
  tokens: 9216
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Drive-qualify Windows path fixtures with os.name == \"nt\" rather than os.sep alone, since CPython 3.13 narrowed ntpath.isabs() to require a drive letter or UNC prefix"

key-files:
  created:
    - .planning/todos/pending/2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md
  modified:
    - tests/test_builder.py
    - .planning/phases/52-v0-8-0-release-prep-prep-only/52-CI-EVIDENCE.md
    - .planning/WINDOWS.md

key-decisions:
  - "Fixed the CI-blocking defect test-side only (drive-qualify the fixture), left typsphinx/builder.py untouched, and filed the real product-side isabs inconsistency as a todo -- per the owner's explicit decision recorded in this plan's <context>, preserving Phase 52's zero-product-lines prep-only fence"
  - "The sibling test test_post_process_images_rehome_cross_drive_value_error_relocates was NOT changed -- it builds its fixture from builder.doctreedir (a real pytest tmp path, genuinely drive-qualified on Windows already), so it does not share the same latent defect; verified rather than assumed"

requirements-completed: []  # REL-07 deliberately stays open until /gsd-complete-milestone (STATE.md, ROADMAP.md D-08)

coverage:
  - id: D1
    description: "test_post_process_images_rehome_escape_relocates_with_warning's fixture is genuinely absolute on Windows under CPython 3.13 (drive-qualified), unchanged on POSIX"
    verification:
      - kind: unit
        ref: "tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning"
        status: pass
      - kind: e2e
        ref: "gh run view 31858016832 -- Test Python 3.13 on windows-latest job, success"
        status: pass
    human_judgment: false
  - id: D2
    description: "Outstanding product-side inconsistency in TypstBuilder._track_image() (bare path.isabs() vs. the platform-independent posixpath.isabs()+_is_drive_qualified() idiom its sibling _escapes_outdir() already uses) filed as a todo, not fixed"
    verification:
      - kind: other
        ref: "test -f .planning/todos/pending/2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "Third ci.yml authority run: all 12/12 jobs success, Test Python 3.13 on windows-latest named explicitly, discharging Phase 52 SC#3's toolchain half"
    verification:
      - kind: e2e
        ref: "gh run view 31858016832 --json jobs --jq '[.jobs[].conclusion]|unique' == [\"success\"]"
        status: pass
    human_judgment: false
  - id: D4
    description: "Broken Windows ledger entries 3, 4, 5, 6 all marked fixed; open_count: 0"
    verification:
      - kind: other
        ref: ".planning/WINDOWS.md frontmatter open_count: 0, fixed_count: 6"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-08-15
status: complete
---

# Phase 52 Plan 09: Close the Last CI Defect Test-Side, File the Product Inconsistency, Prove Green Summary

**Drive-qualified a Windows-only test fixture to close CPython 3.13's `ntpath.isabs()` regression, filed the exposed `_track_image()` product-side inconsistency as a todo, and drove a third `ci.yml` dispatch to 12/12 green — discharging Phase 52 SC#3's toolchain half and zeroing the Broken Windows ledger.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-15T01:56:00Z
- **Completed:** 2026-08-15T02:12:10Z
- **Tasks:** 3
- **Files modified:** 4 (1 created, 3 modified)

## Accomplishments

- Closed the last CI-blocking defect from plans 52-04/52-08: CPython 3.13 narrowed `ntpath.isabs()` so a driveless leading-separator path is no longer absolute on Windows, which made `TypstBuilder._track_image()`'s rehome branch silently no-op for `test_post_process_images_rehome_escape_relocates_with_warning`'s fixture. Fixed the fixture (drive-qualified on Windows, unchanged on POSIX) rather than the product code, honoring Phase 52's zero-product-lines prep-only fence.
- Filed the real, still-open product-side inconsistency (`typsphinx/builder.py:910`'s bare `path.isabs()` vs. its own sibling `_escapes_outdir()`'s platform-independent `posixpath.isabs()` + `_is_drive_qualified()` idiom) as a named todo, so the finding survives independently of the test fix going green.
- Pushed the milestone branch (fast-forward `21eb4398..6924a0be`) and dispatched a third `ci.yml` run (`31858016832`): all 12 of 12 jobs report `success`, including `Test Python 3.13 on windows-latest` — the lane that carried this defect. `[.jobs[].conclusion]|unique` is `["success"]`.
- Appended the third run's evidence to `52-CI-EVIDENCE.md` as a pure append (186 insertions, 0 deletions) — both prior sections (red 8-failure run, 11/12 run) verified byte-unchanged before and after (`grep -c` on both prior run IDs stayed at 6 and 8 respectively).
- Closed Broken Windows ledger entries 3, 4, 5 (confirmed fixed by the second run's own evidence) and 6 (this plan's finding, confirmed fixed by the third run) — `open_count: 0`.

## Task Commits

1. **Task 1: Repair the fixture so it is genuinely absolute on the running platform** - `e78d5a64` (fix)
2. **Task 2: File the product-side inconsistency as a todo** - `6924a0be` (docs)
3. **Task 3: Third CI dispatch, evidence, and ledger close** - `5ee9433a` (docs)

**Plan metadata:** SUMMARY.md commit (this file) — see below.

## Files Created/Modified

- `tests/test_builder.py` - `test_post_process_images_rehome_escape_relocates_with_warning`'s `abs_uri` fixture now drive-qualified on Windows (`os.name == "nt"`), unchanged on POSIX
- `.planning/todos/pending/2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md` - new todo naming the outstanding `_track_image()` isabs drive-awareness inconsistency, `resolves_phase: null`
- `.planning/phases/52-v0-8-0-release-prep-prep-only/52-CI-EVIDENCE.md` - third run section appended (push, dispatch, all 12 job conclusions, no-irreversible-action re-confirmation, ledger closure note)
- `.planning/WINDOWS.md` - ledger entries 3, 4, 5, 6 marked `fixed`; frontmatter `open_count: 0`, `fixed_count: 6`

## Decisions Made

- Fixed the CI-blocking defect test-side only, per the owner's explicit decision recorded in `52-09-PLAN.md`'s `<context>`: fix the test, file the product issue, keep Phase 52's zero-product-lines fence intact for the release. `typsphinx/builder.py` was never touched — confirmed empty across all three commits (`git diff --name-only -- typsphinx/ 21eb4398 HEAD`).
- Did NOT change the sibling test `test_post_process_images_rehome_cross_drive_value_error_relocates` — it constructs its fixture from `builder.doctreedir` (a real pytest tmp path), which is already genuinely drive-qualified on Windows, so it does not share the same latent defect. Verified by reading the test rather than assumed.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The plan's own risk callout — "you cannot execute Windows locally" — held as expected: the fixture fix could only be proven green locally on POSIX under both locales; the Windows lanes of this plan's own CI dispatch (run `31858016832`) served as the GREEN authority for the actual fix, confirming `Test Python 3.13 on windows-latest` now `success`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 52 SC#3's toolchain half is discharged: the third `ci.yml` dispatch on the exact pushed tip reports `success` for all 12 jobs. Combined with plan 52-05's independent local coverage of the two docs builds and the full-corpus `-b typstpdf` GATE-02 gate (`52-GREEN-TREE-EVIDENCE.md`), SC#3 is fully discharged.
- The Broken Windows ledger is at `open_count: 0` — no longer blocks `/gsd-ship`.
- One new todo is now in `.planning/todos/pending/`: `2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md` (builder, minor) — a genuine candidate for the next milestone's backlog, not blocking this one.
- REL-07 deliberately stays open per the milestone's `branching_strategy: milestone` decision — it closes at `/gsd-complete-milestone`, not in this phase. Not marked complete here.
- No irreversible action taken by this plan: `git tag -l v0.8.0` and `git ls-remote --tags origin v0.8.0` both empty, `gh pr list` is `[]`, `release.yml` was never dispatched by this plan.

## Self-Check

- FOUND: tests/test_builder.py (modified, verified present)
- FOUND: .planning/todos/pending/2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md
- FOUND: .planning/phases/52-v0-8-0-release-prep-prep-only/52-CI-EVIDENCE.md (third section appended)
- FOUND: .planning/WINDOWS.md (open_count: 0)
- FOUND commit e78d5a64 (task 1)
- FOUND commit 6924a0be (task 2)
- FOUND commit 5ee9433a (task 3)

## Self-Check: PASSED

---
*Phase: 52-v0-8-0-release-prep-prep-only*
*Completed: 2026-08-15*
