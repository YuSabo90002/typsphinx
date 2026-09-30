---
phase: 47
slug: two-layer-output-content-wrapper-split-target-as-path-collis
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-11
updated: 2026-08-12
---

# Phase 47 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `47-RESEARCH.md` §"Validation Architecture". The Per-Task Verification Map is
> filled once PLAN.md files exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`); the suite already contains real-subprocess `sphinx-build` gates |
| **Config file** | `pyproject.toml` — no new config needed |
| **Quick run command** | `pytest tests/test_builder_output_stem.py tests/test_two_layer_output_gate.py tests/test_collision_validator_gate.py -x` |
| **Full suite command** | `pytest` (or `tox -e py313`) |
| **Estimated runtime** | **Measured (plan 47-09, wave 4):** `uv run pytest -q` = ~200s (0:03:18–0:03:21 across two runs), 1027 passed / 5 skipped / 0 failed, worktree-provisioned venv, Linux x86_64 |

---

## Sampling Rate

- **After every task commit:** Run the quick run command above
- **After every plan wave:** Run `pytest` in full, plus `black --check .`, `ruff check .`, `mypy typsphinx/`
- **Phase gate (before `/gsd-verify-work`):** Full suite green, plus a real `-b typst` and `-b typstpdf`
  build of the B-1/B-2 fixture and the collision fixtures
- **Max feedback latency:** ~200s (the full-suite `uv run pytest -q` runtime measured above) — every task in every plan of this phase has an `<automated>` command that runs in well under this ceiling (the slowest per-task commands are themselves `uv run pytest -q`, i.e. the full suite, run at wave-close in plans 47-04 through 47-08's Task 3 and 47-09's Task 4)

---

## Per-Task Verification Map

*Filled by plan 47-09 (this phase's full-suite-green gate) once every plan's PLAN.md exists.
Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky. Every row below has an automated command; the
`<automated>` command quoted is copied verbatim from each task's own `<verify>` block.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 47-01/T1 | 47-01 | 1 | COMP-01/02/03/04, OUT-03, BLD-02/03/04 | T-47-02/03/04/14 (planned) | Five fixture projects + `47-EXPECTED-STRUCTURE.md` exist, derived from first principles, no builder run | fixture/artifact | `uv run python -c "...missing fixtures check..."` | yes | ✅ green |
| 47-01/T2 | 47-01 | 1 | COMP-01/02/03/04, OUT-03 | n/a (RED-evidence capture, no production code) | `tests/test_two_layer_output_gate.py` records real pre-fix RED (xfail strict) | integration | `uv run pytest tests/test_two_layer_output_gate.py -q` | yes | ✅ green |
| 47-01/T3 | 47-01 | 1 | BLD-02/03/04 | T-47-02/03/04 (planned) | `tests/test_collision_validator_gate.py` records the three non-fatal collision REDs (xfail strict) | integration | `uv run pytest tests/test_collision_validator_gate.py -q` | yes | ✅ green |
| 47-02/T1 | 47-02 | 2 | COMP-01/02/03/04 | T-47-02 (mitigated by 47-09) | End-to-end content/wrapper split for one root-level master | integration | `uv run pytest tests/test_two_layer_output_gate.py -q` | yes | ✅ green |
| 47-02/T2 | 47-02 | 2 | OUT-01/02 | T-47-08 (drive-qualified escape) | OUT-01 disentangled from OUT-02; wrappers land at resolved target path | integration+unit | `uv run pytest tests/test_two_layer_output_gate.py tests/test_builder_output_stem.py -q` | yes | ✅ green |
| 47-02/T3 | 47-02 | 2 | COMP-01/02 | n/a | Builder parity (`-b typst`/`-b typstpdf` byte-identical), D-07 wrapper log, `_is_master_document` gone repo-wide | integration | `uv run pytest tests/test_two_layer_output_gate.py tests/test_preview_version_sync.py -q` | yes | ✅ green |
| 47-03/T1 | 47-03 | 3 | OUT-01 | n/a | OUT-01 expectations moved in `test_builder_output_stem.py`; OUT-02 guard tests kept verbatim | unit | `uv run pytest tests/test_builder_output_stem.py -q` | yes | ✅ green |
| 47-03/T2 | 47-03 | 3 | OUT-02 | T-47-08 (drive-qualified) | Real-`sphinx-build` gate, one fixture per escape shape, outdir-containment assertion | integration | `uv run pytest tests/test_out02_escape_target_gate.py -q` | yes | ✅ green |
| 47-03/T3 | 47-03 | 3 | OUT-02 | T-47-08 (A3 closure) | RESEARCH.md Assumptions-Log A3 closed by measurement (repo-wide grep for a second path-rejection site) | unit+integration | `uv run pytest tests/test_builder_output_stem.py tests/test_out02_escape_target_gate.py tests/test_two_layer_output_gate.py -q` | yes | ✅ green |
| 47-04/T1 | 47-04 | 3 | COMP-01/02, BLD-03 | n/a (corpus migration, no production code touched) | 6 modules / 21 fixtures migrated to content/wrapper shape, de-collided | integration | `uv run pytest tests/test_pdf_render_gate.py tests/test_admonition_bucket_render_gate.py tests/test_desc_container_propagated_target_render_gate.py tests/test_field_list_in_list_item_render_gate.py tests/test_package_only_config_gate.py tests/test_signature_page_boundary_render_gate.py -q` | yes | ✅ green |
| 47-04/T2 | 47-04 | 3 | COMP-01/02, BLD-03 | n/a | 6 single-fixture render gates migrated | integration | `uv run pytest tests/test_abbr_pep_separator_render_gate.py tests/test_confval_field_body_render_gate.py tests/test_desc_signature_anchor_render_gate.py tests/test_inline_math_after_text_render_gate.py tests/test_preview_smoke_gate.py tests/test_table_in_list_item_render_gate.py -q` | yes | ✅ green |
| 47-04/T3 | 47-04 | 3 | COMP-01/02, BLD-03 | n/a | Toctree and malformed-entry gates migrated (5 modules, 7 fixtures) | integration | `uv run pytest tests/test_changelog_page_gate.py tests/test_deflist_term_concat_render_gate.py tests/test_duplicate_include_label_render_gate.py tests/test_missing_and_malformed_master_gate.py tests/test_rubric_propagated_target_render_gate.py -q` | yes | ✅ green |
| 47-05/T1 | 47-05 | 3 | COMP-01/02, BLD-03 | n/a | Nested-toctree and layout cluster migrated (6 modules, 7 fixtures) | integration | `uv run pytest tests/test_integration_nested_toctree.py tests/test_desc_content_indent_render_gate.py tests/test_figure_propagated_target_render_gate.py tests/test_heading_depth_render_gate.py tests/test_paragraph_concat_render_gate.py tests/test_static_asset_copy_gate.py -q` | yes | ✅ green |
| 47-05/T2 | 47-05 | 3 | COMP-01/02, BLD-03 | n/a | Multi-document and reference cluster migrated (6 modules, 7 fixtures) | integration | `uv run pytest tests/test_integration_multi_doc.py tests/test_absolute_image_render_gate.py tests/test_confval_field_spacing_render_gate.py tests/test_desc_signature_concat_render_gate.py tests/test_ref_target_nested_list_render_gate.py tests/test_target_label_render_gate.py -q` | yes | ✅ green |
| 47-05/T3 | 47-05 | 3 | COMP-01/02, BLD-03 | n/a | Remaining group-B render gates migrated (5 modules, 5 fixtures) | integration | `uv run pytest tests/test_citation_degradation_gate.py tests/test_deflist_term_inline_children_gate.py tests/test_epigraph_render_gate.py tests/test_nested_figure_render_gate.py tests/test_rubric_strong_nesting_render_gate.py -q` | yes | ✅ green |
| 47-06/T1 | 47-06 | 3 | COMP-01/02, BLD-03 | n/a | End-to-end integration and image cluster migrated (6 modules, 6 fixtures) | integration | `uv run pytest tests/test_integration_basic.py tests/test_integration_advanced.py tests/test_glob_image_render_gate.py tests/test_desc_rubric_decoupling_render_gate.py tests/test_paragraph_propagated_target_render_gate.py tests/test_substitution_definition_render_gate.py -q` | yes | ✅ green |
| 47-06/T2 | 47-06 | 3 | COMP-01/02, BLD-03 | n/a | Entry-metadata and typography cluster migrated (6 modules, 7 fixtures); D-04 repeated-docname fixture added | integration | `uv run pytest tests/test_document_metadata_render_gate.py tests/test_admonition_greyscale_pipeline.py tests/test_deflist_definition_multiblock_render_gate.py tests/test_label_at_char_render_gate.py tests/test_rubric_indent_invariance.py tests/test_wide_table_render_gate.py -q` | yes | ✅ green |
| 47-06/T3 | 47-06 | 3 | COMP-01/02, BLD-03 | n/a | Remaining group-C render gates migrated (5 modules, 5 fixtures) | integration | `uv run pytest tests/test_citation_render_gate.py tests/test_desc_bodyless_concat_render_gate.py tests/test_external_link_style_render_gate.py tests/test_nested_table_render_gate.py tests/test_signature_break_and_arrow_gate.py -q` | yes | ✅ green |
| 47-07/T1 | 47-07 | 3 | COMP-01/02, BLD-03 | n/a | Page-count and typography cluster migrated (6 modules, 5 fixtures) | integration | `uv run pytest tests/test_signature_typography_multi_signature_page_count_gate.py tests/test_signature_typography_gate.py tests/test_desc_sig_space_render_gate.py tests/test_inline_literal_overflow_render_gate.py tests/test_paragraph_soft_newline_render_gate.py tests/test_table_empty_caption_anchor_render_gate.py -q` | yes | ✅ green |
| 47-07/T2 | 47-07 | 3 | COMP-01/02, BLD-03 | n/a | Template-contract and propagated-target cluster migrated (6 modules, 6 fixtures) | integration | `uv run pytest tests/test_documented_params_contract_gate.py tests/test_xref_orphan_degrade_render_gate.py tests/test_captioned_table_propagated_target_render_gate.py tests/test_deflist_nested_definition_render_gate.py tests/test_list_item_nested_block_render_gate.py tests/test_rubric_option_concat_render_gate.py -q` | yes | ✅ green |
| 47-07/T3 | 47-07 | 3 | COMP-01/02, BLD-03 | n/a | Remaining group-D gates + malformed-docname gate migrated (5 modules, 5 fixtures) | integration | `uv run pytest tests/test_non_str_docname_gate.py tests/test_codly_caption_listitem_leak_render_gate.py tests/test_desc_break_marker_buffer_swap_gate.py tests/test_field_body_typography_render_gate.py tests/test_signature_overflow_render_gate.py -q` | yes | ✅ green |
| 47-08/T1 | 47-08 | 3 | COMP-01/02, OUT-03, BLD-02/03 | n/a | Template-routing, config-mapping, metadata-route suites migrated (9 modules) | integration | `uv run pytest tests/test_template_import_path.py tests/test_package_template_routing.py tests/test_config_template_mapping.py tests/test_params_exclusivity_gate.py tests/test_typst_elements_pass_through_gate.py tests/test_typst_lang_gate.py tests/test_authors_pipeline_stage_gate.py tests/test_entry_metadata_route_uniformity.py tests/test_entry_metadata_precedence.py -q` | yes | ✅ green |
| 47-08/T2 | 47-08 | 3 | COMP-01/02, OUT-03, BLD-02/03 | n/a | `typst_documents`-shape gates and nested-master fixture migrated (8 modules) | integration | `uv run pytest tests/test_default_typst_documents_gate.py tests/test_empty_typst_documents_optout_gate.py tests/test_nested_master_render_gate.py tests/test_target_name_render_gate.py tests/test_cross_doc_label_namespace_render_gate.py tests/test_multi_master_metadata_no_leak.py tests/test_admonition_locale_title_precedence_gate.py tests/test_pdf_generation.py -q` | yes | ✅ green |
| 47-08/T3 | 47-08 | 3 | COMP-01/02, OUT-03, BLD-02/03 | n/a | Dogfooding builds + corpus gate + shared test root re-proven; 15 additional fixtures de-collided opportunistically | full suite | `uv run pytest -q` | yes | ✅ green |
| 47-09/CP1 | 47-09 | 4 | BLD-02/03/04 | T-47-02/03/04 | D-01 decision checkpoint (locked, pre-resolved by project owner: option-a, hard ExtensionError, no fallback) — realized and proven by 47-09/T3's automated command below | decision, realization tested by the next row | `uv run pytest tests/test_collision_validator_gate.py tests/test_two_layer_output_gate.py -q` | yes (via 47-09/T3) | ✅ green |
| 47-09/CP2 | 47-09 | 4 | BLD-02/03/04 | T-47-02/03/04/14/15 | D-03 decision checkpoint (locked, pre-resolved by project owner: option-a, one validator, error-only, pre-write, aggregate) — realized and proven by 47-09/T3's automated command below | decision, realization tested by the next row | `uv run pytest tests/test_collision_validator_gate.py tests/test_two_layer_output_gate.py -q` | yes (via 47-09/T3) | ✅ green |
| 47-09/T3 | 47-09 | 4 | BLD-02/03/04, COMP-01/02 | T-47-02/03/04/14/15 | `TypstBuilder._validate_output_path_collisions()` + `_collision_key()` implemented; all four collision kinds route through one pre-write validator; D-04 repeated-docname write-path bug fixed | unit+integration | `uv run pytest tests/test_collision_validator_gate.py tests/test_two_layer_output_gate.py -q` | yes | ✅ green |
| 47-09/T4 | 47-09 | 4 | BLD-02/03/04, COMP-01/02 | T-47-02/03/04/14/15 | CR-01 gate inverted (`test_typst_documents_collision_gate.py`), `_resolve_output_stem`/`_wrapper_output_relpath` split moved responsibility to the validator, phase closed green on full suite + lint/type trio + both dogfooding builds | full suite + lint/type + integration | `uv run pytest -q` (plus `uv run black --check .`, `uv run mypy typsphinx/`, `uv run tox -e docs-html`, `uv run tox -e docs-pdf`) | yes | ✅ green |
| 47-10/T1 | 47-10 | 5 | (milestone invariant #5, binding constraint #2) | T-47-16 | Milestone branch pushed to `origin` with upstream tracking, no PR opened | remote/network | `git ls-remote --heads origin gsd/v0.8.0-multi-master-composition \| grep -q refs/heads/gsd/v0.8.0-multi-master-composition` | yes | ✅ green |
| 47-10/T2 | 47-10 | 5 | BLD-04, OUT-02 | T-47-04, T-47-08 | CI run completed with Windows/macOS lanes green; BLD-04 and drive-qualified OUT-02 cases proven to have executed on non-Linux lanes | CI/remote | `gh run list --branch gsd/v0.8.0-multi-master-composition --json conclusion,status --limit 1 \| grep -q '"conclusion":"success"'` | yes | ✅ green (run 31492380799, over `be4c4d5`, after triage-fixing a real Windows-only OUT-02 defect found by run 31491228938) |
| 47-10/T3 | 47-10 | 5 | (SC#1-SC#5 evidence mapping) | T-47-16 | `47-CI-EVIDENCE.md` records run id, SHAs, per-lane conclusions, SC#1-SC#5 evidence mapping; Manual-Only Verifications and Validation Sign-Off ticked | artifact + full suite | `uv run python -c "...47-CI-EVIDENCE.md marker check..."` (plus `uv run pytest -q`) | yes | ✅ green |

Rows for plan 47-10 (wave 5) were recorded on schedule at 47-09 close, before wave 5 executed,
per that task's own instruction ("one row per task across all ten plans") — their Automated
Command and expected Secure Behavior were transcribed verbatim from `47-10-PLAN.md`'s own
`<verify>` blocks, with Status honestly marked `⬜ pending` at that time rather than backfilled.
**Updated here by 47-10/T3 itself, now that wave 5 has executed**: all three rows measured green.
Run 31491228938 (over `6f8a23c`) surfaced two real defects — the Windows-only OUT-02
platform-dependent-`os.path` guard and four pre-existing ruff findings — triaged, fixed, and
pushed as `be4c4d5`; the re-dispatched run 31492380799 (over `be4c4d5`) completed with all 12
jobs green, including both `windows-latest` and `macos-latest` lanes. Full detail, quoted log
lines, and the SC#1–SC#5 evidence mapping live in `47-CI-EVIDENCE.md`.

### Requirement → evidence contract (from RESEARCH.md, binding constraint #4)

| Req ID | Evidence that proves it | Pre-fix RED required? | RED shape |
|--------|-------------------------|------------------------|-----------|
| COMP-01 | Real `sphinx-build` subprocess; emitted `.typ` structural assertion | Yes | Content file has NO `#show: project.with(` and no template import |
| COMP-02 | Real `sphinx-build` subprocess; path assertion | Yes | Wrapper exists at the target-derived path (pre-fix: today's single-file shape) |
| COMP-03 | Real `sphinx-build` + real `typst.compile()` | Yes | **Classic `TypstError`** — `file not found (searched at .../guide/index.typ)`, measured this session |
| COMP-04 | Real `typst.compile()` + `pypdf` text extraction | Yes | **Structural `pypdf` assertion, NOT `TypstError`** — B-2 was measured as compiles-fine-but-wrong-output: a second title-page-shaped block and a second `"Contents"` heading appear before the nested content's body marker |
| OUT-01 | Unit (`_resolve_output_stem`) + real `sphinx-build` | No — behavior change, existing expectations move | n/a |
| OUT-02 | Unit + integration, one fixture per escape shape | No — preserved behavior; regression test proves it survives the OUT-01 rewrite | n/a |
| OUT-03 | Real `sphinx-build`; structural invariant | No | n/a |
| BLD-02 | Real `sphinx-build` subprocess; marker-string presence in emitted `.typ` | Yes | **Structural** — exit 0, the surviving file contains only one master's marker, no collision warning anywhere in stdout/stderr |
| BLD-03 | Real `sphinx-build` subprocess | Yes | **Structural** — `[("index","index.typ",…)]` exits 0 with no warning today |
| BLD-04 | Unit assertion on the comparison function + Windows/macOS CI lanes | Yes | **Structural, at the unit level** — the comparison does not `casefold()`. The physical collision is unobservable on Linux, so the fixture must assert the comparison itself folds case |

---

## Wave 0 Requirements

- [x] `tests/test_two_layer_output_gate.py` — new module; COMP-01, COMP-02, COMP-03, COMP-04, OUT-03
      (written by 47-01, made to pass by 47-02, still green after 47-09)
- [x] `tests/test_collision_validator_gate.py` — new module; BLD-02, BLD-03, BLD-04, each with its own
      pre-fix RED per binding constraint #4 (written by 47-01, made to pass by 47-09/T3, `xfail`
      markers removed)
- [x] `tests/test_builder_output_stem.py` — existing; OUT-01 expectations moved (47-03), the three
      OUT-02 escape cases stay as regression tests, and the two CR-01 fallback assertions moved to
      `test_resolve_output_stem_no_longer_falls_back_on_*` (resolver, unchanged-stem) plus
      `test_validate_output_path_collisions_raises_on_*` (validator, `ExtensionError`) per D-03
      replacing CR-01 (47-09/T4)
- [x] `tests/test_typst_documents_collision_gate.py` — existing; every one of its five methods now
      asserts `returncode != 0` plus an `ExtensionError`/`output path collision` substring, replacing
      the old `returncode == 0` + warning-substring contract (47-09/T4). The module's assertions
      inverted
- [x] `tests/test_preview_version_sync.py` — re-run and green throughout (unaffected — content files
      carry the D-06 preamble unconditionally as designed)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions | Status |
|----------|-------------|------------|-------------------|--------|
| Branch is on `origin` with a completed CI run over the Windows and macOS lanes | Milestone invariant #5 / binding constraint #2 | Requires a real push and a real GitHub Actions run — not reproducible in-process | `git push -u origin gsd/v0.8.0-multi-master-composition`, then `git ls-remote --heads origin` must hit, and `gh run list --branch gsd/v0.8.0-multi-master-composition` must show a completed run including the Windows and macOS lanes | **DISCHARGED** — 47-10/T1 pushed the branch (`git ls-remote` hit, verbatim output in `47-CI-EVIDENCE.md` "Branch on origin"); 47-10/T2 drove CI run `31492380799` to completion, `conclusion: success`, both `windows-latest` and `macos-latest` jobs green (both Python versions) |
| BLD-04's physical collision consequence on a case-insensitive filesystem | BLD-04 | Linux CI cannot observe a case-insensitive overwrite; only the Windows/macOS lanes can | Confirm the Windows and macOS CI lanes run the `test_collision_validator_gate.py` BLD-04 case | **DISCHARGED** — `test_bld04_case_collision_rejected_typst`/`_typstpdf` and `test_collision_key_folds_case_but_not_unicode_normalization` all logged `PASSED` (not skipped) on both `windows-latest` and `macos-latest` in run `31492380799`; quoted log lines in `47-CI-EVIDENCE.md` "Completed CI run" |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — every row in the Per-Task
      Verification Map above carries a real automated command
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — every task has one
- [x] Wave 0 covers all MISSING references — the five Wave 0 Requirements above are all `[x]`
- [x] No watch-mode flags — no automated command in this phase uses `--watch`/`-f`/equivalent
- [x] Feedback latency measured at Wave 0 and recorded above (~200s, see Sampling Rate)
- [x] `nyquist_compliant: true` set in frontmatter

**Both Manual-Only Verifications rows above are now DISCHARGED**, ticked by 47-10/T3 against the
measured CI evidence recorded in `47-CI-EVIDENCE.md`: the branch is on `origin`
(`git ls-remote --heads origin gsd/v0.8.0-multi-master-composition` hit, verbatim output recorded)
and a completed CI run (`31492380799`, `conclusion: success`) covers both the `windows-latest` and
`macos-latest` lanes, with the BLD-04 case-collision comparison and all three OUT-02 escape shapes
— including the drive-qualified case — proven via quoted PASSED log lines to have EXECUTED (not
skipped) on both.

**Approval:** granted — full phase-level Nyquist validation is now complete. Every row in the
Per-Task Verification Map is `✅ green`, both Manual-Only Verifications rows are discharged, and
every ROADMAP Phase 47 success criterion (SC#1 through SC#5) is mapped to a named artifact or a
command run live, per `47-CI-EVIDENCE.md`'s "ROADMAP Phase 47 success criteria — evidence mapping"
section.
