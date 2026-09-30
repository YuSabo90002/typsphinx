---
phase: 49-per-master-include-graph-with-state-guarded-includes
plan: 03
subsystem: testing
tags: [sphinx, typst, toctree, state, pytest, xfail, fixtures]

# Dependency graph
requires:
  - phase: 49-01
    provides: "49-EXPECTED-STRUCTURE.md's Emission contract, Degenerate-shape outcome table, and
      Fixture specification entries 3-9 (the written-first source for every asserted value in
      this plan's fixtures and gate module); 49-EVIDENCE.md's State-syntax measurement (the
      decided state key and edge-key format probes)"
provides:
  - "Seven new fixture projects under tests/fixtures/state_guard_*_gate/, transcribing
    49-EXPECTED-STRUCTURE.md's Fixture specification entries 3-9"
  - "49-SHAPES-RED-EVIDENCE.md: verbatim pre-fix real-compile transcripts, full Sphinx warning
    baselines and pypdf marker counts for all seven shapes, including two classic-TypstError REDs
    (self/URL, and an additional measured cycle-case RED) and one silent non-fatal content-drop
    RED (three-master defect A reproduction)"
  - "tests/test_state_guard_shapes_gate.py: the shapes gate driving all seven fixtures, 8 tests
    recorded xfail(strict=True) naming 49-04, 9 invariance-guard/pure tests passing today"
affects: [49-04, 49-05, 49-06]

# Actuals (#2632)
actuals:
  tokens: 21936
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Shapes-gate pattern: one module-scoped fixture builds every named fixture once via both
      -b typst and -b typstpdf, cached in a dict keyed by fixture name, shared across every test
      class so N fixtures cost N sphinx-build pairs total, not N-per-test-class"
    - "xfail-reason-as-named-constant: long xfail reason strings factored into module-level
      _REASON_X constants so `@pytest.mark.xfail(strict=True, reason=_REASON_X)` stays on one
      physical line under black's line-length limit -- required for grep-based plan verification
      that checks the literal 'xfail(strict=True' substring stays on one line"
    - "RED-EVIDENCE.md as a parsed data source, not a restated inline copy: the no-lost-diagnostics
      backstop test parses 49-SHAPES-RED-EVIDENCE.md's own 'Full warning list' bullets per section
      at test-collection time, so the baseline comparison cannot drift from the recorded evidence"

key-files:
  created:
    - tests/fixtures/state_guard_self_and_url_gate/ (conf.py, index.rst, child.rst)
    - tests/fixtures/state_guard_cycle_gate/ (conf.py, alpha.rst, beta.rst)
    - tests/fixtures/state_guard_selfref_gate/ (conf.py, index.rst, other.rst)
    - tests/fixtures/state_guard_glob_gate/ (conf.py, index.rst, guide/{zulu,alpha,mike}.rst)
    - tests/fixtures/state_guard_orphan_ref_gate/ (conf.py, index.rst, orphan_doc.rst)
    - tests/fixtures/state_guard_three_master_gate/ (conf.py, m1/m2/m3.rst, mid.rst, common_a/b.rst)
    - tests/fixtures/state_guard_substring_key_gate/ (conf.py, index.rst, guideext.rst, guide.rst)
    - .planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-SHAPES-RED-EVIDENCE.md
    - tests/test_state_guard_shapes_gate.py
  modified: []

key-decisions:
  - "Discovered an ADDITIONAL, unplanned classic-TypstError RED beyond D-10's named 'one classic
    RED': state_guard_cycle_gate's 2-node mutual toctree currently produces a genuine mutual
    #include() pair (alpha.typ includes beta.typ, beta.typ includes alpha.typ back), which Typst
    aborts with 'maximum show rule depth exceeded'. The current write-time emitter has no cycle
    guard at all -- this was measured, not assumed, and recorded in full in
    49-SHAPES-RED-EVIDENCE.md Section 2 rather than silently treated as an invariance baseline."
  - "Discovered the three-master fixture reproduces defect A live and non-fatally: the
    build-scoped write-time ledger lets only ONE master's own toctree entry for a shared child
    survive per document, determined purely by alphabetical write order -- COMMON-A-MARKER is
    entirely absent from manual2.pdf pre-fix, and COMMON-B-MARKER is absent from both manual1.pdf's
    Mid section and all of manual3.pdf. Recorded verbatim with grep'd include-line evidence
    (m3.typ has ZERO include lines at all) rather than asserted from the design doc alone."
  - "Corrected an initial label-selector assumption: multi-word document titles ('Common A',
    'Common B') slugify to hyphenated Typst label ids ('common-a', 'common-b'), NOT the docname
    with its underscore preserved. Verified via a live typst.query() probe before writing the
    three-master test's heading-level assertions, avoiding a silently-wrong test."
  - "Refactored xfail reason strings into named module-level constants after discovering black's
    line-breaking behavior splits '@pytest.mark.xfail(strict=True, reason=\"...\")' across
    multiple physical lines whenever the combined line exceeds 88 chars -- which defeats the
    plan's own acceptance-criteria grep for the literal substring 'xfail(strict=True'. Verified
    empirically with a throwaway black run before committing to the pattern."
  - "Classified test 6 (orphan reference) and test 10 (no-lost-diagnostics) as NOT xfail, since
    every one of their assertions already holds on the unfixed tree (Phase 48's own compile-time
    guard for the orphan case; a tautological self-check for the diagnostics backstop) -- keeping
    them as invariance guards rather than forcing an xfail label onto passing behavior."

patterns-established:
  - "Shapes-gate module-scoped build cache (see tech-stack.patterns above), reusable for any
    future gate module driving many small fixture projects through the same two-builder pipeline."
  - "Named-constant xfail reasons to satisfy grep-based plan verification against black's
    line-wrapping -- reusable whenever a plan's acceptance criteria greps for a literal decorator
    substring."

requirements-completed: [COMP-05, COMP-06, COMP-09]

coverage:
  - id: D1
    description: "Five D-06 degenerate-shape fixtures (self/URL, cycle, self-reference, glob,
      orphan-reference) built to 49-EXPECTED-STRUCTURE.md's Fixture specification entries 3-7,
      each carrying a load-bearing-properties comment block and confirmed accepted by a real -b
      typst build on the unfixed tree"
    requirement: "COMP-05"
    verification:
      - kind: integration
        ref: "tests/test_state_guard_shapes_gate.py::TestSelfAndUrlGate,
          TestCycleGate, TestSelfRefGate, TestGlobGate, TestOrphanRefGate"
        status: pass
    human_judgment: false
  - id: D2
    description: "Three-master and substring-key fixtures built to Fixture specification entries
      8-9, plus 49-SHAPES-RED-EVIDENCE.md recording every shape's pre-fix real-compile transcript,
      full Sphinx warning baseline and pypdf marker count -- including two classic-TypstError REDs
      and one silent non-fatal content-drop RED (three-master defect A reproduction)"
    requirement: "COMP-09"
    verification:
      - kind: other
        ref: "49-SHAPES-RED-EVIDENCE.md Sections 1-7, each with a verbatim reproduction command,
          captured build output and 'What this evidence licenses' classification"
        status: pass
    human_judgment: false
  - id: D3
    description: "tests/test_state_guard_shapes_gate.py drives all seven fixtures, asserting each
      shape's plan-time-decided outcome, the substring relation itself, and the warning baselines,
      with post-fix assertions recorded as strict xfails naming 49-04 and zero XPASS"
    requirement: "COMP-06"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_state_guard_shapes_gate.py -q -- 17 collected, 9 passed,
          8 xfailed, 0 failed, 0 xpassed"
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-08-14
status: complete
---

# Phase 49 Plan 03: Shapes and Coverage Fixtures Summary

**Seven new state-guard shape fixtures transcribed from 49-EXPECTED-STRUCTURE.md, one
RED-EVIDENCE artifact recording two classic-TypstError REDs and a live three-master
defect-A reproduction, and a 17-test shapes gate (9 passing invariance guards, 8 strict
xfails naming 49-04, zero XPASS) driving all seven through real `-b typst`/`-b typstpdf`
compiles.**

## Performance

- **Duration:** ~40 min
- **Started:** 2026-08-14T~16:35:00+09:00 (approx., worktree provisioning)
- **Completed:** 2026-08-14T17:21:20+09:00
- **Tasks:** 3
- **Files modified:** 30 (29 created, 0 modified — no `typsphinx/` file touched)

## Accomplishments

- Built five D-06 degenerate-shape fixtures (self/external-URL/duplicate-entry, 2-node cycle,
  literal self-reference, `:glob:` toctree, `:orphan:` reference) to 49-EXPECTED-STRUCTURE.md's
  written specification, each with a load-bearing-properties comment block and confirmed accepted
  by a real `-b typst` markup build on the unfixed tree.
- Built the three-master coverage fixture (SC#2/COMP-09's "not 2-master-specific" obligation) and
  the substring-key adjacency fixture (COMP-06's array-vs-string semantics detector).
- Captured `49-SHAPES-RED-EVIDENCE.md`: verbatim pre-fix real-compile transcripts, full Sphinx
  warning lists and `pypdf` marker occurrence counts for all seven shapes. Discovered — by direct
  measurement, not by assumption — that the cycle fixture produces its OWN classic `TypstError`
  (`maximum show rule depth exceeded`, via a genuine mutual `#include()` pair) beyond D-10's
  explicitly named "one classic RED" (the self/URL fixture's `file not found`), and that the
  three-master fixture reproduces defect A live and non-fatally (a silent, zero-warning
  content-drop where the build-scoped write-time ledger lets only one master keep each shared
  child, verified down to the exact emitted include lines: `m3.typ` has zero includes at all).
- Authored `tests/test_state_guard_shapes_gate.py`: a module-scoped build cache runs all seven
  fixtures once through both builders, then 17 tests assert each shape's plan-time-decided
  outcome. Eight tests are `xfail(strict=True)` naming 49-04 (their assertions require the
  `#state(...)` array mechanism that does not exist until 49-04 lands); nine are plain invariance
  guards or pure string-level proofs that already hold on the unfixed tree.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the five D-06 degenerate-shape fixtures** - `79a08cc0` (test)
2. **Task 2: Build three-master/substring-key fixtures, capture shapes RED evidence** - `162069c7` (test)
3. **Task 3: Author tests/test_state_guard_shapes_gate.py** - `02ac4362` (test)

_No TDD tasks — this plan authors fixtures and a gate module, not production code; the gate's own
post-fix assertions are the recorded strict xfails, not a RED/GREEN cycle against code this plan
touches._

## Files Created/Modified

- `tests/fixtures/state_guard_self_and_url_gate/` - D-03/D-10 self/external-URL/duplicate-entry fixture
- `tests/fixtures/state_guard_cycle_gate/` - 2-node toctree cycle fixture
- `tests/fixtures/state_guard_selfref_gate/` - literal self-referencing toctree fixture
- `tests/fixtures/state_guard_glob_gate/` - `:glob:` toctree fixture (sorted-vs-authoring order)
- `tests/fixtures/state_guard_orphan_ref_gate/` - `:orphan:` document referenced but not toctree'd
- `tests/fixtures/state_guard_three_master_gate/` - three masters sharing two overlapping children
- `tests/fixtures/state_guard_substring_key_gate/` - COMP-06 array-vs-string dark-guard fixture
- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-SHAPES-RED-EVIDENCE.md` -
  pre-fix transcripts, warning baselines, pypdf marker counts for all seven shapes
- `tests/test_state_guard_shapes_gate.py` - the shapes gate module (17 tests)

## Decisions Made

See `key-decisions` in frontmatter above. In summary: discovered two facts by direct measurement
that the plan's own specification did not fully anticipate — an additional classic-TypstError RED
in the cycle fixture (distinct from D-10's named self/URL RED) and a live, non-fatal three-master
reproduction of defect A — and recorded both in full rather than silently smoothing them into the
expected "invariance baseline" framing. Also corrected a label-selector assumption (multi-word
titles slugify with hyphens, not underscores) via a live probe before writing the dependent test,
and refactored xfail reasons into named constants after discovering black's line-wrapping would
otherwise defeat the plan's own grep-based acceptance check.

## Deviations from Plan

None (Rule 1-4) — no bug fix, missing functionality, blocking fix, or architectural change was
required. Two items are worth naming as measurement corrections rather than deviations, since
they did not change scope, only sharpen accuracy against the plan's own binding constraint #6
(derive from measurement, not assumption):

1. **Additional pre-fix RED discovered in the cycle fixture.** The plan's own framing names
   `state_guard_self_and_url_gate` as "the phase's one classic-TypstError RED" (D-10). Measuring
   `state_guard_cycle_gate` against the unfixed tree showed it ALSO fails to compile today (a
   different Typst-level error, `maximum show rule depth exceeded`, from a genuine mutual
   `#include()` pair the current mechanism has no guard against). Recorded in full in
   `49-SHAPES-RED-EVIDENCE.md` Section 2 and reflected in the gate's own xfail for that shape,
   with an explicit note that this is an additional finding, not a contradiction of D-10's framing.
2. **Label-selector correction before writing the three-master test.** Multi-word titles ("Common
   A", "Common B") produce hyphenated Typst label ids ("common-a", "common-b"), not the docname
   with its underscore. Verified via a live `typst.query()` probe against an already-built fixture
   before writing `TestThreeMasterGate`'s heading-level assertions, avoiding a test that would
   have silently asserted against the wrong selector.

## Issues Encountered

- **Black line-wrapping defeats the plan's own grep-based xfail check (self-caught, before
  committing Task 3).** The plan's acceptance criteria require
  `grep -c 'xfail(strict=True' tests/test_state_guard_shapes_gate.py` to return at least 8.
  Writing each `@pytest.mark.xfail(strict=True, reason="...")` with a long inline reason string
  caused `black` to reformat the decorator across multiple physical lines (`strict=True,` and
  `reason=(` each on their own line), which breaks the literal-substring grep. Verified the
  behavior empirically with a throwaway `black` run, then refactored every reason string into a
  named module-level constant (`_REASON_X`) so each decorator's own line
  (`@pytest.mark.xfail(strict=True, reason=_REASON_X)`) stays under black's 88-character limit and
  keeps the required substring intact. Re-verified the grep and the companion "every reason names
  49-04 within 400 chars" check both pass after the refactor, and that two INCIDENTAL matches
  (a module-docstring mention and a code comment, both also containing the literal substring
  `xfail(strict=True`) needed their own wording adjusted so they did not spuriously fail the
  400-char "names 49-04" check.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 49-04 (the emitter/tracer plan) has this plan's seven shapes gate as an additional acceptance
  surface beyond 49-02's composition gate: after the emitter lands, `test_state_guard_shapes_gate.py`
  should flip its 8 xfails to plain passes with zero XPASS, and `test_state_guard_shapes_gate.py`'s
  own module-scoped `all_builds` fixture requires no changes.
- `49-SHAPES-RED-EVIDENCE.md`'s "What this evidence licenses" section explicitly labels which
  sections are REDs (1, 2, 6), which are invariance baselines (3, 4, 5, 7) — 49-04's own
  post-fix re-verification pass can use this classification directly rather than re-deriving it.
- The full fast suite (`uv run pytest -m "not slow" -q`) is at **1036 passed, 58 deselected, 8
  xfailed** after this plan (was 1027 passed / 58 deselected at the wave-1 baseline — +9 new
  passing tests, +8 new xfailed tests, zero regressions).
- No blockers. `git status --porcelain typsphinx/` printed nothing throughout all three tasks.

---
*Phase: 49-per-master-include-graph-with-state-guarded-includes*
*Completed: 2026-08-14*

## Self-Check: PASSED

- FOUND: `tests/fixtures/state_guard_self_and_url_gate/conf.py`
- FOUND: `tests/fixtures/state_guard_cycle_gate/conf.py`
- FOUND: `tests/fixtures/state_guard_selfref_gate/conf.py`
- FOUND: `tests/fixtures/state_guard_glob_gate/conf.py`
- FOUND: `tests/fixtures/state_guard_orphan_ref_gate/conf.py`
- FOUND: `tests/fixtures/state_guard_three_master_gate/conf.py`
- FOUND: `tests/fixtures/state_guard_substring_key_gate/conf.py`
- FOUND: `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-SHAPES-RED-EVIDENCE.md`
- FOUND: `tests/test_state_guard_shapes_gate.py`
- FOUND commit: `79a08cc0`
- FOUND commit: `162069c7`
- FOUND commit: `02ac4362`
