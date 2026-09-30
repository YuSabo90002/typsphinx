---
phase: 74-the-doctest-block-handler-its-real-compile-gate-and-the-docs
plan: 07
subsystem: ci-evidence
tags: [ci, github-actions, sc4, first-push, release-branch]

# Dependency graph
requires:
  - phase: 74-05
    provides: SC1_VERDICT = MET, SC3_VERDICT = MET, D05_VERDICT = MET (gated on before push)
  - phase: 74-06
    provides: SC4_LOCAL_VERDICT = MET (gated on before push)
provides:
  - "74-CI-EVIDENCE.md: the wave-4 gate, tip identity and fence, decoy census, first push with
    tracking, one CI dispatch, the completed all-green three-OS run with every job transcribed,
    the four named windows/macos lanes, the tox lint step, required checks at close, and
    SC4_CI_VERDICT = MET"
  - "The milestone branch gsd/v0.9.6-doctest-block-rendering-and-release now exists on origin at
    PUSHED_SHA, tracking origin, with one completed workflow_dispatch CI run"
affects: []

# Actuals (#2632)
actuals:
  tokens: 2879
  tasks: 2
  commits: 2
plan_head_before: e54d47d0b00d77f600d1aa27b0f78a031db055c7

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Immediately-pre-push branch census (local + origin) for the milestone branch namespace,
      mirroring the pattern established in 72-CI-EVIDENCE.md"

key-files:
  created:
    - .planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-CI-EVIDENCE.md
  modified: []

key-decisions:
  - "Task 1 (tracer) re-ran its own <verify> after commit before expanding to Task 2, per the
    tracer feedback gate row 3 (interactive, end-of-phase, automated-only verify) — no checkpoint
    was needed since the automated verify passed both before and after the Task 1 commit."
  - "No decoy branch existed anywhere (local or origin) at the pre-push census, matching the
    planning-time expectation; DECOY_ACTION = none-present and nothing was deleted."
  - "The push was a genuine branch creation (ORIGIN_BEFORE = none), not a fast-forward, matching
    the orchestrator's pre-measured state."

requirements-completed: [TRN-01, TRN-02, QUA-14]

coverage:
  - id: D1
    description: "The milestone branch gsd/v0.9.6-doctest-block-rendering-and-release is on origin
      for the first time, at PUSHED_SHA, tracking origin, with no decoy and no tag riding along"
    requirement: TRN-01
    verification:
      - kind: other
        ref: "74-CI-EVIDENCE.md ## Push (verify block re-run automated, all PASS)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Exactly one CI run was dispatched against PUSHED_SHA via workflow_dispatch and
      waited on in the foreground to completion: all 12 jobs success, both windows-latest and both
      macos-latest lanes named individually and success, lint ran through tox"
    requirement: TRN-02
    verification:
      - kind: other
        ref: "74-CI-EVIDENCE.md ## Job census / ## windows-latest lanes / ## macos-latest lanes / ## Lint through tox"
        status: pass
    human_judgment: false
  - id: D3
    description: "main's required status checks at phase close equal the phase-head record
      (REQUIRED_STRICT_HEAD, REQUIRED_CONTEXTS_HEAD); no second dispatch and no release.yml run
      exist at PUSHED_SHA; SC4_CI_VERDICT = MET"
    requirement: QUA-14
    verification:
      - kind: other
        ref: "74-CI-EVIDENCE.md ## Required checks at phase close / ## SC4 CI verdict"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-19
status: complete
---

# Phase 74 Plan 07: CI Evidence (First Push, SC4 CI Half) Summary

**PUSHED_SHA = e54d47d0b00d77f600d1aa27b0f78a031db055c7, RUN_ID = 35476044079,
RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/35476044079,
JOB_COUNT = 12, NON_SUCCESS_JOBS = 0, REQUIRED_CHECKS_UNCHANGED = yes, SC4_CI_VERDICT = MET.**

The milestone branch `gsd/v0.9.6-doctest-block-rendering-and-release` went on `origin` for the
first time this milestone, and the one `workflow_dispatch` CI run against it completed all green
across all 12 jobs, including both `windows-latest` and both `macos-latest` lanes, with `main`'s
required status checks unchanged from phase head to phase close.

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-19T23:23:32Z
- **Completed:** 2026-09-19T23:31:25Z (CI run completion)
- **Tasks:** 2
- **Files modified:** 1 (`74-CI-EVIDENCE.md`, built incrementally across both tasks)

## Accomplishments

- **Task 1 (tracer).** Gated on wave 4 (`SC1_VERDICT`, `SC3_VERDICT`, `D05_VERDICT`, all `MET`
  from `74-TIP-EVIDENCE.md`, and `SC4_LOCAL_VERDICT = MET` from `74-GATES-EVIDENCE.md`). Confirmed
  the tip identity: `PUSHED_SHA` equals this worktree's own `BASE_74_07` HEAD, wave 4 is merged
  into it, the `typsphinx/` scope fence holds (only `pathfmt.py` and `translator.py` changed since
  the milestone base), `.github/` and `flake.nix` untouched, version still `0.9.2`, no tag at the
  tip. Ran the decoy census immediately before the push: no decoy anywhere
  (`DECOY_ACTION = none-present`). Pushed with `git push --no-follow-tags -u origin
  gsd/v0.9.6-doctest-block-rendering-and-release` — a genuine branch creation
  (`ORIGIN_BEFORE = none`) — confirmed the origin head now equals `PUSHED_SHA` and the branch
  tracks `origin`. Dispatched exactly one CI run (`RUN_ID = 35476044079`) via
  `gh workflow run CI --ref gsd/v0.9.6-doctest-block-rendering-and-release`, located it in
  `gh run list` with `headSha = PUSHED_SHA` and `createdAt` after `PUSH_AT`. The tracer feedback
  gate's automated `<verify>` was re-run after the commit and passed before expanding to Task 2
  (interactive, `end-of-phase`, automated-only verify — no checkpoint needed, per
  `checkpoints.md`'s tracer feedback gate row 3).
- **Task 2.** Waited in the foreground for `RUN_ID` to complete (`gh run watch` inside the Bash
  tool's 600000ms timeout, then `gh run view` status polling) — the run finished inside the first
  watch window with `conclusion = success`. Transcribed all 12 jobs (`JOB_COUNT = 12`,
  `NON_SUCCESS_JOBS = 0`), confirmed the sorted job-name set equals `REFERENCE_JOB_NAMES` from
  `74-BASE-EVIDENCE.md` (`JOB_NAMES_MATCH_REFERENCE = yes`), named both `windows-latest` and both
  `macos-latest` lanes individually — all four success. Quoted the `Lint and Format Check` job's
  `Run lint with tox` step's `black --check .` and `ruff check .` command lines and its `lint: OK`
  verdict, showing CI ran the same lint through tox this worktree ran locally in 74-06. Confirmed
  `DISPATCH_COUNT = 1` and `RELEASE_RUNS_AT_PUSHED = 0`. Re-read `main`'s required status checks
  (`REQUIRED_STRICT_CLOSE = true`, `REQUIRED_CONTEXTS_CLOSE` matching the six-context phase-head
  string) — `REQUIRED_CHECKS_UNCHANGED = yes`. Recorded `SC4_CI_VERDICT = MET`.

## Task Commits

Each task was committed atomically (plain `git commit`, per this plan's
`<worktree_provisioning>` instruction — no GSD commit helper):

1. **Task 1: Tracer — gate on wave 4, tip identity and fence, decoy census, the first push with
   tracking, and one CI dispatch** - `5c7a1ba8` (docs)
2. **Task 2: Wait for the run in the foreground to completion, transcribe every job, name the
   four windows and macos lanes, quote the tox lint step, and re-read the required checks at
   phase close** - `bd10ec3c` (docs)

_Note: per `<worktree_provisioning>`'s "Plain git commit" instruction, both commits are plain
`git commit` — no GSD commit helper was used, and no `74-VERIFICATION.md` was created._

## Files Created/Modified

- `.planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-CI-EVIDENCE.md` -
  the phase's remote-CI evidence record: head check/provisioning, wave-4 gate, tip identity and
  fence, decoy census, push, dispatch (Task 1); the completed run, job census, windows/macos lane
  tables, the tox lint quote, dispatch count and no-release-run, required checks at close, and the
  SC4 CI verdict (Task 2).

## Decisions Made

- Task 1's tracer feedback gate re-ran the automated `<verify>` chain after the commit rather than
  synthesizing a checkpoint, because the run is interactive with `human_verify_mode = end-of-phase`
  and the tracer's `<verify>` carries only `<automated>` (no `<human-check>`) — per checkpoints.md's
  tracer feedback gate row 3.
- No branch was deleted or re-pointed: the decoy census found no `gsd/v0.9.6-milestone` anywhere,
  so the constraint-10 ordering concern (fast-forward + HEAD re-point acting on the main checkout)
  never applied to this run.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `74-CI-EVIDENCE.md` is complete and committed with `SC4_CI_VERDICT = MET`. Phase 74's SC4 is now
  fully discharged (local half from 74-06, remote half from this plan).
- `gsd/v0.9.6-doctest-block-rendering-and-release` is on `origin`, tracking, with one completed
  all-green CI run at the phase tip. No decoy exists, no tag was created.
- No blockers. Phase 74's remaining work (per STATE.md / ROADMAP.md) is orchestrator-owned
  tracking updates after this wave completes.

---
*Phase: 74-the-doctest-block-handler-its-real-compile-gate-and-the-docs*
*Completed: 2026-09-19*

## Self-Check: PASSED

- `[ -f .planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-CI-EVIDENCE.md ]` -> FOUND
- `git log --oneline -3` shows `bd10ec3c`, `5c7a1ba8` at the top, both present.
- Both tasks' `<automated>` `<verify>` scripts re-run against final HEAD and both exited 0
  (printed `ALL PASS`).
- `git diff --diff-filter=D --name-only HEAD~1 HEAD` empty at both commit boundaries;
  `git status --short` clean.
- All plan-level `<verification>` bullets hold: the canonical branch is on origin at `PUSHED_SHA`
  with no decoy and no tag and tracks origin; one dispatched CI run at `PUSHED_SHA` completed all
  green with all four Windows/macOS lanes named, the job set equal to the reference run's, and
  lint run through tox; the required checks are unchanged from phase head to phase close.
