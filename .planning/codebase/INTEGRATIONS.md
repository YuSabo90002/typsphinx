# External Integrations

**Analysis Date:** 2026-07-22

## APIs & External Services

**None directly used.** typsphinx does not call external APIs or web services. All functionality is self-contained within the Python package and Typst compiler.

## Data Storage

**Databases:**
- Not applicable — typsphinx is a build-time Sphinx extension, not a runtime service

**File Storage:**
- Local filesystem only
- Input: reStructuredText sources in `source/` directory (Sphinx project)
- Output: `.typ` (Typst markup) files in build directory, optionally compiled to `.pdf`
- Template assets: Loaded from `typsphinx/templates/` (bundled) or user-specified paths

**Caching:**
- Sphinx's built-in environment cache (`doctree.pickle`, `environment.pickle`) in `.doctrees/`
- Not user-configurable; managed by Sphinx

## Authentication & Identity

**Auth Provider:**
- None — typsphinx does not authenticate with external services

**Project Author/Copyright:**
- Configured via `typst_authors` config (dict, optional) or standard Sphinx metadata (project, author, release, copyright)
- Mapped to Typst template parameters; no authentication required

## Monitoring & Observability

**Error Tracking:**
- None configured — errors logged via Python's `logging` module

**Logs:**
- Destination: Console and Sphinx logger (`typsphinx` module loggers in each file)
- Level: Controlled by Sphinx's log level (default INFO)
- Custom errors: `TypstCompilationError` in `pdf.py` wraps typst-py failures with source location context

## CI/CD & Deployment

**Hosting:**
- GitHub (repository: `https://github.com/YuSabo90002/typsphinx`)

**CI Pipeline:**
- GitHub Actions (`.github/workflows/`):
  - `ci.yml` - Test matrix (py312/py313 × ubuntu/windows/macos), lint, type check, coverage, build
  - `release.yml` - Validate version, build sdist+wheel, publish to PyPI (trusted publishing via OIDC)
  - `docs.yml` - Build docs (HTML via furo, PDF via typstpdf builder) on push
  - `drift.yml` - Weekly dependency resolution check, files issues on breakage
- Codecov integration: Coverage uploaded in ci.yml via `codecov/codecov-action@v5` (requires `CODECOV_TOKEN` secret)
- Release management: Version tag triggers release.yml; publishes to PyPI and creates GitHub Release via softprops/action-gh-release@v3

**Secrets/Credentials:**
- `CODECOV_TOKEN` - Codecov API token (used in ci.yml)
- `PYPI_API_TOKEN` - PyPI trusted publishing (used in release.yml, alternative to deprecated password)
- `TEST_PYPI_API_TOKEN` - TestPyPI API token (optional, for pre-release testing)
- All stored in GitHub Actions secrets; never committed

## Environment Configuration

**Required env vars:**
- None for end users — typsphinx uses only Sphinx config values (conf.py)
- CI only: `SPHINX_LANGUAGE` (docs.yml, defaults to "en")

**Secrets location:**
- GitHub Actions: `.github/workflows/*.yml` references `${{ secrets.* }}`
- Local development: `.env` files not used or committed

## Typst Universe Packages (External @preview Packages)

These four Typst packages are imported in the bundled template (`templates/base.typ`) and must stay synchronized across three files (`writer.py`, `template_engine.py`, `base.typ`) per `tests/test_preview_version_sync.py`:

**Embedded in `templates/base.typ` (lines 8, 9, 14, 19):**
- `@preview/codly:1.3.0` - Syntax highlighting for code blocks
  - Imported as: `#import "@preview/codly:1.3.0": *`
  - Exported items used: codly-init (applied via `#show`), codly (configured with languages)
  - Purpose: Code block styling and highlighting
  - Requirement: Mandatory for all code blocks (Design 3.5)

- `@preview/codly-languages:0.1.10` - Language definitions for codly
  - Imported as: `#import "@preview/codly-languages:0.1.10": *`
  - Exported items used: codly-languages
  - Purpose: Provides syntax highlighting rules for programming languages
  - Requirement: Comprehensive language support (Design 3.5)

- `@preview/mitex:0.2.7` - LaTeX math support
  - Imported as: `#import "@preview/mitex:0.2.7": *`
  - Exported items used: Provides LaTeX-to-Typst math conversion
  - Purpose: Renders LaTeX math via `typst_use_mitex=True` config
  - Requirement: Math rendering (Design 3.3, Requirement 4.1)

- `@preview/gentle-clues:1.3.1` - Admonition styling (notes, warnings, etc.)
  - Imported as: `#import "@preview/gentle-clues:1.3.1": *`
  - Exported items used: Admonition callout styling
  - Purpose: Displays admonitions (note, warning, danger, etc.) with visual styling
  - Requirement: Admonition conversion (Requirement 2.8-2.10)

**Version Synchronization Points:**
- `typsphinx/templates/base.typ` - Lines 8, 9, 14, 19 (source of truth)
- `typsphinx/writer.py` - `_PREVIEW_VERSIONS` dict (consulted when writing per-document imports)
- `typsphinx/template_engine.py` - `_PREVIEW_VERSIONS` dict (consulted during template rendering)
- `tests/test_preview_version_sync.py` - Asserts all three agree

**Synchronization Hazard (WR-07):**
If Typst Universe packages are upgraded (e.g., codly 1.2.0 → 1.3.0), ALL THREE locations must be updated together or the build fails. No automatic version pinning; manual verification required.

## Sphinx Intersphinx Mapping

Configured in `docs/source/conf.py` for documentation cross-references:

**External Doc Sites (read-only):**
- Python docs: `("python", ("https://docs.python.org/3", None))`
- Sphinx docs: `("sphinx", ("https://www.sphinx-doc.org/en/master", None))`

## GitHub Actions Dependencies

**Actions used in workflows:**
- `actions/checkout@v6` - Clone repository
- `astral-sh/setup-uv@v7` - Install uv package manager
- `actions/upload-artifact@v7` / `actions/download-artifact@v8` - CI artifact storage
- `codecov/codecov-action@v5` - Upload coverage reports
- `pypa/gh-action-pypi-publish@release/v1` - Publish to PyPI
- `softprops/action-gh-release@v3` - Create GitHub Release

## Dependabot Configuration

**Automated dependency updates (.github/dependabot.yml):**
- Pip ecosystem: Weekly (Monday 00:00), grouped by category:
  - `sphinx-typst-stack` - Sphinx, docutils, typst (allows auto-update together)
  - Individual updates for other packages
  - Excludes: sphinx-autodoc-typehints, sphinx-intl (kept independent)
- GitHub Actions: Monthly updates, max 3 open PRs

---

*Integration audit: 2026-07-22*
