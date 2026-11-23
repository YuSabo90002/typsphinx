---
id: T002
title: State README dependency upper bounds and add the CHANGELOG Fixed entry
wave: 1
deps: []
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - README.md
  - CHANGELOG.md
  - tests/test_readme_structure_gate.py
  - tests/test_release_0_10_0_docs_gate.py
---

# T002 — State README dependency upper bounds and add the CHANGELOG Fixed entry

## Context

DOCS-AUDIT queue #1 and #2 (owner ruling `fix-doc`, "3: A"): README.md:35 says "Sphinx 9.1 or higher" while pyproject.toml:29 pins `"sphinx>=9.1,<10"`, and README.md:36 says "typst-py 0.15.0 or higher" while pyproject.toml:31 pins `"typst>=0.15.0,<0.16"`; docs/source/installation.rst:8 and the example READMEs already say "(below 10)". M009 also fixes issue #194 in T001 (option lists, definition-list classifiers and productionlists no longer fail the PDF compile; visitor-less nodes no longer break compilation), and that user-visible fix needs a CHANGELOG `[Unreleased]` `### Fixed` entry (LESSONS 006). `tests/test_release_0_10_0_docs_gate.py::test_unreleased_holds_only_planned_for_future_releases` currently asserts the `[Unreleased]` subsections are exactly `### Documentation` and `### Planned for Future Releases`, so it must be updated to admit `### Fixed`. `tests/test_readme_structure_gate.py` pins README headings but no Requirements text.

## Approach

- README `## Requirements`: "Sphinx 9.1 or higher (below 10)" and "typst-py 0.15.0 or higher (below 0.16)"; change no other README line (SC6).
- CHANGELOG `## [Unreleased]`: add a `### Fixed` section (Keep a Changelog order, before or after `### Documentation` consistently with the file's existing sections; above `### Planned for Future Releases`) with an entry saying option lists, definition-list classifiers and productionlists now render in Typst/PDF output instead of failing the PDF compile (#194), and that nodes without a Typst visitor no longer break compilation (they still warn). Leave every existing CHANGELOG line unchanged, including the link block (SC7).
- Update `test_unreleased_holds_only_planned_for_future_releases` to the new subsection set while still asserting the `### Documentation` README bullet; add a README Requirements assertion (both bounds) to `tests/test_readme_structure_gate.py`, and a `### Fixed` entry assertion (mentions #194) in the release gate or the README gate module.
- Do not touch `typsphinx/` or any T001 path. No version bump (veto).

## Interface contract

- None

## Intent coverage

- SC6
- SC7

## Acceptance criteria

1. SC6: README `## Requirements` states "Sphinx 9.1 or higher (below 10)" and "typst-py 0.15.0 or higher (below 0.16)"; `git diff a31fd6ca -- README.md` changes only those two lines; `tests/test_readme_structure_gate.py` asserts both bounds.
2. SC7: CHANGELOG `## [Unreleased]` has a `### Fixed` entry naming option lists, definition-list classifiers, productionlists and #194, plus the visitor-less-node fallback; `git diff a31fd6ca -- CHANGELOG.md` shows only added lines in `[Unreleased]`; the updated release gate passes and still asserts the `### Documentation` bullet.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev && LC_ALL=C uv run pytest tests/test_readme_structure_gate.py tests/test_release_0_10_0_docs_gate.py tests/test_release_0_9_8_docs_gate.py tests/test_changelog_extraction.py tests/test_deps_contract_docs_gate.py tests/test_readme_version_sync.py -v && grep -F 'Sphinx 9.1 or higher (below 10)' README.md && grep -F '0.15.0 or higher (below 0.16)' README.md && grep -n '^### Fixed' CHANGELOG.md && uv run black --check tests/ && uv run ruff check tests/
```

Heavy: no

## Log

- 2026-11-23 — created by plan (quick lane, orchestrator-written)
