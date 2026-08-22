---
phase: 54-one-bundle-rule-template-key-per-document-selection-four-del
plan: 02
subsystem: infra
tags: [packaging, ci, setuptools, wheel, pyproject-toml, github-actions]

# Dependency graph
requires: []
provides:
  - "typsphinx/templates/README.md — the bundled \"typst\" key's non-.typ canary file, BLD-05's subject"
  - "Recursive templates/**/* package-data glob in pyproject.toml (was templates/*.typ)"
  - "CI build-job step 'Verify wheel carries the template bundle' that opens the real wheel and fails by name on regression"
affects: [55-v0.8.0-derived-defects, 56-per-document-template-documentation]

# Actuals (#2632)
actuals:
  tokens: 1000
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Wheel-content assertion via zipfile.ZipFile(...).namelist() run against a real uv build artifact in CI, never inferred from the package-data glob text"

key-files:
  created:
    - typsphinx/templates/README.md
  modified:
    - pyproject.toml
    - .github/workflows/ci.yml

key-decisions:
  - "README.md content follows D-11's required-literals list verbatim (_template/typst/, typst_document_templates, base.typ) and links to published docs by name rather than restating the parameter contract"
  - "CI step placed immediately after the existing 'Build package' step and before 'Check package', per D-13 — no new job, no pytest-shells-out-to-build-tool"

patterns-established:
  - "Recursive package-data glob (templates/**/*) is the standing shape for this package's bundled non-Python assets; a future asset kind needs no second edit"

requirements-completed: [BLD-05]

coverage:
  - id: D1
    description: "typsphinx/templates/ has a non-.typ file (README.md), giving BLD-05's assertion a real subject"
    requirement: BLD-05
    verification:
      - kind: unit
        ref: "manual acceptance check: grep -n '_template/typst/' / 'typst_document_templates' / 'base.typ' typsphinx/templates/README.md, all three literals present"
        status: pass
    human_judgment: false
  - id: D2
    description: "pyproject.toml's [tool.setuptools.package-data] glob widened from templates/*.typ to templates/**/*, and a locally built wheel demonstrably contains typsphinx/templates/README.md"
    requirement: BLD-05
    verification:
      - kind: integration
        ref: "uv build then zipfile.ZipFile(dist/*.whl).namelist() contains 'typsphinx/templates/README.md' (exit 0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "A new CI build-job step opens the built wheel and fails the job by name if the bundle's non-.typ file is missing, positioned immediately after 'Build package' and before 'Check package'"
    requirement: BLD-05
    verification:
      - kind: unit
        ref: "yaml.safe_load(.github/workflows/ci.yml) — build job step index check: 'Verify wheel carries the template bundle' index == 'uv build' step index + 1 (exit 0)"
        status: pass
      - kind: integration
        ref: "the step's exact run body executed locally via uv run python -c '...' against the real dist/*.whl — printed OK and exited 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full test suite and existing packaging test stay green after both changes"
    verification:
      - kind: unit
        ref: "uv run pytest tests/ -q -> 1270 passed, 5 skipped"
        status: pass
      - kind: unit
        ref: "uv run pytest tests/test_readthedocs_config.py -q -> 6 passed"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-08-16
status: complete
---

# Phase 54 Plan 02: One-Bundle-Rule Packaging Canary Summary

**Added `typsphinx/templates/README.md` as the bundled `"typst"` key's non-`.typ` canary, widened `pyproject.toml`'s package-data glob to `templates/**/*`, and added a CI `build`-job step that opens the real wheel and fails by name if the canary is missing.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-08-16T00:00Z (approx.)
- **Completed:** 2026-08-16T00:09Z
- **Tasks:** 2
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments
- `typsphinx/templates/` now contains a real non-`.typ` file, giving BLD-05's "the bundle carries a non-`.typ` file" assertion an actual subject — before this plan the directory held only `base.typ`.
- `pyproject.toml`'s `[tool.setuptools.package-data]` glob for the `"typsphinx"` key is `templates/**/*` (recursive), replacing the `.typ`-only `templates/*.typ`, so a future non-`.typ` bundle file (e.g. `templates/fonts/x.otf`) reaches the wheel with no second edit.
- CI's existing `build` job gained one new step, `Verify wheel carries the template bundle`, that opens the wheel `uv build` just produced with `zipfile.ZipFile(...).namelist()` and fails the job by name — citing both the missing path and `pyproject.toml`'s `[tool.setuptools.package-data]` — if the canary is absent. No new job, no rebuild per matrix cell, `twine check` untouched.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the bundle's non-`.typ` canary and widen the package-data glob** - `89334ecb` (feat)
2. **Task 2: Add the wheel-content assertion step to the CI `build` job** - `d2f0acce` (feat)

**Plan metadata:** committed separately per worktree-mode convention (SUMMARY.md only, orchestrator merges STATE.md/ROADMAP.md updates centrally).

## Files Created/Modified
- `typsphinx/templates/README.md` - the bundle's non-`.typ` canary; documents what the directory is, that it's copied wholesale to `<outdir>/_template/typst/`, how `base.typ` is overridden, how a user registers their own bundle via `typst_document_templates`, and that this file is also the wheel-content canary
- `pyproject.toml` - `[tool.setuptools.package-data]`'s `"typsphinx"` value widened from `["templates/*.typ"]` to `["templates/**/*"]`, with a comment recording the recursion as load-bearing
- `.github/workflows/ci.yml` - new `Verify wheel carries the template bundle` step in the `build` job, inserted between `Build package` (`uv build`) and `Check package` (`twine check`)

## Decisions Made
- README wording matches D-11's required-literals list exactly (`_template/typst/`, `typst_document_templates`, `base.typ`) and cites the published "Templates" documentation by name instead of restating the custom-template parameter contract, keeping the file short (35 lines) per the plan's guidance.
- The CI step's Python one-liner runs via `uv run python -c "..."` (matching the surrounding steps' `uv run` idiom, e.g. `uv run twine check`) rather than a bare `python -c`, since no prior step in this job guarantees a bare `python` on `PATH` at that point (`uv python install 3.12` installs an interpreter uv manages, not necessarily `PATH`-visible as `python`).
- Kept the glob-widening comment's wording ("the actual wheel built by the previous step") free of the literal substring `uv build` to avoid ambiguity with the acceptance criterion "exactly one `uv build` invocation" (that substring now appears exactly once, on the real `run: uv build` line).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- `uv run ruff check .` failed to execute in this worktree with `Could not start dynamically linked executable: ruff` — a pre-existing NixOS sandbox limitation on the generic-linux ruff binary, unrelated to this plan's changes (confirmed via project memory: this is a known standing environment issue, not a code defect; the project's own CI runs ruff successfully on `ubuntu-latest`). `black --check .` (310 files unchanged) and `mypy typsphinx/` (0 issues) both ran clean, and the full `pytest` suite passed (1270 passed, 5 skipped, 0 failed), so ruff's local unavailability does not indicate a regression.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- BLD-05 is fully satisfied and this plan's artifacts are self-contained: the wheel-content check is real (built and inspected locally, matching exactly what the new CI step runs), not inferred from the glob text.
- No coupling to the other Phase 54 plans' bundle-copy mechanics (D-01–D-05), `_template/` prefix reservation, or CONF-19 detection — this plan only touches packaging metadata, the bundled `"typst"` key's own directory contents, and CI. Safe to land independently of wave ordering within this phase.
- Per this plan's `<artifacts_this_phase_produces>` note: 54-01 (also wave 1) is explicitly forbidden from asserting an exact manifest over `typsphinx/templates/`, since this plan added a file to it.

## Self-Check: PASSED

- FOUND: typsphinx/templates/README.md
- FOUND: .planning/phases/54-one-bundle-rule-template-key-per-document-selection-four-del/54-02-SUMMARY.md
- FOUND commit: 89334ecb
- FOUND commit: d2f0acce

---
*Phase: 54-one-bundle-rule-template-key-per-document-selection-four-del*
*Completed: 2026-08-16*
