# Phase 70: Typing Modernization and Its Behaviour-Identity Evidence - Pattern Map

**Mapped:** 2026-09-13
**Files analyzed:** 13 (10 typing-conversion files + `CLAUDE.md` + `pyproject.toml` + the todo move) plus the evidence-file convention
**Analogs found:** 13 / 13

This phase is unusual for pattern mapping: it is a mechanical *edit*, not new-file creation, and its
own codebase already contains the target idiom in one file (`typsphinx/builder.py`'s existing
`collections.abc.Iterator` import). The most load-bearing "analog" is therefore not a sibling file of
the same role, but this project's own prior evidence-transcript convention (v0.9.3 Phase 68), which
governs how `70-*-EVIDENCE.md` files should be shaped, plus the target idiom already present.

## File Classification

| File to modify | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/translator.py` | translator (docutils visitor) | transform | `typsphinx/builder.py` (same-repo, already-converted import shape) | role-match, idiom-exact |
| `typsphinx/builder.py` | builder (Sphinx `Builder` subclass) | file-I/O + transform | itself, `Iterator` import already converted at line 11 | exact (self-analog for the one remaining conversion) |
| `typsphinx/template_engine.py` | service (template loader/renderer) | transform | `typsphinx/template_registry.py` (sibling service, same `Dict`/`Any` shape) | exact |
| `typsphinx/template_registry.py` | service (config resolver) | transform | `typsphinx/template_engine.py` | exact |
| `typsphinx/writer.py` | writer (docutils `Writer` subclass) | transform | `typsphinx/translator.py` (also imports `Tuple`/`Any` from `typing`) | role-match |
| `typsphinx/__init__.py` | config/setup (Sphinx `setup()` entry point) | event-driven (Sphinx extension registration) | none in-repo (only file with the `UP035`+`F401` ruff-fix survivor) | role-match, needs the one hand edit |
| `tests/conftest.py` | test fixture module | request-response (pytest fixtures) | `tests/test_include_edge_derivation_unit.py` (same `Dict, List` shape) | exact |
| `tests/test_bundle_layout_sweep_gate.py` | test (policy/sweep gate) | batch (filesystem sweep) | `tests/test_include_edge_derivation_unit.py` | exact |
| `tests/test_include_edge_derivation_unit.py` | test (unit) | transform | `tests/test_bundle_layout_sweep_gate.py` | exact |
| `tests/test_include_ledger_removal_gate.py` | test (policy/sweep gate) | batch (filesystem sweep) | `typsphinx/builder.py:11` for the `Iterator` half; `tests/test_bundle_layout_sweep_gate.py` for the `Dict`/`Set` half | exact (split analog: import-move case) |
| `CLAUDE.md:75` | doc (contributor instruction) | n/a | v0.9.3 Phase 68's `CLAUDE.md` "Conventions & gotchas" rewrite (`68-TOX-EVIDENCE.md` test excerpt) | exact (same file, same convention: prior rewrite already replaced a stale deferral bullet in this same section) |
| `pyproject.toml:128-129` | config (ruff ignore list) | n/a | none needed — this is the flip itself, not a pattern to imitate | n/a |
| `.planning/todos/pending/2026-07-22-...md` → `todos/completed/` | doc (todo lifecycle) | n/a | this project's existing todo-move convention (folded-todo-with-flip, per CONTEXT D-constraint 2) | role-match |
| New evidence files `70-*-EVIDENCE.md` | evidence transcript (not source code) | n/a | `.planning/milestones/v0.9.3-phases/68-.../68-TOX-EVIDENCE.md` and `68-02-PLAN.md`'s `sk()` verify block | exact |

## Pattern Assignments

### `typsphinx/__init__.py` (config/setup, the one hand-edit survivor)

**Analog:** self — `ruff check . --fix` converts every other file to completion; this file alone
needs one manual line edit because `Dict` becomes unused once its sole use-site elsewhere converts.

**Current import (lines 14-15):**
```python
import importlib.metadata
from typing import Any, Dict
```

**Target form (per D-01's instruction and the ROADMAP-documented survivor fix):**
```python
import importlib.metadata
from typing import Any
```
`Any` stays imported (confirmed still used elsewhere in the file); only `Dict` is dropped, not the
whole `typing` import line. This is the sole hand edit in the whole conversion; every other file's
`ruff check . --fix` pass is expected to fully resolve without manual intervention.

---

### `typsphinx/builder.py` (already-converted `Iterator`, remaining `Dict`/`List`/`Set`/`Tuple`)

**Analog:** itself, line 11 — this is the target idiom already committed and lint-clean today.

**Current imports (lines 8-13):**
```python
import hashlib
import posixpath
import shutil
from collections.abc import Iterator
from os import path
from typing import Any, Dict, List, Set, Tuple
```

**Target shape (30 findings resolve here; `Iterator` line untouched, `typing` line shrinks to `Any` only if nothing else from `typing` remains — confirmed `Any` stays used):**
```python
import hashlib
import posixpath
import shutil
from collections.abc import Iterator
from os import path
from typing import Any
```
Every `Dict[...]`/`List[...]`/`Set[...]`/`Tuple[...]` annotation in this file becomes
`dict[...]`/`list[...]`/`set[...]`/`tuple[...]` in place — this is what `ruff check . --fix` performs
automatically; no hand edit expected here (unlike `__init__.py`).

---

### `typsphinx/translator.py`, `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/template_registry.py`

**Analog for the import-line shape:** `typsphinx/template_registry.py` and
`typsphinx/template_engine.py` are mutual analogs — both import exactly `Any, Dict` (or `Any, Dict,
List`) from `typing` today and both keep `Any` after conversion:

```python
# template_registry.py:29 (before)
from typing import Any, Dict
# template_engine.py:13 (before)
from typing import Any, Dict, List
```
Target: `from typing import Any` in both, with every `Dict[...]`/`List[...]` annotation converted to
`dict[...]`/`list[...]`.

`writer.py:10` (`from typing import Any, Tuple`) and `translator.py:9`
(`from typing import Any, Dict, List, NamedTuple, Tuple`) follow the same shape — `Any` (and, for
`translator.py`, `NamedTuple`) survive the import line; `Tuple`/`Dict`/`List` do not. Note
CONTEXT's Established Patterns already flags `translator.py:773`'s `str | List[str] | None` as a
case where only the inner `List` converts and the `|` count must stay unchanged — this is the kind
of line the masked-AST leg (a) is built to catch if disturbed.

---

### `tests/conftest.py`, `tests/test_include_edge_derivation_unit.py`, `tests/test_bundle_layout_sweep_gate.py`

**Analog:** these three are mutual analogs, all importing `Dict`/`List` for local dict/list literal
annotations (module-level constants, function return types):

```python
# conftest.py:6 (before)               from typing import Any, Dict
# test_include_edge_derivation_unit.py:25 (before)   from typing import Dict, List
# test_bundle_layout_sweep_gate.py:42 (before)        from typing import Dict, List
```

`test_bundle_layout_sweep_gate.py:87` shows the module-level-constant `AnnAssign` shape the masked-AST
leg (a) mask must also cover (confirmed it does, per RESEARCH's empirical validation):
```python
EXCLUDED_SWEEP_PATHS: Dict[str, str] = {
```
→ `EXCLUDED_SWEEP_PATHS: dict[str, str] = {`. `conftest.py` keeps `Any` after conversion (its import
line becomes `from typing import Any`); the other two files' typing import lines are expected to
**vanish entirely** once `Dict`/`List` are their only uses — this is one of D-06/Pitfall-6's
"import line vanishes" cases the masked-AST harness must handle via node deletion, not in-place
blanking.

---

### `tests/test_include_ledger_removal_gate.py` (the import-split case)

**Analog:** `typsphinx/builder.py:11` for the target `collections.abc` import shape; itself for the
before-state.

**Current shape (line 47):**
```python
from typing import Dict, Iterator, Set
```

**Target shape** (this is the file RESEARCH explicitly calls out as the import-*split* case the
masked-AST mask must get right):
```python
from typing import Dict, Set
from collections.abc import Iterator
```
(exact ordering per `ruff --fix`'s isort pass — do not hand-order this; let `ruff check . --fix`
produce it, then verify with `ruff check .` showing zero remaining). `Dict`/`Set` then convert to
`dict`/`set` in the body, at which point (per the file's own usage) the `typing` import line may
itself vanish if nothing else from `typing` remains — confirmed empirically in RESEARCH ("two files
lose the import line entirely" includes this file's `typing` half after `Dict`/`Set` convert, while
the new `collections.abc import Iterator` line persists).

---

### `CLAUDE.md:75` (DOC-22 rewrite)

**Analog:** v0.9.3 Phase 68's own rewrite of a stale sentence in the same "Conventions & gotchas"
section (evidenced in `68-TOX-EVIDENCE.md`'s `test_dev_extra_pins_tox_uv_not_tox_uv_bare` docstring
excerpt), which is direct precedent for "replace a deferral-era sentence with an operational-fact
sentence, drop history, in the same file/section."

**Current bullet (verbatim, `CLAUDE.md:75`):**
```markdown
- **Python 3.12+ is required.** ruff intentionally ignores `UP006`/`UP035` (the `Dict`/`List` → `dict`/`list` upgrades) — this is a deliberate deferral, not a compatibility constraint; the modernization pass is filed at `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`. Don't "modernize" typing imports until that todo lands.
```

**Target shape per D-01/D-02/D-03/D-04** (rewrite is confined to this one bullet; keep the
Python-floor clause, drop every flip-dependent clause, add the standing annotation-style
instruction, no history note, no `__future__`/PEP-604 prohibition):
```markdown
- **Python 3.12+ is required.** Annotations use builtin generics (`dict[str, Any]`, `list[str]`,
  `set[...]`, `tuple[...]`) and `collections.abc` for abstract types such as `Iterator`, not
  `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`.
```
(Exact wording is Claude's Discretion within D-01..D-03; the shape above satisfies all four
decisions and is a single self-contained line, matching this bullet's existing one-paragraph style.)

---

### `pyproject.toml:128-129` (the ignore-flip, Wave 2 plan only)

**Current (lines 124-129):**
```toml
ignore = [
    "E501",   # Line too long (handled by black)
    "T201",   # print found (used in tests for debugging)
    "B017",   # asserting blind exception in tests
    "UP035",  # typing.Dict/List/Set deprecation; modernization deferred (see .planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md)
    "UP006",  # Use dict instead of Dict; same deferral as UP035 above
```
**Target:** delete both `"UP035"` and `"UP006"` lines (with their comments) from the `ignore` array
entirely — no replacement lines, no comment placeholder. This is the sole edit that turns the
now-enforced rules on; it must land only after every Wave 1 conversion file is already clean,
matching ROADMAP constraint 1's ordering.

---

### Evidence files (`70-*-EVIDENCE.md`, QUA-12 legs)

**Analog:** `.planning/milestones/v0.9.3-phases/68-.../68-TOX-EVIDENCE.md` lines 248-326, and
`68-02-PLAN.md` lines 253/305 for the `sk()` masked-AST helper embedded in a verify block.

**Evidence-line shape to copy (`KEY = value`, paired base-vs-current, then an explicit equality
statement):**
```
$ masked AST hash (docstrings + assert messages masked), current tree
ba5710611d00849ec86999bb79862e7cac91c34a209403a5cc799b0a706257d7

$ masked AST hash, git show BASE_68_02:tests/test_toolchain_config_gate.py
ba5710611d00849ec86999bb79862e7cac91c34a209403a5cc799b0a706257d7
```
followed by a one-line verdict ("Equal — no compared name, expression or statement changed.").
Phase 70's leg (a) evidence file should reuse exactly this shape per file (10 files, each getting a
`BASE / CURRENT / verdict` triple), substituting Phase 70's own `Mask` class (annotation +
`typing`/`collections.abc` import masking, per CONTEXT's Specific Ideas and RESEARCH's node-deletion
refinement) for Phase 68's docstring/assert-message mask. The `sk()` function name and one-line
invocation convention (`sk() { uv run python -c '<Mask class + sk()>'; }`) should also be reused
verbatim as the verify-block idiom.

**Pytest count evidence line shape** (same file, further down, "Equal to TWO_FILE_RESULT_BEFORE"):
```
$ uv run pytest tests/test_toolchain_config_gate.py tests/test_pdf_render_gate.py -q -p no:cacheprovider
tests/test_toolchain_config_gate.py ....                                 [ 11%]
tests/test_pdf_render_gate.py ...............................            [100%]

============================== 35 passed in 5.56s ==============================
```
Phase 70's leg (b) full-suite evidence should follow this same `$ command` / raw-output / verdict
triple, at full-suite scope rather than two-file scope, per D-05's broader corpus. Use the
unanchored `grep -oE '[0-9]+ tests? collected'` form documented in RESEARCH (§ Leg (b)) when
extracting the collected-count line — the `=`-decorated pytest summary line breaks an anchored
`^[0-9]` match.

**Diff-hunk census evidence line shape** (`68-TOX-EVIDENCE.md`'s git-diff transcript with a
line-range callout):
```
Removed lines are only base 302-304 and 367-368 (the assertion-message tail sits two lines
earlier than the plan's approximate 366-368 census, confirmed by direct measurement); base
lines 1-301 are untouched.
```
Reuse this "state the exact line range touched, and what's confirmed untouched" prose shape for
leg (c)'s per-file diff census and for DOC-23's hunk-by-hunk classification (D-11).

## Shared Patterns

### The `typing` import survives, only specific names drop
**Source:** measured across all 10 conversion-target files (`typsphinx/translator.py:9`,
`builder.py:13`, `template_engine.py:13`, `template_registry.py:29`, `writer.py:10`,
`tests/conftest.py:6` all keep `Any`, `translator.py` also keeps `NamedTuple`).
**Apply to:** every one of the 6 files above. Do not delete the `from typing import ...` line
wholesale — only remove the specific `Dict`/`List`/`Set`/`Tuple` names from it. For
`tests/test_bundle_layout_sweep_gate.py`, `tests/test_include_edge_derivation_unit.py`, and the
`typing`-half of `tests/test_include_ledger_removal_gate.py`, the import line vanishes entirely
because nothing else from `typing` remains — this is the expected, not the erroneous, outcome for
those three files specifically.

### `ruff check . --fix` does the rewrite; only one hand edit exists
**Source:** RESEARCH § "Full conversion command sequence" — `uv run ruff check . --fix --statistics`
resolves 113 of 115 findings; only `typsphinx/__init__.py:15` needs manual editing (drop unused
`Dict`).
**Apply to:** all 10 conversion files. Plans should run the fixer, not hand-edit annotations line by
line, except for the one documented `__init__.py` survivor.

### Evidence files are markdown transcripts, no new committed script/test
**Source:** CONTEXT "Claude's Discretion" + v0.9.3 Phase 64 D-05 convention, demonstrated in
`68-TOX-EVIDENCE.md`.
**Apply to:** every QUA-12 leg's evidence output. Do not add a new `tests/*.py` file or a new
committed `.py` script for the masked-AST harness — it runs inline inside a verify block
(`uv run python -c '...'`), exactly as Phase 68's `sk()` did, and its transcript is pasted into the
phase's evidence markdown.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `typsphinx/__init__.py`'s hand-edit | config/setup | n/a | No other file in this conversion needs a manual (non-`ruff --fix`) edit; it is genuinely a singleton case documented directly in RESEARCH/ROADMAP, not something to pattern-match against a sibling file |

## Metadata

**Analog search scope:** `typsphinx/*.py` (all 6 source modules), `tests/conftest.py` and the 4 named
test files, `CLAUDE.md`, `pyproject.toml`, and `.planning/milestones/v0.9.3-phases/68-.../` (evidence
convention).
**Files scanned:** 13 conversion-target files + 2 prior-art evidence files (Phase 68).
**Pattern extraction date:** 2026-09-13
</content>
