# Evidence — codebase

<!-- Written by the codebase mapper during /gsd-path-inspect. Read by define
     (brownfield mode), researchers (fifth standard dimension), the planner
     (conventions are binding), and reviewers. -->

Repo root: /home/yuta/Documents/typsphinx
Scanned: 2026-11-03 (sidecar at 79ed090eb30aeb255e5775c699c41c9fc3dd766c, clean `git status` before and after)
Checks run: (all in the verify sidecar, after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`; shim check `grep -q typsphinx-fhs-run "$(command -v uv)"` → ok; sidecar venv is uv-managed CPython 3.14)
- `LC_ALL=C uv run pytest tests/ -q -p no:cacheprovider -o addopts=""` → 1731 passed, 18 skipped, 0 failed, exit 0, 125.65 s (skip reasons not captured)
- `uv run black --check .` → 382 files unchanged, exit 0
- `uv run ruff check .` → All checks passed
- `uv run mypy typsphinx/` → Success: no issues found in 9 source files
- Read-only network: `gh release list --limit 3` → v0.9.8 Latest (2026-11-02T17:01:48Z); `gh run list --workflow release.yml --limit 3` → v0.9.8 tag push run success; `gh issue list --state open` and `gh pr list` → no rows printed
- Not run: `tox`, docs builds (`tox -e docs-html|docs-pdf`), `linkcheck`, `uv build`

## Map

- **Stack**: Python package `typsphinx` 0.9.8 (`pyproject.toml:7`), `requires-python >=3.12`, classifiers 3.12/3.13. Runtime deps: `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16` (typst-py; no Typst CLI). setuptools build backend; `uv` + `uv.lock`; `tox` with `tox-uv~=1.35` (`tox.ini:15`) and `uv-venv-lock-runner`. Dev: pytest, pytest-cov, black 26, ruff 0.15–0.17, mypy, pypdf, pillow, sphinxcontrib-bibtex (dev-only by design, `pyproject.toml:44-50`). Docs extra: furo, sphinx-autodoc-typehints, sphinx-intl, myst-parser. Typst Universe `@preview` packages pinned in three places: codly 1.3.0, codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1, diagraph 0.3.7 (`typsphinx/writer.py:266-270`, `typsphinx/template_engine.py:705-709`, `typsphinx/templates/base.typ:8-23`). NixOS `flake.nix` devShell with FHS shims for the maintainer only.
- **Entry points**: `sphinx.builders` entry points `typst` and `typstpdf` both → `typsphinx` (`pyproject.toml:63-65`); `typsphinx/__init__.py:setup()` registers `TypstBuilder`/`TypstPDFBuilder`, nine `typst_*` config values, and one `config-inited` handler (`check_config_at_init`, `typsphinx/__init__.py:73`). Helper scripts: `scripts/extract_changelog_section.py` (used by release), `scripts/render_admonition_greyscale.py`.
- **Architecture**: Sphinx builder → writer → translator. `builder.py` (2642 lines) drives writing, output-path collision validation, registry-key and template-path validation, image tracking/relocation, and in `finish()` copies each used template bundle directory to `<outdir>/_template/<key>/`; `TypstPDFBuilder.finish()` compiles master docs via `pdf.py` (typst-py). `writer.py` emits per-docname content `.typ` (imports + codly init, no template) and per-`typst_documents` wrapper files that apply the template and `#include()` content. `translator.py` (8149 lines, 98 `visit_*` / 91 `depart_*`, one `TypstTranslator` class at :512) does node→Typst conversion; `unknown_visit` logs a warning and continues (`translator.py:5875-5886`). `template_engine.py` maps metadata to template params; `template_registry.py` resolves `typst_document_templates` keys; `removed_config.py` warns on four removed config names; `pathfmt.py` quotes paths for messages.
- **Conventions**: Builtin generics and `collections.abc` types (Python 3.12+); black 88 cols, ruff rule set `E,F,W,I,N,UP,B,A,C4,T20` with `N802` ignored for visitor names (`pyproject.toml:127-137`); config-shape errors raised as `sphinx.errors.ExtensionError` (13 raise sites) or logged via `sphinx.util.logging` warnings; pytest with `--strict-markers` and `filterwarnings = error::DeprecationWarning, error::PendingDeprecationWarning` (`pyproject.toml:79-91`). Test style is one file per defect/feature "gate" (`tests/test_*_render_gate.py`, `test_*_gate.py`) with a disjoint fixture project under `tests/fixtures/<name>/`, building real Sphinx output and asserting on emitted `.typ` and often compiled PDF text (pypdf). Long rationale comments citing requirement/phase IDs are pervasive in code, config, and tests. Commits are Conventional-Commit style (`docs`/`chore`/`test`/`feat`/`fix`), plus GSD Path pipeline subjects (`plan:`, `build:`, `T00N:`, `ship:`).
- **Maturity**: Classified "Production/Stable"; 188 entries in `tests/`, ~1749 collected tests, full suite green on this HEAD with lint/format/type clean. CI (`.github/workflows/ci.yml`) has jobs test, lint, type-check, coverage, build (wheel-content check), integration; plus `docs.yml`, `drift.yml` (weekly latest-deps), `links.yml` (advisory repo-wide link check), `release.yml` (tag-triggered PyPI trusted publishing). Dependabot for uv (grouped sphinx/docutils/typst stack) and Actions. Known scaffolding/gaps: index entries are skipped (`translator.py:6586-6592`, "we don't generate indices"); dev extra lists `pre-commit` but no `.pre-commit-config.yaml` exists; CHANGELOG `Unreleased` lists only "Planned for Future Releases" (glossary generation, index generation, pre-commit hooks, more Typst Universe template integration).
- **Recent activity**: Last ~60 non-merge commits: GSD Path M001 (`release-0-9-8`) shipped 2026-11-03 (`67142766 ship: M001 — release-0-9-8`) — graphviz rendering via `@preview/diagraph`, BibTeX support, `typst_debug` removal, CLAUDE.md corrections, 0.9.8 CHANGELOG; v0.9.8 released to GitHub/PyPI 2026-11-02. Since then only Dependabot bumps (tox-uv 1.37.2, sphinx group, pypdf 6.21.4) merged to main. Earlier (Sep–Oct 2026) work was under the prior GSD tooling in `.planning/` (removed from the tree by `8443ef55`, 1901 files deleted; preserved under tag `planning-archive-2026-10-02`). Main checkout is on `gsd-path/M002` with only `.project/STATE.md` modified (phase inspect/active, milestone null).

## Finding: The full test suite, lint, format, and type checks are green at the audited HEAD

- **Claim**: At 79ed090e, pytest reports 1731 passed / 18 skipped / 0 failed; black, ruff, and mypy all exit clean.
- **Source**: commands listed under Checks run (sidecar, uv-managed CPython 3.14)
- **Confidence**: high (for this interpreter); medium for py312/py313 equivalence — the sidecar ran 3.14, which is outside the declared classifiers and CI matrix
- **Why it matters here**: Planning can assume a green baseline; any new RED is introduced by the milestone. Baseline counts are interpreter-dependent, so compare like with like (CLAUDE.md "Interpreters may differ").

## Finding: `.planning/` is gone from the tree but 46 references to it remain in code and tests

- **Claim**: `git ls-files | grep ^.planning/` returns 0 files, yet 34 files under `tests/` and `typsphinx/translator.py` contain 46 `.planning/` path references in docstrings/comments, and `.github/workflows/links.yml:12,42` still excludes `.planning`.
- **Source**: `grep -rc "\.planning/" typsphinx tests`; `git show --stat 8443ef55` (1901 files deleted); tag `planning-archive-2026-10-02`
- **Confidence**: high
- **Why it matters here**: Rationale pointers in tests and the translator are dangling in the working tree (resolvable only via the archive tag). A docs/cleanup milestone might target them; a planner should not expect those evidence files to exist on disk.

## Finding: Unsupported doctree nodes warn and continue rather than fail

- **Claim**: `TypstTranslator.unknown_visit` logs `unknown node type: <node>` as a Sphinx warning and does not raise or skip; `unknown_departure` is a no-op. Children of an unknown node are still visited.
- **Source**: `typsphinx/translator.py:5875-5895`; comment at `:3196` ("warn and continue -- it does NOT skip")
- **Confidence**: high
- **Why it matters here**: New node support is usually added as a `visit_*`/`depart_*` pair plus a render-gate test; under `-W` a user build fails on unknown nodes, otherwise text may leak unformatted. The planner should expect "support X" work to start by observing this warning.

## Finding: Index and glossary-generation features are not implemented

- **Claim**: `visit_index` always raises `SkipNode` (no index is generated); `visit_glossary` is a pass-through that renders the inner definition list only. CHANGELOG `[Unreleased]` lists glossary generation and index generation as planned.
- **Source**: `typsphinx/translator.py:6586-6592`, `:6627-6640`; `CHANGELOG.md:8-14`
- **Confidence**: high
- **Why it matters here**: These are the only forward-looking items the repository itself names; a likely candidate scope for the next milestone.

## Finding: `pre-commit` is a dev dependency with no configuration

- **Claim**: `pre-commit>=3.0` is in the `dev` extra but no `.pre-commit-config.yaml` exists; CHANGELOG lists "Pre-commit hooks" as planned.
- **Source**: `pyproject.toml:39`; `ls .pre-commit-config.yaml` → not found; `CHANGELOG.md:12`
- **Confidence**: high
- **Why it matters here**: Half-built tooling item; installing it does nothing today.

## Finding: The `@preview` package versions are triplicated and test-gated

- **Claim**: Five `@preview` imports are hard-coded identically in `writer.py:266-270`, `template_engine.py:705-709`, and `templates/base.typ:8-23`; `tests/test_preview_version_sync.py` enforces agreement.
- **Source**: grep shown in Map; CLAUDE.md "@preview version-sync hazard"
- **Confidence**: high
- **Why it matters here**: Any milestone adding or bumping a Typst package must touch all three files in one task, or CI fails.

## Finding: Gate tests are the dominant test idiom and build real Sphinx projects

- **Claim**: Most of the 188 test-directory entries are `test_*_gate.py` files, each using a disjoint fixture tree in `tests/fixtures/` (only one Sphinx `rootdir` root, `tests/roots/test-basic`); many compile PDF via typst-py and extract text with pypdf. PDF-dependent tests skip via `importorskip("typst")`/`importorskip("pypdf")` and `skipif(not TYPST_AVAILABLE)`.
- **Source**: `ls tests`, `ls tests/roots`, `ls tests/fixtures`; grep for `importorskip`/`skipif` in `tests/*.py`
- **Confidence**: high
- **Why it matters here**: Planner Verify commands should target individual gate files (`uv run pytest tests/test_<x>_gate.py`) — the full suite takes ~2 minutes. New fixtures go in `tests/fixtures/<name>/`, not `tests/roots/`.

## Finding: The sidecar/worktree interpreter is CPython 3.14, outside the declared support matrix

- **Claim**: A fresh `uv sync` in a linked worktree builds `.venv` on uv-managed CPython 3.14 (`.venv/pyvenv.cfg` version_info = 3.14), while `pyproject.toml` classifiers, black `target-version`, and CI test only 3.12/3.13.
- **Source**: sidecar `.venv/pyvenv.cfg`; `pyproject.toml:17-18,98`; `tox.ini:2`
- **Confidence**: high
- **Why it matters here**: Task Verify evidence from isolated worktrees is gathered on 3.14, not on a CI interpreter. Version-sensitive behaviour (warnings, typing) could pass locally and differ in CI, or vice versa.

## Finding: Out-of-tree evidence files from the prior tool's milestone sit at `docs/` root

- **Claim**: `docs/S02-LOCAL-PARITY-EVIDENCE.md`, `docs/S03-ARTIFACT-GATE-EVIDENCE.md`, `docs/S04-PUBLISHED-SITE-EVIDENCE.md` are tracked, outside `docs/source/`, and labelled "Slice M002/S02" from the earlier (gsd-pi) milestone numbering.
- **Source**: `ls docs`; `head -5 docs/S02-LOCAL-PARITY-EVIDENCE.md`
- **Confidence**: high
- **Why it matters here**: "M002" in those files is not the current GSD Path milestone M002; agents grepping for M002 will hit them. They are not part of the built docs.

## Finding: Config-shape validation is concentrated in the builder, with one deliberate event-hook exception

- **Claim**: Output-path collisions, registry-key references, and template-path rules are validated in `TypstBuilder` methods (`builder.py:1068`, `:1237`, `:1302`) raising `ExtensionError`; removed config names are detected only by the `config-inited` handler in `removed_config.py:67` (four names, including `typst_debug` removed in 0.9.8).
- **Source**: `grep -nE "def " typsphinx/builder.py`; `typsphinx/removed_config.py:40-66`; `typsphinx/__init__.py:62-73`
- **Confidence**: high
- **Why it matters here**: Removing a config value follows the `removed_config.py` pattern; new validation belongs in the builder methods. The pattern is binding on a planner.

## Apparent intent

- Inference: the project is in maintenance-plus-incremental-feature mode after a stable 0.9.x line, aiming toward 1.0 — based on "Production/Stable" classifier, 0.9.8 just released, only Dependabot activity since, and CHANGELOG's planned list (glossary, index, pre-commit, Typst Universe templates).
- Inference: the process is migrating fully from the old `.planning/` GSD tooling to GSD Path (`.project/`) — based on `8443ef55` archive commit, `fb349035` adopting GSD Path 1.7.1, and M001 shipped through the GSD Path pipeline with PR integration.
- Inference: there is an earlier-planned Read the Docs migration (`.readthedocs.yaml` present; `Documentation` URL already points to readthedocs.io in `pyproject.toml:58`) — status of that migration not established from code.

## Open questions for define

- What is milestone M002's goal: one of the CHANGELOG "Planned" items (index generation, glossary generation, pre-commit hooks, more Typst Universe templates), a 1.0 release, or something else?
- Should the 46 dangling `.planning/` references in tests/translator and the `.planning` exclusion in `links.yml` be cleaned up, or kept as historical pointers resolvable via the archive tag?
- Should `docs/S0[2-4]-*-EVIDENCE.md` remain tracked at `docs/` root?
- Is Python 3.14 meant to be supported (add classifier/CI matrix), or should worktree venvs be pinned to 3.12/3.13 so local evidence matches CI?
- Is `pre-commit` in the dev extra intentional without a config, or should it be configured or dropped?

## Blocked areas

- tox environments, docs builds (html/pdf), linkcheck, and `uv build` were not run (time cost / network); CI status of those jobs on HEAD not checked.
- The 18 skipped tests' reasons were not captured (`-q` without `-rs`).
- `.project/archive/` and installed GSD Path skill bundles excluded by brief.
