---
phase: 53-template-registry-foundation
plan: 10
subsystem: infra
tags: [ci, github-actions, gh-cli, evidence, milestone-branch]

# Dependency graph
requires:
  - phase: 53-05
    provides: byte-identity RED-evidence baseline and the first CI-evidence artifact shape
  - phase: 53-08
    provides: WR-01/WR-02 robustness fixes (container-shape guard, truthy-unusable-template-field guard)
  - phase: 53-09
    provides: REQUIREMENTS.md TPL-01/TPL-05/CONF-16 traceability corrections
provides:
  - "gsd/v0.9.0-per-document-templates on origin at 35ee8a0e (48c957cd..35ee8a0e fast-forward)"
  - "A completed workflow_dispatch CI run (31884774067) certifying 35ee8a0e with all 12 jobs success"
  - "A staleness-assertion + positive-content-proof pattern in 53-CI-EVIDENCE.md, re-runnable by any future round"
affects: [54-one-bundle-rule, 55-v0.8.0-derived-defects, 57-v0.9.0-release-prep]

actuals:
  tokens: 4300
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Three-fact currency assertion (remote-agreement / staleness-log-empty / positive-content-grep) for CI evidence that ages"
    - "Match CI runs on (name, event, headSha) tuple, never on recency -- a same-push Link Check run is a decoy"

key-files:
  created: []
  modified:
    - .planning/phases/53-template-registry-foundation/53-CI-EVIDENCE.md

key-decisions:
  - "Recorded 33 for the _template.typ file count, not the plan's stale '32' -- test_registry_prewrite_validation_gate.py (added by 53-06/53-07) is a legitimate net-growth addition, explained in the artifact rather than silently overwritten or hidden"
  - "Left Run 1/Run 2 sections from the prior round untouched; appended this round as a new dated section per the plan's explicit instruction not to edit history"

patterns-established:
  - "Currency rule published in the artifact itself: .planning/docs/CHANGELOG.md-only commits after the certified head do not invalidate; typsphinx/tests commits do and require re-push + re-dispatch"

requirements-completed: [TPL-01, TPL-03, TPL-04, TPL-05, CONF-14, CONF-15, CONF-16, CONF-17, CONF-18]

coverage:
  - id: D1
    description: "gsd/v0.9.0-per-document-templates pushed to origin, advancing the stale 48c957cd tip to 35ee8a0e (fast-forward, no force, no PR)"
    requirement: "TPL-01"
    verification:
      - kind: other
        ref: "git ls-remote --heads origin gsd/v0.9.0-per-document-templates -> 35ee8a0ee8a4f8701c99a6596be8e37d975de307"
        status: pass
    human_judgment: false
  - id: D2
    description: "workflow_dispatch CI run 31884774067 over 35ee8a0e completed with conclusion success on all 12 jobs, including both windows-latest and both macos-latest test legs"
    requirement: "CONF-18"
    verification:
      - kind: other
        ref: "gh run view 31884774067 --json jobs -> 12/12 conclusion:success"
        status: pass
    human_judgment: false
  - id: D3
    description: "Staleness assertion recorded empty and positive-content proof recorded present for the certified head, closing SC#5 on falsifiable evidence rather than a bare 'a run succeeded' claim"
    verification:
      - kind: other
        ref: "git log 35ee8a0e..gsd/v0.9.0-per-document-templates -- typsphinx/ tests/ (empty); git show 35ee8a0e:typsphinx/template_registry.py | grep -c '...' -> 1; git show 35ee8a0e:.planning/REQUIREMENTS.md | grep -c '| TPL-01 | Phase 53 | Complete |' -> 1"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-08-15
status: complete
---

# Phase 53 Plan 10: Milestone Branch CI Currency Summary

**Pushed `gsd/v0.9.0-per-document-templates` to `origin` at the wave-8 tip (`35ee8a0e`, carrying plan 53-08's and 53-09's commits) and dispatched a fresh `workflow_dispatch` CI run (31884774067) that completed 12/12 jobs `success`, closing SC#5 on evidence that proves it certifies the code that ships rather than a stale run a later commit had already overtaken.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-08-15T21:20:00+09:00 (approx., worktree provisioning)
- **Completed:** 2026-08-15T21:55:00+09:00 (approx.)
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments

- Measured the pre-push candidate SHA (`35ee8a0e`) by ref name (never `HEAD`, which in this
  isolated worktree returns the executor's own agent branch), confirmed both plan 53-08's and
  53-09's commits are present on it, and ran the four CI-parity gates plus an `LC_ALL=C` locale
  control locally before pushing anything.
- Pushed the milestone branch (`git push origin gsd/v0.9.0-per-document-templates`, fast-forward
  `48c957cd..35ee8a0e`, no force, no PR opened), dispatched `gh workflow run CI`, and identified
  the correct run (`31884774067`) among two runs the same push fired by matching all three of
  name `CI`, event `workflow_dispatch`, and `headSha` -- not by recency, which would have picked
  the decoy `Link Check` run instead.
- Captured all 12 job conclusions verbatim: every one `success`, including both `windows-latest`
  and both `macos-latest` `Test Python …` legs SC#5 names individually.
- Asserted currency at recording time with three independently re-run facts (remote-agreement,
  an empty `git log <head>..<branch> -- typsphinx/ tests/`, and a positive content grep proving
  which code the certified SHA carries) and published the invalidation rule that governs this
  evidence going forward, naming the worktree-merge hazard that will move the tip again.

## Task Commits

Each task was committed atomically:

1. **Task 1: Local CI-parity gates and the pre-push tip measurement** - `c01ebf8b` (docs)
2. **Task 2: Push the measured tip, dispatch CI, and capture per-lane conclusions** - `ecd78d0f` (docs)
3. **Task 3: Assert the evidence is not stale, and record the rule that keeps it that way** - `615e2893` (docs)

_No TDD tasks in this plan -- pure measurement and documentation, no source or test code touched._

## Files Created/Modified

- `.planning/phases/53-template-registry-foundation/53-CI-EVIDENCE.md` - gained a new
  "Gap-closure round 2 — 2026-08-15 (plan 53-10)" section (347 lines) with three subsections
  (Task 1/2/3 evidence), an extended per-success-criterion audit, and the published currency
  rule. The existing "Run 1" / "Run 2" sections from the prior round are byte-unchanged.

## Decisions Made

- **Recorded the real measured `_template.typ` file count (33), not the plan's stated expectation
  (32).** `git diff d1eff100 35ee8a0e --stat -- tests/` shows `test_registry_prewrite_validation_gate.py`
  (added by the 53-06/53-07 gap-closure round, which landed after the plan's acceptance criterion
  was written) references the string too. This is net growth of the regression net the count
  protects, not shrinkage, so it required an explanation rather than a code fix -- documented in
  the artifact per the plan's own "MUST NOT record any value a command did not produce" rule.
- **Left Run 1/Run 2 untouched, appended a new dated section.** Following the plan's explicit
  instruction and the precedent the prior round itself set (recording a failed Run 1 honestly
  rather than deleting it), this round's evidence is additive, not a rewrite.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - stale plan expectation vs. measured reality] `_template.typ` file count is 33, not the plan's stated 32**
- **Found during:** Task 3 (re-measuring standing invariants)
- **Issue:** The plan's acceptance criteria state `grep -rl "_template\.typ" tests/ | wc -l` returns
  32, based on the count at plan-authoring time (before 53-06/53-07's
  `test_registry_prewrite_validation_gate.py` fixture landed).
- **Fix:** Recorded the actual measured value (33) in the artifact with a full explanation --
  identified the new file via `git diff --stat`, confirmed it references `_template.typ`, and
  stated explicitly that this is net growth (a new regression-coverage file), not a shrinkage
  that would signal lost test coverage. No code or test was changed; this is a documentation
  correction analogous to the artifact's own existing Run 1/Run 2 honesty precedent.
- **Files modified:** `.planning/phases/53-template-registry-foundation/53-CI-EVIDENCE.md`
- **Verification:** `git diff d1eff10076af99d50b9bbb90acd6054a6b09762c 35ee8a0ee8a4f8701c99a6596be8e37d975de307 --stat -- tests/` and `grep -l "_template\.typ" tests/test_registry_prewrite_validation_gate.py` both re-run and cited verbatim in the artifact.
- **Committed in:** `615e2893` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 -- stale expectation corrected against measured reality)
**Impact on plan:** No scope creep, no code touched. The correction makes the artifact more accurate than the plan's own stated expectation, consistent with this plan's entire purpose (measuring rather than assuming).

## Issues Encountered

None. All three tasks executed cleanly: gates green, push fast-forwarded without rejection, CI run
identified unambiguously on the first attempt via the three-field match, all 12 jobs concluded
`success` on the first dispatch (no re-dispatch needed), and all three currency facts re-measured
without surprises.

## User Setup Required

None - no external service configuration required. `gh` was already authenticated (account
`YuSabo90002`, `workflow` scope present) per this plan's precondition; no new credential was
created.

## Next Phase Readiness

- SC#5 is closed on falsifiable, re-checkable evidence: the certified head, the staleness
  assertion, and the positive content proof are all in `53-CI-EVIDENCE.md`, along with the
  published invalidation rule for future rounds to apply without re-deriving it.
- **Currency caveat, stated explicitly per this plan's own rule:** this plan's own commits
  (`c01ebf8b`, `ecd78d0f`, `615e2893`) and this SUMMARY, plus whatever phase-tracking commits the
  orchestrator makes after merging this wave, all touch only `.planning/` -- they do NOT
  invalidate the `35ee8a0e` certification. Any future commit touching `typsphinx/` or `tests/`
  WOULD invalidate it and require a fresh push + `workflow_dispatch` + a new dated section.
- Phase 53 is otherwise unblocked for closeout: SC#1-SC#4 remain MET (re-confirmed this round,
  unchanged in substance), and SC#5 moves from "stale" (as `344b9510`'s re-verification scored it)
  to "MET" on this round's own run.
- No blockers for Phase 54, which depends on Phase 53 completing first per the milestone's one
  hard ordering constraint.

---
*Phase: 53-template-registry-foundation*
*Completed: 2026-08-15*
