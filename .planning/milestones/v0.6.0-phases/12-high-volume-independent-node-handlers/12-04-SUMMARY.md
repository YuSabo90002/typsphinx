---
phase: 12-high-volume-independent-node-handlers
plan: 04
subsystem: translator
tags: [docutils, sphinx, typst, translator, render-gate]

# Dependency graph
requires:
  - phase: 12-high-volume-independent-node-handlers (plans 01-03)
    provides: file-ownership sequencing on translator.py and test_pdf_render_gate.py (versionmodified, xref/refid depart_term anchor fix, desc_* handlers)
provides:
  - visit_transition/depart_transition (BLK-01) horizontal-rule handler
  - visit_glossary/depart_glossary (BLK-04) pass-through handler
  - visit_tabular_col_spec (BLK-05) SkipNode handler
  - visit_abbreviation/depart_abbreviation (BLK-06) stateless inline-expansion handler
  - trivial_blocks_render_gate fixture project
  - TestTrivialBlocksRenderGate real-compile test class
affects: [phase-13-shared-dispatch-point-changes, phase-15-full-corpus-validation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "dummy-Text-node delegation for stateless inline expansion (depart_abbreviation -> visit_Text), the fourth use of this idiom in translator.py"
    - "emit-literal-then-SkipNode for self-closing content-bearing nodes (visit_transition)"
    - "bare-SkipNode for self-closing no-content-equivalent nodes (visit_tabular_col_spec)"

key-files:
  created:
    - tests/fixtures/trivial_blocks_render_gate/conf.py
    - tests/fixtures/trivial_blocks_render_gate/index.rst
  modified:
    - typsphinx/translator.py
    - tests/test_pdf_render_gate.py

key-decisions:
  - "Placed all four new handlers together in one block immediately after depart_index, rather than scattering them near each idiom's original analog -- keeps the BLK-01/04/05/06 group locally readable as a single cohesive unit matching the plan's single-task grouping."
  - "Chose distinctive ALL-CAPS sentinel tokens (GLOSSARYDEFSENTINEL, LEAKCOLSPECSENTINEL, ABBREXPANSIONSENTINEL) in the fixture so the render-gate test can positively assert presence (glossary def, abbr expansion) and negatively assert absence (tabularcolumns leak) without ambiguity."

requirements-completed: [BLK-01, BLK-04, BLK-05, BLK-06]

coverage:
  - id: D1
    description: "A `----` transition renders a horizontal rule (line(length: 100%)) in the compiled PDF"
    requirement: "BLK-01"
    verification:
      - kind: e2e
        ref: "tests/test_pdf_render_gate.py::TestTrivialBlocksRenderGate::test_trivial_blocks_pdf_renders_rule_glossary_and_abbr_no_leak"
        status: pass
    human_judgment: false
  - id: D2
    description: "A `.. glossary::` renders its underlying definition list (transparent pass-through)"
    requirement: "BLK-04"
    verification:
      - kind: e2e
        ref: "tests/test_pdf_render_gate.py::TestTrivialBlocksRenderGate::test_trivial_blocks_pdf_renders_rule_glossary_and_abbr_no_leak"
        status: pass
    human_judgment: false
  - id: D3
    description: "A `.. tabularcolumns::` LaTeX-only hint is skipped safely via raise nodes.SkipNode with no leaked column-spec content"
    requirement: "BLK-05"
    verification:
      - kind: e2e
        ref: "tests/test_pdf_render_gate.py::TestTrivialBlocksRenderGate::test_trivial_blocks_pdf_renders_rule_glossary_and_abbr_no_leak"
        status: pass
    human_judgment: false
  - id: D4
    description: "An `:abbr:` renders inline as 'term (expansion)' at every occurrence (stateless), routed through visit_Text escaping"
    requirement: "BLK-06"
    verification:
      - kind: e2e
        ref: "tests/test_pdf_render_gate.py::TestTrivialBlocksRenderGate::test_trivial_blocks_pdf_renders_rule_glossary_and_abbr_no_leak"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-07-12
status: complete
---

# Phase 12 Plan 04: Trivial Structural Node Handlers (BLK-01/04/05/06) Summary

**Four small additive translator.py handlers -- transition-to-rule, glossary pass-through, tabularcolumns SkipNode, and stateless abbreviation-expansion -- proven correct through a real sphinx-build -> typst.compile() -> pypdf round-trip.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-07-12T11:15:30+09:00 (base commit)
- **Completed:** 2026-07-12T11:20:12+09:00
- **Tasks:** 3
- **Files modified:** 3 (1 modified, 2 created)

## Accomplishments
- `visit_transition`/`depart_transition` (BLK-01): closes a genuine content gap -- a `----` transition rendered nothing before this plan; now emits `line(length: 100%)` then `raise nodes.SkipNode`.
- `visit_glossary`/`depart_glossary` (BLK-04): transparent pass-through pair that silences the `unknown_visit: <glossary>` warning noted as a deferred item in Plan 12-02 -- the wrapped `definition_list` already rendered correctly via the existing chain, and the term anchor fix (Plan 12-02's `depart_term`) is left untouched, not duplicated.
- `visit_tabular_col_spec` (BLK-05): bare `raise nodes.SkipNode` that safely drops the LaTeX-only `.. tabularcolumns::` hint with no risk of leaking the column-spec string.
- `visit_abbreviation`/`depart_abbreviation` (BLK-06): closes a genuine content gap -- the `explanation` attribute was completely dropped before this plan. Now appended inline as `" (expansion)"` via a dummy `nodes.Text(...)` delegated to `visit_Text`, inheriting the existing escaping regime automatically. Stateless per D-08 -- no first-occurrence tracking variable, expands on every occurrence.
- New `trivial_blocks_render_gate` fixture project exercising all four cases in one minimal Sphinx project.
- New `TestTrivialBlocksRenderGate` class extending the GATE-01 standing bar: a real compile proves the rule renders, the glossary definition reaches the PDF, the tabularcolumns spec token is absent (no leak), and the abbreviation renders as `term (expansion)` -- with no `LEAK_SIGNATURES` token present.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add transition, glossary, tabular_col_spec, abbreviation handlers** - `f5be1c1` (feat)
2. **Task 2: Create the trivial_blocks_render_gate fixture project** - `734fc17` (test)
3. **Task 3: Add TestTrivialBlocksRenderGate real-compile class** - `fa72b4d` (test)

_Note: Task 2/3 are `test` commits per the plan's own file classification (fixture project + test class), not TDD RED/GREEN pairs -- this plan is not TDD-tagged._

## Files Created/Modified
- `typsphinx/translator.py` - Added `visit_transition`/`depart_transition`, `visit_glossary`/`depart_glossary`, `visit_tabular_col_spec`, `visit_abbreviation`/`depart_abbreviation` (inserted as one block immediately after `depart_index`)
- `tests/fixtures/trivial_blocks_render_gate/conf.py` - Minimal Sphinx config (master `typst_documents` tuple)
- `tests/fixtures/trivial_blocks_render_gate/index.rst` - Fixture covering a `----` transition, a `.. glossary::` term, a `.. tabularcolumns::` hint before a `list-table`, and an `:abbr:` role, each with a distinctive sentinel token
- `tests/test_pdf_render_gate.py` - Added `trivial_blocks_render_gate_dir` fixture and `TestTrivialBlocksRenderGate` class (sentinel constants `GLOSSARY_DEF_SENTINEL`, `LEAK_COL_SPEC_SENTINEL`, `ABBR_EXPANSION_SENTINEL`)

## Decisions Made
- All four handlers were placed in a single new block directly after `depart_index` rather than distributed near each idiom's original analog location (`visit_comment`/`visit_raw` for BLK-01, `visit_desc_content` for BLK-04, `visit_title_reference`/`visit_literal_strong` for BLK-06) -- this keeps the entire BLK-01/04/05/06 group locally readable as the single cohesive unit the plan's Task 1 describes, at a small cost of not being physically adjacent to each analog.
- Fixture sentinel tokens use distinctive ALL-CAPS names (`GLOSSARYDEFSENTINEL`, `LEAKCOLSPECSENTINEL`, `ABBREXPANSIONSENTINEL`) rather than natural prose, so the render-gate test's positive assertions (glossary definition, abbreviation expansion) and negative assertion (tabularcolumns no-leak) are unambiguous.

## Deviations from Plan

None - plan executed exactly as written. All four handlers match the `12-PATTERNS.md`/`12-RESEARCH.md` target implementations verbatim (confirmed via direct comparison before writing).

## Issues Encountered
- `black` reformatted `tests/test_pdf_render_gate.py` after the Task 3 edit (whitespace/line-wrap normalization only, confirmed via `git diff --stat` showing pure insertions with no unrelated lines touched). Re-ran the fast suite, render-gate suite, ruff, and black after the reformat -- all green.
- Pre-existing environmental failures (documented in `deferred-items.md` under Plan 12-01, carried forward unchanged): 45 tests across `tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py` fail with `Could not start dynamically linked executable: uv` (NixOS sandbox limitation, `["uv", "run", "sphinx-build", ...]` subprocess invocation). Confirmed none of these files were touched by this plan and the failure count/set is unchanged before and after (45 failed both times). Out of scope per SCOPE BOUNDARY rule.
- Confirmed as a side effect: the `WARNING: unknown node type: <glossary ...>` warning noted as a deferred item in Plan 12-02's `deferred-items.md` is now resolved -- rebuilding `xref_refid_render_gate` after this plan's `visit_glossary`/`depart_glossary` pass-through produces no glossary-related warning.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- BLK-01/04/05/06 complete; the phase's remaining requirement groups (versionmodified/VER-01, xref/XREF-01, desc_*/DESC-01..04) landed in Plans 12-01/12-02/12-03, so Phase 12 requirement coverage (XREF-01, VER-01, DESC-01..04, BLK-01, BLK-04, BLK-05, BLK-06) is now fully closed pending orchestrator wave-completion bookkeeping.
- Phase 13 (shared dispatch-point changes: BLK-02/BLK-03, `visit_title` generalization) can proceed independently -- no shared state or file conflicts introduced by this plan beyond the now-stable `translator.py`/`test_pdf_render_gate.py` files.
- No blockers identified.

## Self-Check: PASSED

- FOUND: typsphinx/translator.py (visit_transition, visit_glossary, visit_tabular_col_spec, visit_abbreviation all present)
- FOUND: tests/fixtures/trivial_blocks_render_gate/conf.py
- FOUND: tests/fixtures/trivial_blocks_render_gate/index.rst
- FOUND: tests/test_pdf_render_gate.py (TestTrivialBlocksRenderGate class present, 8/8 render-gate tests pass)
- FOUND commit f5be1c1, 734fc17, fa72b4d in `git log --oneline`

---
*Phase: 12-high-volume-independent-node-handlers*
*Completed: 2026-07-12*
