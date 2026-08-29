---
phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere
plan: 04
subsystem: message-formatting
tags: [python, stdlib, path-quoting, repr, template-registry, exclusion-boundary]

requires:
  - phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere
    provides: "typsphinx/pathfmt.py::quote_path() -- MSG-02's delimiter-aware
      path-quoting helper, imported at module scope with zero import-cycle risk"
provides:
  - "typsphinx/template_registry.py's CONF-17 violation message and
    existence-check message now route their `template` value through
    quote_path() instead of `!r` -- removing backslash-doubling and the
    leaked PosixPath(...)/WindowsPath(...) class-name wrapper"
  - "tests/test_template_registry_path_quoting_gate.py -- MSG-05's own gate,
    3 classes / 5 tests, covering both of D-12's independent RED shapes plus
    SC#3's exclusion control for the deliberately-unrouted type-check message"
  - "60-04-EVIDENCE.md -- plan base SHA, discovery grep with full D-05
    classification, both RED transcripts, the two-tree exclusion-control
    measurement (pre-fix vs post-fix, byte-identical), GREEN transcripts,
    RED-first ledger, edge-reachability proof, zero-test-edit measurement,
    known gate gaps, and the wave-3 handoff"
affects: [60-05-acceptance]

actuals:
  tokens: 9435
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "The type-check branch immediately preceding a routed elif is a
      deliberate, measured EXCLUSION -- documented in a source comment citing
      the requirement ID (MSG-05) and success criterion (SC#3) it satisfies,
      rather than left silent or flagged as a TODO."
    - "Two-tree exclusion-control measurement: temporarily git-checkout the
      pre-fix module (keeping the new test file), run the exclusion
      selector, restore HEAD, run it again, and diff the two transcripts --
      proves an excluded site's behavior is byte-identical across the fix
      without relying on the test suite alone to notice a regression."

key-files:
  created:
    - tests/test_template_registry_path_quoting_gate.py
    - .planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-04-EVIDENCE.md
  modified:
    - typsphinx/template_registry.py

key-decisions:
  - "The two structurally-independent template!r sites (CONF-17 violation at
    :440, existence check at :453, post-fix line numbers) both route through
    quote_path(); the registry key on both lines and the deliberately-excluded
    type-check message's template at :420 stay on `!r` -- exactly matching
    D-06/D-07/D-05's classification with no deviation."
  - "Both of D-12's independent RED shapes were recorded FAILING against the
    unfixed tree BEFORE the fix: the doubled-backslash shape (a str template,
    matching every other still-!r site in the codebase) and a second shape
    with NO prior coverage anywhere in the suite -- a leaked
    PosixPath(...) class-name wrapper for a nonexistent Path-typed template."
  - "A comment introduced while wiring the fix accidentally re-inflated the
    literal substring `{template!r}` inside a source comment, doubling the
    acceptance-criteria grep count for the surviving type-check repr
    conversion from 1 to 2. Caught during self-verification (not by the
    plan's own automated gate, which greps template_registry.py, not
    comments specifically, but by re-running the plan's own acceptance-
    criteria grep before considering the task done) and fixed in a
    follow-up commit with zero functional change."

patterns-established:
  - "A deliberately-excluded interpolation gets its own dedicated exclusion-
    control test class (not folded into the routed-site test classes), named
    so a `-k` selector can isolate it, and measured with a two-tree
    before/after comparison rather than trusted to a single post-fix
    assertion."

requirements-completed: [MSG-05]

coverage:
  - id: D1
    description: "typsphinx/template_registry.py's CONF-17 violation message and existence-check message route their `template` value through quote_path(); the registry key on both lines is untouched, matching D-06/D-07."
    requirement: MSG-05
    verification:
      - kind: unit
        ref: "tests/test_template_registry_path_quoting_gate.py::TestRegistryTemplatePathQuoting (both methods)"
        status: pass
      - kind: unit
        ref: "tests/test_template_registry_path_quoting_gate.py::TestRegistryPathLikeTemplateNoClassWrapper::test_pathlike_template_existence_message_leaks_no_class_wrapper"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both of D-12's independent RED shapes (doubled backslash for a str template, leaked PosixPath(...) wrapper for a Path template) were recorded FAILING against the unfixed tree before the fix landed, with verbatim transcripts."
    requirement: MSG-05
    verification:
      - kind: unit
        ref: "60-04-EVIDENCE.md ## RED shape 1 and ## RED shape 2 sections"
        status: pass
    human_judgment: false
  - id: D3
    description: "The type-check message (reached when template is neither str nor os.PathLike) is measurably still on Python's repr conversion, proven by a dedicated exclusion-control test class that stays green both before and after the fix (two-tree measurement), and the two pre-existing assertions pinning its output for a list and a bytes template are green with zero edits."
    requirement: MSG-05
    verification:
      - kind: unit
        ref: "tests/test_template_registry_path_quoting_gate.py::TestRegistryTypeCheckMessageStaysReprQuoted (both methods)"
        status: pass
      - kind: unit
        ref: "tests/test_template_registry.py::test_non_path_template_field_raises_extension_error_not_typeerror and ::test_bytes_template_field_raises_extension_error_not_typeerror"
        status: pass
    human_judgment: false
  - id: D4
    description: "The empty-value and wrong-type edges are proven structurally unreachable at both routed sites, and the CONF-17/existence checks stay structurally independent, with source lines and existing control tests recorded as proof."
    requirement: MSG-05
    verification:
      - kind: unit
        ref: "60-04-EVIDENCE.md ## Edge reachability section (three claims, each resting on source lines plus an existing unmodified control test)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Zero existing test assertions modified; the full suite, black --check, mypy typsphinx/, and the AST repr-census guard are all green."
    requirement: MSG-05
    verification:
      - kind: unit
        ref: "git diff --name-status against plan base SHA (tests/ shows only one Added file); uv run pytest -q (1499 passed, 5 skipped); uv run black --check .; uv run mypy typsphinx/; uv run pytest tests/test_repr_census_guard.py -q"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-29
status: complete
---

# Phase 60 Plan 04: template_registry.py Path-Quoting Wiring (MSG-05) Summary

**`typsphinx/template_registry.py`'s CONF-17 violation and existence-check messages now route `template` through `quote_path()`, closing both a backslash-doubling defect and a leaked `PosixPath(...)` wrapper defect, while the adjacent type-check message stays measurably on `repr()` as SC#3's deliberate exclusion.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-29T10:30:00Z (approx.)
- **Completed:** 2026-08-29T11:15:03Z
- **Tasks:** 3
- **Files modified:** 3 (1 modified, 2 created)

## Accomplishments

- Both path-valued `template` interpolations in `typsphinx/template_registry.py`
  (the CONF-17 violation message and the existence-check message) now route through
  `typsphinx.pathfmt.quote_path()` instead of Python's `!r` conversion — removing
  backslash-doubling for Windows-shaped `str` templates and removing the leaked
  `PosixPath(...)`/`WindowsPath(...)` class-name wrapper for `pathlib.Path` templates.
- A new gate module, `tests/test_template_registry_path_quoting_gate.py` (3 classes,
  5 tests), records BOTH of D-12's independent RED shapes against the unfixed tree —
  the doubled-backslash shape (matching every other still-`!r` site in the codebase)
  and a genuinely new shape with no prior coverage anywhere in the suite: a leaked
  `pathlib` class-name wrapper for a nonexistent `Path`-typed template.
- The type-check message two lines above the routed sites (reached when `template`
  is neither `str` nor `os.PathLike`) is a deliberate, measured EXCLUSION per SC#3 —
  proven unchanged by a dedicated exclusion-control test class run in a two-tree
  before/after measurement (pre-fix and post-fix transcripts are byte-identical),
  and the two pre-existing assertions pinning its `repr()` output for a `list` and a
  `bytes` template stay green with zero edits.
- The empty-value and wrong-type edges at both routed sites, and the structural
  independence of the CONF-17 and existence checks, are all proven unreachable/
  independent with source-line citations and existing unmodified control tests
  (`60-04-EVIDENCE.md`'s `## Edge reachability` section).
- Zero existing test assertions modified anywhere under `tests/` (measured via
  `git diff --name-status` against the plan base SHA — only one `A`dded file); the
  full suite (1499 passed, 5 skipped), `black --check .`, `mypy typsphinx/`, and the
  AST repr-census guard are all green.

## Task Commits

Each task was committed atomically:

1. **Task 1: Run the discovery grep, then commit MSG-05's two RED shapes and the exclusion control** - `af420f9b` (test)
2. **Task 2: Route template_registry.py's two path-valued template interpolations through quote_path()** - `623d023f` (feat)
3. **Task 2 (follow-up fix): Reword SC#3 exclusion comment to avoid inflating template!r grep count** - `7b1c4e3c` (fix)
4. **Task 3: Record MSG-05's RED-first ledger, the edge-unreachability proof, and the wave-3 handoff** - `ec81b4ff` (docs)

## Files Created/Modified

- `typsphinx/template_registry.py` - two `template` interpolations (CONF-17 violation
  message, existence-check message) now route through `quote_path()`; one new
  module-scope import (`from typsphinx.pathfmt import quote_path`); the type-check
  message's exclusion documented in a source comment citing MSG-05/SC#3
- `tests/test_template_registry_path_quoting_gate.py` - MSG-05's own gate (3 classes,
  5 tests): `TestRegistryTemplatePathQuoting` (RED shape 1),
  `TestRegistryPathLikeTemplateNoClassWrapper` (RED shape 2, no prior coverage),
  `TestRegistryTypeCheckMessageStaysReprQuoted` (SC#3's exclusion control)
- `.planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-04-EVIDENCE.md` -
  plan base SHA, discovery grep with full D-05 classification of every `!r` hit,
  both RED transcripts, the two-tree exclusion-control measurement, GREEN
  transcripts, RED-first ledger, edge-reachability proof, zero-test-edit
  measurement, known gate gaps, wave-3 handoff, and the ruff-deferred-to-CI note

## Decisions Made

- Implemented D-06/D-07/D-05's classification exactly as locked in `60-CONTEXT.md`:
  the two `template` interpolations at the CONF-17 and existence-check sites route
  through `quote_path()`; the registry `key` on both lines and the type-check
  message's `template` stay on `!r`.
- Chose to add a short source comment above the type-check branch explicitly citing
  MSG-05/SC#3 as the reason it stays unrouted, per the plan's own instruction that
  any comment added there must state the exclusion is deliberate rather than read
  as a TODO or oversight.
- Performed the two-tree exclusion-control measurement AFTER committing task 2's
  fix (using the real committed `HEAD`, not an uncommitted working-tree state) —
  the plan's own instruction text implies this ordering ("`git checkout HEAD --
  typsphinx/template_registry.py`" only restores something meaningful once the fix
  is actually committed).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed own sequencing error that discarded task 2's uncommitted edits mid-measurement**
- **Found during:** Task 2 (the two-tree exclusion-control measurement)
- **Issue:** The plan's own two-tree procedure reads `git checkout HEAD --
  typsphinx/template_registry.py` to restore the post-fix module. Task 2's fix had
  not yet been committed when this executor first ran that command, so `HEAD`
  resolved to task 1's commit (which never touched `typsphinx/template_registry.py`)
  — silently discarding the uncommitted routing edit instead of restoring it.
- **Fix:** Recognized the discarded edit immediately (a `grep -n "quote_path"` on the
  restored file returned nothing), redid the two edits (the import line and the two
  `quote_path(template)` substitutions) identically to the first pass, then
  committed task 2 BEFORE re-running the two-tree measurement so `HEAD` correctly
  resolved to the committed fix.
- **Files modified:** `typsphinx/template_registry.py`
- **Verification:** Re-ran the full gate (`tests/test_template_registry_path_quoting_gate.py`,
  5 passed), `tests/test_template_registry.py` (76 passed), `black --check .`, and
  `mypy typsphinx/` after redoing the edits — all green — before committing.
- **Committed in:** `623d023f` (Task 2 commit)

**2. [Rule 1 - Bug] Fixed a comment that accidentally inflated an acceptance-criteria grep count**
- **Found during:** Task 2 (post-commit acceptance-criteria verification, before
  starting task 3)
- **Issue:** The source comment documenting the type-check message's SC#3 exclusion
  used the literal substring `{template!r}` (with the fix applied to a pre-existing
  typo that had dropped the opening brace). This accidentally registered as a
  SECOND match for `grep -cE '\{template!r\}' typsphinx/template_registry.py`,
  inflating the count to 2 when the plan's acceptance criteria require exactly 1
  (the type-check branch's own genuine, code-level repr conversion).
- **Fix:** Reworded the comment to describe the interpolation in prose ("this
  branch's `template` interpolation below") without repeating its literal source
  form. No functional change to any message, interpolation, or logic.
- **Files modified:** `typsphinx/template_registry.py`
- **Verification:** `grep -cE '\{template\!r\}' typsphinx/template_registry.py` → `1`;
  `grep -c 'quote_path(' typsphinx/template_registry.py` → `2`; re-ran the full gate,
  existing tests, black, mypy, census guard, and the full suite (1499 passed, 5
  skipped) — all green.
- **Committed in:** `7b1c4e3c` (separate follow-up commit, not amended into `623d023f`,
  per the standing git-safety rule to always create new commits rather than
  amending)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs introduced and caught within
this executor's own work, discovered during its own verification loop before moving
to the next task; zero deviations from `60-CONTEXT.md`'s locked product decisions).
**Impact on plan:** Both fixes are internal to this plan's own edits, discovered and
corrected before any commit was left in a broken or misleading state. `quote_path()`
routing matches D-06/D-07/D-05 exactly as specified; no scope creep.

## Issues Encountered

None beyond the two auto-fixed deviations above, both resolved within Task 2 before
proceeding to Task 3.

## User Setup Required

None - no external service configuration required. Stdlib-only wiring against the
already-existing `typsphinx.pathfmt.quote_path()` helper from wave 1; zero new
dependencies.

## Next Phase Readiness

`typsphinx/template_registry.py`'s two path-valued `template` interpolations are
wired, gated, and measured against the plan's own acceptance criteria and the
project's full verification suite. Wave 3's acceptance plan can now run its
repo-wide SC#2 grep and SC#3 over-reach audit against this module alongside its two
sibling wave-2 plans (`60-02` builder.py, `60-03` writer.py) — this plan's own
`60-04-EVIDENCE.md` § "Wave-3 handoff" gives the exact grep command, the
`quote_path(` count (2), the surviving `template!r` count (1, at line 420), and the
full list of identifier-valued names this module must still render through `!r`
after the phase. No blockers.

---
*Phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere*
*Completed: 2026-08-29*

## Self-Check: PASSED

- FOUND: `typsphinx/template_registry.py`
- FOUND: `tests/test_template_registry_path_quoting_gate.py`
- FOUND: `.planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-04-EVIDENCE.md`
- FOUND commit: `af420f9b` (test)
- FOUND commit: `623d023f` (feat)
- FOUND commit: `7b1c4e3c` (fix)
- FOUND commit: `ec81b4ff` (docs)
