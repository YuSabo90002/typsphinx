---
phase: 37-signature-typography-the-desc-family
plan: 02
subsystem: testing
tags: [sphinx, typst, pytest, pypdf, typst-py, gate-01, desc-signature]

# Dependency graph
requires:
  - phase: 36-shared-emission-seam-cleanup
    provides: "desc_signature/rubric decoupling (visit_desc_signature owns its own emission), the sibling body-less desc parbreak() fix (FID-06) this plan's control mirrors"
provides:
  - "tests/fixtures/signature_break_and_arrow_gate/ -- one fixture project carrying the nested-desc SIG-08 defect shape, the content-follows-nested-member non-regression shape, a sibling body-less desc control, a SIG-06 return-annotation case, and both the D-11 optional-group defect and its nested-optional non-regression control"
  - "tests/test_signature_break_and_arrow_gate.py -- 9 hand-derived assertions (5 RED, 4 CONTROL-GREEN) against 37-EMISSION-CONTRACT.md sections 6.1, 6.2, 7, 8"
  - "37-GATE-EVIDENCE-02.md -- SHA-anchored verbatim RED/CONTROL split, the SIG-08 break-count arithmetic, the full pre-phase index.typ, and the D-11 contract-section-6.2 correction restated"
affects: ["37-05 (lands the SIG-08 fix, must flip this plan's 2 SIG-08 RED assertions green)", "37-07 (lands the SIG-06 and D-11 fixes, must flip this plan's 3 SIG-06/D-11 RED assertions green)", "37-08 (merges 37-GATE-EVIDENCE-01..04.md)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Gate module shape cloned from tests/test_desc_bodyless_concat_render_gate.py: fixture-dir + temp_build_dir pytest fixtures, a sys.executable -m sphinx build helper (never uv run sphinx-build), a typst/pypdf availability skip on compiled-PDF classes only, separate classes for structural (.typ) vs. compiled-PDF assertions."
    - "U+200B-stripping helper (_strip_zwsp) applied unconditionally before every compiled-PDF text comparison, per 37-EMISSION-CONTRACT.md section 4.2's measured spurious-ZWSP-at-unrelated-glyph-boundaries hazard."
    - "Structural placement assertions search for the quoted string literal (e.g. '\", \"') rather than a specific wrapper call name (text(...) vs. raw(...)), so the assertion survives the later monospace-primitive swap without needing to be rewritten."

key-files:
  created:
    - tests/fixtures/signature_break_and_arrow_gate/conf.py
    - tests/fixtures/signature_break_and_arrow_gate/index.rst
    - tests/test_signature_break_and_arrow_gate.py
    - .planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE-02.md
  modified: []

key-decisions:
  - "Converted per-construct prose descriptions in the fixture's index.rst into rST comments (`..`) rather than paragraphs -- a paragraph under each section heading would have added desc-unrelated content between the section heading and each construct's directive, shifting the SIG-08 break-count derivation off the hand-measured 9 (pre-phase) / 8 (post-fix) baseline. Comments emit zero doctree/typ content, keeping the derivation clean while still documenting each construct's purpose in the source."
  - "D-11's structural placement assertion searches for the separator's underlying quoted string literal ('\", \"') rather than a specific wrapper function name, since the pre-phase wrapper is text(...) and the post-Phase-37 wrapper becomes raw(...) (a change owned by a different task in plan 37-07) -- this keeps the assertion stable across that unrelated wrapper swap."
  - "Deliberately did NOT call `requirements mark-complete` for SIG-06/SIG-08 despite them appearing in this plan's frontmatter `requirements` field. This plan establishes RED evidence only -- neither requirement is actually satisfied by the code today (the arrow glyph is not emitted; the exact break count is not achieved). REQUIREMENTS.md's SIG-06/SIG-08 checkboxes are left unchecked; plans 37-05 (SIG-08) and 37-07 (SIG-06) own the actual fix and will call mark-complete when it lands. Flipping the checkbox now would misrepresent the codebase's actual state during the Wave 2/4 interim, matching the project's own documented \"premature completion\" hazard (see project memory on phase.complete auto-flipping deferred requirements)."

patterns-established:
  - "Deliberate RED window: a gate-establishing plan whose module docstring explicitly labels which node ids are RED (must flip GREEN in a NAMED later plan) and which are CONTROL-GREEN (must never flip, and are labelled as controls in both the test name and docstring so a later plan cannot mistakenly 'fix' a control into the defect case)."

requirements-completed: []  # Deliberate: SIG-06/SIG-08 are NOT satisfied by this plan (RED-establishment only). See key-decisions.

# Metrics
duration: ~26min
completed: 2026-08-01
status: complete
---

# Phase 37 Plan 02: SIG-06/SIG-08/D-11 Gate Module Summary

**Hand-derived RED/CONTROL gate against the untouched translator: 5 assertions RED (SIG-08 exact break count, SIG-08 no-adjacent-break, SIG-06 arrow glyph, D-11 separator placement, D-11 target-vs-defective PDF text) and 4 CONTROL-GREEN assertions (SIG-08 content-follows-nested-member, SIG-08 sibling body-less control, D-11 explicit-concatenation non-regression, D-11 nested-optional printf control), every expected string/count derived from 37-EMISSION-CONTRACT.md sections 6.1/6.2/7/8, never from running the translator.**

## Performance

- **Duration:** ~26 min
- **Started:** 2026-08-01T04:35:41Z
- **Completed:** 2026-08-01T05:01:49Z
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 4 created, 0 modified (`typsphinx/` completely untouched -- confirmed via `git diff --stat` across all three task commits)

## Accomplishments

- Built and measured (via a real `sphinx-build -b typst` build, a doctree dump through `env.get_and_resolve_doctree`, and a real `typst.compile()` + `pypdf` extraction) a fixture project carrying all six required constructs in one document: the SIG-08 nested-desc defect (2 adjacent `parbreak()`), the content-follows-nested-member non-regression shape, the sibling body-less `desc` control, a SIG-06 return-annotation case, the D-11 dropped-separator defect (`desc_optional` with a following sibling), and the D-11 nested-optional non-regression control (both `desc_optional`s last children).
- Shipped a 9-test gate module (`TestSigBreakStructuralGate`, `TestSigArrowPdfGate`, `TestD11SeparatorStructuralGate`, `TestD11SeparatorPdfGate`) whose RED/CONTROL split against the untouched translator matches, node-for-node, this plan's own predicted split: 5 failed, 4 passed.
- Derived the SIG-08 exact expected break count (8) by hand from the fixture's doctree (9 `desc` nodes, 1 nested-pair suppression under 37-EMISSION-CONTRACT.md section 8's emission-position-marker rule) -- confirmed the pre-phase actual count is 9 via direct `grep -c "parbreak()"` measurement, not assumed.
- Confirmed by direct measurement (not by re-reading CONTEXT.md) that 37-EMISSION-CONTRACT.md section 6.2's correction holds: the closing bracket and the following `**kwargs` parameter ARE already `+`-joined on the untouched tree, so that half of D-11 is a non-regression assertion, not a fix.
- Recorded the full RED/CONTROL evidence (verbatim pytest output, the SHA measured against, the SIG-08 arithmetic, the complete pre-phase `index.typ`, and the D-11 target-vs-current table) in `37-GATE-EVIDENCE-02.md`, naming plan 37-05 as the SIG-08 fix owner and plan 37-07 as the SIG-06/D-11 fix owner (confirmed by reading both plans' own frontmatter, not assumed).

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the signature_break_and_arrow_gate fixture project** - `49e2254` (test)
2. **Task 2: Ship the SIG-06/SIG-08/D-11 gate module, hand-derived and recorded RED** - `e846227` (test)
3. **Task 3: Record the RED/GREEN split as evidence** - `2584a9f` (docs)

_TDD note: not applicable -- this plan's own `type="auto"` tasks are not `tdd="true"`; the plan itself IS the phase's TDD RED-establishment step for a fix that lands in later plans._

## Files Created/Modified

- `tests/fixtures/signature_break_and_arrow_gate/conf.py` - Minimal Sphinx config, `index` as the master document
- `tests/fixtures/signature_break_and_arrow_gate/index.rst` - Six labelled constructs (nested desc defect, content-follows-nested-member, sibling body-less control, SIG-06 return annotation, D-11 defect, D-11 nested-optional control), prose kept in rST comments so no unrelated doctree content shifts the SIG-08 break-count derivation
- `tests/test_signature_break_and_arrow_gate.py` - 9-test gate module: `TestSigBreakStructuralGate` (4 tests, no skip), `TestSigArrowPdfGate` (1 test, typst/pypdf skip), `TestD11SeparatorStructuralGate` (2 tests, no skip), `TestD11SeparatorPdfGate` (2 tests, typst/pypdf skip)
- `.planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE-02.md` - SHA-anchored RED/CONTROL evidence record (this plan's own, not the shared merge target -- 37-08 merges the four sibling files)

## Decisions Made

- Converted per-construct prose into rST comments in the fixture (see `key-decisions` in frontmatter) -- keeps the SIG-08 break-count derivation clean (9 pre-phase, 8 post-fix) by construction rather than by re-deriving around extra paragraph content.
- D-11's structural placement assertion keys off the separator's quoted string literal, not a specific wrapper function name, so it survives the unrelated `text(...)` -> `raw(...)` swap that lands elsewhere in the phase.
- Did NOT mark SIG-06/SIG-08 complete in REQUIREMENTS.md despite their presence in this plan's frontmatter `requirements` field -- this plan is RED-establishment only; see frontmatter `key-decisions` for the full rationale.

## Deviations from Plan

None - plan executed exactly as written. All six fixture constructs, all nine test assertions, and the evidence file match the plan's `<action>` and `<acceptance_criteria>` blocks for all three tasks. No `typsphinx/` file was read for the purpose of copying its current output into an assertion -- every expected string/count was hand-derived from `37-EMISSION-CONTRACT.md` first, then checked against a real build for confirmation (never the reverse).

## Issues Encountered

- **Worktree environment provisioning (NixOS sandbox):** the worktree's fresh `uv sync --extra dev` installed generic-linux ELF `ruff` (no compatible dynamic linker on this NixOS host). Resolved by symlinking the main checkout's already-patched `ruff` binary (identical build ID, confirmed via `file`) into the worktree's `.venv/bin/ruff`, alongside the documented `uv` symlink fix from `CLAUDE.md`. No project file was changed; this was pure environment setup, consistent with the documented NixOS-sandbox pattern.
- **Prose-vs-comment fixture authoring:** an early draft of `index.rst` included a real prose paragraph under each section heading (for readability). Rebuilding revealed this shifted the measured `parbreak()` count from 9 to 10 and risked tripping the "no `**bold**` markup" acceptance check (the literal `` ``**kwargs`` `` code-span). Converted all per-construct prose to rST comments before finalizing -- resolved inline during Task 1, no separate fix commit needed since it predated any commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 37-05 (Wave 2) can proceed to fix `depart_desc`'s doubled `parbreak()` -- this plan's two SIG-08 RED assertions (`test_sig08_exact_break_count_after_fix`, `test_sig08_no_adjacent_break_statements_anywhere`) and two SIG-08 CONTROL assertions are ready to gate that fix.
- Plan 37-07 (Wave 4) can proceed to fix `visit_desc_returns` (SIG-06) and `depart_desc_optional` (D-11) -- this plan's three RED assertions and two CONTROL assertions (one D-11, one SIG-08-unrelated D-11 control) are ready to gate that fix.
- Plan 37-08's evidence merge has this plan's `37-GATE-EVIDENCE-02.md` ready, including the plan-ownership table (37-05 for SIG-08, 37-07 for SIG-06/D-11) so the merge does not need to re-derive which plan owns which flip.
- No blockers. Full repo-wide `uv run pytest -q --tb=no -rf` shows exactly the 5 expected RED failures and 657 passed / 1 skipped elsewhere (the pre-existing, unrelated network-gated skip) -- zero regressions.

## Self-Check: PASSED

- `tests/fixtures/signature_break_and_arrow_gate/conf.py` - FOUND
- `tests/fixtures/signature_break_and_arrow_gate/index.rst` - FOUND
- `tests/test_signature_break_and_arrow_gate.py` - FOUND
- `.planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE-02.md` - FOUND
- `.planning/phases/37-signature-typography-the-desc-family/37-02-SUMMARY.md` - FOUND
- Commit `49e2254` (Task 1) - FOUND in `git log`
- Commit `e846227` (Task 2) - FOUND in `git log`
- Commit `2584a9f` (Task 3) - FOUND in `git log`
- Commit `7076aa9` (this SUMMARY) - FOUND in `git log`

---
*Phase: 37-signature-typography-the-desc-family*
*Completed: 2026-08-01*
