---
phase: 53-template-registry-foundation
plan: 07
subsystem: infra
tags: [sphinx-extension, config-validation, template-registry, error-handling]

# Dependency graph
requires:
  - phase: 53-template-registry-foundation
    provides: resolve_template_registry(), _violates_conf17(), _validate_registry_key_shape() (plans 53-02/53-03/53-06)
provides:
  - "_violates_conf17() closes the cross-drive absolute-path ValueError crash (CR-02)"
  - "resolve_template_registry() accumulate loop closes the non-str key and non-dict definition AttributeError crashes (WR-02, WR-03)"
  - "A total sorted() iteration key over mixed registry key types, preserving D-03's all-str byte-identical determinism"
affects: [phase-54-one-bundle-rule]

# Actuals (#2632)
actuals:
  tokens: 3588
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Narrow try/except ValueError around a single os.path arithmetic call, mirroring builder.py's _track_image() D-07 cross-drive relpath() guard"
    - "Total sorted() key via a (not isinstance(k, str), k-or-repr(k)) tuple to make an accumulate-then-raise-once validation loop robust to heterogeneous input types without breaking existing message ordering"

key-files:
  created: []
  modified:
    - typsphinx/template_registry.py
    - tests/test_template_registry.py

key-decisions:
  - "Deliberately did NOT adopt 53-REVIEW.md's suggested repr(k) for both sort-key partitions -- repr() switches to double quotes for a string containing an apostrophe, which would silently reorder such a key relative to today's plain sorted() and break D-03's published byte-identical ordering. Used k (unwrapped) for the str partition instead."
  - "The non-str key guard is a TYPE GUARD placed as the first statement in the accumulate loop body, before the _validate_registry_key_shape() dispatch -- not an eighth entry in the frozen seven-case _KEY_SHAPE_REJECTION_CASES denylist (53-03-PLAN.md prohibition, D-02)."
  - "The second (build) loop at the end of resolve_template_registry() got a documentation-only comment, not a redundant second guard -- it is reachable only after the accumulate loop proves every key is a str and every definition is a dict-or-falsy."

requirements-completed: [CONF-15, CONF-17, CONF-18]

coverage:
  - id: D1
    description: "A legal cross-drive absolute template path (Windows) resolves or fails with this module's own ExtensionError, never a raw ValueError"
    requirement: CONF-17
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py#test_conf17_cross_drive_commonpath_valueerror_is_not_a_violation"
        status: pass
      - kind: unit
        ref: "tests/test_template_registry.py#test_conf17_cross_drive_valueerror_surfaces_as_extension_error_not_valueerror"
        status: pass
    human_judgment: false
  - id: D2
    description: "A non-str registry key stops the build with this module's own accumulated ExtensionError naming the offending key, never a raw AttributeError"
    requirement: CONF-18
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py#test_non_str_registry_key_raises_extension_error_not_attributeerror"
        status: pass
    human_judgment: false
  - id: D3
    description: "A truthy non-dict registry definition stops the build with this module's own accumulated ExtensionError naming the offending value; a falsy definition still normalizes and resolves"
    requirement: CONF-15
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py#test_non_dict_definition_raises_extension_error_not_attributeerror"
        status: pass
      - kind: unit
        ref: "tests/test_template_registry.py#test_falsy_definition_still_normalizes_and_resolves"
        status: pass
    human_judgment: false
  - id: D4
    description: "A heterogeneous key set (mixed int/str) stops the build with the module's ExtensionError, never sorted()'s TypeError, and D-03's byte-identical determinism survives the new ordering, including a mixed-type key set"
    requirement: CONF-18
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py#test_mixed_type_keys_raise_extension_error_not_sorted_typeerror"
        status: pass
      - kind: unit
        ref: "tests/test_template_registry.py#test_mixed_type_key_message_is_byte_identical_across_insertion_orders"
        status: pass
      - kind: unit
        ref: "tests/test_template_registry.py#test_three_independently_broken_keys_raise_once_order_independently"
        status: pass
    human_judgment: false
  - id: D5
    description: "A non-str key never reaches TypstBuilder._collision_key(): all_keys stays isinstance(key, str)-filtered, so a registry mixing a non-str key with two case-colliding str keys reports BOTH failures in one accumulated raise"
    requirement: CONF-18
    verification:
      - kind: unit
        ref: "tests/test_template_registry.py#test_non_str_key_is_excluded_from_case_collision_comparison"
        status: pass
    human_judgment: false

# Metrics
duration: 13min
completed: 2026-08-15
status: complete
---

# Phase 53 Plan 07: Registry Robustness Guards Summary

**Two narrow guards close every remaining raw-Python-exception crash path in `resolve_template_registry()`/`_violates_conf17()` — a cross-drive absolute template path, a non-`str` registry key, and a truthy non-`dict` definition all now surface as this module's own accumulated `ExtensionError`.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-08-15T10:47:54Z
- **Completed:** 2026-08-15T10:57:38Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `_violates_conf17()` now catches the `ValueError` `os.path.commonpath()` raises for two absolute paths on different Windows drives and returns `False` (legal, per D-07), mirroring `builder.py`'s established `_track_image()` cross-drive `relpath()` guard.
- `resolve_template_registry()`'s accumulate loop gained a non-`str` key type guard and a truthy non-`dict` definition guard, both feeding the same `failures` list and the same `typst_document_templates: N invalid definition(s): ...` message shape — no second error-message format was introduced.
- The loop's `sorted()` key is now total across mixed key types (`str`-before-non-`str` partition, then `str`-vs-`str` inside each partition) so a heterogeneous key set can no longer trip `sorted()`'s own `TypeError`, while the existing all-`str` ordering and D-03's byte-identical cross-insertion-order determinism are unchanged.
- `_KEY_SHAPE_REJECTION_CASES` stays exactly seven entries; `_validate_registry_key_shape()` is untouched and never sees a non-`str` key.
- Both `53-REVIEW.md` reproduction one-liners (`{42: {}}` and `{"report": "not-a-dict"}`) now raise `ExtensionError` instead of `AttributeError`, independently re-verified in this session.

## Task Commits

Each task was committed atomically:

1. **Task 1: Cross-drive absolute template path stops crashing CONF-17's predicate** - `8d45e0b5` (fix)
2. **Task 2: Non-str keys and non-dict definitions join the accumulated ExtensionError** - `eb69904f` (fix)

**Plan metadata:** commit pending (this SUMMARY + REQUIREMENTS.md, worktree mode — STATE.md/ROADMAP.md excluded, owned by orchestrator)

## Files Created/Modified
- `typsphinx/template_registry.py` - `_violates_conf17()` gains `except ValueError: return False`; `resolve_template_registry()` gains a total sort key, a non-`str` key guard, and a non-`dict` definition guard, all feeding the existing accumulate-then-raise-once pass
- `tests/test_template_registry.py` - 10 new tests (2 for Task 1, 8 for Task 2, one parametrized over 3 falsy values); all 65 pre-existing tests unmodified

## Decisions Made
- Deliberately did NOT use `53-REVIEW.md`'s suggested `repr(k)` for both sort-key partitions — `repr()` switches to double quotes for a string containing an apostrophe, which would silently reorder such a key relative to today's plain `sorted()` and break D-03's published byte-identical message ordering for any config that happens to have such a key. Used the raw key (`k`) for the `str` partition and `repr(k)` only for the non-`str` partition, where no pre-existing ordering guarantee exists to preserve.
- The non-`str` key guard is placed as a TYPE GUARD — the first statement in the accumulate loop body, before dispatch into `_validate_registry_key_shape()` — rather than as an eighth entry in `_KEY_SHAPE_REJECTION_CASES`, per `53-03-PLAN.md`'s locked prohibition (D-02) that the denylist stays at exactly seven cases.
- The second (build) loop at the end of `resolve_template_registry()` received a documentation comment recording its reachability argument (it only runs once `failures` is empty, by which point every key is a `str` and every definition is a `dict` or falsy) rather than a redundant second guard that could drift from the first.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' `<action>` sections were followed verbatim, including the explicit instruction not to use `repr(k)` for the `str` partition of the sort key.

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Both ⚠ WARNING rows in `53-VERIFICATION.md`'s Anti-Patterns table (`_violates_conf17()`'s cross-drive crash; the non-`str`/non-`dict` `AttributeError` pair) are closed.
- `53-REVIEW.md`'s CR-02, WR-02, and WR-03 are each discharged with a named, passing test.
- SC#3's framing sentence — "every malformed registry stops the build with a message naming the specific reason" — now holds over the module's whole input surface, not just the six shapes the resolver originally anticipated.
- Full suite: 1252 passed, 5 skipped, 0 failed (baseline 1242/5/0 + 10 new tests). `black --check` and `mypy typsphinx/template_registry.py` both clean.
- No blockers for Phase 54.

## Self-Check: PASSED

- FOUND: typsphinx/template_registry.py
- FOUND: tests/test_template_registry.py
- FOUND: .planning/phases/53-template-registry-foundation/53-07-SUMMARY.md
- FOUND commit: 8d45e0b5 (Task 1)
- FOUND commit: eb69904f (Task 2)

---
*Phase: 53-template-registry-foundation*
*Completed: 2026-08-15*
