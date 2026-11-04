# Review — wave 1, cycle 1

Reviewed HEAD: 0eb2ecbd1c8d47e06d4710b066da0faee7fb71a1
Review scope: final

Wave verdict: pass
Cycle: 1
Depth: full
Lens:
Tasks reviewed: 2

Inspection mode: reconstructed product — verify sidecar `verify/wave-1-cycle-1` checked out at 0eb2ecbd1c8d47e06d4710b066da0faee7fb71a1. `git diff --stat 28d0e7d9 0eb2ecbd` touches only `.project/build/verify-ledger.jsonl`, so the reviewed product equals T001 landing (2843375, parent c913040e = task base) plus T002 landing (28d0e7d9, parent aced58a9 = task base). `git diff --stat c1606cd9 c913040e` touches only `.project/` paths, so the T001 base product equals the v0.10.0 release c1606cd9.

## T001 — Add every README-only item to the manual and record the mapping table: pass

- ✅ T001/AC1 — `git diff c1606cd9 0eb2ecbd -- README.md` deleted lines (190) checked row by row against T002's Log table (rows 1–30) and the built HTML at reviewed HEAD: every non-Contributing item is in a docs/source page (e.g. templates.rst Package Dependencies has `0.2.7` and `@preview/codly:2.0.0`; configuration.rst:26-34 states the root_doc/project/author derivation, `make_filename_from_project`, explicit empty list override and the full-wrapper consequence; builders.rst:130-131 "only the wrappers become PDFs"; bibliography.rst:36-56 not-a-dependency/install/no-config, :203-212 pybtex and Typst `#bibliography()`/`#cite()` not used). T001 diff adds only new lines to docs/source (no existing manual line removed or reworded: the 3 deleted lines in the commit are task-file frontmatter only), so E6 holds; README-only items (codly sub-bullets, docutils nodes, multi-document, plain citations, template mapping, third-party nodes, toctree example, typst_deps.py, cov-report=html, examples) were added, so E7 holds.
- ✅ T001/AC2 — contributing.rst diff: `+ │   ├── typst_deps.py       # Typst @preview package versions` (Project Structure), `uv run pytest --cov=typsphinx --cov-report=html` (Running Tests), `examples/basic/` and `examples/advanced/` bullet (Testing); diff has only `+` lines in contributing.rst, nothing reworded.
- ✅ T001/AC3 — orchestrator isolated Verify (ledger, commit 2843375, exit 0): `sphinx-build -W -E -b html` "build succeeded.", contributing.html grep matched, 6 docs gates "78 passed". Reviewer clean rebuild at reviewed HEAD (fresh dir, `-E`, `-w` file) exit 0, warning file 0 bytes; each added row's text found in built index/bibliography/configuration/output_layout/contributing HTML.
- ✅ T001/AC4 — T001 Log lines 68-79 list each added item with file § section.

Warnings (non-blocking):
- none

Contract violations (blocking):
- none (changed paths: 5 docs/source files, all in `files`, plus the task file with only status/agent/base fields and appended Log)

## T002 — Rewrite README.md to the approved shape, update its gates, add the CHANGELOG bullet: pass

- ✅ T002/AC1 — `grep '^## ' README.md` at reviewed HEAD prints exactly the ten approved headings in order; README.md:3-12 keep six badges, the one-line description and the Documentation/Issue Tracker/PyPI line. Orchestrator Verify heading-string test passed (exit 0).
- ✅ T002/AC2 — README.md:40-58 pip block and uv block (clone, `uv sync`, `uv sync --extra dev`); Quick Start subsections are exactly Basic Configuration (README.md:62-75, minimal conf.py, no `#### typst_documents`), Build Typst Output (:77-85, `-b typst` and `-b typstpdf`), Example Document (:87-122, rST example).
- ✅ T002/AC3 — README.md:20-30 eleven bullets, each one physical line, no nested bullet; bibliography bullet :30 feature-only with bibliography guide link; Graphviz bullet :29 with diagrams guide link; `grep -c '@preview/'` = 0, `grep -c -i -E 'pybtex|CSL|#bibliography'` = 0.
- ✅ T002/AC4 — README.md:141-143 Contributing is one link sentence; :160-162 links CHANGELOG.md; file ends :166-167 with the Status line and the Python/Sphinx/Typst line.
- ✅ T002/AC5 — README.md:151-158 credits Sphinx, Typst, mitex, codly, gentle-clues, diagraph, typst-py and GSD Path (`https://github.com/open-gsd/gsd-path`); `grep -c gsd-core` = 0.
- ✅ T002/AC6 — `git diff c1606cd9 0eb2ecbd -- CHANGELOG.md` shows only three added lines under `## [Unreleased]` (`### Documentation`, the README-simplified bullet, blank); no line removed.
- ✅ T002/AC7 — orchestrator isolated Verify (ledger, commit 28d0e7d9, exit 0): targeted gates "31 passed", full suite "1908 passed, 1 skipped", ruff "All checks passed!", mypy "Success: no issues found in 10 source files", black "401 files would be left unchanged." Test diff deletes no test: one rename `test_readme_quickstart_explains_typst_documents` → `test_quickstart_explains_typst_documents` (still asserts README Quick Start shape), 11 new tests in tests/test_readme_structure_gate.py; Status-line gate tests/test_readme_version_sync.py untouched; Documentation-link gate still asserts 8 ordered `/en/latest/` links within `## Documentation`. Log lines 82-113 hold the removed-item table.

Warnings (non-blocking):
- none

Contract violations (blocking):
- none (changed paths: README.md, CHANGELOG.md, 4 test files, all in `files`, plus the task file with only status/agent/base fields and appended Log)

## Intent coverage

### SC1 — README structure (surface: README.md): `grep '^## ' README.md` outputs exactly these lines in this order and nothing else: `## Overview`, `## Features`, `## Requirements`, `## Installation`, `## Quick Start`, `## Documentation`, `## Contributing`, `## License`, `## Acknowledgments`, `## Version History`. The badges, the one-line description and the Documentation/Issue Tracker/PyPI link line above `## Overview` remain.: pass
- ✅ Heading list matches exactly, order included (E1); preamble lines README.md:3-12 present.
- **Surface**: README.md (as rendered on GitHub)
- **Check**: `grep '^## ' README.md` at 0eb2ecbd and read README.md:1-13 (walkthrough step 1)
- **Observed**: ten headings Overview, Features, Requirements, Installation, Quick Start, Documentation, Contributing, License, Acknowledgments, Version History, nothing else; six badges, description and link line above Overview.

### SC2 — Installation and Quick Start (surface: README.md): `## Installation` keeps the `pip install typsphinx` block and the uv block (clone, `uv sync`, `uv sync --extra dev`). `## Quick Start` has exactly the subsections `### Basic Configuration`, `### Build Typst Output`, `### Example Document`; Basic Configuration is a minimal conf.py example with no `#### typst_documents` subsection; Build Typst Output shows both `sphinx-build -b typst` and `sphinx-build -b typstpdf` commands; Example Document keeps an rST example.: pass
- ✅ README.md:38-122 as listed under T002/AC2.
- **Surface**: README.md (as rendered on GitHub)
- **Check**: read README.md Installation and Quick Start (walkthrough step 2)
- **Observed**: pip block; uv block with clone, `uv sync`, `uv sync --extra dev`; three `###` subsections only; conf.py with commented extensions line and `typst_use_mitex = True`; `sphinx-build -b typst source build/typst` and `sphinx-build -b typstpdf source build/pdf`; rST example with math and code-block.

### SC3 — Features (surface: README.md): every bullet under `## Features` is a single physical source line with no nested sub-bullet; the bibliography bullet is one line that states only the feature (plain rST citations and sphinxcontrib-bibtex `:cite:` / `.. bibliography::` render in the output) and links to the bibliography user guide, with the design notes and constraints left to that guide (`grep -c -i -E 'pybtex|CSL|#bibliography' README.md` prints `0`); a bullet states that Graphviz DOT diagrams (`.. graphviz::`, `.. digraph::`, `.. graph::`) compile into Typst/PDF output without a Graphviz installation, linking to the diagrams user guide; `grep -c '@preview/' README.md` prints `0`.: pass
- ✅ README.md:20-30 one line per bullet (E3); bibliography and Graphviz bullets as required; both greps print 0.
- **Surface**: README.md (as rendered on GitHub)
- **Check**: read README.md:18-31; `grep -c -i -E 'pybtex|CSL|#bibliography' README.md`; `grep -c '@preview/' README.md` (walkthrough step 3)
- **Observed**: 11 single-line bullets, none indented; bibliography bullet links `/en/latest/user_guide/bibliography.html`; Graphviz bullet names the three directives, "without a Graphviz installation", links `/en/latest/user_guide/diagrams.html`; both counts 0.

### SC4 — Contributing, Version History, Status (surface: README.md): `## Contributing` contains only a link to the contributing guide (no step list, no Development Guidelines); `## Version History` links to CHANGELOG.md; the file still ends with the `**Status**: Stable (v0.10.0) - Production ready` line and the Python/Sphinx/Typst line.: pass
- ✅ README.md:141-143, :160-162, :166-167.
- **Surface**: README.md (as rendered on GitHub)
- **Check**: read README.md Contributing, Version History and last lines (walkthrough step 4)
- **Observed**: "See the [Contributing Guide](…/en/latest/contributing.html)." only; "See [CHANGELOG.md](CHANGELOG.md) …"; last two lines are the Status line and `**Python**: 3.12+ | **Sphinx**: 9.1+ | **Typst**: 0.15+`.

### SC5 — Acknowledgments (surface: README.md): `## Acknowledgments` still credits Sphinx, Typst, mitex, codly and gentle-clues, and adds diagraph (renders Graphviz diagrams; `https://typst.app/universe/package/diagraph`) and typst-py (performs the Typst compilation; `https://github.com/messense/typst-py`); the development credit links GSD Path (`https://github.com/open-gsd/gsd-path`); `grep -c 'gsd-core' README.md` prints `0`.: pass
- ✅ README.md:151-158; N1 held: all seven upstream credits present; `grep -c gsd-core` = 0.
- **Surface**: README.md (as rendered on GitHub)
- **Check**: read README.md:149-158; `grep -c 'gsd-core' README.md` (walkthrough step 4)
- **Observed**: Sphinx, Typst, mitex, codly, gentle-clues, diagraph (`https://typst.app/universe/package/diagraph`, "to render Graphviz diagrams"), typst-py (`https://github.com/messense/typst-py`, "to perform the Typst compilation"), "Developed with Claude Code and GSD Path" (`https://github.com/open-gsd/gsd-path`); count 0.

### SC6 — No information lost (surface: docs HTML manual): for every information item removed from README.md (search space: lines deleted by `git diff c1606cd9 -- README.md`), a page under docs/source states that information. Items the manual did not already state are added to the appropriate docs/source page in English; where README and the manual disagreed, the manual's statement stands and only README-only information is added. Exception (C5): the README `## Contributing` content (the fork/branch/test/PR step list and the Development Guidelines bullets) is deleted, not moved. README `## Development` content is not excepted: README-only items there (e.g. the `typst_deps.py` Project Structure line, the `--cov-report=html` command, the example-projects testing note) are added to docs/source/contributing.rst (C7). The task log records the removed-item → docs location table (Contributing items marked `deleted per C5`), and the final reviewer checks each row against the built HTML.: pass
- ✅ All 190 deleted README lines map to T002 Log rows 1–30 (rows 29–30 `deleted per C5`) or to the SC5 credit swap; each row's docs location checked in the HEAD build's HTML text (see T001/AC1). E6: T001 diff only adds lines to docs/source; existing statements unchanged (contributing.rst `pdf.py # TypstPDFBuilder` kept). E7: README-only items have new homes. N2 held. N3 (judgment): every added item states concrete content, not a pointer — the mermaid `setup(app)`/`app.add_node(mermaid, typst=(typst_visit_mermaid, None))` example verbatim plus the three How-it-works bullets and the API link (configuration.rst § Third-Party Extension Nodes); the `typst_template_mapping` dict and key/value meaning (configuration.rst § Template Parameter Mapping); the toctree `:maxdepth: 2`/`:numbered:` example and the `set heading(offset: heading.offset + 1)` rule (output_layout.rst § Multi-Document Projects); a `[Smith2020]_` rST example (bibliography.rst § Plain reStructuredText Citations); `:linenos:`, multiple languages, `:emphasize-lines:` sub-bullets (index.rst § Key Features); the exact coverage command, `typst_deps.py` tree line and example-project paths (contributing.rst).
- **Surface**: docs HTML manual (pages that receive content moved out of README)
- **Check**: `LC_ALL=C uv run sphinx-build -E -b html docs/source <fresh scratch dir> -w <file>` at 0eb2ecbd, HTML converted to text and grepped per table row; table compared against `git diff c1606cd9 0eb2ecbd -- README.md` deleted lines (walkthrough steps 2–3)
- **Observed**: all added-row strings found (index.html, user_guide/bibliography.html, user_guide/configuration.html, user_guide/output_layout.html, contributing.html); already-in-manual rows found in user_guide/templates.html (0.2.7, `@preview/codly:2.0.0`), configuration/builders/output_layout/quickstart/contributing pages; table covers every deleted line; Contributing step list and Development Guidelines absent from docs, marked `deleted per C5`.

### SC7 — Manual builds (surface: docs HTML manual): a clean HTML build of the docs (`rm -rf docs/_build` first, then `tox -e docs-html` or the equivalent `sphinx-build -b html docs/source docs/_build/html`) succeeds with no warning that the base revision c1606cd9 does not also produce, and each docs page that received moved content shows it in the built HTML.: pass
- ✅ E8: clean builds only. Reviewer clean build at reviewed HEAD (which includes T002's CHANGELOG change, pulled in by docs/source/changelog.rst `.. include:: ../../CHANGELOG.md`, so T001's recorded build alone did not cover it) exit 0, "build succeeded.", warning file 0 bytes — zero warnings, so none the base lacks. T001 orchestrator Verify `-W -E` build also "build succeeded.". Moved content visible in each receiving page (see SC6).
- **Surface**: docs HTML manual (pages that receive content moved out of README)
- **Check**: `rm -rf <scratch>/html-head; LC_ALL=C uv run sphinx-build -E -b html docs/source <scratch>/html-head -w <scratch>/html-head.warn` (walkthrough step 1)
- **Observed**: exit 0, "build succeeded.", 0-byte warning file; added content present in the five receiving pages.

### SC8 — CHANGELOG (surface: CHANGELOG.md): `## [Unreleased]` gains one bullet stating that the README was simplified and details moved to the manual; every other existing CHANGELOG line is unchanged.: pass
- ✅ Diff vs c1606cd9 is three added lines only; one bullet "README simplified: configuration, advanced usage and development details moved to the manual." under a new `### Documentation` heading.
- **Surface**: CHANGELOG.md
- **Check**: read CHANGELOG.md `## [Unreleased]`; `git diff c1606cd9 0eb2ecbd -- CHANGELOG.md` (walkthrough steps 1–2)
- **Observed**: `### Documentation` + the one bullet + blank line added above `### Planned for Future Releases`; no removed or modified line.

### SC9 — On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean; README-pinning gates are updated to the new README rather than deleted (the Status-line and Documentation-link gates still assert those parts).: pass
- ✅ T002 orchestrator isolated Verify on product 28d0e7d9 (identical product to reviewed HEAD 0eb2ecbd; only `.project/build/verify-ledger.jsonl` differs): `uv sync --extra dev --extra docs`, "1908 passed, 1 skipped", black "401 files would be left unchanged.", ruff "All checks passed!", mypy "Success: no issues found in 10 source files", exit 0. No test deleted (see T002/AC7); tests/test_readme_version_sync.py unchanged; Documentation-link gate still asserts the 8 ordered links.

## Summary for orchestrator

- blocked findings: none
- repeat offenders: none
- warnings worth a human eye: none
