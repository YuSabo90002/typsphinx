---
phase: 74-the-doctest-block-handler-its-real-compile-gate-and-the-docs
plan: 02
subsystem: core-translator
tags: [sphinx, typst, render-gate, real-compile-gate, fixture, doctest, tdd-red]

# Dependency graph
requires:
  - phase: 74-the-doctest-block-handler-its-real-compile-gate-and-the-docs
    provides: "phase-wide ROADMAP/CONTEXT/RESEARCH binding constraints (RED-before-GREEN, D-06 fixture contexts, TRN-01/TRN-02)"
provides:
  - "GATE-01 real-compile gate module (tests/test_doctest_block_render_gate.py) with 11 tests over 3 masters, covering D-06's context (a) plain-paragraph doctest block and context (b) shapes (b1) definition-list Examples: item and (b2) bullet-list item, both non-first-position"
  - "the doctest_block_render_gate fixture project (conf.py + 3 reST documents) proving the missing handler on a real sphinx-build -b typstpdf compile"
  - "verbatim RED evidence (74-RED-EVIDENCE.md), recorded on a commit whose typsphinx/ tree equals the milestone base 6cc44f22, proving the gate detects the defect before any fix lands"
affects: [74-03]

# Actuals (#2632)
actuals:
  tokens: 17836
  tasks: 2
  commits: 4
  plan_head_before: 8ea10273265e3966b6e650bad43cf90c9598ed65

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One module-scoped pytest fixture (doctest_block_build, built on tmp_path_factory) drives ONE sphinx-build -b typstpdf invocation shared across every test method -- the standing GATE-01 pattern from tests/test_inline_image_separator_render_gate.py"
    - "Expected doctest text is read from the fixture's own reST source via _source_doctest_block (never transcribed from observed build output), matching the 'evidence not laundered' discipline the phase's threat register requires (T-74-06)"
    - "RED restore-free choreography: this plan needed no git checkout <SHA> -- <file> restore step, because the worktree's own HEAD already carries no handler -- confirmed by a zero-diff against the milestone base before any commit"

key-files:
  created:
    - tests/test_doctest_block_render_gate.py
    - tests/fixtures/doctest_block_render_gate/conf.py
    - tests/fixtures/doctest_block_render_gate/index.rst
    - tests/fixtures/doctest_block_render_gate/context_a_paragraph.rst
    - tests/fixtures/doctest_block_render_gate/context_b_nonfirst_positions.rst
    - .planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-RED-EVIDENCE.md
  modified: []

key-decisions:
  - "Task 1 (tracer) proved context (a) end to end first -- fixture, gate module (6 tests), real compile, and RED transcript -- before Task 2 widened the module to the full 11-test / 3-master D-06 set. This matches the plan's own tracer-then-expansion structure and let the tracer feedback gate (row 3: interactive, end-of-phase, automated-only <verify>) re-run and pass before expansion, per checkpoints.md's precedence chain."
  - "Context (b)'s two shapes were built as a definition-list Examples: item (b1) and a bullet-list item (b2), per the CONTEXT.md D-06 AMENDED correction -- not a literal field-list/definition-list pair -- because research measured that only a bullet-list item genuinely exercises in_list_item/list_item_needs_separator; a definition/field_body container never sets that flag."
  - "requirements-completed is deliberately empty: TRN-01/TRN-02's truths are only half-discharged by this plan (the RED half). They become true only when 74-03 lands the handler and the same gate turns GREEN, per this plan's own <flagged_assumptions> section."

requirements-completed: []  # TRN-01, TRN-02 close only after 74-03 turns this gate GREEN (per this plan's <output> directive: do not edit REQUIREMENTS.md)

coverage:
  - id: D1
    description: "GATE-01 real-compile gate module (11 tests, 3 masters) covering D-06's context (a) and context (b) shapes (b1)/(b2), recorded observably RED against the pre-handler translator"
    requirement: "TRN-02"
    verification: []
    human_judgment: true
    rationale: "This plan's success criterion is a RED gate, not a passing one -- the 8 required tests are EXPECTED to FAIL right now (that is the proof the gate detects the defect), and the handler does not exist until 74-03. A verification entry with status: pass would misrepresent what was measured; the plan's own <verify> automated blocks (re-run and confirmed passing for both tasks) are the actual proof this deliverable is correct, not a pytest PASS."
  - id: D2
    description: "Verbatim RED transcript in 74-RED-EVIDENCE.md (pytest -rA output, direct sphinx-build -b typstpdf log, RED_TREE_SHA identity check against the milestone base, RED_VERDICT = MET)"
    requirement: "TRN-02"
    verification: []
    human_judgment: true
    rationale: "Evidentiary/documentation artifact. Its correctness was self-verified via the plan's own automated <verify> scripts for both tasks (all measured, no HALT emitted), not via a pass/fail test run of production code."

# Metrics
duration: ~11min
completed: 2026-09-19
status: complete
---

# Phase 74 Plan 02: The doctest_block GATE-01 Real-Compile Gate (RED) Summary

**Eleven-test GATE-01 render gate over three masters, recorded observably RED against the pre-handler translator, proving context (a)'s plain-paragraph doctest block is a real `typst.compile()` refusal and context (b)'s definition-list/bullet-list shapes collapse without a separator.**

## Performance

- **Duration:** ~11 min
- **Started:** 2026-09-19T22:04:55Z
- **Completed:** 2026-09-19T22:15:28Z
- **Tasks:** 2
- **Files modified:** 6 (5 created test/fixture files + 1 evidence file)

## Accomplishments
- Built the `doctest_block_render_gate` fixture (3 masters: `index`, `context_a_paragraph`, `context_b_nonfirst_positions`) exactly per D-06's two contexts and three shapes.
- Wrote `tests/test_doctest_block_render_gate.py` with the 11 fixed test ids the spec names, all expected text sourced from the fixture's own reST via `_source_doctest_block` (never from observed output).
- Recorded the gate observably RED at `RED_TREE_SHA` (215e9715...), whose `typsphinx/` tree is byte-identical to the milestone base `6cc44f22` -- confirmed by a zero-diff, not assumed.
- The direct `-b typstpdf` build reproduced the real compile refusal research predicted: exit 2, `expected semicolon or line break` (10 occurrences), 3 `unknown node type: <doctest_block` warnings (one per shape sentinel), and only `context_b_nonfirst_positions-out.pdf` written (the two (b) shapes compile fine pre-handler; their RED is content/line-structure only, matching the research prediction).
- Task 1 ran as a `type="tracer"` task: context (a) alone, end to end, before Task 2 expanded to the full 3-master/11-test module. The tracer feedback gate (automated-only `<verify>`, interactive end-of-phase mode) re-ran and passed before expansion began.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: context (a) end to end** - `39a985e0` (test) + `d421feb9` (docs, tracer RED evidence)
2. **Task 2: Context (b) shapes, full eleven-test module, verbatim RED transcript** - `215e9715` (test) + `035babe0` (docs, full RED evidence)

_Note: each task's own `<verify>` automated block was re-run and confirmed passing (matching the plan's own acceptance criteria) before proceeding to the next task -- no separate "plan metadata" commit beyond the two evidence commits above, per this plan's explicit instruction not to touch REQUIREMENTS.md/ROADMAP.md/STATE.md._

## Files Created/Modified
- `tests/test_doctest_block_render_gate.py` - the GATE-01 gate module: 11 tests, `FIXTURE_DIR`/`MASTER_DOCNAMES`/`SHAPE_SENTINELS`/`UNKNOWN_DOCTEST_BLOCK`/`FENCE_OPEN` constants, `_source_doctest_block` (expected-text-from-source helper), `_unknown_doctest_chunks`, `_assert_pdf_magic`, `_read_typ`, module-scoped `doctest_block_build` fixture
- `tests/fixtures/doctest_block_render_gate/conf.py` - 3 `typst_documents` masters, all `-out.typ` de-collision targets
- `tests/fixtures/doctest_block_render_gate/index.rst` - root master toctreeing both context documents
- `tests/fixtures/doctest_block_render_gate/context_a_paragraph.rst` - context (a): leading paragraph, doctest block, trailing paragraph
- `tests/fixtures/doctest_block_render_gate/context_b_nonfirst_positions.rst` - context (b): shape (b1) definition-list `Examples:` item, shape (b2) bullet-list item, both non-first position
- `.planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-RED-EVIDENCE.md` - head-check/provisioning record, tracer RED (context a), RED tree identity, RED pytest run (verbatim `-rA` transcript), RED direct build (verbatim log), RED emitted regions (the collapsed `text(">>> ` lines the gate rejects), RED verdict (`MET`)

## Decisions Made
- Followed D-06's AMENDED correction exactly: context (b) is a bullet-list item (b2), not a literal field-list, because only a bullet-list item genuinely exercises `in_list_item`/`list_item_needs_separator` (research measured this directly against the translator source).
- `requirements-completed` left empty in this SUMMARY's frontmatter -- TRN-01/TRN-02 close only when 74-03 turns this same gate GREEN, per this plan's own `<flagged_assumptions>` and `<output>` sections.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The GATE-01 gate is fully built, collects 11 tests, and is recorded observably RED on a commit whose `typsphinx/` tree equals the milestone base (`6cc44f22`), verified by a zero-diff.
- 74-03 can now implement `visit_doctest_block`/`depart_doctest_block` (D-03/D-04) and turn this exact gate GREEN -- no further fixture or gate-module work is expected to be needed.
- Zero pre-existing test files were touched (`git diff --name-status 6cc44f22..HEAD -- tests` is all `A` rows), and `typsphinx/` is byte-identical to the milestone base across this whole plan.

---
*Phase: 74-the-doctest-block-handler-its-real-compile-gate-and-the-docs*
*Completed: 2026-09-19*

## Self-Check: PASSED

- All 6 key files (5 test/fixture files + 74-RED-EVIDENCE.md) verified present with `[ -f ]`.
- All 4 task commits (`39a985e0`, `d421feb9`, `215e9715`, `035babe0`) verified present in `git log --oneline`.
- Both tasks' own `<automated>` `<verify>` scripts (Task 1's context-(a) tracer check, Task 2's full 11-test/RED-verdict check) were re-run against the final HEAD and both exited 0 -- all acceptance criteria and plan-level `<verification>` bullets hold: 11 tests collected, `RED_TREE_SHA`'s `typsphinx/` tree is byte-identical to the milestone base, the eight required tests are FAILED, and `git diff --name-status 6cc44f22..HEAD -- tests` is all `A` rows.
