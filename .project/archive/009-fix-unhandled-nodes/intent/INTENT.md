# Intent — typsphinx

Lane: quick   <!-- two deliverable-sized tasks in one wave (T: translator visitors for option list / classifier / productionlist + unknown_visit separator fallback + tests + CHANGELOG Fixed entry; T: README requirement bounds); all rendering and scope choices ruled by the owner, no RESEARCH or NEEDS-USER items; the two tasks share no file and no cross-wave risk -->

Review panel: off

Finding skeptics: off

Surfaces: typstpdf / typst builder output (`sphinx-build -b typstpdf` / `-b typst`: emitted .typ and compiled PDF), README.md (as rendered on GitHub), CHANGELOG.md

## Summary

Issue #194: at v0.10.0 (HEAD a31fd6ca) any document containing an rST option list, a definition-list classifier, or a Sphinx `productionlist` makes `sphinx-build -b typstpdf` fail with `TypstError: expected semicolon or line break`, because these nodes have no visitor and `unknown_visit` only warns and descends, so their children are juxtaposed in the code-mode body. M009 adds dedicated visitors that render the three constructs properly — option lists as `terms(...)` with monospace options and italic monospace arguments, classifiers as `term : classifier` in italics inside the term, productionlists as an aligned three-column monospace grammar with anchors that `:token:` references link to — and makes `unknown_visit` emit a separator so that a visitor-less node can no longer break compilation, while keeping its `unknown node type` warning and its text. Existing output for already-supported nodes stays byte-identical. README's Requirements gain the Sphinx `<10` and typst-py `<0.16` upper bounds, and CHANGELOG `[Unreleased]` gains a `### Fixed` entry. The warning-only nodes from #194's Additional Context (hlist, sidebar, centered, acks, PEP 695 type parameters) stay out; no release in this milestone.

## Problem

- `typstpdf` exits 2 on option lists (a single option between two paragraphs is enough), classifiers and productionlists (evidence-codebase.md, probes `optlist`, `classifier`, `prod`, `mixed`; issue #194). The whole master document fails, not just the construct.
- Classifier text is emitted outside and before the `terms(...)` call (translator.py:2784-2830), so a separator-only fix would compile but misplace it.
- `unknown_visit` (translator.py:5804-5825) has no code-mode safety net, so any future visitor-less node with two inline children reproduces the same fatal error.
- No test or docs page uses these constructs, so neither the suite nor `tox -e docs-pdf` catches a regression.
- DOCS-AUDIT queue #1/#2: README.md:35-36 omit the `<10` (Sphinx) and `<0.16` (typst-py) upper bounds stated in pyproject.toml:29,31.

## Users

Sphinx users building PDF/Typst output with typsphinx whose sources use option lists (CLI docs), classifiers (API/glossary docs) or productionlists (grammar docs) — including the #194 reporter; README readers checking supported versions.

## Success criteria

1. Option list (surface: typstpdf output): a fixture document with an option list builds with `sphinx-build -b typstpdf` at exit status 0 and no `unknown node type` warning for any option-list node (`option_list`, `option_list_item`, `option_group`, `option`, `option_string`, `option_argument`, `description`). The emitted .typ renders the list as `terms(...)`: each item's term holds its option strings in monospace (`raw`), each `option_argument` in italic monospace, multiple options of one group joined by `, `, and each option's argument delimiter preserved exactly as docutils records it (`-c FILE` keeps the space, `--see=FILE` keeps `=`); the description is the item body. The extracted PDF text (pypdf) contains every option string, argument and description. The fixture includes a single-item option list between two paragraphs, a multi-option group with arguments (`-c FILE, --see=FILE`), and a description containing `"`, `\` and `#`, each of which compiles and shows those characters literally in the PDF text.
2. Classifier (surface: typstpdf output): a fixture definition list whose items carry classifiers builds with `typstpdf` at exit status 0 and no `unknown node type` warning for `classifier`. Each classifier is emitted inside its own `terms.item` term (not before the `terms(...)` call) as ` : ` followed by the classifier in italics; an item with several classifiers shows them in source order (`term : c1 : c2`); a classifier containing inline markup (`*emphasis*`, ``literal``) keeps that markup inside the term. The PDF text shows `term : c1 : c2` on the term line.
3. Productionlist (surface: typstpdf output): a fixture with `.. productionlist::` (including one with a group name, `.. productionlist:: grp`, and a production with several `|` continuation lines) builds with `typstpdf` at exit status 0 and no `unknown node type` warning for `productionlist` or `production`. The grammar is emitted as a monospace three-column layout (name, `::=`, rule) with continuation lines placed in the rule column under the first rule line; each production carries an anchor from its node ids so that a `:token:` reference in the same master document becomes a working PDF-internal link to that production; a `:token:` reference whose target does not resolve is emitted as plain text without a link, and the build still exits 0.
4. Generic fallback (surface: typstpdf output): for a node type without a visitor, `unknown_visit` still logs `unknown node type: ...` and still emits the node's text, and adds the separation needed so that juxtaposed children no longer produce `expected semicolon or line break`. A test-only visitor-less node with two inline children, placed in each of: a body paragraph, a list item, a table cell, and a heading / definition-list term, builds with `typstpdf` at exit status 0 in every placement, logs the warning, and the node's text appears in the extracted PDF text.
5. No regression (surface: typstpdf output): output for nodes that already have visitors is byte-identical to a31fd6ca — no existing test's expected .typ string is edited (search space: `git diff a31fd6ca -- tests/` limited to pre-existing test files; check: no changed or removed assertion line about emitted .typ output; absent result: the diff touches existing test files only to add new tests or imports). On the final HEAD, `LC_ALL=C uv run pytest tests/` reports 0 failed, `black --check .`, `ruff check .`, `mypy typsphinx/` are clean, and a clean `tox -e docs-pdf` build (`rm -rf docs/_build` first) succeeds.
6. README bounds (surface: README.md): `## Requirements` states "Sphinx 9.1 or higher (below 10)" and states the typst-py upper bound `<0.16` (e.g. "typst-py 0.15.0 or higher (below 0.16)"), matching pyproject.toml:29,31; no other README line changes.
7. CHANGELOG (surface: CHANGELOG.md): `## [Unreleased]` gains a `### Fixed` section with an entry stating that option lists, definition-list classifiers and productionlists now render in Typst/PDF output instead of failing the PDF compile (referencing #194), and that visitor-less nodes no longer break compilation; the existing `### Documentation` bullet and every other existing CHANGELOG line are unchanged.

## Edge coverage

| Edge | Criterion | Category | Disposition | Detail |
|------|-----------|----------|-------------|--------|
| E1 | SC1 | empty | criterion SC1 | single-item option list between two paragraphs compiles (owner ruling 11A; the `mixed` probe reproducer) |
| E2 | SC1 | adjacency | criterion SC1 | multi-option group `-c FILE, --see=FILE`: options joined by `, `, docutils delimiter (space or `=`) preserved (owner ruling 11A) |
| E3 | SC1 | encoding | criterion SC1 | description with `"`, `\`, `#` compiles and shows them literally (owner ruling 11A) |
| E4 | SC2 | ordering | criterion SC2 | several classifiers keep source order: `term : c1 : c2` (owner ruling 12A) |
| E5 | SC2 | adjacency | criterion SC2 | inline markup inside a classifier stays inside the term (owner ruling 12A) |
| E6 | SC3 | adjacency | criterion SC3 | several `|` continuation lines sit in the rule column (owner ruling 13A) |
| E7 | SC3 | empty | criterion SC3 | unresolved `:token:` → plain text, no link, build exits 0; group-named productionlist compiles (owner ruling 13A) |
| E8 | SC4 | adjacency | criterion SC4 | fallback must compile in paragraph, list item, table cell, heading/term placements (owner ruling 10A) |
| E9 | SC5 | boundary | criterion SC5 | output may change only for visitor-less nodes; existing expected .typ untouched; docs-pdf must pass (owner ruling 9A) |
| E10 | SC6 | none | dismissed | fixed README text; no data shape |
| E11 | SC7 | none | dismissed | fixed CHANGELOG entry; no data shape |

## Prohibitions

| Prohibition | Criterion | Must not | Disposition | Detail |
|-------------|-----------|----------|-------------|--------|
| N1 | SC4 | silently drop an unknown node's text so readers lose content without noticing | criterion SC4 | owner ruling 14A: the node's text must appear in the PDF text and the warning must still be logged |
| N2 | SC4 | silence or downgrade the `unknown node type` warning, hiding unsupported nodes from users | criterion SC4 | owner ruling 7A: the warning stays |
| N3 | SC1 | none | dismissed | rendering layout of option lists; content preservation is already stated in SC1 (every option, argument and description in the PDF text); no values, safety, privacy, fairness or transparency stake |
| N4 | SC2 | none | dismissed | rendering layout of classifiers; no values, safety, privacy, fairness or transparency stake |
| N5 | SC3 | none | dismissed | rendering layout and internal links of grammars; no values, safety, privacy, fairness or transparency stake |
| N6 | SC5 | none | dismissed | regression and tooling checks; no person-facing stake beyond the output pinned by SC5 |
| N7 | SC6 | none | dismissed | fixed version-bound text copied from pyproject.toml |
| N8 | SC7 | none | dismissed | fixed CHANGELOG entry |

## Scope: in

- Dedicated visitors for option list nodes (`option_list`, `option_list_item`, `option_group`, `option`, `option_string`, `option_argument`, `description`), `classifier`, and `productionlist` / `production`, rendering as ruled in SC1–SC3 (owner rulings 4A, 5A, 6A).
- `unknown_visit` code-mode separator fallback that keeps the warning and the text (owner rulings 2A, 7A).
- Subprocess gate tests with fixtures under `tests/fixtures/` for SC1–SC4.
- README Requirements upper bounds (DOCS-AUDIT #1, #2; owner ruling 3A `fix-doc`).
- CHANGELOG `[Unreleased]` `### Fixed` entry.

## Scope: out (vetoes)

- Warning-only nodes from #194's Additional Context — `hlist`/`hlistcol`, `sidebar` (including its title-as-heading effect), `centered`, `acks`, PEP 695 `desc_type_parameter_list`/`desc_type_parameter` — owner ruling 1A: only the three compile-breaking constructs.
- Version bump / release 0.10.1 — owner ruling 8A: release in a separate milestone, like M006.
- Closing #194 — owner ruling 8A: PR body says `Refs #194`, the issue stays open for the remaining nodes.
- Removing or downgrading the `unknown node type` warning — owner ruling 7A.
- Do not break: byte-identical output for every node that already has a visitor (owner ruling 9A); the `/_typsphinx/deps.typ` public contract and `@preview` single-source rule (CLAUDE.md).

## Constraints

- Python 3.12+, builtin generics, black line length 88, ruff `N802` visitor naming (CLAUDE.md).
- New integration tests follow the subprocess-gate convention (`tests/test_*_gate.py` building a fixture with `sys.executable -m sphinx`); PDF text checks use pypdf (dev extra `pypdf>=6.14,<7`).
- Tests asserting warning text are run under `LC_ALL=C` (CI runs in English).
- Worktree executions provision with `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and run via `uv run` (CLAUDE.md).
- Integration is pull-request (STATE); the PR body uses `Refs #194`, not a closing keyword. PR checks, merge and issue updates are not success criteria (LESSONS 001).
- Folded DOCS-AUDIT rulings #1/#2 get their task id in place of `planned: no` when the task is written (LESSONS 006).

## Current state (brownfield only)

- **What exists**: typsphinx 0.10.0, a Sphinx extension (Python ≥3.12, Sphinx ≥9.1,<10, docutils ≥0.21,<0.23, typst-py ≥0.15,<0.16) with `typst`/`typstpdf` builders; builder → writer → translator (translator.py, 8078 lines, 189 visit/depart methods) → template engine; each content `.typ` body is one code-mode `#{ ... }` block. Suite 1908 passed / 1 skipped on CPython 3.14; black/ruff/mypy clean; CI ubuntu/windows/macos × 3.12–3.14. No product-code change since M004.
- **Must not break**: output of every node that already has a visitor (byte-identical; ruling 9A); the `unknown node type` warning (ruling 7A); the `deps.typ` contract.
- **Doc-vs-code rulings**: DOCS-AUDIT #1 README "Sphinx 9.1 or higher" → fix-doc ("3: A"); #2 README "typst-py 0.15.0 or higher" → fix-doc ("3: A").
- **Ground truth**: `.project/research/evidence-codebase.md`, `.project/research/DOCS-AUDIT.md`

## Risks

- The generic fallback separator could change bytes for nodes that currently compile (e.g. visitor-less nodes inside contexts whose own separator flags already handle them); SC5 pins that existing expected output stays unchanged.
- Classifier routing into the term buffer interacts with the definition-list frame (`visit_term`/`depart_term` body redirection, translator.py:2764-2830).
- `:token:` link resolution depends on productionlist anchors being emitted in a label form the existing reference visitor resolves.

## Open questions

- none

## Corrections

<!-- Verbatim user corrections from playback and later phases. Append-only. -->
