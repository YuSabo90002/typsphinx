---
phase: 41-v0-7-0-release-automation-release-prep
plan: 07
subsystem: release-process
tags: [release-evidence, changelog, handoff, prep-publish-fence, roadmap-verdict]

requires:
  - phase: 41-01
    provides: 41-REL04-EVIDENCE.md (SC#1's live-run demonstration and D-09 job-graph proof)
  - phase: 41-02
    provides: the version bump + curated CHANGELOG entry SC#2 measures directly
  - phase: 41-04
    provides: 41-JA-GLYPH-BAR.md + 41-JA-GLYPHBAR-SIGNOFF.md (SC#3's `ja` glyph-bar half)
  - phase: 41-05
    provides: 41-GREEN-TREE-EVIDENCE.md (SC#3's mechanical half)
  - phase: 41-06
    provides: 41-SC4-INVARIANTS.md (SC#4's milestone-invariant proof)
provides:
  - 41-RELEASE-EVIDENCE.md, an SC#1-SC#5 roll-up citing sibling verdicts by quotation, with SC#2
    measured directly and SC#5's first fence observation
  - 41-HANDOFF.md, a standalone 7-item publish checklist for /gsd-complete-milestone, with SC#5's
    second, independent fence observation
affects: [gsd-complete-milestone, v0.7.0-close]

tech-stack:
  added: []
  patterns:
    - "Roll-up-by-citation: quote a sibling evidence file's own verdict sentence rather than
      re-deriving or retyping the measured value, so a transcription error cannot create a second,
      divergent number."
    - "Two independent absence observations at two separate moments, both local AND remote tag
      probes, as the proof shape for 'no irreversible action was taken' (35-HANDOFF.md convention)."

key-files:
  created:
    - .planning/phases/41-v0-7-0-release-automation-release-prep/41-RELEASE-EVIDENCE.md
    - .planning/phases/41-v0-7-0-release-automation-release-prep/41-HANDOFF.md
  modified: []

key-decisions:
  - "41-RELEASE-EVIDENCE.md is deliberately not named 41-VERIFICATION.md (verifier-reserved name that would be clobbered), following the 35-RELEASE-EVIDENCE.md precedent."
  - "SC#2 is measured directly in this plan (typsphinx.__version__, pyproject.toml, README.md, uv.lock, CHANGELOG heading + tail link block) because no sibling evidence file already owns it."
  - "Both stated qualifications from sibling files (Invariant 1's dev-only pillow addition; Invariant 3's scope limited to the 3 single-hit handlers) are carried into the roll-up unmodified rather than smoothed into an unqualified PROVEN."

patterns-established:
  - "Phase-close roll-up plans cite and quote rather than re-measure, except for the one criterion no sibling plan owns."

requirements-completed: [REL-04, REL-05]

coverage:
  - id: D1
    description: "41-RELEASE-EVIDENCE.md rolls up all five ROADMAP success criteria, quoting each sibling evidence file's own verdict and measuring SC#2 directly"
    requirement: "REL-04"
    verification:
      - kind: manual_procedural
        ref: ".planning/phases/41-v0-7-0-release-automation-release-prep/41-RELEASE-EVIDENCE.md (automated verify block passed: all required section markers present, tag-emptiness re-confirmed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "41-HANDOFF.md records the 7-item publish checklist with Owner/Ordering for every step, the excluded-actions list, D-14's deferred todos, and SC#5's second fence observation"
    requirement: "REL-05"
    verification:
      - kind: manual_procedural
        ref: ".planning/phases/41-v0-7-0-release-automation-release-prep/41-HANDOFF.md (automated verify block passed: 7 numbered checklist items, both tag probes empty, REQUIREMENTS.md diff empty)"
        status: pass
    human_judgment: false

duration: 32min
completed: 2026-08-03
status: complete
---

# Phase 41 Plan 07: Release-Evidence Roll-Up + Publish Handoff Summary

**Rolled up all five ROADMAP SC#1-SC#5 verdicts by citation into `41-RELEASE-EVIDENCE.md` (measuring
only SC#2 directly, since no sibling plan owns it), and wrote the standalone `41-HANDOFF.md`
7-item publish checklist — proving the prep/publish fence held with two independent, timestamped
`git tag`/`git ls-remote` observations 2m44s apart, both empty.**

## Performance

- **Duration:** ~32 min
- **Started:** 2026-08-03T12:04:00Z (approx.; environment provisioning + evidence reading)
- **Completed:** 2026-08-03T12:16:42Z (Task 2 commit)
- **Tasks:** 2/2
- **Files modified:** 2 (both newly created)

## Accomplishments

- `41-RELEASE-EVIDENCE.md` created: opens with the reserved-filename rationale, carries one `## SC#N`
  section per ROADMAP criterion (each quoting the criterion verbatim and its evidence file's own
  verdict sentence), closes with a `## Phase verdict` table (all five PROVEN, with two explicit
  non-breaching qualifications carried forward rather than smoothed away) and a phase-wide
  `## Executed versus skipped` list.
- SC#2 measured directly, live, in this plan's own worktree: `typsphinx.__version__` → `0.7.0`;
  `pyproject.toml:7` → `version = "0.7.0"`; `README.md:317` → `Stable (v0.7.0)`; `uv.lock`'s
  `typsphinx` self-entry → `0.7.0`; `CHANGELOG.md:10` → `## [0.7.0] - 2026-08-03`; tail link block
  → `[0.7.0]:` at line 918 and `[Unreleased]:` advanced to `v0.7.0...HEAD` at line 935.
- SC#5's fence proven by two independent, timestamped observations: observation 1
  (2026-08-03T12:12:29Z, in `41-RELEASE-EVIDENCE.md`) and observation 2 (2026-08-03T12:15:13Z, in
  `41-HANDOFF.md`, 2m44s later) — both `git tag -l v0.7.0` and `git ls-remote --tags origin v0.7.0`
  empty on every probe, exit 0 each time.
- `41-HANDOFF.md` created: restates REL-04/REL-05 verbatim, maps all five success criteria to their
  discharging plan/evidence file, then a 7-item checklist (merge → tag → `release.yml` run →
  translations-repo second tag → RTD confirmation → REQUIREMENTS.md flip with the known
  `phase.complete` auto-flip hazard named → filing the two resolved todos), each item with an
  explicit Owner and Ordering; a `Not done in this phase, by design` list of every excluded
  destructive action; and a D-14 section naming all four todos deferred to v0.7.1+ with reasons.

## Task Commits

Each task was committed atomically:

1. **Task 1: Roll every success criterion up and take the first fence observation** - `af90ff1` (docs)
2. **Task 2: Write the publish handoff checklist and take the second fence observation** - `ba43af5` (docs)

_No TDD tasks in this plan — both tasks are documentation roll-up/measurement, not code._

## Files Created/Modified

- `.planning/phases/41-v0-7-0-release-automation-release-prep/41-RELEASE-EVIDENCE.md` - the SC#1-SC#5
  roll-up (created, not named `41-VERIFICATION.md` per the reserved-filename hazard)
- `.planning/phases/41-v0-7-0-release-automation-release-prep/41-HANDOFF.md` - the standalone
  publish checklist for `/gsd-complete-milestone` (created)

## Decisions Made

- SC#2 is measured directly in this plan rather than cited, because no sibling evidence file already
  carries a live re-run of these specific version-literal transcripts — this is the one criterion
  this roll-up plan owns outright.
- Both of `41-SC4-INVARIANTS.md`'s stated qualifications (the dev-only `pillow` addition under
  Invariant 1; the scope limit to only the 3 single-hit handlers under Invariant 3) are quoted into
  the roll-up's `## Phase verdict` table as explicit qualifications on an otherwise-PROVEN row,
  rather than either upgraded to an unqualified pass or downgraded to PARTIAL — both would misstate
  what the sibling file itself recorded.
- The handoff's checklist item 7 (filing the two resolved todos) is deliberately grouped after item 6
  (the REQUIREMENTS.md flip) rather than treated as independent administrative work, because both
  describe the same close-side "make the record match reality" action for REL-04 and D-12.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' automated verify blocks passed on the first
run; no sibling gap, skip, or NOT MET verdict was found anywhere in the six sibling evidence files
read for this roll-up, so no PARTIAL/NOT PROVEN/OPEN row was needed in the phase verdict table
beyond the two explicit qualifications already recorded in `41-SC4-INVARIANTS.md` itself (both
carried forward verbatim, not newly discovered by this plan).

**Out-of-scope observation, not fixed (per the scope-boundary rule):** the pending todo
`.planning/todos/pending/2026-07-29-project-md-unterminated-html-comments.md` remains in
`todos/pending/` even though plan 41-03 already terminated the two PROJECT.md HTML comments it
describes. This is consistent with `41-CONTEXT.md` D-13 (which scoped only the code fix, not this
specific todo's filing) and with `STATE.md`'s own record that this todo was never promoted into
v0.7.0 scope at the v0.6.5 close (unlike the two todos that were promoted, MATH-02 and REL-04) — it
is not a gap this plan's checklist needed to name, and this plan made no change to it.

## Issues Encountered

None. The worktree's own `.venv/bin/ruff` entry point (installed fresh by this plan's own
`uv sync --extra dev` run) worked directly with no NixOS dynamic-linker patch needed — unlike a
prior sibling plan's (41-05's) recorded shim requirement, this worktree's `uv sync` produced a
working native binary without a `patchelf` step.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 41 is fully evidenced and closed on the prep side: all five ROADMAP success criteria are
PROVEN (with two explicit, non-breaching qualifications carried forward, never smoothed over), and
`41-HANDOFF.md` is a standalone, self-contained checklist `/gsd-complete-milestone` can execute
without re-reading this phase's discussion history. `.planning/REQUIREMENTS.md` is confirmed
untouched (`git diff --name-only -- .planning/REQUIREMENTS.md` empty over both this plan's commits)
— REL-04 and REL-05 both remain Pending, exactly as this phase's own prohibitions require, until
`/gsd-complete-milestone` runs the checklist this plan wrote.

No blockers. The next action for this milestone is `/gsd-complete-milestone` itself, following
`41-HANDOFF.md`'s 7-item checklist in order.

---
*Phase: 41-v0-7-0-release-automation-release-prep*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `.planning/phases/41-v0-7-0-release-automation-release-prep/41-RELEASE-EVIDENCE.md`
- FOUND: `.planning/phases/41-v0-7-0-release-automation-release-prep/41-HANDOFF.md`
- FOUND: `.planning/phases/41-v0-7-0-release-automation-release-prep/41-07-SUMMARY.md`
- FOUND commit `af90ff1` (Task 1: roll-up + observation 1)
- FOUND commit `ba43af5` (Task 2: handoff checklist + observation 2)
