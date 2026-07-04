# Requirements: typsphinx (CI-repair + modernize milestone)

**Defined:** 2026-07-04
**Core Value:** Every CI job passes again on `main` — lint, the full test matrix, coverage, and the docs PDF build — with a dependency set that is pinned and reproducible so this rot doesn't silently recur.

## v1 Requirements

Requirements for this milestone. Each maps to roadmap phases.

### Dependency Pinning

<!-- The root-cause fix: pin to a known-good, mutually-compatible combination. -->

- [x] **PIN-01**: `typst` pinned to `>=0.14.1,<0.15` in `pyproject.toml`, resolving the `typst.TypstError: unknown variable: kai` break (mitex 0.2.4 uses `kai`, removed by typst 0.15)
- [x] **PIN-02**: `sphinx` upper-bounded `<9` and `docutils` upper-bounded `<0.22` in `pyproject.toml`
- [x] **PIN-03**: `uv.lock` regenerated to match the new pins and resolving cleanly across the per-Python-version markers (sphinx ≤8.1.3 on 3.10, up to 8.3.0 on 3.11–3.13)
- [x] **PIN-04**: `tox.ini` dependency lists mirror the `pyproject.toml` ceilings so no tox env (test/type) independently re-resolves an unbounded version
- [x] **PIN-05**: Dead dependency `sphinx-testing` (unused since 2019) removed
- [x] **PIN-06**: The exact typst 0.14.x patch is confirmed empirically green in CI; whether the sphinx/docutils ceilings are load-bearing vs precautionary is documented

### Lint & Format

- [x] **LINT-01**: `black --check .` exits 0 on the full tree (reformat `docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`)
- [x] **LINT-02**: `ruff` passes clean on the full tree

### Tests & Coverage

- [x] **TEST-01**: All matrix test jobs pass on ubuntu/macos/windows across the supported Python range <!-- RESOLVED (Phase 2 gap-closure): 12/12 matrix jobs green in ci.yml run 28702240846 after mapping matrix.python-version to dotless tox env names. -->
- [x] **TEST-02**: The 7 PDF-compilation integration tests pass (`test_integration_advanced.py::TestPDFGenerationIntegration`, `test_integration_nested_toctree.py::TestE2ETypstCompilation`)
- [x] **TEST-03**: Coverage job passes and uploads to Codecov
- [x] **TEST-04**: Type Check and Build Package jobs remain green (currently passing — must not regress)

### Docs Build

- [x] **DOCS-01**: `sphinx-build -b typstpdf` produces a PDF and `docs.yml` completes end-to-end, including the multi-language PDF-copy step that currently errors on a missing PDF

### Python Modernization

<!-- Scope: modernize the Python floor to 3.10–3.13. -->

- [ ] **PYVER-01**: `requires-python` set to `>=3.10`; PyPI classifiers updated (drop 3.9, add 3.13)
- [ ] **PYVER-02**: CI matrix updated to Python 3.10–3.13; hardcoded `uv python install 3.11` (and similar) lines across `ci.yml`/`docs.yml`/`release.yml` reconciled with the floor
- [ ] **PYVER-03**: `[tool.black] target-version`, `[tool.ruff] target-version`, and `[tool.mypy] python_version` aligned to the 3.10 floor (removes the "3.11 cannot parse code formatted for 3.12" class of failure)
- [ ] **PYVER-04**: `tox.ini` `env_list` updated to 3.10–3.13 in lockstep with the CI matrix

### Dev Tooling

- [ ] **TOOL-01**: Dev-tooling floors refreshed conservatively — bump black/ruff/tox; stay on `pytest~=8.4` and `mypy>=1.13,<2.0` this cycle to avoid risky default flips
- [ ] **TOOL-02**: GitHub Actions versions verified/refreshed (`actions/checkout`, `actions/setup-python`, `codecov/codecov-action`) against hosted-runner compatibility

### Durability Guardrails

<!-- Anti-recurrence: make future drift fail loudly instead of silently. -->

- [ ] **DUR-01**: CI uses `uv sync --locked` (or a `uv lock --check` gate) so a stale/rewritten lockfile fails the build instead of being silently regenerated
- [ ] **DUR-02**: A weekly non-blocking scheduled (`schedule:`) drift-detection CI job resolves latest deps and reports breakage early
- [ ] **DUR-03**: `dependabot.yml` groups the `sphinx`/`docutils`/`typst` bumps so a lone `typst` bump can't reintroduce the `kai` break
- [ ] **DUR-04**: CI status badge added to `README.md`

## v2 Requirements

Deferred to a future milestone. Tracked but not in this roadmap.

### Forward Ecosystem Support

- **FWD-01**: Support Sphinx 9 (adapt to any builder/translator API changes)
- **FWD-02**: Support typst 0.15+ (bump `@preview/mitex` to `>=0.2.6` and re-verify the other packages)
- **FWD-03**: Make the hardcoded `@preview` package versions configurable (`typst_package_versions`), eliminating the 3-way sync hazard

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Porting to Sphinx 9 / typst 0.15 / newest `@preview` | This milestone pins to known-good; forward-port is deferred to v2 (FWD-01/02) |
| Configurable `@preview` versions | Not needed for green; revisit only if it blocks pinning (tracked as FWD-03) |
| Incremental-build rebuild tracking (`get_outdated_docs`) | Orthogonal tech debt, not a CI-repair concern |
| Translator state-management refactor | Orthogonal tech debt |
| New translation features / new reST constructs | Maintenance cycle, not a feature cycle |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PIN-01 | Phase 1 | Complete |
| PIN-02 | Phase 1 | Complete |
| PIN-03 | Phase 1 | Complete |
| PIN-04 | Phase 1 | Complete |
| PIN-05 | Phase 1 | Complete |
| PIN-06 | Phase 1 | Complete |
| LINT-01 | Phase 1 | Complete |
| LINT-02 | Phase 1 | Complete |
| TEST-01 | Phase 2 | Complete |
| TEST-02 | Phase 2 | Complete |
| TEST-03 | Phase 2 | Complete |
| TEST-04 | Phase 2 | Complete |
| DOCS-01 | Phase 2 | Complete |
| PYVER-01 | Phase 3 | Pending |
| PYVER-02 | Phase 3 | Pending |
| PYVER-03 | Phase 3 | Pending |
| PYVER-04 | Phase 3 | Pending |
| TOOL-01 | Phase 4 | Pending |
| TOOL-02 | Phase 4 | Pending |
| DUR-01 | Phase 5 | Pending |
| DUR-02 | Phase 5 | Pending |
| DUR-03 | Phase 5 | Pending |
| DUR-04 | Phase 5 | Pending |

**Coverage:**

- v1 requirements: 23 total
- Mapped to phases: 23 (5 phases: Phase 1 = 8, Phase 2 = 5, Phase 3 = 4, Phase 4 = 2, Phase 5 = 4)
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-04*
*Last updated: 2026-07-04 after roadmap creation — full requirement coverage mapped across 5 dependency-ordered phases*
