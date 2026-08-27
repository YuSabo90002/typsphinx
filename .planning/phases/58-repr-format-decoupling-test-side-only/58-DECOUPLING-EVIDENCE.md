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
