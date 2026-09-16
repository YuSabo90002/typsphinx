---
phase: 73-v0-9-5-close-prep-prep-only-unpublished
plan: 06
subsystem: release-prep
tags: [release-verification, sc1-fence, unpublished, d13, d12, evidence]

# Dependency graph
requires:
  - phase: 73 (waves 1-2: 73-01..73-05)
    provides: observation 1 (73-02), local green-tree proof (73-03), the phase's single push and
      CI dispatch (73-04), and the trial-merge pre-flight (73-05)
provides:
  - Observation 2 of 2 of SC#1's unpublished-shaped-tree fence, timestamped 32m46s after
    observation 1, with every remote probe re-run and positively controlled
  - The D-13 milestone fences (typsphinx/ and .github/workflows/ diff since MILESTONE_BASE) re-run
    on the close tip
  - The phase-scoped product diff from PHASE_BASE_SHA, proven to be exactly CHANGELOG.md
  - The D-12 post-dispatch planning-only proof (every commit after PUSHED_SHA touches only
    .planning/)
  - SC1_VERDICT = MET
affects: [73-07 (phase handoff and closeout), complete-milestone (REL-14 observations)]

# Actuals (#2632)
actuals:
  tokens: 6229
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Phase 69's scoped-plus-widened diff shape (not the masked-AST re-run), reused for D-13
      because nothing under typsphinx/ changed in this milestone"
    - "Two positive-controlled observations of the same probe set, separated by two waves and a
      full CI run, to make a repeated 'unpublished' claim falsifiable rather than transcribed"

key-files:
  created: []
  modified:
    - .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-SC1-INVARIANTS.md

key-decisions:
  - "Observation 2 repeats every observation-1 probe with an OBS2_ prefix rather than only
    diffing against observation 1's recorded values, so a live positive control accompanies each
    negative assertion a second time."
  - "The close-tip widened diff is read as Phase 72's five files plus this phase's own
    CHANGELOG.md, C-sorted, rather than expecting it to still equal Phase 72's five-file list
    verbatim — the phase's own product edit is expected to show up in a milestone-wide widened
    diff taken after that edit landed."

requirements-completed: []  # D-08: REL-14 cited for coverage only; checked only at /gsd-complete-milestone

coverage:
  - id: D1
    description: "SC#1 observation 2 of 2: every remote probe (local/remote tags, PyPI, GitHub
      Releases, release.yml runs, branch pull requests) re-run 32m46s after observation 1, all
      still negative for v0.9.3/v0.9.4/v0.9.5, each paired with the same positive control."
    requirement: "REL-14"
    verification:
      - kind: other
        ref: "task 1 <verify> automated block, .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-06-PLAN.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-13 milestone fences re-proven on the close tip: typsphinx/ and
      .github/workflows/ diff since MILESTONE_BASE is empty, the pathspec (16 tracked files) and
      widened-diff (Phase 72's five files plus CHANGELOG.md) controls hold, zero version-bump
      commits, and origin/main not absorbed."
    requirement: "REL-14"
    verification:
      - kind: other
        ref: "task 2 <verify> automated block, .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-06-PLAN.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "Phase-scoped product diff from PHASE_BASE_SHA is exactly CHANGELOG.md (15
      insertions, 0 deletions), and no other named product path changed anywhere in the phase."
    requirement: "REL-14"
    verification:
      - kind: other
        ref: "task 2 <verify> automated block, .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-06-PLAN.md"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-12 post-dispatch proof: PUSHED_SHA is an ancestor of HEAD, every commit after
      it touches only .planning/, no release.yml run ever fired at that tip, and exactly one
      workflow_dispatch CI run exists at it."
    requirement: "REL-14"
    verification:
      - kind: other
        ref: "task 2 <verify> automated block, .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-06-PLAN.md"
        status: pass
    human_judgment: false
  - id: D5
    description: "SC1_VERDICT = MET written to 73-SC1-INVARIANTS.md, closing ROADMAP SC#1 in
      full: two positively-controlled unpublished observations, no version bump, and an empty
      milestone-wide typsphinx/.github-workflows diff."
    requirement: "REL-14"
    verification:
      - kind: other
        ref: "grep SC1_VERDICT .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-SC1-INVARIANTS.md"
        status: pass
    human_judgment: false

duration: 17min
completed: 2026-09-16
status: complete
---

# Phase 73 Plan 06: SC#1 Close-Tip Fence Summary

**Observation 2 of SC#1's unpublished-shaped-tree fence, 32m46s after observation 1 and after the
phase's only push/CI dispatch, plus the D-13 close-tip milestone fences, the CHANGELOG.md-only
phase-scoped diff, and the D-12 post-dispatch planning-only proof — `SC1_VERDICT = MET`.**

`OBS1_AT = 2026-09-16T09:57:35Z`, `OBS2_AT = 2026-09-16T10:30:21Z`,
`CLOSE_MILESTONE_CODE_WORKFLOW_DIFF = empty`, `CLOSE_MILESTONE_PRODUCT_FILES = CHANGELOG.md
CLAUDE.md README.md docs/source/contributing.rst docs/source/index.rst tox.ini`,
`PHASE_PRODUCT_FILES = CHANGELOG.md`, `POST_DISPATCH_PRODUCT_FILES = 0`, `SC1_VERDICT = MET`. No
HALT heading was written.

## Performance

- **Duration:** 17 min
- **Started:** 2026-09-16T10:20:00Z (approx.)
- **Completed:** 2026-09-16T10:36:46Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Re-ran every SC#1 remote probe from observation 1 (version line, local tags, unfiltered
  `git ls-remote --tags`, PyPI HTTP codes, GitHub Releases, `release.yml` run history, branch pull
  requests) 32 minutes 46 seconds later, each still paired with the same positive control against
  `v0.9.2` — the fence held across wave 2's local green-tree proof, the phase's single CI dispatch,
  and the trial-merge pre-flight.
- Re-proved the D-13 milestone-wide `typsphinx/` and `.github/workflows/` diff empty on the close
  tip, against a pathspec control (16 tracked files) and a widened-diff control equal to Phase 72's
  five product files plus this phase's own `CHANGELOG.md`.
- Measured the phase-scoped product diff from `PHASE_BASE_SHA` as exactly `CHANGELOG.md` (15
  insertions, 0 deletions) with no other named product path touched.
- Proved every commit after `PUSHED_SHA` (the phase's single CI dispatch) is planning-only, with no
  `release.yml` run ever having fired at that tip and exactly one `workflow_dispatch` CI run there.
- Wrote `SC1_VERDICT = MET`, closing ROADMAP SC#1.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: SC#1 observation 2 of 2, every remote probe re-run with its positive control** -
   `7fed9a6d` (docs)
2. **Task 2: D-13 fences on the close tip, the phase-scoped product diff, the post-dispatch
   planning-only proof, and the SC#1 verdict** - `5da5b890` (docs)

_Note: this plan carries no TDD tasks; each task is a single evidence-append commit._

## Files Created/Modified
- `.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-SC1-INVARIANTS.md` - appended
  `## Observation 2 of 2`, `## Milestone fences on the close tip (D-13)`,
  `## The phase-scoped product diff`, `## Commits after the CI dispatch`, and `## SC#1 verdict`

## Decisions Made
- Observation 2 repeats every observation-1 probe under an `OBS2_` key with the same positive
  control, rather than diffing only against observation 1's recorded values — a live positive
  control accompanies each negative assertion a second time, not just the first.
- The close-tip widened diff is read as Phase 72's five files plus this phase's own
  `CHANGELOG.md`, C-sorted — expected to gain exactly the one file this phase itself authored,
  not to still equal Phase 72's five-file list verbatim.

## Deviations from Plan

None - plan executed exactly as written. Every automated `<verify>` block in both tasks passed on
first execution; no fix-attempt cycles were needed.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required. Every command in this plan is a read; nothing
was pushed, tagged, released, dispatched or commented (REL-14 prohibition).

## Next Phase Readiness
- SC#1 is closed (`SC1_VERDICT = MET`) and `73-SC1-INVARIANTS.md` now carries both observations
  plus the close-tip fences, ready for 73-07's phase handoff to read verbatim.
- `.planning/REQUIREMENTS.md` was not touched by this plan (verified: `git status --porcelain
  .planning/REQUIREMENTS.md` empty across both commits) — REL-14 stays `- [ ]` / `Pending` per
  D-08, to be checked only at `/gsd-complete-milestone`.
- No blockers. Plan 73-07 can proceed to assemble the phase handoff from this file plus
  `73-CI-EVIDENCE.md`, `73-GREEN-TREE-EVIDENCE.md`, `73-PREFLIGHT-EVIDENCE.md` and
  `73-CLOSEOUT-GUARD.md`.

---
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Completed: 2026-09-16*

## Self-Check: PASSED

- `[ -f .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-SC1-INVARIANTS.md ]` — FOUND
- `git log --oneline --all --grep="73-06"` returns 2 matching commits (`7fed9a6d`, `5da5b890`) —
  FOUND
- Re-ran both tasks' `<verify>` automated blocks against the committed tree: both printed
  `TASK1_VERIFY_PASS` / `TASK2_VERIFY_PASS` with exit 0.
- `grep -c '^## HALT' 73-SC1-INVARIANTS.md` = 0.
- `sed -n "s/^SC1_VERDICT = //p" 73-SC1-INVARIANTS.md` = `MET`.

## Commit Ledger (#3968)

```
plan_head_before: b3e05b6e306cad045903bb55c1ff94e45e37b68d
commits: 2
```
