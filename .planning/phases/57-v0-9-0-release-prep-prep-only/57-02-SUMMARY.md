---
phase: 57-v0-9-0-release-prep-prep-only
plan: 02
subsystem: infra
tags: [ci, github-actions, gh-cli, workflow-dispatch, cross-platform]

# Dependency graph
requires: []
provides:
  - "D-12 run 1 (pre-bump CI check run) dispatched against the untouched phase-head tip and recorded in full"
  - ".planning/phases/57-v0-9-0-release-prep-prep-only/57-CI-EVIDENCE.md with Run 1 fully transcribed and a Run 2 placeholder for plan 57-05"
  - "WINDOWS.md ledger entry 9 — a real, reproducible Windows-only path-separator defect in tests/test_templates_path_collision_gate.py, discovered by this dispatch"
affects: [57-05]

# Actuals (#2632)
actuals:
  tokens: 3000
  tasks: 2
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-CI-EVIDENCE.md
  modified:
    - .planning/WINDOWS.md

key-decisions:
  - "Task 1 pushed the phase-head tip before writing any local file, so the dispatched SHA is provably the untouched phase-head tree (pyproject.toml still reads 0.8.0, CHANGELOG.md has zero '## [0.9.0]' headings)"
  - "The discovered windows-latest failure (test_templates_path_collision_gate.py, path-separator mismatch) is filed to WINDOWS.md rather than fixed, per SCOPE BOUNDARY — the file sits outside this plan's declared files_modified"

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "D-12 run 1 dispatched against the phase-head tip (78bd595d), pushed via plain fast-forward, all 12 jobs read and recorded"
    verification:
      - kind: other
        ref: "gh run view 31956166848 --json jobs (live CI dispatch)"
        status: pass
    human_judgment: false
  - id: D2
    description: "57-CI-EVIDENCE.md written with Run 1 fully transcribed (pre-dispatch confirmation, branch position, pushed SHA, dispatch, job table, disposition) and a Run 2 placeholder"
    verification:
      - kind: other
        ref: "test -f .planning/phases/57-v0-9-0-release-prep-prep-only/57-CI-EVIDENCE.md && grep checks per plan <verify>"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-08-16
status: complete
---

# Phase 57 Plan 02: D-12 Pre-Bump CI Check Run Summary

**Dispatched `ci.yml` against the untouched phase-head tip (78bd595d) and recorded a real, reproducible Windows-only path-separator defect in Phase 54.1's `templates_path` collision-refusal test — 10 of 12 jobs green, both `windows-latest` lanes failing identically.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-08-16T15:46:33Z
- **Tasks:** 2
- **Files modified:** 2 (`57-CI-EVIDENCE.md` created, `WINDOWS.md` updated)

## Accomplishments

- Confirmed the pre-bump tree (`pyproject.toml` version `0.8.0`, zero `## [0.9.0]` CHANGELOG headings) and D-13's sequencing precondition (`uv lock --check` exit 0; 10 `--locked` steps measured live across the four workflow files) before touching anything.
- Re-measured the branch position live (195 commits ahead of `origin/gsd/v0.9.0-per-document-templates`, fast-forward-ok) rather than transcribing any of the three stale figures in CONTEXT/RESEARCH/plan frontmatter.
- Pushed the phase-head tip as a plain fast-forward (`35ee8a0e..78bd595d`) and dispatched `ci.yml` by hand (`workflow_dispatch` has no push trigger on this branch), matching the dispatched run by `headSha`.
- Read every one of the 12 jobs' conclusions: `Build Package`, both `Integration Test` lanes, `Type Check`, `Lint and Format Check`, `Code Coverage`, and 4 of 6 OS/Python test-matrix lanes are `success`; both `windows-latest` lanes (Python 3.12 and 3.13) fail on the identical assertion.
- Root-caused the failure by reading the actual job log: `test_templates_path_collision_gate.py::TestMultiRelationAggregationGate::test_multi_relation_each_key_names_own_bundle_dir_and_own_entry` asserts a forward-slash substring (`'_templates/nested'`) against a message built with the native Windows backslash separator — giving Phases 54/54.1/55/56 their first Windows exposure and finding a real defect the way D-12 predicted.
- Filed the defect to `.planning/WINDOWS.md` (entry 9, `kind: todo`, `phase: 57`) rather than fixing it — the affected test file is outside this plan's declared `files_modified` scope.

## Task Commits

Both tasks landed in a single combined commit, since Task 1 makes only remote changes (a branch push and a workflow dispatch — no local file diff) and Task 2 is the sole task that writes to the working tree:

1. **Task 1 + Task 2: Dispatch D-12 run 1 and write the evidence record** - `131e0d1e` (docs)

**Plan metadata:** not applicable — this is a worktree-isolated executor; the orchestrator commits shared STATE.md/ROADMAP.md updates after the wave merges.

## Files Created/Modified

- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-CI-EVIDENCE.md` - New file. Carries Run 1 (pre-bump check run) fully transcribed per the plan's required section structure, plus a `## Run 2 — post-bump authority run` placeholder for plan 57-05.
- `.planning/WINDOWS.md` - Ledger entry 9 appended: the Windows-only path-separator defect discovered by this dispatch, `status: open`.

## Decisions Made

- **Push before write.** Task 1's action pushes the phase-head tip to `origin` and dispatches `ci.yml` *before* any local file in this worktree is touched, exactly as the plan specifies — this is what makes the dispatched SHA provably the untouched phase-head tree rather than a tree already carrying this phase's own evidence-file commit.
- **Do not fix the discovered defect.** The failing test (`tests/test_templates_path_collision_gate.py`) sits outside this plan's `files_modified` (`57-CI-EVIDENCE.md` only). Per the SCOPE BOUNDARY rule, the defect is filed to the cross-phase ledger and reported honestly in the evidence file's Disposition section rather than silently fixed or papered over.
- **Live re-measurement over transcription.** Every branch-position and `--locked`-count figure in the evidence file was measured fresh at execution time (195 commits ahead, 10 `--locked` steps) rather than copied from `57-CONTEXT.md` (188 / 11) or `57-RESEARCH.md` (190 / 10), per the plan's `must_haves.truths`.

## Deviations from Plan

None — plan executed exactly as written. The CI dispatch reporting `failure` overall (2 of 12 jobs) is not a deviation from the plan: the plan's own `<action>` and `<acceptance_criteria>` explicitly anticipate and require this exact honest-failure-reporting path ("If a job fails, that failure belongs to those phases, NOT to this phase's bump... Report it with its log excerpt and escalate; do not paper over it").

## Issues Encountered

None beyond the CI job failure itself, which is documented above as the expected/handled outcome of this check run, not an execution problem.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `57-CI-EVIDENCE.md` exists with Run 1 complete; plan `57-05` can append Run 2 (the post-bump authority run) to the same file once the version bump (57-01), CHANGELOG (57-03), and migration guide (57-04) plans have merged.
- **Blocker for 57-05 to be aware of, not blocking this plan:** the Windows-only `test_templates_path_collision_gate.py` path-separator defect (WINDOWS.md entry 9) will reproduce identically on plan 57-05's post-bump dispatch unless a fix lands first — this plan's own action explicitly instructs "do not proceed to plan 57-05's authority dispatch expecting it to pass." That decision belongs to the owner or a future plan authorized to touch `tests/`, not to this plan.
- No irreversible action was taken: no `v0.9.0` tag (local or remote), no `release.yml` dispatch, no pull request, `.github/` and `typsphinx/` both show zero diff from this plan.

## Self-Check: PASSED

- FOUND: `.planning/phases/57-v0-9-0-release-prep-prep-only/57-CI-EVIDENCE.md`
- FOUND: `.planning/phases/57-v0-9-0-release-prep-prep-only/57-02-SUMMARY.md`
- FOUND commit: `131e0d1e` (evidence + ledger)
- FOUND commit: `d91f6969` (this summary)

---
*Phase: 57-v0-9-0-release-prep-prep-only*
*Completed: 2026-08-16*
