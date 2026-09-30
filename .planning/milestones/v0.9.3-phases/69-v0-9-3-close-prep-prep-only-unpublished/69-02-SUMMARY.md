---
phase: 69-v0-9-3-close-prep-prep-only-unpublished
plan: 02
subsystem: release-prep
tags: [requirements-fence, sha256-checksum, sc1-invariants, api-coverage, release-prep]

# Dependency graph
requires:
  - phase: 68
    provides: DOC-19..DOC-21 documentation follow-through, the last phase before close prep
provides:
  - 69-CLOSEOUT-GUARD.md — phase-head REQUIREMENTS.md checksum guard (PHASE_BASE_SHA,
    REQ_SHA256_BASE, REQ_LINES_BASE, REL12_HITS_BASE, GUARD_AT), the classification of REL-12's four
    grep hits, and both operator re-verification procedures
  - 69-SC1-INVARIANTS.md — SC#1 observation 1 of 2, every remote negative paired with a positive
    control, plus the milestone-wide typsphinx/ fence (constraint 13)
  - COVERAGE.md — reasoned no-external-API declaration accepted by the seal-time gate
affects: [69-06 (close-time re-verification, observation 2, 69-HANDOFF.md), /gsd-complete-milestone (REL-12's actual close)]

# Actuals (#2632)
actuals:
  tokens: 7770
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Phase-head-before-any-other-plan checksum fence for a REL requirement, reusing the
      61-CLOSEOUT-GUARD.md / 63-CLOSEOUT-GUARD.md shape"
    - "Positive-controlled remote negative probes (every 'X does not exist remotely' probe paired
      with a probe for something that does, from the same fetch)"

key-files:
  created:
    - .planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CLOSEOUT-GUARD.md
    - .planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-SC1-INVARIANTS.md
    - .planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/COVERAGE.md
  modified: []

key-decisions:
  - "REL-12's checkbox and Traceability row are read directly out of .planning/REQUIREMENTS.md and
    quoted, never edited — every value recorded (digest, line count, hit count) agrees byte-for-byte
    with the plan's own planning-time census, confirmed by fresh commands run inside this worktree."
  - "COVERAGE.md accepts the detector's two true-positive-shaped signals as self-referential
    (69-02-PLAN.md's own must_haves citation of this file's opening sentence, and its
    threat_model Trust Boundaries row naming GitHub API/PyPI as read-only) rather than papering
    over the detected:true result."

patterns-established:
  - "Pattern: every SC#1-shaped 'prove X is unpublished' probe pairs its negative with a positive
    control drawn from the identical fetch/listing, so an unreachable remote cannot be mistaken for
    a genuine negative."

requirements-completed: []

coverage:
  - id: D1
    description: "69-CLOSEOUT-GUARD.md records the phase-head REQUIREMENTS.md checksum guard
      (PHASE_BASE_SHA, REQ_SHA256_BASE, REQ_LINES_BASE, REL12_HITS_BASE, GUARD_AT), classifies the
      four REL-12 grep hits, and writes both operator re-verification procedures naming both
      transition entry points."
    requirement: REL-12
    verification:
      - kind: other
        ref: "task 1 <automated> verify (see PLAN.md 69-02, task 1) — re-run inline, exit 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "69-SC1-INVARIANTS.md records SC#1 observation 1 of 2 with a positive control on
      every remote probe (local/remote tag, PyPI, GitHub Release, release.yml, pull-request), plus
      the milestone-wide typsphinx/ fence (constraint 13) measured against a non-vacuous anchor."
    requirement: null
    verification:
      - kind: other
        ref: "task 2 <automated> verify (see PLAN.md 69-02, task 2) — re-run inline, exit 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "COVERAGE.md provides a reasoned no-external-API declaration, naming both detector
      signals as self-referential rather than real integrations, and is accepted by the seal-time
      api-coverage.verify-pre gate."
    requirement: null
    verification:
      - kind: other
        ref: "task 3 <automated> verify (see PLAN.md 69-02, task 3) — re-run inline, exit 0"
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-09-12
status: complete
---

# Phase 69 Plan 02: REL-12 Checksum Fence, SC#1 Observation 1, and API-Coverage Declaration Summary

**Recorded the phase-head REL-12 checksum fence, the first of two separated SC#1
unpublished-shaped-tree observations (every remote negative paired with a positive control), and a
reasoned no-external-API declaration the seal-time gate accepts.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-09-12T22:32:00Z (approx, worktree branch-check pass)
- **Completed:** 2026-09-12T22:39:23Z
- **Tasks:** 3 completed
- **Files modified:** 3 created, 0 modified

## Accomplishments
- `69-CLOSEOUT-GUARD.md` records `PHASE_BASE_SHA = 2db4e803d36d5f7a5db0a92b08cac4988fa88957`,
  `REQ_SHA256_BASE = 02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a`,
  `REQ_LINES_BASE = 172`, `REL12_HITS_BASE = 4`, `GUARD_AT = 2026-09-12T22:33:44Z` — every value
  agreeing byte-for-byte with the plan's own planning-time census — and names both
  `phase.complete`-family transition entry points (`/gsd-execute-phase` and `/gsd-verify-work`) with
  the scratch-backup and `git checkout -- .planning/REQUIREMENTS.md` reversion procedure.
- `69-SC1-INVARIANTS.md` records SC#1 observation 1 of 2: `pyproject.toml:7` still `0.9.2`, no local
  or remote `v0.9.3` tag (against the `v0.9.0`/`v0.9.2` positive controls), PyPI 404 for `0.9.3`
  (against 200 for `0.9.2`), `v0.9.2` still `isLatest` on GitHub Releases, no `release.yml` run since
  `2026-09-02` (against run `33318905691` present), and no pull request from the milestone branch
  (against a non-empty unscoped listing) — plus the milestone `typsphinx/` fence: an empty scoped
  diff against `MILESTONE_BASE = 6181768f64b4cee62a77ac4e26c60c3c976cbb6e`, a non-empty 9-file
  widened diff as the anchor's positive control, and zero version-bump commits.
- `COVERAGE.md` records the detector's `detected: true` result verbatim (two signals, both
  self-referential: 69-02-PLAN.md's own `must_haves` citation of this file's opening sentence, and
  its `threat_model` Trust Boundaries row naming "GitHub API"/PyPI as read-only), explains why
  neither is a real integration, lists the phase's actual network use, and records
  `check api-coverage.verify-pre`'s `"passed": true, "none_declared": true` result.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: record the phase-head REQUIREMENTS.md closeout guard, PHASE_BASE_SHA and both
   operator procedures** - `67172bd6` (docs)
2. **Task 2: SC#1 fence observation 1 of 2, every remote negative paired with a positive control,
   plus the milestone typsphinx/ fence** - `a7dde3dd` (docs)
3. **Task 3: Write the reasoned no-external-API COVERAGE.md and prove the seal-time gate accepts
   it** - `0527f857` (docs)

**Plan metadata:** this SUMMARY's own commit (recorded by the orchestrator after merge; not
committed by this plan in worktree mode).

## Files Created/Modified
- `.planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CLOSEOUT-GUARD.md` - phase-head
  REQUIREMENTS.md checksum fence, lines-under-guard classification, both operator procedures
- `.planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-SC1-INVARIANTS.md` - SC#1
  observation 1 of 2, positive-controlled remote probes, the typsphinx/ fence
- `.planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/COVERAGE.md` - reasoned
  no-external-API declaration and the accepted seal-time gate result

## Decisions Made
- Kept the freshly-measured baseline values (digest, line count, hit count) as the recorded
  baseline rather than the planning-time census figures, per the plan's own instruction to
  re-measure rather than trust — they happened to agree byte-for-byte, and that agreement is
  recorded explicitly as a cross-check, not substituted for the live measurement.
- Classified `COVERAGE.md`'s two detector signals individually with their exact snippets rather
  than a single blanket "false positive" statement, following the precedent `61-CONTEXT.md`/
  `61-COVERAGE.md` set for this exact class of self-referential detector hit.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `69-CLOSEOUT-GUARD.md`'s baseline and both operator procedures are in place for plan 69-06's
  close-time re-verification and for the operator running `phase.complete`-family tooling at
  whichever entry point fires.
- `69-SC1-INVARIANTS.md`'s observation 1 and the `typsphinx/` fence are recorded; observation 2 and
  the phase-scoped diff from `PHASE_BASE_SHA` are owed to plan 69-06, two waves and one CI dispatch
  later.
- `COVERAGE.md` satisfies the seal-time `api-coverage.verify-pre` gate for this phase.
- No blockers. `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md` are
  byte-unchanged by this plan.

## Self-Check: PASSED

- `[ -f .planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-CLOSEOUT-GUARD.md ]` → FOUND
- `[ -f .planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/69-SC1-INVARIANTS.md ]` → FOUND
- `[ -f .planning/phases/69-v0-9-3-close-prep-prep-only-unpublished/COVERAGE.md ]` → FOUND
- `git log --oneline --all | grep -q 67172bd6` → FOUND
- `git log --oneline --all | grep -q a7dde3dd` → FOUND
- `git log --oneline --all | grep -q 0527f857` → FOUND
- Task 1 `<automated>` verify: re-run, exit 0 (PASS)
- Task 2 `<automated>` verify: re-run, exit 0 (PASS)
- Task 3 `<automated>` verify: re-run, exit 0 (PASS)
- Plan-level `<verification>`: REL-12 digest/line-count/hit-count match live file and REL-12 is
  `[ ]`/Pending (PASS); SC#1 observation 1 holds with a positive control on every remote probe
  (PASS); the milestone `typsphinx/` diff is empty against the non-vacuous `MILESTONE_BASE` anchor
  (PASS); `check api-coverage.verify-pre` passes on `COVERAGE.md` (PASS).
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` unchanged since
  `PHASE_BASE_SHA` (confirmed empty `git diff --name-only`).

---
*Phase: 69-v0-9-3-close-prep-prep-only-unpublished*
*Completed: 2026-09-12*
