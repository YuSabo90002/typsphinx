---
phase: 22-typstpdf-target-name-pdf-fix-issue-117
plan: 01
subsystem: infra
tags: [sphinx-builder, typst, pdf-naming, issue-117]

# Dependency graph
requires: []
provides:
  - "TypstBuilder._resolve_output_stem(docname) -- the single source of the typst_documents target-name normalization rule"
  - "TypstBuilder._directory_preserving_relpath(docname, stem) -- keeps a nested docname's output inside its own directory"
  - "All three output-path sites (TypstBuilder.write_doc, TypstPDFBuilder.write_doc, TypstPDFBuilder.finish) wired to the shared stem resolution"
affects: [22.1-typstpdf-compile-root-alignment]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Guarded normalization: resolve once in a private helper, warn-and-degrade on unsafe input, never re-derive the rule at each call site (mirrors _compute_master_included_docnames' getattr/or-[]/if-entry idiom)"

key-files:
  created:
    - tests/test_builder_output_stem.py
  modified:
    - typsphinx/builder.py

key-decisions:
  - "A typst_documents tuple shorter than 2 elements is treated as 'no entry matched' (silent docname fallback, D-02 path) rather than routed through the degenerate-target warning path -- this follows the <action> section's explicit resolution-order algorithm (step 1's length>=2 selection filter, step 2's 'no-entry case is SILENT') over the looser prose grouping in the <behavior> section's bullet list. The short-tuple unit test only asserts the return value, not warning presence, so both readings satisfy the plan's test suite; the implementation follows the more specific algorithmic spec."

requirements-completed: [PDF-01]

coverage:
  - id: D1
    description: "TypstBuilder._resolve_output_stem implements the full D-02/D-03/D-04/D-06/D-07 normalization rule plus the empty/encoding edge cases"
    requirement: "PDF-01"
    verification:
      - kind: unit
        ref: "tests/test_builder_output_stem.py (21 test functions)"
        status: pass
    human_judgment: false
  - id: D2
    description: "All three output-path sites (write_doc x2, finish) derive their filename from the resolved stem, so the compiled PDF is named after the typst_documents target instead of the source docname"
    requirement: "PDF-01"
    verification:
      - kind: unit
        ref: "tests/test_builder.py, tests/test_builder_requirement13.py, tests/test_config_template_mapping.py, tests/test_config_toctree_defaults.py, tests/test_pdf_generation.py"
        status: pass
      - kind: manual_procedural
        ref: "real sphinx-build -b typstpdf smoke run: typst_documents=[('index','manual.typ',...)] emits build/manual.typ + build/manual.pdf; typst_documents=[('index','index',...)] still emits build/index.typ + build/index.pdf"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-07-21
status: complete
---

# Phase 22 Plan 01: typstpdf Target-Name Normalization Summary

**A single guarded `TypstBuilder._resolve_output_stem()` helper now governs all three `.typ`/`.pdf` output-path sites, so `typst_documents = [('index', 'manual.typ', ...)]` finally emits `manual.typ`/`manual.pdf` instead of `index.typ`/`index.pdf` (Issue #117).**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-07-21T13:42:36Z
- **Tasks:** 2
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments
- `TypstBuilder._resolve_output_stem(docname)` implements the whole normalization contract in one place: D-03/D-04 suffix stripping without truncating period-bearing stems (no `os.path.splitext`), D-02 silent docname fallback for non-master documents, D-06/D-07 path/traversal/absolute/drive-letter guard (basename fallback + one warning), and an `edge: empty` degenerate-target guard (empty/whitespace/non-str target → docname fallback + one warning) with verbatim non-ASCII passthrough (`edge: encoding`)
- All three write/read-back sites — `TypstBuilder.write_doc`, `TypstPDFBuilder.write_doc`, `TypstPDFBuilder.finish` — call the same helper; `finish()` resolves the stem exactly once per `doc_tuple` so the `.typ` read-back path and the `.pdf` write path can never drift from each other
- New `_directory_preserving_relpath()` helper keeps a nested master's renamed output inside its own directory (`('sub/index', 'manual.typ', ...)` → `outdir/sub/manual.typ`, not `outdir/manual.typ`) without double-prepending the directory for the common "no rename" case
- `get_target_uri` is functionally byte-identical (still `docname + self.out_suffix`) with a new docstring paragraph explaining why it must stay docname-based (its only consumer, `translator.py:_resolve_xref_docname`, is a round-trip identity keyed to `_namespace_label`'s source-docname label namespace)
- Real `sphinx-build -b typstpdf` smoke run confirms both the fix (`manual.typ`/`manual.pdf`) and the identity-mapping non-regression (`index.typ`/`index.pdf` unchanged) in an actual compiled build, not just unit assertions

## Task Commits

Each task was committed atomically (Task 1 used TDD RED→GREEN):

1. **Task 1: Add TypstBuilder._resolve_output_stem** - `5e97440` (test — RED), `4ca3f76` (feat — GREEN)
2. **Task 2: Wire the three output-path sites to _resolve_output_stem** - `0d4d26c` (fix)

_No plan-metadata commit in worktree mode — SUMMARY.md is committed separately per the parallel-executor protocol; the orchestrator handles STATE.md/ROADMAP.md centrally after the wave merges._

## Files Created/Modified
- `typsphinx/builder.py` - added `_resolve_output_stem`, `_directory_preserving_relpath`; rewired `TypstBuilder.write_doc`, `TypstPDFBuilder.write_doc`, `TypstPDFBuilder.finish` to use them; documented `get_target_uri`'s deliberate docname-based identity
- `tests/test_builder_output_stem.py` - new module, 21 plain `def test_*` functions (no `@pytest.mark.parametrize`), one per normalization rule / edge case, following `tests/test_builder.py`'s house style

## Decisions Made
- The short-tuple degenerate case (`[("index",)]`) is treated as "no entry matched" → silent docname fallback, per the plan's `<action>` resolution-order algorithm (step 1 requires `len(entry) >= 2` to even select the entry; step 2 declares the no-entry case SILENT). This reads as the authoritative operational spec over a looser prose sentence elsewhere in the plan that groups the short-tuple case together with the other degenerate cases as "warns." The unit test for this case (`test_resolve_output_stem_falls_back_on_short_tuple`) only asserts the return value, so both readings pass; the implementation follows the more specific, unambiguous algorithm.
- Drive-qualified fallback (`"C:manual.typ"` → `"manual"`) required stripping the 2-character drive prefix before calling `path.basename`, since POSIX `path.basename` only splits on `/` and would otherwise return `"C:manual"` unchanged (no `:`-awareness on POSIX). Implemented as `fallback_source = stem[2:] if is_drive_qualified else stem` before the basename call.

## Deviations from Plan

None - plan executed exactly as written. (The short-tuple interpretation above is a specification-ambiguity resolution, not a code deviation — both textual variants of the spec are satisfied by the test suite as written.)

## Issues Encountered

None. Local environment is a NixOS sandbox where `uv run <compiled-binary>` fails (documented pre-existing project condition); black/mypy ran fine via `uv run`, ruff via `nix-shell -p ruff --run "ruff check ..."`, and the 45 subprocess-based integration tests in `tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py` + `tests/test_examples_basic.py` fail environmentally (pre-existing, unrelated to this change) — confirmed the failure count and files match the documented baseline exactly, and all 457 other fast-suite tests (plus this plan's own 21) pass.

## Next Phase Readiness
- Issue #117's PDF-naming bug is fixed and proven both by unit tests and a real compiled build; `PDF-01` is complete
- Phase 22.1 (typstpdf compile-root alignment for nested masters, PDF-02) can proceed independently — it touches the `include()`/`image()` root-resolution path, not the filename-derivation path this plan changed
- No blockers

---
*Phase: 22-typstpdf-target-name-pdf-fix-issue-117*
*Completed: 2026-07-21*
