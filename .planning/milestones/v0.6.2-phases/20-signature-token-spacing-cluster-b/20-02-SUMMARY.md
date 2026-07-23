---
phase: 20-signature-token-spacing-cluster-b
plan: 02
subsystem: rendering
tags: [sphinx, typst, translator, field_list, confval, pypdf]

# Dependency graph
requires:
  - phase: 20-signature-token-spacing-cluster-b
    plan: "01"
    provides: the proven pass/pass sibling-shape idiom and the standing GATE-01 real-compile fixture pattern this plan reuses for the field-list colon-space fix
provides:
  - "depart_field_name emits the colon-space form (text(\": \")) instead of the no-space colon"
  - "depart_field emits a sibling-guarded inter-field two-space separator (text(\"  \")) with leading+trailing newlines"
  - "tests/test_confval_field_spacing_render_gate.py — new real-compile GATE-01 render-gate for FID-09"
  - "tests/fixtures/confval_field_spacing_render_gate/{conf.py,index.rst} — offline fixture project (audit's literal the_answer no-blank-line confval repro)"
affects: [21-residual-fidelity-fixes-clusters-c-d-e-f]

# Tech tracking
tech-stack:
  added: []
  patterns: ["sibling-boundary am-I-last idiom applied to depart_field: node.next_node(descend=False, siblings=True) mirrors depart_desc_parameter's comma-separation guard, generalized to a field-list inter-field boundary"]

key-files:
  created:
    - tests/test_confval_field_spacing_render_gate.py
    - tests/fixtures/confval_field_spacing_render_gate/conf.py
    - tests/fixtures/confval_field_spacing_render_gate/index.rst
  modified:
    - typsphinx/translator.py
    - tests/test_field_list_in_list_item_render_gate.py

key-decisions:
  - "Kept the colon-space edit's space INSIDE the strong(...) + text(...) content expression, not around it -- field_name has exactly one call site, so no concat-context awareness was needed (unlike desc_sig_space's four-call-site fix in plan 20-01)."
  - "Verified both leading AND trailing newlines are required around the inter-field text(\"  \") statement via a real, temporary revert-and-rebuild this session -- a leading-only newline reproduces a genuine Typst 'expected semicolon or line break' fatal (Pitfall 4)."
  - "Used the audit catalogue's own literal the_answer no-blank-line repro for the new fixture -- confirmed empirically to match 100% of the real 219-confval Sphinx v9.1.0 corpus form, per 20-RESEARCH.md."

patterns-established:
  - "Field-list inter-sibling separators reuse the desc_parameter am-I-last-sibling idiom (node.next_node(descend=False, siblings=True)), generalizing it beyond comma-joined parameter lists to any sibling-boundary content emission that must wrap BOTH a leading and trailing newline to avoid statement juxtaposition."

requirements-completed: [FID-09]

coverage:
  - id: D1
    description: "field_list :type:/:default: fields render 'Type: int (a number)  Default: 42' -- colon-space plus double-space inter-field boundary, matching ROADMAP SC#3 byte-for-byte (FID-09)"
    requirement: "FID-09"
    verification:
      - kind: integration
        ref: "tests/test_confval_field_spacing_render_gate.py::TestConfvalFieldSpacingRenderGate::test_typstpdf_confval_field_spacing_produces_pdf"
        status: pass
      - kind: integration
        ref: "tests/test_confval_field_spacing_render_gate.py::TestConfvalFieldSpacingRenderGate::test_pdf_extracted_text_matches_pinned_sc3_string"
        status: pass
    human_judgment: false

# Metrics
duration: 15min
completed: 2026-07-20
status: complete
---

# Phase 20 Plan 02: Field-List Colon-Space + Inter-Field Boundary (FID-09) Summary

**Two small, independent `translator.py` edits — `depart_field_name` now emits a colon-space (`text(": ")`) and `depart_field` now emits a sibling-guarded inter-field two-space separator (`text("  ")`, mirroring `depart_desc_parameter`'s "am I last sibling" idiom) — restore lost `:type:`/`:default:` field spacing, proven byte-for-byte against the ROADMAP SC#3 pinned string `"Type: int (a number)  Default: 42"` via a new real-compile GATE-01 fixture with pypdf extracted-text adjacency assert.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-07-20T11:27:19Z (per STATE.md session marker)
- **Completed:** 2026-07-20T11:34:17Z
- **Tasks:** 2 completed
- **Files modified:** 5 (2 modified, 3 created)

## Accomplishments

- Changed `depart_field_name`'s appended literal from `' + text(":"))\n'` to `' + text(": "))\n'` — a real content-value space inside the `+`-joined `strong(...)` expression, restoring the "Type: int" colon-space.
- Changed `depart_field` from a no-op `pass` to a sibling-guarded emit of `'\ntext("  ")\n'` when `node.next_node(descend=False, siblings=True)` is truthy — an inter-field double-space separator with BOTH leading and trailing newlines, verified this session via a real, temporary translator revert + rebuild that a leading-only newline reproduces the genuine Typst "expected semicolon or line break" fatal (Pitfall 4).
- Updated the ONE pre-existing locked assertion in `tests/test_field_list_in_list_item_render_gate.py` (line ~165) from the no-space colon form to the colon-space form, with a revised comment clarifying the colon-space change is a deliberate, codebase-wide edit (D-01) separate from the list-item-separator behavior that test actually verifies.
- Confirmed via exhaustive grep (`grep -n 'text(":")' tests/*.py`) that no test anywhere still locks the old no-space colon form.
- Added `tests/test_confval_field_spacing_render_gate.py` (two tests: structural `.typ` colon-space + inter-field boundary asserts + real `-b typstpdf` compile + `%PDF` magic bytes; and the required pypdf extracted-text exact-string assert for the pinned SC#3 string) with its own offline fixture project using the audit catalogue's literal `the_answer` no-blank-line confval repro.
- Verified both directions this session: temporarily reverted `translator.py` to its pre-Task-1 commit, rebuilt, and confirmed the new fixture's structural assert FAILS with the pre-fix no-space-colon/no-separator output (`strong(text("Type") + text(":"))`, no `text("  ")` anywhere); restored the committed fixed file and confirmed `git diff --stat` clean, then re-ran the fixture to confirm it passes post-fix.
- Confirmed no regression: full fast suite (`pytest tests/ -m "not slow" -q`) went from 485 to 487 passed (the 2 new tests), 0 failures.

## Task Commits

Each task was committed atomically:

1. **Task 1: Colon-space + inter-field boundary edits, and update the one pre-existing locked assertion (FID-09)** - `68ca123` (fix)
2. **Task 2: New GATE-01 render-gate fixture proving FID-09** - `5691d61` (test)

**Plan metadata:** (this commit)

## Files Created/Modified

- `typsphinx/translator.py` - `depart_field_name` emits colon-space; `depart_field` emits sibling-guarded inter-field two-space separator
- `tests/test_field_list_in_list_item_render_gate.py` - the one pre-existing locked colon assertion (line ~165) updated to the colon-space form
- `tests/test_confval_field_spacing_render_gate.py` - new GATE-01 render-gate (structural + real compile + pypdf adjacency)
- `tests/fixtures/confval_field_spacing_render_gate/conf.py` - fixture Sphinx config (mirrors the confval field-body gate fixture shape)
- `tests/fixtures/confval_field_spacing_render_gate/index.rst` - fixture source: the audit's literal `the_answer` no-blank-line `:type:`/`:default:` repro

## Decisions Made

- Kept the colon-space fix's added space INSIDE the `text(": ")` content value rather than adding a separate `+ text(" ")` term — `field_name` has exactly one call site, so no concat-context awareness (unlike `desc_sig_space`) was needed.
- Reused and generalized `depart_desc_parameter`'s `node.next_node(descend=False, siblings=True)` "am I the last sibling" idiom for the field-list inter-field boundary, rather than introducing a new sibling-detection helper.
- Used the audit catalogue's own literal `the_answer` no-blank-line confval repro for the new fixture (not a synthetic one) — this is both the audit's own minimal reproduction AND empirically the form used by 100% of the real 219-confval Sphinx v9.1.0 corpus (per 20-RESEARCH.md), giving the fixture direct traceability to the corpus finding it closes.

## Deviations from Plan

None - plan executed exactly as written. Both tasks matched their described edits precisely; the plan's own acceptance criteria (exhaustive `grep` check, structural `.typ` asserts, pypdf exact-string assert, real pre-fix-fails/post-fix-passes verification) were all satisfied without needing any Rule 1-4 deviation.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- FID-09 is proven, completing Phase 20's full scope (FID-07, FID-08, FID-09 — signature token spacing, cluster B).
- No blockers. The `@preview` version-sync surface (`writer.py`/`template_engine.py`/`templates/base.typ`) and `pyproject.toml` remain untouched (confirmed via `git diff --name-only`), preserving the milestone invariant.
- Phase 21 (Residual Fidelity Fixes, Clusters C/D/E/F) is next in the roadmap.

---
*Phase: 20-signature-token-spacing-cluster-b*
*Completed: 2026-07-20*

## Self-Check: PASSED

All created files verified present on disk; both task commits (`68ca123`, `5691d61`) verified present in git history.
