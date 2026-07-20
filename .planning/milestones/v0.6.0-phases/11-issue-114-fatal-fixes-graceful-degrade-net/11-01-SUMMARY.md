---
phase: 11-issue-114-fatal-fixes-graceful-degrade-net
plan: 01
subsystem: translator
tags: [docutils, typst, sphinx, css-length, graphviz, inheritance_diagram]

# Dependency graph
requires:
  - phase: 10 (v0.5.0 admonition buffer-swap)
    provides: the `visit_title`/`depart_title` admonition buffer-swap idiom this plan's PATTERNS.md cited as precedent (not directly reused by this plan's code, but confirms the file's established conventions)
provides:
  - "_convert_length_to_typst() length-unit converter, wired into visit_image (FIG-01)"
  - "_visit_graphical_placeholder() shared graceful-degrade helper + visit_graphviz/visit_inheritance_diagram (DEG-01, DEG-02)"
affects: [11-02 (figure caption buffer-swap, same file), 11-03 (render-gate fixtures exercising both fixes), 12-14 (later node-handler phases)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Regex-based CSS length-unit conversion via allow-list dispatch (never a deny-list, never positional string-stripping)"
    - "Graceful-degrade placeholder: one logger.warning + native Typst rect()/text() block + raise nodes.SkipNode, sharing one helper across multiple out-of-scope node types"

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - tests/test_translator.py

key-decisions:
  - "Implemented the unit dispatch as an allow-list (%, em, pt, cm, mm, in pass through; px/bare-unitless and pc convert) with a single generic warn+drop fallback for everything else -- per D-02 and the RESEARCH.md session finding that docutils' CSS3_LENGTH_UNITS includes ch/rem/vw/vh/vmin/vmax/Q beyond the explicitly-named ex, all of which correctly fall into the same generic unknown branch"
  - "Confirmed sphinx.ext.graphviz.graphviz and sphinx.ext.inheritance_diagram.inheritance_diagram class names live via direct import before finalizing visit_graphviz/visit_inheritance_diagram method names (RESEARCH.md Assumption A1, now resolved)"
  - "Updated 3 pre-existing image path-adjustment unit tests that asserted the old buggy raw-px passthrough (e.g. 'width: 200px' in output) to assert the corrected pt-converted values -- those tests encoded the exact FIG-01 fatal bug as expected behavior"

patterns-established:
  - "_convert_length_to_typst(): pure regex-parsed unit converter following the _compute_relative_image_path docstring/doctest convention"
  - "_visit_graphical_placeholder(): shared degrade-with-visible-placeholder helper for out-of-scope graphical node types, distinct from the silent visit_index skip and from admonition/gentle-clues rendering"

requirements-completed: [FIG-01, DEG-01, DEG-02]

coverage:
  - id: D1
    description: "_convert_length_to_typst() converts px->pt (1px=0.75pt), bare unitless->px->pt, pc->pt (1pc=12pt); passes through %/em/pt/cm/mm/in unchanged; warns once and drops any other unit (ex/ch/rem/vw/vh/vmin/vmax/Q/malformed)"
    requirement: "FIG-01"
    verification:
      - kind: unit
        ref: "tests/test_translator.py#test_convert_length_px_to_pt"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py#test_convert_length_bare_unitless_treated_as_px"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py#test_convert_length_pc_to_pt"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py#test_convert_length_passthrough_units"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py#test_convert_length_unknown_unit_warns_and_drops"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py#test_convert_length_malformed_value_warns_and_drops"
        status: pass
    human_judgment: false
  - id: D2
    description: "visit_image routes both width and height through _convert_length_to_typst and omits the attribute entirely when the helper returns None; no raw px/unsupported unit ever reaches Typst output"
    requirement: "FIG-01"
    verification:
      - kind: unit
        ref: "tests/test_translator.py#test_image_with_attributes"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py#test_image_path_adjustment_root"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py#test_image_path_adjustment_nested"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py#test_image_path_adjustment_subdirectory"
        status: pass
    human_judgment: false
  - id: D3
    description: "graphviz and inheritance_diagram nodes each render a visible bordered native-Typst rect()/text() placeholder naming the node, emit exactly one logger.warning, and raise nodes.SkipNode before descending into children -- no raw DOT/diagram-spec source can leak"
    requirement: "DEG-01"
    verification:
      - kind: other
        ref: "manual interpreter check: graphviz().walkabout(translator) with DOT-source Text child produces only the rect() placeholder in output, confirming SkipNode prevents child descent (see plan Task 3 acceptance criteria; full real-compile no-leak proof deferred to Plan 11-03's render gate per plan scope)"
        status: pass
    human_judgment: false
  - id: D4
    description: "inheritance_diagram shares the same DEG-01 placeholder helper (DEG-02)"
    requirement: "DEG-02"
    verification:
      - kind: unit
        ref: "grep -q 'def visit_inheritance_diagram' typsphinx/translator.py"
        status: pass
    human_judgment: false

duration: ~15min
completed: 2026-07-12
status: complete
---

# Phase 11 Plan 01: FIG-01 Length Conversion + DEG-01/02 Graceful-Degrade Placeholder Summary

**New `_convert_length_to_typst()` regex-based CSS-length-to-Typst converter wired into `visit_image` (fixes Issue #114's fatal `width: 200px` compile abort), plus a shared `_visit_graphical_placeholder()` helper giving `graphviz`/`inheritance_diagram` a visible bordered Typst `rect()` block + one warning + clean `SkipNode` instead of leaking source or aborting**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-07-12
- **Tasks:** 3 (all autonomous, no checkpoints)
- **Files modified:** 2 (`typsphinx/translator.py`, `tests/test_translator.py`)

## Accomplishments

- `_convert_length_to_typst()`: new pure helper implementing the D-02 unit table exactly (px/unitless -> pt via 1px=0.75pt; pc -> pt via 1pc=12pt; %/em/pt/cm/mm/in pass through; any other unit, including the extended CSS3 set `ch`/`rem`/`vw`/`vh`/`vmin`/`vmax`/`Q` found during research, warns once and drops the dimension). Implemented as a regex-based allow-list, never a deny-list or positional string-strip.
- `visit_image` now routes both `:width:`/`:height:` through the converter and omits the attribute entirely on an unsupported unit — no raw CSS unit can ever reach Typst output again.
- `_visit_graphical_placeholder()` shared helper + `visit_graphviz`/`visit_inheritance_diagram`: each out-of-scope graphical node now emits exactly one `logger.warning` naming the node type, a visible bordered native-Typst `rect(text(...), stroke:, inset:, radius:)` placeholder, then `raise nodes.SkipNode` — never `_visit_admonition`/gentle-clues, never a silent skip, never descending into raw DOT/diagram-spec source.
- Confirmed the `graphviz`/`inheritance_diagram` node-class dispatch names live (`sphinx.ext.graphviz.graphviz.__name__ == "graphviz"`, `sphinx.ext.inheritance_diagram.inheritance_diagram.__name__ == "inheritance_diagram"`) before finalizing method names, resolving RESEARCH.md's open Assumption A1.
- 6 new fast unit tests for the length converter (including `caplog`-based exactly-one-warning assertions for the unknown-unit and malformed-value cases).

## Task Commits

Each task was committed atomically:

1. **Task 1a (RED): failing tests for `_convert_length_to_typst`** - `1849d8a` (test)
2. **Task 1b (GREEN): implement `_convert_length_to_typst`** - `2c04438` (feat)
3. **Task 2: wire converter into `visit_image`** - `69cd941` (fix)
4. **Task 3: DEG-01/DEG-02 graceful-degrade placeholder** - `8e07d26` (feat)

_Task 1 was `tdd="true"`; RED and GREEN gate commits both present, confirming TDD gate compliance (see below)._

## Files Created/Modified

- `typsphinx/translator.py` - Added `_TYPST_PASSTHROUGH_UNITS` module constant; new `_convert_length_to_typst()` method; rewired `visit_image`'s width/height emission; new `_visit_graphical_placeholder()`, `visit_graphviz()`, `visit_inheritance_diagram()` methods near `visit_index`.
- `tests/test_translator.py` - 6 new `test_convert_length_*` unit tests; updated 3 pre-existing image path-adjustment tests (`test_image_path_adjustment_root`, `_nested`, `_subdirectory`) to assert the corrected pt-converted width values instead of the old raw-px passthrough.

## Decisions Made

- Implemented unit dispatch as an allow-list, not a deny-list, so the full extended docutils CSS3 unit set (`ex`, `ch`, `rem`, `vw`, `vh`, `vmin`, `vmax`, `Q`) all correctly fall into one generic "unknown → warn + drop" branch without special-casing any of them individually, per D-02 and the RESEARCH.md session finding.
- Confirmed live node-class names (`graphviz`, `inheritance_diagram`) via a direct interpreter import before writing the `visit_*` method names, resolving the plan's required pre-check (Assumption A1).
- Updated 3 pre-existing unit tests that asserted the old buggy raw-`px` output (`"width: 200px" in output`) — these tests literally encoded the Issue #114 fatal bug as expected behavior; fixing them is required by Task 2's own acceptance criteria ("no verbatim node['width'] interpolation remains") and is a direct, in-scope consequence of the task's own file (Rule 1: auto-fix bug — the old assertions asserted the bug itself, not a separate concern).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated 3 pre-existing image tests asserting the raw-px fatal-bug behavior**
- **Found during:** Task 2 (wiring `_convert_length_to_typst` into `visit_image`)
- **Issue:** `test_image_path_adjustment_root`, `_nested`, and `_subdirectory` asserted `"width: 200px" in output` / `"width: 250px" in output` — i.e. they encoded the exact Issue #114 fatal-abort behavior (`width: 200px` raw output, which is invalid Typst syntax) as the expected/passing state.
- **Fix:** Updated the assertions to the correct converted pt values (`"width: 150pt"`, `"width: 187.5pt"`), matching the CSS-canonical `1px = 0.75pt` conversion now implemented.
- **Files modified:** `tests/test_translator.py`
- **Verification:** `pytest -m "not slow" -q` — full 419-test fast suite green.
- **Committed in:** `69cd941` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug fix carried into its own encoding test)
**Impact on plan:** Necessary and directly in-scope for Task 2's acceptance criteria ("no verbatim node['width']/node['height'] interpolation remains" and "no regression in existing image tests" — these 3 tests would have been the only *false* regressions, since they asserted the bug itself). No scope creep; no other files touched.

## Issues Encountered

None.

## TDD Gate Compliance

Task 1 (`tdd="true"`) followed the mandatory RED → GREEN sequence:
- RED: `1849d8a` `test(11-01): add failing tests for _convert_length_to_typst (FIG-01)` — confirmed failing (`AttributeError: 'TypstTranslator' object has no attribute '_convert_length_to_typst'`) before any implementation existed.
- GREEN: `2c04438` `feat(11-01): implement _convert_length_to_typst helper (FIG-01, D-02)` — all 6 new tests pass.
- No REFACTOR commit was needed (implementation was clean on first pass).

Gate sequence verified in git log: test commit precedes feat commit. Compliant.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- FIG-01 and DEG-01/DEG-02 are fully implemented and unit-tested; `visit_image` never emits a raw unsupported length unit, and `graphviz`/`inheritance_diagram` never leak source or abort the compile.
- Plan 11-02 (FIG-02 caption buffer-swap + `:target:` refid branch) is fully independent of this plan's changes — no shared state, safe to execute in the same wave or sequentially.
- Plan 11-03 (GATE-01 real-compile render-gate fixtures) can now exercise both this plan's fixes and Plan 11-02's fixes through a real `typst.compile()` — the fast unit tests here are necessary but (per D-04/Pitfall 9) not sufficient; the real-compile proof is explicitly deferred there, per this plan's own `<verification>` section.
- No blockers identified.

## Self-Check: PASSED

All task commits (`1849d8a`, `2c04438`, `69cd941`, `8e07d26`) and the summary commit (`22b6961`) verified present in `git log`. `typsphinx/translator.py` verified to contain `_convert_length_to_typst` and `_visit_graphical_placeholder`.

---
*Phase: 11-issue-114-fatal-fixes-graceful-degrade-net*
*Completed: 2026-07-12*
