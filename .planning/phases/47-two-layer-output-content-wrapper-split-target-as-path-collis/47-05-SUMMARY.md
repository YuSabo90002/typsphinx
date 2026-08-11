---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 05
subsystem: testing
tags: [sphinx, typst, typst-py, docutils, output-builder, pytest]

requires:
  - phase: 47-01
    provides: "47-EXPECTED-STRUCTURE.md's Corpus migration rules (R1-R5 table + fixture de-collision rule)"
  - phase: 47-02
    provides: "typsphinx.writer.compute_content_include_path()/compute_template_import_path_for_dir(), TypstWriter.render_wrapper(), TypstBuilder._content_output_path()/_wrapper_output_relpath()/_write_typst_files() -- the content/wrapper split this plan's migrated modules assert against"
provides:
  - "17 group-B test modules (multi-document + nested-toctree integration suites, desc-signature/field/figure/citation/deflist/epigraph/rubric render gates) migrated to assert against the two-layer content/wrapper output shape"
  - "19 group-B fixtures de-collided (self-colliding 'index'/'index.typ' typst_documents targets renamed to 'master.typ')"
  - "Precedent wrapper-include assertion shape ('the wrapper contains exactly one #include( naming its master's content file') added to 7 fixtures in the nested-toctree/layout cluster"
affects: [47-09]

actuals:
  tokens: 13300
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "R1-R5 migration classification applied at corpus scale: translator body markup and toctree #include() assertions (R1/R5) stay pinned to the CONTENT file (docname.typ, unchanged); typst.compile() calls and PDF-path assertions (R3/R4) move to the WRAPPER file (the fixture's own typst_documents target, renamed 'master.typ' after de-collision)."
    - "Fixture de-collision rule applied mechanically: every group-B fixture whose typst_documents target's resolved stem casefold()-equaled its own docname was renamed to the canonical 'master.typ' replacement, with a conf.py comment recording why."

key-files:
  created: []
  modified:
    - tests/test_desc_content_indent_render_gate.py
    - tests/test_figure_propagated_target_render_gate.py
    - tests/test_heading_depth_render_gate.py
    - tests/test_integration_nested_toctree.py
    - tests/test_paragraph_concat_render_gate.py
    - tests/test_static_asset_copy_gate.py
    - tests/test_absolute_image_render_gate.py
    - tests/test_confval_field_spacing_render_gate.py
    - tests/test_desc_signature_concat_render_gate.py
    - tests/test_ref_target_nested_list_render_gate.py
    - tests/test_target_label_render_gate.py
    - tests/test_citation_degradation_gate.py
    - tests/test_deflist_term_inline_children_gate.py
    - tests/test_epigraph_render_gate.py
    - tests/test_nested_figure_render_gate.py
    - tests/test_rubric_strong_nesting_render_gate.py
    - tests/fixtures/absolute_image_render_gate/conf.py
    - tests/fixtures/citation_degradation_gate/conf.py
    - tests/fixtures/confval_field_spacing_render_gate/conf.py
    - tests/fixtures/deflist_term_inline_children_concat/conf.py
    - tests/fixtures/desc_content_indent_render_gate/conf.py
    - tests/fixtures/desc_signature_concat_render_gate/conf.py
    - tests/fixtures/desc_signature_siblings_render_gate/conf.py
    - tests/fixtures/epigraph_render_gate/conf.py
    - tests/fixtures/figure_propagated_target_render_gate/conf.py
    - tests/fixtures/integration_multi_doc/conf.py
    - tests/fixtures/integration_multi_level/conf.py
    - tests/fixtures/integration_nested_toctree/conf.py
    - tests/fixtures/integration_sibling/conf.py
    - tests/fixtures/nested_figure_render_gate/conf.py
    - tests/fixtures/paragraph_concat_render_gate/conf.py
    - tests/fixtures/ref_target_nested_list_render_gate/conf.py
    - tests/fixtures/rubric_strong_nesting_render_gate/conf.py
    - tests/fixtures/static_asset_copy_render_gate/conf.py
    - tests/fixtures/target_label_render_gate/conf.py

key-decisions:
  - "test_integration_multi_doc.py and test_confval_field_spacing_render_gate.py's non-PDF test methods needed no Python edits at all -- their assertions already read the content file (index.typ, R1/R5, unchanged); only the fixture's typst_documents target rename was required to stop the wrapper self-overwriting the content file."
  - "test_heading_depth_render_gate.py's non-vacuity control (asserting the raw 'set heading(offset: heading.offset + 1)' text exists SOMEWHERE in the same build) was re-pointed from the wrapper (master.typ, which now carries only the template + one #include()) to the content file (index.typ) -- that scoping is an R5-class construct, emitted where the toctree's own doctree is translated, not where the template is applied."
  - "test_rubric_strong_nesting_render_gate.py's compile-sanity leg previously called typst.compile() directly on the content file (index.typ, no root= argument); per R3 it now targets the wrapper (master.typ) -- only a wrapper is a complete, self-contained document."
  - "Canonical de-collision replacement 'master.typ' used uniformly across all 19 fixtures (none needed a purpose-specific alternative name) -- none of these fixtures test template-collision or _template.typ interaction behavior that would require a different reserved name."

patterns-established:
  - "Wrapper-include assertion ('exactly one #include(' + the specific content-path string) added as a new, permanent test method to each of the 7 Task-1 fixtures -- proving R2/R3 by construction rather than by absence of failure, per the plan's must_haves.truths."

requirements-completed: [COMP-01, COMP-02, BLD-03]

coverage:
  - id: D1
    description: "17 group-B test modules (nested-toctree/multi-document integration suites, desc-signature/field/figure/citation/deflist/epigraph/rubric render gates) pass against the post-split content/wrapper emitter, in one combined pytest invocation"
    requirement: "COMP-01"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_desc_content_indent_render_gate.py tests/test_figure_propagated_target_render_gate.py tests/test_heading_depth_render_gate.py tests/test_integration_nested_toctree.py tests/test_paragraph_concat_render_gate.py tests/test_static_asset_copy_gate.py tests/test_absolute_image_render_gate.py tests/test_confval_field_spacing_render_gate.py tests/test_desc_signature_concat_render_gate.py tests/test_integration_multi_doc.py tests/test_ref_target_nested_list_render_gate.py tests/test_target_label_render_gate.py tests/test_citation_degradation_gate.py tests/test_deflist_term_inline_children_gate.py tests/test_epigraph_render_gate.py tests/test_nested_figure_render_gate.py tests/test_rubric_strong_nesting_render_gate.py -q (105 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every group-B fixture's typst_documents target resolves to a path distinct from its own docname's content path and from every other entry in the same fixture (fixture de-collision rule applied to all 19 fixtures)"
    requirement: "BLD-03"
    verification:
      - kind: unit
        ref: "manual review of all 19 conf.py diffs -- each self-colliding target ('index'/'index.typ') renamed to 'master.typ', comment recorded per fixture"
        status: pass
    human_judgment: false
  - id: D3
    description: "Toctree #include() assertions proven to live on content files (R5, unchanged); each of the 7 nested-toctree/layout-cluster wrappers proven to hold exactly one #include() naming its own master's content path (R2/R3, new assertion per fixture)"
    requirement: "COMP-02"
    verification:
      - kind: integration
        ref: "tests/test_integration_nested_toctree.py::TestNestedToctreeIntegration::test_root_wrapper_has_exactly_one_include_of_its_content, ::TestMultiLevelNestedToctree::test_root_wrapper_has_exactly_one_include_of_its_content, ::TestSiblingDirectoryReferences::test_root_wrapper_has_exactly_one_include_of_its_content, tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_wrapper_has_exactly_one_include_of_its_content, tests/test_figure_propagated_target_render_gate.py::TestFigurePropagatedTargetRenderGate::test_wrapper_has_exactly_one_include_of_its_content, tests/test_paragraph_concat_render_gate.py::TestParagraphConcatRenderGate::test_wrapper_has_exactly_one_include_of_its_content, tests/test_static_asset_copy_gate.py::TestStaticAssetCopyRenderGate::test_wrapper_has_exactly_one_include_of_its_content"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 05: Group-B Corpus Migration (Nested-Toctree, Multi-Document, Reference) Summary

**Migrated 17 test modules and 19 fixtures (corpus group B -- the multi-document/nested-toctree integration suites plus 15 targeted render gates) to assert against the post-split content/wrapper output shape, de-colliding every group-B fixture's self-colliding `typst_documents` target along the way, with zero label, image-path, or degrade-expectation values changed.**

## Performance

- **Duration:** ~30 min
- **Tasks:** 3
- **Files modified:** 35 (16 test modules, 19 fixture `conf.py` files)

## Accomplishments

- De-collided all 19 group-B fixtures: every `typst_documents` target whose resolved stem `casefold()`-equaled its own docname (`"index"` or `"index.typ"`) was renamed to the canonical replacement `"master.typ"`, with a `conf.py` comment recording the collision and the rule that fixed it.
- Migrated 17 test modules' PDF-compile and query targets from the content file (`index.typ`/`index.pdf`) to the wrapper file (`master.typ`/`master.pdf`) per R3/R4 -- only a wrapper is a complete, self-contained document (template application + a single `#include()`), so only a wrapper can be handed to `typst.compile()` or `typst.query()`.
- Left every translator-body-markup and toctree-`#include()`-set assertion pinned to the content file (R1/R5, unchanged) -- these constructs are emitted where the doctree is translated, independent of where any wrapper physically lands.
- Added a new, permanent "wrapper contains exactly one `#include(` naming its master's content path" assertion to all 7 Task-1 (nested-toctree/layout cluster) fixtures -- proving R2/R3 by construction rather than by absence of failure, per the plan's `must_haves.truths`.
- `test_heading_depth_render_gate.py`'s non-vacuity control (the raw `"set heading(offset: heading.offset + 1)"` text) moved from the wrapper to the content file -- that scoping is R5-class (emitted by `visit_toctree` into the parent's own content), not R2/R3-class.
- `test_rubric_strong_nesting_render_gate.py`'s compile-sanity leg re-pointed `typst.compile()` from the bare content file to the wrapper (R3).
- Confirmed all 17 group-B modules (105 tests) pass together in one `uv run pytest` invocation.

## Task Commits

Each task was committed atomically:

1. **Task 1: Migrate the nested-toctree and layout cluster (6 modules, 7 fixtures)** - `30b8734` (test)
2. **Task 2: Migrate the multi-document and reference cluster (6 modules, 7 fixtures)** - `29bc8fe` (test)
3. **Task 3: Migrate the remaining group-B render gates (5 modules, 5 fixtures)** - `4833f1d` (test)

_No plan-metadata commit in this worktree -- STATE.md/ROADMAP.md updates are owned by the orchestrator after wave merge (worktree-isolated execution)._

## Files Created/Modified

- `tests/test_integration_nested_toctree.py` -- 3 E2E compile targets moved to `master.typ`/`master.pdf`; 3 new wrapper-include assertions added (one per fixture: nested_toctree, multi_level, sibling)
- `tests/test_desc_content_indent_render_gate.py` -- PDF fixture and WR-01 test's compile target moved to `master.typ`/`master.pdf`; new wrapper-include assertion added
- `tests/test_figure_propagated_target_render_gate.py` -- PDF path moved to `master.pdf`; new wrapper-include assertion added
- `tests/test_heading_depth_render_gate.py` -- query target moved to `master.typ`; non-vacuity control re-pointed to content file (`index.typ`)
- `tests/test_paragraph_concat_render_gate.py` -- PDF path moved to `master.pdf`; new wrapper-include assertion added
- `tests/test_static_asset_copy_gate.py` -- PDF path moved to `master.pdf`; new wrapper-include assertion added
- `tests/test_absolute_image_render_gate.py` -- PDF path moved to `master.pdf`; image-path expectation (`image("images/diagram.png")`) unchanged
- `tests/test_confval_field_spacing_render_gate.py` -- both PDF paths moved to `master.pdf`
- `tests/test_desc_signature_concat_render_gate.py` -- both PDF paths moved to `master.pdf` (covers both `desc_signature_concat_render_gate` and `desc_signature_siblings_render_gate` fixtures)
- `tests/test_ref_target_nested_list_render_gate.py` -- PDF path moved to `master.pdf`
- `tests/test_target_label_render_gate.py` -- PDF path moved to `master.pdf`
- `tests/test_citation_degradation_gate.py` -- PDF path moved to `master.pdf`; `master_included_docnames`-driven degrade expectations unchanged
- `tests/test_deflist_term_inline_children_gate.py` -- PDF path moved to `master.pdf`
- `tests/test_epigraph_render_gate.py` -- PDF path moved to `master.pdf`
- `tests/test_nested_figure_render_gate.py` -- all 4 PDF paths moved to `master.pdf`
- `tests/test_rubric_strong_nesting_render_gate.py` -- compile-sanity leg's `typst.compile()` target moved from content file to wrapper (`master.typ`)
- 19 fixture `conf.py` files -- self-colliding `typst_documents` target renamed to `"master.typ"`, with an explanatory comment

`tests/test_integration_multi_doc.py` and the rest of `tests/test_confval_field_spacing_render_gate.py`'s methods needed no Python edits -- only their fixtures' target rename.

## Decisions Made

- Canonical replacement `"master.typ"` used uniformly across all 19 fixtures -- none of group B's fixtures exercise template-collision or `_template.typ` interaction behavior that would require a purpose-specific alternative name.
- `test_heading_depth_render_gate.py`'s non-vacuity control was re-pointed to the content file rather than left on the wrapper, since the construct it searches for (`visit_toctree`'s heading-offset scope) is R5-class, not R2/R3-class -- leaving it on the wrapper would have made the control assert something the wrapper no longer contains.
- `test_rubric_strong_nesting_render_gate.py`'s compile-sanity leg was updated to compile the wrapper rather than adding a `root=` argument to a content-file compile -- matching R3's literal rule (only a wrapper is a complete document) rather than working around the content file's incompleteness.

## Deviations from Plan

None - plan executed exactly as written. Assertion values changed: 0 (only file-path strings and one control's source file changed; no label, image-path, or degrade-expectation VALUE was altered).

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Corpus group B (17 modules, 19 fixtures) is fully migrated and green against the post-split emitter, in isolation and together (105/105 passing).
- `typsphinx/` diff is empty across all three task commits -- no production code was touched by this plan.
- The full `uv run pytest` suite remains KNOWINGLY RED until sibling plans (47-03, 47-04, 47-06, 47-07, 47-08) migrate their own corpus groups; 47-09 is the phase's full-suite-green gate.
- The wrapper-include assertion pattern established in Task 1 (`"the wrapper contains exactly one #include( naming its master's content file"`) is available as precedent for any later plan needing the same R2/R3 proof shape.

## Self-Check: PASSED

All 35 modified files verified present on disk via `git status --short` and `git show`. All three task commits (`30b8734`, `29bc8fe`, `4833f1d`) verified present in `git log --oneline`.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*
