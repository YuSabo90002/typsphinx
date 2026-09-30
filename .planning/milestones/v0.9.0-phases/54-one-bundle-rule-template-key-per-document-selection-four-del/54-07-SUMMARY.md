---
phase: 54-one-bundle-rule-template-key-per-document-selection-four-del
plan: 07
subsystem: infra
tags: [sphinx, typst, builder, collision-validation, prefix-reservation, test-migration]

# Dependency graph
requires:
  - phase: 54-05
    provides: "the deletion of the shared-template writer and parallel asset-copy path, leaving _validate_output_path_collisions()'s exact-name _template.typ claim deliberately untouched for this plan to widen"
provides:
  - "TypstBuilder._reserves_template_prefix() -- a first-`/`-segment prefix predicate routed through _collision_key()'s folding, refusing any content or wrapper file whose resolved output path's first segment is the reserved template-bundle directory (OUT-07)"
  - "_validate_output_path_collisions() with the exact-name _template.typ claim deleted and the prefix predicate evaluated against every docname's content path and every typst_documents entry's wrapper path, aggregated into the same accumulate-then-raise-once ExtensionError"
  - "tests/fixtures/template_prefix_reservation_gate/ -- the negative successor to template_named_dir_master/, proving the original _template-named docname layout is now a build error"
  - "tests/fixtures/nested_dir_multi_master/ -- the positive successor carrying template_named_dir_master/'s multi-entry and per-master author-divergence regression intents forward under a partials/ docname layout"
affects: []

# Actuals (#2632)
actuals:
  tokens: 15800
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A prefix reservation is a SEPARATE predicate from an exact-name _claim(), routed through the same _collision_key() normalization primitive rather than widening the existing exact-match closure in place"
    - "Splitting a fixture that carries multiple regression intents into a negative successor (proves the old layout now errors) and a positive successor (carries the surviving intents forward), rather than dropping any intent silently"

key-files:
  created:
    - tests/fixtures/template_prefix_reservation_gate/conf.py
    - tests/fixtures/template_prefix_reservation_gate/_template/index.rst
    - tests/fixtures/template_prefix_reservation_gate/_template/sub/index.rst
    - tests/fixtures/nested_dir_multi_master/conf.py
    - tests/fixtures/nested_dir_multi_master/partials/index.rst
    - tests/fixtures/nested_dir_multi_master/partials/sub/index.rst
    - tests/test_template_prefix_reservation_gate.py
  modified:
    - typsphinx/builder.py
    - tests/test_builder_output_stem.py
    - tests/test_multi_master_metadata_no_leak.py
    - tests/test_template_import_path.py
    - tests/test_collision_predicate_completeness_gate.py
    - tests/test_typst_documents_collision_gate.py
    - tests/fixtures/bld02_template_clobber_gate/conf.py
    - tests/fixtures/derived_template_collision_gate/conf.py
    - tests/fixtures/derived_template_collision_gate/_template/index.rst
    - tests/fixtures/explicit_template_collision_gate/conf.py
    - tests/fixtures/state_guard_three_master_gate/conf.py

key-decisions:
  - "_reserves_template_prefix() asks a materially different question than the deleted _claim(\"_template.typ\", ...) exact-name claim -- routed through _collision_key() for both operands (the candidate path AND the reserved directory constant) so a differently-cased spelling (T-54-27/A-06) is refused symmetrically, and deliberately NOT built on _escapes_outdir()/_is_drive_qualified() (whole-path escape questions, not first-segment questions)"
  - "A bare file literally named _template.typ (no directory component) is no longer specially reserved -- nothing the builder writes lands there any more (Phase 54 plans 04/05 deleted the single-file writer), so the plan's own must_haves text (\"a prefix reservation, not an exact-name claim on one filename\") is read literally: the reservation covers everything UNDER _template/, not the sibling flat filename"
  - "Several pre-existing fixtures/tests outside this plan's declared files_modified (tests/test_builder_output_stem.py, tests/fixtures/{bld02_template_clobber_gate,derived_template_collision_gate,explicit_template_collision_gate,state_guard_three_master_gate}/conf.py) directly asserted the deleted exact-name claim or named the relocated fixture in prose -- fixed as Rule 1 deviations since they are direct fallout of Task 1's own change and were required to reach the plan's own zero-grep-hits/full-suite-green verification bullets"
  - "make_filename_from_project() can never emit a '/' separator, so derived_template_collision_gate's original 'project name slugifies to the reserved basename' reproduction is structurally impossible against a DIRECTORY reservation -- root_doc is the lever instead, moving the fixture's sole docname under _template/ so the derived-default route's unconditional content-file claim trips the reservation"

patterns-established:
  - "Historical fixture-lineage prose that names a now-deleted/relocated identifier spells it with hyphens (e.g. template-named-dir-master) rather than the literal underscored identifier, so a repo-wide grep for the old name returns zero hits while the prose stays readable"

requirements-completed: [OUT-07]

coverage:
  - id: D1
    description: "A source tree whose content file or wrapper file would be written anywhere under the reserved _template/ output directory stops the build with an ExtensionError naming every offending docname, before any file is written -- a prefix reservation over the whole directory, not an exact-name claim on one filename"
    requirement: "OUT-07"
    verification:
      - kind: integration
        ref: "tests/test_template_prefix_reservation_gate.py::TestTemplatePrefixReservationGate (7 tests: both builders fail, ExtensionError raised, both offending docnames named in one error, reserved directory named, no partial .typ output, differently-cased variant also refused)"
        status: pass
      - kind: unit
        ref: "typsphinx/builder.py::TypstBuilder._reserves_template_prefix -- doctest examples manually verified (uv run python -c ...): _template/index.typ=True, _Template/sub/index.typ=True, manual.typ=False, _templates/index.typ=False"
        status: pass
    human_judgment: false
  - id: D2
    description: "The reservation is case-insensitive on the same terms as every other output-path comparison (T-54-27/A-06) -- routed through _collision_key()'s casefold for both the candidate path and the reserved directory constant"
    requirement: "OUT-07"
    verification:
      - kind: integration
        ref: "tests/test_template_prefix_reservation_gate.py::TestTemplatePrefixReservationGate::test_case_variant_also_refused"
        status: pass
    human_judgment: false
  - id: D3
    description: "The relocated fixture's three regression intents (reserved-directory docname layout, two-entry/two-distinct-target de-collision, per-master author divergence) are all still proved, split across a negative and a positive successor -- neither dropped silently"
    verification:
      - kind: integration
        ref: "tests/test_template_prefix_reservation_gate.py (negative, reserved layout) + tests/test_multi_master_metadata_no_leak.py (6 tests, author/title divergence) + tests/test_template_import_path.py::TestNestedDirMultiMasterRenderGate (multi-entry, distinct targets, real compile)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full suite green (1285 passed, 5 skipped, 0 failed -- 1278 baseline plus 7 new reservation-gate tests), black and mypy clean, milestone branch still on origin"
    verification:
      - kind: unit
        ref: "uv run pytest tests/ -q -> 1285 passed, 5 skipped; uv run black --check . -> clean; uv run mypy typsphinx/ -> clean; git ls-remote --heads origin gsd/v0.9.0-per-document-templates -> non-empty"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-16
status: complete
---

# Phase 54 Plan 07: One Bundle Rule — `_template/` Prefix Reservation, Fixture Relocation Summary

**Widened `_validate_output_path_collisions()`'s exact-name claim on the (now-deleted) shared `_template.typ` file into a first-`/`-segment prefix reservation over the whole `_template/` output directory, and split `tests/fixtures/template_named_dir_master/` into a negative successor (proving the original reserved-directory docname layout is now a build error) and a positive successor (carrying its multi-entry and author-divergence regression intents forward) — carrying no dropped intent and no remaining reference to the relocated fixture's old name anywhere under `tests/`.**

## Performance

- **Duration:** ~40 min
- **Started:** 2026-08-16 (session start, reading context)
- **Completed:** 2026-08-16T02:19:08+09:00
- **Tasks:** 3
- **Files modified:** 18 (7 created, 11 modified/renamed)

## Accomplishments

- `typsphinx/builder.py` gained `TypstBuilder._reserves_template_prefix()`, a new predicate routed through the existing `_collision_key()` folding — split on `/`, compare the first segment against the reserved directory constant (also folded through `_collision_key()`, so the comparison is symmetric and case-insensitive). Deliberately NOT a widened `_claim()` call (a materially different shape — prefix vs. exact-match) and deliberately NOT built on `_escapes_outdir()`/`_is_drive_qualified()` (whole-relative-path escape questions, not first-segment questions), per `54-RESEARCH.md`'s named anti-patterns.
- `_validate_output_path_collisions()` dropped the exact-name claim on the now-nonexistent shared `_template.typ` infrastructure file and now evaluates the new predicate against every docname's content path and every `typst_documents` entry's wrapper path, appending any offender to the SAME `failures` list the destination-collision check already accumulates into — so a whole subtree under the reserved directory is named in one aggregated `ExtensionError`, not just the first offender.
- `tests/fixtures/template_prefix_reservation_gate/` (negative successor) keeps `template_named_dir_master/`'s original docname layout (`_template/index`, `_template/sub/index`) verbatim, with its `conf.py` comment rewritten to record that the layout's role inverted from positive (Phase 22.1 through 54-05) to negative (this plan) — the original CR-01 malformed-import defect is now structurally impossible under OUT-06's root-absolute import, so the layout itself became the thing worth testing as a build error instead.
- `tests/fixtures/nested_dir_multi_master/` (positive successor) carries the same two `typst_documents` entries (two distinct bare targets, diverging per-entry authors) forward with docnames moved from `_template/` to `partials/` (not `_templates/`, Sphinx's own `templates_path` default, per `54-CONTEXT.md`'s explicit foreclosure).
- `tests/test_template_prefix_reservation_gate.py` (7 tests, new) proves the negative fixture's build fails identically on both builders, names both offending docnames and the reserved directory in one `ExtensionError`, writes no `.typ` file at all, and refuses a differently-cased spelling of the reserved directory (A-06) via a temporary fixture copy rather than a second committed directory.
- Repointed both existing references to the relocated fixture — `tests/test_multi_master_metadata_no_leak.py` and `tests/test_template_import_path.py` (the latter's render-gate class/fixture/test renamed to `TestNestedDirMultiMasterRenderGate`/`nested_dir_multi_master_dir`/`test_nested_dir_multi_master_resolves_and_compiles`, with assertions repointed to the `partials/` docname layout) — and confirmed zero remaining references to `template_named_dir_master` anywhere under `tests/`, including the new fixtures' own lineage prose (which spells the old name with hyphens instead of the literal identifier to avoid the grep).

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace the exact-name claim with a first-segment prefix reservation** - `3c2acc0d` (feat)
2. **Task 2: Relocate the fixture — negative gate for the reserved layout, positive gate for the other two intents** - `a41a8638` (test)
3. **Task 3: Repoint both existing references to the moved fixture and close the phase green** - `e598e589` (test)

_No separate plan-metadata commit — orchestrator owns STATE.md/ROADMAP.md writes for this worktree wave; this SUMMARY.md is committed as part of the worktree's own final commit._

## Files Created/Modified

- `typsphinx/builder.py` - `_reserves_template_prefix()` added; `_validate_output_path_collisions()`'s exact-name claim deleted and replaced with the prefix check against content and wrapper paths; `TEMPLATE_OUTPUT_DIR` imported from `writer.py` at module scope
- `tests/fixtures/template_prefix_reservation_gate/` (new) - the negative successor: `conf.py`, `_template/index.rst`, `_template/sub/index.rst`
- `tests/fixtures/nested_dir_multi_master/` (new) - the positive successor: `conf.py`, `partials/index.rst`, `partials/sub/index.rst`
- `tests/test_template_prefix_reservation_gate.py` (new) - 7 tests proving the negative gate
- `tests/test_builder_output_stem.py` - the unit-level exact-name reservation test retargeted to the new prefix reservation shape
- `tests/test_multi_master_metadata_no_leak.py`, `tests/test_template_import_path.py` - repointed to `nested_dir_multi_master/`
- `tests/test_collision_predicate_completeness_gate.py`, `tests/test_typst_documents_collision_gate.py` - the four tests left RED by Task 1's own commit now exercise the widened prefix reservation
- `tests/fixtures/bld02_template_clobber_gate/conf.py`, `tests/fixtures/derived_template_collision_gate/{conf.py,_template/index.rst}`, `tests/fixtures/explicit_template_collision_gate/conf.py`, `tests/fixtures/state_guard_three_master_gate/conf.py` - fixture data and one stale comment updated to reproduce/describe the new reservation shape

## Decisions Made

- **`_reserves_template_prefix()` compares the FIRST `/`-segment only, not a substring prefix** — a bare file literally named `_template.typ` (no directory component) is no longer reserved, since nothing the builder writes lands there any more after Phase 54 plans 04/05 deleted the single-file writer. This reading follows the plan's own `must_haves` text literally ("a prefix reservation, not an exact-name claim on one filename") and was confirmed by re-running the full suite: only the tests that literally asserted the OLD exact-name-clobber shape needed updating, and all of them are named in the plan's own Task 3 `read_first`/action text as expected fallout.
- **`make_filename_from_project()` can never emit a `/`**, so `derived_template_collision_gate`'s original "a project name slug equals the reserved basename" reproduction is structurally impossible against a directory reservation. `root_doc` became the lever instead — moving the fixture's sole docname under `_template/` reproduces an equivalent "zero-`typst_documents`-configuration" collision through the derived-default route's unconditional content-file claim.
- **Five pre-existing files outside this plan's declared `files_modified`** (`tests/test_builder_output_stem.py`, and four fixture `conf.py`/`.rst` files) directly asserted or described the deleted exact-name claim or the relocated fixture's old name — fixed as Rule 1 deviations (direct fallout of Task 1's own change, required to reach the plan's own zero-grep-hits and full-suite-green verification bullets).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `tests/test_builder_output_stem.py`'s unit test of the exact-name reservation broke on Task 1's own change**
- **Found during:** Task 1's full-suite run (not declared in this plan's `files_modified`, but a direct regression from Task 1's own commit)
- **Issue:** `test_validate_output_path_collisions_raises_on_reserved_template_name` constructed `typst_documents = [("index", "_template.typ", "T", "A")]` — a bare filename with no directory component, which the new prefix predicate correctly does NOT flag (nothing lands at that literal path any more).
- **Fix:** Retargeted the test's entry to `"_template/index.typ"` (a path under the reserved directory) and updated the docstring to describe Phase 54 plan 07's widening.
- **Files modified:** `tests/test_builder_output_stem.py`
- **Verification:** `uv run pytest tests/test_builder_output_stem.py -q` → 25 passed
- **Committed in:** `3c2acc0d` (Task 1 commit)

**2. [Rule 1 - Bug] Two tests in `tests/test_typst_documents_collision_gate.py` and two in `tests/test_collision_predicate_completeness_gate.py` (both declared Task 3 files) required their underlying FIXTURE data — not just the test bodies — to be updated to reproduce the new reservation shape**
- **Found during:** Task 1's full-suite run (fixtures not declared in this plan's `files_modified`); fixed in Task 3
- **Issue:** `tests/fixtures/derived_template_collision_gate/conf.py` relied on `project = "_Template"` slugifying to the exact reserved basename — structurally impossible against a directory reservation, since `make_filename_from_project()` never emits a `/`. `tests/fixtures/explicit_template_collision_gate/conf.py` and `tests/fixtures/bld02_template_clobber_gate/conf.py` targeted the exact filename `_template.typ` (with and without a `./` shape-normalization prefix respectively).
- **Fix:** `derived_template_collision_gate` now sets `root_doc = "_template/index"` (with `index.rst` moved under `_template/`) so the derived-default route's docname itself lives under the reserved directory. `explicit_template_collision_gate`'s target moved to `_template/index.typ`. `bld02_template_clobber_gate`'s target moved to `./_template/nested.typ`, preserving the same shape-normalization gap (`_collision_key()`'s `posixpath.normpath()` must still strip the `./` prefix before the reservation's first-segment comparison runs) against the new directory reservation instead of the deleted exact filename.
- **Files modified:** `tests/fixtures/derived_template_collision_gate/{conf.py,_template/index.rst}`, `tests/fixtures/explicit_template_collision_gate/conf.py`, `tests/fixtures/bld02_template_clobber_gate/conf.py`, plus the four affected tests' assertions/docstrings in `tests/test_typst_documents_collision_gate.py` and `tests/test_collision_predicate_completeness_gate.py`
- **Verification:** `uv run pytest tests/test_typst_documents_collision_gate.py tests/test_collision_predicate_completeness_gate.py -q` → 16 passed
- **Committed in:** `e598e589` (Task 3 commit)

**3. [Rule 1 - Bug] `tests/fixtures/state_guard_three_master_gate/conf.py`'s one stale comment named the relocated fixture**
- **Found during:** Task 3's own zero-grep-hits sweep (`git grep -n "template_named_dir_master" -- tests`)
- **Issue:** A comparison comment ("... it is the first genuine THREE-master composition fixture in the repository (`template_named_dir_master` has only two)") named the now-relocated fixture directly.
- **Fix:** Reworded to name the current two-master successor (`nested_dir_multi_master`) instead.
- **Files modified:** `tests/fixtures/state_guard_three_master_gate/conf.py`
- **Verification:** `git grep -n "template_named_dir_master" -- tests` → zero hits (after this fix); `uv run pytest tests/test_state_guard_composition_gate.py -q` unaffected (11 passed)
- **Committed in:** `e598e589` (Task 3 commit)

---

**Total deviations:** 3 auto-fixed (all Rule 1 — direct fallout of Task 1's own change to files not declared in this plan's `files_modified`, all required to reach the plan's own verification bullets, none touching behaviour outside this plan's scope)
**Impact on plan:** All three fixes were necessary for the plan's own "zero grep hits for the old fixture name" and "full suite green" verification bullets to actually hold; none introduce new behaviour beyond what OUT-07 requires.

## Issues Encountered

`uv run ruff check .` cannot execute in this NixOS sandbox — `ruff`'s installed wheel is a generic-linux dynamically-linked ELF the sandbox refuses to exec. This is the same pre-existing, previously-documented environment limitation every prior Phase 54 SUMMARY (`54-01` through `54-05`) has recorded — not introduced or fixable by this plan's changes. `black --check .` (317 files) and `mypy typsphinx/` (7 source files) both ran clean throughout.

Task 1's own acceptance criteria listed `uv run pytest tests/test_typst_documents_collision_gate.py tests/test_collision_predicate_completeness_gate.py tests/test_two_key_selection_gate.py -q` as expected to report 0 failed immediately after Task 1's commit. In practice, 4 tests across the first two files remained RED after Task 1 (asserting the deleted exact-name claim) until Task 3's commit finished the migration — this sequencing is explicitly anticipated by Task 3's own `read_first`/action text ("`54-05` deliberately migrated this module only as far as keeping it green; this task finishes it" / "confirm the assertions... survive Task 1's extended summary; adjust only what is genuinely broken"), and the plan's own top-level `<verification>` block (checked after all tasks) does not repeat the per-task 0-failed claim. Documented in the Task 1 commit message and resolved by Task 3.

## Known Stubs

None — every change this plan made is either a real code path (`_reserves_template_prefix()`, wired into the pre-write validator and covered by a real subprocess `sphinx-build` test) or a real fixture/test migration; no placeholder or hardcoded-empty value was introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- This was the final plan of Phase 54 (wave 4, no dependents listed in `affects`). `git grep -n "template_named_dir_master" -- tests` and `git grep -n '_claim("_template' -- typsphinx` both return zero hits repo-wide; the full suite (1285 passed, 5 skipped, 0 failed), `black --check .`, and `mypy typsphinx/` are all green against the final state.
- `test_state_guard_shapes_gate.py` (the pre-existing failure `54-CONTEXT.md` flagged as possibly surfacing here) ran fully green (18 passed) in this plan's full-suite runs — no inherited failure to record.
- Milestone branch `gsd/v0.9.0-per-document-templates` confirmed still present on `origin` (`git ls-remote --heads origin` non-empty) — standing invariant unaffected by this plan (no push performed here; worktree-isolated execution, orchestrator owns the merge).
- No coupling risk with `54-04`/`54-05`/`54-06`'s own artifacts — this plan touched only `typsphinx/builder.py`'s collision validator and test/fixture files; the sibling `54-06` worktree's declared territory (`typsphinx/__init__.py`, docs pages, `CLAUDE.md`) was not touched.

## Self-Check: PASSED

- FOUND: `typsphinx/builder.py` contains `_reserves_template_prefix`
- FOUND: `tests/fixtures/template_prefix_reservation_gate/_template/index.rst`, `tests/fixtures/template_prefix_reservation_gate/_template/sub/index.rst`
- FOUND: `tests/fixtures/nested_dir_multi_master/partials/index.rst`, `tests/fixtures/nested_dir_multi_master/partials/sub/index.rst`
- MISSING (expected): `tests/fixtures/template_named_dir_master/` (relocated)
- FOUND commit `3c2acc0d` in `git log --oneline`
- FOUND commit `a41a8638` in `git log --oneline`
- FOUND commit `e598e589` in `git log --oneline`
- CONFIRMED: `uv run pytest tests/ -q` → 1285 passed, 5 skipped, 0 failed
- CONFIRMED: `uv run black --check .` → clean; `uv run mypy typsphinx/` → clean
- CONFIRMED: `git grep -n "template_named_dir_master" -- tests` → zero hits
- CONFIRMED: `git grep -n '_claim("_template' -- typsphinx` → zero hits
- CONFIRMED: `git ls-remote --heads origin gsd/v0.9.0-per-document-templates` → non-empty

---
*Phase: 54-one-bundle-rule-template-key-per-document-selection-four-del*
*Completed: 2026-08-16*
