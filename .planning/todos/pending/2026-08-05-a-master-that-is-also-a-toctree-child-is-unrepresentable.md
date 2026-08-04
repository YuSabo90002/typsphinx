---
created: 2026-08-05T00:00:00+09:00
title: "A master listed in typst_documents that is also another master's toctree child does not compile, and would re-expand its template mid-body if it did"
area: builder, writer
source: .planning/phases/44.1-relative-heading-depth-for-toctree-nesting/44.1-CONTEXT.md (deferred, defects B-1 / B-2)
severity: major
files:
  - typsphinx/writer.py:39-71 (`_is_master_document` — the exclusive master/included binary)
  - typsphinx/builder.py:156- (`_resolve_output_stem` — masters are named by their target, not their docname)
  - typsphinx/translator.py (`_compute_relative_include_path` — the include path is derived from the docname)
  - tests/ (new gate: a sub-master reached from a root master's toctree)
---

## Problem

Listing a document in `typst_documents` **and** reaching it from another master's `toctree` is a
configuration a user can plausibly write — "build the whole manual, and also build the guide chapter
as its own PDF". It is broken in two layers.

Measured 2026-08-05 on the current tree, with:

```python
typst_documents = [
    ("index",       "index",        "Root Master",  "A"),
    ("guide/index", "guide_master", "Guide Master", "A"),
]
```

and `index.rst` carrying a `toctree` listing `guide/index`.

### B-1 — hard compile failure: the include path and the output filename disagree

The parent emits the include from the **docname**:

```typst
// index.typ
include("guide/index.typ")
```

but `_resolve_output_stem` names a master's file from its **target** entry, so the file on disk is
`guide/guide_master.typ`. No `guide/index.typ` is ever written. Result:

```
RuntimeError: failed to compile document:
  file not found (searched at .../out/guide/index.typ)
```

Loud, so less dangerous than a silent drop — but the root master cannot be built at all.

### B-2 — with B-1 worked around, the included master re-expands its template into the body

Copying the file to the name the parent expects and querying the root master's resolved heading
levels (with the Phase 44.1 relative-depth/offset repair applied, so the nesting itself is correct):

```
index.typ [1 ·, 1 'Contents', 1 'Root Master Title',
           2 ·, 2 'Contents', 2 'Guide Master Title',   ← second title-page heading + second #outline()
           3 'Page One', 4 'Sub of page one', 3 'Shared Doc', 4 'Shared sub',
           2 'Shared Doc', 3 'Shared sub']              ← plus a duplicate of shared
```

The heading levels nest correctly, so **this is not a heading-offset problem**. The sub-master's
`.typ` carries `#import "../_template.typ": project` and `#show: project.with(...)` because
`writer.py` applies the full template to any document `_is_master_document()` returns true for. When
that file is `#include()`d, the template's title page and `#outline()` are re-emitted in the middle
of the parent's body.

(The trailing duplicate `Shared Doc` is the per-build dedup ledger interacting with two masters — see
`2026-08-05-shared-document-silently-dropped-from-all-but-first-master.md`.)

## Root cause

`writer.py:39-71` `_is_master_document()` treats *master* and *included* as an exclusive binary and
selects the output shape from it: masters get the template, included documents get only the minimal
`@preview` imports. The state "master **and** another master's child" has no representation. One
`.typ` file would have to be simultaneously a self-contained document (template applied, renders
standalone) and a body fragment (no template, safe to inline) — which a single file cannot be.

B-1 is the same premise showing up in the filename layer: one file needs two names, its standalone
target name and the docname-derived name its parent includes.

## Direction (undecided)

Options seen, none evaluated:

- **Emit two files** for such a document — a templated standalone one at the target name and an
  untemplated fragment at the docname — at the cost of doubling output for that document and deciding
  which one `#include()` refers to.
- **Make the template application conditional at Typst level**, so one file can suppress it when
  included. Needs a mechanism the current template contract does not have, and any new template
  parameter is a breaking change for correctly-written custom templates (see the custom-template
  contract item in `44.1-CONTEXT.md` `<deferred>`, roadmapped as Phase 45.1).
- **Reject the configuration explicitly** with a clear error naming both entries, rather than failing
  with a `file not found` from Typst. Cheapest, and strictly better than today even if the feature is
  later supported.
- **Compose at the doctree layer**, where each master's traversal expands the sub-master's content
  independently and the binary disappears — see the architectural note in `44.1-CONTEXT.md`
  `<deferred>`. v0.8.0-class.

Related: [[.planning/phases/44.1-relative-heading-depth-for-toctree-nesting/44.1-CONTEXT.md]]
`<deferred>` defects B-1 / B-2.
</content>
