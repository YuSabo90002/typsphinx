# External Integrations

**Analysis Date:** 2026-07-26

## APIs & External Services

**None called at runtime.** The `typsphinx` package itself does not call external APIs or web
services — all `typst`/`typstpdf` builder functionality is self-contained within the Python
package and the `typst-py` compiler.

Two external platforms sit outside the runtime package, on the *documentation build and hosting*
path only:
- **Read the Docs** hosts and builds this project's own documentation (see Hosting, below) — this
  is a hosting and build platform, not an API this project calls.
- **Typst Universe's package registry** (`packages.typst.org`) serves the four `@preview` packages
  (`codly`, `codly-languages`, `mitex`, `gentle-clues`) fetched at Typst compile time by any project
  using the bundled template — see Typst Universe Packages, below.

Neither is a service `typsphinx`'s own code calls; both are platforms this project's *documentation
build* depends on, and the distinction is deliberate — this project's `api-coverage` gate has a
documented false-positive class that fires on phrasing Read the Docs as an API integration
(`30.1-VERIFICATION.md § Acknowledged Gate Overrides`).

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
- **Read the Docs** is this project's documentation hosting and build platform (migrated from
  GitHub Pages, v0.6.4 milestone). Two linked RTD projects serve the documentation:
  - The parent project (`typsphinx`) serves the English documentation at
    `https://typsphinx.readthedocs.io/en/latest/`.
  - A linked Translations project (`typsphinx-ja`, repository
    `https://github.com/YuSabo90002/typsphinx-doc-translations`) serves the Japanese
    documentation at `https://typsphinx.readthedocs.io/ja/latest/`. That repository's submodule
    (pinning this repository's checked-out commit) and its scheduled pin-bump workflow live
    *there*, not in this repository — this project is consumed by that repository, not the other
    way around.
  - The bare root `https://typsphinx.readthedocs.io/` redirects to the project's Default Version
    (currently `latest`; the milestone plan flips it to `stable` once the `v0.6.4` tag has built
    green — RTD-04).
  - **`.readthedocs.yaml`** is the sole place Read the Docs' build behavior is configured — nothing
    in `conf.py` or this repository's local `tox` tasks reaches it. It pins `build.os:
    ubuntu-24.04` and Python 3.12 (matching `docs.yml`'s `actions/setup-python` pin, so the
    English/Japanese PDF baseline comparison runs on the same Python minor on both sides), installs
    `fonts-noto-cjk` via `apt_packages` (the English documentation contains CJK strings and Typst's
    font fallback is silent — a missing-glyph PDF would otherwise build green with no warning), and
    installs the project itself via `python.install` (`method: uv`, the `docs` extra), because
    RTD's zero-config Sphinx build does not install the project package on its own.
  - **PDF path:** Read the Docs' own LaTeX pipeline is deliberately replaced. `formats: [pdf]`
    alone would silently activate RTD's default LaTeX build and ship an undogfooded PDF; a
    `build.jobs.build.pdf` override runs `sphinx-build -b typstpdf` into a temporary directory and
    copies only the compiled `*.pdf` into `$READTHEDOCS_OUTPUT/pdf/`, so the PDF a reader downloads
    from Read the Docs is the one `typstpdf` itself produced.
- **GitHub** remains the source-code host
  (`https://github.com/YuSabo90002/typsphinx`) — hosting the documentation moved; hosting the code
  did not.

**CI Pipeline:**
- GitHub Actions (`.github/workflows/`), five workflow files:
  - `ci.yml` — Test matrix (py312/py313 × ubuntu/windows/macos), lint, type check, coverage,
    package build, and a basic/advanced example-build integration check.
  - `docs.yml` — Builds HTML (furo) and PDF (`typstpdf`) documentation via `uv run tox -e
    docs-html` / `uv run tox -e docs-pdf`, uploads both as artifacts, and attaches the PDF to
    tagged releases via `softprops/action-gh-release@v3`. Documentation publishing is Read the
    Docs' own git-integration build (see Hosting above); this workflow carries no publish path
    of its own.
  - `drift.yml` — Weekly dependency resolution check (`uv lock --upgrade`), exercises the
    freshly-resolved lock via `tox -e cov,docs-pdf`, files/comments a deduplicated GitHub issue on
    breakage.
  - `release.yml` — Validates the release tag against `pyproject.toml`'s version, builds sdist+wheel,
    publishes to PyPI (trusted publishing via OIDC) and TestPyPI (prerelease tags), and creates the
    GitHub Release.
  - `links.yml` — Repo-wide, real-HTTP link check (`lycheeverse/lychee-action@v2`). Triggers on
    push and pull_request. Advisory posture: never registered as a required status check, so a red
    or cancelled run never blocks a merge. Scope: the whole repository, closing the gap Sphinx's own
    `linkcheck` builder structurally cannot reach — `README.md` and `pyproject.toml` at the
    repository root, which `linkcheck` never walks because it only scans `docs/source/`.
- Codecov integration: Coverage uploaded in `ci.yml` via `codecov/codecov-action@v5` (requires `CODECOV_TOKEN` secret)
- Release management: Version tag triggers `release.yml`; publishes to PyPI and creates GitHub Release via `softprops/action-gh-release@v3`

**Secrets/Credentials:**
- `CODECOV_TOKEN` - Codecov API token (used in ci.yml)
- `PYPI_API_TOKEN` - PyPI trusted publishing (used in release.yml, alternative to deprecated password)
- `TEST_PYPI_API_TOKEN` - TestPyPI API token (optional, for pre-release testing)
- All stored in GitHub Actions secrets; never committed

## Environment Configuration

**Required env vars:**
- None for end users — typsphinx uses only Sphinx config values (conf.py)
- **Language resolution:** `docs/source/conf.py`'s `_resolve_language()` resolves the documentation
  build language with the precedence `READTHEDOCS_LANGUAGE` > `SPHINX_LANGUAGE` > `"en"`.
  `READTHEDOCS_LANGUAGE` is injected by Read the Docs from each project's own Language setting (this
  is the seam that makes the linked `typsphinx-ja` Translations project render Japanese while the
  parent renders English, from the same shared `conf.py`); `SPHINX_LANGUAGE` remains available as a
  local or CI override when not building under Read the Docs.
- **`$READTHEDOCS_OUTPUT`** — injected by the Read the Docs build environment (not user-configured).
  `.readthedocs.yaml`'s PDF job depends on it: it creates `$READTHEDOCS_OUTPUT/pdf/` explicitly
  (that subdirectory does not exist until RTD's own post-build ingestion runs, which is after this
  job) and copies only the compiled PDF into it.

**Secrets location:**
- GitHub Actions: `.github/workflows/*.yml` references `${{ secrets.* }}`
- Local development: `.env` files not used or committed

## Typst Universe Packages (External @preview Packages)

These four Typst packages are imported in the bundled template (`templates/base.typ`) and are
watched for version lockstep across four surfaces by `tests/test_preview_version_sync.py`:
`typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ` (the
extension-internal three), and every `.typ` file under `examples/` (added at the v0.6.3 close,
after a bundled sample shipped three milestones behind and could not compile — nothing had
previously watched bundled samples for version drift).

**A fifth pin site exists and is NOT covered by the guard:** `docs/source/_typst/custom_template.typ`
(this project's own documentation build, not the extension) pins the same four `@preview` packages
at the same versions but is outside `test_preview_version_sync.py`'s scan. This is a known,
carried Warning from Phase 30.1's review — it is documented here rather than repaired, because
repairing it would touch the version-sync surface that this milestone's invariant #2 freezes.

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

**Version Synchronization Points (guarded, 4 surfaces):**
- `typsphinx/templates/base.typ` - Lines 8, 9, 14, 19 (source of truth)
- `typsphinx/writer.py` - `_PREVIEW_VERSIONS` dict (consulted when writing per-document imports)
- `typsphinx/template_engine.py` - `_PREVIEW_VERSIONS` dict (consulted during template rendering)
- `examples/**/*.typ` - every bundled example template that pins one of the four packages
- `tests/test_preview_version_sync.py` - Asserts all four agree

**Unguarded fifth site:**
- `docs/source/_typst/custom_template.typ` - pins the same four packages at the same versions as
  `base.typ` today, but no test watches it; a future version bump to the guarded four could drift
  here silently.

**Synchronization Hazard (WR-07):**
If Typst Universe packages are upgraded (e.g., codly 1.2.0 → 1.3.0), the four guarded locations must
be updated together or the build fails, and the unguarded fifth site must be updated manually in the
same change (nothing will fail loudly if it is forgotten).

## Sphinx Intersphinx Mapping

Configured in `docs/source/conf.py` for documentation cross-references:

**External Doc Sites (read-only):**
- Python docs: `("python", ("https://docs.python.org/3", None))`
- Sphinx docs: `("sphinx", ("https://www.sphinx-doc.org/en/master", None))`

## GitHub Actions Dependencies

**Actions used in workflows:**
- `actions/checkout@v7` - Clone repository (every workflow)
- `actions/setup-python@v6` - Install a pinned Python version (docs.yml only; other workflows use `astral-sh/setup-uv@v7`'s `uv python install` instead)
- `astral-sh/setup-uv@v7` - Install uv package manager
- `actions/upload-artifact@v7` / `actions/download-artifact@v8` - CI artifact storage
- `codecov/codecov-action@v5` - Upload coverage reports
- `lycheeverse/lychee-action@v2` - Repo-wide link check (links.yml, CI-only per D-08; never run locally)
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

*Integration audit: 2026-07-26*
