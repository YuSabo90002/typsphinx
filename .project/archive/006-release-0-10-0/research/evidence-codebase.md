# Evidence — codebase

Repo root: /home/yuta/Documents/typsphinx
Scanned: 2026-11-03 (Audited HEAD 81af8d6b2bd538e99747f65e78c366946d7b81d1, verify sidecar at that revision)
Checks run: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` → ok (sidecar .venv, uv-managed CPython 3.14.4; Sphinx 9.1.1, docutils 0.22.4, typst-py 0.15.0, pytest 9.1.1, tox 4.64.10, tox-uv 1.37.2, black 26.10.1, ruff 0.17.3, mypy 2.4.0); `/usr/bin/env time -v uv run pytest -q -p no:cacheprovider --durations=15` → 1881 passed, 1 skipped in 221.45s (wall 3:42, 98% CPU of 16 cores, max RSS 2.4 GB); `LC_ALL=C uv run pytest -q -p no:cacheprovider -o addopts="" --junitxml=<scratch>/junit.xml` → 1881 passed, 1 skipped in 214.03s (per-file breakdown below); `uv run ruff check .` → All checks passed; `uv run black --check .` → 398 files unchanged; `uv run mypy typsphinx/` → no issues in 10 source files; `gh issue list --state open` → `[]`; `gh run view` of CI on main at 81af8d6b (push, 2026-11-03T12:28) → all 15 jobs success, workflow wall 10m13s; `git status --short` after all runs → empty (only ignored caches)

## Map

- **Stack**: Python >=3.12, classifiers 3.12/3.13/3.14 (pyproject.toml:13-25), setuptools build; runtime deps `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16` (typst-py in-process compiler) (pyproject.toml:27-31). Dev extra: pytest, pytest-cov, tox 4 + tox-uv (`>=1.35,<2`; tox.ini `requires = tox-uv~=1.35`), black 26, ruff, mypy, pypdf, pillow, sphinxcontrib-bibtex (dev-only). No pytest-xdist or other parallel runner in pyproject.toml or uv.lock. Docs extra: furo, sphinx-autodoc-typehints, sphinx-intl, myst-parser. `uv.lock`, `flake.nix`/`flake.lock`. Version 0.9.8. `@preview` pins only in `typsphinx/typst_deps.py:92-98`: codly 2.0.0, codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1, diagraph 0.3.7.
- **Entry points**: `sphinx.builders` entry points `typst`/`typstpdf` → `typsphinx` (pyproject.toml); `typsphinx/__init__.py:30-80` `setup()` registers `TypstBuilder`, `TypstPDFBuilder`, 10 `typst_*` config values and one `config-inited` hook (`removed_config.check_config_at_init`). Scripts: `scripts/extract_changelog_section.py`, `scripts/render_admonition_greyscale.py`.
- **Architecture**: unchanged since the 660e3436 inspection. doctree → `TypstTranslator` (`translator.py`, 8078 lines, 98 `visit_*`/91 `depart_*`; `unknown_visit` at :5804 warns and continues) → `TypstWriter` (`writer.py`, 509 lines) writes content `.typ` files with the `/_typsphinx/deps.typ` preamble and one template wrapper per `typst_documents` entry via `TemplateEngine` (`template_engine.py`, 837) → `TypstBuilder` (`builder.py`, 2858; pre-write collision/registry/template validation, image + `_template/<key>/` bundle copy, `deps.typ` write, drift warning) → `TypstPDFBuilder.finish()` (builder.py:2721) compiles masters through `pdf.py`. Supporting: `template_registry.py` (550), `removed_config.py` (100), `pathfmt.py` (97), `typst_deps.py` (241). Total 13,579 lines in 10 modules.
- **Conventions**: builtin generics, `collections.abc`; black 88 / ruff (E,F,W,I,N,UP,B,A,C4,T20; N802 ignored); pytest `-v --strict-markers`, DeprecationWarning and PendingDeprecationWarning escalated to errors (pyproject.toml `[tool.pytest.ini_options]`). Tests: 191 `test_*.py` files; 142 import `subprocess`, 130 invoke `-m sphinx`, 100 mention `typstpdf`, 86 call typst compile directly; 49 files use module/class/session-scoped fixtures to share one build across tests; 21 use `rootdir`/`SphinxTestApp`. ~190 fixture projects under `tests/fixtures/`, `tests/roots/` holds only `test-basic`. Commit style: `T00N: <sentence>`, `build: …`, `plan: …`, `ship: M00N — <slug>`, PR merge commits into main.
- **Maturity**: all local checks green (Checks run). CI `ci.yml`: test job on ubuntu/windows/macos × 3.12/3.13/3.14 (9 jobs, each `uv run tox -e py31x`), plus lint, type-check, coverage (Codecov), build (wheel bundle check + twine), integration (basic/advanced examples, `-b typst`). Other workflows: `docs.yml` (push main/tags, PR), `links.yml` (every push/PR), `drift.yml` (weekly cron), `release.yml` (tag `v*` / dispatch). CI wall times at 81af8d6b: ubuntu test jobs 5m0s–5m28s, windows 7m52s–10m12s, macos 8m47s–9m16s, coverage 7m9s, lint/type/build ≤16s.
- **Recent activity**: 4,487 commits; 78 in 2026-11, all GSD Path milestones M001–M005 shipped today (tags `milestone/001`…`005`, last product tag `v0.9.8`). M002 externalised `deps.typ`/`typst_dependencies`, M003 Windows test portability, M004 codly 2.0 (breaking), M005 housekeeping + Python 3.14 declaration (5aee2fb9) and CLAUDE.md/doc fixes (c03f3168). `CHANGELOG.md` `## [Unreleased]` carries the M002–M004 Added/Breaking entries; version still 0.9.8, no release since v0.9.8.

## Finding: Full suite is ~214–221 s single-process, unchanged since 660e3436

- **Claim**: At 81af8d6b the full suite takes 214.03 s (LC_ALL=C, `-o addopts=""`) / 221.45 s (default `-v` addopts) with 1881 passed, 1 skipped, running on one core (`time -v`: 98% CPU on a 16-core host). The prior inspection at 660e3436 measured 1883 passed, 1 skipped in 214 s; the 2-test drop matches M005's removal of S03/S04 checks.
- **Source**: the two pytest commands in Checks run; `nproc` → 16; archived `.project/archive/005-housekeeping-py314/research/evidence-codebase.md:5`.
- **Confidence**: high
- **Why it matters here**: any test-speed milestone starts from a 214 s single-core baseline with 15 idle cores; no parallel runner is installed.

## Finding: Suite time is concentrated in three dogfood/corpus gates

- **Claim**: Per-file junit time (sum 213.1 s): `test_corpus_gate` 43.6 s (20%; one test, `test_corpus_compiles_with_no_fatal_error` 44.1 s, a `typstpdf` build of Sphinx's own `doc/` tree), `test_graphviz_docs_gate` 14.5 s (module fixtures building this repo's `docs/source` with typstpdf ~10.9 s and HTML ~3.3 s), `test_bibliography_docs_gate` 11.8 s (a second independent typstpdf build of `docs/source`, ~10.2 s setup). Those three are 70 s (33%). Next: `test_pdf_render_gate` 6.0 s, `test_state_guard_shapes_gate` 4.7 s, `test_changelog_page_gate` 3.8 s; 44 of 191 files take ≥1 s; the long tail of files under 0.5 s sums to 21 s. The top-20 files reach 59% of total.
- **Source**: junit per-classname aggregation of the LC_ALL=C run; `--durations=15` output; tests/test_graphviz_docs_gate.py:202,225 and tests/test_bibliography_docs_gate.py:132 (`scope="module"` fixtures, separate per file).
- **Confidence**: high
- **Why it matters here**: the earlier discarded test-suite-dedup attempt (STATE log, M005 bind line) found only ~5 s from fixture dedup; the measured mass is in the corpus build and two duplicate full-docs typstpdf builds, and in the remaining ~140 s spread across ~190 subprocess-per-fixture files, which is a parallelism question rather than a dedup one.

## Finding: The slow-marked corpus gate runs in CI despite its docstring saying it is excluded

- **Claim**: `tests/test_corpus_gate.py:19-20` says the class is `@pytest.mark.slow` and "excluded from the default/CI fast suite via `-m "not slow"`", but no `-m` filter exists in `tox.ini` (`pytest {posargs:tests/}`, tox.ini:43) or any workflow; CI calls `uv run tox -e py31x` with no posargs. So every CI test job (9) and coverage job clones Sphinx `doc/` at `v{sphinx.__version__}` (cache `~/.cache/typsphinx-corpus-gate/`, outside the repo; local cache already holds `sphinx-v9.1.0` and `sphinx-v9.1.1`) and runs the ~44 s build. It skips (not fails) without network. The single skipped test is `test_empty_url_before_after` (env-gated by `TYPSPHINX_CORPUS_REPORT=1`, tests/test_corpus_gate.py:508-533).
- **Source**: `grep -n '"not slow"\|-m ' tox.ini .github/workflows/*.yml` → no matches; tests/test_corpus_gate.py:102-115,271-275; `pytest.log` line 49 `test_corpus_gate.py ....s`.
- **Confidence**: high
- **Why it matters here**: a planner would assume slow tests are already out of CI; they are not, and 16 test files carry `pytest.mark.slow`. Whether CI should run them is an owner decision, not a bug fix.

## Finding: CI wall time is set by windows/macos test jobs, ~2x ubuntu

- **Claim**: On the main push run at 81af8d6b the workflow took 10m13s; ubuntu test jobs ran 5m0s–5m28s, macos 8m47s–9m16s, windows 7m52s–10m12s (py3.14-windows slowest), coverage 7m9s. Each job runs the full suite single-process via tox.
- **Source**: `gh run view <CI main run> --json jobs`.
- **Confidence**: high
- **Why it matters here**: suite speedups translate to CI only through the windows/macos critical path; tox env provisioning per job is also part of that time (not separately measured).

## Finding: Test-isolation shape for parallel runs is not yet proven

- **Claim**: Gate tests mostly build into `tmp_path`/tmp dirs from read-only `tests/fixtures/<name>/` sources, which suggests parallel-safety, but a session-scoped corpus fixture writes a shared cache under `~/.cache/typsphinx-corpus-gate`, `test_corpus_gate` also creates a git worktree of this repo for its env-gated test, and 9 lines in tests reference `os.chdir`, `Path.home()` or `/tmp/`. No parallel run was attempted in this inspection.
- **Source**: tests/test_corpus_gate.py:110-115,534-536; `grep -rn "os.chdir\|Path.home()\|/tmp/" tests/*.py` → 9 lines.
- **Confidence**: medium
- **Why it matters here**: adding a parallel runner is the obvious lever for the 98%-single-core baseline, and its safety (shared cache, fixture-tree writes such as `__pycache__` under `tests/fixtures/graphviz_degrade_render_gate/` and `package_only_config_gate/` seen after the run) is unmeasured.

## Finding: Historical planning references persist in code and tests

- **Claim**: `.planning/` no longer exists, yet 34 files under `typsphinx/` and `tests/` reference `.planning/…` paths (2 in translator.py), and 595 lines in `typsphinx/*.py` carry GSD phase/decision tags (`Phase NN`, `D-NN`, `SC#`).
- **Source**: `ls -d .planning` → absent; `grep -rl "\.planning/" typsphinx tests | wc -l` → 34; `grep -rn "Phase [0-9]\+\|D-[0-9][0-9]\|SC#" typsphinx/*.py | wc -l` → 595.
- **Confidence**: high
- **Why it matters here**: dangling rationale pointers; harmless at runtime, but a planner reading comments as authoritative will find dead links.

## Apparent intent

- Inference: the next milestone is test-suite speed work — based on M005 INTENT explicitly deferring "Test-suite speed work" to later, the discarded test-suite-dedup attempt in STATE, and the brief requesting current suite timing.
- Inference: a release of the Unreleased M002–M004 changes (breaking codly 2.0) is still pending — based on CHANGELOG `## [Unreleased]` content and version 0.9.8 with no newer `v*` tag.

## Open questions for define

- Is the goal local suite time, CI wall time, or both — and what target (e.g. a number of seconds/minutes) counts as done?
- Is adding a parallel test runner (e.g. pytest-xdist as a dev dependency) acceptable, given the dev-extra/toolchain-pin conventions?
- Should the `slow`-marked tests (corpus gate, ~44 s plus a network clone per CI job) keep running in every CI test job, move to one job/schedule, or be excluded via `-m "not slow"` as the corpus-gate docstring claims?
- May the two separate full-docs typstpdf builds (graphviz and bibliography docs gates) be merged into one shared build, or must each gate keep its own build?
- Is a release (version bump for the codly 2.0 breaking change) in or out of this milestone?

## Blocked areas

- Docs builds (`tox -e docs-html`, `tox -e docs-pdf`) and `linkcheck` were not run.
- Parallel-run safety was not tested (no parallel runner installed; installing one would change the sidecar environment beyond the locked dev/docs extras).
- tox env provisioning time inside CI jobs was not separated from pytest time (job logs not downloaded).
