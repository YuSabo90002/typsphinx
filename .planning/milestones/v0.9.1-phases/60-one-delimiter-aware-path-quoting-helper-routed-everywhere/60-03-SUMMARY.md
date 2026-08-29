---
phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere
plan: 03
subsystem: message-formatting
tags: [python, logging, path-quoting, repr, writer]

requires:
  - phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere
    provides: "typsphinx/pathfmt.py::quote_path() -- the delimiter-aware
      path-quoting helper this plan routes writer.py's debug log through"
provides:
  - "typsphinx/writer.py::render_wrapper()'s wrapper-render DEBUG log --
    wrapper_relative_dir, include_path and template_file now route
    through quote_path() instead of !r; docname on the same line is
    unchanged (D-07)"
  - "tests/test_writer_path_quoting_gate.py -- MSG-04's own gate, 2 test
    classes: TestWrapperDebugLogPathQuoting (RED-first doubled-backslash
    guard) and TestWrapperDebugLogTemplateFileNone (D-03's None-pin,
    green both before and after)"
  - "60-03-EVIDENCE.md -- plan base SHA, discovery grep classification,
    verbatim RED/GREEN transcripts, the two-tree None-pin byte-identity
    proof, D-07 re-confirmation, RED-first ledger, zero-test-edit
    measurement, the known gate gap, and the wave-3 handoff"
affects: [60-05-acceptance]

actuals:
  tokens: 6992
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "The pre-fix/post-fix debug-line comparison for a value that
      cannot otherwise be asserted through caplog alone was done via a
      temporary local print() removed immediately after both halves
      were captured, verified via git diff --stat showing zero residual
      diff against the committed test file -- Sphinx's own logging
      setup does not propagate DEBUG records to a plain basicConfig
      handler outside caplog's own capture mechanism."

key-files:
  created:
    - tests/test_writer_path_quoting_gate.py
    - .planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-03-EVIDENCE.md
  modified:
    - typsphinx/writer.py

key-decisions:
  - "Routed exactly three interpolations (wrapper_relative_dir, include_path, template_file) through quote_path() in render_wrapper()'s DEBUG log; left docname on the same line as !r (D-07, identifier-valued) and left _entry_element_value()'s fallback warning (entry[0], value, default) entirely untouched, re-confirmed by measurement rather than assumed."
  - "No conditional was added at the call site for the None case -- quote_path(None) returns the bare string 'None' by its own D-03 contract, keeping the substitution a straight three-value swap and proven byte-identical across the pre-fix and post-fix trees for the package-alone build path."
  - "template_file's non-None rendering (built from a registry key and a resolved template's basename, forward-slash-only by construction) has no portable unit-test shape for a backslash, so it carries no behavioural backslash gate in this plan -- recorded explicitly as a known gate gap rather than left silent, proven instead by the source route (quote_path( count of 3) plus wave 3's repo-wide grep audit."

patterns-established:
  - "A logger.debug() call site with no existing test coverage is gated by driving the real product method inside caplog.at_level('DEBUG') and filtering records by message prefix -- no re-pasted f-string, no mock of the logger itself."

requirements-completed: [MSG-04]

coverage:
  - id: D1
    description: "typsphinx/writer.py's wrapper-render DEBUG log routes wrapper_relative_dir, include_path and template_file through quote_path(); docname on the same line stays !r."
    requirement: MSG-04
    verification:
      - kind: unit
        ref: "tests/test_writer_path_quoting_gate.py::TestWrapperDebugLogPathQuoting::test_wrapper_debug_log_has_no_doubled_separator_for_windows_shaped_paths"
        status: pass
    human_judgment: false
  - id: D2
    description: "The debug record was recorded FAILING (doubled backslashes visible) against the unfixed tree before the wiring landed."
    requirement: MSG-04
    verification:
      - kind: unit
        ref: "60-03-EVIDENCE.md ## RED -- wrapper-render debug log section"
        status: pass
    human_judgment: false
  - id: D3
    description: "The package-alone template_file=None line is proven byte-identical across the pre-fix and post-fix trees, and no conditional was added at the call site."
    requirement: MSG-04
    verification:
      - kind: unit
        ref: "tests/test_writer_path_quoting_gate.py::TestWrapperDebugLogTemplateFileNone; 60-03-EVIDENCE.md ## None pin (two-tree)"
        status: pass
    human_judgment: false
  - id: D4
    description: "_entry_element_value()'s fallback warning is re-measured as identifier/title/author-valued and left untouched, confirming MSG-04's scope rather than assuming it."
    requirement: MSG-04
    verification:
      - kind: unit
        ref: "60-03-EVIDENCE.md ## D-07 confirmation"
        status: pass
    human_judgment: false
  - id: D5
    description: "Zero existing test assertions modified, and the full suite, black --check, mypy typsphinx/ and the AST census guard are all green."
    requirement: MSG-04
    verification:
      - kind: unit
        ref: "uv run pytest -q (1496 passed, 5 skipped); uv run black --check .; uv run mypy typsphinx/; uv run pytest tests/test_repr_census_guard.py -q (4 passed)"
        status: pass
    human_judgment: false

duration: 24min
completed: 2026-08-29
status: complete
---

# Phase 60 Plan 03: Writer.py Wrapper-Render Debug Log Path Quoting (MSG-04) Summary

**`typsphinx/writer.py`'s wrapper-render DEBUG log routes its three path-valued interpolations through `quote_path()`, RED-first against the unfixed tree, with a two-tree byte-identity proof for the live package-alone `None` case.**

## Performance

- **Duration:** 24 min
- **Started:** 2026-08-29T (see task commits below)
- **Completed:** 2026-08-29
- **Tasks:** 3
- **Files created:** 2 (`tests/test_writer_path_quoting_gate.py`, `60-03-EVIDENCE.md`)
- **Files modified:** 1 (`typsphinx/writer.py`)

## Accomplishments

- `typsphinx/writer.py::render_wrapper()`'s `logger.debug()` call now routes
  `wrapper_relative_dir`, `include_path` and `template_file` through
  `typsphinx.pathfmt.quote_path()` instead of `!r` — a Windows-shaped
  `wrapper_relative_dir` (`"C:\\Users\\runner\\out\\sub"`) no longer produces a
  doubled-backslash debug line. `docname` on the same line is untouched, per D-07.
- MSG-04's own gate (`tests/test_writer_path_quoting_gate.py`, 2 classes) was recorded
  FAILING against the unfixed tree (1 of 2 tests red, doubled backslash runs visible in
  the captured DEBUG record) before the fix landed, then GREEN after.
- D-03's `None` contract — `quote_path(None)` renders the bare string `"None"` — was
  proven byte-identical across the pre-fix and post-fix trees for the live
  package-alone build path (a package configured with no custom template), with no
  conditional added at the call site.
- D-07's writer.py claim was re-measured rather than restated: `_entry_element_value()`'s
  fallback warning (`entry[0]`, `value`, `default`) resolves to a docname and a
  title/author value at both of its call sites, confirming MSG-04's restriction to the
  wrapper-render debug log is correct as written.
- Zero existing test assertions were modified — `git diff --name-status` against the
  plan base SHA shows exactly one added test file under `tests/`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Run the discovery grep, then commit MSG-04's caplog gate RED and its None pin green** - `d7fb5a55` (test)
2. **Task 2: Route writer.py's wrapper-render debug log through quote_path()** - `8aeeb015` (feat)
3. **Task 3: Confirm D-07's writer.py measurement and close MSG-04's evidence** - `3ef8b85e` (docs)

## Files Created/Modified

- `typsphinx/writer.py` - one added `from typsphinx.pathfmt import quote_path` import; three interpolations in `render_wrapper()`'s DEBUG log routed through it
- `tests/test_writer_path_quoting_gate.py` - MSG-04's own gate (2 classes: `TestWrapperDebugLogPathQuoting`, `TestWrapperDebugLogTemplateFileNone`)
- `.planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-03-EVIDENCE.md` - plan base SHA, discovery grep classification, RED/GREEN transcripts, two-tree None-pin proof, D-07 confirmation, RED-first ledger, zero-test-edit measurement, known gate gap, wave-3 handoff

## Decisions Made

- Routed exactly the three path-valued interpolations named in `60-CONTEXT.md` D-06 —
  `wrapper_relative_dir`, `include_path`, `template_file` — leaving `docname` and
  `_entry_element_value()`'s fallback warning untouched, per D-07 (re-confirmed, not
  assumed).
- Used a temporary local `print()` (removed immediately after) to surface the `caplog`-
  captured DEBUG message to stdout for the two-tree byte-identity measurement, since
  Sphinx's own logging setup does not propagate DEBUG records to a plain `basicConfig`
  handler outside `caplog`'s own capture mechanism. Verified zero residual diff against
  the committed test file via `git diff --stat` before proceeding.
- No conditional added at the call site for the `None` case — `quote_path()`'s own D-03
  contract handles it, keeping this call site a straight substitution.

## Deviations from Plan

None - plan executed exactly as written. The one informational correction recorded is
in `60-03-EVIDENCE.md`'s `## RED` section: the plan's own `must_haves.truths` cited
"eleven doubled runs" as the pre-fix count; re-deriving the guard predicate directly
against the captured message measured **9** doubled runs (4 in `wrapper_relative_dir`,
5 in `include_path`; `template_file` in that specific test scenario resolves to the
bundled default template's forward-slash-only import path, contributing zero). This is
a corrected measurement, not a deviation in scope or implementation — the RED verdict
itself (test fails, doubled backslashes present) is unaffected, and no acceptance
criterion or test assertion depends on the exact count.

## Issues Encountered

None. The Sphinx-logging-propagation obstacle for capturing the debug line via
`-s`/`--log-cli-level` (rather than `caplog`'s own capture) was resolved with the
temporary-print technique documented above and left no trace in the final tree.

## User Setup Required

None - no external service configuration required. No new dependency, no new
`typst_*` config value.

## Next Phase Readiness

MSG-04 is closed: `typsphinx/writer.py`'s wrapper-render DEBUG log is fully routed
through `quote_path()` with a RED-first gate, a byte-identity proof for its live
`None` path, and D-07's identifier-valued classification re-confirmed. Wave 3's
acceptance plan can now run its repo-wide grep audit (SC#2) and over-reach measurement
(SC#3) against this module using the handoff recorded in `60-03-EVIDENCE.md`'s
`## Wave-3 handoff` section: `grep -c 'quote_path(' typsphinx/writer.py` returns `3`,
and the four interpolations that must still render through `!r` are `docname`
(`:511`) and `_entry_element_value()`'s `entry[0]`, `value`, `default` (`:154-155`).
No blockers. `ruff check .` remains deferred to CI per this worktree's known
NixOS-sandbox ELF limitation.

---
*Phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere*
*Completed: 2026-08-29*

## Self-Check: PASSED

- FOUND: `tests/test_writer_path_quoting_gate.py`
- FOUND: `.planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-03-EVIDENCE.md`
- FOUND: `typsphinx/writer.py`
- FOUND commit: `d7fb5a55` (test)
- FOUND commit: `8aeeb015` (feat)
- FOUND commit: `3ef8b85e` (docs)
- Re-ran `uv run pytest tests/test_writer_path_quoting_gate.py -q` → 2 passed
- Re-ran `grep -c 'quote_path(' typsphinx/writer.py` → 3
- Re-ran `git diff --name-status 1118199a577533f598a799b51d08b7bc3e9bcc49..HEAD -- tests/` → only `A tests/test_writer_path_quoting_gate.py`
