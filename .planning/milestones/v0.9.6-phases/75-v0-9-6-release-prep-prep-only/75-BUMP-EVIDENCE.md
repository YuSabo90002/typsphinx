# Phase 75 — Bump Evidence (SC1)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-20T08:38:21Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a64ee11a04ac3c9ef

$ test -f .git; echo "exit:$?"
exit:0

$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo "shim_check:ok"
shim_check:ok

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.62ms
   Building typsphinx @ file:///…/agent-a64ee11a04ac3c9ef
      Built typsphinx @ file:///…/agent-a64ee11a04ac3c9ef
Prepared 1 package in 377ms
Installed 90 packages in 59ms
exit:0
```

PYVENV_HOME = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_INFO = 3.14

Per CLAUDE.md § "Interpreters may differ": this worktree's `.venv` is built on uv-managed
CPython 3.14, distinct from the main checkout's interpreter. Recorded here for cross-worktree
comparison, not asserted as an issue.

BASE_75_03 = 526a21d352696cb65c570d07d75ef8c7e3aa96a1
SCRATCH_75_03 = /tmp/tmp.eMEDCoCmWx

## Before

```
$ grep -n '^version = ' pyproject.toml
7:version = "0.9.2"

$ grep -n '\*\*Status\*\*: Stable' README.md
348:**Status**: Stable (v0.9.2) - Production ready

$ grep -A1 -xF 'name = "typsphinx"' uv.lock
name = "typsphinx"
version = "0.9.2"
```

PYPROJECT_VERSION_LINES = 1

## Edit: pyproject.toml

`pyproject.toml`'s `[project].version` moved from `"0.9.2"` to `"0.9.6"` — the only hand-typed
version literal in this task.

## Lock regeneration and idempotency

```
$ sha256sum uv.lock   # before
8ffc95d647af625926c3b0fe83181f51751810ad4b749b3dabff6368bc51289f  uv.lock

$ uv lock
Resolved 91 packages in 543ms
Updated typsphinx v0.9.2 -> v0.9.6

$ sha256sum uv.lock   # after first regeneration
897abaf8c00f648b17875749f8483ea1748dec6c8db63c30a0a835d00746aa96  uv.lock
```

UV_LOCK_EXIT = 0

```
$ uv lock   # second run, idempotency check
Resolved 91 packages in 0.72ms

$ sha256sum uv.lock   # after second regeneration
897abaf8c00f648b17875749f8483ea1748dec6c8db63c30a0a835d00746aa96  uv.lock
```

The two post-regeneration digests are equal (`897abaf8…` both times).

UV_LOCK_IDEMPOTENT = yes

```
$ uv lock --check
Resolved 91 packages in 0.71ms
```

UV_LOCK_CHECK_EXIT = 0

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --locked
Resolved 91 packages in 0.71ms
   Building typsphinx @ file:///…/agent-a64ee11a04ac3c9ef
      Built typsphinx @ file:///…/agent-a64ee11a04ac3c9ef
Prepared 1 package in 454ms
Uninstalled 1 package in 0.57ms
Installed 1 package in 0.51ms
 - typsphinx==0.9.2 (from file:///…/agent-a64ee11a04ac3c9ef)
 + typsphinx==0.9.6 (from file:///…/agent-a64ee11a04ac3c9ef)
```

UV_SYNC_LOCKED_EXIT = 0

```
$ git diff --numstat -- uv.lock
1	1	uv.lock

$ git diff -U0 -- uv.lock
diff --git a/uv.lock b/uv.lock
index edeb4cdd..20564364 100644
--- a/uv.lock
+++ b/uv.lock
@@ -1528 +1528 @@ name = "typsphinx"
-version = "0.9.2"
+version = "0.9.6"
```

Only the `typsphinx` stanza's `version` line changed — no other stanza moved. This is the
expected resolver behaviour (`uv lock` preserves existing pins unless requirements changed), and
`uv lock --check` plus the locked sync above already validate it independently.

UV_LOCK_TYPSPHINX_VERSION = 0.9.6

## Edit: README.md

`README.md`'s Status line moved from `**Status**: Stable (v0.9.2) - Production ready` to
`**Status**: Stable (v0.9.6) - Production ready`, keeping the exact wording
`tests/test_readme_version_sync.py`'s regex requires (`\*\*Status\*\*:\s*Stable \(v(?P<version>\d+\.\d+\.\d+)\)`).

## After

```
$ grep -n '^version = ' pyproject.toml
7:version = "0.9.6"

$ grep -n '\*\*Status\*\*: Stable' README.md
348:**Status**: Stable (v0.9.6) - Production ready

$ grep -A1 -xF 'name = "typsphinx"' uv.lock
name = "typsphinx"
version = "0.9.6"

$ uv run --no-sync python -c "import typsphinx; print(typsphinx.__version__)"
0.9.6
```

IMPORTED_VERSION = 0.9.6

| Surface | Before | After |
|---|---|---|
| `pyproject.toml` line 7 | `version = "0.9.2"` | `version = "0.9.6"` |
| `README.md` line 348 | `**Status**: Stable (v0.9.2) - Production ready` | `**Status**: Stable (v0.9.6) - Production ready` |
| `uv.lock`'s `typsphinx` stanza | `version = "0.9.2"` | `version = "0.9.6"` |
| Imported `typsphinx.__version__` | `0.9.2` | `0.9.6` |

## Version-sync gates

```
$ uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q -rs -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a64ee11a04ac3c9ef
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_readme_version_sync.py .                                      [ 25%]
tests/test_preview_version_sync.py ...                                   [100%]

============================== 4 passed in 0.02s ===============================
```

READMESYNC_PREVIEW_EXIT = 0

```
$ grep -ho '@preview/[a-z-]*:' typsphinx/templates/base.typ | sort -u | wc -l
4
```

PREVIEW_PACKAGE_COUNT = 4

## Commit discipline

The three product edits (`pyproject.toml`, `uv.lock`, `README.md`) are left uncommitted per this
plan's worktree provisioning instructions. Only this evidence file (`75-BUMP-EVIDENCE.md`) is
staged and committed for Task 1; the product edits wait for Task 3's single five-file commit.

## The one commit

Before staging, the working tree's product-scope status was recorded:

```
$ git status --porcelain -- . ':(exclude).planning'
 M CHANGELOG.md
 M README.md
 M pyproject.toml
 M tests/test_changelog_page_gate.py
 M uv.lock
```

Exactly the five expected files and nothing else — no `## HALT` was needed.

Staged by explicit path (never `git add -A`, never `git add .`):

```
$ git add pyproject.toml uv.lock README.md CHANGELOG.md tests/test_changelog_page_gate.py
```

Committed with a plain `git commit` naming the release prep and the version:

```
$ git commit -m "release(75-03): bump typsphinx to 0.9.6 and curate the CHANGELOG ..."
[worktree-agent-a64ee11a04ac3c9ef 84edd348] release(75-03): bump typsphinx to 0.9.6 and curate the CHANGELOG
 5 files changed, 63 insertions(+), 10 deletions(-)
```

BUMP_COMMIT_SHA = 84edd348b52f1f7e95073d2b3ebcbcd36417bc15

```
$ git show --name-only --format='%H %s' HEAD
84edd348b52f1f7e95073d2b3ebcbcd36417bc15 release(75-03): bump typsphinx to 0.9.6 and curate the CHANGELOG

CHANGELOG.md
README.md
pyproject.toml
tests/test_changelog_page_gate.py
uv.lock
```

```
$ git show --name-only --format= HEAD | grep -v '^$' | LC_ALL=C sort | paste -sd'|'
CHANGELOG.md|README.md|pyproject.toml|tests/test_changelog_page_gate.py|uv.lock
```

BUMP_COMMIT_FILES = CHANGELOG.md|README.md|pyproject.toml|tests/test_changelog_page_gate.py|uv.lock

This matches the `LC_ALL=C`-sorted, `|`-joined five-file list exactly.

**The AMENDED resolution this commit implements.** 75-CONTEXT.md's Phase Boundary bullet 1 and
ROADMAP SC1 both name a four-item set — `pyproject.toml`, `uv.lock`, `README.md` and
`CHANGELOG.md` — as landing together in "one commit," while the "Claude's Discretion → The bump
mechanics" bullet separately names a different four-item set —`pyproject.toml`, `uv.lock`,
`README.md` and `tests/test_changelog_page_gate.py` — for the same one commit. Neither text
forbids a superset, and the union of the two four-item sets is the only five-file reading that
satisfies both texts at once: it is a superset of SC1's explicit four-file list, and the test
edit's presence in the same tree state is in any case needed before SC1's own "zero skipped"
changelog-gate reading can be taken on the bumped tip. Phase 46's two-commit split (a separate
CHANGELOG commit, then a separate bump commit) is explicitly not the precedent this phase
follows — Phase 75's binding text requires one commit, not two.
