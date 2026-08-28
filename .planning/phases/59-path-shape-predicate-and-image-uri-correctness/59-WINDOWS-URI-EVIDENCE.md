# Phase 59 — Windows URI Evidence

This file accumulates the real, recorded runs that prove Phase 59's product changes are neither a
regression nor a tautology. Every command output below is pasted verbatim from a live run in this
worktree; nothing is reconstructed, paraphrased, or asserted from memory.

## Phase base SHA

`git rev-parse HEAD` — this worktree's HEAD before any edit to `typsphinx/builder.py`:

```
PHASE_BASE_SHA=ec6bd3a4714a578379ee45e02295abc31fdd8fe3
```

## PATH-01

### RED (pre-fix, direct call)

Recorded at `PHASE_BASE_SHA` (`ec6bd3a4714a578379ee45e02295abc31fdd8fe3`), before any edit to
`typsphinx/builder.py`. Command:

```
uv run pytest tests/test_path_shape_predicate_gate.py -k escapes_outdir_direct
```

Whole output verbatim (run without `-x` to capture both failures in one transcript; the plan's own
`-x`-suffixed verify command also exits non-zero on this tree, stopping at the first of the two):

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a370176102829d43d/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a370176102829d43d
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 2 items

tests/test_path_shape_predicate_gate.py::TestEscapesOutdirDirectCall::test_escapes_outdir_direct_driveless_absolute_is_true FAILED [ 50%]
tests/test_path_shape_predicate_gate.py::TestEscapesOutdirDirectCall::test_escapes_outdir_direct_unc_is_true FAILED [100%]

=================================== FAILURES ===================================
_ TestEscapesOutdirDirectCall.test_escapes_outdir_direct_driveless_absolute_is_true _

self = <test_path_shape_predicate_gate.TestEscapesOutdirDirectCall object at 0x79f63fb55d10>

    def test_escapes_outdir_direct_driveless_absolute_is_true(self):
        """A driveless-absolute Windows stem -- one leading backslash, no
        drive letter -- must be classified as escaping outdir."""
>       assert _escapes_outdir(r"\manuals\guide") is True
E       AssertionError: assert False is True
E        +  where False = _escapes_outdir('\\manuals\\guide')

tests/test_path_shape_predicate_gate.py:29: AssertionError
______ TestEscapesOutdirDirectCall.test_escapes_outdir_direct_unc_is_true ______

self = <test_path_shape_predicate_gate.TestEscapesOutdirDirectCall object at 0x79f63fb56350>

    def test_escapes_outdir_direct_unc_is_true(self):
        """A UNC-shaped Windows stem -- two leading backslashes, a server
        name, a share name -- must be classified as escaping outdir."""
>       assert _escapes_outdir(r"\\srv\share\g") is True
E       AssertionError: assert False is True
E        +  where False = _escapes_outdir('\\\\srv\\share\\g')

tests/test_path_shape_predicate_gate.py:34: AssertionError
=========================== short test summary info ============================
FAILED tests/test_path_shape_predicate_gate.py::TestEscapesOutdirDirectCall::test_escapes_outdir_direct_driveless_absolute_is_true
FAILED tests/test_path_shape_predicate_gate.py::TestEscapesOutdirDirectCall::test_escapes_outdir_direct_unc_is_true
============================== 2 failed in 0.03s ===============================
```

`2 failed`, zero skipped. Both failures are `assert False is True` for the two shapes PATH-01
names: `_escapes_outdir(r"\manuals\guide")` and `_escapes_outdir(r"\\srv\share\g")` both return
`False` on the unfixed tree. `typsphinx/builder.py` is untouched at this point — confirmed by
`git diff --stat -- typsphinx/builder.py` below.

```
$ git diff --stat -- typsphinx/builder.py
(empty)
```

(filled further by plan 59-01 task 3: the through-call-site characterization pin)

## IMG-04 / IMG-06

(filled by plan 59-02)

## IMG-05

(filled by plan 59-03)

## IMG-07 four-combination table

(filled by plan 59-04)

## SC#5 acceptance

(filled by plan 59-05)
