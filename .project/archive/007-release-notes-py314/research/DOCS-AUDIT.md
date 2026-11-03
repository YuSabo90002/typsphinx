# Docs Audit

<!-- Written by the docs auditor (/gsd-path-docs-audit or /gsd-path-inspect).
     Every verdict carries evidence; a verdict without evidence is a defect. -->

Repo root: /home/yuta/Documents/typsphinx
Audited: 2026-11-03
Audited HEAD: 6defa41d1bf9815083d5567c0dd9a4c7f7df4ca1
Alignment mode: no

## Summary

| Verdict | Count |
|---------|-------|
| verified | 70 |
| stale | 4 |
| aspirational | 0 |
| unverifiable | 1 |
| descriptive docs (no testable claims) | 36 |

Worst drift: CLAUDE.md says tox and CI run a py312–py313 matrix, but tox.ini env_list and ci.yml both include py314 (Python 3.14), so contributors following CLAUDE.md under-test one supported interpreter.

## Doc: CLAUDE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "tox # env_list: py312, py313, lint, type, cov, docs" | config | stale | tox.ini:2 → `env_list = py312, py313, py314, lint, type, cov, docs`; CLAUDE.md:28 omits py314 |
| "Everything, matrixed across py312–py313" | config | stale | tox.ini:2 includes py314; pyproject.toml:23 classifier `Python :: 3.14`; pyproject.toml:112 black target-version includes py314 |
| "CI (`.github/workflows/ci.yml`) runs the py312–py313 + lint + type + cov matrix" | integration | stale | .github/workflows/ci.yml:18 `python-version: ['3.12', '3.13', '3.14']`, :24-25 `tox-env: py314`; lint/type/cov jobs at ci.yml:72,93,114 |
| "black --check . / ruff check . / mypy typsphinx/" | command | verified | ran in sidecar: `uv run black --check .` → "399 files would be left unchanged"; `uv run ruff check .` → "All checks passed!"; `uv run mypy typsphinx/` → "Success: no issues found in 10 source files" |
| "pytest # run full suite (config in pyproject.toml)" | command | verified | pyproject.toml:86-108 `[tool.pytest.ini_options]`; ran `LC_ALL=C uv run pytest -q -p no:cacheprovider` in sidecar → "1894 passed, 1 skipped in 215.69s" |
| "tox -e docs-html / docs-pdf / linkcheck" | command | verified | tox.ini:67-98 defines `testenv:docs-html`, `docs-pdf`, `docs`, `linkcheck`; linkcheck not in env_list (tox.ini:2) matching "not run by plain tox" |
| "Builders are auto-discovered via `sphinx.builders` entry points" | config | verified | pyproject.toml:70-72 `typst = "typsphinx"`, `typstpdf = "typsphinx"`; typsphinx/__init__.py:41-42 add_builder |
| "`finish()` writes deps.typ, then copies used bundles, then warns on template dependency drift" | feature | verified | typsphinx/builder.py:2548 `_write_dependencies_file()`, :2550 `_copy_used_template_bundles()`, :2551 `_warn_template_dependency_drift(...)` |
| "TypstBuilder (`name=\"typst\"`) ... TypstPDFBuilder (`name=\"typstpdf\"`)" | structure | verified | typsphinx/builder.py:699 `name = "typst"`, :2709 `name = "typstpdf"` |
| "content `.typ` ... two-line preamble `#import \"/_typsphinx/deps.typ\": *` + `#show: typsphinx-init`" | feature | verified | typsphinx/writer.py:28,266 `deps_preamble_lines()`; generated examples/advanced chapter files start with the preamble (sidecar build of examples/advanced) |
| "Wrapper files — `TypstWriter.render_wrapper()` ... `#include()`s that entry's content file" | feature | verified | typsphinx/writer.py:270 `def render_wrapper`; built advanced-example.typ:19 `#include("index.typ")` |
| "`DEFAULT_PACKAGES` in `typsphinx/typst_deps.py` is the single source of the five `@preview` package specs" | structure | verified | typsphinx/typst_deps.py:92-97 (codly 2.0.0, codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1, diagraph 0.3.7); tests/test_preview_version_sync.py exists and passes in the full suite |
| "bundled `templates/base.typ` imports `/_typsphinx/deps.typ`" | feature | verified | typsphinx/templates/base.typ:11 `#import "/_typsphinx/deps.typ": *` |
| "`/_typsphinx/deps.typ`, its exported names and `typsphinx-init` are a public contract documented in `docs/source/user_guide/templates.rst`" | integration | verified | docs/source/user_guide/templates.rst:124-135 section "Package Dependencies (``deps.typ``)" |
| "pdf.py — `check_typst_available()`, `get_typst_version()`, ... `TypstCompilationError`" | structure | verified | typsphinx/pdf.py:15,59,80 |
| "User-facing config values ... `typst_documents` ... `typst_template` / `typst_template_mapping` / `typst_template_function`, `typst_package` / `typst_package_imports`, `typst_dependencies`, `typst_use_mitex`, `typst_elements`" | config | verified | typsphinx/__init__.py:45-63 add_config_value for each, plus `typst_document_templates` :63 |
| "`tox.ini` pins `tox-uv~=1.35`" | config | verified | tox.ini:17 `requires = tox-uv~=1.35` |
| "`pyproject.toml`'s `dev` extra (the actual pin)" of tox-uv | config | verified | pyproject.toml:39 `"tox-uv>=1.35,<2"` |
| "`tests/test_toolchain_config_gate.py`'s `test_dev_extra_pins_tox_uv_not_tox_uv_bare`" | structure | verified | tests/test_toolchain_config_gate.py:268 |
| "`N802` is ignored in ruff"; "`E501` is ignored in ruff since black owns wrapping" | config | verified | pyproject.toml:143 `"E501"`, :147 `"N802"`; pyproject.toml:111 `line-length = 88` |
| "Annotations use builtin generics ... not `typing.Dict`/`List`/`Set`/`Tuple`/`Iterator`" | config | verified | `grep -rn 'from typing import' typsphinx/` → only translator.py:9 `Any, NamedTuple` |
| "`sphinx.testing.fixtures` is loaded as a pytest plugin ... `conftest.py` also provides `sample_doctree` and `temp_sphinx_app`" | structure | verified | tests/conftest.py:12,22,46 |
| "`tests/roots/` holds Sphinx test projects (e.g. `test-basic`)" | structure | verified | `ls tests/roots` → `test-basic` |
| "A weekly `drift.yml` ... `release.yml` publishes to PyPI" | integration | verified | .github/workflows/drift.yml:4-5 `cron: '0 0 * * 1'`; .github/workflows/release.yml:15,127 `publish-pypi` |
| "PATH carries seven bare commands: `uv`, `tox`, `ruff`, `black`, `mypy`, `pytest` and `sphinx-build`" | integration | verified | flake.nix:66 `typsphinx-fhs-run`, :146 `uvShim`; `which typst` PATH listing in this session shows nix store shim dirs for exactly uv, tox, ruff, black, mypy, pytest, sphinx-build; `grep -q typsphinx-fhs-run "$(command -v uv)"` succeeded |

## Doc: CHANGELOG.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "## [0.10.0] - 2026-11-03" | status | verified | pyproject.toml:7 `version = "0.10.0"`; `uv run python -c "import typsphinx; print(typsphinx.__version__)"` → 0.10.0 |
| "[0.10.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.10.0" | integration | unverifiable | CHANGELOG.md:1645; `git ls-remote --tags origin` lists v0.9.8 but no v0.10.0; PyPI JSON `info.version` → 0.9.8. Resolves only once the release is tagged and published |
| "Every build also writes one shared dependencies file, `<outdir>/_typsphinx/deps.typ`" | feature | verified | sidecar builds of examples/basic and examples/advanced both produced `_typsphinx/deps.typ` |
| "codly is upgraded from 1.3.0 to 2.0.0 (`@preview/codly:2.0.0`)" | integration | verified | typsphinx/typst_deps.py:93 |
| "every code block is now emitted as a code-mode `codly.new(raw(...))` expression" | feature | verified | built examples/advanced chapter2.typ:277 `codly.new(raw("def useful_tip():...", block: true, lang: "python"), number-enabled: false)` |
| "New `typst_dependencies` configuration value" | config | verified | typsphinx/__init__.py:49 |
| "Template dependency drift warning ... (`template dependency drift: ...`)" | feature | verified | typsphinx/builder.py:2553 `_warn_template_dependency_drift`; typsphinx/typst_deps.py:146 pin regex |
| "Planned for Future Releases: Index generation, Pre-commit hooks" | status | verified | not built, consistent with "planned": typsphinx/translator.py:6515-6519 visit_index skips ("we don't generate indices"); no `.pre-commit-config.yaml` at repo root |
| "[Unreleased]: .../compare/v0.10.0...HEAD" link-block ordering | structure | verified | CHANGELOG.md:1645-1646 add `[0.10.0]` above `[0.9.8]`; last line `[Unreleased]` compares from v0.10.0 |

## Doc: README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Python 3.12 or higher" | config | verified | pyproject.toml:10 `requires-python = ">=3.12"` |
| "Sphinx 9.1 or higher" | config | verified | pyproject.toml:29 `"sphinx>=9.1,<10"` |
| "typst-py 0.15.0 or higher" | config | verified | pyproject.toml:31 `"typst>=0.15.0,<0.16"`; installed typst 0.15.0 |
| "LaTeX syntax via mitex (`@preview/mitex:0.2.7`)" | integration | verified | typsphinx/typst_deps.py:95 |
| "codly package (`@preview/codly:2.0.0`)" | integration | verified | typsphinx/typst_deps.py:93 |
| "Direct PDF generation: Self-contained PDF generation via typst-py (no external Typst CLI required)" | feature | verified | `which typst` → not found; `sphinx-build -b typstpdf` of examples/basic and examples/advanced produced basic-example.pdf and advanced-example.pdf |
| "typsphinx is auto-discovered via entry points" | config | verified | pyproject.toml:70-72 |
| "typst_use_mitex = True ... (default: True)" | config | verified | typsphinx/__init__.py:51 `add_config_value("typst_use_mitex", True, ...)` |
| "Each entry is a tuple `(source, target, title, author, documentclass)`" | config | stale | fifth element is optional: typsphinx/builder.py:666 accepts `len(entry) >= 2`; examples/advanced/conf.py and examples/advanced/README.md:225 use a 4-tuple; CLAUDE.md "the optional fifth element `documentclass`". README.md:84 and :233 present all five without marking it optional |
| "When unset, typsphinx derives a single entry from `root_doc`, `project`, and `author` ... `project = \"My Project\"` yields `myproject.typ`" | feature | verified | typsphinx/builder.py:673-685 `make_filename_from_project(config.project) + ".typ"`; tests/fixtures/quickstart_docs_gate/conf.py exercises `myproject` |
| "sphinx-build -b typst source build/typst" / "sphinx-build -b typstpdf source build/pdf" | command | verified | same commands run in sidecar against examples/basic and examples/advanced (srcdir `.`) → .typ and .pdf output |
| "Unknown nodes trigger `unknown_visit()` which logs a warning and extracts text content" | feature | verified | typsphinx/translator.py:5804-5815 logs `unknown node type` and does not raise SkipNode, so child Text nodes are still visited |
| "uv run pytest" | command | verified | ran `LC_ALL=C uv run pytest -q -p no:cacheprovider` in sidecar → "1894 passed, 1 skipped in 215.69s" |
| "uv run tox -e lint / type / py312 / docs-html / docs-pdf / docs / linkcheck" | command | verified | tox.ini:45-98 defines each env; lint/type bodies run directly in sidecar (black, ruff, mypy all pass) |
| Project Structure tree (`builder.py`, `writer.py`, `translator.py`, `template_engine.py`, `pdf.py`, `typst_deps.py`, `templates/`) | structure | verified | `ls typsphinx` shows all listed files (tree is abbreviated: pathfmt.py, removed_config.py, template_registry.py exist but are not listed) |
| "Uses gentle-clues for admonitions" | integration | verified | typsphinx/typst_deps.py:96; typsphinx/translator.py:6201-6250 admonitions map to info/warning/tip |
| "Status: Stable (v0.10.0)" / "Typst: 0.15+" | status | verified | pyproject.toml:7 version 0.10.0, :17 `Development Status :: 5 - Production/Stable`, :31 typst>=0.15.0 |

## Doc: examples/basic/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Sphinx 9.1 or higher (below 10)" / "Python 3.12 or higher" | config | verified | pyproject.toml:10,29 |
| "sphinx-build -b typst . _build/typst" creates `basic-example.typ` and `index.typ`; template copied to `_build/typst/_template/typst/` | command | verified | sidecar build (outdir in scratchpad) → `basic-example.typ`, `index.typ`, `_template/typst/base.typ`, `_template/typst/README.md`, `_typsphinx/deps.typ` |
| "sphinx-build -b typstpdf . _build/pdf" creates both `.typ` and `.pdf` | command | verified | sidecar build → `basic-example.pdf` plus .typ files |
| "typst compile _build/typst/basic-example.typ output.pdf" | command | verified | Typst CLI absent; equivalent `typst.compile('basic-example.typ', root='.')` via typst-py 0.15.0 on the generated wrapper → ok |
| "`extensions = ['typsphinx']`", "`typst_documents`", "`typst_use_mitex`" in conf.py | config | verified | examples/basic/conf.py:15-16,30,40 |
| Project Structure (`conf.py`, `index.rst`, `README.md`) | structure | verified | `ls examples/basic` → README.md conf.py index.rst |

## Doc: examples/advanced/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| Project Structure (`conf.py`, `index.rst`, `chapter1.rst`, `chapter2.rst`, `_typst/custom.typ`) | structure | verified | `ls examples/advanced examples/advanced/_typst` |
| "This will generate: advanced-example.typ, index.typ, chapter1.typ, chapter2.typ, _template/typst/custom.typ" | command | verified | sidecar `sphinx-build -b typst .` → exactly those plus `_typsphinx/deps.typ` |
| "typstpdf ... creates both `.typ` and `.pdf` files" | command | verified | sidecar build → advanced-example.pdf |
| "typst_template = \"_typst/custom.typ\"" is enabled in conf.py | config | verified | examples/advanced/conf.py:76 |
| toctree "generates a Typst compile-time guard ... `if \"index#0>chapter1\" in state(\"typsphinx:include-edges\", ()).get() { include(\"chapter1.typ\") }`" | feature | verified | built index.typ:40-41; wrapper advanced-example.typ:18 publishes `state("typsphinx:include-edges", ()).update(("index#0>chapter1", "index#0>chapter2",))` |
| "Inline: `:math:` → ``mi(`E = mc^2`)`` (emitted in code mode)" | feature | verified | built chapter1.typ:16 `mi(\`a^2 + b^2 = c^2\`)` without `#` |
| Admonitions: note→`#info[]`, warning→`#warning[]`, tip→`#tip[]`, important→`#warning(title: "Important")`, seealso→`#tip[]` | feature | verified | typsphinx/translator.py:6201-6250; built chapter2.typ:254 `info(`, :261,:268 `warning(`, :275 `tip(` |
| "`typst_elements` allowlisted keys only (papersize / fontsize / lang)" | config | verified | typsphinx/template_engine.py:101-113 curated allowlist; examples/advanced/conf.py:62 |
| typst_documents 4-tuple `('index', 'advanced-example.typ', 'Title', 'Author')` | config | verified | examples/advanced/conf.py:36; build produced advanced-example.typ |

## Doc: examples/charged-ieee/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| Approach 1 uses `typst_template_function = {"name": "ieee", "params": {...}}` with `typst_package` | config | verified | examples/charged-ieee/approach1/conf.py:22,71-73 |
| Approach 2 custom template `#import "@preview/charged-ieee:0.1.4": ieee` in `approach2/source/_typst/` | structure | verified | examples/charged-ieee/approach2/source/_typst/_template.typ:5; approach2/conf.py:28 |
| "sphinx-build -b typst -c . source build/typst" then "typst compile paper.typ output.pdf" (both approaches) | command | verified | sidecar run of both approaches → `paper.typ`, `index.typ`, `_typsphinx/` (approach2 also `_template/`); typst-py `compile('paper.typ', root='.')` → compiled for both |
| "Setting both `typst_package` and `typst_template` ... the build warns and ignores `typst_package`" | feature | verified | typsphinx/builder.py:2449 warning text "'typst_package' will be ignored." |

## Doc: typsphinx/templates/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "every file in it, not just `base.typ`, is copied wholesale to `<outdir>/_template/typst/` on every build" | feature | verified | examples/basic build → `_template/typst/base.typ` and `_template/typst/README.md` |
| "place a file at `<srcdir>/_typst/base.typ` ... typsphinx finds it automatically" | feature | verified | typsphinx/template_engine.py:20-41 `TEMPLATE_SEARCH_SUBDIR = "_typst"` |
| "it is also the wheel-content canary for the packaging check in `.github/workflows/ci.yml`" | integration | verified | .github/workflows/ci.yml:162 `target = 'typsphinx/templates/README.md'` |
| "Register your own bundle with a `typst_document_templates` entry ... select it per document via the fifth element" | config | verified | typsphinx/__init__.py:63; typsphinx/template_registry.py |

## Doc: tests/fixtures/state_guard_shapes_evidence/49-SHAPES-RED-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`tests/test_state_guard_shapes_gate.py`'s \"no lost diagnostics\" test can assert every warning recorded here is still present post-fix" | integration | verified | tests/test_state_guard_shapes_gate.py:60 reads this file, :810 `test_warning_baseline_preserved`; passes in the full sidecar suite |

## Descriptive docs

Scope: the `.agents/skills/**` files are vendored third-party agent skills (excluded from black per pyproject.toml:114-118) describing external tools, not this product; AGENTS.md and WORKFLOW.md describe the installed GSD Path pipeline, a dependency in this application. None contains a claim about typsphinx itself.

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
| 1 | accept-drift | "Q1 a" (quoted text absent at HEAD; audit row erroneous) | n/a (accept-drift) |
| 2 | accept-drift | "Q1 a" (quoted text absent at HEAD; audit row erroneous) | n/a (accept-drift) |
| 3 | accept-drift | "Q1 a" (quoted text absent at HEAD; audit row erroneous) | n/a (accept-drift) |
| 4 | fix-doc | "Q2 a" | T001 |
| 5 | accept-drift | "Q3 a" (link resolves once v0.10.0 is tagged) | n/a (accept-drift) |

## Remediation queue

| # | Doc | Claim | Verdict | Class | Suggested action |
|---|-----|-------|---------|-------|------------------|
| 1 | CLAUDE.md | "tox # env_list: py312, py313, lint, type, cov, docs" | stale | fix-doc | Add py314 to the env_list comment (CLAUDE.md:28) |
| 2 | CLAUDE.md | "Everything, matrixed across py312–py313" | stale | fix-doc | Say py312–py314 |
| 3 | CLAUDE.md | "CI (`.github/workflows/ci.yml`) runs the py312–py313 + lint + type + cov matrix" | stale | fix-doc | Say py312–py314 (ci.yml:18) |
| 4 | README.md | "Each entry is a tuple `(source, target, title, author, documentclass)`" | stale | fix-doc | Mark `documentclass` as an optional fifth element (README.md:84,233) |
| 5 | CHANGELOG.md | "[0.10.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.10.0" | unverifiable | NEEDS-USER | Link is dead until v0.10.0 is tagged and published; confirm the release is planned (ship/integration of M006) |
