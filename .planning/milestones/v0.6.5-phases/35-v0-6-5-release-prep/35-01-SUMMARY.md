---
phase: 35-v0-6-5-release-prep
plan: 01
subsystem: testing
tags: [pytest, sphinx, typst, mitex, regression-gate, docutils]

# Dependency graph
requires:
  - phase: 34-inline-math-after-text-separator-fix
    provides: "the GATE-01 fixture (Constructs A-F) and the MATH-01 translator fix (visit_math / visit_math_block separator participation) this plan adds test coverage on top of"
provides:
  - "Construct G in the GATE-01 fixture: a `:label:`-bearing `.. math::` block inside a list item, exercising `_emit_id_anchors`'s label-anchor bookkeeping combined with `visit_math_block`'s list-item-separator flag"
  - "Four new exact-string assertions (mitex #14/#15, native #8/#9) closing WR-02 (Construct G, both paths), WR-03 (Construct F), and WR-04 (Construct E native)"
affects: [35-02-v0-6-5-release-prep-version-bump]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Every new gate-test literal was derived from a real scratch `sphinx-build -b typstpdf` build's emitted index.typ, never copied from review prose"
    - "Each new assertion proven capable of failing via a one-character perturbation driven RED then restored GREEN, per T-35-01's repudiation mitigation"

key-files:
  created: []
  modified:
    - tests/fixtures/inline_math_after_text_render_gate/index.rst
    - tests/test_inline_math_after_text_render_gate.py

key-decisions:
  - "Construct G's reST body matches Task 1's literal spec exactly: `.. math:: G = m a` with `:label: construct-g-labeled-eq` on the following line at 5-space indent (2-space list continuation + 3-space directive-option indent), following the euler-identity precedent in examples/advanced/index.rst for option indentation."
  - "WR-04's candidate assertion string (`text(\"Text before block math.\")\\n$ E = m c^2 $`, with interior spaces around the native math body) turned out to be CORRECT as originally written in 34-REVIEW.md — this contradicts RESEARCH.md's caution that it needed re-deriving to drop the interior spaces. Root cause (confirmed by reading typsphinx/translator.py:4072): `visit_math_block`'s native branch emits `f\"$ {math_content} $\"` (WITH interior spaces) — a structurally different code path from `visit_math` (inline math), whose native form is the interior-space-free `$E = m c^2$` used by Constructs B/D. The no-space convention RESEARCH.md flagged applies only to inline math; block math has always used the spaced form. No literal needed adjusting; the real build simply confirmed the review's own candidate."

patterns-established:
  - "Gate-test assertion additions continue each test method's own numbering sequence (mitex 1-13 -> 14,15; native 1-7 -> 8,9) rather than restarting or renumbering existing comments."

requirements-completed: []  # REL-03 is closed by 35-02, not this plan (D-07: this plan is adjacent test-only work, not itself a numbered SC)

coverage:
  - id: D1
    description: "Construct G (labeled display-math equation inside a list item) added to the GATE-01 fixture, exercising the `_emit_id_anchors` + list-item-separator ordering interaction WR-02 identified as untested"
    verification:
      - kind: unit
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_mitex_path"
        status: pass
      - kind: unit
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_native_path"
        status: pass
    human_judgment: false
  - id: D2
    description: "Four new exact-string assertions closing WR-02 (Construct G mitex + native), WR-03 (Construct F), and WR-04 (Construct E native), each proven capable of failing via one-character perturbation RED/GREEN"
    verification:
      - kind: unit
        ref: "tests/test_inline_math_after_text_render_gate.py (assertions 14, 15, 8, 9 — see RED/GREEN log below)"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-07-29
status: complete
---

# Phase 35 Plan 01: Close WR-02/WR-03/WR-04 Test Warnings Summary

**Added Construct G (labeled display-math inside a list item) to the GATE-01 fixture and four exact-string assertions derived from real `sphinx-build -b typstpdf` builds, closing all three test-side Warnings from the Phase 34 code review with zero `typsphinx/` changes.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-07-29
- **Tasks:** 2/2 completed
- **Files modified:** 2

## Accomplishments

- Construct G appended to `tests/fixtures/inline_math_after_text_render_gate/index.rst`: a bullet-list item containing `Text before labeled block math.` / a `:label: construct-g-labeled-eq`-bearing `.. math:: G = m a` / `Text after labeled block math.` — structurally distinct from Construct E (unlabeled) so it actually exercises `_emit_id_anchors`'s label-anchor bookkeeping.
- Four new exact-string assertions added to `tests/test_inline_math_after_text_render_gate.py`, each derived from a real scratch build (not copied from `34-REVIEW.md`'s illustrative candidates):
  - Assertion 14 (mitex, WR-02): the `[#metadata(none) <index:equation-construct-g-labeled-eq>]` anchor and `mitex(\`G = m a` are newline-separated, plus a `]mitex(` juxtaposition guard.
  - Assertion 15 (mitex, WR-03): `list({\nparbreak()\n\nmi(\`a+b\`)` — no separator or leading operator before Construct F's sole math expression.
  - Assertion 8 (native, WR-04): `text("Text before block math.")\n$ E = m c^2 $` — the native-path equivalent of the existing mitex assertion 7.
  - Assertion 9 (native, WR-02 native half): the anchor and `$ G = m a` are newline-separated, plus a `]$` juxtaposition guard.
- Both test methods (`test_typstpdf_separates_inline_math_mitex_path`, `test_typstpdf_separates_inline_math_native_path`) pass with all 20 pre-existing assertions untouched (no renumbering, no weakening, no deletion) plus the 4 new ones.
- `git diff --name-only -- typsphinx/` is empty for the whole plan — milestone invariant #3 intact.

## Verbatim Emitted Sequences (Task 1)

Captured from two scratch builds (`sys.executable -m sphinx -b typstpdf`, outside the repo tree) after appending Construct G, one with default (mitex) settings and one with `-D typst_use_mitex=0` (native):

**1. Construct G, mitex path** (anchor + `mitex(...)` call):
```
[#metadata(none) <index:equation-construct-g-labeled-eq>]

mitex(`G = m a

`)
```
(the anchor's closing token is `]`; two newlines separate it from `mitex(`, confirming no juxtaposition — `]mitex(` does not occur anywhere in the emitted output.)

**2. Construct G, native path** (anchor + `$...$` call):
```
[#metadata(none) <index:equation-construct-g-labeled-eq>]

$ G = m a

 $
```
(same anchor terminator `]`, two newlines before `$ G = m a`; `]$` does not occur anywhere in the emitted output.)

**3. Construct F, mitex path** (unchanged by the Construct G addition, re-verified post-edit):
```
list({
parbreak()

mi(`a+b`)
})
```

**4. Construct E, native path** (unchanged by the Construct G addition, re-verified post-edit):
```
text("Text before block math.")
$ E = m c^2 $
```

## Discrepancy Found vs. 34-REVIEW.md / 35-RESEARCH.md

RESEARCH.md's "Caution on WR-04's literal candidate string" warned that the review's candidate `'text("Text before block math.")\n$ E = m c^2 $'` (with spaces immediately inside the `$` delimiters) would need correcting to match "every existing native-path assertion['s]... no interior spaces" convention (citing `$E = m c^2$` from Constructs B/D). **The real build shows this caution does not apply to block math**: reading `typsphinx/translator.py:4072`, `visit_math_block`'s native branch is `self.add_text(f"$ {math_content} $")` — deliberately WITH interior spaces — a structurally different emission site from `visit_math` (inline math), whose native form (`f"${math_content}$"` at a different call site) is the interior-space-free convention Constructs B/D exercise. The review's own WR-04 candidate string was correct as originally written; no adjustment was needed. This is recorded here per the plan's explicit instruction to record any discrepancy between a derived literal and the review's candidate.

## RED/GREEN Perturbation Log (Task 2, T-35-01 mitigation)

Each of the four new assertions was temporarily perturbed by one character in the working copy, confirmed to drive that specific assertion RED, then restored and confirmed GREEN again. No perturbed state was committed.

| Assertion | Literal perturbed | RED confirmed | Restored | GREEN confirmed |
|---|---|---|---|---|
| 14 (mitex, Construct G anchor) | `labeled-eq` -> `labeled-eX` (line 265) | Yes — `AssertionError` at line 264 | Yes | Yes — 1 passed |
| 15 (mitex, Construct F) | `a+b` -> `a+X` (line 280) | Yes — `AssertionError` at line 280 | Yes | Yes — 1 passed |
| 8 (native, Construct E) | `E = m c^2` -> `E = m cX2` (line 375) | Yes — `AssertionError` at line 375 | Yes | Yes — 1 passed |
| 9 (native, Construct G anchor) | `labeled-eq` -> `labeled-eX` (line 384) | Yes — `AssertionError` at line 383 | Yes | Yes — 2 passed (full file) |

Final state: `uv run python -m pytest tests/test_inline_math_after_text_render_gate.py -q` → `2 passed`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Append Construct G to the GATE-01 fixture** - `f81fdfa` (test)
2. **Task 2: Add the four exact-string assertions closing WR-02/WR-03/WR-04** - `c0e66a8` (test)

_Note: worktree mode — STATE.md/ROADMAP.md are not touched by this plan; the orchestrator updates them centrally after the wave merges._

## Files Created/Modified

- `tests/fixtures/inline_math_after_text_render_gate/index.rst` - added Construct G (labeled display-math inside a list item)
- `tests/test_inline_math_after_text_render_gate.py` - added assertions 14/15 (mitex) and 8/9 (native)

## Decisions Made

- Used the label value `construct-g-labeled-eq` (Claude's Discretion per CONTEXT.md) rather than 35-RESEARCH.md's draft `newtons-second-law`, for self-documenting grep-ability.
- Confirmed the discrepancy analysis above: WR-04's candidate literal needed no correction — the interior-space form is intentional and specific to `visit_math_block`'s native branch, distinct from `visit_math`'s space-free inline native form.

## Deviations from Plan

None - plan executed exactly as written. The one "discrepancy" the plan anticipated (WR-04's candidate string) was investigated per instruction and found to match the real build output exactly; this is documented above as required, not a deviation from the plan's own instructions.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The GATE-01 gate's own test surface is now complete (WR-02/WR-03/WR-04 all closed); `uv run python -m pytest tests/test_inline_math_after_text_render_gate.py -q` is green with 2 passed, 20 pre-existing + 4 new assertions all present and unweakened.
- Per D-07's ordering constraint, this plan's green state is the prerequisite for 35-02 (version bump + CHANGELOG + full live-run evidence) — the release's own regression evidence should now be measured against this complete test surface.
- WR-01 (the `visit_math_block` redundant blank-line finding) remains deliberately unaddressed per D-05 — filed as a todo by a later plan in this phase, not this one.

---
*Phase: 35-v0-6-5-release-prep*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `tests/fixtures/inline_math_after_text_render_gate/index.rst`
- FOUND: `tests/test_inline_math_after_text_render_gate.py`
- FOUND: `.planning/phases/35-v0-6-5-release-prep/35-01-SUMMARY.md`
- FOUND: commit `f81fdfa` (Task 1)
- FOUND: commit `c0e66a8` (Task 2)
- FOUND: commit `d24caab` (SUMMARY)
