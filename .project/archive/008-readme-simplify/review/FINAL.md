# Final Review — reused full wave

Reviewed HEAD: 02971562f40185553df403fbb5d8bb3127500b0b
Overall verdict: pass
Source review: .project/review/wave-1.cycle1.md
Source commit: 0eb2ecbd1c8d47e06d4710b066da0faee7fb71a1

## Success criteria

### SC1 — README structure (surface: README.md): `grep '^## ' README.md` outputs exactly these lines in this order and nothing else: `## Overview`, `## Features`, `## Requirements`, `## Installation`, `## Quick Start`, `## Documentation`, `## Contributing`, `## License`, `## Acknowledgments`, `## Version History`. The badges, the one-line description and the Documentation/Issue Tracker/PyPI link line above `## Overview` remain.

- **Verdict**: met
- **Check**: `grep '^## ' README.md` at 0eb2ecbd and read README.md:1-13 (walkthrough step 1)
- **Observed**: ten headings Overview, Features, Requirements, Installation, Quick Start, Documentation, Contributing, License, Acknowledgments, Version History, nothing else; six badges, description and link line above Overview.
- **Reference**: .project/review/wave-1.cycle1.md — SC1; evidence: Heading list matches exactly, order included (E1); preamble lines README.md:3-12 present.
- **Finding**: none
- **Fix direction**: none
- **Surface**: README.md (as rendered on GitHub)

### SC2 — Installation and Quick Start (surface: README.md): `## Installation` keeps the `pip install typsphinx` block and the uv block (clone, `uv sync`, `uv sync --extra dev`). `## Quick Start` has exactly the subsections `### Basic Configuration`, `### Build Typst Output`, `### Example Document`; Basic Configuration is a minimal conf.py example with no `#### typst_documents` subsection; Build Typst Output shows both `sphinx-build -b typst` and `sphinx-build -b typstpdf` commands; Example Document keeps an rST example.

- **Verdict**: met
- **Check**: read README.md Installation and Quick Start (walkthrough step 2)
- **Observed**: pip block; uv block with clone, `uv sync`, `uv sync --extra dev`; three `###` subsections only; conf.py with commented extensions line and `typst_use_mitex = True`; `sphinx-build -b typst source build/typst` and `sphinx-build -b typstpdf source build/pdf`; rST example with math and code-block.
- **Reference**: .project/review/wave-1.cycle1.md — SC2; evidence: README.md:38-122 as listed under T002/AC2.
- **Finding**: none
- **Fix direction**: none
- **Surface**: README.md (as rendered on GitHub)

### SC3 — Features (surface: README.md): every bullet under `## Features` is a single physical source line with no nested sub-bullet; the bibliography bullet is one line that states only the feature (plain rST citations and sphinxcontrib-bibtex `:cite:` / `.. bibliography::` render in the output) and links to the bibliography user guide, with the design notes and constraints left to that guide (`grep -c -i -E 'pybtex|CSL|#bibliography' README.md` prints `0`); a bullet states that Graphviz DOT diagrams (`.. graphviz::`, `.. digraph::`, `.. graph::`) compile into Typst/PDF output without a Graphviz installation, linking to the diagrams user guide; `grep -c '@preview/' README.md` prints `0`.

- **Verdict**: met
- **Check**: read README.md:18-31; `grep -c -i -E 'pybtex|CSL|#bibliography' README.md`; `grep -c '@preview/' README.md` (walkthrough step 3)
- **Observed**: 11 single-line bullets, none indented; bibliography bullet links `/en/latest/user_guide/bibliography.html`; Graphviz bullet names the three directives, "without a Graphviz installation", links `/en/latest/user_guide/diagrams.html`; both counts 0.
- **Reference**: .project/review/wave-1.cycle1.md — SC3; evidence: README.md:20-30 one line per bullet (E3); bibliography and Graphviz bullets as required; both greps print 0.
- **Finding**: none
- **Fix direction**: none
- **Surface**: README.md (as rendered on GitHub)

### SC4 — Contributing, Version History, Status (surface: README.md): `## Contributing` contains only a link to the contributing guide (no step list, no Development Guidelines); `## Version History` links to CHANGELOG.md; the file still ends with the `**Status**: Stable (v0.10.0) - Production ready` line and the Python/Sphinx/Typst line.

- **Verdict**: met
- **Check**: read README.md Contributing, Version History and last lines (walkthrough step 4)
- **Observed**: "See the [Contributing Guide](…/en/latest/contributing.html)." only; "See [CHANGELOG.md](CHANGELOG.md) …"; last two lines are the Status line and `**Python**: 3.12+ | **Sphinx**: 9.1+ | **Typst**: 0.15+`.
- **Reference**: .project/review/wave-1.cycle1.md — SC4; evidence: README.md:141-143, :160-162, :166-167.
- **Finding**: none
- **Fix direction**: none
- **Surface**: README.md (as rendered on GitHub)

### SC5 — Acknowledgments (surface: README.md): `## Acknowledgments` still credits Sphinx, Typst, mitex, codly and gentle-clues, and adds diagraph (renders Graphviz diagrams; `https://typst.app/universe/package/diagraph`) and typst-py (performs the Typst compilation; `https://github.com/messense/typst-py`); the development credit links GSD Path (`https://github.com/open-gsd/gsd-path`); `grep -c 'gsd-core' README.md` prints `0`.

- **Verdict**: met
- **Check**: read README.md:149-158; `grep -c 'gsd-core' README.md` (walkthrough step 4)
- **Observed**: Sphinx, Typst, mitex, codly, gentle-clues, diagraph (`https://typst.app/universe/package/diagraph`, "to render Graphviz diagrams"), typst-py (`https://github.com/messense/typst-py`, "to perform the Typst compilation"), "Developed with Claude Code and GSD Path" (`https://github.com/open-gsd/gsd-path`); count 0.
- **Reference**: .project/review/wave-1.cycle1.md — SC5; evidence: README.md:151-158; N1 held: all seven upstream credits present; `grep -c gsd-core` = 0.
- **Finding**: none
- **Fix direction**: none
- **Surface**: README.md (as rendered on GitHub)

### SC6 — No information lost (surface: docs HTML manual): for every information item removed from README.md (search space: lines deleted by `git diff c1606cd9 -- README.md`), a page under docs/source states that information. Items the manual did not already state are added to the appropriate docs/source page in English; where README and the manual disagreed, the manual's statement stands and only README-only information is added. Exception (C5): the README `## Contributing` content (the fork/branch/test/PR step list and the Development Guidelines bullets) is deleted, not moved. README `## Development` content is not excepted: README-only items there (e.g. the `typst_deps.py` Project Structure line, the `--cov-report=html` command, the example-projects testing note) are added to docs/source/contributing.rst (C7). The task log records the removed-item → docs location table (Contributing items marked `deleted per C5`), and the final reviewer checks each row against the built HTML.

- **Verdict**: met
- **Check**: `LC_ALL=C uv run sphinx-build -E -b html docs/source <fresh scratch dir> -w <file>` at 0eb2ecbd, HTML converted to text and grepped per table row; table compared against `git diff c1606cd9 0eb2ecbd -- README.md` deleted lines (walkthrough steps 2–3)
- **Observed**: all added-row strings found (index.html, user_guide/bibliography.html, user_guide/configuration.html, user_guide/output_layout.html, contributing.html); already-in-manual rows found in user_guide/templates.html (0.2.7, `@preview/codly:2.0.0`), configuration/builders/output_layout/quickstart/contributing pages; table covers every deleted line; Contributing step list and Development Guidelines absent from docs, marked `deleted per C5`.
- **Reference**: .project/review/wave-1.cycle1.md — SC6; evidence: All 190 deleted README lines map to T002 Log rows 1–30 (rows 29–30 `deleted per C5`) or to the SC5 credit swap; each row's docs location checked in the HEAD build's HTML text (see T001/AC1). E6: T001 diff only adds lines to docs/source; existing statements unchanged (contributing.rst `pdf.py # TypstPDFBuilder` kept). E7: README-only items have new homes. N2 held. N3 (judgment): every added item states concrete content, not a pointer — the mermaid `setup(app)`/`app.add_node(mermaid, typst=(typst_visit_mermaid, None))` example verbatim plus the three How-it-works bullets and the API link (configuration.rst § Third-Party Extension Nodes); the `typst_template_mapping` dict and key/value meaning (configuration.rst § Template Parameter Mapping); the toctree `:maxdepth: 2`/`:numbered:` example and the `set heading(offset: heading.offset + 1)` rule (output_layout.rst § Multi-Document Projects); a `[Smith2020]_` rST example (bibliography.rst § Plain reStructuredText Citations); `:linenos:`, multiple languages, `:emphasize-lines:` sub-bullets (index.rst § Key Features); the exact coverage command, `typst_deps.py` tree line and example-project paths (contributing.rst).
- **Finding**: none
- **Fix direction**: none
- **Surface**: docs HTML manual (pages that receive content moved out of README)

### SC7 — Manual builds (surface: docs HTML manual): a clean HTML build of the docs (`rm -rf docs/_build` first, then `tox -e docs-html` or the equivalent `sphinx-build -b html docs/source docs/_build/html`) succeeds with no warning that the base revision c1606cd9 does not also produce, and each docs page that received moved content shows it in the built HTML.

- **Verdict**: met
- **Check**: `rm -rf <scratch>/html-head; LC_ALL=C uv run sphinx-build -E -b html docs/source <scratch>/html-head -w <scratch>/html-head.warn` (walkthrough step 1)
- **Observed**: exit 0, "build succeeded.", 0-byte warning file; added content present in the five receiving pages.
- **Reference**: .project/review/wave-1.cycle1.md — SC7; evidence: E8: clean builds only. Reviewer clean build at reviewed HEAD (which includes T002's CHANGELOG change, pulled in by docs/source/changelog.rst `.. include:: ../../CHANGELOG.md`, so T001's recorded build alone did not cover it) exit 0, "build succeeded.", warning file 0 bytes — zero warnings, so none the base lacks. T001 orchestrator Verify `-W -E` build also "build succeeded.". Moved content visible in each receiving page (see SC6).
- **Finding**: none
- **Fix direction**: none
- **Surface**: docs HTML manual (pages that receive content moved out of README)

### SC8 — CHANGELOG (surface: CHANGELOG.md): `## [Unreleased]` gains one bullet stating that the README was simplified and details moved to the manual; every other existing CHANGELOG line is unchanged.

- **Verdict**: met
- **Check**: read CHANGELOG.md `## [Unreleased]`; `git diff c1606cd9 0eb2ecbd -- CHANGELOG.md` (walkthrough steps 1–2)
- **Observed**: `### Documentation` + the one bullet + blank line added above `### Planned for Future Releases`; no removed or modified line.
- **Reference**: .project/review/wave-1.cycle1.md — SC8; evidence: Diff vs c1606cd9 is three added lines only; one bullet "README simplified: configuration, advanced usage and development details moved to the manual." under a new `### Documentation` heading.
- **Finding**: none
- **Fix direction**: none
- **Surface**: CHANGELOG.md

### SC9 — On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean; README-pinning gates are updated to the new README rather than deleted (the Status-line and Documentation-link gates still assert those parts).

- **Verdict**: met
- **Check**: none
- **Observed**: T002 orchestrator isolated Verify on product 28d0e7d9 (identical product to reviewed HEAD 0eb2ecbd; only `.project/build/verify-ledger.jsonl` differs): `uv sync --extra dev --extra docs`, "1908 passed, 1 skipped", black "401 files would be left unchanged.", ruff "All checks passed!", mypy "Success: no issues found in 10 source files", exit 0. No test deleted (see T002/AC7); tests/test_readme_version_sync.py unchanged; Documentation-link gate still asserts the 8 ordered links.
- **Reference**: .project/review/wave-1.cycle1.md — SC9
- **Finding**: none
- **Fix direction**: none
