---
phase: 75-v0-9-6-release-prep-prep-only
plan: 05
subsystem: infra
tags: [release-prep, git-merge-tree, gh-api, ci, dependabot]

requires:
  - phase: 75-v0-9-6-release-prep-prep-only (plan 03)
    provides: the bumped tip (BUMP_COMMIT_SHA = 84edd348, version = "0.9.6") this plan trial-merges
provides:
  - A non-committing proof that merging origin/main into the bumped tip is clean, lint-green,
    and reproducible (same tree SHA twice)
  - main's current required contexts, strict flag, and allowed merge methods, compared against
    Phase 74's close reading
  - A fresh branch and open-pull-request census for the Dependabot ordering input the handoff needs
affects: [75-06, 75-07]

actuals:
  tokens: 2530
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Non-committing trial merge via `git merge-tree --write-tree`, run twice for idempotency,
       checked in a scratch extraction rather than in the worktree — the same pattern used at the
       v0.9.3/v0.9.4/v0.9.5 closes."

key-files:
  created:
    - .planning/phases/75-v0-9-6-release-prep-prep-only/75-PREFLIGHT-EVIDENCE.md
  modified: []

key-decisions:
  - "origin/main has not moved off the milestone base (MAIN_MOVED = no); the trial merge is
     therefore expected — and measured — to be a no-op, but the reading was taken live rather than
     assumed."
  - "main's required contexts, strict flag, and allowed merge methods were read live via gh api
     rather than carried from Phase 74's memory; they are unchanged (REQUIRED_CHECKS_UNCHANGED_SINCE_74
     = yes)."
  - "The branch and open-PR census was measured fresh at this plan's own execution time
     (2026-09-20T09:03:37Z): zero Dependabot branches, zero Dependabot PRs, zero PRs against the
     milestone branch. Neither the nine stale branches recorded at discussion time nor the zero
     measured during research was assumed — this reading stands on its own."

requirements-completed: []  # REL-15 is coverage-only in this plan by design; it closes at /gsd-complete-milestone.

coverage:
  - id: D1
    description: "Non-committing trial merge of origin/main into the bumped tip, checked twice for
      the same tree SHA, with the merged tree's own uv.lock and lint validated in scratch."
    requirement: REL-15
    verification:
      - kind: other
        ref: "75-PREFLIGHT-EVIDENCE.md Task 1 <automated> verify (re-run live during execution)"
        status: pass
    human_judgment: false
  - id: D2
    description: "main's protection/required-contexts/merge-method reads and a fresh branch and
      open-pull-request census, culminating in TRIAL_MERGE_VERDICT = MET."
    requirement: REL-15
    verification:
      - kind: other
        ref: "75-PREFLIGHT-EVIDENCE.md Task 2 verify, re-derived with count constructs that don't
          trip the zero-match grep -c exit-code trap in the literal <automated> text (see Deviations)"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-09-20
status: complete
---

# Phase 75 Plan 05: SC4 Trial Merge and Remote Reads Summary

**A non-committing `git merge-tree --write-tree` proves the release merge against `origin/main` is
clean and lint-green (ruff 0.16.7), and a live `gh api` read confirms `main`'s six required contexts
and strict protection are unchanged since Phase 74, with zero open Dependabot PRs at this reading.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-09-20T09:00:25Z
- **Completed:** 2026-09-20T09:06:38Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments
- `git merge-tree --write-tree HEAD origin/main` exits 0 and prints the identical tree SHA
  (`96d8ca9e9317b25a5ca57c76f7bd75ae88e5340f`) on two recorded runs and a third live verify run — no
  ref, branch, or commit created anywhere.
- The merged tree, extracted into scratch from its own tree object, passes `uv lock --check`, a
  locked `uv sync`, `ruff check .`, and `black --check .`, with the resolved ruff version (0.16.7)
  recorded for CI-skew awareness, and still carries `version = "0.9.6"`.
- `main`'s live protection read (6 required contexts, `strict: true`) is byte-identical to Phase
  74's close reading (`REQUIRED_CHECKS_UNCHANGED_SINCE_74 = yes`); all three merge methods are
  allowed on the repo, but every one of 103 first-parent precedent commits (including the five most
  recent milestone PRs) landed as a real merge commit.
- A fresh branch census (4 remote heads, 0 Dependabot branches, 0 decoys) and a fresh open-PR
  census (0 open, 0 Dependabot, a 5-row all-state control proving the zero is not a broken query, 0
  PRs against the milestone branch) were measured at `PR_CENSUS_AT = 2026-09-20T09:03:37Z`.
- `TRIAL_MERGE_VERDICT = MET`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — non-committing trial merge, twice for the same tree, merged-tree lock/lint** -
   `43a63bf6` (test)
2. **Task 2: main's protection, merge-method precedent, fresh branch/PR census, verdict** -
   `f9a238b9` (test)

**Plan metadata:** committed separately below (this SUMMARY + REQUIREMENTS.md).

## Files Created/Modified
- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-PREFLIGHT-EVIDENCE.md` - full evidence
  trail for both tasks: head check, tip identity, trial merge, merged-tree lock/lint, main
  protection, merge method, branch census, open-PR census, and the trial-merge verdict.

## Decisions Made
- No architectural decisions were needed. The one interpretive call was on how to run Task 2's
  verify oracle safely — see Deviations below; it did not change any recorded value, only how the
  check was re-derived.

## Deviations from Plan

### Auto-fixed Issues

None — no bug, missing functionality, or blocking issue was found in the implementation itself.

### Documented Non-Fix: Task 2 verify-oracle zero-match exit-code trap

**Found during:** Task 2, running the literal `<automated>` verify block after committing.

**Issue:** The Task 2 verify block contains `DB="$(printf '%s\n' "$HL" | grep -c 'refs/heads/dependabot/')"`
and the equivalent `DC="$(...)"` line for the `gsd/v0.9.6-milestone` decoy check. In bash, a plain
variable assignment from a command substitution (`var=$(cmd)`) propagates `cmd`'s own exit status as
the assignment's exit status. `grep -c` exits `1` when it counts zero matches (even though it prints
`0` to stdout). Because the recorded facts are genuinely `DEPENDABOT_BRANCHES = 0` and
`DECOY_ON_ORIGIN = 0` (correct — there are no Dependabot branches or decoys on `origin` at this
reading), the literal verify script's `&&` chain breaks at that exact assignment and the script
exits `1`, even though every fact it is checking is true. This is a verify-oracle format trap
(zero-count `grep -c` inside a `var=$(...) && ...` chain), not a defect in the evidence file or the
underlying measurement.

**Resolution:** I re-derived every assertion in the Task 2 verify block using count constructs that
don't trip this exit-code trap (`grep -c ... || true`, matching the intent of the original checks
exactly) and confirmed every single check passes, including the two that trip the trap
(`DEPENDABOT_BRANCHES = 0` matches the live read; `DECOY_ON_ORIGIN = 0` matches the live read). I did
not edit `75-05-PLAN.md` (plans are not mutated by the executor) and did not alter any recorded
value in `75-PREFLIGHT-EVIDENCE.md` to work around the trap — the recorded values are exactly what
the live `gh`/`git` commands produced.

**Verification:** `/tmp/.../scratchpad/verify_task2_safe.sh`, run against the committed evidence
file and live `gh`/`git` reads, printed `TASK2_VERIFY_PASS_SAFE` with every individual assertion
checked explicitly (see script for the full list). Every value it reads from
`75-PREFLIGHT-EVIDENCE.md` matches a live re-read.

**Committed in:** No code change — this is a verify-methodology note, not a fix to committed content.

---

**Total deviations:** 0 auto-fixed. 1 documented verify-oracle format trap (zero-count `grep -c`
inside a bash assignment chain), worked around during verification only, with no change to the
plan, the evidence file's recorded values, or the underlying facts.
**Impact on plan:** None on content. The oracle format trap is worth carrying forward as a pattern
to avoid in future plan-verify authoring (parallel to the known pytest-collection-count and
parenthesized-explanation oracle traps already on file).

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- SC4's trial-merge clause is discharged: the merge `/gsd-complete-milestone` will perform is
  proven clean and lint-green against `origin/main` as it stood at this reading, with zero refs
  written anywhere in the repository.
- The handoff (75-07) has measured, live-sourced answers for the merge PR: cleanliness, the exact
  six required contexts, the merge method precedent (real merge commit), and today's Dependabot
  ordering input (none pending — the ordering rule is conditional, not currently active).
- No pull request, tag, release, or workflow dispatch was created by this plan; the repository's
  refs, working tree, and remote are unchanged by it apart from the two commits to
  `.planning/phases/75-v0-9-6-release-prep-prep-only/75-PREFLIGHT-EVIDENCE.md` on the milestone
  branch itself.
- `origin/main` may still move before `/gsd-complete-milestone` runs (flagged assumption in the
  plan); the handoff carries the conditional re-read/update-merge step keyed on re-reading
  `origin/main` at that time.

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Completed: 2026-09-20*

## Self-Check: PASSED

- `test -f .planning/phases/75-v0-9-6-release-prep-prep-only/75-PREFLIGHT-EVIDENCE.md` → FOUND.
- `git log --oneline --all | grep -q 43a63bf6` → FOUND (Task 1 commit).
- `git log --oneline --all | grep -q f9a238b9` → FOUND (Task 2 commit).
- All `<acceptance_criteria>` for both tasks re-verified against live `gh`/`git` reads (see
  Deviations for the one verify-oracle note); all PASS.
- Plan-level `<verification>` bullets all confirmed: trial merge exits 0 / same tree SHA three
  times / no ref written; merged tree passes lock-check/sync/ruff/black in scratch and still
  carries 0.9.6; main's protection/contexts/strict/merge-methods recorded from live reads and
  compared against Phase 74; branch/Dependabot/open-PR census matches live reads with a non-empty
  control; `TRIAL_MERGE_VERDICT = MET`.
