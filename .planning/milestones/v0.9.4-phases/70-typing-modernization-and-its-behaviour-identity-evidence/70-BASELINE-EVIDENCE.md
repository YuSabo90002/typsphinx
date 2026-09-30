# Phase 70 — Pre-conversion Baseline

BASE_70_02 = 697a113221a8a267d7e8c6dd1f2b95672f9454d2
PHASE_BASE_SHA = 697a113221a8a267d7e8c6dd1f2b95672f9454d2
SCRATCH_70_02 = /tmp/tmp.gV17Fsgks8

## Head check

Fresh measurements at the start of this plan's execution, in this worktree.

```
$ date -u +%FT%TZ
2026-09-13T04:25:04Z
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aaedef104ece8dc10
$ test -f .git; echo "exit:$?"
exit:0
$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
$ git diff --name-only main HEAD -- . ':(exclude).planning'
(empty)
```

The last command's empty output confirms the worktree tree outside `.planning/` is identical to
`main`'s tip — this baseline is measured on the untouched pre-conversion code.

## Provisioning

Ran `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`.

```
Using CPython 3.13.13 interpreter at: /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin/python3.13
Creating virtual environment at: .venv
Resolved 91 packages in 0.61ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-aaedef104ece8dc10
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-aaedef104ece8dc10
Prepared 1 package in 407ms
Installed 90 packages in 61ms
```
Provisioning exit: 0. 90 packages installed, including `mypy==2.3.1`, `ruff==0.16.6`,
`myst-parser==5.1.0` (docs extra present), `pytest==9.1.1`.

`.venv/pyvenv.cfg`:
```
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
implementation = CPython
uv = 0.11.25
version_info = 3.13.13
include-system-site-packages = false
prompt = typsphinx
```

VENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
VENV_VERSION_INFO = 3.13.13

`VENV_VERSION_INFO` is `3.13.13` — no HALT needed.

## Ruff census

LOCK_RUFF_VERSION = 0.16.6
(from `uv.lock`: `name = "ruff"` / `version = "0.16.6"`)

RUFF_VERSION_BASE = ruff 0.16.6
(from `uv run ruff --version 2>/dev/null`)

`RUFF_VERSION_BASE` equals `ruff ` followed by `LOCK_RUFF_VERSION` — confirmed.

Ran `uv run ruff check . --select UP006,UP035 --output-format=concise > "$S/ruff-base.txt"; echo "exit:$?"`:
```
exit:1
```
Exit 1 as expected — findings exist. The CLI `--select` overrides the config's
`[tool.ruff.lint] ignore` entries for `UP006`/`UP035` (`pyproject.toml:128-129`).

From the lines matching `: UP0(06|35) ` in `ruff-base.txt` (115 total lines in the file, including
the trailing `Found 113 errors.` / `[*] 94 fixable...` summary lines, which do not match the
pattern):

UP_TOTAL_BASE = 113
UP006_BASE = 93
UP035_BASE = 20
UP_FILE_COUNT_BASE = 10

93 + 20 = 113 = UP_TOTAL_BASE. Confirmed non-zero.

Per-file breakdown (`LC_ALL=C sort | uniq -c` over the distinct-file cut of the matching lines):

~~~text up-files
      2 tests/conftest.py
      6 tests/test_bundle_layout_sweep_gate.py
      4 tests/test_include_edge_derivation_unit.py
      9 tests/test_include_ledger_removal_gate.py
      2 typsphinx/__init__.py
     30 typsphinx/builder.py
     12 typsphinx/template_engine.py
      4 typsphinx/template_registry.py
     42 typsphinx/translator.py
      2 typsphinx/writer.py
~~~

`uv run ruff check . --select UP006,UP035 --statistics` (quoted verbatim):
```
93	UP006	[*] non-pep585-annotation
20	UP035	[-] deprecated-import
Found 113 errors.
[*] 94 fixable with the `--fix` option.
```
93 + 20 = 113 = UP_TOTAL_BASE. Confirmed.

The distinct file set from the census (`LC_ALL=C sort -u`):
```
tests/conftest.py
tests/test_bundle_layout_sweep_gate.py
tests/test_include_edge_derivation_unit.py
tests/test_include_ledger_removal_gate.py
typsphinx/__init__.py
typsphinx/builder.py
typsphinx/template_engine.py
typsphinx/template_registry.py
typsphinx/translator.py
typsphinx/writer.py
```
This is exactly the ten files the conversion plans own.

UP_FILES_MATCH_PLAN = YES

## SC#2 base counts

Over `git grep` at `PHASE_BASE_SHA` (`697a113221a8a267d7e8c6dd1f2b95672f9454d2`), pathspecs
`'typsphinx/*.py' 'tests/*.py'`:

```
$ git grep -hoE 'from __future__ import annotations' 697a113221a8a267d7e8c6dd1f2b95672f9454d2 -- 'typsphinx/*.py' 'tests/*.py' | wc -l
0
$ git grep -hoE 'Optional\[' 697a113221a8a267d7e8c6dd1f2b95672f9454d2 -- 'typsphinx/*.py' 'tests/*.py' | wc -l
0
$ git grep -hoE 'Union\[' 697a113221a8a267d7e8c6dd1f2b95672f9454d2 -- 'typsphinx/*.py' 'tests/*.py' | wc -l
0
$ git grep -hoE '[|] None' 697a113221a8a267d7e8c6dd1f2b95672f9454d2 -- 'typsphinx/*.py' 'tests/*.py' | wc -l
82
```

FUTURE_ANNOTATIONS_BASE = 0
OPTIONAL_BASE = 0
UNION_BASE = 0
PIPE_NONE_BASE = 82

## mypy before (leg e)

MYPY_VERSION_BASE = mypy 2.3.1 (compiled: yes)
(from `uv run mypy --version 2>/dev/null`)

Ran `uv run mypy typsphinx/ 2>/dev/null > "$S/mypy-before.out"; echo "exit:$?"`:
```
exit:0
```

MYPY_EXIT_BEFORE = 0
MYPY_STDOUT_SHA256_BEFORE = 46984ca20bf69f7b14ec1fd9bd82101d56a4e109e68f016fd2a04f22481b09b3
(first field of `sha256sum < "$S/mypy-before.out"`; stdout only, stderr excluded per Pitfall 7 —
`uv run`'s own sync/rebuild chatter goes to stderr and must not be captured into the comparison)

~~~text mypy-before
Success: no issues found in 9 source files
~~~

## pytest before (leg b)

Ran `LC_ALL=C uv run pytest --collect-only -q -p no:cacheprovider 2>/dev/null | grep -oE '[0-9]+ tests? collected' | grep -oE '^[0-9]+'`
(the first grep is unanchored, because the summary line is wrapped in `=`):

PYTEST_COLLECTED_BEFORE = 1548

Ran `LC_ALL=C uv run pytest -q -rs -p no:cacheprovider > "$S/pytest-before.out" 2>&1; echo "exit:$?"`:
```
exit:0
```

PYTEST_EXIT_BEFORE = 0

Summary line (`tail -n 1 "$S/pytest-before.out"`):
```
================= 1547 passed, 1 skipped in 131.38s (0:02:11) ==================
```

PYTEST_RESULT_BEFORE = 1547 passed 1 skipped
(from `tail -n 1 "$S/pytest-before.out" | grep -oE '[0-9]+ (passed|failed|skipped|errors?|xfailed|xpassed)' | paste -sd' '`)

1547 + 1 = 1548 = PYTEST_COLLECTED_BEFORE. Confirmed.

PYTEST_WARNINGS_BEFORE = 0
(no "warnings summary" section in the output; informational only)

Skip reasons (`-rs` short summary, every `SKIPPED` line):

~~~text pytest-skips-before
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
~~~
