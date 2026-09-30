---
created: 2026-08-05T00:00:00+09:00
title: "A document toctree'd by two masters is silently dropped from all but the first-written one — the include-dedup ledger is per-build, not per-master"
area: builder, translator
resolves_phase: 49
source: .planning/phases/44.1-relative-heading-depth-for-toctree-nesting/44.1-CONTEXT.md (deferred, defect A)
severity: high
files:
  - typsphinx/builder.py:99 (`self._included_docnames` declaration)
  - typsphinx/builder.py:420 (the reset — once per `write()`)
  - typsphinx/builder.py:432 (the single `sorted(docnames)` write loop — no per-master pass)
  - typsphinx/translator.py:4776-4785 (`visit_toctree`'s dedup against that ledger)
  - tests/ (new gate: two masters sharing a toctree'd document)
---

## Problem

When `typst_documents` declares two or more masters and a document appears in the toctree of more
than one of them, the document is `#include()`d into **only the master whose parent document was
written first**, and silently vanishes from every other master's PDF. `-b typst` exits 0 with no
warning. Which master loses content is decided by docname sort order.

Measured 2026-08-05 on the current tree.

```python
# conf.py
typst_documents = [
    ("index",   "index",   "Master A", "A"),
    ("bmaster", "bmaster", "Master B", "A"),
]
```

`index.rst` and `bmaster.rst` each carry a `toctree` listing `shared`. Emitted output:

```typst
// bmaster.typ  (written first — sorted order)   // index.typ  (written second)
{                                                {
  set heading(offset: 1)                           set heading(offset: 1)
  include("shared.typ")                          }        ← no include() at all
}
```

Master A's document loses `shared` entirely. The only build warning emitted was an unrelated
`toc.not_included`.

The same mechanism was observed in a three-document chain: with masters `amaster` (toctree →
`shared`) and `bmaster` (toctree → `mid` → `shared`), `amaster` is written first and consumes
`shared`, leaving `mid.typ` with an empty offset scope and no include.

## Root cause

`builder.py:99` declares `self._included_docnames: set[str]` and `builder.py:420` resets it **once
per `write()`**. `write()` then iterates `sorted(docnames)` a single time (`builder.py:432`) and
calls `write_doc()` per docname — there is no per-master pass, because a document's `.typ` is emitted
once and shared by every master that includes it. `visit_toctree` (`translator.py:4776-4785`) dedups
each toctree entry against that one ledger, so the ledger spans **the whole build** rather than one
master's include graph.

The ledger's own docstring states the intent as "spans every document composing one master -- not
just this one toctree". The intent is right; the reset scope does not implement it.

The ledger's purpose is sound and must not simply be removed: Typst's `#include()` flattens each file
inline, so including one `.typ` twice re-emits every `<label>` it defines and the compile aborts with
`label ... occurs multiple times`.

## Direction (undecided)

The ledger has to become per-master, which means the writer needs to know **which master's context it
is emitting for** — a notion that does not exist in the current write loop, since one `.typ` serves
all masters. Options seen so far, none evaluated:

- Compute per-master include sets up front (the machinery already exists —
  `_compute_master_included_docnames()` at `builder.py:118` walks `env.toctree_includes` from every
  master) and have `visit_toctree` dedup against the set for the master currently being composed.
  Requires a per-master notion in the write loop.
- Detect the condition and **warn** rather than fix, as a stopgap: a document reachable from more than
  one master is exactly what `_compute_master_included_docnames()` could report. This does not restore
  the lost content but converts a silent failure into a loud one, and is cheap enough for a patch
  release if the real fix is not.
- Resolve it structurally by composing at the doctree layer instead of via `#include()` — see the
  architectural note in `44.1-CONTEXT.md` `<deferred>`. That removes the shared-file premise entirely
  but is a v0.8.0-class change.

Related: [[.planning/phases/44.1-relative-heading-depth-for-toctree-nesting/44.1-CONTEXT.md]]
`<deferred>` defect A. Distinct from
`2026-08-04-duplicate-typst-documents-target-silently-drops-a-master.md`, which is about two masters
resolving to the same *target filename*; this one is about a *shared child document* and a different
mechanism, though both are in the "silent document loss" class.
</content>
