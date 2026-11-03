# Plan — typsphinx

Project verify: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`

## Config

- max_review_cycles: 3
- wave_budget: none
- review_panel: off
- finding_skeptics: off

## Wave 1 — codly 2.0 contract, code-mode emission, surface proof, examples

Goal: typsphinx imports `@preview/codly:2.0.0` as a module and emits every Sphinx code block as one code-mode `codly.new(raw(...), ...)` expression, with the 1.3-era test suite rewritten in the same landing so the suite never goes red (T001); then the compiled PDF and the generated `.typ` of test-basic, examples/basic, examples/advanced and docs/source prove the options, edges, captioned listings and absence of fences/`codly(` calls (T002); then every example and the project docs compile to PDF, the two doc-audit example rulings land, and the whole repository is green (T003). If T002's PDF fixture shows the medium-confidence rules (empty-block `skip-last-empty: false`, `default` → no language) or codly 2.0 itself misbehave, T002 corrects emission inside the Interface contract before T003 builds the examples and docs; a defect that needs a different contract stops the wave for re-planning.
Review depth: full

## Surface contract

### generated content .typ files — T002

Criteria: SC2
Entry: `uv run sphinx-build -E -b typst <project> <outdir>` for `tests/roots/test-basic`, `examples/basic`, `examples/advanced` and `docs/source`, then open the content `.typ` files in `<outdir>` (everything outside `_typsphinx/` and `_template/` that is not a `typst_documents` wrapper)
States: empty — a document with no code block (test-basic) contains no `codly.new`; loading — n/a (batch build); error — any ``` run or a call `codly(` outside a `.`/letter/`-` prefix in a content file (bounded changelog exception in T002 AC3), or a code block emitted any other way; success — each literal_block/doctest_block is exactly one `codly.new(raw("...", block: true[, lang: "..."]), ...)` expression in code mode, including inside captioned figures, list items, admonitions and table cells
Walkthrough:
1. Build the four projects with `-b typst` into fresh output directories.
2. Run `grep -rn '```' <content files>` and `grep -rnE '(^|[^.a-z-])codly\(' <content files>` and confirm no match (docs/source: only the T002 AC3 changelog exception).
3. Open one content file per project and confirm each code block is a single `codly.new(raw(` expression with no leading `#`, no ``` fence and no `{`/`#{` wrapper, and that a captioned block reads `figure(codly.new(...), caption: text("..."), kind: raw)`.
4. Run `LC_ALL=C uv run pytest tests/test_codly2_output_gate.py -rs` and confirm it passes with no skips.

### typstpdf PDF output — T002

Criteria: SC3, SC4
Entry: `uv run sphinx-build -E -b typstpdf tests/fixtures/codly2_render_gate <outdir>` and open the PDF in `<outdir>`
States: empty — an empty `code-block` renders as one empty codly row with its language badge (not a hairline); loading — n/a (batch build); error — the build exits non-zero or the PDF lacks a stated number, highlight, badge or listing caption; success — numbers, highlights, badges and listing captions appear exactly as SC3/SC4 state, in codly 2.0's default look
Walkthrough:
1. Build the fixture with `-b typstpdf` and open the PDF.
2. Check the block without `:linenos:` shows no numbers; the `:linenos:` block starts at 1; the `:lineno-start: 10` block starts at 10, and with `:emphasize-lines: 2` the highlighted row is the one displayed as 11.
3. Check `:emphasize-lines: 2-4,4,6` highlights rows 2, 3, 4 and 6 only; a Python block shows the codly 2.0 "Python" badge; a block with no language shows no badge.
4. Check the captioned `:name:` block reads "Listing 1: ..." while the image figure reads "Figure 1: ...", and the `:numref:` text resolves and links to the listing.
5. Run `LC_ALL=C uv run pytest tests/test_codly2_render_gate.py -rs` and confirm it passes with no skips.

### docs user guide templates page (docs/source/user_guide/templates.rst) — T001

Criteria: SC6
Entry: `uv run sphinx-build -E -b html docs/source <outdir>` then open `<outdir>/user_guide/templates.html` (section on `/_typsphinx/deps.typ`)
States: empty — n/a (static page); loading — n/a; error — the export table still lists `codly-init` or codly 1.3.0, or the page has no migration note; success — the export table lists codly 2.0.0 exporting the module `codly` (`codly.new`, `codly.set_`, `codly.lang-set_`), the `typsphinx-init` paragraph says it registers `codly-languages` through `codly.lang-set_` and installs no raw→codly rule, and a migration note tells template authors what replaced `codly-init` and the state-style calls
Walkthrough:
1. Build the HTML docs and open the Templates page at the deps.typ contract section.
2. Read the export table row for codly: version 2.0.0, exported name `codly` as a module; no `codly-init` export.
3. Read the `typsphinx-init` paragraph and the migration note; confirm both match the generated `_typsphinx/deps.typ` of any build.
4. Open `CHANGELOG.md` `## [Unreleased]` and confirm the breaking-change entry with the migration note and the user-raw-block statement (E9).

## Intent coverage

| Criterion | Task | Acceptance |
|-----------|------|------------|
| SC1 | T001 | AC1 |
| SC2 | T002 | AC1 |
| SC3 | T002 | AC4 |
| SC4 | T002 | AC6 |
| SC5 | T003 | AC1 |
| SC6 | T001 | AC6 |
| SC7 | T003 | AC2 |
| SC8 | T003 | AC3 |
| SC9 | T003 | AC5 |

## Held-out checks

| Edge | Task | Test |
|------|------|------|
| E2 | T002 | tests/test_codly2_render_gate.py |
| E3 | T002 | tests/test_codly2_render_gate.py |
| E4 | T002 | tests/test_codly2_render_gate.py |
| E6 | T002 | tests/test_codly2_render_gate.py |
| E7 | T002 | tests/test_codly2_render_gate.py |

## Dependency notes

- T002 → T001 (data): T002's gates assert the deps.typ text and the `codly.new(raw(...), ...)` emission grammar defined in T001's Interface contract; they also share `typsphinx/translator.py` and `tests/test_translator.py`, which T002 may adjust only within that contract. A reviewer sees T002's tests assert the exact contract strings.
- T003 → T001, T002 (prerequisite effect): SC5 requires the examples and the project docs to compile against the codly 2.0 deps.typ and the final emission, including any emission correction T002 lands; SC9 is checked on the last landing of the milestone, which T003 is. A reviewer sees T003's recorded `tox -e docs-pdf` and examples builds ran on a base containing both landings.
- T003 does not depend on T001's docs content beyond the prerequisite effect above: `tox -e docs-pdf` compiles T001's rewritten templates.rst and CHANGELOG entry because T001 has landed.
- DOCS-AUDIT Remediation queue rows 1 (charged-ieee identical output, fix-code), 2 (advanced README seealso, fix-doc) and 3 (advanced README inline math, fix-doc) are folded into T003 as SC7 and SC8.
- LESSONS 001 (`.gitignore` `build/` vs `.project/`): `git check-ignore` matches none of this plan's new paths or `.project/plan|tasks`; no `.gitignore` change is planned.
- LESSONS 002 (absence criteria vs escaped body text) applies to SC2: CHANGELOG.md history already contains `` `{ codly(...) }` `` (line 912) and `` `#codly(number-format: none)` `` (line 1322); `docs/source/changelog.rst` includes CHANGELOG.md, so the docs/source content file `changelog.typ` carries them as inline `raw("...")` text and the literal `grep -rnE '(^|[^.a-z-])codly\('` over docs/source output can never return no match without rewriting released history (measured in a prior `docs/_build/pdf/changelog.typ`: `raw("{ codly(...) }")`, `raw("#codly(number-format: none)")`). T002 AC3 bounds the check to exempt exactly those inline literals quoting CHANGELOG.md. Owner ruling recorded as INTENT C5 (2026-11-03): exemption accepted (option a).
