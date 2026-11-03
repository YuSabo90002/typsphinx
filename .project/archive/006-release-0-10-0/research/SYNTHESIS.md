# Synthesis

<!-- Quick lane: research and decide skipped (INTENT.md Lane: quick). Settled-only synthesis written by plan. -->

## Settled

- Scope — release prep for 0.10.0 plus three docs-audit fixes; no tag push, no product code (INTENT.md Scope: in / Scope: out; owner rulings C1 "2", C2 "Q1 a  Q2 a  Q3 a  Q4 a").
- Version sites — `pyproject.toml:7`, `README.md:345` status line, and the project's own `version` entry in `uv.lock` (`name = "typsphinx"` at line ~1601); `docs/source/conf.py` reads the version from pyproject (define measurement).
- CHANGELOG conventions — the release heading date is the release-prep commit date (`tests/test_release_0_9_8_docs_gate.py::test_0_9_8_date_is_release_prep_commit_date` pattern); Unreleased keeps only `### Planned for Future Releases` (required by `test_first_unreleased_keeps_planned_for_future_releases`); the 0.9.8 section opens with a lead paragraph (CHANGELOG.md:89-96); `scripts/extract_changelog_section.py` extracts a version section.
- Tests tied to the moved content — `tests/test_release_0_9_8_docs_gate.py::test_link_block_targets_v0_9_8` asserts `[Unreleased]` compares `v0.9.8...HEAD`; `tests/test_deps_contract_docs_gate.py::_unreleased_section` with `test_changelog_unreleased_records_the_change` and `test_changelog_unreleased_records_the_codly_2_breaking_change` read the M002/M004 entries from `## [Unreleased]` (define measurement).
- charged-ieee abstract — approach1 passes a triple-quoted multi-line Python string `ieee_abstract` (`examples/charged-ieee/approach1/conf.py:26-28`) whose embedded newlines differ from approach2's Typst content block `let ieee_abstract = [...]` (`examples/charged-ieee/approach2/source/_typst/_template.typ:37`); DOCS-AUDIT #1 ruled fix-code.
- "sphinx-typst" occurs at examples/charged-ieee/README.md lines 3, 7, 150 (DOCS-AUDIT #2); `## [0.1.0b1]` precedes `## [0.2.0]` in CHANGELOG.md (DOCS-AUDIT #3).

## For the planner

- **Wave-1 blockers**: none; T001 (release metadata + CHANGELOG + gate tests) and T002 (charged-ieee) touch disjoint files.
- **Walking skeleton**: T001 proven by `extract_changelog_section.py 0.10.0`, `uv build` + `twine check`; T002 proven by building both charged-ieee approaches and comparing abstract text.
- **Pitfalls → tasks**: never write a literal triple-backtick in a Verify (LESSONS 004); no index-reading checks in a task Verify (LESSONS 005); keep `### Planned for Future Releases` under Unreleased (T001); repoint, do not delete, the deps-contract changelog assertions (T001).
