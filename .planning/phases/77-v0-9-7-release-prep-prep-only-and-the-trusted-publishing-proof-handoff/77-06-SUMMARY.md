---
phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff
plan: 06
subsystem: infra
tags: [release-prep, ci, github-actions, trusted-publishing, gh-cli, v0.9.7]

# Dependency graph
requires:
  - phase: 77 (waves 1-2, plans 77-01 through 77-05)
    provides: bumped tip with SC3_LOCAL_VERDICT, TRIAL_MERGE_VERDICT, ATT06_VERDICT, CONTROLS_VERDICT all at their passing values
provides:
  - SC#3's CI clause discharged on the bumped tip (0.9.7) via one workflow_dispatch CI run, all 12 jobs green
  - The milestone branch fast-forwarded on origin, no tags, no decoy
  - SC3_CI_VERDICT = MET for 77-07/77-08 to read
affects: [77-07-handoff, 77-08-closeout]

# Actuals (#2632)
actuals:
  tokens: 3723
  tasks: 2
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "DISPATCH_ATTEMPTED marker committed before the CI dispatch runs, RUN_ID committed before the first foreground wait — resumed-executor-safe exactly-one-dispatch guard"

key-files:
  created:
    - .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-CI-EVIDENCE.md
  modified: []

key-decisions:
  - "None - followed plan as specified"

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "Fast-forward push of the bumped milestone tip to origin, with no decoy and no tag"
    verification:
      - kind: other
        ref: "77-CI-EVIDENCE.md § Decoy census, § Push (git ls-remote / git tag --points-at readings)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Exactly one gh workflow run ci.yml dispatch on the bumped tip, behind a committed DISPATCH_ATTEMPTED marker"
    verification:
      - kind: other
        ref: "77-CI-EVIDENCE.md § Dispatch, § Dispatch count and no release run"
        status: pass
    human_judgment: false
  - id: D3
    description: "The dispatched CI run completes green across all 12 jobs including both windows-latest and both macos-latest lanes, matching Phase 76's reference job set"
    verification:
      - kind: other
        ref: "77-CI-EVIDENCE.md § Job census, § windows-latest lanes, § macos-latest lanes (gh run view 36430787178)"
        status: pass
    human_judgment: false
  - id: D4
    description: "main's required status checks are unchanged since 77-05's reading, and SC3_CI_VERDICT = MET"
    verification:
      - kind: other
        ref: "77-CI-EVIDENCE.md § Required checks at phase close, § SC#3 CI verdict"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-09-28
status: complete
---

# Phase 77 Plan 06: SC#3 CI — Bumped-Tip Push and One CI Dispatch Summary

**Fast-forwarded the v0.9.7 milestone branch to origin and obtained a fully green three-OS CI run (12/12 jobs, run 36430787178) on exactly the bumped tip, discharging ROADMAP SC#3's CI clause.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-09-28T13:42:59Z
- **Completed:** 2026-09-28T13:54:17Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments
- Confirmed all four wave-gate verdicts at their passing values (`SC3_LOCAL_VERDICT = MET`, `TRIAL_MERGE_VERDICT = MET`, `ATT06_VERDICT = MET`, `CONTROLS_VERDICT = READY`) before taking any outward action
- Verified the pushed tip's identity and fence: carries the bump commit and every wave-2 evidence/handoff file, reads `version = "0.9.7"`, changes only Phase 76's own files under `typsphinx/` and `.github/` against the milestone base, and carries no tag
- Recorded the decoy census immediately before the push (`DECOY_ACTION = none-present`) and pushed the milestone branch to origin as a fast-forward with `--no-follow-tags` (`987ec3fe` → `df6357fa`)
- Committed `DISPATCH_ATTEMPTED = yes` before dispatching, then dispatched `ci.yml` exactly once against the pushed tip and committed `RUN_ID`/`RUN_URL` before the first foreground wait
- Waited on the run in the foreground to `completed`/`success` (run `36430787178`, ~6m52s), transcribed every one of its 12 jobs, confirmed the sorted job-name set matches Phase 76's reference run `36320335404`, and confirmed all four `windows-latest`/`macos-latest` lanes individually succeeded
- Quoted the `Lint and Format Check` job's own `black --check .` / `ruff check .` / `lint: OK` lines and recorded the pushed tree's own ruff pin (`LOCK_RUFF_VERSION = 0.16.8`)
- Confirmed `DISPATCH_COUNT = 1`, `CI_RUNS_AFTER` exactly one above `CI_RUNS_BEFORE`, and zero `release.yml` runs at the pushed SHA or newer than the Phase 76 rehearsal
- Re-read `main`'s required status checks live and confirmed they are unchanged from 77-05's reading
- Wrote `SC3_CI_VERDICT = MET`

## Task Commits

Each task was committed atomically:

1. **Task 1 (part 1): Wave gate, tip identity/fence, decoy census, fast-forward push, `DISPATCH_ATTEMPTED` marker before dispatch** - `f1054723` (docs)
2. **Task 1 (part 2): Dispatch, `RUN_ID`/`RUN_URL` committed before the first foreground wait** - `5e41c8c7` (docs)
3. **Task 2: Foreground wait, job census, lint-through-tox, dispatch count, required-checks re-read, `SC3_CI_VERDICT = MET`** - `9ab71eea` (docs)

_Note: Task 1's `<action>` steps span two commits because step 6 requires `DISPATCH_ATTEMPTED = yes` committed before the dispatch command runs, and `RUN_ID` committed before the first wait — both write-ahead points the plan mandates as separate commits for resume-safety._

## Files Created/Modified
- `.planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-CI-EVIDENCE.md` - Full evidence trail: wave gate, tip identity/fence, decoy census, push, dispatch, run/job census, lint quotes, dispatch/release-run counts, required-checks re-read, SC#3 CI verdict

## Decisions Made
None - followed plan as specified.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None. The push was a clean fast-forward on the first attempt; the single dispatch registered on the first `gh run list` call with no registration lag and no HTTP 5xx, so none of the plan's edge-case branches (decoy deletion, dispatch retry-after-5xx, resumed-executor adoption) were exercised.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`77-CI-EVIDENCE.md`'s `SC3_CI_VERDICT = MET`, `RUN_ID`, and `PUSHED_SHA` are ready for `77-07-PLAN.md` (wave 4, the SC#4 handoff) to read via `sed` and inline into `77-HANDOFF.md`'s success-criteria table and step 1, per this plan's `key_links`. No blockers or concerns — the bumped tip is proven green on `origin` and no irreversible action (tag, release, PR) was taken alongside the push or dispatch.

---
*Phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff*
*Completed: 2026-09-28*
