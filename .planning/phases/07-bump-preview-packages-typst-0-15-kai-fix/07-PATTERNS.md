# Phase 7: Bump @preview Packages + typst 0.15 (kai fix) - Pattern Map

**Mapped:** 2026-07-11
**Files analyzed:** 5 (all MODIFY, no new files)
**Analogs found:** 5 / 5 (the three sync sites are each other's analogs; pyproject.toml and the test are self-contained edits with no true "analog" needed — the file itself is the pattern)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|-----------------|---------------|
| `typsphinx/writer.py` (lines 94-97) | config/version-declaration | transform (doctree → .typ string emission) | `typsphinx/template_engine.py` (lines 313-316) | exact — same 4 version strings, same literal-string-replacement pattern |
| `typsphinx/template_engine.py` (lines 313-316) | config/version-declaration | transform (template rendering) | `typsphinx/writer.py` (lines 94-97) | exact — identical string set, only variable name differs (`output_parts` vs `imports`) |
| `typsphinx/templates/base.typ` (lines 8-19) | config/version-declaration (Typst source, not Python) | transform (static template consumed by TemplateEngine) | `typsphinx/writer.py` lines 94-97 / `template_engine.py` lines 313-316 | exact same version set; only the mitex import *style* differs (glob vs named) |
| `pyproject.toml` (line 30) | config | build/dependency-pin | none needed — single-line version-range edit, self-contained | n/a (no analog needed; established `>=floor,<ceiling` convention already followed) |
| `tests/test_preview_version_sync.py` | test-guard | static-analysis / regex assertion | itself — verify-only, likely NOT modified | n/a — guard reads the 3 sites above; only touch if new package names are added (they are not) |

## Pattern Assignments

### `typsphinx/writer.py` (config/version-declaration, transform)

**Analog:** `typsphinx/template_engine.py` (identical pattern, sibling sync site)

**Current state** (lines 94-97, verified by direct grep this session):
```python
imports.append('#import "@preview/codly:1.3.0": *')
imports.append('#import "@preview/codly-languages:0.1.1": *')
imports.append('#import "@preview/mitex:0.2.4": mi, mitex')
imports.append('#import "@preview/gentle-clues:1.2.0": *')
```

**Target state** (only 2 of 4 lines change; `codly` and its import *style* are untouched):
```python
imports.append('#import "@preview/codly:1.3.0": *')
imports.append('#import "@preview/codly-languages:0.1.10": *')
imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
imports.append('#import "@preview/gentle-clues:1.3.1": *')
```

**Pattern to copy:** Pure literal-string replacement inside `.append(...)` calls — no restructuring, no reordering, no touching the surrounding `if`/loop context this block sits in. Only the version substring inside each `@preview/<pkg>:<version>` literal changes.

---

### `typsphinx/template_engine.py` (config/version-declaration, transform)

**Analog:** `typsphinx/writer.py` (identical pattern, sibling sync site)

**Current state** (lines 313-316, verified by direct grep this session):
```python
output_parts.append('#import "@preview/codly:1.3.0": *')
output_parts.append('#import "@preview/codly-languages:0.1.1": *')
output_parts.append('#import "@preview/mitex:0.2.4": mi, mitex')
output_parts.append('#import "@preview/gentle-clues:1.2.0": *')
```

**Target state**:
```python
output_parts.append('#import "@preview/codly:1.3.0": *')
output_parts.append('#import "@preview/codly-languages:0.1.10": *')
output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
output_parts.append('#import "@preview/gentle-clues:1.3.1": *')
```

**Pattern to copy:** Byte-identical to `writer.py`'s pattern except the collection variable is named `output_parts` instead of `imports`. Apply the exact same version substitutions.

---

### `typsphinx/templates/base.typ` (config/version-declaration, Typst source)

**Analog:** `writer.py` lines 94-97 / `template_engine.py` lines 313-316 (same version set, different host language — Typst, not Python — and one import-style asymmetry)

**Current state** (lines 8-19, verified by direct grep this session — note lines 9→14→19 are not contiguous; other template content sits between them):
```typst
#import "@preview/codly:1.3.0": *          # line 8
#import "@preview/codly-languages:0.1.1": *  # line 9
...
#import "@preview/mitex:0.2.4": *          # line 14 — GLOB import, unlike the named form in writer.py/template_engine.py
...
#import "@preview/gentle-clues:1.2.0": *   # line 19
```

**Target state:**
```typst
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
...
#import "@preview/mitex:0.2.7": *
...
#import "@preview/gentle-clues:1.3.1": *
```

**IMPORTANT — do not touch the import style:** `base.typ`'s mitex import uses a glob (`: *`), while `writer.py`/`template_engine.py` use a named import (`: mi, mitex`). This asymmetry is pre-existing, intentional (or at least not in scope to fix), and must be preserved — only the version number inside the string changes. Do NOT convert `base.typ`'s glob to a named import or vice versa; that is an unrelated refactor outside this phase's scope (per CONTEXT.md's "Planner implementation note").

---

### `pyproject.toml` (config, build/dependency-pin)

**No codebase analog needed** — this is a single dependency-range edit following the project's own established `>=floor,<ceiling` convention (already used for this exact line, and elsewhere in the same `dependencies` array per PROJECT.md's Key Decisions table).

**Current state** (line 30, verified by grep this session):
```toml
"typst>=0.14.1,<0.15",
```

**Target state:**
```toml
"typst>=0.15.0,<0.16",
```

**Follow-up (not a file edit but required for the pin to take effect):**
```bash
uv lock
uv sync --locked
```

---

### `tests/test_preview_version_sync.py` (test-guard, static-analysis)

**Role:** Verification only — this file is the guard, not a pattern-source. Read in full this session (105 lines): it regex-extracts every `#import "@preview/<name>:<version>"` occurrence from all three sync-site files above, builds a `{filename: {package: version}}` map, and asserts version-string agreement per package across the three files. A second test (`test_all_four_packages_declared`) asserts all four package names (`codly`, `codly-languages`, `mitex`, `gentle-clues`) are present in every file.

**Expected disposition:** Likely **no edit needed**. The test is package-name-agnostic and version-string-agnostic by design — it will automatically validate the new versions once all three sync sites are updated identically, with no changes to the test's own assertions or regex logic required. Only touch this file if the bump were to add/remove a package name (it does not — same four packages, same three sites).

**Verification command** (run after each of the three sync-site edits, per RESEARCH.md's sampling-rate guidance):
```bash
pytest tests/test_preview_version_sync.py -x
```

---

## Shared Patterns

### 3-way lockstep version-string replacement (the only pattern this phase needs)

**Source:** `typsphinx/writer.py:94-97`, `typsphinx/template_engine.py:313-316`, `typsphinx/templates/base.typ:8-19` — these three files ARE each other's pattern source; there is no external analog because this exact "three files must declare identical `@preview` version strings" convention is unique to this codebase (documented in `CLAUDE.md` under "The `@preview` version-sync hazard").

**Apply to:** All three sync-site files, in the same commit/change, using this exact substitution table:

| Package | Old version string | New version string | Changes in all 3 sites? |
|---------|--------------------|--------------------|--------------------------|
| `codly` | `1.3.0` | `1.3.0` (unchanged) | No — leave untouched |
| `codly-languages` | `0.1.1` | `0.1.10` | Yes |
| `mitex` | `0.2.4` | `0.2.7` | Yes |
| `gentle-clues` | `1.2.0` | `1.3.1` | Yes |

**Self-check before considering the edit done** (per RESEARCH.md's "Anti-Patterns to Avoid"):
```bash
grep -n "@preview" typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ
```
Confirm all three files show `codly-languages:0.1.10`, `mitex:0.2.7`, `gentle-clues:1.3.1`, and `codly:1.3.0` (unchanged) with no stray old-version strings remaining.

### Dependency-pin convention (`>=floor,<next-major/next-minor ceiling`)

**Source:** `pyproject.toml:30` (this exact line, pre-existing pattern)
**Apply to:** The `typst` pin only (no other dependency lines are in scope for this phase)
```toml
"typst>=0.15.0,<0.16",
```
This follows the project's existing guard-ceiling convention (per PROJECT.md's Key Decisions table) — do not switch to a bare `>=` floor or an exact pin.

### Empirical compile gate (not a code pattern, but the required verification step for every edit above)

**Source:** `tox.ini` `[testenv:docs-pdf]` (existing env, unmodified)
```ini
[testenv:docs-pdf]
description = Build PDF documentation with typstpdf
runner = uv-venv-lock-runner
extras = docs
changedir = docs
commands =
    sphinx-build -b typstpdf source _build/pdf
```
**Apply to:** Run `tox -e docs-pdf` after all sync-site edits + the `pyproject.toml`/`uv.lock` edit are in place. This is the phase's real done-ness gate (per CONTEXT.md D-01) — `test_preview_version_sync.py` passing only proves the three files agree, not that the versions compile under typst 0.15.

## No Analog Found

None — all 5 files have either a direct sibling-site analog (the two Python sync sites mirror each other; `base.typ` mirrors both minus the mitex import-style asymmetry) or are self-contained single-line/no-op edits following an already-established project convention.

## Metadata

**Analog search scope:** `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`, `pyproject.toml`, `tests/test_preview_version_sync.py` — all read/grepped directly this session; no broader codebase search was needed since RESEARCH.md already pinpointed exact line numbers and CONTEXT.md/CLAUDE.md confirm these are the only 3-way sync sites plus the two supporting files (dependency pin + guard test).
**Files scanned:** 5 (all in scope; grep-verified against RESEARCH.md's cited line contents — all matched exactly, no drift since research was performed)
**Pattern extraction date:** 2026-07-11
