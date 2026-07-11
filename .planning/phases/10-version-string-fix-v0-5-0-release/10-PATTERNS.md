# Phase 10: Version-String Fix + v0.5.0 Release - Pattern Map

**Mapped:** 2026-07-11
**Files analyzed:** 5 (all modified, none newly created)
**Analogs found:** 5 / 5

## File Classification

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|----------------|------|-----------|-----------------|----------------|
| `typsphinx/__init__.py` | config/module-init | request-response (metadata read at import time) | `typsphinx/pdf.py` (`get_typst_version()`, lines 84-107) | exact — same `importlib.metadata.version()` + try/except + string-sentinel-fallback pattern |
| `pyproject.toml` | config | CRUD (single literal field edit) | n/a (data file, not code) — precedent for *how it's consumed* is `docs/source/conf.py:21-25` | role-match |
| `uv.lock` | config (generated artifact) | batch (regenerated, not hand-edited) | n/a — regenerate via `uv lock` | n/a |
| `tests/test_extension.py` | test | request-response (assertion against static file read) | `docs/source/conf.py` (lines 10-25, `tomllib` parse of `pyproject.toml`) | exact — same tomllib-parse-`pyproject.toml` technique, adapted from Sphinx config into a pytest assertion |
| `CHANGELOG.md` | config/docs | CRUD (append new versioned section) | `CHANGELOG.md` itself — `## [0.4.3] - 2025-11-01` entry (lines 10-14) is the in-file structural precedent | exact — same file, same section shape |

## Pattern Assignments

### `typsphinx/__init__.py` (module-init / config, request-response)

**Analog:** `typsphinx/pdf.py` lines 84-107 (`get_typst_version()`)

**Current state to replace** (`typsphinx/__init__.py` lines 1-15):
```python
"""
Sphinx Typst Extension
=======================

A Sphinx extension that provides Typst output format support.
...
:copyright: Copyright 2024 by Sphinx Typst Contributors
:license: MIT, see LICENSE for details.
"""

__version__ = "0.4.3"
__author__ = "YuSabo"

from typing import Any, Dict

from sphinx.application import Sphinx

from typsphinx.builder import TypstBuilder, TypstPDFBuilder
```

**Analog pattern to copy** (`typsphinx/pdf.py` lines 96-105 — existing in-repo precedent for exactly this problem, applied to the `typst` package instead of `typsphinx`):
```python
        # Try to get from package metadata
        try:
            from importlib.metadata import version

            return version("typst")
        except Exception:
            pass

        # Fallback
        return "unknown"
```

**Target implementation shape** (adapt the `pdf.py` try/except + `"unknown"` sentinel to a module-level assignment, catching the specific `PackageNotFoundError` rather than bare `Exception` since this is unconditional module-load code, not a nested fallback inside a broader try):
```python
import importlib.metadata

try:
    __version__ = importlib.metadata.version("typsphinx")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"
__author__ = "YuSabo"
```

Notes:
- `pdf.py` imports `from importlib.metadata import version` (name import) inside the function; `__init__.py`'s top-level placement should use `import importlib.metadata` (module import) so `PackageNotFoundError` is reachable as `importlib.metadata.PackageNotFoundError` without an extra import line — matches stdlib docs usage and keeps the diff minimal.
- `"unknown"` is the exact fallback sentinel string already established in `pdf.py:105` — reuse verbatim for consistency (CONTEXT.md leaves this to discretion, but the in-repo precedent already exists, so match it rather than choosing e.g. `"0.0.0.dev0"`).
- `setup()` (lines 24-65, unchanged) already returns `"version": __version__` at line 62 — no edit needed there; fixing the assignment fixes this automatically.

---

### `tests/test_extension.py` (test, request-response / independent-comparison)

**Analog:** `docs/source/conf.py` lines 10-25 (existing in-repo `tomllib`-based `pyproject.toml` parse)

**Imports pattern to copy** (`docs/source/conf.py` lines 10-13 — note: skip the `tomli` <3.11 fallback branch, since the test file should use plain `import tomllib` given the confirmed 3.12 floor; this fallback is legacy/dead code in `conf.py` itself and not part of this phase's scope):
```python
try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib
```

**Core read pattern** (`docs/source/conf.py` lines 21-25):
```python
# Read version from pyproject.toml
pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
with open(pyproject_path, "rb") as f:
    pyproject_data = tomllib.load(f)
    version = pyproject_data["project"]["version"]
```

**Existing test-file structure to extend** (`tests/test_extension.py` — no fixtures, no class, flat `def test_*()` functions, each doing its own local imports; see existing `test_setup_version_matches`, lines 54-68):
```python
def test_setup_version_matches():
    """Test that setup() returns correct version matching package version."""
    from typsphinx import __version__, setup

    class MockApp:
        def add_builder(self, builder):
            pass

        def add_config_value(self, name, default, rebuild, types):
            pass

    app = MockApp()
    metadata = setup(app)

    assert metadata["version"] == __version__
```

**New test to add** (combine the two patterns above — `tomllib`-parse from `conf.py` + flat-function style from `test_extension.py`; place at module top-level alongside a module-level `import tomllib` and `from pathlib import Path`, consistent with `conf.py`'s style, or inline the import inside the test function to match this file's existing local-import convention — either is acceptable, prefer local-import to match this file's existing 4 tests which all do `from typsphinx import ... ` inside the function body):
```python
def test_version_matches_pyproject_toml():
    """__version__ must match pyproject.toml's [project].version directly --
    an independent check, not merely re-deriving from the same
    importlib.metadata call __version__ itself uses."""
    import tomllib
    from pathlib import Path

    import typsphinx

    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    assert typsphinx.__version__ == pyproject_data["project"]["version"]
```

**Keep unchanged:** `test_setup_version_matches` (lines 54-68) — still validates `setup()` wiring (that it echoes `__version__` rather than a second hardcoded string), just no longer sufficient alone as a drift guard. Add the new test alongside it, do not replace it.

---

### `pyproject.toml` (config, CRUD — single field edit)

No analog needed — this is a literal value edit, not a code pattern.

**Current** (line 7): `version = "0.4.4"`
**Target:** `version = "0.5.0"`

Consuming precedent confirming this is the sole canonical source `docs/source/conf.py:21-25` (see above) and `.github/workflows/release.yml`'s "Verify version matches pyproject.toml" step (not read in full here — RESEARCH.md already confirms it parses this same field via `tomllib`/`tomli`, comparing against the git tag, never reading `__init__.py`).

**Required follow-up in the same task/commit:** run `uv lock` (or `uv sync`) to regenerate `uv.lock`'s embedded `typsphinx` self-version entry — RESEARCH.md Pitfall 2 confirms `ci.yml`'s `examples` job runs `uv sync --locked`, which fails on a stale lockfile.

---

### `CHANGELOG.md` (docs/config, CRUD — append new section)

**Analog:** the file's own existing `## [0.4.3] - 2025-11-01` entry (lines 8-14), which sits directly under the canonical `## [Unreleased]` header at line 8.

**Structural pattern to copy** (lines 8-14):
```markdown
## [Unreleased]

## [0.4.3] - 2025-11-01

### Changed

- **Project Status & Authorship**
  - Updated development status to "Production/Stable" in PyPI classifiers
```

**Insertion point:** Insert the new `## [0.5.0] - <date>` section directly between line 8 (`## [Unreleased]`) and line 10 (`## [0.4.3]`) — i.e. immediately after `## [Unreleased]`, becoming the new most-recent dated entry. **Do NOT** insert near the second, stray `## [Unreleased]`-adjacent block further down the file (RESEARCH.md Pitfall 3 — a duplicate/leftover heading exists near end-of-file under a `### Planned for Future Releases` list; ignore it).

**Content skeleton** (per CONTEXT.md D-06 + RESEARCH.md Code Examples section — themes only, exact prose is implementer's call, follow this file's existing `### Changed` / `### Fixed` / `### Added` subsection convention as seen in the `[0.4.3]` entry above):
```markdown
## [0.5.0] - 2026-07-11

### Changed

- Forward-ecosystem port: Sphinx re-pinned to `>=9.1,<10`, `typst` to `>=0.15.0,<0.16`,
  `docutils` to `>=0.21,<0.23`; Python floor raised to 3.12-3.13
- Bundled `@preview` packages bumped (mitex fixes `unknown variable: kai` under typst 0.15)

### Fixed

- Admonition rendering: fixed a markup/code-mode mismatch causing literal unevaluated
  Typst source instead of typeset prose

### Added

- CI: `typst compile` smoke test; drift.yml/Dependabot guardrails updated
```

Also update per RESEARCH.md Pitfall 3:
- Add link reference near the bottom's existing link list: `[0.5.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.5.0`
- Update the `[Unreleased]:` compare-link (currently `.../compare/v0.4.3...HEAD`) to `.../compare/v0.5.0...HEAD`

Do NOT backfill a `[0.4.4]` entry (RESEARCH.md Pitfall 4 — v0.4.4 was internal tooling only, no user-facing change, consistent with Keep a Changelog convention).

---

## Shared Patterns

### `importlib.metadata.version()` + specific-exception fallback
**Source:** `typsphinx/pdf.py:96-105`
**Apply to:** `typsphinx/__init__.py` only (this phase's sole runtime-code edit)
```python
try:
    from importlib.metadata import version
    return version("typst")
except Exception:
    pass
return "unknown"
```
Adapt: use `importlib.metadata.PackageNotFoundError` (the specific exception, not bare `Exception`) since `__init__.py`'s usage is an unconditional module-level assignment rather than a nested best-effort probe inside a larger function.

### `tomllib`-based independent `pyproject.toml` read
**Source:** `docs/source/conf.py:10-25`
**Apply to:** `tests/test_extension.py` (new drift-guard test)
```python
pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
with open(pyproject_path, "rb") as f:
    pyproject_data = tomllib.load(f)
    version = pyproject_data["project"]["version"]
```
Note path depth differs: `conf.py` is at `docs/source/conf.py` (3 levels below repo root, hence `.parent.parent.parent`), while `tests/test_extension.py` is 2 levels below repo root (hence `.parent.parent` in the test).

### Flat function-style pytest tests, local imports
**Source:** `tests/test_extension.py` (whole file — no classes, no shared fixtures beyond the externally-provided `temp_sphinx_app`)
**Apply to:** the new `test_version_matches_pyproject_toml` function — match existing style (imports inside function body, no class wrapper, one assertion-focused docstring).

## No Analog Found

None — all 5 touched files have a clear, concrete in-repo precedent (either from another file, or from the file's own existing structure).

## Metadata

**Analog search scope:** `typsphinx/` (pdf.py, __init__.py), `docs/source/conf.py`, `tests/test_extension.py`, `pyproject.toml`, `CHANGELOG.md`
**Files scanned:** 6 (5 targets + 1 analog-only reference, `typsphinx/pdf.py`)
**Pattern extraction date:** 2026-07-11
