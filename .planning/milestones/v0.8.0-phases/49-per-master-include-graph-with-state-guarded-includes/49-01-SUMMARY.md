---
phase: 49-per-master-include-graph-with-state-guarded-includes
plan: 01
subsystem: docs
tags: [typst, state, context, toctree, sphinx, planning-artifact]

# Dependency graph
requires:
  - phase: 48-compile-time-cross-reference-guard
    provides: the compile-time label-existence guard (context + query), whose D-08 line-break
      pitfall and guard-shape convention this plan's contract re-confirms and reuses
provides:
  - "49-EVIDENCE.md `## State-syntax measurement` — nine real typst.compile() probes closing D-09
    for the decided state key (`typsphinx:include-edges`) and edge-key format
    (`<parent>#<occurrence>><child>`)"
  - "49-EXPECTED-STRUCTURE.md `## Emission contract` — every string this phase emits, fixed as a
    substitutable template with one worked substitution each"
  - "49-EXPECTED-STRUCTURE.md `## Degenerate-shape outcome table` — all seven D-06 shapes decided
    at plan time, including a refined mechanism for the literal self-reference case"
  - "49-EXPECTED-STRUCTURE.md `## Fixture specification` — ten fixture projects' complete source
    shape and hand-derived expected edge sets per master"
  - "49-EXPECTED-STRUCTURE.md `## Assertion census` — a per-assertion SURVIVES/FLIPS/NEEDS-SEEDING/
    SYNTHETIC-NODE/STALE-PROSE verdict across every test module with a literal Typst include()
    assertion, with a new expected value for every FLIPS row"
affects: [49-02, 49-03, 49-04, 49-05, 49-06]

# Actuals (#2632)
actuals:
  tokens: 21478
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "State-guarded include: a per-master Typst `state` array, published once by each wrapper,
      read by a static per-emission-site `if <key> in state(...).get() { include(...) }` guard
      inside the existing `context { ... }` block — the include DECISION moves from write time to
      compile time"
    - "One-shared-derivation-function rule (D-05), applied to edge-key construction: the graph
      side and the emission side must call the same function, never spell the key twice"

key-files:
  created:
    - .planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md
    - .planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EXPECTED-STRUCTURE.md
  modified: []

key-decisions:
  - "D-09 closed for this phase's own decided spellings: nine real typst.compile() probes measured
    the array-literal rule at arity 0-3, the trailing-comma silent-corruption hazard (str, not
    array; substring containment, not membership; zero compile error), the dark-guard substring
    semantics, the if-brace line-break rule, interleaving/outline/label reachability, and
    standalone-compile behaviour — all against `typsphinx:include-edges` and
    `<parent>#<occurrence>><child>`, not PROJECT.md's superseded `\"inc\"` sketch."
  - "Refined the self-referencing-toctree degenerate shape beyond D-06's original framing: reading
    sphinx/directives/other.py verbatim shows a literal self-reference (a document toctreeing its
    own docname) is filtered by Sphinx's OWN parse_content — via a pre-loop
    `all_docnames.remove(current_docname)` — before it ever reaches `entries` or `includefiles`, a
    DIFFERENT mechanism than the 2-node-cycle case's `traversed`-list handling, though both produce
    the same 'skip, silently' outcome."
  - "Corrected the read_first's framing of two Phase 48 test modules
    (test_xref_orphan_degrade_render_gate.py, test_label_existence_guard_unit.py): word-boundary
    grep against typsphinx/builder.py and translator.py shows only
    test_duplicate_include_label_render_gate.py references the REAL `_included_docnames` symbol
    this phase deletes; the other two reference `master_included_docnames`, a DIFFERENT symbol
    already deleted in Phase 48 itself — recorded as an excluded false positive, not silently
    dropped."
  - "test_toctree_requirement13.py's `test_toctree_single_content_block_multiple_includes` needs a
    genuine reshape, not merely a SYNTHETIC-NODE fix: post-fix each guard opens its own `{ ... }`
    pair, so the test's `find(\"{\")`/`find(\"}\", block_start)` block-extraction logic would
    silently truncate before the second and third entries' includes. Recorded as a FLIPS row with
    the new expected value (assert against the full output, not a truncated slice)."
  - "test_duplicate_include_label_render_gate.py's whole premise (grep all emitted .typ files for
    a literal include() count == 1) is recorded as MIGRATE, not delete: post-fix the diamond target
    carries TWO static guard occurrences (one dark, one live), so the raw-grep count must become 2,
    with the load-bearing dedup proof moved to a real-compile pypdf marker-count assertion — the
    same invariant, proven through the new mechanism."

patterns-established:
  - "Nine-probe D-09 verification pattern: arity sweep (0-3), type/length readback, the
    omitted-trailing-comma counter-probe (recorded, not adopted), the dark-guard substring proof,
    the if-brace line-break rule, interleaving+outline+label reachability, and a standalone-compile
    control — reusable shape for any future Typst `state`-array syntax question."
  - "Occurrence-indexed edge keys (D-04): the emission side counts occurrences PER DOCUMENT across
    all of that document's own toctree entries; the graph side always claims occurrence 0 (first
    non-traversed appearance), so an occurrence >= 1 key is structurally dark by construction,
    never by a runtime check."

requirements-completed: [COMP-05, COMP-06, COMP-10, COMP-12]

coverage:
  - id: D1
    description: "49-EVIDENCE.md's State-syntax measurement closes D-09 for the decided state key
      and edge-key spellings with nine real typst.compile() probes, superseding PROJECT.md's `inc`
      sketch"
    requirement: "COMP-06"
    verification:
      - kind: other
        ref: "typst.compile() probes recorded verbatim in 49-EVIDENCE.md (arity 0-3, readback,
          no-trailing-comma hazard, dark-guard substring, line-break rule, interleaving/outline,
          standalone) — all nine exit-0/exit-1 as predicted"
        status: pass
    human_judgment: false
  - id: D2
    description: "49-EXPECTED-STRUCTURE.md's Emission contract fixes the state key, edge-key
      occurrence rule, array-literal rendering rule, wrapper/guard line shapes, escaping rule,
      includefiles rule, and traversal rule as substitutable templates with worked substitutions"
    requirement: "COMP-05"
    verification:
      - kind: other
        ref: "regex/grep acceptance checks against 49-EXPECTED-STRUCTURE.md: guard-line pattern
          (>=1), array-literal trailing-comma pattern (>=1), 'selecting' non-port citation (>=1)"
        status: pass
    human_judgment: false
  - id: D3
    description: "49-EXPECTED-STRUCTURE.md's Degenerate-shape outcome table decides all seven D-06
      shapes at plan time, with the traversal fact producing each, refining the self-reference
      mechanism after direct source reading"
    requirement: "COMP-05"
    verification:
      - kind: other
        ref: "structural check: table has 8 rows (7 shapes + header), every row carries an
          explicit include/skip/degrade outcome word"
        status: pass
    human_judgment: false
  - id: D4
    description: "49-EXPECTED-STRUCTURE.md's Fixture specification fixes all ten fixture projects'
      complete source shape and hand-derives each master's expected edge set, before any fixture
      exists"
    requirement: "COMP-10"
    verification:
      - kind: other
        ref: "all ten fixture directory names present in 49-EXPECTED-STRUCTURE.md, each with an
          explicitly derived edge set per master; substring fixture states verbatim which key is a
          substring of which and which guard is dark"
        status: pass
    human_judgment: false
  - id: D5
    description: "49-EXPECTED-STRUCTURE.md's Assertion census enumerates every test module with a
      literal Typst include() assertion, deleted-ledger mention, write-path bypass, include-count
      assertion, or synthetic toctree-node construction, with a per-row verdict and new expected
      values for every FLIPS row"
    requirement: "COMP-12"
    verification:
      - kind: other
        ref: "acceptance scripts: census covers all 19 test modules with a literal include(\")
          call and all files mentioning _included_docnames; all five verdict labels present;
          numeric summary closes the section"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-08-14
status: complete
---

# Phase 49 Plan 01: Emission Contract, Fixture Specification, and Assertion Census Summary

**Closed D-09 with nine real `typst.compile()` probes against the decided
`typsphinx:include-edges` / `<parent>#<occurrence>><child>` spellings, then fixed the full
state-guard emission contract, the ten-fixture source specification with hand-derived edge sets,
the seven-shape degenerate outcome table, and a 19-module repo-wide assertion census with
per-row SURVIVES/FLIPS/NEEDS-SEEDING/SYNTHETIC-NODE/STALE-PROSE verdicts — no production or test
code touched.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-08-14T07:20:00Z (approx.)
- **Completed:** 2026-08-14T07:49:16Z
- **Tasks:** 3
- **Files modified:** 2 (both newly created)

## Accomplishments

- Measured the state-guard Typst syntax with nine independent real compiles (arity 0-3 of the
  array-literal rule, type/length readback, the omitted-trailing-comma silent-corruption hazard,
  the dark-guard substring-vs-membership proof, the if-brace line-break rule, interleaving +
  outline + label reachability, and a standalone-compile control), closing D-09 for this phase's
  own decided spellings — never against PROJECT.md's superseded `"inc"` sketch.
- Wrote the emission contract as substitutable templates with one worked substitution each for the
  state key, the edge-key occurrence rule, the array-literal rendering rule, the wrapper body
  shape, the guard line shape, the escaping rule, the `includefiles` rule (D-03), and the
  traversal rule (COMP-05) — including the forbidden LIFO work-stack shape reconstructed from git
  history and the explicit instruction not to port Sphinx's `selecting: X <- Y` tiebreak.
- Decided all seven D-06 degenerate shapes at plan time with the exact traversal fact producing
  each, refining the self-referencing-toctree case beyond D-06's original framing after reading
  `sphinx/directives/other.py`'s `parse_content` verbatim (a literal self-reference is filtered by
  Sphinx's own pre-loop `all_docnames.remove(current_docname)`, never reaching `includefiles` at
  all — a different mechanism than the 2-node-cycle case).
- Fixed the complete source specification for all ten fixture projects (docnames, `.rst` marker
  strings, toctree entry order, `typst_documents` entries) with hand-derived expected edge sets per
  master, including the mirror-pair (COMP-10), the diamond/interleaving (COMP-07/08/09), the
  `self`/external-URL/duplicate-entry D-10 RED reproduction, three degenerate shapes, a three-master
  coverage fixture, a naturally-arising substring-key fixture, and the `:numref:` two-case fixture.
- Produced a repo-wide assertion census covering all 19 test modules carrying a literal Typst
  `include("` assertion (plus 2 fixture `conf.py` files, `examples/advanced/README.md`, and every
  `_included_docnames`/write-path-bypass/synthetic-toctree-node hit), with a new expected value for
  every FLIPS row and a numeric prediction for what 49-04's migration should touch.

## Task Commits

Each task was committed atomically:

1. **Task 1: Measure state-guard syntax, write 49-EVIDENCE.md** - `2171801e` (docs)
2. **Task 2: Write emission contract, fixture spec, degenerate-shape table** - `fea53b14` (docs)
3. **Task 3: Append repo-wide assertion census** - `7e6490ee` (docs)

_No TDD tasks — this plan produces planning artifacts only, no production or test code._

## Files Created/Modified

- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md` -
  `## State-syntax measurement`: nine real-compile probe transcripts closing D-09
- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EXPECTED-STRUCTURE.md` -
  `## Emission contract`, `## Degenerate-shape outcome table`, `## Fixture specification`,
  `## Assertions that must NOT change`, `## Assertion census`, `## How to find any assertion I
  missed`

## Decisions Made

See `key-decisions` in frontmatter above. In summary: D-09 closed against the DECIDED spellings
(not PROJECT.md's sketch); the self-reference degenerate shape's mechanism was refined by direct
source reading rather than transcribed as-is from D-06; two Phase 48 test modules the plan's own
`<read_first>` suspected of mentioning the deleted ledger were found, on precise word-boundary
grep, to reference a different already-deleted symbol and were excluded as false positives (not
silently dropped — recorded with the correction); and one existing test
(`test_toctree_single_content_block_multiple_includes`) was found to need a genuine block-extraction
reshape, not merely a synthetic-node fix, because nested per-guard braces break its `find()`-based
slice logic.

## Deviations from Plan

None - plan executed exactly as written. All `<precondition>` checks, `<verify>` automated
commands, and `<acceptance_criteria>` items for all three tasks passed without requiring any Rule
1-4 fix.

## Issues Encountered

- **Probe design correction (self-caught during Task 1, before any file was written):** the first
  draft of the Typst probes placed the `context { ... }` guard block at a bare top level with no
  `#` prefix, matching the TRANSLATOR's own internal code-mode wrapping
  (`writer.py:239-240`'s `"#{\n" + body`) rather than the simpler markup-mode form
  `49-RESEARCH.md` Pattern 1 had already independently verified. The bare `context {` was parsed as
  literal markup TEXT (visible in the compiled PDF as the literal string `"context { if ... }"`),
  not as code — a silent false-pass that would have produced misleading probe results. Caught by
  inspecting the compiled PDF text before writing anything to `49-EVIDENCE.md`; redesigned to use
  the `#context { ... }` markup-mode-prefixed shape (which `49-RESEARCH.md` had already proven
  correct), re-ran, and confirmed every probe behaves as measured. Zero cost to the plan's own
  timeline (caught before Task 1's first commit); documented here per the "self-check before
  proceeding" discipline.
- **Acceptance-check `__pycache__` false failure (Task 3):** the STALE-PROSE acceptance script's
  bare `grep -rl '_included_docnames' tests/` (no `--include=*.py`) matched three stale `.pyc`
  bytecode files left over from the earlier `uv run pytest` runs in Tasks 1/2, whose basenames
  never appear in prose (they are gitignored build artifacts, not source). Cleaned all
  `__pycache__` directories outside `.venv/` (a disposable, gitignored artifact — not a
  `typsphinx/`/`tests/` source edit) and re-ran; the check then passed as scripted.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 49-02 and 49-03 (the next-wave fixture-authoring plans) build their `.rst`/`conf.py` fixtures
  directly to this plan's `## Fixture specification` — every docname, toctree entry order, and
  marker string is fixed and ready to transcribe.
- 49-04 (the tracer/emitter plan) has its migration scope bounded by the `## Assertion census`'s
  numeric prediction: any test failure outside `test_toctree_requirement13.py` (9 functions),
  `test_translator.py::test_toctree_generates_outline`, and
  `test_duplicate_include_label_render_gate.py`'s one gate test is an unplanned regression, not a
  predicted migration item.
- No blockers. `git status --porcelain typsphinx/ tests/` printed nothing throughout all three
  tasks; the full fast suite (`uv run pytest -m "not slow" -q`) stayed at 1027 passed / 58
  deselected after each task, confirming this plan changed zero production or test behavior.

---
*Phase: 49-per-master-include-graph-with-state-guarded-includes*
*Completed: 2026-08-14*

## Self-Check: PASSED

- FOUND: `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md`
- FOUND: `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EXPECTED-STRUCTURE.md`
- FOUND: `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-01-SUMMARY.md`
- FOUND commit: `2171801e`
- FOUND commit: `fea53b14`
- FOUND commit: `7e6490ee`
