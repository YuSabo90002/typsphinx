# Phase 70 — After-side Runtime Evidence

BASE_70_11 = 44c43e345f8d5916486e5b7c2790bcb16c58f9d0
SCRATCH_70_11 = /tmp/tmp.0myAv8FjS1

## Precondition checks

Task 1 precondition: `70-FLIP-EVIDENCE.md` exists at HEAD with no HALT heading, and
`pyproject.toml`'s `[tool.ruff.lint]` section names neither UP006 nor UP035.

```
$ test -f .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-FLIP-EVIDENCE.md; echo "exit:$?"
exit:0
$ grep -c '^## HALT' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-FLIP-EVIDENCE.md
0
$ sed -n '/^\[tool\.ruff\.lint\]/,/^\[/p' pyproject.toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "T20"]
ignore = [
    "E501",   # Line too long (handled by black)
    "T201",   # print found (used in tests for debugging)
    "B017",   # asserting blind exception in tests
    "UP028",  # yield from (minor optimization)
    "N802",   # Function naming (docutils visitor pattern uses PascalCase)
    "A001",   # Shadowing builtins (copyright in conf.py is Sphinx convention)
    "F841",   # Unused variable (acceptable in tests and mocks)
]

[tool.mypy]
```
Neither `UP006` nor `UP035` appears in `ignore`. Precondition met — proceeding.

## Provisioning

Ran `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`
in this worktree (`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a099ef5f3ff5bdb00`). Exit 0.

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

Both equal 70-02's `70-BASELINE-EVIDENCE.md` keys (`VENV_HOME` and `VENV_VERSION_INFO`) exactly —
confirmed by direct comparison.

## Leg (b) — pytest after

Ran `LC_ALL=C uv run pytest --collect-only -q -p no:cacheprovider 2>/dev/null | grep -oE '[0-9]+ tests? collected' | grep -oE '^[0-9]+'`
(the unanchored form, per 70-02's extraction — the summary line is `=`-decorated):

PYTEST_COLLECTED_AFTER = 1548

Equals `PYTEST_COLLECTED_BEFORE = 1548` from `70-BASELINE-EVIDENCE.md`. Confirmed.

Ran `LC_ALL=C uv run pytest -q -rs -p no:cacheprovider > "$S/pytest-after.out" 2>&1; echo "exit:$?"`:
```
exit:0
```

Summary line (`tail -n 1 "$S/pytest-after.out"`):
```
================= 1547 passed, 1 skipped in 127.63s (0:02:07) ==================
```

PYTEST_RESULT_AFTER = 1547 passed 1 skipped
(from `tail -n 1 "$S/pytest-after.out" | grep -oE '[0-9]+ (passed|failed|skipped|errors?|xfailed|xpassed)' | paste -sd' '`)

Equals `PYTEST_RESULT_BEFORE = 1547 passed 1 skipped`. Confirmed.

PYTEST_WARNINGS_AFTER = 0
(no "warnings summary" section in the output; informational only, matches
`PYTEST_WARNINGS_BEFORE = 0`)

Skip reasons (`-rs` short summary, every `SKIPPED` line):

~~~text pytest-skips-after
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
~~~

Compared against `pytest-skips-before` after stripping `:<line>:` numbers with
`sed -E 's/:[0-9]+:/:/'` and sorting both under `LC_ALL=C sort`:

```
$ diff skips-before-stripped.txt skips-after-stripped.txt
(empty — no differences)
```

SKIP_REASONS_MATCH = YES

Both `PYTEST_COLLECTED_AFTER` and `PYTEST_RESULT_AFTER` equal their base keys, from a run that
exited 0, and the skip reasons match after stripping line numbers.

LEG_B_VERDICT = MET
