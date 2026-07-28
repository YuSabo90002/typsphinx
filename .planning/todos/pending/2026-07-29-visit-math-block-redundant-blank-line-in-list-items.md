---
created: 2026-07-29T00:50:46+09:00
title: Block math inside a list item emits one redundant blank line
area: translator, tests
files:
  - typsphinx/translator.py (the `visit_math_block` site carrying both separation mechanisms, around lines 4079-4088 as measured in the Phase 34 review)
  - tests/test_inline_math_after_text_render_gate.py (the exact-string assertions for Constructs E and G that would have to be re-derived once the emitted shape changes)
  - tests/test_corpus_gate.py (the full-corpus gate that has to be re-run because the emitted `.typ` shape changes across the whole corpus)
---

## Problem

`visit_math_block` (`typsphinx/translator.py:4079-4088`) carries two separation mechanisms that
stack. The pre-existing (unchanged by Phase 34) line `self.add_text("\n\n")` at line 4079
unconditionally emits two newlines after every block-math expression, in every context — top-level
and inside a list item alike — so any following sibling already has guaranteed separating
whitespace before it, regardless of any other bookkeeping. Phase 34 additionally set
`self.list_item_needs_separator = True` when `self.in_list_item` (lines 4087-4088). Because the
next sibling's own visitor (e.g. `visit_paragraph`'s `_emit_forced_break`, or `visit_bullet_list`)
independently consults that same flag and emits its own leading `"\n"` when it is `True`, the two
mechanisms stack: block math is followed by one more blank line than every other block-level
handler produces.

This is inert in Typst code mode — the compiled and visual output is unaffected, because the real
paragraph break is the `parbreak()` call, not the whitespace — so the cost is diff noise and
divergence from every other block-level visitor rather than a rendering defect. The Phase 34 review
(`.planning/phases/34-inline-math-after-text-separator-fix/34-REVIEW.md`, WR-01) reproduced this
empirically: building the fixture's Construct E (`* Text before block math.` / `.. math::` /
`Text after block math.`) emits

```
text("Text before block math.")
mitex(`E = m c^2`)


parbreak()

text("Text after block math.")
```

i.e. two blank lines between the `mitex(...)` call and the following `parbreak()`, versus exactly
one blank line everywhere else in the same document that a block-level construct is followed by a
paragraph.

This was deliberately not picked up in Phase 35 (v0.6.5 release prep) per decision D-05 in
`.planning/phases/35-v0-6-5-release-prep/35-CONTEXT.md`: the fix requires a change under
`typsphinx/`, which milestone invariant #3 forbids for v0.6.5; it changes the emitted output shape,
which forces the GATE-01 fixture's Construct E and Construct G exact-string assertions to be
re-derived and the full-corpus `-b typstpdf` gate to be re-run; and v0.6.5 is a hotfix release
where an output-shape change immediately before the tag is not worth taking. D-10 requires this
todo to be filed now precisely so that decision is a recorded deferral rather than a lost one.

## Solution

Two candidate fixes, as named in the Phase 34 review's Fix field for WR-01:

- **(a) Drop the new bookkeeping.** Remove the `if self.in_list_item:
  self.list_item_needs_separator = True` block added at lines 4087-4088 inside `visit_math_block`,
  on the grounds that the pre-existing unconditional `"\n\n"` already guarantees separation from
  any following sibling — the flag is never actually needed for correctness.
- **(b) Gate the pre-existing unconditional separator instead.** Keep the
  `list_item_needs_separator` flag, but change the pre-existing `self.add_text("\n\n")` at line
  4079 to fire only when `not self.in_list_item`, so exactly one of the two mechanisms is
  responsible for separation in each context — mirroring how `depart_paragraph` already relies
  solely on the flag inside list items, with no hardcoded trailing text of its own.

Whichever option is taken, the follow-up work is the same: re-derive the Construct E and
Construct G exact-string assertions in `tests/test_inline_math_after_text_render_gate.py` from a
fresh build on both the mitex and native emission paths, and re-run the full-corpus
`tests/test_corpus_gate.py` gate to confirm no other fixture's emitted shape regresses.
