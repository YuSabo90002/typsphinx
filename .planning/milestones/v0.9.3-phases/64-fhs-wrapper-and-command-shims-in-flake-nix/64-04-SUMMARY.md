---
phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
plan: 04
subsystem: infra
tags: [ci, github-actions, git, milestone-branch, ruff, dispatch]

requires:
  - phase: 64-02
    provides: "NIX-01's local ruff shim verdict (ruff 0.15.20, `ruff check .` -> All checks passed!) this plan sets beside the CI verdict"
  - phase: 64-03
    provides: "NIX-07/NIX-08 evidence files whose presence on this worktree's HEAD this plan's precondition checks before pushing"
provides:
  - "SC#5: canonical milestone branch gsd/v0.9.3-toolchain-and-dependency-update-repair pushed to origin with upstream tracking"
  - "One completed, all-green 3-OS CI run (34618719267) dispatched against the pushed tip, transcribed job by job -- both windows-latest and both macos-latest lanes named individually"
  - "NIX-01 cross-check: CI's ruff==0.15.20 verdict (Run lint with tox step) quoted and set beside 64-02's local shim verdict -- both agree"
  - "This run labelled as Phase 65's TOX-04 pre-revert baseline"
affects: [65-tox-uv-bare-tox-uv-revert]

actuals:
  tokens: 3015
  tasks: 2
  commits: 2
  plan_head_before: 7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5

tech-stack:
  added: []
  patterns:
    - "Re-measure the branch census at execution time rather than trusting a prior RESOLVED note -- constraint 9 fired twice earlier in this milestone"
    - "gh run watch --exit-status as the bounded-wait mechanism for a dispatched CI run, foregrounded under the Bash tool's timeout"

key-files:
  created:
    - .planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-CI-EVIDENCE.md
  modified: []

key-decisions:
  - "No gsd/v0.9.3-milestone decoy branch existed at this plan's execution time (only the canonical branch was present locally and on origin) -- the merge-base --is-ancestor / git branch -d decoy-handling path in Task 1's action was not needed this time, unlike the roadmap-time correction recorded in ROADMAP.md."
  - "Stated explicitly in the evidence file's Baseline framing section that the pushed tip is the phase's code-bearing tip as of this push, and that a later flake.nix-only gap-closure commit (addressing 64-02's libz.so.1 finding) is anticipated by owner decision and does not invalidate this run as Phase 65's TOX-04 pre-revert baseline, since flake.nix carries zero CI coverage either way."

requirements-completed: []

coverage:
  - id: D1
    description: "Canonical milestone branch pushed to origin with upstream tracking, at the pushed tip, with no decoy branch and no tag"
    verification:
      - kind: other
        ref: "git rev-parse --abbrev-ref '<branch>@{upstream}' + git ls-remote --heads origin, transcribed in 64-CI-EVIDENCE.md Push section"
        status: pass
    human_judgment: false
  - id: D2
    description: "Exactly one workflow_dispatch CI run dispatched against the pushed tip, completed with all twelve jobs green including both windows-latest and both macos-latest lanes named individually"
    verification:
      - kind: other
        ref: "gh run view 34618719267 --json status,conclusion,jobs, transcribed in 64-CI-EVIDENCE.md Run/Job census/windows-latest lanes/macos-latest lanes sections"
        status: pass
    human_judgment: false
  - id: D3
    description: "ruff's CI verdict (ruff==0.15.20, All checks passed!) quoted verbatim and set beside 64-02's local shim verdict; both agree"
    requirement: "NIX-01"
    verification:
      - kind: other
        ref: "gh run view --job 103327017656 --log, transcribed in 64-CI-EVIDENCE.md ruff's verdict section"
        status: pass
    human_judgment: false
  - id: D4
    description: "No release.yml run carries the pushed SHA; no PR, tag, or force-push occurred"
    verification:
      - kind: other
        ref: "gh run list --workflow=release.yml, git tag --points-at, git push output all transcribed in 64-CI-EVIDENCE.md"
        status: pass
    human_judgment: false

duration: 17min
completed: 2026-09-11
status: complete
---

# Phase 64 Plan 04: Milestone Branch Push and 3-OS CI Baseline Summary

**Pushed `gsd/v0.9.3-toolchain-and-dependency-update-repair` to origin with tracking and dispatched one `gh workflow run CI` against the pushed tip — all twelve jobs completed `success`, both `windows-latest` and both `macos-latest` lanes named individually, and CI's `ruff 0.15.20` verdict matches 64-02's local shim verdict exactly.**

## Performance

- **Duration:** ~17 min
- **Started:** 2026-09-11T15:45:00Z (approx.)
- **Completed:** 2026-09-11T16:02:00Z
- **Tasks:** 2
- **Files modified:** 1 (`64-CI-EVIDENCE.md`, created then appended across both tasks)

## Accomplishments

- **Branch census re-measured, not trusted from the RESOLVED note.** No `gsd/v0.9.3-milestone` decoy
  branch existed in this worktree's local branch list or on origin at execution time — only the
  canonical `gsd/v0.9.3-toolchain-and-dependency-update-repair`, `main`-descended, carrying HEAD.
  Constraint 9's decoy-handling path (the `merge-base --is-ancestor` check and conditional
  `git branch -d`) was not exercised this run because there was nothing decoy-shaped to correct.
- **Tip identity confirmed before pushing anything.** `git rev-parse HEAD` equalled the canonical
  branch's own SHA (`PUSHED_SHA = 7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5`) before this plan's own
  commits, `flake.nix` carried 3 matches of `typsphinx-fhs-run`, and `uv sync --extra dev --locked`
  exited 0 with no drift.
- **Pushed the canonical branch, and only it, with tracking.** `git push -u origin
  gsd/v0.9.3-toolchain-and-dependency-update-repair` — no force, no tags, no other ref. GitHub's
  "Create a pull request" hint appeared and was not acted on. `@{upstream}` resolves to
  `origin/gsd/v0.9.3-toolchain-and-dependency-update-repair`, and origin's head SHA for that ref
  equals `PUSHED_SHA`.
- **Dispatched exactly one CI run.** `gh workflow run CI --ref
  gsd/v0.9.3-toolchain-and-dependency-update-repair` produced run `34618719267`, `headSha` equal to
  `PUSHED_SHA`, `event: workflow_dispatch`.
- **Run completed all-green.** `gh run watch 34618719267 --exit-status --interval 30` exited `0`
  after ~7 minutes of wall clock (matching the ~7-minute figure recorded at planning time for prior
  Phase 61/63 CI dispatches). `gh run view` confirms `status: completed`, `conclusion: success`.
  Twelve-job census transcribed literally: both `Test Python 3.12/3.13 on windows-latest` and both
  `Test Python 3.12/3.13 on macos-latest` lanes named individually and green, alongside `Lint and
  Format Check`, `Type Check`, `Code Coverage`, `Build Package`, both `Integration Test` variants,
  and both `ubuntu-latest` test lanes.
- **ruff's CI verdict quoted and cross-checked against 64-02's local shim verdict.** CI's `Run lint
  with tox` step ran `ruff check .` against `ruff==0.15.20` (from the job's own `pip freeze` line)
  and reported `All checks passed!`. 64-02's `64-NIX05-WORKTREE-EVIDENCE.md` recorded the identical
  `ruff 0.15.20` / `All checks passed!` result through the `flake.nix` shim in a nested worktree —
  local and CI lint agree on both version and verdict, the CI side of NIX-01's rationale.
- **No release-workflow route touched.** `gh run list --workflow=release.yml --limit 5` shows none
  of the five most recent runs carrying the pushed SHA; no tag was created; no PR was opened.
- **Baseline labelled.** This run is recorded as Phase 65's TOX-04 pre-revert baseline —
  `tox-uv-bare` is still pinned at this tip, unchanged by this plan.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — branch census, tip identity, lock check, push the canonical branch with
   tracking, dispatch CI exactly once** - `e6d1a365` (docs)
2. **Task 2: Observe the run to completion and transcribe the full job census** - `028c5dba` (docs)

**Plan metadata:** committed alongside this SUMMARY (see final commit).

_Note: this plan is `type: execute`, not TDD — both commits are `docs` (evidence-file-only),
matching this plan's binding `<files_modified>` scope (only `64-CI-EVIDENCE.md`)._

## Files Created/Modified

- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-CI-EVIDENCE.md` - Branch
  census, tip identity and lock check, push and dispatch records (Task 1); the run's final
  status, full job census, windows-latest/macos-latest lane sub-tables, ruff's CI verdict set
  beside 64-02's local verdict, the release.yml non-match, and the dispatch-count closing note
  (Task 2).

## Decisions Made

- No decoy branch existed at execution time, so the `merge-base --is-ancestor` decoy-handling path
  in Task 1's action was measured-not-needed rather than skipped — the branch census still ran and
  is recorded verbatim, confirming the roadmap-time correction (§ ROADMAP.md's RESOLVED constraint-9
  note) held through wave 3 without a third decoy re-creation.
- The evidence file's Baseline framing section states plainly that the pushed tip is the phase's
  code-bearing tip *as of this push*, and that an anticipated later `flake.nix`-only gap-closure
  commit (the owner's 2026-09-12 decision to run this plan before gap-closing 64-02's `libz.so.1`
  finding) does not need a second CI dispatch, since `flake.nix` is invisible to CI either way.

## Deviations from Plan

None — plan executed exactly as written. The one contingency path (decoy-branch handling) was
evaluated and found not applicable; this is the expected outcome of "re-measure, never trust", not
a deviation from it.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

SC#5 is met: the milestone branch is on `origin` with tracking, and one `workflow_dispatch` CI run
at the pushed tip completed with all twelve jobs green, both `windows-latest` and both
`macos-latest` lanes named individually. This run is the pre-revert baseline Phase 65's TOX-04
compares against. Phase 64's remaining open item — 64-02's `libz.so.1` finding affecting
NIX-02/NIX-03/NIX-04 — is unaffected by this plan (owner decision: gap-close after phase
verification) and remains for a Phase 64 gap-closure plan. `NIX-01`'s checkbox, blocked by the
shared-ID gate on sibling plan 64-02, can now close: this plan is the sibling that was
outstanding.

## Self-Check: PASSED

- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-CI-EVIDENCE.md` — FOUND
- Commit `e6d1a365` (Task 1) — FOUND in `git log --oneline --all`
- Commit `028c5dba` (Task 2) — FOUND in `git log --oneline --all`
- Task 1's automated `<verify>` block: re-ran clean before Task 2 began (tracer feedback gate,
  row 3 — interactive/end-of-phase/fully-automated verify) — PASS.
- Task 2's automated `<verify>` block: re-ran clean after transcription — status completed,
  conclusion success, 12 jobs, 0 non-success, 2 windows-latest, 2 macos-latest, Lint and Format
  Check success, all six required name strings present in the evidence file, exactly 1 dispatched
  run on the branch, 0 release.yml runs at the pushed SHA — PASS.
- Plan-level `<verification>` block: "canonical branch on origin with tracking at pushed SHA, no
  decoy, no tag" — PASS. "one workflow_dispatch CI run at that SHA completed with all twelve jobs
  green, both Windows and macOS lanes named" — PASS. "ruff's CI verdict quoted and set against the
  local shim's verdict" — PASS.
- `git status --short` over the full worktree — clean (both commits captured all changes).

---
*Phase: 64-fhs-wrapper-and-command-shims-in-flake-nix*
*Plan: 04*
*Completed: 2026-09-11*
