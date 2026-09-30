---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
plan: 13
subsystem: ci-infra
tags: [ci, github-actions, gh-cli, ruff, uv, release-gating]

# Dependency graph
requires:
  - phase: 70-typing-modernization-and-its-behaviour-identity-evidence
    provides: wave 5's after-side evidence (70-10 SC#1/SC#2/legs a,c,e; 70-11 legs b,d; 70-12 DOC-23), all MET on the canonical tip
provides:
  - "origin/gsd/v0.9.4-typing-modernization, published for the first time with upstream tracking"
  - "one completed, all-green (12/12) workflow_dispatch CI run on the post-flip tip"
  - "70-CI-EVIDENCE.md: the gate quartet on the tip, the branch census, the push, the run transcript, and the SC#1..SC#5 roll-up"
affects: [71-v0-9-4-close-prep]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 2800
  tasks: 2
  commits: 3
  plan_head_before: e70e31fba9039133a153a5bba16577d7b2f889c1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Milestone-first push+dispatch (mirrors 69-04's shape, adapted for a branch that has never been on origin before)"

key-files:
  created:
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CI-EVIDENCE.md
  modified: []

key-decisions:
  - "DECOY = ABSENT: no gsd/v0.9.4-milestone existed locally or on origin at census time, so none of constraint 9's fast-forward/symbolic-ref/delete sequence was needed."
  - "The gate quartet (uv lock --check, ruff, black, mypy, full LC_ALL=C pytest) was re-run locally on the tip before touching origin, per SC#5's local half."

requirements-completed: [QUA-09]

coverage:
  - id: D1
    description: "Canonical branch gsd/v0.9.4-typing-modernization pushed to origin for the first time with upstream tracking, no decoy, no tag."
    requirement: QUA-09
    verification:
      - kind: other
        ref: "Task 1 <verify> automated block (re-run as a scratch script post-commit)"
        status: pass
    human_judgment: false
  - id: D2
    description: "One workflow_dispatch CI run (34742047126) dispatched exactly once on PUSHED_SHA, observed in the foreground to completion, all 12 jobs success including both windows-latest and both macos-latest lanes, and ruff's verdict quoted from Lint and Format Check matching the lock."
    requirement: QUA-09
    verification:
      - kind: other
        ref: "Task 2 <verify> automated block (re-run as a scratch script post-commit); gh run view 34742047126 --json status,conclusion"
        status: pass
    human_judgment: false
  - id: D3
    description: "All five Phase 70 success criteria rolled up from committed evidence: PHASE_SC_ROLLUP = ALL_MET."
    requirement: QUA-09
    verification:
      - kind: other
        ref: "70-CI-EVIDENCE.md ## Phase SC roll-up, cross-checking 70-10/70-11/70-12 verdict keys plus this file's SC5_VERDICT"
        status: pass
    human_judgment: false

duration: 16min
completed: 2026-09-13
status: complete
---

# Phase 70 Plan 13: Push, CI Dispatch and SC Roll-up Summary

**`gsd/v0.9.4-typing-modernization` reached `origin` for the first time; a single dispatched CI run at `e70e31fb` completed 12/12 jobs green (both `windows-latest` and both `macos-latest` lanes), and all five Phase 70 success criteria roll up `ALL_MET`.**

## Performance

- **Duration:** 16 min
- **Started:** 2026-09-13T06:05:41Z
- **Completed:** 2026-09-13T06:21:36Z
- **Tasks:** 2
- **Files modified:** 1 (`70-CI-EVIDENCE.md`, created)

## First section (per this plan's `<output>` contract)

- `PUSHED_SHA = e70e31fba9039133a153a5bba16577d7b2f889c1`
- `ORIGIN_BEFORE = ABSENT`
- `DECOY = ABSENT`
- `RUN_ID = 34742047126`
- `RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/34742047126`
- `JOB_COUNT = 12`
- `NON_SUCCESS_JOBS = 0`
- `CI_RUFF_VERSION = 0.16.6`
- `SC5_VERDICT = MET`
- `PHASE_SC_ROLLUP = ALL_MET`

The run was all green — no failing job, no NOT-MET verdict, nothing awaiting the owner.

## Accomplishments

- Gated on wave 5's evidence: all eight verdict keys (`SC1_VERDICT`, `SC2_VERDICT`, `LEG_A_VERDICT`, `LEG_C_VERDICT`, `LEG_E_VERDICT` from 70-10; `LEG_B_VERDICT`, `LEG_D_VERDICT` from 70-11; `DOC23_VERDICT` from 70-12) were `MET` with no `## HALT` heading in any of the three evidence files, before anything was pushed.
- Ran the gate quartet on the tip in the provisioned worktree venv (Python 3.13.13, matching baseline): `uv lock --check`, `uv run ruff check .`, `uv run black --check .`, `uv run mypy typsphinx/`, and the full `LC_ALL=C uv run pytest -q -p no:cacheprovider` suite (1547 passed, 1 skipped) — all exit 0.
- Re-measured the branch census immediately before the push: `gsd/v0.9.4-milestone` did not exist locally or on origin, so `DECOY = ABSENT` and constraint 9's fast-forward/symbolic-ref/delete sequence was never invoked.
- Confirmed tip identity: the pushed tree is byte-identical to this worktree's HEAD outside `.planning/`, `pyproject.toml` still reads `version = "0.9.2"`, `.github/workflows/` is unchanged since `PHASE_BASE_SHA`, no tag points at the tip, and the lock's ruff version (`0.16.6`) matches the baseline.
- Pushed for the first time: `git push --no-follow-tags -u origin gsd/v0.9.4-typing-modernization`, creating the origin head at `PUSHED_SHA` with upstream tracking (`branch.…remote = origin`, `branch.…merge = refs/heads/gsd/v0.9.4-typing-modernization`); origin lists the `v0.9.2` tag and no `v0.9.4` tag; GitHub's pull-request hint was not acted on.
- Dispatched `gh workflow run CI --ref gsd/v0.9.4-typing-modernization` exactly once and located the run (`34742047126`) by `headSha` = `PUSHED_SHA` and `createdAt` after `PUSH_AT` — no registration lag, resolved on the first list query.
- Waited in the foreground (`timeout 590 gh run watch … --interval 30`, no `run_in_background`) until the run reached `status: completed`, `conclusion: success` — inside the first watch window.
- Transcribed all 12 jobs by name and conclusion (all `success`), naming both `windows-latest` and both `macos-latest` lanes individually, and quoted ruff's verdict from the `Lint and Format Check` job's `Run lint with tox` step: `CI_RUFF_VERSION = 0.16.6`, equal to the lock at the pushed tip.
- Confirmed `DISPATCH_COUNT = 1` (no second dispatch) and `RELEASE_RUNS_AT_PUSHED = 0` (no `release.yml` run touched this SHA).
- Rolled up all five Phase 70 success criteria from committed evidence: `PHASE_SC_ROLLUP = ALL_MET`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — gate on wave 5, gate quartet, census, push, dispatch** - `ef42fa7a` (docs)
2. **Task 2: Observe CI to completion, transcribe jobs, roll up SCs** - `d5a7eb45` (docs)
3. **Fix — bare `CI_RUFF_VERSION` key line** - `4b79fa3e` (fix; see Deviations)

_No `70-13` plan-metadata commit was produced separately: this plan's own `<worktree_provisioning>` note states its evidence-file commits land after the push and touch only `.planning/`, which is exactly the shape of the three commits above. The final SUMMARY commit (below) is the metadata commit._

## Files Created/Modified

- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CI-EVIDENCE.md` — created; the wave-6 gate, gate quartet, census/decoy handling, tip identity, push, dispatch, run transcript, ruff verdict and SC roll-up.

## Decisions Made

- `DECOY = ABSENT`: the branch census (run immediately before the push, per constraint 9) found no `gsd/v0.9.4-milestone` locally or on origin. No fast-forward/symbolic-ref/delete sequence was exercised in this run.
- No second CI dispatch was made or considered — the single run completed inside the first foreground watch window, all green.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `CI_RUFF_VERSION` evidence line carried a trailing explanation, breaking key extraction**
- **Found during:** Task 2, self-check re-run of the automated `<verify>` block via a scratch script (`gsd_run`-equivalent `sed -n "s/^KEY = //p"` extraction)
- **Issue:** The first draft of `70-CI-EVIDENCE.md` wrote `CI_RUFF_VERSION = 0.16.6 — equal to \`LOCK_RUFF_VERSION_TIP\` (0.16.6).` on one line. This plan's `<worktree_provisioning>` note ("Evidence key lines hold the bare value only... Put any explanation on the next line") and the `sed`-based `k()` extractor both require the bare value alone on the `KEY = value` line. The trailing text made `CR="$(k CI_RUFF_VERSION)"` capture the whole explanatory sentence instead of `0.16.6`, which would have failed the `[ "$CR" = "$(k LOCK_RUFF_VERSION_TIP)" ]` comparison in Task 2's `<verify>`.
- **Fix:** Moved the explanation to a parenthetical line below the bare `CI_RUFF_VERSION = 0.16.6` key line.
- **Files modified:** `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CI-EVIDENCE.md`
- **Verification:** Re-ran both tasks' `<verify>` automated blocks as standalone scripts after the fix — both printed `PASS` with no non-zero exit.
- **Committed in:** `4b79fa3e`

---

**Total deviations:** 1 auto-fixed (1 bug — evidence-format correctness, caught before it could mask a real CI mismatch).
**Impact on plan:** No scope creep; the fix only corrected the evidence file's own internal consistency, which the plan's own `<verify>` block would otherwise have failed on a genuine re-run.

## Issues Encountered

None beyond the deviation above. `gh auth status` and `git ls-remote --heads origin refs/heads/main` both succeeded before Task 1 began, satisfying its `<precondition>`. `RUN_ID`'s run resolved on the first `gh run list` query — no registration lag was observed. The CI run completed inside the first `gh run watch` foreground window (well under the plan's 90-minute cap).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 70 is now fully evidenced: `PHASE_SC_ROLLUP = ALL_MET` across SC#1..SC#5, and the milestone branch is on `origin` with a completed, all-green three-OS CI run (milestone invariant #5). No blockers. Phase 71 (v0.9.4 Close Prep, prep-only, unpublished) can proceed — it re-verifies the masked-AST equality on its own close tip and prepares the merge PR behind constraint 10's checksum fence, per ROADMAP.

## Self-Check: PASSED

- `[ -f .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CI-EVIDENCE.md ]` → FOUND
- `git log --oneline --all --grep="70-13"` → returns `ef42fa7a`, `d5a7eb45`, `4b79fa3e` (≥1 commit)
- Task 1 and Task 2 `<acceptance_criteria>` and `<verify>` automated blocks were re-run as standalone scripts after the final fix commit — both printed `TASK1 VERIFY: PASS` / `TASK2 VERIFY: PASS` with exit 0.
- Plan-level `<verification>` re-confirmed: canonical branch on origin at `PUSHED_SHA` with tracking, no decoy, no tag; one `workflow_dispatch` CI run at `PUSHED_SHA` completed with every job green, both `windows-latest` and both `macos-latest` lanes named, ruff's verdict quoted from `Run lint with tox` at the lock's version; all five success criteria rolled up `MET`.

---
*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Completed: 2026-09-13*
