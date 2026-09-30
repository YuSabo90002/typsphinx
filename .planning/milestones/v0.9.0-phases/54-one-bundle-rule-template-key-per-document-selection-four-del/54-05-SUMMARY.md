---
phase: 54-one-bundle-rule-template-key-per-document-selection-four-del
plan: 05
subsystem: infra
tags: [sphinx, typst, builder, template-bundle, deletion, test-migration]

# Dependency graph
requires:
  - phase: 54-04
    provides: "the per-key bundle driver (_used_template_keys accumulator, _copy_used_template_bundles()/_copy_bundle_directory(), root-absolute import) this plan's deletions are made safe by"
provides:
  - "typsphinx/builder.py with five methods deleted (_write_template_file, copy_template_assets, _copy_template_directory, _copy_explicit_assets, _copy_single_asset) and their two call sites removed from prepare_writing()/finish()"
  - "The both-package-and-template-configured build warning (D-03), relocated from the deleted _write_template_file() into _copy_used_template_bundles(), firing once per build per used key"
  - "tests/test_template_assets.py deleted in full, with an 8-row audit mapping each test to its coverage successor"
  - "Every remaining test/fixture assertion of the old root-level _template.typ file migrated to the per-key _template/<key>/ bundle destination"
affects: [54-06, 54-07]

# Actuals (#2632)
actuals:
  tokens: 19500
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Relocating a once-per-build warning from a deleted method into its functional successor, rather than dropping it, when no per-document caller already emits an equivalent (T-54-20)"
    - "Coverage-audit-before-delete: enumerate every test in a module being deleted, name its successor or removal rationale, before removing the module"

key-files:
  created: []
  modified:
    - typsphinx/builder.py
    - typsphinx/writer.py
    - typsphinx/template_registry.py
    - tests/test_output_layout_docs_gate.py
    - tests/test_integration_advanced.py
    - tests/test_integration_basic.py
    - tests/test_external_link_style_render_gate.py
    - tests/test_heading_depth_render_gate.py
    - tests/test_typst_lang_gate.py
    - tests/test_empty_typst_documents_optout_gate.py
    - tests/test_registry_prewrite_validation_gate.py
    - tests/test_package_template_routing.py
    - tests/test_typst_documents_collision_gate.py
    - tests/fixtures/admonition_greyscale_probe/conf.py
    - tests/fixtures/derived_template_collision_gate/conf.py
    - tests/fixtures/package_only_config_gate/conf.py
    - tests/fixtures/template_named_dir_master/conf.py
    - tests/fixtures/template_named_dir_master/_template/index.rst
    - tests/test_template_assets.py (deleted)

key-decisions:
  - "The both-package-and-template warning is relocated into _copy_used_template_bundles(), not dropped -- it now fires once per build PER USED KEY carrying both, generalizing correctly from the old global-config-only check (only the synthesized 'typst' key can ever trigger it, since CONF-15 already rejects a DECLARED registry entry naming both template and package at config-read time; enforced with an assert, not a dead else-branch)"
  - "_validate_output_path_collisions()'s exact-name claim on _template.typ is left completely unchanged, per the plan's own key_links/read_first instruction -- 54-07 widens it into a _template/ prefix reservation. This means the overall plan verification's 'git grep _template\\.typ -- typsphinx returns no hits' bullet is NOT literally satisfied by design; see Known Discrepancies below"
  - "The dead static method TypstWriter._compute_template_import_path() (confirmed zero non-docstring callers before and after this plan) is left in place unremoved, per 54-CONTEXT.md's Deferred Ideas ('not this milestone's responsibility to chase') -- only its stale docstring prose was corrected to stop describing the deleted method as current behaviour"
  - "test_registry_prewrite_validation_gate.py's control-config expected .typ set drops _template.typ but keeps base.typ (54-04's own addition), since the two are now genuinely different files at different paths, not the same file renamed"
  - "test_empty_typst_documents_optout_gate.py's expected set is now just {index.typ} (not {_template.typ, index.typ}) -- an empty typst_documents writes no wrapper, so the write-time _used_template_keys accumulator stays empty and the finish()-time bundle-copy driver creates no _template/ directory at all, unlike the deleted single-file writer which ran unconditionally"

patterns-established:
  - "Audit-before-delete table for a fully-obsoleted test module: for each test, state the behaviour it asserted and where that behaviour is now covered (or why it is a removed configuration surface with no successor)"

requirements-completed: [OUT-04, BLD-06]

coverage:
  - id: D1
    description: "The single-file writer that wrote a shared _template.typ at the outdir root is gone (method + its two call sites in prepare_writing()/write()), and the once-per-build both-package-and-template warning it hosted is relocated into the finish()-time bundle-copy driver rather than silently dropped"
    requirement: "OUT-04"
    verification:
      - kind: unit
        ref: "git grep -c 'def _write_template_file' -- typsphinx (0 hits)"
        status: pass
      - kind: integration
        ref: "tests/test_package_template_routing.py::TestBothConfiguredRouting::test_both_configured_warns_once_and_template_wins"
        status: pass
    human_judgment: false
  - id: D2
    description: "The parallel asset-copy path (copy_template_assets() and its three early returns, _copy_template_directory()'s .typ exclusion, _copy_explicit_assets()/_copy_single_asset() and typst_template_assets' selective-copy semantics) is gone; _copy_used_template_bundles() is the ONLY route from a template directory to the output tree, and finish() contains exactly two calls"
    requirement: "BLD-06"
    verification:
      - kind: unit
        ref: "git grep -n 'copy_template_assets\\|_copy_template_directory\\|_copy_explicit_assets\\|_copy_single_asset\\|dirs_exist_ok' -- typsphinx tests (0 hits)"
        status: pass
      - kind: integration
        ref: "tests/test_bundle_copy_exclusion_manifest_gate.py (4 tests, manifest set includes a nested path proving recursion survives the deletion)"
        status: pass
    human_judgment: false
  - id: D3
    description: "tests/test_template_assets.py deleted in full; every one of its 8 tests audited against a coverage successor or against the removed configuration surface it exercised, with no behaviour silently dropped"
    verification:
      - kind: other
        ref: "8-row audit table in this SUMMARY's ## Deviations / Task 2 commit message; test ! -f tests/test_template_assets.py"
        status: pass
      - kind: integration
        ref: "tests/test_user_template_relative_asset_gate.py::TestUserTemplateRelativeAssetGate (real -b typstpdf compile, proves the bundle-copy driver runs correctly for TypstPDFBuilder's inherited finish())"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every remaining test/fixture assertion of _template.typ's existence at the output root, or in an exact output-set, is migrated to the per-key _template/<key>/ bundle destination -- full suite green with no assertion still naming a file nothing writes"
    verification:
      - kind: unit
        ref: "uv run pytest tests/ -q -> 1278 passed, 5 skipped (1286 minus the 8 deleted test_template_assets.py tests, zero new failures)"
        status: pass
      - kind: unit
        ref: "uv run black --check . -> clean; uv run mypy typsphinx/ -> clean"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-16
status: complete
---

# Phase 54 Plan 05: One Bundle Rule — Delete the Shared-Template Writer and Parallel Asset-Copy Path Summary

**Deleted five `builder.py` methods (the shared-`_template.typ`-at-outdir-root writer plus the parallel asset-copy path with its three early returns and two explicit-list helpers), relocated the one user-facing warning that lived inside the writer, removed a fully-obsoleted 8-test module after auditing every test against its coverage successor, and migrated every remaining test/fixture assertion of the old root-level template file to the per-key `_template/<key>/` bundle path — leaving `_copy_used_template_bundles()` as the sole route from a template directory to the output tree.**

## Performance

- **Duration:** ~40 min
- **Started:** 2026-08-16 (session start, reading context)
- **Completed:** 2026-08-16T01:51:04+09:00
- **Tasks:** 3
- **Files modified:** 19 (1 deleted, 18 modified)

## Accomplishments

- `typsphinx/builder.py` lost `_write_template_file()` entirely (the method that wrote a shared `_template.typ` at the outdir root, unconditionally, once per build) and its call site in `prepare_writing()`. The one behaviour riding inside it that was NOT about writing a file — the once-per-build warning fired when a project configures both `typst_package` and `typst_template` (D-03) — is relocated into `_copy_used_template_bundles()`, generalized correctly to fire per used registry key (though only the synthesized `"typst"` key can ever carry both, since CONF-15 already rejects a declared registry entry naming both at config-read time; enforced with an `assert`, not speculative dead code).
- `typsphinx/builder.py` also lost `copy_template_assets()` (its three early returns: unset global template, package set, empty `typst_template_assets` list), `_copy_template_directory()`, and the explicit asset-list expander/single-asset copier `_copy_explicit_assets()`/`_copy_single_asset()` — including the inherited `shutil.copytree(dirs_exist_ok=True)` default. `finish()`'s body now contains exactly two calls: `copy_image_files()` and `_copy_used_template_bundles()`. `_copy_used_template_bundles()` (landed in 54-04) is now the ONLY route from a template directory to the output tree; "has no bundle" is a per-key property of that driver, not a build-wide early return.
- `tests/test_template_assets.py` (8 tests) deleted in full after auditing every test: one (`automatic_directory_copy`) is covered by the existing manifest-diff and user-template-asset gates; three (`explicit_list`, `glob_pattern`, `empty_list_disables`) tested the now-removed `typst_template_assets` selective-copy configuration surface, which structurally cannot exist under the one-bundle rule; one (`no_template`) is structurally impossible to reproduce (the bundle driver never creates a `_templates/`-shaped directory); one (`with_typst_package`) is now actively FALSE under the new mechanism — proven the opposite by `test_package_template_routing.py`'s both-configured test, closing a genuine pre-existing gap where the template file was written even with a package configured but its sibling assets never were; one (`missing_source`) tested a warning for a feature (named-asset selection) that no longer exists; one (`typstpdf_builder`) is covered by the real `-b typstpdf` compile in `test_user_template_relative_asset_gate.py`.
- Migrated every remaining file-existence and exact-output-set assertion of the old root `_template.typ` to the new per-key `_template/<key>/` bundle path across `test_output_layout_docs_gate.py` (5 tests, including a ten-file-set assertion that becomes a nine-file root-level set plus a separate bundle-path assertion, with matching docstring arithmetic), `test_integration_advanced.py`, `test_integration_basic.py`, `test_external_link_style_render_gate.py`, `test_heading_depth_render_gate.py`, `test_typst_lang_gate.py`'s `TestPreFixBasisFailureProof` fixture, `test_empty_typst_documents_optout_gate.py` (whose expected set is now just `{index.typ}`, since an empty `typst_documents` writes no wrapper and the write-time accumulator never populates), and `test_registry_prewrite_validation_gate.py`'s control-config set.
- Rewrote every stale comment across `builder.py`, `writer.py`, `template_registry.py`, and five fixture files that named the deleted method or described the deleted write as current behaviour — preserving every independent regression rationale each fixture comment carried (target de-collision, per-master author divergence, root-document choice; verified none were accidentally dropped).

## Task Commits

Each task was committed atomically:

1. **Task 1: Remove the shared-template writer and its call site** - `53020877` (feat)
2. **Task 2: Remove the parallel asset-copy path and its two explicit-list helpers** - `6e47a599` (feat)
3. **Task 3: Migrate the remaining output-tree assertions to the per-key bundle layout** - `6c7ff0ce` (test)

_No separate plan-metadata commit — orchestrator owns STATE.md/ROADMAP.md writes for this worktree wave; this SUMMARY.md is committed as part of the worktree's own final commit._

## Files Created/Modified

- `typsphinx/builder.py` - `_write_template_file()`, `copy_template_assets()`, `_copy_template_directory()`, `_copy_explicit_assets()`, `_copy_single_asset()` all deleted; their two call sites removed; the both-configured warning relocated into `_copy_used_template_bundles()`; stale comments repaired throughout
- `typsphinx/writer.py` - stale comments naming the deleted method repaired; the confirmed-dead `_compute_template_import_path()` static method's docstring corrected to stop describing deleted behaviour as current (the function itself is deliberately NOT removed — out of this plan's scope per 54-CONTEXT.md)
- `typsphinx/template_registry.py` - one stale comment repaired
- `tests/test_template_assets.py` - deleted in full (8 tests, audited)
- `tests/test_output_layout_docs_gate.py`, `test_integration_advanced.py`, `test_integration_basic.py`, `test_external_link_style_render_gate.py`, `test_heading_depth_render_gate.py`, `test_typst_lang_gate.py`, `test_empty_typst_documents_optout_gate.py`, `test_registry_prewrite_validation_gate.py`, `test_package_template_routing.py`, `test_typst_documents_collision_gate.py` - assertions/comments migrated to the per-key bundle layout
- `tests/fixtures/admonition_greyscale_probe/conf.py`, `tests/fixtures/derived_template_collision_gate/conf.py`, `tests/fixtures/package_only_config_gate/conf.py`, `tests/fixtures/template_named_dir_master/conf.py`, `tests/fixtures/template_named_dir_master/_template/index.rst` - comment prose updated, all independent regression rationale preserved

## Decisions Made

- **The both-configured warning generalizes to any used key, not just `"typst"`**, even though only `"typst"` can currently reach it (CONF-15 rejects the shape for any declared registry key at config-read time) — this is the more honest generalization of the routing rule `resolve_package_for_engine()` already applies uniformly, and it is enforced with an `assert key == RESERVED_REGISTRY_KEY` rather than a speculative unreachable `else` branch.
- **`_validate_output_path_collisions()`'s exact-name `_template.typ` claim is left completely untouched**, per the plan's own `key_links` and Task 1's `read_first` instruction ("stays functional here... Do not touch it in this plan beyond fixing a comment"). This is a deliberate, explicit exception to the plan's overall verification bullet "`git grep -n \"_template\\.typ\" -- typsphinx` → no hits" — see Known Discrepancies below.
- **The confirmed-dead `TypstWriter._compute_template_import_path()` static method is left in place**, unremoved — 54-CONTEXT.md's Deferred Ideas explicitly says its removal "is still not this milestone's responsibility to chase." Only its docstring's false claim about current behaviour was corrected (past-tense, historical framing), consistent with Task 1's instruction to repair stale comments naming the deleted method rather than leave them lying about current behaviour.
- **Comment fixes were made in three files not in this plan's declared `files_modified`** (`typsphinx/template_registry.py`, `tests/fixtures/template_named_dir_master/_template/index.rst`, and `tests/test_typst_documents_collision_gate.py`) — all three carried a stale reference to the deleted `_write_template_file()` method, discovered by the plan's own instructed `git grep` sweep. Treated as Rule 1 (bug: a comment describing deleted behaviour as current is factually wrong) rather than out-of-scope drift, since fixing them directly furthers this plan's own stated objective and none touch load-bearing test logic.

## Known Discrepancies

The overall plan `<verification>` block states `git grep -n "_template\.typ" -- typsphinx` should return no hits. It does not, by design, for two reasons both explicitly authorized elsewhere in this plan's own text:

1. **`typsphinx/builder.py`** (5 hits, `_validate_output_path_collisions()` and its docstring): the plan's `key_links` states verbatim "The pre-write collision validator still claims the old shared filename by exact name; that claim is `54-07`'s to replace with a prefix reservation and must be left functional here." Task 1's `read_first` repeats this instruction almost verbatim. This is 54-07's work, deliberately deferred.
2. **`typsphinx/writer.py`** (6 hits, the dead `_compute_template_import_path()` static method's docstring and body): 54-CONTEXT.md's Deferred Ideas explicitly declines to chase this function's removal in this milestone. Its docstring prose was corrected to stop describing the deleted method as current behaviour, but the function's own body (including its literal `"_template.typ"` return-value string and doctests) was deliberately left unchanged, since it is confirmed dead code (zero non-docstring callers, before and after this plan) with no doctest-modules execution configured in this project's pytest setup.

Both exceptions are named explicitly in the plan text that governs this task, not discovered ad hoc during execution. `typsphinx/template_engine.py:38`'s one remaining hit is a false-positive substring match (`custom_template.typ`, an unrelated real filename), not a reference to the reserved infrastructure name.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The relocated both-configured warning initially used wording that broke an existing test's substring check**
- **Found during:** Task 1's own verification (running `tests/test_package_template_routing.py`)
- **Issue:** My first relocation of the D-03 warning used new wording (`"configures both 'package' and 'template'"`) that dropped the literal `typst_package`/`typst_template` config-value names `test_package_template_routing.py::TestBothConfiguredRouting::test_both_configured_warns_once_and_template_wins` greps for.
- **Fix:** Restored the original wording (`"Both 'typst_package' and 'typst_template' are configured..."`), which is also more accurate for the ONLY key that can ever reach this branch (the synthesized `"typst"` key, built directly from those two global config values).
- **Files modified:** `typsphinx/builder.py`
- **Verification:** `uv run pytest tests/test_package_template_routing.py -q` → 3 passed
- **Committed in:** `53020877` (Task 1 commit)

**2. [Rule 1 - Bug] `tests/test_typst_lang_gate.py::TestPreFixBasisFailureProof`'s class-scoped fixture still asserted the deleted root file**
- **Found during:** Task 1's full-suite run, expected per the plan's own instruction ("Expect failures in modules asserting the old file's existence at the output root; those are Task 2's" — this one actually surfaced as an ERROR, at fixture setup time, not a plain test FAILURE)
- **Issue:** `custom_template_lang_build_dir`'s fixture body asserted `(build_dir / "_template.typ").exists()` even though the test method's own body had already been migrated to the new bundle path by 54-04 — the fixture setup itself was missed.
- **Fix:** Retargeted the fixture's assertion to `build_dir / "_template" / "typst" / "custom.typ"`, matching what the test method itself already expects.
- **Files modified:** `tests/test_typst_lang_gate.py`
- **Verification:** `uv run pytest tests/test_typst_lang_gate.py -q` → 21 passed
- **Committed in:** `6c7ff0ce` (Task 3 commit)

**3. [Rule 1 - Bug] Three stale references to `_write_template_file()` found outside the plan's declared `files_modified`**
- **Found during:** Task 3's overall-verification grep sweep (`git grep -n "_write_template_file" -- typsphinx tests`)
- **Issue:** `typsphinx/template_registry.py:459`, `tests/fixtures/template_named_dir_master/_template/index.rst:5`, and `tests/test_typst_documents_collision_gate.py:179` all named the deleted method as an explanation of current behaviour.
- **Fix:** Rewrote each to describe the current mechanism (`_validate_output_path_collisions()`'s still-functional exact-name reservation, or the write-time/finish-time template resolution paths generally) without naming the deleted symbol.
- **Files modified:** `typsphinx/template_registry.py`, `tests/fixtures/template_named_dir_master/_template/index.rst`, `tests/test_typst_documents_collision_gate.py`
- **Verification:** `git grep -n "_write_template_file" -- typsphinx tests` → zero hits (after this fix); full suite still green
- **Committed in:** `53020877` (template_registry.py, part of Task 1) and `6c7ff0ce` (the other two, part of Task 3)

---

**Total deviations:** 3 auto-fixed (all Rule 1 — bugs/stale documentation blocking this plan's own acceptance gates or accuracy goals, not scope creep)
**Impact on plan:** All three fixes were necessary for this plan's own stated instructions (preserve the warning's behaviour; repair every stale comment naming the deleted method) to actually hold; none touch behaviour outside this plan's scope.

## Issues Encountered

`uv run ruff check .` cannot execute in this NixOS sandbox — `ruff`'s installed wheel is a generic-linux dynamically-linked ELF the sandbox refuses to exec. This is the same pre-existing, previously-documented environment limitation `54-01-SUMMARY.md`, `54-02-SUMMARY.md`, and `54-04-SUMMARY.md` all recorded — not introduced or fixable by this plan's changes. `black --check .` (315 files) and `mypy typsphinx/` (7 source files) both ran clean throughout.

## Known Stubs

None — every change this plan made is a deletion or a real assertion migration; no placeholder or hardcoded-empty value was introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `54-06` can now register `typst_template_assets`'s removal (the `config-inited` CONF-19 handler) knowing the value is genuinely inert in this build's output — nothing reads it any more, confirmed by this plan's deletion of every consumer.
- `54-07` can now widen `_validate_output_path_collisions()`'s exact-name `_template.typ` claim into a `_template/` prefix reservation and relocate `tests/fixtures/template_named_dir_master/` — this plan deliberately left both untouched, exactly as instructed, so 54-07 inherits a clean, unmodified starting point for that work.
- Full pytest suite (1278 passed, 5 skipped — the 8-test reduction from 54-04's 1286 baseline is exactly `test_template_assets.py`'s deletion, zero new failures), `black --check .`, and `mypy typsphinx/` all green against the final state; `ruff check .` could not run in this environment (documented, pre-existing, unrelated).
- No coupling risk with 54-01/54-02/54-03/54-04's own artifacts — none of their landed files were touched beyond the stale-comment repairs documented above, and every one of 54-04's own new symbols (`_used_template_keys`, `_copy_used_template_bundles`, `_copy_bundle_directory`, `_is_excluded_bundle_entry`, `compute_template_import_path`, `TEMPLATE_OUTPUT_DIR`) is unchanged.
- Milestone branch `gsd/v0.9.0-per-document-templates` unaffected by this plan (no push performed here; worktree-isolated execution, orchestrator owns the merge).

## Self-Check: PASSED

- FOUND: `typsphinx/builder.py` does NOT contain `def _write_template_file`, `def copy_template_assets`, `def _copy_template_directory`, `def _copy_explicit_assets`, or `def _copy_single_asset`
- MISSING (expected): `tests/test_template_assets.py`
- FOUND commit `53020877` in `git log --oneline`
- FOUND commit `6e47a599` in `git log --oneline`
- FOUND commit `6c7ff0ce` in `git log --oneline`
- CONFIRMED: `uv run pytest tests/ -q` → 1278 passed, 5 skipped, 0 failed
- CONFIRMED: `uv run black --check .` → clean; `uv run mypy typsphinx/` → clean
- CONFIRMED: `git grep -n "_write_template_file\|copy_template_assets\|_copy_template_directory\|_copy_explicit_assets\|_copy_single_asset" -- typsphinx tests` → zero hits

---
*Phase: 54-one-bundle-rule-template-key-per-document-selection-four-del*
*Completed: 2026-08-16*
