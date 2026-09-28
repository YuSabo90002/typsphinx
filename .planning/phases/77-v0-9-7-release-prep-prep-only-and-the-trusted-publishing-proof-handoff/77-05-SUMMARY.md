---
phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff
plan: 05
subsystem: release-prep
tags: [git, uv, ruff, black, gh-api, trial-merge, branch-protection]

# Dependency graph
requires:
  - phase: 77 (77-02)
    provides: BUMP_COMMIT_SHA and the bumped 0.9.7 tree this plan's trial merge is taken against
provides:
  - "77-PREFLIGHT-EVIDENCE.md: a non-committing git merge-tree trial merge of the bumped tip against origin/main, proven idempotent and lock/lint-green in scratch"
  - "main's live branch protection (strict, 6 required contexts), allowed merge methods and first-parent merge precedent"
  - "the live branch and open-pull-request census (one Dependabot branch/PR, no gsd/v0.9.7-milestone decoy, zero PRs on the milestone branch)"
  - "TRIAL_MERGE_VERDICT = MET, consumed by 77-06's push gate and 77-07's handoff step 1"
affects: [77-06, 77-07]

# Actuals (#2632)
actuals:
  tokens: 3353
  tasks: 2
  commits: 2
  plan_head_before: 44f9c6a2045b4943664b1a3473dc3b4422ac3ad3
  plan_head_after: 534d63220ce9e7a0985fd7f2f0d6fb1a12e365ed

# Tech tracking
tech-stack:
  added: []
  patterns: ["non-committing trial merge via git merge-tree --write-tree, extracted into a scratch uv --directory checkout for lock/lint verification, never git merge"]

key-files:
  created:
    - .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-PREFLIGHT-EVIDENCE.md
  modified: []

key-decisions:
  - "None beyond the plan as written — both tasks executed exactly as specified, with all readings measured live rather than carried from the planning-time census."

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "Non-committing trial merge (git merge-tree --write-tree) of the bumped tip against origin/main is clean, idempotent across two recorded runs plus a third live verify run, and the extracted merged tree passes uv lock --check, a locked sync, ruff check . and black --check . in scratch while still reading version 0.9.7"
    requirement: REL-17
    verification:
      - kind: other
        ref: "Task 1 <automated> verify (git merge-tree, uv lock --check, uv sync --locked, ruff check ., black --check . against the extracted merged tree)"
        status: pass
    human_judgment: false
  - id: D2
    description: "main's branch protection (strict, 6 required contexts, unchanged since Phase 75's close), merge methods, and first-parent merge-commit precedent (111 hits) read live via gh api and git log"
    requirement: REL-17
    verification:
      - kind: other
        ref: "Task 2 <automated> verify (gh api branches/main/protection/required_status_checks, gh api repo merge-method fields, git log --first-parent recount)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Live branch and open-pull-request census measured at execution time: one Dependabot branch/PR (#157, types-docutils), no gsd/v0.9.7-milestone decoy, zero pull requests against the milestone branch; TRIAL_MERGE_VERDICT = MET"
    requirement: REL-17
    verification:
      - kind: other
        ref: "Task 2 <automated> verify (git ls-remote --heads origin, gh pr list --state open/all, gh pr list --head <milestone-branch>)"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-09-28
status: complete
---

# Phase 77 Plan 05: SC#3 Preflight — Trial Merge and Remote Reads Summary

**Non-committing `git merge-tree` proves the bumped 0.9.7 tip merges clean and lint-green against
an `origin/main` that has moved three Dependabot commits past the milestone base, with `main`'s
protection, merge method and the live branch/PR census recorded for the handoff — `TRIAL_MERGE_VERDICT = MET`.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-09-28T13:26:29Z
- **Completed:** 2026-09-28T13:30:08Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments
- `git merge-tree --write-tree` of `BASE_77_05` (the bumped tip) against `origin/main` exits 0 and
  prints the identical tree SHA `d41a910e448f7205e395aaba0f1d1c6e642e6190` across two recorded runs
  and a third live verify run — no merge commit, no ref, no branch created.
- The merged tree, extracted from its own tree object into a scratch directory, passes
  `uv lock --check`, a locked `uv sync --extra dev --no-install-project`, `ruff check .` (resolving
  ruff 0.16.9, one Dependabot bump ahead of the branch's own 0.16.8) and `black --check .`, while
  still reading `version = "0.9.7"`. The merged `uv.lock` package-name set hashes identically to
  `v0.9.6`'s — no new dependency survives the merge.
- `main`'s branch protection (`strict: true`, 6 required contexts) is read live via `gh api` and
  matches Phase 75's close reading exactly (`REQUIRED_CHECKS_UNCHANGED_SINCE_75 = yes`). All three
  merge methods are allowed on the repository; 111 first-parent history hits confirm every prior
  pull request landed as a real merge commit.
- The branch and pull-request census is measured fresh, not carried from the planning-time census:
  one Dependabot branch/PR (#157, `types-docutils`, dev-only), no `gsd/v0.9.7-milestone` decoy on
  origin, and zero pull requests of any state against the milestone branch.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — non-committing trial merge, idempotency, merged-tree lock and lint** - `a2d3d4d2` (docs)
2. **Task 2: main protection, merge method, live branch/PR census, trial-merge verdict** - `534d6322` (docs)

**Plan metadata:** committed alongside Task 2 in this same wave (no separate metadata commit — this
worktree excludes STATE.md/ROADMAP.md/REQUIREMENTS.md per the orchestrator's parallel-execution
contract; SUMMARY.md is committed as this plan's final commit below).

## Files Created/Modified
- `.planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-PREFLIGHT-EVIDENCE.md` - the full trial-merge, protection, merge-method and census evidence, with `TRIAL_MERGE_VERDICT = MET`

## Decisions Made
None - plan executed exactly as written. The tracer feedback gate (Task 1 → Task 2) was evaluated
per the interactive/`end-of-phase` branch (Task 1's `<verify>` carries only `<automated>` content):
the verify was re-run, passed, and expansion into Task 2 proceeded without a checkpoint.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `77-PREFLIGHT-EVIDENCE.md` is ready for 77-06 (which reads `TRIAL_MERGE_VERDICT` before pushing)
  and 77-07 (which reads `PROTECTION_CONTEXTS`, `OPEN_PRS` and `MAIN_MOVED` into `77-HANDOFF.md`
  step 1, with an explicit instruction to re-read `origin/main` live at the close since it can move
  again — Dependabot PR #157 was still open at this reading).
- No blockers or concerns.

---
*Phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff*
*Completed: 2026-09-28*

## Self-Check: PASSED

- `77-PREFLIGHT-EVIDENCE.md` exists on disk: FOUND
- `a2d3d4d2` (Task 1 commit) present in `git log --oneline --all`: FOUND
- `534d6322` (Task 2 commit) present in `git log --oneline --all`: FOUND
- Both tasks' `<automated>` verify blocks re-run at plan close (`TASK1_VERIFY_PASS`, `TASK2_VERIFY_PASS`)
- No merge/trial-named branch, no new tag, `git tag -l` unchanged, `git diff --name-only` outside `.planning/` empty across the plan
