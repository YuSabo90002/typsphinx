---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 01
subsystem: testing
tags: [pytest, sphinx, typst, gentle-clues, admonitions, gate-01, region-scoping]

# Dependency graph
requires:
  - phase: 38-structural-indentation-info-fields
    provides: SHARED_INDENT_STEP and the desc_content/field_list pad() wrapper (unrelated to this plan's scope, but the phase this one follows in the milestone's execution order)
provides:
  - "A full ten-type admonition census in tests/fixtures/admonition_render_gate/index.rst, each type carrying a distinct greppable sentinel and a CONTROL/DEFECT CASE label"
  - "tests/test_admonition_bucket_render_gate.py: region-scoped .typ-string bucket and catalog-title GATE-01 RED for ADM-01/ADM-02/ADM-03 (D-02, D-03 x2, D-09, D-10, D-04/D-05)"
  - "The compiled-PDF half of ADM-01/ADM-02 inside TestAdmonitionPdfRenderGate, sharing one real compile via a class-scoped fixture"
  - "39-GATE-EVIDENCE-01.md: verbatim RED, the RED-vs-CONTROL table, and the corrected RESEARCH.md blast-radius grep"
affects: [39-05-plan-admonition-taxonomy-translator-fix]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Region-scoped .typ-string assertion via backward-scan-from-sentinel (_clue_open_before/_title_arg_after), restricted to a known function-name allowlist so a generic identifier+({ shape (e.g. par({) is never mistaken for a clue-function box open"
    - "Class-scoped PDF-compile fixture returning extracted text, shared across multiple thin test methods asserting disjoint slices of the same real-compile artifact (topic_line_block_render_gate_pdf_text precedent, now also applied to TestAdmonitionPdfRenderGate)"
    - "Catalog-title expectations read from sphinx.locale.admonitionlabels inside the test itself (never transcribed), so the assertion cannot drift from the source of truth it is proving"

key-files:
  created:
    - tests/test_admonition_bucket_render_gate.py
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-01.md
  modified:
    - tests/fixtures/admonition_render_gate/index.rst
    - tests/test_pdf_render_gate.py

key-decisions:
  - "Removed the redundant standalone 'Golden Note' section from admonition_render_gate/index.rst so exactly one top-level .. note:: construct remains (the pre-existing note-with-bullet-list), satisfying the plan's exact-occurrence acceptance criterion without disturbing the protected note-with-bullet-list/warning-with-code-block/nested-pair regression coverage."
  - "The D-10 base-clue-absence negative-direction guard is scoped to this plan's own ten admonition-fixture sentinels only, deliberately excluding the two topic-fixture sentinels (ADMONITIONCUSTOMSENTINEL, TOPICBODYSENTINEL) that are already the D-09/D-10 DEFECT-CASE subjects -- re-testing 'not clue' for those two would restate their own equality assertions as an extra, uncounted RED not named in the plan's exact-six-failures acceptance criterion."
  - "The catalog-title test and each DEFECT-CASE bucket test are separate, non-parametrized pytest functions/one table-driven function respectively (not pytest.mark.parametrize), matching the plan's literal 'exactly five failing bucket assertions ... and a failing catalog-title assertion' (six total) rather than producing nine-plus separately-counted parametrize nodes."

patterns-established:
  - "_clue_open_before / _title_arg_after: reusable region-scoping helper pair for any future .typ-string gate that needs to resolve 'which construct contains this sentinel' rather than searching the whole document."

requirements-completed: []  # ADM-01/ADM-02/ADM-03 are NOT complete -- this plan is the GATE-01 RED only; the translator fix lands in 39-05.

coverage:
  - id: D1
    description: "admonition_render_gate/index.rst carries all ten real Sphinx admonition types plus the pre-existing nested note/warning pair, each with a distinct body sentinel and a CONTROL/DEFECT CASE comment"
    requirement: "ADM-01"
    verification:
      - kind: integration
        ref: "uv run python -m sphinx -b typst tests/fixtures/admonition_render_gate /tmp -- exits 0, emits index.typ"
        status: pass
      - kind: integration
        ref: "typst.compile() on the emitted index.typ -- no exception"
        status: pass
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonition_pdf_has_no_literal_source_leak"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_admonition_bucket_render_gate.py records the region-scoped RED for the five bucket moves (D-02, D-03 x2, D-09, D-10) and the catalog-title change (D-04/D-05), with the seven CONTROL types green"
    requirement: "ADM-01"
    verification:
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py -- 6 failed (5 DEFECT-CASE + 1 catalog-title), 4 passed (2 self-checks + CONTROL + base-clue-absence guard)"
        status: pass
    human_judgment: false
  - id: D3
    description: "attention/danger route through error() and seealso through tip(), all currently RED against the untouched translator"
    requirement: "ADM-02"
    verification:
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py::test_attention_routes_to_error_bucket, ::test_danger_routes_to_error_bucket -- both FAILED as designed (RED)"
        status: pass
    human_judgment: false
  - id: D4
    description: "the generic .. admonition:: routes to notify() and .. topic:: routes to abstract(), currently RED against the untouched translator (clue() today)"
    requirement: "ADM-03"
    verification:
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py::test_generic_admonition_routes_to_notify, ::test_topic_routes_to_abstract -- both FAILED as designed (RED)"
        status: pass
    human_judgment: false
  - id: D5
    description: "compiled-PDF half of ADM-01/ADM-02: seealso/attention/danger body sentinels and their catalog titles asserted against a real typst.compile(), sharing the fixture with the pre-existing D-04 leak gate"
    requirement: "ADM-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate -- FAILED on header text as designed (RED); body sentinels pass"
        status: pass
    human_judgment: false

# Metrics
duration: 15min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 01: Admonition Taxonomy GATE-01 RED Summary

**Region-scoped `.typ`-string and compiled-PDF GATE-01 RED for ADM-01/ADM-02/ADM-03, hand-derived from 39-CONTEXT.md's locked bucket table and `sphinx.locale.admonitionlabels`, recording six structural failures against the untouched translator with zero `typsphinx/` changes.**

## Performance

- **Duration:** 15 min
- **Started:** 2026-08-02T09:44:31+09:00 (phase-start commit `92c0891`)
- **Completed:** 2026-08-02T09:59:17+09:00
- **Tasks:** 3
- **Files modified:** 4 (1 fixture extended, 1 new test module, 1 existing test module extended, 1 new evidence file)

## Accomplishments
- Extended the existing `admonition_render_gate` fixture into a full ten-type census (note, warning, tip, important, caution, seealso, hint, error, danger, attention) with per-type body sentinels and CONTROL/DEFECT CASE comments, without disturbing the pre-existing Phase 8.1 regression coverage (note-with-bullet-list, warning-with-code-block, nested note/warning pair).
- Wrote a new region-scoped `.typ`-string gate module (`tests/test_admonition_bucket_render_gate.py`) with a backward-scanning helper (`_clue_open_before`) that resolves which gentle-clues function opened the box containing a given sentinel — never a document-wide search — plus a companion helper (`_title_arg_after`) that balance-matches the enclosing box to extract its title argument.
- Recorded the RED: five DEFECT-CASE bucket tests (seealso D-02, attention/danger D-03, generic admonition D-09, topic D-10) plus one table-driven catalog-title test (D-04/D-05) fail against the untouched translator — exactly six failing tests, all structural equality/absence mismatches, none a `sphinx-build` or `typst.compile()` failure.
- Extended `TestAdmonitionPdfRenderGate` with the compiled-PDF half: extracted its inline compile into a class-scoped fixture (mirroring the `topic_line_block_render_gate_pdf_text` precedent) and added `test_admonitionbuckettitlegate`, RED on header text and green on sentinel survival.
- Corrected RESEARCH.md's claim that no fixture contains `danger` — `admonition_render_gate/index.rst` already had it pre-phase; `seealso`/`attention` were genuinely absent, confirmed by a repo-wide grep recorded in the evidence file.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend the admonition render-gate fixture into a full ten-type census** - `14c4330` (test)
2. **Task 2: Write the bucket and catalog-title gate module, RED against the untouched translator** - `61c0ad9` (test)
3. **Task 3: Add the compiled-PDF half for ADM-01/ADM-02 and record the RED evidence** - `301d62c` (test)

_No TDD-style multi-commit tasks in this plan — every task is itself GATE-01 RED authoring, not a red/green/refactor cycle over new production code._

## Files Created/Modified
- `tests/fixtures/admonition_render_gate/index.rst` - Extended to all ten real Sphinx admonition types, each with a body sentinel and a CONTROL/DEFECT CASE comment; removed the redundant standalone "Golden Note" section.
- `tests/test_admonition_bucket_render_gate.py` - New GATE-01 module: two session-scoped `.typ`-build fixtures, `_clue_open_before`/`_title_arg_after` region-scoping helpers, five DEFECT-CASE tests, one CONTROL test, one catalog-title test, one base-clue-absence guard, two self-checks.
- `tests/test_pdf_render_gate.py` - `TestAdmonitionPdfRenderGate`'s compile extracted into a class-scoped `admonition_render_gate_pdf_text` fixture; added `test_admonitionbuckettitlegate` for the compiled-PDF half of ADM-01/ADM-02.
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-01.md` - Verbatim RED for both gate modules, the RED-vs-CONTROL table, the corrected fixture-blast-radius grep, and the `git diff --stat -- typsphinx/` proof of zero source changes.

## Decisions Made
- Removed the pre-existing "Golden Note" section (a second, redundant top-level `.. note::` construct) rather than keeping it unsentineled, so the fixture has exactly one top-level occurrence of each admonition type outside the nested pair — satisfying Task 1's exact-occurrence acceptance criterion. Verified nothing else in the repo references that section by name (`git grep "Golden Note"` — only the fixture itself and an unrelated Phase 11 pattern-doc mention).
- Scoped the D-10 base-clue-absence negative-direction guard to this plan's own ten admonition-fixture sentinels, explicitly excluding the two topic-fixture sentinels that are the D-09/D-10 DEFECT-CASE subjects themselves — avoids an extra, plan-acceptance-criteria-uncounted RED while still discharging the "no real admonition type ever uses base `clue`" invariant the action text asks for.
- Implemented the five DEFECT-CASE bucket checks as five separate test functions (not one parametrized test) and the catalog-title check as one table-driven function collecting all mismatches into a single assertion — matching the plan's literal "exactly five failing bucket assertions ... and a failing catalog-title assertion" (six total failing tests), verified by running the module and counting.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' acceptance criteria and verify commands pass as specified; no Rule 1-4 auto-fixes were needed.

## Issues Encountered
- `uv run ruff` and a freshly-`uv sync`'d `.venv/bin/uv` are generic-linux ELF binaries that fail under this NixOS sandbox (`Could not start dynamically linked executable`) — resolved per the project's standing memory note by symlinking the main checkout's patchelf'd `ruff`/nix-store `uv` into the worktree's `.venv/bin/`, per `nixos-sandbox-test-env` guidance. No code impact; environment-only.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- The GATE-01 RED for the admonition half of Phase 39 is fully recorded: 6 failing tests across two modules, all structural, all traceable to a named decision (D-02/D-03/D-09/D-10/D-04/D-05), against phase-start commit `92c0891`.
- 39-05 (the translator fix plan) can now implement `_visit_admonition`/`_depart_admonition`'s `admonitionlabels` lookup and the five call-site function-name changes, then flip this plan's six RED tests to GREEN without touching their expectations (which are hand-derived from 39-CONTEXT.md, not from any translator output).
- No blockers. `typsphinx/` remains untouched by this plan, confirmed via `git diff --stat`.

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: tests/fixtures/admonition_render_gate/index.rst
- FOUND: tests/test_admonition_bucket_render_gate.py
- FOUND: tests/test_pdf_render_gate.py
- FOUND: .planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-01.md
- FOUND commit: 14c4330 (Task 1)
- FOUND commit: 61c0ad9 (Task 2)
- FOUND commit: 301d62c (Task 3)
