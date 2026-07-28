---
phase: 34-inline-math-after-text-separator-fix
plan: 02
subsystem: translator
tags: [typst, sphinx, translator, math, mitex, separator]

requires:
  - phase: 34-01
    provides: "GATE-01 fixture Sphinx project + tests/test_inline_math_after_text_render_gate.py, recorded RED against the unfixed translator"
provides:
  - "visit_math participates in all three separator protocols (paragraph, code-mode inline concat, list-item), matching visit_literal"
  - "visit_math_block participates in the list-item separator protocol (D-01), placed after _emit_id_anchors"
  - "GATE-01 gate GREEN on both the mitex default and -D typst_use_mitex=0 native emission paths"
  - "34-GATE-EVIDENCE.md GREEN section: post-fix run, per-construct emitted-separator diffs, RED->GREEN verdict (two named commit SHAs), diff scope"
affects: [34-03]

tech-stack:
  added: []
  patterns:
    - "3-protocol leaf-inline-node separator participation (paragraph / code-mode concat / list-item), applied to visit_math exactly as visit_literal/visit_Text already do it"
    - "List-item-only separator participation for block nodes (visit_math_block), isolated from the concat-context half since a block node is never a concat-context sibling"

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - tests/fixtures/inline_math_after_text_render_gate/index.rst
    - tests/test_inline_math_after_text_render_gate.py
    - .planning/phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md

key-decisions:
  - "Corrected the GATE-01 fixture's math content from E=mc^2 to E = m c^2 (a mid-plan deviation, not a separator-shape change) after real typst.compile() proved E=mc^2 parses as a single unknown identifier 'mc' in native Typst math mode -- a pre-existing, unrelated defect only reachable once the separator fix let both builds get past the point the separator bug used to abort them at"

patterns-established:
  - "One fix point upstream of the mitex/native branch (in visit_math) covers both mi(...) and $...$ emission identically -- no per-branch separator logic"

requirements-completed: [MATH-01]

coverage:
  - id: D1
    description: "visit_math implements the full three-protocol separator participation (paragraph / code-mode concat / list-item), matching visit_literal, with the mitex/native branch and label-anchor emission byte-unchanged"
    requirement: MATH-01
    verification:
      - kind: unit
        ref: "inspect.getsource(TypstTranslator.visit_math) structural assertion (exactly one _emit_inline_concat_separator call, exactly one _mark_inline_concat_content call, correct ordering)"
        status: pass
      - kind: integration
        ref: "tests/test_math_mitex.py, tests/test_math_native.py, tests/test_math_fallback.py -q (23 passed, unedited)"
        status: pass
    human_judgment: false
  - id: D2
    description: "visit_math_block implements the list-item half of the separator protocol only (D-01), placed after _emit_id_anchors, with the equation emission and trailing block-close byte-unchanged"
    requirement: MATH-01
    verification:
      - kind: unit
        ref: "inspect.getsource(TypstTranslator.visit_math_block) structural assertion (exactly two list_item_needs_separator references, zero concat-helper references, correct ordering)"
        status: pass
      - kind: integration
        ref: "tests/test_math_mitex.py, tests/test_math_native.py, tests/test_math_fallback.py, tests/test_integration_advanced.py -q (35 passed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "GATE-01 gate (tests/test_inline_math_after_text_render_gate.py) passes on BOTH the mitex default build and the -D typst_use_mitex=0 native build, and 34-GATE-EVIDENCE.md records a SHA-anchored RED->GREEN verdict"
    requirement: MATH-01
    verification:
      - kind: integration
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_mitex_path"
        status: pass
      - kind: integration
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_native_path"
        status: pass
      - kind: other
        ref: "grep -c 'RED → GREEN verdict' .planning/phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md returns 1; full-suite baseline 649 passed, 1 skipped, 0 failed"
        status: pass
    human_judgment: false

duration: 14min
completed: 2026-07-28
status: complete
---

# Phase 34 Plan 02: visit_math / visit_math_block Separator Fix Summary

**Made `visit_math` participate in all three separator protocols (paragraph, code-mode concat, list-item) and `visit_math_block` participate in the list-item protocol, turning the GATE-01 gate GREEN on both the mitex and native `-D typst_use_mitex=0` emission paths**

## Performance

- **Duration:** ~14 min
- **Completed:** 2026-07-28T14:06:03Z
- **Tasks:** 3 completed
- **Files modified:** 4 (1 production, 3 test/evidence)

## Accomplishments
- `visit_math` (inline math) now calls `_emit_inline_concat_separator()` / the `in_list_item` newline guard before emission, and `_mark_inline_concat_content()` / `in_list_item` bookkeeping after -- byte-identical to `visit_literal`'s existing pattern. The mitex/native branch, `_convert_latex_to_typst` call, and label-anchor emission are untouched.
- `visit_math_block` (display math) now newline-separates from a preceding list-item sibling (gated on `in_list_item` / `list_item_needs_separator`, placed after `_emit_id_anchors` to avoid double-separating an anchored equation) and marks itself as a sibling for the next one. No concat-context participation was added (block nodes are never concat-context siblings).
- GATE-01 (`tests/test_inline_math_after_text_render_gate.py`) flipped from `2 failed` (Plan 01's recorded RED) to `2 passed` on both the mitex default and native paths, with the top-level-paragraph control emission staying byte-identical.
- Post-fix full-suite baseline: `649 passed, 1 skipped, 0 failed` -- exactly the state Plan 01's RED evidence predicted (the two gate tests flipping from FAILED to PASSED, nothing else changing).
- `34-GATE-EVIDENCE.md` now carries the complete RED->GREEN record: post-fix pytest run, per-construct emitted-separator diffs for B/C/D/E (all flipped from juxtaposed to correctly separated) and A/`:type:`/F (unregressed), an explicit verdict naming both commit SHAs, and the diff scope.

## Task Commits

Each task was committed atomically:

1. **Task 1: Make visit_math participate in the concat-context and list-item separator protocols** - `d78e223` (fix)
2. **Task 2: Make visit_math_block participate in the list-item separator protocol** - `a259ee0` (fix)
3. **Deviation fix: GATE-01 fixture math content invalid under native Typst** - `a737e16` (fix) -- discovered while proving Task 3's GREEN run; see Deviations below
4. **Task 3: Prove GREEN on both paths and append the GREEN evidence section** - `ee19799` (docs)

**Plan metadata:** commit pending (this SUMMARY + final docs commit)

## Files Created/Modified
- `typsphinx/translator.py` - `visit_math` and `visit_math_block` now participate in the separator protocols every other leaf/block visitor already implements
- `tests/fixtures/inline_math_after_text_render_gate/index.rst` - Corrected math content (`E=mc^2` -> `E = m c^2`) to be valid under native Typst math parsing (deviation, see below)
- `tests/test_inline_math_after_text_render_gate.py` - Updated exact-string assertions to match the corrected math content (separator shape assertions unchanged)
- `.planning/phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md` - Appended the GREEN evidence section (post-fix run, per-construct diffs, RED->GREEN verdict, diff scope)

## Decisions Made
- Applied the exact `visit_literal` 3-protocol pattern to `visit_math` with zero new helpers, per 34-PATTERNS.md's fix shape -- no separator logic was invented or duplicated across the mitex/native branch.
- For `visit_math_block`, only transplanted the list-item half of the pattern (no `_emit_inline_concat_separator()` call), since a block-level node is structurally never a sibling inside one of the five code-mode concat contexts; calling the concat helper there would have wrongly emitted a `+` operator around a block expression.
- Corrected the GATE-01 fixture's math content from `E=mc^2` to `E = m c^2` after discovering (via a direct `typst.compile()` probe) that adjacent letters with no operator between them parse as a single unknown identifier in native Typst math mode -- confirmed empirically: `$E=mc^2$` raises `TypstError: unknown variable: mc`, `$E = m c^2$` compiles cleanly. This matches the existing project convention already used in `tests/test_math_native.py` (`"$ E = m c^2 $"`). The mitex/LaTeX rendering path is unaffected by the added whitespace (verified via NFKC-normalized PDF text extraction: the rendered "mc" substring is unchanged).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] GATE-01 fixture's `E=mc^2` math content is invalid under native Typst, unrelated to the separator defect**
- **Found during:** Task 3 (proving GREEN on both paths) -- the mitex-path gate test passed immediately after Task 2's fix, but the native-path gate test failed with a *new* error: `TypstError: unknown variable: mc`, a real Typst compile fatal distinct from the separator juxtaposition fatal this plan fixes.
- **Issue:** `E=mc^2` (adjacent letters `m` and `c` with no operator between them) is parsed by Typst's native math mode as a single identifier `mc`, which is undefined. This defect was always latent in Plan 01's fixture but was previously masked: the separator bug aborted the build *before* Typst ever reached the point of resolving `mc` as a variable. Fixing the separator bug let the native-path build proceed far enough to expose this second, independent, pre-existing defect.
- **Fix:** Changed every occurrence of `E=mc^2` in `tests/fixtures/inline_math_after_text_render_gate/index.rst` to `E = m c^2` (explicit spacing, matching the existing project convention in `tests/test_math_native.py`), and updated the corresponding exact-string assertions in `tests/test_inline_math_after_text_render_gate.py` to match. Did NOT touch `_convert_latex_to_typst` or any other production code -- fixing the LaTeX-to-Typst implicit-multiplication conversion generally is a distinct, higher-risk problem outside MATH-01's scope (this plan's Non-goals: "No other visitor is retrofitted").
- **Files modified:** `tests/fixtures/inline_math_after_text_render_gate/index.rst`, `tests/test_inline_math_after_text_render_gate.py`
- **Verification:** Confirmed directly via `typst.compile()`: a standalone `$E=mc^2$` raises `TypstError: unknown variable: mc`; a standalone `$E = m c^2$` compiles cleanly. Re-ran both the mitex and native `sphinx-build -b typstpdf` scratch builds against the corrected fixture -- both exit 0 with empty stderr, `index.pdf` present with `%PDF` magic bytes on both paths. Confirmed the mitex-rendered PDF text is unaffected by the added source whitespace (NFKC-normalized extracted text still contains the `mc` substring). No exact-string assertion was weakened to a substring check -- only the literal math content changed.
- **Committed in:** `a737e16`

---

**Total deviations:** 1 auto-fixed (Rule 1 - pre-existing, unrelated test-fixture bug exposed by this plan's fix)
**Impact on plan:** Necessary to complete the GATE-01 gate's GREEN proof on the native path; the separator fix itself (the plan's actual deliverable) required no deviation. No scope creep into production code -- `_convert_latex_to_typst` was deliberately left untouched.

## Issues Encountered

None beyond the deviation documented above. Both `visit_math` and `visit_math_block` edits matched `34-PATTERNS.md`'s fix shape exactly on the first attempt; all acceptance-criteria structural assertions (`inspect.getsource` checks) passed without iteration once black's line-wrapping was applied to the gate test file.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 03's regression sweep has a clean pre-fix full-suite baseline (from `34-01-SUMMARY.md`: 647 passed, 1 skipped, 0 environmentally-failing) and this plan's post-fix baseline (649 passed, 1 skipped, 0 failed) to diff against -- the only expected delta is the two gate tests flipping from FAILED to PASSED.
- `34-GATE-EVIDENCE.md` is now complete for Plan 03 to reference: RED (Plan 01) and GREEN (this plan) sections both present, naming commit SHAs `26f8395ba55e4dd851e07046b6bab42bb5222939` (RED) and `a737e16510081f940d897666ab5181a7df2da3f7` (GREEN).
- No blockers.

---
*Phase: 34-inline-math-after-text-separator-fix*
*Completed: 2026-07-28*
