---
phase: 42-captioned-table-drops-preceding-target-label
plan: 04
subsystem: rendering
tags: [typst, translator, docutils, sphinx, rst-target, cross-reference]

# Dependency graph
requires:
  - phase: 42-01
    provides: the recorded classic-TypstError RED gate (`tests/test_captioned_table_propagated_target_render_gate.py`, commit d28f2c8) that this plan's fix commit turns GREEN
provides:
  - "depart_table's propagated-anchor call moved past the self.in_table = False reset, gated on a was_captioned boolean captured before self.table_caption is reset"
  - "the GREEN half of the phase's RED/GREEN gate pair, recorded in 42-GATE-EVIDENCE-04.md"
affects: [42-05, 42-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Capture a truthiness condition into a local boolean BEFORE the state it reads is reset, when the guarded action must run AFTER that reset (was_captioned pattern)."

key-files:
  created:
    - .planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-04.md
  modified:
    - typsphinx/translator.py

key-decisions:
  - "D-05 followed exactly: the fix is a call-ordering move confined to depart_table; _emit_id_anchors, add_text, visit_table's unconditional call, and depart_figure are all byte-identical after this change."
  - "D-02 followed exactly: skip_ids=set(node.get(\"ids\", [])[:1]) carried across unchanged, so ids[0] still owns the figure <label> and ids[1:] still become metadata(none) anchors."
  - "was_captioned tightened to `self.table_colcount > 0 and bool(self.table_caption)` (both conjuncts required) per the plan's explicit refinement of 42-RESEARCH.md's single-conjunct proposal, so a degenerate zero-column captioned table keeps its exact current (no-op) emission."

requirements-completed: [TBL-03]

coverage:
  - id: D1
    description: "A captioned table preceded by a standalone target compiles and both labels (the figure's own and the propagated target's) resolve, for all four D-01 shapes plus the caption-less control."
    requirement: "TBL-03"
    verification:
      - kind: unit
        ref: "tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate (all 9 methods)"
        status: pass
      - kind: integration
        ref: "uv run python -m sphinx -b typstpdf -q -E tests/fixtures/captioned_table_propagated_target_render_gate <build> (exit 0, index.pdf produced)"
        status: pass
    human_judgment: false
  - id: D2
    description: "No label is defined twice anywhere in the emitted document (the dangling-label fatal is not traded for the Typst duplicate-label fatal)."
    requirement: "TBL-03"
    verification:
      - kind: unit
        ref: "tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_no_duplicate_label_definition"
        status: pass
    human_judgment: false
  - id: D3
    description: "No regression in the pre-existing captioned-table gate, the new figure gate, or the full suite."
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_pdf_render_gate.py tests/test_figure_propagated_target_render_gate.py -q (38 passed)"
        status: pass
      - kind: unit
        ref: "uv run pytest -q (821 passed, 1 skipped -- matches 812 baseline + 9 gate tests)"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-08-03
status: complete
---

# Phase 42 Plan 04: Land the TBL-03 Fix (Call-Ordering Move) + GREEN Evidence Summary

**Moved `depart_table`'s trailing `_emit_id_anchors` call past the `self.in_table = False` reset (gated on a `was_captioned` boolean captured pre-reset) so a captioned table's propagated-target anchor reaches the document body instead of a buffer that gets deleted — turning all 9 tests in the RED gate module GREEN with zero regressions.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-08-03T14:43:18Z
- **Tasks:** 2 completed
- **Files modified:** 2 (1 production, 1 evidence doc)

## Accomplishments

- `TypstTranslator.depart_table` in `typsphinx/translator.py` no longer discards a captioned
  table's propagated remainder-id anchor. `add_text()` diverts every append into
  `self.table_cell_content` while `self.in_table` is True; the pre-fix code called
  `_emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))` while that flag was still set,
  so the anchor was appended to a buffer that gets `del`eted a few statements later and never
  reaches `self.body`. Moving the call to run after `self.in_table = False`, guarded by a new
  local `was_captioned` captured before `self.table_caption` is reset, fixes this.
- All 9 tests in `tests/test_captioned_table_propagated_target_render_gate.py` (plan 42-01's RED
  gate) now pass — the 7 that were RED pre-fix, plus the 2 that already passed (unaffected by the
  bug).
- No regression: the pre-existing captioned-table gate (`TestCaptionedTableRenderGate` and
  siblings in `tests/test_pdf_render_gate.py`) and plan 42-02's figure gate
  (`tests/test_figure_propagated_target_render_gate.py`) both stay green (38/38). Full suite:
  821 passed / 1 skipped — exactly the recorded 812-passed baseline plus the 9 newly-green tests.
- `42-GATE-EVIDENCE-04.md` records: the commit-ordering ancestry proof (RED commit `d28f2c8` is an
  ancestor of fix commit `e5575f3`), the verbatim production diff, a real `-b typstpdf` build's
  emitted `.typ` showing both label forms present for all four D-01 shapes with zero duplicate
  labels, a five-row RED-to-GREEN verdict table, and the full regression/lint/type sweep.

## Task Commits

Each task was committed atomically:

1. **Task 1: Move the depart_table propagated-anchor call past the in-table flag reset** -
   `e5575f3` (fix)
2. **Task 2: Record the GREEN and the regression sweep in 42-GATE-EVIDENCE-04.md** - `798ab72`
   (docs)

_Note: this plan's `tdd="true"` task attribute reuses plan 42-01's existing RED gate rather than
authoring a new test — there is no separate `test(...)` commit in this plan; the RED half already
exists as an ancestor commit (`d28f2c8`, plan 42-01), and this plan's task 1 commit is the GREEN
half._

## Files Created/Modified

- `typsphinx/translator.py` - `depart_table`: introduced local `was_captioned` boolean captured
  before `self.table_caption` is reset; moved the propagated-anchor `_emit_id_anchors` call to run
  after `self.in_table = False`, guarded by `was_captioned`. No other method touched.
- `.planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-04.md` -
  new evidence file: commit ordering proof, full diff, GREEN test output, real-build `.typ`
  excerpts for all four D-01 shapes, RED-to-GREEN verdict table, full regression sweep.

## Decisions Made

- Followed D-05 exactly: this is purely a call-ordering move confined to `depart_table`. No new
  argument was added to `_emit_id_anchors`, `add_text` is untouched, `visit_table`'s unconditional
  non-captioned call is untouched, `depart_figure` is untouched, and the caption-less `else:`
  branch of `depart_table` is byte-for-byte unchanged.
- Followed D-02 exactly: `skip_ids=set(node.get("ids", [])[:1])` was carried across unchanged, so
  `ids[0]` continues to own the figure's own `<label>` and `ids[1:]` continue to become
  `metadata(none)` anchors — no id-ownership change.
- Kept the plan's explicit tightening of `was_captioned` to
  `self.table_colcount > 0 and bool(self.table_caption)` (both conjuncts required), rather than
  simplifying to the single-conjunct form `42-RESEARCH.md` § 1 originally proposed — this keeps a
  degenerate zero-column captioned table on its exact pre-fix (no-op) emission path, per the
  plan's own `<planner_assumptions>` note not to "simplify" this back.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' acceptance criteria were verified command-
by-command against the plan's explicit checklist (diff scope, `grep -c` counts, line-number
ordering, all four automated verify commands) before committing.

## Issues Encountered

**NixOS `ruff` binary could not run via the documented single-shim workaround.** CLAUDE.md's
per-worktree provisioning step (`ln -sf "$(command -v ruff)" .venv/bin/ruff`) assumes a
Nix-store `ruff` is reachable via `command -v ruff`; in this worktree no system `ruff` was
installed anywhere on `PATH`, `/run/current-system/sw/bin`, `/usr/bin`, or `/bin` (only `uv` was
found at a Nix-store path and shimmed successfully). Resolved by running `ruff` under `steam-run`
(a pre-installed NixOS FHS-environment wrapper), i.e. `steam-run uv run ruff check .`, which
executed the venv's own generic-linux `ruff==0.15.20` binary correctly (`All checks passed!`).
This is a worktree-environment workaround, not a code change, and does not affect the fix itself
or its verification — `black`, `mypy`, and `pytest` all ran directly via `uv run` with no wrapper
needed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SC#3 and SC#5's GREEN half are discharged for the table-side fix. `typsphinx/translator.py`'s
  `depart_table` is done for this phase — no further changes to it are expected from 42-05 or
  42-06.
- **Plan 42-05** (caption-less byte-invariance proof, D-04) can proceed: this fix's diff (§2 of
  `42-GATE-EVIDENCE-04.md`) confirms the caption-less `else:` branch of `depart_table` was not
  touched, which is the precondition 42-05's empty-diff proof depends on.
- **Plan 42-06** (Phase 41 reconciliation, SC#6) can proceed: the fix commit `e5575f3` and evidence
  commit `798ab72` are the two commits its re-measured SC#4 invariant sweep needs to include in
  its SHA range, alongside plan 42-01's RED commit `d28f2c8` and plan 42-03's sweep (already
  landed, no production change).
- No blockers.

---
*Phase: 42-captioned-table-drops-preceding-target-label*
*Completed: 2026-08-03*
