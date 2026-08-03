---
phase: 42-captioned-table-drops-preceding-target-label
plan: 06
subsystem: release-prep
tags: [changelog, milestone-invariants, requirements-guard, gate-01, release-reconciliation]

# Dependency graph
requires:
  - phase: 42-04
    provides: "the depart_table fix commit (e5575f3) and its GATE-EVIDENCE-04.md GREEN evidence"
  - phase: 41-v0-7-0-release-automation-release-prep
    provides: "the curated ## [0.7.0] CHANGELOG entry and 41-SC4-INVARIANTS.md's own BASE SHA and column shapes, read-only source material"
provides:
  - "The TBL-03 bullet in the curated ## [0.7.0] CHANGELOG entry, matching MATH-02's granularity and shape"
  - "42-SC4-INVARIANTS.md: Phase 41's SC#4 milestone-invariant sweep re-measured over a range that includes Phase 42's fix commit, with a new change-site-to-RED manifest row for depart_table"
  - "42-CLOSEOUT-GUARD.md: the REL-04/REL-05 checkbox-flip hazard armed with a recorded pre-close baseline, checksum, and a three-step diff-check-and-revert procedure"
affects: [gsd-complete-milestone, v0.7.0-release-prep]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/42-captioned-table-drops-preceding-target-label/42-SC4-INVARIANTS.md
    - .planning/phases/42-captioned-table-drops-preceding-target-label/42-CLOSEOUT-GUARD.md
  modified:
    - CHANGELOG.md

key-decisions:
  - "Reconciliation lives entirely in new files under Phase 42's own directory; no 41-* artifact was edited, per 42-CONTEXT.md's Claude's-Discretion decision"
  - "42-SC4-INVARIANTS.md numbers its sections against REQUIREMENTS.md's milestone-invariant numbering (1, 2, 4, 5, 6) rather than 41-SC4-INVARIANTS.md's own internal '1 of 3 / 2 of 3 / 3 of 3' relabeling, for direct traceability"
  - "The change-site-to-RED manifest carries exactly one row (depart_table) because Phase 42's fix commit (e5575f3) touches exactly one visit_/depart_ handler in exactly one commit"

patterns-established: []

requirements-completed: [TBL-03]

coverage:
  - id: D1
    description: "CHANGELOG.md's curated ## [0.7.0] entry gains one TBL-03 bullet under ### Fixed, matching the MATH-02 bullet's granularity and requirement-ID shape"
    requirement: "TBL-03"
    verification:
      - kind: other
        ref: "grep -c '(TBL-03)' CHANGELOG.md returns 1; awk section-scoped check confirms placement between ### Fixed (line 50) and ### Verified (line 60)"
        status: pass
    human_judgment: false
  - id: D2
    description: "42-SC4-INVARIANTS.md re-measures Phase 41's SC#4 milestone-invariant sweep over a SHA range proven (via git merge-base --is-ancestor) to include Phase 42's depart_table fix commit, with a new change-site-to-RED manifest row in 40.1-NONREGRESSION.md §4's column shape"
    requirement: "TBL-03"
    verification:
      - kind: other
        ref: "git merge-base --is-ancestor e5575f3ab51144405c44764a5b192b9d5f7526b2 d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 (exit 0); git cat-file -e on both RED (d28f2c8) and fix (e5575f3) commits"
        status: pass
    human_judgment: false
  - id: D3
    description: "42-CLOSEOUT-GUARD.md records the four at-risk REQUIREMENTS.md lines (REL-04/REL-05 checkboxes + Traceability rows) verbatim with a sha256sum baseline and a three-step diff-check-and-revert procedure; REQUIREMENTS.md itself left byte-unchanged"
    requirement: "TBL-03"
    verification:
      - kind: other
        ref: "git status --porcelain .planning/REQUIREMENTS.md (empty); grep '^- \\[ \\] \\*\\*REL-0[45]\\*\\*' .planning/REQUIREMENTS.md (both still unchecked)"
        status: pass
    human_judgment: false

duration: 26min
completed: 2026-08-03
status: complete
---

# Phase 42 Plan 06: Phase 41 Release-Prep Reconciliation (SC#6) Summary

**Added the TBL-03 CHANGELOG bullet, re-measured Phase 41's SC#4 milestone-invariant sweep over a range including Phase 42's fix commit with a new change-site-to-RED manifest row, and armed the REL-04/REL-05 checkbox-flip guard with a checksummed pre-close baseline — all in new files, no `41-*` artifact touched.**

## Performance

- **Duration:** 26 min
- **Started:** 2026-08-03T14:30:00Z (approx.)
- **Completed:** 2026-08-03T14:56:38Z
- **Tasks:** 3
- **Files modified:** 1 (`CHANGELOG.md`); 2 new files created

## Accomplishments
- `CHANGELOG.md`'s curated `## [0.7.0]` entry now carries a TBL-03 bullet under `### Fixed`, matching the MATH-02 bullet's granularity — both the table's own name-derived label and the propagated target's label are described as now emitted.
- `42-SC4-INVARIANTS.md` re-derives BASE (`v0.6.5-1-g51e02b6`) and re-measures a fresh HEAD/commit-count, proves plan 42-04's fix commit (`e5575f3`) is inside `<BASE>..HEAD` via `git merge-base --is-ancestor`, and proves the RED commit (`d28f2c8`) is an ancestor of the fix commit. Invariants 1 (deps) and 2 (`@preview`) are confirmed unaffected by Phase 42; invariant 4 (node-handler change carries recorded-RED GATE-01 fixture) gains one manifest row for `depart_table`, in `40.1-NONREGRESSION.md` §4's exact column shape; invariant 5 (test migration per phase) records Phase 42's two new test modules; invariant 6 ("anywhere under X" grep) is confirmed not applicable to any Phase 42 criterion.
- `42-CLOSEOUT-GUARD.md` records REL-04's and REL-05's checkbox and Traceability-row lines verbatim with observed line numbers and a `sha256sum` baseline, records TBL-03's own pre-flip lines for contrast, and gives a three-step ordered diff-check-and-revert procedure to run after any future `phase.complete`-family command.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the TBL-03 bullet to the curated 0.7.0 CHANGELOG entry** - `d57f6d1` (docs)
2. **Task 2: Re-measure Phase 41's SC#4 invariant sweep over a range including Phase 42** - `d3bc623` (docs)
3. **Task 3: Arm the REL-04 / REL-05 checkbox-flip guard** - `527e3f6` (docs)

_No TDD tasks in this plan — all three are documentation/evidence-file tasks._

## Files Created/Modified
- `CHANGELOG.md` - Gained one bullet under `## [0.7.0]` → `### Fixed`: the TBL-03 line (both label forms now emitted for a captioned table preceded by a standalone target)
- `.planning/phases/42-captioned-table-drops-preceding-target-label/42-SC4-INVARIANTS.md` - New file: Phase 41's SC#4 milestone-invariant sweep re-measured over `<BASE>..HEAD` including Phase 42, with a change-site-to-RED manifest row for `depart_table`
- `.planning/phases/42-captioned-table-drops-preceding-target-label/42-CLOSEOUT-GUARD.md` - New file: the REL-04/REL-05 checkbox-flip hazard's pre-close baseline (verbatim lines + checksum) and revert procedure

## Decisions Made
- Followed `42-CONTEXT.md`'s Claude's-Discretion decision exactly: the reconciliation lives in two new files under Phase 42's own directory, and no `41-*` artifact was edited, appended to, or regenerated. Confirmed via `git status --porcelain .planning/phases/41-v0-7-0-release-automation-release-prep/` returning empty after every task.
- `42-SC4-INVARIANTS.md` labels its sections using `REQUIREMENTS.md`'s own milestone-invariant numbers (1, 2, 4, 5, 6) rather than `41-SC4-INVARIANTS.md`'s internal "1 of 3 / 2 of 3 / 3 of 3" relabeling, so a future reader does not need a translation step between the two files.
- The change-site-to-RED manifest carries exactly one row because Phase 42's own diff touches exactly one `visit_`/`depart_`-prefixed handler (`depart_table`) in exactly one commit (`e5575f3`) — confirmed by `git show e5575f3 --stat` showing only `typsphinx/translator.py` touched, and `42-GATE-EVIDENCE-04.md` §2's diff confirming the change is confined to `depart_table`'s body.

## Deviations from Plan

None of the three Rule 1/2/3 categories fired — no bug, no missing critical functionality, and no blocking issue was found in the code under this plan's own `files_modified` scope. Two items are surfaced below because the plan's own instructions required surfacing them explicitly, not because they were autonomously fixed:

### Surfaced, not auto-fixed

**1. [Surfaced per plan instruction] Open owner question: the `## [0.7.0]` heading's date is stale relative to Phase 42's actual landing date**
- **Found during:** Task 1
- **Issue:** `42-RESEARCH.md`'s Assumption A3 / Open Question 1 raised whether the `## [0.7.0]` heading (currently `2026-08-03`, Phase 41's close date) should instead track Phase 42's own landing date. The plan explicitly required leaving the date untouched and re-surfacing this question here rather than deciding it.
- **Action taken:** No edit made to the heading or its date. `git diff -- CHANGELOG.md` confirms the `## [0.7.0]` heading line is byte-identical to its pre-task state.
- **Who decides:** The owner, before `/gsd-complete-milestone` runs. This is cosmetic and does not block SC#6's mechanical requirement (the TBL-03 line itself is present and correctly placed regardless of the heading's date).

**2. [Observed, not corrected] The plan's own Task 1 `<automated>` verify command has a latent scoping bug**
- **Found during:** Task 1 verification
- **Issue:** The literal awk verification command in `42-06-PLAN.md`'s Task 1 `<verify>` block (`awk '/^## \[0.7.0\]/{z=1} z&&/^### Fixed/{f=NR} z&&/^### Verified/{v=NR} /TBL-03/{t=NR} END{exit !(f&&v&&t&&t>f&&t<v)}' CHANGELOG.md`) never resets `z` after entering the `## [0.7.0]` section, so `f` and `v` keep getting overwritten by every later `### Fixed`/`### Verified` heading anywhere else in the 900+-line file, landing on the file's LAST occurrences (line 842 and line 313 respectively) rather than the ones inside `## [0.7.0]`. Run verbatim, it returns exit 1 (a false failure) even though the placement is correct.
- **Action taken:** Not modified — this is a bug in the plan's own verify string, not in `CHANGELOG.md` or any file this task is scoped to touch, so it is out of this task's `files: CHANGELOG.md` scope per the deviation rules' scope boundary. Verified correctness instead with a corrected, section-scoped awk that resets `z` on the next `## [` heading (see below), which confirms `f=50 v=60 t=56` and `t>f && t<v` both hold — the bullet IS correctly placed.
- **Recommendation:** A future plan-authoring pass on this pattern should scope the section check to stop (or reset `z`) at the next `## [` heading, e.g. `awk '/^## \[0\.7\.0\]/{z=1;next} /^## \[/{if(z)exit} z&&/^### Fixed/{f=NR} z&&/^### Verified/{v=NR} z&&/TBL-03/{t=NR} END{exit !(f&&v&&t&&t>f&&t<v)}'`.

---

**Total deviations:** 0 auto-fixed; 2 surfaced per explicit plan instruction (1 open owner question, 1 verify-script observation).
**Impact on plan:** None on scope or correctness — both items are informational surfacing required by the plan itself, not corrective action outside its bounds.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness

SC#6 is discharged: the curated `## [0.7.0]` CHANGELOG entry carries its TBL-03 line, and the SC#4 invariant sweep has a re-measured record covering Phase 42. Combined with `42-05`'s byte-invariance evidence (owned by a sibling plan in this same wave), Phase 42's own success criteria are positioned to close.

**Before `/gsd-complete-milestone` runs, two items need owner attention** (both surfaced above, neither blocking the mechanical requirement):
1. Whether the `## [0.7.0]` heading's date should be updated to reflect Phase 42's actual landing date rather than Phase 41's close date.
2. Confirm Phase 42's own close step (flipping TBL-03's checkbox and Traceability row) follows `42-CLOSEOUT-GUARD.md`'s procedure, so any `phase.complete`-family REL-04/REL-05 auto-flip is caught and reverted before commit, exactly as it was for Phase 41.

`41-HANDOFF.md`'s 7-item publish checklist remains valid and un-executed; it runs only after Phase 42's verifier confirms SC#1-SC#6.

---
*Phase: 42-captioned-table-drops-preceding-target-label*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `CHANGELOG.md`
- FOUND: `.planning/phases/42-captioned-table-drops-preceding-target-label/42-SC4-INVARIANTS.md`
- FOUND: `.planning/phases/42-captioned-table-drops-preceding-target-label/42-CLOSEOUT-GUARD.md`
- FOUND: `.planning/phases/42-captioned-table-drops-preceding-target-label/42-06-SUMMARY.md`
- FOUND commit: `d57f6d1` (Task 1)
- FOUND commit: `d3bc623` (Task 2)
- FOUND commit: `527e3f6` (Task 3)
- FOUND commit: `a47fdb2` (SUMMARY)

All claimed files exist on disk and all claimed commits resolve in `git log --all`.
