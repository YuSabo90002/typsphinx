---
phase: 59-path-shape-predicate-and-image-uri-correctness
plan: 05
subsystem: testing
tags: [image-uri, typst-compile, windows-path, evidence, ci-dispatch]

requires:
  - phase: 59-04
    provides: "IMG-07 fixture (tests/fixtures/windows_shaped_image_uri_gate/) and the committed compile gate (tests/test_windows_image_uri_render_gate.py) this plan re-runs against four reconstructed trees"
provides:
  - "59-WINDOWS-URI-EVIDENCE.md's IMG-07 four-combination table filled with all four MEASURED transcripts, including the DIVERGENT combination A row and its owner-approved D-01a amendment"
  - "59-WINDOWS-URI-EVIDENCE.md's SC#5 acceptance section: the measured zero-test-edit diff, the final local gate (pytest/black/mypy all green, ruff deferred to CI), the per-module skip census (0 skipped across all five new gate modules), and the RED-first ledger naming all five requirements' recorded-failure sections"
  - "59-WINDOWS-URI-EVIDENCE.md's 3-OS CI dispatch subsection, recorded PENDING with the exact owner commands, per design — this plan ran in an isolated worktree, not the milestone branch that carries the phase's merged waves"
affects: [59-05-followup]

actuals:
  tokens: 5551
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "two-tree reconstruction via git checkout $PHASE_BASE_SHA -- <files>, immediately restored to HEAD and verified with git status --porcelain after every combination -- the D-09/58 D-05(b) evidence shape, applied here across FOUR trees instead of two"
    - "measured, not fabricated, CI evidence: a dispatch that cannot complete from a worktree is recorded PENDING with reproducible commands and the local tip SHA, never an older run cited as current"

key-files:
  created: []
  modified:
    - .planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md

key-decisions:
  - "Task 1 (a prior executor run) followed the plan's explicit instruction verbatim on a measured divergence from 59-CONTEXT.md's predicted D-01 table: recorded the measurement, marked the row DIVERGENT, and HALTED for the owner rather than editing the expectation to match"
  - "Owner approved amending 59-CONTEXT.md D-01 in place (recorded as D-01a: AMENDED, commit ab7a42ae, independently re-measured by the orchestrator against typst.compile() before approval) -- the project's established pattern for a locked decision falsified by measurement. This plan's Task 2 records that resolution and resumes the remaining work"
  - "Task 3's CI dispatch is recorded PENDING by design, not attempted: this plan executed as a parallel worktree executor on an agent-* branch, not gsd/v0.9.1-windows-path-correctness (the milestone branch carrying the phase's merged waves). Pushing the worktree branch or dispatching CI against it would not exercise the phase's real tip, so the plan's own <action> instruction ('do not fabricate a result... mark the section PENDING') was followed literally; the orchestrator owns the real dispatch after merge"

requirements-completed: [IMG-04, IMG-05, IMG-07]

coverage:
  - id: D1
    description: "All four D-01 tree combinations (unfixed, key-normalization-only, escaping-only, both) are reconstructed via the two-tree checkout device and re-run through the SAME committed compile gate, with verbatim pytest and direct-build transcripts recorded for each; the measured divergence on combination A is resolved via an owner-approved D-01a amendment to 59-CONTEXT.md"
    requirement: "IMG-07"
    verification:
      - kind: manual_procedural
        ref: "59-WINDOWS-URI-EVIDENCE.md § IMG-07 four-combination table § RED (pre-fix, all four tree combinations) -- MEASURED (plan 59-05)"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#2's core claim (neither half alone closes the compile failure) is proven true by the four measurements: A, B, C all fail to compile, only D compiles -- unaffected by the D-01a amendment"
    requirement: "IMG-07"
    verification:
      - kind: manual_procedural
        ref: "59-WINDOWS-URI-EVIDENCE.md § SC#2 conclusion, unaffected by the divergence"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC#5's zero-test-edit claim is measured (git diff --name-status/--numstat against PHASE_BASE_SHA, cross-checked against 58-REPR-CENSUS.md) rather than asserted: all 8 tests/ entries are additions, none collide with the census's nine enumerated sites"
    requirement: "IMG-04"
    verification:
      - kind: manual_procedural
        ref: "59-WINDOWS-URI-EVIDENCE.md § SC#5 acceptance § Zero test edits (measured)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The phase's final local gate is green: full pytest suite (1465 passed, 5 skipped), black --check ., mypy typsphinx/ all clean; ruff check . explicitly deferred to CI with its stated reason; per-module skip census confirms 0 skipped for all five new gate modules on this dev machine"
    requirement: "IMG-05"
    verification:
      - kind: manual_procedural
        ref: "59-WINDOWS-URI-EVIDENCE.md § SC#5 acceptance § Final local gate (phase tip) and § Per-module skip census"
        status: pass
    human_judgment: false
  - id: D5
    description: "The 3-OS CI lane dispatch is recorded PENDING with reproducible owner commands and this worktree's local tip SHA, rather than fabricated or inferred from an older run, because this plan executed in an isolated worktree that is not the milestone branch carrying the phase's merged waves"
    requirement: []
    verification: []
    human_judgment: true
    rationale: "Whether the eventual CI run (dispatched by the orchestrator after merge onto gsd/v0.9.1-windows-path-correctness) actually goes green on windows-latest is a fact only observable after that dispatch completes -- this plan correctly stops short of fabricating that result, and a human (the orchestrator, then the owner) must confirm the upgraded run URL and per-job conclusions once recorded."

duration: ~55min (prior run ~35min + this continuation ~20min)
completed: 2026-08-29
status: complete
---

# Phase 59 Plan 05: IMG-07 Four-Combination Evidence, SC#5 Measurement and CI Dispatch Summary

**All four of D-01's tree combinations are measured against the real committed compile gate (three matching the design-target prediction exactly, one — combination A's unfixed-tree refusal text — resolved via an owner-approved D-01a amendment to 59-CONTEXT.md); SC#5's zero-test-edit claim is measured against 58-REPR-CENSUS.md rather than asserted, with the full local gate (pytest/black/mypy) green and every new gate module reporting 0 skipped; the 3-OS CI dispatch is recorded PENDING with reproducible owner commands, by design, because this plan ran in an isolated worktree that is not the milestone branch carrying the phase's merged waves.**

## Performance

- **Duration:** ~55 min total (a prior executor run completed Task 1 in ~35 min and halted at a designed checkpoint on a measured divergence; this continuation completed Tasks 2 and 3 in ~20 min after the owner's disposition)
- **Started:** ~2026-08-29T02:00:00Z (Task 1, prior run)
- **Completed:** 2026-08-29 (this continuation)
- **Tasks:** 3 of 3
- **Files modified:** 1 (evidence file only — no product file, no test file)

## Accomplishments
- Reconstructed all four of D-01's tree combinations (unfixed, key-normalization-only, escaping-only, both) via `git checkout $PHASE_BASE_SHA -- typsphinx/{builder,translator}.py`, immediately restoring to `HEAD` and confirming `git status --porcelain typsphinx/` empty after every combination
- For each combination, took two independent measurements (the committed pytest gate and a direct standalone `-b typstpdf` build), capturing Typst's own refusal text verbatim in both
- Combinations B, C and D matched `59-CONTEXT.md` D-01's predicted table exactly; combination A (unfixed) diverged — measured `TypstError: unclosed delimiter`, not the predicted `path must not contain a backslash` — recorded as DIVERGENT and halted for the owner per the plan's own explicit instruction, rather than silently reconciling
- **Owner approved amending `59-CONTEXT.md` D-01 in place** (recorded as `D-01a: AMENDED`, commit `ab7a42ae`, independently re-measured by the orchestrator against `typst.compile()` on the four literal shapes before approval); SC#2's core claim ("neither alone would have closed it") is unaffected — A, B, C all fail to compile and only D compiles
- Measured SC#5's zero-test-edit claim: `git diff --name-status`/`--numstat` against `PHASE_BASE_SHA` shows all 8 `tests/` entries as additions (`A`), cross-checked against `58-REPR-CENSUS.md`'s nine enumerated pass-criterion sites — none of the new paths appear there
- Recorded the phase's final local gate: `uv run pytest -q` (1465 passed, 5 skipped), `uv run black --check .` clean, `uv run mypy typsphinx/` clean; `ruff check .` explicitly deferred to CI per `59-VALIDATION.md`'s stated reason
- Recorded a per-module skip census: all five new gate modules (`test_path_shape_predicate_gate.py`, `test_track_image_key_construction.py`, `test_copy_image_files_name_too_long.py`, `test_image_literal_escaping_gate.py`, `test_windows_image_uri_render_gate.py`) report `0 skipped`
- Recorded a RED-first ledger naming all five requirements (PATH-01, IMG-04, IMG-06, IMG-05, IMG-07) and the exact evidence section holding each one's recorded failure
- Recorded the 3-OS CI dispatch subsection as `PENDING — owner dispatch required` with the exact commands (`git push`, `gh workflow run ci.yml --ref gsd/v0.9.1-windows-path-correctness`, `gh run list`/`gh run watch`) and this worktree's local tip SHA, because this plan executed on an isolated `agent-*` branch rather than the milestone branch carrying the phase's merged waves — per the plan's own instruction, no result was fabricated and no older run was cited

## Task Commits

Each task was committed atomically:

1. **Task 1: Reconstruct all four trees and record D-01's four-combination table** — `89bad115` (test) — measurement recorded, DIVERGENT row flagged, HALT documented in the evidence file itself (prior executor run)
2. **(halt record)** — `2f10800b` (docs) — halt surfaced formally (prior executor run)
3. **(owner disposition, orchestrator-applied)** — `ab7a42ae` — `59-CONTEXT.md` amended in place with `D-01a: AMENDED`, closing the halt
4. **Task 2: Measure SC#5's zero-test-edit claim and record the final local gate** — `ccb0079e` (test)
5. **Task 3: Dispatch the 3-OS CI lane fresh on the post-fix tip and record the result** — `b5912539` (docs) — recorded `PENDING — owner dispatch required` per the plan's own worktree-scope instruction

**Plan metadata:** this SUMMARY's own commit (below)

## Files Created/Modified
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` — filled `## IMG-07 four-combination table` (four verbatim transcripts, DIVERGENT flag, halt-resolution pointer) and `## SC#5 acceptance` (zero-test-edit measurement, final local gate, per-module skip census, RED-first ledger, `### 3-OS CI dispatch` PENDING subsection)

## Decisions Made
- Followed the plan's Task 1 instruction to the letter (prior run): measured, recorded, marked DIVERGENT, and halted — did not attempt to silently reconcile the discrepancy
- Recorded, rather than re-litigated, the owner's approved resolution: `59-CONTEXT.md` D-01a amends D-01 in place with the measured `unclosed delimiter` refusal for the unfixed tree, and explains why D-01's original prediction (built from four isolated single-defect probes) missed the combined-defect literal's actual parse-time failure
- Task 3's CI dispatch was not attempted from this worktree, by design: this plan runs as a parallel worktree executor, and the branch carrying this worktree's commits is not the milestone branch `gsd/v0.9.1-windows-path-correctness` that Phase 59's merged waves live on. Pushing or dispatching against the worktree branch would not exercise the phase's actual post-fix tip, so the section is recorded `PENDING` with exact reproducible commands rather than fabricated or backfilled from an older CI run
- Did not modify STATE.md or ROADMAP.md — per this plan's dispatch instructions, the orchestrator owns those writes after merge

## Deviations from Plan

None in the Rule 1-3 sense (no bug fixed, no missing functionality added, no blocking issue auto-resolved beyond the plan's own designed HALT branch, which was resolved by owner approval before this continuation began). Task 3's PENDING outcome is not a deviation — it is the plan's own explicitly anticipated fallback path (`<action>`: "If the push or the dispatch cannot complete from this worktree ... mark the section PENDING"), taken because its trigger condition (parallel worktree execution, not the milestone branch) is true.

## Issues Encountered

**Task 1's divergence (resolved before this continuation):** `59-CONTEXT.md` D-01's table predicted combination A (unfixed) refuses with `path must not contain a backslash`, but the real measured refusal was `unclosed delimiter`. The owner reviewed and approved amending D-01 in place (`D-01a: AMENDED`, commit `ab7a42ae`), after the orchestrator independently re-measured the four literal shapes directly against `typst.compile()` and reproduced the same result. SC#2's underlying claim was unaffected throughout.

No new issue was encountered in Tasks 2 or 3 of this continuation — both executed cleanly against the already-resolved evidence file.

## User Setup Required

None — no external service configuration required by this plan directly. The 3-OS CI dispatch (Task 3) requires the orchestrator to run the recorded commands (`git push`, `gh workflow run`) after merging this phase's waves onto `gsd/v0.9.1-windows-path-correctness`; those exact commands are recorded in `59-WINDOWS-URI-EVIDENCE.md` § "3-OS CI dispatch".

## Next Phase Readiness

This plan is complete. All three tasks executed, all four D-01 combinations measured with the divergence resolved by owner-approved amendment, SC#5's zero-test-edit claim measured (not asserted) and cross-checked against `58-REPR-CENSUS.md`, the final local gate green, and the per-module skip census confirming `0 skipped` across all five new gate modules.

**One item remains genuinely open, by design:** the 3-OS CI dispatch (`### 3-OS CI dispatch` in the evidence file) is `PENDING — owner dispatch required`. This is not a gap this plan failed to close — a parallel worktree executor cannot meaningfully dispatch CI against a branch that does not carry the phase's merged waves. The orchestrator must run the recorded commands after merging Phase 59's waves onto `gsd/v0.9.1-windows-path-correctness`, then upgrade the subsection from `PENDING` to the recorded run URL, head SHA, and per-job conclusions (with an explicit line for each `windows-latest` job) before the phase's SC#4 can be considered closed.

**No product file was touched by this plan.** `typsphinx/builder.py` and `typsphinx/translator.py` are byte-identical to `HEAD` throughout — confirmed via `git status --porcelain typsphinx/` empty both mid-measurement (Task 1) and at every subsequent commit (Tasks 2 and 3).

## Self-Check: PASSED

- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` — FOUND, contains `### RED (pre-fix, all four tree combinations) -- MEASURED (plan 59-05)`, `### HALT -- owner decision required` with its resolution pointer, `### Zero test edits (measured)`, `### Final local gate (phase tip)`, `### Per-module skip census`, `### RED-first ledger`, and `### 3-OS CI dispatch`
- Commit `89bad115` — FOUND in `git log --oneline --all`
- Commit `2f10800b` — FOUND in `git log --oneline --all`
- Commit `ab7a42ae` — FOUND in `git log --oneline --all`
- Commit `ccb0079e` — FOUND in `git log --oneline --all`
- Commit `b5912539` — FOUND in `git log --oneline --all`
- `git status --porcelain typsphinx/ tests/` — empty (re-confirmed immediately before this SUMMARY was written)
- `git diff --diff-filter=D --name-only ccb0079e~1 ccb0079e` and `b5912539~1 b5912539` — both empty (no deletions in either task commit)
- Re-ran `uv run pytest tests/test_windows_image_uri_render_gate.py -q` on the current (HEAD) tree: `2 passed in 0.53s` — confirms the tree is genuinely restored to the post-fix state

---
*Phase: 59-path-shape-predicate-and-image-uri-correctness*
*Completed: 2026-08-29*
