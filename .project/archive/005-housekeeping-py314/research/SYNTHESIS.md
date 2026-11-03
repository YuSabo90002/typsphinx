# Synthesis

<!-- Quick lane: research and decide skipped (INTENT.md Lane: quick). Settled-only synthesis written by plan. -->

## Settled

- Scope — housekeeping only: CLAUDE.md text, deletion of the three gsd-pi evidence files and their gate checks, Python 3.14 declaration, three fix-doc README/CHANGELOG edits; no product code, no release (INTENT.md Scope: in / Scope: out, owner rulings C1 "3" and C2 "Q1 a  Q2 a  Q3 a  4-1 fix-doc  4-2 fix-doc  4-3 fix-doc").
- CLAUDE.md content — three undocumented modules `typsphinx/template_registry.py`, `typsphinx/removed_config.py`, `typsphinx/pathfmt.py`; 142 test files run Sphinx via `subprocess`/`sys.executable`, one uses `rootdir`; `tests/roots/` holds only `test-basic`; CI test job matrix is ubuntu/windows/macos (`.project/research/evidence-codebase.md` findings; `.github/workflows/ci.yml:13-23`).
- Evidence-file coupling — only `tests/test_release_0_9_8_docs_gate.py` reads the files (`S03`/`S04` constants at lines 34-35; `test_audit_9_s03_has_correction_citing_ci_run`, `test_audit_10_s04_has_post_merge_results`); a repository grep at 660e3436 found no other non-archive reader (define measurement).
- CHANGELOG Planned heading — `### Planned for Future Releases` keeps three items after removing "Glossary generation", so the heading stays; `tests/test_release_0_9_8_docs_gate.py::test_first_unreleased_keeps_planned_for_future_releases` and `tests/test_deps_contract_docs_gate.py::test_changelog_unreleased_records_the_change` require it (define measurement of CHANGELOG.md:84-88).
- Python 3.14 entries — classifiers `pyproject.toml:21-22`, black `target-version` `pyproject.toml:111`, CI matrix `.github/workflows/ci.yml:18-23`, tox `env_list` `tox.ini:2`; ruff `target-version`, mypy `python_version` and `requires-python` stay at 3.12 (INTENT.md Scope: out).
- Full suite passes on uv-managed CPython 3.14 at 660e3436 (1883 passed, 1 skipped; `.project/research/evidence-codebase.md`).

## For the planner

- **Wave-1 blockers**: none; the two slices touch disjoint files.
- **Walking skeleton**: T001 docs/evidence housekeeping; T002 Python 3.14 declaration proven by `uv run tox -e py314`.
- **Pitfalls → tasks**: keep the tox-uv pin text in CLAUDE.md consistent with `tests/test_toolchain_config_gate.py` (T001); do not edit released CHANGELOG sections (T001); black may reject `py314` — the Verify runs `black --check .` (T002); run warning-text tests under `LC_ALL=C`.
