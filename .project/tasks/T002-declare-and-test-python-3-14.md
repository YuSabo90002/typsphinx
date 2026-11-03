---
id: T002
title: Declare Python 3.14 in classifiers, black, the CI test matrix and tox, and prove tox -e py314 and the full suite pass
wave: 1
deps: []
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - pyproject.toml
  - .github/workflows/ci.yml
  - tox.ini
---

# T002 — Declare Python 3.14 in classifiers, black, the CI test matrix and tox, and prove tox -e py314 and the full suite pass

## Context

At 660e3436 worktree venvs already run the full suite green on uv-managed CPython 3.14 (1883 passed, 1 skipped), but `pyproject.toml` classifiers (lines 21-22) list only 3.12/3.13, black `target-version` (line 111) is `["py312", "py313"]`, the CI test matrix (`.github/workflows/ci.yml:18-23`, `python-version: ['3.12', '3.13']` with `include` rows mapping to `tox-env: py312`/`py313`, on ubuntu/windows/macos) and tox `env_list` (`tox.ini:2`, `py312, py313, lint, type, cov, docs`) stop at 3.13. The owner ruled Q3 a: add 3.14 to all four. ruff `target-version` (`py312`), mypy `python_version` (`3.12`) and `requires-python = ">=3.12"` stay unchanged (INTENT Scope out). CI results of the new jobs are observed on the integration PR, not here (INTENT Constraints).

## Approach

- Add `Programming Language :: Python :: 3.14`, `py314` to black's `target-version`, `'3.14'` to the CI matrix with an `include` row `tox-env: py314` (so all three OSes get it), and `py314` to `tox.ini` `env_list`; add a `[testenv:py314]` section only if py312/py313 have their own sections.
- Do not touch the tox-uv `requires` pin or its comment (toolchain-pin sync hazard; `tests/test_toolchain_config_gate.py`).
- If black 26 rejects `py314`, stop and report `blocked` with the error (do not drop it silently).
- Check whether `uv.lock` needs regeneration after the pyproject edit (`uv lock --check`); `uv.lock` is not in `files`, so if it changes, report `NEEDS-ORCHESTRATOR`.

## Interface contract

- None

## Intent coverage

- SC3
- SC7

## Acceptance criteria

1. SC3: `pyproject.toml` classifiers include `Programming Language :: Python :: 3.14`; black `target-version` includes `py314`; `.github/workflows/ci.yml`'s test matrix includes python-version `3.14` mapped to tox env `py314` on ubuntu, windows and macos; `tox.ini` `env_list` includes `py314`; `uv run tox -e py314` passes on the task's tree.
2. SC7: on the task's tree, `LC_ALL=C uv run pytest tests/` reports 0 failed, and `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` are clean.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && grep -q 'Programming Language :: Python :: 3.14' pyproject.toml && grep -E '^target-version = \[' pyproject.toml | grep -q 'py314' && grep -qE "python-version: \[.*'3\.14'" .github/workflows/ci.yml && grep -q 'tox-env: py314' .github/workflows/ci.yml && grep -E '^env_list' tox.ini | grep -q 'py314' && uv lock --check && LC_ALL=C uv run tox -e py314 && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/
```

Heavy: yes

## Log

- 2026-11-03 — created by plan (quick mode)
