---
phase: 72-tox-e-linkcheck-and-root-toctree-deduplication
plan: 06
subsystem: ci
tags: [ci, github-actions, milestone-push, workflow-dispatch, gh-cli]

# Dependency graph
requires:
  - phase: 72-04
    provides: SC3/SC4 toctree dedup verdicts (72-TOCTREE-EVIDENCE.md), all MET
  - phase: 72-05
    provides: SC5_LOCAL_VERDICT MET and TIP_LINKCHECK_VERDICT PASS (72-GATES-EVIDENCE.md)
provides:
  - Milestone branch gsd/v0.9.5-docs-link-check-and-navigation pushed to origin for the first time
  - One workflow_dispatch CI run on the phase tip, observed to completion, all 12 jobs green
  - main's required status checks re-confirmed unchanged from phase head to phase close
affects: [73-close-prep]

# Actuals (#2632)
actuals:
  tokens: 3200
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns: [gh workflow run + foreground gh run watch for milestone-branch CI verification]

key-files:
  created:
    - .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-CI-EVIDENCE.md
  modified: []

key-decisions:
  - "PUSHED_SHA equaled this worktree's own fork base (BASE_72_06) — waves 1-3 plus the wave-4 tracking-update commit were already on the branch tip before this plan started, so no new product commit was needed before the push."
  - "gh workflow run CI succeeded on the first attempt (no HTTP 5xx), unlike Phase 71's run which needed 4 attempts and left a DISPATCH_COUNT=2 discrepancy — this phase's DISPATCH_COUNT is a clean 1."

patterns-established:
  - "Foreground CI wait via `timeout 590 gh run watch <id> --interval 30` inside a single Bash call with the tool's 600000ms timeout, followed by a `gh run view --json status,conclusion` confirmation — completed inside one watch window (run took ~7 minutes wall-clock)."

requirements-completed: [QUA-13, DOC-24, DOC-18]

coverage:
  - id: D1
    description: "Milestone branch gsd/v0.9.5-docs-link-check-and-navigation pushed to origin for the first time (constraint 6 / SC#5 remote half), with a pre-push decoy census finding no gsd/v0.9.5-milestone anywhere, no tag riding along, and the local branch tracking origin"
    requirement: "QUA-13"
    verification:
      - kind: other
        ref: "72-CI-EVIDENCE.md ## Push, ## Decoy census (constraint 6), ## Tip identity and fence — git push --no-follow-tags -u, git ls-remote, git tag --points-at"
        status: pass
    human_judgment: false
  - id: D2
    description: "Exactly one gh workflow run CI --ref ... dispatch observed in the foreground to completion: all 12 jobs success, including both windows-latest and both macos-latest lanes, job set identical to Phase 71's reference run, lint ran through the edited tox.ini (black/ruff/lint: OK quoted), and required checks unchanged from phase head to close"
    requirement: "DOC-24"
    verification:
      - kind: other
        ref: "72-CI-EVIDENCE.md ## Run, ## Job census, ## windows-latest lanes, ## macos-latest lanes, ## Lint through tox, ## Dispatch count and no release run, ## Required checks at phase close, ## SC#5 CI verdict — gh run view/list, gh api branch protection"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC5_CI_VERDICT = MET recorded, closing ROADMAP SC#5's CI half for Phase 72"
    requirement: "DOC-18"
    verification:
      - kind: other
        ref: "72-CI-EVIDENCE.md ## SC#5 CI verdict"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-09-13
status: complete
---

# Phase 72 Plan 06: First Push and CI Dispatch Summary

**Pushed `gsd/v0.9.5-docs-link-check-and-navigation` to origin for the first time and dispatched one `workflow_dispatch` CI run that completed all-green across 12 jobs, including both `windows-latest` and both `macos-latest` lanes.**

PUSHED_SHA = 0b2595df21399363f50e5e1a55935f470e0df00d
RUN_ID = 34761445288
RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/34761445288
JOB_COUNT = 12
NON_SUCCESS_JOBS = 0
REQUIRED_CHECKS_UNCHANGED = yes
SC5_CI_VERDICT = MET

## Performance

- **Duration:** 10 min
- **Started:** 2026-09-13T14:00:22Z
- **Completed:** 2026-09-13T14:10:35Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Re-read all five wave-3 gate keys (SC3_VERDICT, SC4_VERDICT, SC5_LOCAL_VERDICT, TIP_LINKCHECK_VERDICT, LINKCHECK_VERDICT, DOC24_VERDICT) as MET/PASS before pushing anything.
- Ran the constraint-6 decoy census immediately before the push: no `gsd/v0.9.5-milestone` locally or on origin, so the push proceeded with nothing to reconcile.
- Pushed the canonical branch to origin as a brand-new remote branch (`git push --no-follow-tags -u origin gsd/v0.9.5-docs-link-check-and-navigation`), confirmed tracking and no tag at the tip.
- Dispatched `gh workflow run CI --ref gsd/v0.9.5-docs-link-check-and-navigation` exactly once — it succeeded on the first attempt (no HTTP 5xx, unlike Phase 71's run).
- Observed the run to completion in the foreground (`gh run watch`); all 12 jobs succeeded, matching Phase 71's job-name set exactly.
- Quoted the `Lint and Format Check` job's `Run lint with tox` step (black, ruff, `lint: OK`) to prove the runner exercised the edited `tox.ini`.
- Re-read `main`'s required status checks at phase close and confirmed both `strict` and the sorted context set are unchanged from the phase-head record in `72-BASE-EVIDENCE.md`.

## Task Commits

Each task was committed atomically (plain `git commit`, per this plan's project overrides):

1. **Task 1: Tracer — gate on wave 3, tip identity and fence, decoy census, first push with tracking, one CI dispatch** - `71a3070f` (docs)
2. **Task 2: Observe the run to completion in the foreground, transcribe every job, name the four windows and macos lanes, quote the tox lint step, and re-read the required checks at phase close** - `93bdeff1` (docs)

**Plan metadata:** this SUMMARY's own commit (not yet made at the time this table was written).

## Files Created/Modified
- `.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-CI-EVIDENCE.md` - Phase 72's CI evidence: wave-3 gate re-read, tip identity/fence, decoy census, push, dispatch, run observation, job census, lane tables, tox lint quote, dispatch-count/release-run checks, required-checks comparison, and the SC#5 CI verdict.

## Decisions Made
- `PUSHED_SHA` equaled this worktree's own fork base (`BASE_72_06`) — no new product-tree commit was needed before pushing, since waves 1–3 plus the wave-4 tracking-update commit were already on the branch tip.
- Dispatch succeeded cleanly on the first `gh workflow run` attempt; no retry logic or second-dispatch decision was needed (contrast with Phase 71's four-attempt, `DISPATCH_COUNT=2` history, which is documented as a reference shape in `71-CI-EVIDENCE.md`).

## Deviations from Plan

None - plan executed exactly as written. Both tasks' automated `<verify>` commands passed on the first run with no fix-up needed.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. `gh` was already authenticated as `YuSabo90002` with `repo` and `workflow` scopes.

## Next Phase Readiness

- ROADMAP SC#5 for Phase 72 is now fully discharged: the milestone branch is on origin, tracked, undecoyed, untagged, and a completed three-OS CI run on the exact phase tip is transcribed job by job.
- Every later commit of this phase (this SUMMARY's own metadata commit) touches only `.planning/`, which no CI job reads, so no further CI dispatch is needed for the remainder of Phase 72.
- Phase 73 (close prep, prep-only, unpublished) can proceed once the orchestrator has merged this wave and updated STATE.md/ROADMAP.md centrally.

---
*Phase: 72-tox-e-linkcheck-and-root-toctree-deduplication*
*Completed: 2026-09-13*
