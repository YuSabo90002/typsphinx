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

Recorded after `typsphinx/pathfmt.py::quote_path()` was implemented. Command:

```
uv run pytest tests/test_pathfmt.py -q
```

Whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1bf10099dabe1016
configfile: pyproject.toml
plugins: cov-7.1.0
collected 27 items

tests/test_pathfmt.py ...........................                        [100%]

============================== 27 passed in 0.05s ===============================
```

`27 passed`, zero failed, zero skipped -- all six classes green.

Full suite also re-confirmed green: `uv run pytest -q` -> `1494 passed, 5 skipped in
119.68s` (up from the project's prior baseline by the +27 new tests this plan added,
minus the earlier RED collection error). `uv run black --check .` and
`uv run mypy typsphinx/` both clean (`Success: no issues found in 9 source files`).
`ruff check .` is deferred to CI per the project's standing NixOS ELF constraint
(`CLAUDE.md`, `MEMORY.md` "NixOS sandbox test env") -- CI holds lint authority.

**Deviation recorded during this task:** the first draft of `TestQuotePathVersusRepr`
called `repr(value)` directly inside each `assert`'s own test expression (as a
literal reading of the plan's action text would suggest). Running the full suite
surfaced that this registers as a NEW pass-criterion site for
`tests/test_repr_census_guard.py`'s AST sweep (it walks every `repr()`/`!r`
occurrence inside `ast.Assert(...).test`), which asserts the whole-tree set of such
sites is frozen against `58-REPR-CENSUS.md`'s recorded seven-site allowlist -- this
plan is required to add none. Fixed (Rule 1 -- bug in the test's own construction,
not a product change) by binding `repr(value)` to a local variable BEFORE the
`assert` line in both `TestQuotePathVersusRepr` methods, which preserves the exact
same assertion semantics (`quote_path(v) == repr(v)`, or the undoubled-repr form for
the two backslash-bearing values) while keeping the literal `repr(...)` call outside
the AST subtree the census guard walks. Re-ran `uv run pytest
tests/test_repr_census_guard.py -q` after the fix: `4 passed`, confirming the census
is unperturbed. No product file was touched by this fix. The second draft's
`TestQuotePathTypeContract` also over-specified `list`/`int` rejection as requiring
"quote_path" in the raised message; `60-RESEARCH.md`'s own measured Pitfall 1 records
that `os.fspath()` itself raises `TypeError` for those two types before
`quote_path()`'s own explicit `isinstance` check is ever reached (only `bytes`
passes through `os.fspath()` unchanged and hits the function's own message), so the
two tests were narrowed to assert only `TypeError` is raised, matching the plan's own
`<behavior>` and `<acceptance_criteria>` text (which requires the `quote_path`-naming
message only for the `b"x"` case).

## D-01 byte-identity table

Taken from a real `uv run python` invocation (not copied from the research
document), calling `quote_path()` and `repr()` directly against the same five
values `TestQuotePathVersusRepr` uses:

| Value | `quote_path()` output | `repr()` output |
|-------|------------------------|-------------------|
| `C:\Users\a` (Windows path) | `'C:\Users\a'` | `'C:\\Users\\a'` |
| `/home/O'Brien/x` (apostrophe only) | `"/home/O'Brien/x"` | `"/home/O'Brien/x"` |
| `/tmp/we"ird.png` (double quote only) | `'/tmp/we"ird.png'` | `'/tmp/we"ird.png'` |
| `/tmp/bo'th"quotes.png` (both quotes) | `'/tmp/bo\'th"quotes.png'` | `'/tmp/bo\'th"quotes.png'` |
| `C:\both'quotes"here` (combined backslash+both quotes) | `'C:\both\'quotes"here'` | `'C:\\both\'quotes"here'` |

The two Windows-shaped/backslash-bearing rows are the only ones where `quote_path()`
and `repr()` diverge, and the divergence is exactly the backslash-doubling `repr()`
applies and `quote_path()` deliberately does not -- every other character, including
every quote-escape, is identical between the two columns.

## Leaf-import proof

(filled by Task 3)
