# Docs Audit

<!-- Written by the docs auditor (/gsd-path-docs-audit or /gsd-path-inspect).
     Every verdict carries evidence; a verdict without evidence is a defect. -->

Repo root: /home/yuta/Documents/typsphinx
Audited: 2026-11-04
Audited HEAD: c1606cd9ebb4f4e33a6c9301ca6e7abb39a88601
Alignment mode: no

## Summary

| Verdict | Count |
|---------|-------|
| verified | 76 |
| stale | 1 |
| aspirational | 0 |
| unverifiable | 0 |
| descriptive docs (no testable claims) | 36 |

Worst drift: README.md's Acknowledgments credit "GSD" with a link to open-gsd/gsd-core, but the repository is now driven by GSD Path (`.gsd-path/`, AGENTS.md, WORKFLOW.md) and the gsd-core `.planning/` tree was archived out (commit 8443ef55), so the credited tool is no longer the one in use.

Commands below were run in the disposable verify sidecar at the audited HEAD after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`; build outputs went to a scratch directory outside the repo and `git status --short` stayed empty throughout.

## Doc: README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "LaTeX syntax via mitex (`@preview/mitex:0.2.7`)" | integration | verified | typsphinx/typst_deps.py:95 `PreviewPackage(spec="@preview/mitex:0.2.7", ...)` |
| "Using codly package (`@preview/codly:2.0.0`)" | integration | verified | typsphinx/typst_deps.py:93 `PreviewPackage(spec="@preview/codly:2.0.0", alias="codly")`; built chapter2.typ:277 emits `codly.new(raw(...))` |
| "Direct PDF generation: Self-contained PDF generation via typst-py (no external Typst CLI required)" | feature | verified | `which typst` → not found; `uv run sphinx-build -b typstpdf` on examples/basic, examples/advanced, both charged-ieee approaches → each produced a `.pdf` |
| "Python 3.12 or higher / Sphinx 9.1 or higher / typst-py 0.15.0 or higher" | config | verified | pyproject.toml:10 `requires-python = ">=3.12"`, :29 `sphinx>=9.1,<10`, :31 `typst>=0.15.0,<0.16` |
| "uv sync --extra dev" | command | verified | ran in sidecar → environment installed (`uv==0.13.6`, `virtualenv==21.5.1` among installed packages) |
| "typsphinx is auto-discovered via entry points. Adding to extensions list is optional" | integration | verified | pyproject.toml:70-72 `sphinx.builders` entry points; scratch project with no `extensions` built with `-b typstpdf` → `myproject.typ`, `myproject.pdf`, no unknown-config warning |
| "typst_use_mitex = True  # Use mitex for LaTeX math (default: True)" | config | verified | typsphinx/__init__.py:51 `add_config_value("typst_use_mitex", True, ...)` |
| "Each entry is a tuple `(source, target, title, author[, documentclass])`" | config | verified | typsphinx/template_registry.py:494 `resolve_registry_key()`; examples/charged-ieee/approach2/conf.py:15-17 five-element entry built → `paper.typ`, `paper.pdf` |
| "`project = \"My Project\"` yields `myproject.typ` and, under `typstpdf`, `myproject.pdf`" | feature | verified | typsphinx/builder.py:683 `make_filename_from_project(config.project) + ".typ"`; scratch build with `project = "My Project"` → `myproject.typ`, `myproject.pdf` |
| "An explicit `typst_documents` value — including an explicit empty list `[]` — always overrides the derived default" | config | verified | `uv run pytest tests/test_empty_typst_documents_optout_gate.py tests/test_default_typst_documents_gate.py tests/test_default_typst_documents_derivation.py` → passed (part of 47 passed) |
| "sphinx-build -b typst source build/typst / sphinx-build -b typstpdf source build/pdf" | command | verified | ran both builder forms against examples/basic in sidecar → `basic-example.typ` + `index.typ` (typst) and additionally `basic-example.pdf` (typstpdf) |
| "Plain `[Ref]_` reStructuredText citations render directly. For BibTeX ... typsphinx does not depend on it" | integration | verified | pyproject.toml:28-32 runtime deps exclude sphinxcontrib-bibtex (dev-only at :53); `uv run pytest tests/test_bibtex_dependency_gate.py` → 2 passed; fixture tests/fixtures/citation_render_gate exists |
| "Keys are Sphinx metadata names; values are the template parameter names they map to." | config | verified | typsphinx/template_engine.py:535-537 `for sphinx_key, template_key in self.parameter_mapping.items(): if sphinx_key in sphinx_metadata` |
| "This generates `#include()` directives in Typst with proper heading level adjustments." | feature | verified | examples/advanced build → index.typ:37-41 `context { set heading(offset: heading.offset + 1) ... include("chapter1.typ") ... }` |
| "Unknown nodes trigger `unknown_visit()` which logs a warning and extracts text content" | feature | verified | typsphinx/translator.py:5804-5814 logs `unknown node type: ...` and does not raise SkipNode, so child Text nodes are still visited |
| "app.add_node(mermaid, typst=(typst_visit_mermaid, None)) ... self.add_text(...)" | integration | verified | typsphinx/translator.py:887 `def add_text(self, text: str)`; typsphinx/__init__.py:41-42 registers builders named `typst`/`typstpdf` matching the `typst=` visitor key |
| "uv run tox -e lint / type / py312 / docs-html / docs-pdf / docs / linkcheck" | command | verified | tox.ini:2 env_list and sections `[testenv:lint]` (black, ruff), `[testenv:type]` (mypy), `[testenv:docs-html]`, `[testenv:docs-pdf]`, `[testenv:docs]`, `[testenv:linkcheck]` (not in env_list) |
| "See docs/source/user_guide/bibliography.rst / output_layout.rst / configuration.rst" | structure | verified | `ls docs/source/user_guide` → bibliography.rst, configuration.rst, output_layout.rst present |
| "Project Structure tree (builder.py, writer.py, translator.py, template_engine.py, pdf.py, typst_deps.py, templates/)" | structure | verified | `ls typsphinx` shows all listed entries (tree is abbreviated: pathfmt.py, removed_config.py, template_registry.py exist but are not listed) |
| "Documentation ... typsphinx.readthedocs.io ... ja/latest ... Quick links" | integration | verified | `curl -L` → HTTP 200 for the RTD root, /ja/latest/, and all eight /en/latest/ quick links |
| "**Status**: Stable (v0.10.0)" | status | verified | pyproject.toml:7 `version = "0.10.0"`, :17 `Development Status :: 5 - Production/Stable`; git tag v0.10.0 exists; PyPI JSON `info.version` → 0.10.0 |
| "Developed with [Claude Code] and [GSD](https://github.com/open-gsd/gsd-core) (spec-driven development for AI coding agents)" | integration | stale | README.md:339; repo now runs GSD Path (`.gsd-path/runtime.json`, `.gsd-path/status_runtime.py`, AGENTS.md, WORKFLOW.md); commit 8443ef55 "chore: archive the .planning/ tree out of the repository"; link itself returns 200 |

## Doc: CLAUDE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "black --check . / ruff check . / mypy typsphinx/" | command | verified | ran in sidecar: `uv run black --check .` → "400 files would be left unchanged."; `uv run ruff check .` → "All checks passed!"; `uv run mypy typsphinx/` → "Success: no issues found in 10 source files" |
| "tox # env_list: py312, py313, py314, lint, type, cov, docs" | config | verified | tox.ini:2 `env_list = py312, py313, py314, lint, type, cov, docs` |
| "Builders are auto-discovered via `sphinx.builders` entry points (declared in `pyproject.toml`)" | integration | verified | pyproject.toml:70-72; scratch build with no `extensions` succeeded |
| "In `finish()` it copies each used key's whole template bundle directory wholesale to its own `<outdir>/_template/<key>/` ... writes `<outdir>/_typsphinx/deps.typ`" | feature | verified | typsphinx/builder.py:2332 `_copy_used_template_bundles`, :2553 `_warn_template_dependency_drift`, :2611 `_write_dependencies_file`; every example build output contains `_template/typst/` and `_typsphinx/` |
| "two-line preamble `#import \"/_typsphinx/deps.typ\": *` + `#show: typsphinx-init` ... prepended and no template" | feature | verified | typsphinx/typst_deps.py:133 `deps_preamble_lines()`; typsphinx/writer.py:266 uses it in `translate()`; approach1 paper.typ line 1-2 import + `#show: typsphinx-init` |
| "the bundled `templates/base.typ` import that file by the root-absolute path `/_typsphinx/deps.typ`" | structure | verified | typsphinx/templates/base.typ:11 `#import "/_typsphinx/deps.typ": *` |
| "`N802` is ignored in ruff" | config | verified | pyproject.toml:147 `"N802",   # Function naming (docutils visitor pattern uses PascalCase)` |
| "`typst_deps.py` — leaf module and the single source of the five `@preview` package specs (`DEFAULT_PACKAGES`), ... `render_default_deps()`, ... `deps_preamble_lines()`" | structure | verified | typsphinx/typst_deps.py:26-27 imports only `re`, `dataclasses`; :92 `DEFAULT_PACKAGES`, :114 `render_default_deps`, :133 `deps_preamble_lines` |
| "`template_registry.py` ... `resolve_template_registry()` ... no Windows reserved names ... `resolve_registry_key()`" | structure | verified | typsphinx/template_registry.py:50 `{"CON", "PRN", "AUX", "NUL"}`, :181 `TemplateRegistryEntry`, :213 `resolve_template_registry`, :494 `resolve_registry_key` |
| "`removed_config.py` — `check_config_at_init()`, connected to `config-inited` ... (`typst_template_assets`, `typst_authors`, `typst_toctree_defaults`, `typst_debug`)" | feature | verified | typsphinx/__init__.py:74 `app.connect("config-inited", check_config_at_init)`; typsphinx/removed_config.py:40-60 four entries; `uv run pytest tests/test_removed_config_deprecation_gate.py` passed |
| "`pathfmt.py` — leaf module with zero `typsphinx`-internal imports holding `quote_path()`" | structure | verified | typsphinx/pathfmt.py:43 `import os` is its only import; :46 `def quote_path` |
| "`pdf.py` — `check_typst_available()`, `get_typst_version()`, and compilation raising `TypstCompilationError`" | structure | verified | typsphinx/pdf.py:15, :59, :80 |
| "`tests/test_preview_version_sync.py` asserts no five-package spec literal appears under `typsphinx/` outside `typst_deps.py`" | integration | verified | `uv run pytest tests/test_preview_version_sync.py` → passed (part of 47 passed) |
| "`tox.ini` pins `tox-uv~=1.35` (not `>=1.35,<2`)" | config | verified | tox.ini:16 `requires = tox-uv~=1.35`; pyproject.toml:39 dev extra `tox-uv>=1.35,<2`; `uv run pytest tests/test_toolchain_config_gate.py` → 4 passed |
| "CI ... runs the test job on an ubuntu/windows/macos × py312/py313/py314 matrix, plus lint, type and cov jobs" | integration | verified | .github/workflows/ci.yml:17-18 os/python matrix, :72 `tox -e lint`, :93 `tox -e type`, :114 `tox -e cov` |
| "A weekly `drift.yml` ... `release.yml` publishes to PyPI" | integration | verified | .github/workflows/drift.yml:4-5 `cron: '0 0 * * 1'`; .github/workflows/release.yml:15 trusted-publishing `id-token: write`, :126 publish step |
| "PATH carries seven bare commands ... A missing `.venv/bin/<tool>` fails loudly: a `typsphinx-shim:` line ... exits 127 ... `uv` alone also falls back to nixpkgs' own `uv`" | integration | verified | flake.nix:111-112 `typsphinx-shim:` message + `exit 127`; :117-123 six venv shims; :148 uv shim falls back to `${pkgs.uv}/bin/uv`; `grep -q typsphinx-fhs-run "$(command -v uv)"` → match |
| "`tests/roots/` holds only `test-basic` ... `conftest.py` also provides `sample_doctree` and `temp_sphinx_app`" | structure | verified | `ls tests/roots` → test-basic; tests/conftest.py:12 `pytest_plugins = "sphinx.testing.fixtures"`, :22 `sample_doctree`, :46 `temp_sphinx_app` |
| "Most tests are subprocess gates" | structure | verified | `ls tests/test_*.py` → 193 files; 140 are `test_*_gate.py`, 125 of those reference `sys.executable` |
| "Annotations use builtin generics ... not `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`" | config | verified | grep of typsphinx/ for `typing` imports of Dict, List, Set, Tuple or Iterator → no match (translator.py:9 imports only `Any, NamedTuple`) |

## Doc: CHANGELOG.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "## [0.10.0] - 2026-11-03" | status | verified | pyproject.toml:7 `version = "0.10.0"`; `git tag` includes v0.10.0 |
| "[0.10.0]: .../releases/tag/v0.10.0 ... [0.1.0b1]: .../releases/tag/v0.1.0b1" | integration | verified | every `tag/v...` link target in CHANGELOG.md:1648-1673 resolves via `git rev-parse --verify refs/tags/<v>` (no MISSING) |
| "[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.10.0...HEAD" | integration | verified | CHANGELOG.md:1674; v0.10.0 is the newest tag (`git tag` sorted with `sort -V`) |
| "Planned for Future Releases - Index generation - Pre-commit hooks" | status | verified | still unbuilt as stated: no `.pre-commit-config.yaml` at repo root |
| "New `typst_dependencies` configuration value ... `None` (the default) keeps the generated file" | config | verified | typsphinx/__init__.py:49 `add_config_value("typst_dependencies", None, ...)` |
| "Template dependency drift warning ... (`template dependency drift: ...`)" | feature | verified | typsphinx/builder.py:2553, :2606 `f"template dependency drift: {quote_path(relpath)} pins "` |
| "Python 3.14 support ... CI test matrix ... and tox (`py314`)" | config | verified | pyproject.toml:23 classifier; .github/workflows/ci.yml:18, :24-25; tox.ini:2 |

## Doc: examples/basic/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "sphinx-build -b typst . _build/typst ... two files at the root ...: `basic-example.typ` ... and `index.typ` ... copied to `_build/typst/_template/typst/`" | command | verified | ran `-b typst` in examples/basic → root holds `basic-example.typ`, `index.typ` plus directories `_template/` (README.md, base.typ) and `_typsphinx/` |
| "sphinx-build -b typstpdf . _build/pdf ... both `.typ` and `.pdf` files" | command | verified | ran → `basic-example.typ`, `basic-example.pdf`, `index.typ` |
| "typst compile _build/typst/basic-example.typ output.pdf" | command | verified | Typst CLI not installed; compiled the same wrapper with typst-py `typst.compile("basic-example.typ")` from the output dir (default root = that dir) → 83205-byte PDF |
| "Project Structure: conf.py, index.rst, README.md" | structure | verified | `ls examples/basic` → README.md conf.py index.rst |
| "`extensions = ['typsphinx']` ... `typst_documents` ... `typst_use_mitex`" | config | verified | examples/basic/conf.py `extensions = ["typsphinx"]`, `typst_documents = [("index", "basic-example.typ", ...)]`, `typst_use_mitex = True` |
| "Sphinx 9.1 or higher (below 10)" | config | verified | pyproject.toml:29 `sphinx>=9.1,<10` |
| "This example demonstrates: ... Tables ... Cross-references and links" | feature | verified | examples/basic/index.rst:88 `.. list-table::`, :114-116 external links |

## Doc: examples/advanced/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "This will generate: advanced-example.typ ... index.typ ... chapter1.typ ... chapter2.typ ... `_template/typst/custom.typ`" | command | verified | ran `-b typstpdf` in examples/advanced → advanced-example.typ/.pdf, index.typ, chapter1.typ, chapter2.typ, `_template/typst/custom.typ` |
| "The wrapper (`advanced-example.typ`) is a thin file that includes the master's content file, `index.typ`. The chapter includes live inside that content file" | feature | verified | built advanced-example.typ:18-19 state update + `#include("index.typ")`; chapter includes only in index.typ:39-40 |
| "context { set heading(offset: heading.offset + 1) if \"index#0>chapter1\" in state(\"typsphinx:include-edges\", ()).get() { include(\"chapter1.typ\") } ..." | feature | verified | built index.typ:37-41 matches the snippet verbatim |
| "**Inline:** `:math:`E = mc^2`` → ``mi(`E = mc^2`)`` (emitted in code mode" | feature | verified | built index.typ:108 `mi(`E = mc^2`)` |
| "note → #info[], warning → #warning[], tip → #tip[], important → #warning(title: \"Important\")[], seealso → #tip[] with a \"See also\" title" | feature | verified | typsphinx/translator.py:6201-6250 (`info`, `warning`, `tip`, important→`warning`, seealso→`tip`); built chapter2.typ:254-275 emits code-mode `info(...)`, `warning(..., title: "Important")`, `tip(...)` |
| "Allowlisted keys only (papersize / fontsize / lang); any other key aborts the build" | config | verified | typsphinx/template_engine.py:112-116 `ELEMENTS_ALLOWLIST`; :569 `raise ExtensionError` |
| "The custom template provides: Custom title page, Styled headings with color, Page headers and numbering, Table of contents" | feature | verified | examples/advanced/_typst/custom.typ:15 `primary-color`, :23-32 heading fills, :65-83 title page, :116 `header:`, :135 `outline(` |
| "Project Structure: conf.py, index.rst, chapter1.rst, chapter2.rst, _typst/custom.typ, README.md" | structure | verified | `ls examples/advanced examples/advanced/_typst` |
| "See [Configuration Reference](../../docs/source/user_guide/configuration.rst)" | structure | verified | docs/source/user_guide/configuration.rst exists |

## Doc: examples/charged-ieee/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "typst_template_function = {\"name\": \"ieee\", \"params\": {\"title\": project, ... \"authors\": ieee_authors}}" | config | verified | examples/charged-ieee/approach1/conf.py:71-80 same structure (README abbreviates the author dict) |
| "#import \"@preview/charged-ieee:0.1.4\": ieee ... #let project(title: \"\", authors: (), body)" | structure | verified | examples/charged-ieee/approach2/source/_typst/_template.typ:5 import, :7 `#let project(` (actual signature also declares date/toctree/papersize/fontsize/lang) |
| "cd approach1 / approach2; sphinx-build -b typst -c . source build/typst; cd build/typst; typst compile paper.typ output.pdf" | command | verified | ran `-b typstpdf -c . source <out>` in both approaches → `paper.typ`, `paper.pdf`; typst-py `typst.compile("paper.typ")` in each output dir → 77760-byte PDF (Typst CLI not installed) |
| "Both approaches produce identical output when configured correctly" | feature | verified | `cmp approach1/paper.pdf approach2/paper.pdf` → identical |
| "Approach 2 ... hardcodes the department, organization and location for every author and derives each email from the author's name" | feature | verified | approach2/source/_typst/_template.typ:30-33 hardcoded department/organization/location; email `lower(name.split(" ").at(0)) + ".doe@mit.edu"` |
| "Setting both `typst_package` and `typst_template` is unsupported: the build warns and ignores `typst_package`, honouring `typst_template`" | feature | verified | typsphinx/builder.py:2443-2450 warning "'typst_template' will be honoured and 'typst_package' will be ignored." (note: examples/charged-ieee/approach2/conf.py:21-27, not in the inventory, still says setting both "would switch typsphinx to the package-only route") |

## Doc: typsphinx/templates/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "every file in it, not just `base.typ`, is copied wholesale to `<outdir>/_template/typst/` on every build" | feature | verified | examples/basic build → `_template/typst/` holds README.md and base.typ; typsphinx/builder.py:85-104 only drops VCS/OS junk (`.git`, `.DS_Store`, `*~`) |
| "place a file at `<srcdir>/_typst/base.typ` ... typsphinx finds it automatically" | feature | verified | typsphinx/template_engine.py:41 `TEMPLATE_SEARCH_SUBDIR = "_typst"`; typsphinx/writer.py:389 and builder.py:1576 search `<srcdir>/_typst` |
| "it is also the wheel-content canary for the packaging check in `.github/workflows/ci.yml`" | integration | verified | .github/workflows/ci.yml:153-170 checks `typsphinx/templates/README.md` is in the built wheel |
| "Register your own bundle with a `typst_document_templates` entry ... select it per document via the fifth element ... own `<outdir>/_template/<key>/` directory" | config | verified | typsphinx/__init__.py:63 `typst_document_templates`; typsphinx/template_registry.py:494 `resolve_registry_key`; typsphinx/builder.py:2332 per-key copy |

## Doc: tests/fixtures/state_guard_shapes_evidence/49-SHAPES-RED-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`tests/test_state_guard_shapes_gate.py`'s \"no lost diagnostics\" test can assert every warning recorded here is still present post-fix" | integration | verified | tests/test_state_guard_shapes_gate.py:59-60 `EVIDENCE_PATH` points at this file; `uv run pytest tests/test_state_guard_shapes_gate.py -k "lost or diagnostic"` → 7 passed |
| "Section 1-7 fixtures: state_guard_self_and_url_gate ... state_guard_substring_key_gate" | structure | verified | all seven `tests/fixtures/<name>` directories exist |

## Descriptive docs

Scope: the `.agents/skills/**` files are vendored third-party agent skills describing external tools, not this product. AGENTS.md and WORKFLOW.md describe the installed GSD Path pipeline and its source distribution, a dependency in this application. None makes a claim about typsphinx itself.

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

## User rulings

| Queue # | Ruling | User's words | Planned |
|---------|--------|--------------|---------|
| 1 | fix-doc | "4: GSD Path に差し替え / #194 は範囲外 / リリースは含めない" | T002 |

## Remediation queue

| # | Doc | Claim | Verdict | Class | Suggested action |
|---|-----|-------|---------|-------|------------------|
| 1 | README.md | "Developed with [Claude Code] and [GSD](https://github.com/open-gsd/gsd-core) (spec-driven development for AI coding agents)" | stale | NEEDS-USER | Decide whether to keep the historical gsd-core credit, replace it with GSD Path (github.com/open-gsd/gsd-path), or credit both (README.md:339) |
