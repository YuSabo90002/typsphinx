# Evidence — codebase

<!-- Written by the codebase mapper during /gsd-path-inspect. Read by define
     (brownfield mode), researchers (fifth standard dimension), the planner
     (conventions are binding), and reviewers. -->

Repo root: /home/yuta/Documents/typsphinx
Scanned: 2026-11-03 (Audited HEAD 46a72b5f80b9510f67f43031288fcba52478f701, verify sidecar)
Checks run: all in the verify sidecar at 46a72b5f, after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` (venv: uv-managed CPython 3.14, per `.venv/pyvenv.cfg` `version_info = 3.14`) → `LC_ALL=C uv run pytest tests/ -q -p no:cacheprovider -o addopts=""` → 1812 passed, 18 skipped, 0 failed in 131 s; `uv run black --check .` → 394 files unchanged; `uv run ruff check .` → All checks passed; `uv run mypy typsphinx/` → no issues in 10 source files; `pytest ... -rs` → the 18 skips are 17 docs-extra-absent (myst-parser/furo/sphinx-autodoc-typehints) in test_bibliography_docs_gate.py, test_changelog_page_gate.py, test_graphviz_docs_gate.py, plus 1 env-gated (TYPSPHINX_CORPUS_REPORT) in test_corpus_gate.py. tox, docs builds and examples builds were not run.

## Map

- **Stack**: Python >=3.12 package `typsphinx` 0.9.8 (setuptools build backend); runtime deps `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16` (typst-py), locked at sphinx 9.1.1, docutils 0.22.4, typst 0.15.0 (`pyproject.toml:27-31`, `uv.lock`). Dev extra: pytest, pytest-cov, tox + tox-uv, black 26, ruff 0.15-0.17, mypy, pypdf, pillow, sphinxcontrib-bibtex; docs extra: furo, sphinx-autodoc-typehints, sphinx-intl, myst-parser. Typst `@preview` packages codly 1.3.0, codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1, diagraph 0.3.7 (`typsphinx/typst_deps.py:65-71`). Nix flake devShell with FHS shims for the maintainer's NixOS host.
- **Entry points**: `sphinx.builders` entry points `typst` and `typstpdf` → `typsphinx` (`pyproject.toml` `[project.entry-points."sphinx.builders"]`); `typsphinx.setup()` registers both builders, 10 `typst_*` config values and one `config-inited` handler (`typsphinx/__init__.py:41-79`). Scripts: `scripts/extract_changelog_section.py` (release notes), `scripts/render_admonition_greyscale.py`.
- **Architecture**: Sphinx builder → writer → translator. `TypstBuilder` (`builder.py:691`, 2858-line module) validates config/paths/collisions before writing, writes one content `.typ` per docname plus one wrapper `.typ` per `typst_documents` entry via `TypstWriter` (`writer.py`), and in `finish()` writes `_typsphinx/deps.typ`, copies images, copies used template bundles to `_template/<key>/`, then warns on template dependency drift (`builder.py:2532-2551`). `TypstTranslator` (`translator.py`, 8149 lines, 98 `visit_*` / 91 `depart_*`) does node-to-Typst conversion. `TemplateEngine` (`template_engine.py`) wraps; `template_registry.py` resolves `typst_document_templates`; `typst_deps.py` is the single source of package specs; `pathfmt.py` is a leaf path-quoting helper; `removed_config.py` warns on removed config names. `TypstPDFBuilder.finish()` compiles only wrapper files of masters via typst-py and aggregates failures into one ExtensionError (`builder.py:2721+`).
- **Conventions**: builtin generics, black/ruff line 88, ruff rule set E/F/W/I/N/UP/B/A/C4/T20 with N802 ignored for visitor names (`pyproject.toml` `[tool.ruff.lint]`); pytest with `error::DeprecationWarning` and `error::PendingDeprecationWarning` filters (any new deprecation warning fails tests); tests are mostly per-defect "render gate" files (`tests/test_*_render_gate.py`, `*_gate.py`) that build a real Sphinx project and often compile with typst-py, skipped via `TYPST_AVAILABLE`/`PYPDF_AVAILABLE`/`BIBTEX_AVAILABLE` flags; long rationale comments citing phase/requirement IDs (e.g. `Phase 54 (CONF-19)`, `D-03`) in code; config errors raised from builder methods, removed config detected at `config-inited`. Commit style: conventional (`feat:`, `fix:`, `docs:`, `chore(deps):`) historically; under GSD Path, `T00N: <summary>`, `build: ...`, `plan: ...`, `ship: M00N — <slug>`, integration by PR merge.
- **Maturity**: full suite green locally (1812 passed); 192 test files, one Sphinx test root (`tests/roots/test-basic`) plus `tests/fixtures/`; CI (`.github/workflows/ci.yml`) runs tox py312/py313 on ubuntu, windows and macos, plus lint, type, coverage (Codecov) and a wheel build with a wheel-content check; `docs.yml`, `links.yml`, weekly `drift.yml`, tag-triggered `release.yml` (`v*`). PyPI classifier "Production/Stable". No TODO/FIXME left in `typsphinx/` except one historical reference (`translator.py:6347`).
- **Recent activity**: last ~32 commits since tag `v0.9.8` (37d2fdb3) are three GSD Path milestones on 2026-11-03: M001 release-0-9-8 (graphviz PATH proof, `typst_debug` removal, CLAUDE.md fixes, CHANGELOG fold), M002 externalize-typst-deps (`typst_deps.py`, `_typsphinx/deps.typ`, `typst_dependencies`, drift warning; 6 product files, +468/-74 in `typsphinx/`), M003 windows-test-portability (8 tests made OS-independent, README tree). Interleaved Dependabot bumps (tox-uv, ruff, black, mypy, sphinx, pypdf). Before that (Sept–Oct 2026): graphviz/diagraph, bibliography (sphinxcontrib-bibtex), RTD graphviz provisioning.

## Finding: The M002 deps.typ change is unreleased

- **Claim**: `pyproject.toml` version is still 0.9.8 and tag `v0.9.8` points at 37d2fdb3, while CHANGELOG `## [Unreleased]` holds the M002 Added/Changed entries (shared `_typsphinx/deps.typ`, `typst_dependencies`, drift warning, single version source); every content/wrapper file now starts with a new import preamble, which changes generated output for all users.
- **Source**: `pyproject.toml:7`; `git tag`; `git rev-list --count v0.9.8..HEAD` → 32; `CHANGELOG.md:8-40`; `README.md:345` ("Stable (v0.9.8)")
- **Confidence**: high
- **Why it matters here**: the next release must carry an output-format change and a new public contract (`/_typsphinx/deps.typ`); version choice (0.9.9 vs 0.10.0) and release prep are open, and README/pyproject/CHANGELOG link block move together (prior milestone M001 shows the pattern).

## Finding: Local venv runs Python 3.14, outside the declared/CI-tested range

- **Claim**: a fresh `uv sync` in the sidecar built the venv on uv-managed CPython 3.14 and the full suite passed there, but classifiers list only 3.12/3.13 and CI tests only 3.12/3.13.
- **Source**: `.venv/pyvenv.cfg` (`version_info = 3.14`); `pyproject.toml` classifiers; `.github/workflows/ci.yml` matrix `python-version: ['3.12', '3.13']`; tox `env_list = py312, py313, ...`
- **Confidence**: high
- **Why it matters here**: local evidence from a worktree is on a different interpreter than CI; any milestone touching interpreter-sensitive behaviour should not treat local 3.14 runs as CI-equivalent. 3.14 support is de facto working but not declared.

## Finding: CI matrix is three operating systems, not just a Python matrix

- **Claim**: the CI `test` job runs on ubuntu-latest, windows-latest and macos-latest for each of py312/py313 (6 jobs), so Windows-only defects (path separators, ANSI colour) surface only in CI; M003 existed to fix 8 such failures.
- **Source**: `.github/workflows/ci.yml:13-23`; CLAUDE.md line 82 describes only "py312–py313 + lint + type + cov matrix"
- **Confidence**: high
- **Why it matters here**: a planner reading CLAUDE.md alone would not budget for Windows/macOS behaviour; tests asserting paths or console text must be OS-neutral.

## Finding: Builder always rebuilds every document

- **Claim**: `TypstBuilder.get_outdated_docs()` yields every `env.found_docs` entry unconditionally ("For now, we rebuild all documents on every build"); no incremental write exists.
- **Source**: `typsphinx/builder.py:1640-1650`
- **Confidence**: high
- **Why it matters here**: build-time features and tests can assume full rewrites; incremental-build support would be new work, not a fix.

## Finding: Several product modules are absent from CLAUDE.md's architecture list

- **Claim**: `typsphinx/` contains `template_registry.py` (550 lines), `removed_config.py` (100), and `pathfmt.py` (97) in addition to the modules CLAUDE.md describes; `removed_config.py` owns the only event handler (`config-inited`) and lists four removed names (`typst_template_assets`, `typst_authors`, `typst_toctree_defaults`, `typst_debug`).
- **Source**: `wc -l typsphinx/*.py`; `typsphinx/__init__.py:61-75`; `typsphinx/removed_config.py:40-62`
- **Confidence**: high
- **Why it matters here**: removing or renaming a config value has an established route (add to `REMOVED_CONFIG_VALUES`, warn once); registry-key validation deliberately does not reuse builder path predicates (`template_registry.py:9-22`).

## Finding: Test suite is a large set of regression gates, many of which require typst-py and real builds

- **Claim**: 192 test files, most named `*_gate.py`, each pinning one previously fixed defect or contract; ~170 `skipif` uses gate on optional modules (typst-py, pypdf, sphinxcontrib-bibtex, myst-parser). With `--extra dev` only, 17 docs-build gates skip because the docs extra is not installed, so a dev-only lane does not exercise the real docs build.
- **Source**: `ls tests`; `grep -rn skipif tests`; `pytest -rs` output above
- **Confidence**: high
- **Why it matters here**: the project Verify for a docs-touching milestone needs `--extra dev --extra docs` (or tox docs envs), otherwise those gates pass by skipping. Full suite takes ~2 min.

## Finding: Repository-root evidence files and tests that read them

- **Claim**: `docs/S02-LOCAL-PARITY-EVIDENCE.md`, `docs/S03-ARTIFACT-GATE-EVIDENCE.md`, `docs/S04-PUBLISHED-SITE-EVIDENCE.md` sit outside `docs/source/` (not built) and are read by `tests/test_release_0_9_8_docs_gate.py:34-35`.
- **Source**: `ls docs`; `tests/test_release_0_9_8_docs_gate.py:34-35`
- **Confidence**: high
- **Why it matters here**: these look like stale process artifacts but deleting them breaks a test; any cleanup must move the gate with them.

## Finding: The `@preview` single source is guarded by tests and a build-time warning

- **Claim**: the five package specs exist as literals only in `typsphinx/typst_deps.py`; `tests/test_preview_version_sync.py` enforces it, and `builder._warn_template_dependency_drift` warns on user bundle pins that disagree.
- **Source**: `typsphinx/typst_deps.py:65-71`; `typsphinx/builder.py:2553`; `tests/test_preview_version_sync.py`
- **Confidence**: high
- **Why it matters here**: a version bump is a one-file edit plus render-gate reruns; reintroducing a literal elsewhere fails the suite.

## Apparent intent

- The project is in a maintenance/hardening phase of a stable extension, heading toward the next release that ships the deps.typ externalisation — based on Unreleased CHANGELOG content, three same-day milestones of fixes/refactors, and no new node-support work since v0.9.8.
- It is consolidating its process under GSD Path (milestone branches `gsd-path/M00N`, PR integration, `.project/` archives) after earlier GSD tooling — based on commit history and `.project/STATE.md` (`integration_default: pull-request`).
- Cross-platform correctness is an active concern — based on the 3-OS CI matrix and M003.

## Open questions for define

- Is the next milestone the release of the Unreleased deps.typ change, and at which version (0.9.9 or 0.10.0, given the changed output preamble and new public contract)?
- Should Python 3.14 be declared and added to CI/tox, given the suite already passes on 3.14 locally?
- Should `docs/S0[234]-*.md` evidence files and their test gate be kept, moved, or retired?
- Is incremental building (`get_outdated_docs`) in or out of scope going forward?

## Blocked areas

- tox environments, `tox -e docs-html/docs-pdf`, and the examples' `typstpdf` builds — not run (time; docs extra not installed in the sidecar); their gates were skipped or covered only by tests that build fixtures.
- CI results on windows/macos — not observable from the sidecar; M003 archive manifest records the Windows observation but was not re-checked.
- `.project/archive/**` excluded from scanning per brief beyond the three MANIFEST.md headers read for recent-activity context.
