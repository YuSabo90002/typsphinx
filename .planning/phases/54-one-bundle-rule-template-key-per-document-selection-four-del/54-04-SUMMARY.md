---
phase: 54-one-bundle-rule-template-key-per-document-selection-four-del
plan: 04
subsystem: infra
tags: [sphinx, typst, importlib-resources, template-bundle, root-absolute-import]

# Dependency graph
requires:
  - phase: 54-01
    provides: three real-compile RED gates recorded against the pre-relocation tree (OUT-05, TPL-02/OUT-06, BLD-06/OUT-04)
  - phase: 54-02
    provides: typsphinx/templates/README.md, the bundled "typst" key's non-.typ canary
  - phase: 54-03
    provides: the published <srcdir>/_typst/base.typ shadow route and the retracted BLD-06 symlink clause
provides:
  - "TypstBuilder._used_template_keys write-time accumulator + _copy_used_template_bundles()/_copy_bundle_directory() finish()-time driver -- every used registry key's bundle copied wholesale to <outdir>/_template/<key>/ (OUT-04)"
  - "writer.compute_template_import_path(key, filename) -- root-absolute /_template/<key>/<file>.typ import, replacing the deleted depth-counted compute_template_import_path_for_dir() (OUT-06)"
  - "template_engine.TEMPLATE_SEARCH_SUBDIR='_typst' -- the shadow-template search path is now <srcdir>/_typst, never srcdir itself (D-14)"
  - "template_engine.get_default_template_path() resolved through importlib.resources; default_template_bundle_traversable() for the bundle-copy driver (SC#2)"
  - "A-01 guard: CONF-17's parent-directory predicate applied to the RESOLVED path of every used key, including the synthesized \"typst\" key, inside _copy_used_template_bundles()"
  - "The three 54-01 RED gates (test_user_template_relative_asset_gate.py, test_two_key_selection_gate.py, test_bundle_copy_exclusion_manifest_gate.py) now pass unconditionally, no xfail marker"
affects: [54-05, 54-06, 54-07]

# Actuals (#2632)
actuals:
  tokens: 24851
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Write-time accumulator (self._used_template_keys) -> finish()-time consumer, mirroring self.images/copy_image_files()"
    - "importlib.resources.files()/as_file() for loader-agnostic package-data resolution, with the context manager held open around the entire copy, not just the path lookup"
    - "Root-absolute Typst import path (/_template/<key>/<file>.typ) resolved via Typst's own project-root handling (pdf.py's root=self.outdir), eliminating depth-counting entirely"

key-files:
  created: []
  modified:
    - typsphinx/builder.py
    - typsphinx/writer.py
    - typsphinx/template_engine.py
    - tests/fixtures/typst_lang_gate/srcdir_shadow_lang/base.typ (renamed to _typst/base.typ)
    - tests/fixtures/typst_lang_gate/srcdir_shadow_lang/conf.py
    - tests/test_template_engine.py
    - tests/test_typst_lang_gate.py
    - tests/test_template_import_path.py
    - tests/test_two_layer_output_gate.py
    - tests/test_entry_metadata_route_uniformity.py
    - tests/test_default_typst_documents_gate.py
    - tests/test_examples_charged_ieee_gate.py
    - tests/test_nested_master_render_gate.py
    - tests/test_package_only_config_gate.py
    - tests/test_package_template_routing.py
    - tests/test_registry_prewrite_validation_gate.py
    - tests/test_target_name_render_gate.py
    - tests/test_signature_page_boundary_render_gate.py
    - tests/test_signature_overflow_render_gate.py
    - tests/test_readthedocs_config.py
    - .readthedocs.yaml
    - tests/test_bundle_copy_exclusion_manifest_gate.py
    - tests/test_user_template_relative_asset_gate.py
    - tests/test_two_key_selection_gate.py

key-decisions:
  - "A-01's guard applies CONF-17's existing os.path.commonpath predicate to the RESOLVED path of every used key (not just declared ones), raising immediately (not accumulated) -- matches the plan's literal 'raise' wording rather than the destination-collision block's aggregate wording"
  - "Bundle-destination collisions (two used keys folding to the same <outdir>/_template/<key>/ via _collision_key()) ARE accumulated and raised once, following _validate_output_path_collisions()'s idiom -- resolved BEFORE any copy for either colliding key runs"
  - "_write_template_file()'s own search_paths also moved to srcdir/_typst for consistency with the Task 1 acceptance criterion (no remaining search_paths=[srcdir]-shaped call anywhere in typsphinx) -- it is still called this plan (deleted in 54-05), so leaving it on the old search path would have made its output silently diverge from render_wrapper()'s resolution for a shadow-route project"
  - "Package-alone skip condition in _copy_used_template_bundles() is entry.package and not entry.template (mirrors render_wrapper()'s own predicate exactly) -- NOT entry.template is None, which would have wrongly skipped a key with neither template nor package set (that key still resolves to the bundled default and its wrapper does import it)"

patterns-established:
  - "Defensive getattr(self, '_used_template_keys', None) at the top of a finish()-time consumer, mirroring CONF-19's own getattr(config, '_raw_config', {}) convention -- protects against a builder constructed directly (bypassing init()) by several pre-existing unit tests"

requirements-completed: [TPL-02, OUT-04, OUT-05, OUT-06]

coverage:
  - id: D1
    description: "Every used registry key's resolved template bundle is copied wholesale to <outdir>/_template/<key>/ at finish() time, fed by a write-time accumulator; a used key carrying a package and no template copies nothing; a build that writes no wrapper creates no _template/ directory at all"
    requirement: "OUT-04"
    verification:
      - kind: integration
        ref: "tests/test_bundle_copy_exclusion_manifest_gate.py::TestBundleCopyExclusionManifestGate (4 tests, genuinely green, no xfail marker)"
        status: pass
      - kind: integration
        ref: "tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate::test_both_bundles_are_published (genuinely green, no xfail marker)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Two masters naming two different registry keys produce two visibly-different-templates PDFs in one build, each key's bundle at its own reserved destination; a root master and a nested master naming the SAME key emit the byte-identical root-absolute import string"
    requirement: "TPL-02"
    verification:
      - kind: integration
        ref: "tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate (6 tests, genuinely green, no xfail marker)"
        status: pass
    human_judgment: false
  - id: D3
    description: "A wrapper imports its own key's bundled template by a root-absolute path (compute_template_import_path) that does not depend on the wrapper's own nesting depth -- the depth-counted compute_template_import_path_for_dir() is deleted"
    requirement: "OUT-06"
    verification:
      - kind: unit
        ref: "tests/test_template_import_path.py::TestComputeTemplateImportPath (7 tests including an explicit two-endpoint equality assertion)"
        status: pass
      - kind: other
        ref: "git grep -n 'compute_template_import_path_for_dir' -- typsphinx tests -> zero hits"
        status: pass
    human_judgment: false
  - id: D4
    description: "A user-supplied template's own same-directory #image() reference compiles green through a real typst.compile(), because the template and its asset are copied into the same bundle"
    requirement: "OUT-05"
    verification:
      - kind: integration
        ref: "tests/test_user_template_relative_asset_gate.py::TestUserTemplateRelativeAssetGate (4 tests, genuinely green, no xfail marker)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The bundled default template resolves through importlib.resources (not Path(__file__).parent), and the shadow-template search path moved to <srcdir>/_typst so a resolved template's parent can never be the source tree by the search-path route; the same CONF-17 parent-directory predicate additionally covers the explicit-route bare-filename case (A-01)"
    verification:
      - kind: unit
        ref: "git grep -n '__file__' -- typsphinx/template_engine.py returns no hit inside get_default_template_path; git grep -n 'search_paths=\\[.*srcdir\\]' -- typsphinx returns zero hits"
        status: pass
      - kind: integration
        ref: "tests/test_entry_metadata_route_uniformity.py (A2/A3/collapse routes, all relocated to _typst/, all green)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Full suite green, no xfail remaining from this phase; black and mypy clean"
    verification:
      - kind: unit
        ref: "uv run pytest tests/ -q -> 1286 passed, 5 skipped, 0 xfailed"
        status: pass
      - kind: unit
        ref: "uv run black --check . -> clean; uv run mypy typsphinx/ -> clean"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-16
status: complete
---

# Phase 54 Plan 04: One Bundle Rule — Root-Absolute Import, Finish-Time Bundle Copy Summary

**Every used `typst_document_templates` registry key's resolved template bundle is now copied wholesale to `<outdir>/_template/<key>/` at `finish()` time, and every wrapper imports its own key's template by a root-absolute `/_template/<key>/<file>.typ` path that does not depend on the wrapper's own nesting depth — turning Phase 53's registry plumbing into an observable, per-document template selection for the first time, and closing a previously-unnamed whole-source-tree-copy hole in the synthesized built-in key (A-01).**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-16 (session start, reading context)
- **Completed:** 2026-08-16T01:09:23+09:00
- **Tasks:** 3
- **Files modified:** 24 (1 renamed, 23 modified; 0 new files)

## Accomplishments

- `typsphinx/builder.py` gained a write-time `self._used_template_keys` accumulator (mirroring `self.images`), a `_copy_bundle_directory()` generalizing the existing `os.walk()` + `shutil.copy2` copy loop with D-04's four-kind exclusion and D-05's fatal/non-fatal error split, and `_copy_used_template_bundles()` — the `finish()`-time driver that resolves every used key's template, applies the A-01 parent-directory guard, detects bundle-destination collisions, and copies each bundle (holding `importlib.resources.as_file()`'s context open around the entire copy for the bundled default).
- `typsphinx/writer.py`'s `render_wrapper()` now builds its `TemplateEngine`'s search path from `<srcdir>/_typst` (never bare `srcdir`) and computes its template import via the new `compute_template_import_path(key, filename)` — a pure `f"/_template/{key}/{filename}"` string with no depth argument at all, replacing the deleted `compute_template_import_path_for_dir()`.
- `typsphinx/template_engine.py`'s `get_default_template_path()` now resolves the bundled `"typst"` key's `base.typ` through `importlib.resources` instead of `Path(__file__).parent` arithmetic (SC#2), and a new `TEMPLATE_SEARCH_SUBDIR = "_typst"` constant plus `default_template_bundle_traversable()` support the relocated shadow route (D-14) and the bundle-copy driver respectively.
- The `<srcdir>/base.typ` shadow-template fixture and its unit test were relocated to `<srcdir>/_typst/base.typ`, closing Pitfall 0 (a stray `base.typ` at `srcdir`'s own root previously made the synthesized `"typst"` key's resolved-template PARENT directory equal `srcdir` itself, which the new bundle-copy rule would otherwise have copied wholesale — the entire source tree — into published build output).
- A-01 (resolved `54-CONTEXT.md` assumption): the same CONF-17 parent-directory predicate `template_registry.py` already applies to every DECLARED key's `template` value now also applies to the RESOLVED path of every USED key inside `_copy_used_template_bundles()` — closing the explicit-route half of the same hole (a bare-filename `typst_template` planted directly at `srcdir`'s own root) that D-14 only closed structurally for the search-path route.
- Migrated 15 test modules plus `.readthedocs.yaml` off the old depth-counted `_template.typ` import shape to the new root-absolute `/_template/<key>/<file>.typ` shape — wrapper-content assertions, the direct unit tests of the deleted depth-counting helper (`tests/test_template_import_path.py` rewritten wholesale, `tests/test_two_layer_output_gate.py`'s `TestComputeTemplateImportPathForDir` replaced), and prose describing the output layout.
- Removed the three `xfail(strict=False)` markers `54-01` recorded — `tests/test_user_template_relative_asset_gate.py`, `tests/test_two_key_selection_gate.py`, `tests/test_bundle_copy_exclusion_manifest_gate.py` all now pass unconditionally; the full suite runs green with zero xfails from this phase.

## Task Commits

Each task was committed atomically:

1. **Task 1: One used key's bundle at `<outdir>/_template/<key>/`, imported root-absolutely, compiled green** - `a35a922a` (feat)
2. **Task 2: Migrate every assertion that named the old wrapper import string** - `ec0e6330` (test)
3. **Task 3: Remove the three xfail markers and prove the phase's headline behaviour green** - `7d1f9f51` (test)

_No separate plan-metadata commit — orchestrator owns STATE.md/ROADMAP.md writes for this worktree wave; this SUMMARY.md is committed as part of the worktree's own final commit._

## Files Created/Modified

- `typsphinx/builder.py` - `_used_template_keys` accumulator; `_copy_bundle_directory()`, `_copy_used_template_bundles()`, `_is_excluded_bundle_entry()` and the three D-04 exclusion constants; `_write_template_file()`'s search path moved to `srcdir/_typst`; `finish()` calls the new driver
- `typsphinx/writer.py` - `TEMPLATE_OUTPUT_DIR`, `compute_template_import_path()` replace the deleted `compute_template_import_path_for_dir()`; `render_wrapper()`'s search path and template-file computation updated
- `typsphinx/template_engine.py` - `TEMPLATE_SEARCH_SUBDIR`, `default_template_bundle_traversable()`; `get_default_template_path()` resolved through `importlib.resources`
- `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/base.typ` → `_typst/base.typ` - D-14 relocation (git-renamed, content unchanged apart from a comment-header path update)
- `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/conf.py` - comment block updated to name the new shadow path
- `tests/test_template_engine.py` - `test_resolve_template_search_path` plants `base.typ` in a `_typst` subdirectory
- `tests/test_typst_lang_gate.py` - `test_undeclared_argument_basis_raises` mutates the real bundle file at `_template/typst/custom.typ`, not the orphaned root `_template.typ`
- `tests/test_template_import_path.py` - rewritten wholesale: `TestComputeTemplateImportPath` (unit tests of the new function) + `TestTemplateNamedDirMasterRenderGate` (migrated render gate)
- `tests/test_two_layer_output_gate.py` - `TestComputeTemplateImportPath` replaces `TestComputeTemplateImportPathForDir`; wrapper/content assertions migrated
- `tests/test_entry_metadata_route_uniformity.py` - A2's srcdir shadow and A3/collapse's bare-filename `typst_template` both relocated to `_typst/`
- `tests/test_default_typst_documents_gate.py`, `test_examples_charged_ieee_gate.py` (the real `charged-ieee/approach2` example), `test_nested_master_render_gate.py`, `test_package_only_config_gate.py`, `test_package_template_routing.py`, `test_registry_prewrite_validation_gate.py`, `test_target_name_render_gate.py`, `test_signature_page_boundary_render_gate.py`, `test_signature_overflow_render_gate.py` - wrapper-import and probe-anchor assertions migrated to the new shape
- `.readthedocs.yaml` + `tests/test_readthedocs_config.py` - build-job comment and its paired assertion message no longer describe a single shared `_template.typ` at the output root
- `tests/test_bundle_copy_exclusion_manifest_gate.py`, `tests/test_user_template_relative_asset_gate.py`, `tests/test_two_key_selection_gate.py` - `xfail(strict=False)` markers removed; docstrings/comments rewritten to name `54-04` and their requirement ID

## Decisions Made

- **A-01's guard raises immediately per key**, not accumulated — the plan's own action text says "raise an `ExtensionError`" for this case, distinct from the bundle-destination-collision check two paragraphs later, which explicitly says "accumulate a failure and raise one `ExtensionError`". Read literally, only the destination-collision half follows `_validate_output_path_collisions()`'s aggregate idiom.
- **`_write_template_file()`'s search path was also moved to `srcdir/_typst`**, even though that method is not deleted until `54-05`. Without this, its own `TemplateEngine` would still search bare `srcdir` for a shadow `base.typ`, silently diverging from `render_wrapper()`'s (updated) resolution for any project relying on the shadow route — and Task 1's own acceptance criterion (`git grep -n "search_paths=\[.*srcdir\]" -- typsphinx` returns no hit) would have failed otherwise.
- **The package-alone skip condition in `_copy_used_template_bundles()` is `entry.package and not entry.template`**, mirroring `render_wrapper()`'s own predicate exactly — not `entry.template is None`, which would have wrongly skipped a key declaring NEITHER `template` nor `package` (such a key still resolves to the bundled default via `TemplateEngine`'s own priority walk, and its wrapper's `render_wrapper()` DOES import it, so its bundle must be copied too).
- **Two doc-comment word choices were reworded to avoid literal substring matches** against this plan's own acceptance-criteria greps: `TEMPLATE_SEARCH_SUBDIR`'s docstring no longer spells out the literal `search_paths=[srcdir]` shape it replaces (paraphrased instead), and `get_default_template_path()`'s docstring no longer spells out `Path(__file__).parent` (paraphrased as "module-file-location arithmetic"). Both changes are purely cosmetic — the underlying explanation is unchanged.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `_copy_used_template_bundles()` crashed on a builder constructed without `init()`**
- **Found during:** Task 2 (running the full suite to find the migration set)
- **Issue:** Several pre-existing unit tests in `tests/test_pdf_generation.py::TestPDFErrorHandling` construct a `TypstPDFBuilder(app, env)` directly and call `finish()` without ever calling `init()` (Sphinx's own `Builder.__init__` does not call it) or `write()`. Task 1's new `_copy_used_template_bundles()` unconditionally read `self._used_template_keys`, raising `AttributeError` for all 6 such tests.
- **Fix:** Changed the guard to `if not getattr(self, "_used_template_keys", None): return`, mirroring CONF-19's own established `getattr(config, "_raw_config", {})` defensiveness convention — a builder that never wrote a wrapper correctly has nothing to copy.
- **Files modified:** `typsphinx/builder.py`
- **Verification:** `uv run pytest tests/test_pdf_generation.py -q` → 30 passed (was 6 failing before the fix)
- **Committed in:** `ec0e6330` (Task 2 commit)

**2. [Rule 1 - Bug] `tests/test_typst_lang_gate.py::test_undeclared_argument_basis_raises` mutated an orphaned file**
- **Found during:** Task 1's own acceptance gate (`uv run pytest tests/test_typst_lang_gate.py -q` must report 0 failed)
- **Issue:** This test mutates the SIBLING TEMPLATE FILE a real build writes (previously `_template.typ` at the outdir root) to strip its `lang` parameter, then asserts recompiling the wrapper against that mutated file RAISES. After Task 1's relocation, the wrapper no longer imports `_template.typ` at all (it imports `/_template/typst/custom.typ`), so `_template.typ` is now an orphaned, unimported file — mutating it proves nothing, and the compile no longer raises.
- **Fix:** Retargeted the mutation at the REAL bundle file the build actually writes and the wrapper actually imports (`_template/typst/custom.typ`).
- **Files modified:** `tests/test_typst_lang_gate.py`
- **Verification:** `uv run pytest tests/test_typst_lang_gate.py -q` → 21 passed
- **Committed in:** `a35a922a` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs blocking this plan's own acceptance gates, not scope creep)
**Impact on plan:** Both fixes were necessary for Task 1/Task 2's own stated acceptance criteria to pass; neither touches behaviour outside this plan's scope.

## Issues Encountered

`uv run ruff check .` cannot execute in this NixOS sandbox — `ruff`'s installed wheel is a generic-linux dynamically-linked ELF the sandbox refuses to exec. This is the same pre-existing, previously-documented environment limitation `54-01-SUMMARY.md` and `54-02-SUMMARY.md` both recorded (this repository's own `CLAUDE.md`/project memory tracks the analogous `tox-uv-bare` hazard for the same problem class) — not introduced or fixable by this plan's changes. `black --check .` (316 files) and `mypy typsphinx/` (7 source files) both ran clean throughout.

## Known Stubs

None — every production code path added this plan is fully wired and exercised by a real `sphinx-build`/`typst.compile()` test; no placeholder or hardcoded-empty value was introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `54-05` can now delete `_write_template_file()`, `copy_template_assets()`'s three early returns, `_copy_explicit_assets()`/`_copy_single_asset()`, and `tests/test_template_assets.py` — every wrapper's `#import` now points exclusively at its own key's copied bundle, so the old shared-file write is genuinely dead output (still produced this plan, deliberately, per the plan's own instruction not to break assertions `54-05` migrates).
- `54-06`'s documentation rewrite can describe the shipped `<outdir>/_template/<key>/` layout and the root-absolute import contract as fact, not aspiration — both are now real, tested behaviour.
- `54-07` (OUT-07's `_template/` prefix reservation, negative build-stop test, and `tests/fixtures/template_named_dir_master/`'s relocation) was explicitly out of THIS plan's scope (`OUT-07` is absent from this plan's `requirements` frontmatter; `_validate_output_path_collisions()` was not touched) — its own fixture still coexists correctly today (a docname directory literally named `_template` alongside the NEW `_template/typst/` bundle directory, verified via a real build in this plan's Task 2 migration of `tests/test_template_import_path.py`).
- No coupling risk with `54-01`/`54-02`/`54-03`'s own artifacts: `typsphinx/templates/README.md` (54-02) is correctly excluded from nothing (it is copied as part of the bundle, by design) and does not collide with any manifest-diff assertion this plan added; the CHANGELOG/docs edits from `54-03` were not touched.
- Full pytest suite (1286 passed, 5 skipped, 0 xfailed), `black --check .`, and `mypy typsphinx/` all green against the final state; `ruff check .` could not run in this environment (documented, pre-existing, unrelated).
- Milestone branch `gsd/v0.9.0-per-document-templates` confirmed still present on `origin` (`git ls-remote --heads origin` non-empty) — standing invariant #5 unaffected by this plan (no push performed here; the branch was already current from an earlier phase).

## Self-Check: PASSED

- FOUND: `typsphinx/builder.py` contains `_used_template_keys`, `_copy_used_template_bundles`, `_copy_bundle_directory`, `_is_excluded_bundle_entry`, `followlinks=False`, `.DS_Store`
- FOUND: `typsphinx/writer.py` contains `compute_template_import_path`, `TEMPLATE_OUTPUT_DIR`
- FOUND: `typsphinx/template_engine.py` contains `TEMPLATE_SEARCH_SUBDIR`, `default_template_bundle_traversable`, `importlib.resources`
- FOUND: `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/_typst/base.typ`
- MISSING (expected): `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/base.typ` (relocated)
- FOUND commit `a35a922a` in `git log --oneline --all`
- FOUND commit `ec0e6330` in `git log --oneline --all`
- FOUND commit `7d1f9f51` in `git log --oneline --all`
- CONFIRMED: `uv run pytest tests/ -q` → 1286 passed, 5 skipped, 0 xfailed
- CONFIRMED: `git grep -c "xfail" -- tests/test_user_template_relative_asset_gate.py tests/test_two_key_selection_gate.py tests/test_bundle_copy_exclusion_manifest_gate.py` → 0 for all three

---
*Phase: 54-one-bundle-rule-template-key-per-document-selection-four-del*
*Completed: 2026-08-16*
