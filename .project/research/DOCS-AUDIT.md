# Docs Audit

<!-- Written by the docs auditor (/gsd-path-docs-audit or /gsd-path-inspect).
     Every verdict carries evidence; a verdict without evidence is a defect. -->

Repo root: /home/yuta/Documents/typsphinx
Audited: 2026-11-07
Audited HEAD: a31fd6ca45bfb1a1873f3f191ca8fb565416e2e9
Alignment mode: no

Commands ran only in the supplied verify sidecar at the recorded HEAD, in a fresh
`.venv` from `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs`
(uv-managed CPython 3.14.4, `.venv/pyvenv.cfg` `version_info = 3.14`), with `LC_ALL=C`.
Build outputs went to the session scratchpad (`$O` below =
`/tmp/claude-1000/-home-yuta-Documents-typsphinx/c97f0df6-b939-4dcd-a14b-fd4bd3dfa7a7/scratchpad/ex`).
No Typst CLI is installed in this environment (`which typst` → not found); Typst CLI
compile claims were checked with `typst.compile(<path>)` from typst-py 0.15.0, which uses
the same compiler and the same default root (the input file's directory).

## Summary

| Verdict | Count |
|---------|-------|
| verified | 87 |
| stale | 2 |
| aspirational | 0 |
| unverifiable | 0 |
| descriptive docs (no testable claims) | 35 |

Worst drift: README.md states "Sphinx 9.1 or higher" and "typst-py 0.15.0 or higher", but `pyproject.toml:29,31` pins `sphinx>=9.1,<10` and `typst>=0.15.0,<0.16`, and `docs/source/installation.rst:8` and both example READMEs say "below 10" — the README is the one doc that omits the upper bound.

## Doc: AGENTS.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Run the first successful interpreter with `-B .gsd-path/status_runtime.py --repo <absolute-root>`" | command | verified | `.gsd-path/status_runtime.py` exists (13056 bytes); `python3 -B .gsd-path/status_runtime.py --repo /home/yuta/Documents/typsphinx` → valid JSON with keys `advance, completion, default_branch, git, handoff, ...`, `handoff.next` = "Invoke $gsd-path to continue with inspect." |

The rest of AGENTS.md describes GSD Path pipeline internals and the GSD Path source distribution (`plugin.json`, `skills/`, `scripts/sync_skill_resources.py`), which are claims about an installed dependency, not this product; they are out of scope.

## Doc: WORKFLOW.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Project installs record the selected runtime in `.gsd-path/runtime.json` and keep a stable launcher at `.gsd-path/status_runtime.py`" | structure | verified | `.gsd-path/runtime.json` exists: `{"digest": "e05c5aad…", "schema": "gsd-path/runtime/v1", "version": "1.7.1"}`; `.gsd-path/status_runtime.py` exists and runs (see AGENTS.md row) |

The rest of WORKFLOW.md is the GSD Path phase SOP and source-checkout layout (an installed dependency); out of scope.

## Doc: CLAUDE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`black --check .`" (CI lint command) | command | verified | `uv run black --check .` → "All done! 401 files would be left unchanged." |
| "`ruff check .`" | command | verified | `uv run ruff check --no-cache .` → "All checks passed!" |
| "`mypy typsphinx/`" | command | verified | `uv run mypy typsphinx/` → "Success: no issues found in 10 source files" |
| "`pytest` # run full suite (config in pyproject.toml)" | command | verified | `pyproject.toml:87` `testpaths = ["tests"]`, `:91` addopts; `LC_ALL=C uv run pytest -q -p no:cacheprovider -o addopts=""` → "1908 passed, 1 skipped in 218.30s", exit 0 |
| "`pytest -m \"not slow\"` # skip slow-marked tests" | config | verified | `pyproject.toml:92-93` registers marker `slow`; used at `tests/test_changelog_page_gate.py:165,214` |
| "`tox` # env_list: py312, py313, py314, lint, type, cov, docs" | config | verified | `tox.ini:2` `env_list = py312, py313, py314, lint, type, cov, docs` |
| "`tox -e docs-html` / `tox -e docs-pdf` / `tox -e linkcheck`" | config | verified | `tox.ini:67,75,92` define `[testenv:docs-html]`, `[testenv:docs-pdf]`, `[testenv:linkcheck]` |
| "Builders are auto-discovered via `sphinx.builders` entry points (declared in `pyproject.toml`)" | config | verified | `pyproject.toml:70-72` `[project.entry-points."sphinx.builders"]` `typst`/`typstpdf` |
| "`TypstBuilder` (`name=\"typst\"`) … `TypstPDFBuilder` (`name=\"typstpdf\"`) subclasses it" | structure | verified | `typsphinx/builder.py:691,699` and `:2698,2709` |
| "`_copy_used_template_bundles()` … `_write_dependencies_file()` … `_warn_template_dependency_drift()`" | structure | verified | all three defined/used in `typsphinx/builder.py` (grep) |
| "`TypstWriter.translate()` … `TypstWriter.render_wrapper()`" | structure | verified | `typsphinx/writer.py` defines `class TypstWriter`, `def translate`, `def render_wrapper` |
| "content `.typ` … two-line preamble `#import \"/_typsphinx/deps.typ\": *` + `#show: typsphinx-init`" | feature | verified | `$O/basic-typst/basic-example.typ:1-2` begins with exactly those two lines; `deps_preamble_lines` in `typsphinx/typst_deps.py` |
| "`TypstTranslator` (subclass of `SphinxTranslator`), the largest module" | structure | verified | `typsphinx/translator.py:512` `class TypstTranslator(SphinxTranslator)`; `wc -l` → translator.py 8078 lines, next largest builder.py 2858 |
| "`N802` is ignored in ruff" / "`E501` is ignored in ruff" / "Line length 88" | config | verified | `pyproject.toml:143` E501, `:147` N802, `:111,135` `line-length = 88` |
| "`typst_deps.py` — leaf module and the single source of the five `@preview` package specs (`DEFAULT_PACKAGES`)" | structure | verified | `typsphinx/typst_deps.py:26-27` imports only `re`, `dataclasses`; `:92-98` five specs; grep for the codly, mitex, gentle-clues and diagraph `@preview/` specs in other `typsphinx/*.py` and `templates/base.typ` finds only a docstring mention (`translator.py:6660`, no version) |
| "`template_registry.py` — `resolve_template_registry()` … `resolve_registry_key()` … `TemplateRegistryEntry`" | structure | verified | all defined in `typsphinx/template_registry.py` (grep) |
| "`removed_config.py` — `check_config_at_init()`, connected to `config-inited` … (`typst_template_assets`, `typst_authors`, `typst_toctree_defaults`, `typst_debug`)" | structure | verified | `typsphinx/__init__.py:74` `app.connect("config-inited", check_config_at_init)`; `typsphinx/removed_config.py:11-22` names all four |
| "`pathfmt.py` — leaf module with zero `typsphinx`-internal imports holding `quote_path()`" | structure | verified | `typsphinx/pathfmt.py:43` sole import `os`; `def quote_path` present |
| "`pdf.py` — `check_typst_available()`, `get_typst_version()`, … `TypstCompilationError`" | structure | verified | `typsphinx/pdf.py:59,80`; `class TypstCompilationError` present |
| "`tests/test_preview_version_sync.py` asserts …" | structure | verified | file exists at `tests/test_preview_version_sync.py` |
| "Every build generates `<outdir>/_typsphinx/deps.typ` … bundled `templates/base.typ` import that file" | feature | verified | `$O/basic-typst/_typsphinx/` present after build; `typsphinx/templates/base.typ:11` `#import "/_typsphinx/deps.typ": *` |
| "User-facing config values (all registered in `__init__.py`, prefix `typst_`) include `typst_documents`, `typst_template` / `typst_template_mapping` / `typst_template_function`, `typst_package` / `typst_package_imports`, `typst_dependencies`, `typst_use_mitex`, `typst_elements`" | config | verified | `typsphinx/__init__.py:45-63` `add_config_value` for each, plus `typst_document_templates` |
| "`tests/roots/` holds only `test-basic`"; "`conftest.py` also provides `sample_doctree` and `temp_sphinx_app`"; "`sphinx.testing.fixtures` is also loaded as a pytest plugin" | structure | verified | `ls tests/roots` → `test-basic`; `tests/conftest.py:12` `pytest_plugins = "sphinx.testing.fixtures"`, `:22`, `:46` |
| "Most tests are subprocess gates … running `sys.executable -m sphinx`" | structure | verified | 125 of 141 `tests/test_*_gate.py` files contain `sys.executable` (grep -c) |
| "`tox.ini` pins `tox-uv~=1.35`" and "`pyproject.toml`'s `dev` extra (the actual pin)" | config | verified | `tox.ini:17` `requires = tox-uv~=1.35`; `pyproject.toml:39` `"tox-uv>=1.35,<2"`; `tests/test_toolchain_config_gate.py:268` `test_dev_extra_pins_tox_uv_not_tox_uv_bare` |
| "CI … runs the test job on an ubuntu/windows/macos × py312/py313/py314 matrix, plus lint, type and cov jobs. A weekly `drift.yml` … files an issue … `release.yml` publishes to PyPI" | integration | verified | `.github/workflows/ci.yml:17-18` matrix; jobs `lint`, `type-check`, `coverage` (`:53,74,95`; also `build`, `integration`); `drift.yml:4` schedule, `:37-46` gh issue; `release.yml:127-133` `publish-pypi` → pypi.org/p/typsphinx |
| "PATH carries seven bare commands: `uv`, `tox`, `ruff`, `black`, `mypy`, `pytest` and `sphinx-build`" | integration | verified | `flake.nix:118-123` venvShims list tox/ruff/black/mypy/pytest/sphinx-build, `:146` `uvShim`; `grep -q typsphinx-fhs-run "$(command -v uv)"` → match |
| "Python 3.12+ is required. Annotations use builtin generics … not `typing.Dict`/`List`/…" | config | verified | `pyproject.toml:10` `requires-python = ">=3.12"`; no `from typing import` of Dict, List, Set, Tuple or Iterator in `typsphinx/*.py` (only `Any, NamedTuple` at `translator.py:9`) |
| "A fresh worktree's `.venv` is built on uv-managed CPython" | integration | verified | sidecar `.venv/pyvenv.cfg` `home = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin` |

## Doc: README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Standard docutils nodes … paragraphs, sections, lists, tables, admonitions" | feature | verified | `typsphinx/translator.py:1094` visit_section, `:2250` visit_bullet_list, `:4061` visit_table, `:6337` visit_admonition |
| "Mathematical expressions: LaTeX syntax via mitex, or native Typst math syntax" | feature | verified | `typsphinx/__init__.py:51` `typst_use_mitex`; README example build emits `mi(` / `mitex(` (`readme-ex/build/pdf/index.typ:17,21`) |
| "Code blocks with syntax highlighting: Using the codly package" | feature | verified | README example build emits `codly.new(raw(..., lang: "python"), ...)` (`index.typ:26`) |
| "Images and figures" / "Cross-references" | feature | verified | `typsphinx/translator.py:4700` visit_image, `:2897` visit_figure, `:5542` visit_reference |
| "Direct PDF generation: Self-contained PDF generation via typst-py (no external Typst CLI required)" | feature | verified | `sphinx-build -b typstpdf . $O/basic-pdf` → `basic-example.pdf` produced with no `typst` binary on PATH |
| "Multi-document support: … toctree integration using `#include()`" | feature | verified | `$O/adv-typst/index.typ:38-42` `include("chapter1.typ")` / `include("chapter2.typ")` |
| "Graphviz diagrams: `.. graphviz::`, `.. digraph::` and `.. graph::` … without a Graphviz installation" | feature | verified | `typsphinx/translator.py:6656-6662` visit_graphviz via diagraph `render`; `typsphinx/typst_deps.py:97` diagraph spec; `tests/test_graphviz_render_gate.py` in the passing suite |
| "Bibliographies and citations: Plain reStructuredText citations and sphinxcontrib-bibtex" | feature | verified | `typsphinx/translator.py:3668` visit_citation; `tests/test_bibtex_citation_render_gate.py`, `tests/test_citation_render_gate.py` in the passing suite |
| "Python 3.12 or higher" | config | verified | `pyproject.toml:10` `requires-python = ">=3.12"`; PyPI JSON `requires_python` = `>=3.12` |
| "Sphinx 9.1 or higher" | config | stale | `pyproject.toml:29` `"sphinx>=9.1,<10"`; `docs/source/installation.rst:8` "Sphinx 9.1 or later (below 10)"; `examples/basic/README.md:8`, `examples/advanced/README.md:31` "(below 10)"; README.md:35 omits the bound |
| "typst-py 0.15.0 or higher" | config | stale | `pyproject.toml:31` `"typst>=0.15.0,<0.16"`; README.md:36 omits the `<0.16` bound |
| "`pip install typsphinx`" | command | verified | PyPI JSON for typsphinx → version `0.10.0` |
| "`uv sync` … `uv sync --extra dev`" | command | verified | `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` in sidecar → completed, installs listed |
| "typsphinx is auto-discovered via entry points. Adding to extensions list is optional" | config | verified | `pyproject.toml:70-72`; README example project with `conf.py` lacking `extensions` built with `-b typstpdf` → `x.pdf` |
| "`typst_use_mitex = True` # Use mitex for LaTeX math (default: True)" | config | verified | `typsphinx/__init__.py:51` default `True` |
| "`sphinx-build -b typst source build/typst`" / "`sphinx-build -b typstpdf source build/pdf`" | command | verified | README example (`README.md:92-115`) saved as `readme-ex/source/index.rst`; `sphinx-build -q -b typstpdf source build/pdf` → `index.typ`, `x.typ`, `x.pdf`; examples built with `-b typst` likewise |
| "This will generate a Typst file with: Proper heading hierarchy, Formatted text with emphasis, LaTeX math via mitex, Syntax-highlighted code blocks with codly" | feature | verified | `readme-ex/build/pdf/index.typ:6,14,24` `heading(depth: 1/2)`, `:9,11` `strong`/`emph`, `:17,21` `mi`/`mitex`, `:26` `codly.new` |
| "Full documentation is available at typsphinx.readthedocs.io" and the Quick links (Installation, Quick Start, User Guide, Configuration Reference, Output Layout, Examples, API Reference, Contributing) | integration | verified | `curl -L` → HTTP 200 for each `/en/latest/` page; sources exist under `docs/source/` |
| "日本語ドキュメントは typsphinx.readthedocs.io/ja/latest/ にあります" | integration | verified | `curl` `https://typsphinx.readthedocs.io/ja/latest/` → 200 |
| "MIT License - see LICENSE" | config | verified | `LICENSE` exists; `pyproject.toml:11` `license = "MIT"` |
| "Uses gentle-clues for admonitions" / "diagraph to render Graphviz" / "typst-py to perform the Typst compilation" | integration | verified | `typsphinx/typst_deps.py:96-97`; `pyproject.toml:31`; `typsphinx/pdf.py:110-155` |
| "**Status**: Stable (v0.10.0)" | status | verified | `pyproject.toml:7` `version = "0.10.0"`; tag `v0.10.0` exists; PyPI latest 0.10.0 |
| "**Python**: 3.12+ \| **Sphinx**: 9.1+ \| **Typst**: 0.15+" | config | verified | `pyproject.toml:10,29,31`; the "+" shorthand matches the lower bounds (the missing upper bound is recorded on the Requirements rows) |

## Doc: CHANGELOG.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "[Unreleased] … README simplified: configuration, advanced usage and development details moved to the manual" | status | verified | `git log` → `28d0e7d9 T002: Rewrite README.md to the approved shape`; README.md now 167 lines and links to RTD pages for configuration/output layout/contributing |
| "Planned for Future Releases: Index generation / Pre-commit hooks / Additional Typst Universe template integration" | status | verified | still unbuilt as stated: `typsphinx/translator.py:6515-6521` visit_index raises `SkipNode` ("we don't generate indices"); no `.pre-commit-config.yaml` in repo root |
| "[0.10.0] … `<outdir>/_typsphinx/deps.typ` … imports the five Typst Universe packages … defines `typsphinx-init`" | feature | verified | `$O/basic-typst/_typsphinx/` written; `typsphinx/typst_deps.py:92-98,118-123` |
| "New `typst_dependencies` configuration value … validated before any `.typ` file is written" | config | verified | `typsphinx/__init__.py:49`; `typsphinx/builder.py:1766-1768` `_validate_typst_dependencies()` before writing |
| "Template dependency drift warning … (`template dependency drift: ...`)" | feature | verified | `typsphinx/builder.py:2606` |
| "Python 3.14 support … classifier, CI test matrix … tox (`py314`)" | config | verified | `pyproject.toml:23`; `.github/workflows/ci.yml:18,24-25`; `tox.ini:2` |
| "codly is upgraded from 1.3.0 to 2.0.0 (`@preview/codly:2.0.0`)" | config | verified | `typsphinx/typst_deps.py:93` |
| Release headings `## [x.y.z]` each have a `[x.y.z]:` release link and a matching `v` tag; `[Unreleased]` compares from v0.10.0 | structure | verified | loop over all 27 headings: every version has a `^[v]:` link and `git rev-parse refs/tags/v<v>` succeeds (0.1.0b1 → `CHANGELOG.md:1676`, tag `v0.1.0b1`); `CHANGELOG.md:1677` `[Unreleased]: …/compare/v0.10.0...HEAD` |

Older release sections are dated history records of what each release contained (for example 0.1.0b1's "Python: ≥3.9", "286 tests"); they describe past states, not current behaviour, and were not re-audited as present-tense claims.

## Doc: examples/basic/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Python 3.12 or higher; Sphinx 9.1 or higher (below 10)" | config | verified | `pyproject.toml:10,29` |
| "`sphinx-build -b typst . _build/typst`" creates "`basic-example.typ` … and `index.typ` … template … copied to `_build/typst/_template/typst/`" | command | verified | `cd examples/basic && sphinx-build -q -b typst . $O/basic-typst` → rc 0 (only warning: missing `_static`), outputs `basic-example.typ`, `index.typ`, `_template/typst/{base.typ,README.md}`, `_typsphinx/` |
| "`sphinx-build -b typstpdf . _build/pdf`" creates both `.typ` and `.pdf` | command | verified | `$O/basic-pdf` → `basic-example.typ`, `index.typ`, `basic-example.pdf` |
| "`typst compile _build/typst/basic-example.typ output.pdf`" | command | verified | Typst CLI absent; `typst.compile('$O/basic-typst/basic-example.typ')` (typst-py 0.15.0, default root = file dir) → 83205-byte `%PDF-` |
| Project structure: `conf.py`, `index.rst`, `README.md` | structure | verified | `find examples/basic` → exactly those three files |
| "`extensions = ['typsphinx']`, `typst_documents`, `typst_use_mitex`" in conf.py | config | verified | `examples/basic/conf.py` sets all three |
| Features demonstrated: formatting, lists, code blocks, math, tables, links | feature | verified | `examples/basic/index.rst:23,54,64` code-block, `:75-79` math, `:88` list-table, `:114-115` external links |

## Doc: examples/advanced/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| Project structure incl. `_typst/custom.typ`, `chapter1.rst`, `chapter2.rst` | structure | verified | `find examples/advanced` → conf.py, index.rst, chapter1.rst, chapter2.rst, `_typst/custom.typ`, README.md |
| "`sphinx-build -b typst . _build/typst`" generates `advanced-example.typ`, `index.typ`, `chapter1.typ`, `chapter2.typ`, `_template/typst/custom.typ` | command | verified | `sphinx-build -q -b typst . $O/adv-typst` → exactly those files plus `_typsphinx/` |
| "`sphinx-build -b typstpdf . _build/pdf`" creates both `.typ` and `.pdf` | command | verified | `$O/adv-pdf/advanced-example.pdf` present |
| "`typst_template = \"_typst/custom.typ\"`" is enabled in conf.py | config | verified | `examples/advanced/conf.py` sets it |
| Toctree guard `context { set heading(offset: heading.offset + 1) if "index#0>chapter1" in state("typsphinx:include-edges", ()).get() { include("chapter1.typ") } … }` | feature | verified | `$O/adv-typst/index.typ:38-42` matches verbatim |
| "Inline: `:math:`E = mc^2`` → ``mi(`E = mc^2`)``" | feature | verified | `$O/adv-typst/index.typ:108` `mi(`E = mc^2`)` |
| Admonitions: note→info, warning→warning, tip→tip, important→warning titled "Important", seealso→tip titled "See also" | feature | verified | `typsphinx/translator.py:6200-6250` mapping; `$O/adv-typst/chapter2.typ:254-275` emits `info(…, title: "Note")`, `warning(…, title: "Warning")`, `warning(…, title: "Important")`, `tip(…)` (code-mode calls with a title argument, same functions as the README's `#info[]` shorthand) |
| typst_elements "Allowlisted keys only (papersize / fontsize / lang) … `_typst/custom.typ` declares all three" | config | verified | `examples/advanced/conf.py` `typst_elements` = papersize/fontsize/lang; build succeeds and PDF compiles (`$O/adv-pdf/advanced-example.pdf`) |
| "See Configuration Reference (../../docs/source/user_guide/configuration.rst)" | structure | verified | `docs/source/user_guide/configuration.rst` exists |

## Doc: examples/charged-ieee/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| Approach 1 uses `typst_template_function` with `name: "ieee"` and `params` incl. title/abstract/index-terms/paper-size/authors | config | verified | `examples/charged-ieee/approach1/conf.py` `typst_template_function` matches; `typst_package = "@preview/charged-ieee:0.1.4"` |
| Approach 2 custom template `#import "@preview/charged-ieee:0.1.4": ieee` with `project(...)` mapping authors | structure | verified | `examples/charged-ieee/approach2/source/_typst/_template.typ:1-30` |
| "`cd approach1; sphinx-build -b typst -c . source build/typst; cd build/typst; typst compile paper.typ output.pdf`" (and same for approach2) | command | verified | both `sphinx-build -q -b typst -c . source $O/ieee-approachN` → `paper.typ`, `index.typ`; Typst CLI absent, `typst.compile(paper.typ)` → 77760-byte PDF for each |
| "Both approaches produce identical output when configured correctly" | feature | verified | `typst.compile(approach1/paper.typ) == typst.compile(approach2/paper.typ)` → `True` |
| "Approach 2 … hardcodes the department, organization and location for every author and derives each email from the author's name" | feature | verified | `approach2/source/_typst/_template.typ:31-33` hardcoded organization/location, `email: lower(name.split(" ").at(0)) + ".doe@mit.edu"` |
| "Setting both `typst_package` and `typst_template` is unsupported: the build warns and ignores `typst_package`, honouring `typst_template`" | feature | verified | `typsphinx/builder.py:2443-2450` warning "'typst_template' will be honoured and 'typst_package' will be ignored." |

## Doc: typsphinx/templates/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "every file in it, not just `base.typ`, is copied wholesale to `<outdir>/_template/typst/`" | feature | verified | `$O/basic-typst/_template/typst/` contains `base.typ` and `README.md` |
| "place a file at `<srcdir>/_typst/base.typ` … typsphinx finds it automatically" | feature | verified | `typsphinx/template_engine.py:41` `TEMPLATE_SEARCH_SUBDIR = "_typst"`; `typsphinx/writer.py:389`, `typsphinx/builder.py:1576,2461` search `srcdir/_typst` |
| "`README.md` … is also the wheel-content canary for the packaging check in `.github/workflows/ci.yml`" | integration | verified | `.github/workflows/ci.yml:153-171` "Verify wheel carries the template bundle", target `typsphinx/templates/README.md` |
| "the bundle's only non-`.typ` file" | structure | verified | `ls typsphinx/templates` → `README.md`, `base.typ` |
| "Register your own bundle with a `typst_document_templates` entry … select it per document via the fifth element of `typst_documents`" | config | verified | `typsphinx/__init__.py:63` `typst_document_templates`; `typsphinx/template_registry.py` `resolve_registry_key`; `examples/charged-ieee/approach*/conf.py` use fifth element `"typst"` |

## Descriptive docs

<!-- Every inventoried doc with no testable claims, one path per line.
     The union of this list and the Doc section paths must equal the frozen
     inventory exactly. -->

- .agents/skills/async-python-patterns/SKILL.md
- .agents/skills/async-python-patterns/references/details.md
- .agents/skills/code-review-excellence/SKILL.md
- .agents/skills/deployment-pipeline-design/SKILL.md
- .agents/skills/deployment-pipeline-design/references/advanced-strategies.md
- .agents/skills/deployment-pipeline-design/references/details.md
- .agents/skills/docx/SKILL.md
- .agents/skills/error-handling-patterns/SKILL.md
- .agents/skills/error-handling-patterns/references/details.md
- .agents/skills/find-skills/SKILL.md
- .agents/skills/git-advanced-workflows/SKILL.md
- .agents/skills/git-advanced-workflows/references/details.md
- .agents/skills/github-actions-templates/SKILL.md
- .agents/skills/pdf/SKILL.md
- .agents/skills/pdf/forms.md
- .agents/skills/pdf/reference.md
- .agents/skills/pptx/SKILL.md
- .agents/skills/python-performance-optimization/SKILL.md
- .agents/skills/python-performance-optimization/references/advanced-patterns.md
- .agents/skills/python-performance-optimization/references/details.md
- .agents/skills/python-testing-patterns/SKILL.md
- .agents/skills/python-testing-patterns/references/advanced-patterns.md
- .agents/skills/python-testing-patterns/references/details.md
- .agents/skills/secrets-management/SKILL.md
- .agents/skills/skill-creator/SKILL.md
- .agents/skills/skill-creator/agents/analyzer.md
- .agents/skills/skill-creator/agents/comparator.md
- .agents/skills/skill-creator/agents/grader.md
- .agents/skills/skill-creator/references/schemas.md
- .agents/skills/sql-code-review/SKILL.md
- .agents/skills/sql-optimization/SKILL.md
- .agents/skills/uv-package-manager/SKILL.md
- .agents/skills/uv-package-manager/references/advanced-patterns.md
- .agents/skills/xlsx/SKILL.md
- tests/fixtures/state_guard_shapes_evidence/49-SHAPES-RED-EVIDENCE.md

Scope: the `.agents/skills/` files are third-party agent skill bundles installed from external sources (`skills-lock.json` records each `source`, e.g. `wshobson/agents`, with a `computedHash`); their contents describe those dependencies, not typsphinx. The `49-SHAPES-RED-EVIDENCE.md` file is a dated, verbatim pre-fix evidence record read as fixture data by `tests/test_include_ledger_removal_gate.py:107` and `tests/test_state_guard_shapes_gate.py`; it records past output, not present-tense claims.

## Alignment (alignment mode only)

Not applicable — alignment mode is false for this run.

## User rulings

<!-- Appended after the ruling walk (standalone runs). Verbatim, append-only.
     accept-drift rulings suppress the item in future audits.
     `planned: no` rows are the alignment queue: /gsd-path and /gsd-path-plan offer
     to absorb them until drained. When a ruling becomes a task, set
     planned to the task id — never delete the row. -->

| Queue # | Ruling | User's words | Planned |
|---------|--------|--------------|---------|
| 1 | fix-doc | "3: A" | T002 |
| 2 | fix-doc | "3: A" | T002 |

## Remediation queue

<!-- Every non-verified claim, classified. The user rules on this queue;
     the auditor never fixes anything.
     Numbers are unique and strictly increasing, not necessarily contiguous.
     A persisting row keeps its number; a new row takes a number above every
     prior queue number and every User rulings Queue #. Never reuse a retired
     number: a ruling stays bound to the item it was made for. -->

| # | Doc | Claim | Verdict | Class | Suggested action |
|---|-----|-------|---------|-------|------------------|
| 1 | README.md | "Sphinx 9.1 or higher" | stale | fix-doc | Evidence: README.md:35 vs `pyproject.toml:29` `<10`; state "Sphinx 9.1 or higher (below 10)" as installation.rst:8 and the example READMEs do |
| 2 | README.md | "typst-py 0.15.0 or higher" | stale | fix-doc | Evidence: README.md:36 vs `pyproject.toml:31` `<0.16`; state the `<0.16` upper bound |
