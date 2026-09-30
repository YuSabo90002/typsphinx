---
phase: 36-shared-emission-seam-cleanup
reviewed: 2026-08-01T00:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - tests/fixtures/desc_rubric_decoupling_render_gate/conf.py
  - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
  - tests/fixtures/desc_rubric_decoupling_render_gate/index.rst
  - tests/fixtures/inline_math_after_text_render_gate/index.rst
  - tests/fixtures/inline_math_pdf_text_mitex.golden.txt
  - tests/fixtures/inline_math_pdf_text_native.golden.txt
  - tests/test_desc_rubric_decoupling_render_gate.py
  - tests/test_inline_math_after_text_render_gate.py
  - typsphinx/translator.py
findings:
  critical: 0
  warning: 1
  info: 1
  total: 2
status: issues_found
---

# Phase 36: Code Review Report

**Reviewed:** 2026-08-01T00:00:00Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Phase 36 makes two changes to `typsphinx/translator.py`: (1) `visit_desc_signature`/
`depart_desc_signature` and `visit_rubric`/`depart_rubric` no longer delegate to
`visit_strong`/`depart_strong` via a dummy `nodes.strong()` node — each now carries a
verbatim inline copy of that body (D-01, intentional triplication); (2) `visit_math_block`
now clears `list_item_needs_separator` (was: sets it to `True`) after emitting its own
unconditional `"\n\n"` trailing separator (MATH-02).

I diffed each of the three inlined copies against `visit_strong`/`depart_strong` character
by character (via `git diff` against the pre-phase commit) and they are byte-identical —
no unintended divergence between the three copies was found. I traced `visit_math_block`'s
`list_item_needs_separator` state through the plain, `:label:`-anchored, and
single-element-in-list-item paths (Constructs E/G/H in the render-gate fixture) against
both the mitex and native math emission branches; `False` is correct on every path reached,
including the `:label:` path where `_emit_id_anchors` arms the flag before the math is
emitted — the unconditional clear after the trailing `"\n\n"` correctly overwrites that
pre-armed state. `test_block_math_pdf_text_is_invariant_across_the_math02_fix` independently
confirms the fix is byte-for-byte PDF-text-inert against a pre-fix baseline. SC#1 (AST-based
`test_desc_signature_and_rubric_do_not_delegate_to_visit_strong`) and SC#2
(golden-file byte-equality `test_emitted_typ_is_byte_identical_to_golden`) both exercise
real, non-tautological assertions — `golden.typ` was captured in a commit (`b37ea40`)
that precedes the actual decoupling edits (`8708ab0`/`12547a2`), confirmed via `git log`,
so SC#2 is a genuine regression guard, not a self-referential check. All 6 new/changed
tests pass locally; `black`/`ruff` are clean on the changed files.

One test-quality issue is worth flagging (WARNING) — the two PDF-text invariance
baselines (`inline_math_pdf_text_mitex.golden.txt` / `inline_math_pdf_text_native.golden.txt`)
are byte-for-byte identical to each other, which is never stated or asserted anywhere,
so the double-baseline structure is silently indistinguishable from a single shared one.

## Warnings

### WR-01: Mitex and native PDF-text invariance baselines are byte-identical but never asserted or documented as such

**File:** `tests/fixtures/inline_math_pdf_text_mitex.golden.txt`, `tests/fixtures/inline_math_pdf_text_native.golden.txt`

**Issue:** `diff` shows the two files are byte-for-byte identical (both math renderer paths
apparently extract the same PDF text via pypdf, plausibly because mitex transpiles LaTeX to
native Typst math AST before the same math typesetter runs). `test_block_math_pdf_text_is_invariant_across_the_math02_fix`
(`tests/test_inline_math_after_text_render_gate.py:496-556`) treats them as two independent,
per-path baselines captured separately in Task 1 ("captured once in Task 1 from the UNFIXED
translator"), but nothing in the test or the fixture headers documents — or asserts — that
this identity is expected. As written, the double-baseline design provides no more
discriminating power than a single shared golden file would: if `PDF_TEXT_BASELINE_NATIVE`
were accidentally pointed at the mitex file's content (or vice versa) during a future edit,
this test would not catch the mistake, silently weakening the "before/after the fix, per
path" invariance guarantee the test's own docstring (D-04) claims to provide.

**Fix:** Either (a) add a short comment atop the two golden files (or in the test) noting
that mitex and native paths are expected to extract identical PDF text because both route
through the same underlying Typst math typesetter, or (b) collapse the two files into one
shared `PDF_TEXT_BASELINE` constant used for both loop iterations, making the intentional
identity explicit in code rather than an unstated coincidence:
```python
PDF_TEXT_BASELINE = (
    Path(__file__).parent / "fixtures" / "inline_math_pdf_text.golden.txt"
)
...
for label, extra_args in (("mitex", ()), ("native", ("-D", "typst_use_mitex=0"))):
    ...
    baseline_text = PDF_TEXT_BASELINE.read_text(encoding="utf-8")
```

## Info

### IN-01: `dummy_strong_count == 2` assertion is a whole-file substring count, fragile to future docstring text

**File:** `tests/test_desc_rubric_decoupling_render_gate.py:228-239`

**Issue:** `dummy_strong_count = source_text.count(DUMMY_STRONG_LITERAL)` counts raw
occurrences of the string `"dummy_strong = nodes.strong()"` anywhere in
`typsphinx/translator.py`, including inside docstrings/comments, not just executable
statements. Currently this is safe (exactly 2 real occurrences, both in
`visit_literal_strong`/`depart_literal_strong`, confirmed via `grep`), but a future
docstring that quotes the exact literal (e.g. while documenting the historical delegation
pattern, as this phase's own docstrings come close to doing) would silently inflate the
count and fail the assertion for a reason unrelated to actual delegation behavior.

**Fix:** Not urgent given the current file content, but an AST-based check (reusing
`_delegating_calls_in`'s walk, checking for an `ast.Assign` to a `nodes.strong()` call
inside the two `literal_strong` functions specifically) would be robust to future comment
text. Low priority since assertion (a)/(b) in the same test already cover the functional
delegation requirement independently.

---

_Reviewed: 2026-08-01T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
