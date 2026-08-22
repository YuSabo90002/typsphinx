---
phase: 53-template-registry-foundation
plan: 03
subsystem: builder/writer
tags: [sphinx, typst, template-registry, validation, extension-error]

# Dependency graph
requires:
  - "53-02: typsphinx/template_registry.py's TemplateRegistryEntry, RESERVED_REGISTRY_KEY, resolve_template_registry(), resolve_registry_key() (no validation yet)"
provides:
  - "resolve_template_registry(): CONF-18's seven-case key-shape denylist, CONF-16's reserved-key check, CONF-15's template/package xor, CONF-17's _violates_conf17() path arithmetic, D-08's per-key existence check -- all accumulated into one independent ExtensionError, order-independent via sorted() iteration (D-03/D-05/D-09)"
  - "resolve_registry_key(): CONF-14's unregistered-key raise (naming sorted(registry.keys())) and D-06's non-str element [4] raise"
  - "_is_windows_reserved_name(), _has_case_collision() (routes through TypstBuilder._collision_key() via a local import), _validate_registry_key_shape(), _violates_conf17() -- the module's new private predicates"
  - "tests/test_template_registry.py: 46 new tests (11 -> 57) covering CONF-14..18, D-06, D-08, D-09"
affects: [53-04, 53-05]

# Actuals (#2632)
actuals:
  tokens: 8821
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "accumulate-then-raise-once validation, mirroring _validate_output_path_collisions() through an independent ExtensionError (D-03)"
    - "local (function-body) import to reuse TypstBuilder._collision_key() without a circular module-level import"
    - "denylist enumeration with a fixed check order and a module-level reason-count constant assertable by an enumeration test"

key-files:
  created: []
  modified:
    - typsphinx/template_registry.py
    - tests/test_template_registry.py

key-decisions:
  - "_has_case_collision() imports TypstBuilder locally, inside the function body, not at module scope -- builder.py already imports template_registry.py at ITS module scope, so a module-scope reverse import would deadlock the import graph. By the time this function runs, typsphinx.builder is always already fully imported."
  - "CONF-17 and D-08 checks are two structurally independent `if` statements (never if/elif), so a template value violating both reports both reasons in one raise (D-09), matching the plan's explicit prohibition on short-circuiting."
  - "Renamed two test fixture template names (only_template.typ -> solo_tpl.typ; no_such_global_template.typ -> no_such_global_tpl.typ) to avoid an accidental grep(_template\\.typ) match that would have silently inflated the protected 32-file regression-net count to 33."
  - "The seven key-shape rejection reasons and their check order are exposed via a module-level _KEY_SHAPE_REJECTION_CASES constant so an enumeration test can assert 'exactly seven' rather than relying on manual review."

requirements-completed: [TPL-01, TPL-05, CONF-14, CONF-15, CONF-16, CONF-17, CONF-18]

coverage:
  - id: D1
    description: "CONF-18's seven-case key-shape denylist: empty/whitespace-only, '.'/'..', path separators, Windows reserved device names (case-folded, with/without extension), trailing dot, trailing space, case collision via TypstBuilder._collision_key() -- each with its own case-specific message; the four deliberately-NOT-rejected shapes (Windows-illegal punctuation, control character, leading dot, interior whitespace) stay accepted; COM0/LPT0/ICONIC negative controls confirmed not reserved"
    requirement: CONF-18
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py::test_registry_key_shape_denylist_case_raises (13 parametrized cases), ::test_registry_two_keys_differing_only_by_case_raises, ::test_registry_key_deliberately_accepted_shapes_resolve_without_raising (4 parametrized), ::test_registry_key_reserved_name_boundary_not_rejected (3 parametrized), ::test_key_shape_validator_exposes_exactly_seven_distinct_rejection_reasons"
        status: pass
    human_judgment: false
  - id: D2
    description: "CONF-16: a user-defined key equal to the literal 'typst' raises; 'Typst'/'TYPST' resolve without raising (case-collision check compares only registered keys, never the synthesized built-in)"
    requirement: CONF-16
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py::test_registry_key_literal_typst_raises, ::test_registry_key_case_variant_of_typst_resolves_without_raising"
        status: pass
    human_judgment: false
  - id: D3
    description: "CONF-15: a definition carrying both template and package raises; only template, only package, or neither all resolve"
    requirement: CONF-15
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py::test_definition_with_both_template_and_package_raises, ::test_definition_with_template_xor_package_or_neither_resolves"
        status: pass
    human_judgment: false
  - id: D4
    description: "CONF-17: a template whose resolved parent directory is srcdir itself, or an ancestor of srcdir, raises; a subdirectory, a sibling reached via .., and an absolute path outside srcdir all stay legal"
    requirement: CONF-17
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py::test_conf17_template_parent_is_srcdir_itself_raises, ::test_conf17_template_parent_is_ancestor_of_srcdir_raises, ::test_conf17_template_under_subdirectory_of_srcdir_resolves, ::test_conf17_template_in_sibling_directory_resolves, ::test_conf17_absolute_template_path_outside_srcdir_resolves"
        status: pass
    human_judgment: false
  - id: D5
    description: "D-08/D-09: a user-defined key's nonexistent template raises; the built-in typst key's nonexistent global template does NOT raise (untouched warn-and-fallback); a template that both violates CONF-17 and does not exist reports both reasons in one raise"
    requirement: CONF-17
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py::test_user_defined_key_template_names_nonexistent_file_raises, ::test_builtin_typst_key_nonexistent_global_template_does_not_raise, ::test_conf17_and_not_found_both_reported_in_one_raise"
        status: pass
    human_judgment: false
  - id: D6
    description: "D-03/D-05: three independently-broken keys produce exactly one ExtensionError naming all three, byte-identical across two different dict insertion orders"
    requirement: TPL-01
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py::test_three_independently_broken_keys_raise_once_order_independently"
        status: pass
    human_judgment: false
  - id: D7
    description: "CONF-14: an unregistered registry key raises naming sorted(registry.keys()); an empty registry lists ['typst'] not []; the lookup is exact str equality (Paper != paper)"
    requirement: CONF-14
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py::test_resolve_registry_key_unregistered_key_raises_naming_registered_keys, ::test_resolve_registry_key_empty_registry_lists_typst_not_empty_list, ::test_resolve_registry_key_lookup_is_exact_str_equality_not_casefolded"
        status: pass
    human_judgment: false
  - id: D8
    description: "D-06: element [4] present but not a str (None, int, tuple) raises the same CONF-14-class error naming the offending value; an absent element [4] still resolves to the built-in typst key (TPL-04 regression guard); resolution order across masters does not change the raised message"
    requirement: TPL-05
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py::test_resolve_registry_key_non_str_element_four_raises (3 parametrized), ::test_resolve_registry_key_absent_element_four_still_resolves_to_typst, ::test_resolve_registry_key_bad_key_fails_identically_regardless_of_master_order"
        status: pass
    human_judgment: false
  - id: D9
    description: "Full regression net stays green: builder.py untouched, the collision/entry-metadata gates pass, the 32-file _template.typ-asserting file count is unchanged, and only tests/test_template_registry.py is a modified test file"
    verification:
      - kind: unit
        ref: "uv run pytest tests/ -q (1220 passed / 7 pre-existing baseline failures / 5 skipped); uv run pytest tests/test_typst_documents_collision_gate.py tests/test_collision_predicate_completeness_gate.py tests/test_builder_output_stem.py tests/test_entry_metadata_route_uniformity.py -q (all pass); git diff -- typsphinx/builder.py (empty); grep -rl _template\\.typ tests/ | wc -l (32)"
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-08-15
status: complete
---

# Phase 53 Plan 03: Template Registry Validation Summary

**Extended `resolve_template_registry()`/`resolve_registry_key()` with CONF-14..18's full validation pass -- a fixed-order seven-case key-shape denylist, the CONF-16 reserved-key check, CONF-15's template/package xor, CONF-17's path-arithmetic bundle-escape guard, and D-08's per-key existence check -- all accumulated into a single independent `ExtensionError`, adding 46 tests (11 -> 57) while leaving `typsphinx/builder.py` completely untouched.**

## Performance

- **Duration:** ~40 min
- **Completed:** 2026-08-15T09:05:00Z
- **Tasks:** 3/3
- **Files modified:** 2 (`typsphinx/template_registry.py`, `tests/test_template_registry.py`)

## Accomplishments

- **Task 1 (CONF-18/CONF-16):** Added `_WINDOWS_RESERVED_NAMES` (the exact 22-name set, `COM0`/`LPT0`/`CLOCK$` deliberately absent), `_is_windows_reserved_name()`, `_has_case_collision()` (routes through `TypstBuilder._collision_key()` via a local import to sidestep a circular import), and `_validate_registry_key_shape()` -- a fixed-order, denylist-only predicate covering exactly the seven CONF-18 cases, exposed via a countable `_KEY_SHAPE_REJECTION_CASES` constant. Wired CONF-16's literal-`"typst"` reserved-key check into the same accumulation pass. 36 tests (20 pre-existing + 16 new).
- **Task 2 (CONF-15/CONF-17/D-08/D-09):** Added `_violates_conf17()` -- a single `os.path.commonpath` comparison covering both "parent is srcdir" and "parent is an ancestor of srcdir" -- and wired CONF-15's template/package xor plus D-08's bare `os.path.isfile()` existence check into `resolve_template_registry()`'s per-declared-key loop. CONF-17 and the existence check are structurally independent `if` statements (not `elif`), so a template violating both reports both reasons in the same raise (D-09). The built-in `"typst"` key's existence is never checked (it is synthesized after the loop, never from `declared`), preserving `resolve_template()`'s existing warn-and-fall-back path. 13 new tests, plus 2 pre-existing tests updated to create real backing files so D-08's new existence check does not regress them.
- **Task 3 (CONF-14/D-06):** Extended `resolve_registry_key()` to raise `ExtensionError` for a `str` key absent from the registry (naming `sorted(registry.keys())`, exact equality -- `"Paper"` never satisfies `"paper"`) and for a present-but-non-`str` element `[4]` (`None`/int/tuple -- the same CONF-14-class error, never joining `_is_usable_typst_documents_entry()`'s tolerate-and-skip contract, never coerced to the built-in key). An absent element `[4]` still resolves to `"typst"` (TPL-04 regression guard, re-tested). 8 new tests.

## Task Commits

Each task was committed atomically:

1. **Task 1: CONF-18's seven-case key-shape denylist and CONF-16's reserved key** - `36afe601` (feat)
2. **Task 2: CONF-15's xor, CONF-17's path arithmetic, and D-08's existence check** - `81925abf` (feat)
3. **Task 3: CONF-14's unregistered key and D-06's non-str element [4]** - `eb3093b3` (feat)

_No plan-metadata commit beyond SUMMARY.md's own commit -- per the worktree-executor instructions, this plan runs inside an isolated worktree; the orchestrator applies STATE.md/ROADMAP.md/REQUIREMENTS.md updates centrally after merge._

## Files Created/Modified

- `typsphinx/template_registry.py` - added `_WINDOWS_RESERVED_NAMES`, `_KEY_SHAPE_REJECTION_CASES`, `_is_windows_reserved_name()`, `_has_case_collision()`, `_validate_registry_key_shape()`, `_violates_conf17()`; extended `resolve_template_registry()`'s validation pass and `resolve_registry_key()`'s raise branches.
- `tests/test_template_registry.py` - 46 new tests across the three tasks; 2 pre-existing tests updated to create real backing template files (D-08 compatibility); 2 fixture filenames renamed to avoid an accidental `_template.typ` grep-count collision.

## Decisions Made

- **Local (function-body) import for `_has_case_collision()`.** `builder.py` imports `template_registry.py` at module scope; a module-scope reverse import (`from typsphinx.builder import TypstBuilder` at the top of `template_registry.py`) would deadlock the import graph. Importing `TypstBuilder` inside the function body is safe because by the time this function is CALLED at runtime, `typsphinx.builder` has always already finished importing this module. This satisfies ROADMAP SC#4's "route through the SAME comparison, not a re-derived one" requirement without relocating `_collision_key()` out of `builder.py` (which would have exceeded this plan's `typsphinx/template_registry.py`-only file scope).
- **CONF-17 and D-08 as two independent `if` statements, never `elif`.** This is what makes D-09's "both failures reported in one raise" possible for a template value that is both CONF-17-violating and nonexistent.
- **Two pre-existing 53-02 tests needed real backing files.** `test_two_entries_naming_same_user_defined_key_share_one_object` and `test_user_defined_key_omitting_template_function_gets_none_not_inherited` declared `template` paths that did not exist on disk; Task 2's new D-08 existence check would have made them raise. Created the referenced files (in subdirectories, to also avoid tripping CONF-17) rather than weakening the new check -- these are this plan's OWN test file, not the protected 32-file `_template.typ` regression net.
- **Renamed two fixture filenames** (`only_template.typ` -> `solo_tpl.typ`; `no_such_global_template.typ` -> `no_such_global_tpl.typ`) after discovering they accidentally matched the phase's protected `grep -rl "_template\.typ" tests/` count, inflating it from 32 to 33. Verified back to 32 after the rename.

## Deviations from Plan

### Auto-fixed Issues

None -- no bug, missing-critical-functionality, or blocking issue required a Rule 1/2/3 fix beyond ordinary TDD iteration (writing tests first, observing RED, implementing to GREEN, as the plan itself directs). The grep-count and pre-existing-test-compatibility issues above were caught and fixed during this plan's own TDD loop, not discovered as separate defects after the fact.

### Noted, Not Auto-fixed (out of scope)

**1. [Scope boundary, carried from 53-01/53-02] Pre-existing `test_state_guard_shapes_gate.py` failures**
- **Found during:** every full-suite run in this plan (`uv run pytest tests/ -q`).
- **Issue:** 7 parametrized tests fail with `FileNotFoundError` reading a path the v0.8.0 milestone archival (`2ea4db0f`) relocated -- unrelated to this plan's scope, already logged in `deferred-items.md` and `WINDOWS.md` by plan 53-01.
- **Action taken:** none (already tracked). Re-confirmed the failure set is unchanged (still exactly these 7) across every full-suite run in this plan.

---

**Total deviations:** 0 auto-fixed; 1 noted/deferred (out of this plan's scope, carried forward unchanged).

## Issues Encountered

None beyond the one noted deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

TPL-01, TPL-05, CONF-14, CONF-15, CONF-16, CONF-17, and CONF-18 are all functionally complete and covered by 46 new passing tests (57 total in `tests/test_template_registry.py`). `typsphinx/builder.py` is untouched by this plan -- confirmed via `git diff`, and via the collision/entry-metadata gate tests passing unchanged -- so plan 53-04 (working in `template_engine.py`/`test_template_engine.py`) and this plan should merge without conflict. The full suite's failure set stays exactly the 7-test pre-existing baseline; the protected `_template.typ`-asserting 32-file count is unchanged. Plan 53-05's full four-shape SC#2 byte-identity measurement against `53-RED-EVIDENCE.md` remains open (not this plan's job -- this plan added validation only, on the new `typst_document_templates` config surface; it deliberately left the existing `typst_template`/`typst_package`/`typst_template_function` globals' behaviour for the `"typst"` key untouched, per D-08).

---
*Phase: 53-template-registry-foundation*
*Completed: 2026-08-15*

## Self-Check: PASSED

- FOUND: `typsphinx/template_registry.py`
- FOUND: `tests/test_template_registry.py`
- FOUND: `.planning/phases/53-template-registry-foundation/53-03-SUMMARY.md`
- FOUND commit `36afe601` (Task 1)
- FOUND commit `81925abf` (Task 2)
- FOUND commit `eb3093b3` (Task 3)
