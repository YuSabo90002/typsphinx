---
phase: 06-raise-runtime-pins-python-floor
verified: 2026-07-09T23:20:00Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 6: Raise Runtime Pins + Python Floor Verification Report

**Phase Goal:** The extension installs, imports, and registers both builders against Sphinx 9.1 +
docutils 0.22 on Python 3.12–3.13 with a regenerated lockfile — an atomic pin-raise that stands up
the real ecosystem so every downstream phase can diagnose against it.

**Verified:** 2026-07-09T23:20:00Z
**Status:** passed
**Branch:** `release/v0.5.0` (all Phase 6 work confirmed here per D-01; `main` confirmed untouched)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `uv sync --locked` exits 0 against the regenerated lockfile — PIN-03 | ✓ VERIFIED | Ran `uv sync --locked` live: `Resolved 87 packages... Checked 25 packages...`, exit 0 |
| 2 | Lockfile resolves sphinx to 9.1.x and docutils to 0.22.4, typst unchanged in 0.14.1–0.15 — FWD-01 / PIN-01 | ✓ VERIFIED | `grep -A3 'name = "sphinx"' uv.lock` → `version = "9.1.0"`; `grep -A3 'name = "docutils"' uv.lock` → `version = "0.22.4"`; `grep -A2 'name = "typst", specifier'` → `>=0.14.1,<0.15` unchanged |
| 3 | `sphinx-build -b typst tests/roots/test-basic` succeeds, produces `index.typ` + `_template.typ` under Sphinx 9.1 — FWD-01 | ✓ VERIFIED | Live run: `Running Sphinx v9.1.0` ... `build succeeded.`, exit 0; both files present at output path with non-zero size |
| 4 | Both `typst` and `typstpdf` builders register when a Sphinx application is constructed — FWD-01 | ✓ VERIFIED | Live Python registration smoke printed `typst: OK` and `typstpdf: OK`, exit 0 (warnings emitted are pre-existing `sphinx.addnodes` double-registration noise, not errors — not introduced by this phase) |
| 5 | `import typsphinx` succeeds cleanly under the raised stack — FWD-01 | ✓ VERIFIED | `uv run python -c "import typsphinx; print(typsphinx.__version__)"` → `0.4.3`, exit 0, no traceback |
| 6 | Repo-wide grep for old pins/floors (py310, py311, `sphinx>=5.0,<9`, `docutils>=0.18,<0.22`, bare 3.10/3.11) returns zero hits across toml/ini/yml/yaml — PIN-02 | ✓ VERIFIED | Both plan-specified grep commands run live against the full repo tree: zero matches (exit 1 = no match) for both the old-ceiling/py310/py311 pattern and the bare-3.10/3.11 pattern |
| 7 | The typst pin remains `>=0.14.1,<0.15` (Phase 7 scope fence honored) | ✓ VERIFIED | `grep -n "typst>=0.14.1,<0.15" pyproject.toml` → present unchanged; `git diff main release/v0.5.0` on the three `@preview` version-sync files (`writer.py`, `template_engine.py`, `templates/base.typ`) and `tests/test_preview_version_sync.py` is empty — none touched |

**Score:** 7/7 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | `requires-python >=3.12`, classifiers 3.12/3.13 only, `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `types-docutils>=0.21`, black/ruff/mypy target-versions at 3.12(/3.13) | ✓ VERIFIED | Read file directly — all 7 target values present exactly as specified: `requires-python = ">=3.12"` (line 10), classifiers only list `3`, `3.12`, `3.13` (lines 20-22), `dependencies` has `sphinx>=9.1,<10` / `docutils>=0.21,<0.23` / `typst>=0.14.1,<0.15` unchanged (lines 28-30), dev extra `types-docutils>=0.21` (line 43), dead `tomli` conditional line removed (confirmed absent), `[tool.black] target-version = ["py312", "py313"]` (line 85), `[tool.ruff] target-version = "py312"` (line 100), `[tool.mypy] python_version = "3.12"` (line 117) |
| `uv.lock` | Regenerated, sphinx 9.1.x, docutils 0.22.x, header `requires-python >=3.12` | ✓ VERIFIED | Header line 3: `requires-python = ">=3.12"`; sphinx `9.1.0`; docutils `0.22.4`; `git show --stat 1743aef` shows 329 deletions / 28 net additions — genuinely regenerated, not hand-edited |
| `tox.ini` | `env_list` py312/py313, `[testenv]` + `[testenv:type]` sphinx>=9.1,<10 + docutils>=0.21,<0.23 + types-docutils>=0.21 | ✓ VERIFIED | Read file directly — `env_list = py312, py313, lint, type, cov, docs` (line 2), `[testenv]` deps has `sphinx>=9.1,<10` (line 21), `[testenv:type]` deps has `sphinx>=9.1,<10` / `types-docutils>=0.21` / `docutils>=0.21,<0.23` (lines 40-42) |
| `.github/workflows/ci.yml` | matrix `['3.12','3.13']`, single-runner jobs on Python 3.12 | ✓ VERIFIED | Read file directly — matrix `python-version: ['3.12', '3.13']`, `include:` only has 3.12/py312 and 3.13/py313 entries, all 5 single-runner jobs (lint, type-check, coverage, build, integration) install `3.12`, matrix-driven install line untouched (`uv python install ${{ matrix.python-version }}`) |
| `.github/workflows/docs.yml`, `release.yml`, `drift.yml` | single-runner Python 3.12 | ✓ VERIFIED | Read all three files directly — docs.yml `python-version: "3.12"`; release.yml both jobs (validate, build) install `3.12`; drift.yml install `3.12` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `pyproject.toml requires-python` | `uv.lock` header + `ci.yml` matrix | version-floor agreement | ✓ WIRED | All three read `>=3.12` / `['3.12','3.13']` in lockstep — no interpreter mismatch |
| `pyproject.toml docutils` ceiling | `tox.ini [testenv:type]` docutils ceiling + `types-docutils` floor | split-brain manual sync | ✓ WIRED | pyproject `docutils>=0.21,<0.23` / `types-docutils>=0.21` == tox.ini `[testenv:type]` `docutils>=0.21,<0.23` / `types-docutils>=0.21` — exact match, both sites updated together |
| `pyproject.toml [project] sphinx` | `tox.ini [testenv]` + `[testenv:type]` sphinx | triplicated declaration | ✓ WIRED | All three read `sphinx>=9.1,<10` |
| `pyproject.toml` pin edits | `uv.lock` regeneration | atomicity | ✓ WIRED | Both land in the same local commit `1743aef` (`git show --stat`) — no partial state; second commit `058a850` immediately follows with the tox/CI mirror before any push readiness check |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| FWD-01 | 06-01-PLAN.md | sphinx re-pinned `>=9.1,<10`, extension builds/imports/registers both builders under Sphinx 9.1 | ✓ SATISFIED | Truths 1-5 above; live registration smoke + live `-b typst` build both pass |
| PIN-01 | 06-01-PLAN.md | docutils re-pinned `>=0.21,<0.23` | ✓ SATISFIED | pyproject.toml + tox.ini + uv.lock all confirm `docutils>=0.21,<0.23` resolving to `0.22.4` |
| PIN-02 | 06-01-PLAN.md | Python range raised to 3.12-3.13 across every declaration site, 3.10/3.11 dropped | ✓ SATISFIED | All 21 declaration sites read directly + confirmed via live grep audits (zero hits) |
| PIN-03 | 06-01-PLAN.md | `uv.lock` regenerated, `uv sync --locked` green | ✓ SATISFIED | Live `uv sync --locked` exit 0; lockfile header/sphinx/docutils versions confirmed |

REQUIREMENTS.md cross-reference: all four IDs (FWD-01, PIN-01, PIN-02, PIN-03) are marked `[x]` and
"Complete" against Phase 6 in the requirements traceability table — consistent with the evidence
above. No orphaned Phase-6 requirement IDs found in REQUIREMENTS.md beyond these four.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | none found | — | `git diff main release/v0.5.0` on the changed files scanned for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` — zero hits. Pure declaration-surface change as intended; no source code touched. |

### Scope-Fence Compliance (explicitly checked, not reported as gaps per task instructions)

| Fence | Status | Evidence |
|-------|--------|----------|
| `typst` pin stays `>=0.14.1,<0.15` | ✓ HONORED | Unchanged in pyproject.toml and uv.lock |
| 3-way `@preview` version-sync files untouched | ✓ HONORED | `git diff main release/v0.5.0` on `writer.py`, `template_engine.py`, `templates/base.typ`, `tests/test_preview_version_sync.py` is empty |
| No `traverse()`→`findall()` / full pytest-suite work | ✓ HONORED | Only the 7 declared config files were modified (confirmed via `git show --stat` on both commits) |
| No CI-hiding config (`continue-on-error`, skip, `allow-failure`) | ✓ HONORED | Read ci.yml/docs.yml/release.yml/drift.yml in full — none present |
| `main` branch untouched (D-01) | ✓ HONORED | `git log main -3` shows no Phase 6 commits; `git ls-remote --heads origin` shows no `release/v0.5.0` on the remote (local-only, consistent with SUMMARY's "not pushed" claim — pushing was not a required must-have for this phase) |
| PDF/`docs-pdf` lanes not used as a gate | ✓ HONORED | Verification did not invoke `-b typstpdf` or `tox -e docs-pdf`; full pytest suite was not run as a gate |

### Human Verification Required

None. All must-haves are verifiable via fast CLI checks and were run live in this verification
pass (not just re-stated from SUMMARY.md).

### Gaps Summary

No gaps found. All 7 observable truths, all 5 required artifacts (21 declaration sites), and all 4
key links verified directly against the codebase — not inferred from SUMMARY.md claims. All fast
CLI gates specified in the plan's `<verification>` section were re-run independently in this
verification pass and passed:

1. `uv sync --locked` → exit 0.
2. Registration smoke (`typst: OK`, `typstpdf: OK`) → exit 0.
3. `sphinx-build -b typst tests/roots/test-basic` → `build succeeded.`, `index.typ` + `_template.typ` produced.
4. `import typsphinx` → clean.
5. Repo-wide grep audits (old ceilings/py310/py311, bare 3.10/3.11) → zero hits, confirmed live.
6. Atomicity: both task commits (`1743aef`, `058a850`) present on `release/v0.5.0`, together covering pyproject.toml + uv.lock + tox.ini + all 4 workflow files with no partial-pin intermediate state pushed (branch is not pushed to origin at all yet, which is a stronger guarantee against a partial-state push than required).

Requirement traceability (FWD-01, PIN-01, PIN-02, PIN-03) is fully satisfied and consistent between
REQUIREMENTS.md, the PLAN frontmatter, and the actual codebase state on `release/v0.5.0`.

---

_Verified: 2026-07-09T23:20:00Z_
_Verifier: Claude (gsd-verifier)_
