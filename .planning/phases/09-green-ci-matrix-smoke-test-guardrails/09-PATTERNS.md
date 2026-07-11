# Phase 9: Green CI Matrix + Smoke Test + Guardrails - Pattern Map

**Mapped:** 2026-07-11
**Files analyzed:** 4 (2 new code files, 2 CI/config verification-only surfaces)
**Analogs found:** 2 exact / 2 verification-only (no code analog needed)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `tests/test_preview_smoke_gate.py` (new) | test | request-response (subprocess invoke → compile → assert) | `tests/test_pdf_render_gate.py` | exact |
| `tests/fixtures/preview_smoke/conf.py` (new) | config (Sphinx fixture project) | request-response | `tests/fixtures/admonition_render_gate/conf.py` | exact |
| `tests/fixtures/preview_smoke/index.rst` (new) | fixture content | transform (rST → Typst) | `tests/fixtures/admonition_render_gate/index.rst` | exact |
| `.github/workflows/{ci,docs,drift}.yml`, `.github/dependabot.yml`, `pyproject.toml` | config (verification-only, CI-01/CI-03) | N/A | themselves (read/verify, no edit expected per D-06/D-02) | n/a — no code analog needed |

## Pattern Assignments

### `tests/test_preview_smoke_gate.py` (test, request-response)

**Analog:** `tests/test_pdf_render_gate.py` (Phase 8.1's D-04 gate — the exact sphinx-build → typst.compile() → assert pipeline this phase reuses)

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
Adaptation for the new file: the smoke gate only needs `typst` (compile-success is sufficient per RESEARCH.md D-04/D-05 — no text-extraction assertion is required), so drop the `pypdf` import/availability block entirely and gate solely on `TYPST_AVAILABLE`. This also simplifies the skipif condition below (no `and PYPDF_AVAILABLE`).

**Fixture-path pattern** (lines 43-58):
```python
@pytest.fixture
def fixtures_dir():
    """Return the path to tests/fixtures/ directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def admonition_render_gate_dir(fixtures_dir):
    """Return the path to the admonition_render_gate fixture project."""
    return fixtures_dir / "admonition_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"
```
Copy verbatim, renaming the fixture-specific accessor to `preview_smoke_dir` pointing at `fixtures_dir / "preview_smoke"`.

**skipif + class pattern** (lines 61-70):
```python
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the D-04 render gate",
)
class TestAdmonitionPdfRenderGate:
    """
    Real-compile acceptance gate for the admonition markup/code-mode fix.

    Requirements: D-04 (08.1-RESEARCH.md, 08.1-VALIDATION.md).
    """
```
Adapt to: `@pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst-py is required for the CI-02 preview-package smoke gate")` on a class (or bare function) named e.g. `TestPreviewSmokeGate` / `test_preview_smoke_all_four_packages_compile`, docstring referencing CI-02/09-RESEARCH.md instead of D-04/08.1.

**Core sphinx-build → typst.compile() pattern** (lines 93-120, the load-bearing excerpt):
```python
result = subprocess.run(
    [
        sys.executable,
        "-m",
        "sphinx",
        "-b",
        "typst",
        str(admonition_render_gate_dir),
        str(temp_build_dir),
    ],
    capture_output=True,
    text=True,
)
assert result.returncode == 0, (
    f"sphinx-build failed:\n"
    f"stdout: {result.stdout}\n"
    f"stderr: {result.stderr}"
)

index_typ = temp_build_dir / "index.typ"
assert index_typ.exists(), "index.typ was not generated"

# 2. Compile the emitted .typ to PDF with typst-py.
pdf_output = temp_build_dir / "index.pdf"
typst.compile(str(index_typ), output=str(pdf_output))

assert pdf_output.exists(), "PDF file was not created"
assert pdf_output.stat().st_size > 0, "PDF file is empty"
```
Copy this block verbatim (swap `admonition_render_gate_dir` → the new fixture-dir fixture name). Preserve the inline comment (lines 79-92) explaining why `sys.executable -m sphinx` is used instead of `uv run sphinx-build` (PATH-shadowing hazard in this project's dev sandbox) — it applies identically to the new test and should not be dropped or paraphrased away.

**Error handling / assertion pattern:** No `try/except` wrapper is used anywhere in the analog — errors propagate naturally (`subprocess.run` returncode is asserted; `typst.compile()` is called unwrapped so a `typst.TypstError` fails the test with the real Typst error message in the traceback, e.g. `unknown variable: kai`). RESEARCH.md explicitly confirms this bare-call pattern is sufficient for CI-02 — do not add a `try/except typst.TypstError` wrapper; an uncaught exception is the intended, loudest signal.

**What NOT to reuse from the analog:** The final block (lines 125-133, pypdf text-extraction + `LEAK_SIGNATURES` substring checks) is specific to the admonition markup/code-mode leak-detection concern (D-04, Phase 8.1) and is NOT part of this phase's pattern — CI-02 only needs compile-success, not text-content assertions. Per RESEARCH.md "Alternatives Considered," do not conflate the two concerns.

---

### `tests/fixtures/preview_smoke/conf.py` (config, Sphinx fixture project)

**Analog:** `tests/fixtures/admonition_render_gate/conf.py`

**Full pattern to copy** (entire file, 15 lines):
```python
project = "Admonition Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template plus the gentle-clues @preview import -- included
# documents only get a minimal import set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Admonition Render Gate", "Test Author"),
]
```
Adapt `project`/`typst_documents` title strings to "Preview Smoke" (or similar); update the trailing comment to reference all four `@preview` packages instead of just gentle-clues, since Pattern 3 in RESEARCH.md confirms all four are unconditionally imported on the master-document path regardless — the comment's substance (master doc → full template + imports) still applies verbatim, just broaden the wording.

---

### `tests/fixtures/preview_smoke/index.rst` (fixture content, transform)

**Analog:** `tests/fixtures/admonition_render_gate/index.rst`

**Structural pattern to copy** (docstring-style intro + section headers + directive blocks):
```rst
Admonition Render Gate
=======================

This fixture exists solely to be compiled to PDF and text-extracted by
``tests/test_pdf_render_gate.py`` (D-04). It is not meant to be read as
prose -- it exercises the admonition markup/code-mode fix against a real
Typst compile.

Golden Note
-----------

.. note::

   This setting only applies to local custom templates (``typst_template``).
   Typst Universe packages (``typst_package``) handle assets automatically.
```
Follow this exact shape (title/underline, explanatory intro referencing the new test module and requirement ID, then one section per exercised directive type) but with content per RESEARCH.md's exact recommended fixture (Code Examples section):
```rst
Preview Smoke
=============

.. note::

   Exercises gentle-clues (admonition -> clue-type content block).

.. code-block:: python

   x = 1

Exercises codly + codly-languages (labeled code block -> codly()/codly-range()
calls, initialized globally via #codly(languages: codly-languages)).

.. math::

   e^{i \pi} + 1 = 0

Exercises mitex (block math -> a real ``mitex(`...`)`` call -- this is the
code path the ``kai`` regression broke, and the only one the existing
admonition_render_gate fixture never invokes).
```
**Critical requirement (do not omit):** the `.. math::` block is the one piece of content the admonition analog never included — it is the entire point of this new fixture (RESEARCH.md Anti-Pattern: "Trusting `#import` presence as proof of coverage"). All three directive types (`.. note::`, `.. code-block:: python`, `.. math::`) must be present for the fixture to close the CI-02 gap; a fixture missing the math block would compile fine but prove nothing about mitex.

---

## Shared Patterns

### sphinx-build subprocess invocation (avoid PATH-shadowing hazard)
**Source:** `tests/test_pdf_render_gate.py` lines 93-105 (comment at 79-92)
**Apply to:** `tests/test_preview_smoke_gate.py`
```python
result = subprocess.run(
    [sys.executable, "-m", "sphinx", "-b", "typst", str(fixture_dir), str(build_dir)],
    capture_output=True,
    text=True,
)
```
Always invoke via `sys.executable -m sphinx`, never `["uv", "run", "sphinx-build", ...]` — a documented PATH-shadowing hazard in this repo's dev sandbox makes the latter exit 127 when spawned from a pytest subprocess.

### skipif-on-availability, no `slow` marker
**Source:** `tests/test_pdf_render_gate.py` lines 61-64
**Apply to:** `tests/test_preview_smoke_gate.py`
```python
@pytest.mark.skipif(not TYPST_AVAILABLE, reason="...")
```
Confirmed via RESEARCH.md: no test in this repo uses the declared `slow` marker — do not introduce it here; the fixture compile is sub-second.

### Master-document fixture wiring
**Source:** `tests/fixtures/admonition_render_gate/conf.py` (`typst_documents` list)
**Apply to:** `tests/fixtures/preview_smoke/conf.py`
```python
typst_documents = [
    ("index", "index", "<Title>", "Test Author"),
]
```
Declaring `index` as a master document routes it through the full-template path (`template_engine.py`/`templates/base.typ`), which — per RESEARCH.md Pattern 3 — unconditionally imports and initializes all four `@preview` packages identically to the included-document path; master-document choice is for parity with the existing 8.1 gate, not because it changes which packages get imported.

## No Analog Found / Verification-Only Files

These files are read/verified, not created or meaningfully modified — CONTEXT.md D-02/D-06 explicitly forbid manufacturing edits here unless verification finds a real discrepancy:

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `.github/workflows/ci.yml` | config (CI workflow) | event-driven | CI-01 observes it via a PR run; D-02 forbids trigger edits. `workflow_dispatch` already exists — use `gh workflow run ci.yml --ref release/v0.5.0` to pre-flight, no file change. |
| `.github/workflows/docs.yml` | config (CI workflow) | event-driven | Same — no `workflow_dispatch`, no trigger edit permitted (D-02); observed only via the `release/v0.5.0 -> main` PR. |
| `.github/workflows/drift.yml` | config (CI workflow) | batch (weekly `uv lock --upgrade`) | Confirmed via grep: no hardcoded version ceilings exist to update (CI-03 verification, D-06). |
| `.github/dependabot.yml` | config | event-driven | `sphinx-typst-stack` group has pattern-only matching (`sphinx*`/`docutils*`/`typst*`), no version fields — confirmed no edit needed. |
| `pyproject.toml` (ceilings) | config | N/A | `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16` already present (lines 28-30) — confirmed already correct from Phases 6/7, no edit needed for CI-03. |

**Additional non-file action surfaced by research (not a git-tracked file, out of PATTERNS.md's normal scope but load-bearing for planning):** `main` branch's `required_status_checks.contexts` (a GitHub repo *setting*, via `gh api repos/.../branches/main/protection`) is stale — it still names `"Test Python 3.10 on ubuntu-latest"` / `"Test Python 3.11 on ubuntu-latest"`, job names `ci.yml` no longer produces, and never included the OS-matrix/`build-docs` variants. This has no code analog; the planner should treat it as a `gh api --method PUT` task, not a file edit.

## Metadata

**Analog search scope:** `tests/`, `tests/fixtures/`, `.github/workflows/`, `.github/dependabot.yml`, `pyproject.toml`
**Files scanned:** `tests/test_pdf_render_gate.py`, `tests/test_preview_version_sync.py` (referenced, not excerpted — internal-only version-sync check, no new file mirrors it), `tests/fixtures/admonition_render_gate/conf.py`, `tests/fixtures/admonition_render_gate/index.rst`, `.github/workflows/drift.yml`, `.github/dependabot.yml`, `pyproject.toml`
**Pattern extraction date:** 2026-07-11
