# Evidence — codebase

Repo root: /home/yuta/Documents/typsphinx
Scanned: 2026-11-03 (Audited HEAD 660e3436274607e52981b849ef77701edfe9cad9, verify sidecar at that revision)
Checks run: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` → ok (sidecar .venv, uv-managed CPython 3.14); `LC_ALL=C uv run pytest -q -p no:cacheprovider -o addopts=""` → 1883 passed, 1 skipped, 0 failed in 214s; `uv run ruff check .` → All checks passed; `uv run black --check .` → 398 files unchanged; `uv run mypy typsphinx/` → no issues in 10 source files; `gh issue list --state open` → `[]` (no open issues); `git status --short` after all runs → empty

## Map

- **Stack**: Python >=3.12 (classifiers 3.12/3.13), setuptools build; runtime deps `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16` (typst-py, in-process compiler) (pyproject.toml:1-34). Dev: pytest, tox 4 + tox-uv, black 26, ruff, mypy, pypdf, pillow, sphinxcontrib-bibtex (dev-only by design). Docs extra: furo, myst-parser, sphinx-intl, sphinx-autodoc-typehints. Lockfile `uv.lock`; Nix `flake.nix`/`flake.lock` devShell. Version 0.9.8. Typst Universe packages pinned only in `typsphinx/typst_deps.py:92-98`: codly 2.0.0 (as module `codly`), codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1, diagraph 0.3.7.
- **Entry points**: `sphinx.builders` entry points `typst` / `typstpdf` → `typsphinx` (pyproject.toml "Entry points"); `typsphinx/__init__.py:30-80` `setup()` registers `TypstBuilder`, `TypstPDFBuilder`, 10 `typst_*` config values and the project's only event hook (`config-inited` → `removed_config.check_config_at_init`). Scripts: `scripts/extract_changelog_section.py`, `scripts/render_admonition_greyscale.py`.
- **Architecture**: doctree → `TypstTranslator` (`translator.py`, 8078 lines, 98 `visit_*`, `unknown_visit` at :5804 warns and continues) → `TypstWriter` (`writer.py`) writes each docname's content `.typ` with the two-line `/_typsphinx/deps.typ` preamble and renders one wrapper per `typst_documents` entry through `TemplateEngine` (`template_engine.py`) → `TypstBuilder` (`builder.py`, 2858 lines) validates output-path/registry/template collisions pre-write, copies images and used template bundles to `_template/<key>/`, writes `_typsphinx/deps.typ`, warns on template dependency drift → `TypstPDFBuilder.finish()` (builder.py:2721) compiles masters via `pdf.py` (typst-py). Supporting modules not named in CLAUDE.md's Architecture list: `template_registry.py` (550 lines, `typst_document_templates` resolution/key-shape validation), `removed_config.py` (removed-value warnings: typst_template_assets, typst_authors, typst_toctree_defaults, typst_debug), `pathfmt.py` (`quote_path` for messages).
- **Conventions**: builtin generics, `collections.abc` types; black 88 / ruff (E,F,W,I,N,UP,B,A,C4,T20; N802 ignored for visitor names); pytest `filterwarnings` escalate DeprecationWarning and PendingDeprecationWarning to errors (pyproject.toml filterwarnings). Tests are overwhelmingly per-defect "gate" files (`test_*_render_gate.py`, `test_*_gate.py`) that run Sphinx as a subprocess (`sys.executable -m sphinx`) over a dedicated `tests/fixtures/<name>/` project and assert on emitted `.typ` and/or PDF text. Commit style under GSD Path: `T00N: <sentence>`, `build: ...`, `plan: ...`, `ship: M00N — <slug>`, PR merge commits into main; earlier history uses conventional `feat:/fix(NN-NN):/docs:` with GSD phase numbers. CHANGELOG follows Keep a Changelog with `## [Unreleased]`.
- **Maturity**: All checks green at HEAD (see Checks run). 195 test files under tests/, ~190 fixture projects under `tests/fixtures/`, one under `tests/roots/` (`test-basic`). CI (`.github/workflows/ci.yml`) runs tox py312/py313 on ubuntu/windows/macos plus lint, type, cov (Codecov), and a build job verifying the wheel carries the template bundle; `docs.yml`, `links.yml`, weekly `drift.yml`, tag/dispatch-triggered `release.yml` with PyPI trusted publishing (`id-token: write`). Examples: `examples/basic`, `examples/advanced`, `examples/charged-ieee/{approach1,approach2}`. No TODO/FIXME markers in `typsphinx/` except a historical tag reference at translator.py:6276.
- **Recent activity**: Five GSD Path milestones shipped on 2026-11-03 via PRs #187-#190: M001 release 0.9.8 (tag v0.9.8), M002 externalize Typst deps into `_typsphinx/deps.typ` + `typst_dependencies` + drift warning, M003 Windows test portability, M004 codly 1.3 → 2.0 upgrade (code-mode `codly.new(raw(...))` emission). Since 2026-09 the non-`.project` churn concentrates in uv.lock, CHANGELOG.md, pyproject.toml, translator.py, tests/test_preview_version_sync.py and the graphviz/diagraph gates; the pre-2026-10 history is the old GSD `.planning/` tree (since removed, 4477 commits total).

## Finding: Unreleased breaking change sits on top of the 0.9.8 version string

- **Claim**: `pyproject.toml` declares `version = "0.9.8"` and tag `v0.9.8` exists, while `CHANGELOG.md` `## [Unreleased]` (line 8, before `## [0.9.8] - 2026-11-03` at line 90) records the M002 deps.typ contract and a "Breaking: codly is upgraded from 1.3.0 to 2.0.0" entry with no compatibility shim.
- **Source**: pyproject.toml:7; CHANGELOG.md:8-90; `git tag --sort=-creatordate`
- **Confidence**: high
- **Why it matters here**: the next release must pick a version that signals a breaking template contract change (0.10.0 vs 1.0.0 vs 0.9.9); `release.yml` publishes on any `v*` tag, so the version decision and release-prep (bump, CHANGELOG link block) are open work if this milestone ships a release.

## Finding: Test style is subprocess fixture gates, not sphinx.testing rootdir

- **Claim**: `tests/roots/` contains only `test-basic`; ~190 fixture projects live in `tests/fixtures/`, 142 test files reference `subprocess`/`sys.executable`, and 128 reference `tests/fixtures`; only one test file uses the `rootdir`/`@pytest.mark.sphinx` route that CLAUDE.md's Tests section describes as the integration mechanism.
- **Source**: `ls tests/roots tests/fixtures`; `grep -ln "subprocess\|sys.executable" tests/*.py | wc -l` → 142; `grep -c "rootdir\|@pytest.mark.sphinx"` → 1 file; CLAUDE.md:74
- **Confidence**: high
- **Why it matters here**: the planner should model new tests on an existing `test_*_render_gate.py` + `tests/fixtures/<name>/` pair; following CLAUDE.md alone would produce tests that do not match the dominant convention.

## Finding: CLAUDE.md architecture list omits three modules

- **Claim**: `typsphinx/` has 10 modules; CLAUDE.md's Architecture section describes `__init__`, builder, writer, translator, template_engine, typst_deps, pdf, and does not describe `template_registry.py` (550 lines), `removed_config.py` (100), or `pathfmt.py` (97).
- **Source**: `wc -l typsphinx/*.py`; CLAUDE.md "Architecture"
- **Confidence**: high
- **Why it matters here**: `typst_document_templates` key validation and the removed-config warning path live in modules a planner reading only CLAUDE.md would not look for; the docs auditor may flag this as a doc gap.

## Finding: Sidecar venv runs on Python 3.14 while CI and classifiers cover 3.12/3.13

- **Claim**: a fresh `uv sync` in the worktree built `.venv` on uv-managed CPython 3.14 (`pyvenv.cfg` `version_info = 3.14`), and the full suite passed there; CI matrix and pyproject classifiers name only 3.12 and 3.13, and black `target-version` is py312/py313.
- **Source**: `.venv/pyvenv.cfg`; .github/workflows/ci.yml:17-18; pyproject.toml classifiers
- **Confidence**: high
- **Why it matters here**: local verify evidence from worktrees is on an untested-in-CI interpreter; test-count comparisons with the main checkout (which may use nixpkgs Python) need the interpreter recorded. Not a failure.

## Finding: Stray slice-evidence files in docs/

- **Claim**: `docs/S02-LOCAL-PARITY-EVIDENCE.md`, `docs/S03-ARTIFACT-GATE-EVIDENCE.md`, `docs/S04-PUBLISHED-SITE-EVIDENCE.md` are tracked under `docs/` (outside `docs/source/`), committed 2026-10-03 by the earlier gsd-pi graphviz-parity work (commit 9e5b9449 and neighbours).
- **Source**: `ls docs`; `git log -- docs/S02-LOCAL-PARITY-EVIDENCE.md`
- **Confidence**: high
- **Why it matters here**: they are process evidence from a retired tooling era, not user docs; whether to keep, move, or delete them is a user call.

## Finding: The deps.typ indirection is the load-bearing integration seam

- **Claim**: every content file, wrapper and `templates/base.typ` imports `/_typsphinx/deps.typ` (root-absolute, compile root = outdir); package specs exist only in `typst_deps.py:92-98`; `tests/test_preview_version_sync.py` gates against re-pinning; `typsphinx-init` only applies `codly.lang-set_(languages: codly-languages)` (typst_deps.py:106-111).
- **Source**: typsphinx/typst_deps.py:85-145; CHANGELOG.md Unreleased; M004 archive MANIFEST.md success rows
- **Confidence**: high
- **Why it matters here**: any change to Typst package versions or init behaviour is a one-file edit plus gate updates; renaming deps.typ exports is a documented breaking change (docs/source/user_guide/templates.rst).

## Apparent intent

- Inference: the project is converging on a next release that ships the M002-M004 work (deps.typ contract, `typst_dependencies`, codly 2.0) — based on a populated `## [Unreleased]` with a Breaking entry, no open issues, and M001 having been a release milestone.
- Inference: the maintainer favours one-defect-one-gate hardening with surface-level (PDF/.typ) evidence over refactoring — based on ~190 single-purpose fixtures and gate tests and the size of translator.py/builder.py left unsplit.

## Open questions for define

- Is this milestone a release (version bump + CHANGELOG release block + tag), and if so which version number signals the codly 2.0 / deps.typ breaking change?
- If it is not a release, what feature or fix is the milestone's goal? (No open GitHub issues exist to suggest one.)
- Should `docs/S0x-*-EVIDENCE.md` remain in the repository?
- Should CLAUDE.md's Architecture/Tests sections be updated to name `template_registry.py`, `removed_config.py`, `pathfmt.py` and the `tests/fixtures/` gate convention?
- Should Python 3.14 be added to CI/classifiers given worktree venvs already run on it?

## Blocked areas

- Identity of the 1 skipped test was not resolved (skip reason not captured; `-o addopts=""` suppressed `-v`); ~30 test files contain `skipif`/`pytest.skip`.
- Docs builds (`tox -e docs-html`, `tox -e docs-pdf`) and `linkcheck` were not run in this inspection.
