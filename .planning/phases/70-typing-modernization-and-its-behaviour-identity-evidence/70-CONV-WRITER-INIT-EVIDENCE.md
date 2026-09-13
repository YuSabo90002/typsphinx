# Phase 70 — Conversion: writer.py and __init__.py

BASE_70_07 = 6d75e9d5b9254be7f3ff3712b61878a7ae85d332
(from `git rev-parse HEAD` at the start of this plan's execution, before any commit)

## Head check and provisioning

Fresh measurements at the start of this plan's execution, in this worktree.

```
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9a3a29e4a793db3b
$ test -f .git; echo "exit:$?"
exit:0
$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo "SHIM_OK"
SHIM_OK
```

Preconditions (task 1's `<precondition>`), each checked before any conversion:

```
$ grep -n "^PILOT_TRANSLATOR\|^PILOT_LEDGER\|^CONTROL_RENAME\|^CONTROL_IMPORT\|^MASK_HARNESS_SHA256" .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-MASK-PILOT-EVIDENCE.md
MASK_HARNESS_SHA256 = 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65
PILOT_TRANSLATOR = EQUAL
PILOT_LEDGER = EQUAL
CONTROL_RENAME = DIFFER
CONTROL_IMPORT = DIFFER
$ grep -c '^## HALT' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-MASK-PILOT-EVIDENCE.md
0
```
`PILOT_TRANSLATOR = EQUAL`, `PILOT_LEDGER = EQUAL`, `CONTROL_RENAME = DIFFER`, `CONTROL_IMPORT = DIFFER`,
no HALT heading — all four precondition keys hold.

```
$ H="$(sed -n '/^~~~python mask-harness$/,/^~~~$/p' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-MASK-PILOT-EVIDENCE.md | sed '1d;$d')"
$ printf '%s\n' "$H" | sha256sum
11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65  -
```
The harness block hashes to `MASK_HARNESS_SHA256`.

```
$ BASE=697a113221a8a267d7e8c6dd1f2b95672f9454d2
$ git log --format=%H "$BASE"..HEAD -- CLAUDE.md
3c5e281cccf7efea39fe38ffc10c72ebe74d95fa
$ git log --format=%H "$BASE"..HEAD -- CLAUDE.md | grep -c .
1
$ git merge-base --is-ancestor 3c5e281cccf7efea39fe38ffc10c72ebe74d95fa 6d75e9d5b9254be7f3ff3712b61878a7ae85d332; echo "exit:$?"
exit:0
```
The single CLAUDE.md commit since `PHASE_BASE_SHA` (`3c5e281c`) is an ancestor of `BASE_70_07`.

```
$ git diff --quiet 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD -- typsphinx/writer.py typsphinx/__init__.py; echo "exit:$?"
exit:0
```
Neither file changed between `PHASE_BASE_SHA` and this plan's fork point — the conversion below is
the first edit either file receives.

Provisioning: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`
exited 0, installing 90 packages including `typsphinx==0.9.2` (editable, this worktree's own path).

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

Both keys equal 70-02's recorded `VENV_HOME`/`VENV_VERSION_INFO` exactly — same interpreter,
confirming constraint 6.

## Conversion

With `P="typsphinx/writer.py typsphinx/__init__.py"`:

```
$ uv run ruff check $P --select UP006,UP035 --output-format=concise
typsphinx/__init__.py:15:1: UP035 `typing.Dict` is deprecated, use `dict` instead
typsphinx/__init__.py:29:27: UP006 [*] Use `dict` instead of `Dict` for type annotation
typsphinx/writer.py:10:1: UP035 `typing.Tuple` is deprecated, use `tuple` instead
typsphinx/writer.py:284:20: UP006 [*] Use `tuple` instead of `Tuple` for type annotation
Found 4 errors.
[*] 2 fixable with the `--fix` option.
exit:1
```
4 findings (2 per file), matching `70-BASELINE-EVIDENCE.md`'s per-file counts
(`typsphinx/writer.py` 2, `typsphinx/__init__.py` 2). Non-zero count confirmed before any fix.

Pass 1: `uv run ruff check $P --select UP006,UP035 --fix`
```
UP035 `typing.Dict` is deprecated, use `dict` instead
  --> typsphinx/__init__.py:15:1
UP035 `typing.Tuple` is deprecated, use `tuple` instead
  --> typsphinx/writer.py:10:1
Found 4 errors (2 fixed, 2 remaining).
exit:1
```
The 2 UP006 usages (`Dict[str, Any]` at `__init__.py:29`, `Tuple[str, ...]` at `writer.py:284`) were
fixed. The 2 remaining are the two files' own `from typing import ...` header lines (one UP035
diagnostic per file) — not independently fixable by the `--select`-scoped pass because the header
line's own rewrite is a config-rule concern (I001/F401), which pass 2 covers.

Pass 2: `uv run ruff check $P --fix`
```
F401 `typing.Dict` imported but unused
  --> typsphinx/__init__.py:15:25
help: Remove unused import: `typing.Dict`
Found 2 errors (1 fixed, 1 remaining).
exit:1
```
This pass used the config rules (F401 unused-import): `typsphinx/writer.py`'s header line
`from typing import Any, Tuple` shrank to `from typing import Any` (its `Tuple` import became
unused once pass 1 converted the sole usage to `tuple`, and F401 removes it — writer.py is not
`__init__.py`, so the carve-out does not apply). `typsphinx/__init__.py`'s `from typing import Any,
Dict` line is left untouched: ruff reports F401 but offers no fix (no `[*]` marker), because
`typsphinx/__init__.py` is a package `__init__.py` file and ruff withholds unused-import fixes there
unless `--preview` is enabled — this is the documented survivor.

No hand edit was made to `writer.py`. `sed`, `--preview` and `--unsafe-fixes` were never invoked.

Confirming the two remaining diagnostics are both on `typsphinx/__init__.py` line 15:
```
$ uv run ruff check $P --select UP006,UP035 --output-format=concise
typsphinx/__init__.py:15:1: UP035 `typing.Dict` is deprecated, use `dict` instead
Found 1 error.
exit1:1
$ uv run ruff check $P --output-format=concise
typsphinx/__init__.py:15:25: F401 `typing.Dict` imported but unused
Found 1 error.
exit2:1
```

INIT_SURVIVOR_COUNT = 2
(one UP035 under `--select`, one F401 with no fix offered under the config rules — both on
`typsphinx/__init__.py` line 15; nothing else remains on either file, no `## HALT: unexpected
residue` needed)

`git diff --stat -- $P` at this point:
```
 typsphinx/__init__.py | 2 +-
 typsphinx/writer.py   | 4 ++--
 3 files changed, 3 insertions(+), 3 deletions(-)
```

## Hand edit

Used the Edit tool to change `typsphinx/__init__.py` line 15 from
`from typing import Any, Dict` to `from typing import Any`. No `sed`, `--preview` or
`--unsafe-fixes` were used — this is the only manual line edit in the phase.

```
$ sed -n 15p typsphinx/__init__.py
from typing import Any
```

INIT_LINE_15 = from typing import Any

```
$ uv run ruff check typsphinx/writer.py typsphinx/__init__.py --select UP006,UP035
All checks passed!
exit1:0
$ uv run ruff check typsphinx/writer.py typsphinx/__init__.py
All checks passed!
exit2:0
```
Both scoped and config-rule ruff checks exit 0 on the two files.

`git status --short` immediately before commit:
```
 M typsphinx/__init__.py
 M typsphinx/writer.py
```
Only the two target files are modified — no other file touched.

Commit: `47159f96` — `refactor(70-07): move writer.py and __init__.py onto builtin generics
(QUA-11)`, touching only the two files (`git diff --diff-filter=D --name-only HEAD~1 HEAD` empty —
no deletions).

Full `git diff -- typsphinx/writer.py typsphinx/__init__.py` (the entire conversion, both files):
```diff
diff --git a/typsphinx/__init__.py b/typsphinx/__init__.py
index 8fc0f95c..d98e01da 100644
--- a/typsphinx/__init__.py
+++ b/typsphinx/__init__.py
@@ -12,7 +12,7 @@ sources using Sphinx, which can then be compiled to PDF using the Typst compiler
 """
 
 import importlib.metadata
-from typing import Any, Dict
+from typing import Any
 
 from sphinx.application import Sphinx
 
@@ -26,7 +26,7 @@ from typsphinx.builder import TypstBuilder, TypstPDFBuilder, _default_typst_docu
 from typsphinx.removed_config import check_config_at_init
 
 
-def setup(app: Sphinx) -> Dict[str, Any]:
+def setup(app: Sphinx) -> dict[str, Any]:
     """
     Sphinx extension setup function.
 
diff --git a/typsphinx/writer.py b/typsphinx/writer.py
index 2e4f6269..ae4ac519 100644
--- a/typsphinx/writer.py
+++ b/typsphinx/writer.py
@@ -7,7 +7,7 @@ document trees to Typst markup.
 
 import posixpath
 from pathlib import PurePosixPath
-from typing import Any, Tuple
+from typing import Any
 
 from docutils import writers
 from sphinx.util import logging
@@ -281,7 +281,7 @@ class TypstWriter(writers.Writer):
         doctree: Any,
         wrapper_relative_dir: str,
         content_relative_path: str,
-        edge_keys: Tuple[str, ...] = (),
+        edge_keys: tuple[str, ...] = (),
         template_entry: TemplateRegistryEntry | None = None,
     ) -> str:
         """
```
Every changed line carries a typing name (`Dict`/`Tuple`/`dict`/`tuple`/`typing`), confirmed in full
by the Task 2 changed-line census below.

## Leg (a)

For each file, the masked hash of the working-tree (converted) file is compared against the masked
hash of the same path read from `PHASE_BASE_SHA` (`697a113221a8a267d7e8c6dd1f2b95672f9454d2`),
using the harness extracted and hash-checked above.

```
$ git show 697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/writer.py | sk
ef10bdb40b105c61d0bdaa73749ffa62c1050a93a1833ae41cdf1f40fdc9bc08
$ sk < typsphinx/writer.py
ef10bdb40b105c61d0bdaa73749ffa62c1050a93a1833ae41cdf1f40fdc9bc08
```

WRITER_MASK = EQUAL

```
$ git show 697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/__init__.py | sk
6b44c4dc942282ea3b94733831b5f343793d9ec453fa5fcde7899d6da1d34b7b
$ sk < typsphinx/__init__.py
6b44c4dc942282ea3b94733831b5f343793d9ec453fa5fcde7899d6da1d34b7b
```

INIT_MASK = EQUAL

Both pairs are 64-character hex digests and equal. Additionally, both files DO differ from base at
the raw text level (`git diff --quiet` exits 1 for each — confirmed in "Head check and
provisioning" is for the pre-conversion state; post-conversion:
```
$ git diff --quiet 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD -- typsphinx/writer.py; echo "exit:$?"
exit:1
$ git diff --quiet 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD -- typsphinx/__init__.py; echo "exit:$?"
exit:1
```
), so the equal masked hashes are proving structural equivalence under the annotation/import mask,
not a no-op edit. No HALT needed.

Evidence file committed alongside this record.
