# Roadmap: typsphinx (CI-repair + modernize milestone)

## Overview

typsphinx's CI went red because loose, unbounded dependency constraints let a fresh
resolution jump to `sphinx==9.0.4`, `docutils==0.22.4`, and `typst==0.15.0` — the last of
which breaks PDF compilation because the hardcoded `@preview/mitex:0.2.4` package uses a
`kai` symbol that typst 0.15 turned into a hard error. This milestone pins the runtime
dependency graph back to a known-good, mutually-compatible combination (not a forward port
to sphinx 9 / typst 0.15), confirms every CI job goes green as a result, then opportunistically
modernizes the supported Python range (3.10–3.13) and dev tooling, and closes with durability
guardrails so this exact class of silent drift cannot recur unnoticed. The five phases are
sequential and each ends with a strictly greener-than-before CI state: the pin fix must land
alone first so a red/green result is unambiguous, Python-floor and tooling changes ride on top
of a confirmed-green baseline, and the guardrails close the loop last.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Pin Runtime Dependencies to Known-Good** - Pin typst/sphinx/docutils to a reproducible, mutually-compatible combination and make the tree lint-clean (completed 2026-07-04)
- [ ] **Phase 2: Verify the Green Baseline** - Confirm the pin turns every CI job green and guard the 3-way `@preview` version sync against future desync
- [ ] **Phase 3: Modernize Python Floor (3.10-3.13)** - Bump the supported Python range across every config surface as one atomic, CI-verified batch
- [ ] **Phase 4: Refresh Dev Tooling** - Conservatively bump dev-tooling floors and verify GitHub Actions versions
- [ ] **Phase 5: Durability Guardrails** - Enforce lockfile currency and add drift detection so the rot cannot silently recur

## Phase Details

### Phase 1: Pin Runtime Dependencies to Known-Good

**Goal**: Runtime dependency versions are pinned to a reproducible, empirically-confirmed, mutually-compatible combination, and the codebase is lint-clean. This is the actual bug fix, landing alone so a red/green result is unambiguous.
**Depends on**: Nothing (first phase)
**Requirements**: PIN-01, PIN-02, PIN-03, PIN-04, PIN-05, PIN-06, LINT-01, LINT-02
**Success Criteria** (what must be TRUE):

  1. Every runtime dependency (`typst`, `sphinx`, `docutils`) has an explicit upper bound in `pyproject.toml` — `typst>=0.14.1,<0.15` empirically confirmed to compile the `docs-pdf` target cleanly, `sphinx<9`, `docutils<0.22` — none left unbounded.
  2. `uv.lock` is regenerated and committed to match the new pins, resolving cleanly across all supported Python-version markers.
  3. `tox.ini`'s `[testenv]` and `[testenv:type]` dependency lists mirror the same ceilings as `pyproject.toml` (no independent, unbounded re-resolution path in the `type` env).
  4. The dead `sphinx-testing` dependency is removed from `pyproject.toml`/`uv.lock`.
  5. `black --check .` and `ruff check .` both exit 0 on the full tree, and the confirmed-good typst patch (plus any rejected candidates) is recorded in `PROJECT.md`'s Key Decisions table.

**Plans**: 2/2 plans complete

- [x] 01-01-PLAN.md — Pin runtime deps (typst/sphinx/docutils upper bounds), mirror tox ceilings, remove sphinx-testing, regenerate uv.lock, confirm docs-pdf + record typst patch/ceiling finding in PROJECT.md (PIN-01..06)
- [x] 01-02-PLAN.md — Lint-clean the tree: black reformat (separate commit per D-04) + ruff clean (LINT-01/02)

### Phase 2: Verify the Green Baseline

**Goal**: The Phase 1 pin is confirmed to turn every previously-red CI job green across the full platform/Python matrix, and the 3-way `@preview` version sync hazard is protected by an automated test rather than manual memory.
**Depends on**: Phase 1
**Requirements**: TEST-01, TEST-02, TEST-03, TEST-04, DOCS-01
**Success Criteria** (what must be TRUE):

  1. All 12 test-matrix jobs (3 OS x 4 Python versions) pass to completion — not just the ubuntu-only jobs.
  2. The 7 PDF-compilation integration tests pass (`test_integration_advanced.py::TestPDFGenerationIntegration`, `test_integration_nested_toctree.py::TestE2ETypstCompilation`).
  3. The coverage job passes and uploads to Codecov; Type Check and Build Package jobs remain green with no regression.
  4. `sphinx-build -b typstpdf` produces a PDF and `docs.yml` completes end-to-end, including the multi-language PDF-copy step that previously errored on a missing PDF.
  5. A new automated test asserts the `@preview` package versions declared in `writer.py`, `template_engine.py`, and `templates/base.typ` are identical, so a future desync fails CI loudly instead of silently.

**Plans**: 2 plans
**Wave 1**

- [ ] 02-01-PLAN.md — Add the `@preview` version-sync guard test (D-03) and run the cheap local pre-check on the pinned tree (D-01)

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 02-02-PLAN.md — Push a work branch + PR targeting main and observe ci.yml (12 matrix jobs + lint/type/coverage/build/integration) and docs.yml (end-to-end incl. PDF-copy) green (D-01/D-02)

### Phase 3: Modernize Python Floor (3.10-3.13)

**Goal**: The supported Python range is uniformly modernized to 3.10-3.13 across every config surface, landing as one atomic batch on top of a confirmed-green baseline so any new failure is attributable to the Python bump alone.
**Depends on**: Phase 2
**Requirements**: PYVER-01, PYVER-02, PYVER-03, PYVER-04
**Success Criteria** (what must be TRUE):

  1. `requires-python>=3.10` and PyPI classifiers (3.9 dropped, 3.13 added) are set in `pyproject.toml`.
  2. `ci.yml`'s test matrix covers Python 3.10-3.13, and every hardcoded `uv python install` line across `ci.yml`/`docs.yml`/`release.yml` is reconciled with the new floor.
  3. `[tool.black]`, `[tool.ruff]`, and `[tool.mypy]` target-versions all align to the 3.10 floor.
  4. `tox.ini`'s `env_list` is updated to `py310, py311, py312, py313` in lockstep with the CI matrix (no tox env without a CI caller, and vice versa).
  5. The full CI matrix is green again on 3.10-3.13, confirming no reformatting regression or 3.13 wheel-availability gap in dev/docs dependencies.

**Plans**: TBD

### Phase 4: Refresh Dev Tooling

**Goal**: Dev-tooling floors and CI action versions are refreshed conservatively, without introducing risky default-behavior flips unrelated to the CI-repair goal.
**Depends on**: Phase 3
**Requirements**: TOOL-01, TOOL-02
**Success Criteria** (what must be TRUE):

  1. Black/ruff/tox dev-tooling floors are bumped conservatively; the project deliberately stays on `pytest~=8.4` and `mypy>=1.13,<2.0` this cycle rather than jumping to a new major.
  2. GitHub Actions versions (`actions/checkout`, `actions/setup-python`, `codecov/codecov-action`) are verified/refreshed for hosted-runner compatibility.
  3. CI remains green after the tooling refresh, with no regression introduced by any version bump.

**Plans**: TBD

### Phase 5: Durability Guardrails

**Goal**: CI enforces lockfile currency and proactively surfaces future dependency drift, so the silent multi-year rot this milestone fixes cannot recur unnoticed.
**Depends on**: Phase 4
**Requirements**: DUR-01, DUR-02, DUR-03, DUR-04
**Success Criteria** (what must be TRUE):

  1. CI uses `uv sync --locked` (or an equivalent `uv lock --check` gate), so a stale or silently-rewritten lockfile fails the build loudly instead of drifting.
  2. A weekly, non-blocking scheduled CI job resolves latest dependencies and reports drift early without blocking merges.
  3. `dependabot.yml` groups the `sphinx`/`docutils`/`typst` cluster so a lone dependency bump can't reintroduce the `kai`-class break.
  4. A CI status badge is visible on `README.md`, reflecting the now-green, guarded pipeline.

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Pin Runtime Dependencies to Known-Good | 2/2 | Complete    | 2026-07-04 |
| 2. Verify the Green Baseline | 0/2 | Not started | - |
| 3. Modernize Python Floor (3.10-3.13) | 0/TBD | Not started | - |
| 4. Refresh Dev Tooling | 0/TBD | Not started | - |
| 5. Durability Guardrails | 0/TBD | Not started | - |

---
*Roadmap created: 2026-07-04*
*Granularity: standard (5 phases, dependency-ordered, matching research's converged phase structure)*
