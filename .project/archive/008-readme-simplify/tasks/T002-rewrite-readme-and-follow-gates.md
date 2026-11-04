---
id: T002
title: Rewrite README.md to the approved shape, update its gates, add the CHANGELOG bullet
wave: 1
deps: [T001]
status: done
agent: build_T002
base: aced58a96f273064c8f5ce5bec619387c03f21f4
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
- 2026-11-04 — build_T002 (coder): README.md rewritten (348 → 164 lines) to the SC1 heading list; kept preamble, Overview, Requirements, Installation (pip + uv), Basic Configuration (minimal conf.py), Build Typst Output, Example Document, Documentation section (unchanged, incl. ja line and 8 quick links), License, Version History, Status lines. Features one line per bullet; added Graphviz bullet (link `/en/latest/user_guide/diagrams.html`) and feature-only bibliography bullet (link `/en/latest/user_guide/bibliography.html`); both URLs and `/en/latest/contributing.html` return 200. Acknowledgments adds diagraph and typst-py; credit switched to GSD Path (`https://github.com/open-gsd/gsd-path`, 200). typst-py URL confirmed: `gh repo view messense/typst-py` → "typst-py", "Python binding to typst". CHANGELOG: one `### Documentation` bullet under `[Unreleased]`. Gates: added tests/test_readme_structure_gate.py (SC1–SC5); tests/test_quickstart_docs_gate.py README-Quick-Start typst_documents check now asserts quickstart.rst names typst_documents and README Quick Start has exactly the three subsections and no `#### typst_documents`; tests/test_no_stale_github_io_links.py 8-in-order deep-link check scoped to `## Documentation` (plus every README `/en/` link must be `/en/latest/`); tests/test_release_0_10_0_docs_gate.py Unreleased check allows exactly the new bullet and still requires Planned for Future Releases. Other declared gates (registry, template layout, bundle sweep, bibliography, deps contract) needed no change (only forbid text; still pass).
  Removed-item → docs location table (base = README.md@c1606cd9, identical at aced58a9):

  | # | README item (base line) | Docs location (file § section) | Status |
  |---|---|---|---|
  | 1 | Features mitex `@preview/mitex:0.2.7` (23) | user_guide/templates.rst § Package Dependencies (table: mitex 0.2.7) | already in manual |
  | 2 | Features codly `@preview/codly:2.0.0` (25) | user_guide/templates.rst § Package Dependencies / `deps.typ` (`@preview/codly:2.0.0`) | already in manual |
  | 3 | Features codly sub-bullets: `:linenos:`, multiple languages, highlight lines (26–28) | index.rst § Key Features (Code Highlighting sub-bullets) | added by T001 |
  | 4 | Features bibliography: plain `[Ref]_` citations render (34) | index.rst § Key Features; user_guide/bibliography.rst § Plain reStructuredText Citations | added by T001 |
  | 5 | Features bibliography: install/enable sphinxcontrib-bibtex yourself, no dependency, no bibliography config, resolved nodes are ordinary docutils nodes, style owned by pybtex, Typst `#bibliography()`/`#cite()`/CSL not used, setup and constraints (34) | user_guide/bibliography.rst (setup, design, constraints sections) | already in manual |
  | 6 | `#### typst_documents`: tuple shape `(source, target, title, author[, documentclass])`, fifth element = registry key into `typst_document_templates` (81–86) | user_guide/configuration.rst § Typst Documents (items 1–5, "Document registry key") | already in manual |
  | 7 | typst_documents: wrapper `.typ` per entry, one PDF per wrapper under typstpdf, content `.typ` per docname (86–92) | user_guide/output_layout.rst § Wrapper and Content Files; user_guide/builders.rst § Document Definitions | already in manual |
  | 8 | typst_documents unset → derived from `root_doc`/`project`/`author`, `make_filename_from_project`, `myproject.typ`/`.pdf`, derived entry makes root a master with full wrapper (94–101) | user_guide/configuration.rst § Typst Documents; quickstart.rst (Your First PDF, `build/pdf/myproject.pdf`) | already in manual |
  | 9 | explicit value incl. `[]` overrides the derived default (103–105) | user_guide/configuration.rst § Typst Documents ("including an explicit empty list") | already in manual |
  | 10 | only named/derived masters become PDFs; toctree-only docs are `.typ` content files pulled in by `#include()` (107–110) | user_guide/builders.rst § Document Definitions ("only the wrappers become PDFs"); user_guide/output_layout.rst § Wrapper and Content Files | already in manual |
  | 11 | Advanced Usage › Custom Templates `typst_template = '_typst/custom.typ'` (161–168) | user_guide/templates.rst § Custom Template Files; quickstart.rst | already in manual |
  | 12 | Advanced Usage › Template Parameter Mapping example and key/value meaning (170–183) | user_guide/configuration.rst § Template Configuration › Template Parameter Mapping | added by T001 |
  | 13 | Advanced Usage › Multi-Document Projects toctree example, `#include()` with heading level adjustment (185–199) | user_guide/output_layout.rst § Multi-Document Projects | added by T001 |
  | 14 | Advanced Usage › Working with Third-Party Extensions (mermaid `app.add_node` example, How it works bullets, Sphinx add_node API link) (201–229) | user_guide/configuration.rst § Third-Party Extension Nodes | added by T001 |
  | 15 | Configuration Options intro + link to configuration reference (231–233) | user_guide/configuration.rst (the full reference itself) | already in manual |
  | 16 | Config bullet `typst_documents` (235) | user_guide/configuration.rst § Typst Documents | already in manual |
  | 17 | Config bullet `typst_use_mitex` (236) | user_guide/configuration.rst § mitex Support | already in manual |
  | 18 | Config bullet `typst_template` (237) | user_guide/templates.rst § Custom Template Files | already in manual |
  | 19 | Config bullet `typst_elements` paper size, fonts (238) | user_guide/configuration.rst § Paper Size and Format | already in manual |
  | 20 | Config bullet `typst_template_mapping` (239) | user_guide/configuration.rst § Template Parameter Mapping | added by T001 |
  | 21 | Development: uses uv, follows TDD (243) | contributing.rst (uv setup; "Write tests first (TDD approach)") | already in manual |
  | 22 | Development setup: `uv sync --extra dev`, `uv run pytest` (247–252) | contributing.rst § Development setup / Running Tests | already in manual |
  | 23 | `uv run pytest --cov=typsphinx --cov-report=html` (255) | contributing.rst § Running Tests | added by T001 |
  | 24 | tox commands: `tox`, `-e lint`, `-e type`, `-e py312`, `-e docs-html`, `-e docs-pdf`, `-e docs`, `-e linkcheck` (257–267) | contributing.rst (tox block, lines ~120–132) | already in manual |
  | 25 | Testing Strategy: unit tests, integration tests (272–273) | contributing.rst § Coding Guidelines › Testing | already in manual |
  | 26 | Testing Strategy: example projects `examples/basic/`, `examples/advanced/` (274) | contributing.rst § Coding Guidelines › Testing | added by T001 |
  | 27 | Project Structure tree (builder/writer/translator/template_engine/pdf/templates, tests, docs, examples, pyproject) (276–292) | contributing.rst § Project Structure | already in manual |
  | 28 | Project Structure `typst_deps.py` line (286) | contributing.rst § Project Structure | added by T001 |
  | 29 | Contributing "Contributions are welcome" + fork/branch/tests/`uv run pytest`/PR steps (313–319) | — | deleted per C5 |
  | 30 | Contributing › Development Guidelines (TDD, black, Sphinx conventions, tests) (321–326) | — | deleted per C5 |

  Not in the table (not a removed information item): the Acknowledgments GSD credit linking `open-gsd/gsd-core` (339) was replaced by the GSD Path credit per DOCS-AUDIT #1 fix-doc / SC5. Reworded, not removed: Features math sub-bullets → "LaTeX syntax via mitex, or native Typst math syntax"; codly bullet → "Using the codly package, with line numbers and highlighted lines"; bibliography bullet → feature-only one line.
- 2026-11-05 — build_T002 Verify: pass, exit 0 — targeted gates 31 passed; full suite `LC_ALL=C uv run pytest tests/` 1908 passed, 1 skipped; black (401 files unchanged), ruff, mypy clean. (In my run the two pytest steps were piped through `tail`, so their exit codes were not chained. The orchestrator rerun of the exact command is authoritative; both outputs showed 0 failed.)
- 2026-11-04 — orchestrator Verify (sidecar gsd-path-verify/task-t002-verify): pass, exit 0; output tail:
  ```
   + sphinxcontrib-bibtex==2.7.0
   + sphinxcontrib-devhelp==2.0.0
   + sphinxcontrib-htmlhelp==2.1.0
   + sphinxcontrib-jsmath==1.0.1
   + sphinxcontrib-qthelp==2.0.0
   + sphinxcontrib-serializinghtml==2.0.0
   + tomli-w==1.2.0
   + tox==4.64.10
   + tox-uv==1.37.2
   + tox-uv-bare==1.37.2
   + twine==7.0.0
   + types-docutils==0.23.0.20260923
   + typing-extensions==4.16.0
   + typsphinx==0.10.0 (from file:///home/yuta/.gsd-path/projects/4018706f853274cd7713143cf7ba094e230867e5ad2bfc5891d0cd69027eb98b/4b529697c911aff5766d6b9c03f122ba2ed9565d87a00e2f51ea62f3fd0642ec/verify/task-t002-verify)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.13.6
   + virtualenv==21.5.1
  All done! ✨ 🍰 ✨
  401 files would be left unchanged.
  ```
