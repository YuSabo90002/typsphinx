---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 04
subsystem: testing
tags: [sphinx, typst, typst-py, pytest, corpus-migration, two-layer-output]

requires:
  - phase: 47-01
    provides: "47-EXPECTED-STRUCTURE.md's Corpus migration rules (R1-R5 table + the fixture de-collision rule) -- the binding authority this plan follows verbatim"
  - phase: 47-02
    provides: "typsphinx.writer's content/wrapper split (TypstWriter.translate()/render_wrapper()) and typsphinx.builder's _write_typst_files() -- the post-split emitter this plan's fixtures and modules now build against"
provides:
  - "Group A of the corpus migration (34 fixtures, 17 test modules) fully de-collided and migrated to the two-layer output shape -- one quarter of the phase's largest single cost"
  - "The de-collision idiom (bare 'index' target -> 'master.typ', with a comment naming 47-EXPECTED-STRUCTURE.md's rule) siblings 47-05..47-08 can follow verbatim"
  - "The R1-R5 migration idiom applied at module scale: index.typ (content, R1/R5) stays; index.pdf/typst.compile(index_typ) (R3/R4) repoint to master.typ/master.pdf"
affects: [47-05, 47-06, 47-07, 47-08, 47-09]

actuals:
  tokens: 20727
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Fixture de-collision: every group-A conf.py's self-colliding bare 'index' typst_documents target renamed to 'master.typ', with a comment citing 47-EXPECTED-STRUCTURE.md's rule -- element [0]/[2]/[3] never touched"
    - "R1-R5 test-module migration: a read_text()+body-markup assertion stays on the docname-derived content file (index.typ, unchanged path); a typst.compile()/PDF-path assertion repoints to the wrapper (master.typ/master.pdf)"
    - "Deliberately-malformed typst_documents entries (a nonexistent docname, an empty tuple) are exempt from de-collision -- they can never produce a physically-colliding content file, so renaming them would defeat the fixture's own purpose"

key-files:
  created: []
  modified:
    - tests/fixtures/admonition_render_gate/conf.py
    - tests/fixtures/block_quote_markup_render_gate/conf.py
    - tests/fixtures/captioned_table_render_gate/conf.py
    - tests/fixtures/codly_config_leak_render_gate/conf.py
    - tests/fixtures/codly_offset_render_gate/conf.py
    - tests/fixtures/desc_container_propagated_target_render_gate/conf.py
    - tests/fixtures/desc_signature_render_gate/conf.py
    - tests/fixtures/field_list_in_list_item_render_gate/conf.py
    - tests/fixtures/figure_length_render_gate/conf.py
    - tests/fixtures/figure_target_caption_render_gate/conf.py
    - tests/fixtures/footnote_render_gate/conf.py
    - tests/fixtures/graphviz_degrade_render_gate/conf.py
    - tests/fixtures/manpage_render_gate/conf.py
    - tests/fixtures/package_only_config_gate/conf.py
    - tests/fixtures/signature_page_boundary_render_gate/conf.py
    - tests/fixtures/table_width_render_gate/conf.py
    - tests/fixtures/todo_render_gate/conf.py
    - tests/fixtures/topic_line_block_render_gate/conf.py
    - tests/fixtures/trivial_blocks_render_gate/conf.py
    - tests/fixtures/version_modified_render_gate/conf.py
    - tests/fixtures/xref_refid_render_gate/conf.py
    - tests/fixtures/abbr_pep_separator_render_gate/conf.py
    - tests/fixtures/confval_field_body_render_gate/conf.py
    - tests/fixtures/desc_signature_anchor_render_gate/conf.py
    - tests/fixtures/inline_math_after_text_render_gate/conf.py
    - tests/fixtures/preview_smoke/conf.py
    - tests/fixtures/table_in_list_item_render_gate/conf.py
    - tests/fixtures/changelog_include_gate/conf.py
    - tests/fixtures/deflist_term_concat_render_gate/conf.py
    - tests/fixtures/deflist_term_in_listitem_render_gate/conf.py
    - tests/fixtures/deflist_term_nested_list_render_gate/conf.py
    - tests/fixtures/duplicate_include_label_render_gate/conf.py
    - tests/fixtures/missing_and_malformed_master_gate/conf.py
    - tests/fixtures/rubric_propagated_target_render_gate/conf.py
    - tests/test_pdf_render_gate.py
    - tests/test_desc_container_propagated_target_render_gate.py
    - tests/test_field_list_in_list_item_render_gate.py
    - tests/test_package_only_config_gate.py
    - tests/test_signature_page_boundary_render_gate.py
    - tests/test_abbr_pep_separator_render_gate.py
    - tests/test_confval_field_body_render_gate.py
    - tests/test_desc_signature_anchor_render_gate.py
    - tests/test_inline_math_after_text_render_gate.py
    - tests/test_preview_smoke_gate.py
    - tests/test_table_in_list_item_render_gate.py
    - tests/test_changelog_page_gate.py
    - tests/test_deflist_term_concat_render_gate.py
    - tests/test_duplicate_include_label_render_gate.py
    - tests/test_missing_and_malformed_master_gate.py
    - tests/test_rubric_propagated_target_render_gate.py

key-decisions:
  - "tests/test_preview_smoke_gate.py's compile target stayed on index.typ (not repointed to the wrapper), per the plan's own read_first instruction: D-06 makes the four @preview imports + codly init/config calls unconditional on the content file even for a docname that is also a typst_documents entry, so this module's core assertion class shifts R2 -> R1. Added the new D-06-derived assertion the plan explicitly called for (imports present in the content file for exactly that case) rather than inventing a different repointing."
  - "tests/fixtures/missing_and_malformed_master_gate/conf.py's ONE valid entry (docname 'index') was de-collided to 'master.typ'; its two deliberately-malformed entries ('ghost' -- a nonexistent docname -- and an empty tuple) were left untouched, because neither can ever produce a physically-colliding content file (no ghost.rst exists, and an empty tuple has no docname at all) -- de-colliding them would defeat the fixture's own purpose of exercising D-04's found-docs-discriminating branch and D-05/D-07's malformed-entry branch."
  - "The canonical de-collision replacement 'master.typ' (verbatim from 47-EXPECTED-STRUCTURE.md's rule) was used for all 34 fixtures uniformly -- none of group A's fixtures had a purpose-specific reason to pick a different name."

patterns-established:
  - "Every de-collided conf.py carries an inline comment naming 47-EXPECTED-STRUCTURE.md's fixture de-collision rule and explaining why the bare 'index' target would collide -- so a future reader does not mistake 'master.typ' for an arbitrary rename."

requirements-completed: [COMP-01, COMP-02, BLD-03]

coverage:
  - id: D1
    description: "21-fixture, 6-module multi-fixture render-gate cluster (admonition/figure/table/codly/desc_signature/xref/manpage/etc.) de-collided and migrated to the two-layer output shape"
    requirement: "COMP-01"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_pdf_render_gate.py tests/test_admonition_bucket_render_gate.py tests/test_desc_container_propagated_target_render_gate.py tests/test_field_list_in_list_item_render_gate.py tests/test_package_only_config_gate.py tests/test_signature_page_boundary_render_gate.py -q"
        status: pass
    human_judgment: false
  - id: D2
    description: "6 single-fixture render gates (abbr-pep-separator, confval-field-body, desc-signature-anchor, inline-math-after-text, preview-smoke, table-in-list-item) de-collided and migrated; both PDF-text golden files (inline_math_pdf_text_mitex/native.golden.txt) verified unchanged"
    requirement: "COMP-02"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_abbr_pep_separator_render_gate.py tests/test_confval_field_body_render_gate.py tests/test_desc_signature_anchor_render_gate.py tests/test_inline_math_after_text_render_gate.py tests/test_preview_smoke_gate.py tests/test_table_in_list_item_render_gate.py -q"
        status: pass
    human_judgment: false
  - id: D3
    description: "7-fixture, 5-module toctree/malformed-entry gate cluster de-collided and migrated, including missing_and_malformed_master_gate's D-02 attempt-all-then-raise contract against the new content+wrapper file pair; repo-wide _is_master_document grep reconfirmed zero-hit"
    requirement: "BLD-03"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_changelog_page_gate.py tests/test_deflist_term_concat_render_gate.py tests/test_duplicate_include_label_render_gate.py tests/test_missing_and_malformed_master_gate.py tests/test_rubric_propagated_target_render_gate.py -q"
        status: pass
      - kind: other
        ref: "grep -rn \"_is_master_document\" tests/test_missing_and_malformed_master_gate.py tests/fixtures/missing_and_malformed_master_gate/ (zero hits)"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 04: Group-A Corpus Migration Summary

**De-collided all 34 group-A fixtures' self-colliding `typst_documents` target (bare `"index"` -> `"master.typ"`) and migrated all 17 group-A test modules' compile/PDF-path assertions from the pre-split one-file-per-docname shape to the two-layer content/wrapper shape, closing R2/R3/R4 (wrapper) vs. R1/R5 (docname-derived content) per 47-EXPECTED-STRUCTURE.md's binding migration rules.**

## Performance

- **Duration:** ~45 min
- **Tasks:** 3
- **Files modified:** 50 (34 fixture `conf.py`, 16 test modules touched + 1 needing no change)

## Accomplishments

- **Task 1 (21 fixtures, 6 modules):** De-collided `admonition_render_gate`, `block_quote_markup_render_gate`, `captioned_table_render_gate`, `codly_config_leak_render_gate`, `codly_offset_render_gate`, `desc_container_propagated_target_render_gate`, `desc_signature_render_gate`, `field_list_in_list_item_render_gate`, `figure_length_render_gate`, `figure_target_caption_render_gate`, `footnote_render_gate`, `graphviz_degrade_render_gate`, `manpage_render_gate`, `package_only_config_gate`, `signature_page_boundary_render_gate`, `table_width_render_gate`, `todo_render_gate`, `topic_line_block_render_gate`, `trivial_blocks_render_gate`, `version_modified_render_gate`, `xref_refid_render_gate`. Migrated `tests/test_pdf_render_gate.py`'s 19 `typst.compile(index_typ)`/`index.pdf` pairs to `master.typ`/`master.pdf` via a single regex-driven substitution (all 19 shared the identical pre-fix idiom). `tests/test_package_only_config_gate.py` needed its whole build/reconstruction/diff-matrix fixture chain redirected at the wrapper, since every one of its BUG-A..F assertions is template-application territory. `tests/test_signature_page_boundary_render_gate.py`'s page-override probe (which searches for `#import "_template.typ"` / `#show: project.with(...)`) was repointed at the wrapper, whose own `#include("index.typ")` still pulls in the content file carrying the page-boundary sentinels. `tests/test_admonition_bucket_render_gate.py` needed no changes -- every assertion is region-scoped body markup (R1) on `index.typ`.
- **Task 2 (6 fixtures, 6 modules):** De-collided `abbr_pep_separator_render_gate`, `confval_field_body_render_gate`, `desc_signature_anchor_render_gate`, `inline_math_after_text_render_gate`, `preview_smoke`, `table_in_list_item_render_gate`. Migrated the standard `index.pdf` -> `master.pdf` idiom across four modules. `test_inline_math_after_text_render_gate.py`'s golden-file invariance test was repointed without touching either golden file (confirmed via `git diff --stat` on both). `test_preview_smoke_gate.py` was migrated per its own plan-called-out exception: D-06 makes the module's core assertion an R1 (content-file) concern, so its compile target stayed on `index.typ` and a new D-06-derived assertion was added instead (the four imports present in the content file even for a docname that is also a `typst_documents` entry).
- **Task 3 (7 fixtures, 5 modules):** De-collided `changelog_include_gate`, `deflist_term_concat_render_gate`, `deflist_term_in_listitem_render_gate`, `deflist_term_nested_list_render_gate`, `duplicate_include_label_render_gate`, and the ONE valid entry in `missing_and_malformed_master_gate` (its two deliberately-malformed entries left untouched -- see Decisions). `rubric_propagated_target_render_gate` was also de-collided. Migrated the standard `index.pdf` -> `master.pdf` idiom across `test_changelog_page_gate.py`, `test_deflist_term_concat_render_gate.py` (3 classes), `test_duplicate_include_label_render_gate.py`, `test_rubric_propagated_target_render_gate.py`. `test_missing_and_malformed_master_gate.py`'s D-02 attempt-all-then-raise assertion now checks both the unchanged content file (`index.typ`, R1) and the wrapper pair (`master.typ`/`master.pdf`, R2-R4). Reconfirmed the repo-wide `_is_master_document` grep is zero-hit (already fixed by plan 47-02).
- All 17 group-A modules pass together: `uv run pytest` over the full group-A module list -- 79 passed, 4 skipped (the 4 skips are `myst_parser`-gated `test_changelog_page_gate.py` classes; `myst-parser` lives in the `docs` extra, not installed in this dev-only worktree sandbox -- pre-existing, unrelated to this plan).
- `git diff --stat typsphinx/` is empty throughout -- no production code touched.

## Task Commits

1. **Task 1: Migrate the multi-fixture render-gate cluster (6 modules, 21 fixtures)** - `a549a3d` (test)
2. **Task 2: Migrate the single-fixture render gates (6 modules, 6 fixtures)** - `3cd1b4b` (test)
3. **Task 3: Migrate the toctree and malformed-entry gates (5 modules, 7 fixtures)** - `c8e0d32` (test)

## Files Created/Modified

34 fixture `conf.py` files (target de-collision only -- `element [0]`/`[2]`/`[3]` never touched) and 16 test modules (compile/PDF-path repointing per the R1-R5 table; `test_admonition_bucket_render_gate.py` needed no edits). See frontmatter `key-files.modified` for the full list.

## Decisions Made

- `tests/test_preview_smoke_gate.py`'s compile target stayed on `index.typ` rather than being repointed to the wrapper, per the plan's own explicit read_first instruction for this module: D-06 makes the module's core proof (the four `@preview` packages actually compile when invoked) an R1 concern once every content file unconditionally carries those imports and calls. Added the new D-06-derived assertion the plan called for instead of inventing a different repointing.
- `tests/fixtures/missing_and_malformed_master_gate/conf.py`'s two deliberately-malformed `typst_documents` entries (`("ghost", "ghost", ...)` and `()`) were left untouched by the de-collision rule -- neither can ever produce a physically-colliding content file (no `ghost.rst` exists in the fixture; the empty tuple has no docname at all), so renaming either would defeat the fixture's own purpose of exercising D-04's found-docs-discriminating branch and D-05/D-07's malformed-entry branch.
- The canonical replacement `"master.typ"` (verbatim from 47-EXPECTED-STRUCTURE.md's rule) was used uniformly across all 34 fixtures -- none had a purpose-specific reason to choose a different name.

## Deviations from Plan

None - plan executed exactly as written. Every task's acceptance criteria were met without needing a Rule 1-4 deviation: no bug was found in the emitter, no missing functionality needed adding, and no blocking issue required a workaround beyond what the plan itself anticipated (the `test_preview_smoke_gate.py` R2->R1 shift and the `missing_and_malformed_master_gate` malformed-entry exemption were both explicitly called out by the plan itself, not discovered mid-execution).

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Group A (34 fixtures, 17 modules) is fully migrated and de-collided; plans 47-05 through 47-08 migrate groups B/C/D against the same R1-R5 table and fixture de-collision rule this plan established the idiom for.
- The regex-driven bulk substitution used for `test_pdf_render_gate.py`'s 19 identical `pdf_output = X / "index.pdf"` / `typst.compile(str(index_typ), output=str(pdf_output))` pairs is a reusable technique for any sibling module with the same repeated shape.
- No blockers for downstream plans: this plan's own designated verification (all 17 group-A modules, `black --check .`, the repo-wide `_is_master_document` grep, `git diff --stat typsphinx/`) all pass as specified. `ruff check .` could not run in this sandbox (pre-existing NixOS generic-linux-ELF limitation, unrelated to this plan).
- The full `uv run pytest` suite remains knowingly RED outside group A's own modules -- groups B, C, D and the residual plan still carry the pre-split self-collision failures; 47-09 is the phase's full-suite-green gate.

## Self-Check: PASSED

All 34 fixture `conf.py` files and 16 modified test modules verified present on disk. All three task commits (`a549a3d`, `3cd1b4b`, `c8e0d32`) verified present in `git log --oneline --all`.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*
