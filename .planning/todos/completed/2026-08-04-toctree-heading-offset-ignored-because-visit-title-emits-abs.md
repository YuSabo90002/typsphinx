---
created: 2026-08-04T02:42:12.761Z
title: "`set heading(offset: 1)` is ignored because visit_title emits an absolute `level:` — switch to `depth:`"
area: translator
severity: major
files:
  - typsphinx/translator.py:800-809
  - typsphinx/translator.py:4761-4762
  - tests/test_translator.py:83,97
  - tests/test_topics.py:161-208
  - tests/test_toctree_requirement13.py:88-108
---

## Problem

Sphinx nests toctree'd documents one level deeper than their parent: a `#` title in
a document reached through a toctree renders as an `<h2>` under the parent's `<h1>`.
`visit_toctree` implements that by wrapping the generated `include()` calls in a
scope block carrying `set heading(offset: 1)`
(`typsphinx/translator.py:4761-4762`).

But `visit_title` emits the heading with the **absolute** `level:` parameter:

```python
emitted_level = max(1, self.section_level)
self.add_text(f"heading(level: {emitted_level}, {{")   # translator.py:800-809
```

In Typst, `level:` is the final absolute level and **overrides** the ambient
`heading(offset: ...)`; only `depth:` is relative, resolving to `offset + depth`.
So the offset the toctree carefully sets has no effect at all, and every included
document's headings render at the same level as the master's — the PDF outline is
flat instead of nested.

Verified empirically against the pinned `typst>=0.15.0,<0.16` (typst-py 0.15.0):

```typst
#{
  set heading(offset: 2)
  heading(level: 1, {text("absolute-level")})   // → level 1  (offset ignored)
  heading(depth: 1, {text("relative-depth")})   // → level 3  (offset + depth)
}
```

`typst.query(..., 'heading', field='level')` returns `[1, 3]`.

## Solution

Emit `depth:` instead of `level:` in `visit_title`, so the effective level becomes
`offset + depth` and the toctree's `set heading(offset: 1)` finally applies:

```python
self.add_text(f"heading(depth: {emitted_depth}, {{")
```

Points to work through when planning:

- **Clamp semantics change.** The existing `max(1, self.section_level)` clamp
  (D-06) exists because Typst rejects `level: 0`. `depth` is likewise `>= 1`, so a
  `max(1, ...)` clamp is still needed, but the rationale comment should be
  rewritten — it is no longer about an absolute floor.
- **`_write_template_file` / `base.typ` interaction.** Check whether the master
  template or any user template sets its own `heading(offset:)`; the master
  document itself renders at `offset: 0`, so `depth == level` there and master
  output should be byte-identical.
- **Nested toctrees.** Nested scope blocks each add `offset: 1`, so depth-relative
  headings should now compose correctly at 3+ levels — worth an integration test
  that asserts the resolved level via `typst.query(..., field='level')` rather than
  only grepping the `.typ` source.
- **Test churn.** Many tests assert the literal string `heading(level: N`
  (`tests/test_translator.py:83,97`, `tests/test_topics.py:161-208`,
  `tests/test_pdf_render_gate.py:2766`, and the golden fixture
  `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`). These encode the
  buggy contract and must be updated deliberately — per project policy, test edits
  need owner sign-off and a re-proof that the new assertions fail against the
  pre-fix commit.
- **Non-section titles.** Admonition/topic/table-caption titles return before the
  heading path, so they are unaffected; the `.. contents::` topic label is likewise
  unaffected.
