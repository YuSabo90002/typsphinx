# Phase 4: Refresh Dev Tooling - Pattern Map

**Mapped:** 2026-07-05
**Files analyzed:** 5 (no new files — all modifications to existing config/doc surfaces)
**Analogs found:** 5 / 5 (all analogs are prior-phase edits to these same surfaces)

This phase creates **no new source files**. Every "file to modify" already exists;
the most valuable analog for each is the **prior phase's own edit** to that same
surface (Phase 1's tox↔pyproject mirror-pinning; Phase 3's per-surface-commit +
minimal-diff-lock + push→observe sequence), not a different file in the tree.

## File Classification

| File to Modify | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `pyproject.toml` `[project.optional-dependencies] dev` | config (dependency manifest) | batch (constraint-string edit → resolver input) | Phase 1's `pyproject.toml` runtime-ceiling edit (`typst`/`sphinx`/`docutils`) + Phase 3's Task 1 (`requires-python`/target-version bump) | exact — same file, same section-editing technique, same author intent (floor+ceiling / lockstep) |
| `pyproject.toml` ruff `UP035`/`UP006` comment text | config (comment-only) | transform (string replace) | Phase 3 D-04's README/pyproject text-cleanup precedent (folded-in doc fix pattern) | role-match |
| `tox.ini` `[testenv]`/`[testenv:lint]`/`[testenv:type]` `deps` | config (tox env manifest) | batch (mirrored constraint-string edit) | Phase 1's `tox.ini` dep-ceiling mirror (PIN-04) + Phase 3 Task 2 (`env_list` bump) | exact |
| `tox.ini` `[tox] requires = tox-uv>=1.0` (4th mirror point, D-07) | config (tox bootstrap) | batch | Same `tox.ini`, no direct prior-phase precedent for this specific line (new in Phase 4 per D-07) — nearest analog is the `[testenv*]` deps mirror technique applied to a different section | role-match (novel 4th surface, but identical mirror mechanics) |
| `README.md` lines 36 & 323 (Python 3.9→3.10) | doc (plain text) | transform (string replace) | Phase 3's `pyproject.toml` classifier cleanup (3.9 removed, 3.13 added) — same "modernize stale version reference" intent, applied to prose instead of TOML | role-match |
| `.github/workflows/ci.yml` / `docs.yml` — `upload-artifact@v5→v7`, `download-artifact@v6→v8` | config (CI workflow YAML) | event-driven (workflow trigger → job steps) | Phase 3 Task 3 (`ci.yml`/`docs.yml`/`release.yml` interpreter-pin reconciliation) — same "bump a version string across multiple workflow files, verify via push→observe" technique | role-match |
| `uv.lock` (regenerated, not hand-edited) | config (generated lockfile) | batch (resolver output) | Phase 3 Task 1's `uv lock` regeneration (marker-branch collapse, minimal-diff verification) | exact |

## Pattern Assignments

### `pyproject.toml` `[project.optional-dependencies] dev` (config, batch)

**Analog:** This same file, Phase 1's ceiling-adding edit and Phase 3's floor-bump edit (both already merged into current `pyproject.toml`).

**Current state to edit** (`/home/yuta/Documents/typsphinx/pyproject.toml` lines 35-48):
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
    "pre-commit>=3.0",
    "types-docutils>=0.18",
    "twine>=5.0",
    "build>=1.0",
]
```

**Target state** (per D-01/D-02/D-07/D-08 — exact ceiling syntax is planner's discretion):
```toml
dev = [
    "pytest>=8.4,<10",       # or >=9,<10 — planner picks (D-01)
    "pytest-cov>=4.0",       # untouched — not in D-02's tool list
    "tox>=4.56,<5",
    "tox-uv>=1.35,<2",       # D-07 — 4th mirror point, in scope
    "black>=26,<27",
    "ruff>=0.15,<0.16",
    "mypy>=1.13,<3.0",       # D-08 — literal D-01 syntax, do NOT raise floor to >=2
    "pre-commit>=3.0",       # untouched — not in D-02's tool list
    "types-docutils>=0.18",
    "twine>=5.0",
    "build>=1.0",
]
```

**Precedent for the floor+ceiling edit technique — Phase 1's runtime-dependency edit** (established D-01/D-02 there, same file):
```toml
# Source: Phase 1 (01-CONTEXT.md D-01) — analogous "add ceiling to existing floor" edit
dependencies = [
    "sphinx>=5.0,<9",
    "docutils>=0.18,<0.22",
    "typst>=0.14.1,<0.15",
]
```
Phase 1's rule ("upper bounds only, keep existing floors, strict reproducibility carried by regenerated `uv.lock` not exact `==` pins") is the direct ancestor of D-02's "floor-at-resolved + one guard ceiling" — same technique, extended from runtime deps to dev deps.

**Precedent for regenerating `uv.lock` minimal-diff after this edit — Phase 3 Task 1** (`03-01-SUMMARY.md` key-decisions):
> "Ran plain `uv lock` (no `--upgrade`) per the plan's hard gate; `git diff uv.lock` showed only the expected marker-branch collapse... plus the incidental `Removed chardet v5.2.0` line — no genuine version bump."

Apply the identical gate here: `uv lock` (never `--upgrade`), then `git diff uv.lock` must show only entries tied to the touched dev-tool constraints, no unrelated transitive bumps.

**Do NOT touch** (out of scope per D-02/Research Pitfalls 2-3):
- `[dependency-groups] dev = ["types-docutils>=0.22.2.20251006"]` at lines 134-137 — a separate PEP 735 surface, not named in D-02, leave as-is.
- `pytest-cov`, `pre-commit`, `twine`, `build`, `types-docutils` floors — not in D-02's tool list.

---

### `pyproject.toml` ruff `UP035`/`UP006` comment text (config, transform)

**Analog:** Phase 3's "fold small doc fix into the batch" precedent (D-04 here mirrors Phase 3's approach of doing text cleanup alongside the main version-floor work, not as a separate phase).

**Current state** (`/home/yuta/Documents/typsphinx/pyproject.toml` lines 111-112):
```toml
    "UP035",  # typing.Dict/List/Set deprecation (Python 3.9+ support)
    "UP006",  # Use dict instead of Dict (Python 3.9+ support)
```

**Target state** (per D-04 — "Python 3.9+ support" → reflect the current 3.10 floor):
```toml
    "UP035",  # typing.Dict/List/Set deprecation (Python 3.10+ support)
    "UP006",  # Use dict instead of Dict (Python 3.10+ support)
```
(Exact replacement wording is a comment-only change; no functional effect — verify `ruff check .` and `black --check .` stay clean, per Research Pitfall 4.)

---

### `tox.ini` `[testenv]` / `[testenv:lint]` / `[testenv:type]` `deps` (config, batch)

**Analog:** Phase 1's PIN-04 tox-mirror precedent + Phase 3 Task 2's `env_list` edit (same file, same "mirror pyproject.toml exactly" discipline).

**Current state to edit** (`/home/yuta/Documents/typsphinx/tox.ini`):
```ini
[testenv]
description = Run tests with pytest
package = wheel
wheel_build_env = .pkg
runner = uv-venv-lock-runner
deps =
    pytest>=7.0
    pytest-cov>=4.0
    sphinx>=5.0,<9
commands =
    pytest {posargs:tests/}

[testenv:lint]
description = Run linting checks
runner = uv-venv-lock-runner
deps =
    black>=23.0
    ruff>=0.1.0
commands =
    black --check .
    ruff check .

[testenv:type]
description = Run type checking with mypy
runner = uv-venv-lock-runner
deps =
    mypy>=1.0
    sphinx>=5.0,<9
    types-docutils>=0.18
    docutils>=0.18,<0.22
commands =
    mypy typsphinx/
```

**Target state:** mirror the exact strings chosen for `pyproject.toml [dev]` above:
- `[testenv]`: `pytest>=8.4,<10` (or `>=9,<10`), leave `pytest-cov>=4.0` and `sphinx>=5.0,<9` untouched.
- `[testenv:lint]`: `black>=26,<27`, `ruff>=0.15,<0.16`.
- `[testenv:type]`: `mypy>=1.13,<3.0`, leave `sphinx`/`types-docutils`/`docutils` untouched.

**Important — `[testenv:cov]` inherits, do not duplicate** (RESEARCH.md, verified this session, `tox.ini` lines 39-44):
```ini
[testenv:cov]
description = Run tests with coverage
deps =
    {[testenv]deps}
commands =
    pytest --cov=typsphinx --cov-report=term-missing --cov-report=html {posargs:tests/}
```
Bumping `[testenv]`'s `pytest` string automatically propagates here via the `{[testenv]deps}` substitution — do not add a second pytest line.

**Precedent for the mirror-editing discipline — Phase 1 (`01-CONTEXT.md`, "Carried-Forward / Pre-Locked"):**
> "`tox.ini` `[testenv]` and `[testenv:type]` dep lists must mirror the same ceilings as `pyproject.toml` so no tox env independently re-resolves an unbounded version (PIN-04)."

This is the exact rule D-02b restates for Phase 4's dev tools — same file, same two sections (`[testenv]`, `[testenv:type]`), same mechanism.

---

### `tox.ini` `[tox] requires = tox-uv>=1.0` (4th mirror point, D-07)

**Current state** (`/home/yuta/Documents/typsphinx/tox.ini` line 4):
```ini
[tox]
env_list = py310, py311, py312, py313, lint, type, cov, docs
isolated_build = True
requires = tox-uv>=1.0
```

**Target state** (D-07):
```ini
requires = tox-uv>=1.35,<2
```
Must be bumped **in lockstep** with the same string in `pyproject.toml [dev]`'s `tox-uv` entry — this is a distinct section (`[tox]`, not `[testenv*]`) but the identical mirror discipline applies (Research Pitfall 2: easy to miss because it's outside the `[testenv*]` blocks a naive grep would find).

---

### `README.md` Python 3.9 references (doc, transform)

**Analog:** Phase 3's classifier cleanup in `pyproject.toml` (same "drop the stale floor reference" intent, prose instead of TOML) — no README-specific prior-phase edit exists, so this is a role-match, not exact.

**Current state:**
```markdown
# Line 36 (/home/yuta/Documents/typsphinx/README.md)
- Python 3.9 or higher

# Line 323
**Python**: 3.9+ | **Sphinx**: 5.0+ | **Typst**: 0.11.1+
```

**Target state (D-04):**
```markdown
- Python 3.10 or higher
...
**Python**: 3.10+ | **Sphinx**: 5.0+ | **Typst**: 0.11.1+
```

**Precedent — Phase 3's `pyproject.toml` classifier edit** (`03-01-SUMMARY.md`, Accomplishments): "`pyproject.toml` now declares `requires-python = ">=3.10"`, drops the 3.9 classifier, adds the 3.13 classifier" — same underlying floor (3.10), same "remove the stale lower version, don't touch anything else" scope discipline, now applied to the two README lines Phase 3 left behind.

---

### `.github/workflows/ci.yml` / `docs.yml` — `upload-artifact@v5→v7`, `download-artifact@v6→v8`

**Analog:** Phase 3 Task 3 — the `ci.yml`/`docs.yml`/`release.yml` interpreter-pin reconciliation (`03-01-SUMMARY.md` Task Commits #3, commit `2e285d4`), the closest prior "bump a version string across multiple workflow files uniformly" precedent, plus Phase 3 Plan 02's push→observe verification of workflow changes.

**Current occurrences verified this session** (`grep -n` across `.github/workflows/*.yml`):
```
docs.yml:46,52   uses: actions/upload-artifact@v5
ci.yml:47,126,155,188   uses: actions/upload-artifact@v5
release.yml:100  uses: actions/upload-artifact@v5
release.yml:116,137,206  uses: actions/download-artifact@v6
```

**Target state (research recommendation, pending planner/user confirmation per Open Question 1):**
```yaml
uses: actions/upload-artifact@v7    # was @v5 (node20 → node24)
uses: actions/download-artifact@v8  # was @v6 (node20 → node24)
```
Apply uniformly to **every** occurrence across `ci.yml`, `docs.yml`, and (if in scope) `release.yml` — same multi-file, same-string, uniform-bump technique Phase 3 Task 3 used for the Python-version pins (`grep -n python-version:/tox-env:/uv python install` across all three workflow files, single pass).

**Do NOT change:** `actions/checkout@v6`, `actions/setup-python@v6`, `astral-sh/setup-uv@v7`, `codecov/codecov-action@v5` — per D-03, all four remain current/`node24`-or-composite, no edit.

**Precedent for the push→observe verification of a workflow-file change — Phase 3 Plan 02** (`03-02-SUMMARY.md`):
```
- ci.yml run https://.../runs/28709010375 — conclusion success (18 jobs)
- docs.yml run https://.../runs/28709010382 — conclusion success
```
Reuse this exact gate (D-05) for the artifact-action bump: push a PR targeting `main`, observe `ci.yml` + `docs.yml` green on the new head before closing the phase.

---

### `uv.lock` (regenerated, batch)

**Analog:** Phase 3 Task 1's regeneration gate (already excerpted above under `pyproject.toml`).

**Core pattern to copy verbatim:**
```bash
# Source: Phase 3 Task 1 precedent, STATE.md — do NOT use --upgrade
uv lock
git diff uv.lock   # confirm only entries tied to touched constraints changed
```
Expect: version bumps for black, ruff, tox, tox-uv, pytest, mypy (matching the resolved versions already in `uv.lock` today — 26.5.1/0.15.20/4.56.1/1.35.2/9.1.1/2.1.0 — so if these are *already* the resolved versions, the diff may show **zero** version changes, only the constraint-string metadata, similar to Phase 3's "marker-branch collapse, no genuine version bump" outcome). Any unexpected transitive-dependency bump outside the touched packages should be treated as a deviation to flag, not silently committed.

---

## Shared Patterns

### Per-surface commit granularity (D-06)
**Source:** Phase 3 Plan 01 (`03-01-SUMMARY.md` tech-stack.patterns): "Per-surface commit granularity for a config-only phase (D-04): pyproject+lock as one atomic commit, tox.ini alone, then the three workflow YAMLs together"
**Apply to:** All Phase 4 file edits — land as (1) `pyproject.toml` dev deps + regenerated `uv.lock`, (2) `tox.ini` env deps (+ `[tox] requires`), (3) README + ruff-comment cleanup, (4) workflow artifact-action bump (if confirmed in-scope) — each its own commit within a single PR.

### Minimal-diff `uv.lock` regeneration (no `--upgrade`)
**Source:** Phase 3 Task 1 (`03-01-SUMMARY.md` key-decisions, quoted above) and Phase 3 Plan 02 (`03-02-SUMMARY.md`: "Ran plain `uv lock` (no `--upgrade`)... producing a minimal 2-line diff")
**Apply to:** The `pyproject.toml`-dev-deps commit and any subsequent lock regeneration this phase requires.

### Push → observe = done (D-05)
**Source:** Phase 2/3 established pattern, most concretely demonstrated in `03-02-SUMMARY.md`'s "CI Re-observation" section (gh run URLs + job-conclusion checks for both `ci.yml` and `docs.yml`, plus a human-verify checkpoint before merge).
**Apply to:** The phase-closing gate — push a PR targeting `main`, fetch `gh run view <id> --json jobs -q '[.jobs[].conclusion] | unique'` and confirm `["success"]` for both `ci.yml` and `docs.yml`, before marking Phase 4 done.

### tox↔pyproject "mirror, don't inherit" (D-02b, D-07)
**Source:** Phase 1 `01-CONTEXT.md` ("`tox.ini` ... must mirror the same ceilings as `pyproject.toml`... PIN-04") — the direct ancestor of D-02b/D-07 in this phase.
**Apply to:** Every constraint string bumped in `pyproject.toml [dev]` must have its exact-same string re-typed (not inherited/interpolated) into the corresponding `tox.ini` section — `[testenv]`, `[testenv:lint]`, `[testenv:type]`, and (new for Phase 4, D-07) `[tox] requires`.

## No Analog Found

None. Every file/section this phase touches has either a direct prior-phase edit to the same file (exact match) or a clear structural analog from Phase 1/3's config-refresh work (role-match). No net-new source files are created in this phase.

## Metadata

**Analog search scope:** `/home/yuta/Documents/typsphinx/pyproject.toml`, `tox.ini`, `README.md`, `.github/workflows/{ci,docs,release}.yml`, `.planning/phases/01-pin-runtime-dependencies-to-known-good/01-CONTEXT.md`, `.planning/phases/03-modernize-python-floor-3-10-3-13/{03-01-SUMMARY.md,03-02-SUMMARY.md}`
**Files scanned:** 8 (5 target config/doc files + 3 prior-phase context/summary docs)
**Pattern extraction date:** 2026-07-05
