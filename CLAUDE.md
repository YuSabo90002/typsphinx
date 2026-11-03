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

# Everything, matrixed across py312–py313
tox                          # env_list: py312, py313, lint, type, cov, docs

# Build the project's own docs (from docs/)
tox -e docs-html             # HTML via furo
tox -e docs-pdf              # PDF via the typstpdf builder (dogfoods this extension)
tox -e linkcheck             # Check external links and anchors (needs network; not run by plain tox)
```

To exercise the builders manually against a Sphinx project:

```bash
sphinx-build -b typst    source build/typst   # emit .typ files
sphinx-build -b typstpdf source build/pdf     # emit .typ + compiled .pdf
```

## Architecture

The pipeline follows Sphinx's standard builder → writer → translator layering. Data flows: **doctree → TypstTranslator (node-by-node) → body string → TemplateEngine (wrap in template) → .typ file → [PDF compile]**.

- **`__init__.py`** — `setup(app)` registers both builders and all `typst_*` config values. Builders are auto-discovered via `sphinx.builders` entry points (declared in `pyproject.toml`), so users don't strictly need to add `typsphinx` to `extensions`.

- **`builder.py`** — `TypstBuilder` (`name="typst"`) drives the write loop and image copying, accumulating the `typst_document_templates` registry keys actually used as it writes each document. In `finish()` it copies each used key's whole template bundle directory wholesale to its own `<outdir>/_template/<key>/` directory (`_copy_used_template_bundles()`) — the one route from a template directory to the output tree. Before that, `finish()` writes `<outdir>/_typsphinx/deps.typ` (`_write_dependencies_file()`: the generated default from `typst_deps.py`, or the `typst_dependencies` file copied byte-identical), and after the copy it warns on template dependency drift (`_warn_template_dependency_drift()`). `TypstPDFBuilder` (`name="typstpdf"`) subclasses it: `write_doc` still emits `.typ`, and `finish()` compiles master documents to PDF via `pdf.py`.

- **`writer.py`** — `TypstWriter` splits output into two kinds of file:
  - *Content files* — `TypstWriter.translate()` runs the translator and writes every docname's content `.typ` unconditionally, with the two-line preamble `#import "/_typsphinx/deps.typ": *` + `#show: typsphinx-init` (`typst_deps.deps_preamble_lines()`) prepended and **no template** — because Typst's `#include()` does not inherit imports or top-level show rules from the parent file, each file must re-declare them.
  - *Wrapper files* — `TypstWriter.render_wrapper()`, called by the builder once per `typst_documents` entry, applies the full template through `TemplateEngine` and `#include()`s that entry's content file. Template application lives only here.

- **`translator.py`** — `TypstTranslator` (subclass of `SphinxTranslator`), the largest module, holding the `visit_*`/`depart_*` methods. This is where nearly all rST-node → Typst-syntax conversion lives; it is the file you will most often edit when adding or fixing node support. Note `N802` is ignored in ruff because docutils' visitor pattern requires PascalCase method names like `visit_Text`.

- **`template_engine.py`** — `TemplateEngine` loads a template (default `templates/base.typ` or a user template), maps Sphinx metadata (project/author/release/copyright + `typst_elements`) to template parameters, extracts toctree options, generates the optional `typst_package` import, emits the same `deps.typ` preamble on every route, and renders the final document. It hard-codes no `@preview` package version.

- **`typst_deps.py`** — leaf module and the single source of the five `@preview` package specs (`DEFAULT_PACKAGES`), the default `deps.typ` text (`render_default_deps()`), the preamble (`deps_preamble_lines()`), and the comment-stripping pin scanner the drift warning uses.

- **`pdf.py`** — thin wrapper over `typst-py`: `check_typst_available()`, `get_typst_version()`, and compilation raising `TypstCompilationError` with the underlying typst error attached.

### The `@preview` version-sync hazard

The five Typst Universe `@preview` package versions (`codly`, `codly-languages`, `mitex`, `gentle-clues`, `diagraph`) have a single source: `DEFAULT_PACKAGES` in `typsphinx/typst_deps.py`. Every build generates `<outdir>/_typsphinx/deps.typ` from it (imports plus the `typsphinx-init` show function that sets up codly), and every content file, wrapper and the bundled `templates/base.typ` import that file by the root-absolute path `/_typsphinx/deps.typ` (compile root = outdir) instead of pinning versions. To bump a version, edit `typst_deps.py` only. The hazard that remains is reintroducing a pin elsewhere, and these gates cover it: `tests/test_preview_version_sync.py` asserts no five-package spec literal appears under `typsphinx/` outside `typst_deps.py`, that the generated `deps.typ` equals the module's definitions, and that the repository's own templates (`docs/source/_typst/`, `examples/`, the template test fixtures) pin none of the five; for user templates, the build-time drift warning (`template dependency drift: ...`) flags a bundle `.typ` file pinning a version different from the effective `deps.typ`. `/_typsphinx/deps.typ`, its exported names and `typsphinx-init` are a public contract documented in `docs/source/user_guide/templates.rst` — renaming an export is a breaking change.

## Configuration surface

User-facing config values (all registered in `__init__.py`, prefix `typst_`) include: `typst_documents` (defines master docs, format `[(source, target, title, author[, documentclass]), ...]`, where the optional fifth element `documentclass` is a template registry key into `typst_document_templates`), `typst_template` / `typst_template_mapping` / `typst_template_function`, `typst_package` / `typst_package_imports`, `typst_dependencies` (path to one file, srcdir-relative or absolute, copied byte-identical to `<outdir>/_typsphinx/deps.typ` in place of the generated default; `None` = default), `typst_use_mitex` (LaTeX math via mitex vs. native Typst math), and `typst_elements`. Rich author structure (department/organization/location/email) is expressed via `typst_template_function`'s `params` route, not a dedicated config value — the dedicated author-details value that once existed here was removed in Phase 45.1 (CONF-10). The asset-list config value that once selected which template-directory files reached the output was removed in Phase 54 (CONF-19) — every used template's whole bundle directory is now copied wholesale to `<outdir>/_template/<key>/` automatically.

## Tests

`sphinx.testing.fixtures` is loaded as a pytest plugin. `tests/roots/` holds Sphinx test projects (e.g. `test-basic`) used by integration tests via the `rootdir` fixture; `conftest.py` also provides `sample_doctree` and `temp_sphinx_app` fixtures. Test categories span unit (translator, template engine), integration (multi-doc, nested toctree, PDF generation), config coverage, math (mitex/native/fallback), and documentation-example verification.

## Conventions & gotchas

- **Python 3.12+ is required.** Annotations use builtin generics (`dict[str, Any]`, `list[str]`, `set[str]`, `tuple[str, ...]`) and take abstract types such as `Iterator` from `collections.abc`, not `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`.
- Line length 88 (black); `E501` is ignored in ruff since black owns wrapping.
- `tox.ini` pins `tox-uv~=1.35` (not `>=1.35,<2`) — see the comment in that file; tox's ini parser splits a single-line `requires` on commas, so `>=1.35,<2` breaks tox's startup and `~=1.35` is the comma-free equivalent. The pin was earlier `tox-uv-bare` (QUA-04, Phase 45.2) only because the `uv` bundled with `tox-uv` could not exec on NixOS; the NixOS FHS shims now handle that, which is why plain `tox-uv` is correct again.
- **Toolchain-pin sync hazard, same shape as the `@preview` one above.** The `tox-uv` (vs. `tox-uv-bare`) rationale is restated in multiple places that must move together whenever this pin is ever revisited: `pyproject.toml`'s `dev` extra (the actual pin), `tox.ini`'s `requires` line and its comment, `flake.nix`'s header/`uvShim` comments, this file's two mentions, and `tests/test_toolchain_config_gate.py`'s `test_dev_extra_pins_tox_uv_not_tox_uv_bare` docstring (the gate that enforces the pin). Update all of them in the same commit — this drifted out of sync once already (Phase 65 → Phase 68).
- CI (`.github/workflows/ci.yml`) runs the py312–py313 + lint + type + cov matrix. A weekly `drift.yml` re-resolves latest allowed deps and files an issue on breakage. `release.yml` publishes to PyPI.

### NixOS development shell

**Scope.** This subsection applies only on the maintainer's NixOS machine, where `direnv` loads `flake.nix`'s devShell in the main checkout. CI and non-NixOS contributors have no shims and need none — nothing here changes how CI or a non-NixOS contributor runs any of these commands.

**What the shims are.** On that machine, PATH carries seven bare commands: `uv`, `tox`, `ruff`, `black`, `mypy`, `pytest` and `sphinx-build` — the same commands named in § Commands above. Each walks up from the current directory to this checkout's own `.venv/bin/<tool>` and runs it inside an FHS sandbox (`typsphinx-fhs-run`), which is what lets generic-linux binaries that `uv` installs or downloads execute, together with everything they spawn. A missing `.venv/bin/<tool>` fails loudly: a `typsphinx-shim:` line on stderr names the tool and prints the provisioning line as a hint, then the shim exits 127 — it never silently runs some other binary. `uv` alone also falls back to nixpkgs' own `uv`, so a fresh clone or worktree with no `.venv` yet can run its first `uv sync`. Once `.venv` exists, `uv --version` reports the version `uv.lock` pins.

**Prerequisite and check.** Launch Claude Code from a shell in which `direnv` has already loaded the main checkout's devShell. Before provisioning a worktree, confirm the shim is on PATH by running exactly: `grep -q typsphinx-fhs-run "$(command -v uv)"`.

**No manual step.** No manual `ln -sf` or `patchelf` step exists or is needed — those two words appear in this sentence and nowhere else in this file. A `Could not start dynamically linked executable` error means the shim is not on PATH (the session was not launched from the direnv-loaded checkout); relaunch from that shell — it is not a code regression.

**Locale.** The sandbox passes the host's `LANG` through unchanged, so Sphinx warning text stays localised inside it exactly as outside. CI runs in English, so a test asserting warning text should also be run under `LC_ALL=C` locally.

**Interpreters may differ.** A fresh worktree's `.venv` is built on uv-managed CPython, while the main checkout's may be on nixpkgs' `python3` — the two may differ. Compare both `.venv/pyvenv.cfg` `home` and `version_info` before comparing test counts between them.

**Rationale pointer.** Why the development shell is built this way is recorded in `flake.nix`'s own header notes — see that file, not this one.

### Worktree-isolated execution

**Detection rule:** you are running inside an isolated git worktree when `.git` is a FILE (a `gitdir:` pointer), not a directory — check with `test -f .git`. Sequential main-tree execution has `.git` as a directory and needs none of the steps below.

**NixOS boundary.** The recipe below is unchanged and mandatory on every machine; `flake.nix` does not substitute for it. On the maintainer's NixOS machine the recipe itself runs through the shims described in the section above, because a worktree's `.venv` is built on a generic-linux interpreter that NixOS runs only inside the sandbox — so the worktree depends on those shims being present. The shims reach a worktree only because they are inherited through PATH from a session launched in the direnv-loaded main checkout: `direnv` never loads inside a worktree itself, and a worktree's own `.envrc` is never allowed there.

When operating inside a worktree, provision the worktree's own environment before running anything:

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
uv run pytest   # run ALL subsequent commands via `uv run`
```

1. **Provision first.** `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` unsets those two vars so `uv` creates a fresh worktree-local `.venv` instead of syncing into an already-activated main venv and re-pointing it at the worktree.
2. **Run everything via `uv run`.** e.g. `uv run pytest …`. Inside the test fixtures, Sphinx is still invoked as `sys.executable -m sphinx`, which under `uv run` resolves to the worktree venv's python — so `import typsphinx` binds to the worktree's editable copy. This complements the existing NixOS `sys.executable -m sphinx` guidance and does not contradict it.

**Rationale:** the main `.venv` holds a PEP-660 editable finder (`__editable__.typsphinx-*.pth`) that resolves `import typsphinx` to the MAIN checkout's absolute path (`/…/typsphinx/typsphinx`), and `.venv` is gitignored so a fresh worktree starts with no venv of its own. Without the per-worktree `uv sync` + `uv run`, a worktree executor edits files in the worktree but pytest imports the UNCHANGED main-tree package — gates stay RED after a correct fix, and later waves don't see earlier waves' changes. Verified 2026-07-20 that a worktree `uv sync` + `uv run` is isolated (main `.venv` untouched) and works under the NixOS sandbox.
