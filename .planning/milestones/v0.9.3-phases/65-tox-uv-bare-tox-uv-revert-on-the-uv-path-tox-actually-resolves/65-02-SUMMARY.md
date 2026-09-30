---
phase: 65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves
plan: 02
subsystem: toolchain
tags: [ci, github-actions, tox-uv, uv, push, workflow-dispatch]

# Dependency graph
requires:
  - phase: 65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves (plan 01)
    provides: the four-file revert commit (REVERT_SHA) and TOX-01..TOX-03 MET, gating this plan's push
provides:
  - origin/gsd/v0.9.3-toolchain-and-dependency-update-repair advanced (fast-forward) to the post-revert tip
  - one workflow_dispatch CI run (34681968010) completed all-green on that tip
  - 65-CI-EVIDENCE.md — wave-1 gate, branch census, constraint-13 fence, push, dispatch, 12-job census, per-lane uv resolution vs the pre-revert baseline, ruff's CI verdict, TOX-04 closure
affects: [65 (phase verification, TOX-04 now MET), the orchestrator's post-merge main-checkout re-sync (D-05)]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 5160
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Push-then-dispatch-then-observe-in-foreground sequence mirrored from Phase 64 P04, re-measuring the branch census and constraint-13 fence live rather than trusting planning-time notes"
    - "Per-lane uv-path table (baseline vs. new venv> line) as the observational proof that tox-uv's bundled discovery branch, not the setup-uv PATH branch, is what CI now resolves"

key-files:
  created:
    - .planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-CI-EVIDENCE.md
  modified: []

key-decisions:
  - "No gsd/v0.9.3-milestone decoy existed at this plan's re-measurement (neither locally nor on origin) — the branch census found nothing to delete and nothing to halt on, unlike the decoy-pair hazard the roadmap flagged for Phase 64."
  - "The constraint-13/D-06 fence's clause (c) collapsed to a no-op comparison in this instance: merge-base(HEAD, origin/main) equals origin/main itself, since HEAD had not diverged from main under typsphinx/ or .github/workflows/ at all this milestone — recorded as measured, not assumed."

requirements-completed: [TOX-04]

coverage:
  - id: D1
    description: "Fast-forward push of the canonical branch to the post-revert tip, gated on wave 1's proven revert (REVERT_SHA ancestor of HEAD, TOX-01..TOX-03 MET, no DIVERGENT), with the constraint-13/D-06 four-file fence held over the pushed tip and no decoy branch present"
    requirement: "TOX-04"
    verification:
      - kind: integration
        ref: "65-02-PLAN.md Task 1 <verify> automated block (re-run live against the pushed tip, all conditions PASS)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Exactly one workflow_dispatch CI run (34681968010) dispatched on the pushed tip, observed in the foreground to completion: all 12 jobs success, both windows-latest and both macos-latest lanes named individually, ruff's verdict quoted from Lint and Format Check / Run lint with tox, per-lane uv resolution tabulated against the Phase 64 pre-revert baseline (run 34618719267) showing the bundled .venv uv now resolves on every lane instead of hostedtoolcache"
    requirement: "TOX-04"
    verification:
      - kind: integration
        ref: "65-02-PLAN.md Task 2 <verify> automated block (re-run live against the completed run, all conditions PASS)"
        status: pass
    human_judgment: false

duration: 13min
completed: 2026-09-12
status: complete
---

# Phase 65 Plan 02: Push, Dispatch, and Observe CI Summary

**One fast-forward push put the wave-1 revert on `origin`, and one `workflow_dispatch` CI run completed all 12 jobs green — including both Windows and both macOS lanes — with every test lane and the lint job now resolving tox-uv's bundled `.venv/bin/uv` instead of setup-uv's `hostedtoolcache` copy, closing TOX-04.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-09-12T07:53:00Z
- **Completed:** 2026-09-12T08:06:07Z
- **Tasks:** 2 completed
- **Files modified:** 1 (`65-CI-EVIDENCE.md`, created and then extended)

## Accomplishments

- Re-verified wave 1's gate live (`REVERT_SHA` an ancestor of HEAD, TOX-01..TOX-03 MET, zero DIVERGENT headings), confirmed the worktree head check and Phase 64 shims, and ran the required provisioning (`uv sync --extra dev` then `--locked`, exit 0) before touching origin.
- Re-measured the `gsd/v0.9.3*` branch census live: no `gsd/v0.9.3-milestone` decoy exists locally or on origin, so there was nothing to delete and no halt condition.
- Held the constraint-13/D-06 four-file fence over the tip: the revert commit lists exactly `pyproject.toml`, `tests/test_toolchain_config_gate.py`, `tox.ini` and `uv.lock`; no later commit touches any fenced path; nothing under `typsphinx/` or `.github/workflows/` differs from the merge-base with `origin/main`; no tracked file outside `.planning/` names `TOX_UV_PATH`.
- Pushed `gsd/v0.9.3-toolchain-and-dependency-update-repair` to `origin` as a fast-forward (`7afbf5b2…` → `d9c75553…`), with no force, no tag, and no other ref, and dispatched exactly one `gh workflow run CI --ref …`, resolving it to run `34681968010` at the correct `headSha`.
- Waited in the foreground (no `run_in_background`) until the run reached `completed`/`success`, then transcribed all 12 job conclusions, named both `windows-latest` and both `macos-latest` lanes individually, and quoted ruff's and black's verdicts verbatim from `Lint and Format Check` / `Run lint with tox`, set beside the local run in `65-REVERT-EVIDENCE.md`.
- Tabulated the `venv>` uv path for all six test lanes plus the lint job against the Phase 64 pre-revert baseline (run `34618719267`): every lane moved from `hostedtoolcache` (setup-uv's PATH branch) to the runner checkout's own `.venv` uv (tox-uv's bundled branch) — no lane still names `hostedtoolcache`.
- Confirmed no `release.yml` run carries the pushed SHA and that exactly one `workflow_dispatch` CI run exists at that SHA, then closed the requirement table: TOX-04 MET.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — wave-1 gate, head check and provisioning, branch census, constraint-13 fence, fast-forward push, dispatch CI exactly once** - `fe45b392` (docs)
2. **Task 2: Observe the run to completion in the foreground, transcribe the twelve-job census, quote ruff's CI verdict, record per-lane uv resolution** - `a7713886` (docs)

**Plan metadata:** committed separately, see below.

_Note: Both tasks touch only the evidence markdown — no production code changes in this plan (constraint: this plan produces no code symbol and no tracked file other than the evidence)._

## Files Created/Modified

- `.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-CI-EVIDENCE.md` - wave-1 gate, head check/provisioning, branch census, tip identity and constraint-13 fence, push, dispatch, run, job census, windows/macos lane sub-tables, ruff's verdict, uv resolved on CI, comparison with the pre-revert baseline, no-release-run check, dispatch count, requirement closure (TOX-04 MET)

## Decisions Made

- No decoy branch existed at this plan's own re-measurement (Constraint 9 requires re-measuring, never trusting the planning-time census) — recorded as a fact, not assumed from the plan's own planning-time table.
- Constraint-13 fence clause (c) was measured exactly as written even though it reduced to comparing HEAD against `origin/main` itself in this instance (the merge-base of the two is `origin/main`'s own tip) — no shortcut was taken on the grounds that the comparison "obviously" holds.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' automated `<verify>` blocks passed on the first attempt after Task 2's evidence-writing self-correction below.

### Auto-fixed Issues

**1. [Rule 1 - Bug in my own evidence draft] Literal `Run linters` string embedded in prose broke the Task 2 verify's zero-count assertion**
- **Found during:** Task 2's own `<verify>` automated block, which requires `grep -c 'Run linters' "$F"` to equal `0` (guarding against citing `release.yml`'s differently-named lint step)
- **Issue:** While drafting the `## ruff's verdict` section's closing sentence, I wrote "no `Run linters` string appears anywhere in this evidence" — which itself contains the literal string the gate forbids, tripping the count to 1.
- **Fix:** Rephrased the sentence to describe the same fact ("whose step name is absent from this evidence") without ever spelling out the forbidden literal.
- **Files modified:** `.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-CI-EVIDENCE.md`
- **Verification:** Re-ran `grep -c 'Run linters' 65-CI-EVIDENCE.md` → `0`; Task 2's full `<verify>` automated block re-run afterward, all conditions PASS.
- **Committed in:** `a7713886` (part of the Task 2 evidence commit — caught before the commit was made).

---

**Total deviations:** 1 auto-fixed (1 self-caught documentation bug in the evidence draft). **Impact:** No scope creep, no product/config change; caught and resolved entirely inside the verification loop before Task 2 was marked done.

## Issues Encountered

None beyond the deviation above (resolved inline).

## Authentication Gates

None — `gh auth status` was already authenticated (repo, workflow scopes) at plan start; no login flow was needed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `PUSHED_SHA = d9c7555323e843b5a389ed4354ce656d2fd05ca2` is now `origin`'s head for `gsd/v0.9.3-toolchain-and-dependency-update-repair`, and CI run `34681968010` completed all-green on it — TOX-04 is MET, closing Phase 65's requirement set (TOX-01..TOX-04, all MET).
- **Reminder to the orchestrator (65-02-PLAN.md "Orchestrator step after this plan merges"):** after this plan's worktree merges and before phase verification, re-sync the MAIN checkout's own `.venv` once with `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` (from `/home/yuta/Documents/typsphinx`, not from any worktree), recording `uv --version` and `.venv/pyvenv.cfg`'s `home`/`version_info` before and after, then appending the result as `## Addendum: main-checkout re-sync (orchestrator, D-05)` to `65-REVERT-EVIDENCE.md` and committing it as `docs(65): record main-checkout uv switch (D-05)`. This plan did not perform that step — it runs outside any worktree by design.
- Track B (`/gsd-plan-phase 66`) remains independent and can proceed in parallel; nothing in this plan touches Track B's files.

---
*Phase: 65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves*
*Completed: 2026-09-12*

## Self-Check: PASSED

- `65-02-SUMMARY.md` exists on disk — FOUND
- `65-CI-EVIDENCE.md` exists on disk — FOUND
- Commit `fe45b392` (Task 1 evidence + push + dispatch) — FOUND in `git log --oneline --all`
- Commit `a7713886` (Task 2 evidence + closure) — FOUND
- Both tasks' `<acceptance_criteria>` re-verified against HEAD (Tasks 1-2 `<verify>` automated blocks re-run live): PASS
- All plan-level `<verification>` bullets re-confirmed: PASS
- `plan_head_before: d9c7555323e843b5a389ed4354ce656d2fd05ca2`, `commits: 2` (measured via `git rev-list --count`)
