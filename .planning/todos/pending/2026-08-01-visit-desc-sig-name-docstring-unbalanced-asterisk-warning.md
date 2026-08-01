---
created: 2026-08-01T00:00:00+09:00
title: "`visit_desc_sig_name`'s docstring has an unbalanced `*` that emits a docutils warning and a stray `problematic` node in the API reference docs"
area: translator, docs
resolves_phase: null
source: .planning/phases/37-signature-typography-the-desc-family/37-08-PLAN.md Task 1 (`tox -e docs-pdf` output)
files:
  - typsphinx/translator.py (`visit_desc_sig_name`'s docstring, the phrase "PyTypeObject *type, no intersphinx")
---

## Problem

Discovered running `tox -e docs-pdf` during Phase 37's closeout (37-08 Task 1). The docs build
emits:

```
typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_desc_sig_name:33:
WARNING: Inline emphasis start-string without end-string. [docutils]
```

Root cause: the docstring (added in plan `37-06`, extended in `37-09`) contains the phrase
`"unresolved-C-domain-type measurement (PyTypeObject *type, no intersphinx)"`. The single `*`
before `type` is parsed by docutils/Sphinx as an unterminated inline-emphasis start marker when
the docstring is rendered as reStructuredText via autodoc.

This is not purely cosmetic: the docs build's own log additionally shows

```
WARNING: unknown node type: <problematic ids="id2" refid="id1">*</problematic>
```

during `writing output... [api/index]` — docutils inserts a `problematic` node for the unmatched
`*`, and typsphinx's translator has no handler for it, so the literal `*` renders ungracefully
(dropped/garbled) in the project's own `docs/_build/pdf/typsphinx.pdf` API reference page for this
method.

## Solution

Escape the asterisk in the docstring, e.g. `PyTypeObject \*type` or rephrase to avoid a bare `*`
(``PyTypeObject`` followed by a pointer parameter named `type`, with no intersphinx configured).
Verify with `tox -e docs-pdf` that both the docutils warning and the `problematic` node disappear,
and that `uv run pytest -m "not slow" -q` stays green (no test asserts on this docstring's exact
text).

Out of scope for `37-08` (the phase-closeout plan): `typsphinx/translator.py` is not in that plan's
`files_modified`, and this warning does not gate any Phase 37 requirement (SIG-01..09) — it is a
docs-build hygiene nit discovered incidentally while running `tox -e docs-pdf` as part of Task 1's
gate sweep.
