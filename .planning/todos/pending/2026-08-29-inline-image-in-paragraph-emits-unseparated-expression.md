---
created: 2026-08-29
title: "An inline image inside a paragraph is emitted with no separator before `image(...)`, so Typst aborts the whole compile with `expected semicolon or line break` and no PDF is produced"
area: translator
severity: blocker
source: owner report 2026-08-29 ("par(image(...)) になるパターンが存在するっぽい / typst
  によってエラーが出て画像が出力されない"), reproduced and root-caused during capture
files:
  - typsphinx/translator.py:4718  # visit_image() -- emits `image("...")` with no preceding separator
  - typsphinx/translator.py:4768  # depart_image() -- emits the trailing "\n\n" that saves the FOLLOWING boundary only
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
