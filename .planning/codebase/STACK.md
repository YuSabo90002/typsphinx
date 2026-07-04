# Technology Stack

**Analysis Date:** 2026-07-04

## Languages

**Primary:**
- Python 3.9+ - Core implementation language for the Sphinx extension

**Secondary:**
- Typst - Output format for documentation (generated, not written)
- reStructuredText - Input format for documentation
- YAML - Configuration for GitHub Actions and Dependabot

## Runtime

**Environment:**
- Python 3.9, 3.10, 3.11, 3.12 (supported versions per `pyproject.toml`)

**Package Manager:**
- uv - Fast Python package and virtual environment manager
- Lockfile: `uv.lock` (present)

## Frameworks

**Core:**
- Sphinx 5.0+ - Documentation generation framework
- docutils 0.18+ - Markup language processing system

**Testing:**
- pytest 7.0+ - Test runner
- pytest-cov 4.0+ - Code coverage plugin
- sphinx-testing 1.0+ - Sphinx extension testing utilities

**Build/Dev:**
- black 23.0+ - Code formatter
- ruff 0.1.0+ - Fast Python linter
- mypy 1.0+ - Static type checker
- tox 4.0+ - Test automation tool
- tox-uv 1.0+ - Uv integration for tox
- twine 5.0+ - Package upload utility
- build 1.0+ - Python package builder
- pre-commit 3.0+ - Git hook framework

## Key Dependencies

**Critical:**
- typst 0.14.1+ - Typst compiler as Python package; core to PDF generation via `typsphinx.pdf.compile_typst_to_pdf()`
- docutils 0.18+ - Core dependency for AST processing of reStructuredText

**Infrastructure:**
- setuptools 65.0+ - Package build backend
- wheel - Wheel format distribution

**Documentation:**
- furo 2024.0+ - Clean, modern Sphinx theme (`docs` extra)
- sphinx-autodoc-typehints 1.0+ - Type hint support in documentation
- sphinx-intl 2.0+ - Internationalization support for multi-language docs

**Type Hints:**
- types-docutils 0.18+ - Type stubs for docutils

## Configuration

**Environment:**
- No `.env` files required; all configuration via Python code in Sphinx `conf.py`
- Build configuration: `pyproject.toml` (project metadata, build system, tool settings)

**Build:**
- `pyproject.toml`: Main project configuration, entry points, test setup
  - Entry points: `[project.entry-points."sphinx.builders"]` registers `typst` and `typstpdf` builders
- `tox.ini`: Test environment definitions for tox-based testing
- `flake.nix`: Nix development shell for reproducible development environment
- `uv.lock`: Dependency lock file for deterministic builds

**Formatting & Linting:**
- `.black` in `pyproject.toml`: Line length 88, targets Python 3.9+
- `.ruff` in `pyproject.toml`: Linter with E, F, W, I, N, UP, B, A, C4, T20 rules; line length 88
- `.mypy` in `pyproject.toml`: Type checking (warn_return_any=false, check_untyped_defs=false)

## Platform Requirements

**Development:**
- Linux, macOS, Windows (CI tests on ubuntu-latest, macos-latest, windows-latest)
- Nix development shell with:
  - Python 3
  - Node.js (for CLI/tooling)
  - pnpm (package manager)
  - uv (Python dependency manager)
  - Git

**Production:**
- Any Python 3.9+ environment with pip/uv
- Distribution: PyPI package registry
- No system-level Typst compiler required (bundled via typst-py package)

## Package Discovery & Entry Points

**Sphinx Builder Registration:**
- Location: `pyproject.toml` `[project.entry-points."sphinx.builders"]`
- `typst = "typsphinx"` - Typst builder (generates `.typ` files)
- `typstpdf = "typsphinx"` - PDF builder (generates PDFs directly)
- Auto-discovered by Sphinx via entry points (no manual extension registration required)

**Template Assets:**
- Location: `typsphinx/templates/*.typ` (packaged via `[tool.setuptools.package-data]`)

---

*Stack analysis: 2026-07-04*
