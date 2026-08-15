---
phase: 49-per-master-include-graph-with-state-guarded-includes
reviewed: 2026-08-14T00:00:00Z
depth: standard
files_reviewed: 22
files_reviewed_list:
  - typsphinx/translator.py
  - typsphinx/builder.py
  - typsphinx/writer.py
  - tests/test_include_edge_derivation_unit.py
  - tests/test_include_ledger_removal_gate.py
  - tests/test_state_guard_composition_gate.py
  - tests/test_state_guard_shapes_gate.py
  - tests/test_state_guard_numref_gate.py
  - tests/test_duplicate_include_label_render_gate.py
  - tests/test_toctree_requirement13.py
  - tests/test_translator.py
  - tests/test_citation_render_gate.py
  - tests/fixtures/state_guard_two_master_gate/conf.py
  - tests/fixtures/state_guard_mirror_pair_gate/conf.py
  - tests/fixtures/state_guard_self_and_url_gate/conf.py
  - tests/fixtures/state_guard_cycle_gate/conf.py
  - tests/fixtures/state_guard_selfref_gate/conf.py
  - tests/fixtures/state_guard_glob_gate/conf.py
  - tests/fixtures/state_guard_orphan_ref_gate/conf.py
  - tests/fixtures/state_guard_three_master_gate/conf.py
  - tests/fixtures/state_guard_substring_key_gate/conf.py
  - tests/fixtures/state_guard_numref_two_case_gate/conf.py
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 49: Code Review Report

**Reviewed:** 2026-08-14T00:00:00Z
**Depth:** standard
**Files Reviewed:** 22
**Status:** issues_found

## Summary

Phase 49 replaces the build-scoped `_included_docnames` write-time dedup ledger
with a per-master, compile-time include mechanism: a DFS
(`derive_master_edge_keys`) computes each master's own edge-key set, each
wrapper publishes its set as a Typst `state` array
(`render_include_edge_state`), and each content file emits a per-emission-site
guard (`render_include_guard`) that reads that state at compile time. The
architecture is sound and the single-derivation-point discipline (one function
building the edge-key string, called identically from the graph side and the
emission side) structurally eliminates the class of cross-side spelling drift
the design notes worry about.

Traced the traversal against `sphinx/directives/other.py` and
`sphinx/environment/adapters/toctree.py` (installed Sphinx source, not
assumed): `derive_master_edge_keys`'s recursive, `traversed`-seeded DFS
correctly mirrors `env.toctree_includes`'s own accumulation order
(`note_toctree()`'s `setdefault(docname, []).extend(include_files)`, called
once per `.. toctree::` directive in document order), and the translator's
per-document `_toctree_entry_occurrences` counter is built over the identical
ordered source, so the graph side's occurrence-0-always claim and the emission
side's per-site occurrence numbering cannot drift apart for the documented
scenarios (self/URL entries, cycles, literal self-reference, glob, duplicate
entries). The fixtures and their gates are hand-derived from
`49-EXPECTED-STRUCTURE.md`'s own contract, not read back from the emitter's
own output — no laundered-gate pattern found in any of the reviewed test
files.

Two real, if narrow, defects were found and are detailed below: an
unescaped-separator collision in the edge-key format itself (a docname
containing a literal `#` or `>` can make two structurally different edges
collide on the identical string, defeating the whole compile-time-guard
mechanism silently), and an unbounded-recursion crash risk in the DFS for a
sufficiently deep/long include chain. Neither is exercised by any of the
phase's own fixtures.

## Warnings

### WR-01: Edge-key format has no separator escaping — `#`/`>` in a docname can collide two unrelated edges onto the same string

**File:** `typsphinx/translator.py:195-231` (`make_include_edge_key`)

**Issue:** `make_include_edge_key` builds the key as
`f"{escaped_parent}#{occurrence}>{escaped_child}"`, where `escaped_parent`/
`escaped_child` are each routed through `escape_typst_string()`. That helper
only escapes `\`, `"`, `\n`, `\r`, `\t` (confirmed by reading its body,
`translator.py:167-171`) — it does **not** escape the two characters (`#`,
`>`) this format itself uses as structural separators. Because the separators
are not escaped out of the docname components, two semantically different
`(parent, occurrence, child)` triples can produce a byte-identical key
string. Verified directly against the production function:

```python
>>> from typsphinx.translator import make_include_edge_key
>>> make_include_edge_key('a', 'b#1>c', occurrence=0)
'a#0>b#1>c'
>>> make_include_edge_key('a#0>b', 'c', occurrence=1)
'a#0>b#1>c'
>>> _ == _  # both equal
True
```

`#` and `>` are ordinary, valid filename characters on POSIX filesystems
(only `>` is reserved on Windows), and Sphinx docnames are derived directly
from source file paths with no character-set restriction — so a project with
a file literally named e.g. `chapter#1.rst` or `guide/a>b.rst` can trigger
this collision. Because both `derive_master_edge_keys()` (graph side) and
`visit_toctree()` (emission side) call the *same* function, this is not a
cross-side drift bug — both sides agree on the (wrong) key — but a colliding
key can make an unrelated guard fire (or fail to fire) for the wrong edge,
silently including/excluding the wrong document with zero diagnostic at any
layer. This is exactly the failure class (silent content drop with no
warning) the whole phase exists to eliminate, just reached through key
collision rather than through the deleted ledger's single-winner semantics.
No fixture or test in this phase (including
`state_guard_substring_key_gate`, which covers array-vs-string containment,
not separator collision) exercises a docname containing `#` or `>`.

**Fix:** Escape the two structural separator characters as part of
`escape_typst_string()`'s output when building the key (or add a
second, key-specific escaping pass inside `make_include_edge_key`), e.g.:

```python
def _escape_edge_key_component(text: str) -> str:
    """Escape characters make_include_edge_key()'s own format uses as
    structural separators, on top of escape_typst_string()'s Typst-literal
    escaping, so a docname containing '#' or '>' cannot collide two
    structurally different edges onto the same key string."""
    escaped = escape_typst_string(text)
    return escaped.replace("\\", "\\\\").replace("#", "\\#").replace(">", "\\>")
```

(Note: ordering versus `escape_typst_string`'s own backslash-doubling needs
care — the simplest robust fix is to percent-encode `#`/`>`/`%` in the raw
docname *before* calling `escape_typst_string`, so the delimiter escaping and
the Typst-literal escaping never interact.)

### WR-02: Unbounded recursion in `derive_master_edge_keys` can crash the whole build on a deep include chain

**File:** `typsphinx/translator.py:280-297` (`derive_master_edge_keys`, nested `walk()`)

**Issue:** `walk()` recurses once per traversed child with no depth limit and
no iterative fallback:

```python
def walk(parent: str) -> None:
    for child in toctree_includes.get(parent, []):
        if child not in traversed:
            edge_keys.append(make_include_edge_key(parent, child, occurrence=0))
            traversed.append(child)
            walk(child)
```

For a sufficiently long linear toctree chain (each document toctree-ing
exactly one further document, e.g. a docs project generated/scripted to have
many nesting levels), this will raise `RecursionError` once the chain depth
approaches Python's default recursion limit (1000), aborting the entire
Sphinx build with a raw Python traceback rather than a controlled
`ExtensionError`. This is a correctness/robustness gap (an unhandled crash),
not a performance concern: a project that built fine under the deleted
ledger's single, flat, iterative membership-set mechanism can now fail to
build at all purely because of chain depth. No fixture in this phase
exercises a chain anywhere near this depth, so the gap is untested.

**Fix:** Convert `walk()` to an explicit-stack iterative traversal that still
preserves document order (push children onto an explicit stack *in reverse*
so pop-order matches append-order, or use a `collections.deque` processed
front-to-back per parent) — the existing design notes are explicit that a
naive LIFO push/pop reverses sibling order, so care is needed to preserve
the documented ordering guarantee while removing the recursion depth
dependency. Alternatively, raise Python's recursion limit locally around the
call with a clear, actionable `ExtensionError` if a `RecursionError` is
still hit, so the failure is diagnosable rather than a bare traceback.

## Info

### IN-01: `_write_typst_files`'s lazy `_master_include_edges` fallback re-derives on every call once the mapping is legitimately empty

**File:** `typsphinx/builder.py:982-983`

**Issue:** `if not self._master_include_edges: self._master_include_edges = self._build_include_edge_map()` treats an *empty* mapping (e.g. a build with no usable `typst_documents` entries) identically to a *never-derived* mapping, so this branch re-runs `_build_include_edge_map()` on every docname write in that scenario instead of once. Harmless (the map is genuinely empty either way, and this is a `dict`/`getattr` walk over `typst_documents`, not something disk- or network-bound), but it silently defeats the "derive once, up front" intent documented immediately above it, purely because `{}` is falsy. Not flagged as a Warning since there is no correctness impact and performance is explicitly out of scope for this review — noted for awareness only.

**Fix:** Track derivation state with an explicit sentinel (e.g. `self._master_include_edges: Dict[...] | None = None`, checked via `is None`) rather than relying on emptiness, if this path is ever revisited.

---

_Reviewed: 2026-08-14T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
