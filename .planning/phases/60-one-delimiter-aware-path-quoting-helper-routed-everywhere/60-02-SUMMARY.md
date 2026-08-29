---
phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere
plan: 02
subsystem: message-formatting
tags: [python, builder, path-quoting, repr, sphinx-extension-diagnostics]

requires:
  - phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere (plan 01)
    provides: "typsphinx/pathfmt.py::quote_path() -- the delimiter-aware
      helper this plan wires into typsphinx/builder.py"
provides:
  - "typsphinx/builder.py: all 23 path-valued interpolations (the three
    57-11 message builders, _resolve_target_stem()'s path-refusal
    warning, the v0.8.0-era output-path collision family including two
    AMENDED target sites, _track_image()'s image-rehome warning, and
    _copy_bundle_directory()'s I/O messages) now route through
    quote_path() instead of !r / a hardcoded apostrophe delimiter"
  - "typsphinx/builder.py::_validate_output_path_collisions()'s
    target_text local -- a single isinstance(target, str) narrowing
    read at both amended message sites, so a non-str typst_documents
    target (None, int, list) still raises ExtensionError with its
    current repr() rendering instead of an unhandled TypeError"
  - "tests/test_builder_path_quoting_gate.py -- MSG-03's behavioural
    gate for builder.py's inline sites, 5 classes / 7 tests"
  - "three added single-quote-half methods (D-12) plus a
    SINGLE_QUOTE_SHAPED_PATH constant on the existing
    TestWindowsPathEscapingRegressionGuard in
    tests/test_templates_path_collision_gate.py, by pure addition only"
  - "60-02-EVIDENCE.md -- plan base SHA, discovery grep, per-family RED
    transcripts, the two-tree non-str-target pin, GREEN transcripts,
    RED-first ledger, measured zero-test-edit proof, known gate gaps,
    and the wave-3 handoff"
affects: [60-05-acceptance]

actuals:
  tokens: 15500
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "One target_text binding read at two message sites inside the
      same method, rather than a duplicated inline conditional --
      matches the existing three-extracted-message-builder discipline
      one level down, and keeps a type-narrowing decision from
      drifting between two call sites reading the same value."
    - "Behavioural RED recorded per site in the shape that site's
      pre-fix defect actually produces: the doubled-backslash shape
      for every !r site, and the single-quote-closes-delimiter-early
      shape (not backslash-doubling, already green since Phase 57) for
      the three extracted message builders -- D-12."

key-files:
  created:
    - tests/test_builder_path_quoting_gate.py
  modified:
    - typsphinx/builder.py
    - tests/test_templates_path_collision_gate.py
    - .planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-02-EVIDENCE.md

key-decisions:
  - "Implemented the planner-surfaced type-narrowing exactly as specified: _is_usable_typst_documents_entry() constrains only entry[0] (the docname) to str, leaving entry[1] (the target) unconstrained -- so _validate_output_path_collisions() binds target_text = quote_path(target) if isinstance(target, str) else repr(target) once and reads it at both amended message sites (:1192, :1199), keeping a today-warned config typo (None/int/list target) as an ExtensionError rather than an unhandled TypeError."
  - "Routed the image-rehome warning's relocation key (D-08c) despite its variable name being 'key' -- it is the post-Phase-59 relative path _typst_converted/{digest}-{basename}, not the registry key SC#3 protects; left every actual registry-key interpolation (key, existing_key, declared_key, RESERVED_REGISTRY_KEY, the two summary joiners) untouched."
  - "Left _copy_bundle_directory()'s copy-failure except branch (src_file/dest_file inside the fatal-copy ExtensionError) routed but ungated in this plan -- reaching it needs a real shutil.copy2 failure on the resolved template file, not portably constructible as a unit test; recorded honestly in 60-02-EVIDENCE.md's Known gate gaps rather than skipped silently, with wave 3's repo-wide grep audit as its proof."

patterns-established:
  - "A wiring plan's own RED gate re-derives its assertion predicate locally (re.findall(r'\\\\\\\\+', message) inline in the new test module) rather than importing a sibling test module's helper class, keeping each wave-2 plan's gate self-contained and mergeable alongside the two sibling wiring plans in the same wave."

requirements-completed: [MSG-03]

coverage:
  - id: D1
    description: "All 23 path-valued interpolations in typsphinx/builder.py -- the three 57-11 message builders, _resolve_target_stem()'s target/fallback, the output-path collision family's relpath/content_relpath/wrapper_relpath/TEMPLATE_OUTPUT_DIR (both branches), _track_image()'s resolved_uri/key, and _copy_bundle_directory()'s src_file/dest_file/template_filename/src_dir/dest_dir -- route through quote_path() instead of !r or a hardcoded apostrophe delimiter."
    requirement: MSG-03
    verification:
      - kind: unit
        ref: "tests/test_builder_path_quoting_gate.py -- 5 classes / 7 tests"
        status: pass
      - kind: unit
        ref: "tests/test_templates_path_collision_gate.py -- 19 tests including 3 added single-quote methods"
        status: pass
    human_judgment: false
  - id: D2
    description: "The two target interpolations D-06's original enumeration missed (builder.py :1192 and :1199, inside _validate_output_path_collisions()) route through quote_path() via a single isinstance(target, str)-narrowed target_text binding, so a non-str typst_documents target still raises ExtensionError (never TypeError) with its current repr() rendering unchanged."
    requirement: MSG-03
    verification:
      - kind: unit
        ref: "tests/test_builder_path_quoting_gate.py::TestBuilderIdentifierQuotingControl -- both methods green before AND after the fix (60-02-EVIDENCE.md ## Non-str target characterization)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Each of the five message families (three 57-11 builders' single-quote half, _resolve_target_stem, _track_image's rehome warning, both output-path-collision branches, _copy_bundle_directory) was recorded FAILING against the unfixed tree before its wiring landed, in the shape its site actually admits."
    requirement: MSG-03
    verification:
      - kind: unit
        ref: "60-02-EVIDENCE.md -- RED sections + RED-first ledger, all 8 rows pointing at real transcripts"
        status: pass
    human_judgment: false
  - id: D4
    description: "tests/test_templates_path_collision_gate.py changed by pure addition (one constant, three methods, zero removed source lines), no other pre-existing test file changed at all, and the full suite, black --check, mypy typsphinx/, and the AST repr-census guard are all green."
    requirement: MSG-03
    verification:
      - kind: unit
        ref: "git diff --name-status against plan base SHA (1 A, 1 M with zero '-' lines); uv run pytest -q (1504 passed, 5 skipped); uv run black --check .; uv run mypy typsphinx/; uv run pytest tests/test_repr_census_guard.py -q"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every identifier-valued interpolation in typsphinx/builder.py (registry keys in every form, docnames, the whole-tuple config entry, the config doc-tuple) is measurably untouched -- docname!r count unchanged, and the negative grep for any routed name still under !r prints nothing."
    requirement: MSG-03
    verification:
      - kind: unit
        ref: "grep -cE '{docname!r}' typsphinx/builder.py -> 10; grep -nE '{(resolved_path|srcdir|...|TEMPLATE_OUTPUT_DIR)!r}' typsphinx/builder.py -> empty"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-29
status: complete
---

# Phase 60 Plan 02: builder.py Path-Quoting Wiring (MSG-03) Summary

**All 23 path-valued diagnostic interpolations in `typsphinx/builder.py` now route through `typsphinx/pathfmt.py::quote_path()`, including two `target` sites D-06's original enumeration missed, closed behind a RED-first gate at all five message families plus a type-narrowing control proven green before and after the fix.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-08-29T10:45:00Z (approx.)
- **Completed:** 2026-08-29T11:10:29Z
- **Tasks:** 3
- **Files modified:** 4 (1 created, 3 modified)

## Accomplishments

- `typsphinx/builder.py`'s three 57-11 message builders
  (`_conf17_violation_message`, `_templates_path_collision_message`,
  `_bundle_destination_collision_message`) now select their delimiter via
  `quote_path()` instead of a hardcoded apostrophe, so a path containing a
  literal single quote (e.g. `/home/O'Brien's Projects/...`) can no longer
  visually close the delimiter early — proven by three new single-quote
  methods added to the existing `TestWindowsPathEscapingRegressionGuard`.
- `_resolve_target_stem()`'s path-refusal warning, `_track_image()`'s
  image-rehome warning, both branches of `_validate_output_path_collisions()`
  (including the two AMENDED `target` sites at `:1192`/`:1199` D-06's
  original enumeration missed), and `_copy_bundle_directory()`'s two I/O
  error messages all route through `quote_path()` — a Windows-shaped path
  now shows single, not doubled, backslashes in every one of these
  diagnostics.
- A `target_text` binding (`quote_path(target) if isinstance(target, str)
  else repr(target)`) closes the gap the planner surfaced during planning:
  `_is_usable_typst_documents_entry()` never constrains the type of a
  `typst_documents` entry's target, so an unconditional route would have
  turned a today-warned config typo (`None`, an `int`) into an unhandled
  `TypeError` on every build. `TestBuilderIdentifierQuotingControl` proves
  this control is green both before and after the fix.
- Identifier-valued interpolations (registry keys in every form, docnames,
  the whole-tuple config entry) are measurably untouched — `docname!r`
  count stays at 10, and a negative grep for any routed name still under
  `!r` prints nothing.
- All five message families were recorded FAILING against the unfixed
  tree before their wiring landed, in the shape each site's defect
  actually produces (doubled backslashes for the `!r` sites, an
  early-closing single quote for the three extracted 57-11 builders) —
  full verbatim transcripts and a RED-first ledger are in
  `60-02-EVIDENCE.md`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Run the discovery grep, then commit MSG-03's behavioural gate RED at all five message families** - `f62788de` (test)
2. **Task 2: Route every path-valued interpolation in typsphinx/builder.py through quote_path()** - `3d2c6c96` (feat)
3. **Task 3: Record MSG-03's RED-first ledger, the zero-test-edit measurement, and the known gate gaps** - `1db98996` (docs)

## Files Created/Modified

- `tests/test_builder_path_quoting_gate.py` - new; MSG-03's behavioural gate for builder.py's inline (non-extracted) message sites, 5 classes / 7 tests
- `tests/test_templates_path_collision_gate.py` - added `SINGLE_QUOTE_SHAPED_PATH` constant + 3 single-quote-half test methods to the existing `TestWindowsPathEscapingRegressionGuard`, by pure addition
- `typsphinx/builder.py` - one new import (`from typsphinx.pathfmt import quote_path`), 23 interpolations routed through it, `target_text` narrowing added, three message-builder docstrings updated
- `.planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-02-EVIDENCE.md` - plan base SHA, discovery grep, per-family RED transcripts, the two-tree non-str-target pin, GREEN transcripts, RED-first ledger, measured zero-test-edit proof, known gate gaps, wave-3 handoff

## Decisions Made

- The `target_text` local is bound ONCE, immediately after `target = entry[1]`, and read at both of the two amended message sites (`:1192`'s collision-branch description and `:1199`'s reserved-directory-branch description) — one binding read at two sites, matching the "one place a message sentence is built" discipline the three extracted 57-11 message builders already embody, and guaranteeing the narrowing cannot drift between the two sites.
- `_resolve_target_stem()`'s `target`/`fallback` needed NO narrowing — its warning sits inside an `isinstance(target, str)` branch, so both values are already guaranteed `str` there (unlike the two `_validate_output_path_collisions()` sites, which read `entry[1]` directly with no such guard).
- `_copy_bundle_directory()`'s copy-failure `except` branch is routed but left without a behavioural gate in this plan, recorded explicitly in `60-02-EVIDENCE.md`'s Known gate gaps rather than silently skipped — reaching it needs a real `shutil.copy2` failure on the resolved template file, which is not portably constructible as a unit test; wave 3's repo-wide grep audit (SC#2) is its proof instead.

## Deviations from Plan

None - plan executed exactly as written, including the planner-surfaced `target_text` narrowing addendum (folded into task 2's own `<action>` and `<flagged_assumptions>`, not a deviation discovered during execution).

## Issues Encountered

None. `black` reformatted two whitespace-only lines (one in `typsphinx/builder.py`, one in the newly-created `tests/test_builder_path_quoting_gate.py`) during task 2's verification pass; re-run confirmed both files clean and no test content changed.

## User Setup Required

None - no external service configuration required. Zero new runtime dependencies, zero new `typst_*` config values.

## Next Phase Readiness

`typsphinx/builder.py` is fully wired for MSG-03. Wave 3's `60-05` acceptance plan can now run its
repo-wide discovery grep across all three wave-2 modules (`builder.py`, `writer.py` from `60-03`,
`template_registry.py` from `60-04`), confirm `template_registry.py:410` is measurably still `!r`
(SC#3), and re-derive the zero-test-edit proof against `58-REPR-CENSUS.md` for the whole phase. No
blockers. `60-02-EVIDENCE.md`'s `## Wave-3 handoff` section lists the exact grep commands, the
`quote_path(` count (27), and the full identifier-valued stays-unrouted list this module's audit
should check against.

---
*Phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere*
*Completed: 2026-08-29*
