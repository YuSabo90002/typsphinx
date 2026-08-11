# Phase 44: `typst_documents` Default Derivation + Builder Input Hardening - Pattern Map

**Mapped:** 2026-08-04
**Files analyzed:** 6 (2 modified production files, 4 new test-related files)
**Analogs found:** 6 / 6

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `typsphinx/__init__.py` (registration line, L44) | config | request-response (one-line literal→callable swap) | itself (surrounding `add_config_value` block, L44-60) | exact — edit-in-place, no external analog needed |
| `typsphinx/builder.py` (`_default_typst_documents`, new function) | utility (pure config-derivation function) | transform | `sphinx/builders/latex/__init__.py::default_latex_documents` (installed `.venv`) | exact — this is a direct transcription target |
| `typsphinx/builder.py` (`TypstPDFBuilder.finish()`, BLD-01 guard) | builder / controller-equivalent | batch (aggregate-then-raise loop) | the existing `if not doc_tuple:` guard 3 lines above, same file/method | exact — same method, same loop, same style |
| `typsphinx/builder.py` (`finish()`, D-03 warning wording) | builder | request-response | the existing `logger.warning(...)` block at L906-909, same method | exact — wording-only edit |
| `tests/fixtures/<new>/conf.py` (CONF-08 unset-default fixture) | test fixture (config) | CRUD (static config file) | `tests/fixtures/missing_and_malformed_master_gate/conf.py` (structure/comment style); deviates from all 103 existing fixtures by omitting `typst_documents` | role-match — same fixture shape, opposite content |
| `tests/test_<new>_default_derivation_gate.py` (CONF-08 gate) | test (integration, subprocess) | request-response | `tests/test_missing_and_malformed_master_gate.py` | exact — same subprocess-gate pattern, template for structure |
| `tests/fixtures/<new>/conf.py` (BLD-01 non-str-docname fixture) | test fixture (config) | CRUD (static config file) | `tests/fixtures/missing_and_malformed_master_gate/conf.py` | exact — same "one valid master + bad entries" shape, new bad-entry kind |
| `tests/test_<new>_non_str_docname_gate.py` (BLD-01 gate) | test (integration, subprocess) | request-response | `tests/test_missing_and_malformed_master_gate.py` | exact — same subprocess-gate pattern |

## Pattern Assignments

### `typsphinx/__init__.py` (config registration, L44)

**Analog:** itself — the surrounding block in the same file (`typsphinx/__init__.py:28-66`), read in full this session.

**Current state, the line D-04 changes** (line 44):
```python
def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_builder(TypstBuilder)
    app.add_builder(TypstPDFBuilder)

    # Register configuration values
    app.add_config_value("typst_documents", [], "html", [list])   # <-- L44, this line changes
    app.add_config_value("typst_template", None, "html", [str, type(None)])
    ...
```

**Target shape** — every other `add_config_value` call in this block keeps the exact positional-arg convention `(name, default, "html", [types])`; a callable default fits without changing that shape:
```python
from typsphinx.builder import TypstBuilder, TypstPDFBuilder, _default_typst_documents

...
    app.add_config_value("typst_documents", _default_typst_documents, "html", [list])
```

**Import placement:** `typsphinx/__init__.py:25` already does `from typsphinx.builder import TypstBuilder, TypstPDFBuilder` — extend that same import line with `_default_typst_documents` rather than adding a second import line, matching the file's existing single-import-per-module style.

---

### `typsphinx/builder.py` — new `_default_typst_documents(config)` function

**Analog:** `sphinx/builders/latex/__init__.py::default_latex_documents` (installed `sphinx==9.1.0`, read via `inspect.getsource` this session — see RESEARCH.md "Code Examples").

**Upstream pattern being transcribed** (verified this session):
```python
# .venv/.../sphinx/builders/latex/__init__.py:575-587
def default_latex_documents(config: Config) -> list[tuple[str, str, str, str, str]]:
    """Better default latex_documents settings."""
    project = texescape.escape(config.project, config.latex_engine)
    author = texescape.escape(config.author, config.latex_engine)
    return [
        (
            config.root_doc,
            make_filename_from_project(config.project) + '.tex',
            texescape.escape_abbr(project),
            texescape.escape_abbr(author),
            config.latex_theme,
        )
    ]

# registration, same file:604-606
app.add_config_value(
    'latex_documents', default_latex_documents, '', types=frozenset({list, tuple})
)
```

**typsphinx transcription (this phase, new)** — no `texescape` (Typst has no equivalent macro-escaping need; `entry[2]`/`entry[3]` are dead weight per D-02/Pitfall 4), `.typ` instead of `.tex`, literal `"typst"` for the 5th element:
```python
def _default_typst_documents(config: Config) -> list:
    """Sphinx-native default for ``typst_documents``, mirroring
    ``sphinx.builders.latex.default_latex_documents`` (CONF-08).

    Derives a single master entry from ``root_doc``/``project``/``author``,
    with the target name in LaTeX's own shape (``make_filename_from_project``).
    Only invoked when the user has NOT set ``typst_documents`` in conf.py --
    an explicit setting (including an explicit ``[]``) always wins, because
    Sphinx's ``Config.__getattr__`` checks ``_raw_config`` before falling
    back to this callable default.
    """
    return [
        (
            config.root_doc,
            make_filename_from_project(config.project) + ".typ",
            config.project,
            config.author,
            "typst",
        )
    ]
```

**Imports needed** (`typsphinx/builder.py` currently imports, L8-22 — read this session):
```python
import os
import posixpath
import shutil
from collections.abc import Iterator
from os import path
from typing import List, Set, Tuple

from docutils import nodes
from sphinx.builders import Builder
from sphinx.errors import ExtensionError
from sphinx.util import logging
from sphinx.util.osutil import ensuredir

from typsphinx.pdf import compile_typst_file_to_pdf
from typsphinx.writer import TypstWriter
```
Add: `from sphinx.config import Config` (for the type hint) and `from sphinx.util.osutil import make_filename_from_project` (extend the existing `sphinx.util.osutil` import line rather than adding a new one, matching the file's one-import-per-module convention — it already imports `ensuredir` from that same module).

**Placement:** module-level, immediately above `class TypstBuilder` (L27) — keeps it close to `_resolve_output_stem`, its downstream consumer, per RESEARCH.md's Assumption A1 (a free organizational choice, not a locked contract).

---

### `typsphinx/builder.py` — `TypstPDFBuilder.finish()`, BLD-01 guard

**Analog:** the existing `if not doc_tuple:` guard three lines above the insertion point, same method, same file (`typsphinx/builder.py:924-928`, read in full this session).

**Current code at the insertion site** (verified against current file, offsets 916-931 this session):
```python
for doc_tuple in typst_documents:
    # doc_tuple format: (sourcename, targetname, title, author).
    # Resolve the stem ONCE so the .typ read-back path and the .pdf
    # write path can never drift from each other (Issue #117).
    # Mirror _resolve_output_stem's own length guard here: a
    # malformed entry (e.g. an empty tuple from a misconfigured
    # typst_documents) must not raise an uncaught IndexError on
    # doc_tuple[0] before that helper's defenses ever run.
    if not doc_tuple:
        logger.warning(f"Malformed typst_documents entry: {doc_tuple!r}")
        failures.append((repr(doc_tuple), "malformed typst_documents entry"))
        continue
    docname = doc_tuple[0]
    stem = self._resolve_output_stem(docname)
    relative_path = self._directory_preserving_relpath(docname, stem)
    typ_file = path.normpath(path.join(self.outdir, relative_path + ".typ"))
```

**BLD-01's guard, inserted immediately after `docname = doc_tuple[0]`, matching the sibling guard's exact shape (warn → append to `failures` → `continue`)**:
```python
    docname = doc_tuple[0]
    if not isinstance(docname, str):
        message = (
            f"typst_documents entry has a non-str docname: {docname!r} "
            "-- expected a str"
        )
        logger.warning(message)
        failures.append((repr(docname), message))
        continue
    stem = self._resolve_output_stem(docname)
    relative_path = self._directory_preserving_relpath(docname, stem)
    typ_file = path.normpath(path.join(self.outdir, relative_path + ".typ"))
```

**Error-aggregation pattern this joins** (unchanged, already exists at the bottom of `finish()`, L963-967):
```python
if failures:
    summary = "; ".join(f"{docname}: {err}" for docname, err in failures)
    raise ExtensionError(
        f"typstpdf: {len(failures)} master document(s) failed: {summary}"
    )
```
`failures: List[Tuple[str, str]]` is declared once at L914 — no new list, no new exception class.

**Do NOT** validate inside `_directory_preserving_relpath` itself (RESEARCH.md Pitfall 3) — that method has other callers (`write_doc`) that only ever receive real docnames from `env.found_docs`; the guard belongs in `finish()`'s loop, in the same place as the sibling `if not doc_tuple:` check.

---

### `typsphinx/builder.py` — `finish()`, D-03 warning wording (early-return branch)

**Analog:** the existing block itself, `typsphinx/builder.py:906-910` (wording-only change, same log level).

**Current:**
```python
if not typst_documents:
    logger.warning(
        "No documents defined in typst_documents. Nothing to compile."
    )
    return
```

**Target wording** (severity stays `WARNING` — D-03 explicit; matches Sphinx LaTeX's `no "latex_documents" config value found; no documents will be written` precedent for the equivalent situation):
```python
if not typst_documents:
    logger.warning(
        "typst_documents is explicitly set to an empty list -- nothing will "
        "be compiled. Remove the setting entirely to use the derived "
        "default (root_doc/project/author)."
    )
    return
```
Reachable only via an explicit `typst_documents = []` once D-04 lands (unset now resolves through the callable default instead).

---

### `tests/fixtures/<new_conf08_fixture>/conf.py` (CONF-08 — omits `typst_documents` entirely)

**Analog (deviated from deliberately):** `tests/fixtures/missing_and_malformed_master_gate/conf.py` (read in full this session, 2693 bytes) — for the *comment-block convention* (explains what the fixture proves, what must NOT be added/removed and why); content deviates because this is the first fixture of 104 that must NOT set `typst_documents`.

**Structural convention to copy** (project/author/release header, `extensions = ["typsphinx"]`, then a comment explaining the load-bearing omission):
```python
# Sphinx configuration for the CONF-08 default-derivation gate.
#
# Deliberately has NO `typst_documents = ...` line -- this is the ONLY way
# to exercise the unset path; all 103 other conf.py files in this repo set
# typst_documents explicitly (repo-wide census, RESEARCH.md). Do not add a
# typst_documents line here; doing so would silently stop this fixture from
# exercising CONF-08 at all.

project = "Quickstart Default Gate"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

# typst_documents intentionally left unset -- CONF-08's derivation must
# resolve it to [('index', 'quickstartdefaultgate.typ', project, author,
# 'typst')].
```
Recommendation (RESEARCH.md Open Question 2): a small purpose-built fixture (2-3 files: `conf.py` + `index.rst`), not a reuse of the shared `tests/roots/test-basic` (which already sets `typst_documents` and is shared across unrelated gates).

---

### `tests/test_<new>_default_derivation_gate.py` (CONF-08 gate)

**Analog:** `tests/test_missing_and_malformed_master_gate.py` (full file read this session, 231 lines) — the established real-`sphinx-build`-subprocess gate module shape.

**Imports + skip-guard + subprocess-helper pattern to copy verbatim** (lines 37-79 of the analog):
```python
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GATE_FIXTURE_DIR = FIXTURES_DIR / "<new_fixture_name>"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's.
    """
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", builder, str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the default-derivation gate",
)
class TestDefaultTypstDocumentsDerivationGate:
    """CONF-08: unset typst_documents still produces a PDF, named via
    make_filename_from_project; an explicit setting always wins (SC#2)."""

    def test_unset_typst_documents_produces_pdf(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir, "typstpdf")

        assert result.returncode == 0, (
            f"Expected a successful build with typst_documents unset:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (build_dir / "quickstartdefaultgate.typ").exists()
        assert (build_dir / "quickstartdefaultgate.pdf").exists()
```
Note the polarity: unlike `test_missing_and_malformed_master_gate.py` (a deliberate must-FAIL gate), CONF-08's gate is a normal must-SUCCEED gate — matching the majority-pattern `*_render_gate.py` modules (`test_target_name_render_gate.py` et al.), asserting `returncode == 0`.

---

### `tests/fixtures/<new_bld01_fixture>/conf.py` + `tests/test_<new>_non_str_docname_gate.py` (BLD-01 gate)

**Analog:** `tests/fixtures/missing_and_malformed_master_gate/conf.py` + `tests/test_missing_and_malformed_master_gate.py` — directly reusable as the template; BLD-01 adds a THIRD bad-entry kind (non-str docname) rather than reusing the two existing kinds.

**Fixture pattern** (one valid master + one bad entry, mirroring the analog's `typst_documents` list shape exactly):
```python
project = "Non-Str Docname Gate"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index", project, author),
    (123, "manual.typ", "Bad Docname", "Test Author"),
]
```

**Gate assertions to copy from the analog's must-fail shape** (`test_mixed_bad_entries_fail_build_but_good_master_still_compiles`, L96-169):
- `result.returncode != 0`
- an aggregate-message fragment specific to BLD-01's new wording (`"typst_documents entry has a non-str docname"`)
- `(build_dir / "index.typ").exists()` and `(build_dir / "index.pdf").exists()` — the valid master still compiles (D-02's attempt-all-then-raise contract, same as WR-01's)
- absence of the raw `TypeError` string (mirrors the analog's `"IndexError" not in result.stderr` regression assertion) to prove the crash is caught, not merely relocated

## Shared Patterns

### Aggregate-then-raise error handling
**Source:** `typsphinx/builder.py:914,924-927,963-967` (`failures: List[Tuple[str, str]]`, the `if not doc_tuple:` guard, the terminal `ExtensionError`)
**Apply to:** BLD-01's guard — join the existing list, do not invent a second error path or raise immediately (RESEARCH.md "Don't Hand-Roll", "Anti-Patterns to Avoid").

### Sphinx callable-config-default protocol
**Source:** `sphinx/config.py:446-470` (`Config.__getattr__`, installed `.venv`, read this session) — callable defaults are invoked fresh on every access, never cached (`self.__dict__[name] = default` only happens on the non-callable branch).
**Apply to:** `_default_typst_documents` — must stay a pure function of its `config` argument; no memoization, no module-level mutable state (RESEARCH.md Pitfall 1).

### Real-`sphinx-build`-subprocess gate skeleton
**Source:** `tests/test_missing_and_malformed_master_gate.py:37-79` (`TYPST_AVAILABLE` try/except guard, `_run_sphinx_build` via `sys.executable -m sphinx`, per-module copy of the helper — not shared/imported).
**Apply to:** both new gate test modules (CONF-08 and BLD-01) — same skip-guard convention, same subprocess invocation style, sidesteps the documented NixOS PATH-shadowing hazard.

### Fixture `conf.py` header-comment convention
**Source:** `tests/fixtures/missing_and_malformed_master_gate/conf.py:1-38` — explains what the fixture proves, enumerates each `typst_documents` entry's purpose, and warns against edits that would silently stop exercising the condition (e.g. "do not add a ghost.rst file").
**Apply to:** both new fixtures — especially the CONF-08 fixture, where the *absence* of a line is the load-bearing fact and needs an explicit comment saying so.

## No Analog Found

None — every file this phase touches or creates has a direct, verified analog in the current codebase.

## Metadata

**Analog search scope:** `typsphinx/` (both production files read in full), `tests/` (test_config.py, test_target_name_render_gate.py, test_missing_and_malformed_master_gate.py, and the `missing_and_malformed_master_gate` fixture directory read in full), installed `sphinx==9.1.0` package (`sphinx/builders/latex/__init__.py`, `sphinx/config.py`).
**Files scanned:** 8 (2 production, 4 test/fixture analogs, 2 upstream Sphinx source files) plus a `tests/` directory listing (63 `*_gate.py` modules, 3 fixture dirs with "master" in the name) to confirm naming conventions and rule out an existing reusable fixture.
**Pattern extraction date:** 2026-08-04
</content>
