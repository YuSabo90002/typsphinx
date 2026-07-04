# External Integrations

**Analysis Date:** 2026-07-04

## APIs & External Services

**Package Distribution:**
- PyPI - Official Python package repository
  - Distribution: `typsphinx` package
  - Published via: `pypa/gh-action-pypi-publish` GitHub Action in release workflow

**Typst Packages (imported in generated output):**
- `@preview/mitex:0.2.4` - LaTeX math support in Typst documents (optional, controlled by `typst_use_mitex` config)
- `@preview/codly:1.3.0` - Syntax highlighting for code blocks in Typst

## Data Storage

**Databases:**
- None - Stateless extension; no persistent data storage

**File Storage:**
- Local filesystem only
  - Input: Sphinx source files (reStructuredText/Markdown)
  - Output: Generated `.typ` files in `_build/typst/` or PDFs in `_build/pdf/` (paths configurable via `typst_output_dir`)
  - Template assets: `typsphinx/templates/` directory (packaged with distribution)

**Caching:**
- Sphinx's internal caching via `.doctrees/` (handled by Sphinx framework)
- No external cache service

## Authentication & Identity

**Auth Provider:**
- None - This is a library/extension, not an application
- GitHub Actions: Uses `secrets.CODECOV_TOKEN`, `secrets.PYPI_API_TOKEN`, `secrets.TEST_PYPI_API_TOKEN` for CI/CD operations

## Monitoring & Observability

**Error Tracking:**
- None at application level
- Custom exception: `TypstCompilationError` (`typsphinx/pdf.py`) for Typst compilation failures

**Logs:**
- Sphinx logging framework (`sphinx.util.logging`) via standard `logger.getLogger(__name__)` pattern
- No centralized logging service; logs output to stderr/console during build

## CI/CD & Deployment

**Hosting:**
- GitHub - Repository hosting and GitHub Pages for documentation
- PyPI - Package distribution

**CI Pipeline:**
- GitHub Actions (`.github/workflows/`)
  - `ci.yml`: Multi-matrix testing (Python 3.9-3.12, ubuntu/macos/windows), linting, type checking, coverage, build validation
  - `release.yml`: Release orchestration — validation, build, PyPI publish (production + TestPyPI for pre-releases), GitHub Release creation
  - `docs.yml`: Documentation build and deployment to GitHub Pages
  - Triggers: Pushes to `main` and `develop`, PRs, tags matching `v*`, workflow dispatch

**Coverage Service:**
- Codecov - Code coverage tracking
  - Integration: `codecov/codecov-action@v5` in CI workflow
  - Token: `secrets.CODECOV_TOKEN`
  - Upload: Coverage reports from pytest via `--cov-report=xml`

**Documentation Deployment:**
- GitHub Pages - Auto-deployed from `main` branch
  - Deployment action: `peaceiris/actions-gh-pages@v4`
  - Source: `docs/_build/multilang/` (multi-language HTML build)
  - URL: `https://yusabo90002.github.io/typsphinx/`

## Environment Configuration

**Required for Local Development:**
- No env vars required (Python stdlib + installed packages)
- Development environment: Nix flake or `uv sync`

**Required for CI/CD (GitHub Secrets):**
- `CODECOV_TOKEN` - Codecov coverage uploads (optional; `fail_ci_if_error: false`)
- `PYPI_API_TOKEN` - Production PyPI publishing (trusted publishing workflow)
- `TEST_PYPI_API_TOKEN` - TestPyPI pre-release publishing
- `GITHUB_TOKEN` - Automatic in GitHub Actions for release artifacts and pages deployment

**Secrets location:**
- GitHub repository secrets (`.github/` workflows read via `${{ secrets.VAR_NAME }}`)
- Local: `.env*` files (if used) are `.gitignore`d and not tracked

## Webhooks & Callbacks

**Incoming:**
- GitHub webhooks - Automatic triggers for:
  - Pull request events → runs CI
  - Push to `main` → builds and deploys documentation to GitHub Pages
  - Tag push `v*` → triggers release workflow

**Outgoing:**
- None at code level
- CI notifications: GitHub Actions status checks on PRs
- Documentation: Deployed to GitHub Pages (static push, no callback)

## Sphinx Configuration System

**Registered Config Values** (`typsphinx/__init__.py`):
- `typst_documents` - List of documents to build
- `typst_template` - Custom Typst template path
- `typst_template_mapping` - Document-to-template mapping
- `typst_toctree_defaults` - Table of contents defaults
- `typst_use_mitex` - Enable LaTeX math support (default: True)
- `typst_elements` - Custom element mappings
- `typst_package` - Custom Typst package name
- `typst_package_imports` - List of Typst package imports
- `typst_template_function` - Custom template rendering function
- `typst_authors` - Author metadata
- `typst_author_params` - Author parameter configuration
- `typst_output_dir` - Output directory path (default: `_build/typst`)
- `typst_debug` - Debug mode flag
- `typst_template_assets` - Additional template assets to include

**Configured in:**
- Sphinx `conf.py` (user's documentation project)

---

*Integration audit: 2026-07-04*
