# Phase 49 Plan 01 — Expected Emission Contract, Fixture Specification, and Assertion Census

**Written:** 2026-08-14
**Binding constraint #6 compliance:** every emitted string, edge key, and expected observation
below is derived by reading `49-EVIDENCE.md`'s `## State-syntax measurement` (Task 1's own
real-compile transcripts), `49-CONTEXT.md`'s decisions D-03..D-08, Sphinx 9.1.0's own source
(`sphinx/util/nodes.py`, `sphinx/directives/other.py`, `sphinx/builders/latex/__init__.py`,
`sphinx/builders/singlehtml.py`, all read verbatim this task), and each proposed fixture's own
`conf.py`/`.rst` content specified here, read literally by hand. **No builder was run to produce
this document, and the Typst probes cited from `49-EVIDENCE.md` are hand-written files exercising
the Typst language, not emitter output** — no typsphinx code implementing this phase's mechanism
exists in the working tree while this document is written (`git status --porcelain typsphinx/
tests/` prints nothing throughout Task 2 and Task 3).

---

## Emission contract

Every string this phase emits is fixed here as a substitutable template, with one worked
substitution each, so every expected value in the rest of this phase — and in every later plan —
is a substitution into this contract rather than an independent derivation (D-05).

### The state key (D-07)

**Template:** the literal string `typsphinx:include-edges` (measured and adopted in
`49-EVIDENCE.md`'s State-syntax measurement, superseding PROJECT.md's `"inc"` sketch). It appears
in exactly two emitted shapes:

1. The wrapper's publication call: `#state("typsphinx:include-edges", ()).update((<edge_keys>))`.
2. Each guard's read: `state("typsphinx:include-edges", ()).get()`.

No third shape exists — the key string is never interpolated into any other construct.

### The edge key (D-04)

**Template:** `<parent_docname>#<occurrence>><child_docname>` — the parent's docname, a literal
`#`, the 0-based occurrence index of THIS emission site among the emission sites in that parent
naming that same child, a literal `>`, then the child's docname.

**The occurrence rule is a property of BOTH sides, and the two sides count differently by
design:**

- **Emission side (translator, per content file):** for the document currently being translated,
  maintain a per-child counter across ALL of that document's toctree entries (flattened in
  document order across however many `.. toctree::` directives the document has — `49-RESEARCH.md`
  Architecture Patterns Pattern 2 confirms `env.toctree_includes[docname]` is exactly this
  flattened, document-order list). For the Nth time a given child docname appears as an entry in
  THIS document's own includefiles list, its occurrence is N (0-based). One guard line is emitted
  per entry, unconditionally, regardless of whether that guard will ever fire for any master.
- **Graph side (builder, per master's DFS):** a child is claimed by its parent at that child's
  FIRST non-traversed appearance in the parent's ordered list, which — because a document's
  `traversed` membership can only grow, never shrink, during one master's walk — is ALWAYS the
  occurrence-0 appearance. **The graph side therefore never emits an edge key whose occurrence is
  ≥ 1; only occurrence-0 keys can ever appear in ANY master's published edge set.**

**Worked example (duplicate entry inside one toctree directive):** document `index` toctrees
`child` twice. `env.toctree_includes["index"] == ["child", "child"]` (Sphinx's own `parse_content`
warns `duplicated entry found in toctree: child` but still appends BOTH occurrences to
`includefiles` — measured directly this task, `sphinx/directives/other.py:165-177`, read
verbatim: the `else` branch of the `if docname in all_docnames` check only logs a warning; it does
not `continue`, so the append two lines below still runs). The content file `index.typ` therefore
emits TWO guard lines:
```
if "index#0>child" in state("typsphinx:include-edges", ()).get() { include("child.typ") }
if "index#1>child" in state("typsphinx:include-edges", ()).get() { include("child.typ") }
```
but the graph side's DFS, walking `index`'s children `["child", "child"]`, claims `child` at its
FIRST appearance (`traversed` gains `child` immediately), so the second appearance is already
`in traversed` and contributes NO edge. The published edge set for any master reaching `index`
therefore contains `index#0>child` and never `index#1>child` — the second guard line is
**structurally dark forever**, by construction, not by accident. This is exactly what prevents the
"same file `#include()`d twice, every label it defines re-emitted, compile fatal" failure class
D-04 exists to close.

### The array-literal rendering rule

**Template:** `()` for zero keys; for one or more keys, a parenthesized comma-separated list of
double-quoted keys with an UNCONDITIONAL trailing comma after the LAST element —
`("<key1>", "<key2>", ..., "<keyN>",)`.

**Worked substitutions, licensed by `49-EVIDENCE.md` Probes 1-4 (arity 0 through 3, all measured
compiling with type `array` and the correct `len()`):**

- Zero keys: `#state("typsphinx:include-edges", ()).update(())`
- One key: `#state("typsphinx:include-edges", ()).update(("index#0>child",))`
- Two keys: `#state("typsphinx:include-edges", ()).update(("index#0>a", "index#0>b",))`
- Three keys: `#state("typsphinx:include-edges", ()).update(("index#0>a", "index#0>b", "index#0>c",))`

The uniform unconditional-trailing-comma rule is what removes the `len(keys) == 1` special case
RESEARCH Pitfall 1 warns is otherwise required: `49-EVIDENCE.md` Probe 3 measured that a trailing
comma is accepted identically at arity 2 and arity 3 (not merely tolerated at arity 1), so the
SAME construction expression — always append a trailing comma when the key count is ≥ 1, never
when it is 0 — is correct at every arity with no branch on the specific count. `49-EVIDENCE.md`
Probe 5 measured the omitted-comma case as the silent-corruption hazard this rule exists to
prevent by construction (the published state's Typst type degrades from `array` to `str`, and the
guard degrades from array membership to substring containment, with **zero compile-time error**).

### The wrapper body shape

**Template:** the publication line first, then the existing content-include line, with nothing
between them:
```
#state("typsphinx:include-edges", ()).update((<edge_keys>))
#include("<content_relative_path>")
```

**Fully substituted, a master with two edge keys** (`writer.py:299-300`'s existing
`compute_content_include_path()` output unchanged, per the "unchanged surfaces" bullet below):
```
#state("typsphinx:include-edges", ()).update(("index#0>zmid", "zmid#0>shared",))
#include("index.typ")
```

**Fully substituted, a master with one edge key** (the trailing-comma case every single-master,
single-edge project hits on every build, per D-09/Pitfall 1):
```
#state("typsphinx:include-edges", ()).update(("bmaster#0>shared",))
#include("bmaster.typ")
```

### The guard line shape

**Template:** one line per emission site, emitted INSIDE the existing `context { ... }` block
(`translator.py:5075-5077`), after the existing `set heading(offset: heading.offset + 1)` line
(D-08, unchanged), with the condition and its opening `{` on ONE unbroken line — `49-EVIDENCE.md`
Probe 7 measured that a newline between the condition and its opening brace fails with the
verbatim error `expected block`, and Probe 7's passing variant keeps them on one line:
```
if "<edge_key>" in state("typsphinx:include-edges", ()).get() { include("<relative_path>.typ") }
```

**Fully substituted, one concrete key and relative path:**
```
if "index#0>zmid" in state("typsphinx:include-edges", ()).get() { include("zmid.typ") }
```

The surrounding scope block is UNCHANGED in shape (D-08): the guard lines replace ONLY the
unconditional `include()` calls currently emitted at `translator.py:5114-5115`; the `context {`
opener, the `set heading(offset: heading.offset + 1)` line, and the closing `}` all survive
byte-identical.

### The escaping rule

Every docname interpolated into any of these literals — on BOTH the publication side (the edge
keys inside the wrapper's `.update((...))` call) and the guard side (the edge key inside each
`if "..." in ...` condition, and the relative include path inside `include("...")`)  — routes
through the existing `escape_typst_string()` helper (`translator.py:141-172`, read verbatim this
task), so a docname containing a quote or a backslash yields a valid Typst string literal that
still matches exactly on both sides. `escape_typst_string()` applies no Unicode normalization on
either side (it only escapes `\`, `"`, `\n`, `\r`, `\t`), so key equality between the publication
side and the guard side is exact code-point equality, not normalized equality.

### The `includefiles` rule (D-03)

Both the builder-side graph traversal (COMP-05's DFS) and the translator-side guard emission
(`visit_toctree`) iterate the toctree node's INCLUDE-FILE list (`node["includefiles"]`, equivalently
`env.toctree_includes[docname]` at the builder layer per `49-RESEARCH.md` Pattern 2), **never**
its entry list (`node["entries"]`). Measured this task, `sphinx/directives/other.py:146-149`:
```python
if url_match or ref == 'self':
    toctree['entries'].append((title, ref))
    continue
```
`self` and external-URL entries are appended to `entries` and then the loop `continue`s — they
NEVER reach `toctree['includefiles'].append(docname)` two lines further down. Two consequences:

1. `self` and external-URL entries never produce a guard at all (there is no `includefiles` entry
   for them to iterate), which closes the currently-live compile fatal
   (`TypstError: file not found (searched at .../self.typ)`, reproduced in `49-RESEARCH.md` Code
   Examples against the current unfixed tree) as a structural consequence of the mechanism change,
   not a separate patch.
2. The emptiness check that currently short-circuits `visit_toctree` on an empty `entries` list
   (`translator.py:5054-5057`, `if not entries: ... raise nodes.SkipNode`) must switch to checking
   the `includefiles` list instead, so a toctree containing ONLY `self`/external-URL entries (an
   entries-only toctree) correctly emits no `context { ... }` block at all, rather than emitting an
   empty one.

### The traversal rule (COMP-05)

A recursive walk over each parent's ordered `includefiles` list, with an ordered `traversed` list
threaded through the recursion, seeded with `[master_docname]` before the walk begins and appended
to BEFORE recursing into each newly-claimed child — mirroring `inline_all_toctrees`
(`sphinx/util/nodes.py:499-517`, read verbatim this task) and its two callers that seed
`traversed` with the compiling document's own docname
(`sphinx/builders/latex/__init__.py:389-391`: `inline_all_toctrees(self, self.docnames, indexfile,
tree, darkgreen, [indexfile])`; `sphinx/builders/singlehtml.py:95`:
`inline_all_toctrees(self, set(), master, tree, darkgreen, [master])`).

```python
def derive_master_edge_keys(toctree_includes, master_docname):
    traversed = [master_docname]
    edge_keys = []
    def walk(parent):
        for child in toctree_includes.get(parent, []):
            if child not in traversed:
                edge_keys.append(make_include_edge_key(parent, child, occurrence=0))
                traversed.append(child)
                walk(child)
            # else: already traversed -- dark, no edge emitted (first-encounter-wins)
    walk(master_docname)
    return edge_keys
```

**The forbidden shape, by name and by defect:** a LIFO work-stack fed by forward `.append()`
iteration (`stack = [master]; while stack: p = stack.pop(); for c in children(p): stack.append(c)`)
processes the LAST-listed child of any given parent FIRST, silently reversing sibling order with
NO compile error — reconstructed this session from `git show 8184f4d5^:typsphinx/builder.py`, the
deleted `_compute_master_included_docnames` function (`49-RESEARCH.md` Common Pitfalls 3). This is
a DIFFERENT function solving a DIFFERENT problem (a flat cross-master union for XREF-safety), but
its traversal SHAPE is exactly what COMP-05/SC#3 forbids reusing for this phase's per-master DFS,
which must preserve document order. Genuine recursion (as shown above) or an explicit stack with
children pushed in REVERSE order both correctly preserve document order; a naive forward-push LIFO
stack does not.

**Sphinx's own `document is referenced in multiple toctrees: [...], selecting: X <- Y` message
governs NONE of this** and must NOT be ported. That message comes from `_check_toc_parents`
(`sphinx/environment/__init__.py:942-959`, cited in `PROJECT.md` lines 98-102, not re-read this
task since PROJECT.md's own citation is already a direct source read), which takes a plain
lexicographic `max(parents)` — a DIFFERENT tiebreak than this phase's own first-encounter-wins DFS
— and is never consulted by `assemble_doctree`/`inline_all_toctrees`. The `selecting: X <- Y`
wording must not appear anywhere in this phase's own emitted text, log messages, or code comments
as if it were this phase's own rule.

### The unchanged surfaces

`_compute_relative_include_path()` (`translator.py:4592-4626`, read verbatim this task — a pure
docname-to-docname relative-path computation via `PurePosixPath`) and
`compute_content_include_path()` (`writer.py:25-61`, read verbatim this task — a
`posixpath.relpath()` computation from a wrapper's resolved directory to a content file's own
resolved path) both survive this phase completely untouched. Only the DECISION to emit an
`include()` moves (from unconditional, to state-guarded); the path arithmetic behind every
`include()` argument this phase emits is unaffected.

---

## Degenerate-shape outcome table

One row per shape, each carrying the DECIDED outcome and the traversal fact that produces it.
These are transcriptions of D-06 plus D-03, refined where this task's own direct source reading
(`sphinx/directives/other.py`, verbatim, this task) sharpens the mechanism beyond D-06's original
framing — every refinement is called out explicitly below its row.

| Shape | Decided outcome | Traversal fact |
|---|---|---|
| 2-node toctree cycle (master `A` toctrees `B`; `B` toctrees `A`) | **skip** the back edge; compile succeeds; each body appears exactly once; no unbounded recursion | `traversed` is seeded with the master's own docname and appended to before recursion (per the "Traversal rule" above), so when `B`'s own walk reaches `A`, `A` is already in `traversed` and the edge is skipped — `derive_master_edge_keys` terminates because `traversed` only grows |
| Self-referencing toctree (a document toctreeing its own docname, not the `self` magic keyword) | **skip**, silently, via a DIFFERENT mechanism than the cycle case — refined below | Sphinx's OWN `TocTree.parse_content` removes the current document from its candidate pool BEFORE the entry loop even starts (`all_docnames.remove(current_docname)`, `sphinx/directives/other.py:98`), so a literal self-reference is caught by the SAME "reference to nonexisting document" branch a genuinely broken toctree entry would hit — it warns and `continue`s, NEVER reaching `entries` OR `includefiles`. There is nothing for the guard mechanism to see; no guard line is ever emitted for it at all, not even a dark one |
| `self` magic keyword and external-URL entries | **skip, silently, with no new diagnostic** — typsphinx adds no warning Sphinx does not have | `sphinx/directives/other.py:146-149`: `if url_match or ref == 'self': entries.append(...); continue` — never reaches `includefiles`, so D-03's includefiles-only iteration never sees them; no guard line is emitted (see Emission contract, "includefiles rule") |
| `:glob:` toctree | **no special handling needed** — guards emitted in the expanded SORTED order | `sphinx/directives/other.py:109-129`: glob entries are expanded at PARSE time into `sorted(patfilter(all_docnames, pat_name))` and appended to BOTH `entries` and `includefiles` in that sorted order — by the time the builder's DFS or the translator's `visit_toctree` sees the node, a glob toctree is indistinguishable from an explicit toctree listing the same docnames in that same sorted order |
| `:orphan:` document referenced but not toctree'd | **not included** (present in no master's edge set); a cross-reference to it **degrades to plain text** through Phase 48's compile-time guard, per compiled wrapper | The orphaned docname never appears in any `env.toctree_includes[...]` value reachable from any master's DFS seed, so `derive_master_edge_keys` never visits it and no wrapper's published state ever contains a key naming it as a child — no new mechanism; Phase 48's existing `query(<label>).len() > 0` guard already handles a target absent from the compiled document |
| Three or more masters sharing two or more overlapping children | **included** in every master's own PDF — each master's PDF contains each shared child exactly once, at the position its own traversal order dictates — a coverage obligation, not a design question | The SAME algorithm runs once per master with NO special case; each master's `traversed` list is freshly seeded with `[master_docname]` and independent of every other master's walk, so the SAME shared child can be claimed by a DIFFERENT parent in each master with no cross-master coordination needed |
| Duplicate entry inside one toctree directive (same child docname listed twice under one `.. toctree::`) | **included exactly once** | Sphinx warns (`duplicated entry found in toctree: <docname>`) but still appends BOTH occurrences to `includefiles` (`sphinx/directives/other.py:165-177`, the `else` branch only logs, it does not `continue`); the graph side's DFS claims the child at its FIRST occurrence (occurrence 0) and the second occurrence is already `in traversed`, so only the occurrence-0 edge key is ever published — see the Emission contract's worked duplicate-entry example above |

---

## Fixture specification

For each of the ten fixture projects this phase adds, this section fixes the exact source shape
so 49-02, 49-03 and 49-06 build TO this specification rather than the specification being read
back off them. Every expected edge set below is derived BY HAND from the "Traversal rule" and
"Emission contract" sections above, against each fixture's OWN `conf.py`/`.rst` content as
specified here — never against any emitter's output.

### 1. `state_guard_two_master_gate` (COMP-07, COMP-08, COMP-09)

**Docnames:** `index` (root doc, master A), `zmid`, `shared`, `bmaster` (master B, `:orphan:`).

**`conf.py`** (load-bearing properties — do NOT touch any of these, or this fixture silently stops
exercising defect A / the diamond / interleaving):
```python
project = "Two Master Gate"
author = "Probe Author"
extensions = ["typsphinx"]
typst_documents = [
    ("index", "manual.typ", "Two Master Gate — Index", "Probe Author"),
    ("bmaster", "bmanual.typ", "Two Master Gate — B", "Probe Author"),
]
```
Neither target (`manual.typ`, `bmanual.typ`) casefold-equals any docname's own content path
(`index.typ`, `zmid.typ`, `shared.typ`, `bmaster.typ`) — the Phase 47 BLD-03 self-collision
validator would otherwise refuse the build before this fixture ever reaches typst compile.

**`index.rst`** — shaped like Sphinx's own default `index.rst`: prose, one toctree listing `zmid`
then `shared` IN THAT ORDER, then an Indices-and-tables-shaped section:
```rst
Index
=====

PROSE-BEFORE-MARKER

.. toctree::
   :maxdepth: 2

   zmid
   shared

Indices and tables
===================

PROSE-AFTER-MARKER
```

**`zmid.rst`** — toctrees `shared`:
```rst
ZMid
====

.. toctree::
   :maxdepth: 2

   shared
```

**`shared.rst`** — the marker is chosen to match the 2026-08-11 baseline verbatim (PROJECT.md
lines 74-78) so the pre-fix RED this fixture reproduces is directly comparable:
```rst
Shared
======

SHARED-CHAPTER-MARKER
```

**`bmaster.rst`** — `:orphan:` so Sphinx emits no not-in-any-toctree warning:
```rst
:orphan:

BMaster
=======

.. toctree::
   :maxdepth: 2

   shared
```

**Derived edge set, master `index`:** `derive_master_edge_keys` walk: `traversed=[index]`;
child `zmid` not traversed → `index#0>zmid`; `traversed=[index, zmid]`; recurse `zmid`: child
`shared` not traversed → `zmid#0>shared`; `traversed=[index, zmid, shared]`; recurse `shared`: no
children. Back to `index`'s second child `shared` — ALREADY traversed → skip (dark, no edge).
**Edge set(`index`) = `["index#0>zmid", "zmid#0>shared"]`.**

**Derived edge set, master `bmaster`:** `traversed=[bmaster]`; child `shared` not traversed →
`bmaster#0>shared`; `traversed=[bmaster, shared]`; recurse `shared`: no children.
**Edge set(`bmaster`) = `["bmaster#0>shared"]`.**

**Expected observation:** `shared.typ` is byte-identical on disk regardless of which master
compiles it (both compiles read the exact same content file). `SHARED-CHAPTER-MARKER` appears
**exactly once** in EACH master's PDF — in `manual.pdf` via `zmid.typ`'s own guard for
`zmid#0>shared` (the direct guard in `index.typ` for `index#0>shared` stays dark, since `zmid`
claimed `shared` first); in `bmanual.pdf` via `bmaster.typ`'s own direct guard for
`bmaster#0>shared`. Master A's (`manual.pdf`) extracted text order is PROSE-BEFORE-MARKER, ZMid's
heading, SHARED-CHAPTER-MARKER, then PROSE-AFTER-MARKER — document-order interleaving preserved,
the "Indices and tables" section rendering AFTER the toctree's own children, not before.

### 2. `state_guard_mirror_pair_gate` (COMP-10)

**Docnames:** `xmastera` (master A, `root_doc`), `xmasterb` (master B, `:orphan:`), `zmid`,
`shared`.

**`conf.py`:**
```python
project = "Mirror Pair Gate"
author = "Probe Author"
extensions = ["typsphinx"]
root_doc = "xmastera"
typst_documents = [
    ("xmastera", "mastera.typ", "Mirror Pair A", "Probe Author"),
    ("xmasterb", "masterb.typ", "Mirror Pair B", "Probe Author"),
]
```

**`xmastera.rst`** — toctrees `zmid` then `shared`:
```rst
XMasterA
========

.. toctree::
   :maxdepth: 2

   zmid
   shared
```

**`xmasterb.rst`** — `:orphan:`, toctrees `shared` then `zmid` (the MIRRORED order):
```rst
:orphan:

XMasterB
========

.. toctree::
   :maxdepth: 2

   shared
   zmid
```

**`zmid.rst`** — toctrees `shared` (same as fixture 1, reused shape):
```rst
ZMid
====

.. toctree::
   :maxdepth: 2

   shared
```

**`shared.rst`:**
```rst
Shared
======

SHARED-MIRROR-MARKER
```

**Derived edge set, master `xmastera`:** `traversed=[xmastera]`; child `zmid` not traversed →
`xmastera#0>zmid`; `traversed += zmid`; recurse `zmid`: child `shared` not traversed →
`zmid#0>shared`; `traversed += shared`; recurse `shared`: no children. Back to `xmastera`'s
second child `shared` — already traversed → skip. **Edge set(`xmastera`) =
`["xmastera#0>zmid", "zmid#0>shared"]`.** Expected resolved heading-level sequence
(`typst.query(f, "heading", field="level")`): `[1, 2, 3]` — `xmastera` at 1, `zmid` nested at 2,
`shared` nested under `zmid` at 3.

**Derived edge set, master `xmasterb`:** `traversed=[xmasterb]`; child `shared` not traversed
(first in THIS master's own list) → `xmasterb#0>shared`; `traversed += shared`; recurse `shared`:
no children. Next child `zmid` not traversed → `xmasterb#0>zmid`; `traversed += zmid`; recurse
`zmid`: child `shared` ALREADY traversed → skip (dark: `zmid`'s own claim on `shared` is lost).
**Edge set(`xmasterb`) = `["xmasterb#0>shared", "xmasterb#0>zmid"]`.** Expected resolved
heading-level sequence: `[1, 2, 2]` — `xmasterb` at 1, `shared` direct at 2, `zmid` direct and
EMPTY (its own toctree's `shared` claim lost) also at 2.

This reproduces, against this phase's own decided key spellings, both the mirror-pair result
`49-RESEARCH.md` measured independently (Architecture Patterns Pattern 1 / Code Examples) and
PROJECT.md's own LaTeX-builder precedent (lines 88-104): **which position claims a multiply-
reachable document is decided PURELY by the parent's own entry order, never by a "prefer deeper"
heuristic and never by Sphinx's own `selecting: X <- Y` lexicographic tiebreak** — that message
comes from `_check_toc_parents`, a function this phase's DFS never calls and must not imitate.

### 3. `state_guard_self_and_url_gate` (D-03, D-10)

**Docnames:** `index` (root doc, master), `child`.

**`conf.py`:**
```python
project = "Self And URL Gate"
author = "Probe Author"
extensions = ["typsphinx"]
typst_documents = [("index", "manual.typ", "Self And URL Gate", "Probe Author")]
```

**`index.rst`** — one toctree whose entries are, in order: `self`, an external-URL entry with a
title, then `child` listed twice:
```rst
Index
=====

.. toctree::
   :maxdepth: 2

   self
   External Site <https://example.com>
   child
   child
```

**`child.rst`:**
```rst
Child
=====

CHILD-BODY-MARKER
```

**Sphinx's own read-phase behaviour (measured verbatim by `49-RESEARCH.md` Code Examples, this
exact shape):** `entries = [(None, 'self'), ('External Site', 'https://example.com'),
(None, 'child'), (None, 'child')]`; `includefiles = ['child', 'child']` — `self` and the external
URL never reach `includefiles` (D-03's "includefiles rule"); the duplicate `child` entry warns
(`duplicated entry found in toctree: child`) but both occurrences still reach `includefiles`.

**Derived edge set, master `index`:** `traversed=[index]`; first `child` not traversed →
`index#0>child`; `traversed += child`; recurse `child`: no children. Second `child` already
traversed → skip. **Edge set(`index`) = `["index#0>child"]`.**

**Emitted guards in `index.typ` (two lines, per the duplicate-entry occurrence rule):**
```
if "index#0>child" in state("typsphinx:include-edges", ()).get() { include("child.typ") }
if "index#1>child" in state("typsphinx:include-edges", ()).get() { include("child.typ") }
```
Only the first ever fires (the graph side never emits an `index#1>child` key for ANY master); the
second is structurally dark. No guard of any kind is emitted for `self` or the external URL (they
never reach `includefiles`).

**Pre-fix (CURRENT, unfixed tree) behaviour to record as the RED baseline** — reproduced verbatim
in `49-RESEARCH.md` Code Examples against the current unfixed tree: the CURRENT
`translator.py:5095` loop iterates `entries` (not `includefiles`), so it unconditionally emits
`include("self.typ")` and `include("https://example.com.typ")`, neither of which exists on disk;
the CURRENT `_included_docnames` ledger correctly dedups the two `child` entries to one
`include("child.typ")`. Sphinx's own build exits 0 (only the duplicate-entry warning); Typst's
compile aborts: `TypstError: file not found (searched at .../self.typ)`.

**Post-fix expectation:** no guard for `self` or the external URL, `child` included exactly once,
compile succeeds — closing D-10's RED as a structural consequence of D-03, per the "includefiles
rule" above.

### 4. `state_guard_cycle_gate`

**Docnames:** `alpha` (root doc, master), `beta`.

**`conf.py`:**
```python
project = "Cycle Gate"
author = "Probe Author"
extensions = ["typsphinx"]
typst_documents = [("alpha", "manual.typ", "Cycle Gate", "Probe Author")]
```

**`alpha.rst`:**
```rst
Alpha
=====

.. toctree::
   :maxdepth: 2

   beta
```

**`beta.rst`** — toctrees `alpha` back, closing the 2-node cycle:
```rst
Beta
====

.. toctree::
   :maxdepth: 2

   alpha

BETA-BODY-MARKER
```

**Derived edge set, master `alpha`:** `traversed=[alpha]`; child `beta` not traversed →
`alpha#0>beta`; `traversed=[alpha, beta]`; recurse `beta`: child `alpha` ALREADY traversed (seeded
at the very start of the walk) → skip (dark, no edge). **Edge set(`alpha`) =
`["alpha#0>beta"]`.**

`beta.typ`'s own guard for `alpha` (occurrence 0 within `beta`'s own includefiles list,
`beta#0>alpha`) is emitted as a guard line in `beta.typ` (the content file is written
unconditionally, per COMP-01, regardless of what any master's graph derives), but this key is
NEVER published by any master's graph side — `alpha` is always the traversal SEED, never a
"child" claimed by any parent in this graph, so the key `beta#0>alpha` can never appear in any
master's `.update((...))` call. **Expected observation:** compile succeeds, `ALPHA` and
`BETA-BODY-MARKER` each appear exactly once, no unbounded recursion.

### 5. `state_guard_selfref_gate`

**Docnames:** `index` (root doc, master), `other`.

**`conf.py`:**
```python
project = "Self Reference Gate"
author = "Probe Author"
extensions = ["typsphinx"]
typst_documents = [("index", "manual.typ", "Self Reference Gate", "Probe Author")]
```

**`index.rst`** — toctrees ITS OWN docname `index` (a literal self-reference by docname, NOT the
`self` magic keyword covered by fixture 3), plus one ordinary child `other` so the document is not
otherwise empty:
```rst
Index
=====

.. toctree::
   :maxdepth: 2

   index
   other
```

**`other.rst`:**
```rst
Other
=====

OTHER-BODY-MARKER
```

**Sphinx's own read-phase mechanism (refined per the degenerate-shape table above, measured this
task by reading `sphinx/directives/other.py:97-98,151-163` verbatim):** `parse_content` computes
`all_docnames = env.found_docs.copy() | generated_docnames; all_docnames.remove(current_docname)`
ONCE, before the entry loop begins — so for the SAME document's OWN docname, this pre-removal
means the entry `index` (from within `index.rst` itself) is NOT in `frozen_all_docnames`, and the
`if docname not in frozen_all_docnames:` branch fires: Sphinx logs `toctree contains reference to
nonexisting document 'index'` and `continue`s — the self-referencing entry NEVER reaches `entries`
OR `includefiles`. `env.toctree_includes["index"] == ["other"]` — the self-reference is not merely
dark, it is structurally ABSENT.

**Derived edge set, master `index`:** `traversed=[index]`; child `other` (the ONLY entry in
`env.toctree_includes["index"]`) not traversed → `index#0>other`; `traversed=[index, other]`;
recurse `other`: no children. **Edge set(`index`) = `["index#0>other"]`.**

**Emitted guards in `index.typ`:** exactly ONE guard line (`if "index#0>other" in ... {
include("other.typ") }`) — there is no second, dark guard for the self-reference, because there
was never an `includefiles` entry to emit a guard FROM.

**Expected observation:** compile succeeds, `OTHER-BODY-MARKER` appears exactly once, no
duplicate `INDEX` heading, no infinite include chain.

### 6. `state_guard_glob_gate`

**Docnames:** `index` (root doc, master), `guide/alpha`, `guide/mike`, `guide/zulu` — authored on
disk in `zulu, alpha, mike` order (deliberately NOT alphabetical) so the sorted glob expansion is
observable against on-disk/authoring order.

**`conf.py`:**
```python
project = "Glob Gate"
author = "Probe Author"
extensions = ["typsphinx"]
typst_documents = [("index", "manual.typ", "Glob Gate", "Probe Author")]
```

**`index.rst`:**
```rst
Index
=====

.. toctree::
   :glob:
   :maxdepth: 2

   guide/*
```

**`guide/zulu.rst`, `guide/alpha.rst`, `guide/mike.rst`** (files created on disk in this order —
`zulu` first, `alpha` second, `mike` third — the load-bearing property this fixture depends on;
reordering the FILE CREATION does nothing to the expected output, since the glob expansion sorts
by docname, not by creation order, which is precisely the point):
```rst
Zulu
====

ZULU-BODY-MARKER
```
```rst
Alpha
=====

ALPHA-BODY-MARKER
```
```rst
Mike
====

MIKE-BODY-MARKER
```

**Sphinx's own glob expansion (measured verbatim, `sphinx/directives/other.py:109-129`):**
`doc_names = sorted(docname for docname in patfilter(all_docnames, pat_name) ...)` — the glob is
expanded at PARSE time into `["guide/alpha", "guide/mike", "guide/zulu"]` (alphabetical), appended
to BOTH `entries` and `includefiles` in that sorted order, indistinguishable from an explicit
toctree by the time the builder's DFS or the translator's `visit_toctree` ever sees the node.

**Derived edge set, master `index`:** `traversed=[index]`; children in
`env.toctree_includes["index"]` = `["guide/alpha", "guide/mike", "guide/zulu"]` (sorted); none
previously traversed, none have their own children. **Edge set(`index`) =
`["index#0>guide/alpha", "index#0>guide/mike", "index#0>guide/zulu"]`** — in SORTED order.

**Expected observation:** `manual.pdf`'s extracted text order is Alpha, then Mike, then Zulu — the
sorted expansion order, not the on-disk file-creation order — with no special-case handling
required anywhere in the new mechanism, per the Degenerate-shape outcome table's `:glob:` row.

### 7. `state_guard_orphan_ref_gate`

**Docnames:** `index` (root doc, master), `orphan_doc` (`:orphan:`, toctree'd by nobody).

**`conf.py`:**
```python
project = "Orphan Reference Gate"
author = "Probe Author"
extensions = ["typsphinx"]
typst_documents = [("index", "manual.typ", "Orphan Reference Gate", "Probe Author")]
```

**`index.rst`** — no toctree at all, only a cross-reference to a label defined in the orphan:
```rst
Index
=====

See :ref:`orphan-target-label`.
```

**`orphan_doc.rst`:**
```rst
:orphan:

Orphan Doc
==========

.. _orphan-target-label:

Orphan Section
--------------

ORPHAN-BODY-MARKER
```

**Derived edge set, master `index`:** `env.toctree_includes["index"] == []` (no toctree directive
in `index.rst` at all). `traversed=[index]`; no children to walk. **Edge set(`index`) = `[]`**
(the empty array literal, `()`).

**Expected observation:** `orphan_doc.typ` is written unconditionally (COMP-01) but is included by
NO wrapper's published state — `ORPHAN-BODY-MARKER` never appears in `manual.pdf`. The
`:ref:`orphan-target-label`` cross-reference degrades to plain text via Phase 48's existing
compile-time `query(<label>).len() > 0` guard (the label is never defined anywhere in `index`'s
own compiled document, since `orphan_doc.typ` is never `#include()`d into it) — no new mechanism.

### 8. `state_guard_three_master_gate`

**Docnames:** `m1` (root doc, master A), `m2` (master B, `:orphan:`), `m3` (master C,
`:orphan:`), `mid`, `common_a`, `common_b`.

**`conf.py`:**
```python
project = "Three Master Gate"
author = "Probe Author"
extensions = ["typsphinx"]
root_doc = "m1"
typst_documents = [
    ("m1", "manual1.typ", "Three Master Gate — M1", "Probe Author"),
    ("m2", "manual2.typ", "Three Master Gate — M2", "Probe Author"),
    ("m3", "manual3.typ", "Three Master Gate — M3", "Probe Author"),
]
```

**`m1.rst`** — toctrees `mid` then `common_a`:
```rst
M1
==

.. toctree::
   :maxdepth: 2

   mid
   common_a
```

**`m2.rst`** — `:orphan:`, toctrees `common_a` then `common_b`:
```rst
:orphan:

M2
==

.. toctree::
   :maxdepth: 2

   common_a
   common_b
```

**`m3.rst`** — `:orphan:`, toctrees `common_b` then `mid`:
```rst
:orphan:

M3
==

.. toctree::
   :maxdepth: 2

   common_b
   mid
```

**`mid.rst`** — toctrees `common_b`:
```rst
Mid
===

.. toctree::
   :maxdepth: 2

   common_b
```

**`common_a.rst`:**
```rst
Common A
========

COMMON-A-MARKER
```

**`common_b.rst`:**
```rst
Common B
========

COMMON-B-MARKER
```

**Derived edge set, master `m1`:** `traversed=[m1]`; child `mid` not traversed → `m1#0>mid`;
`traversed += mid`; recurse `mid`: child `common_b` not traversed → `mid#0>common_b`;
`traversed += common_b`; recurse `common_b`: no children. Back to `m1`'s second child `common_a`
not traversed → `m1#0>common_a`; `traversed += common_a`; recurse: no children.
**Edge set(`m1`) = `["m1#0>mid", "mid#0>common_b", "m1#0>common_a"]`.** `common_b` claimed by
`mid` (nested).

**Derived edge set, master `m2`:** `traversed=[m2]`; child `common_a` not traversed →
`m2#0>common_a`; `traversed += common_a`; recurse: no children. Child `common_b` not traversed →
`m2#0>common_b`; `traversed += common_b`; recurse: no children. **Edge set(`m2`) =
`["m2#0>common_a", "m2#0>common_b"]`.** `common_b` claimed DIRECTLY by `m2`.

**Derived edge set, master `m3`:** `traversed=[m3]`; child `common_b` not traversed →
`m3#0>common_b`; `traversed += common_b`; recurse: no children. Child `mid` not traversed →
`m3#0>mid`; `traversed += mid`; recurse `mid`: child `common_b` ALREADY traversed → skip (dark:
`mid#0>common_b` is never published by `m3`, even though `mid.typ` carries that exact guard line
on disk — the SAME content file, shared across all three masters). **Edge set(`m3`) =
`["m3#0>common_b", "m3#0>mid"]`.** `common_b` claimed DIRECTLY by `m3`.

**Expected observation:** `common_b` is claimed by a DIFFERENT parent in each master —  `mid` (in
`m1`), `m2` itself (in `m2`), `m3` itself (in `m3`) — three distinct parents across three distinct
masters, with NO cross-master coordination in the algorithm (each master's `traversed` list is
independently seeded and never shared). `COMMON-B-MARKER` appears exactly once in each of
`manual1.pdf`, `manual2.pdf`, `manual3.pdf`. This is the coverage obligation proving the fix is
not 2-master-specific.

### 9. `state_guard_substring_key_gate` (D-09/Probe 6's semantics, reproduced in a realistic
fixture rather than an artificial one)

**Docnames:** `index` (root doc, master), `guideext` (a proper prefix-extension of `guide` —
`"guide"` is a literal prefix of `"guideext"`), `guide`.

**`conf.py`:**
```python
project = "Substring Key Gate"
author = "Probe Author"
extensions = ["typsphinx"]
typst_documents = [("index", "manual.typ", "Substring Key Gate", "Probe Author")]
```

**`index.rst`** — toctrees `guideext` FIRST, then `guide` (the plan's own instruction: "a document
whose docname is a proper prefix-extension of another ... and then that shorter-named document"):
```rst
Index
=====

.. toctree::
   :maxdepth: 2

   guideext
   guide
```

**`guideext.rst`** — the longer-named document itself toctrees the shorter-named one:
```rst
GuideExt
========

.. toctree::
   :maxdepth: 2

   guide

GUIDEEXT-SUBSTRING-MARKER
```

**`guide.rst`:**
```rst
Guide
=====

GUIDE-SUBSTRING-MARKER
```

**Derived edge set, master `index`:** `traversed=[index]`; child `guideext` not traversed →
`index#0>guideext`; `traversed += guideext`; recurse `guideext`: child `guide` not traversed →
`guideext#0>guide`; `traversed += guide`; recurse `guide`: no children. Back to `index`'s second
child `guide` — ALREADY traversed → skip (dark: `index#0>guide` never published).
**Edge set(`index`) = `["index#0>guideext", "guideext#0>guide"]`.**

**The substring relationship, stated verbatim:** the DARK, never-published key `"index#0>guide"`
is a proper SUBSTRING of the PUBLISHED key `"index#0>guideext"` — the first 13 characters of
`"index#0>guideext"` are exactly `"index#0>guide"` (since `"guideext"` begins with the literal
prefix `"guide"`). If Typst's array-membership test degraded to substring containment (the
`49-EVIDENCE.md` Probe 5 hazard, which the mandatory trailing-comma construction rule prevents by
construction), the dark guard `if "index#0>guide" in state(...).get() { include("guide.typ") }`
in `index.typ` would INCORRECTLY fire against the published `"index#0>guideext"` string. With the
array correctly constructed (Probe 6 semantics), it does not: `"index#0>guide"` is not an ELEMENT
of the array `["index#0>guideext", "guideext#0>guide"]`, only a substring of one of its elements —
array membership is exact-element equality, never substring containment.

**Expected observation:** `GUIDE-SUBSTRING-MARKER` appears exactly ONCE in `manual.pdf`, reached
via `guideext.typ`'s own guard for `guideext#0>guide` (nested, at the deeper heading level under
`GuideExt`) — NOT via `index.typ`'s own direct (dark) guard for `index#0>guide`. This proves the
dark guard correctly did not fire, in a realistic fixture where the substring relationship arises
naturally from first-encounter-wins semantics rather than being manufactured artificially.

### 10. `state_guard_numref_two_case_gate` (Open Question #2, `49-06`'s own fixture)

**Docnames:** `index` (root doc, master A), `other_master` (master B, `:orphan:`),
`shared_fig_doc` (contains figure `fig-x`, toctree'd by BOTH masters at different traversal
positions), `only_doc` (contains figure `fig-y`, toctree'd ONLY by `other_master`).

**`conf.py`:**
```python
project = "Numref Two Case Gate"
author = "Probe Author"
extensions = ["typsphinx"]
root_doc = "index"
numfig = True
typst_documents = [
    ("index", "manual.typ", "Numref Two Case Gate — Index", "Probe Author"),
    ("other_master", "manual2.typ", "Numref Two Case Gate — Other", "Probe Author"),
]
```

**`index.rst`** — toctrees `shared_fig_doc` (its only child), references `fig-x`:
```rst
Index
=====

.. toctree::
   :maxdepth: 2

   shared_fig_doc

Case (a) reference: :numref:`fig-x`.
```

**`other_master.rst`** — `:orphan:`, toctrees `only_doc` FIRST then `shared_fig_doc` — the
DIFFERENT traversal position relative to `index`'s own placement of `shared_fig_doc` — references
BOTH `fig-x` (case a) and `fig-y` (case b):
```rst
:orphan:

Other Master
============

.. toctree::
   :maxdepth: 2

   only_doc
   shared_fig_doc

Case (a) reference: :numref:`fig-x`. Case (b) reference: :numref:`fig-y`.
```

**`shared_fig_doc.rst`** — figure `fig-x`, its own caption text fixed here:
```rst
Shared Fig Doc
==============

.. figure:: /_static/placeholder.png
   :name: fig-x

   Figure X Caption
```

**`only_doc.rst`** — figure `fig-y`, its own caption text fixed here, toctree'd ONLY from
`other_master`, never from `index`/`root_doc`:
```rst
Only Doc
========

.. figure:: /_static/placeholder.png
   :name: fig-y

   Figure Y Caption
```

**Derived edge set, master `index`:** `traversed=[index]`; child `shared_fig_doc` not traversed →
`index#0>shared_fig_doc`; `traversed += shared_fig_doc`; recurse: no children.
**Edge set(`index`) = `["index#0>shared_fig_doc"]`.**

**Derived edge set, master `other_master`:** `traversed=[other_master]`; child `only_doc` not
traversed (listed FIRST) → `other_master#0>only_doc`; `traversed += only_doc`; recurse: no
children. Child `shared_fig_doc` not traversed (listed SECOND) →
`other_master#0>shared_fig_doc`; `traversed += shared_fig_doc`; recurse: no children.
**Edge set(`other_master`) = `["other_master#0>only_doc", "other_master#0>shared_fig_doc"]`.**

**The two `:numref:` cases this fixture exists to measure (49-06's own job to run and record —
NOT re-derived numerically here, per `49-RESEARCH.md` Open Question 1's own acknowledgment that
the exact typsphinx-side fallback text is not fully traced):**

- **Case (a) — differing numbers:** `fig-x` (in `shared_fig_doc`) is reachable from BOTH masters.
  `env.toc_fignumbers` is populated by a SINGLE walk rooted ONLY at `root_doc` (`index`) —
  measured this task from `49-RESEARCH.md`'s own direct read of
  `sphinx/environment/collectors/toctree.py:372-373` — so Sphinx bakes ONE literal number into
  BOTH masters' `:numref:` reference text (identical text in both, since numref substitution is
  not master-aware). Typst's OWN `figure()` numbering is a separate, PER-COMPILED-WRAPPER counter:
  in `index`'s compile, `fig-x` is Typst's figure 1 (its only figure); in `other_master`'s compile,
  `fig-x` is Typst's figure 2 (`fig-y`, listed first via `only_doc`, is Typst's figure 1). The two
  masters' compiled captions therefore disagree with EACH OTHER (and at least one disagrees with
  the single Sphinx-baked reference text) — this is the "numbers differ" case.
- **Case (b) — no number assigned at all:** `fig-y` (in `only_doc`) is NEVER reached by the
  `root_doc`-rooted `env.toc_fignumbers` walk (it is toctree'd only from `other_master`, which is
  not `root_doc`). `get_fignumber()` raises on the missing entry, and `_resolve_numref_xref()`
  catches this and falls back to the reference's own literal `contnode` text with **zero
  warning** — even though `fig-y`'s figure body physically appears in `other_master.pdf` (via this
  phase's own state-guard mechanism, `other_master#0>only_doc`) and Typst assigns it its own
  number there. The `:numref:` reference site's rendered text is therefore NOT a number at all,
  and does not match Typst's own assigned number either.

Both figures' names (`fig-x`, `fig-y`), both captions, and both `:numref:` reference sites are
fixed above; the exact rendered fallback text for case (b) and the exact compiled numbers for case
(a) are 49-06's own measurement (real `sphinx-build` + `typst.compile()` + `pypdf`), not derived
here.

---

## Assertions that must NOT change

The following survive this phase's blast radius byte-identical, and no plan in this phase may
treat a change to any of them as in-scope:

- **The heading-offset emission (D-08)** — one `set heading(offset: heading.offset + 1)` per
  toctree, inside the `context { ... }` block, unchanged in wording or position. The per-entry
  guard is added INSIDE this existing block, never wrapped around it.
- **`_compute_relative_include_path()`** (`translator.py:4592-4626`) — the docname-to-docname
  relative-path computation for every `include()` argument.
- **`compute_content_include_path()`** (`writer.py:25-61`) — the wrapper-to-content relative-path
  computation.
- **`compute_template_import_path_for_dir()`** (`writer.py:64+`) — the wrapper's own
  `_template.typ` import path, a pure depth-count function, untouched by anything in this phase.
- **The wrapper's template application** (`render_wrapper()`'s `#show: project.with(...)` line and
  everything the `TemplateEngine` contributes) — unaffected; only the two lines this contract adds
  (state publication, unchanged `#include()`) touch `render_wrapper()`'s body.
- **The four `@preview` import lines** (`codly`, `codly-languages`, `mitex`, `gentle-clues`) and
  their version pins in every content file's unconditional preamble (D-06 of Phase 47) — this
  phase adds zero new `@preview` packages and zero new version-lockstep sites (ROADMAP binding
  constraint #7).
- **Every existing assertion about a wrapper's `#include(` line, other than the addition of ONE
  preceding publication line directly above it** — the `#include("<content_relative_path>")` line
  itself, and its argument's value, do not change.

---

## Assertion census

Appended by Task 3. This section is the DEFINITIVE list of what 49-04's migration task may touch:
after the emitter lands, a failing test module NOT on this list is an unplanned regression to
investigate, not a migration item. Built by repo-wide grep, never by reading the emitter — no file
under `typsphinx/` or `tests/` was touched to produce this section either
(`git status --porcelain typsphinx/ tests/` prints nothing throughout Task 3).

**Methodology, per ROADMAP.md binding constraint #6 (read verbatim this task, lines 385-394):**
"No laundered gates... Expected wrapper/content structure must be derived from first principles
— from the `typst_documents` config plus the toctree source read literally from the `.rst`
fixtures — and written down before running the new emitter. Prefer structural/regex assertions
over full exact-string diffs; reserve exact strings for what is deterministic by construction...
Copy-pasting the new emitter's output into the 'expected' block proves only that the code does
what the code does." Every FLIPS row below substitutes into the `## Emission contract` above; none
is presented as read from a build.

**Searches run, per milestone invariant #4 (repo-wide, not scoped to `<read_first>`'s named
files):**

1. `grep -rl 'include("' --include=*.py tests/` — literal Typst include call in every Python file
   under `tests/`.
2. `grep -rl 'include("' docs/ examples/` — the same search extended to documentation and example
   projects.
3. `grep -rn '\b_included_docnames\b' typsphinx/ tests/ docs/` — the deleted ledger's EXACT name
   (word-boundary matched, to exclude the unrelated, already-deleted-in-Phase-48
   `master_included_docnames` / `_compute_master_included_docnames` symbols, which a naive
   substring grep for `_included_docnames` also catches as false positives).
4. `grep -rn '\.write_doc(\|\._write_typst_files(' tests/*.py` — direct calls to the per-document
   write path, bypassing the builder's own `write()`.
5. `grep -rn '\.count(.*include\|include.*\.count(' tests/*.py` — assertions that count include
   occurrences rather than test membership.
6. `grep -rln 'addnodes.toctree\|nodes.toctree\|toctree()' tests/` — tests that construct a
   synthetic toctree node by hand.

### 1. `tests/test_toctree_requirement13.py` — FLIPS (whole module; largest single concentration)

Every test function in this module constructs a synthetic `addnodes.toctree()` node and sets ONLY
`toctree["entries"]`, never `toctree["includefiles"]` — SYNTHETIC-NODE, per D-03: post-fix
`visit_toctree` reads `includefiles`, which defaults to empty on a hand-built node with no
`includefiles` key ever set, so every one of these tests would see an EMPTY toctree (immediate
`SkipNode`, zero output) unless fixed.

| Line(s) | Test | Assertion as written | Verdict | New expected value |
|---|---|---|---|---|
| 47-80 | `test_toctree_generates_include_directives` | `'include("intro.typ")' in output` etc. | SYNTHETIC-NODE | Set `toctree["includefiles"] = ["intro", "getting_started", "api"]` alongside `entries`; assertions then SURVIVE (guard lines still contain the substring) |
| 83-113 | `test_toctree_with_heading_offset` | `"context {" in output`; `"{" in output` (loose OR) | SYNTHETIC-NODE (needs `includefiles = ["chapter1"]`); the loose `"{" in output` presence check SURVIVES once fixed (does not count) |
| 116-143 | `test_toctree_with_nested_path` | `'include("chapter1/section.typ")' in output` etc. | SYNTHETIC-NODE — needs `includefiles = ["chapter1/section", "chapter2/sub/content"]` |
| 146-172 | `test_toctree_empty_entries` | `output == ""`; `"include(" not in output` | SURVIVES as written — `entries=[]` with `includefiles` unset both default to empty, so the empty-toctree early-exit fires either way. (Recommend also setting `toctree["includefiles"] = []` explicitly for clarity, not required for correctness.) |
| 175-192 | `test_toctree_skip_node_raised` | `pytest.raises(nodes.SkipNode)` | SURVIVES — `visit_toctree` raises `SkipNode` unconditionally at the end of every code path (empty-entries early exit AND the populated-entries main path both end in `raise nodes.SkipNode`), regardless of this phase's changes |
| 196-238 | `test_toctree_single_content_block_multiple_includes` | `output.count("{") == 1`; `output.count("}") == 1`; then `block_start = output.find("{"); block_end = output.find("}", block_start)`; substring checks within `block_content` | **FLIPS, with a genuine new-shape hazard, not merely a SYNTHETIC-NODE fix.** Post-fix EACH guard emits its OWN `if "<key>" in state(...).get() { include(...) }` — a NESTED `{`/`}` pair per entry — so for 3 entries the brace counts become `output.count("{") == 4` (1 `context {` + 3 guard `{`) and `output.count("}") == 4`, not 1. Additionally the `find("{")`/`find("}", block_start)` pair now captures only up through the FIRST guard's own closing brace — `block_content` would NOT contain `chapter2.typ`/`chapter3.typ` at all, a silent false-negative, not merely a count mismatch. **New expected value:** set `includefiles = ["chapter1", "chapter2", "chapter3"]`; replace the brace-count assertions with `output.count("{") == 4` / `output.count("}") == 4` (1 scope + N guards); replace the `find`-based block extraction with `block_content = output` (the whole output IS the single `context { ... }` scope, guards nested inside it) and keep the three `include("chapterN.typ")` substring-membership checks against the FULL output instead of a truncated slice. |
| 241-277 | `test_toctree_heading_offset_appears_once` | `re.findall(r"set heading\(offset: heading\.offset \+ 1\)", output)` count == 1 | SYNTHETIC-NODE (needs `includefiles` set to `["doc1","doc2","doc3"]`); the offset-line-count assertion itself SURVIVES (D-08: exactly one `set heading(offset:...)` line regardless of entry count, guards do not add a second one) |
| 280-317 | `test_toctree_reduced_line_count` | `5 <= len(lines) <= 6` for 3 entries | SYNTHETIC-NODE (needs `includefiles` set); the LINE COUNT itself SURVIVES — each entry still emits exactly ONE text line (`context {` / `set heading(...)` / 3× guard line / `}` = 6 lines total, same shape as today's `context {` / `set heading(...)` / 3× `include()` / `}`) |
| 320-353 | `test_toctree_single_entry_with_single_block` | `output.count("{") == 1`; `output.count("}") == 1`; `output.count("include(") == 1` | SYNTHETIC-NODE (needs `includefiles = ["single"]`) AND brace-count FLIPS: `output.count("{") == 2` (1 context + 1 guard), `output.count("}") == 2`. `output.count("include(") == 1` SURVIVES (one guard emits exactly one `include(` call). |

### 2. `tests/test_translator.py` — one FLIPS function, rest SURVIVES/out-of-scope

| Line(s) | Test | Assertion as written | Verdict | New expected value |
|---|---|---|---|---|
| 2088-2119 | `test_toctree_generates_outline` | Same synthetic-node shape as class 1 above: `toctree["entries"] = [...]`, `toctree.walkabout(translator)`, then `'include("intro.typ")' in output` etc. | SYNTHETIC-NODE | Set `toctree["includefiles"] = ["intro", "getting_started", "api"]` before `walkabout`; assertions then SURVIVE (no brace-count assertion in this one, only substring membership) |
| (4 total `include("` hits; the other 3 are inside this same function's assertion block) | — | — | — | — |

`test_template_engine.py`'s six `addnodes.toctree()` constructions (lines 523-673) are a SEPARATE,
UNRELATED synthetic-node use — they set `toctree["maxdepth"]`/`["numbered"]`/`["caption"]` and
call `TemplateEngine.extract_toctree_options()`, never `includefiles`/`entries`/`visit_toctree` —
**out of scope**, SURVIVES untouched.

### 3. `tests/test_duplicate_include_label_render_gate.py` — FLIPS (whole module premise migrates)

| Line(s) | Assertion as written | Verdict | New expected value |
|---|---|---|---|
| 166-175 | `include_count = 0; for typ_path in temp_build_dir.rglob("*.typ"): include_count += typ_path.read_text(...).count('include("shared.typ")'); assert include_count == 1` | **FLIPS — MIGRATE, do not delete.** The whole module's premise is the deleted ledger's write-time dedup (docstring line 25 explicitly names `TypstBuilder._included_docnames`, now STALE — see STALE-PROSE below). Post-fix, `shared.typ` gets a STATIC guard line at EVERY emission site regardless of whether it fires — for this fixture's diamond (`shared` reachable directly from the master AND nested under `sub`), that is TWO static occurrences of the literal substring `include("shared.typ")` in the emitted tree (one dark, one live), not one. A raw grep-based count across all `.typ` files no longer proves dedup once the guard model makes text presence and RUNTIME inclusion two different things. | **Migrate to a real-compile invariant**, mirroring COMP-07/COMP-09's own gate pattern: keep the `.typ`-file grep as a STRUCTURAL sanity check but change its expected value to `== 2` (documented as "two static guard sites, only one ever live"), and ADD the load-bearing assertion in its place — `pypdf`-extract `master.pdf`'s text and assert `shared`'s own body marker (already asserted via the `<shared:shared-anchor>` label count at lines 186-193, which itself SURVIVES unchanged) appears exactly ONCE in the COMPILED PDF. This asserts the SAME invariant (no duplicate label, no duplicate visible body) through the state-guard mechanism instead of through the deleted ledger. |
| 186-193 | `shared_text.count("[#metadata(none) <shared:shared-anchor>]") == 1`; `"link(<shared:shared-anchor>" in shared_text` | SURVIVES — `shared.typ`'s own body (the label definition and the same-document `link()`) is completely unaffected by the toctree-emission change; this content lives OUTSIDE any `visit_toctree` guard | — |
| 149-161, 198-206 | `"occurs multiple times" not in result.stderr`; PDF exists/non-empty/`%PDF` magic | SURVIVES — real-compile outcome assertions, unaffected by which mechanism (ledger vs. state) prevents the duplicate | — |

**STALE-PROSE, this module:** line 25, `` `TypstBuilder._included_docnames` `` — the attribute this
phase deletes (COMP-11). Replacement wording: describe the state-guard mechanism (each emission
site's STATIC guard, published per-master as Typst `state`) as the fix instead of the ledger.

### 4. `tests/test_builder.py` — NEEDS-SEEDING (4 sites), one SURVIVES assertion

| Line | Call | Verdict | Remedy |
|---|---|---|---|
| 129 (`test_write_doc_creates_output_file`) | `builder.write_doc("index", sample_doctree)` after `init()` + `prepare_writing()`, WITHOUT `write()` | NEEDS-SEEDING | No seeding action required for correctness: per the "Integration Points" pattern (`init()` declares `self._included_docnames` today; the new per-master edge map follows the same shape, declared with an empty default in `init()` and populated for real in `write()`), `render_wrapper(..., edge_keys=self._master_include_edges.get(docname, ()))` gracefully publishes `()` when `write()` was never called — matching today's `getattr(self.builder, "_included_docnames", None)` graceful-fallback precedent. `sample_doctree` (`tests/conftest.py:22-42`) carries no toctree at all, so no guard is ever emitted for this test regardless. Recorded here as CHECKED, not silently skipped. |
| 155 (`test_write_doc_generates_typst_content`) | Same call | NEEDS-SEEDING | Same remedy. This test's own `'#include("index.typ")' in wrapper_content` assertion (line 179) SURVIVES independently (wrapper's own single include, unaffected by the empty published edge set) |
| 192 (`test_finish_completes_build`) | Same call, then `builder.finish()` | NEEDS-SEEDING | Same remedy — no content assertion at all, only "does not raise" |
| 518 (`test_post_process_images_collects_image_nodes`-adjacent write test) | `builder.write_doc("index", doc)` on a hand-built doctree containing only an `image` node | NEEDS-SEEDING | Same remedy — asserts only `"images/test.png" in builder.images`, unrelated to toctree/include content |

### 5. `tests/test_missing_and_malformed_master_gate.py`, `tests/test_two_layer_output_gate.py` —
mentions of `_write_typst_files()` in comments only (lines 133 and 255 respectively), not direct
calls bypassing `write()` — **SURVIVES**, not NEEDS-SEEDING (no actual write-path bypass).

### 6. Wrapper-only `include("` assertions — SURVIVES across every remaining hit

The following modules' `include("` hits are ALL assertions against a WRAPPER file's own single
`#include("<content>.typ")` line (unaffected — this phase adds only a PRECEDING `#state(...)`
line) or a CONTENT file's substring-membership check (unaffected — the guard line still CONTAINS
the `include("...")` call as a substring). Verified by direct inspection of every hit this task,
not assumed from the file list alone:

| Module | Line(s) | Shape | Verdict |
|---|---|---|---|
| `tests/test_builder_requirement13.py` | 159 | Wrapper `#include("index.typ")` | SURVIVES |
| `tests/test_citation_render_gate.py` | 590-596 | `next(line for line in index_typ.splitlines() if 'include("second.typ")' in line)`, then `assert "<" not in include_line` | SURVIVES — the substituted guard line (`if "index#0>second" in state("typsphinx:include-edges", ()).get() { include("second.typ") }`) contains no `<` character anywhere (the edge-key format uses `#`/`>` only); `next(...)` still finds exactly one matching line for a single toctree entry |
| `tests/test_collision_predicate_completeness_gate.py` | 244 | Wrapper `#include("other.typ")` | SURVIVES |
| `tests/test_default_typst_documents_gate.py` | 142, 180 | Wrapper `#include("index.typ")` (two fixtures) | SURVIVES |
| `tests/test_desc_content_indent_render_gate.py` | 526, 531 | Wrapper `#include(` count == 1 + `#include("index.typ")` | SURVIVES |
| `tests/test_figure_propagated_target_render_gate.py` | 289, 294 | Wrapper `#include(` count == 1 + `#include("index.typ")` | SURVIVES |
| `tests/test_integration_multi_doc.py` | 107-109 | Content-file substring checks (`"chapter1.typ" in content`, `"include(" in content`) | SURVIVES |
| `tests/test_integration_nested_toctree.py` | 119-132, 164-166, 195-201, 263-268, 295-301, 364-365, 392-398 | Content-file relative/absolute path substring checks (present/absent) + wrapper `#include(` count == 1, ×3 fixtures | SURVIVES — every check is either substring membership (present in a guard line) or substring absence (an absolute-path variant never emitted, unaffected) or a wrapper's own single-include count |
| `tests/test_nested_master_render_gate.py` | 249, 285, 355-369, 407-410, 442 | Content-file substring checks + wrapper `#include("api/index.typ")` + `original_text.index('include("usage.typ")') < original_text.index('image("../logo.png")')` source-order check | SURVIVES — the guard wraps the include call as a prefix on the same line, preserving its relative text position ahead of the (unrelated, untouched) image reference |
| `tests/test_paragraph_concat_render_gate.py` | 182, 187 | Wrapper `#include(` count == 1 + `#include("index.typ")` | SURVIVES |
| `tests/test_signature_page_boundary_render_gate.py` | 226, 230 (docstring prose, not an assertion) | — | SURVIVES / not an assertion |
| `tests/test_static_asset_copy_gate.py` | 180, 185-186 | Wrapper `#include(` count == 1 + `#include("index.typ")` | SURVIVES |
| `tests/test_target_name_render_gate.py` | 245 | Wrapper `#include("../index.typ")` | SURVIVES |
| `tests/test_template_import_path.py` | 354, 369 | Wrapper `#include("_template/index.typ")` / `#include("_template/sub/index.typ")` (two entries) | SURVIVES |
| `tests/test_two_layer_output_gate.py` | 167 | Wrapper `"#include(" in content` (membership, not count) | SURVIVES |

### 7. STALE-PROSE

| File | Line(s) | Stale claim | Replacement wording |
|---|---|---|---|
| `tests/test_duplicate_include_label_render_gate.py` | 25 | `` a builder-scoped ledger (``TypstBuilder._included_docnames``, shared across every document composing one master) records each absolute docname the first time it is emitted `` | Replace with: "a per-master Typst `state` array (published by each wrapper, guarded per emission site in the shared content file) resolves which occurrence of a repeated toctree entry is live at COMPILE time, not write time" |
| `tests/test_citation_render_gate.py` | 583-585 | `` visit_toctree reads node['entries'] directly and raises nodes.SkipNode `` | Replace with: "visit_toctree reads node['includefiles'] directly (D-03) and raises nodes.SkipNode" |
| `examples/advanced/README.md` | 113-123 | Shows a PRE-Issue-#7, PRE-D-07 illustrative snippet (`{ #set heading(offset: 1) #include("chapter1.typ") }`, a separate block per entry with an ABSOLUTE offset) — already stale relative to the CURRENT codebase (single consolidated `context { set heading(offset: heading.offset + 1) }` block), and will be EVEN MORE stale once this phase adds the state-guard line. **Out of this phase's own scope** — `49-CONTEXT.md`'s `<domain>` explicitly assigns "documenting the two-layer output shape" to Phase 51, not Phase 49. Recorded here so it is not silently missed, not treated as a Phase 49 migration item. | Deferred to Phase 51: regenerate this example against the current `context {}`/guard shape |

**Excluded as false positives (checked, not genuine stale prose for THIS phase):**
`tests/fixtures/bld03_ghost_entry_xref_gate/conf.py`, `tests/fixtures/bld03_unhashable_docname_gate/conf.py`,
`tests/test_xref_orphan_degrade_render_gate.py` (line 31), `tests/test_label_existence_guard_unit.py`
(lines 53, 411, 414) — all reference `master_included_docnames` /
`_compute_master_included_docnames`, a DIFFERENT symbol already deleted in Phase 48 itself (not
`_included_docnames`, this phase's own ledger). Confirmed via word-boundary grep
(`\b_included_docnames\b`) against `typsphinx/builder.py`/`translator.py`: only
`test_duplicate_include_label_render_gate.py` references the REAL symbol this phase deletes.
Neither `test_xref_orphan_degrade_render_gate.py` nor `test_label_existence_guard_unit.py`
constructs a toctree node or reads `includefiles`/`entries` anywhere — **out of scope**, SURVIVES
untouched, despite being named in this task's own `<read_first>` as "the two Phase 48 modules that
mention the deleted ledger by name" (that framing conflated the two distinct symbols; corrected
here after direct source reading).

### 8. NO-HIT categories, checked and empty

- `grep -rln 'addnodes.toctree\|nodes.toctree\|toctree()' tests/` returned exactly THREE files —
  `test_template_engine.py` (out of scope, class 2 above), `test_toctree_requirement13.py` (class
  1), `test_translator.py` (class 2) — no other synthetic-toctree-node construction exists
  anywhere in the suite.
- `grep -rln '\.write_doc(\|\._write_typst_files(' tests/*.py` returned `test_builder.py` (class
  4, genuine bypass) and `test_missing_and_malformed_master_gate.py` /
  `test_two_layer_output_gate.py` (class 5, comment mentions only, not genuine bypasses) — no
  other test reaches the per-document write path directly.
- `docs/` carries zero `include("` hits.

## How to find any assertion I missed

Re-run these exact commands from the repository root; every hit above traces to one of them:

```bash
grep -rl 'include("' --include=*.py tests/
grep -rl 'include("' docs/ examples/
grep -rn '\b_included_docnames\b' typsphinx/ tests/ docs/
grep -rn '\.write_doc(\|\._write_typst_files(' tests/*.py
grep -rn '\.count(.*include\|include.*\.count(' tests/*.py
grep -rln 'addnodes.toctree\|nodes.toctree\|toctree()' tests/
```

**Numeric summary — the prediction 49-04 is measured against:**

- **Total file-level hits across all six searches:** 21 files carrying a literal `include("`
  substring under `tests/` (19 `.py` test modules + 2 fixture `conf.py` comment blocks), plus 1
  `examples/` doc file, plus 6 files carrying `_included_docnames`-family mentions (2 real, 4
  false-positive), plus 4 write-path mentions (1 genuine bypass module with 4 call sites, 2
  comment-only), plus 3 synthetic-toctree-node modules.
- **SURVIVES:** 16 of the 19 test modules survive their `include("` assertions completely
  unchanged (`test_builder_requirement13.py`, `test_citation_render_gate.py`,
  `test_collision_predicate_completeness_gate.py`, `test_default_typst_documents_gate.py`,
  `test_desc_content_indent_render_gate.py`, `test_figure_propagated_target_render_gate.py`,
  `test_integration_multi_doc.py`, `test_integration_nested_toctree.py`,
  `test_nested_master_render_gate.py`, `test_paragraph_concat_render_gate.py`,
  `test_signature_page_boundary_render_gate.py`, `test_static_asset_copy_gate.py`,
  `test_target_name_render_gate.py`, `test_template_import_path.py`, `test_translator.py`'s
  non-toctree assertions, `test_two_layer_output_gate.py`), plus `test_xref_orphan_degrade_render_gate.py`
  and `test_label_existence_guard_unit.py` (out of scope, false-positive `_included_docnames`
  match) and `test_missing_and_malformed_master_gate.py` (comment-only write-path mention).
- **FLIPS:** 2 modules — `test_toctree_requirement13.py` (9 test functions, all SYNTHETIC-NODE;
  3 of the 9 ALSO carry a brace-count FLIPS; 1 of the 9 carries a genuine block-extraction
  reshape) and `test_duplicate_include_label_render_gate.py` (1 test function, MIGRATE its
  ledger-dedup premise to a real-compile invariant) — plus `test_translator.py`'s single
  `test_toctree_generates_outline` function (SYNTHETIC-NODE).
- **NEEDS-SEEDING:** 1 module, 4 call sites (`test_builder.py` lines 129, 155, 192, 518) — all
  resolved with NO code-side seeding action required (graceful empty-edge-set default, no
  assertion depends on toctree content).
- **SYNTHETIC-NODE:** 10 test functions total across 2 modules (9 in
  `test_toctree_requirement13.py`, 1 in `test_translator.py`), all requiring `toctree["includefiles"]`
  to be set alongside `toctree["entries"]`.
- **STALE-PROSE:** 3 genuine items (`test_duplicate_include_label_render_gate.py:25`,
  `test_citation_render_gate.py:583-585`, `examples/advanced/README.md:113-123`, the last one
  deferred to Phase 51) plus 5 false-positive exclusions recorded and explained (not silently
  dropped).

**Prediction 49-04 is measured against:** after the emitter lands, running
`uv run pytest -m "not slow" -q`, the ONLY new failures should be inside
`test_toctree_requirement13.py` (9 functions) and `test_translator.py::test_toctree_generates_outline`
(SYNTHETIC-NODE, brace-count, and block-extraction FLIPS) and
`test_duplicate_include_label_render_gate.py::TestDuplicateIncludeLabelRenderGate::test_typstpdf_diamond_include_deduplicated`
(the MIGRATE FLIPS). Any OTHER test module failing after 49-04 lands is an unplanned regression,
not a predicted migration item.

---

*This document was written entirely before any file under `typsphinx/` or `tests/` was touched by
this plan — every row above is a prediction, not a report.*
