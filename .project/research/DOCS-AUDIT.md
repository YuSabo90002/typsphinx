# Docs Audit

<!-- Written by the docs auditor (/gsd-path-docs-audit or /gsd-path-inspect).
     Every verdict carries evidence; a verdict without evidence is a defect. -->

Repo root: /home/yuta/Documents/typsphinx
Audited: 2026-11-03
Audited HEAD: 46a72b5f80b9510f67f43031288fcba52478f701
Alignment mode: no

## Summary

| Verdict | Count |
|---------|-------|
| verified | 84 |
| stale | 3 |
| aspirational | 0 |
| unverifiable | 0 |
| descriptive docs (no testable claims) | 36 |

Worst drift: examples/charged-ieee/README.md says "Both approaches produce identical output when configured correctly", but the shipped approach1 example builds a PDF titled "Paper Title" (charged-ieee's default) instead of the project title, because its `typst_template_function["params"]` omits `title`.

All commands below ran in the verify sidecar at the audited HEAD after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` (rc=0); build outputs went to a scratch directory outside the checkout. No Typst CLI is installed (`command -v typst` → empty); `typst compile` claims were checked with typst-py's `typst.compile(<file>)` from inside the output directory, which uses the same default compile root (the file's directory).

## Doc: CLAUDE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "tox ... env_list: py312, py313, lint, type, cov, docs" | config | verified | tox.ini:2 `env_list = py312, py313, lint, type, cov, docs` |
| "`tox -e linkcheck` ... not run by plain tox" | config | verified | tox.ini:92 `[testenv:linkcheck]`; absent from env_list tox.ini:2 |
| "`tox -e docs-html` HTML via furo; `tox -e docs-pdf` PDF via the typstpdf builder" | config | verified | tox.ini:67-81 (`sphinx-build -b html`, `sphinx-build -b typstpdf source _build/pdf`); furo in docs extra pyproject.toml:55 |
| "`black --check .`; `ruff check .`; `mypy typsphinx/`" | command | verified | sidecar: `uv run black --check .` → 394 files unchanged; `uv run ruff check .` → All checks passed; `uv run mypy typsphinx/` → Success: no issues found in 10 source files |
| "`pytest -m \"not slow\"` skip slow-marked tests" | config | verified | pyproject.toml:90-92 `--strict-markers`, marker `slow` registered |
| "`TypstBuilder` (`name=\"typst\"`) ... `TypstPDFBuilder` (`name=\"typstpdf\"`) subclasses it" | structure | verified | typsphinx/builder.py:699, :2698, :2709 |
| "Builders are auto-discovered via `sphinx.builders` entry points" | config | verified | pyproject.toml `[project.entry-points."sphinx.builders"]` typst/typstpdf = "typsphinx" |
| "`_copy_used_template_bundles()` ... `_write_dependencies_file()` ... `_warn_template_dependency_drift()`" | structure | verified | typsphinx/builder.py:2332, :2611, :2553 |
| "`TypstWriter.translate()` ... `TypstWriter.render_wrapper()`" | structure | verified | typsphinx/writer.py:235, :270 |
| "two-line preamble `#import \"/_typsphinx/deps.typ\": *` + `#show: typsphinx-init` (`typst_deps.deps_preamble_lines()`)" | feature | verified | typsphinx/typst_deps.py:104-110; emitted at top of built paper.typ (charged-ieee approach1 build) |
| "single source of the five `@preview` package specs (`DEFAULT_PACKAGES`), `render_default_deps()`" | structure | verified | typsphinx/typst_deps.py:65-70, :85 |
| "bundled `templates/base.typ` import that file by the root-absolute path `/_typsphinx/deps.typ`" | feature | verified | typsphinx/templates/base.typ:11 |
| "`tests/test_preview_version_sync.py` asserts no five-package spec literal ... outside `typst_deps.py`" | integration | verified | sidecar: `uv run pytest tests/test_preview_version_sync.py tests/test_toolchain_config_gate.py -q` → 10 passed |
| "`pdf.py` ... `check_typst_available()`, `get_typst_version()`, ... `TypstCompilationError`" | structure | verified | typsphinx/pdf.py:15, :59, :80 |
| "`N802` is ignored in ruff"; "Line length 88 (black); `E501` is ignored in ruff" | config | verified | pyproject.toml:110, :134, :142, :146 |
| "`tox.ini` pins `tox-uv~=1.35`" | config | verified | tox.ini:17 `requires = tox-uv~=1.35` |
| "`pyproject.toml`'s `dev` extra (the actual pin)" names tox-uv, gate `test_dev_extra_pins_tox_uv_not_tox_uv_bare` | config | verified | pyproject.toml dev extra `"tox-uv>=1.35,<2"`; tests/test_toolchain_config_gate.py:268; gate passed in the 10-passed run above |
| "CI ... runs the py312–py313 + lint + type + cov matrix" | integration | verified | .github/workflows/ci.yml:18 `['3.12', '3.13']`, :51 lint, :72 type-check, :112 `tox -e cov` |
| "weekly `drift.yml` ... files an issue on breakage. `release.yml` publishes to PyPI" | integration | verified | .github/workflows/drift.yml:10, :37-43 (`gh issue list --label drift`); .github/workflows/release.yml:15 (PyPI trusted publishing), :114 |
| "`sphinx.testing.fixtures` is loaded as a pytest plugin ... `tests/roots/` holds ... `test-basic` ... `sample_doctree` and `temp_sphinx_app` fixtures" | structure | verified | tests/conftest.py:12, :22, :46; `ls tests/roots` → test-basic |
| "`typst_dependencies` (path to one file, srcdir-relative or absolute ...; `None` = default)" | config | verified | typsphinx/__init__.py:47-49 |
| "typst_documents ... optional fifth element `documentclass` is a template registry key into `typst_document_templates`" | config | verified | typsphinx/__init__.py:59-63; examples/charged-ieee/approach1/conf.py:16-18 uses fifth element "typst" and builds |
| "The asset-list config value ... was removed in Phase 54 (CONF-19)" | config | verified | typsphinx/removed_config.py:39-41 (`typst_template_assets` removed) |
| "PATH carries seven bare commands ... `typsphinx-fhs-run` ... shim exits 127" | integration | verified | flake.nix:66 (`typsphinx-fhs-run`), :89, :111-112 (`typsphinx-shim:` hint, `exit 127`), :123, :146 (uvShim falls back to nixpkgs uv) |
| "confirm the shim is on PATH by running exactly: `grep -q typsphinx-fhs-run \"$(command -v uv)\"`" | command | verified | ran in sidecar → exit 0 (`shim-ok`) |
| "`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` ... `uv run pytest`" | command | verified | sidecar provisioning rc=0; `uv run pytest -q` → see README.md pytest row |

## Doc: README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "LaTeX syntax via mitex (`@preview/mitex:0.2.7`)" | config | verified | typsphinx/typst_deps.py:68 |
| "Using codly package (`@preview/codly:1.3.0`)" | config | verified | typsphinx/typst_deps.py:66 |
| "Highlight specific lines" | feature | verified | typsphinx/translator.py:2439-2441, :2531 (`hl_lines` → `codly(highlights: ...)`) |
| "Direct PDF generation: Self-contained PDF generation via typst-py (no external Typst CLI required)" | feature | verified | no `typst` on PATH; `uv run sphinx-build -b typstpdf examples/basic <out>` → basic-example.pdf |
| "Python 3.12 or higher; Sphinx 9.1 or higher; typst-py 0.15.0 or higher" | config | verified | pyproject.toml:10 `>=3.12`, :28 `sphinx>=9.1,<10`, :30 `typst>=0.15.0,<0.16` |
| "`typst_use_mitex = True` ... (default: True)" | config | verified | typsphinx/__init__.py:51 |
| "When unset, typsphinx derives a single entry from `root_doc`, `project`, and `author` ... same filename helper Sphinx's own LaTeX builder uses" | feature | verified | typsphinx/__init__.py:45 callable default; typsphinx/builder.py:669-683 (`make_filename_from_project(config.project) + ".typ"`) |
| "`sphinx-build -b typst source build/typst`; `sphinx-build -b typstpdf source build/pdf`" | command | verified | ran both builders on examples/basic, examples/advanced, examples/charged-ieee/approach1+2 → .typ and .pdf emitted |
| "Keys are Sphinx metadata names; values are the template parameter names they map to." | config | verified | typsphinx/template_engine.py:534-535 `for sphinx_key, template_key in self.parameter_mapping.items()` |
| "This generates `#include()` directives in Typst" (toctree) | feature | verified | built examples/advanced index.typ:40-41 `include("chapter1.typ")` (guarded) |
| "Unknown nodes trigger `unknown_visit()` which logs a warning and extracts text content" | feature | verified | typsphinx/translator.py:5875-5886 (warns, does not raise SkipNode, so child Text nodes are still visited) |
| "`uv run tox -e lint` / `type` / `py312` / `docs-html` / `docs-pdf` / `docs` / `linkcheck`" | command | verified | tox.ini:45, :53, :23 (py312 via env_list), :67, :75, :83, :92; lint/type tools run directly in sidecar → pass (CLAUDE.md rows) |
| "Run tests: `uv run pytest`" | command | verified | sidecar: `uv run pytest -q -p no:cacheprovider` → 1812 passed, 18 skipped in 132.62s |
| "Example projects: `examples/basic/` and `examples/advanced/`" | structure | verified | both directories exist and build |
| Project Structure tree (`builder.py`, `writer.py`, `translator.py`, `template_engine.py`, `pdf.py`, `typst_deps.py`, `templates/`) | structure | verified | all listed paths exist (`ls typsphinx`); tree is partial — pathfmt.py, removed_config.py, template_registry.py are not shown |
| "Bibliographies ... typsphinx does not depend on it [sphinxcontrib-bibtex]" | config | verified | pyproject.toml:27-31 runtime deps exclude it; listed only in dev extra |
| Doc links `docs/source/user_guide/bibliography.rst`, `output_layout.rst`, `configuration.rst` | structure | verified | `ls docs/source/user_guide` lists all three |
| "**Status**: Stable (v0.9.8)" | status | verified | pyproject.toml:3 `version = "0.9.8"`, classifier `Development Status :: 5 - Production/Stable`; tag v0.9.8 exists |

## Doc: CHANGELOG.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| Release link block (`[0.9.8]` ... `[0.1.0b1]` → `releases/tag/v...`) | integration | verified | every `tag/v*` target in CHANGELOG.md:1600-1625 resolves via `git rev-parse refs/tags/<t>` (none missing) |
| "`[Unreleased]: .../compare/v0.9.8...HEAD`" | integration | verified | CHANGELOG.md:1625; tag v0.9.8 exists |
| Unreleased: "`<outdir>/_typsphinx/deps.typ` ... Every `typst` and `typstpdf` build writes it" | feature | verified | every example build output contains `_typsphinx/deps.typ`; not in v0.9.8 (`git show v0.9.8:typsphinx/typst_deps.py` fails; commit bdbcdd17 not an ancestor of v0.9.8) |
| Unreleased: "an empty, non-string or missing value stops the build with a `typst_dependencies:` error" | feature | verified | typsphinx/builder.py:2656-2669 |
| Unreleased: "`template dependency drift: ...`" warning | feature | verified | typsphinx/builder.py:2606 |
| Unreleased: "The five package versions have a single source ... `typsphinx/typst_deps.py`" | structure | verified | typsphinx/typst_deps.py:65-70; tests/test_preview_version_sync.py passed |
| "Planned for Future Releases: Glossary generation, Index generation, Pre-commit hooks" | status | verified | not built: typsphinx/translator.py:6586-6592 index nodes skipped ("we don't generate indices"); no `.pre-commit-config.yaml` in repo root |

## Doc: docs/S02-LOCAL-PARITY-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`pkgs.graphviz` added to the devShell `mkShell` `packages` list ... in the unconditional base list" | config | verified | flake.nix:154-177 (inside base list before `lib.optionals`) |
| "it is deliberately NOT added to `fhsRun`'s `targetPkgs`, and no `dot` shim was added" | config | verified | flake.nix:70 `targetPkgs = p: [ p.zlib ];` |
| "Build command `... sphinx-build -b html source _build/html` (the `changedir`/args `tox -e docs-html` uses)" | command | verified | tox.ini:67-73 |

## Doc: docs/S03-ARTIFACT-GATE-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`tests/test_graphviz_docs_gate.py`'s third class, `TestDogfoodedDiagramHTMLBuild`" | structure | verified | tests/test_graphviz_docs_gate.py:550 |
| Correction: "the environment-independent guard in CI remains `tests/test_readthedocs_config.py` (`graphviz` in `.readthedocs.yaml`'s `build.apt_packages`)" | config | verified | .readthedocs.yaml:26 `- graphviz`; tests/test_readthedocs_config.py exists |

## Doc: docs/S04-PUBLISHED-SITE-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "The fix merged to `main` as `6c55e5b1` (\"Merge pull request #165 ...\")" | status | verified | `git log -1 --format=%s 6c55e5b1` → "Merge pull request #165 from YuSabo90002/milestone/M002" |
| "A1 — PASS. `class=\"graphviz\"` occurs 1 time in the served HTML" | integration | verified | `curl -sS -L https://typsphinx.readthedocs.io/en/latest/user_guide/diagrams.html` 2026-11-03 → HTTP 200; `class="graphviz` count 1 |
| "A3 — PASS. `digraph dogfood {` occurs ... 0 times in the raw HTML" | integration | verified | same fetch → count 0 |

## Doc: examples/basic/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`sphinx-build -b typst . _build/typst`" → "`basic-example.typ` ... and `index.typ` ... copied to `_build/typst/_template/typst/`" | command | verified | `uv run sphinx-build -b typst examples/basic <out>` → basic-example.typ, index.typ, _template/typst/{base.typ,README.md}, _typsphinx/ |
| "`sphinx-build -b typstpdf . _build/pdf`" creates both `.typ` and `.pdf` | command | verified | `<out>` → basic-example.pdf, basic-example.typ, index.typ |
| "`typst compile _build/typst/basic-example.typ output.pdf`" | command | verified | Typst CLI absent; typst-py `typst.compile('basic-example.typ')` from the output dir (same default root) → 86101-byte `%PDF-` |
| "`extensions = ['typsphinx']`; `typst_documents`; `typst_use_mitex`" in conf.py | config | verified | examples/basic/conf.py (extensions, typst_documents entry `basic-example.typ`, `typst_use_mitex = True`) |
| Project structure `conf.py`, `index.rst`, `README.md` | structure | verified | `ls examples/basic` → README.md conf.py index.rst |
| "Python 3.12 or higher; Sphinx 9.1 or higher (below 10)" | config | verified | pyproject.toml:10, :28 |

## Doc: examples/advanced/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| Project structure (`conf.py`, `index.rst`, `chapter1.rst`, `chapter2.rst`, `_typst/custom.typ`) | structure | verified | `ls -R examples/advanced` |
| Generated files `advanced-example.typ`, `index.typ`, `chapter1.typ`, `chapter2.typ`, `_template/typst/custom.typ` | command | verified | `uv run sphinx-build -b typst examples/advanced <out>` → exactly those plus `_typsphinx/deps.typ` |
| "`sphinx-build -b typstpdf . _build/pdf`" creates `.typ` and `.pdf` | command | verified | `<out>` → advanced-example.pdf |
| "`typst_template = \"_typst/custom.typ\"`" enabled in conf.py | config | verified | examples/advanced/conf.py:76 |
| Guard snippet `if "index#0>chapter1" in state("typsphinx:include-edges", ()).get() { include("chapter1.typ") }`; wrapper publishes edges | feature | verified | built index.typ:40-41; advanced-example.typ:18-19 (`#state("typsphinx:include-edges", ()).update(...)`, `#include("index.typ")`) |
| "**Inline:** `:math:`E = mc^2`` → `#mi(`E = mc^2`)`" | feature | stale | built index.typ:127-128 emits code-mode `mi(`E = mc^2`)` inside `par({...})`, no `#` prefix |
| note → `#info[]`, warning → `#warning[]`, tip → `#tip[]`, important → `#warning(title: "Important")[]` | feature | verified | typsphinx/translator.py:6271-6302 (`_visit_admonition(node, "info"/"warning"/"tip"/"warning")`) |
| "seealso ... (rendered as #info(title: \"See Also\")[])" | feature | stale | typsphinx/translator.py:6315-6321 `visit_seealso` → `_visit_admonition(node, "tip")` ("converts to #tip[]") |
| "Allowlisted keys only (papersize / fontsize / lang); any other key aborts the build" | config | verified | typsphinx/template_engine.py:101-113, :526 (ELEMENTS_ALLOWLIST) |

## Doc: examples/charged-ieee/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "**Location**: `approach1/`" / "`approach2/`" | structure | verified | `find examples/charged-ieee -type f` → approach1/{conf.py,source/index.rst}, approach2/{conf.py,source/index.rst,source/_typst/_template.typ} |
| "`sphinx-build -b typst -c . source build/typst`" (both approaches) | command | verified | `uv run sphinx-build -b typst -c examples/charged-ieee/approachN examples/charged-ieee/approachN/source <out>` → paper.typ, index.typ for N=1,2 |
| "`cd build/typst; typst compile paper.typ output.pdf`" | command | verified | Typst CLI absent; typst-py `typst.compile('paper.typ')` in each output dir → 79059 / 79228-byte `%PDF-` |
| "Both approaches produce identical output when configured correctly" | feature | stale | pypdf text of typstpdf builds differs: approach1 first line "Paper Title" (charged-ieee default), approach2 "Machine Learning Applications in Computer Vision"; approach1 conf.py:65-72 params omit `title` |
| "`typst_package` and `typst_template` are mutually exclusive and cannot be set together" | config | verified | typsphinx/builder.py:2446 ("Both 'typst_package' and 'typst_template' are ...") |
| "its custom Typst template in `approach2/source/_typst/` hardcodes the department, organization and location ... and derives each email from the author's name" | feature | verified | examples/charged-ieee/approach2/source/_typst/_template.typ (`authors.map(name => (... department: "Computer Science", organization: ..., location: "Cambridge, MA", email: lower(name.split(" ").at(0)) + ".doe@mit.edu"))`) |
| "Rich author details ... are declared through `typst_template_function[\"params\"][\"authors\"]` in Approach 1" | config | verified | examples/charged-ieee/approach1/conf.py:43-72; built paper.typ `authors: ((name: "John Doe", department: ...),)` |

## Doc: typsphinx/templates/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "every file in it, not just `base.typ`, is copied wholesale to `<outdir>/_template/typst/`" | feature | verified | examples/basic typst build → `_template/typst/` holds base.typ and README.md |
| "place a file at `<srcdir>/_typst/base.typ` ... typsphinx finds it automatically" | feature | verified | typsphinx/template_engine.py:41 `TEMPLATE_SEARCH_SUBDIR = "_typst"` (search-path priority 2) |
| "it is also the wheel-content canary for the packaging check in `.github/workflows/ci.yml`" | integration | verified | .github/workflows/ci.yml:150-160 (`target = 'typsphinx/templates/README.md'`) |
| "Register your own bundle with a `typst_document_templates` entry ... select it per document via the fifth element" | config | verified | typsphinx/__init__.py:59-63 |

## Doc: tests/fixtures/state_guard_shapes_evidence/49-SHAPES-RED-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`tests/test_state_guard_shapes_gate.py`'s \"no lost diagnostics\" test can assert every warning recorded here is still present" | integration | verified | tests/test_state_guard_shapes_gate.py:59-69 (`EVIDENCE_PATH` → this file; list zipped against its sections); suite run → see README.md pytest row |
| Reproduction shape `uv run python -m sphinx -b typst tests/fixtures/<fixture> ...` | command | verified | 11 `tests/fixtures/state_guard_*` fixture dirs exist; the sphinx module invocation is the same one used for all example builds above |

## Descriptive docs

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

Scope: the `.agents/skills/` files are vendored third-party agent skills (generic guidance, not claims about typsphinx). AGENTS.md and WORKFLOW.md describe the installed GSD Path pipeline and its source distribution; in this application those are dependency claims, so they are scoped out rather than audited.

## Alignment (alignment mode only)

- **INTENT success criteria**: n/a (alignment mode: no)
- **Done tasks**: n/a
- **SYNTHESIS decisions**: n/a
- **STATE vs frontmatter**: n/a

## User rulings

| Queue # | Ruling | User's words | Planned |
|---------|--------|--------------|---------|
| 1 | fix-code | "5-1 fix-code" | T003 |
| 2 | fix-doc | "5-2 fix-doc" | T003 |
| 3 | fix-doc | "5-3 fix-doc" | T003 |

## Remediation queue

| # | Doc | Claim | Verdict | Class | Suggested action |
|---|-----|-------|---------|-------|------------------|
| 1 | examples/charged-ieee/README.md | "Both approaches produce identical output when configured correctly" | stale | NEEDS-USER | Either add `"title": project` to approach1's `typst_template_function["params"]` (fix-code) or drop/qualify the identical-output note (fix-doc) |
| 2 | examples/advanced/README.md | "seealso ... (rendered as #info(title: \"See Also\")[])" | stale | fix-doc | Say seealso renders through `#tip` (translator.py:6315-6321) |
| 3 | examples/advanced/README.md | "**Inline:** `:math:`E = mc^2`` → `#mi(`E = mc^2`)`" | stale | fix-doc | Show the emitted code-mode form `mi(`E = mc^2`)` or note the `#` applies only in markup mode |
