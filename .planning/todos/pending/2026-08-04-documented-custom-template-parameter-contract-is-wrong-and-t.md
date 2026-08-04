---
created: 2026-08-04T09:35:49.531Z
title: "The documented custom-template parameter contract is wrong — the documented example fails to compile"
area: docs, writer
severity: major
files:
  - docs/source/user_guide/templates.rst:144-149,187-192
  - typsphinx/writer.py:259-261
  - typsphinx/template_engine.py:511-556
  - typsphinx/templates/base.typ:39-50
  - docs/source/_typst/custom_template.typ:68-70
---

## Problem

`docs/source/user_guide/templates.rst:187-192` publishes the custom-template contract as exactly
four parameters:

> Your template function receives these parameters:
> - `title` … - `authors` … - `date` … - `body`

That is not what typsphinx passes. `typsphinx/writer.py:259-261` merges
`TemplateEngine.extract_toctree_options(self.document)` into the template parameters
**unconditionally**, so any master document containing a `toctree` also receives
`toctree_maxdepth`, `toctree_numbered` and `toctree_caption`
(`template_engine.py:548-555`). Typst rejects undeclared named arguments, and neither the
bundled `project()` (`templates/base.typ:39-50`) nor the documented example declares an
argument sink, so a template written to the published contract cannot compile.

**Reproduced end to end 2026-08-04** (Sphinx 9.1.0, typst-py 0.15.0). A minimal project whose
`_templates/custom.typ` is the `templates.rst:144-149` example verbatim, `index.rst` carrying a
`:maxdepth: 2` toctree over one child, and `typst_template = "_templates/custom.typ"`:

```
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed:
  index: Typst compilation failed: TypstError: unexpected argument: toctree_maxdepth
```

The generated `#show: project.with(…)` call contained:

```typst
#show: project.with(
  title: "Demo",
  authors: ("A",),
  date: "1.0",
  toctree_maxdepth: 2,
  toctree_numbered: false,
  toctree_caption: none,
)
```

The project's own docs build works only because the in-repo example
`docs/source/_typst/custom_template.typ:68-70` happens to declare all three toctree parameters.
A user following the published documentation gets a hard build failure with an error that names
a parameter the documentation never mentions.

Note `extract_toctree_options` returns `{}` when the document has no toctree
(`template_engine.py:531-533`), so the documented example does work for a single-document
project — which is very likely why this went unnoticed.

Also relevant: `toctree_maxdepth` is not a value a user could supply from `conf.py` at all — it is
derived from the doctree. So it is a typsphinx-owned parameter that the documentation simply never
declared, not a user-facing setting that was forgotten.

Found while discussing Phase 44.1 (TOC-01), while evaluating whether the outline depth could be
corrected by adding a template parameter. It is unrelated to TOC-01 and was deliberately kept out
of that phase. See
`.planning/phases/44.1-relative-heading-depth-for-toctree-nesting/44.1-CONTEXT.md` `<deferred>`
for the full measurement.

## Solution

TBD — the fix could go either way and the choice has a compatibility consequence worth deciding
deliberately:

1. **Fix the documentation.** Declare the three toctree parameters in
   `templates.rst:187-192` and add them to the example at `:144-149`. Cheapest, and it makes the
   published contract match shipped behaviour. Does not help templates already written against
   the documented four.
2. **Fix the passing side.** Only emit the toctree parameters when the template is known to accept
   them (e.g. only on the bundled-template path), so a four-parameter template keeps working.
   Changes behaviour for existing correct templates and adds a branch that does not exist today.
3. **Give `project()` an argument sink** (`..args`) in `templates/base.typ` and document that
   custom templates should do the same. Makes future parameter additions non-breaking, but only
   for templates that adopt it.

Whichever is chosen, note the standing consequence: **adding any new template parameter is a
breaking change** for correctly-written custom templates (verified: `unexpected argument` on a
minimal case). That constraint should be recorded wherever the template contract is documented.

A regression test is worth adding either way — build a project whose custom template declares only
the documented parameters and assert the documented contract holds.
