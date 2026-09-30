---
created: 2026-08-29
title: "An inline image inside a paragraph is emitted with no separator before `image(...)`, so Typst aborts the whole compile with `expected semicolon or line break` and no PDF is produced"
area: translator
severity: blocker
resolves_phase: 62
source: owner report 2026-08-29 ("par(image(...)) になるパターンが存在するっぽい / typst
  によってエラーが出て画像が出力されない"), reproduced and root-caused during capture
files:

  - typsphinx/translator.py:4718  # visit_image() -- emits `image("...")` with no preceding separator
  - typsphinx/translator.py:4768  # depart_image() -- emits the trailing "\n\n" that saves the FOLLOWING boundary only

audit_acknowledged:
  milestone: v0.9.1
  at: 2026-08-29

closed: 2026-08-30
closed_by: "Phase 62 plan 03, Task 3"
status: resolved
---

## Problem

Any image node that is **not** the first thing in its paragraph is emitted directly
adjacent to the preceding code-mode expression, on the same line. Typst then refuses to
parse the file.

### Reproduction (measured 2026-08-29, main-tree `.venv`)

`index.rst`:

```rst
Title
=====

.. |sub| image:: img.png

Inline substitution |sub| in a sentence.
```

`sphinx-build -b typst` succeeds and emits (`index.typ`):

```typst
par({text("Inline substitution ")image("img.png")

text(" in a sentence.")})
```

`text("Inline substitution ")` and `image("img.png")` are two juxtaposed code-mode
expressions **on one line with nothing between them** -- the same `})par(` / `]par(`
class the translator already guards against elsewhere (see the comments at
`translator.py:636`, `:976`, `:4838`), but the inline-image boundary is not covered.

Compiling that file:

```
TypstError: expected semicolon or line break
```

And `sphinx-build -b typstpdf` does not degrade -- it dies outright:

```
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed:
  index: Typst compilation failed: TypstError: expected semicolon or line break
```

No PDF is written for **any** master document in the project, not just the offending one.

### Root cause is the PRECEDING boundary only

Inserting a single `\n` before `image(` makes the identical document compile cleanly
(verified: `as-emitted: FAIL expected semicolon or line break` → `with line break: OK`).

`depart_image()` already emits `"\n\n"` when not in a figure, which is why the boundary
*after* the image is safe. `visit_image()` emits nothing before it, which is why the
boundary *before* it is not.

### Trigger matrix (measured)

| shape | emitted | compiles |
|---|---|---|
| `\|sub\| leading image then text.` | `par({image("img.png")` then newline | **yes** |
| `Inline substitution \|sub\| in a sentence.` | `par({text("…")image("img.png")` | **no** |
| `Two in a row \|sub\| \|sub\| here.` | `text(" ")image("img.png")` | **no** |
| `- item with \|sub\| inline` (list item) | `text("item with ")image("img.png")` | **no** |
| standalone `.. image::` (block level) | own line | yes |
| `.. figure::` | `  image("…"),` inside `figure(` | yes |

So the trigger is: **an image node preceded by any sibling content in the same paragraph
or list item.** The image being at the start of its paragraph is the only safe inline
position, which is why this has gone unnoticed -- the project's own docs never place a
substitution image mid-sentence.

## Solution

In `visit_image()`, emit a separator before `image(` when the current output does not
already end at a line boundary -- i.e. mirror what the surrounding inline emitters
(`visit_Text`, `visit_emphasis`, `visit_literal`, …) already do for the same juxtaposition
hazard. The existing `list_item_needs_separator` / newline-before-sibling machinery around
`translator.py:887` (`add_text`) and `:4838` is the precedent to follow rather than a
bare unconditional `"\n"`, because a leading `\n` right after `par({` would be harmless
but a `\n` inside `figure(` -- where `visit_image` indents with two spaces -- must stay
suppressed.

Regression tests should cover all four failing shapes in the trigger matrix above, and
should assert on a real Typst compile (not only on the emitted string), since the string
looks plausible and only the parser rejects it.

## Resolution (Phase 62)

**Closed against the EXTENDED 16-shape matrix, not this record's original 4-row trigger
matrix above.** Live measurement during Phase 62 planning and execution found the actual
trigger surface substantially larger than this todo's own reproduction: **16 measured
failing shapes** (`.planning/research/FEATURES.md` § Q1, each given its own fixture document
and its own `typst_documents` master under
`tests/fixtures/inline_image_separator_render_gate/`), plus the image-free `index.rst` root
master, which fails only transitively because Typst's `#include()` re-parses a poisoned
content file:

- `fail_01_sub_mid_sentence`
- `fail_02_two_subs_adjacent`
- `fail_03_sub_in_list_item`
- `fail_04_block_image_second_in_list_item`
- `fail_05_image_in_table_cell`
- `fail_06_image_in_definition_list_body`
- `fail_07_image_in_admonition`
- `fail_08_image_in_footnote_body`
- `fail_09_image_in_legend_mid_text`
- `fail_10_two_images_in_legend`
- `fail_11_image_after_inline_literal`
- `fail_12_image_after_emphasis`
- `fail_13_image_after_reference`
- `fail_14_image_in_field_list_body`
- `fail_15_image_in_section_title`
- `fail_16_image_with_width_mid_sentence`

**One fix closed all sixteen, plus the image-free root master.** The gate proved this on a
real `sphinx-build -b typstpdf` build over all 18 masters in one invocation: 17 refused
(`index` + the 16 `fail_*` docnames above) against the unfixed tree, all 17 compile
post-fix, and none of the 9 must-keep-passing shapes regressed.

**The 9 must-keep-passing shapes and the single measured delta.** `pass_a_standalone_block_image`,
`pass_b_figure_with_caption`, `pass_c_image_first_in_paragraph`,
`pass_d_image_with_dimensions_and_scale_align`, `pass_e_image_with_propagated_target_id`,
`pass_f_figure_with_plain_legend`, `pass_g_figure_in_list_item_after_paragraph`,
`pass_h_figure_first_in_list_item`, `pass_i_bare_image_first_in_list_item`. Eight of the
nine are byte-identical before and after the fix. The ninth, `pass_c_image_first_in_paragraph`
(an image FIRST in its paragraph, followed by text), gains exactly one empty line between
the image and the following text -- because the leading separator call now marks the
paragraph as having content, so the following text node emits its own separator, the same
boundary shape every other inline emitter already produces. This delta is pinned exactly
(not waived) by two committed goldens (`goldens/pass_c_image_first_in_paragraph.pre_fix.typ`
and `goldens/pass_c_image_first_in_paragraph.typ`) and a dedicated assertion that the diff
between them is exactly one added empty line, zero removed lines.

**The mechanism actually shipped** is this todo's own suggested precedent -- the
`list_item_needs_separator` / newline-before-sibling triad `visit_Text` and four other
emitters already use (`_add_paragraph_separator()` + `_emit_inline_concat_separator()` +
`in_list_item`/`list_item_needs_separator`) -- but its SCOPE is AMENDED from what planning
first recommended. The originally-recommended placement confined the triad's leading half to
`visit_image()`'s non-`in_figure` (`else`) branch only. **Measured insufficient**: that
placement left 3 of the 16 failing shapes still refused --

- `fail_09_image_in_legend_mid_text` and `fail_10_two_images_in_legend` -- an image inside a
  figure's legend has `self.in_figure == True`, so it takes the `if self.in_figure:` branch,
  which an else-only placement never reaches. `visit_legend()` already sets
  `in_list_item`/`list_item_needs_separator` for exactly this purpose; the image simply never
  consulted them.
- `fail_14_image_in_field_list_body` -- a concat context (`:Returns:` field-list body). The
  leading half alone was not the problem here; `depart_image()`'s unconditional trailing two
  newlines broke the concat expression with a NEW refusal the unfixed tree never produced,
  `cannot apply unary '+' to content`.

The shipped mechanism therefore hoists the triad's leading half to run on BOTH the
`in_figure` and non-`in_figure` paths (closing the two legend shapes), and makes
`depart_image()`'s trailing bookkeeping concat-aware -- it consults
`_mark_inline_concat_content()` before the unconditional trailing newlines, so a field-list-
body concat context is not broken (closing the field-list shape). Both `in_figure` branch
BODIES stay textually unmodified; the net product diff over `typsphinx/translator.py` is a
pure 9-line insertion, 0 deletions, 0 modified lines.

**Gate module and fixture paths:**
`tests/test_inline_image_separator_render_gate.py` (`TestInlineImageSeparatorFullMatrix`,
`TestInlineImageSeparatorFailShapes`, `TestInlineImageSeparatorGoldens`) and
`tests/fixtures/inline_image_separator_render_gate/` (27 `.rst` documents, 18
`typst_documents` masters, `goldens/` with 10 committed `.typ` files).

**RED transcript:** see
`.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-RED-EVIDENCE.md`
for the full verbatim aggregate `ExtensionError` recorded against a genuinely restored unfixed
`typsphinx/translator.py`, the `pass_parent` positive control, and the golden-capture
provenance.
