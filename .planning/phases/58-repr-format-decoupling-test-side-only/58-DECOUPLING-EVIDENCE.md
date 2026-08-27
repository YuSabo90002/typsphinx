# Phase 58: `repr()`-Format Decoupling — Decoupling Evidence

This file accumulates the real, recorded runs that prove Phase 58's rewrite (MSG-01) is neither a
regression nor a tautology. Every command output below is pasted verbatim from a live run in this
worktree; nothing is reconstructed, paraphrased, or asserted from memory.

## SC#2 (a) — pre-rewrite green baseline (both target tests)

Recorded BEFORE any edit to `tests/test_out02_escape_target_gate.py` or `tests/_path_naming.py`
(which does not exist yet). This is the only point in the plan where this baseline can be captured —
after Step 3 rewrites the assertion, the tree is no longer the pre-rewrite tree.

`git rev-parse HEAD` — phase-base SHA (this worktree's HEAD before any edit):

```
3b0f2b93f924f28eba94a0e92ea76996e9d743ad
```

`git merge-base HEAD gsd/v0.9.1-windows-path-correctness` — merge-base against the milestone branch:

```
3b0f2b93f924f28eba94a0e92ea76996e9d743ad
```

`uv run python -c "import typst; print(typst.__file__)"` — proof that `TYPST_AVAILABLE` is true in
this venv, so a SKIP cannot masquerade as a pass:

```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4dccbfe29904a32f/.venv/lib/python3.13/site-packages/typst/__init__.py
```

`uv run pytest tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -q`
— whole captured output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4dccbfe29904a32f
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_out02_escape_target_gate.py ...                               [ 75%]
tests/test_builder.py .                                                  [100%]

============================== 4 passed in 1.18s ===============================
```

`4 passed`, zero skips. The venv is correctly provisioned and both target tests are green on the
pre-rewrite tree.

## SC#1/SC#2 (b) — post-rewrite green: escape-target gate

Recorded AFTER `tests/_path_naming.py` was created and `tests/test_out02_escape_target_gate.py`'s
pass criterion was rewritten onto it (D-01/D-02/D-03), including a mid-task correction: the real
product emits the identical warning line 3 times per build (not once — `_resolve_target_stem()` is
invoked once via `get_target_uri()`'s cross-reference resolution and again during wrapper-output-path
resolution at write time), so the line-selection step de-duplicates before asserting exactly one
DISTINCT line, preserving D-02's actual guarantee (a raw path leaking from an unrelated source would
still produce a second, DIFFERENT line and fail loudly) without depending on how many internal call
sites happen to log the same message.

`uv run pytest tests/test_out02_escape_target_gate.py -q` — whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4dccbfe29904a32f
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items

tests/test_out02_escape_target_gate.py ...                               [100%]

============================== 3 passed in 0.65s ===============================
```

`3 passed`, zero skips.

The AST pass-criterion count for this file, run as
`uv run python -c "import ast,pathlib;t=ast.parse(pathlib.Path('tests/test_out02_escape_target_gate.py').read_text(encoding='utf-8'));print(sum(1 for a in ast.walk(t) if isinstance(a,ast.Assert) for s in ast.walk(a.test) if (isinstance(s,ast.Call) and isinstance(s.func,ast.Name) and s.func.id=='repr') or (isinstance(s,ast.FormattedValue) and s.conversion==114)))"`:

```
0
```

Measured `1` on the pre-rewrite tree (the `assert repr(target) in combined_output` line); this
number moving from 1 to 0 IS SC#1 for this file.

`git status --porcelain typsphinx/` — expected empty (SC#4 — `typsphinx/` untouched by this task):

```
(empty)
```

`uv run black --check tests/_path_naming.py tests/test_out02_escape_target_gate.py`:

```
All done! ✨ 🍰 ✨
2 files would be left unchanged.
```

Exit code 0.

`uv run ruff check tests/_path_naming.py tests/test_out02_escape_target_gate.py` failed to execute in
this worktree's `.venv` on this NixOS host (see sub-heading below); the `nix-shell -p ruff` retry
succeeded.

### ruff via `nix-shell -p ruff` fallback

The worktree venv's `ruff` binary is a generic-linux ELF that cannot exec on NixOS (dynamic-linker
stub error, not a lint failure — an environment defect, not a code RED):

```
$ uv run ruff check tests/_path_naming.py tests/test_out02_escape_target_gate.py
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```

Retry via `nix-shell -p ruff --run "ruff check tests/_path_naming.py tests/test_out02_escape_target_gate.py"`:

```
All checks passed!
```

CI, not this worktree, is the lint authority of record for these two files; the `nix-shell` retry
above is the successful route and is recorded for completeness.

## SC#2 (c) — recorded falsification: builder.py:697 (docname target warning)

D-05(b): a real, temporary edit to `typsphinx/builder.py`'s docname-target warning, dropping ONLY
the `{target!r}` interpolation while leaving the `fallback` interpolation (and its `!r` conversion)
untouched — the D-03 fallback-trap shape. Made, measured, and reverted inside this single task; the
edit never survived to a commit.

**Step 1 — the falsifying edit.** `git diff -- typsphinx/builder.py` while the edit was in place:

```diff
diff --git a/typsphinx/builder.py b/typsphinx/builder.py
index a967a58c..ea829349 100644
--- a/typsphinx/builder.py
+++ b/typsphinx/builder.py
@@ -694,7 +694,7 @@ class TypstBuilder(Builder):
                     return docname
                 logger.warning(
                     "a path is not supported in a typst_documents target "
-                    f"name: {target!r} -- using {fallback!r} instead"
+                    f"name: -- using {fallback!r} instead"
                 )
                 stem = fallback
             elif "/" in stem and not posixpath.basename(stem).strip():
```

The `ESCAPE_WARNING_SUBSTRING` anchor (`"a path is not supported in a typst_documents target
name"`) survives intact across the implicit string concatenation, and the `fallback` interpolation
is left fully in place — this is exactly the D-03 trap shape: for the `drive` shape, `fallback`'s
value IS `target`'s basename, so a predicate weaker than full-value matching would stay green here.

**Step 2 — the RED.** `uv run pytest
tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof -q` —
whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4dccbfe29904a32f
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items

tests/test_out02_escape_target_gate.py FFF                               [100%]

=================================== FAILURES ===================================
_________ test_escape_shape_refused_with_containment_proof[traversal] __________

shape = 'traversal'
tmp_path = PosixPath('/tmp/pytest-of-yuta/pytest-1592/test_escape_shape_refused_with0')

    @pytest.mark.skipif(
        not TYPST_AVAILABLE,
        reason="typst-py is required for the escape-target-gate tests",
    )
    @pytest.mark.parametrize("shape", ["traversal", "absolute", "drive"])
    def test_escape_shape_refused_with_containment_proof(shape, tmp_path):
        """OUT-02: each escape shape still exits 0, warns naming the offending
        target, writes the wrapper at the basename fallback inside the build
        directory, and -- the containment proof -- every regular file under
        the build directory resolves under the resolved build directory.
    
        Marked to run on every platform (including the drive-qualified case),
        per the plan's own instruction: the drive check is a string-shape
        check, not a filesystem behaviour, so D-05's platform-independence
        principle applies to it too.
        """
        build_dir = tmp_path / "build"
        target = _target_for_shape(shape)
    
        result = _run_sphinx_build(
            ESCAPE_TARGET_GATE_FIXTURE_DIR,
            build_dir,
            "typst",
            env={"TYPSPHINX_ESCAPE_SHAPE": shape},
        )
    
        combined_output = result.stdout + result.stderr
        assert result.returncode == 0, (
            f"Expected a successful build despite the {shape!r} escape "
            f"attempt:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    
        assert ESCAPE_WARNING_SUBSTRING in combined_output, (
            f"Expected the path-guard warning naming the refused target:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        # D-02: apply the naming predicate to the extracted warning LINE, not
        # to the whole captured output -- a raw path leaking from any other
        # source (a config echo, a traceback, a path Sphinx prints) would
        # otherwise keep this test green after the path is removed from the
        # warning itself, which would make Task 2's falsification prove
        # nothing about the thing under test.
        #
        # `_resolve_target_stem()` is invoked multiple times per build for the
        # SAME docname (once via `get_target_uri()`'s cross-reference/toctree
        # resolution calls, once via the wrapper-output-path resolution during
        # writing) -- measured live this session: an unmodified single-docname
        # fixture build emits the IDENTICAL warning line 3 times, not once.
        # De-duplicating before counting keeps D-02's actual guarantee (a
        # DIFFERENT raw path leaking from an unrelated source produces a
        # DIFFERENT line and still fails loudly here) without making this
        # assertion depend on how many internal call sites happen to log the
        # same message.
        warning_lines = list(
            dict.fromkeys(
                line
                for line in combined_output.splitlines()
                if ESCAPE_WARNING_SUBSTRING in line
            )
        )
        assert len(warning_lines) == 1, (
            f"Expected exactly one DISTINCT warning line naming the refused "
            f"target (repeats of the identical line are expected and "
            f"collapsed; a second, DIFFERENT line would indicate a raw path "
            f"leaking from an unrelated source):\n{combined_output}"
        )
        # D-01/D-03: assert MEANING, not representation format -- the
        # offending target is NAMED in the warning line, whether the message
        # site quotes it with `!r`, a hardcoded `'{value}'`, or a future
        # delimiter-aware helper. `path_named_in` requires the FULL target
        # value, never a basename, so a message that only still names the
        # same-basename `fallback` field (the D-03 trap) fails this assertion.
>       assert path_named_in(target, warning_lines[0]), (
            f"Expected the warning to name the offending target {target!r} "
            f"(raw or repr()'d):\n{warning_lines[0]}"
        )
E       AssertionError: Expected the warning to name the offending target '../escape.typ' (raw or repr()'d):
E         WARNING: a path is not supported in a typst_documents target name: -- using 'escape' instead
E       assert False
E        +  where False = path_named_in('../escape.typ', "WARNING: a path is not supported in a typst_documents target name: -- using 'escape' instead")

tests/test_out02_escape_target_gate.py:167: AssertionError
__________ test_escape_shape_refused_with_containment_proof[absolute] __________

shape = 'absolute'
tmp_path = PosixPath('/tmp/pytest-of-yuta/pytest-1592/test_escape_shape_refused_with1')

    @pytest.mark.skipif(
        not TYPST_AVAILABLE,
        reason="typst-py is required for the escape-target-gate tests",
    )
    @pytest.mark.parametrize("shape", ["traversal", "absolute", "drive"])
    def test_escape_shape_refused_with_containment_proof(shape, tmp_path):
        """OUT-02: each escape shape still exits 0, warns naming the offending
        target, writes the wrapper at the basename fallback inside the build
        directory, and -- the containment proof -- every regular file under
        the build directory resolves under the resolved build directory.
    
        Marked to run on every platform (including the drive-qualified case),
        per the plan's own instruction: the drive check is a string-shape
        check, not a filesystem behaviour, so D-05's platform-independence
        principle applies to it too.
        """
        build_dir = tmp_path / "build"
        target = _target_for_shape(shape)
    
        result = _run_sphinx_build(
            ESCAPE_TARGET_GATE_FIXTURE_DIR,
            build_dir,
            "typst",
            env={"TYPSPHINX_ESCAPE_SHAPE": shape},
        )
    
        combined_output = result.stdout + result.stderr
        assert result.returncode == 0, (
            f"Expected a successful build despite the {shape!r} escape "
            f"attempt:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    
        assert ESCAPE_WARNING_SUBSTRING in combined_output, (
            f"Expected the path-guard warning naming the refused target:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        # D-02: apply the naming predicate to the extracted warning LINE, not
        # to the whole captured output -- a raw path leaking from any other
        # source (a config echo, a traceback, a path Sphinx prints) would
        # otherwise keep this test green after the path is removed from the
        # warning itself, which would make Task 2's falsification prove
        # nothing about the thing under test.
        #
        # `_resolve_target_stem()` is invoked multiple times per build for the
        # SAME docname (once via `get_target_uri()`'s cross-reference/toctree
        # resolution calls, once via the wrapper-output-path resolution during
        # writing) -- measured live this session: an unmodified single-docname
        # fixture build emits the IDENTICAL warning line 3 times, not once.
        # De-duplicating before counting keeps D-02's actual guarantee (a
        # DIFFERENT raw path leaking from an unrelated source produces a
        # DIFFERENT line and still fails loudly here) without making this
        # assertion depend on how many internal call sites happen to log the
        # same message.
        warning_lines = list(
            dict.fromkeys(
                line
                for line in combined_output.splitlines()
                if ESCAPE_WARNING_SUBSTRING in line
            )
        )
        assert len(warning_lines) == 1, (
            f"Expected exactly one DISTINCT warning line naming the refused "
            f"target (repeats of the identical line are expected and "
            f"collapsed; a second, DIFFERENT line would indicate a raw path "
            f"leaking from an unrelated source):\n{combined_output}"
        )
        # D-01/D-03: assert MEANING, not representation format -- the
        # offending target is NAMED in the warning line, whether the message
        # site quotes it with `!r`, a hardcoded `'{value}'`, or a future
        # delimiter-aware helper. `path_named_in` requires the FULL target
        # value, never a basename, so a message that only still names the
        # same-basename `fallback` field (the D-03 trap) fails this assertion.
>       assert path_named_in(target, warning_lines[0]), (
            f"Expected the warning to name the offending target {target!r} "
            f"(raw or repr()'d):\n{warning_lines[0]}"
        )
E       AssertionError: Expected the warning to name the offending target '/tmp/escape.typ' (raw or repr()'d):
E         WARNING: a path is not supported in a typst_documents target name: -- using 'escape' instead
E       assert False
E        +  where False = path_named_in('/tmp/escape.typ', "WARNING: a path is not supported in a typst_documents target name: -- using 'escape' instead")

tests/test_out02_escape_target_gate.py:167: AssertionError
___________ test_escape_shape_refused_with_containment_proof[drive] ____________

shape = 'drive'
tmp_path = PosixPath('/tmp/pytest-of-yuta/pytest-1592/test_escape_shape_refused_with2')

    @pytest.mark.skipif(
        not TYPST_AVAILABLE,
        reason="typst-py is required for the escape-target-gate tests",
    )
    @pytest.mark.parametrize("shape", ["traversal", "absolute", "drive"])
    def test_escape_shape_refused_with_containment_proof(shape, tmp_path):
        """OUT-02: each escape shape still exits 0, warns naming the offending
        target, writes the wrapper at the basename fallback inside the build
        directory, and -- the containment proof -- every regular file under
        the build directory resolves under the resolved build directory.
    
        Marked to run on every platform (including the drive-qualified case),
        per the plan's own instruction: the drive check is a string-shape
        check, not a filesystem behaviour, so D-05's platform-independence
        principle applies to it too.
        """
        build_dir = tmp_path / "build"
        target = _target_for_shape(shape)
    
        result = _run_sphinx_build(
            ESCAPE_TARGET_GATE_FIXTURE_DIR,
            build_dir,
            "typst",
            env={"TYPSPHINX_ESCAPE_SHAPE": shape},
        )
    
        combined_output = result.stdout + result.stderr
        assert result.returncode == 0, (
            f"Expected a successful build despite the {shape!r} escape "
            f"attempt:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    
        assert ESCAPE_WARNING_SUBSTRING in combined_output, (
            f"Expected the path-guard warning naming the refused target:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        # D-02: apply the naming predicate to the extracted warning LINE, not
        # to the whole captured output -- a raw path leaking from any other
        # source (a config echo, a traceback, a path Sphinx prints) would
        # otherwise keep this test green after the path is removed from the
        # warning itself, which would make Task 2's falsification prove
        # nothing about the thing under test.
        #
        # `_resolve_target_stem()` is invoked multiple times per build for the
        # SAME docname (once via `get_target_uri()`'s cross-reference/toctree
        # resolution calls, once via the wrapper-output-path resolution during
        # writing) -- measured live this session: an unmodified single-docname
        # fixture build emits the IDENTICAL warning line 3 times, not once.
        # De-duplicating before counting keeps D-02's actual guarantee (a
        # DIFFERENT raw path leaking from an unrelated source produces a
        # DIFFERENT line and still fails loudly here) without making this
        # assertion depend on how many internal call sites happen to log the
        # same message.
        warning_lines = list(
            dict.fromkeys(
                line
                for line in combined_output.splitlines()
                if ESCAPE_WARNING_SUBSTRING in line
            )
        )
        assert len(warning_lines) == 1, (
            f"Expected exactly one DISTINCT warning line naming the refused "
            f"target (repeats of the identical line are expected and "
            f"collapsed; a second, DIFFERENT line would indicate a raw path "
            f"leaking from an unrelated source):\n{combined_output}"
        )
        # D-01/D-03: assert MEANING, not representation format -- the
        # offending target is NAMED in the warning line, whether the message
        # site quotes it with `!r`, a hardcoded `'{value}'`, or a future
        # delimiter-aware helper. `path_named_in` requires the FULL target
        # value, never a basename, so a message that only still names the
        # same-basename `fallback` field (the D-03 trap) fails this assertion.
>       assert path_named_in(target, warning_lines[0]), (
            f"Expected the warning to name the offending target {target!r} "
            f"(raw or repr()'d):\n{warning_lines[0]}"
        )
E       AssertionError: Expected the warning to name the offending target 'C:\\escape.typ' (raw or repr()'d):
E         WARNING: a path is not supported in a typst_documents target name: -- using 'escape' instead
E       assert False
E        +  where False = path_named_in('C:\\escape.typ', "WARNING: a path is not supported in a typst_documents target name: -- using 'escape' instead")

tests/test_out02_escape_target_gate.py:167: AssertionError
=========================== short test summary info ============================
FAILED tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[traversal]
FAILED tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[absolute]
FAILED tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[drive]
============================== 3 failed in 0.67s ===============================
```

**Attribution.** All three failures raise at `tests/test_out02_escape_target_gate.py:167`, the
`assert path_named_in(target, warning_lines[0])` line — the naming assertion specifically. Neither
`assert ESCAPE_WARNING_SUBSTRING in combined_output` (line 127) nor `assert len(warning_lines) == 1`
(line 155) failed for any of the three shapes: the warning substring is still present (only the
`target` field was removed, not the whole message) and exactly one distinct warning line is still
emitted per build, so both of those assertions passed and the failure is attributable to the naming
predicate alone finding the target absent.

**Step 3 — revert and prove it.**

```
$ git checkout -- typsphinx/builder.py
$ git status --porcelain typsphinx/
(empty)
$ git diff --stat -- typsphinx/
(empty)
```

**Step 4 — re-prove green on the restored tree.** `uv run pytest
tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof -q` —
whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4dccbfe29904a32f
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items

tests/test_out02_escape_target_gate.py ...                               [100%]

============================== 3 passed in 0.66s ===============================
```

`3 passed`, zero skips. The same test, same command: RED under the falsification, GREEN against
the real (restored) product message.

## D-05(a) — durable meta-tests and the running census count

`tests/test_path_naming_predicate.py` (D-05(a)) is the durable half of the falsification
contract: 12 fixtureless meta-tests covering the raw/repr/hardcoded-quote/delimiter-wrapped
positive cases, the D-03 fallback trap, all four escape shapes under a falsified line
(parametrized), `os.PathLike` acceptance, and the `ValueError`/`TypeError` refusals.

`uv run pytest tests/test_path_naming_predicate.py -q` — whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4dccbfe29904a32f
configfile: pyproject.toml
plugins: cov-7.1.0
collected 12 items

tests/test_path_naming_predicate.py ............                         [100%]

============================== 12 passed in 0.02s ==============================
```

`12 passed`, zero skips.

`uv run black --check tests/test_path_naming_predicate.py`:

```
All done! ✨ 🍰 ✨
1 file would be left unchanged.
```

Exit code 0.

The AST pass-criterion count for the new module, run as
`uv run python -c "import ast,pathlib;t=ast.parse(pathlib.Path('tests/test_path_naming_predicate.py').read_text(encoding='utf-8'));print(sum(1 for a in ast.walk(t) if isinstance(a,ast.Assert) for s in ast.walk(a.test) if (isinstance(s,ast.Call) and isinstance(s.func,ast.Name) and s.func.id=='repr') or (isinstance(s,ast.FormattedValue) and s.conversion==114)))"`:

```
0
```

The meta-tests introduce no new census site — every representation-quoted message is built in a
separate statement above its assert, never inside the assert's own test expression.

The whole-tree AST pass-criterion count, run as
`uv run python -c "import ast,pathlib;print(sum(1 for f in pathlib.Path('tests').rglob('*.py') if '__pycache__' not in f.parts for a in ast.walk(ast.parse(f.read_text(encoding='utf-8'))) if isinstance(a,ast.Assert) for s in ast.walk(a.test) if (isinstance(s,ast.Call) and isinstance(s.func,ast.Name) and s.func.id=='repr') or (isinstance(s,ast.FormattedValue) and s.conversion==114)))"`:

```
8
```

Measured `9` at plan time on the phase base; this plan's rewrite of
`tests/test_out02_escape_target_gate.py`'s pass criterion removed one path-valued site, moving
the running count to `8`, exactly as expected.

`ruff` in this worktree's venv could not execute (the same NixOS dynamic-linker hazard recorded
above for Task 1). The `nix-shell -p ruff --run "ruff check tests/test_path_naming_predicate.py"`
retry succeeded with `All checks passed!`.

## SC#1/SC#2 (b) — post-rewrite green: image-rehome warning

Recorded AFTER `tests/test_builder.py`'s `test_post_process_images_rehome_escape_relocates_with_warning`
pass criterion was rewritten from `assert repr(abs_uri) in message` onto
`assert path_named_in(abs_uri, message)`, consuming the shared predicate plan 58-01 created in
`tests/_path_naming.py`.

`uv run pytest tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -q`:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1cc6425a290e0e7
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests/test_builder.py .                                                  [100%]

============================== 1 passed in 0.13s ===============================
```

`1 passed`, zero skips.

`uv run pytest tests/test_builder.py -q` — the whole module, proving the added import broke
nothing else in a 600-line file:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1cc6425a290e0e7
configfile: pyproject.toml
plugins: cov-7.1.0
collected 31 items

tests/test_builder.py ...............................                    [100%]

============================== 31 passed in 0.34s ==============================
```

`31 passed`, zero skips.

The AST pass-criterion count for this file, run as
`uv run python -c "import ast,pathlib;t=ast.parse(pathlib.Path('tests/test_builder.py').read_text(encoding='utf-8'));print(sum(1 for a in ast.walk(t) if isinstance(a,ast.Assert) for s in ast.walk(a.test) if (isinstance(s,ast.Call) and isinstance(s.func,ast.Name) and s.func.id=='repr') or (isinstance(s,ast.FormattedValue) and s.conversion==114)))"`:

```
0
```

It measured `1` at the phase base. This number moving from 1 to 0 IS SC#1 for this file.

The whole-tree count, run as
`uv run python -c "import ast,pathlib;print(sum(1 for f in pathlib.Path('tests').rglob('*.py') if '__pycache__' not in f.parts for a in ast.walk(ast.parse(f.read_text(encoding='utf-8'))) if isinstance(a,ast.Assert) for s in ast.walk(a.test) if (isinstance(s,ast.Call) and isinstance(s.func,ast.Name) and s.func.id=='repr') or (isinstance(s,ast.FormattedValue) and s.conversion==114)))"`:

```
7
```

`SC#3 — path-valued pass-criterion count is now zero`. It was `9` at the phase base and `8` after
plan 58-01; this plan's rewrite removes the second and final path-valued site, moving the running
count to `7` — exactly the seven non-path sites, with zero path-valued sites remaining.

`uv run black --check tests/test_builder.py`:

```
All done! ✨ 🍰 ✨
1 file would be left unchanged.
```

Exit code 0. (An intermediate `assert path_named_in(\n    abs_uri, message\n), f"..."` shape was
first tried; `black` reformatted it onto three lines, which split the literal
`path_named_in(abs_uri, message)` substring the plan's own acceptance criterion greps for across a
line break. Shortened the failure-message f-string so the whole `assert` statement fits black's
88-column limit on one physical line — `black --check` now reports the file unchanged, and the
literal substring the acceptance grep needs is intact.)

`uv run ruff check tests/test_builder.py` in this worktree's venv:

```
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```

### ruff could not execute in this worktree

The same NixOS dynamic-linker hazard recorded in plan 58-01's evidence. The
`nix-shell -p ruff --run "ruff check tests/test_builder.py"` retry:

```
All checks passed!
```

Lint authority for this file falls to CI (the freshly-synced worktree venv's `ruff` is a
generic-linux ELF that cannot exec on this NixOS host; this is an environment defect, not a code
RED).

`git status --porcelain typsphinx/`:

```
```

Empty — no output.

## SC#2 (c) — recorded falsification: builder.py:1767 (image-rehome warning)

D-05(b): a real, temporary edit to `typsphinx/builder.py`'s image-rehome warning, dropping ONLY the
`{resolved_uri!r}` interpolation while leaving the `key` interpolation (and its `!r` conversion)
untouched — the same-basename analogue of the D-03 trap: the relocation key ends in the same
basename (`chart.png`) as the URI it replaced, so a message still carrying `key` is exactly the
shape a basename-based predicate would wrongly accept. Made, measured, and reverted inside this
single task; the edit never survived to a commit.

**Step 1 — the falsifying edit.** `git diff -- typsphinx/builder.py` while the edit was in place:

```diff
diff --git a/typsphinx/builder.py b/typsphinx/builder.py
index a967a58c..28cb51a3 100644
--- a/typsphinx/builder.py
+++ b/typsphinx/builder.py
@@ -1764,7 +1764,7 @@ class TypstBuilder(Builder):
                     f"{path.basename(resolved_uri)}"
                 )
                 logger.warning(
-                    f"could not rehome image URI {resolved_uri!r} relative "
+                    f"could not rehome image URI relative "
                     f"to the doctree directory -- relocated to {key!r}"
                 )
             elif path.isfile(path.join(self.srcdir, rel_uri)):
```

The literal `could not rehome image URI` survives intact (only the `resolved_uri` interpolation
inside the f-string is removed), and the `key` interpolation with its `!r` conversion is left fully
in place.

**Step 2 — the RED.** `uv run pytest
tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -q` — whole
output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1cc6425a290e0e7
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests/test_builder.py F                                                  [100%]

=================================== FAILURES ===================================
________ test_post_process_images_rehome_escape_relocates_with_warning _________

temp_sphinx_app = <SphinxTestApp buildername='html'>
caplog = <_pytest.logging.LogCaptureFixture object at 0x71f8f3bc12b0>

    def test_post_process_images_rehome_escape_relocates_with_warning(
        temp_sphinx_app, caplog
    ):
        """
        D-05/D-06: an absolute URI whose rehome result cannot possibly sit
        under doctreedir -- built from the filesystem root -- is relocated
        to the reserved namespace plus a short hash prefix plus the basename
        of the ORIGINAL absolute URI, and emits exactly one WARNING naming
        the offending URI.
        ...
        """
        ...
        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
        assert len(warning_records) == 1
        message = warning_records[0].getMessage()
        assert "could not rehome image URI" in message
        # Format-agnostic: holds whether the message site quotes with `!r`
        # (today), a hardcoded '{value}', or MSG-02's delimiter-aware helper
        # (Phase 60) -- asserting that the URI is NAMED in the message, not
        # asserting a particular representation of it.
>       assert path_named_in(abs_uri, message), f"{abs_uri!r} not named in {message!r}"
E       AssertionError: '/typsphinx_test_50_03_escape_root/chart.png' not named in "WARNING: could not rehome image URI relative to the doctree directory -- relocated to '_typst_converted/bb60dcd8-chart.png'"
E       assert False
E        +  where False = path_named_in('/typsphinx_test_50_03_escape_root/chart.png', "WARNING: could not rehome image URI relative to the doctree directory -- relocated to '_typst_converted/bb60dcd8-chart.png'")

tests/test_builder.py:597: AssertionError
------------------------------ Captured log call -------------------------------
WARNING  sphinx.typsphinx.builder:logging.py:138 WARNING: could not rehome image URI relative to the doctree directory -- relocated to '_typst_converted/bb60dcd8-chart.png'
=========================== short test summary info ============================
FAILED tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning
============================== 1 failed in 0.15s ===============================
```

`1 failed`, containing the literal `AssertionError` and `path_named_in`.

**Attribution.** The failure raises at `tests/test_builder.py:597`, the
`assert path_named_in(abs_uri, message)` line — the naming assertion specifically. Neither
`assert len(warning_records) == 1` nor `assert "could not rehome image URI" in message` failed:
exactly one WARNING record is still emitted and the literal substring `could not rehome image URI`
is still present in its message (only the `resolved_uri` interpolation was removed, not the whole
message), so both of those assertions passed and the failure is attributable to the naming
predicate alone finding the URI absent — the surviving `key` field (`'_typst_converted/bb60dcd8-chart.png'`)
shares the basename `chart.png` with the removed `abs_uri`, exactly the same-basename trap shape,
and the full-value predicate correctly refuses to be satisfied by it.

**Step 3 — revert and prove it.**

```
$ git checkout -- typsphinx/builder.py
$ git status --porcelain typsphinx/
(empty)
$ git diff --stat -- typsphinx/
(empty)
```

**Step 4 — re-prove green on the restored tree.** `uv run pytest
tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -q` — whole
output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1cc6425a290e0e7
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests/test_builder.py .                                                  [100%]

============================== 1 passed in 0.13s ===============================
```

`1 passed`, zero skips. The same test, same command: RED under the falsification, GREEN against the
real (restored) product message.

### SC#2 — the three recorded runs, both sites

| Site | Pre-rewrite green | Post-rewrite green | Recorded RED |
|---|---|---|---|
| `tests/test_out02_escape_target_gate.py:134` (docname target) | `## SC#2 (a)` above | `## SC#1/SC#2 (b) — post-rewrite green: escape-target gate` above | `## SC#2 (c) — recorded falsification: builder.py:697 (docname target warning)` above |
| `tests/test_builder.py:598` (image-rehome) | `## SC#2 (a)` above (this file's baseline is recorded in the same section, run before either rewrite) | `## SC#1/SC#2 (b) — post-rewrite green: image-rehome warning` above | `## SC#2 (c) — recorded falsification: builder.py:1767 (image-rehome warning)` above (this section) |

**SC#4 scope observation.** `git diff --stat -- typsphinx/`:

```
```

Empty — no output.

`git diff --name-only 3b0f2b93f924f28eba94a0e92ea76996e9d743ad..HEAD -- typsphinx/` (the phase-base
SHA recorded in `## SC#2 (a)` above):

```
```

Empty — no output. `typsphinx/` is byte-identical to the phase base at this point in the plan,
proven both against the working tree and against the phase-base SHA.

## D-09 — the census guard observed RED (deliberate falsification)

`tests/test_repr_census_guard.py` (D-08/D-09) parses every `tests/**/*.py` with `ast`, walks each
`ast.Assert` node's `.test` expression only, and asserts the collected `repr()`/`!r`
pass-criterion hit set equals a recorded seven-site allowlist. A guard that has never been
observed RED is not known to be load-bearing — this section records the one-time falsification
cycle D-09 requires before the guard is trusted, run against `tests/test_preview_version_sync.py`
specifically (untouched by this phase, zero `repr(`/`!r` occurrences before the injection, and
excluded from `REWRITTEN_PATH_VALUED_MODULES` so the injection trips exactly one assertion, not
two).

**Step 1 — baseline.** `uv run pytest tests/test_repr_census_guard.py -q` — whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7d7c18e818f01603
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_repr_census_guard.py ....                                     [100%]

============================== 4 passed in 0.61s ===============================
```

`4 passed`, zero skips — the baseline captured immediately before the injection, so the RED in
Step 3 is attributable to the injection and nothing else.

**Step 2 — injection.** One throwaway, deliberately TRUE assertion appended as the last statement
of `test_all_four_packages_declared` in `tests/test_preview_version_sync.py`. The function's body
ended at line 118 before the injection; the injected statement became line 119, exactly as
predicted before running anything. `git diff -- tests/test_preview_version_sync.py` while the
edit was in place:

```diff
diff --git a/tests/test_preview_version_sync.py b/tests/test_preview_version_sync.py
index aebb664a..8a298041 100644
--- a/tests/test_preview_version_sync.py
+++ b/tests/test_preview_version_sync.py
@@ -116,6 +116,7 @@ def test_all_four_packages_declared():
             f"{filename} is missing expected @preview packages: {missing} "
             f"(declared: {declared})"
         )
+        assert "codly" in repr(EXPECTED_PACKAGES)  # temporary; reverted in this task
 
 
 def test_example_templates_match_canonical_versions():
```

The injected assertion is deliberately TRUE (`"codly"` is a member of `EXPECTED_PACKAGES`, so
`repr(EXPECTED_PACKAGES)` always contains the literal `codly`) — the host module itself stays
green throughout, and the only thing that changes is the whole-tree census.

**Step 3 — RED.** `uv run pytest tests/test_repr_census_guard.py -q` — whole output verbatim:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7d7c18e818f01603
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_repr_census_guard.py F...                                     [100%]

=================================== FAILURES ===================================
___________ test_pass_criterion_repr_sites_match_recorded_allowlist ____________

    def test_pass_criterion_repr_sites_match_recorded_allowlist():
        """The collected pass-criterion set must equal the recorded allowlist
        exactly. A new entry means a test grew a pass criterion coupled to a
        value's representation format and 58-REPR-CENSUS.md is now stale; a
        missing entry means a site moved or was removed and the census must be
        re-derived, not the allowlist quietly edited."""
        collected, _ = _collect_pass_criterion_repr_sites()
    
        found_but_not_allowlisted = collected - PASS_CRITERION_REPR_ALLOWLIST
        allowlisted_but_not_found = PASS_CRITERION_REPR_ALLOWLIST - collected
    
>       assert collected == PASS_CRITERION_REPR_ALLOWLIST, (
            "The repr()/!r pass-criterion census has drifted from the recorded "
            "allowlist in 58-REPR-CENSUS.md.\n"
            f"Sites found but NOT allowlisted (new pass-criterion site -- "
            f"58-REPR-CENSUS.md is stale): {sorted(found_but_not_allowlisted)}\n"
            f"Allowlisted sites no longer found (a site moved or was removed -- "
            f"re-derive the census, do not quietly edit the allowlist): "
            f"{sorted(allowlisted_but_not_found)}"
        )
E       AssertionError: The repr()/!r pass-criterion census has drifted from the recorded allowlist in 58-REPR-CENSUS.md.
E         Sites found but NOT allowlisted (new pass-criterion site -- 58-REPR-CENSUS.md is stale): [('test_preview_version_sync.py', 119)]
E         Allowlisted sites no longer found (a site moved or was removed -- re-derive the census, do not quietly edit the allowlist): []
E       assert frozenset({('...', 832), ...}) == frozenset({('...', 847), ...})
E         
E         Extra items in the left set:
E         ('test_preview_version_sync.py', 119)
E         Use -v to get more diff

tests/test_repr_census_guard.py:154: AssertionError
=========================== short test summary info ============================
FAILED tests/test_repr_census_guard.py::test_pass_criterion_repr_sites_match_recorded_allowlist
========================= 1 failed, 3 passed in 0.62s ==========================
```

`1 failed, 3 passed`, exactly as D-09 requires: the failure is
`test_pass_criterion_repr_sites_match_recorded_allowlist`, in its "sites found but not
allowlisted" branch, naming `test_preview_version_sync.py` and line `119` — the exact line the
injection landed on. The other three tests (`test_no_path_valued_pass_criterion_site_remains`,
`test_sweep_is_not_vacuous`, `test_allowlist_entries_point_at_real_lines`) stayed green: the
injected site is not path-valued (so it does not trip the zero-path-valued check), the sweep still
parsed well over `MINIMUM_FILES_SWEPT` files, and every allowlist entry still points at a real
line — the RED is attributable to the census-drift assertion alone.

**Step 4 — revert, unconditionally, and prove it.** `git checkout -- tests/test_preview_version_sync.py`, then two clean checks:

```
$ git checkout -- tests/test_preview_version_sync.py
$ git status --porcelain tests/test_preview_version_sync.py
(empty)
$ git status --porcelain tests/
?? tests/test_repr_census_guard.py
```

`git status --porcelain tests/test_preview_version_sync.py` produced no output — the perturbation
left no trace. `git status --porcelain tests/` shows nothing but the new, still-untracked
`tests/test_repr_census_guard.py` — no survivor of the falsification remains anywhere under
`tests/`. This second check matters because this perturbation is under `tests/`, where SC#4's
`git status --porcelain typsphinx/` gate (the one plans 58-01 and 58-02 lean on) is blind to a
survivor here.

**Step 5 — green again.** `uv run pytest tests/test_repr_census_guard.py -q` — whole output
verbatim, closing the loop on the same command that opened it:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7d7c18e818f01603
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_repr_census_guard.py ....                                     [100%]

============================== 4 passed in 0.60s ===============================
```

`4 passed`, zero skips — the same test, same command, same result as Step 1's baseline.

**What this transcript establishes.** A guard that has never been seen RED is not known to be
load-bearing, and this one has now been seen RED against a real, deliberately introduced
pass-criterion site — attributed specifically to the census-equality assertion, reverted cleanly,
and re-proven green on the restored tree.

## Phase gate — full suite, formatting, lint

`uv run pytest -q` — the full suite, verbatim final summary line (full transcript run in this
worktree; zero failures):

```
================= 1437 passed, 5 skipped in 123.26s (0:02:03) ==================
```

All zero failures — no re-run against the phase-base SHA is needed. For completeness, the five
skips (re-run with `-rs` to capture reasons) are all pre-existing and environment-gated, unrelated
to this phase's changes:

```
SKIPPED [1] tests/test_changelog_page_gate.py:167: myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class
SKIPPED [1] tests/test_changelog_page_gate.py:176: myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class
SKIPPED [1] tests/test_changelog_page_gate.py:186: myst-parser is required to build docs/source; it lives in the docs extra only (D-01), so a dev-only CI lane skips this class
SKIPPED [1] tests/test_changelog_page_gate.py:218: myst-parser is required to build the changelog include fixture; it lives in the docs extra only (D-01)
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1437 passed, 5 skipped in 121.58s (0:02:01) ==================
```

`uv run black --check .` — whole tree, verbatim:

```
All done! ✨ 🍰 ✨
342 files would be left unchanged.
```

Exit code 0.

`uv run ruff check .` — whole tree, in this worktree's venv:

```
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```

### ruff could not execute in this worktree

The same NixOS dynamic-linker hazard recorded in plans 58-01 and 58-02's evidence: the
freshly-synced worktree venv's `ruff` binary is a generic-linux ELF that cannot exec on this NixOS
host — an environment defect, not a code RED. Retry via
`nix-shell -p ruff --run "ruff check ."`:

```
All checks passed!
```

Lint authority for this phase falls to CI, consistent with plans 58-01 and 58-02.

`uv run mypy typsphinx/` — recorded as a no-change control, since this phase changes no file under
`typsphinx/`:

```
Success: no issues found in 8 source files
```

This result must be, and is, byte-identical in shape to the pre-phase baseline: `typsphinx/` has
zero commits in this phase's range (proven in `## SC#4` below), so mypy has nothing new to report.

## SC#4 — no file under typsphinx/ changed by this phase

The phase-base SHA is `3b0f2b93f924f28eba94a0e92ea76996e9d743ad`, recorded in the `## SC#2 (a)`
section above (`git rev-parse HEAD` — this worktree's HEAD before any edit in plan 58-01).

`git status --porcelain typsphinx/`:

```
```

Empty — no output.

`git diff --name-only -- typsphinx/`:

```
```

Empty — no output.

`git diff --stat 3b0f2b93f924f28eba94a0e92ea76996e9d743ad..HEAD -- typsphinx/`:

```
```

Empty — no output.

`git log --oneline 3b0f2b93f924f28eba94a0e92ea76996e9d743ad..HEAD -- typsphinx/`:

```
```

Empty — no output. No commit in this phase's range touches `typsphinx/` at all, proven at phase
scope (not merely per task) against the same base SHA plans 58-01 and 58-02 measured their own
per-task checks against.

## SC#5 — milestone branch on origin

`git rev-parse gsd/v0.9.1-windows-path-correctness` — the local tip about to be published:

```
3bce62b793824e23671059a600c2bd10ebe52580
```

`git ls-remote --heads origin` filtered for `0.9.1` — expected to match nothing before the push:

```
(no match)
```

`git branch --list 'gsd/v0.9.1-milestone'` — expected empty. This project's commit helper creates a
decoy `gsd/<milestone>-milestone` sibling most rounds; none exists this round:

```
(empty)
```

`git push -u origin gsd/v0.9.1-windows-path-correctness` — whole output verbatim:

```
remote:
remote: Create a pull request for 'gsd/v0.9.1-windows-path-correctness' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/gsd/v0.9.1-windows-path-correctness
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        gsd/v0.9.1-windows-path-correctness -> gsd/v0.9.1-windows-path-correctness
branch 'gsd/v0.9.1-windows-path-correctness' set up to track 'origin/gsd/v0.9.1-windows-path-correctness'.
```

`git branch -vv` filtered to the milestone branch — the line carries the
`[origin/gsd/v0.9.1-windows-path-correctness]` tracking marker:

```
+ gsd/v0.9.1-windows-path-correctness      3bce62b7 (/home/yuta/Documents/typsphinx) [origin/gsd/v0.9.1-windows-path-correctness] docs(phase-58): update tracking after wave 2
```

`git ls-remote --heads origin gsd/v0.9.1-windows-path-correctness` — returns a SHA:

```
3bce62b793824e23671059a600c2bd10ebe52580	refs/heads/gsd/v0.9.1-windows-path-correctness
```

`git ls-remote --heads origin 'gsd/v0.9.1-milestone'` — must return nothing:

```
(no output)
```

`git rev-parse --abbrev-ref 'gsd/v0.9.1-windows-path-correctness@{upstream}'` — must print exactly
`origin/gsd/v0.9.1-windows-path-correctness`:

```
origin/gsd/v0.9.1-windows-path-correctness
```

`git tag -l 'v0.9.1*'` and `git ls-remote --tags origin 'v0.9.1*'` — both must produce no output,
proving this phase created no tag:

```
(no output)
(no output)
```

**Two honest notes.**

First: the pushed tip is this worktree's view of the milestone branch as of this wave's start
(`3bce62b7`, carrying plans 58-01 and 58-02's commits, but not this plan's own three commits, which
land on the branch only after the orchestrator merges this worktree back). A remote that is a few
commits behind the phase's final tip is expected and is not a failure of SC#5, whose wording is
about the branch being on `origin` and tracking, not about the remote holding every commit this
phase will ever produce.

Second: `.github/workflows/ci.yml`'s `push` and `pull_request` triggers are scoped to `main` and
`develop` only (verified: lines 3-8 of that file), so this push dispatches no CI run. Phase 58's
SC#5 does not require one — the fresh 3-OS lane belongs to the product-code phases (59-61) whose
success criteria name it explicitly. Recorded as RESEARCH.md Assumption A2, resolved by re-reading
SC#5's literal wording at plan time, not by preference.
