---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 05
subsystem: translator
tags: [sphinx, typst, gentle-clues, admonitions, i18n, gate-01, translator]

# Dependency graph
requires:
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 01)
    provides: "39-01's GATE-01 RED: tests/test_admonition_bucket_render_gate.py (6 structurally-RED assertions) and tests/test_pdf_render_gate.py's TestAdmonitionPdfRenderGate compiled-PDF half, hand-derived from 39-CONTEXT.md's locked bucket table and sphinx.locale.admonitionlabels"
provides:
  - "Five re-routed gentle-clues call sites: seealso->tip (D-02), danger->error and attention->error (D-03), generic .. admonition::->notify (D-09), non-contents .. topic::->abstract (D-10)"
  - "A single sphinx.locale.admonitionlabels catalog lookup inside _visit_admonition (by node.__class__.__name__), giving all ten real admonition types their static title; todo_node/generic-admonition/topic correctly unaffected since their class names are not catalog keys"
  - "_depart_admonition's static-title branch now escapes through escape_typst_string (T-39-01) before interpolation"
  - "Four renamed + re-derived test functions and one new precedence test in tests/test_admonitions.py; two re-derived assertions in tests/test_topics.py"
affects: [39-06-rubric-nesting, 39-08-test-migration-census]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A bucket is expressed purely as a gentle-clues function name passed to the shared _visit_admonition helper -- never a colour literal (D-01)"
    - "A single catalog lookup (node.__class__.__name__ against sphinx.locale.admonitionlabels) inside the shared helper, rather than ten per-call-site custom_title edits, exploiting the verified byte-identical key<->class-name correspondence"
    - "Dynamic (node-derived) title always checked before the static/catalog title in _depart_admonition -- precedence locked by a dedicated regression test"

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - tests/test_admonitions.py
    - tests/test_topics.py

key-decisions:
  - "Implemented the admonitionlabels lookup as ONE edit inside _visit_admonition (module-level import + lookup-by-class-name), not ten call-site edits -- 39-CONTEXT.md's Claude's Discretion section left this open and the catalog-key/class-name equivalence was re-verified live before relying on it (uv run python -c catalog-key-set check, exit 0)."
  - "Verified the new precedence test (test_note_with_own_title_wins_over_catalog) actually catches a reordering regression: temporarily swapped _depart_admonition's if/elif order in place, re-ran the test, observed it fail (catalog value \"Note\" leaked through in place of the directive-supplied \"Custom Note Title\"), then reverted with `git checkout -- typsphinx/translator.py` and re-confirmed green."
  - "Did not rename tests/test_topics.py's two moved-assertion test functions (test_topic_converts_to_clue_box, test_topic_title_with_multiple_children_does_not_concatenate) -- the plan's action text explicitly scoped the 'exactly four renames' requirement to tests/test_admonitions.py only; updated their docstrings/class docstring instead to describe the D-10 abstract routing so no stale claim survives."

patterns-established:
  - "Round-trip verification for string-literal escaping: call the private helper methods directly (_visit_admonition/_depart_admonition) with a synthetic node class name absent from the catalog, feed a title containing a quote and a backslash, then wrap the emitted body in a minimal Typst document and run it through typst.compile() to prove it's not just escaped correctly but genuinely compilable."

requirements-completed: [ADM-01, ADM-02, ADM-03]

coverage:
  - id: D1
    description: "seealso re-routed to the success bucket (tip), joining hint/tip; danger and attention re-routed to the single error-bucket function (error), folding what were three separate functions pre-phase into one"
    requirement: "ADM-01"
    verification:
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py::test_seealso_routes_to_tip_bucket, ::test_attention_routes_to_error_bucket, ::test_danger_routes_to_error_bucket -- all PASS (flipped RED->GREEN)"
        status: pass
      - kind: unit
        ref: "tests/test_admonitions.py::test_seealso_converts_to_tip_with_title, ::test_danger_converts_to_error, ::test_attention_converts_to_error -- all PASS"
        status: pass
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate -- PASS (compiled-PDF half)"
        status: pass
    human_judgment: false
  - id: D2
    description: "attention and danger both fold into the same error function as error itself -- the red bucket is now a single function, and the previously distinct danger function no longer appears as a value passed by any call site"
    requirement: "ADM-02"
    verification:
      - kind: unit
        ref: "grep -vE '^\\s*#' typsphinx/translator.py | grep -cE '_visit_admonition\\([^)]*\"danger\"' returns 0 (danger never passed as clue_type after this plan); tests/test_admonition_bucket_render_gate.py::test_control_buckets_never_move stays PASS (the seven non-moving types confirmed unchanged)"
        status: pass
    human_judgment: false
  - id: D3
    description: "the generic .. admonition:: emits notify() and the non-contents .. topic:: emits abstract(); the base gentle-clues clue function no longer appears as a value passed by any call site"
    requirement: "ADM-03"
    verification:
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py::test_generic_admonition_routes_to_notify, ::test_topic_routes_to_abstract, ::test_no_real_admonition_type_ever_uses_base_clue -- all PASS"
        status: pass
      - kind: unit
        ref: "grep -vE '^\\s*#' typsphinx/translator.py | grep -cE '_visit_admonition\\([^)]*\"clue\"' returns 0"
        status: pass
      - kind: unit
        ref: "tests/test_admonitions.py::test_generic_admonition_converts_to_notify, tests/test_topics.py::TestTopicConversion (both clue-box tests, now abstract) -- all PASS"
        status: pass
    human_judgment: false
  - id: D4
    description: "all ten real admonition types take their static title from sphinx.locale.admonitionlabels via one lookup in _visit_admonition; the dynamic (directive-supplied) title still wins, and the static title is escaped through escape_typst_string before interpolation"
    requirement: "ADM-03"
    verification:
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py::test_admonition_titles_match_locale_catalog -- PASS (flipped RED->GREEN for 8 of 10 rows, casing fix for seealso)"
        status: pass
      - kind: unit
        ref: "tests/test_admonitions.py::test_note_with_own_title_wins_over_catalog -- PASS; regression-catching property verified by a temporary in-place reorder of _depart_admonition's precedence check (observed FAIL), then reverted via git checkout"
        status: pass
      - kind: other
        ref: "One-off round trip via _visit_admonition/_depart_admonition with a title containing a double quote and backslash, wrapped in a minimal document and compiled with typst.compile() -- 8798 bytes of PDF, no exception. Emitted: info({par({text(\"Body text.\")})\\n\\n}, title: \"A \\\"quoted\\\" title with a \\\\backslash\")"
        status: pass
    human_judgment: false

# Metrics
duration: 30min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 05: Admonition Taxonomy Translator Fix Summary

**Re-routed five gentle-clues call sites (seealso->tip, danger/attention->error, generic admonition->notify, topic->abstract) and centralized all ten real admonition titles on a single `sphinx.locale.admonitionlabels` catalog lookup inside `_visit_admonition`, escaped through the project's one string-escaping helper, flipping plan 39-01's six-test GATE-01 RED to GREEN.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-08-02T02:00:00Z (approx.)
- **Completed:** 2026-08-02T02:26:28Z
- **Tasks:** 3
- **Files modified:** 3 (`typsphinx/translator.py`, `tests/test_admonitions.py`, `tests/test_topics.py`)

## Accomplishments
- Re-routed the five call sites whose bucket moves per 39-CONTEXT.md's locked table: `visit_seealso` (info->tip, D-02), `visit_danger` and `visit_attention` (both ->error, D-03), `visit_admonition` (clue->notify, D-09), `visit_topic`'s non-contents branch (clue->abstract, D-10). Rewrote every docstring the change falsified (seealso, danger, attention, admonition, topic, hint) to name the governing decision instead of a stale mapping rationale.
- Added a module-level `from sphinx.locale import admonitionlabels` import and a single lookup inside `_visit_admonition`, keyed on `node.__class__.__name__` — verified live that every one of the ten real Sphinx admonition class names is a byte-identical catalog key before relying on it. `todo_node`, the generic admonition, and topic are correctly unaffected (their class names are not catalog keys), so their existing title paths (inert fallback / directive-supplied dynamic title) are untouched. Removed the now-dead `custom_title="Important"` (the catalog supplies it byte-identically); `visit_seealso`'s `custom_title="See Also"` had already been removed in the same commit as its bucket move.
- Routed `_depart_admonition`'s static-title branch through the project's single `escape_typst_string` helper (T-39-01), coercing the (now possibly non-ASCII, lazy-i18n-proxy-derived) title to `str` first. Verified with a one-off round trip through `_visit_admonition`/`_depart_admonition` with a title containing a double quote and a backslash, wrapped in a minimal Typst document and compiled with `typst.compile()` — 8798 bytes of PDF produced, no exception.
- Migrated exactly four falsified test functions in `tests/test_admonitions.py` (renamed + re-derived: seealso, danger, attention, generic admonition) with their companion negative "not in output" assertions updated to the new function names; left the other 13 original assertions byte-unchanged. Added one new test locking the directive-title-wins-over-catalog precedence property (T-39-12), and verified it actually catches a regression by temporarily reordering the precedence check in place, observing the test fail, then reverting.
- Migrated the two falsified assertions in `tests/test_topics.py` (clue->abstract) without renaming their functions (the plan's "exactly four renames" scope is `test_admonitions.py`-only); updated stale docstrings instead. Left the box-less `.. contents::` assertion byte-unchanged apart from an added review comment recording it was deliberately left alone.

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-route the five call sites whose bucket moves** - `a6c04ea` (feat)
2. **Task 2: Source the static admonition title from the Sphinx locale catalog and escape it** - `ecf5ab7` (feat)
3. **Task 3: Migrate the falsified in-process assertions and rename the four misleading tests** - `5b9a8cb` (test)

_No TDD-style multi-commit tasks (each task's own RED was plan 39-01's pre-recorded GATE-01, not authored fresh here)._

## Files Created/Modified
- `typsphinx/translator.py` - Admonition zone only (lines ~10, ~302-313, ~4364-4593): admonitionlabels import, five re-routed call sites with corrected docstrings, catalog lookup in `_visit_admonition`, escaping in `_depart_admonition`, updated `_custom_admonition_title` comment. `visit_rubric`, `depart_rubric`, `visit_strong`, `depart_strong`, `visit_desc_signature`, `depart_desc_signature` confirmed byte-unchanged via `git diff 8a37226 --`.
- `tests/test_admonitions.py` - 4 renamed+re-derived tests (seealso/danger/attention/generic-admonition), 1 new precedence test, 13 tests byte-unchanged.
- `tests/test_topics.py` - 2 assertions moved to `abstract({`, 1 assertion byte-unchanged plus an added review comment.

## Decisions Made
- Implemented the `admonitionlabels` lookup as one edit inside `_visit_admonition` (not ten call-site edits) — exploits the verified byte-identical catalog-key/docutils-class-name correspondence; this was explicitly left to Claude's discretion in 39-CONTEXT.md.
- Verified the new precedence test is not vacuously green by temporarily reordering `_depart_admonition`'s if/elif branches in place, confirming the test fails (catalog value `"Note"` leaks through instead of the directive-supplied `"Custom Note Title"`), then reverting with `git checkout -- typsphinx/translator.py`.
- Left `tests/test_topics.py`'s two moved-assertion test function names unrenamed, since the plan's acceptance criteria scope "exactly four renames" to `tests/test_admonitions.py` only; updated their docstrings instead so no stale mapping claim survives (D-14's spirit, without violating the plan's explicit rename count).

## Deviations from Plan

None - plan executed exactly as written. All three tasks' acceptance criteria and verify commands pass as specified; no Rule 1-4 auto-fixes were needed.

## Issues Encountered
- The full `uv run pytest -m "not slow"` run surfaces 4 pre-existing failures in `tests/test_desc_rubric_decoupling_render_gate.py` and `tests/test_rubric_strong_nesting_render_gate.py` — confirmed via `git diff 8a37226 --` that both files are byte-identical to the phase-start commit, and via `git diff 8a37226 -- typsphinx/translator.py` that no rubric/strong/desc_signature handler was touched by this plan. These are the pre-recorded D-13 rubric-decoupling RED fixture that plan 39-06 (not this plan) owns and fixes; out of this plan's scope per its own objective ("This plan does NOT touch `visit_rubric`, `depart_rubric`, `visit_strong` or `visit_desc_signature`").
- `.venv/bin/ruff` and a freshly-`uv sync`'d `.venv/bin/uv` are generic-linux ELF binaries that fail to start under this NixOS sandbox — resolved per the project's standing memory note by symlinking the main checkout's patchelf'd `ruff` and the Nix-store `uv` into the worktree's `.venv/bin/`. No code impact; environment-only.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- ADM-01, ADM-02, and ADM-03 are fully discharged: all six of plan 39-01's GATE-01 assertions (`tests/test_admonition_bucket_render_gate.py`) are GREEN, plus the compiled-PDF half in `tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate` and the pre-existing `TestAdmonitionTitleRegression` multi-child assertion.
- `tests/test_admonitions.py` and `tests/test_topics.py` are both fully green (23 tests combined), `black --check .`, `ruff check .`, and `mypy typsphinx/` all pass repo-wide.
- `git diff -- typsphinx/translator.py` (against phase start) touches only the admonition zone, the import block, and the `_custom_admonition_title` comment, exactly as this plan's `<verification>` requires.
- Plan 39-06 (rubric nesting) can proceed independently — its own pre-recorded RED (`test_desc_rubric_decoupling_render_gate.py`, `test_rubric_strong_nesting_render_gate.py`) is untouched and unaffected by this plan's changes.
- Plan 39-08's test-migration census can check its counts against this plan's recorded tallies: `tests/test_admonitions.py` (4 renamed, 1 added, 13 untouched of 17 original) and `tests/test_topics.py` (2 moved, 1 untouched, 0 renamed).

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*
