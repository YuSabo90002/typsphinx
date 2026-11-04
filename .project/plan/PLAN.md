# Plan — typsphinx

Project verify: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`

## Config

- max_review_cycles: 3
- wave_budget: none
- review_panel: off
- finding_skeptics: off

## Wave 1 — README simplification with no information loss

Goal: every README-only item has a home in docs/source (T001), then README.md is rewritten to the approved section set, its pinning gates follow it, and CHANGELOG records the change (T002).
Review depth: full

## Surface contract

### README.md (as rendered on GitHub) — T002

Criteria: SC1, SC2, SC3, SC4, SC5
Entry: open `README.md` (GitHub file view of the branch, or the file itself)
States: success — exactly the ten `## ` sections in the approved order, minimal Quick Start, one-line Features including Graphviz, link-only Contributing/Version History, Status line, Acknowledgments with diagraph/typst-py/GSD Path; error — any removed section, nested Features bullet, `@preview/`, `gsd-core`, or `pybtex`/`CSL`/`#bibliography` text remains
Walkthrough:
1. Run `grep '^## ' README.md` and compare with SC1's list and order.
2. Read Installation and Quick Start: pip block, uv block, Basic Configuration (minimal conf.py, no `#### typst_documents`), Build Typst Output (`-b typst` and `-b typstpdf`), Example Document.
3. Read Features: one line per bullet, bibliography bullet feature-only with a guide link, Graphviz bullet with a diagrams-guide link.
4. Read Contributing, Version History, Acknowledgments and the trailing Status lines against SC4 and SC5.

### docs HTML manual (pages that receive content moved out of README) — T001

Criteria: SC6, SC7
Entry: clean HTML build `sphinx-build -W -E -b html docs/source <fresh dir>` and the built pages listed in T002's removed-item table
States: success — build exits 0 with no warning and every table row's docs location shows the item; error — a warning, a build failure, or a README-only item with no docs location
Walkthrough:
1. Run the clean build and confirm exit 0 with no warnings.
2. For each row of T002's removed-item → docs location table, open the built HTML page and find the item stated concretely (not a pointer).
3. Compare the table against `git diff c1606cd9 -- README.md` deleted lines; Contributing items are marked `deleted per C5`.

### CHANGELOG.md — T002

Criteria: SC8
Entry: open `CHANGELOG.md` at `## [Unreleased]`
States: success — one new bullet saying README was simplified and details moved to the manual, all other lines unchanged; error — no bullet, or another line changed
Walkthrough:
1. Read `## [Unreleased]` and find the bullet.
2. Check `git diff c1606cd9 -- CHANGELOG.md` shows only added lines in that section.

## Intent coverage

| Criterion | Task | Acceptance |
|-----------|------|------------|
| SC1 | T002 | AC1 |
| SC2 | T002 | AC2 |
| SC3 | T002 | AC3 |
| SC4 | T002 | AC4 |
| SC5 | T002 | AC5 |
| SC6 | T001 | AC1 |
| SC7 | T001 | AC3 |
| SC8 | T002 | AC6 |
| SC9 | T002 | AC7 |

## Dependency notes

- T002 depends on T001's landed effect: T002 deletes README text whose docs home T001 adds to docs/source; run first, T002 would delete README-only information that has no home yet (N2). A reviewer sees it as every row of T002's removed-item table pointing at a docs/source location present in T002's base (or `deleted per C5`).
- DOCS-AUDIT queue #1 (fix-doc, README credit → GSD Path) is folded into T002 as SC5.
