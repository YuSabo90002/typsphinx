---
phase: 71-v0-9-4-close-prep-prep-only-unpublished
plan: 06
subsystem: release-prep
tags: [evidence, sc1-fence, masked-ast, ci, unpublished-shape]

# Dependency graph
requires:
  - phase: 70-typing-modernization-and-its-behaviour-identity-evidence
    provides: "the mask harness, PHASE_BASE_SHA (697a1132), the ten converted files, and the leg (a) table this plan re-measures against"
provides:
  - "SC#1 observation 2 of 2: the unpublished-shaped fence re-probed 40m12s after observation 1, across wave 2, the CI dispatch and the trial-merge pre-flight — unchanged"
  - "the phase-scoped product diff: empty over typsphinx/ and tests/ from PHASE_BASE_SHA, with a positively-controlled widened diff (CHANGELOG.md, +10/-0)"
  - "the post-dispatch planning-only proof: every commit after PUSHED_SHA touches only .planning/"
  - "D-11 part 1 on the close tip: no code change since Phase 70's CODE_FREEZE_ANCHOR, with a positive control across Phase 70's own range"
  - "D-11 part 2: Phase 70's masked-AST harness re-run live on the close tip against PHASE_BASE_SHA for all ten converted files, non-vacuously, cross-checked against Phase 70's leg (a) table"
affects: [71-07, "gsd-complete-milestone"]

# Actuals (#2632)
actuals:
  tokens: 7956
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Masked-AST equality re-run against a prior phase's recorded harness, hash-checked before use, never retyped"
    - "Positive-control pairing for every empty/absent probe result (v0.9.2 vs v0.9.3/v0.9.4, real code range vs empty close-tip diff)"

key-files:
  created: []
  modified:
    - .planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-SC1-INVARIANTS.md

key-decisions:
  - "Task 1's automated verify was run verbatim and its literal 'exactly one workflow_dispatch run at PUSHED_SHA' assertion fails (measures 2, not 1) — recorded as the owner-approved AMENDED reading from 71-CI-EVIDENCE.md, not edited around or silently passed."

requirements-completed: []  # D-09: REL-13 closes only at /gsd-complete-milestone, on the observed merge.

coverage:
  - id: D1
    description: "SC#1 observation 2 of 2: every observation-1 probe re-run at a later timestamp with the same positive controls; the unpublished-shaped fence holds"
    verification:
      - kind: other
        ref: "71-SC1-INVARIANTS.md § Observation 2 of 2 (live git/gh/curl probes, transcribed verbatim)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The phase-scoped product diff over typsphinx/ and tests/ is empty from PHASE_BASE_SHA, with a positively-controlled widened diff proving the anchor is real"
    verification:
      - kind: other
        ref: "71-SC1-INVARIANTS.md § The phase-scoped product diff"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every commit after PUSHED_SHA (the single CI dispatch) is .planning/-only"
    verification:
      - kind: other
        ref: "71-SC1-INVARIANTS.md § Commits after the CI dispatch"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-11 part 1: no code change since Phase 70's CODE_FREEZE_ANCHOR, on the close tip"
    verification:
      - kind: other
        ref: "71-SC1-INVARIANTS.md § Code freeze on the close tip (D-11 part 1)"
        status: pass
    human_judgment: false
  - id: D5
    description: "D-11 part 2: Phase 70's masked-AST harness re-run on the close tip for all ten converted files, non-vacuous, cross-checked against Phase 70's leg (a) table"
    verification:
      - kind: other
        ref: "71-SC1-INVARIANTS.md § Masked-AST re-run on the close tip (D-11 part 2), § Non-vacuity controls (D-11 part 2), § Cross-check with the Phase 70 leg (a) table"
        status: pass
    human_judgment: false
  - id: D6
    description: "The 71-04 dispatch-count anomaly (literal count 2 at PUSHED_SHA) is a known, owner-approved AMENDED reading, not a defect in this plan's work"
    verification: []
    human_judgment: true
    rationale: "This is a judgment about an owner decision recorded in 71-CI-EVIDENCE.md, not a fact this plan's own commands can adjudicate — the human should see the exact literal-vs-AMENDED split before signing off."

duration: 12min
completed: 2026-09-13
status: complete
---

# Phase 71 Plan 06: SC#1 Close-Tip Evidence — Observation 2, Product-Diff Fence, and D-11 Summary

**Second SC#1 observation, phase-scoped product diff and post-dispatch planning-only proof, and D-11's two-part "no code change slipped in" check — all MET on the close tip, with the known 71-04 dispatch-count discrepancy re-measured and recorded rather than papered over.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-09-13T09:11:31Z
- **Completed:** 2026-09-13T09:23:00Z (approx.)
- **Tasks:** 2 completed
- **Files modified:** 1 (`71-SC1-INVARIANTS.md`, plus this SUMMARY)

## First section (per plan `<output>` instruction)

```
OBS1_AT = 2026-09-13T08:31:24Z
OBS2_AT = 2026-09-13T09:11:36Z
PHASE_PRODUCT_FILES = CHANGELOG.md
POST_DISPATCH_PRODUCT_FILES = 0
CLOSE_CODE_FREEZE_DIFF_FILES = 0
D11_MASK_EQUAL_COUNT = 10
PHASE70_TABLE_MATCH = 10
D11_VERDICT = MET
```

No HALT heading was written anywhere in this plan's work.

## Accomplishments

- **Observation 2 of 2** re-ran every observation-1 probe (version line, local/remote tags, PyPI,
  GitHub Releases, release-workflow runs, pull requests) 40 minutes 12 seconds later, spanning
  wave 2 in full — the local green-tree proof, the phase's only push and CI dispatch, and the
  trial-merge pre-flight. Every probe reproduced the same positive control and the same result:
  the tree is still unpublished-shaped.
- **The phase-scoped product diff** over `typsphinx/` and `tests/` from `PHASE_BASE_SHA`
  (`f1f7d54a…`) is empty; the widened `--numstat` diff from the same anchor lists exactly
  `CHANGELOG.md` with 10 additions and 0 deletions, proving the anchor is real.
- **The post-dispatch planning-only proof**: every one of the 15 commits after `PUSHED_SHA`
  (`7a42bf99…`) touches only `.planning/`. No `release.yml` run exists at `PUSHED_SHA`.
- **D-11 part 1**: the last commit touching `typsphinx/` or `tests/` is still
  `CODE_FREEZE_ANCHOR` (`e721ff89…`), its diff to the close tip is empty, and the same pathspec
  lists exactly Phase 70's own ten converted files across Phase 70's own range (the positive
  control). The merge-base of HEAD and `origin/main` still equals `MILESTONE_BASE` — no `main`
  commit absorbed.
- **D-11 part 2**: Phase 70's masked-AST harness was extracted from `70-MASK-PILOT-EVIDENCE.md`
  and hash-checked (`11cdbeb6…`) against its recorded `MASK_HARNESS_SHA256` before use — never
  retyped. Re-run live on the close tip, all ten converted files' masked hashes equal their
  `PHASE_BASE_SHA` counterparts (`D11_MASK_EQUAL_COUNT = 10`), while all ten files' raw bytes
  genuinely differ from that base (`D11_RAW_DIFFER_COUNT = 10`) — the equality is not vacuous.
  Two independent mutation controls (a class rename, a non-`typing` import removal) both changed
  the hash (`CONTROL_RENAME_71 = DIFFER`, `CONTROL_IMPORT_71 = DIFFER`). Every close-tip hash was
  also found, byte-for-byte, in Phase 70's own leg (a) table, computed on the same CPython
  `3.13.13` interpreter (`PHASE70_TABLE_MATCH = 10`).

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — SC#1 observation 2 of 2, the phase-scoped product diff, the post-dispatch
   planning-only proof, and D-11 part 1 on the close tip** — `bb855abd` (docs)
2. **Task 2: D-11 part 2 — Phase 70's masked-AST harness re-run on the close tip** — `36d98fcd`
   (docs)

**Plan metadata commit:** recorded via `gsd-tools query commit` below.

## Files Created/Modified

- `.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-SC1-INVARIANTS.md` — appended
  `## Observation 2 of 2`, `## The phase-scoped product diff`, `## Commits after the CI dispatch`,
  `## Code freeze on the close tip (D-11 part 1)`, `## Masked-AST re-run on the close tip (D-11
  part 2)`, `## Non-vacuity controls (D-11 part 2)`, `## Cross-check with the Phase 70 leg (a)
  table`, and `## D-11 verdict`. No product-tree file was modified; `71-VERIFICATION.md` was not
  created.

## Decisions Made

None new — this plan follows `71-CONTEXT.md` D-05, D-10 and D-11 and Phase 69's precedent shape
exactly, with Claude's discretion limited to invocation mechanics (already exercised in Phase 70).

## Deviations from Plan

### Recorded, not auto-fixed (owner-approved reading, per project briefing note 3)

**1. [Owner-approved AMENDED reading] Task 1's literal dispatch-count assertion fails as written**
- **Found during:** Task 1, running the plan's own `<automated>` verify verbatim.
- **Issue:** The verify asserts `gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 50 --json headSha --jq '[.[] | select(.headSha == "$P")] | length'` equals `1`. The live, re-measured count at `PUSHED_SHA` (`7a42bf99…`) is `2`: run `34748483361` (success, `RUN_ID`) and the cancelled surplus run `34748491771`, both documented in `71-CI-EVIDENCE.md` and its "AMENDED 2026-09-13 — dispatch count" addendum.
- **Fix:** None applied — the plan was run verbatim, not edited, and no GitHub state (dispatch, cancel, delete) was touched. Per the owner's decision recorded in `71-CI-EVIDENCE.md`, this is read as "exactly one run at `PUSHED_SHA` concluded `success` and it is `RUN_ID`; the only other run is the cancelled `34748491771`," which was independently re-measured here as `SUCCESS_COUNT = 1` and the sole non-success run's `databaseId` equal to `34748491771`.
- **Files modified:** None (this is a verification-command reading, not a code or evidence-format issue).
- **Verification:** Both the plan's literal verify (exit `1`, recorded verbatim) and the AMENDED-form check (exit `0`) were run and their real outputs are transcribed in `71-SC1-INVARIANTS.md` § "Commits after the CI dispatch" and in this SUMMARY.
- **Committed in:** `bb855abd` (Task 1 commit, evidence includes both readings).

---

**Total deviations:** 1 (an owner-approved AMENDED reading of a pre-existing, already-documented anomaly from 71-04 — not a defect introduced by this plan).
**Impact on plan:** None on the substance of SC#1 or D-11: every other assertion in both tasks' verifies passed as written, including the ten-file masked-AST equality, the non-vacuity controls, and the code-freeze diff. The one non-matching assertion concerns a procedural GitHub Actions bookkeeping discrepancy the owner has already adjudicated, not the phase's technical claims.

## Verify Results (both tasks, run verbatim)

**Task 1's own `<automated>` verify, run exactly as written:**
```
$ bash <extracted Task 1 verify script>
exit: 1
```
The chain runs to completion via `&&` short-circuiting until the assertion
`[ "$(gh run list --workflow=ci.yml --branch "$BR" --event workflow_dispatch --limit 50 --json headSha --jq '[.[] | select(.headSha == "'"$P"'")] | length')" = 1 ]`, where the live count is `2`, not `1`. No `key not 0:` or `missing section:` message printed — every other checked condition passed; this is the sole point of failure, isolated and re-confirmed independently:
```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 50 --json headSha --jq '[.[] | select(.headSha == "7a42bf996b1aaca24a8b17346be78459e6d41e2b")] | length'
2
```

**The AMENDED-form scratch check (project briefing note 3), run separately, never substituted into the plan file:**
```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 50 --json headSha,conclusion,databaseId -q '[.[] | select(.headSha == "7a42bf996b1aaca24a8b17346be78459e6d41e2b" and .conclusion == "success")] | length'
1
$ gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 50 --json headSha,conclusion,databaseId -q '[.[] | select(.headSha == "7a42bf996b1aaca24a8b17346be78459e6d41e2b" and .conclusion != "success")] | map(.databaseId) | join(",")'
34748491771
```
Both conditions match the AMENDED reading (`SUCCESS_COUNT = 1`, sole non-success `databaseId =
34748491771`): exit `0`.

**Task 2's own `<automated>` verify, run exactly as written:**
```
$ bash <extracted Task 2 verify script>
exit: 0
```
Passed in full — no messages printed, every key and section check succeeded.

## Issues Encountered

None beyond the recorded deviation above, which is itself a re-measurement rather than a new
problem: it confirms `71-CI-EVIDENCE.md`'s own AMENDED addendum, word for word, on the close tip.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- SC#1 is now fully closed for this phase: two separated, positively-controlled observations both
  show the unpublished shape; the phase's own product-tree diff is confined to `CHANGELOG.md`;
  every post-dispatch commit is planning-only; and D-11 (both parts) confirms no code changed
  since Phase 70's verification.
- `71-07` (the phase's closing plan, if the roadmap's SC#4/handoff work remains) can proceed with
  this evidence in hand. `71-CLOSEOUT-GUARD.md`'s re-verification protocol still applies at phase
  close and again after any `phase.complete`-family tooling runs.
- The 71-04 dispatch-count discrepancy remains recorded (not resolved by deletion) in both
  `71-CI-EVIDENCE.md` and here; no further action is required of this plan or its successors
  unless the owner revisits that decision.

---
*Phase: 71-v0-9-4-close-prep-prep-only-unpublished*
*Completed: 2026-09-13*
