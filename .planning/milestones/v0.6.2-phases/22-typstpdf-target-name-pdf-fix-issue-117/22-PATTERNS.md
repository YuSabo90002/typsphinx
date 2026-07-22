# Phase 22: typstpdf Target-Name PDF Fix (Issue #117) - Pattern Map

**Mapped:** 2026-07-21
**Files analyzed:** 5 (1 modify-only, 2 modify+possibly-modify, 1 new test module, 1 fixture-conf extension)
**Analogs found:** 5 / 5

RESEARCH.md already contains verbatim excerpts of the three write/read sites and a GATE-01 shape
citation from `tests/test_desc_signature_concat_render_gate.py` — not repeated here. This file adds
the analog mapping RESEARCH.md left open: **where the new private helper/logger call should live**,
**which existing fixture is cheapest to extend for the get_target_uri non-regression proof**, and
**what a table-driven pure-function test / caplog-warning test looks like in this repo**.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/builder.py` (`_resolve_output_stem` helper) | utility/private-helper method on `TypstBuilder` | transform (docname → stem string) | `typsphinx/builder.py:92-128` `_compute_master_included_docnames` | exact — same class, same "private helper computed from `self.config`/`self.env`, called from `write()`/`write_doc()`/`finish()`" shape |
| `typsphinx/builder.py` (3 call-site edits) | builder (write/finish path) | file-I/O | `typsphinx/builder.py:313-350` (`TypstBuilder.write_doc`), `:634-673` (`TypstPDFBuilder.write_doc`), `:675-726` (`TypstPDFBuilder.finish`) | exact — these ARE the sites being edited; RESEARCH.md's Code Examples section already has them verbatim |
| `tests/test_target_name_render_gate.py` (NEW, name TBD) | test (real-compile render gate) | request-response (subprocess sphinx-build) | `tests/test_cross_doc_label_namespace_render_gate.py` (whole file) — closer than `test_desc_signature_concat_render_gate.py` because it also demonstrates the negative-assertion idiom (asserting a filename is ABSENT, matching D-10's "assert `index.typ`/`index.pdf` absent") | exact |
| `tests/test_corpus_gate.py` (1-line edit ~line 330) | test (slow/network integration) | file-I/O assertion | itself, pre-existing — no analog needed, just the sibling `outdir / "index.pdf"` → `outdir / "sphinx-corpus.pdf"` edit RESEARCH.md already located | n/a (surgical edit) |
| `tests/fixtures/cross_doc_label_namespace_render_gate/conf.py` (POSSIBLY MODIFY: `typst_documents` target) | config (test fixture) | CRUD (config literal) | itself — already the closest existing multi-doc + cross-`:ref:` fixture in the corpus | exact |
| (optional) table-driven unit tests for `_resolve_output_stem` stem cases | test (unit, pure function) | transform | `tests/test_builder.py:19-38` (`test_typst_builder_has_correct_attributes`, `test_typst_builder_has_required_methods`) — plain `def test_*` functions, one assertion group per case, NO `@pytest.mark.parametrize` anywhere in this repo | role-match |
| (optional) caplog-based warning test for D-06 | test (unit, log assertion) | event-driven (log record) | `tests/test_footnotes.py:153-173` `test_dangling_reference_warns` | exact |

## Pattern Assignments

### `typsphinx/builder.py` — new `_resolve_output_stem` helper

**Analog:** `typsphinx/builder.py:92-128` (`TypstBuilder._compute_master_included_docnames`)

This is the strongest analog in the codebase: it is the ONLY existing private helper on
`TypstBuilder` that (a) reads `self.config.typst_documents` directly via `getattr(...) or []`
(the exact defensive-default idiom D-02's "no entry → docname" fallback should reuse), (b) has a
`set[str]`/`str`-returning pure-computation signature with no side effects, and (c) is called from
multiple downstream sites rather than being single-use.

**Signature + defensive-getattr style** (`builder.py:92-115`):
```python
def _compute_master_included_docnames(self) -> set[str]:
    """Compute the transitive toctree closure of the master document(s).
    ...
    Returns:
        The set of docnames included in some compiled master, or an empty
        set when no masters are configured (which the translator treats as
        "unknown" and does not degrade against).
    """
    typst_documents = getattr(self.config, "typst_documents", []) or []
    masters = [entry[0] for entry in typst_documents if entry]
    toctree_includes = getattr(self.env, "toctree_includes", {}) or {}
    ...
```
Reuse verbatim: `getattr(self.config, "typst_documents", []) or []` and the `if entry:` guard
against a possibly-malformed tuple — `_resolve_output_stem` should look up `doc_tuple[0] == docname`
the same defensive way (RESEARCH.md's illustrative snippet already does this; this is the confirmed
house-style precedent for it, not just a hypothesis).

**Docstring style to match:** Google-style `Args:`/`Returns:` blocks, a prose paragraph explaining
*why* (not just what) before the mechanics — see full docstring at `builder.py:93-113`. The new
helper's docstring should explain the D-03/D-04/D-06/D-07 normalization rule in the same prose-then-
mechanics shape, referencing the docs-contract line (`docs/configuration.rst:43`) the way this one
references the `translator.py` line numbers it depends on.

**Placement:** immediately after `init()` and before `get_outdated_docs()`, mirroring where
`_compute_master_included_docnames` sits relative to `init()` (both are setup/lookup helpers used
by later pipeline stages, placed early in the class body, ahead of the Sphinx-protocol methods they
serve).

### `typsphinx/builder.py` — the 3 call-site edits

**Analog:** the sites themselves (already fully excerpted in RESEARCH.md's "Code Examples" —
`builder.py:329`, `:646`, `:703-725`). No additional excerpt needed here; the only NEW pattern to
apply at each site is substituting `docname` with `self._resolve_output_stem(docname)` in the
`path.join(self.outdir, ... )` calls, matching the existing `path.join(self.outdir, docname +
self.out_suffix)` call shape exactly (import already present: `from os import path`, `builder.py:10`).

### `typsphinx/builder.py` — the D-06 `logger.warning` call

**Analog:** `builder.py:298-301` (inside `post_process_images`, the "no matching image mimetype"
guarded-degradation warning) — the closest existing "detect an unsupported input shape, warn with
the exact value AND what will happen instead, then degrade gracefully rather than raise" pattern in
this file.

**Import/logger idiom** (`builder.py:15,21` — note: `sphinx.util.logging`, NOT stdlib `logging`):
```python
from sphinx.util import logging
...
logger = logging.getLogger(__name__)
```
This differs from `template_engine.py`/`pdf.py`, which use plain stdlib `import logging`. Since the
new helper lives in `builder.py`, use the **existing module-level `logger`** already defined at
`builder.py:21` — do not re-import.

**Message-style convention to copy** (`builder.py:298-301`):
```python
logger.warning(
    f"a suitable image for typst builder not found: "
    f"{mimetypes} ({node.get('uri', '')})"
)
```
Lower-case sentence start, f-string with the offending value interpolated, states the consequence
implicitly via context. D-06's exact wording is already locked in CONTEXT.md/RESEARCH.md
("a path is not supported in a `typst_documents` target name; emitting `manual.typ` / `manual.pdf`
next to the source document instead") — match this same lower-case, single-`logger.warning(f"...")`-
call shape (see also the `finish()`-local warning at `builder.py:696-698` and `:709` for the
sibling "guarded degrade inside this same class" precedent).

### `tests/test_target_name_render_gate.py` (NEW)

**Analog:** `tests/test_cross_doc_label_namespace_render_gate.py` (full file, 231 lines) — use this
over `test_desc_signature_concat_render_gate.py` (RESEARCH.md's cited analog) because it additionally
demonstrates:
1. The **negative-presence assertion** idiom needed for D-10's "index.typ/index.pdf absent" half —
   see its "(1) COLLISION" block's `assert not re.search(...)` pattern at line 176, and the direct
   `.exists()` check pattern to invert for `assert not (temp_build_dir / "index.pdf").exists()`.
2. Structured multi-part assertions with a `# (n) LABEL:` comment banner per concern (lines 163,
   181, 211, 222) — mirrors D-10's two distinct concerns (presence of target-named files, absence
   of docname-named files) cleanly as two labelled blocks.

**Fixture/build-driver boilerplate to copy verbatim** (lines 60-95):
```python
@pytest.fixture
def cross_doc_label_namespace_render_gate_dir():
    return Path(__file__).parent / "fixtures" / "cross_doc_label_namespace_render_gate"

@pytest.fixture
def temp_build_dir(tmp_path):
    return tmp_path / "_build"

def _run_sphinx_build_typstpdf(source_dir: Path, build_dir: Path) -> subprocess.CompletedProcess:
    """Invoked as `sys.executable -m sphinx` (never `uv run sphinx-build`) ..."""
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )
```
For the new GATE-01 test, point the fixture-dir helper at `tests/roots/test-basic` (D-10) instead of
a `tests/fixtures/...` subfolder — `test-basic` lives directly under `tests/roots/`, so the fixture
should read `Path(__file__).parent / "roots" / "test-basic"`, not `"fixtures" / ...`.

**typst-availability skip guard to copy verbatim** (lines 52-57, 111-114):
```python
try:
    import typst  # noqa: F401
    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False
...
@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the ... render gate",
)
class Test...:
```

**PDF-magic assertion tail to copy verbatim** (lines 222-230, also matches RESEARCH.md's
`test_desc_signature_concat_render_gate.py` excerpt — both agree byte-for-byte on this idiom):
```python
pdf_output = temp_build_dir / "output.pdf"
assert pdf_output.exists(), "..."
assert pdf_output.stat().st_size > 0, "PDF file is empty"
with open(pdf_output, "rb") as f:
    assert f.read(4) == b"%PDF", "Generated file is not a valid PDF"
```

### `tests/fixtures/cross_doc_label_namespace_render_gate/conf.py` (POSSIBLY MODIFY)

**Analog:** itself — this is already the cheapest existing multi-doc + cross-`:ref:` fixture in the
corpus (RESEARCH.md's Open Question 2 recommendation), confirmed by direct read.

**Current state** (full file, `conf.py`):
```python
extensions = ["typsphinx"]

typst_documents = [
    ("index", "index", "Cross-Doc Namespace Gate", "Test Author"),
]
```
It is currently an **identity mapping** (`target == docname`). To give the `get_target_uri`
non-regression claim (RESEARCH.md Pitfall 1 / Common Pitfall 1) a real-compile proof, change the
target element to a non-identity value, e.g. `("index", "namespace-gate", ...)`, and confirm
`tests/test_cross_doc_label_namespace_render_gate.py`'s existing PDF-presence assertion at line 223
(`temp_build_dir / "index.pdf"`) is updated to match (`namespace-gate.pdf`) — this is the SAME kind
of D-11-style consumer update RESEARCH.md already flagged for `test_corpus_gate.py`, just localized
to this fixture's own test file. `pagea.typ`/`pageb.typ` (the toctree-included children, not
`typst_documents` entries) are unaffected per D-02 and keep their current filenames — only the
`index.pdf`/`index.typ` assertion at that file's line 223 (and the fixture's own target string)
change.

### Optional: table-driven unit tests for `_resolve_output_stem`

**Analog:** `tests/test_builder.py` — no `@pytest.mark.parametrize` exists ANYWHERE in this test
suite (`grep -rl "parametrize" tests/test_*.py` returns nothing); the house convention for
"multiple related cases" is one plain `def test_<case>():` function per case, each with its own
docstring naming the specific input shape being covered — see `test_builder.py:19-38` for the
shape (short, single-assertion-group, imports `TypstBuilder` inline inside the function body rather
than at module top, matching the whole file's style at lines 13/21/30). If the planner adds D-03/
D-04/D-06/D-07 stem-case unit tests, follow this same "one function per case" convention rather than
introducing the first `parametrize` usage in the repo — e.g. `test_resolve_output_stem_strips_typ_suffix`,
`test_resolve_output_stem_preserves_period_in_stem`, `test_resolve_output_stem_extensionless_target`,
`test_resolve_output_stem_guards_path_separator`, one function each.

### Optional: caplog-based warning test for D-06

**Analog:** `tests/test_footnotes.py:153-173` (`test_dangling_reference_warns`)

```python
def test_dangling_reference_warns(temp_sphinx_app: SphinxTestApp, caplog):
    """D-08: a dangling footnote_reference ... logs a logger.warning naming
    the refid and skips, emitting no footnote(...) call at all.
    """
    ...
    with caplog.at_level("WARNING"):
        doc.walkabout(translator)

    output = translator.astext()
    assert "footnote(" not in output
    assert any("missing" in record.getMessage() for record in caplog.records)
```
This is the ONLY `caplog` usage pattern found in the suite that pairs "assert a specific substring
appears in some emitted warning's `.getMessage()`" with "assert the degraded output still has the
expected shape" — directly applicable to a D-06 test: build (or call `_resolve_output_stem`
directly) with a path-bearing target under `caplog.at_level("WARNING")`, then assert both
`any("path is not supported" in r.getMessage() for r in caplog.records)` AND that the returned stem
equals the basename fallback.

## Shared Patterns

### Logger idiom (module-level, `sphinx.util.logging`)
**Source:** `typsphinx/builder.py:15,21`
**Apply to:** the new `_resolve_output_stem` helper's D-06 warning call — reuse the existing
module-level `logger`, do not add a new import (this file already uses `from sphinx.util import
logging` / `logger = logging.getLogger(__name__)`, distinct from `template_engine.py`/`pdf.py`'s
stdlib `import logging`).

### Defensive `getattr(self.config, ..., default) or default` config access
**Source:** `typsphinx/builder.py:114,116` (`_compute_master_included_docnames`) and `:693`
(`finish()`)
**Apply to:** `_resolve_output_stem`'s own `typst_documents` lookup — same
`getattr(self.config, "typst_documents", []) or []` idiom, tolerant of `None` and of a missing
attribute (relevant for hand-built test doctrees / mock builders per the comment at `builder.py:88-89`).

### Real-compile render-gate structure (`sys.executable -m sphinx` subprocess, typst-availability skip, PDF-magic tail)
**Source:** `tests/test_cross_doc_label_namespace_render_gate.py` (whole file) and
`tests/test_desc_signature_concat_render_gate.py` (RESEARCH.md's cited excerpt — the two agree)
**Apply to:** the new GATE-01 test module (D-10).

## No Analog Found

None — every file in scope has at least a role-match analog above.

## Metadata

**Analog search scope:** `typsphinx/` (all 5 modules), `tests/` (all `test_*.py` + `tests/fixtures/*/conf.py` + `tests/roots/test-basic/`)
**Files scanned:** `typsphinx/builder.py`, `typsphinx/translator.py` (logger grep only),
`typsphinx/template_engine.py`, `typsphinx/pdf.py` (logger-idiom comparison only),
`tests/test_builder.py`, `tests/test_cross_doc_label_namespace_render_gate.py`,
`tests/test_footnotes.py`, `tests/fixtures/cross_doc_label_namespace_render_gate/conf.py`,
plus a repo-wide `grep -rl "parametrize"` / `grep -rl "caplog"` sweep of `tests/`
**Pattern extraction date:** 2026-07-21
