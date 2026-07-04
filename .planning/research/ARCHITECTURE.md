# Architecture Research: Maintenance Edit Surface

**Domain:** CI-repair / dependency-pinning maintenance milestone (typsphinx)
**Researched:** 2026-07-04
**Confidence:** HIGH — every path below was read directly from the repo at HEAD; no external research was needed for this dimension (this is a codebase-topology question, not an ecosystem question).

## Scope of This Document

This is not "how does the translator work" (already covered by `.planning/codebase/ARCHITECTURE.md`). This is: **where do version/config edits physically land, in what groups, and in what order**, so the roadmap can phase the maintenance work without ever leaving the repo in a broken intermediate state.

Four independent edit *concerns* were found. They have different blast radii and different verification gates, which is why they should be phased separately rather than as one giant diff.

## Files-to-Edit, Grouped by Concern

### Concern A — Runtime dependency pins (the actual CI-breaking bug)

| File | Exact site | Current state | Edit needed |
|------|-----------|----------------|--------------|
| `pyproject.toml` | `[project].dependencies` (lines 29–33) | `sphinx>=5.0`, `docutils>=0.18`, `typst>=0.14.1` — all unbounded above | Add upper bounds: `typst` pinned to a 0.14.x-line ceiling (e.g. `>=0.14.1,<0.15`), `sphinx` and `docutils` capped below their newly-resolved majors (e.g. `sphinx>=5.0,<9.0`, `docutils>=0.18,<0.22`) |
| `uv.lock` | whole file (resolved: `typst==0.15.0`, `sphinx==9.1.0`/`9.0.4`/`8.1.3`/`7.4.7` per Python version, `docutils==0.22.4`/`0.21.2`) | Stale — resolves the newer majors that broke CI | Regenerate (`uv lock`) *after* the pyproject ceilings land, so it re-resolves to the known-good line |
| `tox.ini` | `[testenv].deps` (line 14: `sphinx>=5.0`) and `[testenv:type].deps` (lines 34–36: `sphinx>=5.0`, `types-docutils>=0.18`, `docutils>=0.18`) | Duplicate, independently-unbounded version constraints — **not** derived from `pyproject.toml` | Mirror the same ceilings here. This is a hidden 4th sync hazard: tox's `deps=` lists are hand-maintained copies of the runtime constraint and will silently drift from `pyproject.toml` if only one is edited |

**Why this is the highest-priority concern:** the CI failure evidence in `.planning/PROJECT.md` (`typst.TypstError: unknown variable: kai`) traces directly to `typst==0.15.0` being resolved. Nothing else in the repo needs to change to turn this green.

### Concern B — The three hardcoded `@preview` version sites (sync hazard)

These three locations declare the **same four Typst Universe package pins** independently, as literal strings, with no shared constant:

| # | File | Lines | What's declared |
|---|------|-------|------------------|
| 1 | `typsphinx/writer.py` | 94–97, inside `TypstWriter.translate()` — the "included document" (non-master) import block | `@preview/codly:1.3.0`, `@preview/codly-languages:0.1.1`, `@preview/mitex:0.2.4` (as `mi, mitex`), `@preview/gentle-clues:1.2.0` |
| 2 | `typsphinx/template_engine.py` | 313–316, inside `TemplateEngine.render()` — the "master document" essential-imports block | Same four packages/versions, same `mi, mitex` import spec for mitex |
| 3 | `typsphinx/templates/base.typ` | 8, 9, 14, 19 — the bundled default template's top-of-file imports | Same four packages/versions, but mitex is imported as `*` (all symbols) rather than `mi, mitex` — a pre-existing minor import-style inconsistency, not a version mismatch |

**Current status: all three agree** (codly 1.3.0, codly-languages 0.1.1, mitex 0.2.4, gentle-clues 1.2.0) — confirmed by direct read, matching the tech-debt note already logged in `.planning/codebase/CONCERNS.md`.

**The hazard, explicitly:** a single compiled PDF pulls from *both* sites 1/2 and site 3 (or 1 and 2) at once — the master document's imports (site 2, or site 3 if no template override) coexist in the same compilation graph as an included document's imports (site 1), because Typst's `#include()` does not propagate imports across file boundaries — each file must re-declare its own. If only one of the three sites is edited to bump a package version (e.g. `codly:1.3.0` → `1.4.0` in `template_engine.py` but not in `writer.py`), the master file and an included file end up importing **two different versions of the same Typst package into one compilation**. That is structurally the same class of failure already seen in this milestone's motivating bug (`unknown variable: kai` — a package/compiler version mismatch), just self-inflicted instead of externally triggered. Symptoms would range from a hard compile error to silent, inconsistent rendering (e.g. `codly-init` initialized against one package version, `codly()` called against another).

**For this milestone specifically:** since the fix is pinning the *typst compiler* down to 0.14.x (Concern A), not bumping the bundled `@preview` package versions, these three sites likely do **not** need to change. The action item is verification, not edit: confirm all three still read identically after the pin lands, and do not let a future PR touch one without grepping for the other two. Any future work that *does* change one of these four package versions must change it in all three files in the same commit — this is the single most important cross-file invariant in the whole edit surface, more important than any single file's diff.

**Recommended guardrail (optional, out of scope for "green" but cheap insurance):** a one-line grep-based CI check (`grep -c '@preview/codly:1.3.0'` across the three files, asserting count matches expected occurrences) would catch a silent divergence before it reaches a release. Not required to close this milestone.

### Concern C — CI/workflow matrix and action versions

| File | Edit site | Current state | Edit needed |
|------|-----------|----------------|--------------|
| `.github/workflows/ci.yml` | `jobs.test.strategy.matrix.python-version` (line 18) | `['3.9', '3.10', '3.11', '3.12']` | Drop `3.9`, add `3.13` → `['3.10', '3.11', '3.12', '3.13']` |
| `.github/workflows/ci.yml` | `lint`/`type-check`/`coverage`/`build`/`integration` jobs' fixed `uv python install 3.11` (lines 59, 80, 101, 135, 167) | Hardcoded to 3.11 | No change required — 3.11 is inside the new 3.10–3.13 floor/ceiling; only touch if standardizing on a different single version |
| `.github/workflows/docs.yml` | `actions/setup-python@v6` `python-version: "3.11"` (lines 22–24) | 3.11 | No change required, same reasoning |
| `.github/workflows/release.yml` | `uv python install 3.11` (lines 33, 86) | 3.11 | No change required |
| `.github/dependabot.yml` | exists, two ecosystems: `pip` (weekly) and `github-actions` (monthly) | Present, generic — does not itself pin any version | No edit required to fix CI, but note its role below |
| `.github/workflows/*.yml` | action versions (`actions/checkout@v6`, `astral-sh/setup-uv@v7`, `actions/upload-artifact@v5`, `actions/download-artifact@v6`, `codecov/codecov-action@v5`, `actions/setup-python@v6`, `pypa/gh-action-pypi-publish@release/v1`, `peaceiris/actions-gh-pages@v4`, `softprops/action-gh-release@v2`) | Already fairly current across all three workflow files | Optional refresh pass only — not required for green, low risk, do last |

**`flake.nix` — explicitly does NOT pin a Python version.** It declares `pkgs.python3` and `pkgs.uv` from `nixpkgs-unstable` with no version constraint at all (confirmed by direct read — no `python310`/`python311` selector, just the rolling `python3` alias). This means `flake.nix` is **not an edit site** for the Python-floor bump; it will pick up whatever Python 3 nixpkgs-unstable currently ships. No action needed here for this milestone, but worth flagging: local Nix-shell development is not protected by the same floor/ceiling as CI, so a contributor on `nix develop` could be on a Python version outside the declared 3.10–3.13 support range without any error.

**`.github/dependabot.yml`'s role:** it did **not** cause the drift (loose `>=` constraints with no ceiling meant dependabot had nothing to "bump" — the drift came from fresh `uv sync`/`uv lock` resolution picking the newest allowed version, not from a merged dependabot PR). Its relevance going forward is different: once Concern A adds upper bounds to `pyproject.toml`, dependabot's `pip` ecosystem entries will respect those ceilings and stop proposing PRs that cross them — so tightening the pins in Concern A also fixes dependabot's future behavior as a side effect. No edit to `dependabot.yml` itself is required.

### Concern D — Tool target-version alignment (follows the Python floor bump)

| File | Edit site | Current state | Edit needed |
|------|-----------|----------------|--------------|
| `pyproject.toml` | `[project].requires-python` (line 10) | `>=3.9` | `>=3.10` |
| `pyproject.toml` | `[project].classifiers` (lines 21–24) | Lists `3.9`, `3.10`, `3.11`, `3.12` | Drop `3.9` classifier, add `3.13` classifier |
| `pyproject.toml` | `[tool.black].target-version` (line 88) | `["py39", "py310", "py311", "py312"]` | `["py310", "py311", "py312", "py313"]` |
| `pyproject.toml` | `[tool.ruff].target-version` (line 103) | `"py39"` | `"py310"` |
| `pyproject.toml` | `[tool.mypy].python_version` (line 120) | `"3.9"` | `"3.10"` |
| `tox.ini` | `[tox].env_list` (line 2) | `py39, py310, py311, py312, lint, type, cov, docs` | `py310, py311, py312, py313, lint, type, cov, docs` |
| `pyproject.toml` | `[tool.ruff.lint].ignore` comments referencing "Python 3.9+ support" (`UP035`, `UP006`, `UP028`, lines 111–113) | Justified by the 3.9 floor | Not required to change for green, but once the floor is 3.10 these ignores are candidates for removal in a later cleanup — flagged, not required this milestone |

**Dependency note:** Concern D's `tox.ini` env_list edit and Concern C's `ci.yml` matrix edit are two names for the same fact (the supported Python list) expressed in two files — they must be edited together, in the same commit, or `tox -e py313` will exist with nothing in CI ever invoking it (or vice versa: CI matrix requests `py313` but no such tox env exists, producing a hard tox error, not a silent skip).

## Synchronization Hazards Summary

| Hazard | Sites involved | Failure mode if desynced | Severity |
|--------|-----------------|---------------------------|----------|
| **@preview package version drift** | `writer.py` (94–97), `template_engine.py` (313–316), `templates/base.typ` (8,9,14,19) | Two different versions of the same Typst package loaded into one compiled document → compile error or silent bad output (same failure *class* as the `kai` bug) | Critical — always edit all three together, never touch in isolation |
| **Runtime dep ceiling vs. tox's duplicate deps** | `pyproject.toml` dependencies vs. `tox.ini` `[testenv]`/`[testenv:type]` `deps=` | tox resolves an unbounded `sphinx`/`docutils` even after `pyproject.toml` is capped, silently reintroducing the same class of break in the `type` env specifically | High — this is easy to miss because it's not the file anyone thinks to check first |
| **Python-support-list vs. tox env_list vs. CI matrix** | `pyproject.toml` `requires-python`/classifiers, `tox.ini` `env_list`, `ci.yml` matrix | CI requests a tox env that doesn't exist (hard failure), or tox supports a version CI never tests (silent gap, not a break) | Medium — must land in one commit, but failure mode is loud (build breaks obviously) rather than silent |
| **Tool target-versions lagging the floor** | `[tool.black]`, `[tool.ruff]`, `[tool.mypy]` in `pyproject.toml` | Lint/type-check jobs pass but reference a Python version below the actual floor — not a hard break, just a stale-tooling smell that resurfaces the next time this milestone-style drift happens | Low |

## Suggested Safe Build Order

The core principle: **isolate the bug-fix pin from the modernization work**, so if the pin alone doesn't turn CI green, that failure is not entangled with an unrelated Python-matrix change, and vice versa.

```
Phase 1 — Pin runtime deps to known-good (Concern A only)
    │
    │  Edit: pyproject.toml [project].dependencies ceilings
    │        tox.ini [testenv]/[testenv:type] deps ceilings (mirror exactly)
    │        regenerate uv.lock
    │
    │  Gate: full CI matrix green (lint, test matrix, coverage, docs-pdf)
    │        — this is the actual bug fix; verify it in isolation before
    │          touching anything else, so a red run is unambiguous
    ▼
Phase 2 — Verify the @preview 3-way sync is untouched (Concern B, verification only)
    │
    │  No edit expected. Confirm writer.py / template_engine.py / base.typ
    │  still agree after Phase 1's typst pin (they should — this milestone
    │  pins the compiler, not the packages). Grep all three, diff against
    │  the table in this document.
    ▼
Phase 3 — Bump Python floor + CI matrix + tool targets together (Concerns C + D, one atomic batch)
    │
    │  Edit (single commit/PR): pyproject.toml requires-python, classifiers,
    │        [tool.black]/[tool.ruff]/[tool.mypy] target-versions
    │        tox.ini env_list
    │        ci.yml matrix.python-version
    │
    │  Gate: full CI matrix green again, now on 3.10–3.13
    │        — do this only after Phase 1 is confirmed green, so a failure
    │          here is known to be about the Python bump, not the dep pins
    ▼
Phase 4 — Optional low-risk refresh (action versions, dependabot hardening)
    │
    │  Edit: any workflow action version bumps not already current
    │        optionally add pip ceilings-awareness note to dependabot.yml
    │        (no functional edit required — ceilings from Phase 1 already
    │        constrain it)
    │
    │  Gate: none blocking — this can land anytime, even in parallel with
    │        Phase 3, since it's decoupled from both the pin and the
    │        Python-version work
```

**Rationale for this order:**
1. Phase 1 must be first and alone because it is the actual fix for the CI-red state described in `.planning/PROJECT.md` — everything else is opportunistic modernization riding along in the same milestone. Landing Python-3.13 support on top of a still-broken `typst` pin would make it impossible to tell which change fixed (or didn't fix) what.
2. Phase 2 costs nothing (no edit expected) but must happen before anyone assumes the @preview sites are "handled" — it's the cheapest place to catch a surprise incompatibility between typst 0.14.x and the bundled package versions before it ships.
3. Phase 3 is the only place where three files (`pyproject.toml`, `tox.ini`, `ci.yml`) must move in lockstep — bundling them into one PR avoids a state where `tox -e py313` exists but CI never calls it, or CI's matrix references a tox env that doesn't exist yet.
4. Phase 4 is genuinely independent — action-version bumps and dependabot config don't interact with the Python or typst pins at all, so sequencing them last (or in parallel) carries no risk and keeps the higher-stakes phases' diffs focused and easy to bisect.

## Sources

- Direct repository reads (HEAD, 2026-07-04): `pyproject.toml`, `tox.ini`, `flake.nix`, `uv.lock`, `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `.github/workflows/release.yml`, `.github/dependabot.yml`, `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`
- `.planning/PROJECT.md` (milestone context, CI failure evidence)
- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/CONCERNS.md` (existing codebase map — corroborates the @preview hardcoding tech-debt note)

---
*Architecture research for: typsphinx CI-repair/maintenance milestone*
*Researched: 2026-07-04*
