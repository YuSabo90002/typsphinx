---
phase: 03-modernize-python-floor-3-10-3-13
plan: 01
subsystem: infra
tags: [python, uv, tox, github-actions, pyproject, black, ruff, mypy]

# Dependency graph
requires:
  - phase: 02-verify-the-green-baseline
    provides: Confirmed-green full CI matrix on the pre-existing 3.9-3.12 range (Phase 2 D-01), the dotless include:-mapping fix (TEST-01), and the @preview version-sync guard test — the stable baseline this plan bumps forward.
provides:
  - "pyproject.toml requires-python floor moved from >=3.9 to >=3.10; classifiers drop 3.9, add 3.13"
  - "[tool.black]/[tool.ruff]/[tool.mypy] target-versions aligned to the 3.10 floor"
  - "uv.lock regenerated (plain uv lock, no --upgrade) with all <3.10 marker branches collapsed and the transitive chardet dep dropped"
  - "tox.ini env_list updated to py310-py313 (dotless), in lockstep with the CI matrix"
  - "ci.yml test matrix + include: mapping updated to 3.10-3.13/py310-py313; all five hardcoded single-version installs (lint/type/coverage/build/integration) moved 3.11 -> 3.10"
  - "docs.yml setup-python and release.yml's two uv python install lines moved 3.11 -> 3.10"
affects: [03-02-push-observe-full-matrix]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-surface commit granularity for a config-only phase (D-04): pyproject+lock as one atomic commit, tox.ini alone, then the three workflow YAMLs together"
    - "uv.lock regeneration without --upgrade to collapse Python-floor marker branches without pulling unrelated dependency bumps"

key-files:
  created: []
  modified:
    - pyproject.toml
    - uv.lock
    - tox.ini
    - .github/workflows/ci.yml
    - .github/workflows/docs.yml
    - .github/workflows/release.yml

key-decisions:
  - "Ran plain `uv lock` (no --upgrade) per the plan's hard gate; git diff uv.lock showed only the expected <3.10 marker-branch collapse (every uv-lock stdout line read `Updated X vOLD, vNEW -> vNEW`) plus the incidental `Removed chardet v5.2.0` line — no genuine version bump, so the commit proceeded without flagging a deviation."
  - "black --check . reported '50 files would be left unchanged' both before and after the target-version bump to [py310,py311,py312,py313] — confirming D-03's no-op prediction, so no separate reformat commit was needed."

requirements-completed: [PYVER-01, PYVER-02, PYVER-03, PYVER-04]

coverage:
  - id: D1
    description: "pyproject.toml requires-python bumped to >=3.10; classifiers drop 3.9, add 3.13"
    requirement: "PYVER-01"
    verification:
      - kind: unit
        ref: "uv run python -c \"import tomllib; ...\" — printed req: >=3.10, cls containing 3.10/3.11/3.12/3.13 and no 3.9"
        status: pass
    human_judgment: false
  - id: D2
    description: "black/ruff/mypy target-versions aligned to the 3.10 floor"
    requirement: "PYVER-03"
    verification:
      - kind: other
        ref: "Read pyproject.toml lines confirming target-version=[py310,py311,py312,py313], py310, python_version=3.10"
        status: pass
      - kind: unit
        ref: "uv run black --check . -- 50 files would be left unchanged"
        status: pass
    human_judgment: false
  - id: D3
    description: "uv.lock regenerated minimal-diff (marker-branch collapse + chardet drop only, no unrelated version bumps)"
    requirement: "PYVER-01"
    verification:
      - kind: other
        ref: "uv lock stdout (all lines 'Updated X vOLD, vNEW -> vNEW' + one 'Removed chardet v5.2.0'); git diff --stat uv.lock (54 insertions, 1102 deletions, zero '+version = ' lines)"
        status: pass
    human_judgment: false
  - id: D4
    description: "tox.ini env_list updated to py310-py313 dotless, in lockstep with the CI matrix"
    requirement: "PYVER-04"
    verification:
      - kind: unit
        ref: "grep env_list tox.ini -- env_list = py310, py311, py312, py313, lint, type, cov, docs"
        status: pass
    human_judgment: false
  - id: D5
    description: "ci.yml/docs.yml/release.yml single-version interpreter pins reconciled to 3.10; ci.yml matrix + include: mapping cover 3.10-3.13"
    requirement: "PYVER-02"
    verification:
      - kind: unit
        ref: "grep -n python-version:/tox-env:/uv python install across ci.yml, docs.yml, release.yml"
        status: pass
    human_judgment: false
  - id: D6
    description: "Quick local test pre-check stays green under the new floor"
    verification:
      - kind: unit
        ref: "uv run pytest tests/ -q -m \"not integration and not slow\" -- 402 passed"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-07-04
status: complete
---

# Phase 3 Plan 1: Modernize Python Floor to 3.10-3.13 Summary

**Every Python-floor config surface (pyproject.toml metadata + tool target-versions, regenerated uv.lock, tox.ini env_list, ci.yml/docs.yml/release.yml interpreter pins) moved uniformly from the old 3.9-3.12 range to 3.10-3.13, landed as three per-surface commits with zero unrelated dependency drift.**

## Performance

- **Duration:** 6 min (commits span 19:51:46 -> 19:52:31 JST)
- **Started:** 2026-07-04T10:49:41Z (approx, per STATE.md session start)
- **Completed:** 2026-07-04T10:52:59Z
- **Tasks:** 3 (all type="auto")
- **Files modified:** 6 (pyproject.toml, uv.lock, tox.ini, ci.yml, docs.yml, release.yml)

## Accomplishments
- `pyproject.toml` now declares `requires-python = ">=3.10"`, drops the 3.9 classifier, adds the 3.13 classifier, and aligns `[tool.black]`/`[tool.ruff]`/`[tool.mypy]` target-versions to the 3.10-3.13 floor.
- `uv.lock` regenerated with plain `uv lock` (no `--upgrade`); confirmed the diff is exactly the predicted marker-branch collapse plus the incidental `chardet` drop — no genuinely different resolved version for any package.
- `tox.ini` `env_list` now reads `py310, py311, py312, py313, lint, type, cov, docs`, matching the CI matrix 1:1 with dotless env names (avoiding the Phase 2 TEST-01 dotted/dotless hazard).
- `ci.yml`'s test matrix and `include:` mapping cover 3.10-3.13 with a clean dotless mapping; all five hardcoded single-version jobs (lint, type-check, coverage, build, integration) plus `docs.yml`'s `setup-python` step plus both `release.yml` installs now standardize on the 3.10 floor.
- Quick local pre-checks pass under the new configuration: `uv run pytest tests/ -q -m "not integration and not slow"` → 402 passed; `uv run black --check .` → 50 files unchanged both before and after the target-version bump.

## Task Commits

Each task was committed atomically:

1. **Task 1: Bump pyproject.toml Python floor + classifiers + tool target-versions and regenerate uv.lock** - `fce2ffb` (feat)
2. **Task 2: Update tox.ini env_list to py310-py313 in lockstep with the CI matrix** - `06dbb64` (feat)
3. **Task 3: Reconcile ci.yml/docs.yml/release.yml to the 3.10 floor and the 3.10-3.13 matrix** - `2e285d4` (feat)

_Note: no separate reformat commit was needed — `black --check .` was a no-op both before and after the target-version bump (D-03 confirmed not to trigger)._

## Files Created/Modified
- `pyproject.toml` - requires-python floor, classifiers, black/ruff/mypy target-versions
- `uv.lock` - regenerated (plain `uv lock`); `<3.10` marker branches collapsed, `chardet` dropped
- `tox.ini` - `env_list` updated to py310-py313 dotless
- `.github/workflows/ci.yml` - test matrix + include: mapping to 3.10-3.13/py310-py313; five hardcoded installs 3.11 -> 3.10
- `.github/workflows/docs.yml` - `setup-python` `python-version` 3.11 -> 3.10
- `.github/workflows/release.yml` - both `uv python install` lines 3.11 -> 3.10

## Decisions Made
- Ran plain `uv lock` (never `--upgrade`) per the plan's hard gate on Task 1; inspected `git diff uv.lock` before committing and confirmed it matches the predicted shape exactly (marker-branch collapse + `chardet` drop, `git diff --stat` = 54 insertions / 1102 deletions, zero `+version = ` diff lines for any package) — no deviation to report.
- Confirmed D-03 ("black reformat as a direct consequence of the target-version bump") does not trigger here: `black --check .` reports the identical "50 files would be left unchanged" result both before and after the bump, so no fourth commit was added.

## Deviations from Plan

None - plan executed exactly as written. The uv.lock hard gate was checked and passed cleanly (no genuine version bumps found); no Rule 1-4 deviations were needed.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All six config surfaces now uniformly declare the 3.10-3.13 Python floor, committed as three clean per-surface commits ready for Plan 02's push -> observe gate.
- Local cheap pre-checks (`pytest -q -m "not integration and not slow"`, `black --check .`) are green; the authoritative full 3-OS x 4-Python-version CI matrix (including `docs.yml`) has not yet been observed on GitHub Actions — that is Plan 02's job, per carried-forward Phase 2 D-01 (push -> observe is the definition of done).
- No blockers. `release.yml` changes (both `uv python install 3.11 -> 3.10` lines) only exercise on a real tag push and were verified by reading the diff, per the plan's Manual-Only Verification note in 03-VALIDATION.md.

---
*Phase: 03-modernize-python-floor-3-10-3-13*
*Completed: 2026-07-04*

## Self-Check: PASSED

All six modified files (pyproject.toml, uv.lock, tox.ini, .github/workflows/ci.yml, .github/workflows/docs.yml, .github/workflows/release.yml) confirmed present on disk. All three task commits (fce2ffb, 06dbb64, 2e285d4) confirmed present in git log.
