# Phase 70 — Conversion: template_engine.py and template_registry.py

BASE_70_06 = 6d75e9d5b9254be7f3ff3712b61878a7ae85d332
(from `git rev-parse HEAD` at the start of this plan's execution, before any commit)

## Head check and provisioning

Fresh measurements at the start of this plan's execution, in this worktree.

```
$ date -u +%FT%TZ
2026-09-13T05:03:40Z
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-acffb38d5a3b4d554
$ test -f .git; echo "exit:$?"
exit:0
$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo SHIM_OK
SHIM_OK
```

Preconditions (task 1's `<precondition>`), each checked before any conversion:

```
$ grep -n "^PILOT_TRANSLATOR\|^PILOT_LEDGER\|^CONTROL_RENAME\|^CONTROL_IMPORT\|^MASK_HARNESS_SHA256" .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-MASK-PILOT-EVIDENCE.md
252:MASK_HARNESS_SHA256 = 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65
295:PILOT_TRANSLATOR = EQUAL
306:PILOT_LEDGER = EQUAL
327:CONTROL_RENAME = DIFFER
339:CONTROL_IMPORT = DIFFER
$ grep -q '^## HALT' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-MASK-PILOT-EVIDENCE.md && echo HALT_FOUND || echo NO_HALT
NO_HALT
```
`70-MASK-PILOT-EVIDENCE.md` holds `PILOT_TRANSLATOR = EQUAL`, `PILOT_LEDGER = EQUAL`,
`CONTROL_RENAME = DIFFER` and `CONTROL_IMPORT = DIFFER` with no HALT heading, and the harness
block's own hash equals `MASK_HARNESS_SHA256` (verified below).

```
$ git log --format=%H 697a113221a8a267d7e8c6dd1f2b95672f9454d2..HEAD -- CLAUDE.md
3c5e281cccf7efea39fe38ffc10c72ebe74d95fa
$ git merge-base --is-ancestor 3c5e281cccf7efea39fe38ffc10c72ebe74d95fa HEAD; echo "isanc:$?"
isanc:0
```
The single CLAUDE.md commit since `PHASE_BASE_SHA` is exactly one commit, and it is an ancestor
of HEAD.

```
$ git diff --quiet 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD -- typsphinx/template_engine.py typsphinx/template_registry.py; echo "diffexit:$?"
diffexit:0
```
Neither file changed between `PHASE_BASE_SHA` and this plan's fork point — the conversion below
is the first edit either file receives.

```
$ H="$(sed -n '/^~~~python mask-harness$/,/^~~~$/p' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-MASK-PILOT-EVIDENCE.md | sed '1d;$d')"; printf '%s\n' "$H" | sha256sum
11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65  -
```
Matches `MASK_HARNESS_SHA256` exactly. All preconditions met — no HALT.

Provisioning: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`
exited 0, installing 90+ packages including `typsphinx==0.9.2` (editable, this worktree's own path).

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

With `P="typsphinx/template_engine.py typsphinx/template_registry.py"`:

```
$ uv run ruff check $P --select UP006,UP035 --output-format=concise
typsphinx/template_engine.py:13:1: UP035 `typing.Dict` is deprecated, use `dict` instead
typsphinx/template_engine.py:13:1: UP035 `typing.List` is deprecated, use `list` instead
typsphinx/template_engine.py:110:21: UP006 [*] Use `dict` instead of `Dict` for type annotation
typsphinx/template_engine.py:262:23: UP006 [*] Use `list` instead of `List` for type annotation
typsphinx/template_engine.py:263:28: UP006 [*] Use `dict` instead of `Dict` for type annotation
typsphinx/template_engine.py:266:32: UP006 [*] Use `list` instead of `List` for type annotation
typsphinx/template_engine.py:468:26: UP006 [*] Use `dict` instead of `Dict` for type annotation
typsphinx/template_engine.py:469:25: UP006 [*] Use `dict` instead of `Dict` for type annotation
typsphinx/template_engine.py:470:10: UP006 [*] Use `dict` instead of `Dict` for type annotation
typsphinx/template_engine.py:505:17: UP006 [*] Use `dict` instead of `Dict` for type annotation
typsphinx/template_engine.py:604:56: UP006 [*] Use `dict` instead of `Dict` for type annotation
typsphinx/template_engine.py:665:23: UP006 [*] Use `dict` instead of `Dict` for type annotation
typsphinx/template_registry.py:29:1: UP035 `typing.Dict` is deprecated, use `dict` instead
typsphinx/template_registry.py:215:6: UP006 [*] Use `dict` instead of `Dict` for type annotation
typsphinx/template_registry.py:469:15: UP006 [*] Use `dict` instead of `Dict` for type annotation
typsphinx/template_registry.py:495:15: UP006 [*] Use `dict` instead of `Dict` for type annotation
Found 16 errors.
[*] 13 fixable with the `--fix` option.
exit:1
```
16 findings (12 `template_engine.py` + 4 `template_registry.py`), matching
`70-BASELINE-EVIDENCE.md`'s per-file breakdown exactly. Non-zero count confirmed before any fix.

Pass 1: `uv run ruff check $P --select UP006,UP035 --fix`
```
Found 16 errors (13 fixed, 3 remaining).
exit:1
```
The 3 remaining are the two files' own `from typing import ...` header lines (one UP035
diagnostic per removed name: 2 on `template_engine.py:13`, 1 on `template_registry.py:29`) — not
independently fixable by the `--select`-scoped pass because the header line's own rewrite
(dropping the removed names, leaving `Any` alone) is a config-rule concern (`F401`), which pass 2
covers.

Pass 2: `uv run ruff check $P --fix`
```
Found 3 errors (3 fixed, 0 remaining).
exit:0
```
This pass used the config rule (F401 unused-import), shrinking both header lines in place to
`from typing import Any`. Neither line moved or vanished — both files keep `Any` in use elsewhere
(`Any | None` parameters, `Dict[str, Any]` → `dict[str, Any]` bodies), so this is the
shrink-in-place shape, not the import-split or import-vanish shape 70-04's ledger-gate file
exercised.

No hand edit was made in either file. `sed`, `--preview` and `--unsafe-fixes` were never invoked.

Confirming both scoped and config-rule passes now exit 0:
```
$ uv run ruff check $P --select UP006,UP035
All checks passed!
exit1:0
$ uv run ruff check $P
All checks passed!
exit2:0
```

`git diff --stat -- $P`:
```
 typsphinx/template_engine.py   | 22 +++++++++++-----------
 typsphinx/template_registry.py |  8 ++++----
 2 files changed, 15 insertions(+), 15 deletions(-)
```

Both typing import lines, quoted after conversion:
```
$ sed -n '13p' typsphinx/template_engine.py
from typing import Any
$ sed -n '29p' typsphinx/template_registry.py
from typing import Any
```

Full `git diff -- typsphinx/template_engine.py`:
```diff
diff --git a/typsphinx/template_engine.py b/typsphinx/template_engine.py
index 21de2218..844af521 100644
--- a/typsphinx/template_engine.py
+++ b/typsphinx/template_engine.py
@@ -10,7 +10,7 @@ import logging
 import re
 from dataclasses import dataclass
 from pathlib import Path
-from typing import Any, Dict, List
+from typing import Any
 
 from sphinx.errors import ExtensionError
 
@@ -107,7 +107,7 @@ class _ElementsEmissionKind:
 # introspected from Python, and most `project()` params (title/authors/date/
 # toctree_*) already arrive via `parameter_mapping`/`extract_toctree_options`
 # -- adding them here would create a second, colliding source of truth.
-ELEMENTS_ALLOWLIST: Dict[str, str] = {
+ELEMENTS_ALLOWLIST: dict[str, str] = {
     "papersize": _ElementsEmissionKind.STRING,
     "fontsize": _ElementsEmissionKind.RAW,
     "lang": _ElementsEmissionKind.STRING,
@@ -259,11 +259,11 @@ class TemplateEngine:
         self,
         template_path: str | None = None,
         template_name: str | None = None,
-        search_paths: List[str] | None = None,
-        parameter_mapping: Dict[str, str] | None = None,
+        search_paths: list[str] | None = None,
+        parameter_mapping: dict[str, str] | None = None,
         typst_package: str | None = None,
         typst_template_function: Any | None = None,
-        typst_package_imports: List[str] | None = None,
+        typst_package_imports: list[str] | None = None,
     ):
         """
         Initialize TemplateEngine.
@@ -465,9 +465,9 @@ class TemplateEngine:
 
     def map_parameters(
         self,
-        sphinx_metadata: Dict[str, Any],
-        typst_elements: Dict[str, Any] | None = None,
-    ) -> Dict[str, Any]:
+        sphinx_metadata: dict[str, Any],
+        typst_elements: dict[str, Any] | None = None,
+    ) -> dict[str, Any]:
         """
         Map Sphinx metadata to template parameters.
 
@@ -502,7 +502,7 @@ class TemplateEngine:
         # `_convert_to_authors_tuple`, etc.), and every other key's
         # differently-typed assignment later in the method would then be a
         # type error.
-        params: Dict[str, Any] = {}
+        params: dict[str, Any] = {}
 
         # CONF-10/D-F removed the dict-of-dicts author-details config value
         # that used to seed params["authors"] unconditionally here, before
@@ -601,7 +601,7 @@ class TemplateEngine:
             # Import entire module: #import "@package:version"
             return f'#import "{self.typst_package}"'
 
-    def extract_toctree_options(self, doctree: Any) -> Dict[str, Any]:
+    def extract_toctree_options(self, doctree: Any) -> dict[str, Any]:
         """
         Extract toctree options from doctree for template parameters.
 
@@ -662,7 +662,7 @@ class TemplateEngine:
         return template
 
     def render(
-        self, params: Dict[str, Any], body: str, template_file: str = None
+        self, params: dict[str, Any], body: str, template_file: str = None
     ) -> str:
         """
         Render final Typst document with template and body.
```

Full `git diff -- typsphinx/template_registry.py`:
```diff
diff --git a/typsphinx/template_registry.py b/typsphinx/template_registry.py
index 55bd19df..52a064f1 100644
--- a/typsphinx/template_registry.py
+++ b/typsphinx/template_registry.py
@@ -26,7 +26,7 @@ This module adds zero new runtime dependencies -- only stdlib.
 
 import os
 from dataclasses import dataclass
-from typing import Any, Dict
+from typing import Any
 
 from sphinx.errors import ExtensionError
 
@@ -212,7 +212,7 @@ class TemplateRegistryEntry:
 
 def resolve_template_registry(
     config: Any, srcdir: str
-) -> Dict[str, TemplateRegistryEntry]:
+) -> dict[str, TemplateRegistryEntry]:
     """Resolve every declared ``typst_document_templates`` entry into a
     ``TemplateRegistryEntry``, plus the synthesized built-in ``"typst"``
     key -- after validating every declared key (D-05, order-independent
@@ -466,7 +466,7 @@ def resolve_template_registry(
     # already proven every key is a `str` and every definition is a `dict`
     # or falsy -- a second, independent guard here would be redundant
     # state that could drift from the first.
-    registry: Dict[str, TemplateRegistryEntry] = {}
+    registry: dict[str, TemplateRegistryEntry] = {}
     for key, definition in declared.items():
         definition = definition or {}
         registry[key] = TemplateRegistryEntry(
@@ -492,7 +492,7 @@ def resolve_template_registry(
 
 
 def resolve_registry_key(
-    registry: Dict[str, TemplateRegistryEntry], entry: tuple
+    registry: dict[str, TemplateRegistryEntry], entry: tuple
 ) -> TemplateRegistryEntry:
     """Resolve one ``typst_documents`` tuple's registry key (TPL-04) to
     its ``TemplateRegistryEntry``.
```

Every changed line is a typing-name rename or the import-line shrink (confirmed structurally by
the Task 2 changed-line census below). Neither diff touches a `@preview` import string or the
docstring prose at `template_engine.py:274`/`:819` — confirmed:
```
$ git diff -- typsphinx/template_engine.py | grep -F '@preview'
(empty)
$ git diff -- typsphinx/template_engine.py | grep -E 'List of directories|Tuple of author names'
(empty)
```

Commit: `a7f35d33` — `refactor(70-06): move template_engine.py and template_registry.py onto builtin generics (QUA-11)`,
touching only the two files.

## Leg (a)

For each file, the masked hash of the working-tree (converted) file is compared against the
masked hash of the same path read from `PHASE_BASE_SHA`
(`697a113221a8a267d7e8c6dd1f2b95672f9454d2`).

```
$ git show 697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/template_engine.py | sk
7288a028075f8d778fdfa1a64ae89ea5af60a8ac720e6e30d222bc77e6c8d822
$ sk < typsphinx/template_engine.py
7288a028075f8d778fdfa1a64ae89ea5af60a8ac720e6e30d222bc77e6c8d822
```

TEMPLATE_ENGINE_MASK = EQUAL

```
$ git show 697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/template_registry.py | sk
655662483067c768432fe0ddcd6bb8ad9c101b50897a7ae4fb8ce0db77e421dc
$ sk < typsphinx/template_registry.py
655662483067c768432fe0ddcd6bb8ad9c101b50897a7ae4fb8ce0db77e421dc
```

TEMPLATE_REGISTRY_MASK = EQUAL

Both masked hashes equal base — no HALT needed.
