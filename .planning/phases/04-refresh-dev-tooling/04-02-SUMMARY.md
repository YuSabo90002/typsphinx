---
phase: 04-refresh-dev-tooling
plan: 02
subsystem: infra
tags: [github-actions, ci, workflows, node20, node24, hosted-runner]

# Dependency graph
requires:
  - phase: 04-refresh-dev-tooling (plan 01)
    provides: dev-tool floor+ceiling bounds (pyproject.toml + tox.ini + uv.lock), no overlap with workflow files
provides:
  - actions/upload-artifact bumped v5->v7 (node24) across ci.yml (x4), docs.yml (x2), release.yml (x1)
  - actions/download-artifact bumped v6->v8 (node24) across release.yml (x3)
  - Runtime confirmation (action.yml runs.using) for all 6 previously-scoped actions plus the 3 A2 straggler actions
  - A recorded, tracked/deferred TOOL-02 finding: softprops/action-gh-release@v2 still declares node20 (v3 exists and is node24)
affects: [phase-04-plan-03, phase-04-plan-04, phase-05-durability-guardrails]

# Tech tracking
tech-stack:
  added: []
  patterns: [uniform multi-file same-string version-tag bump (Phase 3 Task 3 precedent), runtime-verify via raw.githubusercontent.com action.yml grep]

key-files:
  created: []
  modified:
    - .github/workflows/ci.yml
    - .github/workflows/docs.yml
    - .github/workflows/release.yml

key-decisions:
  - "Bumped only actions/upload-artifact and actions/download-artifact tags; left checkout@v6, setup-python@v6, setup-uv@v7, codecov-action@v5 untouched per D-03 amended (already node24/composite)"
  - "Runtime-verified all 6 D-03 actions plus the 3 A2 straggler actions (pypa/gh-action-pypi-publish, peaceiris/actions-gh-pages, softprops/action-gh-release) via raw.githubusercontent.com action.yml fetch"
  - "softprops/action-gh-release@v2 declares node20 -- recorded as a tracked/deferred TOOL-02 candidate (not silently closed) per RESEARCH A2 obligation; a node24 v3 is available upstream but bumping it is out of this plan's scope"

patterns-established:
  - "Runtime-verify a GitHub Action's Node declaration by fetching its pinned tag's action.yml from raw.githubusercontent.com and grepping the runs: block, rather than trusting semver-major currency alone"

requirements-completed: [TOOL-02]

coverage:
  - id: D1
    description: "actions/upload-artifact bumped @v5->@v7 uniformly across ci.yml (4), docs.yml (2), release.yml (1); actions/download-artifact bumped @v6->@v8 across release.yml (3); occurrence-count conservation confirms no stale v5/v6 pin left behind"
    requirement: "TOOL-02"
    verification:
      - kind: other
        ref: "grep -c 'actions/upload-artifact@v7' .github/workflows/{ci,docs,release}.yml == 4/2/1; grep -c 'actions/download-artifact@v8' .github/workflows/release.yml == 3"
        status: pass
    human_judgment: false
  - id: D2
    description: "Runtime confirmation that both bumped actions declare node24, the four unchanged actions remain node24/composite, and the three A2 straggler actions are runtime-checked with results recorded (including the node20 softprops finding, explicitly flagged not silently closed)"
    requirement: "TOOL-02"
    verification:
      - kind: other
        ref: "curl raw.githubusercontent.com/actions/upload-artifact/v7/action.yml + download-artifact/v8/action.yml -> both node24 (exit 0 per plan's automated verify)"
        status: pass
    human_judgment: true
    rationale: "The softprops/action-gh-release@v2 node20 finding is a judgment call for whether/when to open a follow-up bump (out of this plan's scope, tracked as deferred) -- a human should confirm the deferral is acceptable rather than an automated pass/fail gate deciding it."

duration: 8min
completed: 2026-07-05
status: complete
---

# Phase 4 Plan 2: GitHub Actions Node-24 Artifact Bump Summary

**Bumped actions/upload-artifact@v5->v7 and actions/download-artifact@v6->v8 across ci.yml/docs.yml/release.yml (10 occurrences), runtime-verified all 9 actions in the six workflows via action.yml, and recorded softprops/action-gh-release@v2's node20 declaration as a tracked/deferred TOOL-02 straggler.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-07-04T15:53:00Z
- **Completed:** 2026-07-04T16:01:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Every `actions/upload-artifact` pin across the three workflows is now `@v7` (node24): ci.yml x4, docs.yml x2, release.yml x1.
- Every `actions/download-artifact` pin in release.yml is now `@v8` (node24): x3.
- Occurrence-count conservation confirmed (grep totals unchanged pre/post) -- no stale v5/v6 pin left behind, none accidentally duplicated.
- Runtime-verified `runs.using` for all 6 D-03-scoped actions (upload-artifact@v7, download-artifact@v8, checkout@v6, setup-python@v6, setup-uv@v7, codecov-action@v5) -- all node24 or composite.
- Runtime-verified the 3 A2 straggler actions not checked during research: pypa/gh-action-pypi-publish@release/v1 (composite), peaceiris/actions-gh-pages@v4 (node24), softprops/action-gh-release@v2 (**node20** -- flagged, see Deviations/Issues below).

## Task Commits

Each task was committed atomically:

1. **Task 1: Bump upload-artifact and download-artifact tags uniformly across the three workflows** - `0527965` (feat)
2. **Task 2: Runtime-verify bumped + unchanged actions and check the three A2 stragglers** - no code commit (verification-only task; findings recorded in this SUMMARY, plan-metadata commit follows)

**Plan metadata:** committed separately per `<final_commit>` step.

_Note: Task 2 produced no file changes to the workflow surfaces -- its "commit" is this SUMMARY.md itself, landed as part of the plan-metadata commit._

## Files Created/Modified
- `.github/workflows/ci.yml` - 4x `actions/upload-artifact@v5` -> `@v7` (lines 47, 126, 155, 188)
- `.github/workflows/docs.yml` - 2x `actions/upload-artifact@v5` -> `@v7` (lines 46, 52)
- `.github/workflows/release.yml` - 1x `actions/upload-artifact@v5` -> `@v7` (line 100); 3x `actions/download-artifact@v6` -> `@v8` (lines 116, 137, 206)

## Decisions Made
- Confirmed via `raw.githubusercontent.com/<action>/<tag>/action.yml` fetch (not semver-major alone) that `upload-artifact@v7` and `download-artifact@v8` both declare `runs.using: node24`, matching Research assumption A1/A2 and D-03 amended.
- Left `actions/checkout@v6`, `actions/setup-python@v6`, `astral-sh/setup-uv@v7`, `codecov/codecov-action@v5` untouched -- all four runtime-confirmed node24 (checkout, setup-python, setup-uv) or composite (codecov-action), matching D-03 amended's exact six-action split.
- `softprops/action-gh-release@v2` (used in both `docs.yml` line 67 and `release.yml` lines 177/212) declares `runs.using: node20`. Per the plan's explicit instruction ("if any of the three still declares node20, record it explicitly as a tracked/deferred TOOL-02 item... do NOT silently close the phase"), this is recorded here as a **tracked/deferred finding**, not fixed in this plan (bumping it is out of this plan's declared scope -- only upload-artifact/download-artifact tags were authorized for edit). Checked upstream: `softprops/action-gh-release@v3` exists and declares `node24` -- a viable follow-up bump target for a future plan/phase (candidate: Phase 5 durability-guardrails, alongside the already-deferred SHA-pinning work).

## Deviations from Plan

None - plan executed exactly as written. Task 1's file edits and Task 2's runtime verification both completed per the plan's `<action>` and `<acceptance_criteria>` with no auto-fixes required.

## Issues Encountered

**softprops/action-gh-release@v2 node20 straggler (RESEARCH A2, plan Task 2 finding):**
- **What:** `curl -sf https://raw.githubusercontent.com/softprops/action-gh-release/v2/action.yml | grep -A2 'runs:'` returns `using: "node20"` -- this action is NOT covered by the D-03/D-03-amended six-action scope (it is a release/docs-only action explicitly called out in RESEARCH assumption A2 as unchecked).
- **Where used:** `.github/workflows/docs.yml` line 67 and `.github/workflows/release.yml` lines 177, 212.
- **Resolution:** Per the plan's explicit non-closure instruction, this is recorded here as a tracked/deferred TOOL-02 item, NOT silently closed and NOT fixed in this plan (out of Task 1's declared scope, which only authorized upload-artifact/download-artifact edits). Upstream `@v3` is confirmed `node24` and is the natural bump target for whichever future plan/phase picks this up (candidate: Phase 5 durability-guardrails).
- **Other two A2 stragglers cleared:** `pypa/gh-action-pypi-publish@release/v1` runs as `composite` (not directly node-versioned, no deprecation exposure); `peaceiris/actions-gh-pages@v4` runs as `node24` (current).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- ci.yml/docs.yml artifact-action bumps are ready for the plan 04's D-05 push->observe CI gate (this plan does not itself push/observe -- that is a later plan in this phase per the roadmap).
- release.yml only fires on a tag push and is not exercised by the D-05 PR gate; its upload/download-artifact bumps carry the same node24 runtime proof as ci.yml/docs.yml (Assumption A1 risk: low, per plan `<verification>`).
- A tracked/deferred candidate exists for a future phase: bump `softprops/action-gh-release@v2` -> `@v3` (node20 -> node24) in `docs.yml` and `release.yml`. Recommend Phase 5 (durability guardrails) as the natural home, alongside the already-deferred SHA-pinning work.

---
*Phase: 04-refresh-dev-tooling*
*Completed: 2026-07-05*

## Self-Check: PASSED
- FOUND: .planning/phases/04-refresh-dev-tooling/04-02-SUMMARY.md
- FOUND: 0527965 (Task 1 commit)
