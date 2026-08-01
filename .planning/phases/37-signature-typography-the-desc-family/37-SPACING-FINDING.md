# 37 — Wrapper vertical-spacing finding (post-Wave-3, orchestrator-measured)

**Status:** open — owner decided 2026-08-01 to fix inside Phase 37.
**Found by:** the post-merge gate after Wave 3 (`37-06`), via
`tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_block_math_pdf_text_is_invariant_across_the_math02_fix`.
**Measured by:** orchestrator, on the merged tree at `f13586d`, with real
`sphinx-build -b typst` + `typst.compile(format="png", ppi=140)` renders.

---

## 1. The defect

`37-EMISSION-CONTRACT.md` §3 mandates the `desc_signature` wrapper as:

```
block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {
```

Rendered, **every signature's glyphs overlap the first line of its own description body.**
This is not a `pypdf` line-grouping artifact — it is visible in the rasterised page.

Reproduced on two independent fixtures:

| Fixture | Signatures on the page | All overlapping? |
|---|---|---|
| `tests/fixtures/signature_typography_gate` (p.3) | 10 | yes |
| `tests/fixtures/inline_math_after_text_render_gate` (p.3) | 1 (`math_inline_default`) | yes |

The MATH-02 golden caught it because the confval signature stopped starting its own
extracted-text line:

```
-prose then math (math following a sibling, exactly one separator).
-math_inline_default Type: 𝑥  Default: The value of 𝑥 computed inline
+prose then math (math following a sibling, exactly one separator).math_inline_default
+Type: 𝑥  Default: The value of 𝑥 computed inline
```

## 2. Why the contract's measurement missed it

§3 justifies the zeroing with `[measured]` figures:

> Typst `block()`'s default spacing adds ~26.5pt of vertical gap at each block boundary
> (14.39pt plain-flow baseline vs. 40.88pt with `block()` defaults vs. 14.48pt with both
> zeroed), which would reintroduce a SIG-08-shaped doubled-gap defect in a new form.

Those figures are not reproduced by the real generated document. The probe they came from
did not carry the surrounding paragraph flow, so zeroing `above`/`below` removes the
**paragraph separation** the signature needs, not merely a redundant block gap.

The stated fear — "a SIG-08-shaped doubled-gap defect in a new form" — **does not
materialise**, because Wave 2 (`37-05`) already removed the duplicate `parbreak()` at its
source with the emission-position marker. The zeroing was therefore over-corrective: it
compensates for a defect that no longer exists, and pays for it with overlapping glyphs.

## 3. Variants compiled and compared (same emitted document, wrapper string swapped)

| Variant | Wrapper | Result |
|---|---|---|
| v1 (current) | `block(above: 0pt, below: 0pt, sticky: true, …)` | ✗ signature overlaps its body on every signature |
| v2 | `block(sticky: true, …)` — Typst defaults | ✓ **clean and uniform**; best of the four |
| v3 | `block(above: 0pt, below: 0.5em, sticky: true, …)` | ~ body separation restored, but a *following* signature still crowds the paragraph above it (`above: 0pt`) |
| v4 | `block(above: 0pt, below: 1.2em, sticky: true, …)` | ~ same residual as v3 |

**v2 also renders the SIG-08 nested-desc case correctly** — checked on
`tests/fixtures/signature_break_and_arrow_gate` p.3: `class SigBreakOuterClassOne` → body →
`sig_break_inner_method_one()` → body spacing is uniform, with no doubled gap. So adopting
Typst's default block spacing does not resurrect SIG-08.

Renders retained under the session scratchpad (`var_v1_current/`, `var_v2_defaults/`,
`var_v3_below05/`, `var_v4_below12/`, `break_cur/`, `break_def/`).

## 4. What a fix must do

1. Amend `37-EMISSION-CONTRACT.md` §3: replace the `above: 0pt, below: 0pt` mandate and its
   measurement paragraph with the corrected measurement above. Record *why* the original
   figure was wrong, so the next phase does not re-derive the same mistake.
2. Change the wrapper in `typsphinx/translator.py` (`visit_desc_signature`).
3. **Re-derive by hand** every expected string that embeds the wrapper text. Known sites:
   - `tests/test_signature_typography_gate.py` (Wave 1, `37-01`)
   - `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` (Wave 1, `37-04`)
   - any expectation added by `37-06` / `37-07`
   Re-derivation only — regenerating from the new output voids the phase's evidence
   (ROADMAP SC#5, milestone invariant #4).
4. Hand-update the two Phase 34 goldens
   (`tests/fixtures/inline_math_pdf_text_mitex.golden.txt`,
   `inline_math_pdf_text_native.golden.txt`), recording in the commit message that the change
   is Phase-37-induced signature typography and **not** a MATH-02 regression — the Phase 34
   invariance claim is about the MATH-02 fix, which remains untouched.
5. Re-run the visual check. `37-08`'s `must_haves` require the owner to confirm the wrapper
   "introduces no visible artifact beyond the intended spacing"; that criterion is what this
   finding currently violates.
