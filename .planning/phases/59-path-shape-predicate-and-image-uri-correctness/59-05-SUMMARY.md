---
phase: 59-path-shape-predicate-and-image-uri-correctness
plan: 05
subsystem: testing
tags: [image-uri, typst-compile, windows-path, evidence, halt]

requires:
  - phase: 59-04
    provides: "IMG-07 fixture (tests/fixtures/windows_shaped_image_uri_gate/) and the committed compile gate (tests/test_windows_image_uri_render_gate.py) this plan re-runs against four reconstructed trees"
provides:
  - "59-WINDOWS-URI-EVIDENCE.md's IMG-07 four-combination table filled with all four MEASURED transcripts (not the design-target predictions alone), and an explicit DIVERGENT flag on combination A"
  - "A HALT condition, per the plan's own Task 1 instruction, surfaced to the owner: 59-CONTEXT.md D-01's predicted Typst refusal text for the unfixed tree (`path must not contain a backslash`) does not match the measured text (`unclosed delimiter`)"
affects: [59-05-followup]

actuals:
  tokens: 3693
  tasks: 1
  commits: 1

tech-stack:
  added: []
  patterns:
    - "two-tree reconstruction via git checkout $PHASE_BASE_SHA -- <files>, immediately restored to HEAD and verified with git status --porcelain after every combination -- the D-09/58 D-05(b) evidence shape, applied here across FOUR trees instead of two"

key-files:
  created: []
  modified:
    - .planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md

key-decisions:
  - "Followed the plan's explicit Task 1 instruction verbatim: on a measured divergence from 59-CONTEXT.md's predicted table, record the measurement and mark the row DIVERGENT rather than edit the expectation to match, and HALT for the owner rather than proceed to Tasks 2/3 in the same run"
  - "Did not attempt to resolve the divergence's root cause as fact -- recorded a plausible explanation (the design table was inferred from four ISOLATED single-defect hand-compiled probes, never from the actual combined-defect literal the real pipeline emits) as a hypothesis for the owner to evaluate, not as a closed finding"

requirements-completed: []

coverage:
  - id: D1
    description: "All four D-01 tree combinations (unfixed, key-normalization-only, escaping-only, both) are reconstructed via the two-tree checkout device and re-run through the SAME committed compile gate, with verbatim pytest and direct-build transcripts recorded for each"
    requirement: "IMG-07"
    verification:
      - kind: manual_procedural
        ref: "59-WINDOWS-URI-EVIDENCE.md § IMG-07 four-combination table § RED (pre-fix, all four tree combinations) -- MEASURED (plan 59-05)"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#2's core claim (neither half alone closes the compile failure) is proven true by the four measurements: A, B, C all fail to compile, only D compiles"
    requirement: "IMG-07"
    verification:
      - kind: manual_procedural
        ref: "59-WINDOWS-URI-EVIDENCE.md § SC#2 conclusion, unaffected by the divergence"
        status: pass
    human_judgment: false
  - id: D3
    description: "Combination A's measured Typst refusal text (unclosed delimiter) diverges from 59-CONTEXT.md D-01's prediction (path must not contain a backslash); this plan halted per its own explicit instruction rather than silently reconciling the discrepancy, leaving Tasks 2 and 3 (SC#5 zero-test-edit measurement, final local gate, and the 3-OS CI dispatch) unexecuted pending an owner decision"
    requirement: "IMG-07"
    verification: []
    human_judgment: true
    rationale: "The plan's own Task 1 instruction requires this exact divergence to HALT for the owner -- whether to amend 59-CONTEXT.md D-01 in place (the project's established pattern for a locked decision falsified by measurement) or pursue some other resolution is a decision only the owner can make, not one this executor is authorized to resolve unilaterally."

duration: ~35min
completed: 2026-08-29
status: halted
---

# Phase 59 Plan 05: IMG-07 Four-Combination Evidence — HALTED on a Measured Divergence Summary

**All four of D-01's tree combinations were reconstructed and measured against the real committed compile gate; three of four match the design-target prediction exactly, but combination A (unfixed) measures Typst's `unclosed delimiter` refusal instead of the predicted `path must not contain a backslash` — the plan's own instruction requires recording this and halting for the owner rather than reconciling it, so Tasks 2 and 3 (SC#5 measurement and the 3-OS CI dispatch) are unexecuted.**

## Performance

- **Duration:** ~35 min
- **Started:** ~2026-08-29T02:00:00Z (approximate — context reading + venv provisioning)
- **Completed:** 2026-08-29T02:35:00Z
- **Tasks:** 1 of 3 (Task 1 executed to completion of its measurement work; halted before its own `<done>` criteria could be satisfied because the criteria assume no divergence; Tasks 2 and 3 not started)
- **Files modified:** 1 (evidence file only — no product file, no test file)

## Accomplishments
- Reconstructed all four of D-01's tree combinations (unfixed, key-normalization-only, escaping-only, both) via `git checkout $PHASE_BASE_SHA -- typsphinx/{builder,translator}.py`, immediately restoring to `HEAD` and confirming `git status --porcelain typsphinx/` empty after every combination
- For each combination, took two independent measurements: the committed pytest gate (`tests/test_windows_image_uri_render_gate.py -q`) and a direct standalone `python -m sphinx -b typstpdf ... TYPSPHINX_WIN_URI_MODE=file` build, capturing Typst's own refusal text verbatim in both
- Combinations B (key normalization only → `unclosed delimiter`), C (escaping only → `path must not contain a backslash`) and D (both → compiles, real `%PDF`-magic `master.pdf`) all match `59-CONTEXT.md` D-01's predicted table exactly
- **Discovered a genuine divergence on combination A (unfixed):** measured `TypstError: unclosed delimiter`, not the predicted `path must not contain a backslash`. The unescaped double quote in the combined-defect literal terminates the Typst string literal at parse time, before the semantic-level backslash-in-path check the prediction assumed would fire first
- SC#2's core claim ("neither alone would have closed it") is unaffected by the divergence — A, B, and C all fail to compile and only D compiles, proving the two-fix conjunction is genuinely necessary regardless of which exact error text fires on the unfixed tree
- Per the plan's own explicit Task 1 instruction ("do NOT edit the expectation to match... record the measurement, mark the row DIVERGENT, and HALT for the owner"), recorded the full measured table and all four verbatim transcripts into `59-WINDOWS-URI-EVIDENCE.md`, then HALTED rather than proceeding to Task 2 (SC#5 zero-test-edit measurement, final local gate) or Task 3 (3-OS CI dispatch)

## Task Commits

Each task was committed atomically:

1. **Task 1: Reconstruct all four trees and record D-01's four-combination table** — `89bad115` (test) — measurement recorded, DIVERGENT row flagged, HALT documented in the evidence file itself
2. **Task 2: Measure SC#5's zero-test-edit claim and record the final local gate** — NOT EXECUTED (halted before this task)
3. **Task 3: Dispatch the 3-OS CI lane fresh on the post-fix tip and record the result** — NOT EXECUTED (halted before this task)

**Plan metadata:** this SUMMARY's own commit (below)

## Files Created/Modified
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` — filled `## IMG-07 four-combination table` § `### RED (pre-fix, all four tree combinations)` with the full measured table, four verbatim transcripts (pytest + direct build for each), the SC#2 conclusion, and a `### HALT — owner decision required` subsection

## Decisions Made
- Followed the plan's Task 1 instruction to the letter: measured, recorded, marked DIVERGENT, and halted — did not attempt to silently reconcile the discrepancy by adjusting either the code, the fixture, or the recorded expectation
- Continued gathering all four combinations' full transcripts before halting (rather than stopping at the first divergent measurement) because the plan's own acceptance criteria and the owner's eventual decision both need the complete picture, and gathering B/C/D required no code change and was itself informative (it confirmed the divergence is isolated to combination A, not systemic)
- Did not proceed to Task 2 (zero-test-edit measurement, final local gate) or Task 3 (CI dispatch) despite those tasks being largely independent of the divergence, because Task 3 explicitly gates on "tasks 1 and 2 have recorded a complete local RED-then-green" and Task 1's own `<done>` criteria are not met while the divergence is unresolved — proceeding further risked compounding an already-flagged HALT condition with additional unreviewed work

## Deviations from Plan

None in the Rule 1-3 sense (no bug fixed, no missing functionality added, no blocking issue auto-resolved). This is not a deviation from the plan — it is the plan's own designed HALT branch, taken because its explicit trigger condition (a measured divergence from `59-CONTEXT.md` D-01's table) occurred.

## Issues Encountered

**The core finding, in one sentence:** `59-CONTEXT.md` D-01's table predicts combination A (unfixed) refuses with `path must not contain a backslash`, but the real measured refusal is `unclosed delimiter` — a genuine discrepancy between the design document's inferred prediction (built from isolated single-defect probes) and the actual pipeline's combined-defect output, first caught by this plan's real measurement rather than assumed.

This does not indicate a bug in `typsphinx/builder.py` or `typsphinx/translator.py` — no product file was touched by this plan, and SC#2's underlying claim (neither fix alone closes the compile failure) is still true. It indicates the *prediction* in `59-CONTEXT.md` was imprecise about which specific `TypstError` fires for the unfixed tree. See `59-WINDOWS-URI-EVIDENCE.md` § "HALT — owner decision required" for the full record and a proposed (not decided) resolution path.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

**This plan is HALTED, not complete.** Owner review is required before this plan (or a follow-up) can proceed to:
1. Task 2 — measure SC#5's zero-test-edit claim against `58-REPR-CENSUS.md`, and record the final local gate (`uv run pytest -q`, `black --check .`, `mypy typsphinx/`, per-module skip census, RED-first ledger)
2. Task 3 — dispatch the 3-OS CI lane fresh on this phase's own post-fix tip

Recommended owner decision path (from the evidence file's HALT section): either (a) amend `59-CONTEXT.md` D-01 in place with this measurement — the project's own established pattern for a locked decision falsified by measurement (see STATE.md's "[Phase 56] D-03 was AMENDED..." precedent) — after which Task 1's acceptance criteria should be read against the corrected table and this plan's remaining tasks resumed, or (b) some other resolution the owner specifies.

**No code or test file was touched.** `typsphinx/builder.py` and `typsphinx/translator.py` are byte-identical to `HEAD` (confirmed via `git status --porcelain typsphinx/` empty both mid-measurement and at commit time). The next executor (continuing this plan or a follow-up) can resume Task 2 immediately once the owner's decision is recorded, without any tree repair.

## Self-Check: PASSED

- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` — FOUND, contains `### RED (pre-fix, all four tree combinations) -- MEASURED (plan 59-05)` and `### HALT -- owner decision required`
- Commit `89bad115` — FOUND in `git log --oneline --all`
- `git status --porcelain typsphinx/` — empty (re-confirmed immediately before this SUMMARY was written)
- `git diff --diff-filter=D --name-only HEAD~1 HEAD` — empty (no deletions in the Task 1 commit)
- Re-ran `uv run pytest tests/test_windows_image_uri_render_gate.py -q` on the current (HEAD) tree immediately before this section: `2 passed in 0.54s` — confirms the tree is genuinely restored to the post-fix state, not left mid-reconstruction
- The plan-level `<verification>` block's full-suite/black/mypy/CI-dispatch items are NOT re-confirmed here — they belong to Tasks 2/3, which did not execute

---
*Phase: 59-path-shape-predicate-and-image-uri-correctness*
*Completed: 2026-08-29 (halted)*
