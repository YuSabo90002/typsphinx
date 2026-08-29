# Phase 60 Plan 01 — MSG-02 Evidence

## Phase base SHA

`git rev-parse HEAD` — this worktree's HEAD before any file was created for this plan:

```
PHASE_BASE_SHA=31441d09bd8168f1bcc5170749f6d9646a1d5151
```

## MSG-02 RED

Recorded at `PHASE_BASE_SHA` (`31441d09bd8168f1bcc5170749f6d9646a1d5151`), before
`typsphinx/pathfmt.py` was created. Command:

```
uv run pytest tests/test_pathfmt.py -x
```

Whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1bf10099dabe1016/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1bf10099dabe1016
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 0 items / 1 error

==================================== ERRORS ====================================
____________________ ERROR collecting tests/test_pathfmt.py ____________________
ImportError while importing test module '/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1bf10099dabe1016/tests/test_pathfmt.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_pathfmt.py:36: in <module>
    from typsphinx.pathfmt import quote_path
E   ModuleNotFoundError: No module named 'typsphinx.pathfmt'
=========================== short test summary info ============================
ERROR tests/test_pathfmt.py
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.07s ===============================
```

Exit code: `2` (non-zero). `typsphinx/pathfmt.py` does not exist at this point --
`test ! -e typsphinx/pathfmt.py` succeeds, and `git status --porcelain typsphinx/`
is empty (no product file touched by this task). This is MSG-02's legitimate RED
against the unfixed tree: a collection error (module absent), not a test-logic
failure -- the correct RED shape for a wave-1 tracer slice that gates a module
which does not exist yet.

## MSG-02 GREEN

(filled by Task 2)

## D-01 byte-identity table

(filled by Task 2)

## Leaf-import proof

(filled by Task 3)
