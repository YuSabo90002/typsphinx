---
phase: 73-v0-9-5-close-prep-prep-only-unpublished
plan: 05
subsystem: release-prep
tags: [git, merge-tree, uv, ruff, black, github-api, dependabot, pre-flight]

# Dependency graph
requires:
  - phase: 73-v0-9-5-close-prep-prep-only-unpublished (73-01, 73-02)
    provides: the CHANGELOG's ### Added / ### Changed / ### Fixed region and MILESTONE_BASE in 73-SC1-INVARIANTS.md
provides:
  - A non-committing trial merge of origin/main into the milestone branch, measured live and reproducible
  - Proof that the merged uv.lock is valid and the merged tree lints cleanly at the merged ruff/black versions
  - main's strict branch protection and required contexts, cross-checked against Phase 72's base reading
  - The #143/#145 merge-commit precedent and a live, untouched census of Dependabot PRs #146-#150
affects: [73-HANDOFF.md, /gsd-complete-milestone's branch-update and merge steps]

# Actuals (#2632)
actuals:
  tokens: 5324
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns: ["non-committing trial merge via git merge-tree --write-tree", "scratch-directory git archive + uv --directory for isolated lock/lint checks"]

key-files:
  created: [".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-PREFLIGHT-EVIDENCE.md"]
  modified: []

key-decisions:
  - "main moved during this phase's own execution window: all five Dependabot PRs (#146-#150) merged between planning (2026-09-14) and this plan's execution (2026-09-16), landing a ruff 0.16.6 -> 0.16.7 bump on origin/main. This is exactly D-07's anticipated case, caught live by the trial merge rather than assumed from planning-time state."
  - "TRIAL_IS_NOOP = no (not yes as the planning-time census expected) because main genuinely moved; the merge is still conflict-free (MERGE_RC = 0) and the merged-tree lint at the merged lock's ruff 0.16.7 is authoritative per D-07."
  - "requirements-completed: [] per D-08 — REL-14 is cited in this plan's frontmatter for coverage only; no requirement is marked complete by this plan."

requirements-completed: []

coverage:
  - id: D1
    description: "Non-committing trial merge of origin/main into the milestone branch, measured conflict-free and reproducible from its recorded inputs, with a valid merged uv.lock"
    requirement: REL-14
    verification:
      - kind: other
        ref: "git merge-tree --write-tree (twice, reproduced) + uv lock --check on a git-archive scratch copy of MERGE_TREE; re-run live by the plan's own <automated> verify block"
        status: pass
    human_judgment: false
  - id: D2
    description: "Merged-tree lint at the merged lock's ruff/black versions, main's strict protection and required contexts cross-checked against Phase 72's base reading, the #143/#145 merge-commit precedent, and a live untouched census of Dependabot PRs #146-#150"
    requirement: REL-14
    verification:
      - kind: other
        ref: "uv --directory <scratch> run --no-sync ruff check . / black --check . on a git-archive'd MERGE_TREE; gh api branches/main/protection; gh pr view 146..150; re-run live by the plan's own <automated> verify block"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-09-16
status: complete
---

# Phase 73 Plan 05: REL-14 Update-Step Pre-Flight Summary

**Non-committing trial merge of `origin/main` caught D-07's case live: all five Dependabot PRs (#146-#150) had already merged into `main` since planning, bumping `ruff` to 0.16.7 — the merge is conflict-free and the merged tree lints and locks clean at that version, so the handoff's branch-update step is now known-live rather than a no-op.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-09-16T10:13:33Z
- **Completed:** 2026-09-16T10:19:42Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments
- Measured, without committing anything, that `git merge-tree --write-tree` of this branch's HEAD against `origin/main`'s live tip is conflict-free (`MERGE_RC = 0`) and reproducible (same tree SHA on a second run) — `MERGE_TREE = 228dc64ea867e2f993b97229faf6607774ed39c6`.
- Discovered live that `main` moved during this phase's own execution: `ORIGIN_MAIN_SHA = 6e2b789922207eb72e7aef3216fdfd924dd4bcd9` differs from `MILESTONE_BASE = 098a8ff64cf008822eef9dc69f75102ded3f7bc1` — all five Dependabot PRs (#146-#150) had merged into `main` between the phase's planning census (2026-09-14) and this plan's execution (2026-09-16). `TRIAL_IS_NOOP = no`.
- Archived `MERGE_TREE`'s `pyproject.toml`/`uv.lock` into a scratch directory and confirmed `uv lock --check` exits 0; the merged `pyproject.toml:7` still reads `version = "0.9.2"`; the merged lock's `ruff` pin is `0.16.7` (bumped from this branch's own `0.16.6` by #147).
- Archived the whole `MERGE_TREE` into a second scratch directory, ran a hash-verified `uv sync --locked` from the merged `uv.lock`, and confirmed `ruff check .` and `black --check .` both exit 0 at the merged lock's `ruff` 0.16.7 — the merged-tree lint D-07 names as authoritative when `main` has moved.
- Read `main`'s branch protection live: `strict: true`, six required contexts, byte-identical to `REQUIRED_CONTEXTS_HEAD` recorded at Phase 72's base.
- Recorded the `#143`/`#145` merge-commit precedent (both merged with a merge commit, never squash/rebase) and a live census of Dependabot PRs #146-#150 — every one already `MERGED` outside this phase's own actions, with zero comments or reviews by the authenticated `gh` account on any of them.
- `TRIAL_MERGE_VERDICT = MET`. HEAD and the canonical branch ref are unmoved; `git status --porcelain` lists only this plan's own evidence file at every checkpoint; the merge-base of HEAD and `origin/main` is still exactly `MILESTONE_BASE`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — fetch, non-committing trial merge of origin/main reproduced from its inputs, and the merged lock checked in scratch** - `baad4336` (docs)
2. **Task 2: Merged-tree lint at the merged lock's versions, main's protection and merge-method precedent, and the Dependabot census recorded without acting** - `59521c57` (docs)

**Plan metadata:** SUMMARY commit follows in the same push as this file.

## Files Created/Modified
- `.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-PREFLIGHT-EVIDENCE.md` - Every fact the handoff's branch-update and merge steps depend on: trial-merge inputs/outputs, merged-lock check, merged-tree lint, main's protection, merge-method precedent, and the Dependabot census — all measured live in this worktree, nothing copied from CONTEXT.md or RESEARCH.md.

## Decisions Made
- `main` had moved by execution time (all five Dependabot PRs merged), which is D-07's anticipated case rather than the planning-time no-op expectation. The plan's own re-measurement caught this correctly: `MAIN_MOVED = yes`, `TRIAL_IS_NOOP = no`, and the merged-tree lint (rather than a same-tree assumption) is what the handoff should rely on.
- No fix was made to anything: per the plan's own instruction, a merged-tree lint failure would have been a `## FINDING` for the owner, never patched here. Both `ruff check .` and `black --check .` passed on the merged tree at `ruff` 0.16.7, so no finding was needed.

## Deviations from Plan

None - plan executed exactly as written. The plan explicitly anticipated (Task 1's `<action>` step 2 and D-07) that `main` might have moved since planning and instructed the plan to measure and record that live rather than assume the planning-time no-op — which is exactly what happened and was recorded.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The handoff (`73-HANDOFF.md`, a later plan in this phase) can now rely on: a conflict-free, non-no-op trial merge; a valid merged lock; a clean merged-tree lint at `ruff` 0.16.7; `main`'s strict protection with contexts equal to Phase 72's base reading; the `#143`/`#145` merge-commit precedent; and a live, untouched census of Dependabot PRs #146-#150 (all already merged before the milestone PR would even open — D-06's order held itself this time, since Dependabot's own rebase-and-merge cadence outpaced this phase).
- **Caveat carried forward explicitly in the evidence file:** `ORIGIN_MAIN_SHA` and `MERGE_TREE` are valid only for this moment — the handoff must re-run `git merge-tree --write-tree` immediately before any real merge, since both `HEAD` and `origin/main` are moving targets and `main` has already proven, within this very phase, that it can move between measurement and use.
- No blockers.

## Self-Check: PASSED
- `test -f .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-PREFLIGHT-EVIDENCE.md` -> FOUND
- `git log --oneline --all --grep="73-05"` -> FOUND (`baad4336`, `59521c57`, and this SUMMARY's own commit)
- Task 1's `<acceptance_criteria>` re-verified: `## Fetch and divergence` records `ORIGIN_MAIN_SHA`, `MAIN_ONLY_COMMITS`, the merge-base equal to `MILESTONE_BASE`, and `MAIN_MOVED` with the moved-main commits named — PASS. `## Trial merge` records verbatim output with `MERGE_RC = 0`, `MERGE_TREE`, `MERGE_TREE_REPRODUCED = yes`, `TRIAL_IS_NOOP`, and the re-measure caveat — PASS. `## Merged lock` records the scratch path, `LOCK_CHECK_EXIT = 0` with `LOCK_CHECK_UV_VERSION`, `MERGED_VERSION_LINE`, `MERGED_RUFF_LOCK_VERSION`, `BRANCH_RUFF_LOCK_VERSION`, `MERGED_CHANGELOG_BOLD = 6` — PASS. `## Nothing moved` shows HEAD/canonical ref unmoved, only the evidence file in `git status`, merge-base still `MILESTONE_BASE` — PASS.
- Task 2's `<acceptance_criteria>` re-verified: `## Merged-tree lint` records the locked scratch sync, `MERGED_RUFF_RUN_VERSION = MERGED_RUFF_LOCK_VERSION`, verbatim ruff/black outputs with both exits `0` — PASS. `## main protection (D-09)` records `PROTECTION_STRICT = true`, contexts equal to Phase 72's base, count, and names verbatim — PASS. `## Merge-method precedent (D-10)` records `MERGE_PRECEDENT_HITS = 2` — PASS. `## Dependabot and open pull requests (D-06)` records the positive control, verbatim open-PR listing, `GH_ACTOR`, five `| #<n> |` rows and `PR_<n>_*` keys, `OPEN_PRS`, `DEPENDABOT_OPEN_PRS`, `PR_CENSUS_AT`, and the untouched/order statement — PASS. `## What the handoff can rely on` summarises every key with `TRIAL_MERGE_VERDICT = MET` — PASS.
- Both tasks' `<verify><automated>` blocks re-run verbatim from this worktree, both exit 0.
- `git rev-list --merges a54a2d8a3b06b388c7ee004e5cfbe3405431421d..HEAD` -> empty (no merge commit landed on this branch).
- `git diff --name-only a54a2d8a3b06b388c7ee004e5cfbe3405431421d -- . ':(exclude).planning'` -> empty (no product-tree file changed).

---
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Plan: 05*
*Completed: 2026-09-16*
