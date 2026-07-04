# typsphinx

## What This Is

typsphinx is a Sphinx extension that translates reStructuredText documentation into Typst markup (`.typ`) and compiles it to PDF, via the `sphinx-build -b typst` and `-b typstpdf` builders. It's a mature, PyPI-published Python package for teams who author docs in Sphinx but want Typst-quality typeset PDF output.

This planning cycle is a **maintenance milestone**: the project went unmaintained while its dependency pins stayed loose, so CI now resolves newer major versions of the ecosystem (sphinx 9, docutils 0.22, typst 0.15) and fails across lint, tests, coverage, and the docs PDF build. The goal is to get every CI job green again by pinning back to a known-good dependency combination, and to opportunistically modernize the supported Python range and dev tooling while we're in here.

## Core Value

Every CI job passes again on `main` — lint, the full test matrix, coverage, and the docs PDF build — with a dependency set that is pinned and reproducible so this rot doesn't silently recur.

## Requirements

### Validated

<!-- Existing capabilities inferred from the mapped codebase. -->

- ✓ `sphinx-build -b typst` builder: reST → Typst markup (`.typ`) — existing
- ✓ `sphinx-build -b typstpdf` builder: Typst → PDF via typst-py — existing
- ✓ Visitor-pattern translator covering headings, paragraphs, inline markup, code blocks, tables, figures, lists, references, admonitions, math (mitex) — existing
- ✓ Template engine: default template, custom templates, Typst Universe (`@preview/*`) package support — existing
- ✓ Master vs. included document handling (`#include()`), image/asset copying, nested directory preservation — existing
- ✓ i18n scaffolding (sphinx-intl), full pytest suite (~400 tests), tox-based lint/typecheck/coverage, GitHub Actions CI + docs + release workflows — existing

### Active

<!-- This milestone. Building toward green + modernized CI. -->

- [ ] All CI lint checks pass (`black --check`, ruff) on `main`
- [ ] The full test matrix passes: the `unknown variable: kai` typst-compilation break is resolved by pinning to a known-good dependency combination
- [ ] Coverage job passes; docs workflow produces a PDF and completes
- [ ] Runtime dependencies pinned to a reproducible known-good set: `typst` back to a 0.14.x compatible with the bundled `@preview` packages (codly 1.3.0, codly-languages 0.1.1, mitex 0.2.4, gentle-clues 1.2.0), plus `sphinx`/`docutils` upper bounds
- [ ] Supported Python range modernized to 3.10–3.13: `requires-python>=3.10`, drop EOL 3.9, add 3.13, CI matrix updated
- [ ] Dev tooling modernized: Black/mypy target versions aligned to the new Python floor; CI action versions refreshed as needed

### Out of Scope

- Adapting code/templates to *support* Sphinx 9 / typst 0.15 / newest `@preview` packages — deferred; this cycle pins to known-good rather than upgrading forward
- Configurable `@preview` package versions (tech-debt item) — not required for green; revisit if it blocks pinning
- Incremental-build rebuild tracking, translator state-management refactor — orthogonal tech debt, not part of a CI-repair milestone
- New translation features / new reST constructs — this is a maintenance cycle, not a feature cycle

## Context

- **Failure evidence (CI run, 2026-07-04):** loose pins resolved `sphinx==9.0.4`, `docutils==0.22.4`, `typst==0.15.0`, Python 3.11. Three buckets: (1) `black --check` reformats 3 files (`docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`); (2) 7 PDF-integration tests + all 12 matrix jobs + docs PDF build fail on `typst.TypstError: unknown variable: kai` — a pinned `@preview` package incompatible with the typst 0.15 compiler; (3) matrix jobs exit 254/1 cascading from the same compile error. Type Check and Build Package jobs currently pass.
- **`kai` origin:** the symbol appears nowhere in typsphinx source — it comes from inside a pinned Typst Universe package (likely `gentle-clues:1.2.0` or `codly`) when compiled by typst 0.15. Pinning typst back to the 0.14.x line where those packages compile is the fix.
- **Codebase map:** `.planning/codebase/` (ARCHITECTURE, STACK, CONCERNS, CONVENTIONS, INTEGRATIONS, STRUCTURE, TESTING) refreshed 2026-07-04.
- **Tech-debt note (from CONCERNS.md):** hardcoded `@preview` versions live in two places (`typsphinx/writer.py`, `typsphinx/template_engine.py`) plus `typsphinx/templates/base.typ` — keep these three in sync when pinning.

## Constraints

- **Tech stack**: Python package; Sphinx builder API; Typst via typst-py — pinning must keep the extension importable and the builders registered
- **Compatibility**: `@preview` package versions and the typst compiler version must be mutually compatible — this is the crux of the fix
- **Reproducibility**: `uv.lock` must be regenerated to match the new pins; tox/uv drives all CI checks
- **Platforms**: CI runs ubuntu/macos/windows — pins must produce green on all three

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pin runtime deps to known-good rather than upgrade forward | Fastest, lowest-risk path to green CI; avoids a large sphinx-9/typst-0.15 porting effort in a maintenance cycle | — Pending |
| Pin `typst` to 0.14.x compatible with bundled `@preview` packages | The `kai` break is a typst 0.15 ⇄ package incompatibility; reverting the compiler restores compilation | Confirmed: `typst==0.14.9` (resolved in `uv.lock`); `docs-pdf` builds `index.pdf` locally with no `kai` error (typst 0.15.0 reproduces it) |
| Modernize Python floor to 3.10–3.13 (drop EOL 3.9, add 3.13) | 3.9 reached EOL Oct 2025; "green + modernize" scope | — Pending |
| Defer supporting sphinx 9 / typst 0.15 to a future milestone | Explicitly chosen to pin, not port; keeps scope bounded | — Pending |
| `sphinx<9`/`docutils<0.22` ceilings are precautionary, not load-bearing for the `kai` break (D-03) | The `kai` break is purely the typst 0.15 compiler; per RESEARCH's Linux reproduction, `docs-pdf` builds with `typst` pinned even with sphinx/docutils unbounded. Ceilings still applied per D-03 as guardrails against unrelated sphinx-9 / docutils-0.22 drift | Precautionary (not load-bearing) confirmed on Linux; `docs-pdf` builds green with typst 0.14.9, sphinx 7.4.7/8.1.3, docutils 0.21.2. Full 3-OS × Python-version matrix confirmation is Phase 2's gate |

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
*Last updated: 2026-07-04 after initialization*
