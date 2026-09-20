# Phase 75 — Green Tree Evidence (SC4 local half)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-20T08:59:51Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1d62911013b1999

$ test -f .git; echo "exit:$?"
exit:0

$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo "shim_check:ok"
shim_check:ok

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
Using CPython 3.14.4
Resolved 91 packages in 0.63ms
Prepared 1 package in 438ms
Installed 90 packages in 58ms
exit:0

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --locked
Resolved 91 packages in 2ms
Checked 90 packages in 0.63ms
exit:0
```

The `--locked` sync exits 0 — the lock is in sync with `pyproject.toml` on this tip, so every gate
below runs against a lock that CI's own sync would also accept.

```
$ grep -E "^home|^version_info" .venv/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
version_info = 3.14
```

Per CLAUDE.md § "Interpreters may differ": this worktree's interpreter is uv-managed CPython
3.14, recorded here for cross-worktree comparison against `75-BASE-EVIDENCE.md`'s interpreter,
not asserted as an issue.

PYVENV_HOME = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_INFO = 3.14
BASE_75_04 = 44d22075a77f5b425062b51329b6de1c3b27adbc
SCRATCH_75_04 = /tmp/tmp.2YVgvXOThx

## Wave-1 gate

Quoted from `75-BUMP-EVIDENCE.md`:

```
BUMP_COMMIT_SHA = 84edd348b52f1f7e95073d2b3ebcbcd36417bc15
BUMP_COMMIT_FILES = CHANGELOG.md|README.md|pyproject.toml|tests/test_changelog_page_gate.py|uv.lock
```

Quoted from `75-CHANGELOG-EVIDENCE.md`:

```
EXTRACT_MATCHES_SECTION = yes
```

```
$ git merge-base --is-ancestor 84edd348b52f1f7e95073d2b3ebcbcd36417bc15 HEAD; echo "exit:$?"
exit:0

$ sed -n 7p pyproject.toml
version = "0.9.6"
```

Both hold — the bump commit is an ancestor of this worktree's HEAD and `pyproject.toml` line 7
reads the bumped version, so every measurement below is taken on the bumped tree.

## Lint trio

```
$ uv run ruff check .
All checks passed!
```

RUFF_EXIT = 0

```
$ uv run black --check .
All done! ✨ 🍰 ✨
358 files would be left unchanged.
```

BLACK_EXIT = 0

```
$ uv run mypy typsphinx/
Success: no issues found in 9 source files
```

MYPY_EXIT = 0

Lint is the gate this project has seen fail only in CI; run here first, on the bumped tip.

## Full pytest

Plain run:

```
$ uv run pytest -rs -p no:cacheprovider
...
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1569 passed, 1 skipped in 118.51s (0:01:58) ==================
exit:0
```

C-locale run (matching CI's English locale):

```
$ LANG=C LC_ALL=C uv run pytest -rs -p no:cacheprovider
...
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1569 passed, 1 skipped in 115.31s (0:01:55) ==================
exit:0
```

Both runs' full logs are saved at `$S/p7504_pytest.txt` and `$S/p7504_pytest-c.txt`. The only
`SKIPPED` line in either run is `tests/test_corpus_gate.py:530`, an env-gated measurement test
unrelated to the changelog page gate — zero `SKIPPED` lines name
`tests/test_changelog_page_gate.py` in either run.

These numbers are recorded, not compared with the main checkout's — this worktree's interpreter
(uv-managed CPython 3.14) may differ from the main checkout's.

FULL_PYTEST_EXIT = 0
FULL_PYTEST_C_EXIT = 0
FULL_PYTEST_PASSED = 1569
FULL_PYTEST_C_PASSED = 1569
FULL_PYTEST_FAILED = 0
FULL_PYTEST_C_FAILED = 0
FULL_PYTEST_ERRORS = 0
CHANGELOG_GATE_SKIPS = 0

## @preview invariant

```
$ uv run pytest tests/test_preview_version_sync.py -v -p no:cacheprovider
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]
============================== 3 passed in 0.02s ===============================
```

PREVIEW_SYNC_EXIT = 0

```
$ grep -ho '@preview/[a-z-]*:' typsphinx/templates/base.typ | sort -u | wc -l
4
```

PREVIEW_PACKAGE_COUNT = 4

```
$ git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b HEAD -- typsphinx/templates typsphinx/writer.py typsphinx/template_engine.py
(empty)
```

The three `@preview` sync surfaces are untouched across the whole milestone.

Every exit above is 0 — no HALT is needed for this task.

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Plan: 04*
