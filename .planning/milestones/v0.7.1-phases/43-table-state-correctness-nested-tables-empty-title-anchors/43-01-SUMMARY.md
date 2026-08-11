---
phase: 43-table-state-correctness-nested-tables-empty-title-anchors
plan: 01
subsystem: translator
tags: [sphinx, docutils, typst, table-state, translator, gate-01]

# Dependency graph
requires: []
provides:
  - "typsphinx/translator.py: self._table_state_stack + _push_table_state()/_pop_table_state() -- a full snapshot save/restore around NESTED visit_table/depart_table pairs (TBL-04 fix)"
  - "tests/fixtures/nested_table_render_gate/{conf.py,index.rst}: seven-section TBL-04 reproduction corpus, reusable by later plans"
  - "tests/test_nested_table_render_gate.py: GATE-01 structural render gate, 7 test methods covering all D-01 nesting shapes plus the header-cell/adjacency/empty-cell/control edges"
  - "43-GATE-EVIDENCE-01.md: RED commit SHA (05d49334d80705a4884ae63af9ba6e9e60b20be0) plan 43-05 consumes as the pre-fix side of the phase-wide SC#4 sweep"
affects: [43-02, 43-03, 43-04, 43-05]

# Actuals (#2632)
actuals:
  tokens: 17839
  tasks: 3
  commits: 5

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Snapshot save/restore around nesting (imitates the existing visit_caption/depart_caption buffer-swap idiom): push a full scalar snapshot only when a container of the same kind is already open, reset for the nested use, pop-and-restore before deciding the emitted markup's destination"

key-files:
  created:
    - tests/fixtures/nested_table_render_gate/conf.py
    - tests/fixtures/nested_table_render_gate/index.rst
    - tests/test_nested_table_render_gate.py
    - .planning/phases/43-table-state-correctness-nested-tables-empty-title-anchors/43-GATE-EVIDENCE-01.md
  modified:
    - typsphinx/translator.py

key-decisions:
  - "Split the RED commit into two small commits (fixture+test, then evidence file) rather than one, since the evidence file could not record its OWN commit SHA in a single self-referential commit without amending (forbidden). Both commits still precede the fix commit and neither touches translator.py."
  - "No additional translator.py change was needed for Tasks 2 and 3 beyond Task 1's fix -- the eight-scalar snapshot (including in_thead) already generalizes over shape, depth, and the header-cell edge (RESEARCH Assumption A2 CONFIRMED and closed) by construction."

patterns-established:
  - "Balanced-delimiter text scanning (_extract_paren_block/_count_top_level_brace_entries in the test file) for making positional/cell-count assertions against flattened Typst markup text, where naive per-line indentation matching is unreliable once a cell's own content is itself a nested table() call at the same relative indent."

requirements-completed: [TBL-04]

coverage:
  - id: D1
    description: "A list-table nested inside another list-table's cell preserves the outer table's header cells, plain cell, and caption; the inner table renders inside its own cell"
    requirement: TBL-04
    verification:
      - kind: integration
        ref: "tests/test_nested_table_render_gate.py#test_list_table_in_list_table_preserves_outer_cells_and_caption"
        status: pass
    human_judgment: false
  - id: D2
    description: "A grid table nested in a list-table, and a list-table nested in a grid table, both preserve every outer sentinel; the list-in-grid case's leaked cell now renders inside the outer table"
    requirement: TBL-04
    verification:
      - kind: integration
        ref: "tests/test_nested_table_render_gate.py#test_grid_table_in_list_table_preserves_outer_cells_and_caption"
        status: pass
      - kind: integration
        ref: "tests/test_nested_table_render_gate.py#test_list_table_in_grid_table_keeps_leaked_cell_inside_outer_table"
        status: pass
    human_judgment: false
  - id: D3
    description: "A three-level table nest renders all three levels' own cells -- the fix generalizes over depth, not just the shape measured first"
    requirement: TBL-04
    verification:
      - kind: integration
        ref: "tests/test_nested_table_render_gate.py#test_three_level_nest_preserves_every_levels_own_cells"
        status: pass
    human_judgment: false
  - id: D4
    description: "A table nested inside an OUTER HEADER cell leaves the outer table's remaining header cells classified as header cells (self.in_thead restored)"
    requirement: TBL-04
    verification:
      - kind: integration
        ref: "tests/test_nested_table_render_gate.py#test_nested_table_inside_header_cell_keeps_outer_header_classification"
        status: pass
    human_judgment: false
  - id: D5
    description: "Sibling text before a nested table in the same cell survives; a row with a deliberately empty cell keeps its full cell count; sibling top-level tables each render independently"
    requirement: TBL-04
    verification:
      - kind: integration
        ref: "tests/test_nested_table_render_gate.py#test_adjacency_empty_cell_and_sibling_tables_all_render_correctly"
        status: pass
    human_judgment: false
  - id: D6
    description: "A top-level table with no nesting stays byte-unchanged (SC#4, this plan's half); full suite plus black/ruff/mypy all green"
    requirement: TBL-04
    verification:
      - kind: integration
        ref: "tests/test_nested_table_render_gate.py#test_top_level_control_table_is_bare_table_no_figure_wrapper"
        status: pass
      - kind: other
        ref: "uv run python -m pytest -q (828 passed, 1 skipped) + uv run black --check . + uv run ruff check . + uv run mypy typsphinx/"
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-08-04
status: complete
---

# Phase 43 Plan 01: Nested-Table State Correctness Summary

**Fixed `translator.py`'s table state to survive nesting via a snapshot save/restore stack (`_push_table_state`/`_pop_table_state`), closing TBL-04 across all seven measured shapes -- list-in-list, grid-in-list, list-in-grid (including the leaked-cell ordering edge), a three-deep nest, a header-cell nest (confirming RESEARCH Assumption A2), and an adjacency/empty-cell/sibling-table edge -- with a recorded RED baseline against the unfixed translator and a two-build byte-invariance proof over three pre-existing table fixtures.**

## Performance

- **Duration:** ~40 min (measured commit span 00:06:26Z-00:17:20Z; setup/exploration preceded the first commit)
- **Started:** 2026-08-04 (session start)
- **Completed:** 2026-08-04T00:17:37Z
- **Tasks:** 3/3
- **Files modified:** 5 (1 production file, 4 test/fixture/evidence files)

## Accomplishments

- Closed TBL-04: a table nested inside another table's cell no longer silently clobbers the enclosing table's cells, column count, column widths, caption, header-row flag, or span counters.
- Recorded a genuine RED baseline against the unfixed translator (a structural defect that compiles cleanly with no downstream error surface), for all seven fixture sections, with a 40-hex RED commit SHA plan 43-05 will consume.
- Proved the fix generalizes over both SHAPE (three distinct outer/inner directive-type combinations) and DEPTH (a three-level nest), with no per-depth special case in the fix.
- Confirmed RESEARCH Assumption A2 (`self.in_thead` restoration across a nested table inside a header cell) with a dedicated fixture section -- the hazard was real and is now closed.
- Ran the two-build byte-invariance proof (this plan's half of SC#4) over three pre-existing table fixtures, all diffs empty, backed by a positive control proving the two builds ran genuinely different code.

## Task Commits

Each task was committed atomically (Task 1 split into a RED-artifacts commit, a RED-evidence commit, and the fix commit, per the RED-first discipline):

1. **Task 1a: RED fixture + render gate (section 1 only)** - `05d4933` (test) -- `typsphinx/translator.py` untouched
2. **Task 1b: RED evidence baseline** - `91b3a61` (docs) -- `typsphinx/translator.py` still untouched
3. **Task 1c: TBL-04 fix (save/restore stack)** - `d58501a` (feat)
4. **Task 2: generalize over shape and depth (sections 2-4)** - `db6d35a` (test)
5. **Task 3: header-cell/adjacency/empty-cell edges + byte-invariance** - `ca507ef` (test)

## Files Created/Modified

- `typsphinx/translator.py` - Added `self._table_state_stack`, `_push_table_state()`/`_pop_table_state()`; `visit_table` pushes+resets on nesting; `depart_table` restructured to build a local `emission_str` and decide its destination as an explicit nested-vs-top-level branch; extended (not replaced) the Phase 25 `table_cell_content` lifetime comment
- `tests/fixtures/nested_table_render_gate/conf.py` - Fixture Sphinx config, `index` as a master document
- `tests/fixtures/nested_table_render_gate/index.rst` - Seven-section TBL-04 reproduction corpus
- `tests/test_nested_table_render_gate.py` - GATE-01 render gate, 7 test methods + 2 balanced-delimiter helper functions
- `.planning/phases/43-table-state-correctness-nested-tables-empty-title-anchors/43-GATE-EVIDENCE-01.md` - RED baseline, RED commit SHA, GREEN transcripts for all three tasks, SC#4 byte-invariance sweep with positive control

## Decisions Made

- **RED commit self-reference resolved via two small commits.** The plan asked for "the fixture, the test and the evidence file" to be committed together as the RED commit, with the evidence file recording that same commit's own SHA -- a self-reference that cannot be satisfied in one commit without amending (which the harness's Git Safety Protocol forbids). Resolved by committing the fixture+test first (`05d4933`), then a small evidence-only follow-up (`91b3a61`) that references `05d4933`'s SHA. Both commits precede the fix commit and neither touches `typsphinx/translator.py`, satisfying the acceptance criterion's actual check (`git log --format=%H -- tests/fixtures/nested_table_render_gate` yields a commit that does not also touch the translator).
- **No additional fix code was needed for Tasks 2 and 3.** Task 1's eight-scalar snapshot (covering `in_thead`, not just the five scalars the source todo named) already generalized correctly to every shape, depth, and the header-cell edge when measured. RESEARCH Assumption A2 is CONFIRMED (the hazard was real) and CLOSED by the same fix.
- **Caught and corrected a self-introduced RED-first-discipline violation mid-task.** The fix was initially written before the RED fixture/test/evidence existed. Caught before committing: reverted `typsphinx/translator.py` to HEAD via `git checkout --`, saved the fix as a patch file, built and measured the RED baseline properly, committed it, then reapplied the fix via `git apply` and re-measured GREEN. No RED evidence in the final `43-GATE-EVIDENCE-01.md` was transcribed from a planning document or from the initial (out-of-order) run.

## Deviations from Plan

None (Rules 1-4) - plan executed as written. The one process correction (the RED-first-discipline self-catch above) is documented under Decisions Made, not as a Rule 1-4 deviation, since no code behavior was affected -- it was corrected before any commit was made.

## Issues Encountered

- **RST syntax errors in the initial fixture draft** (Section 3's grid table right-border alignment; Section 5's `:header-rows: 1` list-table with only one row, which docutils rejects as "insufficient data" for the body). Both fixed before the RED build: Section 3's grid table was regenerated with a Python script computing exact column-width alignment; Section 5's inner table gained a filler `NT5INNERBODY` body row to satisfy docutils' row-count rule (not part of the plan's named sentinel set, but required for the fixture to parse at all).
- **Naive per-line indentation counting proved unreliable for Task 3's empty-cell-count assertion**, since a nested table's own cell entries happen to share the same 2-space relative indent as the outer table's own cells once the text is flattened. Resolved with a balanced-brace depth counter (`_count_top_level_brace_entries`) and a balanced-paren block extractor (`_extract_paren_block`), added as module-level test helpers.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- TBL-04 is fully closed with a real RED-to-GREEN proof recorded in `43-GATE-EVIDENCE-01.md`, including the RED commit SHA (`05d49334d80705a4884ae63af9ba6e9e60b20be0`) that plan 43-05's phase-wide SC#4 two-build byte-invariance sweep is expected to consume as the pre-fix side.
- The full test suite (828 passed, 1 skipped), `black --check .`, `ruff check .`, and `mypy typsphinx/` are all green on this worktree's HEAD; `pyproject.toml`/`uv.lock` are unmodified (no new dependency).
- No blockers for 43-03 (FIG-01, the parallel figure-nesting fix in the same file) or 43-04 (TBL-05 + QUA-01) -- both touch different, non-overlapping code paths in `translator.py` per the wave plan.

---
*Phase: 43-table-state-correctness-nested-tables-empty-title-anchors*
*Completed: 2026-08-04*

## Self-Check: PASSED

All claimed created/modified files verified present on disk (`typsphinx/translator.py`,
`tests/fixtures/nested_table_render_gate/{conf.py,index.rst}`,
`tests/test_nested_table_render_gate.py`, `43-GATE-EVIDENCE-01.md`). All five claimed commits
verified present in `git log` (`05d4933`, `91b3a61`, `d58501a`, `db6d35a`, `ca507ef`), with
`05d4933^` confirmed to be `7bdaf40` (this worktree's expected base), proving the RED commits
genuinely precede the fix and this branch's history is isolated from concurrent worktree agents.
