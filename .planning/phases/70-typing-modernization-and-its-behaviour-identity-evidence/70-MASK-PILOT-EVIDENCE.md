# Phase 70 — Mask Pilot and Tracer Conversion

BASE_70_04 = 5f50d7ee849120b9c3e9854856c59c67d2deb445
(from `git rev-parse HEAD` at the start of this plan's execution, before any commit)

SCRATCH_70_04 = /tmp/tmp.ATDpvMmXic

## Head check and provisioning

Fresh measurements at the start of this plan's execution, in this worktree.

```
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9e31f5eabd23bb47
$ test -f .git; echo "exit:$?"
exit:0
$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo "SHIM_OK"
SHIM_OK
```

Preconditions (task 1's `<precondition>`), each checked before any conversion:

```
$ sed -n 75p CLAUDE.md
- **Python 3.12+ is required.** Annotations use builtin generics (`dict[str, Any]`, `list[str]`,
  `set[str]`, `tuple[str, ...]`) and take abstract types such as `Iterator` from `collections.abc`,
  not `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`.
```
Line 75 contains `collections.abc` and not `todos/pending` — the flip-dependent claim and the todo
path are both absent, confirming 70-01's rewrite is in place at this fork point.

```
$ grep -n "^UP_FILES_MATCH_PLAN\|^PHASE_BASE_SHA" .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-BASELINE-EVIDENCE.md
PHASE_BASE_SHA = 697a113221a8a267d7e8c6dd1f2b95672f9454d2
UP_FILES_MATCH_PLAN = YES
$ grep -q '^## HALT' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-BASELINE-EVIDENCE.md && echo HALT_FOUND || echo NO_HALT
NO_HALT
```
`70-BASELINE-EVIDENCE.md` holds `PHASE_BASE_SHA` and `UP_FILES_MATCH_PLAN = YES` with no HALT heading.

```
$ git diff --quiet 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD -- typsphinx/translator.py tests/test_include_ledger_removal_gate.py; echo "exit:$?"
exit:0
```
Neither file changed between `PHASE_BASE_SHA` and this plan's fork point — the conversion below is
the first edit either file receives.

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

With `P="typsphinx/translator.py tests/test_include_ledger_removal_gate.py"`:

```
$ uv run ruff check $P --select UP006,UP035 --output-format=concise
[... 51 diagnostic lines across the two files ...]
Found 51 errors.
[*] 46 fixable with the `--fix` option.
```
Non-zero finding count (51) confirmed before any fix.

Pass 1: `uv run ruff check $P --select UP006,UP035 --fix`
```
Found 51 errors (46 fixed, 5 remaining).
exit:1
```
The 5 remaining are the two files' own `from typing import ...` header lines (one UP035 diagnostic
per removed name: 3 on `translator.py:9`, 2 on `tests/test_include_ledger_removal_gate.py:47`) —
not independently fixable by the `--select`-scoped pass because the header line's own rewrite
(splitting `Iterator` into a new `collections.abc` import, dropping the removed names) is a
config-rule concern (`I001`/`F401`), which pass 2 covers.

Pass 2: `uv run ruff check $P --fix`
```
Found 6 errors (6 fixed, 0 remaining).
exit:0
```
This pass used the config rules (I001 import-sort, F401 unused-import), rewriting the two files'
header lines: `tests/test_include_ledger_removal_gate.py`'s `from typing import Dict, Iterator, Set`
split into `from collections.abc import Iterator` (new line, sorted before `from pathlib import
Path` per isort's module-group ordering) and `from typing import Dict, Set` (which itself later
converts to nothing once `Dict`/`Set` become `dict`/`set`, since no other `typing` name is used in
this file); `typsphinx/translator.py`'s header shrank in place to `from typing import Any,
NamedTuple`.

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
 tests/test_include_ledger_removal_gate.py | 14 ++++----
 typsphinx/translator.py                   | 58 +++++++++++++++----------------
 2 files changed, 36 insertions(+), 36 deletions(-)
```

Full `git diff -- tests/test_include_ledger_removal_gate.py`:
```diff
diff --git a/tests/test_include_ledger_removal_gate.py b/tests/test_include_ledger_removal_gate.py
index ae57fea0..6febd197 100644
--- a/tests/test_include_ledger_removal_gate.py
+++ b/tests/test_include_ledger_removal_gate.py
@@ -43,8 +43,8 @@ import re
 import subprocess
 import sys
 import textwrap
+from collections.abc import Iterator
 from pathlib import Path
-from typing import Dict, Iterator, Set
 
 import pytest
 from sphinx.testing.util import SphinxTestApp
@@ -351,14 +351,14 @@ def _reconstruct_fstring_shape(node: ast.JoinedStr) -> str:
     return "".join(parts)
 
 
-def _collect_docstring_constant_ids(tree: ast.AST) -> Set[int]:
+def _collect_docstring_constant_ids(tree: ast.AST) -> set[int]:
     """Return the ``id()`` of every AST ``Constant`` node that IS a
     module/class/function docstring (its containing body's own first
     statement, a bare string expression) -- so a docstring's own worked
     example (e.g. ``render_include_edge_state()``'s ``Returns:`` section)
     is excluded from the state-call literal collection below, which is
     about genuine emission SITES, not documentation."""
-    ids: Set[int] = set()
+    ids: set[int] = set()
     for node in ast.walk(tree):
         if isinstance(
             node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
@@ -371,12 +371,12 @@ def _collect_docstring_constant_ids(tree: ast.AST) -> Set[int]:
     return ids
 
 
-def _module_level_string_constants(tree: ast.Module) -> Dict[str, str]:
+def _module_level_string_constants(tree: ast.Module) -> dict[str, str]:
     """Collect every module-level ``NAME = "literal"`` / ``NAME: T =
     "literal"`` assignment's own resolved string value, keyed by name --
     used to resolve a ``{NAME}`` f-string interpolation captured inside a
     ``state(...)`` call site back to its own literal value."""
-    constants: Dict[str, str] = {}
+    constants: dict[str, str] = {}
     for node in tree.body:
         if (
             isinstance(node, ast.Assign)
@@ -397,7 +397,7 @@ def _module_level_string_constants(tree: ast.Module) -> Dict[str, str]:
     return constants
 
 
-def _collect_state_call_first_arg_literals(root: Path) -> Set[str]:
+def _collect_state_call_first_arg_literals(root: Path) -> set[str]:
     """Collect every DISTINCT resolved literal string passed as the
     first argument to a Typst ``state(...)`` call, across every ``.py``
     file under ``root`` -- collected STRUCTURALLY via ``ast``, not
@@ -409,7 +409,7 @@ def _module_level_string_constants(tree: ast.Module) -> Dict[str, str]:
     own module/class/function DOCSTRING is explicitly excluded (see
     ``_collect_docstring_constant_ids``) -- a second spelling would be
     detected here, not assumed absent."""
-    literals: Set[str] = set()
+    literals: set[str] = set()
     for path in _iter_python_files(root):
         tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
         docstring_ids = _collect_docstring_constant_ids(tree)
```

`typsphinx/translator.py`'s diff (58 lines, all `Dict`/`List`/`Tuple` → `dict`/`list`/`tuple`
renames plus the one header-line shrink) is omitted here for length; every changed line matches a
typing name, confirmed by the Task 2 changed-line census below. Line 9 is now
`from typing import Any, NamedTuple`; line 773 (`str | list[str] | None`, only the inner name
converted, `|` count unchanged) and line 126 (`xref: tuple[str, str] | None`) were spot-read after
the fix and match `70-PATTERNS.md`'s predicted shape exactly.

Commit: `b4d044d4` — `refactor(70-04): move translator.py and the ledger gate onto builtin generics (QUA-11)`,
touching only the two files.

## Mask harness

The harness is RESEARCH.md's `Mask` class (§ Leg (a)), unchanged in behaviour. It reads source from
stdin, applies `Mask().visit`, calls `ast.fix_missing_locations`, and prints the SHA-256 hex digest
of `ast.dump(tree, annotate_fields=True, include_attributes=False)`.

~~~python mask-harness
import ast
import hashlib
import sys


class Mask(ast.NodeTransformer):
    def visit_ImportFrom(self, node):
        if node.module in ("typing", "collections.abc"):
            return None
        return node

    def visit_FunctionDef(self, node):
        return self._mask_func(node)

    def visit_AsyncFunctionDef(self, node):
        return self._mask_func(node)

    def _mask_func(self, node):
        self.generic_visit(node)
        node.returns = None
        a = node.args
        for arg in a.posonlyargs + a.args + a.kwonlyargs:
            arg.annotation = None
        if a.vararg:
            a.vararg.annotation = None
        if a.kwarg:
            a.kwarg.annotation = None
        return node

    def visit_AnnAssign(self, node):
        self.generic_visit(node)
        node.annotation = ast.Constant(value=None)
        return node


t = ast.parse(sys.stdin.read())
t = Mask().visit(t)
ast.fix_missing_locations(t)
print(
    hashlib.sha256(
        ast.dump(t, annotate_fields=True, include_attributes=False).encode()
    ).hexdigest()
)
~~~

MASK_HARNESS_SHA256 = 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65
(first field of `sed -n '/^~~~python mask-harness$/,/^~~~$/p' "$F" | sed '1d;$d' | sha256sum` — the
exact extraction every later verify uses)

Helper definition, exactly as every later verify extracts and runs it:
```bash
H="$(sed -n '/^~~~python mask-harness$/,/^~~~$/p' "$F" | sed '1d;$d')"
sk() { uv run python -c "$H"; }
```

Why the `ImportFrom` node is DELETED (`return None`) rather than blanked in place (RESEARCH
Pitfall 6): three shapes occur across the phase's ten conversion-target files — an import line can
shrink in place (`translator.py`'s `Any, Dict, List, NamedTuple, Tuple` → `Any, NamedTuple`), move
(`Iterator` resorting into a new `collections.abc` line, this plan's ledger-gate file), or vanish
entirely (no `typing` name survives). Setting `node.names = []` / `node.module = "<MASKED>"` while
leaving the (now-empty) node at its original body position still participates in `ast.dump()`'s
output via its position relative to sibling statements, so a move or vanish produces a spurious
`DIFFER` even on a correct conversion — confirmed this plan's own pilot below only reaches `EQUAL`
on the ledger-gate file (a move-and-split case) once `visit_ImportFrom` returns `None` instead of a
mutated node.

What this leg does not prove on its own: because the entire `ImportFrom` node is deleted before
hashing, an equal masked hash proves the non-import, non-annotation code is structurally unchanged —
no statement, expression, call or control-flow node moved, was added, or was removed — but it does
not independently prove the import list itself is *correct* (e.g., that a legitimately-used `Any`
import wasn't accidentally dropped, since any annotation referencing `Any` is also nulled by the
annotation mask regardless of whether `Any` stayed imported). That gap is closed by leg (e) (`mypy
typsphinx/`, which would flag an undefined `Any`/`NamedTuple` name) and leg (b) (pytest collection,
which would fail to import a `tests/` module with a broken import) — Task 2 below runs both against
this plan's own conversion.

## Pilot (SC#3)

For each of the two files, the masked hash of the working-tree (converted) file is compared against
the masked hash of the same path read from `PHASE_BASE_SHA` (`697a113221a8a267d7e8c6dd1f2b95672f9454d2`).

```
$ git show 697a113221a8a267d7e8c6dd1f2b95672f9454d2:typsphinx/translator.py | sk
8c766e23d771c614aa166b6ebe9ea481b8969a9b0726ed31eea2b176afe3c329
$ sk < typsphinx/translator.py
8c766e23d771c614aa166b6ebe9ea481b8969a9b0726ed31eea2b176afe3c329
```

PILOT_TRANSLATOR = EQUAL
(shrink-in-place: the typing line keeps `Any, NamedTuple`; hash matches RESEARCH.md's own recorded
`8c766e23...` for this file)

```
$ git show 697a113221a8a267d7e8c6dd1f2b95672f9454d2:tests/test_include_ledger_removal_gate.py | sk
6af6dd86276c3acb15479940e325e6db77931ec60d7b0a444c7d2e3bc7204849
$ sk < tests/test_include_ledger_removal_gate.py
6af6dd86276c3acb15479940e325e6db77931ec60d7b0a444c7d2e3bc7204849
```

PILOT_LEDGER = EQUAL
(move and vanish: `Iterator` moves to `collections.abc`, and the `typing` line disappears entirely
once `Dict`/`Set` convert to `dict`/`set`)

Both pilot files hash EQUAL to base — no HALT needed.

## Non-vacuity controls

Work performed only in copies under `$S` (`/tmp/tmp.ATDpvMmXic`); the tracked tree was never edited
for these controls.

`typsphinx/translator.py` copied to `$S/rename.py` with the first `class TypstTranslator(` replaced
by `class TypstTranslatorZZZ(` via a `uv run python -c` string replace (`str.replace(...,
count=1)`, not `sed`):
```
$ sk < $S/rename.py
5c954eacaaed23319400a434ca5194560e7275ea033267e944d0b0ea0c6d8fb1
$ sk < typsphinx/translator.py
8c766e23d771c614aa166b6ebe9ea481b8969a9b0726ed31eea2b176afe3c329
```

CONTROL_RENAME = DIFFER
(matches RESEARCH.md's own recorded rename-control transition `8c766e23...` → `5c954eac...` exactly)

`tests/test_include_ledger_removal_gate.py` copied to `$S/noimport.py` with its `import textwrap`
line removed the same way:
```
$ sk < $S/noimport.py
28efd38f08dbe49bb4daf8a0730ca632e3c8a5e9ff90f039934b2b6b4aaa89c3
$ sk < tests/test_include_ledger_removal_gate.py
6af6dd86276c3acb15479940e325e6db77931ec60d7b0a444c7d2e3bc7204849
```

CONTROL_IMPORT = DIFFER

Both controls DIFFER from their originals — the mask is not vacuous. No HALT needed.

## Changed-line census

For the two files, over `git diff "$PHASE_BASE_SHA" HEAD`, with diff headers (`+++`/`---`) and
blank added/removed lines excluded:

```
$ git diff "$B" HEAD -- $P | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)( |$)' | grep -vE '^[+-][[:space:]]*$' \
    | grep -cvE '(Dict|List|Set|Tuple|Iterator|dict|list|set|tuple|typing|collections\.abc)'
0
```

NON_TYPING_LINES_70_04 = 0
(every non-blank changed line carries a typing name)

```
$ git diff "$B" HEAD -- $P | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)( |$)' | grep -cw assert
0
```

ASSERT_LINES_70_04 = 0
(no changed line contains the word `assert`)

```
$ git diff "$B" HEAD -- $P | grep -E '^[+-]' | grep -F '@preview'
(empty)
```
No changed line contains `@preview`.

```
$ git diff --quiet "$B" HEAD -- tests/test_authors_pipeline_stage_gate.py; echo "exit:$?"
exit:0
```
`tests/test_authors_pipeline_stage_gate.py` (the file whose `ast.Dict` at line 515 must stay
byte-identical) is untouched by this plan's conversion, confirmed by an empty diff.

## Gates

```
$ uv run black --check typsphinx/translator.py tests/test_include_ledger_removal_gate.py
All done! ✨ 🍰 ✨
2 files would be left unchanged.
exit:0
```

```
$ uv run ruff check .
All checks passed!
exit:0
```
Repo-wide, config-rule ruff is clean — the still-present `UP006`/`UP035` ignores mean this check
does not itself re-verify the two converted files' UP006/UP035 cleanliness (Task 1 already did,
with `--select` explicitly overriding the ignores); it confirms the conversion introduced no other
config-rule violation anywhere in the repo.

```
$ uv run mypy typsphinx/ 2>/dev/null
Success: no issues found in 9 source files
```

MYPY_STDOUT_SHA256_70_04 = 46984ca20bf69f7b14ec1fd9bd82101d56a4e109e68f016fd2a04f22481b09b3
(stdout only, stderr excluded per Pitfall 7 — equal to `MYPY_STDOUT_SHA256_BEFORE`)

```
$ LC_ALL=C uv run pytest -q -rs -p no:cacheprovider > "$S/pytest.out" 2>&1; echo "exit:$?"
exit:0
$ tail -n 1 "$S/pytest.out"
================= 1547 passed, 1 skipped in 129.06s (0:02:09) ==================
```

PYTEST_RESULT_70_04 = 1547 passed 1 skipped
(from the same `grep -oE '[0-9]+ (passed|failed|skipped|errors?|xfailed|xpassed)' | paste -sd' '`
extraction 70-02 used — equal to `PYTEST_RESULT_BEFORE`)

Both leg (e) (mypy) and leg (b) (pytest) are unchanged from base: the conversion altered no runtime
behaviour, no type-checking outcome, and no test outcome — closing the gap leg (a) alone leaves open
(import-list correctness), exactly as the Mask harness section above says it would.
