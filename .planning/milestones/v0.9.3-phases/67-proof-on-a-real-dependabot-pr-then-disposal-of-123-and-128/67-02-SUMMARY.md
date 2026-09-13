---
phase: 67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128
plan: 02
subsystem: infra
tags: [dependabot, github-actions, ci, evidence-only, uv, ruff, nixos]

# Dependency graph
requires:
  - phase: 67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128
    provides: "67-01's DEP02_VERDICT = MET, PROOF_SHA, SC2_BRANCH = can, MECHANICAL_CLOSE = none (wave-1 gate)"
provides:
  - "#138 (ruff 0.15.20 -> 0.16.6) merged into main as a two-parent merge commit MERGE_SHA_138, on the owner's go-ahead (D-03)"
  - "SC#3 merits recorded from live measurements: dev-extra scope, no new violation on main or the FHS-run milestone tip, REL-12 conflict-free with a valid lock, NIX-01 consistency statement"
  - "D-04 divergence recorded (not fixed): main's CI lints RUFF_VERSION_138 while the milestone worktree shim still reports RUFF_VERSION_MILESTONE until REL-12"
affects: [67-04-PLAN.md, 67-05-PLAN.md, 69-REL-12]

# Actuals (#2632)
actuals:
  tokens: 4315
  tasks: 3
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns: ["evidence-only phase: KEY = value bare lines in a phase evidence markdown, no code/test file", "checkpoint:decision with gate=blocking-human before an irreversible merge, resumed via coordinator relay"]

key-files:
  created:
    - .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-RUFF-EVIDENCE.md
  modified: []

key-decisions:
  - "Owner answered 'merge' at the Task 2 checkpoint:decision (gate=blocking-human), relayed verbatim by the coordinator; OWNER_DECISION_138 and DECIDED_AT_138 were recorded from that reply before any further action, and the gate was fully re-asserted from fresh commands (never from the checkpoint relay) before the merge command ran."
  - "HEAD_MOVED = no throughout: #138's head stayed at 88088071e02a7411800f504e06b1ded9d6891cc7 (equal to PROOF_SHA) from Task 1's read through the merge in Task 3, so the moved-head branch and its FHS re-measurement were never exercised."
  - "Merge executed with exactly gh pr merge 138 --merge --match-head-commit HEAD138, no other flags, producing a two-parent commit changing only pyproject.toml and uv.lock."

patterns-established:
  - "Pattern (from Phases 66/67-01): KEY = value bare lines in the evidence file, re-assertable via sed -n 's/^KEY = //p' — a bare line must not carry trailing prose or the sed-based verify extracts the whole remainder of the line, not just the value."

requirements-completed: []

coverage:
  - id: D1
    description: "Wave-1 gate and D-03 pre-merge gate for #138: head re-read, mergeStateStatus CLEAN, all six required checks success, SC#3 merits (dev-extra scope, Lint conclusion, FHS ruff check at RUFF_VERSION_138 with All checks passed!, PyPI latest, empty grep), REL-12 merge-tree + uv lock --check both exit 0, NIX-01/D-04 statements — all recorded before the owner was asked"
    requirement: DEP-05
    verification:
      - kind: other
        ref: "gh pr view 138; gh api .../check-runs; FHS-run ruff --version and ruff check .; git merge-tree; uv lock --check — recorded in 67-RUFF-EVIDENCE.md sections through '## NIX-01 interaction and D-04 divergence'"
        status: pass
    human_judgment: false
  - id: D2
    description: "#138 merged into main as a two-parent merge commit on the owner's explicit go-ahead, with the gate re-asserted immediately before the merge from fresh commands, and D-04 (milestone branch does not absorb main) verified after"
    requirement: DEP-05
    verification:
      - kind: other
        ref: "gh pr merge 138 --merge --match-head-commit; git rev-list --parents; git merge-base --is-ancestor; git merge-tree — recorded in 67-RUFF-EVIDENCE.md '## Owner decision (#138)' through '## Handoff to 67-04'"
        status: pass
    human_judgment: false

duration: 11min (active; excludes the checkpoint wait for the owner's reply)
completed: 2026-09-12
status: complete
---

# Phase 67 Plan 02: Merge of #138 (ruff 0.15.20 -> 0.16.6) into main, owner-approved Summary

**#138 merged into `main` as a two-parent commit `cf3305ce` after a fully re-measured D-03 pre-merge gate and SC#3 merit set — the owner answered "merge" at a `gate="blocking-human"` checkpoint, and D-04's divergence (milestone shim still reports `0.15.20` until REL-12) is recorded, not fixed.**

## Performance

- **Duration:** 11 min (active work; excludes the wall-clock time the checkpoint spent waiting for the owner's reply)
- **Started:** 2026-09-12T13:29:00Z (approx.)
- **Completed:** 2026-09-12T13:39:32Z
- **Tasks:** 3 (1 tracer, 1 checkpoint:decision, 1 auto)
- **Files modified:** 1 (created)

## First section (per plan `<output>`)

- OWNER_DECISION_138 = merge
- HEAD138 = 88088071e02a7411800f504e06b1ded9d6891cc7
- HEAD_MOVED = no
- RUFF_VERSION_138 = 0.16.6
- MILESTONE_RUFF_CHECK = pass
- MERGE_SHA_138 = cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a
- MERGED_AT_138 = 2026-09-12T13:37:03Z
- REL12_POSTMERGE_EXIT = 0

No `## HALT` heading was ever written in this plan's evidence file.

## Accomplishments
- Read the wave-1 gate from `67-PROOF-EVIDENCE.md` (`DEP02_VERDICT = MET`, no HALT) and the D-03 pre-merge gate for #138: OPEN at `HEAD138` with `mergeStateStatus` CLEAN, `MAIN_BEFORE_138` fetched, branch protection's six contexts read, and `HEAD_MOVED = no` (head unchanged since 67-01's proof).
- Measured SC#3's six merits live: `ruff` confined to the `dev` extra with no `[project] dependencies` entry; the exact range-bump diff; `Lint and Format Check` success on #138's own CI; an FHS-run `ruff check .` at `RUFF_VERSION_138` (`0.16.6`) on the milestone tip printing `All checks passed!` / `exit:0`; PyPI's latest (`0.16.7`, one patch ahead); and an empty `git grep` for the milestone's own ruff version elsewhere in the tree.
- Ran the REL-12 merge simulation (`git merge-tree` exit 0, exported tree, `uv lock --check` exit 0) and recorded the NIX-01/D-04 statements (milestone shim stays at `0.15.20` until REL-12 absorbs #138's lock).
- Stopped at the `checkpoint:decision` (`gate="blocking-human"`) and, on the owner's relayed `merge` reply, recorded `OWNER_DECISION_138`/`DECIDED_AT_138`, ran the idempotency check (PR was OPEN, `ALREADY_MERGED_138 = no`), fully re-asserted the gate from fresh commands (never from the checkpoint relay), and merged with exactly `gh pr merge 138 --merge --match-head-commit HEAD138`.
- Verified the resulting two-parent merge commit `cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a` changes exactly `pyproject.toml` and `uv.lock`, pins `RUFF_VERSION_138`, is on `origin/main`, and is NOT an ancestor of the milestone branch (D-04); confirmed `REL12_POSTMERGE_EXIT = 0` against the post-merge `origin/main`.
- Snapshotted dependabot's open-PR list, the Dependabot Updates run history, and #123/#128 read-only after the merge — #138 dropped from the open list, #123 and #128 unchanged.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: wave-1 gate, D-03 pre-merge gate and SC#3 merits for #138** - `74ad1f9f` (docs)
2. **Task 2: checkpoint:decision (gate="blocking-human")** - no commit (checkpoint only); owner answered "merge"
3. **Task 3: Re-assert the gate, merge #138, record main and dependabot after it** - `72162d19` (feat)

**Plan metadata:** committed separately (this SUMMARY + REQUIREMENTS.md, if any changes) after this file is written.

## Files Created/Modified
- `.planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-RUFF-EVIDENCE.md` - full D-03 gate, SC#3 merits, REL-12 simulation, NIX-01/D-04 statements, owner decision, merge record, post-merge main and dependabot snapshots, handoff to 67-04.

## Decisions Made
- Every value recorded at Task 3 (the re-asserted gate, the idempotency check, the merge, and the post-merge state) came from fresh commands run in this plan — none was copied from the Task 2 checkpoint relay, per the coordinator's explicit instruction and D-03's own discipline.
- The gate re-assertion found no difference from Task 1's measurements (origin/main unchanged, #138 still OPEN/CLEAN at the same head, all six checks still success), so the merge proceeded without triggering the "state changed after decision" HALT path.
- `gh pr merge 138 --merge --match-head-commit "$HEAD138"` was run with exactly those flags — no `--admin`, `--auto`, `--squash`, `--rebase` or `--delete-branch` — consistent with the DEP-05 prohibition against bypassing branch protection.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None. `HEAD_MOVED` stayed `no` throughout, so the moved-head branch (step 4 of Task 1) was never exercised in this run — it is documented in the evidence file as "not taken."

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `main` is now at `MERGE_SHA_138 = cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a`, carrying ruff `0.16.6` in `pyproject.toml`'s `dev` extra and `uv.lock`.
- 67-04 (close #123 as superseded) can proceed once it re-snapshots #123's own thread — this plan snapshotted `headRefOid`/`updatedAt` unchanged, but 67-04 must read live, not from this SUMMARY.
- 67-03 (close #128) is unaffected by this plan; #128's own snapshot here is also unchanged.
- 67-05 records the final DEP-02/DEP-05 closure and the SC#4 grouped-update coverage gap, after both 67-03 and 67-04 land.
- No blockers or concerns carried forward. DEP-05 itself does not close here (`requirements-completed: []`) — it closes in 67-05.

## Self-Check: PASSED

- FOUND: `.planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-RUFF-EVIDENCE.md`
- FOUND: commit `74ad1f9f` (Task 1)
- FOUND: commit `72162d19` (Task 3)

---
*Phase: 67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128*
*Completed: 2026-09-12*
