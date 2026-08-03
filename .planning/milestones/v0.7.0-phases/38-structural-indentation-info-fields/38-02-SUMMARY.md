---
phase: 38-structural-indentation-info-fields
plan: 02
subsystem: testing
tags: [sphinx, typst, docutils, field-lists, pytest, render-gate]

requires:
  - phase: 37-signature-typography-the-desc-family
    provides: SHARED_INDENT_STEP (D-08 constant hand-off) and the render-gate/hand-derivation pattern (test_signature_typography_gate.py's _slice/_expected_* family) this plan mirrors
provides:
  - "tests/fixtures/field_body_typography_render_gate/ -- a fixture Sphinx project exercising every FLD-02/FLD-03 field-body shape in one -b typst build"
  - "tests/test_field_body_typography_render_gate.py -- the per-sub-part FLD-01/FLD-02/FLD-03 structural gate, hand-derived from 38-EMISSION-CONTRACT.md sections 4-5, RED against the untouched translator"
  - "38-GATE-EVIDENCE-02.md -- verbatim RED evidence, pre-phase FLD-03 sub-part bytes, pre-phase single-value PDF text, and the D-13 disposition record"
affects: [38-05, 38-06, 38-07, 38-08]

tech-stack:
  added: []
  patterns:
    - "Session-scoped -b typstpdf fixture build shared by both structural (.typ) and compiled-PDF-text assertions in one gate module"
    - "Per-construct region slicing via section headings (_section/_slice), mirroring test_signature_typography_gate.py"
    - "Hand-derivation helpers built on escape_typst_string ALONE (no dot-splitting, no ZWSP injection) to avoid the SIG-07 escape-helper trap"

key-files:
  created:
    - tests/fixtures/field_body_typography_render_gate/conf.py
    - tests/fixtures/field_body_typography_render_gate/index.rst
    - tests/test_field_body_typography_render_gate.py
    - .planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE-02.md
  modified: []

key-decisions:
  - "FLD-03's hand-derivation helpers (_expected_bold_mono/_expected_italic_mono) compose escape_typst_string alone -- never Phase 37's _emit_signature_leaf_wrapper -- so the gate cannot pass if the wrong escape helper is reused"
  - "The FLD-02 consecutive-fields trap and the no-ZWSP assertion were found GREEN pre-phase; kept as non-regression controls (not converted to defect cases) since both properties must SURVIVE the phase, not merely start true"
  - "D-13's stray parbreak() is left in place per 38-CONTEXT.md/38-EMISSION-CONTRACT.md; re-confirmed via a fresh grep in this plan's own evidence file rather than trusting the planning-time citation"

requirements-completed: [FLD-01, FLD-02, FLD-03]

coverage:
  - id: D1
    description: "Fixture project exercising multi-value bulleted, single-entry collapsed, single-value (returns/rtype/raises), resolvable-xref, typeless, non-ASCII, collapsed-inline, and single-field-list field-body shapes in one -b typst build"
    requirement: "FLD-01"
    verification:
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate -- fixture build (session fixture assertions), pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "FLD-03 per-sub-part gate (name/type/label, three separate checks) recording structural RED against the untouched translator"
    requirement: "FLD-03"
    verification:
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_name_bold_monospace -- RED (expected pre-phase)"
        status: fail
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_type_italic_monospace -- RED (expected pre-phase)"
        status: fail
    human_judgment: true
    rationale: "This plan's job is to record structural RED, not to make it pass -- a human/verifier must confirm the RED is intentional (gate-authoring plan) rather than a regression, per milestone invariant #4."
  - id: D3
    description: "FLD-02 inline-join, consecutive-fields trap, and bulleted-half non-regression control, plus FLD-01's field-body positional check"
    requirement: "FLD-02"
    verification:
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_bulleted_multi_value_non_regression_control -- pass (required GREEN)"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_single_value_returns_no_block_paragraph_wrapper -- RED (expected pre-phase)"
        status: fail
    human_judgment: true
    rationale: "Same as D2 -- RED is the intentional deliverable of this gate-authoring plan; a verifier must confirm the RED/GREEN split matches the plan's acceptance criteria rather than auto-classifying failures as bugs."

duration: 55min
completed: 2026-08-01
status: complete
---

# Phase 38 Plan 02: FLD-02/FLD-03 Structural Gate Summary

**One fixture Sphinx project plus a 20-test per-sub-part pytest gate recording 15 structural RED / 5 CONTROL-GREEN against the untouched translator for field-body typography (FLD-01/FLD-02/FLD-03), hand-derived from 38-EMISSION-CONTRACT.md sections 4-5.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-08-01T10:38:00Z (approx)
- **Completed:** 2026-08-01T11:33:26Z
- **Tasks:** 3
- **Files modified:** 4 (all new files; no existing file touched)

## Accomplishments

- Built `tests/fixtures/field_body_typography_render_gate/` — one Sphinx project exercising all nine field-body constructs FLD-02/FLD-03 are judged on (multi-value bulleted, single-entry collapsed, single-value returns/rtype/raises trio, resolvable-type cross-reference, typeless param, non-ASCII param, collapsed-inline confval control, and a single-field field list) in a single `-b typst`/`-b typstpdf` build.
- Wrote `tests/test_field_body_typography_render_gate.py` — 20 tests (parametrized to more node-ids) covering FLD-01's field-body positional check, FLD-02's inline join / consecutive-fields trap / bulleted-half non-regression, and FLD-03's per-sub-part name/type/label checks plus the typeless, non-ASCII, no-ZWSP, and cross-reference-composition edges. Every expected string is hand-derived via `escape_typst_string` alone or copied verbatim from `38-EMISSION-CONTRACT.md` — never pasted from running new translator code (none exists yet).
- Recorded `38-GATE-EVIDENCE-02.md` with the full verbatim pytest output, a per-node-id RED/CONTROL-GREEN table with one-sentence failure reasons, confirmation that zero REDs are compile failures, the pre-phase FLD-03 sub-part bytes, the pre-phase single-value PDF text (label and value on separate lines), and a freshly re-run D-13 disposition grep (stray `parbreak()` LEFT IN PLACE, ~7.15pt accepted cost).

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the field-body typography fixture** — `b6d9fb5` (test)
2. **Task 2: Write the FLD-02/FLD-03 gate module with per-sub-part hand-derived expectations** — `8647e25` (test)
3. **Task 3: Record the verbatim RED and the D-13 disposition evidence** — `645f0d2` (docs)

**Plan metadata:** _pending — this final commit_

## Files Created/Modified

- `tests/fixtures/field_body_typography_render_gate/conf.py` — minimal Sphinx config (project/author/release, `extensions = ["typsphinx"]`, `typst_documents`), header comment naming FLD-01/02/03 and D-05/06/07/13.
- `tests/fixtures/field_body_typography_render_gate/index.rst` — nine labelled constructs, each preceded by a `..` comment naming its requirement and defect-case-or-CONTROL role.
- `tests/test_field_body_typography_render_gate.py` — the gate module: `_expected_bold_mono`, `_expected_italic_mono`, `_slice`, `_section`, `_heading_marker`, a session-scoped `-b typstpdf` build fixture shared by `typ_text`/`pdf_text`, and 14 test functions (4 parametrized to 4 cases each for the two FLD-03 per-sub-part checks) = 20 collected node-ids.
- `.planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE-02.md` — the RED evidence file (Task 3's required output).

## Decisions Made

- **Hand-derivation, not delegation.** `_expected_bold_mono`/`_expected_italic_mono` are built on `escape_typst_string` alone (no dot-splitting, no ZWSP injection step), matching contract §5.3's warning that reusing Phase 37's `_emit_signature_leaf_wrapper` would smuggle an unauthorized zero-width space into field bodies.
- **Two pre-phase-GREEN properties kept as non-regression controls, not weakened into defect cases:** `test_fld02_consecutive_single_value_fields_stay_on_separate_lines` and `test_fld03_no_zero_width_space_anywhere_in_field_bodies` both already pass against the untouched translator (the first because label and value are ALREADY on separate lines pre-phase, which trivially satisfies "labels don't run together"; the second because no code path injects ZWSP into a field body today). Both are legitimate — they encode properties the phase must not regress, even though they happen to already hold. Documented explicitly in the evidence file per the plan's own instruction ("if any assertion is GREEN against the untouched translator, do not adjust it into red — record it and reclassify it").
- **D-13 re-confirmed, not merely cited.** Re-ran the grep `38-RESEARCH.md` Open Question 2 asked for against the current tree (rather than trusting the planning-time citation verbatim) and got the same result: `tests/test_inline_math_after_text_render_gate.py:291` pins the exact `list({\nparbreak()...` shape. The LEFT-IN-PLACE decision, both reasons, and the accepted ~7.15pt cost are recorded in `38-GATE-EVIDENCE-02.md` §6.
- **The resolvable-xref link's exact whitespace left untested.** `test_fld03_resolvable_type_composes_inside_link_unchanged_label` uses `\s*` between the link's opening token and the nested italic-monospace call, rather than pinning the exact newline pattern (`link(<label>, \n` observed pre-phase), because contract §5.4's post-phase prose example does not commit to a specific newline byte and `visit_literal_emphasis`'s post-phase separator mechanics are a different plan's implementation choice (D-12).

## Deviations from Plan

None — plan executed exactly as written. Two ruff/black-tooling notes worth recording as environment setup, not scope deviations:

- The worktree's `.venv/bin/ruff` installed by `uv sync --extra dev` is a generic-linux binary NixOS's stub-ld cannot exec ("Could not start dynamically linked executable"). Symlinked a NixOS-store-provided `ruff` binary (`/nix/store/.../ruff-0.15.14/bin/ruff`, dynamically linked against Nix's own glibc/ld-linux) into `.venv/bin/ruff`, matching the `CLAUDE.md`-documented `uv`/`ruff` shim pattern. This is local worktree-venv plumbing only; no repository file changed.

## Issues Encountered

None — every RED failure investigated was a plain `AssertionError` from a string/regex comparison, never a `TypstError`/`TypstCompilationError`. Confirmed by grepping the full pytest output for both signatures (zero matches) and by directly re-running `sphinx-build -b typstpdf` on the fixture (exit 0, valid `%PDF`-prefixed PDF produced).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The FLD-01/FLD-02/FLD-03 RED baseline this plan recorded is ready for the plan(s) that implement the translator fix (predicted: 38-07 per `38-EMISSION-CONTRACT.md` §7's blast-radius table) to turn RED, using this module's hand-derived expectations as the target — no expected string in this gate should be re-derived from the new code's own output.
- Both confval control modules (`test_confval_field_spacing_render_gate.py`, `test_confval_field_body_render_gate.py`) are confirmed green and byte-unmodified by this plan; any future plan touching `field_list`/`field_body` handlers must keep them green.
- The full suite (`-m "not slow"`) shows 664 passed / 15 failed (all 15 within this new module, all expected) / 29 deselected — no collateral damage elsewhere in the tree.
- `black --check .`, `ruff check .`, and `mypy typsphinx/` all pass across the whole repository.

---
*Phase: 38-structural-indentation-info-fields*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: `tests/fixtures/field_body_typography_render_gate/conf.py`
- FOUND: `tests/fixtures/field_body_typography_render_gate/index.rst`
- FOUND: `tests/test_field_body_typography_render_gate.py`
- FOUND: `.planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE-02.md`
- FOUND: `.planning/phases/38-structural-indentation-info-fields/38-02-SUMMARY.md`
- FOUND commit: `b6d9fb5` (Task 1)
- FOUND commit: `8647e25` (Task 2)
- FOUND commit: `645f0d2` (Task 3)
