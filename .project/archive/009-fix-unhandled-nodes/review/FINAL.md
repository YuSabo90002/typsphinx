# Final Review — reused full wave

Reviewed HEAD: cd2225311f18986b2dc0e4d373766b010ffa5c00
Overall verdict: pass
Source review: .project/review/wave-1.cycle1.md
Source commit: a7f2dd20ce2dfde4802cb20d0473feb6e5ea3d52

## Success criteria

### SC1 — Option list (surface: typstpdf output): a fixture document with an option list builds with `sphinx-build -b typstpdf` at exit status 0 and no `unknown node type` warning for any option-list node (`option_list`, `option_list_item`, `option_group`, `option`, `option_string`, `option_argument`, `description`). The emitted .typ renders the list as `terms(...)`: each item's term holds its option strings in monospace (`raw`), each `option_argument` in italic monospace, multiple options of one group joined by `, `, and each option's argument delimiter preserved exactly as docutils records it (`-c FILE` keeps the space, `--see=FILE` keeps `=`); the description is the item body. The extracted PDF text (pypdf) contains every option string, argument and description. The fixture includes a single-item option list between two paragraphs, a multi-option group with arguments (`-c FILE, --see=FILE`), and a description containing `"`, `\` and `#`, each of which compiles and shows those characters literally in the PDF text.

- **Verdict**: met
- **Check**: `LC_ALL=C uv run python -m sphinx -b typstpdf -E tests/fixtures/unhandled_nodes_render_gate/option_list <mktemp outdir>`, read `<outdir>/index.typ`, pypdf `extract_text()` of `<outdir>/master.pdf` (walkthrough step 1)
- **Observed**: exit 0, empty warning log; `terms.item(raw("-c") + raw(" ") + emph(raw("FILE")) + text(", ") + raw("--see") + raw("=") + emph(raw("FILE")), ...)`; PDF lines `-c FILE, --see=FILE`, `Description with "quotes", back\slash and #hash.`, `-a` / `option a` between the two paragraphs
- **Reference**: .project/review/wave-1.cycle1.md — SC1; evidence: option_list fixture rc=0, no `unknown node type` warning; `terms(...)` with `raw` options, `emph(raw(...))` arguments, `text(", ")` join, `raw(" ")` / `raw("=")` delimiters, description as item body; PDF text has all options, arguments, descriptions and literal `"` `\` `#`. E1 (single item between paragraphs), E2 (`-c FILE, --see=FILE`), E3 (`"`, `\`, `#`) all observed. N3 dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: typstpdf / typst builder output (`sphinx-build -b typstpdf` / `-b typst`: emitted .typ and compiled PDF)

### SC2 — Classifier (surface: typstpdf output): a fixture definition list whose items carry classifiers builds with `typstpdf` at exit status 0 and no `unknown node type` warning for `classifier`. Each classifier is emitted inside its own `terms.item` term (not before the `terms(...)` call) as ` : ` followed by the classifier in italics; an item with several classifiers shows them in source order (`term : c1 : c2`); a classifier containing inline markup (`*emphasis*`, ``literal``) keeps that markup inside the term. The PDF text shows `term : c1 : c2` on the term line.

- **Verdict**: met
- **Check**: `LC_ALL=C uv run python -m sphinx -b typstpdf -E tests/fixtures/unhandled_nodes_render_gate/classifier <mktemp outdir>`, read index.typ, pypdf text (walkthrough step 2)
- **Observed**: exit 0, empty warning log; `terms.item(text("term") + text(" : ") + emph(text("c1")) + text(" : ") + emph(text("c2")), ...)`, no text before `terms(`; PDF lines `term : c1 : c2` and `marked : emphasis classifier : literal classifier`
- **Reference**: .project/review/wave-1.cycle1.md — SC2; evidence: classifier fixture rc=0, no warning; classifiers inside `terms.item` term as `text(" : ") + emph(...)` in source order (E4), inline `emph`/`raw` kept inside the term (E5); PDF term line `term : c1 : c2`. N4 dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: typstpdf / typst builder output (`sphinx-build -b typstpdf` / `-b typst`: emitted .typ and compiled PDF)

### SC3 — Productionlist (surface: typstpdf output): a fixture with `.. productionlist::` (including one with a group name, `.. productionlist:: grp`, and a production with several `|` continuation lines) builds with `typstpdf` at exit status 0 and no `unknown node type` warning for `productionlist` or `production`. The grammar is emitted as a monospace three-column layout (name, `::=`, rule) with continuation lines placed in the rule column under the first rule line; each production carries an anchor from its node ids so that a `:token:` reference in the same master document becomes a working PDF-internal link to that production; a `:token:` reference whose target does not resolve is emitted as plain text without a link, and the build still exits 0.

- **Verdict**: met
- **Check**: `LC_ALL=C uv run python -m sphinx -b typstpdf -E tests/fixtures/unhandled_nodes_render_gate/productionlist <mktemp outdir>`, read index.typ, pypdf text and page `/Annots` `/Link` destinations (walkthrough step 3)
- **Observed**: exit 0, empty warning log; PDF text `expr ::= term ("+" term)*` … `factor ::= NUMBER` / `| "(" expr ")"` / `| "-" factor` / `stmt ::= expr ";"`; paragraph links resolve to `/XYZ` y=762.8 (expr) and y=684.2 (stmt); `nosuchtoken` has no annotation
- **Reference**: .project/review/wave-1.cycle1.md — SC3; evidence: productionlist fixture rc=0, no warning; `grid(columns: 3, ...)` of `raw` name / `raw("::=")` / `raw` rule, continuations as `[], [], <rule>` (E6); `<index:grammar-token-*>` anchors; `:token:` refs are `link(<index:grammar-token-expr>, ...)` / `link(<index:grammar-token-grp-stmt>, ...)` whose PDF `/Link` annotations target the expr and stmt rows; unresolved `nosuchtoken` plain `raw`, no link, exit 0; group-named list compiles (E7). N5 dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: typstpdf / typst builder output (`sphinx-build -b typstpdf` / `-b typst`: emitted .typ and compiled PDF)

### SC4 — Generic fallback (surface: typstpdf output): for a node type without a visitor, `unknown_visit` still logs `unknown node type: ...` and still emits the node's text, and adds the separation needed so that juxtaposed children no longer produce `expected semicolon or line break`. A test-only visitor-less node with two inline children, placed in each of: a body paragraph, a list item, a table cell, and a heading / definition-list term, builds with `typstpdf` at exit status 0 in every placement, logs the warning, and the node's text appears in the extracted PDF text.

- **Verdict**: met
- **Check**: `LC_ALL=C uv run python -m sphinx -b typstpdf -E tests/fixtures/unhandled_nodes_render_gate/fallback <mktemp outdir>`, stderr grep `unknown node type`, pypdf text (walkthrough step 4)
- **Observed**: exit 0; 14 warnings; PDF shows `Heading with head-alpha head-beta`, `Body paragraph with para-alpha para-beta inside it.`, list items with `item-alpha item-beta` / `itemblock-alpha itemblock-beta`, cells `cell-alpha cell-beta` / `cellblock-alpha cellblock-beta` / `cellafter-alpha cellafter-beta`, `Term with term-alpha term-beta`, `defblock-alpha defblock-beta`
- **Reference**: .project/review/wave-1.cycle1.md — SC4; evidence: fallback fixture rc=0 with inline and block test-only nodes in heading, body paragraph, body level, list item, table cell, definition term and definition (E8); 14 `unknown node type` warnings, one per placement (N2: warning kept, `logger.warning` unchanged in `unknown_visit`); every `<word>-alpha`/`<word>-beta` text in PDF text (N1: no text dropped). Base translator emits juxtaposed `text("body-alpha ")raw("body-beta")text(...)`; HEAD newline-separates.
- **Finding**: none
- **Fix direction**: none
- **Surface**: typstpdf / typst builder output (`sphinx-build -b typstpdf` / `-b typst`: emitted .typ and compiled PDF)

### SC5 — No regression (surface: typstpdf output): output for nodes that already have visitors is byte-identical to a31fd6ca — no existing test's expected .typ string is edited (search space: `git diff a31fd6ca -- tests/` limited to pre-existing test files; check: no changed or removed assertion line about emitted .typ output; absent result: the diff touches existing test files only to add new tests or imports). On the final HEAD, `LC_ALL=C uv run pytest tests/` reports 0 failed, `black --check .`, `ruff check .`, `mypy typsphinx/` are clean, and a clean `tox -e docs-pdf` build (`rm -rf docs/_build` first) succeeds.

- **Verdict**: met
- **Check**: `git diff --diff-filter=M a31fd6ca HEAD -- tests/`; base-vs-HEAD `-b typst -E` builds of every tests/fixtures + tests/roots project and docs/source, `diff -rq` of outputs; recorded isolated Verify for suite/lint/docs (walkthrough step 5)
- **Observed**: no .typ assertion edits; all pre-existing outputs byte-identical; recorded Verify exit 0
- **Reference**: .project/review/wave-1.cycle1.md — SC5; evidence: Pre-existing test files changed vs a31fd6ca: tests/test_readme_structure_gate.py (one added test) and tests/test_release_0_10_0_docs_gate.py (CHANGELOG-subsection assertions only) — no emitted-.typ assertion changed or removed. Byte-identity: a31fd6ca vs HEAD translator over 189 fixture/root projects + docs/source with `-b typst -E`: identical exit codes in 190 builds, 795 .typ each, only the four new M009 fixtures differ — no node with a visitor changed output (E9). Output change is confined to visitor-less nodes in bare statement contexts (`unknown_visit` returns early in paragraph / list item / markup / concat contexts), permitted by ruling 9A. Full suite / black / ruff / mypy / clean docs typstpdf: T001 orchestrator isolated Verify exit 0 (1926 passed, 1 skipped per coder log; "build succeeded" in tail) and T002 ledger exit 0 on disjoint files; final-HEAD project Verify runs once at ship via `prepare-final`. N6 dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: typstpdf / typst builder output (`sphinx-build -b typstpdf` / `-b typst`: emitted .typ and compiled PDF)

### SC6 — README bounds (surface: README.md): `## Requirements` states "Sphinx 9.1 or higher (below 10)" and states the typst-py upper bound `<0.16` (e.g. "typst-py 0.15.0 or higher (below 0.16)"), matching pyproject.toml:29,31; no other README line changes.

- **Verdict**: met
- **Check**: read `## Requirements` and compare with pyproject.toml:29,31; `git diff a31fd6ca HEAD -- README.md`
- **Observed**: one hunk, 2 lines removed / 2 added, exactly the two bound lines
- **Reference**: .project/review/wave-1.cycle1.md — SC6; evidence: README.md diff vs a31fd6ca changes only the two Requirements lines to `Sphinx 9.1 or higher (below 10)` and `typst-py 0.15.0 or higher (below 0.16)`, matching pyproject.toml:29,31. E10, N7 dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: README.md (as rendered on GitHub)

### SC7 — CHANGELOG (surface: CHANGELOG.md): `## [Unreleased]` gains a `### Fixed` section with an entry stating that option lists, definition-list classifiers and productionlists now render in Typst/PDF output instead of failing the PDF compile (referencing #194), and that visitor-less nodes no longer break compilation; the existing `### Documentation` bullet and every other existing CHANGELOG line are unchanged.

- **Verdict**: met
- **Check**: read `## [Unreleased]`; `git diff a31fd6ca HEAD -- CHANGELOG.md`
- **Observed**: `### Fixed` at CHANGELOG.md:10 above `### Documentation`; add-only hunk
- **Reference**: .project/review/wave-1.cycle1.md — SC7; evidence: CHANGELOG.md diff vs a31fd6ca is 7 added lines, no removals: `### Fixed` + one entry naming option lists, definition-list classifiers, productionlists, #194 link and "A node type without a Typst visitor no longer breaks compilation"; `### Documentation` bullet untouched; `test_unreleased_fixed_records_issue_194` PASSED (ledger). E11, N8 dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: CHANGELOG.md
