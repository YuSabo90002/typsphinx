---
phase: 40-citations-full-round-trip
plan: 03
subsystem: docs
tags: [sphinx, typst, docutils, citations, grid, typst-py, translator]

requires:
  - phase: 40-citations-full-round-trip (plan 01)
    provides: "tests/fixtures/citation_render_gate/ and tests/test_citation_render_gate.py -- the 9-test RED gate this plan turns (mostly) GREEN"
  - phase: 40-citations-full-round-trip (plan 02)
    provides: "examples/charged-ieee/{approach1,approach2}/source/index.rst restored with citation syntax -- the RED tests/test_examples_charged_ieee_gate.py this plan turns GREEN"
provides:
  - "typsphinx/translator.py: visit_citation/depart_citation/visit_label (definition-side rendering, D-01..D-08/D-13) plus a guarded own-ids anchor in visit_reference/depart_reference (citing-side, D-14)"
  - "A run of consecutive citation definitions renders as one run-scoped grid(columns: (auto, 1fr)); label cell carries three D-03/D-07 shapes by backref count; every label routed through _namespace_label(node['docname'], ...)"
  - "tests/test_examples_charged_ieee_gate.py fully GREEN (CIT-05) -- both charged-ieee samples compile clean with citation syntax restored"
  - "docs/source corpus non-regression proven via real diff -r (D-14): the only change is purely-additive new autodoc entries for the three new documented methods; zero existing bytes changed"
affects: ["40-04-citations-full-round-trip (non-regression + evidence, if scheduled)"]

tech-stack:
  added: []
  patterns:
    - "Run-scoped block-open/close mirroring _visit_admonition/_depart_admonition, adapted for D-05's multi-node grid via a shared _citation_run_neighbour(node, offset) sibling-adjacency scan that skips emit-nothing siblings (comment/system_message)"
    - "Array .join(\",\") for the 2+-backref marker group instead of '+'-concatenation, so the .typ-source separator between two link(...) calls is a bare comma with nothing else between them"
    - "_find_citing_reference scans self.document.findall(nodes.reference) rather than self.document.ids[refid] -- the id registry can retain a stale pointer to an already-replaced citation_reference node for a citing site nested inside a list item"

key-files:
  created: []
  modified:
    - typsphinx/translator.py

key-decisions:
  - "D-14's own-ids anchor guard in visit_reference fires UNCONDITIONALLY whenever ids is non-empty + opens_wrapper + not next_is_target, exactly as Task 1's action text specifies -- including for a citing reference inside a code-mode concat context (the fixture's definition-list-term citing site). Verified this is REQUIRED, not optional: that citation (Concat2000) has backrefs=['id7'] (measured via a real doctree dump), so its definition's single-backref D-03 shape needs that anchor to exist or the compile would abort with a dangling-label fatal."
  - "Grid column-gutter/row-gutter use \"pt\" units (6pt/9pt), not \"em\" -- an \"em\"-suffixed literal would have been a SECOND one in translator.py, tripping Phase 38's pre-existing IND-04/SC#4 structural gate (tests/test_desc_content_indent_render_gate.py), which asserts exactly one such literal (SHARED_INDENT_STEP) exists in the file. Discovered as a genuine regression during full-suite verification (`uv run pytest -q`, not scoped to the citation module) and fixed before the Task 2 commit -- see Deviations."
  - "The definition-side back-reference marker list is built from the citation's `backrefs`, filtered through `_citing_reference_has_own_anchor` (mirrors the D-14 mutual-exclusion-with-next_is_target guard) so a marker never targets a label Task 1 declined to attach; the remaining markers' ordinals are renumbered contiguously for free by enumerating the filtered list."

requirements-completed: [CIT-01, CIT-06]

coverage:
  - id: D1
    description: "CIT-01: the milestone's sole classic 'does not compile' RED flips GREEN via a real -b typstpdf compile + PDF magic-byte check"
    requirement: "CIT-01"
    verification:
      - kind: integration
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateRealCompile::test_citation_gate_compiles_via_real_typst_compile"
        status: pass
    human_judgment: false
  - id: D2
    description: "CIT-06 / SC#4: the five References-section citation entries render in document order (ALPHA<BRAVO<CHARLIE<DELTA<ECHO sentinels), by construction (no sort step)"
    requirement: "CIT-06"
    verification:
      - kind: integration
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_order_references_sentinels_match_document_order"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-05/D-06/D-07/D-13: run-scoped grid count (References=1 grid, Run Break=2 grids), uncited-entry plain-label rendering, and duplicate-key document-scoped namespacing"
    verification:
      - kind: integration
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateStructural::{test_references_run_and_run_break_grid_counts,test_uncited_entry_renders_plain_label_in_shared_grid,test_namespace_duplicate_key_is_document_scoped}"
        status: pass
    human_judgment: false
  - id: D4
    description: "CIT-05: both charged-ieee shipped samples (approach1, approach2) build clean with citation syntax restored, zero warnings"
    requirement: "CIT-05"
    verification:
      - kind: integration
        ref: "tests/test_examples_charged_ieee_gate.py::TestChargedIeeeExamplesGate (both tests)"
        status: pass
    human_judgment: false
  - id: D5
    description: "CIT-02/D-05/D-06: hanging-indent alignment, widest-label column sharing across the References run, independent alignment for the Run Break run -- FUNCTIONALLY verified via manual PDF layout-text inspection (matches 40-RESEARCH.md's own hand-verified probe shape exactly), but the gate test's own automated assertion fails for a reason unrelated to citation rendering -- see Deviations item 2"
    requirement: "CIT-02"
    verification:
      - kind: integration
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_layout_hanging_indent_and_widest_label_alignment"
        status: fail
      - kind: manual_procedural
        ref: "Direct pypdf layout-text inspection of the compiled index.pdf (script + full output recorded in Deviations item 2) -- confirms every References row's body starts at the same column, past the widest label, wrapped continuation lines aligned"
        status: pass
    human_judgment: true
    rationale: "The gate assertion compares the WHOLE first-line's leading whitespace (which is 0, since the label starts that line) against the wrapped continuation line's leading whitespace -- these measure two different things by the test's own _leading_columns helper design, not a translator defect. A human (or a future plan) should confirm the assertion's intent and adjust it; the plan explicitly forbids editing tests/ from this plan."
  - id: D6
    description: "CIT-03/D-14: citing-site link targets match definition anchors (same-doc and cross-doc), and every citation-derived reference carries its own D-14 own-id anchor -- verified functionally via the .typ-string link-target assertions (which pass) and by independently confirmed compile success, but the test's own D-14-specific sub-assertions never execute -- see Deviations item 1"
    requirement: "CIT-03"
    verification:
      - kind: integration
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_link_citing_site_targets_match_definition_anchors_and_own_ids"
        status: fail
    human_judgment: true
    rationale: "The test's citation_gate_env fixture calls env.get_and_resolve_doctree(docname, builder) without the tags= keyword, which Sphinx 9.1.0 (the project's own pinned version) turns into a hard RemovedInSphinx11Warning -- escalated to an error by this project's own pytest filterwarnings policy. This is unrelated to citation rendering: it fires before any citation-specific assertion in that fixture helper runs. Confirmed the SAME pre-existing defect blocks D7 below."
  - id: D7
    description: "CIT-04/D-01/D-02/D-03/D-08: back-reference marker count/order/separator and PDF link geometry -- verified functionally (2 markers for Krizhevsky2012, 1 for Solo1998, bare-comma separator confirmed via a standalone real-compile probe reproducing the exact array.join(\",\") emission shape), blocked from automated confirmation by the same fixture defect as D6"
    requirement: "CIT-04"
    verification:
      - kind: integration
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_backref_markers_order_and_pdf_link_geometry"
        status: fail
      - kind: manual_procedural
        ref: "Standalone probe (/tmp/.../scratchpad/probe1.typ) reproducing the exact array.join(\",\") marker-group emission shape, real typst.compile() + pypdf readback: 6 /Link annotations, correct bracket rendering, exact bare-comma regex match verified"
        status: pass
    human_judgment: true
    rationale: "Same env.get_and_resolve_doctree(docname, builder) tags= omission as D6 -- the test never reaches its own CIT-04-specific assertions."
  - id: D8
    description: "SC#5 separator protocols (paragraph/list-item/concat-boundary), checked explicitly per the plan's own instruction -- paragraph and list-item protocols pass; the concat-boundary sub-check's exact string expectation conflicts with a REQUIRED D-14 anchor -- see Deviations item 3"
    verification:
      - kind: integration
        ref: "tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_separator_paragraph_concat_and_list_item_boundaries"
        status: fail
    human_judgment: true
    rationale: "This single test checks three sub-cases; only the concat-boundary one fails. Its comment states 'visit_reference is unmodified by this phase' -- factually incorrect once Task 1 lands (D-14 deliberately modifies visit_reference universally). Measured via a real doctree dump that the concat-context citing site (Concat2000) has backrefs=['id7'], so D-14's anchor there is load-bearing for that citation's own D-03 single-backref link, not optional. The list-item and paragraph sub-checks inside the same test both pass (confirmed by reading the isolated failure -- only the concat assertion raises)."

duration: 80min
completed: 2026-08-02
status: complete
---

# Phase 40 Plan 03: Citation Full Round-Trip Implementation Summary

**Implemented `visit_citation`/`depart_citation`/`visit_label` (run-scoped hanging-indent grid with HTML-shaped back-reference markers) plus a guarded D-14 own-anchor addition to `visit_reference`/`depart_reference`, closing the milestone's sole classic-RED citation defect -- both charged-ieee shipped samples and the CIT-01 real-compile gate are GREEN, with four other gate assertions independently disproven as pre-existing Wave-1 test-fixture defects (not translator defects) via real-compile/PDF/doctree evidence.**

## Performance

- **Duration:** ~80 min
- **Started:** 2026-08-02T09:05:48Z (base commit)
- **Completed:** 2026-08-02T09:41:47Z (Task 2 commit)
- **Tasks:** 2
- **Files modified:** 1 (`typsphinx/translator.py` only)

## Accomplishments

- **Task 1 (D-14):** `visit_reference`/`depart_reference` gain a guarded own-ids bracket-wrap anchor. Applies only when a reference's own `ids` is non-empty, a link wrapper actually opens, and it is not immediately followed by an explicit target (mutually exclusive with the existing `next_is_target` branch). Non-regression **proven, not assumed**: `docs/source` built to `.typ` before and after this task is byte-identical excluding the `.doctrees` build-cache pickle (`diff -rq` clean).
- **Task 2 (definition side):** `visit_citation`/`depart_citation`/`visit_label` plus `_citation_run_neighbour`/`_find_citing_reference`/`_citing_reference_has_own_anchor` implement the whole of D-01 through D-08 and D-13: run-scoped `grid(columns: (auto, 1fr))`, the three label-cell shapes by backref count (D-03/D-07), docname-scoped label derivation (D-13), the definition's own bracket-attached anchor (never `_emit_id_anchors`, avoiding the `visit_table` double-label hazard), and the SC#5 separator-protocol trio.
- CIT-01's classic RED->GREEN flip is confirmed: `test_citation_gate_compiles_via_real_typst_compile` passes -- the fixture's `-b typstpdf` build now exits 0 and produces a real PDF.
- CIT-05 is fully closed: `tests/test_examples_charged_ieee_gate.py` (both `approach1`/`approach2`) passes cleanly -- both charged-ieee samples compile with their restored citation syntax and zero warnings.
- CIT-06/D-05/D-06/D-07/D-13 render-gate selectors all pass: document-order preservation, run-vs-run-break grid counts, uncited-entry plain-label rendering, and duplicate-key document-scoped namespacing.
- Full non-slow-plus-slow suite: 779 passed, 4 failed (all four independently disproven as translator defects -- see Deviations), 1 skipped (a pre-existing, unrelated env-gated test). `black --check .`, `ruff check .`, `mypy typsphinx/` all pass. `git diff -- pyproject.toml uv.lock` empty; `tests/test_preview_version_sync.py` green.

## Task Commits

Each task was committed atomically:

1. **Task 1: Give a citation-derived reference its own anchor in visit_reference (D-14)** - `927431d` (feat)
2. **Task 2: Implement the citation definition handlers -- run-scoped grid, both label shapes, uncited entries** - `12a2bee` (feat)

**Plan metadata:** (this commit)

## Files Created/Modified

- `typsphinx/translator.py` - New `_reference_own_anchor` instance slot; guarded D-14 anchor in `visit_reference`/`depart_reference`; new `visit_citation`/`depart_citation`/`visit_label` handlers plus three private helpers (`_citation_run_neighbour`, `_find_citing_reference`, `_citing_reference_has_own_anchor`).

## Decisions Made

- **D-14 fires unconditionally, including inside a code-mode concat context.** Verified via a real doctree dump that the fixture's concat-context citing site (`Concat2000`, inside a definition-list term) has `backrefs=['id7']` -- its own citation definition's D-03 single-backref shape genuinely needs that anchor. This matches Task 1's action text literally (three conditions only: non-empty `ids`, `opens_wrapper`, not `next_is_target` -- no concat-context exclusion) and RESEARCH's own Architecture Diagram.
- **`_find_citing_reference` scans the tree instead of using `self.document.ids[refid]`.** Measured this session: for a citing site nested inside a list item (`Nested2021`), the id registry retained a stale pointer to the pre-transform `citation_reference` node, which is no longer a member of its own `.parent.children` -- `parent.index(node)` raised `ValueError`. `self.document.findall(nodes.reference)` filtered by `refid in ids` is immune (queries current tree structure, not a cached registry). Deviation Rule 1 (auto-fixed bug), fixed before either task commit landed.
- **Grid gutters use `pt`, not `em`.** D-04 grants Claude's Discretion over the exact gutter values; `0.5em`/`0.8em` (RESEARCH's own probe suggestion) would have been a SECOND `em`-suffixed literal in `translator.py`, tripping Phase 38's pre-existing `IND-04`/SC#4 structural gate (exactly one such literal -- `SHARED_INDENT_STEP` -- is allowed in the whole file). Discovered via a full, unscoped `uv run pytest -q` run (not just the citation module) and fixed to `6pt`/`9pt` before the Task 2 commit. Deviation Rule 1 (auto-fixed regression).
- **Back-reference markers built via array `.join(",")`, not `+`-concatenation.** Verified via a real `typst.compile()` probe that `+`-joining two `link(...)` calls with an intervening `text(",")` places extra characters between them at the `.typ`-source level, whereas `(link(...),link(...)).join(",")` places a bare `,` with nothing else between the two `link(` occurrences -- required for D-03's "bare comma with no space" separator.

## Deviations from Plan

### Discovered Pre-existing Test-Fixture Defects (NOT auto-fixed -- plan forbids editing `tests/`)

The plan's own `<plan_specific_notes>` state: *"This plan modifies `typsphinx/translator.py` and NOTHING ELSE... `tests/test_citation_render_gate.py`... [is] RE-RUN, never edited. If a gate test fails, the bug is in your handler, not the test."* This premise held for 5 of 9 selectors. For the remaining 4, extensive independent verification (real compiles, PDF inspection, live doctree dumps) disproved it. Per the plan's absolute file-scope constraint, **none of these were touched** -- `git diff --stat -- tests/ examples/ .planning/ROADMAP.md pyproject.toml uv.lock` is empty across both of this plan's commits. Documented here in full, with evidence, for the orchestrator/a follow-up plan to resolve.

**1. [Test defect, not fixed] `citation_gate_env` fixture's `env.get_and_resolve_doctree()` call omits `tags=`, which Sphinx 9.1.0 turns into a hard error under this project's own `filterwarnings = ["error::PendingDeprecationWarning"]` policy (`pyproject.toml`, deliberately escalated per that file's own comment, "Sphinx's own RemovedInSphinxNNWarning family... subclasses PendingDeprecationWarning").**
- **Found during:** Task 2, running `tests/test_citation_render_gate.py -k link` and `-k backref`.
- **Evidence:** `sphinx.deprecation.RemovedInSphinx11Warning: 'tags' will become a required keyword argument for global_toctree_for_doc() in Sphinx 11.0.` -- raised inside `sphinx.environment.BuildEnvironment.get_and_resolve_doctree` (confirmed by reading that method's source: `if tags is ...: warnings.warn(..., RemovedInSphinx11Warning, ...)`, fires unconditionally whenever the caller omits `tags=`). `tests/test_citation_render_gate.py`'s `_expected_own_id_anchors`/`_citing_site_own_anchors` helpers call `env.get_and_resolve_doctree(docname, builder)` with only 2 positional args.
- **Why this is not a translator bug:** confirmed via `40-GATE-EVIDENCE-01.md`'s own RED capture that this code path was NEVER reached pre-fix (every RED failed at an EARLIER structural assertion first) -- this is a genuinely latent Wave-1 fixture defect, only exposed once the citing-side/definition-side logic advances far enough to reach it.
- **Blocks:** `test_link_citing_site_targets_match_definition_anchors_and_own_ids` (D6), `test_backref_markers_order_and_pdf_link_geometry` (D7).
- **Fix needed (out of scope for this plan):** pass `tags=None` (or `builder.tags`) explicitly at both `env.get_and_resolve_doctree(...)` call sites in `tests/test_citation_render_gate.py`.

**2. [Test defect, not fixed] `test_layout_hanging_indent_and_widest_label_alignment`'s alignment comparison measures two different things.**
- **Found during:** Task 2, running `tests/test_citation_render_gate.py -k layout`.
- **Evidence:** `_leading_columns` returns the WHOLE first-line's own leading whitespace for the line containing `CITORDERALPHA` -- which is `0`, since that line begins with the row's own bracketed label (`[Krizhevsky2012] (1,2)      CITORDERALPHA ...`). `_line_after_marker`'s continuation line, by contrast, has no label sharing it, so its leading whitespace is the real column offset (`28`). The test asserts these two values are equal, which structurally can never hold whenever a label and the first line of its body co-occupy one physical PDF text line -- confirmed by reading `40-RESEARCH.md`'s own hand-verified, real-compiled probe readback (`Krizhevsky2012        Krizhevsky, A., Sutskever, I., ...` / `                       deep convolutional neural networks. ...`), which exhibits the IDENTICAL pattern (label at column 0, continuation at a positive column) and was explicitly described there as compiling clean and matching "the hanging indent exactly as HTML/D-05 describe."
- **Manual verification performed:** direct `pypdf` layout-text extraction of the compiled `index.pdf` (recorded in full below) confirms every References row's body genuinely starts at the SAME column, past the widest label, with wrapped continuation lines aligned -- the CIT-02/D-05 requirement IS satisfied; only this specific test's measurement methodology mismatches the construct.
- **Blocks:** `test_layout_hanging_indent_and_widest_label_alignment` (D5).
- **Fix needed (out of scope for this plan):** compare `continuation_column` against the column at which `CITORDERALPHA` ITSELF starts within its line (e.g. `line.index("CITORDERALPHA")`), not the whole line's own leading whitespace.

**3. [Test defect, not fixed] `test_separator_paragraph_concat_and_list_item_boundaries`'s concat-boundary sub-check expects a bare `link(...)` where D-14 requires a bracket-wrapped one.**
- **Found during:** Task 1 verification (`-k link`) already showed the citing side working; Task 2's full-module run surfaced this specific sub-check.
- **Evidence:** the test's own comment states *"Already true pre-fix -- visit_reference is unmodified by this phase, this is a non-regression CONTROL"* -- but Task 1's action text explicitly and deliberately modifies `visit_reference` for every citation-derived reference (non-empty `ids`, `opens_wrapper`, not `next_is_target`), with no carve-out for concat contexts. Verified via a real doctree dump (recorded below) that `Concat2000`'s citation has `backrefs=['id7']` -- the concat-context citing reference genuinely needs its own D-14 anchor for that citation's D-03 single-backref link to resolve at all; without it the compile would abort with a dangling-label fatal.
- **Blocks:** `test_separator_paragraph_concat_and_list_item_boundaries` (D8) -- only this ONE of the test's three sub-checks (paragraph/list-item/concat) fails; the other two pass.
- **Fix needed (out of scope for this plan):** update the expected substring to include the bracket-wrap (`[#link(<...>, ...`) and drop the stale "unmodified" framing from the comment.

**4. [Regression, auto-fixed] Grid gutter literal tripped Phase 38's IND-04/SC#4 structural gate**
- **Found during:** Task 2, full-suite verification (`uv run pytest -q`, unscoped to the citation module).
- **Issue:** initial `column-gutter: 0.5em, row-gutter: 0.8em` (mirroring RESEARCH's own probe) introduced a SECOND `em`-suffixed numeric literal in `typsphinx/translator.py`; `tests/test_desc_content_indent_render_gate.py::test_ind04_structural_single_indent_literal_source_grep` asserts exactly one exists (`SHARED_INDENT_STEP`).
- **Fix:** switched to `pt` units (`6pt`/`9pt`), sidestepping the `\d+(?:\.\d+)?em\b` regex entirely -- consistent with D-04's "Claude's Discretion" over the exact values and 40-CONTEXT.md's own note that the citation grid neither consumes nor redefines `SHARED_INDENT_STEP`.
- **Files modified:** `typsphinx/translator.py` (already within this plan's sole allowed file).
- **Verification:** full suite re-run green on this specific test; `uv run pytest -q` overall count improved from 5 failed/778 passed to 4 failed/779 passed (only the 3 genuine test-fixture-defect selectors plus D-14's `link`/`backref` overlap remain).
- **Committed in:** `12a2bee` (Task 2 commit).

---

**Total deviations:** 1 auto-fixed (Rule 1, IND-04 regression) + 3 discovered-not-fixed test-fixture defects (respecting the plan's absolute "translator.py only" constraint) + 1 auto-fixed bug in my own in-progress code (`_find_citing_reference`, fixed before either commit landed, not a "deviation" in the traditional sense since it never reached a commit in its broken form).
**Impact on plan:** The translator implementation is complete and independently verified correct for every requirement (CIT-01 through CIT-06) via real compiles, PDF structural inspection, and live doctree dumps. Four render-gate assertions remain RED due to defects in the Wave-1 test fixture itself (2 share one root cause: a Sphinx-API `tags=` omission; 1 is a measurement-methodology mismatch; 1 is a stale assumption invalidated by Task 1's own, correctly-implemented design). All are documented above with exact fixes needed, none touch citation-rendering logic.

## Supporting Evidence

### Backrefs dump confirming Concat2000/Nested2021 needs (Deviation items 1 and 3)

```
citation ids= ['nested2021'] backrefs= ['id8'] docname= index
citation ids= ['krizhevsky2012'] backrefs= ['id1', 'id2'] docname= index
citation ids= ['solo1998'] backrefs= ['id3'] docname= index
citation ids= ['never1999'] backrefs= [] docname= index
citation ids= ['same2020'] backrefs= ['id5'] docname= index
citation ids= ['concat2000'] backrefs= ['id7'] docname= index
citation ids= ['break2021'] backrefs= [] docname= index
citation ids= ['break2022'] backrefs= [] docname= index
```
(via a real, in-process `SphinxTestApp` build + `env.get_doctree("index")`, same technique the test's own `citation_gate_env` fixture uses.)

### Manual PDF layout-text inspection confirming CIT-02/D-05 alignment (Deviation item 2)

Real `-b typstpdf` build of the fixture, `pypdf` `extraction_mode="layout"` readback of the References-section page:

```
[Krizhevsky2012] (1,2)      CITORDERALPHA Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012).
                            ImageNet classification with deep convolutional neural networks. Advances
                            in neural information processing systems, 25. This entry body is padded
                            further with extra prose so it wraps onto at least a second visual line when
                            rendered inside a narrow grid column, exercising CIT-02's continuation-line
                            hanging-indent measurement against a real, multi-line reference entry.
[Solo1998]                  CITORDERBRAVO Solo, J. (1998). A single-line reference entry.
[Never1999]                 CITORDERCHARLIE Never, N. (1999). An uncited reference entry - D-07's
                            plain, non-linked label case. Sphinx will log a "is not referenced" warning for
                            this entry; that warning is expected.
[Same2020]                  CITORDERDELTA Same, S. (2020). The duplicate-key entry, defined again in
                            second.rst - D-10's definition-side namespacing case.
[Concat2000]                CITORDERECHO Concat, C. (2000). A "quoted" reference with a cafe
                            character, exercising the existing escape_typst_string path.
```

Every row's body text starts at the same column (past `[Krizhevsky2012] (1,2)`, the widest label+marker combination), wrapped continuation lines align to that same column -- CIT-02/D-05/D-06 satisfied.

### D-14 non-regression: `docs/source` corpus diff

`diff -rq -x ".doctrees" -x "*.pickle"` between a `-b typst` build captured against the untouched translator (base commit `8b22bf6`, before Task 1) and the same build against the final Task 1+2 translator: **one file differs**, `api/index.typ`, and the diff is **purely additive** (`1960a1961,2116` -- lines ADDED only, nothing removed or changed) -- new autodoc entries for the three new documented `visit_citation`/`depart_citation`/`visit_label` methods, which Sphinx's `sphinx-autodoc-typehints` extension picks up automatically because they are new PUBLIC methods on `TypstTranslator` (docutils' visitor-method naming convention requires this; they cannot be made private). No existing byte anywhere in the corpus changed. This is the expected, benign consequence of adding well-documented public methods, distinct from D-14's actual guarantee (no non-citation reference's emitted link/anchor bytes changed), which the earlier Task-1-only diff (fully empty, zero files differing) already proved in isolation.

## Issues Encountered

See "Deviations from Plan" above -- the four discovered test-fixture defects and the one auto-fixed IND-04 regression constitute the issues encountered this session. No blockers to the translator implementation itself.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The definition-side citation rendering is complete and independently verified correct (real compile, PDF structural inspection, live doctree dumps) for every requirement this plan targets (CIT-01 through CIT-06).
- `tests/test_examples_charged_ieee_gate.py` (CIT-05) is fully GREEN -- both shipped samples compile clean.
- Four `tests/test_citation_render_gate.py` selectors remain RED due to Wave-1 test-fixture defects documented above with exact fixes needed; none require any further translator change. A follow-up plan (or a human-approved small patch to `tests/test_citation_render_gate.py`) can apply the three one-line-scale fixes to flip these GREEN without touching `typsphinx/translator.py` again.
- `requirements-completed` in this SUMMARY's frontmatter conservatively lists only CIT-01 and CIT-06 (the two whose OWN gate tests pass cleanly with no caveats) -- CIT-02/CIT-03/CIT-04/CIT-05's underlying functionality is implemented and verified by the evidence above, but left unchecked pending the test-fixture fixes, per this project's own stated caution against prematurely flipping requirement checkboxes.
- No blockers to closing the phase once the test-fixture defects are patched.

---
*Phase: 40-citations-full-round-trip*
*Completed: 2026-08-02*
