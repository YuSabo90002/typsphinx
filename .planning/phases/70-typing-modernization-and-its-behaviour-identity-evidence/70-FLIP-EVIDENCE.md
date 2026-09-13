# Phase 70 — The Ignore Flip

BASE_70_09 = 48fb3fbc3cba7b3409b3c768715a1c011312f777
PRE_FLIP_SHA = 48fb3fbc3cba7b3409b3c768715a1c011312f777
(both from `git rev-parse HEAD` at the start of this plan's execution, in this worktree)

## Provisioning

Ran `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`.
Exit 0. 90 packages installed, including `mypy==2.3.1`, `ruff==0.16.6`, `myst-parser==5.1.0`
(docs extra present), `pytest==9.1.1`, matching 70-02's provisioning.

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

Both equal 70-02's `VENV_HOME` / `VENV_VERSION_INFO` (`70-BASELINE-EVIDENCE.md:53-54`). Confirmed.

RUFF_VERSION_FLIP = ruff 0.16.6
(from `uv run ruff --version 2>/dev/null`)

`RUFF_VERSION_FLIP` equals `RUFF_VERSION_BASE` (`70-BASELINE-EVIDENCE.md:63`, `ruff 0.16.6`).
Confirmed — no mid-flight ruff bump (constraint 4).

## Pre-flip residue check

Ran `uv run ruff check . --select UP006,UP035; echo "exit:$?"`:
```
All checks passed!
exit:0
```

Zero residue repo-wide, under the still-present ignores overridden by `--select`. No HALT needed.

`IGNORE_LEN_PRE = ` read with `uv run python -c` and `tomllib`:

```
$ uv run python -c 'import tomllib; d=tomllib.load(open("pyproject.toml","rb")); i=d["tool"]["ruff"]["lint"]["ignore"]; print(len(i)); print(i)'
9
['E501', 'T201', 'B017', 'UP035', 'UP006', 'UP028', 'N802', 'A001', 'F841']
```

IGNORE_LEN_PRE = 9

## The flip commit

Used the Edit tool to delete the whole `"UP035",` line and the whole `"UP006",` line, each with
its trailing comment, from the ignore array. Nothing else in `pyproject.toml` changed.

Ran `git mv .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md
.planning/todos/completed/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`. The
file's content is unchanged.

Committed exactly those two changes together (`0224b5ea`):
`chore(70-09): drop the UP006/UP035 ignores and move the typing todo to completed (QUA-09, DOC-22)`.

`git show --name-status -M --format= HEAD`:
```
R100	.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md	.planning/todos/completed/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md
M	pyproject.toml
```
Exactly `M pyproject.toml` and one `R100` rename from pending to completed. Confirmed.

`git diff -U0 "$PRE_FLIP_SHA" HEAD -- pyproject.toml`:
```
diff --git a/pyproject.toml b/pyproject.toml
index 4194688d..bcef7a73 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -128,2 +127,0 @@ ignore = [
-    "UP035",  # typing.Dict/List/Set deprecation; modernization deferred (see .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md)
-    "UP006",  # Use dict instead of Dict; same deferral as UP035 above
```
Two removed lines, zero added. Confirmed.

## Post-flip checks

`IGNORE_LEN_POST = ` read the same way as `IGNORE_LEN_PRE`:

```
$ uv run python -c 'import tomllib; d=tomllib.load(open("pyproject.toml","rb")); i=d["tool"]["ruff"]["lint"]["ignore"]; print(len(i)); print(i)'
7
['E501', 'T201', 'B017', 'UP028', 'N802', 'A001', 'F841']
```

IGNORE_LEN_POST = 7

`IGNORE_LEN_POST` (7) equals `IGNORE_LEN_PRE` (9) minus 2. Confirmed. The list still contains
`B017` and `UP028`, and contains neither `UP006` nor `UP035`.

`git grep -n 'todos/pending/2026-07-22-modernize' -- . ':!.planning'` at HEAD:
```
(empty; grep exit 1)
```
Empty, as required.

Positive control — the same grep at `PRE_FLIP_SHA` (`48fb3fbc3cba7b3409b3c768715a1c011312f777`):
```
$ git grep -n 'todos/pending/2026-07-22-modernize' 48fb3fbc3cba7b3409b3c768715a1c011312f777 -- . ':!.planning'
48fb3fbc3cba7b3409b3c768715a1c011312f777:pyproject.toml:128:    "UP035",  # typing.Dict/List/Set deprecation; modernization deferred (see .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md)
```
One line, in `pyproject.toml`, as expected.

`uv run ruff check . --select UP006,UP035; echo "exit:$?"`:
```
All checks passed!
exit:0
```

Bare `uv run ruff check .; echo "exit:$?"`:
```
All checks passed!
exit:0
```

Both exit 0. No `preview` setting anywhere in `pyproject.toml`
(`grep -nE '^[[:space:]]*preview[[:space:]]*=' pyproject.toml` — exit 1, no match).

ruff now enforces UP006/UP035 on a tree with nothing left to enforce, and the todo left
`pending/` in the same commit as the last reference to it.

