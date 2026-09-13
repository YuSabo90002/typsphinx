# Phase 70 — DOC-22 Evidence (CLAUDE.md:75)

BASE_70_01 = 697a113221a8a267d7e8c6dd1f2b95672f9454d2

## Head check

```
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-afdab82168e458ea5

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

## Before

```
$ sed -n 75p CLAUDE.md
- **Python 3.12+ is required.** ruff intentionally ignores `UP006`/`UP035` (the `Dict`/`List` → `dict`/`list` upgrades) — this is a deliberate deferral, not a compatibility constraint; the modernization pass is filed at `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`. Don't "modernize" typing imports until that todo lands.
```

Line 75 starts with `- **Python 3.12+ is required.**`, as expected. Proceeding with the rewrite.

## After

```
$ sed -n 75p CLAUDE.md
- **Python 3.12+ is required.** Annotations use builtin generics (`dict[str, Any]`, `list[str]`, `set[str]`, `tuple[str, ...]`) and take abstract types such as `Iterator` from `collections.abc`, not `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`.

$ git diff -U0 "$BASE_70_01" HEAD -- CLAUDE.md
diff --git a/CLAUDE.md b/CLAUDE.md
index ff8ab6b2..17194349 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -75 +75 @@ User-facing config values (all registered in `__init__.py`, prefix `typst_`) inc
-- **Python 3.12+ is required.** ruff intentionally ignores `UP006`/`UP035` (the `Dict`/`List` → `dict`/`list` upgrades) — this is a deliberate deferral, not a compatibility constraint; the modernization pass is filed at `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`. Don't "modernize" typing imports until that todo lands.
+- **Python 3.12+ is required.** Annotations use builtin generics (`dict[str, Any]`, `list[str]`, `set[str]`, `tuple[str, ...]`) and take abstract types such as `Iterator` from `collections.abc`, not `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`.
```

The diff has exactly one removed line and one added line, both at line 75. Commit `3c5e281c` (`docs(70-01): rewrite CLAUDE.md typing bullet as an annotation-style instruction (DOC-22)`) is the only commit in `BASE_70_01..HEAD` touching CLAUDE.md, and `git show --name-only` for it lists only `CLAUDE.md`.

## Provisioning

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
Using CPython 3.13.13 interpreter at: /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin/python3.13
Creating virtual environment at: .venv
Resolved 91 packages in 0.75ms
...
Installed 90 packages in 58ms
```

VENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin

VENV_VERSION_INFO = 3.13.13

The interpreter is 3.13.13, as required.

## D-04 neutrality

```
$ git grep -l CLAUDE -- 'tests/*.py'
tests/fixtures/templates_path_collision_multi_gate/conf.py
tests/test_citation_degradation_gate.py
tests/test_readthedocs_config.py
tests/test_toolchain_config_gate.py
```

None of these files reads `CLAUDE.md` — the fixture `conf.py` is a Sphinx config used by a template-collision fixture (unrelated to this document), and the three `tests/test_*.py` hits are prose in docstrings and assertion messages, none of which quotes or parses line 75.

```
$ LC_ALL=C uv run pytest tests/fixtures/templates_path_collision_multi_gate/conf.py tests/test_citation_degradation_gate.py tests/test_readthedocs_config.py tests/test_toolchain_config_gate.py -q -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-afdab82168e458ea5
configfile: pyproject.toml
plugins: cov-7.1.0
collected 27 items

tests/test_citation_degradation_gate.py .................                [ 62%]
tests/test_readthedocs_config.py ......                                  [ 85%]
tests/test_toolchain_config_gate.py ....                                 [100%]

============================== 27 passed in 1.07s ==============================
```

CLAUDE_TESTS_EXIT = 0

```
$ uv run ruff check .
All checks passed!
```

```
$ uv run black --check .
All done! ✨ 🍰 ✨
355 files would be left unchanged.
```

Both exit 0. The CLAUDE.md:75 rewrite is lint-neutral and test-neutral (D-04).

## Pending-path census

```
$ git grep -n 'todos/pending/2026-07-22-modernize' -- . ':!.planning'
pyproject.toml:128:    "UP035",  # typing.Dict/List/Set deprecation; modernization deferred (see .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md)
```

PENDING_REFS_AFTER_70_01 = 1

The positive control at `BASE_70_01`:

```
$ git grep -n 'todos/pending/2026-07-22-modernize' "$BASE_70_01" -- . ':!.planning'
697a113221a8a267d7e8c6dd1f2b95672f9454d2:CLAUDE.md:75:- **Python 3.12+ is required.** ruff intentionally ignores `UP006`/`UP035` (the `Dict`/`List` → `dict`/`list` upgrades) — this is a deliberate deferral, not a compatibility constraint; the modernization pass is filed at `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`. Don't "modernize" typing imports until that todo lands.
697a113221a8a267d7e8c6dd1f2b95672f9454d2:pyproject.toml:128:    "UP035",  # typing.Dict/List/Set deprecation; modernization deferred (see .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md)
```

Two lines at the base (CLAUDE.md and pyproject.toml); one line after this plan (pyproject.toml only). The rewritten bullet no longer cites the pending path.

## Reading against D-01..D-03

**Before the flip** (ignores still present in `pyproject.toml`, product code not yet converted): the
rewritten bullet is purely an instruction about how to write annotations — builtin generics and
`collections.abc` for abstract types. It makes no claim about what ruff currently enforces or
suppresses, so it cannot be contradicted by the still-present `UP006`/`UP035` ignores. On the
contrary, it is exactly what authorises the conversion plans in waves 2-3 to proceed under the
still-present ignores: a contributor reading it today is told the target shape to write toward,
without being told that the linter already enforces it.

**After the flip** (ignores removed in 70-09, `ruff check .` enforcing `UP006`/`UP035`): the same
bullet remains true, because ruff now enforces the exact shape the bullet describes — builtin
generics and `collections.abc` imports. The bullet still makes no claim about ruff's configuration
(it never mentions ruff, `ignore`, or ruff's rule codes), so nothing about it becomes stale or false
when the ignore lines disappear. It reads identically and correctly on both sides of the flip, which
is the two-commit truth 70-10 re-checks (SC#1).
