---
phase: 16-silent-drop-node-handlers-length-converter-refactor
plan: 03
subsystem: translator
tags: [typst, docutils, length-conversion, figure, table, gate-01]

# Dependency graph
requires:
  - phase: 16-01
    provides: todo_node handler pattern (visit_/depart_ + gated SkipNode), render-gate fixture convention
  - phase: 16-02
    provides: manpage handler pattern (delegation to visit_emphasis), render-gate fixture convention
provides:
  - "_convert_length_to_typst wired into visit_figure/depart_figure (:figwidth:) and depart_table (:width:, covering .. table::/.. csv-table::/.. list-table::)"
  - "block(width: ...)[...] wrapper pattern for figure()/table() calls (Typst rejects a direct width: kwarg on either function)"
  - "TestFigureFigwidthRenderGate + TestTableWidthRenderGate real-compile acceptance gates"
affects: [phase-17-fidelity-audit, phase-18-fidelity-fixes]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "block(width: X)[#figure(...)] / block(width: X)[#table(...)] wrapper — the only Typst-valid way to apply a computed width to figure()/table() (both reject a direct width: kwarg)"
    - "convert-once-at-visit, consume-at-depart via a per-node instance attribute (_figure_block_width) — prevents the unsupported-unit drop-warning from firing twice for the same node"

key-files:
  created:
    - tests/fixtures/table_width_render_gate/conf.py
    - tests/fixtures/table_width_render_gate/index.rst
  modified:
    - typsphinx/translator.py
    - tests/test_pdf_render_gate.py
    - tests/fixtures/figure_length_render_gate/index.rst

key-decisions:
  - "Wrapped the WHOLE figure()/table() call in block(width: ...)[...] rather than passing width: as a kwarg — Typst's figure()/table() both reject a direct width: argument (verified via real compile per 16-RESEARCH.md Pitfall 3)"
  - "Converted the length exactly once, in visit_figure (stored on self._figure_block_width for depart_figure to consume+reset) — converting again in depart would double-fire the unsupported-unit warning and break the one-warning-per-occurrence contract"
  - "depart_table computes+consumes the converted width in a single method (no cross-visit state needed) since visit_table does not participate in table() emission"

patterns-established:
  - "Length-bearing block-call wrapper: when a Typst function rejects a direct length kwarg, wrap the whole call in block(width: ...)[...] instead of modifying the call's own argument list"

requirements-completed: [LEN-01]

coverage:
  - id: D1
    description: ":figwidth: on .. figure:: wires through _convert_length_to_typst and wraps figure() in block(width: ...)[...] — px converts to pt (0.75 ratio), % passes through, unsupported units warn-and-drop with no wrapper"
    requirement: "LEN-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestFigureFigwidthRenderGate::test_figwidth_pdf_wraps_block_and_compiles"
        status: pass
    human_judgment: false
  - id: D2
    description: ":width: on .. table::/.. csv-table::/.. list-table:: (all converging on nodes.table) wires through _convert_length_to_typst and wraps table() in block(width: ...)[...] — same px/%/unsupported-unit contract as D1"
    requirement: "LEN-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestTableWidthRenderGate::test_table_width_pdf_wraps_block_and_compiles"
        status: pass
    human_judgment: false
  - id: D3
    description: "visit_image behavior unchanged (pre-existing FIG-01 length-conversion gate still green) — the LEN-01 refactor is behavior-preserving at the load-bearing v0.6.0 call site"
    requirement: "LEN-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestFigureLengthRenderGate::test_figure_length_pdf_converts_px_and_drops_unknown_unit"
        status: pass
    human_judgment: false

# Metrics
duration: 15min
completed: 2026-07-16
status: complete
---

# Phase 16 Plan 03: Length-Converter Refactor (LEN-01) Summary

**Wired `_convert_length_to_typst` into `visit_figure`/`depart_figure` (`:figwidth:`) and `depart_table` (`:width:`, covering `.. table::`/`.. csv-table::`/`.. list-table::`), closing LEN-01 as the single shared CSS-length -> Typst-length helper used at every length-bearing docutils site.**

## Performance

- **Duration:** ~15 min (RED commit to GREEN commit)
- **Started:** 2026-07-16T21:54Z (Task 1 RED commit)
- **Completed:** 2026-07-16T21:57Z (Task 2 GREEN commit)
- **Tasks:** 2
- **Files modified:** 4 (1 source, 1 test file, 1 extended fixture, 1 new fixture pair)

## Accomplishments
- `visit_figure`/`depart_figure` now read `node.get("width")` (docutils' `:figwidth:` assignment), convert once via `_convert_length_to_typst`, and wrap the whole `figure()` call in `block(width: ...)[#figure(...)]` when the value converts — matching the verified-by-real-compile constraint that Typst's `figure()` rejects a direct `width:` kwarg.
- `depart_table` applies the identical wrapper pattern for `:width:` on `.. table::`/`.. csv-table::`/`.. list-table::` (all three converge on `nodes.table` via docutils' `Table.set_table_width()`, so one wiring covers all three directive types with no per-directive branching).
- Two new real-compile GATE-01 acceptance-fixture test classes (`TestFigureFigwidthRenderGate`, `TestTableWidthRenderGate`) prove both sites through a genuine `sphinx-build -> typst.compile() -> pypdf` round-trip, including the exact px->pt conversion value, the %-passthrough, and the drop-with-exactly-one-warning unsupported-unit contract.
- The pre-existing `TestFigureLengthRenderGate` (the v0.6.0 FIG-01 `visit_image` gate) stays green unmodified — proving the refactor is behavior-preserving at the load-bearing call site, closing the STATE.md blocker noted for this phase.
- `_convert_length_to_typst` remains the single conversion implementation in the file (`grep -c 'def _convert_length_to_typst'` == 1) with no duplicated px/pc arithmetic added at either new call site (`grep -cE '0\.75|\* 12'` unchanged at 4, all inside the one helper).

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend figure fixture with figwidth cases + create table_width fixture + failing tests (RED)** - `ee0b4b0` (test)
2. **Task 2: Wire _convert_length_to_typst into visit_figure/depart_figure and depart_table (GREEN)** - `eaa691d` (feat)

_TDD task (Task 2, `tdd="true"`): RED confirmed in Task 1's commit (both new test classes failed against main, with the pre-existing figure-length gate staying green); GREEN confirmed in Task 2's commit. No separate refactor commit was needed — the implementation matched the wrapper shape on the first pass._

## Files Created/Modified
- `typsphinx/translator.py` - Added `_figure_block_width` instance state; wired figwidth wiring into `visit_figure`/`depart_figure` and width wiring into `depart_table`, both via the shared `_convert_length_to_typst` helper and the `block(width: ...)[...]` wrapper shape
- `tests/fixtures/figure_length_render_gate/index.rst` - Extended (append-only) with three `:figwidth:` sections: 400px, 75%, 5ex (unsupported unit)
- `tests/fixtures/table_width_render_gate/conf.py` - New fixture conf, copied from the figure_length_render_gate template
- `tests/fixtures/table_width_render_gate/index.rst` - New fixture: `.. table::` (200px), `.. list-table::` (50%), `.. csv-table::` (1ex unsupported), each with a distinct sentinel first-cell token, none carrying a title argument
- `tests/test_pdf_render_gate.py` - Added `table_width_render_gate_dir` fixture, `TABLEPXSENTINEL7Q4`/`TABLELISTSENTINEL8Q5`/`TABLECSVSENTINEL9Q6` sentinel constants, and `TestFigureFigwidthRenderGate` + `TestTableWidthRenderGate` classes

## Decisions Made
- Wrapped the whole `figure()`/`table()` call in `block(width: ...)[...]` rather than attempting to pass `width:` as a function argument — this is the only verified-working shape (real-compile failure confirmed both functions reject a direct `width:` kwarg per 16-RESEARCH.md Pitfall 3); the `visit_image` kwarg pattern was deliberately NOT copied to either site.
- Converted the figure's length exactly once, in `visit_figure`, storing the result on a new `self._figure_block_width` instance attribute for `depart_figure` to consume and reset — converting a second time in depart would fire the unsupported-unit warning twice for the same occurrence, breaking the drop-with-one-warning contract inherited from Phase 11 (D-02).
- `depart_table` needed no cross-visit state: `visit_table` does not participate in `table()` emission (that all happens in `depart_table`), so the read-convert-emit sequence lives entirely in one method, using `self.body.append` (never `self.add_text`) to avoid the pre-existing stale `table_cell_content` buffer misrouting hazard documented at that call site.

## Deviations from Plan

None - plan executed exactly as written. The wrapper shapes, state-attribute name, and warning-count expectations all matched the plan's `<action>`/`<acceptance_criteria>` on the first implementation pass; no auto-fixes were needed.

## Issues Encountered

None specific to this plan's scope. Note for the record: `uv run python -m pytest -m "not slow" ...` (the plan's exact fast-suite verification command) reports 3 pre-existing failures in `tests/test_examples_basic.py` (`TestBasicExampleBuild::test_build_typst_succeeds`/`test_build_generates_typ_file`/`test_generated_typ_is_valid`), all `exit status 127` from shelling out to `["uv", "run", "sphinx-build", ...]` — this is the exact PATH-shadowing hazard `_run_sphinx_build_typst`'s own docstring in `test_pdf_render_gate.py` documents and works around via `sys.executable -m sphinx`; `test_examples_basic.py` predates that workaround and was not touched by this plan (not in `files_modified`). Confirmed pre-existing and unrelated to this plan's changes by reproducing the same 3 failures with `typsphinx/translator.py` temporarily reverted to its pre-Task-2 state. Out of scope per the deviation rules' scope boundary (files this plan did not modify); logged here rather than in a separate deferred-items file since it is a known, previously-documented environmental gap, not a new discovery.

## Next Phase Readiness

LEN-01 is closed: the exhaustive docutils audit (image/figure/table — the only three length-normalized-attribute sites) is now fully wired through the single `_convert_length_to_typst` implementation, each proven by a real `typst.compile()` acceptance fixture. This closes the last of the three Phase 16 requirements (TODO-01, MAN-01 from waves 1-2; LEN-01 from this wave). Phase 16 is ready for its full-corpus/requirements verification pass; Phase 17 (Rendering-Fidelity Audit) can proceed once Phase 16 closes, per the roadmap's stated dependency (the audit needs the new handlers already landed so it surfaces genuinely-silent divergence, not the already-scheduled todo_node/manpage drops).

---
*Phase: 16-silent-drop-node-handlers-length-converter-refactor*
*Completed: 2026-07-16*

## Self-Check: PASSED

All created/modified files confirmed present on disk (`typsphinx/translator.py`, `tests/test_pdf_render_gate.py`, `tests/fixtures/figure_length_render_gate/index.rst`, `tests/fixtures/table_width_render_gate/conf.py`, `tests/fixtures/table_width_render_gate/index.rst`, this SUMMARY.md). All three task/summary commit hashes (`ee0b4b0`, `eaa691d`, `55d07d2`) confirmed present in `git log --oneline --all`.
