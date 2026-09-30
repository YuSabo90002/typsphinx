---
phase: 73-v0-9-5-close-prep-prep-only-unpublished
plan: 02
subsystem: release-process
tags: [release-prep, requirements-fence, sc1-invariants, api-coverage, evidence]

# Dependency graph
requires:
  - phase: 72-tox-e-linkcheck-and-root-toctree-deduplication
    provides: PUSHED_SHA (CI-tested pushed tip) and PRODUCT_DIFF_FILES (the five-file milestone diff), read from 72-CI-EVIDENCE.md and 72-GATES-EVIDENCE.md
provides:
  - "73-CLOSEOUT-GUARD.md: phase-head REL-14 baseline (PHASE_BASE_SHA, REQ_SHA256_BASE, REQ_LINES_BASE, REL14_HITS_BASE, GUARD_AT), tied to Phase 72's pushed tip, with both operator procedures for phase.complete and /gsd-verify-work"
  - "73-SC1-INVARIANTS.md: SC#1 observation 1 of 2 (every remote negative for v0.9.3/v0.9.4/v0.9.5 paired with a positive control against v0.9.2) and the D-13 milestone fences (MILESTONE_BASE, empty typsphinx/+.github/workflows/ diff, pathspec and widened-diff controls)"
  - "COVERAGE.md: reasoned no-external-API declaration accepted by the seal-time api-coverage.verify-pre gate"
affects: [73-03, 73-05, 73-06, 73-07]

# Actuals (#2632)
actuals:
  tokens: 9083
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Whole-file SHA-256 fence over .planning/REQUIREMENTS.md as the primary requirement-flip detector (line-count-neutral flips are invisible to wc -l)"
    - "Unfiltered git ls-remote --tags fetched once, with counts derived for all probed refs, avoiding the silent-empty-vs-unreachable ambiguity of a filtered probe"
    - "Every remote negative paired with a positive control from the same source/listing"
    - "Scoped-diff-plus-widened-diff-plus-pathspec-control triad proving an empty git diff isn't an artifact of a broken anchor"

key-files:
  created:
    - .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CLOSEOUT-GUARD.md
    - .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-SC1-INVARIANTS.md
    - .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/COVERAGE.md
  modified: []

key-decisions:
  - "None - followed plan as specified (carries forward D-08 and D-13 from 73-CONTEXT.md verbatim)"

patterns-established:
  - "Pattern 1: The REL-14 closeout guard is byte-for-byte modeled on 71-CLOSEOUT-GUARD.md, substituting REL-13 for REL-14 and re-deriving every value fresh rather than copying Phase 71's numbers"
  - "Pattern 2: The SC#1 invariants file follows Phase 69's lightweight scoped-plus-widened shape, not Phase 71's masked-AST variant, because nothing under typsphinx/ changed this milestone (D-13)"

requirements-completed: []  # D-08: this plan reads REL-14 for coverage only and never edits REQUIREMENTS.md

coverage:
  - id: D1
    description: "Phase-head REL-14 closeout guard recorded before any other plan's commit: PHASE_BASE_SHA, REQ_SHA256_BASE, REQ_LINES_BASE, REL14_HITS_BASE and GUARD_AT, tied to Phase 72's CI-tested pushed tip, with both operator procedures (phase.complete from /gsd-execute-phase, and /gsd-verify-work's inline transition) written out"
    requirement: REL-14
    verification:
      - kind: other
        ref: "73-02-PLAN.md Task 1 <verify> automated command (re-run live against the committed 73-CLOSEOUT-GUARD.md)"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#1 observation 1 of 2: every remote negative for v0.9.3/v0.9.4/v0.9.5 (local/remote tags, PyPI, GitHub Releases, release.yml runs, branch PRs) paired with a positive control against the existing v0.9.2, plus the D-13 milestone-wide typsphinx/+.github/workflows/ diff proven empty against a pathspec control and a widened-diff control matching Phase 72's PRODUCT_DIFF_FILES"
    requirement: REL-14
    verification:
      - kind: other
        ref: "73-02-PLAN.md Task 2 <verify> automated command (re-run live against the committed 73-SC1-INVARIANTS.md)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Reasoned no-external-API COVERAGE.md written and accepted by the live api-coverage.verify-pre gate, explaining both detected signals rather than fabricating a capability matrix"
    verification:
      - kind: other
        ref: "node gsd-tools.cjs check api-coverage.verify-pre .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished (live run)"
        status: pass
    human_judgment: false

# Metrics
duration: 9min
completed: 2026-09-16
status: complete
---

# Phase 73 Plan 02: Phase-Head REL-14 Fence, SC#1 Observation 1, and API Coverage Declaration Summary

**Records the REL-14 checksum fence, the D-13 milestone fences and SC#1's first fully-positively-controlled remote observation, and a reasoned COVERAGE.md, all at phase head before any other plan's commit lands.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-09-16T09:53:00Z (approx.)
- **Completed:** 2026-09-16T10:02:25Z
- **Tasks:** 3
- **Files modified:** 3 (all newly created)

## First section: key values recorded

```
PHASE_BASE_SHA = c6bc641aa1745e6413b4f33c4d0c572a962da430
REQ_SHA256_BASE = 7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad
REQ_LINES_BASE = 70
REL14_HITS_BASE = 4
OBS1_AT = 2026-09-16T09:57:35Z
MILESTONE_BASE = 098a8ff64cf008822eef9dc69f75102ded3f7bc1
MAIN_MOVED_OBS1 = yes
MILESTONE_CODE_WORKFLOW_DIFF = empty
```

## Accomplishments

- `73-CLOSEOUT-GUARD.md` records the REL-14 checksum fence baseline at phase head — digest, line
  count and hit count agree digit-for-digit with the planning-time census (70 lines, 4 hits), and
  the phase base is proven tied to Phase 72's CI-tested pushed tip (`PUSHED_SHA` is an ancestor of
  `PHASE_BASE_SHA` with an empty product-tree diff between them). Both operator procedures
  (`phase.complete` from `/gsd-execute-phase`, and `/gsd-verify-work`'s inline transition) are
  written with the scratch-backup instruction and the "reverted and reported, never committed"
  rule.
- `73-SC1-INVARIANTS.md` records SC#1's first observation: every remote probe for `v0.9.3`,
  `v0.9.4` and `v0.9.5` (tags, PyPI, GitHub Releases, `release.yml` runs, branch PRs) came back
  empty/negative, each paired with a positive control against the existing `v0.9.2` from the same
  listing. The D-13 milestone-wide diff over `typsphinx/` and `.github/workflows/` from
  `MILESTONE_BASE` (`098a8ff6`, matching Phase 72's pushed tip) is empty, proven against a
  pathspec control (16 tracked files) and a widened-diff control that reproduces Phase 72's own
  `PRODUCT_DIFF_FILES` exactly.
- `COVERAGE.md` declares no external API integration, explaining both signals the live detector
  raised over this phase's plan bodies (the declaration's own required opening line, and the
  Trust Boundaries table's read-only "GitHub API, PyPI" row). The live
  `check api-coverage.verify-pre` run reports `"passed": true`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — record the phase-head REQUIREMENTS.md closeout guard for REL-14** - `47a1d7ab` (docs)
2. **Task 2: SC#1 fence observation 1 of 2 with a positive control on every remote negative, and the D-13 milestone fences at phase head** - `59c690a3` (docs)
3. **Task 3: Write the reasoned no-external-API COVERAGE.md and prove the seal-time gate accepts it** - `fc3955c7` (docs)

**Plan metadata:** commit follows this SUMMARY.

_Note: this plan carries no TDD tasks; all three commits are `docs`-typed evidence artifacts._

## Files Created/Modified

- `.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CLOSEOUT-GUARD.md` - phase-head REL-14 checksum fence, baseline, lines-under-guard classification, and both operator procedures
- `.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-SC1-INVARIANTS.md` - SC#1 observation 1 of 2 and the D-13 milestone fences
- `.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/COVERAGE.md` - reasoned no-external-API declaration, seal gate result

## Decisions Made

None - followed plan as specified. D-08 and D-13 from `73-CONTEXT.md` were carried forward
verbatim; no new decision was required during execution.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. One observational note, not a deviation: `origin/main` has moved past `MILESTONE_BASE`
(`098a8ff6` → `6e2b7899`) since the milestone branch was cut. This is recorded as
`MAIN_MOVED_OBS1 = yes` in `73-SC1-INVARIANTS.md`, per the plan's own instruction that a moved
`main` is not a failure at this observation — it is D-07's case, measured by plan 73-05's
non-committing trial merge against the live `origin/main` tip, not against the fixed
`MILESTONE_BASE` anchor used here.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The REL-14 checksum fence baseline, the Phase-72 tie, and both operator procedures are in place
  for plan 73-07's close-time re-verification and the orchestrator's third observation.
- SC#1's first observation is recorded; plan 73-06 owns observation 2 (the close-tip repeat) two
  waves and one CI dispatch later.
- `COVERAGE.md` satisfies the seal-time API-coverage gate for this phase directory.
- No blockers. This plan modified no product-tree file and never touched
  `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` or `.planning/STATE.md`.

---
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Completed: 2026-09-16*

## Self-Check: PASSED

- `[ -f .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CLOSEOUT-GUARD.md ]` → FOUND
- `[ -f .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-SC1-INVARIANTS.md ]` → FOUND
- `[ -f .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/COVERAGE.md ]` → FOUND
- `git log --oneline --all --grep="73-02"` → found `47a1d7ab`, `59c690a3`, `fc3955c7` (all three task commits)
- All three tasks' `<acceptance_criteria>` and `<verify>` automated commands were re-run live and passed (see per-task verification above).
- Plan-level `<verification>` re-confirmed: REL-14 fence baseline recorded and tied to Phase 72; SC#1 observation 1 holds with positive controls; D-13 milestone diff empty against proven pathspec/widened-diff controls; `check api-coverage.verify-pre` reports `"passed": true`.
