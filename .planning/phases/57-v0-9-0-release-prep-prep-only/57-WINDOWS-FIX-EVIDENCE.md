# Phase 57 Plan 10 — Windows-only path-separator fix evidence

**Owner decision (2026-08-17):** "fix it as an independent plan inside this phase."
This plan makes `tests/test_templates_path_collision_gate.py`'s resolved-path
assertion separator-portable. The product (`typsphinx/builder.py`) was never
wrong — only the test hardcoded a POSIX separator against a resolved
filesystem path.

---

### Pre-fix RED (cited, not re-derived)

This defect is **Windows-only** and **cannot be reproduced on this Linux
host** — `os.path.join`/`pathlib.Path` join with `/` (forward slash) on
POSIX, so no local run on this development machine can turn this assertion
red. No local RED transcript exists or can exist for this defect. The RED
proof is the cited CI run below, re-read live in this plan.

Commands run (this plan, live):

```
$ gh run view 31956166848 --json headSha,conclusion,jobs
```

Verbatim relevant fields (headSha and overall conclusion):

```json
{"conclusion": "failure", "headSha": "78bd595d344f46c6e1f5a18bce0e24da1f66a9ee"}
```

`headSha` matches the untouched phase-head commit `78bd595d` that plan
`57-02` pushed and dispatched — this run predates every wave-1 edit,
confirming the defect belongs to Phase 54.1's `templates_path`
collision-refusal work, not to this phase's version bump.

Two, and only two, jobs failed (read out of the same live `gh run view`
call, both identical failure signature):

| Job name | Conclusion |
|---|---|
| Test Python 3.13 on windows-latest | **failure** |
| Test Python 3.12 on windows-latest | **failure** |

(All other 10 jobs — `Build Package`, both `Integration Test` lanes,
`Type Check`, `Lint and Format Check`, both `ubuntu-latest` lanes, both
`macos-latest` lanes, `Code Coverage` — read `success`.)

Command run (this plan, live):

```
$ gh run view 31956166848 --log-failed
```

Verbatim `AssertionError` excerpt (Python 3.13 on windows-latest lane;
the Python 3.12 lane fails identically at the same line and test):

```
>       assert "_templates/nested" in message, (
            f"Expected beta's resolved bundle directory (containing "
            f"'_templates/nested') named:\n{message}"
        )
E       AssertionError: Expected beta's resolved bundle directory (containing '_templates/nested') named:
E         typst: 3 pre-write template path failure(s): 'alpha': registry key 'alpha''s resolved template bundle directory 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates' collides with the Sphinx templates_path entry '_templates' (resolved to 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates') -- the whole bundle directory is copied to the build output, so this would republish the project's Sphinx template directory; move the Typst template into a directory that is not on templates_path (this repository uses _typst/) and update typst_template / typst_document_templates to match; 'beta': registry key 'beta''s resolved template bundle directory 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates\\nested' collides with the Sphinx templates_path entry '_templates' (resolved to 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_templates') -- the whole bundle directory is copied to the build output, so this would republish the project's Sphinx template directory; move the Typst template into a directory that is not on templates_path (this repository uses _typst/) and update typst_template / typst_document_templates to match; 'gamma': registry key 'gamma''s resolved template bundle directory 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_typst' collides with the Sphinx templates_path entry '_typst/inner' (resolved to 'D:\\a\\typsphinx\\typsphinx\\tests\\fixtures\\templates_path_collision_multi_gate\\_typst/inner') -- the whole bundle directory is copied to the build output, so this would republish the project's Sphinx template directory; move the Typst template into a directory that is not on templates_path (this repository uses _typst/) and update typst_template / typst_document_templates to match

tests\test_templates_path_collision_gate.py:255: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_templates_path_collision_gate.py::TestMultiRelationAggregationGate::test_multi_relation_each_key_names_own_bundle_dir_and_own_entry
============ 1 failed, 1412 passed, 9 skipped in 328.33s (0:05:28) ============
```

**Root cause, read directly from the excerpt:** the assertion checked the
literal substring `'_templates/nested'` (forward slash) against beta's
*resolved* bundle directory, which the builder joins via `pathlib.Path` and
therefore renders with the platform's native `os.sep` —
`...\_templates\nested` on Windows, visible verbatim in the excerpt above.
The message itself is correct on both platforms; only the test's expected
string hardcoded POSIX.

---

### Classification sweep

Every assertion in `tests/test_templates_path_collision_gate.py` whose
expected value is a string literal containing `/` was enumerated (full-file
`grep -n "/"`, 387 lines) and classified. Two assertions carry a
slash-bearing literal; every other slash in the file is either a docstring/
comment (prose like "is / is-contained-by / contains"), a `Path(...)  /
"..."` construction (the pathlib division operator — already
separator-agnostic, not a hardcoded literal), or `tmp_path / "build"`
(same). Those are not assertions on message content and are excluded from
the table.

| Line (pre-fix) | Assertion | Expected substring | Classification | Disposition |
|---|---|---|---|---|
| 255 | `assert "_templates/nested" in message` | `'_templates/nested'` | **resolved-path** — part of beta's resolved bundle directory (`pathlib.Path`-joined; carries `os.sep` on Windows, confirmed in the CI excerpt: `...\_templates\nested`) | **Fixed** — now built with `str(Path("_templates") / "nested")` |
| 259 | `assert "_typst/inner" in message` | `'_typst/inner'` | **config-echoed** — a `templates_path` value taken verbatim from the fixture's `conf.py` (`templates_path = ["_templates", "_typst/inner"]`); confirmed in the same CI excerpt: the entry name portion (`templates_path entry '_typst/inner'`) keeps its internal forward slash on Windows because it is a string being appended, not resolved via `pathlib` parts | **Left unchanged**, comment added explaining why |

No other resolved-path assertion exists in this file. The sweep was
property-driven (every slash-bearing string literal), not line-number-driven
— CI named only line 255, but the search set was the whole file.

---

### The change

```diff
-        assert "_templates/nested" in message, (
-            f"Expected beta's resolved bundle directory (containing "
-            f"'_templates/nested') named:\n{message}"
-        )
-        assert "_typst/inner" in message, (
+        # Separator-portable: this substring is part of beta's RESOLVED
+        # bundle directory, which the builder joins via pathlib.Path and
+        # therefore renders with the platform's native os.sep (backslash
+        # on Windows -- confirmed by CI run 31956166848's log excerpt:
+        # '...\\_templates\\nested'). Build the expected substring with
+        # Path(...) too, so this assertion holds on both POSIX and
+        # Windows instead of hardcoding a forward slash.
+        beta_bundle_tail = str(Path("_templates") / "nested")
+        assert beta_bundle_tail in message, (
+            f"Expected beta's resolved bundle directory (containing "
+            f"{beta_bundle_tail!r}) named:\n{message}"
+        )
+        # NOT separator-portable, and that is correct: '_typst/inner' is
+        # a templates_path CONFIG VALUE echoed verbatim from the
+        # fixture's conf.py (`templates_path = ["_templates",
+        # "_typst/inner"]`), not a resolved filesystem path -- it stays a
+        # literal forward slash on every platform because that is what
+        # the config literally contains. Do not "fix" this one to use
+        # Path(...); doing so would stop proving the entry is echoed as
+        # configured.
+        assert "_typst/inner" in message, (
```

Only `tests/test_templates_path_collision_gate.py` was touched. No file
under `typsphinx/` or `.github/` was modified — `pathlib.Path` was already
imported at the top of the module (used by `FIXTURE_DIR` etc.), so no new
import was needed either. The product's resolved-path messages were always
correct on Windows; the assertion, not the message, hardcoded POSIX.

---

### Post-fix local green

Provisioned this worktree's own environment first, per this project's
`CLAUDE.md` § "Worktree-isolated execution":

```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
$ uv sync --extra dev
```

Target file, isolated:

```
$ uv run python -m pytest tests/test_templates_path_collision_gate.py -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac64e8b56dc8252a5
configfile: pyproject.toml
plugins: cov-7.1.0
collected 12 items

tests/test_templates_path_collision_gate.py ............                 [100%]

============================== 12 passed in 3.04s ==============================
```

Full local suite, verbatim (`uv run python -m pytest -q`):

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac64e8b56dc8252a5
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0
collected 1422 items

tests/test_abbr_pep_separator_render_gate.py ..                          [  0%]
tests/test_absolute_image_render_gate.py .                               [  0%]
tests/test_admonition_bucket_render_gate.py ............                 [  1%]
tests/test_admonition_greyscale_pipeline.py ..                           [  1%]
tests/test_admonition_locale_title_precedence_gate.py .........          [  1%]
tests/test_admonitions.py ..................                             [  3%]
tests/test_authors_pipeline_stage_gate.py ........                       [  3%]
tests/test_builder.py ...............................                    [  5%]
tests/test_builder_output_stem.py .........................              [  7%]
tests/test_builder_requirement13.py .....                                [  7%]
tests/test_bundle_copy_exclusion_manifest_gate.py ....                   [  8%]
tests/test_bundle_layout_sweep_gate.py .........                         [  8%]
tests/test_captioned_table_propagated_target_render_gate.py .........    [  9%]
tests/test_changelog_extraction.py ......                                [  9%]
tests/test_changelog_page_gate.py ..ssss                                 [ 10%]
tests/test_citation_caption_dangling_label_gate.py ...                   [ 10%]
tests/test_citation_degradation_gate.py .................                [ 11%]
tests/test_citation_render_gate.py .........                             [ 12%]
tests/test_codly_caption_listitem_leak_render_gate.py ..                 [ 12%]
tests/test_collision_predicate_completeness_gate.py ...........          [ 13%]
tests/test_collision_validator_gate.py .......                           [ 13%]
tests/test_conf17_prewrite_gate.py ...                                   [ 13%]
tests/test_config.py ........                                            [ 14%]
tests/test_config_other_options.py ........                              [ 15%]
tests/test_config_template_mapping.py .......                            [ 15%]
tests/test_confval_field_body_render_gate.py .                           [ 15%]
tests/test_confval_field_spacing_render_gate.py ..                       [ 15%]
tests/test_converted_image_collision_render_gate.py ...                  [ 16%]
tests/test_corpus_gate.py ....s                                          [ 16%]
tests/test_cross_doc_label_namespace_render_gate.py .                    [ 16%]
tests/test_default_typst_documents_derivation.py .............           [ 17%]
tests/test_default_typst_documents_gate.py ..                            [ 17%]
tests/test_deflist_definition_multiblock_render_gate.py .                [ 17%]
tests/test_deflist_nested_definition_render_gate.py .                    [ 17%]
tests/test_deflist_term_concat_render_gate.py ...                        [ 17%]
tests/test_deflist_term_inline_children_gate.py ........                 [ 18%]
tests/test_desc_bodyless_concat_render_gate.py .                         [ 18%]
tests/test_desc_break_marker_buffer_swap_gate.py .....                   [ 18%]
tests/test_desc_container_propagated_target_render_gate.py .             [ 18%]
tests/test_desc_content_indent_render_gate.py ...............            [ 19%]
tests/test_desc_rubric_decoupling_render_gate.py .....                   [ 20%]
tests/test_desc_sig_space_render_gate.py ..                              [ 20%]
tests/test_desc_signature_anchor_render_gate.py .                        [ 20%]
tests/test_desc_signature_concat_render_gate.py ..                       [ 20%]
tests/test_docs_contract_claims_gate.py ........                         [ 21%]
tests/test_docs_template_layout_gate.py ...                              [ 21%]
tests/test_document_metadata_render_gate.py ....                         [ 21%]
tests/test_documented_params_contract_gate.py .......                    [ 22%]
tests/test_duplicate_include_label_render_gate.py .                      [ 22%]
tests/test_empty_typst_documents_optout_gate.py ..                       [ 22%]
tests/test_entry_metadata_precedence.py .......................          [ 24%]
tests/test_entry_metadata_route_uniformity.py .....                      [ 24%]
tests/test_entry_points.py ..                                            [ 24%]
tests/test_epigraph_render_gate.py .                                     [ 24%]
tests/test_examples_basic.py ...............                             [ 25%]
tests/test_examples_charged_ieee_gate.py ..                              [ 25%]
tests/test_extension.py ......                                           [ 26%]
tests/test_external_link_style_render_gate.py ...                        [ 26%]
tests/test_field_body_typography_render_gate.py ........................ [ 28%]
.                                                                        [ 28%]
tests/test_field_list_in_list_item_render_gate.py ..                     [ 28%]
tests/test_figure_propagated_target_render_gate.py ........              [ 28%]
tests/test_footnotes.py .....                                            [ 29%]
tests/test_glob_image_render_gate.py .                                   [ 29%]
tests/test_hand_compile_root_gate.py ..........                          [ 30%]
tests/test_heading_depth_render_gate.py .......                          [ 30%]
tests/test_include_edge_derivation_unit.py ............................. [ 32%]
....                                                                     [ 32%]
tests/test_include_edge_separator_collision_gate.py ....                 [ 33%]
tests/test_include_ledger_removal_gate.py ..........                    [ 33%]
tests/test_inline_literal_overflow_render_gate.py ..                     [ 33%]
tests/test_inline_math_after_text_render_gate.py ...                    [ 34%]
tests/test_inline_references.py ..............                          [ 35%]
tests/test_integration_advanced.py .............                        [ 36%]
tests/test_integration_basic.py .............                           [ 36%]
tests/test_integration_multi_doc.py .........                           [ 37%]
tests/test_integration_nested_toctree.py .................              [ 38%]
tests/test_label_at_char_render_gate.py .                                [ 38%]
tests/test_label_existence_guard_unit.py ................                [ 40%]
tests/test_line_blocks.py ...                                            [ 40%]
tests/test_list_item_nested_block_render_gate.py .                       [ 40%]
tests/test_master_include_set_predicate_gate.py ....                     [ 40%]
tests/test_math_fallback.py ........                                     [ 41%]
tests/test_math_mitex.py .........                                       [ 41%]
tests/test_math_native.py ......                                         [ 42%]
tests/test_missing_and_malformed_master_gate.py ..                       [ 42%]
tests/test_multi_master_metadata_no_leak.py ......                      [ 42%]
tests/test_nested_figure_render_gate.py .......                          [ 43%]
tests/test_nested_master_render_gate.py ...                              [ 43%]
tests/test_nested_table_render_gate.py .......                           [ 43%]
tests/test_nested_toctree_paths.py ..........                            [ 44%]
tests/test_no_stale_github_io_links.py ....                              [ 44%]
tests/test_non_str_docname_gate.py .                                     [ 45%]
tests/test_out02_escape_target_gate.py ...                               [ 45%]
tests/test_output_layout_docs_gate.py .............                      [ 46%]
tests/test_package_only_config_gate.py ............                     [ 46%]
tests/test_package_template_routing.py ...                               [ 47%]
tests/test_paragraph_concat_render_gate.py ..                            [ 47%]
tests/test_paragraph_propagated_target_render_gate.py .                  [ 47%]
tests/test_paragraph_soft_newline_render_gate.py .                       [ 47%]
tests/test_params_authors_writers.py ........................            [ 49%]
tests/test_params_exclusivity_gate.py .....................              [ 50%]
tests/test_pdf_generation.py ..............................              [ 52%]
tests/test_pdf_render_gate.py ...............................            [ 54%]
tests/test_preview_smoke_gate.py .                                       [ 54%]
tests/test_preview_version_sync.py ...                                   [ 55%]
tests/test_prewrite_failure_aggregation_gate.py ....                     [ 55%]
tests/test_quickstart_docs_gate.py .....                                 [ 55%]
tests/test_readme_version_sync.py .                                      [ 55%]
tests/test_readthedocs_config.py ......                                 [ 56%]
tests/test_ref_target_nested_list_render_gate.py .                       [ 56%]
tests/test_registry_container_shape_gate.py .........                   [ 57%]
tests/test_registry_documentation_gate.py .......................       [ 58%]
tests/test_registry_prewrite_validation_gate.py ..........               [ 59%]
tests/test_removed_config_deprecation_gate.py ..........                [ 60%]
tests/test_reserved_key_case_prewrite_gate.py ..                        [ 60%]
tests/test_rubric_indent_invariance.py .......                          [ 60%]
tests/test_rubric_option_concat_render_gate.py .                        [ 60%]
tests/test_rubric_propagated_target_render_gate.py .                    [ 60%]
tests/test_rubric_strong_nesting_render_gate.py ......                  [ 61%]
tests/test_sanitize_label_injectivity_unit.py .......................... [ 63%]
.....                                                                    [ 63%]
tests/test_signature_break_and_arrow_gate.py ............               [ 64%]
tests/test_signature_overflow_render_gate.py ......                     [ 64%]
tests/test_signature_page_boundary_render_gate.py ...                   [ 64%]
tests/test_signature_typography_gate.py ...............                 [ 65%]
tests/test_signature_typography_multi_signature_page_count_gate.py .    [ 66%]
tests/test_state_guard_composition_gate.py ...........                  [ 66%]
tests/test_state_guard_numref_gate.py ......                            [ 67%]
tests/test_state_guard_shapes_gate.py ..................                [ 68%]
tests/test_static_asset_copy_gate.py ..                                 [ 68%]
tests/test_substitution_definition_render_gate.py .                     [ 68%]
tests/test_table_empty_caption_anchor_render_gate.py ..                 [ 68%]
tests/test_table_in_list_item_render_gate.py .                          [ 68%]
tests/test_target_label_render_gate.py .                                [ 68%]
tests/test_target_name_render_gate.py ..                                [ 69%]
tests/test_template_codly.py ......                                     [ 69%]
tests/test_template_engine.py .......................................... [ 72%]
.................................................                        [ 75%]
tests/test_template_import_path.py ............                        [ 76%]
tests/test_template_mitex.py ..                                         [ 76%]
tests/test_template_prefix_reservation_gate.py .......                  [ 77%]
tests/test_template_registry.py ........................................ [ 80%]
....................................                                     [ 82%]
tests/test_templates_path_collision_gate.py ............                [ 83%]
tests/test_toctree_requirement13.py .........                           [ 84%]
tests/test_toolchain_config_gate.py ....                                [ 84%]
tests/test_topics.py .....                                              [ 84%]
tests/test_translator.py ............................................... [ 88%]
.......................................................................  [ 93%]
tests/test_two_key_selection_gate.py ......                             [ 93%]
tests/test_two_layer_output_gate.py ............                        [ 94%]
tests/test_typst_documents_collision_gate.py .....                      [ 94%]
tests/test_typst_elements_pass_through_gate.py ..........                [ 95%]
tests/test_typst_lang_gate.py .....................                     [ 96%]
tests/test_typst_string_escape_gate.py .....                            [ 97%]
tests/test_user_template_relative_asset_gate.py ............            [ 98%]
tests/test_whole_document_xref_unit.py ..........                       [ 98%]
tests/test_wide_table_render_gate.py .                                  [ 98%]
tests/test_xref_compile_time_guard_render_gate.py ......                [ 99%]
tests/test_xref_orphan_degrade_render_gate.py .                         [ 99%]
tests/test_xref_whole_document_guard_render_gate.py ........            [100%]

================= 1417 passed, 5 skipped in 119.05s (0:01:59) ==================
```

**1417 passed, 5 skipped, 0 failed** — matches the wave-1 post-merge
baseline recorded in `STATE.md` exactly. The POSIX side did not regress.

Fence check, also run this plan:

```
$ git diff --name-only -- typsphinx/ .github/
(empty)
```

---

### What this plan does NOT claim

- **No green Windows lane has been observed for this fix.** This defect is
  Windows-only and cannot be reproduced on this Linux host — there is no
  way to run the fixed test on `windows-latest` from this plan. Confirming
  the fix actually clears both `windows-latest` lanes is **plan `57-05`'s
  post-bump authority dispatch**, not this plan's job.
- This plan does not assert that CI run `31956166848` (or any run) will
  come back all-`success` after this fix. It only proves: (1) the pre-fix
  RED is real and cited from a live re-read, (2) the fix is scoped to the
  one resolved-path assertion the sweep found, (3) the local POSIX suite
  is unaffected, and (4) no product or CI-workflow file was touched.
- No irreversible action was taken: no `v0.9.0` tag (local or remote), no
  `release.yml` dispatch, no pull request.
