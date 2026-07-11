# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- 🚧 **v0.5.0 — forward-ecosystem** — Phases 6–10 (in progress)

## Phases

**Phase Numbering:**

- Integer phases (6, 7, 8): Planned milestone work
- Decimal phases (7.1, 7.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

<details>
<summary>✅ v0.4.4 — CI-repair + modernize (Phases 1–5) — SHIPPED 2026-07-05</summary>

Restored a fully green CI pipeline on `main` by pinning the runtime dependency graph back to a
known-good, reproducible combination, then modernized the Python floor (3.10–3.13) and dev tooling
and installed durability guardrails so the drift cannot silently recur. Full phase detail, success
criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.4.4-ROADMAP.md`](milestones/v0.4.4-ROADMAP.md).

- [x] Phase 1: Pin Runtime Dependencies to Known-Good (2/2 plans) — completed 2026-07-04
- [x] Phase 2: Verify the Green Baseline (3/3 plans) — completed 2026-07-04
- [x] Phase 3: Modernize Python Floor (3.10–3.13) (2/2 plans) — completed 2026-07-04
- [x] Phase 4: Refresh Dev Tooling (4/4 plans) — completed 2026-07-04
- [x] Phase 5: Durability Guardrails (4/4 plans) — completed 2026-07-05

</details>

### 🚧 v0.5.0 — forward-ecosystem (In Progress)

**Milestone Goal:** Port typsphinx forward from the v0.4.4 known-good pins to the current ecosystem —
Sphinx 9.1 (FWD-01) and typst 0.15+ (FWD-02) — bumping the bundled `@preview` packages to versions
that compile cleanly (no `kai`-class breaks), fixing any Sphinx-9 / docutils-0.22 breakage, keeping
every CI job green, and releasing v0.5.0 to PyPI. Latest-only, no compatibility range.

- [x] **Phase 6: Raise Runtime Pins + Python Floor** - Sphinx 9.1 / docutils 0.22 / Python 3.12–3.13 pins + regenerated lockfile (blocking prerequisite) (completed 2026-07-09)
- [x] **Phase 7: Bump @preview Packages + typst 0.15 (kai fix)** - typst 0.15 pin + four `@preview` bumps; `docs-pdf` compiles with no `kai` (highest-risk phase) (completed 2026-07-11)
- [x] **Phase 8: API & Test Compatibility (Sphinx 9 / docutils 0.22)** - `traverse()`→`findall()` swap + full pytest suite green on the new stack (completed 2026-07-11)
- [x] **Phase 9: Green CI Matrix + Smoke Test + Guardrails** - observed all-green Actions run + `typst compile` smoke test + drift/Dependabot ceiling bumps (completed 2026-07-11)
- [x] **Phase 10: Version-String Fix + v0.5.0 Release** - `__version__`→0.5.0; PyPI wheel+sdist + GitHub Release via green `release.yml` (completed 2026-07-11)

## Phase Details

### Phase 6: Raise Runtime Pins + Python Floor

**Goal**: The extension installs, imports, and registers both builders against Sphinx 9.1 + docutils 0.22 on Python 3.12–3.13 with a regenerated lockfile — an atomic pin-raise that stands up the real ecosystem so every downstream phase can diagnose against it. (Expected state after this phase: PDF/`docs-pdf` lanes stay red on the `kai` break — that fix is Phase 7.)
**Depends on**: Nothing (first phase of milestone; builds on the v0.4.4 green baseline)
**Requirements**: FWD-01, PIN-01, PIN-02, PIN-03
**Success Criteria** (what must be TRUE):

  1. `uv`/`pip` resolves `sphinx>=9.1,<10` and `docutils>=0.21,<0.23` (docutils 0.22.4), and a `sphinx-build` invocation confirms both the `typst` and `typstpdf` builders register under Sphinx 9.1
  2. The supported Python range reads 3.12–3.13 everywhere — `pyproject.toml` `requires-python`>=3.12 + classifiers, `tox.ini` `env_list`, the CI/docs/release workflow matrices, and the black/ruff/mypy target-versions — with 3.10 and 3.11 removed
  3. `uv sync --locked` is green at every lockfile-currency gate site against a regenerated, minimal-diff `uv.lock`
  4. The sphinx + docutils + python-floor + lockfile changes land as one atomic change, so no intermediate state attempts to install Sphinx 9.1 on Python 3.10/3.11

**Plans**: 1/1 plans complete

- [x] 06-01-PLAN.md — Atomic pin-raise: pyproject sphinx/docutils/python floor + regenerated uv.lock, then mirror the 3.12 floor into tox.ini + all four CI workflows (single wave, atomic)

### Phase 7: Bump @preview Packages + typst 0.15 (kai fix)

**Goal**: `typst` is raised to 0.15 and the four bundled `@preview` packages are bumped in lockstep so the `typstpdf` builder compiles the project docs to PDF with zero `kai`-class errors — the empirical root-cause fix and the highest-risk gate of the milestone.
**Depends on**: Phase 6 (needs the typst-0.15-capable stack installed to reproduce and compile-verify)
**Requirements**: FWD-02, PKG-01, PKG-02, PKG-03
**Success Criteria** (what must be TRUE):

  1. `typst` is pinned `>=0.15.0,<0.16` and a real `docs-pdf` compile produces the PDF with no `unknown variable: kai` (or any other) `TypstError` — verified by an actual compile, not changelog inference
  2. mitex `0.2.4`→`0.2.7`, gentle-clues `1.2.0`→`1.3.1`, and codly-languages `0.1.1`→`0.1.10` are bumped, and codly `1.3.0` is empirically confirmed to compile under typst 0.15
  3. The 3-way `@preview` version sync (`writer.py` / `template_engine.py` / `templates/base.typ`) agrees in lockstep and `tests/test_preview_version_sync.py` passes

**Contingency**: If `kai` persists after the mitex bump, bisect by reverting one package at a time. codly `1.3.0` is the fallback suspect — it is already at the registry ceiling (no newer version exists), so a source-level workaround/patch is the escalation path if it breaks.
**Plans**: 1/1 plans complete

- [x] 07-01-PLAN.md — Atomic bump: raise the typst pin (`>=0.15.0,<0.16`) + regenerate uv.lock, bump the four `@preview` versions in lockstep across the 3 sync sites, then prove `docs-pdf` compiles kai-free (single wave, atomic)

### Phase 8: API & Test Compatibility (Sphinx 9 / docutils 0.22)

**Goal**: The translator, writer, builder, and config registration are confirmed compatible with Sphinx 9.1 + docutils 0.22, the soft-deprecated docutils API is modernized, and the full pytest suite — including the now-`kai`-free PDF integration tests — passes on the new stack.
**Depends on**: Phase 7 (the full pytest suite includes PDF integration tests, which need the `kai` fix landed)
**Requirements**: API-01, API-02
**Success Criteria** (what must be TRUE):

  1. The deprecated `doctree.traverse()` at `template_engine.py:239` is replaced with `doctree.findall()` (consistent with `builder.py`) and no `traverse()` deprecation warnings remain
  2. The translator / writer / builder / config registration run without `AttributeError`/`TypeError`/deprecation-removal breakage against the resolved Sphinx 9.1 + docutils 0.22 (incl. the docutils 0.22 multi-`<term>` definition-list edge case)
  3. The full pytest suite (~400 tests, incl. PDF integration) passes locally against the new stack
  4. The tree is black/ruff/mypy clean after any reformatting surfaced by the target-version bump

**Plans**: 3/3 plans complete

Plans:
**Wave 1**

- [x] 08-01-PLAN.md — Wave 1: API-01 `traverse()`→`findall()` source swap + `test_translator.py` 3× `OptionParser`→`frontend.get_default_settings`
- [x] 08-02-PLAN.md — Wave 1: builder.app→_app (test_builder/test_pdf_generation) + `writer_name`→`writer=get_writer_class` (test_documentation_configuration/usage)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 08-03-PLAN.md — Wave 2: permanent `filterwarnings` deprecation guard (pyproject.toml) + optional multi-`<term>` hardening + full-suite/black/ruff/mypy phase gate

### Phase 08.1: admonition rendering fix — translator markup/code-mode mismatch (INSERTED)

**Goal:** Admonitions (`.. note::`, `.. warning::`, etc.) render typeset prose in the compiled PDF instead of literal, unevaluated Typst source (`par({text(...)})`) — by switching `_visit_admonition` from markup-mode (`clue_type[`) to a code-mode content-block form (`clue_type({ ... })`) at its single choke point in `translator.py`. Scope-widened per user decision: preserve inline markup in admonition titles (buffer-swap, D-02), add the missing types `hint`/`error`/`danger`/`attention` + generic `.. admonition::` (D-06), strengthen the loose unit asserts (D-03), and add a real `docs-pdf` compile + PDF-text-extraction acceptance gate (D-04/D-05).
**Requirements**: None (scope defined by CONTEXT.md decisions D-01..D-06; no REQ-IDs mapped)
**Depends on:** Phase 8
**Plans:** 4/4 plans complete

Plans:

**Wave 1**

- [x] 08.1-01-PLAN.md — pypdf dev dependency behind a blocking-human legitimacy checkpoint (SUS false-positive), enabling the D-04 PDF-text-extraction gate
- [x] 08.1-02-PLAN.md — Core fix: `_visit_admonition`/`_depart_admonition` code-mode content-block body (D-01) + admonition-aware `visit_title` buffer-swap for inline-markup titles (D-02) + strengthened/nested unit tests (D-03/D-05)

**Wave 2** *(blocked on 08.1-02)*

- [x] 08.1-03-PLAN.md — New admonition types (D-06): hint→tip, error→error, danger→danger, attention→warning, generic `.. admonition::`→base clue() + per-type tests

**Wave 3** *(blocked on 08.1-01/02/03)*

- [x] 08.1-04-PLAN.md — Real-render acceptance gate (D-04): minimal fixture + `tests/test_pdf_render_gate.py` (typst.compile + pypdf no-leak assertion) + `tox -e docs-pdf` phase gate

### Phase 9: Green CI Matrix + Smoke Test + Guardrails

**Goal**: Every CI lane goes green on an observed Actions run across the full matrix, a `typst compile` smoke test guards against future `kai`-class breaks slipping past the internal-only sync test, and the durability guardrails are bumped to the new majors.
**Depends on**: Phase 8
**Requirements**: CI-01, CI-02, CI-03
**Success Criteria** (what must be TRUE):

  1. An observed Actions run shows every job green — lint, the 3-OS × Python 3.12–3.13 test matrix, type-check, coverage, build, and `docs.yml` (docs-PDF ubuntu-only)
  2. A `typst compile` smoke test is wired into CI that would fail loudly on a `kai`-class `@preview` break before release (closing the gap the internal-only version-sync test misses)
  3. `drift.yml` ceilings and the `sphinx-typst-stack` Dependabot group reflect `sphinx<10` / `typst<0.16` / `docutils<0.23`

**Plans**: 2/2 plans complete

Plans:

**Wave 1**

- [x] 09-01-PLAN.md — CI-02: `typst compile` smoke test — new `preview_smoke` fixture exercising all four `@preview` packages (incl. a real `.. math::` → mitex) + `tests/test_preview_smoke_gate.py` + documented negative-control proof

**Wave 2** *(blocked on 09-01)*

- [x] 09-02-PLAN.md — CI-03 guardrail verification (no-op per D-06) + stale `main` branch-protection reconciliation + CI-01 observation: open `release/v0.5.0 → main` PR, observe every job green, do NOT merge (D-03)

### Phase 10: Version-String Fix + v0.5.0 Release

**Goal**: Phase 10 *prepares* the v0.5.0 release on `release/v0.5.0` — the version string is corrected to 0.5.0 and single-sourced (`__version__` derived from `importlib.metadata`; `pyproject.toml` `version` bumped `0.4.4`→`0.5.0` as the sole source), and `CHANGELOG.md` gains a curated v0.5.0 entry. The tag, `release.yml` publish (PyPI + GitHub Release), and the `release/v0.5.0 → main` merge (PR #112) are **deferred to milestone completion** (`/gsd-complete-milestone`), mirroring the v0.4.4 precedent.
**Depends on**: Phase 9 (release only after the full CI matrix is confirmed green)
**Requirements**: REL-01 (version-fix half; publish half completes at milestone close)
**Success Criteria** (what must be TRUE):

  1. `typsphinx/__init__.py` no longer hardcodes a version — `__version__` derives from `importlib.metadata.version("typsphinx")`, `pyproject.toml` `version` is bumped `0.4.4`→`0.5.0` as the single source, importing typsphinx reports `0.5.0`, and the stale `0.4.3` is gone
  2. `CHANGELOG.md` has a curated `v0.5.0` entry (Sphinx 9.1 + docutils 0.22 / typst 0.15 + `@preview` kai fix / admonition render fix / Python 3.12–3.13 floor / CI smoke-gate + guardrails) — the single source for the eventual GitHub Release body
  3. The full test suite + `black`/`ruff`/`mypy` stay green on `release/v0.5.0` after single-sourcing (incl. `tests/test_extension.py` reconciled off the tautological assert); no tag pushed, no publish, PR #112 left open

**Deferred to `/gsd-complete-milestone` (REL-01 publish half):** merge `release/v0.5.0 → main` (PR #112) → tag `v0.5.0` → `release.yml` green end-to-end → `typsphinx==0.5.0` on PyPI (wheel + sdist) + GitHub Release.

**Plans**: 2/2 plans complete

Plans:

**Wave 1** *(parallel — disjoint files, no cross-dependency)*

- [x] 10-01-PLAN.md — Single-source `__version__` via `importlib.metadata` (+ `PackageNotFoundError` fallback), bump `pyproject.toml` `0.4.4`→`0.5.0`, regenerate `uv.lock`, add the independent `tomllib` drift-guard test
- [x] 10-02-PLAN.md — Curated `## [0.5.0]` `CHANGELOG.md` entry under the top `## [Unreleased]` header + link-reference fixes

## Progress

**Execution Order:**
Phases execute in numeric order: 6 → 7 → 8 → 9 → 10

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Pin Runtime Dependencies to Known-Good | v0.4.4 | 2/2 | Complete | 2026-07-04 |
| 2. Verify the Green Baseline | v0.4.4 | 3/3 | Complete | 2026-07-04 |
| 3. Modernize Python Floor (3.10–3.13) | v0.4.4 | 2/2 | Complete | 2026-07-04 |
| 4. Refresh Dev Tooling | v0.4.4 | 4/4 | Complete | 2026-07-04 |
| 5. Durability Guardrails | v0.4.4 | 4/4 | Complete | 2026-07-05 |
| 6. Raise Runtime Pins + Python Floor | v0.5.0 | 1/1 | Complete    | 2026-07-09 |
| 7. Bump @preview Packages + typst 0.15 (kai fix) | v0.5.0 | 1/1 | Complete    | 2026-07-11 |
| 8. API & Test Compatibility (Sphinx 9 / docutils 0.22) | v0.5.0 | 3/3 | Complete    | 2026-07-11 |
| 9. Green CI Matrix + Smoke Test + Guardrails | v0.5.0 | 2/2 | Complete    | 2026-07-11 |
| 10. Version-String Fix + v0.5.0 Release | v0.5.0 | 2/2 | Complete   | 2026-07-11 |

---
*Roadmap created: 2026-07-04 · Reorganized: 2026-07-05 at v0.4.4 milestone close · v0.5.0 phases (6–10) added: 2026-07-09*
