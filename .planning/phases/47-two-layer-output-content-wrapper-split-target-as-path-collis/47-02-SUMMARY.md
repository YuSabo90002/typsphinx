---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 02
subsystem: infra
tags: [sphinx, typst, typst-py, docutils, output-builder]

requires:
  - phase: 47-01
    provides: "tests/test_two_layer_output_gate.py (strict-xfail gate module), tests/fixtures/two_layer_root_master_gate/, tests/fixtures/two_layer_nested_master_gate/, 47-EXPECTED-STRUCTURE.md's per-fixture expected-path derivations"
provides:
  - "typsphinx.writer.compute_content_include_path() -- a two-endpoint posixpath.relpath wrapper->content #include() path computation"
  - "typsphinx.writer.compute_template_import_path_for_dir() -- wrapper-directory-based _template.typ import depth computation"
  - "TypstWriter.render_wrapper() -- the wrapper-.typ emitter (template application + #include()), replacing the old is_master branch of translate()"
  - "TypstWriter.translate() rewritten to unconditionally emit the CONTENT file (D-06 preamble, no template) for every docname"
  - "typsphinx.builder._escapes_outdir() -- the OUT-02-only escape guard (parent traversal / absolute / drive-qualified), split out of the old four-term is_guarded expression"
  - "TypstBuilder._content_output_path(), _wrapper_output_relpath(), _write_typst_files() -- the shared content+wrapper write path both builders now use"
  - "TypstPDFBuilder.finish() reading back through _wrapper_output_relpath() so only wrapper files are ever compiled"
  - "D-07 build-log line on -b typst naming the wrapper files written"
affects: [47-03, 47-04, 47-05, 47-06, 47-07, 47-08, 47-09, 47-10]

actuals:
  tokens: 15200
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Content/wrapper split: every docname gets an unconditional, docname-derived content file (no template) plus zero-or-more target-derived wrapper files (one per typst_documents entry naming that docname), each carrying the template application and a single #include() of the content file"
    - "Two-endpoint posixpath.relpath for a cross-file reference whose two endpoints resolve independently (wrapper directory, content path) vs. a depth-only '../' counter for a reference to a fixed-location file (_template.typ at the outdir root) -- the same repo now carries both shapes side by side as a deliberate contrast, not an accidental duplication"
    - "One shared write path (_write_typst_files) called by both TypstBuilder.write_doc and the inherited TypstPDFBuilder.write_doc, making byte-identical .typ output across builders structural rather than a maintained coincidence"

key-files:
  created: []
  modified:
    - typsphinx/writer.py
    - typsphinx/builder.py
    - tests/test_two_layer_output_gate.py
    - tests/test_entry_metadata_precedence.py
    - tests/test_missing_and_malformed_master_gate.py
    - tests/fixtures/missing_and_malformed_master_gate/conf.py
    - tests/fixtures/missing_and_malformed_master_gate/chapter1.rst

key-decisions:
  - "Task 1 and Task 2 landed in one combined commit (36a5f58) rather than two separate task commits: verifying Task 1's own <verify> in isolation (root-master fixture only, nested fixture still xfailing) turned out to require temporarily reverting the OUT-01 guard rewrite, and empirical testing showed the content/wrapper split alone (independent of OUT-01) already closes B-1 and B-2 for the nested fixture -- see Deviations."
  - "TypstPDFBuilder.write_doc() was deleted entirely rather than kept as a one-line delegation to _write_typst_files() -- it is now literally identical to the inherited TypstBuilder.write_doc(), so removing the override is the more literal reading of 'ONE shared write path' than two near-duplicate one-liners."
  - "_wrapper_output_relpath(entry) resolves via self._resolve_output_stem(entry[0]) (docname-based first match), not a per-entry-target computation -- matching the plan's literal instruction to keep _resolve_output_stem's existing matching rules verbatim. This means two typst_documents entries sharing one docname still resolve their WRAPPER PATH via the first match (title/author are per-entry via D-08, but path resolution is not yet) -- a known, plan-acknowledged limitation deferred to 47-09's unified validator."
  - "The wrapper's #include() is emitted as a direct markup-mode `#include(\"path\")` line, not wrapped in a `#{ include(...) }` code-mode block, so the literal substring COMP-02's gate asserts (`#include(`) is trivially present."

patterns-established:
  - "compute_content_include_path()/compute_template_import_path_for_dir() docstrings use the >>> Examples convention (verified via `python -m doctest`); the pre-existing _compute_template_import_path() docstring convention was the template."

requirements-completed: [COMP-01, COMP-02, COMP-03, COMP-04, OUT-01, OUT-02, OUT-03]

coverage:
  - id: D1
    description: "A content file (docname-derived, no template) and a wrapper file (target-derived, full template + #include()) are both emitted for a root-level master, verified via a real sphinx-build + real typst.compile()"
    requirement: "COMP-01"
    verification:
      - kind: integration
        ref: "tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_comp01_content_file_has_no_template"
        status: pass
      - kind: integration
        ref: "tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_comp02_wrapper_file_has_template_and_include"
        status: pass
    human_judgment: false
  - id: D2
    description: "Content files stay docname-derived and wrappers land at their resolved target path, independently, for a nested fixture whose wrapper target strays into an unrelated directory (OUT-01/OUT-03)"
    requirement: "OUT-03"
    verification:
      - kind: integration
        ref: "tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_out03_content_files_stay_docname_derived"
        status: pass
    human_judgment: false
  - id: D3
    description: "B-1 (COMP-03): a nested wrapper whose #include() previously named a physically different file now compiles successfully via a real typst.compile()"
    requirement: "COMP-03"
    verification:
      - kind: integration
        ref: "tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_comp03_b1_nested_master_compiles"
        status: pass
    human_judgment: false
  - id: D4
    description: "B-2 (COMP-04): a toctree-included master's template no longer re-expands mid-body -- verified by real pypdf structural extraction (no second title page, exactly one outline)"
    requirement: "COMP-04"
    verification:
      - kind: integration
        ref: "tests/test_two_layer_output_gate.py::TestTwoLayerOutputGatePdf::test_comp04_b2_no_mid_body_template_reexpansion"
        status: pass
    human_judgment: false
  - id: D5
    description: "OUT-01 reversed: a path-bearing typst_documents target resolves exactly where written, with no separator guard; OUT-02 kept: traversal/absolute/drive-qualified targets still fall back to a basename with a warning"
    requirement: "OUT-01"
    verification:
      - kind: unit
        ref: "tests/test_builder_output_stem.py (23 of 27 tests pass unchanged; 4 separator-guard tests now fail as the plan's own acceptance criteria requires -- see Known Deferred Failures)"
        status: pass
    human_judgment: false
  - id: D6
    description: "-b typst and -b typstpdf emit byte-identical .typ files from one shared write path; only wrapper files compile to PDF"
    requirement: null
    verification:
      - kind: integration
        ref: "tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_typst_and_typstpdf_emit_byte_identical_typ_files"
        status: pass
    human_judgment: false
  - id: D7
    description: "Two consecutive -b typst builds of the same project produce byte-identical wrapper and content files (deterministic emission order)"
    requirement: null
    verification:
      - kind: integration
        ref: "tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_typst_build_is_deterministic_across_runs"
        status: pass
    human_judgment: false
  - id: D8
    description: "-b typst logs which wrapper files it wrote and states those are the files to compile (D-07)"
    requirement: null
    verification:
      - kind: integration
        ref: "tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_typst_build_log_names_the_wrapper_files_to_compile"
        status: pass
    human_judgment: false
  - id: D9
    description: "The master/included boolean predicate (_is_master_document) is gone from the repository, proven by a repo-wide grep over typsphinx/ and tests/ rather than reading writer.py alone"
    requirement: null
    verification:
      - kind: other
        ref: "grep -rn \"_is_master_document\" typsphinx/ tests/ (zero hits)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 02: Two-Layer Content/Wrapper Split Summary

**Replaced the "one `.typ` per docname, shape decided by a build-wide master/included boolean" rule with an unconditional docname-derived CONTENT file plus zero-or-more target-derived WRAPPER files per `typst_documents` entry, closing B-1 (COMP-03, a nested wrapper's `#include()` naming a physically different file) and B-2 (COMP-04, a toctree-included master's template re-expanding mid-body) by construction, and reversing Phase 44's D-05/D-06/D-07 path-rejection guard (OUT-01) while keeping its escape-prevention half (OUT-02).**

## Performance

- **Duration:** ~55 min
- **Tasks:** 3 (combined into 2 commits -- see Deviations)
- **Files modified:** 7 (2 production modules, 5 test/fixture files)

## Accomplishments

- `typsphinx/writer.py`: deleted `_is_master_document()` and its call site; rewrote `TypstWriter.translate()` to unconditionally emit the docname-derived CONTENT file (D-06 preamble, no template); added `TypstWriter.render_wrapper()` carrying the surviving template-application logic, now reading title/author positionally off its own entry tuple (D-08, via the new `_entry_element_value()`) instead of a docname first-match scan; added the two new module-level pure functions `compute_content_include_path()` (a genuine two-endpoint `posixpath.relpath`) and `compute_template_import_path_for_dir()` (a depth counter from the WRAPPER's own resolved directory).
- `typsphinx/builder.py`: split the four-term `is_guarded` boolean into the new `_escapes_outdir()` (OUT-02's three escape terms only, dropping the separator-membership term OUT-01 reverses); added `_content_output_path()` (unconditional, docname-derived), `_wrapper_output_relpath()` (OUT-01: the resolved stem as-is, no `_directory_preserving_relpath()` forcing), and `_write_typst_files()` -- the one shared write path both `TypstBuilder.write_doc` and the now-inherited `TypstPDFBuilder.write_doc` use; updated `TypstPDFBuilder.finish()` to read back through `_wrapper_output_relpath()` so only wrapper files are ever compiled; implemented D-07's build-log line naming the wrapper files `-b typst` wrote.
- Fixed a pre-existing bug in the plan 47-01 gate module (`tests/test_two_layer_output_gate.py`): a class-scoped pytest fixture defined as an instance method is deprecated as of pytest 9.1 (`PytestRemovedIn10Warning`), and this repo escalates `DeprecationWarning` to a hard error -- the fixture-setup error was silently making the dependent `xfail(strict=True)` COMP-04 test report `xfailed` for the WRONG reason. Moved the fixture to module level per this repo's established convention (`test_pdf_render_gate.py`'s `admonition_render_gate_pdf_text`).
- All 6 xfail markers plan 47-01 seeded (COMP-01, COMP-02, COMP-03, COMP-04, OUT-03, `compute_content_include_path` unit) removed and now genuinely pass; added the three `compute_template_import_path_for_dir` unit cases from task 1's `<behavior>` block.
- Added a byte-identity test (`-b typst`/`-b typstpdf` emit identical `.typ` files; only wrapper files compile to PDF), a determinism test (two consecutive `-b typst` builds byte-match), and a build-log assertion for D-07.
- Repo-wide `grep -rn "_is_master_document" typsphinx/ tests/` now returns zero hits (success criterion 1) -- fixed four remaining comment-only references in modules outside this plan's own `files_modified` scope.

## Task Commits

Both were combined per-file into two commits rather than one-per-task (see Deviations for why Tasks 1 and 2 landed together):

1. **Task 1 (tracer) + Task 2 (OUT-01/OUT-02 disentangle)** - `36a5f58` (feat) - the full content/wrapper split plus the OUT-01 guard rewrite, `typsphinx/writer.py`, `typsphinx/builder.py`, `tests/test_two_layer_output_gate.py`
2. **Task 3 (builder parity, D-07 logging, repo-wide grep)** - `ef0ec2d` (test) - byte-identity/determinism/log tests, `TypstBuilder.write()`'s D-07 log line, and the four comment-only `_is_master_document` reference fixes

_No TDD-marked tasks landed a separate RED-then-GREEN pair in this plan's own commits -- the RED evidence was already recorded by 47-01's xfail markers; this plan's job was making them pass._

## Files Created/Modified

- `typsphinx/writer.py` - content/wrapper split: `translate()` always emits content, new `render_wrapper()` emits the template+include wrapper, two new path-computation functions
- `typsphinx/builder.py` - `_escapes_outdir()`, `_content_output_path()`, `_wrapper_output_relpath()`, `_write_typst_files()`, D-07 log line, `TypstPDFBuilder.finish()` read-back fix
- `tests/test_two_layer_output_gate.py` - xfail markers removed, byte-identity/determinism/log tests added, `compute_template_import_path_for_dir` unit tests added, COMP-04 fixture moved to module level
- `tests/test_entry_metadata_precedence.py` - comment-only `_is_master_document` reference fixed
- `tests/test_missing_and_malformed_master_gate.py` - comment-only `_is_master_document` reference fixed
- `tests/fixtures/missing_and_malformed_master_gate/conf.py` - comment-only `_is_master_document` reference fixed
- `tests/fixtures/missing_and_malformed_master_gate/chapter1.rst` - comment-only `_is_master_document` reference fixed

## Decisions Made

- `_wrapper_output_relpath(entry)` resolves via `self._resolve_output_stem(entry[0])` (docname-based first match), matching the plan's literal instruction to keep `_resolve_output_stem`'s existing matching rules verbatim rather than rewriting it to a per-entry-target computation. Two `typst_documents` entries sharing one docname therefore still resolve their WRAPPER PATH via the first match even though D-08 makes their title/author independently per-entry -- a known, plan-acknowledged gap 47-09's unified validator is expected to close.
- `TypstPDFBuilder.write_doc()` was deleted entirely (inherits `TypstBuilder.write_doc()`) rather than kept as a redundant one-line override, since both bodies became literally identical after the split -- the more literal reading of "ONE shared write path."
- The wrapper's `#include()` is emitted as a direct markup-mode `#include("path")` line (not a `#{ include(...) }` code-mode block), so the literal `#include(` substring COMP-02's gate asserts is trivially present and the emission stays simple.
- The pre-existing CR-01 collision check inside `_resolve_output_stem()` was left computing its "effective" comparison through `_directory_preserving_relpath()` (its pre-OUT-01 shape) exactly as the plan directs -- this can produce a synthetic, not-actually-written comparison path for a path-bearing target, but this is explicitly deferred to 47-09's unified validator and does not affect this plan's own fixtures.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed a class-scoped pytest fixture defined as an instance method in `tests/test_two_layer_output_gate.py`**
- **Found during:** Task 1 (initial full-implementation test run)
- **Issue:** `TestTwoLayerOutputGatePdf.nested_master_outer_pdf_text` (written in plan 47-01) was a class-scoped fixture defined as an instance method (`def nested_master_outer_pdf_text(self, tmp_path_factory)`). pytest 9.1's `PytestRemovedIn10Warning` deprecates this shape, and this repo's `pyproject.toml` escalates `DeprecationWarning` to a hard error (`filterwarnings = ["error::DeprecationWarning"]`). This made pytest raise during fixture resolution BEFORE the fixture body ever ran, and the dependent `xfail(strict=True)` test reported `xfailed` for the WRONG reason -- a fixture-setup error masquerading as the expected pre-fix RED, which would have continued masquerading as unrelated post-fix passes without ever actually running the real assertion.
- **Fix:** Moved the fixture to module level (removed `self`), matching `tests/test_pdf_render_gate.py`'s established `admonition_render_gate_pdf_text` convention.
- **Files modified:** `tests/test_two_layer_output_gate.py`
- **Verification:** `uv run pytest tests/test_two_layer_output_gate.py::TestTwoLayerOutputGatePdf -v` now genuinely executes and passes the real COMP-04 pypdf structural assertion.
- **Committed in:** `36a5f58` (Task 1+2 commit)

**2. [Rule 1 - Bug/Structural] Repo-wide grep for `_is_master_document` found four remaining comment-only references outside this plan's `files_modified` scope**
- **Found during:** Task 3 (running the repo-wide grep success criterion 1 demands)
- **Issue:** Task 3's action explicitly requires this grep to return zero hits, but `tests/fixtures/missing_and_malformed_master_gate/{conf.py,chapter1.rst}`, `tests/test_missing_and_malformed_master_gate.py`, and `tests/test_entry_metadata_precedence.py` (none in this plan's own `files_modified`) each carried a comment describing behavior in terms of the now-deleted `_is_master_document()`.
- **Fix:** Reworded each comment to describe the equivalent Phase 47 mechanism (`TypstBuilder._write_typst_files()`'s per-docname wrapper-entry matching loop for the docname-scan comments; `_entry_element_value()`'s positional D-08 read for the first-match-convention comment) without changing any test's assertions or fixture's functional configuration.
- **Files modified:** `tests/fixtures/missing_and_malformed_master_gate/conf.py`, `tests/fixtures/missing_and_malformed_master_gate/chapter1.rst`, `tests/test_missing_and_malformed_master_gate.py`, `tests/test_entry_metadata_precedence.py`
- **Verification:** `grep -rn "_is_master_document" typsphinx/ tests/` returns zero hits; `uv run pytest tests/test_entry_metadata_precedence.py -q` (26 passed) and the one already-passing test in `tests/test_missing_and_malformed_master_gate.py` are unaffected (its OTHER test was already failing pre-edit for an unrelated, plan-acknowledged reason -- see Known Deferred Failures).
- **Committed in:** `ef0ec2d` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (1 Rule 3 blocking, 1 Rule 1 structural repo-wide cleanup). Both were necessary for this plan's own designated `<verification>` and success criteria to be measured correctly, not scope creep into the deferred corpus-migration work (see Known Deferred Failures).

## Task-Ordering Note (not a deviation, but a discovered fact worth recording)

Plan 47-02's Task 1 was designed as an isolated tracer slice: land the content/wrapper split for the ROOT-master fixture only, leaving the nested fixture's B-1/B-2 tests genuinely still `xfail`ing until Task 2's OUT-01 guard rewrite lands. Verifying this intermediate state empirically (temporarily reverting the OUT-01 guard change) showed that B-1 (COMP-03) and B-2 (COMP-04) are BOTH already closed by the content/wrapper split alone, independent of whether `_resolve_output_stem`'s separator guard has been reversed yet -- because the translator's own toctree `#include()` computation is always docname-to-docname (unaffected by this plan), and once content files are unconditionally written at their docname path (COMP-01), that computation resolves correctly regardless of where any entry's WRAPPER physically lands. OUT-01's guard rewrite only changes WHERE THE WRAPPER FILE ITSELF is written (`manuals/guide.typ` vs. the old truncated+relocated `guide/guide.typ`), which is what OUT-03's own test independently verifies. Given this, isolating Task 1 to leave the nested gate tests genuinely `xfail`ing (as the plan's task-1-only acceptance criteria assumed) was not achievable without either (a) leaving genuinely-fixed tests marked `xfail(strict=True)`, which fails pytest's own strict-xfail contract (XPASS), or (b) prematurely removing their markers mid-task-1, which blurs the task boundary the plan intended. Tasks 1 and 2 were therefore combined into one commit; this is recorded here rather than silently reshaping the task list, since 47-EXPECTED-STRUCTURE.md and future phase retrospectives may want to know B-1/B-2's true dependency shape.

## Known Deferred Failures (explicitly acknowledged by this plan, not fixed here)

Per this plan's own `<verification>` section: *"The full `uv run pytest` suite is KNOWINGLY RED after this plan: 87 fixture projects still configure a self-colliding target and 68 modules still read the pre-split file shape. Plans 47-04 through 47-08 close that, and 47-09 is the phase's full-suite-green gate. Do not attempt to fix unrelated modules here."*

Confirmed and measured this task:

- `tests/test_builder_output_stem.py`: 4 of 42 tests now fail (`test_resolve_output_stem_guards_posix_path_separator`, `test_resolve_output_stem_guards_backslash_path_separator`, `test_resolve_output_stem_warns_on_path_bearing_target`, `test_resolve_output_stem_warns_once_on_path_bearing_target_with_empty_basename`) -- this is the exact, plan-predicted "still-passing separator-truncation assertion is itself the signal that OUT-01 was not applied" outcome. Deferred to plan 47-03 per the plan's own text.
- Full `uv run pytest -q`: 227 failed, 672 passed, 5 skipped, 7 xfailed, 101 errors (measured before Task 3's additions; Task 3 adds 3 more passing tests and does not touch any failing corpus fixture). Traced one representative failure (`tests/test_typst_lang_gate.py::TestMalformedLanguage::test_build_does_not_abort`) to confirm root cause: its fixture's `typst_documents` entry uses an identity target (`docname == target`, a common pre-47 pattern), which under the new architecture makes the WRAPPER resolve to the SAME physical path as the CONTENT file -- the wrapper write silently overwrites the content file with a self-referential `#include()`, producing `TypstError: cyclic import`. This is precisely D-01's canonical self-collision scenario (`bld03_self_collision_gate`, plan 47-01), matching the plan's own "87 fixture projects still configure a self-colliding target" text. Not fixed here -- the unified pre-write collision validator that rejects this instead of silently overwriting is 47-09's job.
- `tests/test_template_import_path.py::TestTemplateNamedDirMasterRenderGate::test_template_named_dir_master_resolves_and_compiles` fails: its fixture's target (`"index"`, matching its own docname's basename) relied on the NOW-REVERSED `_directory_preserving_relpath()` D-05 forcing to relocate the wrapper into the docname's own directory; OUT-01 makes the same bare target resolve at the outdir root instead. This is exactly OUT-01's documented reversal notice ("D-05... a nested docname's output forced into that docname's own directory... is NOT sacred") acting on an existing fixture -- corpus migration territory for plans 47-04 through 47-08, not this plan.

None of these are regressions introduced by an implementation mistake; each traces directly to a locked, plan-acknowledged reversal or migration debt this phase's later waves close.

## Issues Encountered

None beyond the two auto-fixed deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `compute_content_include_path()` and `compute_template_import_path_for_dir()` (`typsphinx.writer`) and `_escapes_outdir()`, `_content_output_path()`, `_wrapper_output_relpath()`, `_write_typst_files()` (`typsphinx.builder`) are the load-bearing new symbols later phase-47 plans should build on, not re-derive.
- Plan 47-03 (per this plan's own `<verification>` note) is expected to move `tests/test_builder_output_stem.py`'s 4 now-failing separator-guard tests to reflect OUT-01.
- Plans 47-04 through 47-08 migrate the ~87 existing fixture projects (and the ~68 test modules asserting against their pre-split output shape) per `47-EXPECTED-STRUCTURE.md`'s "Corpus migration rules" (R1-R5 table + fixture de-collision rule) -- the self-collision failures traced above are exactly the migration target.
- Plan 47-09 is the phase's full-suite-green gate, expected to land the unified pre-write collision validator (D-02/D-03) that makes a self-colliding or duplicate-target configuration fail loudly BEFORE any write, closing the gap `_wrapper_output_relpath()`'s docname-first-match limitation and the corpus's identity-target fixtures both currently fall into.
- No blockers for downstream plans: this plan's own designated verification (`tests/test_two_layer_output_gate.py`, `tests/test_preview_version_sync.py`, `tests/test_builder_output_stem.py` apart from the 4 acknowledged failures, `black --check .`, `mypy typsphinx/`, the repo-wide `_is_master_document` grep) all pass as specified. `ruff check .` could not run in this sandbox (pre-existing NixOS generic-linux-ELF limitation, unrelated to this plan, tracked separately per 47-01's own note).

## Self-Check: PASSED

All modified files verified present on disk. Both task commits (`36a5f58`, `ef0ec2d`) verified present in `git log --oneline --all`.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*
