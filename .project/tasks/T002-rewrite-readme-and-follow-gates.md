---
id: T002
title: Rewrite README.md to the approved shape, update its gates, add the CHANGELOG bullet
wave: 1
deps: [T001]
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - README.md
  - CHANGELOG.md
  - tests/test_readme_structure_gate.py
  - tests/test_quickstart_docs_gate.py
  - tests/test_no_stale_github_io_links.py
  - tests/test_readme_version_sync.py
  - tests/test_release_0_10_0_docs_gate.py
  - tests/test_registry_documentation_gate.py
  - tests/test_docs_template_layout_gate.py
  - tests/test_bundle_layout_sweep_gate.py
  - tests/test_bibliography_docs_gate.py
  - tests/test_deps_contract_docs_gate.py
---

# T002 — Rewrite README.md to the approved shape, update its gates, add the CHANGELOG bullet

## Context

The owner wants README.md (348 lines at c1606cd9) back to a simple shape with details left to the manual (INTENT.md Summary, C1–C5). T001 has already added every README-only item to docs/source (its landed docs/source changes are in this task's base). This task rewrites README.md to exactly the sections in SC1 (Overview, Features, Requirements, Installation, Quick Start, Documentation, Contributing, License, Acknowledgments, Version History), applies SC2–SC5, switches the development credit from gsd-core to GSD Path (DOCS-AUDIT queue #1, fix-doc), adds diagraph and typst-py credits (C3), adds a Graphviz Features bullet (C3) and a feature-only bibliography bullet (C4), deletes Contributing content (C5), and adds one `[Unreleased]` CHANGELOG bullet (SC8). README-pinning tests are updated to the new README, never deleted (SC9).

## Approach

- Keep above `## Overview`: the badges, the one-line description, and the Documentation | Issue Tracker | PyPI link line (SC1).
- Installation keeps the `pip install typsphinx` block and the uv block (clone, `uv sync`, `uv sync --extra dev`). Quick Start subsections are exactly `### Basic Configuration` (minimal conf.py, no `#### typst_documents`), `### Build Typst Output` (`sphinx-build -b typst` and `sphinx-build -b typstpdf`), `### Example Document` (SC2).
- Features: one physical line per bullet, no sub-bullets, no `@preview/` text; bibliography bullet states only that plain rST citations and sphinxcontrib-bibtex `:cite:` / `.. bibliography::` render, with a link to the bibliography user guide, and no `pybtex`/`CSL`/`#bibliography` text; a Graphviz bullet states `.. graphviz::` / `.. digraph::` / `.. graph::` DOT diagrams compile into Typst/PDF without a Graphviz installation, linking to the diagrams user guide (SC3). Use Read the Docs URLs consistent with the Documentation section's existing link style.
- `## Contributing`: only a link to the contributing guide. `## Version History`: a link to CHANGELOG.md. Keep the trailing `---`, `**Status**: Stable (v0.10.0) - Production ready` and the Python/Sphinx/Typst line (SC4).
- `## Acknowledgments`: keep Sphinx, Typst, mitex, codly, gentle-clues; add diagraph (`https://typst.app/universe/package/diagraph`, renders Graphviz diagrams) and typst-py (`https://github.com/messense/typst-py`, performs the Typst compilation; confirm the URL resolves to the typst-py project before using it); development credit links GSD Path `https://github.com/open-gsd/gsd-path`; no `gsd-core` anywhere (SC5, prohibition N1).
- Every informational item you delete from README must already be stated in docs/source (T001 added the README-only ones), or be README Contributing content (C5). Append to this task's Log a Markdown table `| # | README item (base line) | Docs location (file § section) | Status |`, Status ∈ {`already in manual`, `added by T001`, `deleted per C5`}, covering every deleted item; if an item has no docs home, stop with `NEEDS-ORCHESTRATOR` rather than dropping it (SC6, E7).
- CHANGELOG: add exactly one bullet under `## [Unreleased]` (e.g. a `### Documentation` or `### Changed` subsection) saying README was simplified and details moved to the manual; change no other line (SC8). `tests/test_release_0_10_0_docs_gate.py::test_unreleased_holds_only_planned_for_future_releases` asserts the old shape — update it to allow the new bullet while still asserting "Planned for Future Releases" stays.
- Update every gate that asserts removed README text (notably `tests/test_quickstart_docs_gate.py`'s README Quick Start / Configuration Options checks) to the new README; keep `tests/test_readme_version_sync.py` and `tests/test_no_stale_github_io_links.py` asserting the Status line and the Documentation link set (SC9). Add `tests/test_readme_structure_gate.py` pinning SC1–SC5 (exact `## ` heading list and order, Quick Start subsections, single-line Features with zero `@preview/`, zero `gsd-core`, the credit names, zero `pybtex|CSL|#bibliography`).
- English, terse. No `typsphinx/` change, no version bump, no tag (scope out). Do not edit docs/source (T001 owns it).

## Interface contract

- None

## Intent coverage

- SC1
- SC2
- SC3
- SC4
- SC5
- SC8
- SC9

## Acceptance criteria

1. `grep '^## ' README.md` outputs exactly `## Overview`, `## Features`, `## Requirements`, `## Installation`, `## Quick Start`, `## Documentation`, `## Contributing`, `## License`, `## Acknowledgments`, `## Version History`, in that order (E1); badges, description and the top link line remain.
2. Installation has the pip and uv blocks; Quick Start has exactly Basic Configuration (minimal conf.py, no `#### typst_documents`), Build Typst Output (`-b typst` and `-b typstpdf`), Example Document.
3. Every Features bullet is one physical line with no nested bullet (E3); the bibliography bullet is feature-only with a guide link; the Graphviz bullet exists with a diagrams-guide link; `grep -c '@preview/' README.md` and `grep -c -i -E 'pybtex|CSL|#bibliography' README.md` print `0`.
4. Contributing is a link only; Version History links CHANGELOG.md; the file ends with the Status line and the Python/Sphinx/Typst line.
5. Acknowledgments credits Sphinx, Typst, mitex, codly, gentle-clues, diagraph, typst-py, and GSD Path (`https://github.com/open-gsd/gsd-path`); `grep -c 'gsd-core' README.md` prints `0`.
6. `## [Unreleased]` has one new bullet about the README simplification; no other CHANGELOG line changed.
7. Full suite 0 failed, black/ruff/mypy clean; README-pinning gates updated not deleted, `tests/test_readme_structure_gate.py` added; Log holds the removed-item → docs location table covering every deleted README item.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && test "$(grep '^## ' README.md | tr '\n' '|')" = "## Overview|## Features|## Requirements|## Installation|## Quick Start|## Documentation|## Contributing|## License|## Acknowledgments|## Version History|" && test "$(grep -c '@preview/' README.md)" = 0 && test "$(grep -c 'gsd-core' README.md)" = 0 && grep -q 'open-gsd/gsd-path' README.md && grep -q 'diagraph' README.md && grep -q 'typst-py' README.md && LC_ALL=C uv run pytest tests/test_readme_structure_gate.py tests/test_quickstart_docs_gate.py tests/test_no_stale_github_io_links.py tests/test_readme_version_sync.py tests/test_release_0_10_0_docs_gate.py -o addopts="" -q && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/
```

Heavy: yes

## Log

- 2026-11-04 — created by plan (quick mode)
