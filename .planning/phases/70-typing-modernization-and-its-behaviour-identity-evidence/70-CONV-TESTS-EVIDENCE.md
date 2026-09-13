# Phase 70 — Conversion: tests/ remainder

BASE_70_08 = 6d75e9d5b9254be7f3ff3712b61878a7ae85d332
(from `git rev-parse HEAD` at the start of this plan's execution, before any commit)

## Head check and provisioning

Fresh measurements at the start of this plan's execution, in this worktree.

```
$ date -u +%FT%TZ
2026-09-13T05:05:15Z
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2227131f16a5da6c
$ test -f .git; echo "exit:$?"
exit:0
$ git rev-parse --abbrev-ref HEAD
worktree-agent-a2227131f16a5da6c
```

Preconditions (task 1's `<precondition>`), each checked before any conversion:

```
$ grep -A3 'PILOT_TRANSLATOR\|PILOT_LEDGER\|CONTROL_RENAME\|CONTROL_IMPORT\|MASK_HARNESS_SHA256' 70-MASK-PILOT-EVIDENCE.md
PILOT_TRANSLATOR = EQUAL
PILOT_LEDGER = EQUAL
CONTROL_RENAME = DIFFER
CONTROL_IMPORT = DIFFER
MASK_HARNESS_SHA256 = 11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65
$ grep -q '^## HALT' 70-MASK-PILOT-EVIDENCE.md && echo HALT_FOUND || echo NO_HALT
NO_HALT
```
All four pilot/control keys hold their required values, and the harness block hashes to
`MASK_HARNESS_SHA256` exactly (confirmed independently below, in `## Conversion`).

```
$ git log --format=%H 697a113221a8a267d7e8c6dd1f2b95672f9454d2..HEAD -- CLAUDE.md
3c5e281cccf7efea39fe38ffc10c72ebe74d95fa
$ git merge-base --is-ancestor 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD; echo "exit:$?"
exit:0
```
Exactly one CLAUDE.md commit since `PHASE_BASE_SHA`, and `PHASE_BASE_SHA` is an ancestor of HEAD.

```
$ git diff --quiet 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD -- tests/conftest.py tests/test_bundle_layout_sweep_gate.py tests/test_include_edge_derivation_unit.py; echo "exit:$?"
exit:0
```
None of the three target files had changed since `PHASE_BASE_SHA` before this plan's own
conversion — confirmed.

Provisioning: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`
exited 0, installing 90 packages including `typsphinx==0.9.2` (editable, this worktree's own path),
`mypy==2.3.1`, `ruff==0.16.6`, `myst-parser==5.1.0` (docs extra present), `pytest==9.1.1`.

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

With `P="tests/conftest.py tests/test_bundle_layout_sweep_gate.py tests/test_include_edge_derivation_unit.py"`:

```
$ uv run ruff check $P --select UP006,UP035 --output-format=concise
tests/conftest.py:6:1: UP035 `typing.Dict` is deprecated, use `dict` instead
tests/conftest.py:84:24: UP006 [*] Use `dict` instead of `Dict` for type annotation
tests/test_bundle_layout_sweep_gate.py:42:1: UP035 `typing.Dict` is deprecated, use `dict` instead
tests/test_bundle_layout_sweep_gate.py:42:1: UP035 `typing.List` is deprecated, use `list` instead
tests/test_bundle_layout_sweep_gate.py:87:23: UP006 [*] Use `dict` instead of `Dict` for type annotation
tests/test_bundle_layout_sweep_gate.py:105:34: UP006 [*] Use `list` instead of `List` for type annotation
tests/test_bundle_layout_sweep_gate.py:112:12: UP006 [*] Use `list` instead of `List` for type annotation
tests/test_bundle_layout_sweep_gate.py:153:44: UP006 [*] Use `list` instead of `List` for type annotation
tests/test_include_edge_derivation_unit.py:25:1: UP035 `typing.Dict` is deprecated, use `dict` instead
tests/test_include_edge_derivation_unit.py:25:1: UP035 `typing.List` is deprecated, use `list` instead
tests/test_include_edge_derivation_unit.py:296:30: UP006 [*] Use `dict` instead of `Dict` for type annotation
tests/test_include_edge_derivation_unit.py:296:40: UP006 [*] Use `list` instead of `List` for type annotation
Found 12 errors.
[*] 7 fixable with the `--fix` option.
```
Non-zero finding count (12: 2 conftest.py + 6 test_bundle_layout_sweep_gate.py + 4
test_include_edge_derivation_unit.py) confirmed before any fix — matches
`70-BASELINE-EVIDENCE.md`'s per-file breakdown exactly.

Pass 1: `uv run ruff check $P --select UP006,UP035 --fix`
```
Found 12 errors (7 fixed, 5 remaining).
exit:1
```
The 5 remaining are the three files' own `from typing import ...` header lines (one UP035
diagnostic per removed name: 1 on `tests/conftest.py:6`, 2 on
`tests/test_bundle_layout_sweep_gate.py:42`, 2 on `tests/test_include_edge_derivation_unit.py:25`)
— not independently fixable by the `--select`-scoped pass because the header line's own rewrite
(dropping the removed names, or removing the whole import line once nothing remains) is a
config-rule concern (`I001`/`F401`), which pass 2 covers.

Pass 2: `uv run ruff check $P --fix`
```
Found 5 errors (5 fixed, 0 remaining).
exit:0
```
This pass used the config rules (F401 unused-import), rewriting the three files' header lines:
`tests/conftest.py`'s `from typing import Any, Dict` shrank in place to `from typing import Any`;
`tests/test_bundle_layout_sweep_gate.py`'s and `tests/test_include_edge_derivation_unit.py`'s
`from typing import Dict, List` lines vanished entirely, since neither file uses any other
`typing` name.

No hand edit was made in any file. `sed`, `--preview` and `--unsafe-fixes` were never invoked.

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
 tests/conftest.py                          | 4 ++--
 tests/test_bundle_layout_sweep_gate.py     | 9 ++++-----
 tests/test_include_edge_derivation_unit.py | 3 +--
 3 files changed, 7 insertions(+), 9 deletions(-)
```

Import block of each file, after conversion:

`tests/conftest.py` (lines 5-6):
```python
from pathlib import Path
from typing import Any
```

`tests/test_bundle_layout_sweep_gate.py` (lines 40-41, the `from typing import Dict, List` line
removed entirely):
```python
import re
from pathlib import Path
```

`tests/test_include_edge_derivation_unit.py` (lines 24-25, the `from typing import Dict, List`
line removed entirely):
```python
from pathlib import Path

import pytest
```

Full diff:
```diff
diff --git a/tests/conftest.py b/tests/conftest.py
index 8012a42d..27c5f5bd 100644
--- a/tests/conftest.py
+++ b/tests/conftest.py
@@ -3,7 +3,7 @@ pytest configuration and fixtures for typsphinx tests.
 """
 
 from pathlib import Path
-from typing import Any, Dict
+from typing import Any
 
 import pytest
 from docutils import nodes
@@ -81,7 +81,7 @@ def temp_sphinx_app(tmp_path: Path) -> SphinxTestApp:
 
 
 @pytest.fixture
-def sphinx_config() -> Dict[str, Any]:
+def sphinx_config() -> dict[str, Any]:
     """Sample Sphinx configuration for testing."""
     return {
         "project": "Test Project",
diff --git a/tests/test_bundle_layout_sweep_gate.py b/tests/test_bundle_layout_sweep_gate.py
index d2f0d126..78a9b621 100644
--- a/tests/test_bundle_layout_sweep_gate.py
+++ b/tests/test_bundle_layout_sweep_gate.py
@@ -39,7 +39,6 @@ below names paths relative to the repository root (T-56-14).
 
 import re
 from pathlib import Path
-from typing import Dict, List
 
 REPO_ROOT = Path(__file__).resolve().parent.parent
 
@@ -84,7 +83,7 @@ DELETED_WRITE_TEMPLATE_FILE_METHOD_RE = re.compile(r"\b_write_template_file\b")
 # everywhere else -- the same line-scoped-exemption shape
 # tests/test_docs_template_layout_gate.py's `templates_path` rule already
 # established for this codebase.
-EXCLUDED_SWEEP_PATHS: Dict[str, str] = {
+EXCLUDED_SWEEP_PATHS: dict[str, str] = {
     "docs/source/changelog.rst": (
         "Historical release notes describing what was true at the version "
         "they document (the _template.typ-era output layout, at the "
@@ -102,14 +101,14 @@ EXCLUDED_SWEEP_PATHS: Dict[str, str] = {
 }
 
 
-def _discover_policed_files() -> List[Path]:
+def _discover_policed_files() -> list[Path]:
     """Discover every policed file at run time -- never a hardcoded list.
 
     ``docs/source/`` is walked for ``*.rst``/``*.md``; ``README.md`` is
     yielded directly; ``examples/`` is walked for ``*.md``/``*.rst``/
     ``*.py``. Skips ``__pycache__`` and any ``_build`` output directory.
     """
-    files: List[Path] = []
+    files: list[Path] = []
     for root in POLICED_ROOTS:
         if not root.exists():
             continue
@@ -150,7 +149,7 @@ def _excluded_lines_for(relpath: str) -> set:
     return lines
 
 
-def _find_offenses(pattern: re.Pattern) -> List[str]:
+def _find_offenses(pattern: re.Pattern) -> list[str]:
     """Every ``relpath:lineno: line text`` offense the given pattern finds
     across every policed file, honouring EXCLUDED_SWEEP_PATHS (both
     whole-file and line-scoped entries)."""
diff --git a/tests/test_include_edge_derivation_unit.py b/tests/test_include_edge_derivation_unit.py
index 522bf1ab..7816c966 100644
--- a/tests/test_include_edge_derivation_unit.py
+++ b/tests/test_include_edge_derivation_unit.py
@@ -22,7 +22,6 @@ which drives one real Sphinx build via ``SphinxTestApp``.
 """
 
 from pathlib import Path
-from typing import Dict, List
 
 import pytest
 from docutils import nodes
@@ -293,7 +292,7 @@ class TestMakeIncludeEdgeKeySeparatorInjectivity:
 # ---------------------------------------------------------------------------
 
 
-def _linear_chain(n: int) -> Dict[str, List[str]]:
+def _linear_chain(n: int) -> dict[str, list[str]]:
     """A synthesized ``toctree_includes`` mapping for a straight-line
     include chain ``d0 -> d1 -> ... -> d(n-1) -> d(n)`` of ``n`` edges."""
     return {f"d{i}": [f"d{i + 1}"] for i in range(n)}
```

Commit: `3b473894` — `refactor(70-08): move the remaining tests/ files onto builtin generics (QUA-11)`,
touching only the three files.

## Leg (a)

Harness verified by hash before use:
```
$ H="$(sed -n '/^~~~python mask-harness$/,/^~~~$/p' 70-MASK-PILOT-EVIDENCE.md | sed '1d;$d')"
$ printf '%s\n' "$H" | sha256sum
11cdbeb68cae48a890dfc98736ae2ff7fc15c4557cddad6c5f3a06f425db8a65
```
Equal to `MASK_HARNESS_SHA256`. `sk() { uv run python -c "$H"; }` defined from this exact
extraction.

For each of the three files, the masked hash of the working-tree (converted) file is compared
against the masked hash of the same path read from `PHASE_BASE_SHA`
(`697a113221a8a267d7e8c6dd1f2b95672f9454d2`).

```
$ git show 697a113221a8a267d7e8c6dd1f2b95672f9454d2:tests/conftest.py | sk
e86284ce44fd0afa1077e595be4b05080990810c11657b03ed430f9e24c31a6e
$ sk < tests/conftest.py
e86284ce44fd0afa1077e595be4b05080990810c11657b03ed430f9e24c31a6e
```
conftest.py: EQUAL (shrink-in-place: the typing line keeps `Any`)

```
$ git show 697a113221a8a267d7e8c6dd1f2b95672f9454d2:tests/test_bundle_layout_sweep_gate.py | sk
813565e78879f6fd6637a267a4da432acf3b988d75662ee610435e80473de84b
$ sk < tests/test_bundle_layout_sweep_gate.py
813565e78879f6fd6637a267a4da432acf3b988d75662ee610435e80473de84b
```
test_bundle_layout_sweep_gate.py: EQUAL (import line vanishes entirely, including the
module-level `EXCLUDED_SWEEP_PATHS: Dict[str, str]` annotated-constant conversion)

```
$ git show 697a113221a8a267d7e8c6dd1f2b95672f9454d2:tests/test_include_edge_derivation_unit.py | sk
adffe23b45742160fba01dd0668dc92c4944976c2d10d58bf84aeb5bdc617d8a
$ sk < tests/test_include_edge_derivation_unit.py
adffe23b45742160fba01dd0668dc92c4944976c2d10d58bf84aeb5bdc617d8a
```
test_include_edge_derivation_unit.py: EQUAL (import line vanishes entirely)

All three pairs are equal.

TESTS_MASK = EQUAL

No HALT needed.

## Leg (c) census

Over `git diff "$PHASE_BASE_SHA" HEAD` for the three files, with headers and blank lines
excluded:

```
$ git diff 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD -- tests/conftest.py tests/test_bundle_layout_sweep_gate.py tests/test_include_edge_derivation_unit.py --stat
 tests/conftest.py                          | 4 ++--
 tests/test_bundle_layout_sweep_gate.py     | 9 ++++-----
 tests/test_include_edge_derivation_unit.py | 3 +--
 3 files changed, 7 insertions(+), 9 deletions(-)
```
Per-file added+removed line counts: `tests/conftest.py` 2+2, `tests/test_bundle_layout_sweep_gate.py`
5+4, `tests/test_include_edge_derivation_unit.py` 1+2 (matching the full diff quoted above under
`## Conversion`).

```
$ git diff "$B" HEAD -- $P | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)( |$)' | grep -vE '^[+-][[:space:]]*$' \
    | grep -cvE '(Dict|List|Set|Tuple|Iterator|dict|list|set|tuple|typing|collections\.abc)'
0
```

NON_TYPING_LINES_70_08 = 0
(every changed non-blank line carries a typing name)

```
$ git diff "$B" HEAD -- $P | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)( |$)' | grep -cw assert
0
```

ASSERT_LINES_70_08 = 0
(no changed line contains the word `assert`)

```
$ git diff --quiet 697a113221a8a267d7e8c6dd1f2b95672f9454d2 HEAD -- tests/test_authors_pipeline_stage_gate.py; echo "exit:$?"
exit:0
$ sed -n 515p tests/test_authors_pipeline_stage_gate.py
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
```
`tests/test_authors_pipeline_stage_gate.py` (the file whose `ast.Dict` at line 515 must stay
byte-identical) is untouched by this plan's conversion, confirmed by an empty diff, and line 515
still contains `ast.Dict`.

## Gates

```
$ uv run black --check tests/conftest.py tests/test_bundle_layout_sweep_gate.py tests/test_include_edge_derivation_unit.py
All done! ✨ 🍰 ✨
3 files would be left unchanged.
exit:0
```

```
$ uv run ruff check .
All checks passed!
exit:0
```
Repo-wide, config-rule ruff is clean — the still-present `UP006`/`UP035` ignores mean this check
does not itself re-verify the three converted files' UP006/UP035 cleanliness (Task 1 already did,
with `--select` explicitly overriding the ignores); it confirms the conversion introduced no other
config-rule violation anywhere in the repo, and that the parallel wave-3 siblings' in-flight
changes (invisible to this worktree) do not affect this check.

```
$ uv run mypy typsphinx/ 2>/dev/null
Success: no issues found in 9 source files
exit:0
```

MYPY_STDOUT_SHA256_70_08 = 46984ca20bf69f7b14ec1fd9bd82101d56a4e109e68f016fd2a04f22481b09b3
(stdout only, stderr excluded per Pitfall 7 — equal to `MYPY_STDOUT_SHA256_BEFORE`)

```
$ LC_ALL=C uv run pytest --collect-only -q -p no:cacheprovider 2>/dev/null | grep -oE '[0-9]+ tests? collected' | grep -oE '^[0-9]+'
1548
```

PYTEST_COLLECTED_70_08 = 1548
(equal to `PYTEST_COLLECTED_BEFORE`)

```
$ LC_ALL=C uv run pytest -q -rs -p no:cacheprovider; echo "exit:$?"
...
tests/test_xref_whole_document_guard_render_gate.py ........             [100%]

=========================== short test summary info ============================
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1547 passed, 1 skipped in 133.52s (0:02:13) ==================
exit:0
```

PYTEST_RESULT_70_08 = 1547 passed 1 skipped
(equal to `PYTEST_RESULT_BEFORE`; 1547 + 1 = 1548 = `PYTEST_COLLECTED_70_08`, confirmed)

Both leg (e) (mypy) and leg (b) (pytest) are unchanged from base: the conversion altered no
type-checking outcome and no test outcome. Combined with leg (a) (`TESTS_MASK = EQUAL`) and this
section's leg (c) census (`NON_TYPING_LINES_70_08 = 0`, `ASSERT_LINES_70_08 = 0`), the three
remaining `tests/` files are proven structurally identical to base under the mask, with no
assertion touched and no runtime-behaviour or test-outcome change.

No HALT needed.
