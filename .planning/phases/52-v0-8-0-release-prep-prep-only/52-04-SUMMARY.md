---
phase: 52-v0-8-0-release-prep-prep-only
plan: 04
subsystem: ci
tags: [github-actions, workflow_dispatch, ruff, locale, windows, ci-authority]

requires:
  - phase: 52-01
    provides: version = "0.8.0" in pyproject.toml
  - phase: 52-02
    provides: curated ## [0.8.0] CHANGELOG entry
  - phase: 52-03
    provides: TestThreeMasterGate three-master goal-claim gate test
provides:
  - A dispatched, live workflow_dispatch CI run on the exact merged tip (headSha aaeec804),
    with every job's conclusion read and recorded verbatim
  - Three real, reproducible, pre-existing CI-only-visible defects discovered and root-caused
    (ruff import-sort violation; locale-dependent hardcoded-Japanese test baseline; Windows-only
    backslash-doubling in a warning message), filed to .planning/WINDOWS.md
  - Four independent no-irreversible-action observations (no tag, no PR, no unexpected
    release.yml run, ci.yml/typsphinx/ both untouched)
affects: [52-05, 52-06, 52-07, gsd-complete-milestone]

actuals:
  tokens: 9500
  tasks: 1
  commits: 1

tech-stack:
  added: []
  patterns:
    - "CI-dispatch-as-authority (D-08): push the milestone branch by pinned SHA, dispatch
      ci.yml by hand via workflow_dispatch, match the run by headSha, read every job."

key-files:
  created:
    - .planning/phases/52-v0-8-0-release-prep-prep-only/52-CI-EVIDENCE.md
  modified:
    - .planning/WINDOWS.md

key-decisions:
  - "Did not attempt to fix any of the three discovered defects: all three require editing
    tests/ files outside this plan's declared files_modified scope (52-CI-EVIDENCE.md only),
    the wave-parallel constraint under which this plan runs alongside sibling plans 52-05/52-06
    in separate worktrees. Filed to .planning/WINDOWS.md instead, per the executor's SCOPE
    BOUNDARY rule, and reported as a blocker for an explicit decision rather than silently
    retried or silently accepted as green."

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "A live workflow_dispatch CI run on the exact post-bump, post-CHANGELOG,
      post-gate-test merged tip (aaeec804), matched by headSha, with every job's conclusion
      read and recorded verbatim in 52-CI-EVIDENCE.md"
    requirement: REL-07
    verification:
      - kind: other
        ref: "gh run view 31855486993 --json jobs (recorded in 52-CI-EVIDENCE.md)"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#3's toolchain-half authority discharged — every job reports success"
    requirement: REL-07
    verification:
      - kind: other
        ref: "gh run view 31855486993 --json conclusion (recorded: failure, 8/12 jobs failed)"
        status: fail
    human_judgment: true
    rationale: "This deliverable is NOT met. The dispatched run is red on 8 of 12 jobs from
      three independent, real, pre-existing defects. A human decision is needed on how to
      proceed: authorize a fix-and-redispatch (this plan's declared scope does not permit
      editing tests/), or route the fix through a separate plan/phase before SC#3 can close."
  - id: D3
    description: "No irreversible action taken (no tag, no PR, no release.yml dispatch, ci.yml
      and typsphinx/ both untouched)"
    requirement: REL-07
    verification:
      - kind: other
        ref: "git tag -l v0.8.0 / git ls-remote --tags origin v0.8.0 / gh pr list / gh run
          list --workflow=release.yml (all recorded in 52-CI-EVIDENCE.md)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-15
status: blocked
---

# Phase 52 Plan 04: Dispatched CI Authority Run Summary

**Dispatched a live `workflow_dispatch` run on the exact merged tip (`aaeec804`) and found it
red — three independent, real, pre-existing defects (a `ruff` import-sort violation, a
locale-dependent hardcoded-Japanese test baseline, and a Windows-only warning-message
backslash-doubling bug) that only a live CI run could surface, none fixable within this plan's
declared single-file scope.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-08-15T00:52:00Z
- **Completed:** 2026-08-15T01:17:00Z
- **Tasks:** 1 of 2 (Task 1 attempted and recorded but its acceptance criterion — all-`success`
  — is not met; Task 2's content, which does not depend on Task 1's outcome, was folded into
  the same evidence file and is complete)
- **Files modified:** 2 (`52-CI-EVIDENCE.md` created, `.planning/WINDOWS.md` appended)

## Accomplishments

- Re-measured the branch position live (178 commits ahead of `origin`, not the stale 155/157/159
  figures carried in `52-CONTEXT.md`/`52-RESEARCH.md`/the planner's own count) and confirmed a
  clean fast-forward ancestry before pushing.
- Pushed the pinned merged tip `aaeec80439c7b5f0dfe5e0d64f4af83bd0550b3e` to
  `origin/gsd/v0.8.0-multi-master-composition` by explicit SHA (never `HEAD`, never `--force`),
  confirmed the fast-forward, and dispatched `ci.yml` by hand via `workflow_dispatch`, matched
  by `headSha` (run `31855486993`).
- Read every one of the twelve jobs' conclusions and root-caused all eight failures to three
  independent, real, reproducible, pre-existing defects — not flakiness — by reading the actual
  job logs individually across all affected lanes:
  1. `ruff` `I001` unsorted import block in `tests/test_builder.py:569` (Lint job only) — never
     checked locally on any prior commit, because `ruff` cannot execute on this NixOS machine at
     all (a filed, still-open toolchain defect).
  2. Hardcoded-Japanese baseline warning fragments in
     `tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved`
     failing against English-locale CI runners (all six OS/Python lanes + `Code Coverage`) — the
     diagnostic itself fires correctly, just in English, not Japanese.
  3. A Windows-only backslash-doubling defect in a warning message constructed by
     `TypstBuilder.post_process_images` / `_track_image()`, breaking
     `test_post_process_images_rehome_escape_relocates_with_warning` on both Windows lanes only
     — structurally invisible on this Linux development machine, the same class of defect that
     caught real cp1252/path-separator/OUT-02 bugs at prior milestone closes.
- Filed all three to the cross-phase defect register (`.planning/WINDOWS.md`, entries 3–5) so
  they stay visible and block `/gsd-ship` until resolved or waived.
- Recorded the four independent no-irreversible-action observations (empty `git tag -l v0.8.0`,
  empty `git ls-remote --tags origin v0.8.0`, zero open PRs, and a `release.yml` run listing
  showing nothing newer than the pre-existing v0.7.1 release run) with a `date -u` timestamp.
- Confirmed `ci.yml` and every file under `typsphinx/` remain untouched by this plan
  (`git diff --name-only` both empty).

## Task Commits

1. **Task 1 (attempted, recorded, not accepted as green): Push, dispatch, read every job** -
   `c87a9213` (docs) — records the pushed SHA, the dispatch, the full job table, the three
   root-caused defects, and the (independently true) no-irreversible-action observations that
   were originally Task 2's scope, folded into the same commit since they do not depend on
   Task 1's outcome.

**Plan metadata:** not yet created — this plan halts before the final metadata commit pending
a decision on how to proceed (see "Next Phase Readiness" below).

## Files Created/Modified

- `.planning/phases/52-v0-8-0-release-prep-prep-only/52-CI-EVIDENCE.md` — the full run
  transcript: pre-push confirmation, pushed SHA, push, dispatch, the twelve-job conclusion
  table, a root-cause section for each of the three defects with log excerpts and a
  job-to-defect mapping table, an escalation section, the no-irreversible-action observations,
  what the run does not cover, and the ledger entries filed.
- `.planning/WINDOWS.md` — three new entries (ids 3–5): two `kind: todo` (the Windows backslash
  defect, the locale-dependent baseline defect) and one `kind: lint-warning` (the ruff
  violation), all `phase: 52`, all `status: open`.

## Decisions Made

- **Did not attempt to fix any of the three discovered defects.** All three require editing
  `tests/test_builder.py` and/or `tests/test_state_guard_shapes_gate.py`, which sit outside this
  plan's declared `files_modified` scope (`52-CI-EVIDENCE.md` only) — the wave-parallel
  constraint this plan runs under, alongside sibling plans 52-05 and 52-06 in independent
  worktrees. The executor's own SCOPE BOUNDARY rule ("Only auto-fix issues DIRECTLY caused by
  the current task's changes... out-of-scope discoveries... log... do NOT fix them") applies:
  none of the three defects was introduced by this plan (`git diff --name-only -- typsphinx/`
  and `-- .github/` are both empty), so none is in scope to auto-fix here, even though the
  plan's own `<action>` text anticipates a fix-and-redispatch cycle (matching the Phase 46
  `46-04` precedent for a `ruff` `B904` violation). Filed to `.planning/WINDOWS.md` instead and
  reported as a blocker requiring an explicit decision.
- **Recorded the "no irreversible action" observations (Task 2's content) in the same commit as
  Task 1**, since they are independently true regardless of the CI run's outcome and do not
  require Task 1 to have succeeded.

## Deviations from Plan

### Not auto-fixed — filed as a blocker instead (see "Decisions Made" above)

**1. [Rule 4 territory / out-of-scope per SCOPE BOUNDARY] Dispatched CI run reports `failure`
for 8 of 12 jobs from three independent, real, pre-existing defects**
- **Found during:** Task 1 (push, dispatch, read every job)
- **Issue:** The authority run required by this plan's own acceptance criteria (`[.jobs[].conclusion]|unique == ["success"]`)
  is not achievable without editing `tests/` files this plan is not scoped to touch.
- **Fix:** None applied. Root-caused, documented with log excerpts, and filed to
  `.planning/WINDOWS.md` (entries 3–5).
- **Files that would need changing (not touched):** `tests/test_builder.py` (two separate
  defects: the ruff import-sort at line 569, and the Windows backslash-doubling assertion
  around line 555), `tests/test_state_guard_shapes_gate.py` (the locale-dependent baseline
  table, around line 781).
- **Commit:** `c87a9213` (the evidence commit; no fix commit exists)

---

**Total deviations:** 1 blocker filed, 0 auto-fixed.
**Impact on plan:** This plan's core success criterion (SC#3's toolchain-half authority,
discharged by an all-`success` CI run) is not met. No source or test file was touched — the
tree remains exactly as plans 52-01/52-02/52-03 left it. Nothing irreversible occurred.

## Issues Encountered

The executor's own local full-suite run (cited in this plan's `<upstream_state>`: "1170 passed,
5 skipped, exit 0") did not surface any of the three defects found here, because: (a) `ruff`
cannot execute at all on the local NixOS machine, so the import-sort violation was never
checked; (b) the local development environment's own locale yields the Japanese diagnostic
wording the test's baseline table hardcodes, so the mismatch against English-locale CI runners
was invisible locally; (c) the backslash-doubling defect is Windows-`pathlib`-specific and
structurally cannot reproduce on Linux. This is exactly the class of defect D-08 assigns CI
authority to catch, and exactly why this plan exists as a separate, mandatory dispatch step
rather than trusting the local run.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Blocked.** This plan's core deliverable — a live CI run proving the post-bump tree green
(SC#3's toolchain half) — is not achieved. `52-CI-EVIDENCE.md` fully documents the attempt, the
failure, and the root cause of every failing job; nothing was papered over.

**A decision is needed on how to proceed**, since this plan's declared scope does not permit the
fix:
1. **Authorize a fix-and-redispatch plan** (matching the Phase 46 `46-04` precedent) scoped to
   touch `tests/test_builder.py` and `tests/test_state_guard_shapes_gate.py`, fixing all three
   defects, then re-push and re-dispatch `ci.yml`, recording the second run alongside this one
   in `52-CI-EVIDENCE.md`.
2. **Widen this plan's own scope** to permit the fix directly, if the orchestrator judges the
   wave-parallel file-lock does not apply here (sibling plans 52-05/52-06 touch neither
   `tests/test_builder.py` nor `tests/test_state_guard_shapes_gate.py`, so a direct fix carries
   no file-level merge-conflict risk with them — but it is still outside this plan's own
   declared `files_modified`).
3. **Defer the fix**, accepting SC#3's toolchain-half authority as unmet for this dispatch and
   filing all three defects (already done, `.planning/WINDOWS.md` entries 3–5) for a later phase
   — but this leaves REL-07/SC#3 genuinely unproven until a green dispatch exists, which
   `/gsd-ship` and `/gsd-complete-milestone` would need to account for.

Plans 52-05 and 52-06 (local docs/corpus evidence and the SC#4 invariant sweep) are independent
of this outcome and can proceed regardless. Plan 52-07 (the mechanical post-authority-SHA
assertion) depends on this plan's accepted authority SHA existing, which does not yet exist.

## Self-Check: PASSED

- FOUND: `.planning/phases/52-v0-8-0-release-prep-prep-only/52-CI-EVIDENCE.md`
- FOUND: `.planning/phases/52-v0-8-0-release-prep-prep-only/52-04-SUMMARY.md`
- FOUND: commit `c87a9213` (CI evidence + WINDOWS.md ledger)
- FOUND: commit `a2a71e26` (this SUMMARY)
