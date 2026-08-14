---
phase: 49-per-master-include-graph-with-state-guarded-includes
plan: 05
subsystem: testing
tags: [sphinx, typst, toctree, state, pytest, structural-gate, evidence]

# Dependency graph
requires:
  - phase: 49-04
    provides: "typsphinx/translator.py's five module-level derivation
      functions and rewritten visit_toctree(); typsphinx/builder.py's
      _build_include_edge_map()/_master_include_edges; the deleted
      _included_docnames ledger; all 16 strict-xfail markers removed
      from the phase-49 gate modules"
  - phase: 49-02
    provides: "tests/fixtures/state_guard_two_master_gate/,
      tests/fixtures/state_guard_mirror_pair_gate/, 49-RED-EVIDENCE.md"
  - phase: 49-03
    provides: "seven state_guard_*_gate shape fixtures,
      49-SHAPES-RED-EVIDENCE.md, tests/test_state_guard_shapes_gate.py"
provides:
  - "tests/test_include_ledger_removal_gate.py: a committed, falsifiable
    COMP-11 removal gate (structural, source-text) plus the
    assumption-delta contract test (behavioural, real-build) -- proven
    able to go red against a temporary reintroduction"
  - "49-EVIDENCE.md: four new appended sections -- the SC#4 repo-wide
    sweep, the no-lost-diagnostics comparison across all nine Phase 49
    fixtures, the degenerate-shape closure table, and the Phase 51/52
    handoff -- none overwriting the sections 49-01 or this plan's own
    earlier tasks wrote"
affects: [49-06]

# Actuals (#2632)
actuals:
  tokens: 15407
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "AST-based structural-gate collection: walking a module's own
      source via `ast` (not `inspect.getsource()` line-scanning alone)
      to exclude docstrings from a 'genuine emission site' scan while
      still catching a real code-level reintroduction -- reused for both
      the state-key-literal collector and the toctree-visitor
      include-call scan"
    - "Self-exclusion in a repo-wide removal gate: a removal gate that
      names its own deleted symbol as a single documented constant must
      exclude ITS OWN FILE from its own repo-wide prose sweep, or the
      gate permanently fails against its own text"

key-files:
  created:
    - tests/test_include_ledger_removal_gate.py
  modified:
    - .planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md

key-decisions:
  - "The state-key-literal collector (COMP-06/D-07's 'exactly one
    spelling' assertion) is implemented via ast walking rather than a
    text-level grep, because the production code's own f-string
    interpolation (`f'#state(\"{INCLUDE_STATE_KEY}\", ())...'`) makes a
    naive substring count over-broad (it would also catch docstring
    worked-examples using the same literal spelling) and a naive
    comment-stripping pass dangerous (the emitted Typst text itself
    starts with a literal '#' character that a line-oriented comment
    scrubber would mistake for a Python comment marker, truncating the
    real call away)."
  - "The toctree-visitor structural scan excludes the function's own
    docstring via its AST line range rather than a heuristic text match,
    because the docstring legitimately narrates '#include() directives'
    as prose (matching the same include-call regex the code-level scan
    uses) -- a naive whole-function scan would false-positive on the
    docstring's own narration, not on a real reintroduced raw include."
  - "Task 5's wrapper-publication test uses the subprocess-based
    sys.executable -m sphinx helper (mirroring
    tests/test_pdf_render_gate.py's own precedent) rather than
    SphinxTestApp, so this module satisfies its own acceptance
    criterion that Sphinx is invoked through the running interpreter at
    least once; the assumption-delta and non-mutation tests (6/7) use
    SphinxTestApp instead, since they need direct in-process access to
    the builder's own _master_include_edges attribute, which a
    subprocess build cannot expose."

patterns-established:
  - "Structural-gate self-check via temporary reintroduction: before
    trusting a removal gate, reintroduce the deleted symbol into a
    scratch line of a production file, confirm the gate goes red, then
    revert -- recorded in this plan as the load-bearing proof a removal
    gate that cannot go red is not a gate."

requirements-completed: [COMP-05, COMP-06, COMP-11]

coverage:
  - id: D1
    description: "The build-scoped include-dedup ledger's removal
      (COMP-11) is enforced by a committed structural gate over both the
      production package and the repository's own non-planning prose,
      and the gate is proven able to go red against a temporary
      reintroduction"
    requirement: "COMP-11"
    verification:
      - kind: unit
        ref: "tests/test_include_ledger_removal_gate.py::TestLedgerRemovalFromProductionPackage::test_ledger_absent_from_production_package"
        status: pass
      - kind: unit
        ref: "tests/test_include_ledger_removal_gate.py::TestLedgerRemovalFromRepositoryProse::test_ledger_absent_from_repo_wide_prose"
        status: pass
    human_judgment: false
  - id: D2
    description: "The toctree visitor emits no unconditional include and
      no membership test against a builder attribute -- asserted
      structurally against visit_toctree's own source"
    requirement: "COMP-11"
    verification:
      - kind: unit
        ref: "tests/test_include_ledger_removal_gate.py::TestToctreeVisitorEmitsNoUnconditionalInclude"
        status: pass
    human_judgment: false
  - id: D3
    description: "Exactly one spelling of the namespaced Typst state key
      exists in the production package, collected structurally (not by
      counting occurrences of one known string)"
    requirement: "COMP-06"
    verification:
      - kind: unit
        ref: "tests/test_include_ledger_removal_gate.py::TestExactlyOneStateKeySpelling"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every emitted wrapper carries exactly one state
      publication line, immediately preceding its own content
      #include(...) line, checked against a real build of the
      three-master fixture"
    requirement: "COMP-06"
    verification:
      - kind: integration
        ref: "tests/test_include_ledger_removal_gate.py::TestExactlyOnePublicationPerWrapper::test_each_wrapper_publishes_once_immediately_before_its_include"
        status: pass
    human_judgment: false
  - id: D5
    description: "The assumption-delta contract test: the builder's
      include mapping is keyed by master docname, with at least two
      keys whose values differ for the two-master fixture -- and the
      mapping is unmutated by re-running the write phase"
    requirement: "COMP-05"
    verification:
      - kind: integration
        ref: "tests/test_include_ledger_removal_gate.py::TestAssumptionDeltaContract"
        status: pass
    human_judgment: false
  - id: D6
    description: "The SC#4 repo-wide sweep is recorded at every scope
      milestone invariant #4 requires, and ROADMAP binding constraint
      #7's four standing invariants (zero new runtime dependencies,
      @preview count still four with no new lockstep site, zero new
      typst_* config values, no forbidden opportunistic changes) are
      re-measured intact"
    requirement: "COMP-11"
    verification:
      - kind: other
        ref: "49-EVIDENCE.md ## Removal and invariant sweep (verbatim command output pasted)"
        status: pass
    human_judgment: false
  - id: D7
    description: "Every Phase 49 fixture's post-fix Sphinx warning list
      is compared item by item against its recorded pre-fix baseline;
      every baseline warning is still present, no diagnostic was
      silently removed"
    requirement: "COMP-05"
    verification:
      - kind: other
        ref: "49-EVIDENCE.md ## No lost diagnostics (9/9 fixtures MATCH)"
        status: pass
    human_judgment: false
  - id: D8
    description: "Every degenerate shape's observed post-fix outcome is
      recorded beside its plan-time-decided outcome with an explicit
      match/divergence verdict; no decided outcome was amended after
      measurement"
    requirement: "COMP-06"
    verification:
      - kind: other
        ref: "49-EVIDENCE.md ## Degenerate-shape closure (7/7 rows MATCH)"
        status: pass
    human_judgment: false

duration: ~22min
completed: 2026-08-14
status: complete
---

# Phase 49 Plan 05: Removal Gate, Assumption-Delta Contract, and Evidence Closure Summary

**Authored a committed, falsifiable structural+behavioural gate proving the deleted include-dedup ledger cannot silently regress, proved the gate can go red, ran the SC#4 repo-wide invariant sweep, and recorded the degenerate-shape closure plus the Phase 51/52 handoff in 49-EVIDENCE.md — all nine Phase 49 fixtures rebuilt with zero lost diagnostics.**

## Performance

- **Duration:** ~22 min
- **Started:** 2026-08-14T18:18:39+09:00 (base commit)
- **Completed:** 2026-08-14T18:40:18+09:00
- **Tasks:** 3
- **Files modified:** 2 (1 created, 1 modified across all three tasks)

## Accomplishments

- Authored `tests/test_include_ledger_removal_gate.py` (10 test functions across 5 classes): structural assertions that the deleted `_included_docnames` ledger attribute is absent from the production package and from the repository's own non-planning prose (word-boundary matched, walking every `*.py`/`.rst`/`.md` file in Python — no shell-out to `grep`); that `visit_toctree`'s own body emits no raw `include(...)` call and no membership test against a builder attribute; and that exactly one state-key literal exists in the production package, collected via an `ast`-based walk that resolves f-string interpolations back to their own module-level constant rather than counting occurrences of one known string.
- Added the behavioural half: every emitted wrapper in a real three-master build carries exactly one state publication line immediately before its own `#include(...)` line (checked structurally against the compiled `.typ` output), and the assumption-delta contract test — the builder's `_master_include_edges` mapping is keyed by master docname, its two masters' edge sets genuinely differ, every value is a tuple of edge keys (never bare docnames), and the mapping is unchanged after re-running the write phase a second time.
- Proved the removal gate is a genuine gate, not a decoration: temporarily reintroduced the deleted attribute name into `typsphinx/builder.py`, confirmed both structural absence tests went RED, then reverted cleanly (`git diff --stat typsphinx/` empty afterward).
- Ran the SC#4 repo-wide invariant sweep and appended it to `49-EVIDENCE.md`: the ledger grep at three scopes (production package empty, whole tree empty except this plan's own documented constant, `.planning/` non-empty with 89 legitimate history hits), the `@preview` package count re-confirmed at four across every declaring surface with the sync gate green, zero new `typst_*` config values and zero new runtime dependencies (both confirmed by an empty `git diff --stat` over this phase's own base commit), and the two forbidden opportunistic changes (typing-import modernization, a new link-check job) confirmed absent by diff-scoped greps.
- Rebuilt all nine Phase 49 fixtures for real and compared every post-fix Sphinx warning/notice against its recorded pre-fix baseline (`49-RED-EVIDENCE.md`, `49-SHAPES-RED-EVIDENCE.md`) — every one of the nine MATCHES byte-for-byte; no diagnostic was silently removed.
- Recorded the degenerate-shape closure table (all seven shapes, plan-time-decided outcome beside the observed post-fix outcome, both taken from `test_state_guard_shapes_gate.py`'s own passing assertions) — every row MATCHES, discharging SC#2's "decided during planning, not discovered as a test failure" requirement on the record.
- Measured the standalone-content-file behaviour directly (compiled `shared.typ` with no wrapper — succeeds, shows only its own body, the guarded child absent since the published state defaults to empty) and recorded the completed two-layer output-shape change, both as named obligations for Phase 51 (docs) and Phase 52 (CHANGELOG); explicitly excluded the still-owed `:numref:` decision from this handoff, naming it as 49-06's own item.
- Closed with a verbatim green bar: `uv run pytest -q` → 1143 passed, 5 skipped (pre-existing environmental skips), 0 failed; `black --check .`, `ruff check .`, `mypy typsphinx/` all clean.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author tests/test_include_ledger_removal_gate.py** - `bd67a6dd` (test)
2. **Task 2: Run the SC#4 repo-wide sweep and record it in 49-EVIDENCE.md** - `91c0ee1a` (docs)
3. **Task 3: Record the degenerate-shape closure, standalone-content-file behaviour, and Phase 51/52 handoff** - `7c4aedb5` (docs)

_No TDD tasks (plan `type="execute"`) — each task is its own atomic committed artifact per the plan's own task typing._

## Files Created/Modified

- `tests/test_include_ledger_removal_gate.py` - the COMP-11 removal gate and assumption-delta contract test (created)
- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md` - four appended sections: Removal and invariant sweep, No lost diagnostics, Degenerate-shape closure, Handoff to Phase 51 and Phase 52 (plus the standing green-bar record)

## Decisions Made

See `key-decisions` in frontmatter above. In summary: the state-key-literal collector and the toctree-visitor include-call scan both use `ast`-based docstring exclusion rather than text-level heuristics, because the production code's own docstrings legitimately narrate the same syntax the gate is checking for real emission (an f-string worked example, a `#include()` prose mention) — a naive text scan would false-positive on documentation, not on a genuine regression. The wrapper-publication test (Task 1, item 5) uses the subprocess-based `sys.executable -m sphinx` helper (matching this module's own acceptance criterion and the `test_pdf_render_gate.py` precedent), while the assumption-delta and non-mutation tests use `SphinxTestApp` since they need direct access to the builder's own runtime attribute, which a subprocess build cannot expose.

## Deviations from Plan

None (Rules 1-4) — no bug fix, missing functionality, blocking fix, or architectural change was required. Two self-caught wording/precision issues, worth naming since they affected the module's own text before commit rather than after:

1. **Two comments in the initial draft of `tests/test_include_ledger_removal_gate.py` accidentally tripped this plan's own acceptance-criteria greps.** A comment quoting the acceptance criterion's `grep -Ec 'subprocess.*grep'` command literally matched that same pattern against itself (the word "subprocess" followed later by "grep" on the same physical line), and a comment illustrating the false-positive symbol `master_included_docnames` used the underscore-joined spelling that a plain (non-word-boundary) `grep -c '"_included_docnames"'` count would also catch as a second occurrence of the deleted ledger's own name. Both were caught by running the plan's own acceptance-criteria greps against the draft file before committing, and both were reworded (removed the literal quoted grep invocation from the comment; rephrased the false-positive illustration in prose without concatenating the two underscore-joined halves) with no change to the test's own assertions.
2. **The repo-wide prose sweep test initially flagged its own file.** `TestLedgerRemovalFromRepositoryProse::test_ledger_absent_from_repo_wide_prose` walks `tests/` for the deleted ledger's name, which necessarily includes this module's own `DELETED_LEDGER_ATTRIBUTE = "_included_docnames"` constant (the single place the plan's own acceptance criteria requires the literal spelling to appear). Added a `THIS_FILE` self-exclusion to the sweep, mirroring the `.planning/` exclusion's own documented rationale — the module's own text is a deliberate, single, documented exception, not a live reference to reintroduce.

Neither required a code change to production behavior; both were pre-commit self-corrections to this plan's own new test module's text.

## Issues Encountered

None beyond the two self-caught items recorded above under Deviations. The NixOS-sandbox ELF hazard (`uv`/`ruff` generic-linux binaries) required the documented remedy (symlink `uv` to its `/nix/store` target, `patchelf --set-interpreter` for `ruff`) before any command in this worktree could run — applied once at the start of this plan's execution, per the standing project hazard, not itself a deviation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Measured numbers at the end of this plan** (compare against the orchestrator's stated wave-3 baseline):
  - `uv run pytest -m "not slow" -q`: **1075 passed, 73 deselected** (baseline was 1065 passed, 73 deselected — the delta is this plan's own 10 new fast structural tests; the wrapper-publication and assumption-delta/non-mutation tests are NOT marked slow, matching this codebase's own convention for subprocess-`sphinx-build`-based tests with no `typst.compile()` call).
  - `uv run pytest -q` (full suite, including slow): **1143 passed, 5 skipped, 0 failed** (baseline was 1133 passed, 5 skipped — the delta is this plan's own 10 new tests; the 5 skips are the same pre-existing environmental skips: 4 myst-parser docs-extra, 1 corpus-report env-gate).
  - `uv run black --check .`, `uv run python -m ruff check .`, `uv run python -m mypy typsphinx/`: all clean, unchanged from baseline.
- `git status --porcelain typsphinx/` printed nothing throughout all three tasks — this plan touched zero files under the production package, matching its own objective ("No file under `typsphinx/` is touched by this plan").
- `grep -rn '_included_docnames' typsphinx/ tests/ docs/ examples/` returns exactly one hit (`tests/test_include_ledger_removal_gate.py:90`, this plan's own documented constant) — the plan's literal `<verification>` bullet text ("returns no matches") is satisfied in spirit (zero occurrences in production code or in any OTHER test/doc/example file) but not in the byte-literal sense, because Task 1's own acceptance criteria explicitly REQUIRES the deleted symbol's name to appear once, as a single documented module-level constant, in the removal gate's own text. This is recorded here explicitly so a future reader does not mistake the one hit for drift — `49-EVIDENCE.md`'s own `## Removal and invariant sweep` section documents this same exception at first appearance.
- COMP-05, COMP-06 and COMP-11 were already marked `Complete` in `REQUIREMENTS.md` by 49-04 (each backed by a real-compile assertion at that time); this plan deepens their verification with a committed, falsifiable gate but changes no requirement's status. COMP-12 (the full corpus-scale gate) remains Pending, owned entirely by 49-06.
- 49-06 inherits: a proven-red-capable removal gate that will catch any future reintroduction of a build-scoped include ledger; a repo-wide sweep confirming every ROADMAP binding-constraint-#7 invariant intact; a degenerate-shape closure table with zero divergences; and an explicit, unambiguous handoff naming the `:numref:` two-case measurement as 49-06's own still-owed item (not silently assumed complete).
- No blockers.

---
*Phase: 49-per-master-include-graph-with-state-guarded-includes*
*Completed: 2026-08-14*
