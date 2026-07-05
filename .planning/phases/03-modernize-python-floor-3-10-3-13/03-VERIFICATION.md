---
phase: 03-modernize-python-floor-3-10-3-13
verified: 2026-07-04T00:00:00Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 3: Modernize Python Floor (3.10-3.13) Verification Report

**Phase Goal:** The supported Python range is uniformly modernized to 3.10-3.13 across every config surface, landing as one atomic batch on top of a confirmed-green baseline so any new failure is attributable to the Python bump alone.
**Verified:** 2026-07-04
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `pyproject.toml` `requires-python>=3.10`; classifiers drop 3.9, add 3.13 (SC1 / PYVER-01) | ✓ VERIFIED | Read `pyproject.toml` line 10 (`requires-python = ">=3.10"`) and lines 16-27 (classifiers list contains `3`, `3.10`, `3.11`, `3.12`, `3.13`; no `3.9`) |
| 2 | `ci.yml` test matrix covers 3.10-3.13 and every hardcoded `uv python install` across ci.yml/docs.yml/release.yml is reconciled to the new floor (SC2 / PYVER-02) | ✓ VERIFIED | `grep` of ci.yml: matrix `['3.10','3.11','3.12','3.13']`, include: rows `3.10->py310` .. `3.13->py313` (dotless, no `3.9`/`py39`); matrix-driven install line untouched (`uv python install ${{ matrix.python-version }}`); all 5 hardcoded installs read `uv python install 3.10`; docs.yml `python-version: "3.10"`; release.yml both installs `3.10` |
| 3 | `[tool.black]`/`[tool.ruff]`/`[tool.mypy]` target-versions align to the 3.10 floor (SC3 / PYVER-03) | ✓ VERIFIED | Read pyproject.toml lines 87-88 (`target-version = ["py310","py311","py312","py313"]`), 102-103 (`target-version = "py310"`), 119-120 (`python_version = "3.10"`) |
| 4 | `tox.ini` `env_list` updated to `py310, py311, py312, py313` in lockstep with the CI matrix (SC4 / PYVER-04) | ✓ VERIFIED | `grep env_list tox.ini` -> `env_list = py310, py311, py312, py313, lint, type, cov, docs`; matches ci.yml include: tox-env names exactly (dotless, py313 present, py39 absent) |
| 5 | The full CI matrix is green on 3.10-3.13 (no reformat regression, no 3.13 wheel gap); docs.yml completes end-to-end incl. PDF-copy on the 3.10 floor (SC5 / PYVER-02) | ✓ VERIFIED | Independently re-ran `gh run view 28709253590 --json jobs -q '[.jobs[].conclusion] \| unique'` -> `["success"]` across all 18 ci.yml jobs (12 test-matrix incl. all 3 macOS/windows/ubuntu x Python 3.13 lanes, Lint and Format Check, Type Check, Code Coverage, Build Package, 2 Integration jobs); `gh run view 28709253571` (docs.yml `build-docs`) -> `["success"]`. Both runs are on head `2254dad`, which matches the current branch HEAD (`git log -1 --format=%H` -> `2254dadcabffb253280f0520ce4e3708a5853a6a`), so this is not a stale/superseded run. PR #104 confirmed OPEN, mergeable, base `main`. |
| 6 | `uv.lock` regenerated minimal-diff — no unrelated version bumps rode along (D-04 diff-minimization) | ✓ VERIFIED | Read the full PR #104 diff for `uv.lock`: every changed hunk removes a `<3.10`-marker-gated package/version entry with no corresponding new `+version = "..."` line anywhere in the file (0 `+version` lines total) — i.e. every package collapses onto its single already-resolved `>=3.10` version. The only added dependency edge is `tomli` (docs group, `python_version < '3.11'`, needed for the tomllib backport in Plan 02's remediation), plus the incidental `chardet` removal. No genuine version-number change for any existing package. |
| 7 | `release.yml`'s floor reconciliation is correct (validated by diff-read since it only fires on a real tag push, not this PR) | ✓ VERIFIED | `grep -n "uv python install" .github/workflows/release.yml` -> both lines (33, 86) read `uv python install 3.10`; confirmed by direct file read, no `3.11` remaining |

**Score:** 7/7 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | requires-python >=3.10, classifiers 3.10-3.13, black/ruff/mypy target-versions | ✓ VERIFIED | Read in full; all fields match plan spec exactly |
| `uv.lock` | requires-python >=3.10, minimal-diff regeneration | ✓ VERIFIED | `grep requires-python uv.lock` -> `>=3.10`; PR diff confirms marker-collapse-only shape |
| `tox.ini` | env_list py310-py313 dotless, lockstep w/ CI | ✓ VERIFIED | Direct grep match |
| `.github/workflows/ci.yml` | matrix 3.10-3.13, dotless include mapping, 5 installs -> 3.10 | ✓ VERIFIED | Direct grep match, all lines confirmed |
| `.github/workflows/docs.yml` | setup-python 3.10 | ✓ VERIFIED | Direct grep match |
| `.github/workflows/release.yml` | both installs 3.10 | ✓ VERIFIED | Direct grep match |
| `typsphinx/{builder,pdf,template_engine,translator}.py` (in-batch remediation, not a phase-goal artifact but claimed in 03-02-SUMMARY) | `Optional[X]` -> `X \| None`, `zip(..., strict=False)` | ✓ VERIFIED | `grep "Optional\["` returns 0 hits across all four files; `X \| None` present (2/3/11/5 occurrences respectively); both `zip()` call sites in translator.py carry explicit `strict=False` |
| `tests/test_entry_points.py` (dead-branch removal) | pre-3.10 `entry_points()` fallback removed | ✓ VERIFIED | File read in full — only the 3.10+ `entry_points(group=...)` path remains, no `sys` import, no legacy fallback branch |
| `docs/source/conf.py` (tomllib->tomli backport) | try/except ModuleNotFoundError backport | ✓ VERIFIED | Lines 11-13 confirmed: `import tomllib` / `except ModuleNotFoundError: import tomli as tomllib` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| ci.yml matrix (`python-version`) | ci.yml include: mapping | dotless `py310..py313` tox-env values | ✓ WIRED | 4 rows, exact 1:1 mapping, matches matrix versions |
| ci.yml include: mapping | tox.ini `env_list` | same dotless `py310..py313` env names | ✓ WIRED | `env_list` contains exactly the 4 versioned envs the include: block maps to; no orphaned env on either side |
| pyproject.toml `requires-python` | uv.lock `requires-python` | both `>=3.10` | ✓ WIRED | Confirmed both files read `>=3.10` |
| black/ruff/mypy target-versions | the 3.10-floor interpreter single-version jobs now run on | ci.yml/tox.ini/release.yml all pin single-version jobs to 3.10, matching `[tool.ruff] target-version = "py310"` and `[tool.mypy] python_version = "3.10"` | ✓ WIRED | No mismatch between the lowest pinned CI interpreter (3.10) and the tool target-versions (py310/3.10) |
| docs.yml `setup-python: "3.10"` | `docs/source/conf.py` `tomllib` import | tomli backport + docs optional-dependency | ✓ WIRED | conf.py's try/except backport is exercised live by docs.yml's `build-docs` job on the 3.10 floor, which is green (independently reconfirmed run 28709253571) |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| PYVER-01 | 03-01, 03-02 | `requires-python` set to `>=3.10`; classifiers updated (drop 3.9, add 3.13) | ✓ SATISFIED | pyproject.toml read directly (Truth 1) |
| PYVER-02 | 03-01, 03-02 | CI matrix updated to 3.10-3.13; hardcoded `uv python install` lines reconciled across ci.yml/docs.yml/release.yml | ✓ SATISFIED | Truths 2, 5, 7 |
| PYVER-03 | 03-01, 03-02 | black/ruff/mypy target-versions aligned to 3.10 floor | ✓ SATISFIED | Truth 3; independently reconfirmed `nix run nixpkgs#ruff -- check .` -> "All checks passed!" and `uv run black --check .` -> "50 files would be left unchanged" |
| PYVER-04 | 03-01, 03-02 | tox.ini env_list updated to 3.10-3.13 in lockstep with CI matrix | ✓ SATISFIED | Truth 4 |

No orphaned requirements — REQUIREMENTS.md's traceability table maps exactly PYVER-01..04 to Phase 3, and both 03-01-PLAN.md and 03-02-PLAN.md declare all four in `requirements:` frontmatter. All four are marked `[x]` complete in REQUIREMENTS.md.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| pyproject.toml | 111-112 | Stale comments `# Python 3.9+ support` on the `UP035`/`UP006` ruff ignores | ℹ️ Info | Cosmetic only — these ignores relate to PEP 585 generic-typing lint rules and remain functionally valid at the 3.10 floor; the comment text is just outdated (references the pre-bump floor). Does not affect any success criterion. Non-blocking. |

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers found in any of the phase's modified files (pyproject.toml, uv.lock, tox.ini, ci.yml, docs.yml, release.yml, builder.py, pdf.py, template_engine.py, translator.py, test_entry_points.py, conf.py). No stub patterns (empty returns, static empty responses, unused handlers) — these are config edits and small pyupgrade syntax modernizations, not new logic surfaces.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Local ruff clean at py310 target | `nix run nixpkgs#ruff -- check .` | "All checks passed!" | ✓ PASS |
| Local black clean at py310-py313 target | `uv run black --check .` | "50 files would be left unchanged" | ✓ PASS |
| Local test suite green on the running interpreter (3.13) | `uv run pytest tests/ -q -m "not integration and not slow"` | "402 passed" | ✓ PASS |
| Full CI matrix green (authoritative, hosted runners) | `gh run view 28709253590 --json jobs -q '[.jobs[].conclusion] \| unique'` | `["success"]` (18 jobs incl. all 3.13 lanes) | ✓ PASS |
| docs.yml green on the 3.10 floor | `gh run view 28709253571 --json jobs -q '[.jobs[].conclusion] \| unique'` | `["success"]` | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` conventional probes exist in this repo, and neither PLAN nor SUMMARY declares any probe script for this phase (config-only phase; the authoritative check is the hosted CI matrix, covered above). Skipped.

## Human Verification Required

None. Every must-have truth was verifiable by direct file read or by independently re-querying the live GitHub Actions API (not just reading SUMMARY.md's claimed run IDs) — both re-queried runs (`28709253590` ci.yml, `28709253571` docs.yml) returned `["success"]` job-conclusion sets, and their head SHA (`2254dad`) matches the current branch's HEAD commit, confirming the observation is current and not stale.

Note for the developer's own record (not a verification gap): PR #104 remains OPEN/unmerged, per the plan's design — Task 3 of 03-02-PLAN.md is a blocking `checkpoint:human-verify` gate ("Do not merge or mark Phase 3 done until approved"). The phase's own success criteria (config state + CI green) are fully satisfied regardless of merge timing; merging PR #104 is a separate developer action outside this phase's goal.

## Gaps Summary

No gaps found. All 5 ROADMAP success criteria, all 4 requirement IDs (PYVER-01..04), and all must-have truths from both 03-01-PLAN.md and 03-02-PLAN.md are verified directly against the codebase and the live CI API — not merely asserted by SUMMARY.md. The uv.lock diff was independently inspected line-by-line and confirmed to contain zero unrelated version bumps (only marker-branch collapses, an incidental `chardet` drop, and the intentional `tomli` addition from the in-batch remediation). The in-batch ruff/pyupgrade remediation and tomllib->tomli backport (added in Plan 02 to unblock CI, not in the original Plan 01 scope) were also verified present and correctly applied.

---

_Verified: 2026-07-04_
_Verifier: Claude (gsd-verifier)_
