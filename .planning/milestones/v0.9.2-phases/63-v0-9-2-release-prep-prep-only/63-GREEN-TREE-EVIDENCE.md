# Phase 63 — Local Green-Tree Evidence (SC#4, local half)

## Provisioning and tree identity

Provisioning command and its (tail) output:

```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
$ uv sync --extra dev
...
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a207bd1b50c05442b)
 + typst==0.15.0
 + urllib3==2.7.0
 + virtualenv==21.5.1
```

Worktree identity — proving every measurement below is taken against THIS worktree, not the
main checkout:

```
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a207bd1b50c05442b

$ git rev-parse --abbrev-ref HEAD
worktree-agent-a207bd1b50c05442b

$ git rev-parse HEAD
d264a1eeed3d102ca0223bd8b318046e50c020d6

$ uv run python -c 'import typsphinx,os;print(os.path.realpath(typsphinx.__file__))'
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a207bd1b50c05442b/typsphinx/__init__.py

$ uv run python -c 'import typsphinx; print(typsphinx.__version__)'
0.9.2

$ sed -n '7p' pyproject.toml
version = "0.9.2"
```

The imported `typsphinx.__file__` real path lies inside this worktree's own directory tree
(`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a207bd1b50c05442b/typsphinx/__init__.py`),
not the main checkout's `/home/yuta/Documents/typsphinx/typsphinx/__init__.py`. This is the exact
hazard `CLAUDE.md` § "Worktree-isolated execution" documents: the main `.venv` carries a PEP-660
editable finder pointing at the main checkout's absolute path, so without this check a worktree can
edit one tree while measuring another. The version read back through the real import path is
`0.9.2`, matching `sed -n '7p' pyproject.toml`.

## Product-tree delta from the phase base

`PHASE_BASE_SHA` is READ OUT of `63-CLOSEOUT-GUARD.md` § "Baseline" — not re-derived — where it is
recorded as `c31bb048bf5a92b7550bc2aa68efb114437533fa` (subject `docs(63): add pattern map`).

```
$ git cat-file -e c31bb048bf5a92b7550bc2aa68efb114437533fa && echo EXISTS
EXISTS

$ git diff --name-only c31bb048bf5a92b7550bc2aa68efb114437533fa..HEAD -- . ':(exclude).planning' | LC_ALL=C sort
CHANGELOG.md
README.md
pyproject.toml
tests/test_changelog_page_gate.py
uv.lock

$ git diff --name-only c31bb048bf5a92b7550bc2aa68efb114437533fa..HEAD -- typsphinx/
(empty)
```

The product-tree delta is exactly the five files this phase touches: `CHANGELOG.md`, `README.md`,
`pyproject.toml`, `tests/test_changelog_page_gate.py`, and `uv.lock`. The `typsphinx/`-scoped diff
is empty. The non-empty first result is what makes the empty second one a finding rather than the
artifact of an unreachable anchor — the anchor is reachable and the diff mechanism works; it simply
finds nothing under `typsphinx/`.

## Division of authority

This file is authoritative for `pytest`, `black`, `mypy`, and the two documentation builds
(`docs-html`, `docs-pdf`). It is **NOT** authoritative for `ruff` — on this host, in a freshly
`uv sync`-provisioned worktree venv, `ruff` is a generic-linux ELF that cannot execute. This
phase's `ruff` verdict is taken from the dispatched CI run's `Lint and Format Check` job,
recorded in `63-CI-EVIDENCE.md`.

The release-coverage tuple's own proof (RELEASE_VERSIONS extension, docs-extra content-coverage
tests) is also not this file's authority — it required the `docs` extra and was taken in plan
63-01 Task 3 (`uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v`, 6
passed / 0 skipped). This worktree deliberately carries `--extra dev` only, so its suite counts
stay comparable to the carried-in baseline of 1543 passed / 5 skipped.

## SC#4 — full pytest suite

```
$ uv run pytest -q
...
================= 1543 passed, 5 skipped in 124.08s (0:02:04) ==================
```

Compared against the carried-in baseline of **1543 passed and 5 skipped**: exact match, 0 failed
(`grep -cE '[0-9]+ failed' /tmp/63-pytest.txt` returned `0`).

Itemised skips (from a second `-rs` run of the same suite, plus `-v` on the two skip-bearing
files to recover full node ids):

```
$ uv run pytest -q -rs
...
=========================== short test summary info ============================
SKIPPED [1] tests/test_changelog_page_gate.py:168: myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class
SKIPPED [1] tests/test_changelog_page_gate.py:177: myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class
SKIPPED [1] tests/test_changelog_page_gate.py:187: myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class
SKIPPED [1] tests/test_changelog_page_gate.py:219: myst-parser is required to build the changelog include fixture; it lives in the docs extra only (D-01)
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1543 passed, 5 skipped in 121.53s (0:02:01) ==================

$ uv run pytest -q -v tests/test_changelog_page_gate.py tests/test_corpus_gate.py 2>&1 | grep -i skip
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_carries_every_release SKIPPED [ 27%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_has_one_changelog_heading SKIPPED [ 36%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_build_emits_no_changelog_warnings SKIPPED [ 45%]
tests/test_changelog_page_gate.py::TestChangelogIncludeCompilesToPdf::test_included_changelog_reaches_the_pdf SKIPPED [ 54%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3...) [100%]
======================== 6 passed, 5 skipped in 14.04s =========================
```

Node id + verbatim skip reason for each of the five skips:

| Node id | Skip reason (verbatim) |
|---|---|
| `tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_carries_every_release` | myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class |
| `tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_has_one_changelog_heading` | myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class |
| `tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_build_emits_no_changelog_warnings` | myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class |
| `tests/test_changelog_page_gate.py::TestChangelogIncludeCompilesToPdf::test_included_changelog_reaches_the_pdf` | myst-parser is required to build the changelog include fixture; it lives in the docs extra only (D-01) |
| `tests/test_corpus_gate.py::test_empty_url_before_after` | SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1) |

Four trace to the `myst_parser` docs-extra gap, one to the env-gated corpus report — exactly the
itemisation the carried-in baseline requires. No sixth skip occurred, and no failure occurred. The
baseline figures (1543 passed / 5 skipped) were not adjusted; the measurement matched them exactly.

## SC#4 — format, type and version-sync gates

```
$ uv run black --check .
All done! ✨ 🍰 ✨
355 files would be left unchanged.
(exit 0)

$ uv run mypy typsphinx/
Success: no issues found in 9 source files
(exit 0)

$ uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v
tests/test_extension.py::test_version_matches_pyproject_toml PASSED      [ 20%]
tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject PASSED [ 40%]
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 60%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 80%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]
============================== 5 passed in 0.04s ===============================
```

Both `black --check .` and `mypy typsphinx/` exit 0. The version-sync guard trio (5 tests across
`test_version_matches_pyproject_toml`, `test_readme_version_sync.py`, and
`test_preview_version_sync.py`) reports 0 failed.

**Lint-authority split.** `ruff` was *attempted* here additively:

```
$ uv run ruff check .
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
(exit 127)
```

On this host, in a freshly `uv sync`-provisioned worktree venv, `ruff` is a generic-linux ELF that
cannot execute and fails with a dynamic-linker error at exit 127 — the recorded hazard from
`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`. A green `black`
plus `mypy` is **NOT** "lint clean". This phase's `ruff` verdict is taken from the dispatched CI
run's `Lint and Format Check` job (`ci.yml` line ~55-70, whose one substantive step
`Run lint with tox` on line 69 runs `uv run tox -e lint`, i.e. `black --check .` then
`ruff check .`), recorded in `63-CI-EVIDENCE.md`. This local `ruff` failure is never recorded as
this phase's lint verdict, and its silence is never recorded as a pass.

## SC#4 / D-21 — documentation builds on a clean baseline

Both builds were run with the build directory removed as part of the command, not as a preamble:

```
$ rm -rf docs/_build && uv run tox -e docs-html
...
出力中...[100%] user_guide/templates
索引を生成中... genindex py-modindex 完了
モジュールコードをハイライトしています...[100%] typsphinx.writer
追加のページを出力中... search 完了
English (code: en) の検索インデックスを出力... 完了
オブジェクト インベントリを出力... 完了
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (3.93=setup[0.14]+cmd[3.78] seconds)
  congratulations :) (3.97 seconds)
```

```
$ rm -rf docs/_build && uv run tox -e docs-pdf
...
writing output... [user_guide/templates] done
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a207bd1b50c05442b/docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (4.19=setup[0.11]+cmd[4.07] seconds)
  congratulations :) (4.22 seconds)
```

`docs-html`: `build succeeded, 3 warnings.` — matches the last-recorded figure of 3 exactly.
`docs-pdf`: `build succeeded, 5 warnings.`, with the generated-PDF path line
(`Generated PDF: .../docs/_build/pdf/typsphinx.pdf`) — matches the last-recorded figure of 5
exactly.

Both builds were clean-started: `rm -rf docs/_build` ran immediately before each build command
(twice total, once per build), so an incremental rebuild's under-reported-warning hazard does not
apply here — each count reflects a full, freshly-invalidated rebuild rather than a partial one
that could carry stale (and therefore under-counted) warnings from unrelated pages.

Both counts matched the carried-in baseline exactly (3 / 5); no divergence occurred, so no
corrective prose edit to `CHANGELOG.md` was needed. `grep -c '0\.9\.1' CHANGELOG.md` returns `0`.

`git status --porcelain typsphinx/ .planning/REQUIREMENTS.md` is empty after both tasks.
