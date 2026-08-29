---
phase: 61-v0-9-1-release-prep-prep-only
plan: 02
subsystem: release-prep
tags: [changelog, release-fence, requirements-checksum, sc4-invariants, api-coverage]

# Dependency graph
requires:
  - phase: 61 (self, wave 1)
    provides: nothing — this is the phase's first plan, wave 1, depends_on []
provides:
  - a phase-head sha256/line-count/timestamp/PHASE_BASE_SHA guard over .planning/REQUIREMENTS.md, protecting REL-09's unchecked state against the five-consecutive-closes phase.complete auto-flip
  - fence observation 1 of 2 (tag/publish/workflow probes, each with a positive control) proving no irreversible action has occurred, plus a fresh v0.9.0-tag-anchored milestone measurement
  - a written resolution of RESEARCH.md's open question: the milestone-invariant sweep is deliberately not run this phase
  - a reasoned external-API coverage declaration recording the plan-time detector's negative result
affects: [61-04 (reads PHASE_BASE_SHA and appends observation 2), 61-HANDOFF.md (reproduces the post-close reversion protocol)]

# Actuals (#2632)
actuals:
  tokens: 32000
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns: [checksum-guard closeout pattern (57-CLOSEOUT-GUARD.md lineage), positive-controlled fence probes, milestone-invariant-sweep skip decision written in prose]

key-files:
  created:
    - .planning/phases/61-v0-9-1-release-prep-prep-only/61-CLOSEOUT-GUARD.md
    - .planning/phases/61-v0-9-1-release-prep-prep-only/61-SC4-INVARIANTS.md
    - .planning/phases/61-v0-9-1-release-prep-prep-only/COVERAGE.md
  modified: []

key-decisions:
  - "Re-ran the sha256/wc/git rev-parse commands live rather than transcribing 61-PATTERNS.md's research-time values; both matched byte-for-byte, confirming no drift between planning and execution."
  - "Resolved RESEARCH.md Open Question 1 in writing: D-10's four-item literal reading does not name the dependency/@preview/config-value milestone-invariant sweep, and since this phase authors no ### Verified section, the sweep is deliberately skipped rather than run unexamined."
  - "Ran the api-coverage detector CLI directly against 61-CONTEXT.md to reproduce the plan-time result ({\"detected\":false,\"signals\":[]}) rather than assuming it, following the Phase 57/60 COVERAGE.md precedent."

patterns-established:
  - "Positive-controlled fence probe: every network-dependent probe (git ls-remote, gh release list) derives a proof-of-reachability count from the SAME fetched listing as its negative assertion, so an unreachable source cannot pass vacuously."

requirements-completed: []  # REL-09 is cited for coverage purposes only per D-08 — this plan does NOT close it; it stays unchecked and unmet, carried forward to v0.9.2.

coverage:
  - id: D1
    description: "Phase-head REQUIREMENTS.md checksum guard recorded before any other plan ran, with PHASE_BASE_SHA and the three verbatim REL-09-bearing lines"
    requirement: "REL-09"
    verification:
      - kind: other
        ref: "61-CLOSEOUT-GUARD.md's own re-run: sha256sum, wc -l, git rev-parse HEAD, grep -n 'REL-09' all matched the file's recorded Baseline at verification time"
        status: pass
    human_judgment: false
  - id: D2
    description: "Fence observation 1 of 2: local/remote tag probes, publish probe, release-workflow probe, each carrying a positive control proving the source was reached"
    requirement: "REL-09"
    verification:
      - kind: other
        ref: "task 2 <verify> automated command block: git tag -l, git ls-remote --tags origin counts, gh release list Latest-marker count, gh run list — all re-run and matched at verification time"
        status: pass
    human_judgment: false
  - id: D3
    description: "Milestone-invariant-sweep open question resolved in writing (deliberately not run this phase)"
    verification: []
    human_judgment: true
    rationale: "This is a documented reasoning decision (whether D-10's literal four-item fence reading requires the dependency/@preview/config-value sweep), not a mechanically-verifiable output — a human should confirm the written rationale is sound, not just that the section exists."
  - id: D4
    description: "External-API coverage declaration recording the plan-time detector's negative result"
    requirement: null
    verification:
      - kind: other
        ref: "task 3 <verify> automated command block: grep for 'detected'/'signals', line count >= 12, git status --porcelain over typsphinx/ tests/ CHANGELOG.md empty — all passed"
        status: pass
    human_judgment: false

# Metrics
duration: 5min
completed: 2026-08-29
status: complete
---

# Phase 61 Plan 02: Phase-Head Closeout Guard, Fence Observation 1, and Coverage Declaration Summary

**Recorded the REQUIREMENTS.md checksum guard, PHASE_BASE_SHA, and the first of two separated SC#4 fence observations — all before any other plan in Phase 61 had a chance to run — plus a reasoned external-API coverage declaration.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-08-29T15:04:23Z
- **Completed:** 2026-08-29T15:08:49Z
- **Tasks:** 3
- **Files modified:** 3 (all newly created)

## Accomplishments
- `61-CLOSEOUT-GUARD.md` records the phase-head sha256 (`4682f8cd...506d531e1`), line count (258), UTC timestamp, and PHASE_BASE_SHA (`5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41`) for `.planning/REQUIREMENTS.md`, together with the three verbatim REL-09-bearing lines and both a close-time and a post-`phase.complete` detection-and-reversion protocol — the detector for the auto-flip that has fired at five consecutive release-prep closes.
- `61-SC4-INVARIANTS.md` records fence observation 1 of 2: a local tag probe, a positive-controlled unfiltered remote tag listing, a positive-controlled `gh release list`, and a `gh run list --workflow=release.yml` probe — all confirming the fence holds (v0.9.0 still latest, no v0.9.1 tag or release anywhere) — plus a fresh v0.9.0-tag-anchored milestone measurement (137 commits, 23 files / +3011/−72 excluding `.planning/`).
- `COVERAGE.md` records the plan-time api-coverage detector's verbatim negative result (`{"detected":false,"signals":[]}`) and explains why this phase's `gh`-dense plan prose is a false-positive risk at seal time, following the Phase 57/60 precedent.

## Task Commits

Each task was committed atomically:

1. **Task 1: Record the phase-head REQUIREMENTS.md closeout guard and the phase base SHA** - `4fd89d92` (docs)
2. **Task 2: Record fence observation 1 of 2 with positive controls, and resolve the milestone-invariant-sweep question in writing** - `333de2dc` (docs)
3. **Task 3: Write the external-API coverage declaration** - `e9a3fa4e` (docs)

**Plan metadata:** committed separately per the worktree-mode contract (SUMMARY.md + REQUIREMENTS.md only; STATE.md/ROADMAP.md owned by the orchestrator).

## Files Created/Modified
- `.planning/phases/61-v0-9-1-release-prep-prep-only/61-CLOSEOUT-GUARD.md` - phase-head REQUIREMENTS.md checksum guard, PHASE_BASE_SHA, close-time and post-close reversion protocols
- `.planning/phases/61-v0-9-1-release-prep-prep-only/61-SC4-INVARIANTS.md` - fence observation 1 of 2, fresh v0.9.0 milestone anchor, written sweep-skip decision
- `.planning/phases/61-v0-9-1-release-prep-prep-only/COVERAGE.md` - external-API coverage declaration

## Decisions Made
- Re-ran every measurement command live rather than transcribing research-time values; all matched byte-for-byte (checksum, line count, and the `git ls-remote`/`gh release list` fence probes all agreed with the pre-execution research figures), confirming no drift occurred between planning and execution.
- Resolved RESEARCH.md's Open Question 1 in writing: because D-10's literal four-item fence reading does not name the dependency/`@preview`/config-value milestone-invariant sweep, and this phase authors no `### Verified` CHANGELOG section, the sweep is deliberately not run — recorded as a decision with reasoning, not left as a silent absence.
- Reproduced the plan-time api-coverage detector result by running the detector CLI directly against `61-CONTEXT.md` (the phase-scope document that predates any plan), rather than assuming or copying a value — the live run confirmed `{"detected":false,"signals":[]}`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. All three tasks' `<verify>` automated command blocks and `<acceptance_criteria>` were run and passed on the first attempt.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 61-04 can now read `PHASE_BASE_SHA` (`5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41`) from `61-CLOSEOUT-GUARD.md` to scope its `typsphinx/` diff, and appends fence observation 2 of 2 under `61-SC4-INVARIANTS.md`'s `## Handoff to observation 2` section.
- `61-HANDOFF.md` (a later plan) reproduces this plan's post-`phase.complete` detection-and-reversion protocol verbatim per `61-CLOSEOUT-GUARD.md`'s own instruction.
- No blockers or concerns for downstream plans in this phase.

---
*Phase: 61-v0-9-1-release-prep-prep-only*
*Completed: 2026-08-29*
