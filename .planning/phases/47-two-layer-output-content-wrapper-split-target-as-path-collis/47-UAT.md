---
status: complete
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
source: [47-01-SUMMARY.md, 47-02-SUMMARY.md, 47-03-SUMMARY.md, 47-04-SUMMARY.md, 47-05-SUMMARY.md, 47-06-SUMMARY.md, 47-07-SUMMARY.md, 47-08-SUMMARY.md, 47-09-SUMMARY.md, 47-10-SUMMARY.md, 47-11-SUMMARY.md, 47-12-SUMMARY.md, 47-13-SUMMARY.md, 47-14-SUMMARY.md]
started: 2026-08-12T02:03:23Z
updated: 2026-08-12T02:03:23Z
---

## Current Test

[testing complete]

## Tests

### 1. [47-01 D1] 47-EXPECTED-STRUCTURE.md derives, from each fixture's conf.py/rst read literally with no builder run, the exact wrapper/content paths and #include() strings for all five new fixtures, plus the Corpus migration rules section
expected: 47-EXPECTED-STRUCTURE.md derives, from each fixture's conf.py/rst read literally with no builder run, the exact wrapper/content paths and #include() strings for all five new fixtures, plus the Corpus migration rules section
result: pass
source: automated
coverage_id: D1
coverage_source: 47-01-SUMMARY.md
verified_by: other: grep -c '../guide/index.typ' / '../_template.typ' / 'Reversal notice' / '## Corpus migration rules' 47-EXPECTED-STRUCTURE.md (all present)

### 2. [47-01 D2] 47-RED-EVIDENCE.md records verbatim pre-fix RED for COMP-01..04, OUT-03, BLD-02..04 -- COMP-03's is a classic TypstError ('file not found'), COMP-04/BLD-02/BLD-03/BLD-04's are structural
expected: 47-RED-EVIDENCE.md records verbatim pre-fix RED for COMP-01..04, OUT-03, BLD-02..04 -- COMP-03's is a classic TypstError ('file not found'), COMP-04/BLD-02/BLD-03/BLD-04's are structural
result: pass
source: automated
coverage_id: D2
coverage_source: 47-01-SUMMARY.md
verified_by: other: grep -c 'file not found' / heading presence checks against 47-RED-EVIDENCE.md (all present)

### 3. [47-01 D3] tests/test_two_layer_output_gate.py: 6 tests (COMP-01, COMP-02, COMP-03, COMP-04, OUT-03, compute_content_include_path unit) all xfail(strict=True) against the unfixed tree
expected: tests/test_two_layer_output_gate.py: 6 tests (COMP-01, COMP-02, COMP-03, COMP-04, OUT-03, compute_content_include_path unit) all xfail(strict=True) against the unfixed tree
result: pass
source: automated
coverage_id: D3
coverage_source: 47-01-SUMMARY.md
verified_by: integration: uv run pytest tests/test_two_layer_output_gate.py -q

### 4. [47-01 D4] tests/test_collision_validator_gate.py: 7 tests (BLD-02/03/04 x2 builders + _collision_key unit) all xfail(strict=True) against the unfixed tree
expected: tests/test_collision_validator_gate.py: 7 tests (BLD-02/03/04 x2 builders + _collision_key unit) all xfail(strict=True) against the unfixed tree
result: pass
source: automated
coverage_id: D4
coverage_source: 47-01-SUMMARY.md
verified_by: integration: uv run pytest tests/test_collision_validator_gate.py -q

### 5. [47-01 D5] Five new fixture projects under tests/fixtures/, each with a load-bearing-facts conf.py comment
expected: Five new fixture projects under tests/fixtures/, each with a load-bearing-facts conf.py comment
result: pass
source: automated
coverage_id: D5
coverage_source: 47-01-SUMMARY.md
verified_by: other: uv run python -c \"...five conf.py existence check...\" (task 1 <automated> verify, exit 0)

### 6. [47-01 D6] Full suite stays green with only the new xfailed tests added; no production code touched
expected: Full suite stays green with only the new xfailed tests added; no production code touched
result: pass
source: automated
coverage_id: D6
coverage_source: 47-01-SUMMARY.md
verified_by: integration: uv run pytest -q -> 991 passed, 5 skipped, 13 xfailed, 0 failed; git status --porcelain typsphinx/ empty

### 7. [47-02 D1] A content file (docname-derived, no template) and a wrapper file (target-derived, full template + #include()) are both emitted for a root-level master, verified via a real sphinx-build + real typst.compile()
expected: A content file (docname-derived, no template) and a wrapper file (target-derived, full template + #include()) are both emitted for a root-level master, verified via a real sphinx-build + real typst.compile()
result: pass
source: automated
coverage_id: D1
coverage_source: 47-02-SUMMARY.md
verified_by: integration: tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_comp01_content_file_has_no_template | integration: tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_comp02_wrapper_file_has_template_and_include

### 8. [47-02 D2] Content files stay docname-derived and wrappers land at their resolved target path, independently, for a nested fixture whose wrapper target strays into an unrelated directory (OUT-01/OUT-03)
expected: Content files stay docname-derived and wrappers land at their resolved target path, independently, for a nested fixture whose wrapper target strays into an unrelated directory (OUT-01/OUT-03)
result: pass
source: automated
coverage_id: D2
coverage_source: 47-02-SUMMARY.md
verified_by: integration: tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_out03_content_files_stay_docname_derived

### 9. [47-02 D3] B-1 (COMP-03): a nested wrapper whose #include() previously named a physically different file now compiles successfully via a real typst.compile()
expected: B-1 (COMP-03): a nested wrapper whose #include() previously named a physically different file now compiles successfully via a real typst.compile()
result: pass
source: automated
coverage_id: D3
coverage_source: 47-02-SUMMARY.md
verified_by: integration: tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_comp03_b1_nested_master_compiles

### 10. [47-02 D4] B-2 (COMP-04): a toctree-included master's template no longer re-expands mid-body -- verified by real pypdf structural extraction (no second title page, exactly one outline)
expected: B-2 (COMP-04): a toctree-included master's template no longer re-expands mid-body -- verified by real pypdf structural extraction (no second title page, exactly one outline)
result: pass
source: automated
coverage_id: D4
coverage_source: 47-02-SUMMARY.md
verified_by: integration: tests/test_two_layer_output_gate.py::TestTwoLayerOutputGatePdf::test_comp04_b2_no_mid_body_template_reexpansion

### 11. [47-02 D5] OUT-01 reversed: a path-bearing typst_documents target resolves exactly where written, with no separator guard; OUT-02 kept: traversal/absolute/drive-qualified targets still fall back to a basename with a warning
expected: OUT-01 reversed: a path-bearing typst_documents target resolves exactly where written, with no separator guard; OUT-02 kept: traversal/absolute/drive-qualified targets still fall back to a basename with a warning
result: pass
source: automated
coverage_id: D5
coverage_source: 47-02-SUMMARY.md
verified_by: unit: tests/test_builder_output_stem.py (23 of 27 tests pass unchanged; 4 separator-guard tests now fail as the plan's own acceptance criteria requires -- see Known Deferred Failures)

### 12. [47-02 D6] -b typst and -b typstpdf emit byte-identical .typ files from one shared write path; only wrapper files compile to PDF
expected: -b typst and -b typstpdf emit byte-identical .typ files from one shared write path; only wrapper files compile to PDF
result: pass
source: automated
coverage_id: D6
coverage_source: 47-02-SUMMARY.md
verified_by: integration: tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_typst_and_typstpdf_emit_byte_identical_typ_files

### 13. [47-02 D7] Two consecutive -b typst builds of the same project produce byte-identical wrapper and content files (deterministic emission order)
expected: Two consecutive -b typst builds of the same project produce byte-identical wrapper and content files (deterministic emission order)
result: pass
source: automated
coverage_id: D7
coverage_source: 47-02-SUMMARY.md
verified_by: integration: tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_typst_build_is_deterministic_across_runs

### 14. [47-02 D8] -b typst logs which wrapper files it wrote and states those are the files to compile (D-07)
expected: -b typst logs which wrapper files it wrote and states those are the files to compile (D-07)
result: pass
source: automated
coverage_id: D8
coverage_source: 47-02-SUMMARY.md
verified_by: integration: tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_typst_build_log_names_the_wrapper_files_to_compile

### 15. [47-02 D9] The master/included boolean predicate (_is_master_document) is gone from the repository, proven by a repo-wide grep over typsphinx/ and tests/ rather than reading writer.py alone
expected: The master/included boolean predicate (_is_master_document) is gone from the repository, proven by a repo-wide grep over typsphinx/ and tests/ rather than reading writer.py alone
result: pass
source: automated
coverage_id: D9
coverage_source: 47-02-SUMMARY.md
verified_by: other: grep -rn \"_is_master_document\" typsphinx/ tests/ (zero hits)

### 16. [47-03 D1] OUT-01: a POSIX- or backslash-separator-bearing typst_documents target resolves exactly where written (normalized to posix-style separators), with no warning -- the separator-membership guard Phase 44's D-06/D-07 imposed is reversed
expected: OUT-01: a POSIX- or backslash-separator-bearing typst_documents target resolves exactly where written (normalized to posix-style separators), with no warning -- the separator-membership guard Phase 44's D-06/D-07 imposed is reversed
result: pass
source: automated
coverage_id: D1
coverage_source: 47-03-SUMMARY.md
verified_by: unit: tests/test_builder_output_stem.py::test_resolve_output_stem_resolves_posix_path_bearing_target | unit: tests/test_builder_output_stem.py::test_resolve_output_stem_normalizes_backslash_path_bearing_target | unit: tests/test_builder_output_stem.py::test_resolve_output_stem_emits_no_warning_for_path_bearing_target

### 17. [47-03 D2] OUT-01: a nested docname's WRAPPER path is no longer force-relocated into that docname's own directory, while its CONTENT path stays unconditionally docname-derived regardless of the wrapper's target
expected: OUT-01: a nested docname's WRAPPER path is no longer force-relocated into that docname's own directory, while its CONTENT path stays unconditionally docname-derived regardless of the wrapper's target
result: pass
source: automated
coverage_id: D2
coverage_source: 47-03-SUMMARY.md
verified_by: unit: tests/test_builder_output_stem.py::test_wrapper_path_ignores_docname_directory_but_content_path_does_not

### 18. [47-03 D3] OUT-02: the three escape-shaped terms (parent traversal, absolute path, drive-qualified path) are still refused with a basename fallback -- kept verbatim as OUT-02 regression tests
expected: OUT-02: the three escape-shaped terms (parent traversal, absolute path, drive-qualified path) are still refused with a basename fallback -- kept verbatim as OUT-02 regression tests
result: pass
source: automated
coverage_id: D3
coverage_source: 47-03-SUMMARY.md
verified_by: unit: tests/test_builder_output_stem.py::test_resolve_output_stem_guards_parent_traversal | unit: tests/test_builder_output_stem.py::test_resolve_output_stem_guards_absolute_target | unit: tests/test_builder_output_stem.py::test_resolve_output_stem_guards_drive_qualified_target

### 19. [47-03 D4] OUT-02: each of the three escape shapes is refused in a real sphinx-build with a warning naming the offending target AND an outdir-containment proof -- every regular file under the build directory resolves under the resolved build directory, and no escape.typ leaks to the build directory's parent
expected: OUT-02: each of the three escape shapes is refused in a real sphinx-build with a warning naming the offending target AND an outdir-containment proof -- every regular file under the build directory resolves under the resolved build directory, and no escape.typ leaks to the build directory's parent
result: pass
source: automated
coverage_id: D4
coverage_source: 47-03-SUMMARY.md
verified_by: integration: tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[traversal] | integration: tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[absolute] | integration: tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[drive]

### 20. [47-03 D5] RESEARCH.md Assumptions-Log A3 closed by measurement: a repo-wide grep over typsphinx/ for os.sep/os.altsep/isabs/normpath/relpath/basename/the drive-letter idiom found no second, independent path-rejection site for a typst_documents target string; the one literal (non-independent) duplication found (the drive-letter idiom) was extracted into a single shared helper
expected: RESEARCH.md Assumptions-Log A3 closed by measurement: a repo-wide grep over typsphinx/ for os.sep/os.altsep/isabs/normpath/relpath/basename/the drive-letter idiom found no second, independent path-rejection site for a typst_documents target string; the one literal (non-independent) duplication found (the drive-letter idiom) was extracted into a single shared helper
result: pass
source: automated
coverage_id: D5
coverage_source: 47-03-SUMMARY.md
verified_by: other: .planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-RED-EVIDENCE.md 'A3: second path-rejection site search' (grep commands + raw output recorded verbatim)

### 21. [47-04 D1] 21-fixture, 6-module multi-fixture render-gate cluster (admonition/figure/table/codly/desc_signature/xref/manpage/etc.) de-collided and migrated to the two-layer output shape
expected: 21-fixture, 6-module multi-fixture render-gate cluster (admonition/figure/table/codly/desc_signature/xref/manpage/etc.) de-collided and migrated to the two-layer output shape
result: pass
source: automated
coverage_id: D1
coverage_source: 47-04-SUMMARY.md
verified_by: integration: uv run pytest tests/test_pdf_render_gate.py tests/test_admonition_bucket_render_gate.py tests/test_desc_container_propagated_target_render_gate.py tests/test_field_list_in_list_item_render_gate.py tests/test_package_only_config_gate.py tests/test_signature_page_boundary_render_gate.py -q

### 22. [47-04 D2] 6 single-fixture render gates (abbr-pep-separator, confval-field-body, desc-signature-anchor, inline-math-after-text, preview-smoke, table-in-list-item) de-collided and migrated; both PDF-text golden files (inline_math_pdf_text_mitex/native.golden.txt) verified unchanged
expected: 6 single-fixture render gates (abbr-pep-separator, confval-field-body, desc-signature-anchor, inline-math-after-text, preview-smoke, table-in-list-item) de-collided and migrated; both PDF-text golden files (inline_math_pdf_text_mitex/native.golden.txt) verified unchanged
result: pass
source: automated
coverage_id: D2
coverage_source: 47-04-SUMMARY.md
verified_by: integration: uv run pytest tests/test_abbr_pep_separator_render_gate.py tests/test_confval_field_body_render_gate.py tests/test_desc_signature_anchor_render_gate.py tests/test_inline_math_after_text_render_gate.py tests/test_preview_smoke_gate.py tests/test_table_in_list_item_render_gate.py -q

### 23. [47-04 D3] 7-fixture, 5-module toctree/malformed-entry gate cluster de-collided and migrated, including missing_and_malformed_master_gate's D-02 attempt-all-then-raise contract against the new content+wrapper file pair; repo-wide _is_master_document grep reconfirmed zero-hit
expected: 7-fixture, 5-module toctree/malformed-entry gate cluster de-collided and migrated, including missing_and_malformed_master_gate's D-02 attempt-all-then-raise contract against the new content+wrapper file pair; repo-wide _is_master_document grep reconfirmed zero-hit
result: pass
source: automated
coverage_id: D3
coverage_source: 47-04-SUMMARY.md
verified_by: integration: uv run pytest tests/test_changelog_page_gate.py tests/test_deflist_term_concat_render_gate.py tests/test_duplicate_include_label_render_gate.py tests/test_missing_and_malformed_master_gate.py tests/test_rubric_propagated_target_render_gate.py -q | other: grep -rn \"_is_master_document\" tests/test_missing_and_malformed_master_gate.py tests/fixtures/missing_and_malformed_master_gate/ (zero hits)

### 24. [47-05 D1] 17 group-B test modules (nested-toctree/multi-document integration suites, desc-signature/field/figure/citation/deflist/epigraph/rubric render gates) pass against the post-split content/wrapper emitter, in one combined pytest invocation
expected: 17 group-B test modules (nested-toctree/multi-document integration suites, desc-signature/field/figure/citation/deflist/epigraph/rubric render gates) pass against the post-split content/wrapper emitter, in one combined pytest invocation
result: pass
source: automated
coverage_id: D1
coverage_source: 47-05-SUMMARY.md
verified_by: integration: uv run pytest tests/test_desc_content_indent_render_gate.py tests/test_figure_propagated_target_render_gate.py tests/test_heading_depth_render_gate.py tests/test_integration_nested_toctree.py tests/test_paragraph_concat_render_gate.py tests/test_static_asset_copy_gate.py tests/test_absolute_image_render_gate.py tests/test_confval_field_spacing_render_gate.py tests/test_desc_signature_concat_render_gate.py tests/test_integration_multi_doc.py tests/test_ref_target_nested_list_render_gate.py tests/test_target_label_render_gate.py tests/test_citation_degradation_gate.py tests/test_deflist_term_inline_children_gate.py tests/test_epigraph_render_gate.py tests/test_nested_figure_render_gate.py tests/test_rubric_strong_nesting_render_gate.py -q (105 passed)

### 25. [47-05 D2] Every group-B fixture's typst_documents target resolves to a path distinct from its own docname's content path and from every other entry in the same fixture (fixture de-collision rule applied to all 19 fixtures)
expected: Every group-B fixture's typst_documents target resolves to a path distinct from its own docname's content path and from every other entry in the same fixture (fixture de-collision rule applied to all 19 fixtures)
result: pass
source: automated
coverage_id: D2
coverage_source: 47-05-SUMMARY.md
verified_by: unit: manual review of all 19 conf.py diffs -- each self-colliding target ('index'/'index.typ') renamed to 'master.typ', comment recorded per fixture

### 26. [47-05 D3] Toctree #include() assertions proven to live on content files (R5, unchanged); each of the 7 nested-toctree/layout-cluster wrappers proven to hold exactly one #include() naming its own master's content path (R2/R3, new assertion per fixture)
expected: Toctree #include() assertions proven to live on content files (R5, unchanged); each of the 7 nested-toctree/layout-cluster wrappers proven to hold exactly one #include() naming its own master's content path (R2/R3, new assertion per fixture)
result: pass
source: automated
coverage_id: D3
coverage_source: 47-05-SUMMARY.md
verified_by: integration: tests/test_integration_nested_toctree.py::TestNestedToctreeIntegration::test_root_wrapper_has_exactly_one_include_of_its_content, ::TestMultiLevelNestedToctree::test_root_wrapper_has_exactly_one_include_of_its_content, ::TestSiblingDirectoryReferences::test_root_wrapper_has_exactly_one_include_of_its_content, tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_wrapper_has_exactly_one_include_of_its_content, tests/test_figure_propagated_target_render_gate.py::TestFigurePropagatedTargetRenderGate::test_wrapper_has_exactly_one_include_of_its_content, tests/test_paragraph_concat_render_gate.py::TestParagraphConcatRenderGate::test_wrapper_has_exactly_one_include_of_its_content, tests/test_static_asset_copy_gate.py::TestStaticAssetCopyRenderGate::test_wrapper_has_exactly_one_include_of_its_content

### 27. [47-06 D1] 17 group-C test modules (integration, entry-metadata, typography, and remaining render gates) pass together against the post-split content/wrapper emitter in one pytest invocation
expected: 17 group-C test modules (integration, entry-metadata, typography, and remaining render gates) pass together against the post-split content/wrapper emitter in one pytest invocation
result: pass
source: automated
coverage_id: D1
coverage_source: 47-06-SUMMARY.md
verified_by: integration: uv run pytest tests/test_desc_rubric_decoupling_render_gate.py tests/test_glob_image_render_gate.py tests/test_integration_advanced.py tests/test_integration_basic.py tests/test_paragraph_propagated_target_render_gate.py tests/test_substitution_definition_render_gate.py tests/test_admonition_greyscale_pipeline.py tests/test_deflist_definition_multiblock_render_gate.py tests/test_document_metadata_render_gate.py tests/test_label_at_char_render_gate.py tests/test_rubric_indent_invariance.py tests/test_wide_table_render_gate.py tests/test_citation_render_gate.py tests/test_desc_bodyless_concat_render_gate.py tests/test_external_link_style_render_gate.py tests/test_nested_table_render_gate.py tests/test_signature_break_and_arrow_gate.py -q (82 passed)

### 28. [47-06 D2] Every group-C fixture's typst_documents target is de-collided from its own docname's content path (no self-collision) and from any sibling target
expected: Every group-C fixture's typst_documents target is de-collided from its own docname's content path (no self-collision) and from any sibling target
result: pass
source: automated
coverage_id: D2
coverage_source: 47-06-SUMMARY.md
verified_by: other: manual review of all 18 fixtures' conf.py after migration, plus real-build measurement confirming no cyclic-import TypstError on any group-C fixture

### 29. [47-06 D3] D-08's positional per-entry title/author read is proven end to end by a repeated-docname (D-04) fixture whose surviving wrapper carries the correctly-selected entry's own title, not a docname first-match result
expected: D-08's positional per-entry title/author read is proven end to end by a repeated-docname (D-04) fixture whose surviving wrapper carries the correctly-selected entry's own title, not a docname first-match result
result: pass
source: automated
coverage_id: D3
coverage_source: 47-06-SUMMARY.md
verified_by: integration: tests/test_document_metadata_render_gate.py::TestEntryTitleAuthorRenderGate::test_repeated_docname_wrapper_reads_its_own_entry_title_not_first_match

### 30. [47-07 D1] Group-D page-count and typography cluster (6 modules, 5 fixtures) migrated: page-shaped and page-boundary assertions repointed at the compiled WRAPPER (master.typ/master.pdf); translator body markup assertions unchanged on the content file
expected: Group-D page-count and typography cluster (6 modules, 5 fixtures) migrated: page-shaped and page-boundary assertions repointed at the compiled WRAPPER (master.typ/master.pdf); translator body markup assertions unchanged on the content file
result: pass
source: automated
coverage_id: D1
coverage_source: 47-07-SUMMARY.md
verified_by: integration: tests/test_signature_typography_multi_signature_page_count_gate.py::TestSignatureTypographyMultiSignaturePageCountGate::test_multi_signature_document_page_count_at_real_geometry | integration: tests/test_signature_typography_gate.py::TestSignatureTypographyGate (15 tests)

### 31. [47-07 D2] Group-D template-contract and propagated-target cluster (6 modules, 6 fixtures) migrated: the published nine-parameter custom-template contract asserted against the wrapper's show-rule call with an unchanged parameter set; every propagated-target label assertion stays on the content file
expected: Group-D template-contract and propagated-target cluster (6 modules, 6 fixtures) migrated: the published nine-parameter custom-template contract asserted against the wrapper's show-rule call with an unchanged parameter set; every propagated-target label assertion stays on the content file
result: pass
source: automated
coverage_id: D2
coverage_source: 47-07-SUMMARY.md
verified_by: integration: tests/test_documented_params_contract_gate.py (7 tests) | integration: tests/test_xref_orphan_degrade_render_gate.py::TestXrefOrphanDegradeRenderGate::test_typstpdf_orphan_xref_degrades_included_xref_links

### 32. [47-07 D3] Remaining group-D gates and the malformed-docname gate (5 modules, 5 fixtures) migrated; BLD-01's non-str-docname guard re-verified against the rewritten wrapper-path and content-path computation
expected: Remaining group-D gates and the malformed-docname gate (5 modules, 5 fixtures) migrated; BLD-01's non-str-docname guard re-verified against the rewritten wrapper-path and content-path computation
result: pass
source: automated
coverage_id: D3
coverage_source: 47-07-SUMMARY.md
verified_by: integration: tests/test_non_str_docname_gate.py::TestNonStrDocnameGate::test_non_str_docname_fails_build_but_good_master_still_compiles | integration: 17 group-D modules together (82 tests) in one uv run pytest invocation

### 33. [47-08 D1] tests/fixtures/template_named_dir_master/ no longer configures two entries resolving to one target path (BLD-02 duplicate-target)
expected: tests/fixtures/template_named_dir_master/ no longer configures two entries resolving to one target path (BLD-02 duplicate-target)
result: pass
source: automated
coverage_id: D1
coverage_source: 47-08-SUMMARY.md
verified_by: integration: tests/test_template_import_path.py::TestTemplateNamedDirMasterRenderGate::test_template_named_dir_master_resolves_and_compiles

### 34. [47-08 D2] tests/fixtures/nested_master_render_gate/ no longer configures a target resolving onto another docname's content path (general de-collision convention; measured to not be an actual BLD-03 self-collision for this specific fixture)
expected: tests/fixtures/nested_master_render_gate/ no longer configures a target resolving onto another docname's content path (general de-collision convention; measured to not be an actual BLD-03 self-collision for this specific fixture)
result: pass
source: automated
coverage_id: D2
coverage_source: 47-08-SUMMARY.md
verified_by: integration: tests/test_nested_master_render_gate.py::TestNestedMasterRenderGate (all 3 tests)

### 35. [47-08 D3] The template import path (tests/test_template_import_path.py) is derived from the WRAPPER's resolved output directory via compute_template_import_path_for_dir(), not from the master docname
expected: The template import path (tests/test_template_import_path.py) is derived from the WRAPPER's resolved output directory via compute_template_import_path_for_dir(), not from the master docname
result: pass
source: automated
coverage_id: D3
coverage_source: 47-08-SUMMARY.md
verified_by: unit: tests/test_template_import_path.py::TestComputeTemplateImportPathForDir (7-case parametrized matrix + fence + explicit _template-directory marker)

### 36. [47-08 D4] The project's own documentation build (tox -e docs-pdf) still produces its PDF at the same path (docs/_build/pdf/typsphinx.pdf) as before the split
expected: The project's own documentation build (tox -e docs-pdf) still produces its PDF at the same path (docs/_build/pdf/typsphinx.pdf) as before the split
result: pass
source: automated
coverage_id: D4
coverage_source: 47-08-SUMMARY.md
verified_by: other: uv run tox -e docs-pdf (real run, this session): exit 0, docs/_build/pdf/typsphinx.pdf exists, 2,463,726 bytes

### 37. [47-08 D5] The bundled examples/basic project still builds and compiles; examples/advanced's target is confirmed non-colliding by direct read (no test module in this plan's own scope builds it live)
expected: The bundled examples/basic project still builds and compiles; examples/advanced's target is confirmed non-colliding by direct read (no test module in this plan's own scope builds it live)
result: pass
source: automated
coverage_id: D5
coverage_source: 47-08-SUMMARY.md
verified_by: integration: tests/test_examples_basic.py (15 tests, all pass); examples/advanced/conf.py read directly -- target 'advanced-example.typ' != docname 'index'

### 38. [47-08 D6] The full-corpus gate (tests/test_corpus_gate.py) still compiles its master and its assertion still names the same PDF path (sphinx-corpus.pdf)
expected: The full-corpus gate (tests/test_corpus_gate.py) still compiles its master and its assertion still names the same PDF path (sphinx-corpus.pdf)
result: pass
source: automated
coverage_id: D6
coverage_source: 47-08-SUMMARY.md
verified_by: integration: tests/test_corpus_gate.py (4 passed, 1 skipped -- the skip is a pre-existing network/cache-dependent gate, unaffected by this plan)

### 39. [47-09 D1] TypstBuilder._collision_key() folds case (casefold()) and path separators (\\ -> /) on both sides, on every platform, with no Unicode normalization
expected: TypstBuilder._collision_key() folds case (casefold()) and path separators (\\ -> /) on both sides, on every platform, with no Unicode normalization
result: pass
source: automated
coverage_id: D1
coverage_source: 47-09-SUMMARY.md
verified_by: unit: tests/test_collision_validator_gate.py::TestCollisionKeyUnit::test_collision_key_folds_case_but_not_unicode_normalization

### 40. [47-09 D2] A wrapper target resolving onto its own content file's path, another document's content path, or the reserved _template.typ raises a single pre-write ExtensionError naming the collision, with NO output file written
expected: A wrapper target resolving onto its own content file's path, another document's content path, or the reserved _template.typ raises a single pre-write ExtensionError naming the collision, with NO output file written
result: pass
source: automated
coverage_id: D2
coverage_source: 47-09-SUMMARY.md
verified_by: integration: tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld03_self_collision_rejected_typst | integration: tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld03_self_collision_rejected_typstpdf

### 41. [47-09 D3] Two typst_documents entries resolving to the same target raise a single ExtensionError naming both entries, with NO output file written
expected: Two typst_documents entries resolving to the same target raise a single ExtensionError naming both entries, with NO output file written
result: pass
source: automated
coverage_id: D3
coverage_source: 47-09-SUMMARY.md
verified_by: integration: tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld02_duplicate_target_rejected_typst | integration: tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld02_duplicate_target_rejected_typstpdf

### 42. [47-09 D4] Two typst_documents entries naming the SAME docname with DIFFERENT targets are permitted and produce two independent wrapper files, each carrying its own entry's title/author (D-04 write-path fix)
expected: Two typst_documents entries naming the SAME docname with DIFFERENT targets are permitted and produce two independent wrapper files, each carrying its own entry's title/author (D-04 write-path fix)
result: pass
source: automated
coverage_id: D4
coverage_source: 47-09-SUMMARY.md
verified_by: integration: tests/test_document_metadata_render_gate.py::TestEntryTitleAuthorRenderGate::test_repeated_docname_wrapper_reads_its_own_entry_title_not_first_match

### 43. [47-09 D5] The CR-01 gate's five methods invert wholesale to assert build failure (non-zero exit, ExtensionError, output-path-collision substring) instead of exit 0 plus a warning, on both -b typst and -b typstpdf
expected: The CR-01 gate's five methods invert wholesale to assert build failure (non-zero exit, ExtensionError, output-path-collision substring) instead of exit 0 plus a warning, on both -b typst and -b typstpdf
result: pass
source: automated
coverage_id: D5
coverage_source: 47-09-SUMMARY.md
verified_by: integration: tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate (5 methods)

### 44. [47-09 D6] The full test suite is green: 1027 passed, 5 skipped, 0 failed; black --check and mypy both green; both dogfooding builds (docs-html, docs-pdf) succeed
expected: The full test suite is green: 1027 passed, 5 skipped, 0 failed; black --check and mypy both green; both dogfooding builds (docs-html, docs-pdf) succeed
result: pass
source: automated
coverage_id: D6
coverage_source: 47-09-SUMMARY.md
verified_by: other: uv run pytest -q (1027 passed, 5 skipped, 204.73s); uv run black --check .; uv run mypy typsphinx/; uv run tox -e docs-html; uv run tox -e docs-pdf

### 45. [47-10 D1] gsd/v0.8.0-multi-master-composition pushed to origin with upstream tracking, no pull request opened
expected: gsd/v0.8.0-multi-master-composition pushed to origin with upstream tracking, no pull request opened
result: pass
source: automated
coverage_id: D1
coverage_source: 47-10-SUMMARY.md
verified_by: other: git ls-remote --heads origin gsd/v0.8.0-multi-master-composition (verbatim output recorded in 47-CI-EVIDENCE.md, local/remote SHA match); gh pr list --head gsd/v0.8.0-multi-master-composition (empty)

### 46. [47-10 D2] A completed CI run over the branch includes both windows-latest and macos-latest lanes, both green
expected: A completed CI run over the branch includes both windows-latest and macos-latest lanes, both green
result: pass
source: automated
coverage_id: D2
coverage_source: 47-10-SUMMARY.md
verified_by: other: gh run view 31492380799 --json conclusion,status,jobs (conclusion: success, all 12 jobs success, including Test Python 3.12/3.13 on windows-latest and macos-latest)

### 47. [47-10 D3] BLD-04's case-collision comparison and OUT-02's drive-qualified escape shape are proven to have EXECUTED (not skipped) and PASSED on both non-Linux lanes
expected: BLD-04's case-collision comparison and OUT-02's drive-qualified escape shape are proven to have EXECUTED (not skipped) and PASSED on both non-Linux lanes
result: pass
source: automated
coverage_id: D3
coverage_source: 47-10-SUMMARY.md
verified_by: integration: quoted PASSED log lines for test_bld04_case_collision_rejected_typst/_typstpdf, test_collision_key_folds_case_but_not_unicode_normalization, and test_escape_shape_refused_with_containment_proof[drive] on both windows-latest and macos-latest (job 93781726864, 93781726893), recorded verbatim in 47-CI-EVIDENCE.md

### 48. [47-10 D4] A real Windows-only OUT-02 defect (os.path vs posixpath disagreement on absolute-path/basename semantics) found by CI, fixed in typsphinx/builder.py, and re-verified green on both Windows Python versions
expected: A real Windows-only OUT-02 defect (os.path vs posixpath disagreement on absolute-path/basename semantics) found by CI, fixed in typsphinx/builder.py, and re-verified green on both Windows Python versions
result: pass
source: automated
coverage_id: D4
coverage_source: 47-10-SUMMARY.md
verified_by: unit: tests/test_builder_output_stem.py::test_resolve_output_stem_guards_absolute_target; tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[absolute] -- both PASSED on windows-latest in run 31492380799

### 49. [47-10 D5] 47-CI-EVIDENCE.md maps every one of ROADMAP Phase 47's five success criteria (SC#1-SC#5) to a named artifact or command, including a live re-measurement of SC#1's two-layer file set and a repo-wide grep confirming _is_master_document is gone
expected: 47-CI-EVIDENCE.md maps every one of ROADMAP Phase 47's five success criteria (SC#1-SC#5) to a named artifact or command, including a live re-measurement of SC#1's two-layer file set and a repo-wide grep confirming _is_master_document is gone
result: pass
source: automated
coverage_id: D5
coverage_source: 47-10-SUMMARY.md
verified_by: other: uv run python -c \"...47-CI-EVIDENCE.md marker check...\" (SC#1..SC#5, windows-latest, macos-latest, ls-remote all present) -- exits 0

### 50. [47-10 D6] 47-VALIDATION.md's two Manual-Only Verifications rows are both marked discharged with the run id, and its Validation Sign-Off checklist grants full phase-level approval
expected: 47-VALIDATION.md's two Manual-Only Verifications rows are both marked discharged with the run id, and its Validation Sign-Off checklist grants full phase-level approval
result: pass
source: automated
coverage_id: D6
coverage_source: 47-10-SUMMARY.md
verified_by: other: 47-VALIDATION.md Manual-Only Verifications table (both rows DISCHARGED) and Validation Sign-Off Approval line (granted)

### 51. [47-11 D1] Two typst_documents targets differing only in path shape (./manual.typ vs manual.typ) now collide with a pre-write ExtensionError naming both entries, and no .typ file is written
expected: Two typst_documents targets differing only in path shape (./manual.typ vs manual.typ) now collide with a pre-write ExtensionError naming both entries, and no .typ file is written
result: pass
source: automated
coverage_id: D1
coverage_source: 47-11-SUMMARY.md
verified_by: unit: tests/test_collision_predicate_completeness_gate.py::TestBld02PathShapeCollisionGate::test_bld02_path_shape_duplicate_rejected_typst | unit: tests/test_collision_predicate_completeness_gate.py::TestBld02PathShapeCollisionGate::test_bld02_path_shape_duplicate_rejected_typstpdf

### 52. [47-11 D2] A ./-prefixed target that normalizes onto the reserved _template.typ infrastructure file is reported as a collision instead of silently overwriting the template
expected: A ./-prefixed target that normalizes onto the reserved _template.typ infrastructure file is reported as a collision instead of silently overwriting the template
result: pass
source: automated
coverage_id: D2
coverage_source: 47-11-SUMMARY.md
verified_by: unit: tests/test_collision_predicate_completeness_gate.py::TestBld02TemplateClobberGate::test_bld02_dot_slash_template_clobber_rejected_typst | unit: tests/test_collision_predicate_completeness_gate.py::TestBld02TemplateClobberGate::test_bld02_dot_slash_template_clobber_rejected_typstpdf

### 53. [47-11 D3] _collision_key() folds path shape via posixpath.normpath() while still folding case and NOT folding Unicode normalization, and never collapses a leading parent-traversal segment
expected: _collision_key() folds path shape via posixpath.normpath() while still folding case and NOT folding Unicode normalization, and never collapses a leading parent-traversal segment
result: pass
source: automated
coverage_id: D3
coverage_source: 47-11-SUMMARY.md
verified_by: unit: tests/test_collision_predicate_completeness_gate.py::TestCollisionKeyPathShapeUnit (4 tests)

### 54. [47-11 D4] A typst_documents entry with fewer than two elements produces NO wrapper file -- the docname's own content survives intact, a warning names the skipped entry under -b typst, and -b typstpdf reports it in finish()'s aggregate ExtensionError while the well-formed sibling master still gets its PDF
expected: A typst_documents entry with fewer than two elements produces NO wrapper file -- the docname's own content survives intact, a warning names the skipped entry under -b typst, and -b typstpdf reports it in finish()'s aggregate ExtensionError while the well-formed sibling master still gets its PDF
result: pass
source: automated
coverage_id: D4
coverage_source: 47-11-SUMMARY.md
verified_by: unit: tests/test_collision_predicate_completeness_gate.py::TestBld03UnderLengthEntryGate (3 tests) | unit: tests/test_collision_predicate_completeness_gate.py::TestIsUsableTypstDocumentsEntryUnit::test_is_usable_typst_documents_entry_predicate

### 55. [47-11 D5] _is_usable_typst_documents_entry() is the single predicate consulted by all four wrapper-path-resolving sites (collision validator, D-07 wrapper report, write-phase wrapper loop, TypstPDFBuilder.finish())
expected: _is_usable_typst_documents_entry() is the single predicate consulted by all four wrapper-path-resolving sites (collision validator, D-07 wrapper report, write-phase wrapper loop, TypstPDFBuilder.finish())
result: pass
source: automated
coverage_id: D5
coverage_source: 47-11-SUMMARY.md
verified_by: unit: grep -c _is_usable_typst_documents_entry typsphinx/builder.py -> 13 (1 definition + docstring mentions + 4 call sites)

### 56. [47-11 D6] Full suite, black, and mypy all green; existing OUT-02/D-04/D-05/WR-01/BLD-01 regression modules pass unmodified
expected: Full suite, black, and mypy all green; existing OUT-02/D-04/D-05/WR-01/BLD-01 regression modules pass unmodified
result: pass
source: automated
coverage_id: D6
coverage_source: 47-11-SUMMARY.md
verified_by: unit: uv run pytest -q -> 1038 passed, 5 skipped, 0 xfailed | other: uv run black --check . && uv run mypy typsphinx/

### 57. [47-12 D1] The superseded docname-first-match entry resolver (_resolve_entry_element) is deleted from typsphinx/writer.py; render_wrapper()'s _entry_element_value() is the sole production entry-element resolution route
expected: The superseded docname-first-match entry resolver (_resolve_entry_element) is deleted from typsphinx/writer.py; render_wrapper()'s _entry_element_value() is the sole production entry-element resolution route
result: pass
source: automated
coverage_id: D1
coverage_source: 47-12-SUMMARY.md
verified_by: unit: grep -rc '_resolve_entry_element' typsphinx/ (0 matches, all files) | unit: python -c \"import typsphinx.writer as w; hasattr(w, '_resolve_entry_element')\" -> False

### 58. [47-12 D2] Every entry-element semantic that survives D-08 is retargeted onto _entry_element_value() in tests/test_entry_metadata_precedence.py; the four D-08-rejected assertions are deleted with rationale recorded in the module docstring
expected: Every entry-element semantic that survives D-08 is retargeted onto _entry_element_value() in tests/test_entry_metadata_precedence.py; the four D-08-rejected assertions are deleted with rationale recorded in the module docstring
result: pass
source: automated
coverage_id: D2
coverage_source: 47-12-SUMMARY.md
verified_by: unit: tests/test_entry_metadata_precedence.py (23 collected, 27 pre-task minus 4 deletions)

### 59. [47-12 D3] No tracked docstring/comment/test prose still presents the deleted resolver as live code (writer.py, both test modules, and the entry_title_author_render_gate fixture)
expected: No tracked docstring/comment/test prose still presents the deleted resolver as live code (writer.py, both test modules, and the entry_title_author_render_gate fixture)
result: pass
source: automated
coverage_id: D3
coverage_source: 47-12-SUMMARY.md
verified_by: unit: manual grep review of all 4 modified prose sites; historical references now name 47-12-PLAN.md as the removal point

### 60. [47-12 D4] .planning/REQUIREMENTS.md's six genuinely-satisfied checkboxes (COMP-01..04, OUT-01, OUT-03) flip to [x] with matching phase-mapping rows; BLD-02/BLD-03 stay [ ]/Pending
expected: .planning/REQUIREMENTS.md's six genuinely-satisfied checkboxes (COMP-01..04, OUT-01, OUT-03) flip to [x] with matching phase-mapping rows; BLD-02/BLD-03 stay [ ]/Pending
result: pass
source: automated
coverage_id: D4
coverage_source: 47-12-SUMMARY.md
verified_by: unit: grep acceptance criteria (Task 2 <acceptance_criteria>) — all 5 checks pass

### 61. [47-12 D5] Full suite, black --check, ruff check, and mypy typsphinx/ all green (binding constraint #8)
expected: Full suite, black --check, ruff check, and mypy typsphinx/ all green (binding constraint #8)
result: pass
source: automated
coverage_id: D5
coverage_source: 47-12-SUMMARY.md
verified_by: unit: uv run pytest -q -> 1023 passed, 5 skipped; uv run black --check . -> clean; nix-shell -p ruff --run 'ruff check .' -> All checks passed; uv run mypy typsphinx/ -> Success

### 62. [47-13 D1] An under-length typst_documents entry (e.g. (\"ghost\",)) contributes NO docname and NO toctree subtree to master_included_docnames, so a real master's :ref: into that subtree degrades to plain text under -b typst instead of emitting a link() that no compiled document contains, and -b typstpdf never reaches the 'label does not exist' compile fatal while the well-formed sibling master's PDF is still produced
expected: An under-length typst_documents entry (e.g. (\"ghost\",)) contributes NO docname and NO toctree subtree to master_included_docnames, so a real master's :ref: into that subtree degrades to plain text under -b typst instead of emitting a link() that no compiled document contains, and -b typstpdf never reaches the 'label does not exist' compile fatal while the well-formed sibling master's PDF is still produced
result: pass
source: automated
coverage_id: D1
coverage_source: 47-13-SUMMARY.md
verified_by: unit: tests/test_master_include_set_predicate_gate.py::TestGhostEntryXrefRenderGate::test_ghost_entry_subtree_xref_degrades_typst | unit: tests/test_master_include_set_predicate_gate.py::TestGhostEntryXrefRenderGate::test_ghost_entry_no_dangling_label_typstpdf | unit: tests/test_master_include_set_predicate_gate.py::TestGhostEntryIncludeSetUnit::test_ghost_entry_excluded_from_master_include_set

### 63. [47-13 D2] A typst_documents entry whose first element is non-hashable (e.g. a list) is rejected before it reaches the include-set BFS's set operations, so -b typst skips it with the existing 'produces no wrapper file' warning and exits 0 instead of an uncaught TypeError traceback, and -b typstpdf reports it through finish()'s existing non-str-docname failure branch
expected: A typst_documents entry whose first element is non-hashable (e.g. a list) is rejected before it reaches the include-set BFS's set operations, so -b typst skips it with the existing 'produces no wrapper file' warning and exits 0 instead of an uncaught TypeError traceback, and -b typstpdf reports it through finish()'s existing non-str-docname failure branch
result: pass
source: automated
coverage_id: D2
coverage_source: 47-13-SUMMARY.md
verified_by: unit: tests/test_master_include_set_predicate_gate.py::TestUnhashableDocnameRenderGate::test_unhashable_docname_skipped_gracefully_typst | unit: tests/test_master_include_set_predicate_gate.py::TestUnhashableDocnameRenderGate::test_unhashable_docname_reported_by_finish_typstpdf | unit: tests/test_master_include_set_predicate_gate.py::TestUnhashableDocnameIncludeSetUnit::test_compute_master_included_docnames_tolerates_unhashable_docname

### 64. [47-13 D3] _is_usable_typst_documents_entry() is now consulted at all FIVE sites needing the entry-usability answer, including _compute_master_included_docnames() -- its docstring's own consumer enumeration matches the wired reality
expected: _is_usable_typst_documents_entry() is now consulted at all FIVE sites needing the entry-usability answer, including _compute_master_included_docnames() -- its docstring's own consumer enumeration matches the wired reality
result: pass
source: automated
coverage_id: D3
coverage_source: 47-13-SUMMARY.md
verified_by: unit: uv run python -c \"...print('FIVE' in d, '_compute_master_included_docnames' in d)\" -> True True | unit: uv run python -c \"...print('_is_usable_typst_documents_entry' in s)\" -> True

### 65. [47-13 D4] Well-formed masters still yield their full toctree closure and an empty/None typst_documents still yields an empty include set -- the new filter does not over-reject any currently-working configuration
expected: Well-formed masters still yield their full toctree closure and an empty/None typst_documents still yields an empty include set -- the new filter does not over-reject any currently-working configuration
result: pass
source: automated
coverage_id: D4
coverage_source: 47-13-SUMMARY.md
verified_by: unit: tests/test_master_include_set_predicate_gate.py::TestMasterIncludeSetInvarianceGuards (2 tests)

### 66. [47-13 D5] Full suite, black, and mypy all green; the four already-wired sites' regression gates and the existing degrade/citation gates pass with their source unmodified
expected: Full suite, black, and mypy all green; the four already-wired sites' regression gates and the existing degrade/citation gates pass with their source unmodified
result: pass
source: automated
coverage_id: D5
coverage_source: 47-13-SUMMARY.md
verified_by: unit: uv run pytest -q -> 1042 passed, 5 skipped, 0 xfailed | other: uv run black --check . && uv run mypy typsphinx/

### 67. [47-14 D1] The superseded docname-first-match output-stem resolver (_resolve_output_stem) is deleted from typsphinx/builder.py; _resolve_target_stem()/_wrapper_output_relpath() are the sole production output-path resolution routes
expected: The superseded docname-first-match output-stem resolver (_resolve_output_stem) is deleted from typsphinx/builder.py; _resolve_target_stem()/_wrapper_output_relpath() are the sole production output-path resolution routes
result: pass
source: automated
coverage_id: D1
coverage_source: 47-14-SUMMARY.md
verified_by: unit: git grep -c '_resolve_output_stem' -- 'typsphinx/' (0 matches) | unit: uv run python -c \"from typsphinx.builder import TypstBuilder; print(hasattr(TypstBuilder, '_resolve_output_stem'))\" -> False

### 68. [47-14 D2] Every semantic that survives the deletion is retargeted onto _resolve_target_stem()/_wrapper_output_relpath() in tests/test_builder_output_stem.py with expected values verbatim; the three dead semantics are deleted with rationale recorded in the module docstring
expected: Every semantic that survives the deletion is retargeted onto _resolve_target_stem()/_wrapper_output_relpath() in tests/test_builder_output_stem.py with expected values verbatim; the three dead semantics are deleted with rationale recorded in the module docstring
result: pass
source: automated
coverage_id: D2
coverage_source: 47-14-SUMMARY.md
verified_by: unit: tests/test_builder_output_stem.py --collect-only -> 25 collected (28 before, 3 deleted); grep -c 'def test_resolve_target_stem' -> 21; grep -c 'def test_wrapper_output_relpath_accepts_five_element_tuple' -> 1 | unit: grep -c '\"v1.2-manual\"' -> 3 (>= 3 required); grep -c 'マニュアル' -> 2 (>= 2 required) -- expected values carried over verbatim | unit: grep -cE 'def test_resolve_target_stem_guards_(parent_traversal|absolute_target|drive_qualified_target)' -> 3, all expecting \"manual\"

### 69. [47-14 D3] No tracked docstring/comment/test prose outside .planning/ still presents the deleted resolver as live code; typsphinx/ (production code) carries zero references at all, even historical
expected: No tracked docstring/comment/test prose outside .planning/ still presents the deleted resolver as live code; typsphinx/ (production code) carries zero references at all, even historical
result: pass
source: automated
coverage_id: D3
coverage_source: 47-14-SUMMARY.md
verified_by: unit: git grep -c '_resolve_output_stem' -- 'typsphinx/' -> 0 matches (all 7 surviving docstring/comment sites repaired); git grep -c '_resolve_output_stem' -- ':!.planning' -> 9 matches, all in tests/ or tests/fixtures/, all explicitly framed as history naming this plan (47-14) as the removal point -- matching 47-12's own verified precedent that historical mentions survive only in test files, never in typsphinx/ itself

### 70. [47-14 D4] AST-level diff over builder.py's surviving methods proves only the deleted method's body and prose (docstrings/comments) changed -- no other executable line was touched
expected: AST-level diff over builder.py's surviving methods proves only the deleted method's body and prose (docstrings/comments) changed -- no other executable line was touched
result: pass
source: automated
coverage_id: D4
coverage_source: 47-14-SUMMARY.md
verified_by: unit: ast.dump() comparison (docstring node stripped) of _resolve_target_stem, _escapes_outdir, _is_drive_qualified, _collision_key, _validate_output_path_collisions, _content_output_path, _wrapper_output_relpath, _compute_master_included_docnames against HEAD~1 -- all 8 report UNCHANGED

### 71. [47-14 D5] .planning/REQUIREMENTS.md's BLD-02 checkbox and phase-mapping row flip to [x]/Complete; BLD-03 stays [ ]/Pending; no other requirement ID or text is touched
expected: .planning/REQUIREMENTS.md's BLD-02 checkbox and phase-mapping row flip to [x]/Complete; BLD-03 stays [ ]/Pending; no other requirement ID or text is touched
result: pass
source: automated
coverage_id: D5
coverage_source: 47-14-SUMMARY.md
verified_by: unit: Task 2 <acceptance_criteria> -- all 6 checks pass (BLD-02 checked, BLD-03 unchecked, 8 other IDs undisturbed, both phase-mapping rows correct, diff-shape check returns 0, numstat shows exactly 2+/2-)

### 72. [47-14 D6] Full suite, black --check, mypy typsphinx/, and ruff check (via nix-shell fallback) all green; the five named regression modules pass with zero source diff on the four that must stay unmodified
expected: Full suite, black --check, mypy typsphinx/, and ruff check (via nix-shell fallback) all green; the five named regression modules pass with zero source diff on the four that must stay unmodified
result: pass
source: automated
coverage_id: D6
coverage_source: 47-14-SUMMARY.md
verified_by: unit: uv run pytest -q -> 1039 passed, 5 skipped; uv run black --check . -> clean; uv run mypy typsphinx/ -> Success; nix-shell -p ruff --run 'ruff check .' -> All checks passed (uv-managed ruff is a generic-linux ELF unrunnable on this NixOS checkout, the pre-existing documented limitation)

## Summary

total: 72
passed: 72
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none]
