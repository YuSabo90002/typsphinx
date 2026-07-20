# Phase 15: Full-Corpus Validation - Pattern Map

**Mapped:** 2026-07-12
**Files analyzed:** 3 (1 new test module + inline helpers within it; 1 new report artifact; conftest.py extension considered optional)
**Analogs found:** 3 / 3 (all strong role-matches; no "no analog" files)

This phase is validation/measurement scaffolding only — no `typsphinx/` production
files are created or modified. Every new file lives under `tests/` or the phase
directory.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `tests/test_corpus_gate.py` (new sibling module — RESEARCH Pitfall 5: do NOT append to `test_pdf_render_gate.py`) | test (integration, `slow`-marked) | request-response (subprocess sphinx-build) + file-I/O (clone, PDF) | `tests/test_pdf_render_gate.py` | exact (same harness lineage: sphinx-build → typst.compile() → pypdf/file assertions) |
| Corpus clone/cache helper (`get_or_clone_corpus`-style, inline in `test_corpus_gate.py`) | utility | file-I/O + event-driven (skip-on-unavailable) | No direct in-repo analog for git-clone; closest conceptual analog is the `fixtures_dir`/`*_render_gate_dir` fixture-resolution pattern in `tests/conftest.py` + `test_pdf_render_gate.py`, generalized to a session-scoped cache dir | role-match (fixture-resolution pattern), but the git-clone/cache mechanics themselves are genuinely new (RESEARCH confirms no existing precedent) |
| `conf.py` augmentation helper (`wire_typsphinx_into_corpus_conf`-style, inline) | utility | transform (file-I/O append) | `tests/conftest.py::temp_sphinx_app` (writes a `conf.py` from scratch) | partial (same "write a Sphinx conf.py that wires typsphinx in" concern, but append-to-existing vs. write-from-scratch differ) |
| D-07 `git worktree` before/after helper (inline in `test_corpus_gate.py`, or a small standalone script per Open Question 1) | utility | event-driven (git subprocess) + request-response (two sphinx-build runs, diff) | `_run_sphinx_build_typst` in `tests/test_pdf_render_gate.py` (the subprocess invocation half); no analog for the `git worktree` half | role-match for the sphinx-build half only; git-worktree mechanics are new |
| `.planning/phases/15-full-corpus-validation/15-CORPUS-REPORT.md` | doc/report artifact | batch (one-time measurement writeup) | No code analog needed (per task guidance) — see "Report Shape Precedent" below | n/a (documentation, not code) |

## Pattern Assignments

### `tests/test_corpus_gate.py` (test, integration/slow)

**Analog:** `tests/test_pdf_render_gate.py` (read in full-relevant-sections this
session; ~1324 lines, 10 `@pytest.mark.slow` classes after Phase 14).

**Module docstring convention** (lines 1-14):
```python
"""
D-04 real-render acceptance gate for the admonition rendering fix (Phase 08.1).

...closes that gap by running the full pipeline for real:

    sphinx-build -b typst  ->  typst.compile()  ->  pypdf text-extraction

and asserting that none of the literal-source leak signatures ... appear in the
extracted PDF prose.
"""
```
Use this same "what gap does this close, what's the pipeline" docstring shape,
but naming GATE-02/D-01..D-07 instead of D-04.

**Imports pattern** (lines 16-34):
```python
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
```
`test_corpus_gate.py` should mirror this exactly, plus add `import sphinx` (for
`sphinx.__version__` tag resolution — RESEARCH Pattern 1) and `import re` +
`from collections import Counter` (RESEARCH Pattern 4, catalogue parsing). Per
RESEARCH Pitfall 5, cross-module reuse of `LEAK_SIGNATURES`/helpers from
`test_pdf_render_gate.py` is possible via `from test_pdf_render_gate import ...`
(no `tests/__init__.py` exists, confirmed — rootless pytest import discovery
allows this) — but GATE-02 doesn't need `LEAK_SIGNATURES` (that's a leak-string
check specific to the admonition/figure gates); GATE-02 only needs the
subprocess-invocation convention below, which is worth re-deriving locally
rather than importing, since it must be parameterized for `-b typstpdf` vs.
`-b typst` (RESEARCH doesn't reuse `_run_sphinx_build_typst` verbatim — it's
hardcoded to `-b typst`).

**Subprocess invocation pattern** (`_run_sphinx_build_typst`, lines 109-140):
```python
def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run `sphinx-build -b typst` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as `sys.executable -m sphinx` ... this guarantees the exact
    interpreter/venv already running this test is reused, with no dependency
    on external PATH resolution of a `uv` executable ... `["uv", "run", ...]`
    makes exit 127 ... `sys.executable -m sphinx` sidesteps that PATH-shadowing
    hazard entirely.
    """
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )
```
**Copy this exactly**, but generalize the `-b typst` literal to a parameter
(`builder: str`) since GATE-02's SC#1 needs `-b typstpdf` while SC#3's
before/after (D-07) needs `-b typst` only (RESEARCH Pitfall 2 — never invoke
`typst.compile()` on the reverted "before" translator). This is the single
most load-bearing pattern to copy: it is the documented fix for the NixOS
sandbox `uv run` PATH-shadowing hazard (see user memory
`nixos-sandbox-test-env.md`) and must not be reinvented with a different
invocation shape.

**Skip-gate decorator pattern** (lines 143-146, applied at class level):
```python
@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestFigureLengthRenderGate:
    ...
```
`test_corpus_gate.py`'s class should carry `@pytest.mark.slow` the same way
(D-04's CI-exclusion mechanism, already registered in `pyproject.toml`
`[tool.pytest.ini_options] markers` — no new marker needed). The
`TYPST_AVAILABLE`/`PYPDF_AVAILABLE` skipif pattern extends naturally to a THIRD
skip condition unique to this phase: corpus-unavailable (D-05) — but that one
is a **runtime** `pytest.skip()` inside the test/fixture (network/clone can only
be checked at test-run time, not import time), not a `skipif` decorator. See
Code Examples below.

**Core real-compile assertion shape** (`TestFigureLengthRenderGate`, lines
242-285 — representative of all 10 classes' shared shape):
```python
result = _run_sphinx_build_typst(figure_length_render_gate_dir, temp_build_dir)
assert result.returncode == 0, (
    f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
)

index_typ = temp_build_dir / "index.typ"
assert index_typ.exists(), "index.typ was not generated"
typ_source = index_typ.read_text()
# ... source-level assertions ...

pdf_output = temp_build_dir / "index.pdf"
typst.compile(str(index_typ), output=str(pdf_output))  # TypstCompilationError propagates uncaught -- this IS the fatal-check

assert pdf_output.exists(), "PDF file was not created"
assert pdf_output.stat().st_size > 0, "PDF file is empty"
with open(pdf_output, "rb") as f:
    magic = f.read(4)
    assert magic == b"%PDF", "Generated file is not a valid PDF"
```
For GATE-02's SC#1, the corpus test drives the FULL `typstpdf` builder via
subprocess (not an in-process `typst.compile()` call) — see RESEARCH Code
Examples' `test_corpus_compiles_with_no_fatal_error` — but the **assertion
shape is identical**: PDF-exists / non-empty / `%PDF`-magic-bytes, never
`returncode == 0` alone (RESEARCH Pitfall 1: a missing `typst_documents`
entry would make `returncode == 0` pass trivially with `typst.compile()`
never invoked).

**Fixture-resolution pattern** (`tests/conftest.py` lines 43-46 and
`test_pdf_render_gate.py` lines 44-107 — `fixtures_dir` → `*_render_gate_dir`
→ `temp_build_dir`):
```python
@pytest.fixture
def fixtures_dir():
    """Return the path to tests/fixtures/ directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def figure_length_render_gate_dir(fixtures_dir):
    """Return the path to the figure_length_render_gate fixture project."""
    return fixtures_dir / "figure_length_render_gate"

@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"
```
GATE-02's `corpus_doc_dir` fixture should follow the SAME naming/docstring
convention but **must be session-scoped** (unlike these function-scoped
fixtures) per RESEARCH Pitfall 3 — do not copy the function-scoped `tmp_path`
convention verbatim for the corpus clone itself (only for build *output* dirs,
which stay per-test via `tmp_path`).

---

### Corpus clone/cache helper — new, no direct analog

**Closest conceptual analog:** the fixture-resolution chain above
(`fixtures_dir` → named `*_render_gate_dir`), generalized from "resolve a path
to a committed fixture" to "resolve a path to a cached external clone,
cloning on cache-miss, returning None/skip on failure." RESEARCH's own
Code Examples section (verified/reasoned this session, HIGH confidence)
supplies the concrete implementation — reproduced here as the pattern to
follow verbatim:

```python
def get_or_clone_corpus(cache_root: Path) -> Path | None:
    """Return the path to the cloned doc/ tree, or None if unavailable.

    Caches by resolved tag so repeated local runs don't re-clone (Pitfall 3).
    Returns None (never raises) on any failure -- callers pytest.skip (D-05).
    """
    import sphinx

    tag = f"v{sphinx.__version__}"
    dest = cache_root / f"sphinx-{tag}"
    doc_dir = dest / "doc"

    if doc_dir.exists() and (doc_dir / "conf.py").exists():
        return doc_dir

    dest.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "git", "clone", "--depth", "1", "--branch", tag,
            "https://github.com/sphinx-doc/sphinx.git", str(dest),
        ],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0 or not doc_dir.exists():
        return None
    return doc_dir


@pytest.fixture(scope="session")
def corpus_doc_dir(tmp_path_factory):
    cache_root = Path.home() / ".cache" / "typsphinx-corpus-gate"
    doc_dir = get_or_clone_corpus(cache_root)
    if doc_dir is None:
        pytest.skip("Sphinx doc/ corpus unavailable (no network or clone failure) -- D-05")
    return doc_dir
```
Note: `subprocess.run([...])` list-argument form (never `shell=True`) matches
the security convention already established by `_run_sphinx_build_typst` —
reuse that same argument-list discipline here (RESEARCH Security Domain, V5).

---

### `conf.py` augmentation helper — partial analog

**Analog:** `tests/conftest.py::temp_sphinx_app` (lines 45-80) — writes a
minimal `conf.py` from scratch:
```python
conf_py = srcdir / "conf.py"
conf_py.write_text(
    "extensions = ['typsphinx']\n"
    "project = 'Test Project'\n"
    "author = 'Test Author'\n"
)
```
This shows the project's established convention for programmatically writing
Sphinx config from a test (`Path.write_text`, simple string literal). For
GATE-02, D-03 requires **append**, not write-from-scratch (the real
`doc/conf.py` must remain otherwise untouched). Adapt the `write_text`
convention to `open(conf_py, "a", ...)` per RESEARCH Pattern 2:
```python
def wire_typsphinx_into_corpus_conf(corpus_doc_dir: Path) -> None:
    """Append typsphinx wiring to the cloned doc/conf.py (mutates the
    EPHEMERAL clone only -- never the real upstream Sphinx repo)."""
    conf_py = corpus_doc_dir / "conf.py"
    with conf_py.open("a", encoding="utf-8") as f:
        f.write("\n\n# --- typsphinx corpus-gate wiring (test-only, not upstream) ---\n")
        f.write("extensions.append('typsphinx')\n")
        f.write(
            "typst_documents = [('index', 'sphinx-corpus', "
            "'Sphinx Documentation', 'the Sphinx developers')]\n"
        )
```
RESEARCH Pitfall 1 is load-bearing here: assert the appended
`typst_documents` line landed (or assert the final compiled PDF exists) —
never trust `returncode == 0` alone, since `TypstPDFBuilder.finish()`
no-ops silently if `typst_documents` is empty (see
`typsphinx/builder.py` excerpt below).

---

### D-07 `git worktree` before/after helper — new, subprocess half has analog

**Analog (subprocess half only):** `_run_sphinx_build_typst` (see above) —
reuse the exact `sys.executable -m sphinx` invocation shape, parameterized to
accept `-b typst` (not `-b typstpdf`, per RESEARCH Pitfall 2) and an `env`
override for `PYTHONPATH` (to shadow the installed `typsphinx` with the
worktree's pre-fix `translator.py` for that one subprocess call only):
```python
FIX_COMMIT = "79c9d45"  # fix(12-02): emit bracket-wrap <label> anchor in depart_term

def checkout_pre_fix_translator(repo_root: Path, worktree_dir: Path) -> None:
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree_dir), f"{FIX_COMMIT}~1"],
        cwd=repo_root, check=True,
    )

def run_translate_only(corpus_doc_dir: Path, outdir: Path, typsphinx_pythonpath: Path) -> str:
    env = {"PYTHONPATH": str(typsphinx_pythonpath)}
    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(corpus_doc_dir), str(outdir)],
        capture_output=True, text=True, env=env,
    )
    return result.stderr
```
No analog exists for the `git worktree` half — it is a self-contained ~10-line
helper per RESEARCH's own "Don't Hand-Roll" table (no library should own this;
it's a one-time git-level operation, not a standing pattern to reuse
elsewhere).

---

## Shared Patterns

### Subprocess invocation (`sys.executable -m sphinx`, never `uv run` / `shell=True`)
**Source:** `tests/test_pdf_render_gate.py::_run_sphinx_build_typst` (lines
109-140)
**Apply to:** All new subprocess calls in `test_corpus_gate.py` — the SC#1
corpus build, both SC#3 before/after builds, and (for `git`) the clone/worktree
calls (list-argument form, matching the same no-`shell=True` discipline).
**Why:** documented fix for a real NixOS sandbox PATH-shadowing hazard (user
memory `nixos-sandbox-test-env.md`); reinventing risks reintroducing that
failure mode.

### Fatal-error propagation via uncaught `TypstCompilationError`
**Source:** `typsphinx/pdf.py::TypstCompilationError` (imported implicitly
via `typst.compile()`'s raise); consumed uncaught by every
`test_pdf_render_gate.py` class (e.g. line 279:
`typst.compile(str(index_typ), output=str(pdf_output))` with no surrounding
`try/except`).
**Apply to:** `test_corpus_gate.py`'s SC#1 assertion — never wrap the compile
step in `try/except`; let a fatal error fail the test loudly (this IS the
GATE-02 pass/fail signal).

### PDF existence/validity assertion triple
**Source:** repeated verbatim across all 10 classes in
`test_pdf_render_gate.py`, e.g. lines 281-285:
```python
assert pdf_output.exists(), "PDF file was not created"
assert pdf_output.stat().st_size > 0, "PDF file is empty"
with open(pdf_output, "rb") as f:
    magic = f.read(4)
    assert magic == b"%PDF", "Generated file is not a valid PDF"
```
**Apply to:** SC#1's corpus-PDF assertion — this triple (exists / non-empty /
magic-bytes), never `returncode == 0` alone (RESEARCH Pitfall 1).

### `unknown_visit` warning source (for SC#2 catalogue parsing)
**Source:** `typsphinx/translator.py` lines 2424-2445:
```python
def unknown_visit(self, node: nodes.Node) -> None:
    from sphinx.util import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"unknown node type: {node}")

def unknown_departure(self, node: nodes.Node) -> None:
    pass
```
**Apply to:** `test_corpus_gate.py`'s catalogue helper — the warning text is
`str(node)` (full untruncated XML-ish subtree, potentially multi-line), so
parsing MUST anchor on the `"WARNING: unknown node type: <"` line-start
prefix (RESEARCH Pattern 4 `UNKNOWN_NODE_RE`), never split on raw `"\n"` or
use substring counting (RESEARCH Pitfall 4).

### Empty-URL warning source (for D-07/SC#3 before/after measurement)
**Source:** `typsphinx/translator.py::visit_reference`, lines 2358-2369:
```python
if not refuri:
    logger.warning(
        f"Reference node has empty URL. "
        f"Link will be rendered as plain text. "
        f"Check for broken references in source: {node.astext()}"
    )
    self._skip_link_wrapper = True
    return
```
**Apply to:** SC#3's before/after count — grep both stderrs for
`"Reference node has empty URL"` and diff counts. Note the `refid` branch
immediately above (lines 2343-2356, `if not refuri and refid:`) predates
XREF-01 (landed Phase 11, confirmed untouched by commit `79c9d45`) — do not
revert it; only `depart_term`'s label-anchor emission (lines 1234-1267,
specifically the `node.get("ids")` branch at 1262-1264) is the D-07 revert
target.

### `typst_documents`-empty no-op landmine (Pitfall 1 source)
**Source:** `typsphinx/builder.py::TypstPDFBuilder.finish()`, lines 531-538:
```python
typst_documents = getattr(self.config, "typst_documents", [])

if not typst_documents:
    logger.warning(
        "No documents defined in typst_documents. Nothing to compile."
    )
    return
```
**Apply to:** every SC#1 assertion must be keyed on PDF-file-existence, not
`returncode`/`stdout` alone, since this silent early-return makes a
`returncode == 0` check pass trivially without ever calling
`compile_typst_to_pdf` (defined at line 542 onward, `docname = doc_tuple[0]`
— confirms the output filename is `index.pdf`, matching RESEARCH Open
Question 2's resolution: assert on `outdir / "index.pdf"`, not the tuple's
second/"target" field).

## No Analog Found

None outright — every planned file has at least a partial/role-match analog
(see table above). The two genuinely novel mechanics (git clone/cache, git
worktree) have no in-repo precedent per RESEARCH's own "Don't Hand-Roll"
table, but RESEARCH supplies verified/reasoned implementations to use
directly (Code Examples section, reproduced above) rather than the planner
needing to invent them from scratch.

## Report Shape Precedent (for `15-CORPUS-REPORT.md`, D-06)

No prior `.planning/phases/*/` directory contains a committed `*-REPORT.md`
measurement artifact (all prior phase dirs follow the standard
`NN-CONTEXT.md` / `NN-RESEARCH.md` / `NN-PLAN.md` / `NN-SUMMARY.md` /
`NN-VERIFICATION.md` naming — confirmed via the phase directory structure
already read for CONTEXT/RESEARCH this session). `15-CORPUS-REPORT.md` is a
genuinely new artifact shape for this project; no existing report-formatting
convention to copy. Recommend two tables (frequency-ranked `unknown_visit`
catalogue; empty-URL before/after counts + delta), each with a "resolved
corpus tag + commit SHA" preamble line (RESEARCH Security Domain: log
`git rev-parse HEAD` inside the clone for future diffability against a
possibly-force-moved tag).

## Metadata

**Analog search scope:** `tests/` (full `test_pdf_render_gate.py` +
`conftest.py`), `typsphinx/builder.py` (`TypstPDFBuilder.finish()`),
`typsphinx/translator.py` (`visit_reference`/`depart_reference`,
`visit_term`/`depart_term`, `unknown_visit`/`unknown_departure`),
`.planning/phases/*/` (report-shape precedent check).
**Files scanned:** 4 source files read directly this session (line-counted:
1323 + 114 + 567 + relevant ~350 lines of 3509 in translator.py), plus
CONTEXT.md/RESEARCH.md for this phase.
**Pattern extraction date:** 2026-07-12
</content>
