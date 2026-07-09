---
phase: 06-raise-runtime-pins-python-floor
plan: 01
subsystem: infra
tags: [sphinx, docutils, uv, python-floor, pyproject, ci, tox, dependency-pins]

# Dependency graph
requires: []
provides:
  - "pyproject.toml re-pinned to sphinx>=9.1,<10, docutils>=0.21,<0.23, requires-python >=3.12"
  - "uv.lock regenerated resolving sphinx==9.1.0, docutils==0.22.4, requires-python header >=3.12"
  - "tox.ini + all four GitHub Actions workflows (ci/docs/release/drift) mirror the 3.12-3.13 floor"
  - "Both typst and typstpdf Sphinx builders confirmed registering under Sphinx 9.1"
  - "release/v0.5.0 integration branch carries the full, atomic pin-raise (2 local commits, not pushed)"
affects: [07-typst-preview-package-bump, 08-sphinx9-compat-sweep, 09-milestone-completion]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Atomic two-commit landing for cross-file pin raises: pyproject+lockfile in one commit, tox+CI workflows in a second immediately-following commit (mirrors precedent fce2ffb/2e285d4)"

key-files:
  created: []
  modified:
    - pyproject.toml
    - uv.lock
    - tox.ini
    - .github/workflows/ci.yml
    - .github/workflows/docs.yml
    - .github/workflows/release.yml
    - .github/workflows/drift.yml

key-decisions:
  - "Dropped the dead docs-extra tomli conditional (python_version < '3.11') since it is permanently false at the new 3.12 floor and stdlib tomllib always resolves — keeps the PIN-02 grep audit clean of a spurious 3.11 hit (plan-specified, not a deviation)."
  - "Non-matrix CI jobs (lint/type-check/coverage/build/integration in ci.yml, validate/build in release.yml, drift-check in drift.yml) move to the new floor 3.12, not 3.13, per CONTEXT.md discretion default."
  - "Used the minimal-diff targeted lockfile upgrade (uv lock --upgrade-package sphinx --upgrade-package docutils) rather than a full re-resolve; uv sync --locked succeeded on the first attempt so the Pitfall-4 full-relock fallback was not needed."

patterns-established:
  - "Split-brain ceiling sync: docutils/types-docutils/sphinx duplicated across pyproject.toml and tox.ini [testenv:type] with no automated test — must be edited in lockstep by hand each time (documented hazard, no fix landed this phase)."

requirements-completed: [FWD-01, PIN-01, PIN-02, PIN-03]

coverage:
  - id: D1
    description: "pyproject.toml re-pinned: sphinx>=9.1,<10, docutils>=0.21,<0.23, requires-python >=3.12, classifiers/black/ruff/mypy target-versions raised to 3.12-3.13, dead tomli conditional removed, typst pin left untouched"
    requirement: "PIN-01"
    verification:
      - kind: other
        ref: "Read pyproject.toml post-edit; grep audits (old ceilings/py310/py311, bare 3.10/3.11) zero hits"
        status: pass
    human_judgment: false
  - id: D2
    description: "uv.lock regenerated resolving sphinx==9.1.0, docutils==0.22.4; requires-python header auto-updated to >=3.12; uv sync --locked exits 0"
    requirement: "PIN-03"
    verification:
      - kind: other
        ref: "uv sync --locked (exit 0); grep -A2 'name = \"sphinx\"'/'name = \"docutils\"' uv.lock"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both typst and typstpdf builders register under Sphinx 9.1; import typsphinx clean; sphinx-build -b typst tests/roots/test-basic succeeds producing index.typ + _template.typ"
    requirement: "FWD-01"
    verification:
      - kind: integration
        ref: "uv run python -c registration-smoke script (typst: OK / typstpdf: OK); uv run sphinx-build -b typst tests/roots/test-basic /tmp/typst-smoke-out (build succeeded, SMOKE_OK)"
        status: pass
    human_judgment: false
  - id: D4
    description: "tox.ini env_list + [testenv]/[testenv:type] and all four GitHub Actions workflows (ci/docs/release/drift) mirror the 3.12-3.13 floor and Sphinx-9.1/docutils-0.22 ceilings; repo-wide grep audit for old pins/floors returns zero hits"
    requirement: "PIN-02"
    verification:
      - kind: other
        ref: "grep -rn old-ceiling/py310/py311 pattern and bare-3.10/3.11 pattern across *.toml/*.ini/*.yml/*.yaml (both zero hits)"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-07-09
status: complete
---

# Phase 6 Plan 1: Raise Runtime Pins + Python Floor Summary

**Re-pinned typsphinx to sphinx>=9.1,<10 / docutils>=0.21,<0.23 / Python 3.12-3.13 across all 21 declaration sites (pyproject.toml, regenerated uv.lock, tox.ini, and four GitHub Actions workflows), landed as two atomic local commits on `release/v0.5.0`, with both builders confirmed registering and a live `-b typst` build passing under Sphinx 9.1.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-07-09
- **Tasks:** 2
- **Files modified:** 7 (pyproject.toml, uv.lock, tox.ini, ci.yml, docs.yml, release.yml, drift.yml)

## Accomplishments

- Raised `pyproject.toml` to `requires-python >=3.12`, `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `types-docutils>=0.21`, dropped 3.10/3.11 classifiers, raised black/ruff/mypy target-versions to 3.12/3.13, and removed the now-dead `tomli` conditional dependency.
- Regenerated `uv.lock` via `uv lock --upgrade-package sphinx --upgrade-package docutils`, resolving `sphinx==9.1.0` and `docutils==0.22.4`; the lockfile header's `requires-python` auto-updated to `>=3.12`. `uv sync --locked` exits 0.
- Confirmed both the `typst` and `typstpdf` builders register cleanly under Sphinx 9.1, and `import typsphinx` succeeds without a traceback.
- Ran a live `sphinx-build -b typst tests/roots/test-basic` smoke build under the new stack: printed `build succeeded.`, produced both `index.typ` and `_template.typ`.
- Mirrored the 3.12 floor into `tox.ini` (`env_list`, `[testenv]`, `[testenv:type]`) and all four GitHub Actions workflows (`ci.yml` matrix + `include:` mapping + five single-runner installs, `docs.yml`, `release.yml` x2, `drift.yml`), without touching the matrix-driven install line in `ci.yml` or adding any CI-hiding config.
- Ran both repo-wide grep audits (old sphinx/docutils ceilings + `py310`/`py311`, and bare `3.10`/`3.11` python-version literals) across `*.toml`/`*.ini`/`*.yml`/`*.yaml` — zero hits in both.
- Verified the `typst>=0.14.1,<0.15` pin is untouched and no `@preview` version-sync file was touched (Phase 7 scope fence honored).

## Task Commits

Each task was committed atomically:

1. **Task 1: Raise pyproject.toml pins + Python floor and regenerate uv.lock** - `1743aef` (feat)
2. **Task 2: Mirror the 3.12 floor into tox.ini + all four CI workflows, audit, and confirm atomicity** - `058a850` (feat)

_No TDD tasks in this plan (pure declaration-surface change, no test files touched)._

## Files Created/Modified

- `pyproject.toml` - requires-python, classifiers, sphinx/docutils pins, types-docutils floor, dropped dead tomli line, black/ruff/mypy target-versions
- `uv.lock` - regenerated (sphinx 9.1.0, docutils 0.22.4, requires-python header >=3.12; several 3.10/3.11-only transitive packages dropped: tomli, exceptiongroup, zipp, importlib-metadata, backports-tarfile; roman-numerals added as a new sphinx 9.1 transitive dep)
- `tox.ini` - env_list, [testenv] sphinx pin, [testenv:type] sphinx/types-docutils/docutils pins
- `.github/workflows/ci.yml` - matrix, include: mapping, five single-runner uv python install lines
- `.github/workflows/docs.yml` - setup-python python-version
- `.github/workflows/release.yml` - two single-runner uv python install lines
- `.github/workflows/drift.yml` - single-runner uv python install line

## Decisions Made

- Followed the plan's explicit instruction to drop the dead `docs` extra `tomli>=2.0; python_version < '3.11'` line (permanently-false marker at the new 3.12 floor; stdlib `tomllib` always resolves) — this was a plan-specified edit, not an ad-hoc deviation.
- Non-matrix CI jobs move to Python 3.12 (not 3.13), matching CONTEXT.md's stated discretion default.
- Used the targeted minimal-diff lockfile upgrade command exactly as specified; the Pitfall-4 full-relock fallback was not needed since `uv sync --locked` passed on the first attempt.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' `<verify>` automated blocks and `<acceptance_criteria>` were run and confirmed before each commit.

## Issues Encountered

None. The `uv sync --locked` run (part of Task 1's verify block) uninstalled several previously-installed `dev`/`docs` extras packages (black, mypy, pytest, tox, furo, etc.) because the bare command without `--extra dev` only syncs the base dependency group — this is expected `uv` behavior (matches CI's own pattern of `uv sync --extra dev --locked`), not a bug introduced by this phase, and did not affect any acceptance criterion (all of which were run via `uv run` against the base install).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`release/v0.5.0` now carries the real target ecosystem (Sphinx 9.1, docutils 0.22, Python 3.12-3.13) as two atomic local commits, not pushed. Phase 7 (typst re-pin + `@preview` package bump, the `kai` fix) and Phase 8 (Sphinx-9-compat sweep, `traverse()`->`findall()`, full pytest-suite work) can now diagnose against this real stack. The PDF / `docs-pdf` CI lanes are expected to stay red until Phase 7 lands the `mitex`/`codly` bump — this is intentional per D-03 and is not a Phase 6 regression. No blockers.

---
*Phase: 06-raise-runtime-pins-python-floor*
*Completed: 2026-07-09*

## Self-Check: PASSED

All 7 modified files confirmed present (pyproject.toml, uv.lock, tox.ini, ci.yml, docs.yml, release.yml, drift.yml). Both task commits (`1743aef`, `058a850`) confirmed present in git log.
