---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 11
subsystem: translator
tags: [sphinx, typst, gentle-clues, admonitions, gate-01, translator, gap-closure]

# Dependency graph
requires:
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 09)
    provides: "39-09's GATE-01 RED for gap G-39-1: 7 red assertions across tests/test_admonition_bucket_render_gate.py (3) and tests/test_admonition_locale_title_precedence_gate.py (4), recorded verbatim in 39-GATE-EVIDENCE-05.md"
provides:
  - "D-03-R landed: visit_danger now passes the gentle-clues 'danger' id, visit_attention now passes the 'memo' id; visit_error is unchanged. The red family is three pairwise-distinct clue functions instead of one collapsed error(...) call."
  - "Two renamed + hand-re-derived tests in tests/test_admonitions.py (test_danger_converts_to_danger_function, test_attention_converts_to_memo_function)"
  - "A strengthened, corrected test_admonitionbuckettitlegate in tests/test_pdf_render_gate.py with a new negative assertion against gentle-clues' own English 'memo' default title ('Memorize')"
affects: [39-12, 39-13]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A bucket is still expressed purely as a gentle-clues function name passed to the shared _visit_admonition helper -- never a colour literal (D-01 stands unreversed by D-03-R)"
    - "A red-family sub-division: three Sphinx types (danger/attention/error) each carry their own gentle-clues function, rather than collapsing onto one, while every other bucket (note/success/warning) is untouched"

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - tests/test_admonitions.py
    - tests/test_pdf_render_gate.py

key-decisions:
  - "Both docstrings (visit_danger, visit_attention) name D-03-R and gap G-39-1 explicitly rather than the superseded D-03, and avoid spelling the helper-call form verbatim in prose (the plan's own acceptance criteria count occurrences of that exact call form)."
  - "The new compiled-PDF negative assertion targets only the memo/attention leak, not danger: measured directly from gentle-clues' lang.toml that the package's own English AND Japanese default titles for the danger id ('Danger'/'危険') are byte-identical to the Sphinx catalog's own values for the same locale, so no discriminating negative assertion is possible for danger. This asymmetry is documented in the test docstring and inline comment, not left for a reader to wonder about."
  - "Verified the new negative assertion is not vacuously green by a temporary scratch edit to _depart_admonition (`if title_expr and False:`), re-running the gate, observing the extracted PDF text change from 'Attention' to 'Memorize' under the '2.10 Attention Type' heading, then reverting via a second Edit (confirmed zero diff against the Task 1 commit afterward)."

requirements-completed: [ADM-02]

coverage:
  - id: D1
    description: "visit_danger passes the gentle-clues 'danger' id and visit_attention passes the 'memo' id; visit_error is unchanged, leaving exactly one call site passing the error id"
    requirement: "ADM-02"
    verification:
      - kind: unit
        ref: "grep -c '_visit_admonition(node, \"danger\")' typsphinx/translator.py == 1; grep -c '_visit_admonition(node, \"memo\")' typsphinx/translator.py == 1; grep -c '_visit_admonition(node, \"error\")' typsphinx/translator.py == 1; grep -c '_visit_admonition(node, \"clue\")' typsphinx/translator.py == 0"
        status: pass
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py::test_danger_routes_to_danger_function, ::test_attention_routes_to_memo_function, ::test_red_family_types_route_to_distinct_clue_functions -- all PASS (flipped RED->GREEN)"
        status: pass
      - kind: unit
        ref: "tests/test_admonition_locale_title_precedence_gate.py::test_danger_box_opens_with_danger_en, ::test_attention_box_opens_with_memo_en, ::test_danger_box_opens_with_danger_ja, ::test_attention_box_opens_with_memo_ja -- all PASS (flipped RED->GREEN)"
        status: pass
    human_judgment: false
  - id: D2
    description: "No accent-colour argument introduced anywhere; D-01 stands unreversed by D-03-R"
    requirement: "ADM-02"
    verification:
      - kind: unit
        ref: "git diff -- typsphinx/translator.py shows only the id string literal changed at each call site plus docstring prose; no new keyword argument added"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two in-process assertions in tests/test_admonitions.py migrated by hand-derivation (not copied from failing output) and renamed"
    requirement: "ADM-02"
    verification:
      - kind: unit
        ref: "tests/test_admonitions.py::test_danger_converts_to_danger_function, ::test_attention_converts_to_memo_function -- both PASS; grep -c 'test_danger_converts_to_error|test_attention_converts_to_error' tests/test_admonitions.py == 0; git diff -U0 tests/test_admonitions.py | grep -c '^[-+].*def test_' == 4"
        status: pass
    human_judgment: false
  - id: D4
    description: "test_admonitionbuckettitlegate strengthened with a negative assertion proven effective against a lost title argument"
    requirement: "ADM-02"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate -- PASS; effectiveness proven by temporary scratch drop of the title argument in _depart_admonition, observed 'Memorize' leaking into extracted PDF text under the Attention Type heading, then reverted"
        status: pass
    human_judgment: false
  - id: D5
    description: "Rubric and desc_* zones of translator.py byte-unchanged; full fast suite green with exactly the 7 recorded RED tests flipped and nothing else changing state"
    requirement: "ADM-05"
    verification:
      - kind: unit
        ref: "git diff -U0 -- typsphinx/translator.py | grep -c 'rubric|desc_signature|visit_strong' == 0"
        status: pass
      - kind: unit
        ref: "uv run pytest -m 'not slow' -q: 746 passed, 0 failed (baseline was 739 passed, 7 failed -- exactly the 7 RED tests flipped); uv run pytest -q (full suite incl. slow): 774 passed, 1 skipped, 0 failed"
        status: pass
    human_judgment: false

# Metrics
duration: 15min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 11: Red-Family Sub-Division (G-39-1 GREEN) Summary

**Split the collapsed red admonition bucket back into three distinct gentle-clues functions (danger/memo/error) per D-03-R, flipping all 7 RED tests plan 39-09 recorded, and strengthened the compiled-PDF gate against a lost title argument.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-08-02T14:39:00+09:00 (approx.)
- **Completed:** 2026-08-02T14:49:09+09:00
- **Tasks:** 2
- **Files modified:** 3 (`typsphinx/translator.py`, `tests/test_admonitions.py`, `tests/test_pdf_render_gate.py`)

## Accomplishments
- Re-routed exactly two call sites in `typsphinx/translator.py`: `visit_danger` now passes gentle-clues' own `danger` id (was `error`), and `visit_attention` now passes the `memo` id (was `error`). `visit_error` is untouched, leaving exactly one call site passing the `error` id (down from three). No accent-colour argument was introduced anywhere -- D-01 stands unreversed by D-03-R. Both docstrings were rewritten to name D-03-R and gap G-39-1, replacing the now-false D-03 fold rationale, without spelling the helper-call form verbatim in prose (the plan's acceptance criteria count occurrences of that exact form). Checked `visit_error`'s docstring and the `_custom_admonition_title` inline comment (lines 296-315) for statements the change falsifies -- both remain accurate as written and needed no edit, recorded here positively per the plan's instruction.
- Migrated and renamed the two falsified assertions in `tests/test_admonitions.py`: `test_danger_converts_to_error` -> `test_danger_converts_to_danger_function` (now asserts `"danger({"` present / `"danger["` absent), `test_attention_converts_to_error` -> `test_attention_converts_to_memo_function` (now asserts `"memo({"` present / `"memo["` absent). Both expected strings were hand-derived from 39-CONTEXT.md's D-03-R table and `_visit_admonition`'s box-open shape read directly from the helper -- never copied from a failing test's output. Confirmed the error test (`test_error_converts_to_error`) needs no edit even though it asserts the same `"error({"` string danger and attention used to assert -- checked and recorded, not inferred from the diff. Every other assertion in the file is byte-unchanged.
- Rewrote `test_admonitionbuckettitlegate`'s docstring in `tests/test_pdf_render_gate.py` to describe the corrected D-03-R routing and state which of its assertions are bucket-independent (the three body sentinels and the three catalog-title assertions), replacing a docstring that narrated a pre-phase RED already flipped by plan 39-05. Added one new negative assertion: gentle-clues' own English default title for the `memo` id ("Memorize", transcribed from `lang.toml`'s `[lang.en]` table) must never appear in the compiled PDF -- the highest-risk regression this gap introduces, since a dropped `title` argument would silently rename the attention box while every routing assertion still passed. No equivalent guard exists for danger: measured directly that gentle-clues' own English AND Japanese default titles for the `danger` id ("Danger"/"危険") are byte-identical to the Sphinx catalog's own values for that type in both locales, so a text search cannot distinguish a correct box from a title-dropped one there -- documented in a comment rather than left for a reader to wonder about. `TestTopicLineBlockRenderGate` (a different class) was not touched.
- Verified the new negative assertion is real, not vacuously passing: temporarily changed `_depart_admonition`'s title-emission guard to `if title_expr and False:`, re-ran `test_admonitionbuckettitlegate`, and observed the extracted PDF text change from `"2.10 Attention Type\nAttention\n..."` to `"2.10 Attention Type\nMemorize\n..."` -- proof the title argument's presence is exactly what the new assertion depends on. Reverted the scratch edit with a second `Edit` call and confirmed `git diff --stat` against the Task 1 commit was empty afterward (no residual scratch state).

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-route the two red-family call sites** - `0430d47` (feat)
2. **Task 2: Migrate the two falsified in-process assertions and strengthen the compiled-PDF gate** - `bf91cbe` (test)

_No TDD-style multi-commit tasks (each task's own RED was plan 39-09's pre-recorded GATE-01, not authored fresh here)._

## Files Created/Modified
- `typsphinx/translator.py` - Exactly two call sites changed (`visit_danger`, `visit_attention`) plus their docstrings; `visit_error`, `_visit_admonition`, `_depart_admonition`, and every rubric/desc_signature/visit_strong handler confirmed byte-unchanged.
- `tests/test_admonitions.py` - Two tests renamed + re-derived (danger, attention); 16 other tests byte-unchanged.
- `tests/test_pdf_render_gate.py` - `test_admonitionbuckettitlegate`'s docstring rewritten and one new negative assertion added; every other test in the file, including `TestTopicLineBlockRenderGate`, byte-unchanged.

## Decisions Made
- Named D-03-R and G-39-1 explicitly in both rewritten docstrings rather than referencing D-03 as if it still held, per the plan's transparency prohibition (a stale routing claim is the same defect class as a stale test name).
- Scoped the new PDF negative assertion to attention/memo only, with an explicit comment recording why danger has no equivalent guard (measured string identity between the Sphinx catalog and gentle-clues' own package default, in both English and Japanese) -- rather than silently omitting a matching check for danger and leaving a reader to wonder.
- Proved the new negative assertion's effectiveness via a temporary, explicitly-reverted scratch edit rather than reasoning about it abstractly, per the plan's acceptance criteria.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' acceptance criteria and verify commands pass as specified; no Rule 1-4 auto-fixes were needed.

## Issues Encountered
- Sandbox tool restrictions rejected compound `env -u ... uv sync` and `for`-loop shim commands as "too complex to verify containment"; worked around by running `unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev` and issuing the `uv`/`ruff` shim symlinks as separate single commands instead of a loop. No effect on the resulting worktree environment -- confirmed both shims resolve to the correct Nix-store `uv` and the main checkout's patchelf'd `ruff` before running any test.
- None otherwise.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- G-39-1's product change is fully landed and proven: all 7 RED tests plan 39-09 recorded are green (`tests/test_admonition_bucket_render_gate.py` 12/12, `tests/test_admonition_locale_title_precedence_gate.py` 9/9), and nothing else changed state -- full fast suite went from `739 passed, 7 failed` to `746 passed, 0 failed`; full suite (incl. slow) is `774 passed, 1 skipped, 0 failed`, reconciling exactly against the green-plan note's target.
- `black --check .`, `ruff check .`, and `mypy typsphinx/` all pass repo-wide. `tests/test_preview_version_sync.py` is green -- no `@preview` pin moved.
- `git diff --stat -- pyproject.toml typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ` is empty, confirming no import-site or dependency change was needed (both `danger` and `memo` were already in scope through the existing wildcard `@preview/gentle-clues` import).
- Plan 39-12 (ADM-04 artifact re-render, out of this plan's scope) and plan 39-13 (slow corpus gate, also out of scope) can now proceed against this landed routing change.

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: typsphinx/translator.py
- FOUND: tests/test_admonitions.py
- FOUND: tests/test_pdf_render_gate.py
- FOUND: .planning/phases/39-admonition-taxonomy-rubric-nesting/39-11-SUMMARY.md
- FOUND commit: 0430d47 (Task 1)
- FOUND commit: bf91cbe (Task 2)
- FOUND commit: 1707119 (SUMMARY)
