---
phase: 49-per-master-include-graph-with-state-guarded-includes
plan: 04
subsystem: api
tags: [typst, state, context, toctree, sphinx, compile-time-guard]

# Dependency graph
requires:
  - phase: 49-01
    provides: "49-EXPECTED-STRUCTURE.md's Emission contract, Degenerate-shape
      outcome table, Fixture specification, and Assertion census; 49-EVIDENCE.md's
      nine real typst.compile() probes closing D-09 for the decided
      state-key/edge-key spellings"
  - phase: 49-02
    provides: "tests/fixtures/state_guard_two_master_gate/,
      tests/fixtures/state_guard_mirror_pair_gate/, 49-RED-EVIDENCE.md,
      tests/test_state_guard_composition_gate.py (8 strict xfails naming
      this plan)"
  - phase: 49-03
    provides: "seven state_guard_*_gate fixtures, 49-SHAPES-RED-EVIDENCE.md,
      tests/test_state_guard_shapes_gate.py (8 strict xfails naming this plan)"
provides:
  - "typsphinx/translator.py: INCLUDE_STATE_KEY, make_include_edge_key(),
    derive_master_edge_keys(), render_include_edge_state(),
    render_include_guard() -- the complete Phase 49 derivation surface,
    plus a rewritten visit_toctree() that emits compile-time guards instead
    of unconditional includes"
  - "typsphinx/builder.py: TypstBuilder._build_include_edge_map() and
    ._master_include_edges -- the per-master edge mapping, derived
    unconditionally in write() with a lazy fallback for direct-call test
    paths; the build-scoped _included_docnames ledger is deleted"
  - "typsphinx/writer.py: TypstWriter.render_wrapper() gains an edge_keys
    keyword (default ()) and now emits the state-publication line before
    the existing #include() line"
  - "tests/test_include_edge_derivation_unit.py: new 25-test unit module
    covering traversal, key derivation/escaping, publication rendering
    (structural + real-compile arity readback), guard rendering, and
    builder derivation idempotency/non-mutation"
  - "Every census-listed test module migrated to the new mechanism;
    both Phase 49 gate modules' 16 strict xfails removed"
affects: [49-05, 49-06]

# Actuals (#2632)
actuals:
  tokens: 27547
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Compile-time state guard: the include DECISION moves from write
      time (a build-scoped ledger claiming a docname globally, the first
      time any document's toctree names it) to Typst COMPILE time (a
      per-master published state array, read by a static
      per-emission-site guard) -- so the same content file's bytes behave
      differently for every master that includes it"
    - "One-shared-derivation-function rule (D-05) applied to both edge-key
      construction (make_include_edge_key, called from the builder's
      graph walk AND the translator's guard emission) and the per-master
      mapping itself (_build_include_edge_map, called from write() AND
      lazily from the direct-call write path) -- never two independent
      spellings of the same decision"
    - "Document-order first-encounter-wins DFS with an ordered traversed
      list seeded with the master's own docname (mirrors Sphinx's own
      inline_all_toctrees) -- explicitly NOT a LIFO work-stack, which
      would silently reverse sibling order with no compile error"

key-files:
  created:
    - tests/test_include_edge_derivation_unit.py
  modified:
    - typsphinx/translator.py
    - typsphinx/builder.py
    - typsphinx/writer.py
    - tests/test_toctree_requirement13.py
    - tests/test_translator.py
    - tests/test_duplicate_include_label_render_gate.py
    - tests/test_citation_render_gate.py
    - tests/test_state_guard_composition_gate.py
    - tests/test_state_guard_shapes_gate.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Two pre-existing test defects were fixed as Rule 1 auto-fixes, surfaced
    only once the underlying mechanism started passing (neither is a gap
    in this plan's own emitter): test_state_guard_composition_gate.py's
    diamond test hard-pinned a SHA-256 digest captured from the PRE-FIX
    shared.typ bytes, which cannot survive this phase's own intentional
    byte-emission change (an unconditional include() became a guard
    line) -- replaced with a re-read digest-stability check plus a
    structural guard-line assertion, never re-derived from this plan's
    own emitter output per binding constraint #6. test_state_guard_shapes_gate.py's
    empty-arity test asserted a bare 'context {' substring absence, which
    collided with Phase 48's unrelated xref-guard construct (already
    present pre-fix, per 49-SHAPES-RED-EVIDENCE.md Section 5) -- sharpened
    to the toctree-specific 'context {\\n  set heading(offset:' signature."
  - "The relative include path inside each guard's include(\"...\") call is
    now routed through escape_typst_string() (T-49-01's guard-side half),
    a change the pre-Phase-49 code never made for the unconditional
    include() it emitted -- closing a latent escaping gap as a structural
    consequence of rewriting the emission site, not a separate patch."
  - "One STALE-PROSE fix (tests/test_citation_render_gate.py:583-585) was
    applied even though the file is not in this plan's frontmatter
    files_modified list, because 49-EXPECTED-STRUCTURE.md's own assertion
    census explicitly names it with a rewrite instruction and this task's
    own action text says every STALE-PROSE row must be rewritten in this
    plan -- a one-line past-tense comment correction, zero assertion
    changes, verified still passing."
  - "COMP-05 through COMP-11 (7 of the 8 requirements this plan's frontmatter
    names) are marked complete in REQUIREMENTS.md -- each verified by a
    real compile/PDF-readback assertion now passing, not merely an xfail
    removal. COMP-12 (the full corpus-scale gate) stays Pending; it is
    49-06's own deliverable, untouched by this plan."

patterns-established:
  - "Occurrence-indexed edge keys (D-04): the emission side counts
    per-document occurrences across ALL of a document's own toctree
    entries (flattened, document order); the graph side always claims
    occurrence 0 (first non-traversed appearance), so occurrence >= 1 is
    structurally dark by construction, never by a runtime check."
  - "Array-literal uniform trailing-comma rule: () for zero keys, and for
    one-or-more a parenthesized comma-separated list with an
    UNCONDITIONAL trailing comma after the last element -- no
    len(keys) == 1 special case, removing the omitted-trailing-comma
    silent-corruption hazard by construction."

requirements-completed: [COMP-05, COMP-06, COMP-07, COMP-08, COMP-09, COMP-10, COMP-11]

coverage:
  - id: D1
    description: "The include decision resolves at Typst compile time end
      to end: a real two-master PDF build of state_guard_two_master_gate
      produces both PDFs with SHARED-CHAPTER-MARKER exactly once in EACH,
      from one on-disk shared.typ (confirmed by SHA-256 digest identity)"
    requirement: "COMP-07"
    verification:
      - kind: integration
        ref: "tests/test_state_guard_composition_gate.py::TestStateGuardTwoMasterComposition::test_shared_chapter_appears_in_both_masters_pdf"
        status: pass
      - kind: integration
        ref: "tests/test_state_guard_composition_gate.py::TestStateGuardTwoMasterComposition::test_diamond_shared_content_file_identical_across_masters"
        status: pass
    human_judgment: false
  - id: D2
    description: "The traversal is a fresh recursive DFS with an ordered
      traversed list, document-order first-encounter-wins, with the
      forbidden LIFO work-stack shape named and structurally absent"
    requirement: "COMP-05"
    verification:
      - kind: unit
        ref: "tests/test_include_edge_derivation_unit.py::TestDeriveMasterEdgeKeysTraversal::test_last_listed_child_not_emitted_first"
        status: pass
      - kind: integration
        ref: "tests/test_state_guard_composition_gate.py::TestStateGuardMirrorPairComposition::test_mirror_pair_resolved_heading_levels_and_source_divergence"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every emitted string routes through exactly one shared
      derivation function per rule (edge key, publication line, guard
      line), and the graph-side/emission-side call shapes are asserted
      byte-identical, including docname escaping"
    requirement: "COMP-06"
    verification:
      - kind: unit
        ref: "tests/test_include_edge_derivation_unit.py::TestMakeIncludeEdgeKey"
        status: pass
    human_judgment: false
  - id: D4
    description: "The published array literal resolves as a real Typst
      array at every arity 0-3, including the load-bearing arity-1 case
      where a missing trailing comma would silently degrade to a string"
    requirement: "COMP-06"
    verification:
      - kind: integration
        ref: "tests/test_include_edge_derivation_unit.py::TestPublicationArityReadback::test_published_state_resolves_as_array_with_expected_length"
        status: pass
    human_judgment: false
  - id: D5
    description: "The build-scoped ledger and every reference to it in
      typsphinx/'s own source are gone (word-boundary grep for
      _included_docnames returns zero matches)"
    requirement: "COMP-11"
    verification:
      - kind: other
        ref: "grep -rn '\\b_included_docnames\\b' typsphinx/ tests/ docs/ examples/ (0 matches)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Every census-listed assertion is migrated in this same
      plan: 9 SYNTHETIC-NODE functions, 2 FLIPS modules (1 MIGRATE), 1
      STALE-PROSE fix beyond the frontmatter's own file list -- the fast
      suite is green with zero XPASS"
    requirement: "COMP-05"
    verification:
      - kind: integration
        ref: "uv run pytest -m 'not slow' -q -rxX (1065 passed, 73 deselected, 0 failed, 0 xfailed, 0 xpassed)"
        status: pass
    human_judgment: false
  - id: D7
    description: "Both Phase 49 gate modules run with their strict xfails
      removed, zero xpassed, past-tense prose citing the evidence
      artifacts by name"
    requirement: "COMP-09"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_state_guard_composition_gate.py tests/test_state_guard_shapes_gate.py -q -rxX (28 passed, 0 xfailed, 0 xpassed)"
        status: pass
    human_judgment: false

duration: 43min
completed: 2026-08-14
status: complete
---

# Phase 49 Plan 04: Per-Master Include Graph, State-Guarded Includes Summary

**Moved the toctree include decision from write time (a build-scoped ledger picking one global winner) to Typst compile time (a per-master published `state` array read by a static per-emission-site guard), verified end to end by a real two-master PDF build, then migrated every census-flagged test assertion and removed all 16 strict xfails from the two Phase 49 gate modules.**

## Performance

- **Duration:** 43 min
- **Started:** 2026-08-14T08:28:32Z
- **Completed:** 2026-08-14T09:11:21Z
- **Tasks:** 3
- **Files modified:** 10 (1 created, 9 modified)

## Accomplishments

- Added the complete Phase 49 derivation surface to `typsphinx/translator.py`: `INCLUDE_STATE_KEY`, `make_include_edge_key()` (D-05's one shared edge-key point), `derive_master_edge_keys()` (a fresh recursive document-order first-encounter-wins DFS, explicitly not the forbidden LIFO work-stack shape), `render_include_edge_state()` (the uniform trailing-comma array-literal rule), and `render_include_guard()` (the one-line compile-time guard, condition and brace on one physical line per the measured parser constraint).
- Rewrote `visit_toctree()` to iterate the toctree's `includefiles` list instead of `entries` (closing the `self`/external-URL `TypstError: file not found` compile fatal as a structural consequence), emit one guard per entry via a per-document occurrence counter, and deleted the build-scoped `_included_docnames` ledger and all its lookup/dedup logic.
- Added `TypstBuilder._build_include_edge_map()` (the one per-master derivation function) and `_master_include_edges`, derived unconditionally in `write()` with a lazy same-function fallback for the several existing unit tests that call the per-document write path directly without ever calling `write()`.
- Gave `TypstWriter.render_wrapper()` a new `edge_keys` keyword (default `()`, so every existing direct caller keeps working) and made it emit the state-publication line immediately before the existing `#include()` line.
- Proved the tracer end to end: a real `sphinx-build -b typstpdf` of `state_guard_two_master_gate`, read back through `pypdf`, shows `SHARED-CHAPTER-MARKER` exactly once in EACH of the two compiled PDFs — the direct inversion of `49-RED-EVIDENCE.md`'s recorded 0/1 split — from one on-disk `shared.typ` (confirmed by SHA-256 digest identity across both compiles).
- Authored `tests/test_include_edge_derivation_unit.py` (25 tests): traversal (three-child order, mirror-pair orderings, 2-node cycle, self-reference, duplicate child, empty master, the direct last-listed-child regression detector), key derivation/escaping (graph-side vs. emission-side agreement, quote/backslash escaping), publication rendering (arities 0-3 structural + a real-compile type/length readback probe), guard rendering (one-line shape, escaped include path, fresh-translator empty counter), and builder derivation idempotency/non-mutation.
- Migrated every module the assertion census (`49-EXPECTED-STRUCTURE.md`) predicted: all 9 `test_toctree_requirement13.py` functions (SYNTHETIC-NODE, plus 2 genuine brace-count/block-extraction reshapes), `test_translator.py::test_toctree_generates_outline` (SYNTHETIC-NODE), and `test_duplicate_include_label_render_gate.py`'s one MIGRATE function (rewritten from a raw `.typ`-grep dedup check to a structural sanity check plus a load-bearing `pypdf` marker-count proof on the compiled PDF). Also fixed one STALE-PROSE row (`test_citation_render_gate.py`) the census named but the frontmatter's own file list omitted.
- Removed all 16 strict `xfail(strict=True)` markers (7 in `test_state_guard_composition_gate.py`, 8 in `test_state_guard_shapes_gate.py`) after confirming each corresponding assertion now passes for the right reason; rewrote both modules' top-of-file and per-test docstrings in the past tense, citing `49-RED-EVIDENCE.md`/`49-SHAPES-RED-EVIDENCE.md` by name instead of claiming a marker they no longer carry (the Phase 47 WR-02 staleness lesson).

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire the per-master include graph end to end and prove it on one real two-master PDF build** - `7e262c8c` (feat)
2. **Task 2: Migrate every assertion the census marked FLIPS/NEEDS-SEEDING/SYNTHETIC-NODE/STALE-PROSE** - `e2a33c59` (test)
3. **Task 3: Remove the strict-xfail markers and confirm zero XPASS** - `58666752` (test)

_No TDD tasks (plan `type="execute"`, with Task 1 as the phase's own `type="tracer"`) — each task is its own atomic real-compile artifact per the plan's own task typing._

## Files Created/Modified

- `typsphinx/translator.py` - five new module-level derivation functions plus the rewritten `visit_toctree()` and a new per-document occurrence counter
- `typsphinx/builder.py` - `_build_include_edge_map()`/`_master_include_edges` replacing the deleted `_included_docnames` ledger
- `typsphinx/writer.py` - `render_wrapper()`'s new `edge_keys` keyword and the state-publication line
- `tests/test_include_edge_derivation_unit.py` - new 25-test unit module (created)
- `tests/test_toctree_requirement13.py` - 9 functions migrated (includefiles, brace-count/block-extraction reshapes)
- `tests/test_translator.py` - 1 function migrated (includefiles)
- `tests/test_duplicate_include_label_render_gate.py` - MIGRATE: grep-based dedup check plus a new pypdf marker-count load-bearing proof
- `tests/test_citation_render_gate.py` - 1 stale-prose comment rewritten
- `tests/test_state_guard_composition_gate.py` - 7 strict-xfail markers removed, docstrings rewritten past-tense, digest-pin bug fixed
- `tests/test_state_guard_shapes_gate.py` - 8 strict-xfail markers removed, `_REASON_*` constants folded into docstrings, context-substring-check bug fixed
- `.planning/REQUIREMENTS.md` - COMP-05 through COMP-11 marked complete (COMP-12 stays Pending, owned by 49-06)

## Decisions Made

See `key-decisions` in frontmatter above. In summary: two pre-existing test defects (a stale pre-fix digest pin that could never survive this phase's own intentional byte change, and an over-broad `context {` substring check colliding with Phase 48's unrelated xref guard) were fixed as Rule 1 auto-fixes rather than worked around; the guard-side relative include path was routed through `escape_typst_string()` even though the pre-Phase-49 code never escaped its unconditional include path, closing a latent gap as a structural consequence of the rewrite; one STALE-PROSE fix was applied to a file outside the frontmatter's own list because the census and this task's own action text both required it; and COMP-05 through COMP-11 were marked complete in REQUIREMENTS.md, each backed by a real-compile assertion, while COMP-12 (49-06's own corpus-scale gate) was left Pending.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Stale pre-fix SHA-256 digest pin in the diamond test**
- **Found during:** Task 1 verification (running the two gate modules against the new mechanism)
- **Issue:** `test_state_guard_composition_gate.py::test_diamond_shared_content_file_identical_across_masters` hard-pinned a SHA-256 digest captured from `shared.typ`'s PRE-FIX bytes (an unconditional `include()` line). Post-fix, the SAME docname's content carries a state-guarded line instead — a different, intentional byte sequence by this phase's own design, not drift. The digest comparison could never pass post-fix as written.
- **Fix:** Removed the `xfail` marker's premise and replaced the hard-pinned digest comparison with (a) a digest-stability re-read (proving the file wasn't mutated between the two masters' compiles) and (b) a structural regex assertion against the guard line the Emission contract mandates — proving the same invariant (one physical file, correctly guarded) without re-deriving an expected value from this plan's own emitter output (binding constraint #6).
- **Files modified:** `tests/test_state_guard_composition_gate.py`
- **Verification:** `uv run pytest tests/test_state_guard_composition_gate.py::TestStateGuardTwoMasterComposition::test_diamond_shared_content_file_identical_across_masters -q` passes.
- **Committed in:** `7e262c8c` (part of Task 1's commit, since the fix was needed to complete Task 1's own tracer verification)

**2. [Rule 1 - Bug] Over-broad `context {` substring check collided with Phase 48's unrelated xref guard**
- **Found during:** Task 1 verification
- **Issue:** `test_state_guard_shapes_gate.py::test_empty_and_single_entry_array_literals` asserted `"context {" not in orphan_index` to prove no toctree scope block was emitted for a master with no toctree. `state_guard_orphan_ref_gate`'s own `:ref:` cross-reference triggers Phase 48's UNRELATED compile-time xref guard, which also emits a `context { let __tsx_body = [...` construct — already present pre-fix (`49-SHAPES-RED-EVIDENCE.md` Section 5 recorded this exact match, attributing it to Phase 48), but masked pre-fix by an earlier assertion in the same test failing first.
- **Fix:** Sharpened the check to the toctree-specific opening signature (`"context {\n  set heading(offset:"`), which this phase's own mechanism governs, leaving Phase 48's own construct unaffected.
- **Files modified:** `tests/test_state_guard_shapes_gate.py`
- **Verification:** `uv run pytest tests/test_state_guard_shapes_gate.py::TestEmptyAndSingleEntryArities::test_empty_and_single_entry_array_literals -q` passes.
- **Committed in:** `7e262c8c` (part of Task 1's commit, same reason as above)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bug fixes in pre-existing test assertions, neither an architectural change, neither a change to typsphinx production behavior). **Impact on plan:** Zero scope creep; both were necessary to complete Task 1's own tracer verification and were pre-existing defects this phase's mechanism change surfaced, not caused.

## Issues Encountered

- **Several of this plan's own acceptance-check scripts are over-broad and produced false positives against prose, not code** — each investigated and resolved by rewording rather than by weakening the underlying invariant:
  - The `git diff -U0 | grep -c '^-.*heading.offset'` check (meant to prove the D-08 heading-offset CODE line is byte-identical) also matched a removed DOCSTRING sentence containing the phrase "heading offset" — resolved by restoring that specific docstring sentence verbatim and adding a NEW sentence alongside it, rather than deleting/rewording the original.
  - The `grep -c '.pop('` check inside `derive_master_edge_keys`'s own body (meant to prove the function is genuinely recursive, not a LIFO work-stack) also matched the function's own DOCSTRING, which illustrates the FORBIDDEN shape using literal `stack.pop()` text as an example — resolved by rephrasing the illustration in prose without the literal substring.
  - The plan-level `grep -rn '_included_docnames' typsphinx/ tests/ docs/ examples/` check (meant to prove the deleted ledger is gone) is NOT word-boundary-anchored, so it also matches `master_included_docnames`/`_compute_master_included_docnames` — a DIFFERENT symbol Phase 48 already deleted, which 49-01's own census had already identified and excluded as a false positive by the SAME grep imprecision. Word-boundary grep (`\b_included_docnames\b`) confirms zero real matches; the bare grep's false positives are unchanged pre-existing text, not this plan's own output.
  - The Task 2 acceptance script checking "every hand-constructed toctree node carries an includefiles list" flags `test_template_engine.py`'s six `addnodes.toctree()` constructions, which the census explicitly documents as OUT OF SCOPE (they set `maxdepth`/`numbered`/`caption` and call `extract_toctree_options()`, never reaching `visit_toctree` at all) — left untouched per the census's own explicit exclusion.
  - The Task 3 acceptance script `grep -c 'xfail' <module> == 0` conflicts with the SAME task's own action text, which requires rewriting docstrings to state "the pre-fix RED was recorded as a strict xfail" in past tense, citing the evidence artifact. Zero actual `@pytest.mark.xfail` decorators remain in either module (confirmed via `grep -c 'xfail(strict=True'` returning 0 and via `-rxX` pytest output showing 0 xfailed/0 xpassed); the residual `xfail` occurrences are exclusively in the past-tense prose the action text itself requires.
- None of these required any change to production code or to the substance of any test assertion — each was a wording adjustment to satisfy an imprecise mechanized check while preserving (or, in the two Rule-1 cases above, correcting) the underlying invariant.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Measured numbers at the end of this plan** (compare against the orchestrator's stated baselines):
  - `uv run pytest -m "not slow" -q -rxX`: **1065 passed, 73 deselected, 0 failed, 0 xfailed, 0 xpassed** (baseline was 1036 passed, 69 deselected, 8 xfailed — the 8 pre-existing xfails and 4 new deselected-slow tests plus this plan's own 25 new fast unit tests account for the delta).
  - `uv run pytest tests/test_state_guard_composition_gate.py tests/test_state_guard_shapes_gate.py -q -rxX`: **28 passed, 0 failed, 0 xfailed, 0 xpassed** (baseline was 12 passed, 16 xfailed).
  - `uv run pytest -q` (full suite, including slow): **1133 passed, 5 skipped** (pre-existing myst-parser docs-extra environmental skips, unrelated to this phase), **0 failed, 0 xfailed, 0 xpassed**.
  - `uv run black --check typsphinx/ tests/`, `uv run python -m ruff check typsphinx/ tests/`, `uv run python -m mypy typsphinx/`: all clean.
- 49-05 and 49-06 (the next-wave plans) inherit a fully-migrated corpus with zero outstanding xfails from this phase and REQUIREMENTS.md already reflecting COMP-05 through COMP-11 as complete.
- COMP-12 (the full Sphinx `doc/` corpus compiling fatal-free at scale) is explicitly 49-06's own deliverable and was not attempted here, per this plan's own scope boundary.
- No blockers. `git status --porcelain` shows only this SUMMARY.md (untracked) and the REQUIREMENTS.md requirement-completion edit immediately before this plan's final metadata commit — no other uncommitted changes.

---
*Phase: 49-per-master-include-graph-with-state-guarded-includes*
*Completed: 2026-08-14*

## Self-Check: PASSED

- FOUND: `typsphinx/translator.py`
- FOUND: `typsphinx/builder.py`
- FOUND: `typsphinx/writer.py`
- FOUND: `tests/test_include_edge_derivation_unit.py`
- FOUND: `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-04-SUMMARY.md`
- FOUND commit: `7e262c8c`
- FOUND commit: `e2a33c59`
- FOUND commit: `58666752`
