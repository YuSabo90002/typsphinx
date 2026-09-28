# Phase 77 — Bump Evidence (SC#1)

## Head check and provisioning

Timestamp, cwd, worktree check:

```
date -u +%FT%TZ  -> 2026-09-28T13:09:10Z
pwd -P            -> /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac30e4db427ca86b6
test -f .git; echo "exit:$?"  -> exit:0
```

Shim check:

```
grep -c typsphinx-fhs-run "$(command -v uv)"  -> 2
```

Provisioning:

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
```
exited 0 (venv resolved 91 packages, `typsphinx==0.9.6` from the worktree checkout installed
editable, plus every `dev`/`docs`-extra dependency).

PYVENV_HOME = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_INFO = 3.14

BASE_77_02 = 3984b231e30fbb76ba156d2f9b2abe475231bccf
(recorded from `git rev-parse HEAD` before any commit this plan makes; this is the spawn-time
worktree HEAD, verified an ancestor of every later commit.)

SCRATCH_77_02 = /tmp/p7702.CRAwfO
(from `mktemp -d /tmp/p7702.XXXXXX`.)

## Before

The three surfaces, re-measured at execution:

```
grep -n '^version = ' pyproject.toml
7:version = "0.9.6"
```

```
grep -n '\*\*Status\*\*: Stable' README.md
348:**Status**: Stable (v0.9.6) - Production ready
```

```
grep -n -A1 -xF 'name = "typsphinx"' uv.lock
1527:name = "typsphinx"
1528-version = "0.9.6"
```

PYPROJECT_VERSION_LINES = 1
(the count of `^version = ` lines in `pyproject.toml` — confirms it is the sole hand-edited
literal.)

## Dependency surface since v0.9.6

```
git diff --name-only v0.9.6 HEAD -- pyproject.toml uv.lock
```
prints nothing.

DEP_FILES_CHANGED_SINCE_V096 = 0

## Lock regeneration and idempotency

`pyproject.toml`'s `[project].version` edited from `0.9.6` to `0.9.7` — the only hand-typed
version literal in the whole plan.

```
sha256sum uv.lock   (before)
43409e7c0cf95f8b22103536c761dbd740ec3fd0862b025c9499d0c4ce41b7a5  uv.lock

uv lock
Resolved 91 packages in 338ms
Updated typsphinx v0.9.6 -> v0.9.7
```

UV_LOCK_EXIT = 0

```
sha256sum uv.lock   (after first regeneration)
1ce10d841d04f9e154e67c734922e420f68e944527a62d95b6fcb542d8214fa8  uv.lock

uv lock   (second regeneration)
Resolved 91 packages in 0.59ms

sha256sum uv.lock   (after second regeneration)
1ce10d841d04f9e154e67c734922e420f68e944527a62d95b6fcb542d8214fa8  uv.lock
```

The two post-regeneration digests are equal.

UV_LOCK_IDEMPOTENT = yes

```
uv lock --check
Resolved 91 packages in 0.62ms
```

UV_LOCK_CHECK_EXIT = 0

The SC#1 literal reading:

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --locked
Resolved 91 packages in 0.78ms
Prepared 1 package in 401ms
Uninstalled 10 packages in 6ms
Installed 1 package in 0.51ms
 - accessible-pygments==0.0.5
 - beautifulsoup4==4.15.0
 - furo==2025.12.19
 - mdit-py-plugins==0.6.1
 - myst-parser==5.1.0
 - soupsieve==2.8.4
 - sphinx-autodoc-typehints==3.13.6
 - sphinx-basic-ng==1.0.0b2
 - sphinx-intl==2.4.0
 - typsphinx==0.9.6 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac30e4db427ca86b6)
 + typsphinx==0.9.7 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac30e4db427ca86b6)
```

UV_SYNC_DEV_LOCKED_EXIT = 0

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --locked
Resolved 91 packages in 0.63ms
Installed 9 packages in 4ms
 + accessible-pygments==0.0.5
 + beautifulsoup4==4.15.0
 + furo==2025.12.19
 + mdit-py-plugins==0.6.1
 + myst-parser==5.1.0
 + soupsieve==2.8.4
 + sphinx-autodoc-typehints==3.13.6
 + sphinx-basic-ng==1.0.0b2
 + sphinx-intl==2.4.0
```

UV_SYNC_DEV_DOCS_LOCKED_EXIT = 0
(the docs extra is restored immediately after the dev-only literal reading, exactly as
`<worktree_provisioning>` requires.)

```
git diff -U0 -- uv.lock
diff --git a/uv.lock b/uv.lock
index 2b45bc67..cc741e63 100644
--- a/uv.lock
+++ b/uv.lock
@@ -1528 +1528 @@ name = "typsphinx"
-version = "0.9.6"
+version = "0.9.7"
```

Only the `typsphinx` stanza moved — no other stanza's lines changed.

UV_LOCK_CHANGED_STANZAS = typsphinx

UV_LOCK_TYPSPHINX_VERSION = 0.9.7
(read back from the regenerated file's `name = "typsphinx"` stanza.)

## Dependency invariance at the bumped tree

```
git diff -U0 v0.9.6 -- pyproject.toml
diff --git a/pyproject.toml b/pyproject.toml
index ea60e35d..aae2ad62 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -7 +7 @@ name = "typsphinx"
-version = "0.9.6"
+version = "0.9.7"
```

The changed lines are exactly the removed `version = "0.9.6"` and the added `version = "0.9.7"` —
no dependency table changed.

PYPROJECT_DEP_TABLES_UNCHANGED = yes

```
git show v0.9.6:uv.lock | grep -A1 -xF '[[package]]' | sed -n 's/^name = "\(.*\)"$/\1/p' | LC_ALL=C sort | sha256sum
aafccad7c3f1d4cffdfbb3b5fc2963b2fa9428a56aae2714a5235b52fd66f6bd  -

grep -A1 -xF '[[package]]' uv.lock | sed -n 's/^name = "\(.*\)"$/\1/p' | LC_ALL=C sort | sha256sum
aafccad7c3f1d4cffdfbb3b5fc2963b2fa9428a56aae2714a5235b52fd66f6bd  -
```

The two digests match — the package-name set of `uv.lock` is identical to the `v0.9.6` tag's.

UV_LOCK_PACKAGE_SET_UNCHANGED = yes

`README.md`'s Status line edited to read `**Status**: Stable (v0.9.7) - Production ready`,
keeping the wording `_STATUS_LINE_RE` (`tests/test_readme_version_sync.py`) requires.

## After

The same three reads as § Before, plus the imported version:

```
grep -n '^version = ' pyproject.toml
7:version = "0.9.7"

grep -n '\*\*Status\*\*: Stable' README.md
348:**Status**: Stable (v0.9.7) - Production ready

grep -n -A1 -xF 'name = "typsphinx"' uv.lock
1527:name = "typsphinx"
1528-version = "0.9.7"

uv run --no-sync python -c "import typsphinx; print(typsphinx.__version__)"
0.9.7
```

IMPORTED_VERSION = 0.9.7

### Surface / Before / After

| Surface | Before | After |
|---|---|---|
| `pyproject.toml:7` | `version = "0.9.6"` | `version = "0.9.7"` |
| `README.md:348` | `**Status**: Stable (v0.9.6) - Production ready` | `**Status**: Stable (v0.9.7) - Production ready` |
| `uv.lock:1527-1528` (`typsphinx` stanza) | `version = "0.9.6"` | `version = "0.9.7"` |
| Imported `typsphinx.__version__` | n/a | `0.9.7` |

## Version-sync gates

```
LC_ALL=C uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q -rs -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac30e4db427ca86b6
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_readme_version_sync.py .                                      [ 25%]
tests/test_preview_version_sync.py ...                                   [100%]

============================== 4 passed in 0.02s ===============================
```

No `SKIPPED` lines.

READMESYNC_PREVIEW_EXIT = 0

```
grep -ho '@preview/[a-z-]*:' typsphinx/templates/base.typ | sort -u | wc -l
4
```

PREVIEW_PACKAGE_COUNT = 4

## Commit

Only this file, `77-BUMP-EVIDENCE.md`, was staged and committed here, by explicit path. The three
product edits (`pyproject.toml`, `uv.lock`, `README.md`) stayed uncommitted for Task 3's single
five-file commit.

## The one commit

Before staging, the working tree carried exactly the five product files and nothing else:

```
git status --porcelain -- . ':(exclude).planning'
 M CHANGELOG.md
 M README.md
 M pyproject.toml
 M tests/test_changelog_page_gate.py
 M uv.lock
```

No unexpected product change — no `## HALT` needed.

Staged by explicit path:

```
git add pyproject.toml uv.lock README.md CHANGELOG.md tests/test_changelog_page_gate.py
```

Committed with a plain `git commit`, subject `chore(release): prepare 0.9.7` (names the 0.9.7
release prep, not a GSD plan number).

```
git show --name-only --format='%H %s' HEAD
39cb79f970c4137d4238023e1df7291c7c282c3a chore(release): prepare 0.9.7

CHANGELOG.md
README.md
pyproject.toml
tests/test_changelog_page_gate.py
uv.lock
```

BUMP_COMMIT_SHA = 39cb79f970c4137d4238023e1df7291c7c282c3a

BUMP_COMMIT_FILES = CHANGELOG.md|README.md|pyproject.toml|tests/test_changelog_page_gate.py|uv.lock
(the `LC_ALL=C`-sorted, `|`-joined file list from `git show --name-only`.)

SC#1 names four files (`pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`); the Phase
75-carried union adds `tests/test_changelog_page_gate.py`. The bump and the curation share one
commit so a commit touching only `pyproject.toml` — the shape that once stalled every dependency
pull request — cannot exist.

After the commit, the working tree has no remaining product change:

```
git status --porcelain -- . ':(exclude).planning'
```
prints nothing.
