# Intent — typsphinx

Lane: quick   <!-- two deliverable-sized tasks in one wave (docs absorb removed README content; README rewrite + gate updates + CHANGELOG line); no RESEARCH or NEEDS-USER items; no cross-wave risk -->

Review panel: off

Finding skeptics: off

Surfaces: README.md (as rendered on GitHub), docs HTML manual (pages that receive content moved out of README), CHANGELOG.md

## Summary

README.md has grown to 348 lines and carries manual-level detail (Advanced Usage, Configuration Options, Development, a ~30-line `typst_documents` explanation, a paragraph-long bibliography note, pinned `@preview` versions). The owner wants it back to a reasonably simple shape, with fine-grained cautions left to the manual (docs/source). README keeps Overview, Features (one line per item, adding Graphviz diagram support), Requirements, Installation (PyPI and uv), Quick Start (Basic Configuration with a minimal conf.py, Build Typst Output, Example Document), Documentation links, Contributing (link to the contributing guide only), License, Acknowledgments (credit switched from gsd-core to GSD Path; diagraph and typst-py added), Version History (link to CHANGELOG.md) and the Status line. Anything removed from README that the manual does not already say is moved into docs/source in English, the manual winning where the two disagree. README-pinning tests are updated to the new README; one `[Unreleased]` CHANGELOG line records the change. No release in this milestone.

## Problem

- README.md is 348 lines (evidence-codebase.md; `wc -l README.md`), duplicating user_guide/configuration.rst, templates.rst, bibliography.rst and contributing.rst content.
- Features pins `@preview/mitex:0.2.7` and `@preview/codly:2.0.0`; the `@preview` sync gate (`tests/test_preview_version_sync.py`) does not police README, so the next dependency bump leaves README stale.
- DOCS-AUDIT queue #1: README.md:339 credits "GSD" linking `open-gsd/gsd-core`; the repo now runs on GSD Path.

## Users

Visitors reading README.md on GitHub (and, at the next release, on PyPI via `readme = "README.md"`), and users following README into the Read the Docs manual.

## Success criteria

1. README structure (surface: README.md): `grep '^## ' README.md` outputs exactly these lines in this order and nothing else: `## Overview`, `## Features`, `## Requirements`, `## Installation`, `## Quick Start`, `## Documentation`, `## Contributing`, `## License`, `## Acknowledgments`, `## Version History`. The badges, the one-line description and the Documentation/Issue Tracker/PyPI link line above `## Overview` remain.
2. Installation and Quick Start (surface: README.md): `## Installation` keeps the `pip install typsphinx` block and the uv block (clone, `uv sync`, `uv sync --extra dev`). `## Quick Start` has exactly the subsections `### Basic Configuration`, `### Build Typst Output`, `### Example Document`; Basic Configuration is a minimal conf.py example with no `#### typst_documents` subsection; Build Typst Output shows both `sphinx-build -b typst` and `sphinx-build -b typstpdf` commands; Example Document keeps an rST example.
3. Features (surface: README.md): every bullet under `## Features` is a single physical source line with no nested sub-bullet; the bibliography bullet is one line that states only the feature (plain rST citations and sphinxcontrib-bibtex `:cite:` / `.. bibliography::` render in the output) and links to the bibliography user guide, with the design notes and constraints left to that guide (`grep -c -i -E 'pybtex|CSL|#bibliography' README.md` prints `0`); a bullet states that Graphviz DOT diagrams (`.. graphviz::`, `.. digraph::`, `.. graph::`) compile into Typst/PDF output without a Graphviz installation, linking to the diagrams user guide; `grep -c '@preview/' README.md` prints `0`.
4. Contributing, Version History, Status (surface: README.md): `## Contributing` contains only a link to the contributing guide (no step list, no Development Guidelines); `## Version History` links to CHANGELOG.md; the file still ends with the `**Status**: Stable (v0.10.0) - Production ready` line and the Python/Sphinx/Typst line.
5. Acknowledgments (surface: README.md): `## Acknowledgments` still credits Sphinx, Typst, mitex, codly and gentle-clues, and adds diagraph (renders Graphviz diagrams; `https://typst.app/universe/package/diagraph`) and typst-py (performs the Typst compilation; `https://github.com/messense/typst-py`); the development credit links GSD Path (`https://github.com/open-gsd/gsd-path`); `grep -c 'gsd-core' README.md` prints `0`.
6. No information lost (surface: docs HTML manual): for every information item removed from README.md (search space: lines deleted by `git diff c1606cd9 -- README.md`), a page under docs/source states that information. Items the manual did not already state are added to the appropriate docs/source page in English; where README and the manual disagreed, the manual's statement stands and only README-only information is added. Exception (C5): the README `## Contributing` content (the fork/branch/test/PR step list and the Development Guidelines bullets) is deleted, not moved. README `## Development` content is not excepted: README-only items there (e.g. the `typst_deps.py` Project Structure line, the `--cov-report=html` command, the example-projects testing note) are added to docs/source/contributing.rst (C7). The task log records the removed-item → docs location table (Contributing items marked `deleted per C5`), and the final reviewer checks each row against the built HTML.
7. Manual builds (surface: docs HTML manual): a clean HTML build of the docs (`rm -rf docs/_build` first, then `tox -e docs-html` or the equivalent `sphinx-build -b html docs/source docs/_build/html`) succeeds with no warning that the base revision c1606cd9 does not also produce, and each docs page that received moved content shows it in the built HTML.
8. CHANGELOG (surface: CHANGELOG.md): `## [Unreleased]` gains one bullet stating that the README was simplified and details moved to the manual; every other existing CHANGELOG line is unchanged.
9. On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean; README-pinning gates are updated to the new README rather than deleted (the Status-line and Documentation-link gates still assert those parts).

## Edge coverage

| Edge | Criterion | Category | Disposition | Detail |
|------|-----------|----------|-------------|--------|
| E1 | SC1 | ordering | criterion SC1 | heading list must match exactly, order included (owner ruling 7: 見出し一覧の完全一致) |
| E2 | SC2 | none | dismissed | fixed README text; no data shape |
| E3 | SC3 | boundary | criterion SC3 | "one line" means one physical source line per bullet with no nested sub-bullet (owner ruling 3: 1行に揃える); the bibliography bullet describes the feature only (C4) |
| E4 | SC4 | none | dismissed | fixed README text; no data shape |
| E5 | SC5 | none | dismissed | fixed credit list named in the criterion (diagraph and typst-py added per C3) |
| E6 | SC6 | adjacency | criterion SC6 | README and manual disagree → manual wins, only README-only information is added (owner ruling 6: マニュアル優先) |
| E7 | SC6 | empty | criterion SC6 | a removed README item with no docs home is added to docs/source, never dropped (owner ruling 2: 移す), except the README Contributing content, which is deleted (C5) |
| E8 | SC7 | idempotency | criterion SC7 | warning comparison uses clean builds only; incremental rebuilds under-report warnings |
| E9 | SC8 | none | dismissed | single fixed CHANGELOG bullet |
| E10 | SC9 | none | dismissed | command results; no data shape |

## Prohibitions

| Prohibition | Criterion | Must not | Disposition | Detail |
|-------------|-----------|----------|-------------|--------|
| N1 | SC5 | drop upstream credits (Sphinx, Typst, mitex, codly, gentle-clues, diagraph, typst-py) from Acknowledgments | criterion SC5 | |
| N2 | SC6 | lose information removed from README without a home in the manual (README Contributing content excepted per C5) | criterion SC6 | |
| N3 | SC6 | replace moved content in the manual with a vague summary or a "see the source" pointer | judgment | final reviewer checks each moved item in docs/source states the concrete information (config values, code examples, constraints) README stated, not just a pointer |
| N4 | SC1 | none | dismissed | heading layout only; no values, safety, privacy, fairness or transparency stake |
| N5 | SC2 | none | dismissed | install/quick-start text; content preserved by SC2 and SC6 |
| N6 | SC3 | none | dismissed | bullet formatting; information preserved by SC6 |
| N7 | SC4 | none | dismissed | link-only sections; information preserved by SC6 |
| N8 | SC7 | none | dismissed | build check; affects no person beyond SC6 |
| N9 | SC8 | none | dismissed | one CHANGELOG bullet stating the change |
| N10 | SC9 | none | dismissed | test/lint results; affects no person directly |

## Scope: in

- Rewrite README.md to the section set and shapes in SC1–SC5.
- Add to docs/source (English) every removed README item the manual lacks (SC6); README Contributing content is deleted instead (C5).
- Update README-pinning tests (`test_quickstart_docs_gate.py`, `test_no_stale_github_io_links.py`, and any other gate that asserts removed README text) to the new README.
- One `[Unreleased]` CHANGELOG bullet.
- Resolve DOCS-AUDIT queue #1 (fix-doc: credit GSD Path).

## Scope: out (vetoes)

- #194 (option lists / classifiers / productionlist compile failure) — owner: "#194 は範囲外".
- Any release, version bump, tag, or PyPI publication — owner: "リリースは含めない".
- Japanese translation of moved docs content — owner ruling 5: "範囲外" (the translations repo follows separately).
- Product code changes under `typsphinx/`.
- Moving README Contributing content (step list, Development Guidelines) into the manual — owner: "コミュニティがちっちゃすぎるのであんまり縛るべきじゃない気がする" (C5).
- Reviewing or reorganising existing docs/source/contributing.rst content; only README-only Development items are added there — owner: "別マイルストーンで内容を整理します" (C7).
- Do not break: the README Status line and its version-sync gate; the Documentation section's Read the Docs link set and its gate; existing docs/source content the manual already states correctly (manual wins).

## Constraints

- Outward-facing text (README, docs, CHANGELOG) is English and terse.
- Integration is pull-request mode (STATE `integration: pull-request`); PR checks, merge and tag are not success criteria.
- Tests asserting warning text run under `LC_ALL=C`; docs warning baselines need clean builds.

## Current state (brownfield only)

- **What exists**: typsphinx 0.10.0, released (tag v0.10.0 at c1606cd9); Python ≥3.12, Sphinx ≥9.1,<10; 1897 passed / 1 skipped on 3.14, lint/type clean. README.md 348 lines; manual under docs/source (installation, quickstart, user_guide/*, examples, api, contributing, changelog), published on Read the Docs with ja translation.
- **Must not break**: Status-line version sync; Documentation link set; existing correct manual content.
- **Doc-vs-code rulings**: DOCS-AUDIT #1 (README.md:339 gsd-core credit) → fix-doc, "4: GSD Path に差し替え / #194 は範囲外 / リリースは含めない".
- **Ground truth**: `.project/research/evidence-codebase.md`, `.project/research/DOCS-AUDIT.md`

## Risks

- About ten tests read README.md; some assert removed text (Quick Start steps, Configuration Options `typst_documents` bullet). Missing one surfaces only in the full suite.
- Moved content may introduce new docs build warnings (cross-references, duplicate labels).
- Partial overlaps between README and manual (e.g. the mermaid `add_node` example vs templates.rst) need item-by-item comparison, not a section-level assumption.

## Open questions

- none

## Corrections

- C1 2026-11-04: "1: 概要、Feature、Requirements、Instllation(uvは残す)、Quick Start（Basic ConfigurationとExample Documents)、Documentation のリンク、Contributing（contributing.rst へのリンクだけ）、License、Acknowledgments、Status 行、Version Historyへのリンク / 2: 移す / 3: テストを直す / 4: GSD Path に差し替え / #194 は範囲外 / リリースは含めない"
- C2 2026-11-04: "1: 残す / 2: 移す / 3: 1行に揃える / 4: 足す / 5: 範囲外 / 6: マニュアル優先 / 7: 見出し一覧の完全一致 / 8: N1/N2 は成功条件、N3 は判断"
- C3 2026-11-04: "Featureにgraphvizがコンパイルできることを増やすべき。Acknowledgmentにはgraphvizのコンパイルをつかさどる、diagraphとtypstの実質的ビルドを受け持つtypst-pyも追加するべき"
- C4 2026-11-04: "FeatureのBibliographiesの説明はFeatureの説明に集中してシンプルにするべき"
- C5 2026-11-04: "Contributingの内容は消すことにしようかな(コミュニティがちっちゃすぎるのであんまり縛るべきじゃない気がする)。ここだけはマニュアルに移動するの例外としたい"
- C6 2026-11-04: "contributing.rstの内容を見直すことはこのマイルストーンでは触らない"
- C7 2026-11-04: (plan phase; rescinds C6) "C6を消します。つまりcontributing.rstを編集してよいです。別マイルストーンで内容を整理します。"
