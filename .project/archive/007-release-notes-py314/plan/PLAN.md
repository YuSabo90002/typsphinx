# Plan — typsphinx

Project verify: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`

## Config

- max_review_cycles: 3
- wave_budget: none
- review_panel: off
- finding_skeptics: off

## Wave 1 — 0.10.0 release-note and docs follow-up

Goal: the 0.10.0 notes state Python 3.14 support, the advanced example's abstract renders without stray line breaks, and README marks `documentclass` optional (T001).
Review depth: full

## Surface contract

### CHANGELOG.md release notes (`scripts/extract_changelog_section.py 0.10.0` output) — T001

Criteria: SC1
Entry: `uv run python scripts/extract_changelog_section.py 0.10.0`
States: success — exit 0 and the Added list includes a Python 3.14 support bullet; error — non-zero exit or no 3.14 mention
Walkthrough:
1. Run the command and find the Python 3.14 bullet under Added.
2. Confirm the `## [0.10.0] - 2026-11-03` heading line in CHANGELOG.md is unchanged.

### docs/source/examples/advanced.rst — T001

Criteria: SC2
Entry: open `docs/source/examples/advanced.rst` at the `ieee_abstract` example
States: success — the example string has no embedded newline; error — triple-quoted multi-line string remains
Walkthrough:
1. Open the file at the `ieee_abstract =` line and confirm the single-line or concatenated form with the same words.
2. Run `LC_ALL=C uv run pytest tests/test_advanced_example_abstract_gate.py -q` and confirm it passes.

### README.md — T001

Criteria: SC3
Entry: open `README.md` at the two `typst_documents` tuple descriptions
States: success — both mark `documentclass` as an optional fifth element; error — either presents it as required
Walkthrough:
1. Open README.md near line 84 and near line 233 and confirm both say the fifth element is optional.

## Intent coverage

| Criterion | Task | Acceptance |
|-----------|------|------------|
| SC1 | T001 | AC1 |
| SC2 | T001 | AC2 |
| SC3 | T001 | AC3 |
| SC4 | T001 | AC4 |

## Held-out checks

| Edge | Task | Test |
|------|------|------|

## Dependency notes

- Single task; no dependencies. DOCS-AUDIT #4 (fix-doc) is folded into T001 as SC3.
