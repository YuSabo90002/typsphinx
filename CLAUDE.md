# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

typsphinx is a Sphinx extension that adds Typst output builders. It converts docutils/reStructuredText document trees into Typst markup (`typst` builder) and can compile that markup directly to PDF via the `typst-py` package (`typstpdf` builder) — no external Typst CLI required.

## Commands

Development uses `uv` for env/dependency management and `tox` (with `tox-uv`) as the task runner.

```bash
uv sync --extra dev          # install with dev dependencies

# Tests
pytest                       # run full suite (config in pyproject.toml)
pytest tests/test_translator.py                       # single file
pytest tests/test_translator.py::TestClass::test_name # single test
pytest -m "not slow"         # skip slow-marked tests
pytest --cov=typsphinx --cov-report=term-missing      # with coverage

# Lint / format / types (match CI exactly)
black --check .              # black --check . (CI); drop --check to format
ruff check .
mypy typsphinx/

# Everything, matrixed across py310–py313
tox                          # env_list: py310..py313, lint, type, cov, docs

# Build the project's own docs (from docs/)
tox -e docs-html             # HTML via furo
tox -e docs-pdf              # PDF via the typstpdf builder (dogfoods this extension)
```

To exercise the builders manually against a Sphinx project:

```bash
sphinx-build -b typst    source build/typst   # emit .typ files
sphinx-build -b typstpdf source build/pdf     # emit .typ + compiled .pdf
```

## Architecture

The pipeline follows Sphinx's standard builder → writer → translator layering. Data flows: **doctree → TypstTranslator (node-by-node) → body string → TemplateEngine (wrap in template) → .typ file → [PDF compile]**.

- **`__init__.py`** — `setup(app)` registers both builders and all `typst_*` config values. Builders are auto-discovered via `sphinx.builders` entry points (declared in `pyproject.toml`), so users don't strictly need to add `typsphinx` to `extensions`.

- **`builder.py`** — `TypstBuilder` (`name="typst"`) drives the write loop, image copying, and template-asset copying. It also writes a shared `_template.typ` file once per build (`_write_template_file`). `TypstPDFBuilder` (`name="typstpdf"`) subclasses it: `write_doc` still emits `.typ`, and `finish()` compiles master documents to PDF via `pdf.py`.

- **`writer.py`** — `TypstWriter.translate()` is the key control point. It runs the translator to get the body, then branches on **master vs. included** documents via `_is_master_document()`:
  - *Master* documents (those listed in the `typst_documents` config) get the full template applied through `TemplateEngine`.
  - *Included* documents (pulled in via toctree → Typst `#include()`) get only a minimal set of `@preview` imports prepended and **no template** — because Typst's `#include()` does not inherit imports from the parent file, each file must re-declare its own imports.

- **`translator.py`** — `TypstTranslator` (subclass of `SphinxTranslator`), ~2700 lines, ~140 `visit_*`/`depart_*` methods. This is where nearly all rST-node → Typst-syntax conversion lives; it is the file you will most often edit when adding or fixing node support. Note `N802` is ignored in ruff because docutils' visitor pattern requires PascalCase method names like `visit_Text`.

- **`template_engine.py`** — `TemplateEngine` loads a template (default `templates/base.typ` or a user template), maps Sphinx metadata (project/author/release/copyright + `typst_elements`) to template parameters, extracts toctree options, generates package imports, and renders the final document.

- **`pdf.py`** — thin wrapper over `typst-py`: `check_typst_available()`, `get_typst_version()`, and compilation raising `TypstCompilationError` with the underlying typst error attached.

### The `@preview` version-sync hazard

The four Typst Universe `@preview` package versions (`codly`, `codly-languages`, `mitex`, `gentle-clues`) are declared in **three** places that must stay in lockstep: `writer.py`, `template_engine.py`, and `templates/base.typ`. `tests/test_preview_version_sync.py` asserts all three agree — if you bump a version, update all three or CI fails.

## Configuration surface

User-facing config values (all registered in `__init__.py`, prefix `typst_`) include: `typst_documents` (defines master docs, format `[(source, target, title, author), ...]`), `typst_template` / `typst_template_mapping` / `typst_template_function`, `typst_package` / `typst_package_imports`, `typst_use_mitex` (LaTeX math via mitex vs. native Typst math), `typst_elements`, `typst_authors` / `typst_author_params`, `typst_template_assets`, `typst_output_dir`, and `typst_debug`.

## Tests

`sphinx.testing.fixtures` is loaded as a pytest plugin. `tests/roots/` holds Sphinx test projects (e.g. `test-basic`) used by integration tests via the `rootdir` fixture; `conftest.py` also provides `sample_doctree` and `temp_sphinx_app` fixtures. Test categories span unit (translator, template engine), integration (multi-doc, nested toctree, PDF generation), config coverage, math (mitex/native/fallback), and documentation-example verification.

## Conventions & gotchas

- **Python 3.10+ compatibility is required.** ruff intentionally ignores `UP006`/`UP035` (the `Dict`/`List` → `dict`/`list` upgrades) to keep 3.10 support — don't "modernize" typing imports.
- Line length 88 (black); `E501` is ignored in ruff since black owns wrapping.
- `tox.ini` pins `tox-uv~=1.35` (not `>=1.35,<2`) deliberately — see the comment in that file; tox's ini parser splits a single-line `requires` on commas and breaks otherwise.
- CI (`.github/workflows/ci.yml`) runs the py310–py313 + lint + type + cov matrix. A weekly `drift.yml` re-resolves latest allowed deps and files an issue on breakage. `release.yml` publishes to PyPI.

### Worktree-isolated execution

**Detection rule:** you are running inside an isolated git worktree when `.git` is a FILE (a `gitdir:` pointer), not a directory — check with `test -f .git`. Sequential main-tree execution has `.git` as a directory and needs none of the steps below.

When operating inside a worktree, provision the worktree's own environment before running anything:

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
uv run pytest   # run ALL subsequent commands via `uv run`
```

1. **Provision first.** `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` unsets those two vars so `uv` creates a fresh worktree-local `.venv` instead of syncing into an already-activated main venv and re-pointing it at the worktree.
2. **Run everything via `uv run`.** e.g. `uv run pytest …`. Inside the test fixtures, Sphinx is still invoked as `sys.executable -m sphinx`, which under `uv run` resolves to the worktree venv's python — so `import typsphinx` binds to the worktree's editable copy. This complements the existing NixOS `sys.executable -m sphinx` guidance and does not contradict it.

**Rationale:** the main `.venv` holds a PEP-660 editable finder (`__editable__.typsphinx-*.pth`) that resolves `import typsphinx` to the MAIN checkout's absolute path (`/…/typsphinx/typsphinx`), and `.venv` is gitignored so a fresh worktree starts with no venv of its own. Without the per-worktree `uv sync` + `uv run`, a worktree executor edits files in the worktree but pytest imports the UNCHANGED main-tree package — gates stay RED after a correct fix, and later waves don't see earlier waves' changes. Verified 2026-07-20 that a worktree `uv sync` + `uv run` is isolated (main `.venv` untouched) and works under the NixOS sandbox.

**Applicability — worktree isolation is the STANDING execution mode (project owner's decision, 2026-07-20).** `workflow.use_worktrees` is `true` and `.claude/settings.local.json` sets `worktree.baseRef: "head"`, so the #683 fork-base auto-degrade does **not** fire on feature/milestone branches (`worktree base-check` → `shouldDegrade: false, reason: "baseref-head"`) — executor agents run in isolated worktrees by default, including on unmerged milestone branches. Therefore the per-worktree provisioning above (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` + run everything via `uv run`) is **mandatory** for every executor, not conditional. Do **not** override execute-phase to sequential main-tree execution merely because a phase has low parallelism benefit (e.g. one plan per wave) — worktree isolation stays on. The only automatic fall-backs are the framework's own: a non-`claude` runtime (which cannot honor `isolation="worktree"`), a plan that touches a git-submodule path, or a genuine `worktree base-check` degrade signal.
