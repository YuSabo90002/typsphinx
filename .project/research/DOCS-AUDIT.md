# Docs Audit

<!-- Written by the docs auditor (/gsd-path-docs-audit or /gsd-path-inspect).
     Every verdict carries evidence; a verdict without evidence is a defect. -->

Repo root: /home/yuta/Documents/typsphinx
Audited: 2026-11-03
Audited HEAD: 81af8d6b2bd538e99747f65e78c366946d7b81d1
Alignment mode: no

Command evidence below was produced in the verify sidecar at the audited HEAD after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` (uv-managed CPython 3.14.4). Example builds were written to a scratch directory outside the repository (`-d`/outdir both outside the tree).

## Summary

| Verdict | Count |
|---------|-------|
| verified | 71 |
| stale | 3 |
| aspirational | 0 |
| unverifiable | 0 |
| descriptive docs (no testable claims) | 36 |

Worst drift: examples/charged-ieee/README.md says "Both approaches produce identical output when configured correctly", but the two shipped example configurations compile to PDFs whose text differs (approach1's triple-quoted `ieee_abstract` keeps its hard line breaks; approach2's template abstract reflows).

## Doc: README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Python 3.12 or higher / Sphinx 9.1 or higher / typst-py 0.15.0 or higher" | config | verified | pyproject.toml:10 `requires-python = ">=3.12"`, :29 `sphinx>=9.1,<10`, :31 `typst>=0.15.0,<0.16` |
| "LaTeX syntax via mitex (`@preview/mitex:0.2.7`)" / "codly package (`@preview/codly:2.0.0`)" | integration | verified | typsphinx/typst_deps.py DEFAULT_PACKAGES (lines 92-98): `@preview/codly:2.0.0`, `@preview/mitex:0.2.7` |
| "Direct PDF generation: Self-contained PDF generation via typst-py (no external Typst CLI required)" | feature | verified | `command -v typst` → none on PATH; `uv run sphinx-build -b typstpdf` on examples/basic, examples/advanced, charged-ieee approach1/2 each produced a `.pdf` |
| "Multi-document support: Generate multiple Typst files with toctree integration using `#include()`" | feature | verified | examples/advanced typst build → index.typ:40-41 `include("chapter1.typ")`, `include("chapter2.typ")` |
| "`typst_use_mitex = True  # Use mitex for LaTeX math (default: True)`" | config | verified | typsphinx/__init__.py:51 `add_config_value("typst_use_mitex", True, ...)` |
| "When unset, typsphinx derives a single entry from `root_doc`, `project`, and `author` ... same filename helper Sphinx's own LaTeX builder uses" | config | verified | typsphinx/builder.py:21 imports `make_filename_from_project`; :669-683 `_default_typst_documents` uses it + ".typ"; __init__.py:45 registers it as callable default; tests/test_default_typst_documents_derivation.py passed in full suite |
| "sphinx-build -b typst source build/typst" / "sphinx-build -b typstpdf source build/pdf" | command | verified | both builders ran successfully on all four example projects (outputs listed under the examples docs below) |
| "Keys are Sphinx metadata names; values are the template parameter names they map to." | config | verified | typsphinx/template_engine.py:535 `for sphinx_key, template_key in self.parameter_mapping.items()` |
| "Unknown nodes trigger `unknown_visit()` which logs a warning and extracts text content" | feature | verified | typsphinx/translator.py:5804-5815 `unknown_visit` logs `unknown node type: ...` |
| "main configuration options ... `typst_documents`, `typst_use_mitex`, `typst_template`, `typst_elements`, `typst_template_mapping`" | config | verified | typsphinx/__init__.py:45-52 registers all five |
| "uv run tox -e lint / type / py312 / docs-html / docs-pdf / docs / linkcheck" | command | verified | tox.ini:2 env_list and sections `[testenv:lint]`:45, `type`:53, `docs-html`:67, `docs-pdf`:75, `docs`:83 (html + typstpdf), `linkcheck`:92 |
| "Ensure all tests pass: `uv run pytest`" | command | verified | `LC_ALL=C uv run pytest -q` → `1881 passed, 1 skipped in 221.45s` |
| "Use black for code formatting" | command | verified | `uv run black --check .` → `398 files would be left unchanged.` |
| "Project Structure: builder.py, writer.py, translator.py, template_engine.py, pdf.py, typst_deps.py, templates/" | structure | verified | `ls typsphinx` lists all named files plus templates/ (also pathfmt.py, removed_config.py, template_registry.py, not listed; the tree is not claimed exhaustive) |
| "Bibliographies ... typsphinx does not depend on it [sphinxcontrib-bibtex]" / "See docs/source/user_guide/bibliography.rst" | config | verified | pyproject.toml:28-32 runtime deps are sphinx, docutils, typst only; sphinxcontrib-bibtex is dev-only (:54); docs/source/user_guide/bibliography.rst exists |
| "Documentation quick links (Installation, Quick Start, User Guide, Configuration, Output Layout, Examples, API, Contributing, ja/latest)" | integration | verified | `curl -L -o /dev/null -w '%{http_code}'` → 200 for all nine URLs |
| "Status: Stable (v0.9.8)" | status | verified | pyproject.toml:7 `version = "0.9.8"`; `git tag` contains v0.9.8; CHANGELOG.md:89 `## [0.9.8] - 2026-11-03` |

## Doc: CLAUDE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "black --check . / ruff check . / mypy typsphinx/" | command | verified | black → `398 files would be left unchanged.`; ruff → `All checks passed!`; mypy → `Success: no issues found in 10 source files` |
| "pytest -m \"not slow\"  # skip slow-marked tests" | command | verified | pyproject.toml:93 defines `slow` marker; `uv run pytest --collect-only -q -m "not slow"` → `1783/1882 tests collected (99 deselected)` |
| "env_list: py312, py313, py314, lint, type, cov, docs" | config | verified | tox.ini:2 `env_list = py312, py313, py314, lint, type, cov, docs` |
| "tox -e docs-html (HTML via furo) / docs-pdf (typstpdf) / linkcheck" | command | verified | tox.ini:67-98; docs/source/conf.py:71 `html_theme = "furo"` |
| "`_copy_used_template_bundles()`, `_write_dependencies_file()`, `_warn_template_dependency_drift()`; TypstBuilder name=typst, TypstPDFBuilder name=typstpdf" | structure | verified | typsphinx/builder.py:699, 2332, 2532, 2553, 2611, 2709, 2721 |
| "TypstWriter.translate() ... two-line preamble ... `TypstWriter.render_wrapper()`" | structure | verified | typsphinx/writer.py:235, 266 (`deps_preamble_lines()`), 270; example output advanced-example.typ lines 1-2 `#import "/_typsphinx/deps.typ": *` / `#show: typsphinx-init` |
| "TypstTranslator (subclass of SphinxTranslator) ... `N802` is ignored in ruff" | structure | verified | typsphinx/translator.py:512; pyproject.toml:147 |
| "template_engine.py ... hard-codes no `@preview` package version" | structure | verified | `grep -n @preview typsphinx/template_engine.py` → only a docstring example `@preview/charged-ieee:0.1.0` (line 279), none of the five |
| "typst_deps.py — single source of the five `@preview` package specs (`DEFAULT_PACKAGES`), `render_default_deps()`, `deps_preamble_lines()`; leaf module" | structure | verified | typsphinx/typst_deps.py:26-27 imports only re/dataclasses; :92, :114, :133 |
| "template_registry.py — `resolve_template_registry()`, `TemplateRegistryEntry`, `resolve_registry_key()`" | structure | verified | typsphinx/template_registry.py:181, 213, 494 |
| "removed_config.py — `check_config_at_init()`, connected to `config-inited` ... (`typst_template_assets`, `typst_authors`, `typst_toctree_defaults`, `typst_debug`)" | structure | verified | typsphinx/removed_config.py:11-22, 40-54; typsphinx/__init__.py:74 `app.connect("config-inited", check_config_at_init)` |
| "pathfmt.py — leaf ... `quote_path()` used by builder.py, writer.py, translator.py and template_registry.py" | structure | verified | typsphinx/pathfmt.py:43 only `import os`, :46 def; `grep -l quote_path typsphinx/*.py` → builder, writer, translator, template_registry, pathfmt |
| "pdf.py — `check_typst_available()`, `get_typst_version()`, `TypstCompilationError`" | structure | verified | typsphinx/pdf.py:15, 59, 80 |
| "tests/test_preview_version_sync.py asserts ... repository's own templates pin none of the five" | feature | verified | test file exists and passed (7 tests) in full suite; docs/source/_typst/*.typ and examples/advanced/_typst/custom.typ contain no `@preview` import (custom.typ:12 imports `/_typsphinx/deps.typ`) |
| "User-facing config values ... `typst_documents`, `typst_template`, `typst_template_mapping`, `typst_template_function`, `typst_package`, `typst_package_imports`, `typst_dependencies`, `typst_use_mitex`, `typst_elements`" | config | verified | typsphinx/__init__.py:45-63 (plus `typst_document_templates`) |
| "`tests/roots/` holds only `test-basic` ... `conftest.py` also provides `sample_doctree` and `temp_sphinx_app`; `sphinx.testing.fixtures` loaded as plugin" | structure | verified | `ls tests/roots` → test-basic; tests/conftest.py:12, 22, 46 |
| "`tox.ini` pins `tox-uv~=1.35` ... `pyproject.toml`'s `dev` extra (the actual pin) ... `test_dev_extra_pins_tox_uv_not_tox_uv_bare`" | config | verified | tox.ini:15 `requires = tox-uv~=1.35`; pyproject.toml:39 `tox-uv>=1.35,<2`; tests/test_toolchain_config_gate.py:268 exists and passed |
| "CI runs the test job on an ubuntu/windows/macos × py312/py313/py314 matrix, plus lint, type and cov jobs. A weekly `drift.yml` ... files an issue ... `release.yml` publishes to PyPI." | integration | verified | .github/workflows/ci.yml:17-25, 72, 93, 114; drift.yml:4-5 cron `0 0 * * 1`, :37-43 `gh issue`; release.yml:15 PyPI trusted publishing, :114 twine |
| "PATH carries seven bare commands ... runs it inside an FHS sandbox (`typsphinx-fhs-run`)" / "`grep -q typsphinx-fhs-run \"$(command -v uv)\"`" | integration | verified | flake.nix:66 `typsphinx-fhs-run`, :118-123 six venv shims, :146 uvShim; running the check command on this host → exit 0 |
| "Line length 88 (black); `E501` is ignored in ruff" | config | verified | pyproject.toml:111, 135, 143 |

## Doc: CHANGELOG.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Every content file and every wrapper now starts with `#import \"/_typsphinx/deps.typ\": *` and `#show: typsphinx-init`" | feature | verified | examples/advanced typst build: advanced-example.typ, index.typ, chapter1.typ, chapter2.typ all begin with those two lines; `_typsphinx/deps.typ` written in every outdir |
| "New `typst_dependencies` configuration value" | config | verified | typsphinx/__init__.py:49; tests/test_typst_dependencies_gate.py passed (13 tests) |
| "Breaking: codly is upgraded from 1.3.0 to 2.0.0 ... Every code block is now one code-mode `codly.new(raw(...), ...)` expression" | feature | verified | typst_deps.py DEFAULT_PACKAGES `@preview/codly:2.0.0` alias codly; advanced chapter2.typ:244-248 `codly.new(raw("...", block: true, lang: "rust"), number-enabled: false)` |
| "The docs template, the `examples/advanced` template and the test-fixture templates import from `/_typsphinx/deps.typ`" | structure | verified | examples/advanced/_typst/custom.typ:12; typsphinx/templates/base.typ:11; test_preview_version_sync.py passed |
| "0.9.8: `.. graphviz::` ... rendered through the Typst `@preview/diagraph` package" | feature | verified | typst_deps.py DEFAULT_PACKAGES `@preview/diagraph:0.3.7` items `render` |
| "0.9.8 ... removes the inert `typst_debug` configuration value" | config | verified | typsphinx/__init__.py:45-63 registers no `typst_debug`; typsphinx/removed_config.py:22 warns for it |
| "Planned for Future Releases: Index generation / Pre-commit hooks" | status | verified | still unbuilt: no `.pre-commit-config.yaml` at repo root (`ls -a`); CHANGELOG.md:1518 "Index generation not yet supported" |
| "Version sections and compare/tag link block (Unreleased ... 0.1.0b1)" | status | verified | 25 `## [x.y.z]` headings ↔ 25 `v*` tags from `git tag`; 25 `[x.y.z]:` release links plus `[Unreleased]: .../compare/v0.9.8...HEAD` |
| "The format is based on Keep a Changelog" (newest-first ordering) | structure | stale | CHANGELOG.md:1389 `## [0.1.0b1] - 2025-10-13` precedes CHANGELOG.md:1562 `## [0.2.0] - 2025-10-16`; every other section is newest-first |

## Doc: examples/basic/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "sphinx-build -b typst . _build/typst ... create two files at the root of `_build/typst/`: `basic-example.typ` ... and `index.typ` ... template ... copied to `_build/typst/_template/typst/`" | command | verified | build output root: basic-example.typ, index.typ; subdirs `_template/typst/{base.typ,README.md}`, `_typsphinx/deps.typ` |
| "sphinx-build -b typstpdf . _build/pdf ... create both `.typ` and `.pdf` files" | command | verified | output contains basic-example.typ, index.typ, basic-example.pdf |
| "typst compile _build/typst/basic-example.typ output.pdf" | command | verified | Typst CLI absent; equivalent `uv run python -c "typst.compile('<outdir>/basic-example.typ', output=...)"` (typst-py, default root = file dir) → succeeded |
| "conf.py contains `extensions = ['typsphinx']`, `typst_documents`, `typst_use_mitex`" | config | verified | examples/basic/conf.py: `extensions = ["typsphinx"]`, `typst_documents = [("index", "basic-example.typ", ...)]`, `typst_use_mitex = True` |
| "Project Structure: conf.py, index.rst, README.md" | structure | verified | `ls examples/basic` → README.md conf.py index.rst |

## Doc: examples/advanced/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "This will generate: advanced-example.typ, index.typ, chapter1.typ, chapter2.typ, `_template/typst/custom.typ`" | command | verified | `sphinx-build -b typst` outdir contains exactly those plus `_typsphinx/deps.typ` |
| "sphinx-build -b typstpdf . _build/pdf ... creates both `.typ` and `.pdf` files" | command | verified | outdir contains advanced-example.pdf plus the .typ files |
| "compile-time guard ... `context { set heading(offset: heading.offset + 1)` ... `if \"index#0>chapter1\" in state(\"typsphinx:include-edges\", ()).get()`" | feature | verified | generated index.typ:38-42 matches the snippet byte-for-byte; wrapper publishes `#state("typsphinx:include-edges", ()).update(("index#0>chapter1", "index#0>chapter2",))` |
| "Inline: `:math:` → ``mi(`E = mc^2`)`` (emitted in code mode, so no `#` prefix)" | feature | verified | generated chapter2.typ:60 `mi(\`\pi\`)` without `#` |
| "note → #info[]; warning → #warning[]; tip → #tip[]; important → #warning(title: \"Important\"); seealso → #tip[] with \"See also\" title" | feature | verified | chapter2.typ:254 `info(...)`, warning box `warning(..., title: "Warning")`, important `warning(..., title: "Important")`, `tip(...)`; translator.py:6244-6250 `visit_seealso` → `_visit_admonition(node, "tip")` |
| "The custom template is already enabled in `conf.py` by: `typst_template = \"_typst/custom.typ\"`" | config | verified | examples/advanced/conf.py last setting `typst_template = "_typst/custom.typ"` |
| "Allowlisted keys only (papersize / fontsize / lang); any other key aborts the build ... _typst/custom.typ declares all three" | config | verified | typsphinx/template_engine.py:101, 526 ELEMENTS_ALLOWLIST; examples/advanced/_typst/custom.typ:101-103 declares papersize, fontsize, lang |
| "Project Structure: conf.py, index.rst, chapter1.rst, chapter2.rst, _typst/custom.typ, README.md" | structure | verified | `find examples/advanced -type f` lists exactly those six files |

## Doc: examples/charged-ieee/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Approach 1 ... Location: `approach1/`" / "Approach 2 ... Location: `approach2/`" | structure | verified | examples/charged-ieee/approach1/{conf.py,source/index.rst}; approach2/{conf.py,source/index.rst,source/_typst/_template.typ} |
| "cd approach1 / approach2; sphinx-build -b typst -c . source build/typst; cd build/typst; typst compile paper.typ output.pdf" | command | verified | both builds emit paper.typ + index.typ; `typst.compile('<outdir>/paper.typ', ...)` via typst-py succeeded for both (Typst CLI absent); `-b typstpdf` also produced paper.pdf for both |
| "typst_template_function = {\"name\": \"ieee\", \"params\": {title, abstract, index-terms, paper-size, authors}}" | config | verified | examples/charged-ieee/approach1/conf.py `typst_template_function` has exactly those five params; `typst_package = "@preview/charged-ieee:0.1.4"` |
| "Custom Template Example: `#import \"@preview/charged-ieee:0.1.4\": ieee` / `#let project(title, authors, body)` mapping authors" | structure | verified | approach2/source/_typst/_template.typ:5, 7-34 |
| "Both approaches produce identical output when configured correctly" | feature | stale | pypdf text extraction of the two shipped examples' typstpdf output: approach1 5227 chars vs approach2 5229, not equal; diff is the abstract — approach1 keeps the hard newlines of the triple-quoted `ieee_abstract` (approach1/conf.py), approach2's template abstract (_template.typ:37-42) reflows |
| "This example demonstrates two approaches for using the charged-ieee Typst Universe template with sphinx-typst" | structure | stale | README lines 3, 7 and 150 name the project "sphinx-typst"; pyproject.toml:6 `name = "typsphinx"` and the link at line 150 points at the typsphinx repository |
| "Approach 2 ... hardcodes the department, organization and location for every author and derives each email from the author's name" | feature | verified | approach2/source/_typst/_template.typ:28-34 |
| "Setting both `typst_package` and `typst_template` is unsupported: the build warns and ignores `typst_package`, honouring `typst_template`" | feature | verified | typsphinx/builder.py:2443-2450 warning "'typst_template' will be honoured and 'typst_package' will be ignored." |

## Doc: typsphinx/templates/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "every file in it, not just `base.typ`, is copied wholesale to `<outdir>/_template/typst/` on every build" | feature | verified | examples/basic typst and typstpdf outdirs both contain `_template/typst/base.typ` and `_template/typst/README.md` |
| "`README.md` (this file) — the bundle's only non-`.typ` file" | structure | verified | `ls typsphinx/templates` → README.md base.typ |
| "it is also the wheel-content canary for the packaging check in `.github/workflows/ci.yml`" | integration | verified | .github/workflows/ci.yml:153-170 opens the built wheel and fails if `typsphinx/templates/README.md` is missing |
| "place a file at `<srcdir>/_typst/base.typ` ... typsphinx finds it automatically (a \"shadow\" of this file)" | feature | verified | typsphinx/template_engine.py:41 `TEMPLATE_SEARCH_SUBDIR = "_typst"`; typsphinx/writer.py search_paths `os.path.join(srcdir, TEMPLATE_SEARCH_SUBDIR)`; tests/test_template_engine.py passed in full suite |
| "Register your own bundle with a `typst_document_templates` entry ... select it per document via the fifth element of the corresponding `typst_documents` entry" | config | verified | typsphinx/__init__.py:63; typsphinx/template_registry.py:494 `resolve_registry_key()`; charged-ieee approach1/2 conf.py use fifth element `"typst"` and build |

## Doc: tests/fixtures/state_guard_shapes_evidence/49-SHAPES-RED-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`tests/test_state_guard_shapes_gate.py`'s \"no lost diagnostics\" test can assert every warning recorded here is still present post-fix" | integration | verified | tests/test_state_guard_shapes_gate.py:59-60 `EVIDENCE_PATH` points at this file; also read by tests/test_include_ledger_removal_gate.py:107; both passed in full suite (18 tests in the shapes gate) |
| "Reproduction command shape: `uv run python -m sphinx -b typst tests/fixtures/<fixture> <build-dir>`" | command | verified | the shapes gate invokes `sys.executable -m sphinx` under `uv run pytest` and passed; fixture dirs (e.g. tests/fixtures/state_guard_self_and_url_gate/conf.py) exist |

## Descriptive docs

The `.agents/skills/**` files are third-party agent skill bundles (recorded in `skills-lock.json`) that describe generic techniques, not this repository's product; AGENTS.md and WORKFLOW.md describe the installed GSD Path pipeline, a dependency whose source distribution and internals are out of scope in this application. None carries a typsphinx product claim.

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
- AGENTS.md
- WORKFLOW.md

## Alignment (alignment mode only)

Not run: alignment mode is false for this inspection.

## User rulings

| Queue # | Ruling | User's words | Planned |
|---------|--------|--------------|---------|
| 1 | fix-code | "Q2 a" | no |
| 2 | fix-doc | "Q3 a" | no |
| 3 | fix-doc | "Q3 a" | no |

## Remediation queue

| # | Doc | Claim | Verdict | Class | Suggested action |
|---|-----|-------|---------|-------|------------------|
| 1 | examples/charged-ieee/README.md | "Both approaches produce identical output when configured correctly" | stale | NEEDS-USER | Either reword/drop the claim, or make approach1's `ieee_abstract` a single-line string so both shipped examples render the same abstract |
| 2 | examples/charged-ieee/README.md | "This example demonstrates two approaches for using the charged-ieee Typst Universe template with sphinx-typst" | stale | fix-doc | Replace "sphinx-typst" with "typsphinx" at lines 3, 7 and 150 |
| 3 | CHANGELOG.md | "The format is based on Keep a Changelog" (newest-first ordering) | stale | fix-doc | Move the `## [0.1.0b1]` section (line 1389) below `## [0.2.0]` (line 1562) |
