---
phase: 36-shared-emission-seam-cleanup
plan: 02
subsystem: translator
tags: [translator, refactor, adm-06, byte-identity, decoupling]

# Dependency graph
requires: ["36-01"]
provides:
  - "visit_desc_signature/depart_desc_signature own their own emission (no dummy-strong delegation)"
  - "visit_rubric/depart_rubric own their own emission (no dummy-strong delegation)"
  - "36-GATE-EVIDENCE.md: post-decoupling SC#2 diff (empty) and SC#1 delegation census (6 -> 2)"
affects: ["36-04-sweep-and-verdict", "37-signature-typography", "39-rubric-admonition-taxonomy"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Deliberate triplication (D-01): visit_strong's body copied verbatim into visit_desc_signature/depart_desc_signature and visit_rubric/depart_rubric, no shared helper introduced"

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - .planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md

key-decisions:
  - "D-01/D-02/D-03 applied exactly as specified: verbatim copy, unchanged _strong_was_* attribute names, unreachable branches kept rather than pruned"
  - "Measured that git diff --stat between Plan 01's named baseline commit and this plan's decoupling commit includes 4 unrelated paths (ROADMAP.md, STATE.md, Plan 01's own summary/evidence docs) because of intervening orchestrator/Plan-01 commits between the two SHAs — not because this plan's commits touch them. Verified typsphinx/translator.py is byte-identical between the baseline commit and this plan's actual starting commit, then re-ran --stat from that content-identical starting point to get the clean single-file measurement D-07 requires. Recorded both measurements transparently in 36-GATE-EVIDENCE.md rather than silently picking the flattering one."

requirements-completed: [ADM-06]

# Metrics
duration: ~5min (task commits span 09:30:48+09:00 to 09:34:45+09:00; environment provisioning and reading beforehand not included)
completed: 2026-08-01
status: complete
---

# Phase 36 Plan 02: Decouple desc_signature/rubric from visit_strong Summary

**`visit_desc_signature`/`depart_desc_signature` and `visit_rubric`/`depart_rubric` no longer construct a throwaway `nodes.strong()` and delegate — each now inlines `visit_strong`'s/`depart_strong`'s body verbatim (D-01 triplication), with a recorded empty diff proving the emitted `.typ` is byte-identical across the change.**

## Performance

- **Duration:** ~5 min of task-commit work (12547a2 at 09:30:48+09:00 through 49f1436 at 09:34:45+09:00), plus environment provisioning (worktree `uv sync` + NixOS `uv`/`ruff` shim) and research reading beforehand
- **Tasks:** 3
- **Files modified:** 2 (`typsphinx/translator.py`, `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md`); `tests/` confirmed untouched at every commit

## Accomplishments

- Rewrote `visit_desc_signature`/`depart_desc_signature` to inline `visit_strong`'s/`depart_strong`'s body verbatim in place of the dummy-node delegation, keeping the sibling forced-break, the `_is_first_desc_signature`/`_is_first_desc_signature_line` bookkeeping, and the hand-rolled id-anchor loop exactly where they were (not swapped for `_emit_id_anchors`, which would have added bytes).
- Rewrote `visit_rubric`/`depart_rubric` the same way, preserving the `_emit_id_anchors(node)` call and unconditional newline before the inlined body, and the explicit newline + `_emit_forced_break("linebreak()")` after it — including the pre-existing two-blank-line redundancy in the propagated-target-inside-a-list-item construct (R2), reproduced exactly rather than tidied.
- Measured, via two real `sphinx-build -b typst` runs (one at Plan 01's recorded baseline commit in a throwaway git worktree, one at this plan's decoupling commit), that the emitted `index.typ` for the SC#2 combined-construct fixture is byte-identical (`diff` exit 0, empty output) — the decoupling changed no rendering.
- Recorded the post-decoupling SC#1 delegation census: the `dummy_strong = nodes.strong()` site count dropped from 6 (pre-decoupling) to 2 (post-decoupling), both remaining sites owned by `visit_literal_strong`/`depart_literal_strong` (FLD-03, out of scope, Phase 38) — matching the plan's expected disposition exactly.
- Appended both sections plus a `### Regression net` sub-section to `36-GATE-EVIDENCE.md`, with verbatim commands and verbatim output throughout, per D-07 (decoupling evidence kept separate from MATH-02's, which Plan 03 owns).
- Confirmed the full test suite reaches the expected post-decoupling state: `652 passed, 1 skipped, 0 failed` (up from Plan 01's `1 failed, 651 passed, 1 skipped`, the one failure being this plan's own SC#1 assertion flipping RED to GREEN).

## Task Commits

Each task was committed atomically:

1. **Task 1: Decouple visit_desc_signature / depart_desc_signature from visit_strong** - `12547a2` (feat)
2. **Task 2: Decouple visit_rubric / depart_rubric from visit_strong** - `8708ab0` (feat)
3. **Task 3: Record the SC#2 diff and the post-decoupling delegation census in 36-GATE-EVIDENCE.md** - `49f1436` (docs)

## Files Created/Modified

- `typsphinx/translator.py` - `visit_desc_signature`/`depart_desc_signature` (Task 1) and `visit_rubric`/`depart_rubric` (Task 2) rewritten to own their emission; `visit_strong`/`depart_strong`/`visit_literal_strong`/`depart_literal_strong` untouched
- `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md` - Task 3 appended `## Post-decoupling diff (SC#1, SC#2, D-03, D-07)` and `## SC#1 delegation census (post-decoupling)` (with a `### Regression net` sub-section), leaving Plan 01's sections untouched

## Decisions Made

- Applied D-01 (verbatim copy, no shared helper), D-02 (unchanged `_strong_was_in_paragraph`/`_strong_was_in_list_item`/`_strong_was_list_item_needs_separator` attribute names), and D-03 (verbatim copy including the three branches 36-RESEARCH.md proved unreachable from `desc_signature`/`rubric`) exactly as specified — verified by the ast-based acceptance-criteria checks in both tasks and the final `uv run ruff check`/`black --check`/`mypy` trio, all exit 0.
- For the R2 construct's known two-blank-line redundancy (a real cosmetic wart 36-RESEARCH.md documented), reproduced it exactly rather than "fixing" it while copying — confirmed present, unchanged, in the byte-identical diff.
- `git diff --stat` between Plan 01's named baseline commit (`b37ea40`) and this plan's decoupling commit (`8708ab0`) surfaces 4 extra paths (ROADMAP.md, STATE.md, Plan 01's own summary/evidence docs) that are not this plan's work — they landed via intervening Plan-01 and orchestrator commits between the two named SHAs. Rather than silently reporting the misleading raw number, verified `typsphinx/translator.py` is byte-identical between the baseline commit and this plan's actual starting commit (`037504fd`), then additionally measured `git diff --stat` from that content-identical starting point, which shows exactly one path (`typsphinx/translator.py`) — the true D-07 discharge. Both measurements are recorded transparently in `36-GATE-EVIDENCE.md`.

## Deviations from Plan

None - plan executed exactly as written. The `git diff --stat` measurement note above is a documentation clarification recorded in the evidence file (Task 3's own deliverable), not a deviation from any task's action or acceptance criteria — both the literal baseline-to-decoupling stat and the content-identical-starting-point stat are recorded, and the latter satisfies the acceptance criterion ("names exactly one path") as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 03 (MATH-02) can proceed independently — it targets `visit_math_block`, a different handler untouched by this plan, and this plan's decoupling evidence is isolated in its own `36-GATE-EVIDENCE.md` sections per D-07 so Plan 03's MATH-02 diff won't be conflated with the decoupling diff.
- Plan 04 (sweep and verdict) has what it needs: the post-decoupling delegation census (2, both `literal_strong`), the byte-identity proof, and the full-suite result (`652 passed, 1 skipped, 0 failed`) to compare its own final run against.
- Phase 37 (SIG-01..09) and Phase 39 (ADM-01..05/rubric+admonition taxonomy) can now independently restyle `desc_signature`'s and `rubric`'s emission respectively without touching plain `**bold**` markup — the seam is cut.
- The deferred `par()`-loss bug (a rubric containing inline `strong` markup can leave `in_list_item` stuck `True`) remains untouched and unfixed by design (D-02); it is still an open todo for Phase 39, not addressed by this plan.

---
*Phase: 36-shared-emission-seam-cleanup*
*Completed: 2026-08-01*

## Self-Check: PASSED

All modified files confirmed present on disk (`typsphinx/translator.py`,
`.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md`,
this `36-02-SUMMARY.md`) and all three task commit hashes (`12547a2`,
`8708ab0`, `49f1436`) confirmed present in `git log`.
