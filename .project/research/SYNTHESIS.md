# Synthesis

<!-- Quick lane: research and decide skipped (INTENT.md Lane: quick). Settled-only synthesis written by plan. -->

## Settled

- Scope — the three compile-breaking constructs of #194 (option list, classifier, productionlist) get dedicated visitors; `unknown_visit` gains a code-mode separator fallback that keeps the warning and the node text; README Requirements bounds (DOCS-AUDIT #1, #2 fix-doc); CHANGELOG `[Unreleased]` `### Fixed`; warning-only nodes, release and closing #194 are out (INTENT.md Scope in/out; owner rulings 1A, 2A, 3A, 7A, 8A).
- Rendering — option list as `terms(...)` with `raw` option strings, italic `raw` arguments, `, `-joined options and the docutils delimiter preserved; classifier inside its term as ` : ` + italic classifier in source order; productionlist as a monospace three-column (name, `::=`, rule) layout with continuation lines in the rule column and per-production anchors for `:token:` links (INTENT.md SC1–SC3; owner rulings 4A, 5A, 6A, 11A–13A).
- Failure mechanism — every content `.typ` body is one code-mode `#{ ... }` block; `unknown_visit` (typsphinx/translator.py:5804-5815) only warns and descends and `unknown_departure` (5817-5825) is a no-op, so juxtaposed child expressions give `expected semicolon or line break` (evidence-codebase.md Findings 1, 4).
- Classifier placement — `visit_term`/`depart_term` redirect `self.body` to a term buffer (translator.py:2784-2841); `classifier` is a sibling of `term` in `definition_list_item`, so its text currently lands in the outer body before `terms(...)` (evidence-codebase.md Finding 2). The term buffer uses the `_in_term` / `_term_has_content` `+`-concat context (`_CONCAT_CONTEXTS`, translator.py:1625-1632).
- Node classes — `sphinx.addnodes.productionlist` is an `Admonition`/`Body` element and `production` a `Part`/`Inline` element (plan measurement, `uv run python -c ...`).
- No regression — output of nodes with visitors stays byte-identical; no pre-existing expected-.typ assertion is edited; full suite, lint/type and a clean docs PDF build pass (INTENT.md SC5; owner ruling 9A).
- CHANGELOG pin — `tests/test_release_0_10_0_docs_gate.py::test_unreleased_holds_only_planned_for_future_releases` asserts `[Unreleased]` subsections are exactly `### Documentation`, `### Planned for Future Releases`; adding `### Fixed` must update that CHANGELOG (not .typ) assertion (plan measurement: `grep -ln Unreleased tests/*.py`).
- README pin — `tests/test_readme_structure_gate.py` pins README headings but no Requirements line text (plan measurement).
- `.gitignore` — `git check-ignore` matches no `.project/` plan, task or build path (plan measurement; LESSONS 001).
- Integration is pull-request; PR body `Refs #194`; PR checks/merge/issue state are not SCs (INTENT.md Constraints; LESSONS 001).

## For the planner

- **Wave-1 blockers**: none.
- **Walking skeleton**: T001 lands the three visitors, the fallback and their subprocess gate with fixtures, proven by `typstpdf` exit 0 plus pypdf text; T002 lands the README bounds and the CHANGELOG `### Fixed` entry with their gate updates.
- **Pitfalls → tasks**: no literal triple-backtick in Verify (LESSONS 004); enumerate every test asserting changed CHANGELOG/README text in T002 `files` (LESSONS 004); no index-reading checks in Verify (LESSONS 005); DOCS-AUDIT rows #1/#2 carry T002 as planned (LESSONS 006); warning-text assertions under `LC_ALL=C`.
