# Synthesis

<!-- Quick lane: research and decide skipped (INTENT.md Lane: quick). Settled-only synthesis written by plan. -->

## Settled

- Scope — README.md is reduced to the section set in INTENT.md SC1–SC5; README-only information moves to docs/source in English (SC6), except the README Contributing content, which is deleted (C5); docs/source/contributing.rst may receive README-only Development items (C7); no release, no #194, no translation, no `typsphinx/` change (INTENT.md Scope out; C1–C7).
- Manual coverage — docs/source already states the template, `typst_template_mapping`, `add_node` third-party, multi-document, configuration, bibliography and Graphviz material, and contributing.rst already holds the tox environment list and setup steps; README-only Development items measured at plan time: the `typst_deps.py` Project Structure line, `uv run pytest --cov=typsphinx --cov-report=html`, and the `examples/basic/` / `examples/advanced/` testing note (plan measurement against c1606cd9; evidence-codebase.md Map).
- Manual wins on conflict — e.g. contributing.rst's existing structure diagram is left as is (INTENT.md SC6, E6; C7).
- Docs baseline — a clean `sphinx-build -b html docs/source <out>` at c1606cd9 emits 0 warnings (plan measurement, LC_ALL=C), so SC7 is checkable as `sphinx-build -W -E`.
- README-pinning tests — `tests/test_quickstart_docs_gate.py` (Quick Start + Configuration Options `typst_documents` prose), `tests/test_no_stale_github_io_links.py` (Documentation link set), `tests/test_readme_version_sync.py` and `tests/test_release_0_10_0_docs_gate.py` (Status line; the latter also asserts `[Unreleased]` holds only "Planned for Future Releases"), plus scanners that police README for forbidden text (`test_registry_documentation_gate.py`, `test_docs_template_layout_gate.py`, `test_bundle_layout_sweep_gate.py`) (plan measurement: `grep -l README tests/*.py`).
- Integration is pull-request mode; PR checks/merge/tag are not SCs (INTENT.md Constraints; LESSONS 001).

## For the planner

- **Wave-1 blockers**: none.
- **Walking skeleton**: T001 lands every README-only item in docs/source with its mapping table; T002 rewrites README against that table, updates README-pinning gates, adds the CHANGELOG bullet.
- **Pitfalls → tasks**: no literal triple-backtick in Verify (LESSONS 004); enumerate every test that asserts changed README/CHANGELOG text in T002 `files` (LESSONS 004); no index-reading checks (LESSONS 005); replace the DOCS-AUDIT `planned: no` with the task id (LESSONS 006); docs warning checks use clean builds (`-E`, fresh output dir).
