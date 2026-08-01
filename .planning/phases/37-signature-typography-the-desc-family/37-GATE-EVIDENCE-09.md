# Phase 37 Plan 09 GATE Evidence: Signature Wrapper Vertical-Spacing Gap Closure

This is plan `37-09`'s own evidence record (gap closure, wave 5, after the post-merge gate caught
the Wave-3-introduced overlap defect). It supersedes nothing in `37-GATE-EVIDENCE-01..04.md` --
those cover Waves 1-2's RED capture; this covers the fix and re-measurement that closes the phase
out fully green.

Every figure below was read directly from a real `typst.compile()` / `sphinx-build` /
`pypdf.PdfReader` run in this worktree this session. No number was transcribed from
`37-SPACING-FINDING.md` without being independently reproduced first (Task 1's explicit
instruction).

---

## 1. Starting state (measured, matching the orchestrator's `wave_state`)

```
$ uv run pytest -q --tb=no -rf
1 failed, 685 passed, 1 skipped
FAILED tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_block_math_pdf_text_is_invariant_across_the_math02_fix
```

Confirmed at HEAD `ac8a582` (this plan's own creation commit), before any Task 1 edit.

---

## 2. Task 1 -- re-measuring the wrapper spacing (own measurement, not transcribed)

### 2.1 Visual reproduction of the defect

Built `tests/fixtures/signature_typography_gate` and `tests/fixtures/signature_break_and_arrow_gate`
through `-b typst`, swapped the wrapper-open literal in the emitted `.typ` for each of `v1_current`
(`block(above: 0pt, below: 0pt, sticky: true, ...)`, the Wave-3 form) and `v2_defaults`
(`block(sticky: true, ...)`, no override), and rasterised each variant via
`typst.compile(format="png", ppi=140)`.

- **v1_current, `signature_typography_gate` p.3**: every one of the 10 signatures on the page has
  its glyphs directly overlapping the first line of its own description body -- reproduced,
  matching `37-SPACING-FINDING.md`'s table exactly.
- **v2_defaults, same page**: clean, uniform paragraph-to-paragraph spacing throughout; no overlap
  anywhere.
- **v1_current, `signature_break_and_arrow_gate` p.3 (the SIG-08 nested-desc fixture)**: the outer
  class signature overlaps its own body, and the nested method signature overlaps ITS body too --
  the defect reproduces inside the nested case as well.
- **v2_defaults, same page**: uniform spacing at every level of nesting -- no doubled gap, no
  overlap.

(PNGs retained under this session's scratchpad; not committed -- per this project's convention, gate
evidence records the observation and the reproduction method, not binary artifacts.)

### 2.2 Quantitative re-measurement (`context measure(...)` deltas, in real paragraph flow)

An initial attempt to measure the gap via a `context [#metadata((y: here().position().y)) <label>]`
marker placed immediately after the wrapper block (mirroring what the original probe's figures
likely came from) returned the **same** `y` position regardless of the block's `below` value (0pt,
0.5em, and 1.2em all queried identically) -- a zero-height marker with no intervening paragraph
break does not pick up a pending block-spacing collapse, which only resolves once genuine
block-level content follows it. This is documented as the likely cause of the original
14.39/40.88/14.48pt figures' inability to distinguish the zeroed and defaulted forms.

Switching to `measure()` deltas -- `measure(preceding + signature, width: w).height -
measure(preceding, width: w).height - measure(signature, width: w).height` (and the mirror form for
the below-side gap) -- at this project's own 11pt document text size, gives:

| Wrapper | Above-side gap | Below-side gap |
|---|---|---|
| `block(above: 0pt, below: 0pt, sticky: true, ...)` (Wave 3) | **0pt** | **0pt** |
| `block(sticky: true, ...)` (no override) | **13.2pt** | **13.2pt** |
| No block at all -- two ordinary paragraphs in sequence | **13.2pt** | **13.2pt** |

13.2pt = 1.2em at 11pt (Typst's default block/paragraph spacing). The defaulted wrapper's gap is
**byte-for-byte identical** to plain paragraph-to-paragraph flow, on both sides -- confirming that
dropping the override restores exactly the spacing a signature had before Phase 37 wrapped it in a
block at all, not an arbitrary chosen value.

### 2.3 SIG-08 re-verification

Re-rendered `tests/fixtures/signature_break_and_arrow_gate` under `block(sticky: true, ...)`
(section 2.1 above) and separately re-ran `tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate`
(all 4 assertions) after the Task 2 translator edit -- all green (section 5 below). The original
contract's stated fear ("would reintroduce a SIG-08-shaped doubled-gap defect") does not materialise
because plan `37-05` already removed the duplicate `parbreak()` at its source.

### 2.4 Contract amendment

`37-EMISSION-CONTRACT.md` section 3 was amended in place (dated, marked post-Wave-3) with the
corrected wrapper, the measurement above, the explanation of why the original probe missed it, and
the SUPERSEDED disposition of the SIG-08 fear. Section 9's five embedded wrapper lines were updated
to match, mechanically (wrapper text only). Commit `626a4d7`.

---

## 3. Task 2 -- translator change and per-file hand-derivation

### 3.1 Translator change

`typsphinx/translator.py`'s `visit_desc_signature` emission (previously
`f"{prefix}block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: {SHARED_INDENT_STEP}, {{"`)
changed to
`f"{prefix}block(sticky: true, par(hanging-indent: {SHARED_INDENT_STEP}, {{"` -- dropping only the
`above: 0pt, below: 0pt` segment, byte-for-byte matching the amended contract section 3. The
docstring's now-false "mandatory, not cosmetic" claim was rewritten to state the new spacing and
the reason for the change (CLAUDE.md-consistent: code must not assert something no longer true).

### 3.2 Per-file hand-derivation table

Every expected string below was re-derived BY HAND from the amended `37-EMISSION-CONTRACT.md`
section 3 (re-read for each site, per the plan's explicit instruction) -- never by running the new
translator and copying its output.

| File | Site | Old (hand-derived pre-fix) | New (hand-derived from amended §3) | Contract section |
|---|---|---|---|---|
| `typsphinx/translator.py` | `visit_desc_signature` emission (~4943) | `block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: {STEP}, {` | `block(sticky: true, par(hanging-indent: {STEP}, {` | §3 (amended) |
| `typsphinx/translator.py` | docstring (~4883-4898) | asserted zeroing "mandatory, not cosmetic" | states the corrected spacing, the 0pt/13.2pt measurement, and the superseded SIG-08 rationale | §3 (amended) |
| `tests/test_signature_typography_gate.py` | module docstring, region-slicing rationale (~24-27) | quoted the zeroed wrapper literal | quoted the corrected wrapper literal | §3 (amended) |
| `tests/test_signature_page_boundary_render_gate.py` | `EXPECTED_PAGE_COUNT_PRE_PHASE` + `test_page_count_does_not_inflate` | pinned at 6, justified by the zeroed-spacing "Pitfall 1" rationale | re-pinned at 7 -- a REAL re-measurement of this fixture's own tight page geometry under the corrected wrapper (section 4 below), not a golden copied from output to hide a regression | §3 (amended) + own real compile |
| `tests/test_translator.py` | `test_desc_signature_rendering` (~3383-3386) | asserted `"block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {"` | asserted `"block(sticky: true, " "par(hanging-indent: 2.5em, {"` | §3 (amended) |
| `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | 5 signature lines (26, 36, 40, 43, 59) | `block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: 2.5em, {...` | `block(sticky: true, par(hanging-indent: 2.5em, {...` | §3 (amended) + §9 (re-derivation, mechanically updated to match) |

`git diff` on `golden.typ` (commit `76324bf`) confirms exactly 5 lines changed, confined to the
wrapper-open literal; every other byte -- the rubric lines, the plain-bold control, the
`list({...})` structure, every `par({text(...)})` body, every anchor/`linebreak()`/`parbreak()` --
is untouched.

### 3.3 The page-count re-pin (full reasoning)

`tests/test_signature_page_boundary_render_gate.py`'s `signature_page_boundary_render_gate` fixture
is deliberately built with almost no page slack (`PAGE_HEIGHT_PT=200pt`, `PAGE_MARGIN_PT=20pt`) so
the pre-Phase-37 SIG-09 split defect reproduces. `EXPECTED_PAGE_COUNT_PRE_PHASE=6` was originally
measured against the truly untouched (pre-Phase-37, no block, no `sticky: true`) translator, where
the split defect this whole gate exists to catch was PRESENT.

Once the corrected wrapper restores real paragraph spacing (section 2.2), the boundary signature and
its `sticky: true`-bound body no longer fit in the remaining room on page 6. `sticky: true`'s
keep-together then correctly pushes the whole unit onto page 7 AS ONE PIECE -- confirmed by
`test_primary_signature_and_body_share_a_page`, which stays green (name, params, and the body's
first line still land together, one page later). This is the keep-together mechanism doing its job,
not a per-signature spacing regression.

Swept above/below from 0em to 1.2em against the real fixture (real `sphinx-build` + real
`typst.compile()`, `PAGE_HEIGHT_PT`/`PAGE_MARGIN_PT` unchanged):

```
above0em_below0em      -> 6 pages
above0.2em_below0.2em  -> 6 pages
above0.3em_below0.3em  -> 6 pages
above0.4em_below0.4em  -> 6 pages
above0.5em_below0.5em  -> 6 pages
above0.6em_below0.6em  -> 6 pages
above0.8em_below0.8em  -> 6 pages
above0.85em_below0.85em -> 6 pages
above0.9em_below0.9em  -> 7 pages
above0.95em_below0.95em -> 7 pages
above1.0em_below1.0em  -> 7 pages
current_defaults (1.2em) -> 7 pages
```

The page count only crosses from 6 to 7 between 0.85em and 0.9em -- confirming this is specific to
how much extra room THIS ONE keep-together unit needs on THIS deliberately tight fixture, not a
per-signature inflation that would compound across a real (non-adversarial-page-height) document.
Choosing an intermediate value just under this threshold (e.g. 0.85em) purely to keep the old
baseline of 6 would have been an unprincipled magic number contradicting the measured evidence that
full Typst defaults reproduce exact plain-paragraph-flow spacing (section 2.2) -- the simplest,
most defensible choice per D-10's "Claude's discretion, decided by measurement." The baseline was
re-pinned to 7, the real, reproducible page count under the corrected wrapper, with the reasoning
recorded in both the constant's own comment and the test's docstring. Commit `76324bf`.

### 3.4 Task 2 verification

```
$ uv run pytest tests/test_signature_typography_gate.py tests/test_signature_page_boundary_render_gate.py \
    tests/test_signature_overflow_render_gate.py tests/test_signature_break_and_arrow_gate.py \
    tests/test_desc_rubric_decoupling_render_gate.py tests/test_desc_bodyless_concat_render_gate.py -q
37 passed in 4.56s
```

---

## 4. Task 3 -- Phase 34 goldens, surgical update

### 4.1 Diff, both goldens

Rebuilding `tests/fixtures/inline_math_after_text_render_gate` through `-b typstpdf` (both the mitex
default and `-D typst_use_mitex=0` native paths) under the corrected wrapper and diffing the
extracted PDF text against the committed pre-fix baselines:

```
--- baseline (mitex)
+++ current (mitex)
@@ -16,7 +16,8 @@
 Construct C: collapsed field bodies -- the concat context. The [ZWSP]:type[ZWSP]: value is the sole inline math
 (math as the FIRST expression in the concat context, no leading separator). The [ZWSP]:default[ZWSP]: value is
 prose then math (math following a sibling, exactly one separator).
-math_inline_default Type: x  Default: The value of x computed inline
+math_inline_default
+Type: x  Default: The value of x computed inline
 A description paragraph so the confval also exercises the block field-body and normal-paragraph
 path.
 Construct D: definition-list term -- a second concat context.
```

The native-path diff is byte-identical in shape (same single line splits into two, nothing else
differs). Both diffs are confined to exactly this one line -- no other line in either 17-line-visible
document moved.

### 4.2 Why this line, and only this line, changes

Pre-Phase-37, `desc_signature` was wrapped in `strong({...})` -- an INLINE Typst call, not a block.
With no block-level boundary, the confval's signature could join the same visual line as adjacent
concat-context content when there was room, which is why the pre-fix baseline shows
`math_inline_default Type: x  Default: ...` on one line. Phase 37 (Wave 3 onward) wraps
`desc_signature` in a genuine `block(...)` -- an intrinsically block-level Typst construct -- so the
signature can never again share a visual line with adjacent content, REGARDLESS of the `above`/
`below` spacing amount. This is a structural consequence of adopting `block()` at all (D-10), not a
spacing-amount artifact; restoring correct spacing (this plan) does not and cannot revert to the
pre-block inline-joining behaviour. The signature-overlap DEFECT (Wave 3's `above: 0pt, below: 0pt`)
is what is fixed here; the pre-existing inline-vs-block layout change was already locked in by D-10
and is unrelated to this plan's own fix.

Visual re-check (`typst.compile(format="png", ppi=140)` on the rebuilt fixture, page 3): the
`math_inline_default` signature line sits on its own line in bold monospace, with normal paragraph
spacing separating it from the `Type: x  Default: ...` field-body paragraph below -- no overlap, no
visual defect.

### 4.3 Pre-Phase-37-09 baseline lines, preserved verbatim (for the record)

Read directly from git history at this plan's own creation commit (`ac8a582`), BEFORE any Task 1/2/3
edit -- so the original state remains recoverable from this record even though the golden itself has
moved on:

**`tests/fixtures/inline_math_pdf_text_mitex.golden.txt`, line 19 (pre-fix):**
```
math_inline_default Type: 𝑥  Default: The value of 𝑥 computed inline
```

**`tests/fixtures/inline_math_pdf_text_native.golden.txt`, line 19 (pre-fix):**
```
math_inline_default Type: 𝑥  Default: The value of 𝑥 computed inline
```

**Both, after this plan (line 19 becomes two lines, 19-20):**
```
math_inline_default
Type: 𝑥  Default: The value of 𝑥 computed inline
```

### 4.4 Commit message statement

Both golden updates were committed together with `tests/test_signature_page_boundary_render_gate.py`'s
re-pin in commit `76324bf`'s message body is about the wrapper fix itself; the goldens' own change is
recorded here and in this plan's `SUMMARY.md` as explicitly **Phase-37-induced signature typography
(the `block()` wrapper becoming a genuine block-level element), NOT a MATH-02 regression** -- the
MATH-02 fix (Phase 34/36) is untouched by this plan, and its own invariance claim (no *other* line in
either extracted-text document moved) still holds, verified by the diffs in section 4.1 above showing
zero incidental changes.

### 4.5 Byte-exact match confirmation

Each edited golden file was diffed against a fresh `pypdf`-extracted text file from a real rebuild of
the fixture under the final translator state, confirming zero divergence:

```
$ diff tests/fixtures/inline_math_pdf_text_mitex.golden.txt <fresh-extraction>
(empty -- identical)
$ diff tests/fixtures/inline_math_pdf_text_native.golden.txt <fresh-extraction>
(empty -- identical)
```

### 4.6 Task 3 verification

```
$ uv run pytest tests/test_inline_math_after_text_render_gate.py -q
3 passed in 1.29s
```

---

## 5. Final whole-suite result, by node-id set difference (never by count)

### 5.1 Starting state (section 1, reproduced here for the diff)

```
1 failed, 685 passed, 1 skipped
FAILED tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_block_math_pdf_text_is_invariant_across_the_math02_fix
```

### 5.2 Final state

```
$ uv run pytest -q --tb=no -rf
686 passed, 1 skipped in 61.27s (0:01:01)
```

### 5.3 Set difference

**Flipped RED -> GREEN by this plan (exactly 1 node id):**

```
tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_block_math_pdf_text_is_invariant_across_the_math02_fix
```

**No other node id changed state.** Arithmetic: 1 (baseline failed) - 1 (flipped) + 0 (new failures)
= 0 failed. 685 (baseline passed) + 1 (flipped) = 686 passed. Matches the measured `686 passed, 1
skipped` exactly. This is the first point in Phase 37 where the whole suite is fully green -- the
phase's own exit condition for `37-08`.

### 5.4 Named falsifiers, explicitly re-verified GREEN

```
$ uv run pytest tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate -v
test_sig08_exact_break_count_after_fix PASSED
test_sig08_no_adjacent_break_statements_anywhere PASSED
test_sig08_content_follows_nested_member_stays_separated PASSED
test_sig08_sibling_bodyless_control_keeps_one_break PASSED

$ uv run pytest \
    "tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorPdfGate::test_d11_nested_optional_control_unchanged" \
    "tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorStructuralGate::test_d11_explicit_concatenation_non_regression" \
    tests/test_desc_bodyless_concat_render_gate.py -v
test_d11_nested_optional_control_unchanged PASSED
test_d11_explicit_concatenation_non_regression PASSED
test_typstpdf_bodyless_desc_siblings_get_parbreak_and_produce_pdf PASSED

$ uv run pytest \
    "tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_control_widest_segment_fits_column_before_and_after" \
    "tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_column_width_sanity" \
    "tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_fixture_identifier_is_synthetic_and_over_length" \
    "tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_two_page_precondition_guard" \
    "tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_page_count_does_not_inflate" -v
test_control_widest_segment_fits_column_before_and_after PASSED
test_column_width_sanity PASSED
test_fixture_identifier_is_synthetic_and_over_length PASSED
test_two_page_precondition_guard PASSED
test_page_count_does_not_inflate PASSED
```

Every falsifier named in the wave-state brief is GREEN.

### 5.5 Lint/type trio

```
$ uv run black --check .
All done! (183 files would be left unchanged.)

$ uv run ruff check .
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```

### 5.6 Visual re-check summary

Both fixtures named in `37-SPACING-FINDING.md` (`signature_typography_gate`,
`signature_break_and_arrow_gate`) and the `inline_math_after_text_render_gate` confval fixture were
rasterised via real `typst.compile(format="png", ppi=140)` against the final translator state and
visually inspected (section 2.1, section 4.2). No signature's glyphs overlap the first line of its
own description body on any page of any fixture.

---

## 6. Files touched by this plan

| File | Task | Commit |
|---|---|---|
| `.planning/phases/37-signature-typography-the-desc-family/37-EMISSION-CONTRACT.md` | 1 | `626a4d7` |
| `typsphinx/translator.py` | 2 | `76324bf` |
| `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | 2 | `76324bf` |
| `tests/test_signature_page_boundary_render_gate.py` | 2 | `76324bf` |
| `tests/test_signature_typography_gate.py` | 2 | `76324bf` |
| `tests/test_translator.py` | 2 | `76324bf` |
| `tests/fixtures/inline_math_pdf_text_mitex.golden.txt` | 3 | (this plan's remaining commit) |
| `tests/fixtures/inline_math_pdf_text_native.golden.txt` | 3 | (this plan's remaining commit) |
| `.planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE-09.md` | 3 | (this plan's remaining commit) |

---

*Phase: 37-signature-typography-the-desc-family*
*Plan: 09 (gap closure, wave 5)*
*Evidence recorded: 2026-08-01*
