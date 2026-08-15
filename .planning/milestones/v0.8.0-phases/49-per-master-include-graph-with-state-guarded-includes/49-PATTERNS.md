# Phase 49: Per-Master Include Graph with State-Guarded Includes - Pattern Map

**Mapped:** 2026-08-14
**Files analyzed:** 3 production files (modified in place, no new production files) + ~12 new test
fixtures / gate modules called for by `49-VALIDATION.md`'s Wave 0 list
**Analogs found:** 3 / 3 production sites; 5 / 5 test-pattern categories (fixture-build harness,
multi-master `conf.py` shape, corpus gate, `typst.query` readback, "load-bearing properties" comment
convention)

All line numbers below were read live from the current tree on 2026-08-14, not copied from CONTEXT.md
(which explicitly warns its own cited numbers are pre-Phase-47 and stale).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|---------------|
| `typsphinx/builder.py` (edge-set DFS added in `write()`; `_included_docnames` field + reset deleted) | builder/service | transform (doctree adjacency -> per-master edge list) | itself (prior `_included_docnames` ledger machinery being replaced) — no better external analog exists in this codebase | exact (self-analog) |
| `typsphinx/translator.py` `visit_toctree` (guard emission replaces unconditional `include()`) | translator (node-to-text emitter) | transform | itself (current `visit_toctree` body) — Phase 48's guard-emission sites in the same file are the next-best analog for the `if <cond> { ... }` shape | exact (self-analog) + role-match (Phase 48 guard sites) |
| `typsphinx/writer.py` `render_wrapper()` (state publication line added before `#include()`) | writer (template/wrapper composer) | transform | itself (current `render_wrapper()` body) | exact (self-analog) |
| New unit test: shared edge-key derivation function (D-05) | test (unit) | transform | `tests/test_label_existence_guard_unit.py` (Phase 48's compile-time-guard unit tests — nearest "one shared derivation function, asserted from both call sites" precedent) | role-match |
| New fixture: two-master defect-A / diamond / interleaving / mirror-pair / `self`+external-URL+duplicate / degenerate-shape / substring-collision / `:numref:` two-case (~12 fixtures, Wave 0) | test fixture (`conf.py` + `.rst` under `tests/fixtures/<name>/`) | request-response (sphinx-build -> typst.compile -> pypdf/query readback) | `tests/fixtures/cross_doc_label_namespace_render_gate/conf.py` (multi-doc, single master) for shape; `tests/fixtures/template_named_dir_master/conf.py` (two `typst_documents` entries, i.e. genuinely two masters) for the multi-master shape Phase 49 specifically needs | role-match (single existing fixture combines both traits) |
| New gate module: two-master defect-A / diamond / COMP-07 (`tests/test_*_gate.py`) | test (integration, real compile) | request-response | `tests/test_multi_master_metadata_no_leak.py` (two-`typst_documents`-entry gate, `-b typst`, `sys.executable -m sphinx` harness) | exact |
| New gate module: heading-depth / mirror-pair (COMP-10) | test (integration, `typst.query` readback) | request-response | `tests/test_heading_depth_render_gate.py` (`_query_heading_levels` / `_query_heading_outline` via `typst.query(..., "heading", field="level", root=...)`) | exact |
| New gate module: `self`/external-URL/duplicate-entry RED, corpus convergence (COMP-05/COMP-12) | test (integration, real compile / subprocess) | request-response | `tests/test_pdf_render_gate.py` (`_run_sphinx_build_typst`, `typst.compile()` + `pypdf` PDF-text readback) for the RED fixture; `tests/test_corpus_gate.py` (`get_or_clone_corpus`, `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`, `-m slow`) for COMP-12 | exact |
| New unit test: `_included_docnames` removal (COMP-11) | test (structural grep) | transform | `tests/test_master_include_set_predicate_gate.py` (existing structural/grep-style assertion on builder internals — nearest precedent for a repo-wide-grep test) | role-match |

## Pattern Assignments

### `typsphinx/builder.py` — per-master edge-set DFS (COMP-05, replaces `_included_docnames`)

**Analog:** itself. Read live 2026-08-14 at these exact locations (not CONTEXT.md's stale citations):

- Declaration to delete — `typsphinx/builder.py:231`:
```python
self._included_docnames: set[str] = set()
```
- `write()` reset to delete — `typsphinx/builder.py:658` (inside `write()`, right after
  `self.prepare_writing(docnames)`):
```python
# Start each build with a clean include-dedup ledger so re-builds and
# multiple write() invocations do not carry stale state across masters.
self._included_docnames = set()
```
- Site where the per-master edge-set computation belongs — `typsphinx/builder.py:859-920`,
  `_write_typst_files(self, docname, doctree)`. This is the ONE shared write path both builders use
  (per its own docstring) and is where `render_wrapper()` is called per `typst_documents` entry
  (`typsphinx/builder.py:906-914`):
```python
wrapper_output = self.writer.render_wrapper(
    entry, doctree, wrapper_relative_dir, content_relative_path
)
```
  Per RESEARCH's System Architecture Diagram, the edge-set DFS itself should run ONCE in `write()`
  (`typsphinx/builder.py:612+`, which already has `self.env` fully read-resolved and the full
  `docnames` set) — computed into a `{master_docname: (edge_key, ...)}` mapping held on the builder
  for the rest of `write()` — then `_write_typst_files` passes the relevant master's tuple into
  `render_wrapper()` as a new parameter alongside `entry`/`doctree`/`wrapper_relative_dir`/
  `content_relative_path`.
- Existing docstring context worth copying verbatim as the DELETION's own removal-comment precedent —
  `typsphinx/builder.py:220-230` (the long comment above the `_included_docnames` declaration
  explaining the "diamond"/label-collision rationale) is the right shape/tone for a replacement
  comment at the new DFS site: explain WHY (mirrors `inline_all_toctrees`), not just WHAT.

**Anti-pattern warning (RESEARCH Pitfall 3):** do NOT reintroduce the deleted (pre-Phase-48)
`stack.pop()`/`.append()` LIFO walk — it silently reverses sibling order with no compile error. Use
real recursion or a stack with children pushed in reverse order, mirroring `inline_all_toctrees`'s own
recursive shape.

### `typsphinx/translator.py` `visit_toctree` — state-guarded emission (COMP-06/COMP-11, D-03/D-04)

**Analog:** itself. Full current body read live this session at `typsphinx/translator.py:5016-5121`.
Key excerpts:

**Current unconditional-include core loop to replace** (`translator.py:5083-5103` measured this
session — CONTEXT.md's cited `5094-5103`/`5095` fall inside this range and are confirmed still
accurate):
```python
included_docnames = getattr(self.builder, "_included_docnames", None)
for _title, docname in entries:
    if included_docnames is not None:
        if docname in included_docnames:
            logger.debug(...)
            continue
        included_docnames.add(docname)

    relative_path = self._compute_relative_include_path(docname, current_docname)
    logger.debug(...)
    self.add_text(f'  include("{relative_path}.typ")\n')
```
This becomes, per D-03/D-04/D-09: iterate `node["includefiles"]` (or the equivalent already-resolved
list the translator is handed) instead of `entries`; drop the `_included_docnames` ledger read/write
entirely; and replace the bare `include(...)` with the state-guarded form:
```python
self.add_text(f'  if "{edge_key}" in state("{ns}", ()).get() {{ include("{relative_path}.typ") }}\n')
```
using the ONE shared key-derivation function (D-05) for `edge_key`, matching RESEARCH's verified
Pattern 1 syntax exactly (see Shared Patterns below for the syntax itself).

**Surviving unchanged** — `_compute_relative_include_path()`, `typsphinx/translator.py:4592-4620`
(confirmed present, unaffected by the guard per RESEARCH: "only the *decision* to emit moves, not the
path computation").

**Surrounding scope block, unchanged shape** — `translator.py:5075-5077`:
```python
self.add_text("context {\n")
self.add_text("  set heading(offset: heading.offset + 1)\n")
```
D-08 keeps this exactly as-is; the per-entry guard goes INSIDE this existing block, one `if` line per
entry, no new outer construct.

**Guard for empty entries, unchanged shape** — `translator.py:5054-5057`:
```python
if not entries:
    logger.debug("Toctree has no entries, skipping")
    raise nodes.SkipNode
```
Adjust the emptiness check to `includefiles` per D-03 rather than `entries`, since `entries` and
`includefiles` diverge (self/external-URL entries).

### `typsphinx/writer.py` `render_wrapper()` — state publication (COMP-06)

**Analog:** itself. Read live this session, `typsphinx/writer.py:262-311` (full method body).

**Insertion point — before the existing `body` assignment**, `typsphinx/writer.py:299-300`:
```python
docname = entry[0]
include_path = compute_content_include_path(
    wrapper_relative_dir, content_relative_path
)
body = f'#include("{include_path}")\n'
```
Per RESEARCH's Pattern 1 (verified syntax), this becomes:
```python
body = f'#state("{ns}", ()).update(({edge_keys_literal}))\n' f'#include("{include_path}")\n'
```
where `edge_keys_literal` is this master's own edge-key tuple rendered as a Typst array literal — see
Shared Patterns for the mandatory single-element trailing-comma handling (D-09/Pitfall 1).

**Path helper that survives unchanged** — `compute_content_include_path()`, `typsphinx/writer.py:25-40`
(read this session), the wrapper->content relative-path computation; unaffected by this phase.

## Shared Patterns

### The state-guarded include syntax (D-09, verified this session — apply to both `writer.py` and `translator.py`)

**Source:** `49-RESEARCH.md` Architecture Patterns Pattern 1 (7 independent real `typst.compile()` runs
this session; not yet present anywhere in the repo's own code or tests — this is new, verified-by-
research syntax, not an existing in-repo pattern to copy from).

**Apply to:** `writer.py`'s `render_wrapper()` (the `#state(...).update((...))` emission) and
`translator.py`'s `visit_toctree` (the `if "<key>" in state(...).get() { include(...) }` guard, one
per entry, inside the existing `context { ... }` block).

```typst
// wrapper (writer.py render_wrapper) — multi-edge case
#state("<ns>", ()).update(("index>zmid", "zmid>shared"))
#include("index.typ")
```
```typst
// wrapper — REQUIRED trailing comma on a single-edge array (Pitfall 1: its
// absence is NOT a syntax error, it silently degrades `in` from array
// membership to substring containment — a corpus-scale silent-corruption
// hazard, not a compile-fail-fast one)
#state("<ns>", ()).update(("bmaster>shared",))
#include("bmaster.typ")
```
```typst
// content file (translator.py visit_toctree) — inside the EXISTING
// context{} block, condition and its `{` on ONE unbroken line (Phase 48
// D-08's line-break rule, re-confirmed applicable here per Pitfall 2)
context {
  set heading(offset: heading.offset + 1)
  if "index>zmid" in state("<ns>", ()).get() { include("zmid.typ") }
  if "index>shared" in state("<ns>", ()).get() { include("shared.typ") }
}
```

**Mandatory verification obligation carried from D-09/Pitfall 1:** a plan/test must assert the
published state's Typst *type* is an array for the single-master, single-edge case specifically (e.g.
via a `repr(type(...))`/`#repr(state(...).get())` probe fixture) — this is exactly the shape the
corpus's simplest configurations hit on every build, and the failure has zero warning signs at compile
time.

### One-shared-key-derivation function (D-05)

**Source:** no existing in-repo precedent for THIS specific function; apply the project's standing rule
(Phase 40.1 D-06/D-07, Phase 47 D-03: "one judgement, one derivation point, never two spellings of the
same rule") already visible at `_compute_relative_include_path()` (`translator.py:4592`) and
`compute_content_include_path()` (`writer.py:25`) — both are single, shared, importable functions
consulted by exactly one caller class each rather than reimplemented ad hoc.

**Apply to:** both `builder.py`'s DFS (producing the published state array) and `translator.py`'s
`visit_toctree` (producing each guard's condition string) — both MUST call the same function, and a
test must assert the two sides agree (see Pattern Assignments' unit-test row).

### The `sys.executable -m sphinx` subprocess harness (every new integration fixture)

**Source:** `tests/test_pdf_render_gate.py:150-191` (`_run_sphinx_build_typst`), reused verbatim
(module-local copy, not imported) by every other gate module including
`tests/test_multi_master_metadata_no_leak.py:57-79` and `tests/test_heading_depth_render_gate.py:41-81`.

**Apply to:** every new Phase 49 fixture-build helper.

```python
def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path, extra_args: tuple = ()
) -> subprocess.CompletedProcess:
    """
    Run `sphinx-build -b typst` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as `sys.executable -m sphinx` (the sphinx-build console entry
    point's module form) rather than shelling out to `uv run sphinx-build`:
    this guarantees the exact interpreter/venv already running this test is
    reused, with no dependency on external PATH resolution of a `uv`
    executable. ...
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typst",
            *extra_args,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )
```

For fixtures that need a PDF (COMP-07/COMP-08/COMP-09), follow
`tests/test_pdf_render_gate.py:227-262` immediately after the `sphinx-build` call: locate the
wrapper `.typ`, `typst.compile(str(wrapper_typ), output=str(pdf_output))` with NO try/except (any
fatal aborts the fixture loudly), assert `%PDF` magic bytes, then `pypdf.PdfReader` + `extract_text()`
joined across pages.

For fixtures that need resolved heading levels (COMP-10), follow
`tests/test_heading_depth_render_gate.py:84-137` (`_query_heading_levels`/`_query_heading_outline`):

```python
def _query_heading_levels(typ_path: Path, root: Path) -> list:
    """
    root MUST be the build directory, never the .typ file's own directory --
    the emitted include() paths inside a master document are relative to the
    build root, and Typst resolves them against root during query/compile.
    """
    result = typst.query(str(typ_path), "heading", field="level", root=str(root))
    return json.loads(result)
```

No existing test in this repo does a `typst.query` assertion for anything other than heading `level`
(confirmed by repo-wide grep this session — `test_heading_depth_render_gate.py` is the ONLY
`typst.query` call site in the whole test suite). COMP-10's mirror-pair fixture is a direct structural
copy of this module's existing `xmaster`-shaped nested-toctree fixture pattern, not an invention.

### Multi-master `conf.py` shape (`typst_documents` with 2+ entries)

**Source:** `tests/fixtures/template_named_dir_master/conf.py` (2 `typst_documents` entries, divergent
title AND author, exercised by `tests/test_multi_master_metadata_no_leak.py`) — this is the ONLY
fixture found this session with genuinely two `typst_documents` entries pointing at two DIFFERENT
docnames each producing its own independent wrapper (`bld02_duplicate_target_gate` and
`missing_and_malformed_master_gate` also have 2-3 entries but are collision/malformed-entry gates, not
composition gates). `cross_doc_label_namespace_render_gate/conf.py` has only ONE master but TWO
sibling content documents sharing a label-collision risk — useful for the toctree/document-count shape,
not the two-MASTER shape Phase 49 needs.

```python
# tests/fixtures/template_named_dir_master/conf.py (excerpt)
typst_documents = [
    (
        "_template/index",
        "template-dir-master.typ",
        "Template Named Dir Master",
        "Test Author",
    ),
    (
        "_template/sub/index",
        "template-dir-sub.typ",
        "Template Named Dir Master (nested)",
        "Test Author (nested)",
    ),
]
```

**Apply to:** every Phase 49 diamond/two-master fixture (COMP-07, COMP-09, Open Question #2's
`:numref:` two-case fixture): two `typst_documents` entries naming two distinct docnames, each with
its own toctree, sharing a common child docname somewhere in both trees.

### The "Load-bearing properties" `conf.py` comment convention

**Source:** `tests/fixtures/bld02_template_clobber_gate/conf.py:9-22` and
`tests/fixtures/explicit_docname_collision_gate/conf.py:12-16` (both read this session).

```python
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the template-clobber gap:
#   - The target MUST keep the "./" prefix and the `_template` stem
#     (`./_template.typ`) -- this is the reserved-infrastructure collision
#     kind D-03 enumerates, defeated specifically by the missing shape
#     normalization ...
#   - `index.rst`'s body marker `TEMPLATE-CLOBBER-SENTINEL-DDD` must keep
#     its exact spelling -- the pre-fix RED evidence is a
#     `grep -c '^#let project'` proof that ...
```

**Apply to:** every new fixture `conf.py` under `tests/fixtures/` this phase adds (all ~12 of them per
Wave 0) — name exactly which docname/toctree-ordering/entry-shape/sentinel-string is load-bearing to
the specific defect/shape being reproduced, so a future edit does not silently stop exercising it.

### GATE-02 corpus convergence gate (COMP-12)

**Source:** `tests/test_corpus_gate.py:63` (`get_or_clone_corpus`), `:275-284`
(`TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`, `@pytest.mark.slow`).

```python
def test_corpus_compiles_with_no_fatal_error(self, corpus_doc_dir, tmp_path):
    wire_typsphinx_into_corpus_conf(corpus_doc_dir)
    conf_text = (corpus_doc_dir / "conf.py").read_text(encoding="utf-8")
    assert "typst_documents" in conf_text, (...)
    outdir = tmp_path / "_build"
    result = _run_corpus_sphinx_build("typstpdf", corpus_doc_dir, outdir)
    pdf_path = outdir / "sphinx-corpus.pdf"
    assert pdf_path.exists(), (...)
```

**Apply to:** COMP-12 needs no new gate module — this EXISTING gate, run unmodified against the new
composition mechanism, IS the vehicle. Per D-02/binding constraint #5, a convergence failure here is a
stop-and-escalate design-level finding, not a fixture to iterate on (see `49-VALIDATION.md`'s Manual-
Only Verifications table).

### `_included_docnames` removal — structural grep assertion (COMP-11)

**Source:** no existing repo-wide-grep-style pytest assertion was found this session that is a byte-for-
byte match; `tests/test_master_include_set_predicate_gate.py` is the closest existing precedent for a
test that inspects builder internals structurally rather than through a compiled artifact. The simplest
correct implementation is a direct `subprocess.run(["grep", "-rn", "_included_docnames", "typsphinx/"])`
or a Python `pathlib`+`re` walk over `typsphinx/*.py` asserting zero matches, run as a plain unit test
with no fixture dependency.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| Substring-collision edge-key fixture (D-09 Pitfall 1 — two edge keys where one is a substring of the other) | test fixture | request-response | No existing fixture in this repo exercises a Typst `state`/array-vs-string type hazard at all; this is genuinely new territory introduced by this phase's own mechanism. Build from RESEARCH's own three-fixture Pitfall-1 reproduction (`("bmaster>shared")` vs `("bmaster>shared",)` vs the `"master" in "bmaster>shared"` substring-match probe), which is itself the closest thing to an analog (a research-session transcript, not repo code) |
| Degenerate-shape fixtures (2-node cycle, self-reference, `:glob:` toctree, `:orphan:` reference) | test fixture | request-response | `49-CONTEXT.md`/`49-RESEARCH.md` both confirm zero existing coverage in `tests/roots/` (which itself holds only `test-basic`) or `tests/fixtures/`. Build each as its own minimal `tests/fixtures/<shape>_gate/` directory following the "Load-bearing properties" comment convention above; there is no single closer analog than the general fixture-harness pattern already documented |

## Metadata

**Analog search scope:** `typsphinx/*.py` (all three production modules read in full/targeted ranges);
`tests/*.py` (repo-wide grep for `typst_documents`, `typst.query`, `_run_sphinx_build_typst`,
`_included_docnames`); `tests/fixtures/*/conf.py` (repo-wide grep for `typst_documents` entry counts and
"Load-bearing properties" comment blocks); `tests/roots/` (confirmed to hold only `test-basic`, zero
Phase-49-relevant coverage).
**Files scanned:** 3 production modules (full or targeted ranges) + ~9 test/fixture files read in
detail (`test_pdf_render_gate.py`, `test_heading_depth_render_gate.py`, `test_corpus_gate.py`,
`test_multi_master_metadata_no_leak.py`, `template_named_dir_master/conf.py`,
`cross_doc_label_namespace_render_gate/conf.py`, `bld02_template_clobber_gate/conf.py`,
`explicit_docname_collision_gate/conf.py`) + ~70 files grepped for shape/count signals.
**Pattern extraction date:** 2026-08-14
