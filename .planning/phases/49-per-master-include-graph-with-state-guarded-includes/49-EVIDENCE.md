# Phase 49 — Evidence Log

Created by plan 49-01, Task 1. Later plans APPEND new sections to this file — never overwrite it.

## State-syntax measurement

**Purpose:** D-09 records the `#state(<key>, ()).update((...))` / `if <key> in state(<key>,
()).get()` syntax as **unmeasured** and requires it to be verified against a real
`typst.compile()` before any plan depends on it. The two spellings this syntax uses — the
namespaced `state` key (D-07) and the edge key (D-04/D-05) — are Claude's Discretion, so this
measurement is taken against the DECIDED spellings below, not against PROJECT.md's `"inc"` /
`"index>zmid"` sketches, which `49-CONTEXT.md` `<specifics>` explicitly names as superseded.

**Provenance:**

- `typsphinx` package path (worktree isolation confirmed): resolved via `uv run python -c
  "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"` →
  `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae28f6821ca4986fd/typsphinx/__init__.py`
  — the worktree's own copy, not the main checkout.
- Dependency versions read live this session: `typst` `0.15.0`, `sphinx` `9.1.0`, `pypdf`
  `6.14.2` — all match `49-RESEARCH.md`'s own live-verified readings, no drift.
- **No Sphinx build ran** for this section (`git status --porcelain typsphinx/ tests/` prints
  nothing throughout this task) and **no typsphinx emitter ran** — every probe below is a
  throwaway, hand-written `.typ` file exercising the Typst LANGUAGE directly via
  `typst.compile()`/`typst.query()` (typst-py 0.15.0), written under this task's own scratch
  directory (`/tmp/claude-.../scratchpad/49-01-probes/`, outside the repository), never read back
  from any emitter. This does not violate binding constraint #6 (which forbids deriving expected
  TEST values from the new emitter's own output) — these probes derive the SYNTAX contract itself,
  before any code implementing it exists.

**Decided spellings under measurement:**

- **Namespaced state key (D-07):** the literal string `typsphinx:include-edges`. A user-supplied
  `typst_template` is arbitrary Typst and may legitimately call `state("inc")`; a
  project-prefixed key with a separator no bare identifier would use makes a silent collision
  implausible. The bare `"inc"` sketched in PROJECT.md is superseded.
- **Edge key (D-04/D-05):** the format `<parent_docname>#<occurrence>><child_docname>` — parent
  docname, a literal `#`, the 0-based occurrence index of this emission site among the emission
  sites in that parent naming that same child, a literal `>`, then the child docname. For a
  document whose toctree entries are `zmid`, `shared` the keys are `index#0>zmid` and
  `index#0>shared`; for a toctree listing `child` twice they are `index#0>child` and
  `index#1>child`. The graph side always emits occurrence 0 (it claims a child at that child's
  FIRST non-traversed appearance in the parent's ordered list, which is always the first
  appearance), so only occurrence-0 keys can ever appear in a published edge set — which is
  exactly what makes a duplicate emission site (occurrence ≥ 1) structurally dark rather than
  firing a second physical include.

All probe content files below use the top-level MARKUP-mode `#context { ... }` shape (a bare
markup document with a `#`-prefixed context expression) — this is the shape `49-RESEARCH.md`
Architecture Patterns Pattern 1 already independently verified this Typst syntax against, and is
sufficient to measure the guard mechanics this section closes. It is NOT the translator's own
internal `#{ ... }` code-mode body-wrapping (`writer.py:239-240`, `builder.py`'s content-file
assembly) — that wrapping is an unrelated translator implementation detail
(`49-RESEARCH.md` Open Question 2 records this explicitly: "no action needed this phase", since a
bare `context {` with no `#` prefix works correctly ONLY because the translator's own content-file
body is always wrapped in `#{ ... }` before this text is ever emitted). Both forms are valid
Typst; the markup-mode form is the simpler, already-precedented probe shape and changes nothing
about the syntax under test (the `state`/`context`/`if ... in ... .get()` mechanics are identical
either way).

### Probe 1 — Arity 0 (empty edge set)

**Source (verbatim), wrapper (`root.typ`):**
```typst
#state("typsphinx:include-edges", ()).update(())
#include("content0.typ")
```
**Source (verbatim), content (`content0.typ`):**
```typst
= Doc0

#context {
  if "index#0>child" in state("typsphinx:include-edges", ()).get() { include("child0.typ") }
}
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted text: `"Doc0"` — the child's
marker is ABSENT (`child0.typ`'s `CHILD0-MARKER` never appears), confirming the empty-array
default correctly makes every guard false with no compile error.

### Probe 2 — Arity 1 (one edge key, with the required trailing comma)

**Source (verbatim), wrapper:**
```typst
#state("typsphinx:include-edges", ()).update(("index#0>child",))
#include("content1.typ")
```
**Source (verbatim), content:**
```typst
= Doc1

#context {
  if "index#0>child" in state("typsphinx:include-edges", ()).get() { include("child1.typ") }
}
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted text: `"Doc1\nChild1\nCHILD1-
MARKER"` — the child's marker is PRESENT exactly once.

### Probe 3 — Arity 2 and Arity 3 (unconditional trailing comma after the LAST element)

**Source (verbatim), arity-2 wrapper:**
```typst
#state("typsphinx:include-edges", ()).update(("index#0>a", "index#0>b",))
#include("content2.typ")
```
**Source (verbatim), arity-2 content:**
```typst
= Doc2

#context {
  if "index#0>a" in state("typsphinx:include-edges", ()).get() { include("child2a.typ") }
  if "index#0>b" in state("typsphinx:include-edges", ()).get() { include("child2b.typ") }
}
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted text: `"Doc2\nChild2A\nCHILD2A-
MARKER\nChild2B\nCHILD2B-MARKER"` — both children present exactly once.

**Source (verbatim), arity-3 wrapper:**
```typst
#state("typsphinx:include-edges", ()).update(("index#0>a", "index#0>b", "index#0>c",))
#include("content3.typ")
```
**Source (verbatim), arity-3 content:**
```typst
= Doc3

#context {
  if "index#0>a" in state("typsphinx:include-edges", ()).get() { include("child3a.typ") }
  if "index#0>b" in state("typsphinx:include-edges", ()).get() { include("child3b.typ") }
  if "index#0>c" in state("typsphinx:include-edges", ()).get() { include("child3c.typ") }
}
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted text: `"Doc3\nChild3A\nCHILD3A-
MARKER\nChild3B\nCHILD3B-MARKER\nChild3C\nCHILD3C-MARKER"` — all three children present exactly
once.

**Measurement:** a trailing comma after the last element compiles cleanly at arity 2 and arity 3
exactly as it does at arity 1 (Probe 2) and arity 0's own always-empty `()` form (Probe 1). The
uniform rendering rule this licenses — `()` for zero keys, and for one-or-more keys a
parenthesized comma-separated list of double-quoted keys with an UNCONDITIONAL trailing comma
after the last element — therefore needs no `len(keys) == 1` special case; the same construction
rule is correct at every arity.

### Probe 4 — Type-and-length readback at every arity (0, 1, 2, 3)

**Source (verbatim), arity 0:**
```typst
#state("typsphinx:include-edges", ()).update(())
#context [TYPE=#repr(type(state("typsphinx:include-edges", ()).get())) LEN=#state("typsphinx:include-edges", ()).get().len()]
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted text: `"TYPE=array LEN=0"`.

**Source (verbatim), arity 1 — the load-bearing case:**
```typst
#state("typsphinx:include-edges", ()).update(("index#0>child",))
#context [TYPE=#repr(type(state("typsphinx:include-edges", ()).get())) LEN=#state("typsphinx:include-edges", ()).get().len()]
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted text: `"TYPE=array LEN=1"` —
**the type reads as Typst's array type at arity 1**, confirmed by the recorded probe source
reproducing this result when re-run. This is the load-bearing result: it is the shape every
single-master, single-edge project hits on every build, and it is exactly the shape RESEARCH
Pitfall 1 warns is silently degraded to a string if the trailing comma is omitted (Probe 6 below).

**Source (verbatim), arity 2:**
```typst
#state("typsphinx:include-edges", ()).update(("index#0>a", "index#0>b",))
#context [TYPE=#repr(type(state("typsphinx:include-edges", ()).get())) LEN=#state("typsphinx:include-edges", ()).get().len()]
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted text: `"TYPE=array LEN=2"`.

**Source (verbatim), arity 3:**
```typst
#state("typsphinx:include-edges", ()).update(("index#0>a", "index#0>b", "index#0>c",))
#context [TYPE=#repr(type(state("typsphinx:include-edges", ()).get())) LEN=#state("typsphinx:include-edges", ()).get().len()]
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted text: `"TYPE=array LEN=3"`.

**Measurement:** at every arity 0-3, the published state's Typst type reads as `array` and its
length equals the input key count exactly.

### Probe 5 — The no-trailing-comma counter-probe (recording the hazard, not adopting it)

**Source (verbatim), the SAME arity-1 wrapper as Probe 2/4 with the trailing comma removed, using
the decided key format for both the published key and the substring test:**
```typst
#state("typsphinx:include-edges", ()).update(("index#0>child"))
#context [TYPE=#repr(type(state("typsphinx:include-edges", ()).get()))]
#context [SUBSTRING-TEST=#("0>child" in state("typsphinx:include-edges", ()).get())]
```
**Compile result:** `typst.compile()` succeeds — **exit 0, NO error of any kind.**
`pypdf`-extracted text: `"TYPE=str SUBSTRING-TEST=true"`.

**This is the silent-corruption hazard, recorded verbatim, not adopted:** omitting the one-element
array's trailing comma is not a syntax error at all — Typst parses `("index#0>child")` as a
**parenthesized string expression**, not a one-element array, and `state(...).update()` performs
no runtime type check against its default value's type. The published state's Typst type reads as
`str`, not `array`. The guard `"0>child" in state(...).get()` — a proper substring of the
published string `"index#0>child"` — then reads `true`: the `in` operator is polymorphic (array
membership vs. string containment), so this degraded state silently satisfies membership for ANY
key that happens to be a substring of the one published string. This is the exact hazard
`49-RESEARCH.md` Common Pitfalls 1 predicted, now reproduced in this phase's own decided key
spelling rather than merely cited from research.

### Probe 6 — The dark-guard substring case, in the decided key format

**Source (verbatim), wrapper publishing two keys where one is a proper substring of the other
(`"index#0>guide"` is a proper substring of `"index#0>guide2"`):**
```typst
#state("typsphinx:include-edges", ()).update(("index#0>guide", "index#0>guide2",))
#include("content_substring.typ")
```
**Source (verbatim), content — a THIRD guard whose key `"0>guide"` is a proper substring of the
published `"index#0>guide"` and must NOT fire:**
```typst
= DocSubstring

#context {
  if "index#0>guide" in state("typsphinx:include-edges", ()).get() { include("guide_child.typ") }
  if "index#0>guide2" in state("typsphinx:include-edges", ()).get() { include("guide2_child.typ") }
  if "0>guide" in state("typsphinx:include-edges", ()).get() { include("dark_child.typ") }
}
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted text: `"DocSubstring\nGuide\n
GUIDE-MARKER\nGuide2\nGUIDE2-MARKER"` — **the dark child's marker
(`DARK-CHILD-MARKER-MUST-NOT-APPEAR`) is ABSENT** from the compiled PDF's extracted text, while
both correctly-keyed children's markers ARE present. This is the semantics proof, in the decided
key format, that the guard — with the trailing comma correctly present — tests ARRAY membership,
not string containment: the third guard's key is a genuine substring of a published key, and it
correctly does not fire.

### Probe 7 — The line-break rule (RESEARCH Pitfall 2 / Phase 48 D-08, re-confirmed for this
phase's `if` chains)

**Source (verbatim), condition and opening brace on ONE unbroken line — expected: compiles:**
```typst
#state("typsphinx:include-edges", ()).update(("index#0>child",))
#context {
  if "index#0>child" in state("typsphinx:include-edges", ()).get() { [ok] }
}
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted text: `"ok"`.

**Source (verbatim), a newline inserted between the condition and its opening brace — expected:
the parser's expected-block error:**
```typst
#state("typsphinx:include-edges", ()).update(("index#0>child",))
#context {
  if "index#0>child" in state("typsphinx:include-edges", ()).get()
  { [ok] }
}
```
**Compile result:** `typst.compile()` FAILS. Verbatim error: `expected block`.

**Measurement:** the emitted-bytes property is measured, not assumed — every `if "<key>" in
state(...).get() { include(...) }` line this phase's translator emits must keep the condition and
its opening `{` on one unbroken statement.

### Probe 8 — Interleaving and outline reachability, in the decided spellings

**Source (verbatim), wrapper — `#outline()` placed BEFORE the `#include(...)`:**
```typst
#state("typsphinx:include-edges", ()).update(("index#0>child",))
#outline()
#include("content_interleave.typ")
```
**Source (verbatim), content — prose before and after the guarded block, guarded child carries a
labelled heading:**
```typst
= Index

PROSE-BEFORE-MARKER

#context {
  if "index#0>child" in state("typsphinx:include-edges", ()).get() { include("interleave_child.typ") }
}

PROSE-AFTER-MARKER
```
**Source (verbatim), guarded child:**
```typst
= InterleaveChild <interleave-child-label>

CHILD-BODY-MARKER
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted body text (outline table
stripped): `"Index\nPROSE-BEFORE-MARKER\nInterleaveChild\nCHILD-BODY-MARKER\nPROSE-AFTER-MARKER"`
— the extracted text order puts the prose-before marker, then the child's body, then the
prose-after marker, exactly at the toctree's own position in document order.

**`typst.query(f, "heading")` result (verbatim, JSON), confirming outline reachability:**
```json
[
  {"func": "heading", "level": 1, "body": {"func": "text", "text": "Contents"}, "outlined": false, ...},
  {"func": "heading", "level": 1, "body": {"func": "text", "text": "Index"}, "outlined": true, ...},
  {"func": "heading", "level": 1, "body": {"func": "text", "text": "InterleaveChild"},
   "outlined": true, "label": "<interleave-child-label>", ...}
]
```
The outline (placed BEFORE the include in source order) correctly lists the conditionally included
`InterleaveChild` heading — Typst's multi-pass layout resolves the forward reference. A
label-selector query (`typst.query(f, "<interleave-child-label>")`) independently finds exactly
one match, carrying `"body": {"text": "InterleaveChild"}` — the guarded child's labelled heading
is fully `query()`-reachable, not merely visually present.

### Probe 9 — Standalone content-file compile (no wrapper)

**Source (verbatim), compiled directly with no wrapper file:**
```typst
= StandaloneDoc

#context {
  if "index#0>child" in state("typsphinx:include-edges", ()).get() { include("standalone_child.typ") }
}
```
**Compile result:** `typst.compile()` succeeds. `pypdf`-extracted text: `"StandaloneDoc"` — **no
child is included.** With no wrapper ever calling `.update(...)`, `state(...).get()` returns its
declared default `()`, so every guard is false and the compile still succeeds. This is the
documented standalone-compile behaviour Phase 51 writes up, now measured against this phase's own
decided spellings rather than PROJECT.md's sketch.

### D-09 closed for this phase's own spellings

Every arity of the array-literal rule (Probes 1-4), the trailing-comma silent-corruption hazard
(Probe 5), the dark-guard substring semantics (Probe 6), the line-break rule (Probe 7), the
interleaving/outline/label-reachability behaviour (Probe 8), and the standalone-compile behaviour
(Probe 9) are all recorded above as verbatim real-compile transcripts, against the DECIDED state
key `typsphinx:include-edges` (D-07) and the DECIDED edge-key format
`<parent_docname>#<occurrence>><child_docname>` (D-04/D-05) — not against PROJECT.md's `"inc"` /
`"index>zmid"` sketches. D-09's syntax question is CLOSED for this phase's own spellings. No file
under `typsphinx/` or `tests/` was touched to produce this section.
