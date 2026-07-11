# Requirements: typsphinx v0.5.0 — forward-ecosystem

**Defined:** 2026-07-09
**Core Value:** The `typst`/`typstpdf` builders produce correct output and every CI job stays green on the current ecosystem — Sphinx 9 and typst 0.15+ — with the runtime pins raised forward and the bundled `@preview` packages compiling cleanly (no `kai`-class breaks).

**Locked scope decisions (from milestone questioning + research):**

- **Latest-only** — raise pins forward; no Sphinx-8/typst-0.14 compatibility range.
- **Python floor → ≥3.12** — track latest Sphinx (`sphinx>=9.1`); drop 3.10 and 3.11 from the matrix.
- **Bundled `@preview` version bump only** — FWD-03 (user-configurable `@preview` versions) stays out of scope.
- **docs-PDF CI stays ubuntu-only** — cross-OS PDF verification deferred.

## v1 Requirements

Requirements for the v0.5.0 release. Each maps to a roadmap phase (Traceability below).

### Forward Ecosystem (FWD)

- [x] **FWD-01**: `sphinx` is re-pinned to `>=9.1,<10` (the `<9` ceiling dropped) and the extension builds/imports and registers both builders correctly under Sphinx 9.1
- [x] **FWD-02**: `typst` is re-pinned to `>=0.15.0,<0.16` (the `<0.15` ceiling dropped) and the `typstpdf` builder compiles the project docs to PDF under typst 0.15 with no `kai`-class error

### Dependency Graph (PIN)

- [x] **PIN-01**: `docutils` is re-pinned to `>=0.21,<0.23` (Sphinx-9.1-compatible; avoids the unresolvable 0.23)
- [x] **PIN-02**: The supported Python range is raised to 3.12–3.13 (3.10 and 3.11 dropped) across `pyproject.toml` `requires-python` + classifiers, `tox.ini` `env_list`, the CI/docs/release workflow matrices, and the black/ruff/mypy target-versions
- [x] **PIN-03**: `uv.lock` is regenerated to match the raised pins and `uv sync --locked` stays green at all lockfile-currency gate sites

### @preview Packages (PKG)

- [x] **PKG-01**: `mitex` is bumped `0.2.4`→`0.2.7`, empirically resolving the `unknown variable: kai` compile error under typst 0.15 (confirmed by a real `docs-pdf` compile, not changelog alone)
- [x] **PKG-02**: `gentle-clues` (`1.2.0`→`1.3.1`) and `codly-languages` (`0.1.1`→`0.1.10`) are bumped, and `codly` `1.3.0` is confirmed to compile under typst 0.15 (no newer version exists as a fallback — a source-level workaround is the contingency if it breaks)
- [x] **PKG-03**: The 3-way `@preview` version-sync (`writer.py` / `template_engine.py` / `templates/base.typ`) is updated in lockstep and `tests/test_preview_version_sync.py` passes

### API Compatibility (API)

- [x] **API-01**: The deprecated `doctree.traverse()` call at `template_engine.py:239` is replaced with `doctree.findall()` (consistent with `builder.py`)
- [x] **API-02**: The translator / writer / builder / config registration are confirmed compatible with Sphinx 9.1 + docutils 0.22 (any deprecation-removal breakage fixed), and the full pytest suite passes

### CI & Release (CI / REL)

- [ ] **CI-01**: Every CI job is green — lint, the 3-OS × Python 3.12–3.13 test matrix, type-check, coverage, build, and `docs.yml` (docs-PDF ubuntu-only) — confirmed by an observed Actions run
- [x] **CI-02**: A `typst compile` smoke test is added that would catch a `kai`-class `@preview` break before release (closes the gap that the internal-only sync test misses)
- [ ] **CI-03**: The durability guardrails are updated to the new majors — `drift.yml` ceilings and the `sphinx-typst-stack` Dependabot group reflect `sphinx<10` / `typst<0.16` / `docutils<0.23`
- [ ] **REL-01**: `typsphinx/__init__.py` `__version__` is corrected (`0.4.3`→`0.5.0`) in sync with `pyproject.toml`, and v0.5.0 is released to PyPI (wheel + sdist) + GitHub Release with the release workflow green

## v2 Requirements

Deferred to a future release. Tracked but not in this roadmap.

### Configurability (CFG)

- **CFG-01** (was FWD-03): User-configurable `@preview` package versions (`typst_package_imports` / a dedicated config) so the compiler and package versions can be chosen per project

### Cross-OS Verification (XOS)

- **XOS-01**: `docs-pdf` CI coverage extended to macOS and Windows to catch typst 0.15 font/text-shaping regressions

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Sphinx 8 / typst 0.14 compatibility range | v0.5.0 is latest-only; supporting old and new majors simultaneously (version-conditional branching) is out of scope |
| User-configurable `@preview` versions (FWD-03) | Deferred to CFG-01; v0.5.0 bumps bundled versions in-place |
| Cross-OS docs-PDF CI | Deferred to XOS-01; ubuntu-only verification retained |
| Making `drift.yml` a required check | Posture stays advisory-only; revisit separately |
| New translation features / new reST constructs | This is a forward-port milestone, not a feature cycle |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FWD-01 | Phase 6 | Complete |
| FWD-02 | Phase 7 | Complete |
| PIN-01 | Phase 6 | Complete |
| PIN-02 | Phase 6 | Complete |
| PIN-03 | Phase 6 | Complete |
| PKG-01 | Phase 7 | Complete |
| PKG-02 | Phase 7 | Complete |
| PKG-03 | Phase 7 | Complete |
| API-01 | Phase 8 | Complete |
| API-02 | Phase 8 | Complete |
| CI-01 | Phase 9 | Pending |
| CI-02 | Phase 9 | Complete |
| CI-03 | Phase 9 | Pending |
| REL-01 | Phase 10 | Pending |

**Coverage:**

- v1 requirements: 14 total
- Mapped to phases: 14 ✓
- Unmapped: 0 ✓

**Phase distribution:**

- Phase 6 (Raise Runtime Pins + Python Floor): FWD-01, PIN-01, PIN-02, PIN-03
- Phase 7 (Bump @preview Packages + typst 0.15): FWD-02, PKG-01, PKG-02, PKG-03
- Phase 8 (API & Test Compatibility): API-01, API-02
- Phase 9 (Green CI Matrix + Smoke Test + Guardrails): CI-01, CI-02, CI-03
- Phase 10 (Version-String Fix + v0.5.0 Release): REL-01

---
*Requirements defined: 2026-07-09*
*Last updated: 2026-07-09 after roadmap creation — traceability mapped (14/14, phases 6–10)*
