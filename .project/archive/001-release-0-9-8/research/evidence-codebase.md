# Evidence — codebase

Repo root: /home/yuta/Documents/typsphinx
Scanned: 2026-11-03 (Audited HEAD fb3490356dd6b02e7153c421259170ceba8c9b5b, branch gsd-path/M001)
Checks run: all in the disposable sidecar at the recorded HEAD, after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` (succeeded; sidecar interpreter is uv-managed CPython 3.14.4, `typsphinx` imported from the sidecar path) —
`LC_ALL=C uv run pytest -q -p no:cacheprovider -o addopts="" tests/` → 1 failed, 1711 passed, 18 skipped in 125 s (only failure: `tests/test_graphviz_render_gate.py::test_no_graphviz_binary_is_installed`);
`uv run black --check .` → 381 files unchanged;
`uv run ruff check .` → All checks passed;
`uv run mypy typsphinx/` → no issues in 9 source files;
`git ls-remote --tags origin` → newest remote tag v0.9.7; `curl https://pypi.org/pypi/typsphinx/json` → PyPI version 0.9.7.
Skip reasons for the 18 skips were not captured (run was not repeated per the one-full-run constraint).

## Map

- **Stack**: Python >=3.12 (classifiers 3.12/3.13; CI matrix 3.12/3.13 on ubuntu, windows, macos), setuptools build backend, package version 0.9.8 (`pyproject.toml`). Runtime deps: `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16` (typst-py, bundled compiler). Dev extra: pytest, pytest-cov, tox+tox-uv, black 26, ruff 0.15–0.16, mypy, pypdf, pillow, sphinxcontrib-bibtex (dev-only by design). Docs extra: furo, sphinx-autodoc-typehints, sphinx-intl, myst-parser. Locked by `uv.lock`; NixOS dev shell via `flake.nix` (FHS shims, now also `pkgs.graphviz`). Typst Universe packages emitted into output: codly 1.3.0, codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1, diagraph 0.3.7.
- **Entry points**: `sphinx.builders` entry points `typst` and `typstpdf` → `typsphinx` (`pyproject.toml` `[project.entry-points."sphinx.builders"]`); `typsphinx/__init__.py:setup()` registers `TypstBuilder`, `TypstPDFBuilder`, 10 `typst_*` config values (including `typst_document_templates`), and the project's only event hook `config-inited → removed_config.check_config_at_init`. Helper scripts: `scripts/extract_changelog_section.py`, `scripts/render_admonition_greyscale.py`.
- **Architecture**: `builder.py` (2642 lines) validates config up front (output-path collisions, registry-key references, template paths), then per docname `_write_typst_files()` writes an unconditional CONTENT file `<docname>.typ` (via `TypstWriter.translate()` → `TypstTranslator` walk, with the five `@preview` imports prepended to every content file) plus one WRAPPER file per `typst_documents` entry naming that docname (`TypstWriter.render_wrapper()` → `TemplateEngine`, template chosen from the `typst_documents` 5th element through `template_registry.py`; wrapper `#include()`s the content file). `finish()` copies images and each used registry key's whole bundle directory to `<outdir>/_template/<key>/`. `TypstPDFBuilder.finish()` compiles only wrapper files via `pdf.py` (typst-py), collecting all failures into one `ExtensionError`. `translator.py` (8149 lines, 189 visit/depart methods) holds node conversion; `unknown_visit` logs a warning and continues.
- **Conventions**: docutils PascalCase visitor names (ruff N802 ignored); builtin generics, Python 3.12 target; black 88 cols; heavy requirement-ID comments in code (`Phase NN`, `D-NN`, `BLD-03`, `R010`, Japanese "Requirement 13.x" docstrings). Tests are mostly per-defect "render gate" modules (`tests/test_*_render_gate.py`, 187 test files, 166 fixture projects under `tests/fixtures/`, one `tests/roots/test-basic`) that build real fixtures and assert on emitted `.typ`/PDF; warnings escalated to errors (`filterwarnings = error::DeprecationWarning, error::PendingDeprecationWarning`). Commit subjects are conventional-commit style (`docs:` dominant in last 200 non-merge commits: 137 docs, 29 chore, 15 feat, 13 test, 6 fix); recent milestone commits carry a "GSD context:" body. Work lands via PRs into `main`.
- **Maturity**: Builds, lint, type-check pass; 1711/1730 tests pass (1 environmental failure, 18 skipped). Classified "Production/Stable"; released through v0.9.7 on PyPI. 4412 commits since 2025-10-13. CI: test matrix, lint, type, coverage, wheel-content check, `examples/basic` and `examples/advanced` builds; separate docs, drift (weekly), links, release (tag `v*`) workflows.
- **Recent activity**: since 2026-10-03 only Dependabot bumps plus the 2026-11-03 GSD Path adoption commit. Before that: M002 "Graphviz diagrams render on Read the Docs" (2026-10-03, PR #165), bibliography support via sphinxcontrib-bibtex (2026-10-02), `.planning/` tree archived out of the repo (2026-10-02, tag `planning-archive-2026-10-02`), v0.9.8 graphviz/diagraph work (2026-09-30). Hot files: `translator.py`, `builder.py`, `CHANGELOG.md`, `docs/source/user_guide/configuration.rst`.

## Finding: v0.9.8 is version-bumped and dated in CHANGELOG but was never released

- **Claim**: `pyproject.toml` declares version 0.9.8 and `CHANGELOG.md:53` has `## [0.9.8] - 2026-09-30`, but no `v0.9.8` tag exists locally or on origin and PyPI's current version is 0.9.7; `CHANGELOG.md:8` `[Unreleased]` already holds further work (bibliography support, R001–R013).
- **Source**: `git tag`, `git ls-remote --tags origin` (newest v0.9.7), `curl https://pypi.org/pypi/typsphinx/json` → 0.9.7; `CHANGELOG.md:8,53`.
- **Confidence**: high
- **Why it matters here**: a planner assuming 0.9.8 is shipped would bump to 0.9.9 and leave a dated-but-unpublished section; the release story (publish 0.9.8 as-is, or fold Unreleased into it) is an open decision.

## Finding: The graphviz "no dot binary" test fails on the maintainer's own dev shell by construction

- **Claim**: `tests/test_graphviz_render_gate.py:495-510` asserts `shutil.which("dot") is None`, while commit 7945ffbb (M002/S02) added `pkgs.graphviz` to the flake devShell unconditionally (`flake.nix:161-177`). Under that shell the test fails (`dot` at `/nix/store/...-graphviz-12.2.1/bin/dot`); it is the only failure in the full suite.
- **Source**: pytest run above; `git show --stat 7945ffbb`; `flake.nix:177`.
- **Confidence**: high (local failure); medium on whether CI runners have `dot` (CI `ci.yml` does not install graphviz; not checked against runner images).
- **Why it matters here**: local "all green" is unreachable on the NixOS machine; any task Verify running the full suite there will report a red that is not a regression. Two milestone decisions (R010 vs R021 local parity) contradict each other.

## Finding: CLAUDE.md's architecture description of master vs. included documents is stale

- **Claim**: CLAUDE.md says `TypstWriter.translate()` branches on master vs. included via `_is_master_document()`; that function does not exist (`grep -rn _is_master_document typsphinx` → 0 hits). The current design is two-layer: every docname gets a content file with imports and no template; each `typst_documents` entry gets a separate wrapper file (`writer.py:234-277`, `builder.py:2039-2140`). CLAUDE.md also says translator is "~2700 lines, ~140 visit/depart" (actual 8149 lines, 189), "four" `@preview` packages (actual five incl. diagraph, `writer.py:266-270`, `template_engine.py:705-709`, `templates/base.typ:8-23`; `tests/test_preview_version_sync.py:38-42` already checks five), and CI "py312–py313" (actual also windows/macos).
- **Source**: files/lines cited; `wc -l typsphinx/translator.py`.
- **Confidence**: high
- **Why it matters here**: CLAUDE.md is loaded into every agent; planners following it will look for wrong functions and under-count the version-sync surface (five packages, three files).

## Finding: `typst_debug` is registered but never read

- **Claim**: `typst_debug` is registered at `typsphinx/__init__.py:57` and nothing in `typsphinx/` reads it; its only test (`tests/test_config_other_options.py:141-159`) checks registration only. `removed_config.py`'s docstring cites a project rule against leaving inert configuration registered.
- **Source**: `grep -rn typst_debug` across the repo.
- **Confidence**: high
- **Why it matters here**: an inert, documented-in-examples config value (`examples/advanced/conf.py:103`) conflicts with a stated project rule; candidate for removal (via `removed_config.py`) or implementation.

## Finding: Code and test comments point at a `.planning/` tree that is no longer in the repository

- **Claim**: `.planning/` was moved out of the repo (commit 8443ef55, tag `planning-archive-2026-10-02`), but 34 files under `typsphinx/` and `tests/` still cite `.planning/phases/...` evidence paths (e.g. `tests/test_admonition_bucket_render_gate.py:6,62`), as do `tox.ini` comments (`65-REVERT-EVIDENCE.md`, `45.2-TOOLCHAIN-EVIDENCE.md`). Root-level milestone evidence files (`docs/S02-…`, `S03-…`, `S04-…-EVIDENCE.md`) sit in `docs/` outside `docs/source`.
- **Source**: `ls .planning` (absent); `grep -rln "\.planning/" typsphinx tests | wc -l` → 34.
- **Confidence**: high
- **Why it matters here**: rationale referenced by code is only reachable through the archive tag; the docs auditor and planners cannot resolve those references from the working tree.

## Finding: Tests escalate deprecation warnings to errors and the local venv runs Python 3.14

- **Claim**: `pyproject.toml` `filterwarnings` makes `DeprecationWarning`/`PendingDeprecationWarning` errors; a fresh worktree `uv sync` selects uv-managed CPython 3.14.4, which is outside the declared/CI-tested 3.12–3.13 range, yet the suite passed there (except the graphviz case).
- **Source**: `pyproject.toml` `[tool.pytest.ini_options]`; `uv run python -c "import sys; print(sys.version)"`.
- **Confidence**: high
- **Why it matters here**: sidecar evidence is gathered on an interpreter CI never uses; dependency bumps (weekly drift job, Dependabot) can turn upstream deprecations into test failures.

## Finding: Bibliography support is achieved with zero typsphinx code and a dev-only dependency

- **Claim**: sphinxcontrib-bibtex is only in the `dev` extra with a gate test (`tests/test_bibtex_dependency_gate.py`); CHANGELOG states `grep -rc bibtex typsphinx/` totals 0 — support relies on generic citation/reference visitors.
- **Source**: `pyproject.toml` dev extra comment (R012/MEM003); `CHANGELOG.md:12-25`.
- **Confidence**: high
- **Why it matters here**: a planner must not add a runtime dependency or a `[bibtex]` extra; changes to citation visitors in `translator.py` affect bibliography output.

## Apparent intent

- typsphinx is converging on a hardened, PyPI-distributed "LaTeX-builder replacement" for Sphinx with multi-template, multi-document output, gated per defect by render tests — based on 100+ `*_render_gate.py` files, template registry work (Phase 53/54), and Production/Stable classifier. (inference)
- Diagram and citation parity with HTML/LaTeX builders (graphviz via diagraph, bibtex) is the current feature frontier — based on M002 and the Unreleased section. (inference)
- The project is migrating its process tooling from GSD/gsd-pi (`.planning/`) to GSD Path (`.gsd-path/`, AGENTS.md, WORKFLOW.md, commit fb349035) and docs hosting to Read the Docs (`.readthedocs.yaml`, `tests/test_no_stale_github_io_links.py`). (inference)

## Open questions for define

- Should v0.9.8 be published as currently dated, or should the Unreleased bibliography work be folded into it (or into 0.9.9)?
- Which wins for the local suite: R010's "no `dot` on PATH" proof, or R021's devShell graphviz provisioning? (Should the test skip, move to CI-only, or should `dot` leave the default shell?)
- Should CLAUDE.md's architecture/size/package-count text be corrected as part of this milestone?
- Remove `typst_debug` (via the removed-config path) or give it behaviour?
- Should code comments citing `.planning/` paths be rewritten to point at the archive tag, or left as-is?
- What is this milestone's goal? Recent history shows no in-flight product work since 2026-10-03.

## Blocked areas

- Skip reasons of the 18 skipped tests — not captured; repeating the full suite with `-rs` was not permitted.
- `examples/*` builds, docs builds (`tox -e docs-html/docs-pdf`), PDF output quality, and the CI/RTD remote state — not run or checked in this inspection.
- Behaviour on Windows/macOS and on CPython 3.12/3.13 — only CPython 3.14.4 on Linux was exercised.
