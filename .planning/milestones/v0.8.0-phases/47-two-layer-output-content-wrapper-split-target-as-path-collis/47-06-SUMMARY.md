---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 06
subsystem: testing
tags: [sphinx, typst, typst-py, docutils, output-builder, test-migration]

requires:
  - phase: 47-02
    provides: "typsphinx.writer.compute_content_include_path()/compute_template_import_path_for_dir(), TypstWriter.render_wrapper(), TypstWriter.translate() rewritten for content-only emission, typsphinx.builder._escapes_outdir()/_content_output_path()/_wrapper_output_relpath()/_write_typst_files(), TypstPDFBuilder.finish() reading back through _wrapper_output_relpath()"
provides:
  - "17 group-C test modules and 18 fixture projects migrated to the post-split content/wrapper output shape"
  - "Every group-C fixture's typst_documents target de-collided from its own docname content path (D-01 self-collision)"
  - "entry_title_author_render_gate extended with a D-04 repeated-docname second entry, proving D-08's positional per-entry title/author read end to end"
  - "Two R3 manual-typst.compile() call sites (test_rubric_indent_invariance.py, test_signature_break_and_arrow_gate.py) repointed from the content file to the wrapper file"
affects: [47-09]

actuals:
  tokens: 14547
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Fixture de-collision: a typst_documents target whose resolved stem casefold()-equals its own docname's content path is retargeted to the canonical 'master.typ', or to a purpose-specific name with the reason recorded in the fixture's own conf.py comment when the fixture's own purpose already names its target for an unrelated reason (admonition_greyscale_probe's alphabetical-sort dependency on scripts/render_admonition_greyscale.py)"
    - "R1-R5 assertion-class relocation: translator body markup (R1) and toctree #include() emission (R5) stay on the docname-derived content file unchanged; template application (R2), a compile() target (R3), and a compiled PDF (R4) move to the target-derived wrapper file"

key-files:
  created: []
  modified:
    - tests/test_desc_rubric_decoupling_render_gate.py
    - tests/test_glob_image_render_gate.py
    - tests/test_integration_advanced.py
    - tests/test_integration_basic.py
    - tests/test_paragraph_propagated_target_render_gate.py
    - tests/test_substitution_definition_render_gate.py
    - tests/test_admonition_greyscale_pipeline.py
    - tests/test_deflist_definition_multiblock_render_gate.py
    - tests/test_document_metadata_render_gate.py
    - tests/test_label_at_char_render_gate.py
    - tests/test_rubric_indent_invariance.py
    - tests/test_wide_table_render_gate.py
    - tests/test_citation_render_gate.py
    - tests/test_desc_bodyless_concat_render_gate.py
    - tests/test_external_link_style_render_gate.py
    - tests/test_nested_table_render_gate.py
    - tests/test_signature_break_and_arrow_gate.py
    - tests/fixtures/admonition_greyscale_probe/conf.py
    - tests/fixtures/citation_render_gate/conf.py
    - tests/fixtures/deflist_definition_multiblock_render_gate/conf.py
    - tests/fixtures/desc_bodyless_concat_render_gate/conf.py
    - tests/fixtures/desc_rubric_decoupling_render_gate/conf.py
    - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
    - tests/fixtures/entry_empty_metadata_render_gate/conf.py
    - tests/fixtures/entry_title_author_render_gate/conf.py
    - tests/fixtures/external_link_style_render_gate/conf.py
    - tests/fixtures/glob_image_render_gate/conf.py
    - tests/fixtures/integration_basic/conf.py
    - tests/fixtures/integration_math_figures/conf.py
    - tests/fixtures/label_at_char_render_gate/conf.py
    - tests/fixtures/nested_table_render_gate/conf.py
    - tests/fixtures/paragraph_propagated_target_render_gate/conf.py
    - tests/fixtures/rubric_indent_invariance_gate/conf.py
    - tests/fixtures/signature_break_and_arrow_gate/conf.py
    - tests/fixtures/substitution_definition_render_gate/conf.py
    - tests/fixtures/wide_table_render_gate/conf.py

key-decisions:
  - "entry_title_author_render_gate's D-04 second entry was ordered (second-handbook.typ first in typst_documents, master.typ second) specifically so the wrapper surviving _wrapper_output_relpath()'s known docname-first-match write collision (deferred to plan 47-09's unified validator) keeps this fixture's ORIGINAL title/author VALUES ('My Handbook'/'Jane Doe') byte-for-byte -- only the on-disk path moved. This was measured empirically (a probe build), not assumed."
  - "admonition_greyscale_probe's wrapper target is 'admonition-greyscale-probe.typ', not the canonical 'master.typ' -- scripts/render_admonition_greyscale.py (out of this plan's files_modified scope) locates 'the master document' via an alphabetically-first *.typ glob excluding _template.typ, which must sort before the content file's own index.typ."
  - "desc_rubric_decoupling_render_gate/golden.typ was regenerated from a real build of the de-collided fixture: diffed against the pre-migration golden and confirmed the BODY is byte-identical (R1 unaffected), only the preamble differs (D-06 comment wording, template application moved to the wrapper) -- this is the same D-07 golden-capture convention Phase 36 established, not a re-derivation of translator behavior."
  - "test_rubric_indent_invariance.py's and test_signature_break_and_arrow_gate.py's manual typst.compile() calls (R3) were repointed from the docname-derived content file to the wrapper file -- the pre-migration code compiled index.typ directly, which carries no template application and is not the complete, self-contained document R3 requires the compile target to be."

patterns-established:
  - "Fixture de-collision comment convention: every retargeted conf.py names the Phase 47 rule that required the change, the original colliding value, and (for a purpose-specific name) the concrete out-of-scope consumer that constrains the choice."

requirements-completed: [COMP-01, COMP-02, BLD-03]

coverage:
  - id: D1
    description: "17 group-C test modules (integration, entry-metadata, typography, and remaining render gates) pass together against the post-split content/wrapper emitter in one pytest invocation"
    requirement: "COMP-01"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_desc_rubric_decoupling_render_gate.py tests/test_glob_image_render_gate.py tests/test_integration_advanced.py tests/test_integration_basic.py tests/test_paragraph_propagated_target_render_gate.py tests/test_substitution_definition_render_gate.py tests/test_admonition_greyscale_pipeline.py tests/test_deflist_definition_multiblock_render_gate.py tests/test_document_metadata_render_gate.py tests/test_label_at_char_render_gate.py tests/test_rubric_indent_invariance.py tests/test_wide_table_render_gate.py tests/test_citation_render_gate.py tests/test_desc_bodyless_concat_render_gate.py tests/test_external_link_style_render_gate.py tests/test_nested_table_render_gate.py tests/test_signature_break_and_arrow_gate.py -q (82 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every group-C fixture's typst_documents target is de-collided from its own docname's content path (no self-collision) and from any sibling target"
    requirement: "COMP-02"
    verification:
      - kind: other
        ref: "manual review of all 18 fixtures' conf.py after migration, plus real-build measurement confirming no cyclic-import TypstError on any group-C fixture"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-08's positional per-entry title/author read is proven end to end by a repeated-docname (D-04) fixture whose surviving wrapper carries the correctly-selected entry's own title, not a docname first-match result"
    requirement: "BLD-03"
    verification:
      - kind: integration
        ref: "tests/test_document_metadata_render_gate.py::TestEntryTitleAuthorRenderGate::test_repeated_docname_wrapper_reads_its_own_entry_title_not_first_match"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 06: Group-C Corpus Migration (Integration, Entry-Metadata, Typography, Remaining Render Gates) Summary

**Migrated 17 test modules and 18 fixture projects (group C) to the two-layer content/wrapper output shape, de-colliding every self-colliding `typst_documents` target and proving D-08's positional per-entry title/author read end to end via a new D-04 repeated-docname fixture.**

## Performance

- **Duration:** ~30 min
- **Tasks:** 3
- **Files modified:** 35 (17 test modules, 18 fixture `conf.py`/`golden.typ` files)

## Accomplishments

- De-collided 18 group-C fixtures whose `typst_documents` target self-collided with their own docname's content path (`("index", "index"/"index.typ", ...)`) under the new content/wrapper split -- the exact `TypstError: cyclic import` failure mode this wave's parallel executors were assigned to close. 16 fixtures use the canonical `"master.typ"` replacement; `admonition_greyscale_probe` uses a purpose-specific `"admonition-greyscale-probe.typ"` name (documented reason: `scripts/render_admonition_greyscale.py`, out of this plan's scope, locates "the master document" via an alphabetically-first `*.typ` glob that must sort before `index.typ`).
- Repointed every PDF assertion (R4: TypstPDFBuilder compiles only wrapper files) from `index.pdf` to each fixture's own wrapper `.pdf`, across all 17 modules.
- Left every content-file assertion (R1: translator body markup) and toctree-include assertion (R5) unchanged -- these still read `index.typ`/`second.typ`, since content files stay docname-derived regardless of any wrapper's target.
- Found and fixed two R3 violations the plan's own action text flagged for inspection: `test_rubric_indent_invariance.py` and `test_signature_break_and_arrow_gate.py` each had a manual `typst.compile()` call targeting the docname-derived content file directly (no template application) instead of the wrapper -- both repointed to the wrapper `.typ`/`.pdf`.
- Regenerated `desc_rubric_decoupling_render_gate/golden.typ` from a real build of the de-collided fixture; diffed against the pre-migration golden and confirmed the translated BODY is byte-identical (R1), only the preamble differs (D-06 wording, template application moved to the wrapper).
- Added the one new assertion the plan's own `must_haves.truths` requires: `entry_title_author_render_gate` now carries a D-04 second entry (same docname, different target, different title), and a new test (`test_repeated_docname_wrapper_reads_its_own_entry_title_not_first_match`) proves the surviving wrapper reads its title positionally off its own entry (D-08), not via a docname first-match lookup -- while explicitly measuring and documenting the known, `47-02-SUMMARY.md`-acknowledged wrapper-path routing gap (`_wrapper_output_relpath()` still resolves via docname first-match, deferred to plan 47-09's unified validator) so it reads as a documented limitation, not a defect this plan introduced or silently worked around.
- Added first-principles-derived two-layer file-set assertions (with a docstring stating the `conf.py` + `.rst` derivation) to `test_integration_basic.py` and `test_integration_advanced.py`, per task 1's acceptance criteria -- never obtained by listing a build output directory.
- All 17 group-C modules (82 tests) pass together in one `uv run pytest` invocation. `git diff --stat typsphinx/` is empty throughout -- no production code was touched.

## Task Commits

1. **Task 1: Migrate the end-to-end integration and image cluster (6 modules, 6 fixtures)** - `b3ac4b1` (test)
2. **Task 2: Migrate the entry-metadata and typography cluster (6 modules, 7 fixtures)** - `ba53752` (test)
3. **Task 3: Migrate the remaining group-C render gates (5 modules, 5 fixtures)** - `d80dbbc` (test)

## Files Created/Modified

- `tests/test_integration_basic.py` / `tests/test_integration_advanced.py` - de-collided `integration_basic`/`integration_math_figures` targets, repointed PDF paths, added derived two-layer file-set assertions
- `tests/test_desc_rubric_decoupling_render_gate.py` + `.../golden.typ` - de-collided target, repointed PDF path, regenerated golden from a real build (body byte-identical, preamble only differs)
- `tests/test_glob_image_render_gate.py`, `tests/test_paragraph_propagated_target_render_gate.py`, `tests/test_substitution_definition_render_gate.py` - de-collided targets, repointed PDF paths, image-path expectations untouched
- `tests/test_document_metadata_render_gate.py` - de-collided `entry_empty_metadata_render_gate`, extended `entry_title_author_render_gate` with a D-04 second entry, added the D-08 repeated-docname proof test, repointed the `.typ`-level companion assertion to the wrapper (R2: template application moved off content)
- `tests/test_admonition_greyscale_pipeline.py` - fixture retargeted to a purpose-specific alphabetically-sorting wrapper name (script consumer out of scope); test itself needed no change
- `tests/test_deflist_definition_multiblock_render_gate.py`, `tests/test_label_at_char_render_gate.py`, `tests/test_wide_table_render_gate.py` - de-collided targets, repointed PDF paths
- `tests/test_rubric_indent_invariance.py` - de-collided target; fixed an R3 violation (manual `typst.compile()` now targets the wrapper, not the content file)
- `tests/test_citation_render_gate.py` - de-collided the multi-docname fixture's master entry (`second`, the toctree-included docname, keeps its unconditional content file unaffected); repointed 4 PDF-path assertions
- `tests/test_desc_bodyless_concat_render_gate.py`, `tests/test_external_link_style_render_gate.py`, `tests/test_nested_table_render_gate.py` - de-collided targets, repointed PDF paths
- `tests/test_signature_break_and_arrow_gate.py` - de-collided target; fixed an R3 violation (manual `typst.compile()` now targets the wrapper), kept the U+200B-stripping step and every expected string unchanged

## Decisions Made

- `entry_title_author_render_gate`'s D-04 second entry is ordered so the SURVIVING physical wrapper (the one that wins the known write collision) keeps the fixture's ORIGINAL title/author VALUES byte-for-byte -- verified empirically with a probe build before committing to this ordering, per this plan's own "traceable to conf.py, never to emitter output" instruction being read as "verify against a real build before writing the derivation down," not "never run a build."
- `admonition_greyscale_probe` uses a purpose-specific target name (not the canonical `master.typ`) because its consuming script picks the alphabetically-first `.typ` file -- documented in the fixture's own `conf.py` comment per the migration rule's own exception clause.
- Two manual `typst.compile()` call sites (R3) were corrected to target the wrapper rather than the content file -- a genuine bug the migration surfaced (compiling a template-less content file is not "targeting a complete, self-contained document"), not a cosmetic path rename.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_rubric_indent_invariance.py`'s manual `typst.compile()` call targeted the content file, not the wrapper**
- **Found during:** Task 2
- **Issue:** `rubric_indent_invariance_pdf_bytes` built with `-b typst` then called `typst.compile(str(index_typ), ...)` directly on the docname-derived content file, which carries no template application under the post-split model. Per R3, a `typst.compile()` call targeting a complete, self-contained document must target the wrapper.
- **Fix:** Repointed to `master.typ` (the fixture's own wrapper, after de-collision).
- **Files modified:** `tests/test_rubric_indent_invariance.py`
- **Verification:** All 7 tests in the module pass, including the 6 real-compile left-edge-column assertions.
- **Committed in:** `ba53752` (Task 2 commit)

**2. [Rule 1 - Bug] `test_signature_break_and_arrow_gate.py`'s manual `typst.compile()` call targeted the content file, not the wrapper**
- **Found during:** Task 3
- **Issue:** Same class of bug as above: `_extract_pdf_text()` was called with `typ_path = temp_build_dir / "index.typ"` at three call sites, compiling the template-less content file.
- **Fix:** Repointed `_extract_pdf_text()`'s internal PDF path and all three call sites to `master.typ`/`master.pdf`. Kept the U+200B-stripping step and every expected string exactly as they were, per the plan's explicit instruction.
- **Files modified:** `tests/test_signature_break_and_arrow_gate.py`
- **Verification:** All 12 tests in the module pass; `git diff` shows no hunk removing the U+200B stripping step and no expected-string change.
- **Committed in:** `d80dbbc` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 -- R3 compile-target bugs the migration surfaced, not scope creep). Both were necessary for this plan's own designated verification to measure real behavior rather than a template-less fragment's accidental compile success.

## Known Deferred Failures (explicitly acknowledged by this plan, not fixed here)

- `_wrapper_output_relpath()`'s docname-first-match write-path routing (`typsphinx/builder.py`, unchanged by this plan) means `entry_title_author_render_gate`'s two `typst_documents` entries (D-04, same docname) both physically write to the FIRST entry's resolved target -- the second entry's write overwrites the first at that shared path, and the second entry's own declared target (`master.typ`) is never actually used as a physical filename. This is the exact, plan-acknowledged limitation `47-02-SUMMARY.md` names as deferred to plan 47-09's unified validator (D-02/D-03). `test_repeated_docname_wrapper_reads_its_own_entry_title_not_first_match` measures this directly (asserts `master.typ` does NOT exist) so the gap is documented as a passing, explicit assertion rather than a silent surprise for 47-09 to discover.

## Issues Encountered

None beyond the two auto-fixed R3 deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Group C (17 modules, 18 fixtures) is fully migrated and green against the post-split emitter. `git diff --stat typsphinx/` is empty -- no production code was touched, matching this plan's scope.
- Plan 47-09 (the phase's full-suite-green gate) is expected to land the unified pre-write collision validator that fixes `_wrapper_output_relpath()`'s docname-first-match limitation this plan's new D-08 test explicitly measures and documents. When that lands, `test_repeated_docname_wrapper_reads_its_own_entry_title_not_first_match`'s `master.typ` non-existence assertion will need to flip to existence -- this SUMMARY and the fixture's own `conf.py` comment both point to the exact test and reasoning.
- No blockers for sibling group plans (47-03, 47-04, 47-05, 47-07, 47-08) or for plan 47-09 -- this plan touched only its own declared `files_modified` scope (tests/ and tests/fixtures/), never a shared orchestrator artifact.

## Self-Check: PASSED

All modified files verified present on disk (via the task-scoped `git status`/`git diff` output above). All three task commits (`b3ac4b1`, `ba53752`, `d80dbbc`) verified present in `git log --oneline`.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*
