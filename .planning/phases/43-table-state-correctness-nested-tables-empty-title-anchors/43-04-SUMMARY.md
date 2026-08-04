---
phase: 43-table-state-correctness-nested-tables-empty-title-anchors
plan: 04
subsystem: translator
tags: [sphinx, docutils, typst, table-anchoring, translator, gate-01]

# Dependency graph
requires:
  - phase: 43-01
    provides: "_push_table_state()/_pop_table_state() snapshot stack this plan extends with _table_is_captioned"
provides:
  - "typsphinx/translator.py: self._table_is_captioned -- the STRUCTURAL captioned decision from visit_table, stashed for depart_table's anchoring gate, independent of whether the caption renders to anything (TBL-05 fix)"
  - "typsphinx/translator.py: depart_table's RENDERING (table_caption truthiness) and ANCHORING (structural_is_captioned) decisions are now split and allowed to disagree, matching Sphinx's LaTeX builder (D-05)"
  - "typsphinx/translator.py: _emit_id_anchors's docstring corrected to name both real skip_ids callers (depart_figure, depart_table), re-derived from a fresh re-grep run after all three of this phase's translator.py changes had landed (QUA-01)"
  - "tests/fixtures/table_empty_caption_anchor_render_gate/{conf.py,index.rst}: two-section TBL-05 reproduction fixture (empty-rendered raw-html caption + real-caption numbering control)"
  - "tests/test_table_empty_caption_anchor_render_gate.py: GATE-01 real-compile render gate, 2 test methods"
  - "43-GATE-EVIDENCE-04.md: RED commit SHA (de018926ed49f114d260d368ed7cf63794d3cfee) and fix commit SHA (0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2) plan 43-05 consumes for the phase-wide SC#4 sweep"
affects: [43-05]

# Actuals (#2632)
actuals:
  tokens: 11834
  tasks: 3
  commits: 6

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Split RENDERING from ANCHORING as two independently-gated decisions on the same node, deliberately allowed to disagree (mirrors the D-05 LaTeX-builder precedent measured in 43-CONTEXT.md): a value that is only known at depart time (rendered caption truthiness) gates the visual shape, while a value known at visit time (structural node-type check) gates correctness-critical id anchoring -- reusing plan 43-01's snapshot-stack pattern to keep the structural decision correct across nesting"

key-files:
  created:
    - tests/fixtures/table_empty_caption_anchor_render_gate/conf.py
    - tests/fixtures/table_empty_caption_anchor_render_gate/index.rst
    - tests/test_table_empty_caption_anchor_render_gate.py
    - .planning/phases/43-table-state-correctness-nested-tables-empty-title-anchors/43-GATE-EVIDENCE-04.md
  modified:
    - typsphinx/translator.py

key-decisions:
  - "Read the doctree probe via a real Sphinx -b typst build (app.env.get_doctree), not bare docutils.core.publish_doctree -- the latter under-measures: it returned ids: ['tbl-target'] with no 'id1', because docutils' own auto-id assignment for the propagated-target case only fires under Sphinx's full environment. The Sphinx-driven probe matches the fixture's real build path and is what the evidence file records as authoritative, correcting a mismatch discovered during this session's own measurement, not carried from a planning document."
  - "structural_is_captioned (the new TBL-05 anchoring gate) and was_captioned (the existing TBL-02/TBL-03 rendering gate, now also reused to answer 'did this table take the figure-wrapped branch') are both captured as locals at the exact same point in depart_table -- immediately before the nested/top-level destination decision -- because _table_is_captioned now joins the snapshot-stack set (per the plan) and would otherwise read the ENCLOSING table's restored value for a nested table's own depart_table."
  - "self._table_is_captioned is assigned in visit_table AFTER the nested-table push (self._push_table_state()), not before -- an ordering bug caught and corrected during this task before any test ran: assigning it before the push would make the push capture the NEW (inner) table's decision instead of the ENCLOSING table's, defeating the snapshot's whole purpose for this one field. Mirrors the existing table_cells/table_colcount/table_colwidths ordering already in that method."
  - "skip_ids on the anchoring call is conditional, not always {ids[0]}: skip_ids={ids[0]} only when the table actually took the figure-wrapped branch (was_captioned True, i.e. something else already self-anchors ids[0] via the figure's own <label>); on the bare-table branch (structurally captioned but rendered empty) every id is anchored, since nothing else anchors ids[0] for a table that stayed a plain table(...) call."

patterns-established:
  - "Doctree probing via a real Sphinx build (app.env.get_doctree) rather than bare docutils.core.publish_doctree, when a construct's id-propagation behaviour depends on Sphinx's own environment machinery, not docutils alone."

requirements-completed: [TBL-05, QUA-01]

coverage:
  - id: D1
    description: "A captioned table whose title renders to the empty string emits its id anchors, so a :ref: pointing at it resolves and the document compiles to a PDF instead of aborting the whole build at Typst's label-resolution pass"
    requirement: TBL-05
    verification:
      - kind: integration
        ref: "tests/test_table_empty_caption_anchor_render_gate.py::TestTableEmptyCaptionAnchorRenderGate::test_build_exits_zero_and_anchors_the_propagated_target"
        status: pass
    human_judgment: false
  - id: D2
    description: "The empty-rendered-caption table is NOT figure-wrapped and consumes NO table number: a real captioned table later in the same document still renders as Table 1, not Table 2"
    requirement: TBL-05
    verification:
      - kind: integration
        ref: "tests/test_table_empty_caption_anchor_render_gate.py::TestTableEmptyCaptionAnchorRenderGate::test_pdf_text_has_all_cells_and_control_table_is_numbered_one"
        status: pass
    human_judgment: false
  - id: D3
    description: "No new warning is emitted for a caption that renders empty -- the build's warning output is unchanged (D-06), measured via an empty diff between the RED and GREEN build logs' WARNING lines"
    requirement: TBL-05
    verification:
      - kind: other
        ref: "43-GATE-EVIDENCE-04.md warning diff section (grep -i warning on both /tmp/tecarg-red.log and /tmp/tecarg-green.log, both empty)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The visit-side captioned pre-check stays STRUCTURAL (D-07) -- not made value-aware -- confirmed by the doctree probe showing the reproducing construct's title child is a raw node whose astext() is non-empty while its rendered result is empty"
    requirement: TBL-05
    verification:
      - kind: other
        ref: "43-GATE-EVIDENCE-04.md doctree probe section (measured via app.env.get_doctree)"
        status: pass
    human_judgment: false
  - id: D5
    description: "A table title that renders to a non-empty string keeps today's behaviour exactly: figure-wrapped, numbered, ids anchored -- pre-existing table gates (captioned-table-propagated-target, nested-table, nested-figure) all stay green"
    requirement: TBL-05
    verification:
      - kind: integration
        ref: "tests/test_captioned_table_propagated_target_render_gate.py + tests/test_nested_table_render_gate.py + tests/test_nested_figure_render_gate.py (22 passed)"
        status: pass
      - kind: other
        ref: "uv run python -m pytest -q (836 passed, 1 skipped) + uv run black --check . + uv run ruff check . + uv run mypy typsphinx/"
        status: pass
    human_judgment: false
  - id: D6
    description: "_emit_id_anchors's docstring names both real skip_ids callers, depart_figure and depart_table, verified by a re-grep of the call sites performed AFTER this phase's nesting work landed rather than by trusting any recorded count -- and does not enumerate every _emit_id_anchors call site"
    requirement: QUA-01
    verification:
      - kind: other
        ref: "43-GATE-EVIDENCE-04.md QUA-01 section (verbatim grep -n '_emit_id_anchors(' and grep -n 'skip_ids' output, 21 total call sites / exactly 2 skip_ids callers, source assertions in Task 3's own acceptance criteria)"
        status: pass
    human_judgment: false

duration: ~16min
completed: 2026-08-04
status: complete
---

# Phase 43 Plan 04: Empty-Rendered-Caption Table Id Anchoring + `_emit_id_anchors` Docstring Correction Summary

**Split `depart_table`'s single "is this captioned?" check into two independently-gated decisions -- RENDERING (unchanged, gated on the rendered caption's truthiness) and ANCHORING (new, gated on the structural `_table_is_captioned` stashed at visit time) -- so a table whose title node exists but renders to the empty string anchors its ids, is not figure-wrapped, and consumes no table number, matching Sphinx's own LaTeX builder measured against identical input; also corrected `_emit_id_anchors`'s docstring to name both real `skip_ids` callers from a fresh post-nesting-work re-grep.**

## Performance

- **Duration:** ~16 min (measured commit span 00:51:47Z-01:00:48Z; provisioning/exploration preceded the first commit)
- **Started:** 2026-08-04 (session start, forked from `829b807`)
- **Completed:** 2026-08-04T01:02:24Z
- **Tasks:** 3/3
- **Files modified:** 5 (1 production file, 4 test/fixture/evidence files)

## Accomplishments

- Closed TBL-05: a captioned table whose title renders to the empty string (the exact reproducing construct: a `raw-html` role applied to an empty `<span></span>`, whose `astext()` is non-empty but whose rendered result is empty because `visit_raw` raises `SkipNode` for a non-typst format) no longer leaves its ids unanchored on both `visit_table`'s structural path and `depart_table`'s rendered-caption path. A propagated `.. _target:` id on such a table now anchors, so a same-document `:ref:` to it resolves instead of aborting the whole `typst.compile()` with `TypstError: label ... does not exist in the document`.
- Proved the D-05 numbering invariant directly against a compiled PDF (not the `.typ` source): the empty-rendered-caption table stays a bare `table(...)` (not figure-wrapped) and consumes no table number -- a real-caption control table later in the same document renders as `Table 1`, never `Table 2`.
- Confirmed D-06 (no new warning) with an empty diff between the RED and GREEN build logs' `WARNING` output -- the pre-fix failure is a Typst compile FATAL (an `ExtensionError` wrapping a `TypstError`), never a Sphinx-level warning about the caption.
- Recorded a genuine classic-`TypstError` RED baseline against the unfixed translator (exit 2, no PDF produced, the emitted `.typ` showing a dangling `link(<index:tbl-target>, ...)` with no matching anchor), with a 40-hex RED commit SHA plan 43-05 will consume, then a matching GREEN transcript (exit 0, both `metadata(none)` anchors present, PDF produced) after the fix.
- Corrected the `_emit_id_anchors` docstring's stale "sole user is `depart_figure`" claim (false since Phase 25) to name both real `skip_ids` callers, `depart_figure` and `depart_table`, derived from a fresh re-grep run in this session AFTER waves 1-3 of this phase had all landed in `translator.py` -- 21 total call sites, exactly 2 pass `skip_ids`, no discrepancy against D-08's expectation and no third caller introduced by this phase.
- Confirmed every pre-existing table/figure render gate (`captioned_table_propagated_target`, `nested_table`, `nested_figure`) stays green, and the full suite grew from the 834/1 baseline to 836/1 (2 new tests), with `black`/`ruff`/`mypy` all clean and no new runtime dependency.

## Task Commits

Each task was committed atomically (Tasks 1-3 each split into a code/test commit and a small evidence-follow-up commit, per the RED-first discipline and the self-reference problem plan 43-01 established a precedent for):

1. **Task 1a: RED fixture + render gate** - `de01892` (test) -- `typsphinx/translator.py` untouched
2. **Task 1b: RED evidence SHA follow-up** - `51b45b0` (docs)
3. **Task 2a: TBL-05 fix (structural anchoring gate)** - `0b6cbbc` (feat)
4. **Task 2b: GREEN evidence follow-up** - `fe1cd96` (docs)
5. **Task 3a: QUA-01 docstring correction** - `355298d` (docs)
6. **Task 3b: QUA-01 evidence follow-up** - `1937380` (docs)

## Files Created/Modified

- `typsphinx/translator.py` - `__init__` adds `self._table_is_captioned`; `_push_table_state`/`_pop_table_state` extended to snapshot/restore it; `visit_table` stashes the structural decision AFTER the nested-table push; `depart_table` splits `structural_is_captioned` (anchoring gate) from `was_captioned` (rendering gate + "did this table figure-wrap" check for conditional `skip_ids`); `_emit_id_anchors`'s docstring rewritten to name both `skip_ids` callers
- `tests/fixtures/table_empty_caption_anchor_render_gate/conf.py` - Fixture Sphinx config, `index` as a master document, `numfig = True`
- `tests/fixtures/table_empty_caption_anchor_render_gate/index.rst` - Two-section TBL-05 reproduction fixture (empty-rendered raw-html caption + real-caption numbering control)
- `tests/test_table_empty_caption_anchor_render_gate.py` - GATE-01 render gate, 2 test methods (build/anchor/warning assertions; PDF-text/numbering assertions)
- `.planning/phases/43-table-state-correctness-nested-tables-empty-title-anchors/43-GATE-EVIDENCE-04.md` - Doctree probe, RED baseline (RED commit SHA `de018926ed49f114d260d368ed7cf63794d3cfee`), GREEN transcript (fix commit SHA `0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2`), warning diff, QUA-01 re-grep section, full-suite/lint/type gate results

## Decisions Made

- **Doctree probe measured via a real Sphinx build, not bare docutils.** An initial probe using `docutils.core.publish_doctree` under-measured the fixture: it returned `ids: ['tbl-target']` with no auto-assigned `id1`, because that second id is only assigned under Sphinx's full environment (its own `PropagateTargets`/id-assignment machinery), not bare docutils. Re-measured via `app.env.get_doctree("index")` after a real `-b typst` build, which matched the CONTEXT document's own prior measurement (`ids: ['id1', 'tbl-target']`) exactly. The evidence file records the Sphinx-driven probe as authoritative and notes why the bare-docutils attempt disagreed, rather than silently discarding the discrepancy.
- **`self._table_is_captioned` assignment ordering bug caught before any test ran.** The first draft assigned `self._table_is_captioned = is_captioned` immediately after computing `is_captioned`, BEFORE the `if self.in_table: self._push_table_state()` branch -- which would make the push snapshot the NEW (inner) table's decision instead of the ENCLOSING table's, silently defeating the snapshot's purpose for this one field on any nested captioned table. Caught by re-reading `_push_table_state`'s docstring and the existing `table_cells`/`table_colcount`/`table_colwidths` reset ordering in the same method, and moved to occur immediately after the push, alongside those three.
- **`skip_ids` made conditional in `depart_table`, not left as a bare `{ids[0]}`.** T-43-11 in the threat model (double-defining a label) required distinguishing "this table actually figure-wrapped" (skip `ids[0]`, since the figure's own `<label>` postfix already anchors it) from "this table is structurally captioned but did NOT figure-wrap" (anchor `ids[0]` too, since nothing else anchors it). Both conditions are derivable from `was_captioned`, computed once and reused for both the original rendering gate and this new question -- no second re-read of `self.table_caption` after its later reset.

## Deviations from Plan

None (Rules 1-4) - plan executed as written. The `test_table_empty_caption_anchor_render_gate.py` NBSP-normalization fix (Typst emits a non-breaking space between "Table" and the figure number, which the initial assertion in this plan's own new test did not account for) is a self-correction of newly-authored test code within the same task, not a deviation from the plan's specification -- it is documented here for completeness since it landed in the same commit as the translator fix.

## Issues Encountered

- **`docutils.core.publish_doctree` under-measured the doctree probe** (see Decisions Made) -- resolved by probing through a real Sphinx build instead, which is also the path the fixture's actual test exercises.
- **A same-task ordering bug in the `_table_is_captioned` assignment** (see Decisions Made) -- caught and corrected before any GREEN measurement was taken, so no incorrect result was ever recorded as evidence.
- **The NBSP-vs-space mismatch in `test_table_empty_caption_anchor_render_gate.py`'s own numbering assertion** -- `pypdf` extracts Typst's default figure-numbering separator as U+00A0, not a regular space; the test's assertion literal was updated to normalize this before matching, verified against the actual extracted text before the fix.
- **The NixOS `uv`/`ruff` ELF-interpreter hazard**, as documented for this worktree: `.venv/bin/uv` was symlinked to the Nix-store `uv` binary; `.venv/bin/ruff` had no standalone Nix package available in this environment, so its interpreter was patched via `patchelf --set-interpreter` to the same glibc loader path already proven working in the main tree's `.venv` (mirrors plan 43-03's precedent).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- TBL-05 and QUA-01 are both fully closed with a real RED-to-GREEN proof recorded in `43-GATE-EVIDENCE-04.md`, including the RED commit SHA (`de018926ed49f114d260d368ed7cf63794d3cfee`) and fix commit SHA (`0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2`) that plan 43-05's phase-wide SC#4 two-build byte-invariance sweep is expected to consume.
- The full test suite (836 passed, 1 skipped -- 834 baseline + 2 new), `black --check .`, `ruff check .`, and `mypy typsphinx/` are all green on this worktree's HEAD; `pyproject.toml`/`uv.lock` are unmodified (no new dependency).
- No blockers for plan 43-05 (the phase-wide SC#4/SC#5/SC#6 sweep) -- this plan's changes are confined to `visit_table`/`depart_table`/`_emit_id_anchors` in `translator.py`, disjoint from plan 43-01's table-nesting scope (only extending its existing snapshot-stack pattern) and plan 43-03's figure-nesting scope, per the wave plan.

---
*Phase: 43-table-state-correctness-nested-tables-empty-title-anchors*
*Completed: 2026-08-04*

## Self-Check: PASSED

All claimed created/modified files verified present on disk (`typsphinx/translator.py`,
`tests/fixtures/table_empty_caption_anchor_render_gate/{conf.py,index.rst}`,
`tests/test_table_empty_caption_anchor_render_gate.py`, `43-GATE-EVIDENCE-04.md`). All six claimed
commits verified present in `git log` (`de01892`, `51b45b0`, `0b6cbbc`, `fe1cd96`, `355298d`,
`1937380`), with `de01892^` confirmed to be `829b807` (this worktree's expected base), proving the
RED commits genuinely precede the fix and this branch's history is isolated from concurrent
worktree agents.
