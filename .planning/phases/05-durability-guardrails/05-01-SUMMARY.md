---
phase: 05-durability-guardrails
plan: 01
subsystem: infra
tags: [github-actions, uv, ci-cd, workflow-yaml]

requires:
  - phase: 04-refresh-dev-tooling
    provides: node24 artifact-action bumps (upload-artifact@v7, download-artifact@v8) and the tracked softprops@v2 node20 straggler
provides:
  - "--locked flag on all 9 `uv sync` call sites across ci.yml/docs.yml/release.yml (DUR-01 anti-drift gate)"
  - "softprops/action-gh-release bumped @v2 -> @v3 at both call sites (D-11 node24 hardening)"
affects: [05-02, 05-03, 05-04]

tech-stack:
  added: []
  patterns:
    - "uv sync --locked as the standard anti-drift gate for all CI dependency installs"

key-files:
  created: []
  modified:
    - .github/workflows/ci.yml
    - .github/workflows/docs.yml
    - .github/workflows/release.yml

key-decisions:
  - "Isolated Task 1 and Task 2 commits by temporarily reverting the softprops @v3 edit before committing Task 1, then reapplying it for Task 2 — both tasks touch docs.yml/release.yml so this kept commits atomic per-task."

patterns-established:
  - "uv sync --locked: fail the build on uv.lock <-> pyproject.toml desync, at every install site in every workflow"

requirements-completed: [DUR-01]

coverage:
  - id: D1
    description: "All 9 uv sync sites (ci.yml x6, docs.yml x1, release.yml x2) carry --locked, existing --extra flags preserved"
    requirement: DUR-01
    verification:
      - kind: other
        ref: "grep -n 'uv sync' .github/workflows/*.yml | grep -v -- '--locked' (empty output)"
        status: pass
    human_judgment: false
  - id: D2
    description: "softprops/action-gh-release bumped @v2 -> @v3 at docs.yml:67 and release.yml:177, with: blocks unchanged"
    verification:
      - kind: other
        ref: "grep -rn 'softprops/action-gh-release@v2' .github/workflows/ (empty) + grep -rn '@v3' (2 matches)"
        status: pass
    human_judgment: true
    rationale: "Both edited steps are tag-gated (docs.yml on refs/tags/v*, release.yml on tag push/workflow_dispatch) — a normal PR push->observe run does not exercise the runtime behavior of the new action version. Static grep confirms the text swap only; full runtime confirmation is explicitly deferred to plan 05-04 per the plan's Pitfall 3 note."

duration: 12min
completed: 2026-07-05
status: complete
---

# Phase 5 Plan 1: Locked uv sync + softprops v3 bump Summary

**Appended `--locked` to all 9 `uv sync` invocations across ci.yml/docs.yml/release.yml (closing DUR-01) and bumped `softprops/action-gh-release@v2` to `@v3` at both call sites (D-11 node24 hardening) — pure mechanical YAML edits, no structural changes.**

## Performance

- **Duration:** ~12 min
- **Completed:** 2026-07-05
- **Tasks:** 2/2 completed
- **Files modified:** 3 (.github/workflows/ci.yml, docs.yml, release.yml)

## Accomplishments
- Every `uv sync` call site in the repo's three workflow files now fails the build when `uv.lock` and `pyproject.toml` disagree — the core anti-drift gate this milestone exists to install (D-01).
- The bare `uv sync` in ci.yml's integration job (line 179, no `--extra` flag) was correctly caught — it would not have been found by a naive `--extra dev` search (RESEARCH Pitfall 1).
- Both `softprops/action-gh-release@v2` node20 stragglers (tracked since Phase 4) are now `@v3`, matching the repo's moving-major-tag convention and continuing the node24 migration ahead of GitHub's 2026-09-16 hosted-runner node20 removal.

## Task Commits

Each task was committed atomically:

1. **Task 1: Append --locked to all 9 uv sync call sites (DUR-01 / D-01, D-02)** - `5e9a643` (feat)
2. **Task 2: Bump softprops/action-gh-release @v2 -> @v3 at both sites (D-11)** - `8e4b4df` (feat)

_Note: Task 1 and Task 2 both touch docs.yml and release.yml. To keep each commit scoped to exactly one task, the softprops @v3 edit was temporarily reverted to @v2 before staging/committing Task 1, then reapplied and committed as Task 2. Both files' final on-disk state matches the plan's specification._

## Files Created/Modified
- `.github/workflows/ci.yml` - 6 `uv sync` sites gained `--locked` (5x `--extra dev --locked`, 1x bare `--locked`)
- `.github/workflows/docs.yml` - 1 `uv sync` site gained `--locked` (line 31); softprops `@v2`->`@v3` (line 67)
- `.github/workflows/release.yml` - 2 `uv sync` sites gained `--locked` (lines 36, 93); softprops `@v2`->`@v3` (line 177)

## Decisions Made
- Isolated the two tasks' commits by temporarily reverting Task 2's softprops edit before Task 1's commit, then reapplying — since both plan tasks touch the same two files, this was necessary to keep each commit's diff scoped to exactly one task rather than mixing concerns.

## Deviations from Plan

None — plan executed exactly as written. All line numbers matched the plan's pre-verified inventory with zero drift (confirmed via fresh `grep -n "uv sync"` and `grep -n "softprops"` immediately before editing).

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plans 05-02 and 05-03 (dependabot grouping, drift.yml) can proceed independently — no shared file conflicts with this plan's edits.
- Plan 05-04 owns the CI-visible confirmation gate: a PR push->observe run will exercise the `--locked` gate directly, but the softprops `@v3` runtime behavior remains unconfirmed until a real tag push or `workflow_dispatch` (release.yml only) — this is explicitly deferred per the plan's Pitfall 3 note, not a gap in this plan's scope.
- No blockers.

## Self-Check: PASSED

- FOUND: .planning/phases/05-durability-guardrails/05-01-SUMMARY.md
- FOUND: 5e9a643 (Task 1 commit)
- FOUND: 8e4b4df (Task 2 commit)
- FOUND: c7e712e (SUMMARY commit)
