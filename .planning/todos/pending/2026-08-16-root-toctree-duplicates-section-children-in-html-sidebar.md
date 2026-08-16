---
created: 2026-08-16T14:05:00Z
title: "The root `index.rst` lists section indexes AND their children in the same toctree, so the HTML sidebar shows Configuration / Builders / Templates twice — once nested under User Guide, once as its siblings, both pointing at the same pages"
area: docs
severity: minor
files:
  - docs/source/index.rst:41-48   # the "User Guide" toctree
  - docs/source/index.rst:50-56   # the "Examples" toctree, same shape
  - docs/source/user_guide/index.rst:6-12
  - docs/source/examples/index.rst:6-10
---

## Problem

Reported from the rendered HTML sidebar: under the `USER GUIDE` caption, `User Guide` appears as an
expandable node containing Configuration / Builders / Templates / Output Layout — and then
Configuration, Builders and Templates appear **again** as siblings of `User Guide`, linking to the
same pages.

Root cause, measured: `docs/source/index.rst` enumerates the section index **and** that section's
children in one toctree, while the section index already has a toctree over those same children.

```rst
.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/index          <- already toctrees configuration/builders/templates/output_layout
   user_guide/configuration  <- duplicate
   user_guide/builders       <- duplicate
   user_guide/templates      <- duplicate
```

`user_guide/output_layout` is **not** listed at the root, which is why it renders only once — the
asymmetry in the screenshot is the tell, not an unrelated quirk.

The `Examples` toctree (`index.rst:50-56`) has the identical shape: `examples/index` plus `basic`
plus `advanced`, where `examples/index.rst:6-10` already toctrees `basic` and `advanced`.

### Sphinx already warns about this — four times

Measured 2026-08-16 by filtering the html build's own output (these are separate from, and additional
to, the "3 warnings" summary line that the docs build prints):

```
docs/source/examples/basic.rst: document is referenced in multiple toctrees:
  ['examples/index', 'index'], selecting: index <- examples/basic
docs/source/user_guide/builders.rst: document is referenced in multiple toctrees:
  ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/builders
docs/source/user_guide/configuration.rst: ... selecting: user_guide/index <- user_guide/configuration
docs/source/user_guide/templates.rst: ... selecting: user_guide/index <- user_guide/templates
```

Note the **asymmetry in what Sphinx selects**: for the three `user_guide` pages it picks the section
index as parent, but for `examples/basic` it picks the root `index`. Whoever fixes this should not
assume a single consistent rule was in play.

## The PDF is NOT affected — verified, not assumed

This is an HTML-only defect. Phase 49's include-edge state guard already deduplicates the Typst side.
Measured on a real `sphinx-build -b typst` of this project's own docs:

The master wrapper seeds the edge set with the **selected** parent only —

```typst
#state("typsphinx:include-edges", ()).update((
  "index#0>installation", "index#0>quickstart", "index#0>user_guide/index",
  "user_guide/index#0>user_guide/configuration", "user_guide/index#0>user_guide/builders",
  "user_guide/index#0>user_guide/templates", "user_guide/index#0>user_guide/output_layout",
  "index#0>examples/index", "examples/index#0>examples/basic", "examples/index#0>examples/advanced",
  ...))
```

— and it contains **no** `"index#0>user_guide/configuration"` edge. So the include lines the root
`index.typ` emits for the duplicated children (`index.typ:107-109`) are guarded by conditions that
are always false and never fire:

```typst
if "index#0>user_guide/configuration" in state("typsphinx:include-edges", ()).get() { include("user_guide/configuration.typ") }
```

The pages are included exactly once, via `user_guide/index.typ:19-22`. **The guard mechanism is doing
its job here** — this todo is not evidence against it, and fixing `index.rst` must not be justified as
"fixing the PDF".

Two secondary observations from the same measurement, neither a defect on its own:

1. The typst builder emits dead `include(...)` lines for the duplicated entries. Harmless and by
   design (the edge encodes which parent was selected), but it is extra output that disappears once
   the source toctree is deduplicated.
2. HTML and Typst nest `examples/basic` under **different** parents — Sphinx HTML selected `index`,
   while the typst edge map recorded `examples/index#0>examples/basic`. Both render the page once, so
   nothing is broken, but the two builders' navigation trees are not identical for that page. Worth a
   look while in here; it may deserve its own todo if it turns out to be a divergence rather than a
   consequence of the duplication.

## Solution

Almost certainly: drop the redundant child entries from the root toctree and let each section index
own its own children.

```rst
.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/index
```

…and the same for `Examples`. That is the conventional Sphinx shape, silences all four warnings, and
makes the sidebar match the document hierarchy.

Before doing it, decide the intent rather than just deleting lines — the current shape may have been
an attempt to make the children visible without expanding the parent node. If flat visibility is
actually wanted, the fix is `:maxdepth:` / theme sidebar configuration (furo), not duplicate entries.

Verify with: a clean rebuild showing **zero** `referenced in multiple toctrees` warnings, plus a look
at the rendered sidebar. The four warnings are the objective gate; the sidebar is the human check.
Also re-run `sphinx-build -b typst` and confirm the dead guarded include lines are gone and each page
is still included exactly once.

## Related

- `.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md` — a docs-quality CI job. If a
  warnings-as-errors or warning-count gate is ever added there, this class of defect stops being
  something a human has to notice in a screenshot.
