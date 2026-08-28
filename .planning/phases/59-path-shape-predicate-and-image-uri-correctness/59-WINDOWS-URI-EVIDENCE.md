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

### Characterization: byte-identical at both call sites

D-09/D-10: `TestEscapesOutdirCallSiteCharacterization` runs THROUGH both production call sites
(`_resolve_target_stem()` and `_track_image()`), parametrized over the five documented shapes
(driveless-absolute, unc, drive-qualified, posix-absolute, ordinary-relative). Command, run
identically against both trees:

```
uv run pytest tests/test_path_shape_predicate_gate.py -k characterization -q
```

**Pre-fix tree.** `git checkout ec6bd3a4714a578379ee45e02295abc31fdd8fe3 -- typsphinx/builder.py`
(restoring the pre-fix `_escapes_outdir()` while keeping the new tests), then the command above —
whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a370176102829d43d
configfile: pyproject.toml
plugins: cov-7.1.0
collected 14 items / 2 deselected / 12 selected

tests/test_path_shape_predicate_gate.py ............                     [100%]

======================= 12 passed, 2 deselected in 0.27s =======================
```

**Post-fix tree.** `git checkout HEAD -- typsphinx/builder.py` (restoring the fixed predicate;
`git diff --stat -- typsphinx/builder.py` confirmed empty immediately after), then the identical
command — whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a370176102829d43d
configfile: pyproject.toml
plugins: cov-7.1.0
collected 14 items / 2 deselected / 12 selected

tests/test_path_shape_predicate_gate.py ............                     [100%]

======================= 12 passed, 2 deselected in 0.21s =======================
```

**The two runs are byte-identical** in every substantive respect: same collection count (14
collected / 2 deselected / 12 selected), same per-test dot pattern (`............`, all 12 pass),
same summary shape (`12 passed, 2 deselected`). The only differing bytes are the wall-clock timing
figures (`0.27s` vs `0.21s`), which is expected run-to-run non-determinism, not a behavioral
difference — no test result (pass/fail) differs between the two trees. This proves `_resolve_target_stem()`
and `_track_image()` classify all five documented shapes identically before and after PATH-01's
fix, exactly as `_RESOLVE_TARGET_STEM_EXPECTED`'s comment and the call sites' own pre-normalization
(`_resolve_target_stem`) / always-carries-`".."` (`_track_image`'s `relpath()` result) predict.

`git status --porcelain typsphinx/builder.py` after the restore, confirming the temporary checkout
left no trace:

```
(empty)
```

## IMG-04 / IMG-06

(filled by plan 59-02)

## IMG-05

(filled by plan 59-03)

## IMG-07 four-combination table

(filled by plan 59-04)

## SC#5 acceptance

(filled by plan 59-05)
