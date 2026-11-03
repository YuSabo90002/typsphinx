# Plan — typsphinx

Project verify: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`

## Config

- max_review_cycles: 3
- wave_budget: none
- review_panel: off
- finding_skeptics: off

## Wave 1 — release 0.10.0 prep and charged-ieee fixes

Goal: the repository is release-ready at 0.10.0 — version, README status, a dated `## [0.10.0]` CHANGELOG section with a breaking-change lead, link block, newest-first CHANGELOG order, gate tests following the version, and a clean build/twine check (T001) — and the charged-ieee example renders the same abstract in both approaches with its README naming typsphinx (T002).
Review depth: full

## Surface contract

### CHANGELOG.md release notes (`scripts/extract_changelog_section.py 0.10.0` output) — T001

Criteria: SC2
Entry: `uv run python scripts/extract_changelog_section.py 0.10.0`
States: success — exit 0, prints the 0.10.0 section starting with the lead paragraph that names codly 2.0.0, `/_typsphinx/deps.typ` and the custom-template migration; error — non-zero exit, missing section, or the lead omits the breaking change
Walkthrough:
1. Run the command and read its output.
2. Confirm the first paragraph names the codly 2.0.0 breaking change, the deps.typ contract and the template migration, and that the Added/Changed entries from the former Unreleased follow.
3. Open CHANGELOG.md and confirm `## [Unreleased]` holds only `### Planned for Future Releases` and the link block has `[Unreleased]` → `v0.10.0...HEAD` and `[0.10.0]` → `releases/tag/v0.10.0`.

### README.md status line — T001

Criteria: SC1
Entry: open `README.md` at the `**Status**` line
States: success — names v0.10.0; error — still v0.9.8
Walkthrough:
1. Open README.md and find the `**Status**:` line; confirm it names v0.10.0.

### examples/charged-ieee PDFs and README — T002

Criteria: SC4, SC5
Entry: `uv run sphinx-build -E -b typstpdf` for `examples/charged-ieee/approach1` and `examples/charged-ieee/approach2` (using each approach's real source layout), then open both PDFs; open `examples/charged-ieee/README.md`
States: success — the abstract text and line breaks extracted from both PDFs are identical; the README has no "sphinx-typst"; error — abstract differs or old name remains
Walkthrough:
1. Build both approaches with typstpdf into fresh output directories.
2. Extract page-1 text from both PDFs and compare the abstract block.
3. Search the README for "sphinx-typst" and confirm none remain.

## Intent coverage

| Criterion | Task | Acceptance |
|-----------|------|------------|
| SC1 | T001 | AC1 |
| SC2 | T001 | AC2 |
| SC3 | T001 | AC3 |
| SC4 | T002 | AC1 |
| SC5 | T002 | AC2 |
| SC6 | T001 | AC4 |
| SC7 | T001 | AC5 |

## Held-out checks

| Edge | Task | Test |
|------|------|------|

## Dependency notes

- T001 and T002 are independent (disjoint `files`). DOCS-AUDIT #1 and #2 are folded into T002 (SC4, SC5); #3 into T001 (SC3).
- T001 owns SC7 (whole-repository green) and its Verify runs the full suite.
