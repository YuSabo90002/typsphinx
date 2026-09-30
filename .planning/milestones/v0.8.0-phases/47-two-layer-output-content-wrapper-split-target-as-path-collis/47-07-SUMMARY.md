---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 07
subsystem: testing
tags: [sphinx, typst, typst-py, docutils, output-builder, corpus-migration]

requires:
  - phase: 47-01
    provides: "47-EXPECTED-STRUCTURE.md's Corpus migration rules (R1-R5 table + fixture de-collision rule)"
  - phase: 47-02
    provides: "typsphinx.writer.render_wrapper()/compute_content_include_path()/compute_template_import_path_for_dir(); typsphinx.builder._content_output_path()/_wrapper_output_relpath()/_write_typst_files() -- the content/wrapper split this plan's corpus migrates against"
provides:
  - "Corpus group D (17 test modules, 16 fixture projects) migrated to the two-layer content/wrapper output shape and de-collided against the fixture de-collision rule"
  - "Every group-D fixture's typst_documents target renamed 'index' -> 'master.typ' (bare-target self-collision with the docname's own content path), except non_str_docname_gate's deliberately non-str second entry, left untouched by design"
  - "Re-verified end to end: BLD-01's non-str-docname guard still tolerates the rewritten wrapper-path and content-path computation without a raw TypeError"
affects: [47-09]

actuals:
  tokens: 11300
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "R1 (translator body markup) assertions keep reading the docname-derived content file (e.g. index.typ) unchanged; R2/R3 (template application / compile-target) assertions move to the target-derived wrapper file (master.typ/master.pdf) -- the same fixture's test module now reads two distinct files for two distinct assertion classes where both are exercised (documented_params_contract_gate, signature_overflow_render_gate)"
    - "A geometric probe that measures real production page geometry must be compiled atop the WRAPPER's own source (full template application), never the content file's -- appending a context measure() block to an untemplated content file would silently measure Typst's default page geometry instead of the project's A4/margin/font template"

key-files:
  created: []
  modified:
    - tests/test_desc_sig_space_render_gate.py
    - tests/test_inline_literal_overflow_render_gate.py
    - tests/test_paragraph_soft_newline_render_gate.py
    - tests/test_signature_typography_multi_signature_page_count_gate.py
    - tests/test_table_empty_caption_anchor_render_gate.py
    - tests/test_captioned_table_propagated_target_render_gate.py
    - tests/test_deflist_nested_definition_render_gate.py
    - tests/test_documented_params_contract_gate.py
    - tests/test_list_item_nested_block_render_gate.py
    - tests/test_rubric_option_concat_render_gate.py
    - tests/test_xref_orphan_degrade_render_gate.py
    - tests/test_codly_caption_listitem_leak_render_gate.py
    - tests/test_desc_break_marker_buffer_swap_gate.py
    - tests/test_field_body_typography_render_gate.py
    - tests/test_non_str_docname_gate.py
    - tests/test_signature_overflow_render_gate.py
    - tests/fixtures/captioned_table_propagated_target_render_gate/conf.py
    - tests/fixtures/codly_caption_listitem_leak_render_gate/conf.py
    - tests/fixtures/deflist_nested_definition_render_gate/conf.py
    - tests/fixtures/desc_break_marker_buffer_swap_gate/conf.py
    - tests/fixtures/desc_sig_space_render_gate/conf.py
    - tests/fixtures/documented_params_contract_gate/conf.py
    - tests/fixtures/field_body_typography_render_gate/conf.py
    - tests/fixtures/inline_literal_overflow_render_gate/conf.py
    - tests/fixtures/list_item_nested_block_render_gate/conf.py
    - tests/fixtures/non_str_docname_gate/conf.py
    - tests/fixtures/paragraph_soft_newline_render_gate/conf.py
    - tests/fixtures/rubric_option_concat_render_gate/conf.py
    - tests/fixtures/signature_overflow_render_gate/conf.py
    - tests/fixtures/signature_typography_gate/conf.py
    - tests/fixtures/table_empty_caption_anchor_render_gate/conf.py
    - tests/fixtures/xref_orphan_degrade_render_gate/conf.py

key-decisions:
  - "test_signature_typography_gate.py required NO path changes at all -- it is a pure R1 (translator body markup) module that already reads the content file (index.typ) exclusively via `-b typst` (no compile step), so once its fixture's self-collision was fixed by the conf.py target rename, the test passed unmodified. Confirmed by measurement: before the fix, index.typ physically held the WRAPPER's overwritten output (the wrapper silently clobbered the content file at the same path), which is why every sub-part test failed pre-fix -- not because of a translator regression."
  - "test_signature_overflow_render_gate.py's shared build fixture now returns BOTH the content path and the wrapper path, because its own single test file legitimately needs two different files for two different assertion classes in the SAME test: `_extract_addname_and_name` reads the content file's translator-emitted body (R1), while `_measure_widths` must compile its appended context probe atop the WRAPPER's own source so the measured column width reflects the REAL production template (A4/margins/font), not Typst's untemplated default page size."
  - "non_str_docname_gate's second typst_documents entry (docname 123, non-str) was deliberately left untouched by the de-collision rule -- a non-str docname has no content path to compute a collision against, and reaching that computation safely (skipping rather than crashing) is exactly what BLD-01's guard proves. Only the first, valid entry's target was renamed."
  - "The fixture de-collision rule's canonical replacement ('master.typ') was applied uniformly across all 16 group-D fixtures -- none of the fixtures' own stated purposes named a reason for a purpose-specific distinct target, so no fixture needed a conf.py comment beyond the standard collision note."

patterns-established: []

requirements-completed: [COMP-01, COMP-02, BLD-03]

coverage:
  - id: D1
    description: "Group-D page-count and typography cluster (6 modules, 5 fixtures) migrated: page-shaped and page-boundary assertions repointed at the compiled WRAPPER (master.typ/master.pdf); translator body markup assertions unchanged on the content file"
    requirement: "COMP-01"
    verification:
      - kind: integration
        ref: "tests/test_signature_typography_multi_signature_page_count_gate.py::TestSignatureTypographyMultiSignaturePageCountGate::test_multi_signature_document_page_count_at_real_geometry"
        status: pass
      - kind: integration
        ref: "tests/test_signature_typography_gate.py::TestSignatureTypographyGate (15 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Group-D template-contract and propagated-target cluster (6 modules, 6 fixtures) migrated: the published nine-parameter custom-template contract asserted against the wrapper's show-rule call with an unchanged parameter set; every propagated-target label assertion stays on the content file"
    requirement: "COMP-02"
    verification:
      - kind: integration
        ref: "tests/test_documented_params_contract_gate.py (7 tests)"
        status: pass
      - kind: integration
        ref: "tests/test_xref_orphan_degrade_render_gate.py::TestXrefOrphanDegradeRenderGate::test_typstpdf_orphan_xref_degrades_included_xref_links"
        status: pass
    human_judgment: false
  - id: D3
    description: "Remaining group-D gates and the malformed-docname gate (5 modules, 5 fixtures) migrated; BLD-01's non-str-docname guard re-verified against the rewritten wrapper-path and content-path computation"
    requirement: "BLD-03"
    verification:
      - kind: integration
        ref: "tests/test_non_str_docname_gate.py::TestNonStrDocnameGate::test_non_str_docname_fails_build_but_good_master_still_compiles"
        status: pass
      - kind: integration
        ref: "17 group-D modules together (82 tests) in one uv run pytest invocation"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 07: Group-D Corpus Migration (Page-Count, Template-Contract, Malformed-Docname Gates) Summary

**Migrated all 17 group-D test modules and their 16 fixture projects to the two-layer content/wrapper output shape, de-colliding every fixture's `typst_documents` target and repointing every page-shaped/template-contract/PDF-compile assertion at the compiled wrapper while leaving every translator-body-markup assertion on the docname content file -- zero assertion values changed.**

## Performance

- **Duration:** ~30 min
- **Tasks:** 3 (one commit each) + 1 black-formatting fix commit
- **Files modified:** 32 (16 fixture conf.py + 16 test modules)

## Accomplishments

- De-collided all 16 group-D fixtures whose `typst_documents` target ("index") casefold-collided with their own docname's content path ("index.typ") -- renamed to the canonical "master.typ" per the fixture de-collision rule, with one deliberate exception (`non_str_docname_gate`'s non-str second entry, left untouched since a non-str docname has no content path to collide against).
- Repointed every page-count/page-boundary compile target at the WRAPPER (`master.typ`/`master.pdf`) for the six-module typography/page-count cluster, leaving every page-index and page-count expectation byte-unchanged (`test_signature_typography_multi_signature_page_count_gate.py` still expects exactly 4 pages).
- Repointed the published nine-parameter custom-template contract gate (`test_documented_params_contract_gate.py`) at the wrapper's `#show: project.with(...)` call across all three of its build variants (main, determinism, no-toctree) -- the emitted parameter key set is unchanged, confirmed by `git diff` showing no parameter-set hunk.
- Repointed the orphan cross-reference degrade gate's PDF path at the wrapper; the degrade decision itself (driven by `master_included_docnames`, untouched this phase) is unchanged.
- Repointed four PDF-compile-only modules (three propagated-target label gates plus rubric/option) at `master.pdf`, keeping every label/anchor/adjacency assertion on the unchanged content file.
- Repointed the buffer-swap compile-acceptance test's `typst.compile()` call directly at the wrapper (a content file alone is not a complete, self-contained document).
- Repointed the field-body-typography PDF-adjacency fixture at `master.pdf`, keeping every structural `.typ` assertion on the content file.
- Re-verified BLD-01's non-str-docname guard end to end against the rewritten wrapper-path and content-path computation: still reports the offending value through the aggregate `ExtensionError`, never a raw `TypeError`.
- Redesigned `test_signature_overflow_render_gate.py`'s shared build fixture to expose BOTH the content path (for translator-body-markup extraction) and the wrapper path (so the geometric probe measures the real production page geometry from the applied template, not Typst's untemplated default).
- Confirmed `test_signature_typography_gate.py` needed zero changes: it is a pure R1 module reading the content file via `-b typst` with no compile step, and it failed pre-fix only because the fixture's self-collision made the wrapper silently overwrite the content file at the same physical path -- not because of any translator regression.
- All 17 group-D modules pass together in one `uv run pytest` invocation (82 tests, 0 failures).

## Task Commits

1. **Task 1: Migrate the page-count and typography cluster (6 modules, 5 fixtures)** - `256bcc0` (test)
2. **Task 2: Migrate the template-contract and propagated-target cluster (6 modules, 6 fixtures)** - `55f00a4` (test)
3. **Task 3: Migrate the remaining group-D gates and the malformed-docname gate (5 modules, 5 fixtures)** - `0132564` (test)
4. **Deviation fix: black-format the reformatted fixture** - `ed7ca6a` (style)

## Files Created/Modified

- 5 fixtures + 6 test modules (Task 1): `desc_sig_space_render_gate`, `inline_literal_overflow_render_gate`, `paragraph_soft_newline_render_gate`, `signature_typography_gate`, `table_empty_caption_anchor_render_gate` conf.py files; `test_desc_sig_space_render_gate.py`, `test_inline_literal_overflow_render_gate.py`, `test_paragraph_soft_newline_render_gate.py`, `test_signature_typography_multi_signature_page_count_gate.py`, `test_table_empty_caption_anchor_render_gate.py` (`test_signature_typography_gate.py` needed no code change).
- 6 fixtures + 6 test modules (Task 2): `captioned_table_propagated_target_render_gate`, `deflist_nested_definition_render_gate`, `documented_params_contract_gate`, `list_item_nested_block_render_gate`, `rubric_option_concat_render_gate`, `xref_orphan_degrade_render_gate` conf.py files and their matching test modules.
- 5 fixtures + 5 test modules (Task 3): `codly_caption_listitem_leak_render_gate`, `desc_break_marker_buffer_swap_gate`, `field_body_typography_render_gate`, `non_str_docname_gate`, `signature_overflow_render_gate` conf.py files and their matching test modules.

## Decisions Made

See `key-decisions` in frontmatter.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] black-formatted `deflist_nested_definition_render_gate/conf.py`**
- **Found during:** Post-task-3 overall verification (`uv run black --check .`)
- **Issue:** Task 2's renamed target (`"index"` -> `"master.typ"`) made the fixture's `typst_documents` tuple line exceed black's line length, and `black --check .` failed.
- **Fix:** Ran `uv run black tests/fixtures/deflist_nested_definition_render_gate/conf.py`, which wrapped the tuple onto multiple lines -- no content change.
- **Files modified:** `tests/fixtures/deflist_nested_definition_render_gate/conf.py`
- **Verification:** `uv run black --check .` now exits 0 (261 files unchanged); re-ran `tests/test_deflist_nested_definition_render_gate.py` -- still passes.
- **Committed in:** `ed7ca6a`

---

**Total deviations:** 1 auto-fixed (1 Rule 3 blocking). No scope creep -- required for this plan's own `<verification>` (`black --check .` must exit 0).

## Issues Encountered

None beyond the one auto-fixed deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Group D (17 modules, 16 fixtures) is fully migrated and green against the post-47-02 emitter. Combined with groups already migrated by sibling wave-3 plans (47-03 through 47-06/47-08), the corpus migration converges toward 47-09's full-suite-green gate.
- `ruff check .` could not run in this sandbox (pre-existing NixOS generic-linux-ELF limitation, unrelated to this plan, tracked separately per prior phases' notes) -- `black --check .` and `mypy typsphinx/` both pass and were run as the substitute lint/type gate per this plan's `<verification>`.
- `git diff --stat typsphinx/` is empty across all three tasks -- this plan touched only `tests/`.
- The four CR-01 self-collision fixtures explicitly out of scope for this plan (belonging to plan 47-09) were not touched.
- No blockers for 47-09: every group-D fixture's target is now de-collided per the fixture de-collision rule, and every assertion class (R1 content, R2 template application, R3 compile target, R4 PDF path, R5 toctree include) is correctly routed to content or wrapper per `47-EXPECTED-STRUCTURE.md`'s relocation table.

## Self-Check: PASSED

All 32 modified files verified present on disk via the edit tool's own state tracking; all four commits (`256bcc0`, `55f00a4`, `0132564`, `ed7ca6a`) verified present in `git log --oneline`. All 17 group-D modules (82 tests) re-run and pass together in the final verification step.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*
