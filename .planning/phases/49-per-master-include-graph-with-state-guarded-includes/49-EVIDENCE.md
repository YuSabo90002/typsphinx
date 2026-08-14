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

---

## Removal and invariant sweep

**Written by 49-05, Task 2.** Every command below is run over the WHOLE tree, not scoped to files
a requirement happens to name (ROADMAP milestone invariant #4, this phase's own SC#4). Every
command line and its verbatim output is pasted below, captured against this plan's own worktree
after 49-04 landed the emitter.

### 1. The deleted ledger attribute, at three scopes

**Scope A — the production package alone (must be empty):**
```
$ grep -rn '\b_included_docnames\b' typsphinx/
```
```
(no output)
```

**Scope B — the whole tree excluding `.planning/` (must be empty except this phase's own
removal-gate test, which names the deleted attribute as a single documented constant per its own
module docstring — see `tests/test_include_ledger_removal_gate.py`'s own repo-wide prose test,
which excludes itself from its own scan and passes):**
```
$ grep -rn '\b_included_docnames\b' typsphinx/ tests/ docs/ examples/
```
```
tests/test_include_ledger_removal_gate.py:90:DELETED_LEDGER_ATTRIBUTE = "_included_docnames"
```
The single hit is this plan's own removal gate's module-level constant (the ONE place this
module's own text carries the literal spelling, per its own docstring contract) — not a
reintroduction of the deleted symbol into production or test-assertion code.

A non-word-boundary grep also surfaces a DIFFERENT, already-Phase-48-deleted symbol
(`master_included_docnames` / `_compute_master_included_docnames`, which merely ends in the same
suffix) — recorded here so a future reader does not mistake these for a live reference to THIS
phase's own deleted ledger:
```
$ grep -rn '_included_docnames' typsphinx/ tests/ docs/ examples/
```
```
tests/test_label_existence_guard_unit.py:53:    ``typst_documents``, not the deleted ``master_included_docnames``,
tests/test_label_existence_guard_unit.py:411:            if "master_included_docnames" in text:
tests/test_label_existence_guard_unit.py:414:            f"deleted attribute 'master_included_docnames' still mentioned "
tests/test_include_ledger_removal_gate.py:90:DELETED_LEDGER_ATTRIBUTE = "_included_docnames"
tests/test_xref_orphan_degrade_render_gate.py:31:computation, ``TypstBuilder.master_included_docnames``, is deleted; Phase 47's
tests/fixtures/bld03_ghost_entry_xref_gate/conf.py:2:# gate -- the FIFTH site, `_compute_master_included_docnames()`, does not
tests/fixtures/bld03_ghost_entry_xref_gate/conf.py:5:# to `master_included_docnames`, even though `_validate_output_path_
tests/fixtures/bld03_unhashable_docname_gate/conf.py:2:# the FIFTH site, `_compute_master_included_docnames()`, builds its masters
```
Every hit besides this plan's own constant assignment names the DIFFERENT, Phase-48-deleted
symbol (`master_included_docnames` family), confirmed by `49-04-SUMMARY.md`'s own recorded
false-positive lesson and re-confirmed here by direct inspection of each line.

**Scope C — the planning directory (expected non-empty — its own history legitimately records the
deleted symbol; this scope is deliberately NOT swept for absence):**
```
$ grep -rl '_included_docnames' .planning/ | wc -l
```
```
89
```
89 planning files (PLAN.md/SUMMARY.md/EVIDENCE.md/RESEARCH.md artifacts across this and prior
phases) legitimately narrate the deleted ledger's own removal — this is history, not a live
reference, and is excluded from the "must be empty" scopes above by design (see
`tests/test_include_ledger_removal_gate.py`'s own `REPO_WIDE_SCAN_ROOTS` comment).

### 2. Every include call inside the toctree visitor's own body

```
$ uv run python3 -c "
import ast, inspect, re, textwrap
from typsphinx.translator import TypstTranslator
raw = inspect.getsource(TypstTranslator.visit_toctree)
dedented = textwrap.dedent(raw)
tree = ast.parse(dedented)
doc_node = tree.body[0].body[0]
docstring_range = (doc_node.lineno, doc_node.end_lineno)
lines = dedented.splitlines()
pattern = re.compile(r'\binclude\s*\(')
for i, line in enumerate(lines, start=1):
    if docstring_range[0] <= i <= docstring_range[1]:
        continue
    if line.strip().startswith('#'):
        continue
    if pattern.search(line):
        print(i, line)
print('DONE')
"
```
```
DONE
```
Zero non-comment, non-docstring lines inside `visit_toctree`'s own body contain a raw
`include(...)` call — every include this visitor emits is constructed exclusively through
`render_include_guard()` (confirmed present in the function's source:
`"render_include_guard(" in inspect.getsource(TypstTranslator.visit_toctree)` → `True`) and
`_compute_relative_include_path()`. This is the SAME structural check
`tests/test_include_ledger_removal_gate.py::TestToctreeVisitorEmitsNoUnconditionalInclude` runs on
every commit.

### 3. Every distinct state-key literal in the production package

```
$ uv run python /tmp/.../probe_state_collect.py   # ast-based collector, walking every
                                                     # state(...) call site's first argument
                                                     # across typsphinx/*.py
```
```
literals: {'typsphinx:include-edges'}
```
Exactly ONE distinct literal, collected structurally (not by counting occurrences of one known
string) — matching `INCLUDE_STATE_KEY`, the contract's own spelling (D-07).

### 4. The `@preview` package count across every declaring surface

```
$ grep -n '@preview/codly\|@preview/mitex\|@preview/gentle-clues' \
    typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ
```
```
typsphinx/templates/base.typ:8:#import "@preview/codly:1.3.0": *
typsphinx/templates/base.typ:9:#import "@preview/codly-languages:0.1.10": *
typsphinx/templates/base.typ:14:#import "@preview/mitex:0.2.7": *
typsphinx/templates/base.typ:19:#import "@preview/gentle-clues:1.3.1": *
typsphinx/writer.py:250:        imports.append('#import "@preview/codly:1.3.0": *')
typsphinx/writer.py:251:        imports.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/writer.py:252:        imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/writer.py:253:        imports.append('#import "@preview/gentle-clues:1.3.1": *')
typsphinx/template_engine.py:643:            output_parts.append('#import "@preview/codly:1.3.0": *')
typsphinx/template_engine.py:644:            output_parts.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/template_engine.py:645:            output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/template_engine.py:646:            output_parts.append('#import "@preview/gentle-clues:1.3.1": *')
```
All three declaring surfaces agree: four packages (`codly` 1.3.0, `codly-languages` 0.1.10,
`mitex` 0.2.7, `gentle-clues` 1.3.1), byte-identical version pins. The `examples/` tree carries the
SAME four packages at the SAME versions, plus one UNRELATED user-supplied package
(`@preview/charged-ieee:0.1.4`, a documented `typst_package`/custom-template example, not one of
typsphinx's own four bundled imports):
```
$ grep -rn '@preview/' examples/ | grep -v '\.pdf'
```
```
examples/advanced/_templates/custom.typ:12:#import "@preview/codly:1.3.0": *
examples/advanced/_templates/custom.typ:13:#import "@preview/codly-languages:0.1.10": *
examples/advanced/_templates/custom.typ:14:#import "@preview/mitex:0.2.7": *
examples/advanced/_templates/custom.typ:15:#import "@preview/gentle-clues:1.3.1": *
examples/advanced/README.md:253:#     '#import "@preview/codly:1.3.0": *',
examples/advanced/README.md:254:#     '#import "@preview/gentle-clues:1.3.1": *',
examples/charged-ieee/approach2/source/_templates/_template.typ:5:#import "@preview/charged-ieee:0.1.4": ieee
examples/charged-ieee/approach2/conf.py:22:# imports "@preview/charged-ieee:0.1.4" itself, and setting typst_package would
examples/charged-ieee/README.md:78:#import "@preview/charged-ieee:0.1.4": ieee
examples/charged-ieee/approach1/conf.py:22:typst_package = "@preview/charged-ieee:0.1.4"
examples/advanced/conf.py:90:#     '#import "@preview/codly:1.3.0": *',
examples/advanced/conf.py:91:#     '#import "@preview/gentle-clues:1.3.1": *',
```
No new version-lockstep site was introduced by this phase — the enforcing instrument
(`tests/test_preview_version_sync.py`) is unmodified and still passes:
```
$ uv run pytest tests/test_preview_version_sync.py -q
```
```
3 passed in 0.02s
```

### 5. Registered config values — no new `typst_*` value

```
$ grep -n 'add_config_value' typsphinx/__init__.py
```
```
44:    app.add_config_value("typst_documents", _default_typst_documents, "html", [list])
45:    app.add_config_value("typst_template", None, "html", [str, type(None)])
46:    app.add_config_value("typst_template_mapping", None, "html", [dict, type(None)])
47:    app.add_config_value("typst_use_mitex", True, "html", [bool])
48:    app.add_config_value("typst_elements", {}, "html", [dict])
50:    app.add_config_value("typst_package", None, "html", [str, type(None)])
51:    app.add_config_value("typst_package_imports", None, "html", [list, type(None)])
52:    app.add_config_value(
56:    app.add_config_value("typst_debug", False, "html", [bool])
58:    app.add_config_value("typst_template_assets", None, "html", [list, type(None)])
```
Nine registrations (the ninth, spanning lines 52-56, is `typst_template_function`). Confirmed
`typsphinx/__init__.py` carries zero diff across this whole phase:
```
$ git diff --stat dbc42a09..HEAD -- typsphinx/__init__.py
```
```
(no output)
```
`dbc42a09` ("docs(48): mark phase complete and transition to phase 49") is this phase's own base
commit -- the file registering config values has not been touched at all since before this phase
began, so no `typst_*` value could have been added.

### 6. Runtime dependency set — no new runtime dependency

```
$ git diff --stat dbc42a09..HEAD -- pyproject.toml
```
```
(no output)
```
`pyproject.toml`'s `dependencies` array (`sphinx>=9.1,<10`, `docutils>=0.21,<0.23`,
`typst>=0.15.0,<0.16`) is unchanged since before this phase began -- three runtime dependencies,
same as at phase start.

### 7. The two forbidden opportunistic changes

**No typing-import modernization anywhere in this phase's diff** (the `UP006`/`UP035` ruff-ignore
deferral, per `CLAUDE.md`'s own "Conventions & gotchas", stays untouched by this phase):
```
$ git diff dbc42a09..HEAD -- typsphinx/ | grep -n 'UP006\|UP035\|from typing import Dict\|from typing import List'
```
```
(no output)
```

**No link-check job added** (no CI/tox/lint-config surface touched at all this phase):
```
$ git diff --stat dbc42a09..HEAD -- pyproject.toml tox.ini .github/
```
```
(no output)
```

### 8. The census's own "How to find any assertion I missed" commands, re-run

Re-running `49-EXPECTED-STRUCTURE.md`'s own reproducible enumeration commands, post-migration:

```
$ grep -rl 'include("' --include=*.py tests/ | wc -l
```
```
25
```
(24 `.py` test modules + 1 fixture `conf.py` file counted by `--include=*.py`; the two ORIGINAL
fixture `conf.py` comment-block hits the census recorded, `bld04_case_collision_gate` and
`nested_master_render_gate`, are both still present.) Five NEW hits beyond the original census's
21-file prediction, all of them artifacts THIS PHASE itself created (never an unpredicted
regression): `tests/test_state_guard_composition_gate.py` (49-02),
`tests/test_state_guard_shapes_gate.py` (49-03),
`tests/fixtures/state_guard_self_and_url_gate/conf.py` (49-03),
`tests/test_include_edge_derivation_unit.py` (49-04),
`tests/test_include_ledger_removal_gate.py` (this plan, Task 1). 21 + 5 = 26 total files (the
`--include=*.py` restriction above excludes the 2 fixture `conf.py` hits that are also present
under the unrestricted `grep -rl` form, matching the original census's own counting convention).

```
$ grep -rl 'include("' docs/ examples/
```
```
examples/advanced/README.md
```
Unchanged from the census's own recorded STALE-PROSE item (deferred to Phase 51, per
`49-EXPECTED-STRUCTURE.md`'s own explicit exclusion).

```
$ grep -rn '\.write_doc(\|\._write_typst_files(' tests/*.py
```
```
tests/test_missing_and_malformed_master_gate.py:133:        # scans the whole list (TypstBuilder._write_typst_files()'s per-
tests/test_builder.py:129:    builder.write_doc("index", sample_doctree)
tests/test_builder.py:155:    builder.write_doc("index", sample_doctree)
tests/test_builder.py:192:    builder.write_doc("index", sample_doctree)
tests/test_builder.py:518:    builder.write_doc("index", doc)
tests/test_static_asset_copy_gate.py:11:Root cause: ``TypstPDFBuilder.write_doc()`` overrode the base
tests/test_static_asset_copy_gate.py:12:``TypstBuilder.write_doc()`` but omitted its ``self.post_process_images(doctree)``
tests/test_static_asset_copy_gate.py:141:            "output tree -- TypstPDFBuilder.write_doc() must call "
tests/test_two_layer_output_gate.py:255:        (``TypstBuilder._write_typst_files()``, which ``TypstPDFBuilder``
```
Unchanged: `test_builder.py`'s 4 genuine direct-write-path call sites (49-04's own NEEDS-SEEDING
class, resolved with no seeding action required — see `49-04-SUMMARY.md`), the rest comment-only
mentions.

```
$ grep -rln 'addnodes.toctree\|nodes.toctree\|toctree()' tests/
```
```
tests/test_toctree_requirement13.py
tests/test_template_engine.py
tests/test_translator.py
```
Unchanged from the census's own recorded 3-file enumeration — no new synthetic-toctree-node
construction exists anywhere in the suite after the migration.

**Reading:** the enumeration is still complete after 49-04's migration. Every hit the census did
not originally predict traces to a fixture or gate module THIS PHASE itself authored (49-02
through this plan), never to an unmigrated or newly-broken assertion.

### 9. What this sweep discharges

This sweep discharges SC#4 in full (the repo-wide grep obligation, at every scope milestone
invariant #4 requires) and re-measures ROADMAP binding constraint #7's four standing invariants
(zero new runtime dependencies, `@preview` count still four with no new lockstep site, zero new
`typst_*` config values, and — via section 7 above — the two forbidden opportunistic changes
absent) as intact. The `## No lost diagnostics` comparison immediately below discharges the
"no diagnostic silently removed" must-have. COMP-12 (the full corpus-scale convergence gate)
remains owed to 49-06, untouched by this sweep.

---

## No lost diagnostics

**Written by 49-05, Task 2.** Every Phase 49 fixture rebuilt for real (`-b typst`, this plan's own
worktree, post-49-04), full Sphinx warning/notice list compared item by item against the recorded
pre-fix baseline (`49-RED-EVIDENCE.md` for the two composition fixtures, `49-SHAPES-RED-EVIDENCE.md`
for the seven shape fixtures). A DISAPPEARED warning would be a FINDING, reported with its
mechanism — not accepted merely because the build exits 0, since this phase's whole subject is a
class of failure that produces no diagnostic at any layer.

| Fixture | Baseline warning/notice count | Post-fix count | Verdict |
|---|---|---|---|
| `state_guard_two_master_gate` | 1 (`shared.rst`: "document is referenced in multiple toctrees: ['bmaster', 'index', 'zmid'], selecting: zmid <- shared") | 1 (byte-identical message) | MATCH -- every baseline warning still present |
| `state_guard_mirror_pair_gate` | 2 (`shared.rst` + `zmid.rst` "referenced in multiple toctrees" notices) | 2 (byte-identical messages) | MATCH |
| `state_guard_self_and_url_gate` | 2 (1 WARNING -- `toc.duplicate_entry` on `child`; 1 consistency-check "referenced in multiple toctrees" notice) | 2 (byte-identical) | MATCH |
| `state_guard_cycle_gate` | 0 | 0 | MATCH (both empty) |
| `state_guard_selfref_gate` | 1 (WARNING -- `toc.not_readable`, self-reference to `'index'`) | 1 (byte-identical) | MATCH |
| `state_guard_glob_gate` | 0 | 0 | MATCH (both empty) |
| `state_guard_orphan_ref_gate` | 0 | 0 | MATCH (both empty) |
| `state_guard_three_master_gate` | 3 (`common_a.rst`, `common_b.rst`, `mid.rst` "referenced in multiple toctrees" notices) | 3 (byte-identical) | MATCH |
| `state_guard_substring_key_gate` | 1 (`guide.rst`: "referenced in multiple toctrees: ['guideext', 'index'], selecting: index <- guide") | 1 (byte-identical) | MATCH |

**Verbatim post-fix consistency-check lines, pasted for the three multi-warning fixtures (the ones
most at risk of a silently-dropped notice), confirming byte-for-byte identity with their own
pre-fix baseline transcripts above:**

```
$ uv run python -m sphinx -b typst tests/fixtures/state_guard_two_master_gate <build-dir>
...
整合性をチェック中... .../state_guard_two_master_gate/shared.rst: document is referenced in
multiple toctrees: ['bmaster', 'index', 'zmid'], selecting: zmid <- shared
完了
...
build succeeded.
```
```
$ uv run python -m sphinx -b typst tests/fixtures/state_guard_mirror_pair_gate <build-dir>
...
整合性をチェック中... .../state_guard_mirror_pair_gate/shared.rst: document is referenced in
multiple toctrees: ['xmastera', 'xmasterb', 'zmid'], selecting: zmid <- shared
.../state_guard_mirror_pair_gate/zmid.rst: document is referenced in multiple toctrees:
['xmastera', 'xmasterb'], selecting: xmasterb <- zmid
完了
...
build succeeded.
```
```
$ uv run python -m sphinx -b typst tests/fixtures/state_guard_three_master_gate <build-dir>
...
整合性をチェック中... .../state_guard_three_master_gate/common_a.rst: document is referenced in
multiple toctrees: ['m1', 'm2'], selecting: m2 <- common_a
.../state_guard_three_master_gate/common_b.rst: document is referenced in multiple toctrees:
['m2', 'm3', 'mid'], selecting: mid <- common_b
.../state_guard_three_master_gate/mid.rst: document is referenced in multiple toctrees:
['m1', 'm3'], selecting: m3 <- mid
完了
...
build succeeded.
```
```
$ uv run python -m sphinx -b typst tests/fixtures/state_guard_self_and_url_gate <build-dir>
...
.../state_guard_self_and_url_gate/index.rst:4: WARNING: toctree で重複したエントリが見つかりました:
child [toc.duplicate_entry]
更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... .../state_guard_self_and_url_gate/child.rst: document is referenced in
multiple toctrees: ['index', 'index'], selecting: index <- child
完了
...
build succeeded, 1 warning.
```
```
$ uv run python -m sphinx -b typst tests/fixtures/state_guard_selfref_gate <build-dir>
...
.../state_guard_selfref_gate/index.rst:4: WARNING: toctree に存在しないドキュメントへの参照が含ま
れています 'index' [toc.not_readable]
...
build succeeded, 1 warning.
```
```
$ uv run python -m sphinx -b typst tests/fixtures/state_guard_substring_key_gate <build-dir>
...
整合性をチェック中... .../state_guard_substring_key_gate/guide.rst: document is referenced in
multiple toctrees: ['guideext', 'index'], selecting: index <- guide
完了
...
build succeeded.
```
`state_guard_cycle_gate`, `state_guard_glob_gate` and `state_guard_orphan_ref_gate` all rebuild
with `build succeeded.` and zero warnings/notices, matching their own empty pre-fix baselines.

**New warnings appearing post-fix are not automatically a problem** (this phase's own state-guard
mechanism introduces no new Sphinx-level diagnostic of its own — every warning above is Sphinx's
own pre-existing toctree-consistency machinery, unrelated to this phase's change, and the
duplicated-entry warning in particular is Sphinx's own and correctly still fires). **A
DISAPPEARED warning would be the actual risk this comparison exists to catch** — none was found:
every one of the nine fixtures' baseline warning/notice counts is reproduced EXACTLY, with
byte-identical message text, after 49-04's emitter migration.

**What this discharges:** the must-have "No diagnostic Sphinx emits today was silently removed"
truth is closed for all nine Phase 49 fixtures. Combined with the `## Removal and invariant sweep`
section above, this closes SC#4 and binding constraint #7's four standing invariants in full for
this plan; COMP-12's full-corpus-scale convergence pass remains 49-06's own deliverable.

---

## Degenerate-shape closure

**Written by 49-05, Task 3.** One row per shape, in the SAME order as
`49-EXPECTED-STRUCTURE.md`'s own `## Degenerate-shape outcome table`. The OBSERVED column is a
concrete value taken from `tests/test_state_guard_shapes_gate.py`'s own now-passing assertions
(re-confirmed this task: `uv run pytest tests/test_state_guard_shapes_gate.py -q` → **17 passed**)
-- a marker count, a published key list, or a resolved heading level, never a restatement of an
assertion's name.

| Shape | Decided outcome (plan time) | Observed outcome (post-fix, this task) | Verdict |
|---|---|---|---|
| 2-node toctree cycle (`state_guard_cycle_gate`) | Skip the back edge; compile succeeds; each body appears exactly once; no unbounded recursion | `TestCycleGate::test_two_node_cycle_terminates_with_forward_edge_only`: PDF build exits 0; `BETA-BODY-MARKER` count in `manual.pdf` = **1**; published wrapper array contains `"alpha#0>beta"` and does NOT contain `"beta#0>alpha"` | **MATCH** |
| Self-referencing toctree (`state_guard_selfref_gate`) | Skip, silently, via Sphinx's own pre-loop `all_docnames.remove(current_docname)` -- no guard line is ever emitted for it at all | `TestSelfRefGate::test_self_referencing_entry_has_no_guard`: exits 0; published array does NOT contain `"index#0>index"`; DOES contain `"index#0>other"`; `OTHER-BODY-MARKER` count = **1** | **MATCH** |
| `self` magic keyword and external-URL entries (`state_guard_self_and_url_gate`) | Skip, silently, with no NEW diagnostic (typsphinx adds no warning Sphinx does not have) | `TestSelfAndUrlGate::test_self_and_external_url_produce_no_guard`: PDF exits 0; `index.typ` contains neither `include("self.typ")` nor `include("https://example.com.typ")`; `CHILD-BODY-MARKER` count = **1**; Sphinx's own pre-existing duplicated-entry warning is still present in captured output | **MATCH** |
| `:glob:` toctree (`state_guard_glob_gate`) | No special handling needed -- guards emitted in the expanded SORTED order | `TestGlobGate::test_glob_toctree_expands_in_sorted_order`: exits 0; marker offsets in the compiled PDF strictly increase `alpha < mike < zulu`; published array's key positions ALSO strictly increase `"index#0>guide/alpha"` < `"index#0>guide/mike"` < `"index#0>guide/zulu"` | **MATCH** |
| `:orphan:` document referenced but not toctree'd (`state_guard_orphan_ref_gate`) | Not included (present in no master's edge set); a cross-reference to it degrades to plain text via Phase 48's guard | `TestOrphanRefGate::test_orphan_reference_degrades_not_included`: exits 0; `ORPHAN-BODY-MARKER` **absent** from the compiled PDF; published array does NOT contain `"index#0>orphan_doc"`; the `:ref:` cross-reference renders as the plain text `"Orphan Section"` | **MATCH** |
| Three or more masters sharing two or more overlapping children (`state_guard_three_master_gate`) | Included in every master's own PDF, each exactly once, at each master's own traversal-derived position -- no cross-master coordination | `TestThreeMasterGate::test_three_masters_each_render_shared_children_once`: exits 0; `COMMON-A-MARKER` count = **1** in `manual1.pdf` AND `manual2.pdf`; `COMMON-B-MARKER` count = **1** in ALL of `manual1.pdf`/`manual2.pdf`/`manual3.pdf`; resolved heading levels for `common_b` = **`[3]`** (m1, nested under `mid`), **`[2]`** (m2, direct), **`[2]`** (m3, direct); the three wrappers' own bodies are pairwise DIFFERENT (`w1 != w2 != w3 != w1`) | **MATCH** |
| Duplicate entry inside one toctree directive (`state_guard_self_and_url_gate`'s doubled `child` entry) | Included exactly once -- only the occurrence-0 edge key is ever published | `TestSelfAndUrlGate::test_duplicate_entry_occurrence_rule`: `index.typ` carries BOTH `if "index#0>child" in ... { include("child.typ") }` AND `if "index#1>child" in ... { include("child.typ") }` guard lines (two static sites); the published wrapper array contains `"index#0>child"` and does NOT contain `"index#1>child"`; `CHILD-BODY-MARKER` count = **1**; the child's own Typst label (`<child:child>`) is `query()`-reachable exactly **1** time | **MATCH** |

**Every row MATCHES.** No divergence was found -- every observed outcome, measured directly
against the compiled/emitted artifact this task, agrees exactly with the outcome
`49-EXPECTED-STRUCTURE.md` DECIDED at plan time, before any file under `typsphinx/` existed for
this phase. SC#2's "decided during planning rather than discovered as a test failure" requirement
is therefore discharged ON THE RECORD by this table, not merely by assertion -- and per this
plan's own prohibition, no decided outcome in `49-EXPECTED-STRUCTURE.md` was amended to match a
measurement (confirmed: `git diff --name-only HEAD -- .planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EXPECTED-STRUCTURE.md`
prints nothing for this plan).

---

## Handoff to Phase 51 and Phase 52

**Written by 49-05, Task 3.** The two user-visible behaviours this phase creates, each measured
directly (not merely asserted), plus the one item explicitly still owed to 49-06.

**1. The standalone-content-file behaviour (Phase 51's documentation obligation).**

Measured directly: `shared.typ` from `state_guard_two_master_gate`'s own real `-b typst` build,
compiled DIRECTLY with `typst.compile()` -- no wrapper, no `#state(...).update(...)` call ever
runs against it.

```
$ uv run python -m sphinx -b typst tests/fixtures/state_guard_two_master_gate <build-dir>
sphinx-build exit code: 0

$ typst.compile("<build-dir>/shared.typ", output="shared_standalone.pdf", root="<build-dir>")
standalone compile of shared.typ (no wrapper) succeeded

$ pypdf-extracted text of the standalone compile:
'Shared\nSHARED-CHAPTER-MARKER'

SHARED-CHAPTER-MARKER in text: True
NESTED-DOCNAME-BODY-MARKER in text: False
```

The compile SUCCEEDS and produces only that document's OWN body (`shared.typ`'s own heading and
`SHARED-CHAPTER-MARKER`) -- its state-guarded child (`sub/nested`, whose marker is
`NESTED-DOCNAME-BODY-MARKER`) is ABSENT, because with no wrapper ever calling `.update(...)`,
`state("typsphinx:include-edges", ()).get()` returns its declared default `()`, so every guard in
`shared.typ` is false.

**User-facing consequence, in one sentence:** a `typst`/`typstpdf`-builder user should compile the
WRAPPER (e.g. `manual.typ`), not a bare content file directly -- a content file compiled alone is
a valid, successfully-compiling document that simply contains no children, with no error and no
warning at any layer.

**Obligation:** Phase 51 documents this behaviour (per `PROJECT.md`'s own "Known residual risk"
note: "a content `.typ` compiled standalone... sees an empty state and therefore includes no
children -- sane, but it must be documented, since `-b typst` users should compile the wrapper").

**2. The two-layer output-shape change, in its now-complete form (Phase 51's documentation
obligation, Phase 52's CHANGELOG obligation).**

What a reader of the emitted output now sees, with `typst_documents = [("index", "manual.typ",
...)]`: the WRAPPER target (`manual.typ`) is no longer the whole document -- it is a template
application (`#show: project.with(...)`) PLUS a state publication (this phase's own addition,
`#state("typsphinx:include-edges", ()).update((...))`) PLUS one `#include(...)` of the content
file. The BODY lives in the docname-named content file (`index.typ`), which now carries
STATE-GUARDED includes (`if "<edge-key>" in state(...).get() { include(...) }`) at each toctree's
own position, instead of the unconditional `include()` calls it carried before this phase.

Phase 47 introduced the wrapper/content SPLIT (the "two-layer output shape" naming); this phase
COMPLETES it by moving the include DECISION itself into the wrapper's own published `state`,
rather than leaving it resolved unconditionally inside the content file at write time.

**Obligation:** Phase 51 documents this (together with `PROJECT.md`'s own note: "With
`typst_documents = [("index","manual.typ",…)]`, `manual.typ` stops being the whole document and
becomes the wrapper, while the body moves to `index.typ`. Explain this together with v0.7.1's own
rename (`index.typ` → `typsphinx.typ` under the default derivation) in the CHANGELOG"), and Phase
52 announces it in the CHANGELOG.

**3. The `:numref:` measurement -- explicitly NOT discharged here.**

The `:numref:` two-case measurement (Case (a): the two masters' compiled figure numbers
disagreeing with each other and with Sphinx's own single `root_doc`-rooted baked number; Case
(b): a figure reachable ONLY from a non-`root_doc` master falling back to plain reference text
with zero warning, per `49-EXPECTED-STRUCTURE.md`'s own fixture 10,
`state_guard_numref_two_case_gate`) and its own fix-or-document decision are **owed by 49-06**
under D-01, and are **NOT discharged by this plan**. A reader of this handoff must not mistake the
two numbered obligations above for a complete list -- this third item remains outstanding until
49-06 lands.

---

## Standing green bar, confirmed at the close of this plan

```
$ uv run pytest -q
================= 1143 passed, 5 skipped in 104.15s (0:01:44) ==================
```
(The 5 skips are the pre-existing, environmental skips this phase inherited unchanged: 4 ×
myst-parser docs-extra skips in `test_changelog_page_gate.py`, 1 ×
`test_corpus_gate.py` SC#3 env-gated on `TYPSPHINX_CORPUS_REPORT=1`.)

```
$ uv run black --check .
All done! ✨ 🍰 ✨
292 files would be left unchanged.
```

```
$ uv run python -m ruff check .
All checks passed!
```

```
$ uv run python -m mypy typsphinx/
Success: no issues found in 6 source files
```

`git status --porcelain typsphinx/ tests/` prints nothing at the close of this plan -- no file
under either directory carries an uncommitted change.

---

## Corpus convergence measurement

**Written by 49-06, Task 1.** COMP-12/SC#5's corpus half: `tests/test_corpus_gate.py` is the
existing GATE-02 gate (introduced Phase 15, cost-measured at Phase 48 D-11), run here
**unmodified**, with the slow marker selected, against the composition this phase's state-guarded
`visit_toctree()` now produces. This section does not touch the gate's own file — confirmed below.

### Worktree isolation, confirmed before the run

```
$ uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7a7bacfe8f502177/typsphinx/__init__.py
```
The worktree's own copy, not the main checkout — a corpus run against the wrong tree would measure
nothing this phase changed.

### Exact command line, verbatim output, exit status, wall-clock runtime — two runs

**Run 1:**
```
$ time uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -q -s
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7a7bacfe8f502177
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests/test_corpus_gate.py Corpus tag: v9.1.0
Corpus commit SHA: cc7c6f435ad37bb12264f8118c8461b230e6830c
Unknown Visit Catalogue: []
.

============================== 1 passed in 14.53s ==============================

real	0m14.899s
user	0m13.586s
sys	0m0.623s
```
Exit status: `0` (pytest reports `1 passed`, and the command's own trailing exit code — verified
separately via `echo $?` immediately after — was `0`).

**Run 2:**
```
$ time uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -q -s
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7a7bacfe8f502177
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests/test_corpus_gate.py Corpus tag: v9.1.0
Corpus commit SHA: cc7c6f435ad37bb12264f8118c8461b230e6830c
Unknown Visit Catalogue: []
.

============================== 1 passed in 13.63s ==============================

real	0m13.847s
user	0m13.295s
sys	0m0.613s
```
Exit status: `0`.

Corpus tag `v9.1.0`, commit SHA `cc7c6f435ad37bb12264f8118c8461b230e6830c` — same clone both runs
(cached at `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`, matching the tag the installed
`sphinx==9.1.0` resolves to), matching Phase 48's own D-11 corpus.

### Compiled artifact's own properties, as the gate asserts them

The gate's own assertions (`pdf_path.exists()`, `.stat().st_size > 0`, `magic == b"%PDF"`) passed
in both runs above (no `AssertionError` in either transcript). The gate's own `tmp_path` is
ephemeral per-test, so its exact byte size is not printed by the gate itself; a **separate,
independent reproduction** of the identical build (same `get_or_clone_corpus` /
`wire_typsphinx_into_corpus_conf` / `_run_corpus_sphinx_build("typstpdf", ...)` helpers imported
directly from `tests/test_corpus_gate.py`, invoked from a throwaway scratch script outside the
repository, never modifying the gate's own file) captured the artifact's own properties directly:

```
$ uv run python /tmp/.../49-06-corpus/probe.py
EXIT: 0
PDF exists: True
PDF size: 15412931
Magic: b'%PDF'
Catalogue: []
```

**PDF byte size: 15,412,931 bytes (~14.7 MiB)**, begins with the PDF magic bytes (`%PDF`), exit
status `0` — the same build the gate itself runs, reproduced once more independently to record the
byte count the gate's own ephemeral `tmp_path` does not print.

### Unsupported-node catalogue

Both gate runs printed `Unknown Visit Catalogue: []` to stdout (`print(f"Unknown Visit Catalogue:
{catalogue.most_common()}")`, `tests/test_corpus_gate.py`'s own SC#2 byproduct), and the
independent reproduction's own `catalogue_unknown_visit(result.stderr)` call agrees:
`Catalogue: []`. **The unsupported-node catalogue is empty** in every one of the three builds run
for this section — no `WARNING: unknown node type: <...>` line appears anywhere in the captured
stderr of any of them.

### Runtime beside Phase 48's baseline

Phase 48's D-11 recorded (`48-EVIDENCE.md` lines 240-249, `48-VALIDATION.md`'s own baseline row):
pre-fix baseline mean `28.745s` (`(28.93 + 28.56) / 2`), after-guard mean `28.065s` (bottom tier,
`-2.37%`), both measured with `time uv run pytest tests/test_corpus_gate.py -m slow` on the same
worktree-isolated machine class this plan also runs on.

This plan's own two runs: `14.53s` / `13.63s` (pytest-reported), mean `14.08s`
(`(14.53 + 13.63) / 2`).

- **Delta against Phase 48's after-guard mean (`28.065s`):** `14.08 - 28.065 = -13.985s`,
  `-13.985 / 28.065 * 100 = -49.83%`.
- **Delta against Phase 48's pre-fix baseline mean (`28.745s`):** `14.08 - 28.745 = -14.665s`,
  `-14.665 / 28.745 * 100 = -51.02%`.

Both deltas are large and NEGATIVE (faster), not a regression in either direction — this phase's
own compile-time state-guard mechanism did not make the corpus build slower. The magnitude (corpus
build roughly halved in wall-clock time versus Phase 48's own measurement) is larger than a single
run's normal noise band, and is recorded here as an observation rather than investigated further:
Phase 48's D-11 measured `test_corpus_gate.py -m slow` (both `test_corpus_compiles_with_no_fatal_error`
AND `test_empty_url_before_after`, the latter SKIPped in both of Phase 48's own runs per its own
transcript), while this section explicitly selected only the single
`test_corpus_compiles_with_no_fatal_error` node ID — the same node Phase 48 also measured, since
its own companion test was SKIPped identically in both phases' transcripts, so the node selection
does not explain the gap. A plausible contributor is environment variance between worktree
provisioning sessions (disk cache warmth for the corpus clone, machine load at measurement time) —
this plan's own corpus cache was already warm (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`
pre-existed before this task ran), and Phase 48's own baseline notes the absolute numbers are
"specific to the measuring machine" (`48-RESEARCH.md` assumption A3, quoted in `48-EVIDENCE.md`).
**This phase has no cost-tier decision of its own** (Phase 48's D-11 tiers governed Phase 48's own
change and measured its own bottom tier) — a cost change here is **recorded, not acted on**. Since
the change is a large improvement rather than a regression, D-02's escalation path is not
triggered regardless of the tier framing.

### Scope of what this green run shows

Both runs of the existing GATE-02 gate exited `0` against the full, unmodified, un-narrowed Sphinx
`doc/` corpus (154 documents, no reduced subset), through `typsphinx`'s new per-master
state-guarded composition — no `TypstCompilationError`, an empty unsupported-node catalogue, and a
valid non-empty compiled PDF. This demonstrates **convergence for THIS corpus, at THIS Typst
version pin (`typst==0.15.0`) and THIS Sphinx version pin (`sphinx==9.1.0`, corpus tag `v9.1.0`)**
— it is not, and cannot be from a single green run, a proof of convergence in general. PROJECT.md's
own named residual risk ("Known residual risk: the state-guarded include rests on Typst's
`state`/`context` multi-pass layout convergence") therefore **stays named rather than being marked
closed** by this section. The version pin (`typst>=0.15.0,<0.16` in `pyproject.toml`, unchanged
this phase — see the "Removal and invariant sweep" section above, `pyproject.toml` diff empty) is
the thing to re-verify on any future dependency bump that touches Typst's own multi-pass layout
engine.
