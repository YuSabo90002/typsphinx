# Phase 72 — Tip Gates Evidence (tox runs, local quartet, scope)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-13T13:46:13Z
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2c90edb1c4ea7de0
$ test -f .git; echo "exit:$?"
exit:0
$ grep -q typsphinx-fhs-run "$(command -v uv)"; echo matched
matched
```

Provisioning command:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
```
Ran to completion; final resolved lines included `typsphinx==0.9.2 (from
file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2c90edb1c4ea7de0)`, `sphinx==9.1.0`,
`furo==2025.12.19` (docs extra), `tox==4.61.4`, `uv==0.12.13`, `myst-parser==5.1.0`. Exit 0, no
error lines. 90 packages installed.

PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_INFO = 3.13.13

```
$ printenv SPHINX_LANGUAGE READTHEDOCS_LANGUAGE; echo "exit:$?"
exit:1
```
Neither `SPHINX_LANGUAGE` nor `READTHEDOCS_LANGUAGE` is set — printed nothing but `exit:1`, as
required. No HALT.

Before any commit:
```
$ git rev-parse HEAD
4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5
$ mktemp -d
/tmp/tmp.QpwXKEqZct
```

BASE_72_05 = 4b1c822cc83a4779b5b8cc79b38b887dfaf5a1c5
SCRATCH_72_05 = /tmp/tmp.QpwXKEqZct

```
$ grep -nx '\[testenv:linkcheck\]' tox.ini
92:[testenv:linkcheck]
$ grep -c 'tox -e linkcheck' docs/source/contributing.rst
1
```
The tip carries QUA-13 (`[testenv:linkcheck]` in `tox.ini`, landed in wave 1 / 72-02) and DOC-24
(`docs/source/contributing.rst` names `tox -e linkcheck` once, landed in wave 2 / 72-03).

## Tip linkcheck run 1

```
$ rm -rf docs/_build/linkcheck
$ test ! -e docs/_build/linkcheck; echo "exit:$?"
exit:0
$ uv run tox -e linkcheck > "$S/p7205_lc1.log" 2>&1; echo "exit:$?"
exit:0
```

TIP_LINKCHECK_RUN_1_EXIT = 0

`docs/_build/linkcheck/output.json` copied to `$S/p7205_lc1_output.json` (95 lines).

Census, via `uv run python -c` over the JSON lines:

TIP_LINKCHECK_RUN_1_TOTAL = 95
TIP_LINKCHECK_RUN_1_WORKING = 95
TIP_LINKCHECK_RUN_1_UNIQUE_URIS = 95
TIP_LINKCHECK_RUN_1_STATUS_CENSUS = working:95

Non-`working` rows, sorted by `uri`:
```
no non-working rows
```

Run 1 meets SC#1 on its own: exit 0, total 95 equals working 95, at least 1 row. No non-working
row exists, so there is nothing to classify under D-01 (transient) or D-03 (non-transient). No
re-run, and no `docs/source/conf.py` timing key (D-02), are needed.

TIP_LINKCHECK_RUNS = 1
TIP_LINKCHECK_TOTAL = 95
TIP_LINKCHECK_WORKING = 95
TIP_LINKCHECK_VERDICT = PASS

`docs/_build/linkcheck/output.json` in this worktree is run 1's output, the passing run's output.
`docs/source/conf.py` carries 0 `linkcheck_*` keys — no ignore-style key, no timing key.

## Tip docs-html run

Run after linkcheck, so any D-02 key (none fired here) would already be in the tree.

```
$ rm -rf docs/_build/html
$ test ! -e docs/_build/html; echo "exit:$?"
exit:0
$ LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-html > "$S/p7205_html.log" 2>&1; echo "exit:$?"
exit:0
```

```
$ LANG=C LC_ALL=C grep -c 'document is referenced in multiple toctrees' "$S/p7205_html.log" || true
0
```
TOX_HTML_MULTI_TOCTREE = 0

```
$ LANG=C LC_ALL=C grep -E '^build succeeded' "$S/p7205_html.log" || true
build succeeded, 3 warnings.
```
TOX_HTML_WARNINGS = 3

The English `build succeeded` line is present, `TOX_HTML_MULTI_TOCTREE = 0`, and
`TOX_HTML_WARNINGS = 3` equals `BASE_WARNING_COUNT = 3` (72-BASE-EVIDENCE.md). This run
corroborates 72-04's base/tip pair from the real tox environment, and 72-01's base build is its
positive control (`BASE_MULTI_TOCTREE_COUNT = 5`, `BASE_WARNING_COUNT = 3`). No HALT.

Both documentation tox environments have run for real on the final tree and pass.

## Local gate quartet

Interpreter recorded beside the counts (unchanged from provisioning):
```
$ sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg
/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
3.13.13
```

```
$ uv run ruff check .
(no output)
$ echo "exit:$?"
exit:0
```
RUFF_EXIT = 0

```
$ uv run black --check .
(no output)
$ echo "exit:$?"
exit:0
```
BLACK_EXIT = 0

```
$ uv run mypy typsphinx/
(no output)
$ echo "exit:$?"
exit:0
```
MYPY_EXIT = 0

```
$ uv run pytest -q -p no:cacheprovider > "$S/p7205_pytest.log" 2>&1; echo "exit:$?"
exit:0
```
PYTEST_EXIT = 0

Tail of `$S/p7205_pytest.log`:
```
tests/test_xref_whole_document_guard_render_gate.py ........                 [100%]

================= 1547 passed, 1 skipped in 129.75s (0:02:09) ==================
```

PYTEST_PASSED = 1547
PYTEST_SKIPPED = 1
PYTEST_FAILED = 0

```
$ uv run pytest -q -p no:cacheprovider tests/test_changelog_page_gate.py
============================== 6 passed in 4.00s ===============================
```
CHANGELOG_GATE_SKIPPED = 0
Docs extra present: 6 passed, 0 skipped.

All four gate exits are 0.

## Scope fence

```
$ git diff --stat 34c77f59266acb028c8934ff56715dd4454bdfe8 HEAD -- typsphinx/ .github/workflows/
(empty)
```
Empty — SC#5's scope constraint holds.

```
$ git diff --stat 098a8ff64cf008822eef9dc69f75102ded3f7bc1 HEAD -- typsphinx/
(empty)
```
Empty — constraint 2 (milestone-base `typsphinx/` scope) holds.

```
$ git diff --name-only 34c77f59266acb028c8934ff56715dd4454bdfe8 HEAD -- pyproject.toml uv.lock flake.nix tests/ .github/
(empty)
```
Empty — packaging, lockfile, flake, tests and workflows all unchanged since the phase base.

```
$ git diff --name-only 34c77f59266acb028c8934ff56715dd4454bdfe8 HEAD -- . ':(exclude).planning' | sort | tr '\n' ' '
CLAUDE.md README.md docs/source/contributing.rst docs/source/index.rst tox.ini
```
PRODUCT_DIFF_FILES = CLAUDE.md README.md docs/source/contributing.rst docs/source/index.rst tox.ini

Exactly the five edited files named by the plan. `docs/source/conf.py` is not present — no D-02
key fired in 72-02 (`CONF_LINKCHECK_KEYS = 0`) or in this plan's Task 1 (no timing key was added).

## SC#5 local verdict

All four gate exits (`RUFF_EXIT`, `BLACK_EXIT`, `MYPY_EXIT`, `PYTEST_EXIT`) are 0, `PYTEST_FAILED = 0`,
`CHANGELOG_GATE_SKIPPED = 0`, and every scope check above is empty/matching.

SC5_LOCAL_VERDICT = MET
