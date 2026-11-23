# Plan — typsphinx

Project verify: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/ && rm -rf docs/_build && cd docs && LC_ALL=C uv run sphinx-build -b typstpdf -E source _build/pdf`

## Config

- max_review_cycles: 3
- wave_budget: none
- review_panel: off
- finding_skeptics: off

## Wave 1 — unhandled-node fix and doc alignment

Goal: option lists, classifiers and productionlists render and compile under `typstpdf`, visitor-less nodes no longer break compilation, existing output is unchanged (T001); README states the dependency upper bounds and CHANGELOG records the fix (T002).
Review depth: full

## Surface contract

### typstpdf / typst builder output (`sphinx-build -b typstpdf` / `-b typst`: emitted .typ and compiled PDF) — T001

Criteria: SC1, SC2, SC3, SC4, SC5
Entry: `LC_ALL=C uv run python -m sphinx -b typstpdf -E <fixture srcdir> <fresh outdir>` on the fixtures under `tests/fixtures/unhandled_nodes_render_gate/`, then the emitted `<outdir>/index.typ` and the compiled PDF
States: success — exit 0, no `unknown node type` warning for option-list, classifier or productionlist nodes, `.typ` shows `terms(...)` / in-term classifiers / the three-column grammar with anchors, PDF text (pypdf) shows the content; fallback fixture — exit 0 with the `unknown node type` warning still logged and the node text in the PDF; error — exit 2 with `expected semicolon or line break`, a missing warning, or missing text
Walkthrough:
1. Build the option-list fixture with `typstpdf`; confirm exit 0, read the `terms(...)` output in `index.typ` (raw options, italic raw arguments, `, ` join, `-c FILE` / `--see=FILE` delimiters) and extract the PDF text to see every option, argument and the `"` `\` `#` description.
2. Build the classifier fixture; confirm each classifier sits inside its `terms.item` term as ` : ` + italic text and the PDF shows `term : c1 : c2`.
3. Build the productionlist fixture; confirm the three-column grammar, continuation lines in the rule column, the `:token:` link to the production anchor, and the unresolved token as plain text.
4. Build the fallback fixture (a test-only visitor-less node in a paragraph, list item, table cell and term/heading); confirm exit 0, the warning in stderr and the node text in the PDF.
5. Check SC5: `git diff a31fd6ca -- tests/` edits no pre-existing expected-.typ assertion; full suite, black/ruff/mypy and the clean docs PDF build pass.

### README.md (as rendered on GitHub) — T002

Criteria: SC6
Entry: open `README.md` at `## Requirements`
States: success — "Sphinx 9.1 or higher (below 10)" and the typst-py `<0.16` bound, matching pyproject.toml:29,31; error — a bound missing or any other README line changed
Walkthrough:
1. Read `## Requirements` and compare with `pyproject.toml` lines 29 and 31.
2. Check `git diff a31fd6ca -- README.md` changes only those two lines.

### CHANGELOG.md — T002

Criteria: SC7
Entry: open `CHANGELOG.md` at `## [Unreleased]`
States: success — a `### Fixed` section naming option lists, definition-list classifiers and productionlists (#194) and visitor-less nodes, the `### Documentation` bullet intact; error — no entry or another line changed
Walkthrough:
1. Read `## [Unreleased]` and find the `### Fixed` entry.
2. Check `git diff a31fd6ca -- CHANGELOG.md` shows only added lines in that section.

## Intent coverage

| Criterion | Task | Acceptance |
|-----------|------|------------|
| SC1 | T001 | AC1 |
| SC2 | T001 | AC2 |
| SC3 | T001 | AC3 |
| SC4 | T001 | AC4 |
| SC5 | T001 | AC5 |
| SC6 | T002 | AC1 |
| SC7 | T002 | AC2 |

## Dependency notes

- T001 and T002 are independent: disjoint `files`, no shared shapes; both run in parallel.
- DOCS-AUDIT queue #1 and #2 (fix-doc, README requirement bounds) are folded into T002 as SC6.
