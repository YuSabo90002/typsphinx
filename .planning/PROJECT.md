# typsphinx

## What This Is

typsphinx is a Sphinx extension that translates reStructuredText documentation into Typst markup (`.typ`) and compiles it to PDF, via the `sphinx-build -b typst` and `-b typstpdf` builders. It's a mature, PyPI-published Python package for teams who author docs in Sphinx but want Typst-quality typeset PDF output.

This planning cycle is a **forward-compatibility milestone (v0.5.0)**: v0.4.4 pinned the dependency graph back to a known-good set (typst 0.14.9, `sphinx<9`, `docutils<0.22`) to escape multi-year rot. This cycle moves forward — raising the pins to support Sphinx 9 and typst 0.15+, bumping the bundled `@preview` packages to versions that compile cleanly under typst 0.15, and fixing any translator/writer/API breakage — so the extension tracks the current ecosystem again. Latest-only: older Sphinx/typst support is intentionally dropped; a compatibility range is out of scope.

## Core Value

The `typst`/`typstpdf` builders produce correct output and every CI job stays green on the **current** ecosystem — Sphinx 9 and typst 0.15+ — with the runtime pins raised forward and the bundled `@preview` packages compiling cleanly (no `kai`-class breaks).

## Current Milestone: v0.5.0 forward-ecosystem

**Goal:** Port typsphinx forward from the v0.4.4 known-good pins to support Sphinx 9 (FWD-01) and typst 0.15+ (FWD-02), keeping every CI job green — latest-only, no compatibility range.

**Target features:**
- Raise runtime pins — drop the `sphinx<9` / `typst<0.15` ceilings; adopt Sphinx 9 + typst 0.15+
- Bump bundled `@preview` packages (gentle-clues, codly, codly-languages, mitex) to typst-0.15-compatible versions; update the 3-way version-sync (`writer.py` / `template_engine.py` / `templates/base.typ`)
- Fix Sphinx 9 / docutils API and typst 0.15 (`kai`-class) breakage across the translator / writer / template layer
- Update durability guardrails (drift.yml ceilings, Dependabot group) to the new majors; regenerate `uv.lock`
- Release v0.5.0 to PyPI with green CI across the full matrix

## Requirements

### Validated

<!-- Existing capabilities inferred from the mapped codebase. -->

- ✓ `sphinx-build -b typst` builder: reST → Typst markup (`.typ`) — existing
- ✓ `sphinx-build -b typstpdf` builder: Typst → PDF via typst-py — existing
- ✓ Visitor-pattern translator covering headings, paragraphs, inline markup, code blocks, tables, figures, lists, references, admonitions, math (mitex) — existing
- ✓ Template engine: default template, custom templates, Typst Universe (`@preview/*`) package support — existing
- ✓ Master vs. included document handling (`#include()`), image/asset copying, nested directory preservation — existing
- ✓ i18n scaffolding (sphinx-intl), full pytest suite (~400 tests), tox-based lint/typecheck/coverage, GitHub Actions CI + docs + release workflows — existing
- ✓ Runtime dependencies pinned to a reproducible known-good set (typst 0.14.9, `sphinx<9`, `docutils<0.22`); `uv.lock` regenerated and committed; tree lint-clean (`black`/`ruff`) — Validated in Phase 1
- ✓ Every CI job green across the full 3-OS × Python matrix (12 test lanes + lint/type-check/coverage/build/integration) and `docs.yml` end-to-end incl. the multi-language PDF-copy step, confirmed by an observed Actions run — Validated in Phase 2 (CI run 28702240846)
- ✓ The 3-way `@preview` version sync (`writer.py`, `template_engine.py`, `templates/base.typ`) guarded by an automated test that fails CI loudly on desync — Validated in Phase 2
- ✓ Supported Python range modernized to 3.10–3.13: `requires-python>=3.10`, 3.9 dropped / 3.13 added across pyproject classifiers, tox `env_list`, and the CI matrix; black/ruff/mypy target-versions aligned to the 3.10 floor; `uv.lock` regenerated minimal-diff — Validated in Phase 3 (green ci.yml run 28709253590 + docs.yml run 28709253571 on PR #104; all four 3.13 lanes + lint green)
- ✓ Dev tooling floors modernized with guard ceilings (`pytest>=8.4,<10`, `mypy>=1.13,<3.0`, `black>=26,<27`, `ruff>=0.15,<0.16`, `tox>=4.56,<5`, `tox-uv>=1.35,<2`) across pyproject.toml + tox.ini; artifact actions bumped to node24 (upload-artifact@v7 / download-artifact@v8); stale `Test Python 3.9` required-check removed from main protection — Validated in Phase 4 (green ci.yml/docs.yml on PR #105)
- ✓ Durability guardrails installed: `uv sync --locked` at all 9 sites (DUR-01 lockfile-currency gate), standalone weekly+dispatch `drift.yml` forward-drift detector with deduplicated issue reporting + least-privilege perms (DUR-02), `sphinx-typst-stack` Dependabot group scoped to the runtime trio (DUR-03), README CI status badge (DUR-04); `softprops/action-gh-release` @v2→@v3 node24 bump — Validated in Phase 5 (merged PR #106 green: ci.yml run 28730645396 + docs.yml run 28730645381; drift.yml validated post-merge via workflow_dispatch run 28730876125; drift-check confirmed absent from main's required checks)
- ✓ Runtime pins raised forward to the v0.5.0 target ecosystem: `sphinx>=9.1,<10` (FWD-01), `docutils>=0.21,<0.23` (PIN-01, resolves 0.22.4), Python floor raised to 3.12–3.13 across all 21 declaration sites — pyproject `requires-python`/classifiers, tox `env_list`, the ci/docs/release/drift workflows, and black/ruff/mypy target-versions (PIN-02); `uv.lock` regenerated + `uv sync --locked` green (PIN-03). The extension imports and registers both builders under Sphinx 9.1 and `sphinx-build -b typst` builds green; `typst` intentionally left `>=0.14.1,<0.15` (Phase 7). All work on `release/v0.5.0`, `main` untouched — Validated in Phase 6 (7/7 must-haves; 06-VERIFICATION.md)
- ✓ typst raised to `>=0.15.0,<0.16` (FWD-02) and the four bundled `@preview` packages bumped in lockstep across the 3 sync sites — mitex 0.2.4→0.2.7 (the actual `kai` fix, mitex CHANGELOG PR #201), gentle-clues 1.2.0→1.3.1, codly-languages 0.1.1→0.1.10, codly 1.3.0 unchanged (registry ceiling, empirically confirmed to compile) (PKG-01/PKG-02/PKG-03); `uv.lock` regenerated (typst 0.14.9→0.15.0), `test_preview_version_sync.py` + full 402-test suite green, `black`/`ruff` clean. **The empirical `kai` gate is closed**: `tox -e docs-pdf` compiles to a 101-page PDF with zero `TypstError`/`unknown variable: kai` (verified by two independent real compiles) — Validated in Phase 7 (4/4 must-haves; 07-VERIFICATION.md)
- ✓ Green CI matrix observed + `kai`-class smoke guard + guardrails confirmed for v0.5.0: an all-green Actions run across the full 3-OS × Python 3.12–3.13 matrix (lint, type-check, coverage, build, integration ×2) plus `docs.yml` build-docs — 13/13 jobs green, observed on PR #112 (`release/v0.5.0 → main`, left **unmerged** per D-03 for Phase 10) (CI-01); a `typst compile` smoke test (`tests/test_preview_smoke_gate.py` + `tests/fixtures/preview_smoke/`) that exercises all four bundled `@preview` packages via real function calls — incl. a `.. math::` block routing through mitex, the exact path the historical `kai` break lived in and the one the admonition-only gate never invoked — and fails loudly on any `TypstError`, with a documented negative-control proving it catches the `unknown variable: kai` regression (CI-02); durability guardrails (`pyproject` ceilings `sphinx<10`/`typst<0.16`/`docutils<0.23`, `drift.yml`, `sphinx-typst-stack` Dependabot group) confirmed already correct — a verified no-op per D-06 (CI-03); stale `main` branch-protection `required_status_checks` reconciled (removed the non-existent `Test Python 3.10/3.11 on ubuntu-latest` contexts, kept core gates + ubuntu 3.12/3.13, other protection settings preserved). All on `release/v0.5.0`, `main` untouched — Validated in Phase 9 (8/8 must-haves; 09-VERIFICATION.md)
- ✓ v0.5.0 release *prepared* on `release/v0.5.0` (REL-01, version-fix half): `typsphinx/__init__.py` `__version__` is now single-sourced via `importlib.metadata.version("typsphinx")` (with a `PackageNotFoundError`→`"unknown"` fallback, retiring the stale `0.4.3`), `pyproject.toml` bumped `0.4.4`→`0.5.0` as the **sole** version literal, `uv.lock` regenerated in lockstep (`uv sync --extra dev --locked` green), a new independent `tomllib` drift-guard test added (`test_version_matches_pyproject_toml`, keeping the existing `test_setup_version_matches`), and a curated `CHANGELOG.md` `## [0.5.0]` entry added under the top `## [Unreleased]` (the single source for the eventual Release body). **Phase 10 was RE-SCOPED to prep-only (D-01/D-02):** no tag, no publish, no merge — the publish half (merge PR #112 → tag `v0.5.0` → `release.yml` → PyPI wheel+sdist + GitHub Release) is **DEFERRED to `/gsd-complete-milestone`**, mirroring the v0.4.4 precedent — Validated in Phase 10 (6/6 must-haves; 10-VERIFICATION.md; 413/413 tests green, black/ruff/mypy clean; `main` untouched, PR #112 left OPEN)

### Active

<!-- Milestone v0.5.0 (forward-ecosystem). Formal REQ-IDs live in REQUIREMENTS.md. -->

- [x] Sphinx 9 / docutils 0.22 API & test compatibility (API-01/API-02) — `traverse()`→`findall()` + full pytest suite green on the new stack (the FWD-01 pin-raise itself landed in Phase 6). **Validated in Phase 8:** all 6 soft-deprecated docutils/Sphinx call sites modernized, a permanent `filterwarnings` guard (both `DeprecationWarning` + `PendingDeprecationWarning`) installed, in-process suite 357/357 green under the guard, tree black/ruff/mypy clean on `release/v0.5.0`.
- *All in-scope v0.5.0 requirements are now validated (see Validated above). REL-01's remaining **publish half** — merge PR #112 (`release/v0.5.0 → main`) → tag `v0.5.0` → `release.yml` green → `typsphinx==0.5.0` on PyPI (wheel + sdist) + GitHub Release — is a `/gsd-complete-milestone` activity, not a separate phase. The milestone is ready to close.*

### Out of Scope

- Configurable `@preview` package versions (FWD-03, tech-debt item) — deferred; v0.5.0 bumps the bundled versions in-place rather than making them user-configurable
- A Sphinx 8/typst 0.14 ⇄ Sphinx 9/typst 0.15+ compatibility range — v0.5.0 is latest-only; supporting both old and new majors simultaneously is out of scope
- Incremental-build rebuild tracking, translator state-management refactor — orthogonal tech debt, not part of a CI-repair milestone
- New translation features / new reST constructs — this is a maintenance cycle, not a feature cycle

## Context

- **Failure evidence (CI run, 2026-07-04):** loose pins resolved `sphinx==9.0.4`, `docutils==0.22.4`, `typst==0.15.0`, Python 3.11. Three buckets: (1) `black --check` reformats 3 files (`docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`); (2) 7 PDF-integration tests + all 12 matrix jobs + docs PDF build fail on `typst.TypstError: unknown variable: kai` — a pinned `@preview` package incompatible with the typst 0.15 compiler; (3) matrix jobs exit 254/1 cascading from the same compile error. Type Check and Build Package jobs currently pass.
- **`kai` origin:** the symbol appears nowhere in typsphinx source — it comes from inside a pinned Typst Universe package (likely `gentle-clues:1.2.0` or `codly`) when compiled by typst 0.15. Pinning typst back to the 0.14.x line where those packages compile is the fix.
- **Codebase map:** `.planning/codebase/` (ARCHITECTURE, STACK, CONCERNS, CONVENTIONS, INTEGRATIONS, STRUCTURE, TESTING) refreshed 2026-07-04.
- **Tech-debt note (from CONCERNS.md):** hardcoded `@preview` versions live in two places (`typsphinx/writer.py`, `typsphinx/template_engine.py`) plus `typsphinx/templates/base.typ` — keep these three in sync when pinning.
- **`kai` root cause resolved (Phase 7):** the `unknown variable: kai` break came specifically from **mitex** (fixed in mitex 0.2.6, PR #201), not gentle-clues/codly as originally speculated in the failure evidence above. Bumping mitex 0.2.4→0.2.7 cleared it; codly 1.3.0 compiles clean under typst 0.15.
- **Known follow-up bug — RESOLVED in Phase 8.1 (2026-07-11):** `.. note::` / admonitions rendered literal Typst source (`par({text(...)})`) instead of typeset prose — a markup-vs-code-mode mismatch in `typsphinx/translator.py::_visit_admonition` (discovered Phase 7, pre-existing since 2025-10-13; orthogonal to `@preview` versions, invisible until `docs-pdf` first compiled post-`kai`-fix). **Fix:** `_visit_admonition`/`_depart_admonition` now emit the code-mode content-block form `clue_type({...})` (was markup `clue_type[`), and titles route through a `visit_title`/`depart_title` buffer-swap that preserves inline markup (D-02) and fixed a latent title double-emission bug. Scope also widened per discussion: 5 previously-missing admonition types added (`hint`→tip, `error`→error, `danger`→danger, `attention`→warning, generic `.. admonition::`→base `clue()`; D-06), unit asserts strengthened to structural checks (D-03), nested-content coverage (D-05), and a real D-04 acceptance gate (`tests/test_pdf_render_gate.py` + `tox -e docs-pdf`: compile → `pypdf` text-extraction → no-leak assertion) that proves the fix in a real render. Full suite 411/411 green; gentle-clues 1.3.1 / `@preview` versions unchanged.

## Constraints

- **Tech stack**: Python package; Sphinx builder API; Typst via typst-py — pinning must keep the extension importable and the builders registered
- **Compatibility**: `@preview` package versions and the typst compiler version must be mutually compatible — this is the crux of the fix
- **Reproducibility**: `uv.lock` must be regenerated to match the new pins; tox/uv drives all CI checks
- **Platforms**: CI runs ubuntu/macos/windows — pins must produce green on all three

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pin runtime deps to known-good rather than upgrade forward | Fastest, lowest-risk path to green CI; avoids a large sphinx-9/typst-0.15 porting effort in a maintenance cycle | Confirmed: full 3-OS × Python matrix green in Phase 2 (CI run 28702240846) |
| Pin `typst` to 0.14.x compatible with bundled `@preview` packages | The `kai` break is a typst 0.15 ⇄ package incompatibility; reverting the compiler restores compilation | Confirmed: `typst==0.14.9` (resolved in `uv.lock`); `docs-pdf` builds `index.pdf` locally with no `kai` error (typst 0.15.0 reproduces it) |
| Modernize Python floor to 3.10–3.13 (drop EOL 3.9, add 3.13) | 3.9 reached EOL Oct 2025; "green + modernize" scope | Confirmed in Phase 3: full 3.10–3.13 matrix + `docs.yml` green on PR #104 (no 3.13 wheel gap; D-03 ruff pyupgrade reformat fired and was fixed in-batch; `conf.py` `tomllib`→`tomli` backport for the 3.10 docs floor) |
| Defer supporting sphinx 9 / typst 0.15 to a future milestone | Explicitly chosen to pin, not port; keeps scope bounded | — Pending |
| `sphinx<9`/`docutils<0.22` ceilings are precautionary, not load-bearing for the `kai` break (D-03) | The `kai` break is purely the typst 0.15 compiler; per RESEARCH's Linux reproduction, `docs-pdf` builds with `typst` pinned even with sphinx/docutils unbounded. Ceilings still applied per D-03 as guardrails against unrelated sphinx-9 / docutils-0.22 drift | Precautionary (not load-bearing) confirmed on Linux; `docs-pdf` builds green with typst 0.14.9, sphinx 7.4.7/8.1.3, docutils 0.21.2. Full 3-OS × Python-version matrix confirmation is Phase 2's gate |
| Accept already-green pytest 9.1.1 / mypy 2.1.0 with next-major ceilings, not a rollback to literal `pytest~=8.4`/`mypy<2.0` (D-01, Phase 4) | Phase 3's green CI already resolved pytest 9.1.1 + mypy 2.1.0; rolling back would shrink the confirmed known-good set. Honor TOOL-01's spirit ("no risky major flips") via guard ceilings instead — a deliberate, user-owned deviation from TOOL-01's literal wording | Applied: `pytest>=8.4,<10`, `mypy>=1.13,<3.0` in pyproject.toml + tox.ini; Phase 4 CI green on PR #105 |
| All refreshed dev tools get `floor+<next-major` guard ceilings, incl. tox-uv (D-02/D-07, Phase 4) | Matches Phase 1's defensive runtime pinning + the anti-drift milestone theme; no bare `>=` floor leaving an unbounded re-resolution path | Applied lockstep across pyproject.toml `[dev]` + tox.ini (4 mirror points incl. `[tox] requires` for tox-uv): black `>=26,<27`, ruff `>=0.15,<0.16`, tox `>=4.56,<5`, tox-uv `>=1.35,<2` |
| Bump artifact actions to node24: upload-artifact@v5→v7, download-artifact@v6→v8 (D-03 AMENDED 2026-07-05, Phase 4) | Post-research: v5/v6 still declare node20, which GitHub removes from hosted runners 2026-09-16; the original "already at latest majors" premise was wrong | Applied across ci.yml/docs.yml/release.yml (7 + 3 occurrences), runtime-verified node24; Phase 4 CI green |
| Remove stale `Test Python 3.9 on ubuntu-latest` required status check from `main` branch protection, add 3.13 (Phase 4) | Phase-3 leftover: 3.9 was dropped from the CI matrix but the required-check list wasn't updated, leaving a permanent "Expected — waiting for status" pending that blocked PR #105 despite all 18 jobs green | Applied via `gh api PATCH`; PR #105 became MERGEABLE/CLEAN. Required set now ubuntu 3.10–3.13 + Lint/Type/Coverage/Build |
| `softprops/action-gh-release@v2` node20 straggler tracked, not force-bumped in Phase 4 | Outside 04-02's authorized edit scope (artifact-actions only) and needs its own verification; `@v3` exists and is node24 | Deferred to Phase 5 (durability-guardrails) as a tracked item, not silently closed |
| Close the milestone with durability guardrails: `--locked` lockfile-currency gate + standalone weekly `drift.yml` + `sphinx-typst-stack` Dependabot group + README CI badge; softprops@v3 (Phase 5, D-01..D-11) | Install anti-drift controls so the silent multi-year rot this milestone fixed cannot recur unnoticed; keep the drift job advisory (never a required check, D-07) so it reports without blocking merges | Confirmed in Phase 5: PR #106 merged green (ci.yml 28730645396 / docs.yml 28730645381); drift.yml validated via post-merge `workflow_dispatch` (run 28730876125 success, no drift issue = no forward drift); D-11 softprops@v3 runtime confirmation RESOLVED at the v0.4.4 release: `Create GitHub Release` ran green (release run 28731646924, tag `v0.4.4`) |
| Fix `release.yml` version-verify step: `import tomllib` → `tomllib`/`tomli` fallback (v0.4.4 release, PR #110) | PYVER-02's 3.10 floor reconciliation left the tag-only Validate step importing stdlib-only `tomllib` on 3.10; it crashed on the first `v0.4.4` tag push (a release-only regression not exercised by any PR CI) | Fixed on `main` (merge dae500a); re-pushed `v0.4.4` tag; release run 28731646924 green end-to-end → PyPI `typsphinx==0.4.4` (wheel+sdist) + GitHub Release published |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-07-11 after Phase 10 (Version-String Fix + v0.5.0 Release) complete — the FINAL phase of the v0.5.0 milestone. Phase 10 was re-scoped to release *preparation only* (D-01/D-02): `typsphinx.__version__` is now single-sourced from `importlib.metadata` (reporting `0.5.0`, stale `0.4.3` gone) with a `PackageNotFoundError` fallback; `pyproject.toml` is the sole version literal (`0.5.0`); `uv.lock` regenerated; a genuine `tomllib` drift-guard test added; and a curated `CHANGELOG.md` `[0.5.0]` entry prepared as the single source for the Release body. 6/6 must-haves verified (10-VERIFICATION.md); 413/413 tests green, black/ruff/mypy clean on `release/v0.5.0`. Scope fence held: no tag, no PyPI publish, no GitHub Release, `main` untouched, PR #112 left OPEN. **All v0.5.0 phases (6–10 + 8.1) are complete — the milestone is ready for `/gsd-complete-milestone`, which executes the deferred REL-01 publish half (merge PR #112 → tag `v0.5.0` → `release.yml` → PyPI + GitHub Release), mirroring the v0.4.4 precedent.*

<!-- Prior: 2026-07-11 after Phase 9 (Green CI Matrix + Smoke Test + Guardrails) complete — the v0.5.0 stack (Sphinx 9.1 / docutils 0.22 / typst 0.15) is now observed all-green in real CI for the first time: PR #112 (`release/v0.5.0 → main`) shows 13/13 jobs green across the full 3-OS × Python 3.12–3.13 matrix + `docs.yml` build-docs, left **unmerged** for Phase 10 (CI-01). A `typst compile` smoke test (`tests/test_preview_smoke_gate.py` + `tests/fixtures/preview_smoke/`) now guards all four bundled `@preview` packages via real function calls incl. a `.. math::` block through mitex — closing the `kai`-class coverage gap the admonition-only gate missed, proven by a documented negative-control (CI-02). Durability guardrails confirmed already correct (verified no-op, D-06) and the stale `main` branch-protection required-checks reconciled (CI-03 + access-control durability). 8/8 must-haves; 09-VERIFICATION.md; 412/412 tests green; black/ruff/mypy clean on `release/v0.5.0`; `@preview` versions unchanged. Next: Phase 10 (v0.5.0 PyPI release) — add the `__version__` 0.4.3→0.5.0 fix to PR #112, merge, tag, publish.* -->

