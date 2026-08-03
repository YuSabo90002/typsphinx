---
phase: 38-structural-indentation-info-fields
plan: 03
subsystem: testing
tags: [pytest, typst-compile, sphinx-typst, gate-fixture, sig-08, buffer-swap]

# Dependency graph
requires:
  - phase: 37-signature-typography-the-desc-family
    provides: "SIG-08 emission-position-marker suppression (depart_desc, _desc_break_marker) and its signature_break_and_arrow_gate fixture"
provides:
  - "A RED conjunction assertion (TestD10BodyWrapperBreakMarkerGate) proving D-10's obligation with a fixture, not an assumption"
  - "38-EMISSION-CONTRACT.md section 6.2's marker-propagation resolution, adopted at plan time and proven RED-worthy"
  - "The folded buffer-swap todo's fixture (desc inside a glossary definition, nested desc inside that, a top-level control, and a recorded-not-constructible fourth control), measured honestly GREEN pre-phase"
  - "38-GATE-EVIDENCE-03.md recording both outcomes verbatim"
affects: ["38-05 (lands visit_desc_content/depart_desc_content per contract section 2, with the section 6.2 propagation fix and the depart_desc docstring correction)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Conjunction RED assertion: two independently-inconclusive halves (token presence + count) combined into one test so the RED signal cannot be satisfied by accident at any point in a phase's life"
    - "Honest-measurement fixture: build first, measure second, record whichever outcome (RED or GREEN) actually occurs rather than presuming the todo's predicted outcome"

key-files:
  created:
    - tests/fixtures/desc_break_marker_buffer_swap_gate/conf.py
    - tests/fixtures/desc_break_marker_buffer_swap_gate/index.rst
    - tests/test_desc_break_marker_buffer_swap_gate.py
    - .planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE-03.md
  modified:
    - tests/test_signature_break_and_arrow_gate.py

key-decisions:
  - "D-10 discharged with a conjunction assertion (wrapper tokens present AND break count == 8) rather than a single count check, because the count alone is already 8 and correct pre-phase and cannot be RED for the right reason in isolation"
  - "The buffer-swap fixture's pre-phase outcome is GREEN, not the RED the folded todo's prose predicted -- recorded verbatim rather than reshaped into a RED it did not produce, per the todo's own binding instruction"
  - "The buffer-swap fixture is declared a non-regression control to be re-run after plan 38-05 lands the body wrapper, since the wrapper changes what the marker sees at every desc boundary"

patterns-established:
  - "Wrapper-aware adjacency guard: a forward-looking regex assertion that cannot be RED pre-phase (the pattern it guards against does not exist yet) but exists specifically to catch a propagation regression once the wrapper lands"

requirements-completed: [IND-01, IND-05]

coverage:
  - id: D1
    description: "D-10 conjunction assertion (body wrapper tokens present AND break count == 8) added to the SIG-08 gate module, RED pre-phase on the wrapper token's absence"
    requirement: "IND-05"
    verification:
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestD10BodyWrapperBreakMarkerGate::test_d10_wrapper_present_and_break_count_still_eight"
        status: fail
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestD10BodyWrapperBreakMarkerGate::test_d10_no_adjacent_breaks_separated_only_by_wrapper_close"
        status: pass
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestD10BodyWrapperBreakMarkerGate::test_d10_two_level_nesting_yields_exactly_one_break"
        status: pass
    human_judgment: false
  - id: D2
    description: "The four pre-existing SIG-08 tests stay byte-identical in value and stay green -- no Phase 37 expectation was re-pinned"
    verification:
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_exact_break_count_after_fix"
        status: pass
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_no_adjacent_break_statements_anywhere"
        status: pass
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_content_follows_nested_member_stays_separated"
        status: pass
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_sibling_bodyless_control_keeps_one_break"
        status: pass
    human_judgment: false
  - id: D3
    description: "The folded buffer-swap todo's fixture (desc inside a glossary definition, nested desc pair inside that, top-level nesting-only control, and a recorded not-constructible figure-caption/admonition-title control) built and its pre-phase outcome measured"
    requirement: "IND-01"
    verification:
      - kind: unit
        ref: "tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapStructuralGate::test_glossary_single_desc_gets_exactly_one_break"
        status: pass
      - kind: unit
        ref: "tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapStructuralGate::test_glossary_nested_pair_gets_exactly_one_break"
        status: pass
      - kind: unit
        ref: "tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapStructuralGate::test_top_level_control_matches_glossary_nested_pair_count"
        status: pass
      - kind: unit
        ref: "tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapStructuralGate::test_no_adjacent_break_statements_anywhere"
        status: pass
      - kind: integration
        ref: "tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapCompileGate::test_fixture_compiles_via_real_typst_compile"
        status: pass
    human_judgment: false
  - id: D4
    description: "38-GATE-EVIDENCE-03.md records both outcomes verbatim (D-10's RED and the buffer-swap fixture's GREEN) with a RED/CONTROL-GREEN/PRE-EXISTING-GREEN node-id table"
    verification:
      - kind: other
        ref: ".planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE-03.md"
        status: pass
    human_judgment: false

# Metrics
duration: ~25min
completed: 2026-08-01
status: complete
---

# Phase 38 Plan 03: D-10 Conjunction Gate + Buffer-Swap Fixture Summary

**A RED conjunction assertion discharges D-10's marker-propagation resolution with a fixture, and the folded buffer-swap todo's fixture measures an honest GREEN (not the predicted RED), both recorded verbatim in 38-GATE-EVIDENCE-03.md.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-01
- **Tasks:** 3
- **Files modified:** 5 (1 modified, 4 created)

## Accomplishments

- Added `TestD10BodyWrapperBreakMarkerGate` to `tests/test_signature_break_and_arrow_gate.py`: a conjunction assertion (body wrapper's opening AND closing tokens present, AND `parbreak()` count exactly 8) that is RED pre-phase specifically on the wrapper token's absence — not a count mismatch — plus a wrapper-aware adjacency forward-guard and a depth-invariance check. Extended the four pre-existing SIG-08 test docstrings with one Phase 38 note each; no existing assertion value changed (confirmed by `git diff --stat`: 197 insertions, 0 deletions).
- Built `tests/fixtures/desc_break_marker_buffer_swap_gate/` (a `desc` inside a glossary definition, a nested `desc` pair inside that same definition, a top-level nesting-only control, and a documented-not-constructible figure-caption/admonition-title control) and its gate module. Measured the fixture's pre-phase behaviour honestly: GREEN, not the RED the folded todo's prose predicted, because the nested pair's two `depart_desc` calls both run while `self.body` points at the same swapped definition buffer — no genuine cross-buffer marker comparison occurs for this reachable shape. Declared a non-regression control to be re-run once plan 38-05 lands the body wrapper.
- Wrote `38-GATE-EVIDENCE-03.md` recording both outcomes verbatim: the D-10 conjunction test's RED failure message, the pre-phase break count (8) and wrapper-token absence with the producing commands, the D-10 resolution (marker propagation through `depart_desc_content`'s close, per contract section 6.2) with a note that `depart_desc` needs no code change, the buffer-swap fixture's full emitted `.typ` and GREEN disposition, both fixtures' `typst.compile()` exit statuses, and the SIG-08 module's `git diff --stat` with an explicit no-value-changed statement.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the D-10 conjunction assertions to the existing SIG-08 gate** - `7a05d15` (test)
2. **Task 2: Build the buffer-swap fixture and gate for the folded todo** - `387cf35` (test)
3. **Task 3: Record the D-10 and buffer-swap evidence** - `84e1e69` (docs)

_Note: this plan's tasks were all `type="auto"`, no TDD red/green/refactor cycle applies._

## Files Created/Modified

- `tests/test_signature_break_and_arrow_gate.py` - added `TestD10BodyWrapperBreakMarkerGate` (3 new tests: conjunction, wrapper-aware adjacency, depth-invariance) and one docstring sentence to each of the 4 pre-existing SIG-08 tests; no assertion value changed
- `tests/fixtures/desc_break_marker_buffer_swap_gate/conf.py` - minimal Sphinx config for the buffer-swap fixture
- `tests/fixtures/desc_break_marker_buffer_swap_gate/index.rst` - the folded todo's 4-construct fixture (glossary-nested desc, glossary-nested desc pair, top-level nesting-only control, recorded-not-constructible figure/admonition control)
- `tests/test_desc_break_marker_buffer_swap_gate.py` - the buffer-swap gate module (5 tests: 3 per-construct break-count assertions, 1 no-adjacent-break check, 1 real-compile acceptance)
- `.planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE-03.md` - verbatim evidence for both D-10's RED and the buffer-swap fixture's GREEN

## Decisions Made

- **D-10 discharged as a conjunction, not a single count check.** The break-count assertion alone is already 8 and correct pre-phase (nothing to catch), so a bare count check would not be RED for the right reason. Ordering the three asserts inside one test function (wrapper-open, wrapper-close, count) means the failure message names the missing wrapper token pre-phase, and the same test would catch a count regression to 9 post-wrapper-without-propagation.
- **The buffer-swap fixture's honest measurement is GREEN, and it is recorded as such rather than reshaped.** Built exactly per the folded todo's named reachable shape (desc inside a glossary definition, nested desc inside that), the fixture's two relevant `depart_desc` calls never straddle a live `self.body` reassignment — both run inside the same swapped `current_definition_buffer` list, so the marker's buffer-agnostic comparison stays internally consistent for this shape. This is a genuine, useful finding: it narrows exactly which cross-buffer configuration WOULD be hazardous (a departure comparison straddling a live swap, not merely occurring inside a swapped scope), and is now a documented non-regression control plan 38-05 must re-run.
- **The `figure caption / admonition title` control is recorded as structurally not constructible, per the task's own instruction**, rather than silently omitted: `nodes.title` and `nodes.caption` are parsed by docutils as one line of inline content, so a block-level domain directive cannot appear inside either at the RST grammar level.

## Deviations from Plan

None - plan executed exactly as written. Both honest-measurement outcomes explicitly anticipated by the plan (RED for D-10, either RED or GREEN for the buffer-swap fixture) were followed to whichever outcome actually measured true.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 38-05 has everything it needs to land `visit_desc_content`/`depart_desc_content` per contract section 2, with the marker-propagation fix (section 6.2) and the `depart_desc` docstring correction (section 6.3), and to flip `test_d10_wrapper_present_and_break_count_still_eight` GREEN.
- Plan 38-05 must also re-run `tests/test_desc_break_marker_buffer_swap_gate.py` after the wrapper lands, since it changes what the marker sees at every `desc` boundary — this fixture's declared-non-regression status is conditional on that re-run, not a closed matter.
- No blockers. `typsphinx/` was not touched by this plan (confirmed via `git status --porcelain typsphinx/`, empty at every commit).

---
*Phase: 38-structural-indentation-info-fields*
*Completed: 2026-08-01*
