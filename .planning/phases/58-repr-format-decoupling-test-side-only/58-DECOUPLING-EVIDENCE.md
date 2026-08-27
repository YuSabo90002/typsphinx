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

<!-- gsd:write-continue -->
