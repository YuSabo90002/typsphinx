---
id: T001
title: Make the eight Windows-failing tests platform-independent and add typst_deps.py to the README tree
wave: 1
deps: []
status: done
agent: build_T001
base: 3307123fceb391388cb8be1dab03467ad2913a75
worktree: null
task_branch: null
files:
  - tests/test_template_dependency_drift_gate.py
  - tests/test_preview_version_sync.py
  - tests/test_hand_compile_root_gate.py
  - README.md
---

# T001 — Make the eight Windows-failing tests platform-independent and add typst_deps.py to the README tree

## Context

M002 merged to `main` (f8e9b152) with eight tests that fail only on windows-latest (CI run 41589478348, 8 failed / 1794 passed per job); the product is correct in all eight (inspect evidence for this milestone). Causes: (1) `tests/test_preview_version_sync.py::test_five_specs_appear_only_in_typst_deps_module` builds `str(p.relative_to(REPO_ROOT))`, giving `typsphinx\typst_deps.py` on Windows, and compares it with `"typsphinx/typst_deps.py"`; (2) `tests/test_hand_compile_root_gate.py` asserts `MISSING_TEMPLATE_FRAGMENT = "_typsphinx/deps.typ"` is a substring of typst's error, but on Windows typst reports `file not found (searched at \\?\C:\...\build\manuals\_typsphinx\deps.typ)`; (3) six tests in `tests/test_template_dependency_drift_gate.py` slice captured stderr lines in `_drift_messages()` and keep Sphinx's trailing ANSI reset `\x1b[39;49;00m`, because Sphinx 9.1.1 colourises on win32 unless `NO_COLOR` is set. README.md's `### Project Structure` tree omits `typsphinx/typst_deps.py` (DOCS-AUDIT queue #1, fix-doc).

## Approach

- Test-only changes plus the README tree; do not touch anything under `typsphinx/` (INTENT Scope out).
- Drift gate: remove every ANSI SGR escape (`\x1b\[[0-9;]*m`) from each captured line before slicing/comparing (E1). Do not add a project-wide helper or conftest convention (vetoed). Keep every existing assertion's exact message text, count, and order (N1, judgment) — only colour handling changes.
- Version-sync test: compare POSIX-normalised relative paths (e.g. `.as_posix()`), keeping the check that fails if a second file under `typsphinx/` names a five-package spec.
- Hand-compile test: normalise `\` to `/` in the error text before matching the fragment (E3); factor the match into a small function in the same test file and add a test that feeds `\\?\C:\x\_typsphinx\deps.typ`, `C:\x\_typsphinx\deps.typ`, and `/x/_typsphinx/deps.typ` (all match) and `/x/_typsphinx/other.typ` (no match).
- README: add a `typst_deps.py` line with a short comment under `typsphinx/` in the Project Structure tree, keeping the existing alignment.
- Warning-text tests run under `LC_ALL=C`. `FORCE_COLOR=1` with `NO_COLOR` unset makes Linux sphinx-build colourise (measured: coloured stderr), which is the Windows simulation for SC1; confirm the drift gate fails under it before your fix.

## Interface contract

- None

## Intent coverage

- SC1
- SC2
- SC3
- SC4
- SC5

## Acceptance criteria

1. SC1/E1: `env -u NO_COLOR FORCE_COLOR=1 LC_ALL=C uv run pytest tests/test_template_dependency_drift_gate.py` passes, and so does the same run without `FORCE_COLOR`; every ANSI SGR sequence anywhere in a captured warning line is removed before comparison, and the comparisons still match the exact uncoloured messages, counts, and order they asserted before (N1).
2. SC2: `test_five_specs_appear_only_in_typst_deps_module` compares POSIX-normalised relative paths (no `str()` of a native `Path` in that comparison) and still fails if a second file under `typsphinx/` names a five-package spec.
3. SC3/E3: the missing-file assertion normalises `\` to `/` before matching `_typsphinx/deps.typ`; a test in `tests/test_hand_compile_root_gate.py` asserts that `\\?\C:\x\_typsphinx\deps.typ`, `C:\x\_typsphinx\deps.typ`, and `/x/_typsphinx/deps.typ` match and `/x/_typsphinx/other.typ` does not; `test_compile_without_root_raises_naming_the_missing_template` passes on Linux.
4. SC4: README.md's `### Project Structure` tree lists `typst_deps.py` under `typsphinx/` alongside the existing modules.
5. SC5: on the task's tree, `LC_ALL=C uv run pytest tests/` reports 0 failed, and `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` are clean.
6. E1: every ANSI SGR escape sequence (`\x1b[...m`) anywhere in a captured warning line is removed before comparison, not only the trailing reset; the comparison then matches the exact uncoloured message.
7. E3: the check normalises `\` to `/` in the error text before matching `_typsphinx/deps.typ`; the forms `\\?\C:\x\_typsphinx\deps.typ`, `C:\x\_typsphinx\deps.typ`, and `/x/_typsphinx/deps.typ` all match, and `/x/_typsphinx/other.typ` does not.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && env -u NO_COLOR FORCE_COLOR=1 LC_ALL=C uv run pytest tests/test_template_dependency_drift_gate.py -o addopts="" -q && LC_ALL=C uv run pytest tests/test_template_dependency_drift_gate.py tests/test_preview_version_sync.py tests/test_hand_compile_root_gate.py -o addopts="" -q && ! grep -n 'str(p.relative_to' tests/test_preview_version_sync.py && sed -n '/^### Project Structure/,/^## /p' README.md | grep -q 'typst_deps.py' && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/
```

Heavy: yes

## Log

- 2026-11-03 — created by plan (quick mode)
- 2026-11-03 — build_T001 (coder): Pre-fix Windows simulation `env -u NO_COLOR FORCE_COLOR=1 LC_ALL=C uv run pytest tests/test_template_dependency_drift_gate.py -o addopts="" -q` → 6 failed / 22 passed (each captured line kept a trailing `\x1b[39;49;00m`), confirming the simulation colourises stderr on Linux. Changes: drift gate strips every ANSI SGR sequence (`ANSI_SGR_RE = r"\x1b\[[0-9;]*m"`) from each stderr line in `_drift_messages()` before the marker test/slice — all assertions, expected messages, counts, and order unchanged; version-sync test uses `p.relative_to(REPO_ROOT).as_posix()`, expected list unchanged; hand-compile gate adds `_names_missing_template()` (normalises `\` to `/` before matching `MISSING_TEMPLATE_FRAGMENT`), used by `test_compile_without_root_raises_naming_the_missing_template`, plus `TestMissingTemplateMatchIsSeparatorAgnostic` (3 matching forms parametrized, `/x/_typsphinx/other.typ` rejected); README Project Structure gains `typst_deps.py` under `typsphinx/`. Task Verify run in full: exit 0 — FORCE_COLOR drift gate 28 passed; three-file run 48 passed; grep/README checks pass; `LC_ALL=C uv run pytest tests/` 1829 passed, 1 skipped; black --check, ruff, mypy clean. No-colour drift run also 28 passed. docs extra still installed after sync (furo, myst-parser present).
- 2026-11-03 — orchestrator Verify (sidecar gsd-path-verify/task-t001-verify): pass, exit 0; output tail:
  ```
   + sphinxcontrib-bibtex==2.7.0
   + sphinxcontrib-devhelp==2.0.0
   + sphinxcontrib-htmlhelp==2.1.0
   + sphinxcontrib-jsmath==1.0.1
   + sphinxcontrib-qthelp==2.0.0
   + sphinxcontrib-serializinghtml==2.0.0
   + tomli-w==1.2.0
   + tox==4.64.10
   + tox-uv==1.37.2
   + tox-uv-bare==1.37.2
   + twine==7.0.0
   + types-docutils==0.23.0.20260923
   + typing-extensions==4.16.0
   + typsphinx==0.9.8 (from file:///home/yuta/.gsd-path/projects/4018706f853274cd7713143cf7ba094e230867e5ad2bfc5891d0cd69027eb98b/4b529697c911aff5766d6b9c03f122ba2ed9565d87a00e2f51ea62f3fd0642ec/verify/task-t001-verify)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.13.6
   + virtualenv==21.5.1
  All done! ✨ 🍰 ✨
  394 files would be left unchanged.
  ```
