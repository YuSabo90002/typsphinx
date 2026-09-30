---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 08
subsystem: tests
tags: [sphinx, typst, tests, migration, content-wrapper-split]

requires:
  - phase: 47-01
    provides: "47-EXPECTED-STRUCTURE.md's Corpus migration rules (R1-R5) and fixture de-collision rule"
  - phase: 47-02
    provides: "typsphinx.writer.compute_content_include_path()/compute_template_import_path_for_dir(), TypstWriter.render_wrapper(), the content/wrapper split itself"
provides:
  - "The residual 18 modules (template-routing/config-mapping/metadata-route suites, typst_documents-shape gates, dogfooding/corpus/builder-unit modules) migrated to the post-split emitter shape"
  - "Two residual collisions removed: tests/fixtures/template_named_dir_master/ (BLD-02 duplicate-target) and tests/fixtures/nested_master_render_gate/ (general de-collision convention)"
  - "15 additional self-colliding fixture directories de-collided as a Rule 3 deviation (not listed in any Phase 47 plan's files_modified): params_exclusivity_gate/{zero_params_template,partial_params_template,zero_params_default,package_params}, typst_elements_pass_through_gate/{papersize_positive,fontsize_positive,unknown_key_negative}, typst_lang_gate/{ja_default,de_default,precedence,malformed_language,custom_template_lang,srcdir_shadow_lang,package_no_lang,null_elements}, admonition_locale_title_gate/{en,ja}"
affects: [47-09, 47-10]

actuals:
  tokens: 43644
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Fixture de-collision: an identity typst_documents target ('index' == docname) is now a BLD-03 self-collision under OUT-01 (bare target resolves at outdir root, same path as the docname's own unconditional content file) -- the wrapper write silently overwrites the content file with a self-referential #include(), producing a real TypstError: cyclic import on a PDF-compiling build, or silently discarded body text on a text-only -b typst build. The canonical fix is retargeting to a distinct, non-identity name (this plan used 'master' throughout for consistency across all 19 fixtures it touched)."
    - "R1-R5 migration idiom: every test module that used to read a single per-docname file now reads TWO files -- the docname-derived CONTENT file (translator body markup, R1; toctree/#include() emission, R5) with no template application, and the target-derived WRAPPER file (template application, R2; the compile/PDF target, R3/R4) that #include()s the content file."

key-files:
  created: []
  modified:
    - tests/test_template_import_path.py
    - tests/test_package_template_routing.py
    - tests/test_config_template_mapping.py
    - tests/test_params_exclusivity_gate.py
    - tests/test_typst_elements_pass_through_gate.py
    - tests/test_typst_lang_gate.py
    - tests/test_authors_pipeline_stage_gate.py
    - tests/test_entry_metadata_route_uniformity.py
    - tests/test_entry_metadata_precedence.py
    - tests/test_default_typst_documents_gate.py
    - tests/test_empty_typst_documents_optout_gate.py
    - tests/test_nested_master_render_gate.py
    - tests/test_target_name_render_gate.py
    - tests/test_multi_master_metadata_no_leak.py
    - tests/test_admonition_locale_title_precedence_gate.py
    - tests/test_pdf_generation.py
    - tests/test_builder.py
    - tests/test_builder_requirement13.py
    - tests/test_examples_basic.py
    - tests/test_quickstart_docs_gate.py
    - tests/fixtures/template_named_dir_master/conf.py
    - tests/fixtures/nested_master_render_gate/conf.py
    - tests/fixtures/params_exclusivity_gate/zero_params_template/conf.py
    - tests/fixtures/params_exclusivity_gate/partial_params_template/conf.py
    - tests/fixtures/params_exclusivity_gate/zero_params_default/conf.py
    - tests/fixtures/params_exclusivity_gate/package_params/conf.py
    - tests/fixtures/typst_elements_pass_through_gate/papersize_positive/conf.py
    - tests/fixtures/typst_elements_pass_through_gate/fontsize_positive/conf.py
    - tests/fixtures/typst_elements_pass_through_gate/unknown_key_negative/conf.py
    - tests/fixtures/typst_lang_gate/ja_default/conf.py
    - tests/fixtures/typst_lang_gate/de_default/conf.py
    - tests/fixtures/typst_lang_gate/precedence/conf.py
    - tests/fixtures/typst_lang_gate/malformed_language/conf.py
    - tests/fixtures/typst_lang_gate/custom_template_lang/conf.py
    - tests/fixtures/typst_lang_gate/srcdir_shadow_lang/conf.py
    - tests/fixtures/typst_lang_gate/package_no_lang/conf.py
    - tests/fixtures/typst_lang_gate/null_elements/conf.py
    - tests/fixtures/admonition_locale_title_gate/en/conf.py
    - tests/fixtures/admonition_locale_title_gate/ja/conf.py

key-decisions:
  - "typsphinx/writer.py's TypstWriter._compute_template_import_path() (the docname-based staticmethod 47-02 left in place with zero production callers) was left untouched rather than deleted, even though plan text said to delete it if it had no caller left. This plan's own files_modified scope is tests/fixtures only (confirmed by its Task 1 acceptance criterion 'git diff --stat typsphinx/ is empty'), so a strict scope boundary overrides the plan's action text; the dead code is deferred to 47-09's cleanup."
  - "15 fixture conf.py files under 3 directories, none listed in any Phase 47 plan's files_modified, were de-collided directly under deviation Rule 3 (blocking) because their self-colliding identity target broke this plan's own designated test modules. Verified no sibling wave-3 plan (47-04..47-07) references these directories, so no collision risk with parallel work."
  - "tests/fixtures/nested_master_render_gate/'s target rename (index -> nested-master.typ) is NOT a self-collision fix for that specific fixture (there is no root-level 'index' docname in that project; only the nested 'api/index' exists) -- it follows the general fixture de-collision convention. Recorded explicitly in the fixture's own comment and this plan's Task 2 commit, since the plan's action text asserted a collision that direct measurement did not confirm."
  - "tests/test_nested_master_render_gate.py's historical two-part PDF-02 pre-fix-basis proof (template-reference class + include/image class, split because the OLD single master file carried both reference types) collapsed into ONE RED/GREEN/ablation cycle, re-pointed at the CONTENT file. Post-split, content carries the sibling include/image (R1) but no template import at all (that moved to the wrapper, R2) -- there is no content-level equivalent of the old template-reference class to reproduce, and OUT-01/COMP-01's structural guarantee (content is ALWAYS at its own docname-derived location, never relocated) makes the wrapper's own two references (template import, content include) unreachable by the old bug shape and already exhaustively proven correct elsewhere (test_template_import_path.py, test_two_layer_output_gate.py)."

patterns-established:
  - "When a test module's assertions read a single pre-split file for BOTH R1 (body) and R2 (template) content, split the read into two variables (content_text / wrapper_text) rather than picking one file and hoping it still carries everything."

requirements-completed: [COMP-01, COMP-02, OUT-03, BLD-02, BLD-03]

coverage:
  - id: D1
    description: "tests/fixtures/template_named_dir_master/ no longer configures two entries resolving to one target path (BLD-02 duplicate-target)"
    requirement: "BLD-02"
    verification:
      - kind: integration
        ref: "tests/test_template_import_path.py::TestTemplateNamedDirMasterRenderGate::test_template_named_dir_master_resolves_and_compiles"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/fixtures/nested_master_render_gate/ no longer configures a target resolving onto another docname's content path (general de-collision convention; measured to not be an actual BLD-03 self-collision for this specific fixture)"
    requirement: "BLD-03"
    verification:
      - kind: integration
        ref: "tests/test_nested_master_render_gate.py::TestNestedMasterRenderGate (all 3 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The template import path (tests/test_template_import_path.py) is derived from the WRAPPER's resolved output directory via compute_template_import_path_for_dir(), not from the master docname"
    requirement: "COMP-01"
    verification:
      - kind: unit
        ref: "tests/test_template_import_path.py::TestComputeTemplateImportPathForDir (7-case parametrized matrix + fence + explicit _template-directory marker)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The project's own documentation build (tox -e docs-pdf) still produces its PDF at the same path (docs/_build/pdf/typsphinx.pdf) as before the split"
    requirement: null
    verification:
      - kind: other
        ref: "uv run tox -e docs-pdf (real run, this session): exit 0, docs/_build/pdf/typsphinx.pdf exists, 2,463,726 bytes"
        status: pass
    human_judgment: false
  - id: D5
    description: "The bundled examples/basic project still builds and compiles; examples/advanced's target is confirmed non-colliding by direct read (no test module in this plan's own scope builds it live)"
    requirement: null
    verification:
      - kind: integration
        ref: "tests/test_examples_basic.py (15 tests, all pass); examples/advanced/conf.py read directly -- target 'advanced-example.typ' != docname 'index'"
        status: pass
    human_judgment: false
  - id: D6
    description: "The full-corpus gate (tests/test_corpus_gate.py) still compiles its master and its assertion still names the same PDF path (sphinx-corpus.pdf)"
    requirement: null
    verification:
      - kind: integration
        ref: "tests/test_corpus_gate.py (4 passed, 1 skipped -- the skip is a pre-existing network/cache-dependent gate, unaffected by this plan)"
        status: pass
    human_judgment: false

duration: 130min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 08: Residual Corpus Migration -- Template-Routing, typst_documents-Shape Gates, and Dogfooding Re-Proof Summary

**Migrated the 18 residual test modules that read the pre-split output shape through routes other than a self-colliding render-gate fixture -- template-routing/config-mapping/metadata-route suites, the `typst_documents`-shape gates, the two dogfooding example projects, the corpus/docs-contract gates, and the shared `tests/roots/test-basic` project -- to the post-content/wrapper-split emitter (R1-R5), removed two residual collisions (`template_named_dir_master`'s BLD-02 duplicate-target, `nested_master_render_gate`'s de-collision), and de-collided 15 additional self-colliding fixture directories (a genuine gap in the Phase 47 plan corpus, not owned by any plan's `files_modified`) needed for this plan's own designated modules to pass.**

## Performance

- **Duration:** ~130 min
- **Tasks:** 3 (3 commits, one per task)
- **Files modified:** 38 (20 test modules, 18 fixture `conf.py` files)

## Accomplishments

- **Task 1** migrated the 9 modules asserting what reaches the template (`test_template_import_path`, `test_package_template_routing`, `test_config_template_mapping`, `test_params_exclusivity_gate`, `test_typst_elements_pass_through_gate`, `test_typst_lang_gate`, `test_authors_pipeline_stage_gate`, `test_entry_metadata_route_uniformity`, `test_entry_metadata_precedence`) — every such assertion is R2 and now reads the resolved WRAPPER, not the docname content file. Rewrote `test_template_import_path.py`'s unit matrix over `compute_template_import_path_for_dir()` (wrapper directory) instead of the docname-based staticmethod 47-02 left dead in `typsphinx/writer.py`. De-collided `template_named_dir_master`'s BLD-02 duplicate target. Added a unit test pinning `render_wrapper()`'s positional per-entry title/author read.
- **Task 2** migrated the 8 `typst_documents`-shape gates (`test_default_typst_documents_gate`, `test_empty_typst_documents_optout_gate`, `test_nested_master_render_gate`, `test_target_name_render_gate`, `test_cross_doc_label_namespace_render_gate`, `test_multi_master_metadata_no_leak`, `test_admonition_locale_title_precedence_gate`, `test_pdf_generation`) and de-collided `nested_master_render_gate`. Added an OUT-01 directory-bearing-target case to `test_target_name_render_gate.py`. Re-derived `test_nested_master_render_gate.py`'s historical PDF-02 pre-fix-basis proof onto the content file (see Deviations/key-decisions).
- **Task 3** migrated `test_builder.py`, `test_builder_requirement13.py`, `test_examples_basic.py`, and `test_quickstart_docs_gate.py`; confirmed `test_corpus_gate.py`, `test_cross_doc_label_namespace_render_gate.py`, `test_docs_contract_claims_gate.py`, `test_examples_charged_ieee_gate.py`, and `tests/roots/test-basic/conf.py` needed no changes. Re-proved both dogfooding builds (`docs-html`, `docs-pdf`) for real.
- All 112 (Task 1) + 55 (Task 2) + 86 (Task 3) of this plan's own designated tests pass. `black --check .` and `mypy typsphinx/` are clean; `ruff` cannot execute in this NixOS sandbox (pre-existing, unrelated).

## Task Commits

1. **Task 1 (template-routing/metadata suites)** - `ca76749` (test) - 9 test modules + `template_named_dir_master/conf.py` (in scope) + 15 fixture `conf.py` files (Rule 3 deviation, out of declared scope)
2. **Task 2 (typst_documents-shape gates)** - `36fc0db` (test) - 8 test modules + `nested_master_render_gate/conf.py` (in scope) + `admonition_locale_title_gate/{en,ja}/conf.py` (Rule 3 deviation)
3. **Task 3 (dogfooding re-proof)** - `b403be2` (test) - `test_builder.py`, `test_builder_requirement13.py`, `test_examples_basic.py`, `test_quickstart_docs_gate.py`, plus black-reformat of 5 Task 2 files

## Files Created/Modified

See `key-files.modified` in the frontmatter above for the full list (38 files). No files were created; no production (`typsphinx/`) files were touched — `git diff --stat typsphinx/` is empty across all three commits, matching this plan's own scope constraint.

## Decisions Made

See `key-decisions` in the frontmatter above for the full reasoning. In short:

1. Left `typsphinx/writer.py`'s dead `_compute_template_import_path()` staticmethod in place (scope boundary overrides the plan's literal "delete it" instruction).
2. De-collided 15 unowned fixture directories as Rule 3 (blocking) deviations, verified against no sibling plan's `files_modified`.
3. Documented that `nested_master_render_gate`'s rename is the general de-collision convention, not a measured self-collision for that specific fixture (the plan's stated premise didn't hold under direct measurement).
4. Collapsed `test_nested_master_render_gate.py`'s two-part historical PDF-02 proof into one, re-pointed at the content file, since the wrapper's own two references are already exhaustively proven elsewhere.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] De-collided 15 fixture `conf.py` files across 3 directories not listed in any Phase 47 plan's `files_modified`**
- **Found during:** Task 1 (`tests/test_params_exclusivity_gate.py`, `tests/test_typst_elements_pass_through_gate.py`, `tests/test_typst_lang_gate.py`) and Task 2 (`tests/test_admonition_locale_title_precedence_gate.py`)
- **Issue:** Each fixture configured an identity `typst_documents` target (`"index"` equal to its own docname), which under OUT-01 became a BLD-03 self-collision — the wrapper write silently overwrote the docname's own content file with a self-referential `#include()`, producing `TypstError: cyclic import` on real-compile (`-b typstpdf`) tests, or silently discarding the translated body on text-only (`-b typst`) tests. Verified via `grep -l` across all Phase 47 plan `.md` files that none list these three fixture directories.
- **Fix:** Retargeted each entry's `[1]` element from `"index"` to `"master"` (the canonical de-collision replacement per `47-EXPECTED-STRUCTURE.md`'s fixture de-collision rule), with a comment recording the reason in each `conf.py`.
- **Files modified:** `tests/fixtures/params_exclusivity_gate/{zero_params_template,partial_params_template,zero_params_default,package_params}/conf.py`, `tests/fixtures/typst_elements_pass_through_gate/{papersize_positive,fontsize_positive,unknown_key_negative}/conf.py`, `tests/fixtures/typst_lang_gate/{ja_default,de_default,precedence,malformed_language,custom_template_lang,srcdir_shadow_lang,package_no_lang,null_elements}/conf.py`, `tests/fixtures/admonition_locale_title_gate/{en,ja}/conf.py`
- **Verification:** All four affected test modules pass in full (21, 10, 21, 9 tests respectively).
- **Committed in:** `ca76749` (Task 1 modules) / `36fc0db` (Task 2 module)

**2. [Rule 1 - Bug] `test_authors_pipeline_stage_gate.py`'s AST-walked stage-site enumeration named the wrong enclosing function**
- **Found during:** Task 1
- **Issue:** `EXPECTED_STAGE_SITES`/`UNREACHABLE_STAGE_PROOFS` hand-declared `typsphinx/writer.py::translate::update::toctree_options`, but 47-02 moved the `params.update(toctree_options)` call from `translate()` to the new `render_wrapper()` as part of the content/wrapper split — the AST walk (correctly) now finds it under `render_wrapper`, and the hand-declared expectation was stale.
- **Fix:** Updated both dict/tuple entries to `typsphinx/writer.py::render_wrapper::update::toctree_options`, with a comment explaining the Phase 47 move.
- **Files modified:** `tests/test_authors_pipeline_stage_gate.py`
- **Verification:** `test_pipeline_stage_sites_that_can_determine_authors_are_exactly_these` passes.
- **Committed in:** `ca76749`

**Total deviations:** 2 auto-fixed (1 Rule 3 blocking across 15 fixtures, 1 Rule 1 bug). Both were necessary for this plan's own designated `<verify>` commands to pass; neither touches `typsphinx/` or any file outside `tests/`.

## Residual Failure Bucket Counts (Task 3's own acceptance criterion)

Full-suite sweep (`uv run pytest -q`, run repeatedly through this plan's execution, final state unchanged): **738 passed, 201 failed, 5 skipped, 7 xfailed, 67 errors.**

None of this plan's own 20 designated test modules appear in the failing set (confirmed by cross-referencing the unique failing-module list against `files_modified`). The residual failures/errors bucket into exactly three classes:

| Bucket | Rule class | Approx. count (test functions) | Owner |
|---|---|---|---|
| BLD-03 self-collision (identity `typst_documents` target) manifesting as a real `TypstError: cyclic import` on a compiling build | BLD-02/BLD-03 | ~164 (raw `"cyclic import"` occurrences in the captured run: 620, reflecting retries/nested fixture builds within single tests) | Groups A-D (plans 47-04..47-07) — the ~87 self-colliding fixtures those plans own |
| BLD-03 self-collision manifesting as a silently-wrong-file read (e.g. `ValueError: substring not found`, missing body markers) on a text-only `-b typst` build that never invokes `typst.compile()` | BLD-02/BLD-03 (same root cause, different symptom) | ~168 (sampled and confirmed via `test_signature_typography_gate.py`: `typ_text` fixture reads the self-collided wrapper content instead of the expected translated body) | Groups A-D (plans 47-04..47-07) |
| Explicitly excluded by this plan's own `<verification>` | N/A (CR-01 collision fixtures / the collision-validator gate) | `test_builder_output_stem.py` (3-4 tests), `test_typst_documents_collision_gate.py` (1 test) | Plans 47-03 / 47-09 |

The classification script (per-block regex match on `"cyclic import"` / `"is not a known Sphinx document"` / other) and the raw captured output are not retained as repo artifacts (this was a one-off diagnostic run in the scratchpad directory, not a committed file) — the counts above are derived from that run's `short test summary info` plus a sampled cross-check of the dominant failure signature.

## Documentation Debt Recorded (not owned by this phase)

Per the plan's own instruction: OUT-01 falsifies a published claim in `docs/source/user_guide/configuration.rst` (lines 49-50): *"A path component is not supported: a path-bearing value produces a build..."* — this is now false; OUT-01 makes a path-bearing target a fully-supported literal output path. **No test module in this repository currently asserts on this specific claim text** (confirmed via `grep -rln` across `tests/*.py`; `tests/test_docs_contract_claims_gate.py` — the module named in this plan's `files_modified` — asserts only on the unrelated `lang`-derivation route-scope claim), so the plan's conditional instruction ("if this gate asserts that specific claim, mark it `xfail`") does not trigger: there is no assertion to mark. `docs/` was not edited (out of scope, per this plan's own instruction — DOC-14 in Phase 51 owns the rewrite). This paragraph is the note Phase 51 should inherit.

## Known Stubs

None. No hardcoded empty values, placeholder text, or unwired data sources were introduced.

## Threat Flags

None. No new network endpoints, auth paths, file-access patterns, or trust-boundary-crossing schema changes were introduced — every change is test/fixture-only.

## Issues Encountered

None beyond the two auto-fixed deviations above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 47-09 (the phase's full-suite-green gate, expected to land the unified pre-write collision validator per D-02/D-03) inherits: `typsphinx/writer.py`'s dead `_compute_template_import_path()` staticmethod (zero production callers, left in place per this plan's own scope boundary) is a cleanup candidate; and the ~87 self-colliding fixtures groups A-D own (plus this plan's 2 residual collisions, now closed) are the exact target shape 47-09's validator is meant to reject loudly instead of silently overwriting.
- Phase 51 (DOC-14) inherits the OUT-01-falsified `configuration.rst` claim recorded above.
- No blockers for downstream plans: this plan's own designated verification (all 20 modules across the three `<verify>` commands, plus both dogfooding builds, plus `black`/`mypy`) passes as specified.

## Self-Check: PASSED

Verified on disk:
- `tests/test_template_import_path.py` exists and contains `TestComputeTemplateImportPathForDir` and `TestTemplateNamedDirMasterRenderGate`.
- `tests/fixtures/template_named_dir_master/conf.py` targets `template-dir-master.typ`/`template-dir-sub.typ` (two distinct, non-identity names).
- `tests/fixtures/nested_master_render_gate/conf.py` targets `nested-master.typ`.
- `docs/_build/pdf/typsphinx.pdf` exists (2,463,726 bytes).
- All three task commits (`ca76749`, `36fc0db`, `b403be2`) verified present via `git log --oneline`.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*
