# Phase 49: Per-Master Include Graph with State-Guarded Includes - Research

**Researched:** 2026-08-14
**Domain:** Typst `state`/`context` compile-time-resolved per-master include selection, replacing a
build-scoped Python dedup ledger; mirroring Sphinx's own `inline_all_toctrees` document-order DFS.
**Confidence:** HIGH — every load-bearing claim in this document was verified this session either by
reading the cited source lines directly (Sphinx's `util/nodes.py`, `directives/other.py`,
`environment/collectors/toctree.py`, `environment/adapters/toctree.py`, `domains/std/__init__.py`, and
this repo's `translator.py`/`builder.py`/`writer.py`) or by a real `typst.compile()`/`typst.query()` /
`sphinx-build` invocation. No claim in Standard Stack, Architecture Patterns, or Common Pitfalls rests
on training-data memory alone.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** If the `:numref:` measurement shows divergence, it is recorded as a documented limitation
  and handed forward to Phase 51 (docs) and Phase 52 (CHANGELOG) — not fixed in this phase.
  Reversibility: reversible.
- **D-02:** If the full-corpus `state`/`context` multi-pass convergence fails, the phase **stops and
  escalates to the owner** — no partial write-time fallback is available. Reversibility: reversible as
  a process rule, but can block the milestone by design.
- **D-03:** Both the builder-side traversal and the translator-side emission iterate
  `toctreenode['includefiles']`, **not** `node['entries']`. Reversibility: reversible.
- **D-04:** The guard key must be **unique per emission site within its parent document**, not a bare
  `"<parent>><child>"` docname pair. Reversibility: costly (lockstep across corpus).
- **D-05:** Edge keys are produced by **one shared function**, called by both the builder's graph
  computation and the translator's guard emission, with a test asserting the two sides agree.
  Reversibility: reversible, but a mismatch fails silently (content vanishes with no compile error).
- **D-06:** Degenerate graph shapes take Sphinx's own outcome, decided here rather than discovered as a
  test failure (SC#2): 2-node cycle and self-reference → child skipped; `self`/external-URL entries →
  skipped silently, no new warning; `:glob:` toctree → no special handling needed; `:orphan:` document
  referenced but not toctree'd → not included, cross-reference degrades to text via Phase 48's guard;
  ≥3 masters sharing ≥2 overlapping children → same algorithm, no special case.
- **D-07:** The Typst `state` key is **namespaced**, not the bare `"inc"` sketched in PROJECT.md.
  Reversibility: costly. Exact string is Claude's discretion.
- **D-08:** The heading-offset emission is unchanged — one `set heading(offset: heading.offset + 1)`
  per toctree, inside the `context` block, guard **inside** that block. Reversibility: reversible.
- **D-09:** The `#state(<key>, ()).update((...))` / `if <key> in state(<key>, ()).get()` syntax was
  **unmeasured** at CONTEXT time and required verification against a real `typst.compile()` before any
  plan depends on it. **This research closes D-09 — see Architecture Patterns Pattern 1 and Common
  Pitfalls 1-2 for the verified snippets and measured hazards.**
- **D-10:** The `self`/external-URL compile fatal (D-03) closes **inside this phase** with its own
  GATE-01 fixture and pre-fix RED, not as a separate todo.

### Claude's Discretion

- The exact spelling of the edge key (D-04) and of the namespaced `state` key (D-07), provided
  uniqueness-per-emission-site and one-shared-derivation (D-05) hold.
- Whether the builder's traversal walks `env.get_doctree()` doctrees or reads `env.toctree_includes`,
  provided the result is identical to `inline_all_toctrees`'s selection and the emission side derives
  its keys through D-05's shared function. **Research finding: `env.toctree_includes` is the correct,
  lower-cost choice — see Architecture Patterns Pattern 2.**
- Where the shared key-derivation function lives and what it is named.
- Whether the pre-fix REDs are recorded as `xfail(strict=True)` or as a separately-committed evidence
  transcript.
- The internal structure of the published state value (array vs. other membership-testable form), as
  long as D-09's syntax is verified and corpus-scale membership testing stays sane.

### Deferred Ideas (OUT OF SCOPE)

- The PR #131 image path defects (Phase 50).
- Documenting the two-layer output shape and any `:numref:` limitation this phase records (Phase 51).
- The v0.8.0 CHANGELOG entry (Phase 52).
- Replacing Phase 48's `query(<L>).len() > 0` guard with a `state` lookup — Phase 48 D-11 measured the
  **bottom** cost tier, so no coupling obligation to this phase exists.

</user_constraints>

## Summary

This phase deletes a build-scoped Python `set` (`builder._included_docnames`, a single flat ledger
shared across every master in one build) and replaces it with a Typst compile-time mechanism: each
wrapper publishes its own master's include edge set as `#state(<ns>, ()).update((...))`, and each
content file's `visit_toctree` emits a **static, unconditional** `context { ... if <key> in
state(<ns>, ()).get() { include(...) } }` guard per toctree entry — the same content file's bytes are
therefore identical everywhere, and it is the **wrapper**, not the file, that decides which of a
file's own guards fire for that particular compile. This is what makes one shared content file behave
correctly for every master (the diamond) while keeping document-order interleaving (prose stays where
it was written) and heading depth relative (no DFS-depth arithmetic needed anywhere).

This research closes D-09, the phase's single named "unmeasured, load-bearing" risk, with seven
independent real `typst.compile()`/`typst.query()` runs this session (Architecture Patterns Pattern 1,
Common Pitfalls 1-2, Code Examples). The most consequential new finding beyond what CONTEXT.md/
PROJECT.md already recorded: **omitting the one-element array's trailing comma does NOT raise a Typst
error — it silently degrades the guard from exact-key membership to substring containment on a single
string**, which still compiles, still "works" for a single-edge single-master fixture (the trivial case
a hasty test would reach for), and would only misbehave once two edge keys share a common substring —
a corpus-scale hazard invisible in a two-master smoke test. This is a materially worse failure mode
than the "requires a trailing comma" phrasing in `49-CONTEXT.md` suggests (a silent semantic corruption,
not a compile-time syntax error) and belongs in the plan's own verification checklist, not just in a
code-review note.

This research also independently re-derives, from Sphinx 9.1.0 source read directly this session (not
from PROJECT.md's/CONTEXT.md's own citations), the exact mechanism Sphinx uses for `:numref:` figure
numbering (`sphinx/environment/collectors/toctree.py:285-378`, `assign_figure_numbers`) and finds it is
**more specifically wrong for a second master than PROJECT.md's framing suggests**: `env.toc_fignumbers`
is populated by a SINGLE walk starting **only** at `env.config.root_doc` — not a per-toctree-root walk,
not a `typst_documents`-aware walk. A figure reachable **only** through a `typst_documents` master other
than `root_doc` gets **no entry at all** in `env.toc_fignumbers`, which makes `get_fignumber()` raise
`ValueError` and `_resolve_numref_xref()` silently fall back to the reference's own literal
text/label — with **zero warning**, at Sphinx-build time, long before Typst ever sees the document. This
sharpens Open Question #2's measurement procedure into something concrete and mechanically explainable
rather than a vague "numbers might differ" (see Open Questions).

Finally, this research independently re-derives, from the pre-Phase-48 git history (the function itself
is already deleted from the working tree, confirmed by `grep`), the EXACT shape of the LIFO
`stack.pop()`/`.append()` walk COMP-05/SC#3 forbids generalizing — its `stack.pop()` from a list built
by forward `.append()` iteration means the LAST child of a toctree's `includefiles` is processed FIRST,
silently reversing sibling order (Common Pitfalls 3).

**Primary recommendation:** Compute each master's edge set once in `builder.write()` (env is fully
read-resolved by then; the corpus's 154-document scale needs no batching), reading `env.toctree_includes`
directly rather than re-walking doctrees — it already excludes `self`/external-URL entries and already
reflects `:glob:`/`:reversed:` expansion (see Pattern 2), so the DFS is a direct, cheap adjacency-list
walk. Route the state-guard string derivation through one shared function (D-05) that both
`builder.py`'s DFS and `translator.py`'s `visit_toctree` call, keyed **per emission site** (D-04),
verified against the corrected D-09 Typst syntax below.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| COMP-05 | Document-order DFS, first-encounter-wins, matching `inline_all_toctrees` | `sphinx/util/nodes.py:485-524` read verbatim this session (Architecture Patterns, System Diagram). `env.toctree_includes` confirmed as the correct adjacency-list source (Pattern 2), sourced from the SAME `includefiles` list `inline_all_toctrees` reads. The forbidden LIFO walk's exact defect mechanism reconstructed from git history (Common Pitfalls 3) |
| COMP-06 | Wrapper publishes edge set as `state`; content files emit state-guarded includes at toctree position | D-09's syntax verified end-to-end this session — 7 independent `typst.compile()` runs (Architecture Patterns Pattern 1, Code Examples) |
| COMP-07 | A document toctree'd by two masters appears in both masters' PDFs (defect A) | Verified this session: `manual.typ`/`bmanual.typ` diamond fixture, `pypdf`-read, `C-BODY` count 1 in each, from the same byte-identical `shared.typ` |
| COMP-08 | Prose keeps its position relative to included content | Verified this session: `PROSE-BEFORE` -> `ZMid` -> `Shared` -> `C-BODY` -> `PROSE-AFTER` in `pypdf`-extracted text order, guard emitted at the toctree's own position |
| COMP-09 | Diamond `M->[p,q]`, `p->[c]`, `q->[c]`, `M'->[q]` — `c` appears exactly once in each | Verified this session with the exact PROJECT.md-sketched shape; `C-BODY` count is 1 in `manual.typ` (nested under `zmid`) and 1 in `bmanual.typ` (direct), same `shared.typ` file on disk |
| COMP-10 | Heading levels track traversal order, not document identity | Verified this session with `typst.query(f, "heading", field="level")`: the SAME `shared.typ` resolves to level 3 in `manual.typ` and level 2 in `bmanual.typ`. Mirror-pair fixture (`xmaster` `[zmid,shared]` vs `[shared,zmid]`) independently reproduces PROJECT.md's LaTeX-measured precedent exactly (Code Examples) |
| COMP-11 | `visit_toctree` no longer emits unconditional `include()`; `_included_docnames` removed | Current code read this session: `translator.py:5016-5121`, `builder.py:231`/`658` — exact line numbers confirmed live (not trusted from CONTEXT.md's citations alone) |
| COMP-12 | Full Sphinx `doc/` corpus compiles fatal-free under new composition | Not run this session (requires the phase's own implementation to exist first) — corpus cache confirmed present and warm (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`), `test_corpus_gate.py`'s existing gate is the vehicle (Validation Architecture) |

</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Per-master include-edge decision (which content is "in" this compile) | Typst compile pass (`context`/`state`) | Sphinx `BuildEnvironment` (source of the raw adjacency list) | The decision genuinely cannot be made correctly in Python for the diamond case — one content file written once cannot both include and omit the same child for two different masters. Typst resolves it per-compile from published `state`, which is the only place "which master is compiling right now" is knowable |
| Include-edge SET computation (the DFS itself) | `TypstBuilder` (`builder.py`, Python) | — | The traversal rule (mirror `inline_all_toctrees`) is pure graph algorithm over `env.toctree_includes`, entirely a build-time concern; only the PER-EDGE ON/OFF decision moves to Typst, not the graph computation itself |
| Guard-string emission (open/state-check/include) | `TypstTranslator` (`translator.py`, `visit_toctree`) | — | Converting a toctree node to Typst source text is this class's whole job; the guard is a change to WHAT text it emits at a fixed position, not a new tier |
| Shared edge-key derivation (D-05) | One function, imported by both `TypstBuilder` and `TypstTranslator` | — | Per D-05, exactly one derivation point; living in either module and imported by the other is acceptable, but it must not become a second spelling of the same rule in each module |
| Build-scoped include-dedup ledger (`_included_docnames`, deleted) | `TypstBuilder` (deleted) | — | No consumer survives this phase; the responsibility moves entirely to the Typst compile pass |
| `:numref:` figure numbering (unaffected by this phase's mechanism, but interacts with it) | Sphinx `BuildEnvironment` (`env.toc_fignumbers`, computed once from `root_doc` only) | Typst `figure()`'s own per-compile counter | Two genuinely independent numbering authorities that this phase's own composition change does not unify — see Open Questions |
| Test/gate verification | pytest + real `typst.compile()`/`typst.query()` via `typst-py` | Sphinx subprocess build (`sphinx-build`) | Standing GATE-01 bar: correctness proven by compiling and reading back a real PDF/query result, not by asserting on emitted `.typ` string content alone |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `typst` (typst-py) | `0.15.0` [VERIFIED: `importlib.metadata.version("typst")`, this session, via `uv run python`] | `state()`, `context`, `query()` are its own stdlib primitives — no new dependency | Already the project's sole PDF-compile dependency; zero new runtime dependencies is a standing invariant (ROADMAP binding constraint #7) |
| `sphinx` | `9.1.0` [VERIFIED: `sphinx.__version__`, this session] | `env.toctree_includes`, `inline_all_toctrees`'s selection rule, `env.toc_fignumbers` | Already the project's core dependency; every traversal claim in this document was read against this exact installed version, not against Sphinx documentation of unknown vintage |

### Supporting
No new libraries. `pypdf` (already a test dependency, version `6.14.2` [VERIFIED: `pypdf.__version__`,
this session]) is the readback tool for every fixture measured in this document, and is what
`typst.query(..., field="level")` is paired with for COMP-10's resolved-heading-level assertion.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Per-master `state`-guarded includes | Re-scoping the write-time `_included_docnames` ledger per master | Measured and rejected in PROJECT.md, not re-derived here: cannot serve the diamond — `q.typ` must omit the `q->c` edge for `M` (already reaches `c` via `p`) and emit it for `M'`, and one file written once cannot do both |
| Per-master `state`-guarded includes | A flattened include graph carried entirely by the wrapper | Measured and rejected in PROJECT.md: solves the diamond but breaks document-order interleaving (prose after a toctree renders before the chapters) |
| Walking `env.get_doctree()` per master (re-deriving `entries`/`includefiles` from raw doctrees) | Reading `env.toctree_includes` directly | Both give an identical result (verified this session — `env.toctree_includes[docname]` is populated directly from the SAME `toctreenode['includefiles']` `inline_all_toctrees` reads, via `note_toctree()`, `sphinx/environment/adapters/toctree.py:32-47`) but `toctree_includes` is already-resolved, already excludes `self`/external-URL entries, and needs no per-master doctree re-fetch — strictly cheaper with no correctness cost. Recorded as the recommended choice for Claude's Discretion above |

**Installation:** No new packages. No `npm install`/`pip install` step is part of this phase's changes.

**Version verification:** Confirmed live this session via `uv run python -c "import importlib.metadata
as m; print(m.version('typst'))"` -> `0.15.0`, `uv run python -c "import sphinx; print(sphinx.__version__)"`
-> `9.1.0`, `uv run python -c "import pypdf; print(pypdf.__version__)"` -> `6.14.2`. All match
`PROJECT.md`'s already-recorded 2026-08-11/2026-08-12 measurements with no drift.

## Package Legitimacy Audit

Not applicable — this phase adds no new packages of any kind (no new PyPI dependency, no new `@preview`
package). `typst`/`sphinx`/`pypdf` are pre-existing project dependencies, already audited in prior
milestones (Phase 48's audit covers `typst`/`sphinx`; `pypdf` has been a test dependency since the
render-gate pattern was introduced).

## Architecture Patterns

### System Architecture Diagram

```
Sphinx read phase (env.toctree_includes populated per docname,
sphinx/environment/adapters/toctree.py:47 note_toctree(),
from the SAME toctreenode['includefiles'] inline_all_toctrees reads)
        |
        v
builder.write()  -- ONCE per build, before the per-docname write loop
        |
        |  For each typst_documents master docname:
        |    run the SAME DFS inline_all_toctrees runs --
        |    document order, first-encounter-wins, traversed
        |    seeded with [master_docname], read from
        |    env.toctree_includes (Pattern 2) -- and derive
        |    one edge KEY per (parent, child, emission-site) triple
        |    via the ONE shared function (D-05)
        v
{ master_docname: (edge_key, edge_key, ...) }  -- computed once, held on
                                                    the builder for the
                                                    rest of write()
        |
        v
_write_typst_files(docname, doctree)  -- per docname, Sphinx's own write loop
        |
        +--> ALWAYS: write docname's own CONTENT file (.typ, no template).
        |     visit_toctree emits, at the toctree's OWN position, one
        |     STATIC per-entry guard for EVERY includefiles entry --
        |     regardless of which master(s) will ever include this file:
        |
        |       context {
        |         set heading(offset: heading.offset + 1)
        |         if "<edge_key_1>" in state(<ns>, ()).get() { include("<c1>.typ") }
        |         if "<edge_key_2>" in state(<ns>, ()).get() { include("<c2>.typ") }
        |       }
        |
        |     -- the SAME bytes, unconditionally, no matter how many
        |     masters include this file or in what edge-set shape.
        |
        +--> IF docname is a typst_documents master: ALSO write a WRAPPER
              file. render_wrapper() now ALSO emits, before its existing
              #include("<content>.typ"):
                #state(<ns>, ()).update((<this master's own edge keys>))
        |
        v
typst.compile(wrapper.typ)
        |
        |  Typst's OWN multi-pass layout resolves EVERY context{}/query()
        |  in the whole compiled document against THIS wrapper's published
        |  state -- convergence measured working on diamond / interleaving
        |  / outline / label / heading-depth cases this session
        |
        +-- edge_key published in this wrapper's state --> guard fires,
        |    include() runs, content appears at the toctree's own position,
        |    nested at whatever heading depth the traversal-order relative
        |    offset accumulation produces
        |
        +-- edge_key absent (this file compiled standalone, OR this
             specific edge lost first-encounter-wins to a different
             parent) --> guard does not fire, compile still succeeds,
             no content, no error
```

A reader can trace SC#1's/COMP-07's primary use case end to end: `shared.typ`'s bytes are written to
disk exactly ONCE, and the SAME bytes appear in `manual.typ`'s PDF (nested, level 3) and `bmanual.typ`'s
PDF (direct, level 2) because the WRAPPER, not the file, decides which of the file's own static guards
resolve `true` for that specific compile.

### Recommended Project Structure

No new files/directories. Localized to three existing modules:

```
typsphinx/
├── builder.py     # NEW: per-master edge-set computation (mirrors inline_all_toctrees),
│                  #      run once in write(); _included_docnames declaration/reset DELETED
├── translator.py  # visit_toctree: static per-entry state guard replaces unconditional include();
│                  #      entries iteration -> includefiles iteration (D-03)
└── writer.py      # render_wrapper(): #state(<ns>, ()).update((...)) emitted before #include(...)
```

### Pattern 1: The state-guarded include -- D-09's corrected, verified syntax

**What:** A wrapper publishes its master's edge set once, at the top of its own body, as a Typst
`state` array. Every content file's `visit_toctree` emits ONE static `context {}` block per toctree
node containing one `if <key> in state(...).get() { include(...) }` per entry.

**When to use:** `writer.py`'s `render_wrapper()` (the state publication, once per wrapper) and
`translator.py`'s `visit_toctree` (the guard, once per toctree node, one `if` per entry).

**Verified this session (typst-py 0.15.0), the exact working shape — matches the CONTEXT.md sketch
byte-for-byte, now empirically confirmed rather than assumed:**

```typst
// Source: verified via typst.compile() + typst.query() this session.
// manual.typ (wrapper)
#state("inc", ()).update(("index>zmid", "zmid>shared"))
#include("index.typ")
```

```typst
// bmanual.typ (wrapper) -- note the REQUIRED trailing comma on a 1-element array (see Pitfall 1)
#state("inc", ()).update(("bmaster>shared",))
#include("bmaster.typ")
```

```typst
// index.typ (content) -- static, unconditional, regardless of which master(s) will ever include it
= Index

PROSE-BEFORE

#context {
  set heading(offset: heading.offset + 1)
  if "index>zmid" in state("inc", ()).get() { include("zmid.typ") }
  if "index>shared" in state("inc", ()).get() { include("shared.typ") }
}

PROSE-AFTER
```

Compiled and `pypdf`-read this session, `manual.typ`: text order is `Index / PROSE-BEFORE / ZMid /
Shared / C-BODY / PROSE-AFTER` (COMP-08's document-order interleaving), `C-BODY` count is **1**
(`index>shared`'s guard correctly does NOT fire — `zmid` claimed `shared` first, matching
first-encounter-wins). `bmanual.typ` (same `shared.typ` file, different wrapper): text is `BMaster /
Shared / C-BODY`, `C-BODY` count is **1** (COMP-09's diamond). `typst.query(f, "heading",
field="level")` reports `[1, 2, 3]` for `manual.typ` (Index / ZMid / Shared) and `[1, 2]` for
`bmanual.typ` (BMaster / Shared) — the SAME `shared.typ` file resolves to level 3 in one compile and
level 2 in the other, purely from the accumulated relative `heading.offset` (COMP-10).

`#outline()` visibility and `query()`-reachability verified: placing `#outline()` BEFORE
`#include("index.typ")` in the wrapper still lists all three headings including the conditionally
included `Shared` — Typst's multi-pass layout resolves the forward reference correctly. The `heading`
object returned by `typst.query()` carries a `'label': '<shared-label>'` field, confirming a labelled
heading inside a state-guarded include is fully `query()`-reachable, not merely visually present.

Standalone compile of a content file with no wrapper (`typst.compile("index.typ")` directly) produces
only `'Index'` — `state("inc", ()).get()` returns its default `()` with nothing ever `.update()`d, so
every guard is false and no children are included. Matches PROJECT.md's documented standalone-compile
behaviour exactly.

### Pattern 2: `env.toctree_includes` is the correct adjacency-list source, not a doctree re-walk

**What:** `env.toctree_includes: dict[str, list[str]]` is populated during Sphinx's read phase by
`note_toctree()` (`sphinx/environment/adapters/toctree.py:32-47`, read verbatim this session):

```python
# Source: sphinx/environment/adapters/toctree.py:42-47, read this session
include_files = toctreenode['includefiles']
for include_file in include_files:
    env.files_to_rebuild.setdefault(include_file, set()).add(docname)
env.toctree_includes.setdefault(docname, []).extend(include_files)
```

This is called once per `addnodes.toctree` node found during doctree processing, in document order
(docutils `findall()` traversal), and reads the EXACT SAME `toctreenode['includefiles']` list
`inline_all_toctrees` itself reads (`sphinx/util/nodes.py:497`, `includefiles = map(str,
toctreenode['includefiles'])`). Because `includefiles` never contains `self`/external-URL entries
(`sphinx/directives/other.py:129-135`, verified this session — those go to `entries` only, via `if
url_match or ref == 'self': toctree['entries'].append((title, ref)); continue`), `env.toctree_includes`
is ALREADY the D-03-shaped list — no separate filtering needed on the builder side.

**When to use:** The builder's per-master DFS (COMP-05). Read `env.toctree_includes.get(docname, [])`
as the children of `docname`, exactly the way `inline_all_toctrees` reads
`toctreenode['includefiles']`.

**Verified this session:** two documents in one toctree directive that are the SAME docname twice
(`child`, `child`) both survive into `env.toctree_includes[docname]` — confirmed via a live
`sphinx-build -b typstpdf` reproduction (see Common Pitfalls 4/Code Examples): `TocTree.parse_content`
warns once (`duplicated entry found in toctree: child`) but appends to BOTH `entries` and
`includefiles` regardless (`sphinx/directives/other.py:163-174`) — a real, currently-reachable case
D-04's per-emission-site key uniqueness must handle (see Common Pitfalls 5).

### Anti-Patterns to Avoid

- **Omitting the trailing comma on a single-edge array literal, believing it is "just a syntax
  requirement":** it is not a syntax error at all — see Common Pitfalls 1. This is a silent-corruption
  hazard, not a compile-fail-fast one, and needs its own explicit test assertion (array-typedness of
  the published state, not merely "does it compile").
- **Generalizing the deleted `_compute_master_included_docnames`'s `stack.pop()`/`.append()` walk:**
  see Common Pitfalls 3 for the exact reconstructed defect. The function no longer exists in the
  working tree (`grep` confirms zero hits this session) — this is a warning against reintroducing the
  SAME shape from habit/history, not against editing existing code.
- **A bare `"<parent>><child>"` key with no per-emission-site uniqueness:** see Common Pitfalls 5 for
  the concrete duplicate-toctree-entry case this breaks on.
- **Deriving the edge key independently in `builder.py` and `translator.py`:** D-05's whole point — a
  spelling mismatch produces a silent, un-erroring content omission, exactly the failure class this
  phase exists to close, reintroduced one layer up.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Deciding per-master which content is "in" this compile | A second Python-side per-master include-set computation consulted by the translator at write time | Typst's own `state`/`context` resolved per compile (Pattern 1) | Measured impossible to serve correctly from Python for the diamond case (PROJECT.md, re-confirmed by this session's own diamond fixture) — the answer genuinely does not exist until Typst resolves it for THIS specific wrapper |
| Filtering `self`/external-URL toctree entries before emission | A second entries-vs-includefiles reconciliation in the translator | Iterate `toctreenode['includefiles']` directly (D-03) — it is ALREADY filtered, at the Sphinx layer, before the translator ever sees the node (Pattern 2) | `sphinx/directives/other.py` already does this work; re-deriving it in the translator risks disagreeing with Sphinx's own rule (e.g. missing a future entry-type Sphinx adds to `entries`-but-not-`includefiles`) |
| Detecting duplicate/cyclic toctree references | A second visited-set / cycle-detector in the builder's new DFS | Mirror `inline_all_toctrees`'s own `traversed` list exactly (seed with the master's own docname, append before recursing) | Sphinx's own mechanism already handles cycles and self-reference correctly (never re-enters, never re-includes) — reinventing this risks a subtly different (and untested against Sphinx's own corpus) cycle rule |
| Deriving the edge-key string in two places | A translator-local key builder plus a builder-local key builder | ONE shared function (D-05), imported by both modules | A key mismatch does not fail the build — content silently vanishes, exactly the failure class this phase closes, one layer up. This follows the project's standing rule from Phase 40.1 D-06/D-07 and Phase 47 D-03 |

**Key insight:** This phase's entire value is deleting a hand-rolled Python mechanism
(`_included_docnames`) that cannot serve the diamond, replacing it with Typst's OWN compile-time
resolution of the same question — not adding a second hand-rolled mechanism next to it. Every "Don't
Hand-Roll" entry above is really the same insight applied to a different sub-decision inside the same
mechanism.

## Common Pitfalls

### Pitfall 1: Omitting the one-element array's trailing comma is NOT a syntax error — it is a silent
substring-matching corruption

**What goes wrong:** `("bmaster>shared")` (no trailing comma) is parsed by Typst as a **parenthesized
string expression**, not a one-element array. `state(...).update()` happily accepts it — Typst's
`state()` performs no runtime type check against its default value's type. The guard
`"bmaster>shared" in state("inc", ()).get()` then becomes a **substring containment test against a
single string**, not an exact membership test against a collection of keys.

**Verified this session, three fixtures:**

```typst
// no comma
#state("inc", ()).update(("bmaster>shared"))
#context [#repr(state("inc", ()).get())]      // -> "bmaster>shared"  (type: str)

// with comma
#state("inc", ()).update(("bmaster>shared",))
#context [#repr(state("inc", ()).get())]      // -> ("bmaster>shared",)  (type: array)

// the actual hazard: an UNRELATED substring also matches
#state("inc", ()).update(("bmaster>shared"))
#context [#("master" in state("inc", ()).get())]   // -> true
```

Both the with-comma and no-comma wrapper compiled and rendered **identical visible output** in a direct
comparison this session (`INCLUDED-OK` in both cases) — the failure is entirely invisible in a
single-edge smoke test, and only shows up once a second, unrelated edge key happens to be a substring
of (or contain) the first.

**Why it happens:** Typst's grouping parentheses `(expr)` and its one-element-array literal
`(expr,)` are genuinely different grammar productions, and `in` is polymorphic — it means "element of"
for an array and "substring of" for a string. `state()`'s `.update()` does not enforce that the updated
value matches the DEFAULT value's type.

**How to avoid:** Never construct the array literal via naive Python `", ".join(keys)` interpolation
without a trailing comma guard for the 1-key case. Either always emit a trailing comma unconditionally
(`f"({keys_joined},)"` is malformed for 0 or 2+ keys, so this must be conditional on `len(keys) == 1`),
or construct the array with an explicit Typst array constructor that has no single-element ambiguity.
A plan/test MUST assert the published state's Typst *type* is an array (e.g. via
`repr(type(state(...).get()))` in a probe fixture, or structurally by never emitting fewer than the
exact edge count as elements) for the single-master, single-edge case specifically — this is exactly
the shape the corpus's simplest configurations will hit on every build (D-09's own warning).

**Warning signs:** None at compile time — this is the whole danger. A single-master project with
exactly one edge key will "just work" whether or not the comma is present. Only a project with two
edge keys where one is a substring of the other (plausible with hierarchical-looking keys like
`"index>guide"` and `"index>guide2"` — `"guide" in "index>guide2"` is also true) would misbehave, and
even then only by INCLUDING something it should not, not by erroring.

### Pitfall 2: The 2026-08-12 D-08 line-break rule (Phase 48) also governs this phase's `if` chains

**What goes wrong:** `TypstError: expected block` if an `if <condition>`'s opening `{` is separated
from its condition by a bare newline (Phase 48 Pitfall 1, re-confirmed applicable here since this
phase's guard is structurally the same `if <cond> { ... } else { ... }` shape, just without an `else`
branch).

**How to avoid:** Every `if "<key>" in state(<ns>, ()).get() { include("<child>.typ") }` line the
translator emits must keep the condition and its opening `{` on one unbroken statement, exactly as
verified in every fixture this session (all one-line `if` statements, no `else` branch needed since a
false guard should simply produce no output, unlike Phase 48's guard which needed a `body`/`else` fallback).

### Pitfall 3: The deleted `_compute_master_included_docnames`'s LIFO walk (COMP-05's named anti-pattern)
-- reconstructed from git history since the function no longer exists in the tree

**What goes wrong:** Reversed sibling order with NO compile error — the build succeeds, the PDF looks
plausible, and only a careful check of DFS position (not merely "did it compile") catches it.

**The exact defect, reconstructed via `git show 8184f4d5^:typsphinx/builder.py` this session (the
function was deleted by Phase 48's own commit `8184f4d5`, confirmed `grep -rn
_compute_master_included_docnames typsphinx/` returns zero hits in the current tree):**

```python
# Source: git history, typsphinx/builder.py (pre-Phase-48, now deleted)
included: set[str] = set()
stack = list(masters)
while stack:
    docname = stack.pop()          # <-- pops from the END (LIFO)
    if docname in included:
        continue
    included.add(docname)
    for child in toctree_includes.get(docname, []):
        if child not in included:
            stack.append(child)    # <-- pushed in FORWARD iteration order
```

For a toctree listing children `[a, b, c]` in that document order, `stack.append` pushes `a, b, c` in
that order, and the very next `stack.pop()` pops `c` first — the LAST-listed child is visited before
the first, silently reversing document order. This is genuinely a DIFFERENT function than Phase 49
needs (it computed a flat cross-master UNION set for XREF-safety purposes, correctly for that job) —
but its traversal SHAPE is exactly the shape COMP-05/SC#3 forbids reusing for the new per-master DFS,
which must preserve document order.

**How to avoid:** The new per-master DFS must recurse (or use an explicit stack that preserves FIFO
child order, e.g. by reversing the children list before pushing, or by using genuine recursion which
naturally processes children in the order visited) — mirror `inline_all_toctrees`'s own recursive shape
(`for includefile in includefiles: if includefile not in traversed: ... subtree =
inline_all_toctrees(..., recurse into includefile ...)`), not a LIFO work-stack.

**Warning signs:** A mirror-pair fixture like COMP-10's own (`xmaster` `[zmid, shared]` vs
`[shared, zmid]`) is the direct detector — a LIFO-based walk would produce the WRONG member of the pair
claiming `shared` first in at least one of the two orderings.

### Pitfall 4: A duplicate toctree entry within ONE `.. toctree::` directive still reaches
`includefiles` twice -- reproduced live this session against the CURRENT (unfixed) code

**What goes wrong:** `TypstError: file not found (searched at .../self.typ)` for `self`/external-URL
entries, confirming D-10's RED is real and currently reachable; separately, `duplicated entry found in
toctree: child` is a Sphinx WARNING only (not a failure) and the entry survives into BOTH `entries` and
`includefiles`.

**Reproduced this session, real transcript** (`sphinx-build -b typstpdf` against a fixture with
`.. toctree:: \n\n   self\n   Ext <https://example.com>\n   child\n   child`, current unfixed tree):

```
WARNING: toctree で重複したエントリが見つかりました: child [toc.duplicate_entry]
...
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed:
TypstError: file not found (searched at .../self.typ)
```

Sphinx's own build phase exits 0 (only a warning); the fatal is Typst's, from the CURRENT translator's
`for _title, docname in entries:` loop (`translator.py:5095`) unconditionally emitting
`include("self.typ")` and `include("https://example.com.typ")`, neither of which exist on disk. The
CURRENT `_included_docnames` ledger DOES correctly dedup the two `child` entries down to one
`include("child.typ")` — confirmed: `grep -c 'include("child.typ")' index.typ` -> `1`.

**Why this matters for D-04 specifically:** once `_included_docnames` is deleted and replaced by a
STATE-based guard, this SAME duplicate-`child`-entry case becomes a live hazard from a different angle:
`inline_all_toctrees`'s own `traversed` list means `child`'s SECOND occurrence contributes NOTHING to
the edge set (the first occurrence already marked `child` as traversed) — so the graph computation
correctly produces the edge key only ONCE. But the TRANSLATOR still emits TWO separate `if <key> in
state(...).get() { include("child.typ") }` guards (one per occurrence in the source) — and if D-04's
per-emission-site uniqueness is skipped in favor of a bare `"index>child"` key reused at both emission
sites, BOTH guards would see the SAME key present in the state array and BOTH would fire, physically
`#include()`-ing `child.typ` TWICE and reproducing the "label occurs multiple times" fatal this whole
phase exists to prevent — this time laundered through the new mechanism instead of the old one.

**How to avoid:** D-04's per-emission-site key must ensure that when the SAME edge key would appear at
two emission sites in one document, only the FIRST (per the same first-encounter-wins rule the graph
computation uses) is ever present in the edge set — e.g. an ordinal/occurrence suffix baked into the
key, with the builder's DFS only ever emitting the first occurrence's key into the published state.

### Pitfall 5: `env.toc_fignumbers` is not "project-wide" in a generic sense — it is specifically
`root_doc`-rooted, and a `typst_documents` master unreachable from `root_doc` gets NO figure numbers
at all

**What goes wrong:** Assuming `:numref:` divergence is merely "numbers differ because of different DFS
position" understates the mechanism, and could lead to a plan that only tests the "differs" case and
misses the "target has literally no assigned number, and the reference silently degrades to raw
label/title text with zero warning" case.

**Why it happens — verified this session by reading `sphinx/environment/collectors/toctree.py:285-378`
verbatim:**

```python
# Source: sphinx/environment/collectors/toctree.py:372-373, read this session
if env.config.numfig:
    _walk_doc(env.config.root_doc, ())
```

`_walk_doc`/`_walk_doctree` (lines 338-370) recurse through EVERY `addnodes.toctree` node's `entries`
(NOT `includefiles` — a second, independent divergence from `inline_all_toctrees`'s own selection rule,
confirmed by reading lines 349-358) reachable from `root_doc`, using a single flat `assigned: set[str]`
shared across the WHOLE walk (first-encounter-wins, globally, not per-master). Any docname NEVER
reached by this ONE walk — because it is toctree'd only from a `typst_documents` master OTHER than
`root_doc`, and that master's own tree is never itself reachable from `root_doc`'s toctree structure —
gets **no entry** in `env.toc_fignumbers` at all. `get_fignumber()`
(`sphinx/domains/std/__init__.py:1416-1422`, read this session) then raises `ValueError` on a `KeyError`/
`IndexError`, which `_resolve_numref_xref()` (lines 1118-1121) catches by returning `contnode` (the
reference's own literal fallback text) — **silently, no warning emitted**.

**How to avoid:** Do not treat Open Question #2 as "compare two different numbers" only — the fixture
must also cover the "target reachable ONLY through the non-root_doc master" shape, where the expected
Sphinx-baked text is not a divergent number but the UN-numbered fallback text entirely. See Open
Questions for the concrete measurement procedure this finding sharpens.

**Warning signs:** None at Sphinx-build time (no warning); the compiled PDF will show a real Typst
`figure()` number (Typst's own per-compile counter always assigns one) sitting next to a `:numref:`
cross-reference that says something entirely unrelated (the figure's literal caption text, or its bare
label) — a silent, structural mismatch, not a crash.

## Code Examples

### Full diamond + interleaving + heading-depth round-trip (verified this session)

```typst
// Source: verified via typst.compile() + typst.query() this session, typst-py 0.15.0.
// manual.typ
#state("inc", ()).update(("index>zmid", "zmid>shared"))
#include("index.typ")
```
```typst
// bmanual.typ
#state("inc", ()).update(("bmaster>shared",))
#include("bmaster.typ")
```
```typst
// index.typ
= Index

PROSE-BEFORE

#context {
  set heading(offset: heading.offset + 1)
  if "index>zmid" in state("inc", ()).get() { include("zmid.typ") }
  if "index>shared" in state("inc", ()).get() { include("shared.typ") }
}

PROSE-AFTER
```
```typst
// zmid.typ
= ZMid

#context {
  set heading(offset: heading.offset + 1)
  if "zmid>shared" in state("inc", ()).get() { include("shared.typ") }
}
```
```typst
// shared.typ -- byte-identical in both compiles
= Shared <shared-label>

C-BODY
```
```typst
// bmaster.typ
= BMaster

#context {
  set heading(offset: heading.offset + 1)
  if "bmaster>shared" in state("inc", ()).get() { include("shared.typ") }
}
```

Results (`pypdf` text extraction + `typst.query`):

| Wrapper | Extracted text order | `C-BODY` count | `heading` levels (`typst.query(f, "heading", field="level")`) |
|---------|----------------------|----------------|----------------------------------------------------------------|
| `manual.typ` | Index / PROSE-BEFORE / ZMid / Shared / C-BODY / PROSE-AFTER | 1 | `[1, 2, 3]` |
| `bmanual.typ` | BMaster / Shared / C-BODY | 1 | `[1, 2]` |

### The mirror-pair traversal-order fixture (verified this session, reproduces PROJECT.md's LaTeX
precedent exactly)

```typst
// Order A -- xmaster lists [zmid, shared]: zmid claims shared first (nested)
#state("inc", ()).update(("xmaster>zmid", "zmid>shared"))
#include("xmaster.typ")
```
```typst
// Order B -- xmaster lists [shared, zmid]: xmaster claims shared directly;
// zmid's own claim on shared is skipped (already traversed)
#state("inc", ()).update(("xmaster>shared", "xmaster>zmid"))
#include("xmasterB_content.typ")
```

Order A: text `XMaster / ZMid / Shared / C-BODY`, levels `[1, 2, 3]` (Shared nested under ZMid).
Order B: text `XMaster / Shared / C-BODY / ZMid`, levels `[1, 2, 2]` (Shared direct, ZMid direct and
empty — its own child claim on `shared` lost). Exactly matches PROJECT.md's independently-measured
LaTeX precedent (`\chapter{Mid}/\section{Shared}` vs `\chapter{Shared}/\chapter{Mid}`), now reproduced
against this phase's OWN mechanism rather than merely cited from the LaTeX builder.

### D-10's RED, reproduced live this session against the current (unfixed) tree

```
$ sphinx-build -b typstpdf source build   # toctree: self / Ext <https://example.com> / child / child
...
WARNING: toctree で重複したエントリが見つかりました: child [toc.duplicate_entry]
...
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed:
TypstError: file not found (searched at .../self.typ)
Location: .../manual.typ
```

Emitted `index.typ` (current, unfixed): `include("self.typ")`, `include("https://example.com.typ")`,
and a single deduped `include("child.typ")`.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `builder._included_docnames: set[str]` — one flat set per BUILD, shared across every master, reset once in `write()` | `#state(<ns>, ()).update((...))` — one array per WRAPPER, resolved by Typst per compile | This phase | The include decision becomes correct per-master instead of an approximation that cannot distinguish which master is asking (defect A, the diamond) |
| `visit_toctree` iterates `node['entries']` (title, docname-or-self-or-URL pairs) | `visit_toctree` iterates `node['includefiles']` (docname-only, already excludes self/external-URL) | This phase (D-03) | Closes a currently-live compile fatal (`file not found ... self.typ`) as a structural consequence, not a separate patch |
| A hand-rolled builder-side per-master traversal (never existed for this purpose before) | Reads `env.toctree_includes` directly, the SAME adjacency list `inline_all_toctrees` and the figure-numbering walk both already read | This phase | No new Sphinx-facing derivation to maintain; any future Sphinx change to how `includefiles` is populated is inherited automatically |

**Deprecated/outdated:**
- `builder._included_docnames` and its `init()`/`write()` reset — deleted in this phase, per COMP-11.
- The unconditional `include()` emission in `visit_toctree` — replaced by the static per-entry guard.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `env.toctree_includes`'s list-per-docname preserves document order across MULTIPLE `.. toctree::` directives in one document (verified this session only that `note_toctree` is called once per `addnodes.toctree` node via docutils' document-order `findall()`, not verified with a live multi-toctree-per-document fixture) | Architecture Patterns Pattern 2 | Low — `findall()` is a well-established docutils document-order traversal; if wrong, the effect would be visible immediately in any multi-toctree-per-document corpus fixture (Sphinx's own `doc/` tree has several), not silently |
| A2 | The corpus-scale (154-document) `state`/`context` multi-pass convergence holds — this session verified convergence only on small fixtures (diamond, mirror-pair, outline); PROJECT.md already names this the milestone's own named residual risk and ROADMAP binding constraint #5 / D-02 already assign it a stop-and-escalate protocol | Summary, Validation Architecture | High if wrong, but explicitly NOT this research's job to resolve — D-02 already names the process (stop and escalate), and GATE-02 is the phase's own measurement vehicle, not a research-time obligation |
| A3 | The `:numref:` fallback-to-`contnode`-with-no-warning behavior (Common Pitfalls 5) is reachable through typsphinx's OWN `-b typst`/`-b typstpdf` pipeline identically to how it would be through `-b html` (this session read the mechanism in Sphinx's OWN post-transform, builder-agnostic, but did not build a live typsphinx multi-master `:numref:` fixture — that is Open Question #2's own remaining measurement, explicitly deferred to this phase's execution per D-01) | Common Pitfalls 5, Open Questions | Medium — if the typst-specific reference-resolution path (Phase 48's guard machinery) intercepts this differently than assumed, the concrete failure mode could differ from "silent fallback text"; the underlying `env.toc_fignumbers` mechanism itself is builder-agnostic and verified, so the ROOT CAUSE claim is solid even if the exact typsphinx-side manifestation needs the live fixture Open Question #2 calls for |

**If this table is empty:** N/A — three assumptions recorded above; A1 and A3 are low/medium risk and
do not block planning; A2 is explicitly out of research's scope by the milestone's own D-02/binding
constraint #5.

## Open Questions

1. **`:numref:` divergence — now a concrete, mechanically-explained measurement procedure (not merely
   "compare two numbers"), still requiring a live two-master fixture to execute (D-01's job, not
   research's).**
   - What we know: `env.toc_fignumbers` is computed ONCE, walking ONLY from `env.config.root_doc`,
     first-encounter-wins, GLOBALLY (not per-master) — read verbatim this session from
     `sphinx/environment/collectors/toctree.py:285-378`. `get_fignumber()` raises `ValueError` for any
     docname this walk never reached, and `_resolve_numref_xref()` silently falls back to the
     reference's own literal text with **zero warning** in that case
     (`sphinx/domains/std/__init__.py:1087-1170`, `1395-1422`, read this session). Typst's own
     `figure()` numbering is a genuinely separate, per-compiled-wrapper sequential counter (confirmed
     by reading `translator.py:2571-2667`'s `visit_figure`/`depart_figure` — no `numbering:` override
     tying it to Sphinx's number is emitted).
   - What's unclear: the EXACT typsphinx-side rendering of a `:numref:`-referencing `number_reference`
     node once it has fallen back to `contnode` — whether it still routes through Phase 48's
     compile-time label-existence guard (likely yes, since it is still a `reference`-family node) and
     what TEXT specifically appears in that case (the raw label? the figure's own caption title? this
     depends on `contnode`'s construction, not traced fully this session).
   - Recommendation: the phase's own live fixture (D-01) needs **two** cases, not one: (a) the SAME
     figure toctree'd at different DFS positions but reachable from BOTH `root_doc` and a second
     master (tests "numbers differ"), and (b) a figure toctree'd ONLY from a non-`root_doc` master
     (tests "no number assigned at all, silent text fallback"). Case (b) is the sharper, previously
     under-specified finding this research adds. Use `pypdf` to extract BOTH the `:numref:` reference's
     rendered text AND the target figure's own Typst-assigned caption number from each master's
     compiled PDF, for both cases.

2. **`visit_toctree`'s mode-prefix (Phase 48 Pattern 2's open question, NOT reopened by this research
   but worth carrying forward): the current `context {` emission in `visit_toctree` has no `#` prefix
   at all (verified this session, `translator.py:5075`), unlike the label-existence guard sites Phase
   48 touched, which DO compute a `prefix = "#" if self._in_markup_mode else ""`.**
   - What we know: `visit_toctree`'s current bare `context {` compiles correctly in every fixture this
     session (all top-level content-file compiles succeeded) because content files' bodies are
     unconditionally wrapped in a single top-level CODE-mode block by `builder.py`'s
     `_write_typst_files` (`body = "#{\n" + body` if not already so) — `visit_toctree` is therefore
     ALWAYS invoked from code mode, never markup mode, and needs no `prefix` variable the way Phase
     48's reference/citation sites do.
   - What's unclear: whether this invariant (content-file top level is always code mode) could ever be
     violated by a FUTURE translator change that calls `visit_toctree` from inside a markup-mode
     nested context — out of THIS phase's scope to guard against, but worth a one-line comment at the
     new guard-emission site noting the assumption, so a future change that breaks it fails loudly
     rather than silently emitting `context` without its required `#`.
   - Recommendation: no action needed this phase; note only.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| `typst` (typst-py) | D-09's guard verification, all GATE-01 fixtures, GATE-02 | ✓ | 0.15.0 [VERIFIED, this session] | — |
| `sphinx` | Real-build reproduction fixtures (D-10), source-reading verification of `inline_all_toctrees`/`toc_fignumbers` | ✓ | 9.1.0 [VERIFIED, this session] | — |
| `pypdf` | Reading back rendered text and confirming document-order interleaving, `C-BODY` counts | ✓ | 6.14.2 [VERIFIED, this session] | — |
| `typst.query()` (typst-py's own API) | COMP-10's resolved-heading-level assertion vehicle | ✓ | Same 0.15.0 install; `query(input, selector, field=...)` confirmed callable this session with real output | — |
| Cached Sphinx `doc/` corpus (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/`) | COMP-12's GATE-02 full-corpus pass | ✓ | Present and warm, confirmed this session via `ls` | Re-clones automatically if cache absent (existing `get_or_clone_corpus` machinery, unchanged by this phase) |
| `uv run sphinx-build` (a Python entry-point script, not a compiled binary) | Live D-10 reproduction | ✓ | Ran successfully this session under the project's NixOS sandbox | The environment note about `uv run <compiled-binary>` failing (e.g. `uv run ruff`) does NOT apply here — `sphinx-build` is a pure-Python console-script entry point |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** None — everything this phase needs was already present and
working in the project's `.venv` this session, confirmed by direct invocation rather than assumed from
prior phases' records.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 [CITED: matches Phase 48's own live-captured header; not re-captured this session but no dependency change occurred between phases] |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`, read this session, lines 75-96) |
| Quick run command | `uv run pytest -m "not slow"` |
| Full suite command | `uv run pytest` (includes `-m slow` corpus/render-gate tests) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| COMP-07 | A document toctree'd by two masters appears in both masters' PDFs, `pypdf`-read | integration (real `typst.compile()` + `pypdf`) | New fixture (two-master `conf.py`, `typst_documents` with two entries, shared child) — pattern established by this session's own `manual.typ`/`bmanual.typ` measurement | ❌ Wave 0 — new fixture, pre-fix RED must record the CURRENT `SHARED-CHAPTER-MARKER` 0-times-in-`index.pdf` baseline (already measured live 2026-08-11, PROJECT.md) |
| COMP-08 | Prose position relative to included content, document-order interleaving | integration (`pypdf` text-order assertion) | New fixture shaped like Sphinx's default `index.rst` (prose, toctree, "Indices and tables") | ❌ Wave 0 |
| COMP-09 | Diamond: `C-BODY` exactly once in each of two masters' PDFs, same content file | integration (`pypdf`) | New fixture — this session's own `manual.typ`/`bmanual.typ`/`zmid.typ`/`shared.typ`/`bmaster.typ` shape is directly reusable as the test's `.rst`/`conf.py` equivalent | ❌ Wave 0 |
| COMP-10 | Heading levels track traversal order — mirror-pair `[zmid,shared]` vs `[shared,zmid]` | integration (`typst.query(f, "heading", field="level")` against the COMPILED document) | New fixture — this session's `xmasterA`/`xmasterB` shape is directly reusable | ❌ Wave 0 |
| COMP-05/COMP-06/COMP-11 | `visit_toctree` no longer emits unconditional `include()`; `_included_docnames` fully removed | structural (repo-wide grep) + unit | `grep -rn _included_docnames typsphinx/` (must be empty) | N/A — a grep assertion, likely embedded in a new or existing test |
| COMP-05 (D-03) | Iterates `includefiles`, not `entries`; `self`/external-URL toctree entries no longer abort the compile | integration (real `sphinx-build -b typstpdf`) | New fixture reproducing this session's D-10 transcript exactly (`self` / `Ext <https://example.com>` / `child` / `child`) — pre-fix RED already captured this session (Code Examples) | ❌ Wave 0 — this session's transcript is the pre-fix RED evidence; needs to become a committed fixture |
| COMP-05 (D-04) | Duplicate toctree entry (same child twice in one directive) includes exactly once under the new mechanism | integration (real `typst.compile()`) | New fixture, same `.rst` shape as D-10's reproduction, asserting `child.typ`'s body text appears exactly once in the compiled PDF | ❌ Wave 0 |
| COMP-05 (D-06) | Degenerate shapes: 2-node cycle, self-ref, `:glob:`, `:orphan:` reference, ≥3 masters ≥2 overlapping children | integration, one fixture per shape | New fixtures per shape — `tests/roots/` currently has ONLY `test-basic` (confirmed this session, `ls tests/roots/` -> 1 entry), so every shape needs a new root or a new `conf.py`/`.rst` pair | ❌ Wave 0 — zero existing coverage confirmed |
| COMP-12 | Full Sphinx `doc/` corpus compiles fatal-free under new composition | integration (real `sphinx-build → typst.compile()`, `-m slow`) | `uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow` | ✅ (existing gate, `test_corpus_gate.py:284`, confirmed this session) |
| Open Question #2 | `:numref:` two-case measurement (differing number; no number at all) | integration (real `sphinx-build` + `typst.compile()` + `pypdf`, two masters) | New fixture per the two-case procedure in Open Questions | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest -m "not slow"` (fast suite; excludes the corpus gate)
- **Per wave merge:** `uv run pytest` (full suite including the corpus gate)
- **Phase gate:** Full suite green before `/gsd-verify-work`; D-02's stop-and-escalate protocol applies
  if GATE-02's full-corpus pass fails to converge — this is NOT a normal test-fix loop, per binding
  constraint #5

### Wave 0 Gaps
- [ ] A committed diamond fixture (`manual.typ`/`bmanual.typ`/`zmid.typ`/`shared.typ`/`bmaster.typ`
  equivalent, as real `.rst`/`conf.py`) for COMP-07/COMP-09, with pre-fix RED against the 2026-08-11
  baseline
- [ ] A committed mirror-pair fixture (`xmaster` `[zmid,shared]` vs `[shared,zmid]`) for COMP-10
- [ ] A committed prose-interleaving fixture (Sphinx's own default `index.rst` shape) for COMP-08
- [ ] A committed `self`/external-URL/duplicate-entry fixture for D-03/D-10 — this session's own
  transcript is the pre-fix RED evidence and needs to become a committed test asset
- [ ] Five new `tests/roots/`-shaped fixtures (or `conf.py`/`.rst` pairs) for D-06's degenerate shapes:
  2-node cycle, self-reference, `:glob:` toctree, `:orphan:`-referenced document, ≥3 masters ≥2
  overlapping children — zero existing coverage confirmed this session
- [ ] A committed two-case `:numref:` fixture (differing-number case + no-number-assigned case) for
  Open Question #2

*(No framework install needed — pytest, typst-py, pypdf, and Sphinx are all already installed and
working in `.venv`, confirmed this session.)*

## Security Domain

Not applicable to this phase. This is a compile-time include-selection mechanism change to a
document-generation pipeline with no authentication, session, network-input-validation, or
cryptographic surface — the same reasoning Phase 48's research recorded and re-confirmed here: ASVS
categories V2/V3/V4/V6 are structurally inapplicable to a local Sphinx/Typst document-build tool with
no user-facing network service. V5 Input Validation is unchanged by this phase (the edge-key strings
are derived from Sphinx's own already-validated docnames, not from unsanitized external input).

## Sources

### Primary (HIGH confidence — verified this session by direct tool invocation or direct file read)
- `typst.compile()` / `typst.query()` (typst-py 0.15.0) — 20+ distinct `.typ` fixtures compiled this
  session to verify D-09's syntax, the trailing-comma hazard, the outline/query visibility, and the
  mirror-pair traversal-order proof.
- `sphinx-build -b typstpdf` (Sphinx 9.1.0) — one real project build this session, reproducing D-10's
  `self`/external-URL/duplicate-entry fatal against the CURRENT (unfixed) tree.
- `/home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/sphinx/util/nodes.py:485-524`
  (`inline_all_toctrees`) — read directly this session.
- `/home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/sphinx/builders/latex/__init__.py:389-391`
  and `.../sphinx/builders/singlehtml.py:95` — the `traversed` seeding callers, read directly this
  session.
- `/home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/sphinx/directives/other.py:42-183`
  (`TocTree.parse_content`) — read directly this session; confirms `entries`/`includefiles` divergence,
  fresh-per-directive `all_docnames`, `:glob:` expansion, `:reversed:` handling.
- `/home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/sphinx/environment/adapters/toctree.py:32-47`
  (`note_toctree`) — read directly this session; confirms `env.toctree_includes` sources the SAME
  `includefiles` list `inline_all_toctrees` reads.
- `/home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/sphinx/environment/collectors/toctree.py:285-378`
  (`assign_figure_numbers`) — read directly this session; the source of the `:numref:` divergence
  finding sharpened in Open Questions.
- `/home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/sphinx/domains/std/__init__.py:1087-1170,1395-1422`
  (`_resolve_numref_xref`, `get_fignumber`) — read directly this session.
- `typsphinx/translator.py:5016-5121` (`visit_toctree`/`depart_toctree`), `4592` (`_compute_relative_include_path`,
  survives unchanged), `2571-2667` (`visit_figure`, confirming Typst's own independent figure counter) —
  read directly this session, all line numbers confirmed live rather than trusted from CONTEXT.md's
  citations.
- `typsphinx/builder.py:208-231` (`init`, `_included_docnames` declaration), `630-658` (`write()`,
  the reset), `859-935` (`_write_typst_files`) — read directly this session.
- `typsphinx/writer.py:1-40` (`compute_content_include_path`), `262-390` (`render_wrapper`) — read
  directly this session.
- `git show 8184f4d5^:typsphinx/builder.py` — the deleted `_compute_master_included_docnames`'s exact
  LIFO-walk implementation, retrieved from history this session (Common Pitfalls 3).
- `tests/roots/` (`ls`, 1 entry: `test-basic`), `tests/test_master_include_set_predicate_gate.py`
  (`grep`, confirms current 5-test structure post-Phase-48), `tests/test_corpus_gate.py:284` (confirms
  GATE-02's existing entry point) — all confirmed live this session.

### Secondary (MEDIUM confidence)
- `.planning/PROJECT.md` lines 1-170 — the milestone-level design record, cross-checked against this
  session's own independent re-derivation (the mirror-pair traversal-order claim, the diamond claim,
  and the D-09 syntax were all independently re-measured, not merely trusted).
- `.planning/ROADMAP.md` lines 685-757 — Phase 49's own goal/SC text, read directly this session and
  confirmed to match `49-CONTEXT.md`'s citations verbatim.
- `.planning/phases/48-compile-time-cross-reference-guard/48-RESEARCH.md` — Phase 48's own measured
  `context`/`query` guard shape and its D-08 line-break pitfall, re-applied here as Common Pitfalls 2.

### Tertiary (LOW confidence)
- None used. Every claim in this document traces to either a file this session read directly or a
  command this session ran directly.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies, all three existing dependencies' versions verified live.
- Architecture: HIGH — the state-guard's exact working Typst syntax, the trailing-comma hazard, the
  mirror-pair traversal-order proof, and the document-order interleaving were all compiled and read
  back via `pypdf`/`typst.query()` this session, not inferred from documentation or trusted from
  CONTEXT.md's own citations.
- Pitfalls: HIGH — all five pitfalls are transcribed from real `TypstError`/`sphinx-build` transcripts
  or directly-read source produced this session, not anticipated from general Typst/Sphinx knowledge.
- The one genuinely open item (COMP-12's corpus-scale convergence) is explicitly NOT resolved by this
  research and is not claimed to be — D-02/binding constraint #5 already assign it a phase-execution-time
  stop-and-escalate protocol, which this document defers to rather than duplicates.

**Research date:** 2026-08-14
**Valid until:** Tied to `typst-py>=0.15.0,<0.16` and Sphinx `9.1.0`. Re-verify the guard syntax and the
`env.toctree_includes`/`env.toc_fignumbers` mechanisms if either pin changes — Typst's own parser
grammar and Sphinx's own toctree-collection internals are both more load-bearing here than either
Python package's version number. No fixed day-count expiry; re-verify on any `typst-py` or `sphinx`
major/minor bump.
