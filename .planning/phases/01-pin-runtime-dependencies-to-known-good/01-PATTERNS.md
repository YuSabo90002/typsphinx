# Phase 1: Pin Runtime Dependencies to Known-Good - Pattern Map

**Mapped:** 2026-07-04
**Files analyzed:** 7 (3 config edits, 3 black reformats, 1 doc append) + 1 landmine cross-check
**Analogs found:** 7 / 7 (this phase modifies existing files only — no new files; the "analog" for each is its own current excerpt, showing the exact before/after)

This is a config/dependency phase — there are no new source files, controllers, services, or components. Every "pattern" here is a targeted before/after diff on an existing config surface. The planner should treat each row below as a literal `<read_first>` + `<action>` pair.

## File Classification

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|----------------|------|-----------|-----------------|----------------|
| `pyproject.toml` | config | transform (range→lock) | itself (current `[project.dependencies]` / `[project.optional-dependencies].dev` blocks) | exact (self) |
| `tox.ini` | config | transform (mirrors pyproject ceilings) | itself (current `[testenv]` / `[testenv:type]` `deps=` blocks) | exact (self) |
| `uv.lock` | config (machine-generated) | batch (regenerate via CLI) | n/a — never hand-edit; regenerate via `uv lock` | exact (tooling, not hand-pattern) |
| `docs/build_multilang.py` | utility/script | transform (black reformat only) | itself (module docstring / import block, lines 1-10) | exact (self) |
| `tests/test_config_other_options.py` | test | request-response (Sphinx app config assertions) | itself (repeated `conf_py.write_text("""..."""` blocks, e.g. lines 15-20) | exact (self) |
| `tests/test_config_toctree_defaults.py` | test | request-response (Sphinx app config assertions) | `tests/test_config_other_options.py` (same `write_text` triple-quote pattern; toctree file's own calls are single-line and largely already black-clean, but check each `write_text(` call listed below) | role-match |
| `.planning/PROJECT.md` (`## Key Decisions` table) | config/doc | transform (append row) | itself (existing table rows, lines 60-65) | exact (self) |

## Pattern Assignments

### `pyproject.toml` (config, transform)

**Analog:** itself — current lines 29-49

**Current excerpt to change** (lines 29-33, runtime deps):
```toml
dependencies = [
    "sphinx>=5.0",
    "docutils>=0.18",
    "typst>=0.14.1",
]
```
**Target (D-01, upper bounds only, floors unchanged):**
```toml
dependencies = [
    "sphinx>=5.0,<9",
    "docutils>=0.18,<0.22",
    "typst>=0.14.1,<0.15",
]
```

**Current excerpt to change** (lines 35-49, dev extra — PIN-05 removal):
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "tox>=4.0",
    "tox-uv>=1.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
    "sphinx-testing>=1.0",
    "pre-commit>=3.0",
    "types-docutils>=0.18",
    "twine>=5.0",
    "build>=1.0",
]
```
**Target:** delete the `"sphinx-testing>=1.0",` line (line 44) only. Do **not** touch `docs = [...]` (lines 50-54) per D-05 — no ceilings on `furo`/`sphinx-autodoc-typehints`/`sphinx-intl`.

**Do-not-touch guard:** `[tool.black].target-version` (line 88), `[tool.ruff].target-version` (line 103), `[tool.mypy].python_version` (line 120) all still say `py39`/`3.9` — leave untouched this phase (Phase 3 owns the floor bump).

---

### `tox.ini` (config, transform — "fix stale documentation of intent", not a live resolution path)

**Analog:** itself — current lines 6-38

**Current excerpt to change** (`[testenv]`, lines 6-17):
```ini
[testenv]
description = Run tests with pytest
package = wheel
wheel_build_env = .pkg
runner = uv-venv-lock-runner
deps =
    pytest>=7.0
    pytest-cov>=4.0
    sphinx>=5.0
    sphinx-testing>=1.0
commands =
    pytest {posargs:tests/}
```
**Target:** ceiling-mirror `sphinx>=5.0` → `sphinx>=5.0,<9`; delete the `sphinx-testing>=1.0` line entirely (PIN-05).

**Current excerpt to change** (`[testenv:type]`, lines 29-38):
```ini
[testenv:type]
description = Run type checking with mypy
runner = uv-venv-lock-runner
deps =
    mypy>=1.0
    sphinx>=5.0
    types-docutils>=0.18
    docutils>=0.18
commands =
    mypy typsphinx/
```
**Target:** `sphinx>=5.0` → `sphinx>=5.0,<9`; `docutils>=0.18` → `docutils>=0.18,<0.22`. (`types-docutils>=0.18` is a separate stub package name — leave as-is; D-05 doesn't cover dev-only stub packages, and RESEARCH.md doesn't flag it.)

**Important nuance (from RESEARCH.md Architecture Patterns):** every env in this file uses `runner = uv-venv-lock-runner`, under which `deps=` is **inert** — `tox-uv` ignores it and syncs everything from `uv.lock` instead. This edit is required to satisfy PIN-04's literal text (stop the file from documenting an unbounded intent that contradicts `pyproject.toml`), but verification is a static `grep`, not a behavioral test:
```bash
grep -nE 'sphinx>=5\.0[^,]|docutils>=0\.18[^,]' tox.ini   # expect zero matches after edit
grep -n sphinx-testing tox.ini                             # expect zero matches after edit
```
`[testenv:cov]` (lines 40-45) inherits `{[testenv]deps}` — no separate edit needed there; it picks up the `[testenv]` fix automatically.

---

### `uv.lock` (machine-generated config, batch regeneration)

**No hand-edit analog — regenerate only.** Pattern from RESEARCH.md's verified mechanics:
```bash
uv lock
uv lock --check      # confirms not stale/idempotent
git diff pyproject.toml uv.lock   # review both together, never one without the other
```
Expected diff shape (verified this session against a scratch copy with identical edits):
```
Resolved 125 packages in 785ms
Updated docutils v0.21.2, v0.22.4 -> v0.21.2
Removed roman-numerals v4.1.0
Removed six v1.17.0
Updated sphinx v7.4.7, v8.1.3, v9.0.4, v9.1.0 -> v7.4.7, v8.1.3
Updated sphinx-autodoc-typehints v2.3.0, v3.0.1, v3.6.1, v3.12.1 -> v2.3.0, v3.0.1
Removed sphinx-testing v1.0.1
Updated typst v0.15.0 -> v0.14.9
```
**Never hand-edit version strings in `uv.lock`.**

---

### `docs/build_multilang.py` (utility/script, black reformat only — no logic change)

**Analog:** itself — current lines 1-10

**Current excerpt:**
```python
#!/usr/bin/env python3
"""Multi-language documentation build script for typsphinx.

This script builds English and Japanese versions of the documentation
and organizes them for GitHub Pages deployment.
"""
import os
import shutil
import subprocess
from pathlib import Path
```
**Target (black inserts a blank line between the module docstring and the first import):**
```python
#!/usr/bin/env python3
"""Multi-language documentation build script for typsphinx.

This script builds English and Japanese versions of the documentation
and organizes them for GitHub Pages deployment.
"""

import os
import shutil
import subprocess
from pathlib import Path
```
Apply via `black docs/build_multilang.py` (or `black .` for the whole tree), never by hand — this is D-04's separate "black reformat" commit, landed apart from the pin change.

---

### `tests/test_config_other_options.py` (test, black reformat only)

**Analog:** itself — current lines 15-20 (representative; the same `write_text(\n    """..."""\n)` shape repeats at lines 38, 68, 91, 113, 135, 157, 180, 202, 225 per grep)

**Current excerpt (lines 15-20):**
```python
    conf_py.write_text(
        """
extensions = ['typsphinx']
typst_package = "@preview/diagraph:0.2.5"
"""
    )
```
**Target (black collapses the call onto the write_text line and de-indents the closing triple-quote):**
```python
    conf_py.write_text(
        """
extensions = ['typsphinx']
typst_package = "@preview/diagraph:0.2.5"
"""
    )
```
Note: RESEARCH.md's Code Examples section shows the actual collapsed form black produces for this call shape:
```diff
-    conf_py.write_text(
-        """
+    conf_py.write_text("""
 extensions = ['typsphinx']
 typst_package = "@preview/diagraph:0.2.5"
-"""
-    )
+""")
```
Apply the identical collapse to every `conf_py.write_text(` call in this file (9 occurrences at the line numbers above) via `black tests/test_config_other_options.py` — do not hand-edit each one individually; run black and let it apply consistently.

---

### `tests/test_config_toctree_defaults.py` (test, black reformat only)

**Analog:** `tests/test_config_other_options.py` (same repo, same `write_text` reformat pattern — role-match, not exact, because most calls in this file are single-line `write_text("Test\n====\n")` and already black-clean; only the multi-line `write_text(\n    ...\n)` calls at lines 79-80 (`index.rst`), 126, 138, 168 area need inspection)

**Action:** run `black --diff tests/test_config_toctree_defaults.py` first to see the exact minimal diff (RESEARCH.md confirms black's diff for this file is part of the same 3-file, 46-unchanged reformat scope), then apply via `black tests/test_config_toctree_defaults.py`. Do not assume every `write_text` call changes — only the ones black's own diff flags.

---

### `.planning/PROJECT.md` `## Key Decisions` table (doc, append)

**Analog:** itself — current lines 58-65

**Current excerpt:**
```markdown
## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pin runtime deps to known-good rather than upgrade forward | Fastest, lowest-risk path to green CI; avoids a large sphinx-9/typst-0.15 porting effort in a maintenance cycle | — Pending |
| Pin `typst` to 0.14.x compatible with bundled `@preview` packages | The `kai` break is a typst 0.15 ⇄ package incompatibility; reverting the compiler restores compilation | — Pending |
| Modernize Python floor to 3.10–3.13 (drop EOL 3.9, add 3.13) | 3.9 reached EOL Oct 2025; "green + modernize" scope | — Pending |
| Defer supporting sphinx 9 / typst 0.15 to a future milestone | Explicitly chosen to pin, not port; keeps scope bounded | — Pending |
```
**Action (D-03/PIN-06):** update the "Pin `typst` to 0.14.x..." row's Outcome from `— Pending` to the confirmed patch (e.g. `Confirmed: typst==0.14.9`, or whichever patch passes the real CI matrix — do not hardcode 0.14.9 as final without the executor's own CI confirmation per RESEARCH.md's Open Questions #2). **Append a new row** documenting the ceiling load-bearing finding, following the exact same `| Decision | Rationale | Outcome |` column shape, e.g.:
```markdown
| `sphinx<9`/`docutils<0.22` ceilings are precautionary, not load-bearing, for the `kai` break | Full `docs-pdf` build succeeds with `typst` pinned alone, sphinx/docutils left unbounded (verified locally, Linux-only) | Applied per D-03 regardless; documented as precautionary |
```
Keep the existing table's pipe-delimited format exactly; do not restructure the table.

---

## Shared Patterns

### The 3-way `@preview` version coupling landmine (do not touch, but must stay in sync if touched)
**Sources (verified this session, exact excerpts):**

`typsphinx/writer.py` lines 94-97:
```python
imports.append('#import "@preview/codly:1.3.0": *')
imports.append('#import "@preview/codly-languages:0.1.1": *')
imports.append('#import "@preview/mitex:0.2.4": mi, mitex')
imports.append('#import "@preview/gentle-clues:1.2.0": *')
```

`typsphinx/template_engine.py` lines 313-316:
```python
output_parts.append('#import "@preview/codly:1.3.0": *')
output_parts.append('#import "@preview/codly-languages:0.1.1": *')
output_parts.append('#import "@preview/mitex:0.2.4": mi, mitex')
output_parts.append('#import "@preview/gentle-clues:1.2.0": *')
```

`typsphinx/templates/base.typ` — same four `@preview` version strings duplicated a third time (not read in full this pass; grep to confirm exact line numbers before any future edit).

**Apply to:** No file in this phase's scope touches these three — CONTEXT.md/RESEARCH.md explicitly keep `@preview` package versions unchanged (D-05, out-of-scope note). This is documented here **only as a hazard**: if the STATE.md fallback path is ever invoked (pin one `@preview` package to an older release because no single typst 0.14.x satisfies all four), all three of these locations must be edited together, in the same commit, or the writer/template_engine emitted import block will desync from `base.typ`'s own imports. RESEARCH.md confirms this fallback was **not needed** — all three tested 0.14.x patches (0.14.1, 0.14.5, 0.14.9) compiled cleanly with the existing versions — so this landmine is documentation-only for this phase, not an active edit.

### Commit separation (D-04)
**Apply to:** all edits above. Two commits minimum:
1. Pin commit: `pyproject.toml` + `tox.ini` + `uv.lock` (PIN-01..05) — lands alone so CI red/green is unambiguous.
2. Black reformat commit: `docs/build_multilang.py` + `tests/test_config_other_options.py` + `tests/test_config_toctree_defaults.py` (LINT-01) — separate, keeps `git blame` clean.

`PROJECT.md` Key Decisions update (D-03 finding) can ride with either commit or its own — not constrained by D-04 (it's documentation, not code/config under test).

### Verification commands (static, non-behavioral — from RESEARCH.md Validation Architecture)
```bash
grep -n 'typst>=0.14.1,<0.15' pyproject.toml
grep -nE 'sphinx>=5.0,<9|docutils>=0.18,<0.22' pyproject.toml
grep -rn sphinx-testing pyproject.toml tox.ini uv.lock   # expect zero matches
uv lock --check                                           # confirms lock not stale
black --check .                                           # expect 0 files after reformat commit
ruff check .                                               # must be run by executor (sandbox couldn't run ruff)
uv run tox -e docs-pdf                                     # empirical PIN-06 confirmation
```

## No Analog Found

None — every file in this phase's scope is an existing file being edited in place; there are no new files requiring an external analog search.

## Metadata

**Analog search scope:** `pyproject.toml`, `tox.ini`, `uv.lock`, `docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`, `.planning/PROJECT.md`, `typsphinx/writer.py`, `typsphinx/template_engine.py` (landmine cross-check only, not modified this phase).
**Files scanned:** 9 (all read directly, no Glob/Grep-only inference needed — phase scope was explicitly enumerated in CONTEXT.md/RESEARCH.md).
**Pattern extraction date:** 2026-07-04
</content>
