# Docs Audit

<!-- Written by the docs auditor (/gsd-path-docs-audit or /gsd-path-inspect).
     Every verdict carries evidence; a verdict without evidence is a defect. -->

Repo root: /home/yuta/Documents/typsphinx
Audited: 2026-11-03
Audited HEAD: 660e3436274607e52981b849ef77701edfe9cad9
Alignment mode: no

## Summary

| Verdict | Count |
|---------|-------|
| verified | 64 |
| stale | 4 |
| aspirational | 0 |
| unverifiable | 1 |
| descriptive docs (no testable claims) | 36 |

Worst drift: README.md advertises "Automatic line numbering" for code blocks, but every block without `:linenos:` is emitted with `number-enabled: false`, so numbering is opt-in.

Command evidence below was produced in the verify sidecar at the Audited HEAD after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs`; build outputs went to a scratch directory (`$SC` = /tmp/claude-1000/-home-yuta-Documents-typsphinx/fa8a8dc7-89c7-49ea-8cae-028d0787c918/scratchpad/ex).

## Doc: README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "LaTeX syntax via mitex (`@preview/mitex:0.2.7`)" | integration | verified | typsphinx/typst_deps.py:95 `@preview/mitex:0.2.7` |
| "Using codly package (`@preview/codly:2.0.0`)" | integration | verified | typsphinx/typst_deps.py:93 `@preview/codly:2.0.0` |
| "Automatic line numbering" | feature | stale | README.md:26; typsphinx/translator.py:2513-2514 appends `number-enabled: false` when `:linenos:` is absent; advanced example output chapter1.typ/index.typ contain `number-enabled: false`; numbering opt-in since early release (CHANGELOG.md:1356) |
| "Highlight specific lines" | feature | verified | typsphinx/translator.py:2447 `:emphasize-lines:` -> codly `highlighted` |
| "Direct PDF generation: Self-contained PDF generation via typst-py (no external Typst CLI required)" | feature | verified | `command -v typst` → absent; `sphinx-build -b typstpdf . $SC/basic-pdf` in examples/basic → basic-example.pdf produced |
| "Python 3.12 or higher / Sphinx 9.1 or higher / typst-py 0.15.0 or higher" | config | verified | pyproject.toml:10 `>=3.12`, :28 `sphinx>=9.1,<10`, :30 `typst>=0.15.0,<0.16` |
| "typsphinx is auto-discovered via entry points" | integration | verified | pyproject.toml:69-71 `sphinx.builders` entry points typst/typstpdf |
| "typst_use_mitex = True  # Use mitex for LaTeX math (default: True)" | config | verified | typsphinx/__init__.py:51 default `True` |
| "When unset, typsphinx derives a single entry from `root_doc`, `project`, and `author`" using the LaTeX filename helper | config | verified | typsphinx/builder.py:669-683 `_default_typst_documents` uses `make_filename_from_project(config.project) + ".typ"`; registered as callable default at typsphinx/__init__.py:45 |
| "sphinx-build -b typst source build/typst" / "sphinx-build -b typstpdf source build/pdf" | command | verified | examples/basic and examples/advanced built with both builders, exit 0, .typ and .pdf emitted in $SC |
| "Unknown nodes trigger `unknown_visit()` which logs a warning and extracts text content" | feature | verified | typsphinx/translator.py:5804-5815 logs warning, no SkipNode so children (Text) are still visited |
| "This generates `#include()` directives in Typst with proper heading level adjustments" | feature | verified | $SC/advanced-typst/index.typ:38-42 `set heading(offset: heading.offset + 1)` + guarded `include("chapter1.typ")` |
| Configuration options list (`typst_documents`, `typst_use_mitex`, `typst_template`, `typst_elements`, `typst_template_mapping`) | config | verified | typsphinx/__init__.py:45-63 registers all five |
| tox environments `lint` (black, ruff), `type` (mypy), `py312`, `docs-html`, `docs-pdf`, `docs`, `linkcheck` "not run by plain tox" | command | verified | tox.ini:2 env_list excludes linkcheck; tox.ini:45-98 env commands match |
| Project structure tree (builder.py, writer.py, translator.py, template_engine.py, pdf.py, typst_deps.py, templates/) | structure | verified | `ls typsphinx` lists every named file |
| Quick links to typsphinx.readthedocs.io (installation, quickstart, user_guide, configuration, output_layout, examples, api, contributing, ja/latest) | integration | verified | `curl -L -w %{http_code}` → 200 for all nine URLs (2026-11-03) |
| "Status: Stable (v0.9.8)" | status | verified | pyproject.toml:7 `version = "0.9.8"`; tag v0.9.8 exists |
| "Example projects: `examples/basic/` and `examples/advanced/`" | structure | verified | both dirs exist; .github/workflows/ci.yml:188 `example: [basic, advanced]` |
| "typsphinx does not depend on" sphinxcontrib-bibtex; see docs/source/user_guide/bibliography.rst | config | verified | pyproject.toml:48-53 bibtex only in `dev` extra; docs/source/user_guide/bibliography.rst exists |

## Doc: CLAUDE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "black --check ." / "ruff check ." / "mypy typsphinx/" (match CI) | command | verified | `uv run black --check .` → 398 files unchanged; `uv run ruff check .` → All checks passed; `uv run mypy typsphinx/` → no issues in 10 files |
| "env_list: py312, py313, lint, type, cov, docs" | config | verified | tox.ini:2 |
| builder `_copy_used_template_bundles()`, `_write_dependencies_file()`, `_warn_template_dependency_drift()`; writer `translate()` / `render_wrapper()` | structure | verified | typsphinx/builder.py:2332, 2553, 2611; typsphinx/writer.py:235, 270 |
| content files carry the two-line preamble `#import "/_typsphinx/deps.typ": *` + `#show: typsphinx-init` | feature | verified | $SC/advanced-typst/index.typ:1-2 and advanced-example.typ:1-2 |
| `DEFAULT_PACKAGES` in typst_deps.py is the single source of the five `@preview` specs | structure | verified | typsphinx/typst_deps.py:92-97; `uv run pytest tests/test_preview_version_sync.py tests/test_toolchain_config_gate.py` → 11 passed |
| pdf.py exposes `check_typst_available()`, `get_typst_version()`, `TypstCompilationError` | structure | verified | typsphinx/pdf.py:15, 59, 80 |
| build-time warning text `template dependency drift: ...` | feature | verified | typsphinx/builder.py:2606 |
| config values `typst_documents`, `typst_template`, `typst_template_mapping`, `typst_template_function`, `typst_package`, `typst_package_imports`, `typst_dependencies`, `typst_use_mitex`, `typst_elements` (+ `typst_document_templates`) | config | verified | typsphinx/__init__.py:45-63 |
| ruff ignores `N802` and `E501`; line length 88 | config | verified | pyproject.toml black/ruff `line-length = 88`; ruff ignore list contains `E501` and `N802` |
| `tox.ini` pins `tox-uv~=1.35`; dev extra pins tox-uv; gate `test_dev_extra_pins_tox_uv_not_tox_uv_bare` | config | verified | tox.ini:16; pyproject.toml:38 `tox-uv>=1.35,<2`; tests/test_toolchain_config_gate.py:268 (passed) |
| `sphinx.testing.fixtures` plugin, `tests/roots/test-basic`, `sample_doctree` / `temp_sphinx_app` fixtures | structure | verified | tests/conftest.py:12, 22, 46; `ls tests/roots` → test-basic |
| CI runs py312–py313 + lint + type + cov; weekly drift.yml; release.yml publishes to PyPI | integration | verified | .github/workflows/ci.yml:18-23, 70, 91, 112; drift.yml:4-5 cron `0 0 * * 1`; release.yml:127 `publish-pypi` |
| Seven shimmed commands, missing `.venv/bin/<tool>` exits 127 with `typsphinx-shim:` hint | integration | verified | flake.nix:20-21, 111-112, 117-120; `grep -q typsphinx-fhs-run "$(command -v uv)"` → shim present |
| "`ln -sf` or `patchelf` ... appear in this sentence and nowhere else in this file" | structure | verified | `grep -n "ln -sf\|patchelf" CLAUDE.md` → line 92 only |

## Doc: CHANGELOG.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Every content file and every wrapper now starts with `#import "/_typsphinx/deps.typ": *` and `#show: typsphinx-init`" | feature | verified | $SC/advanced-typst/*.typ first two lines; $SC/basic-typst/_typsphinx/deps.typ emitted |
| "A `literal_block` ... is emitted as `codly.new(raw("...", block: true, lang: "..."), ...)`" | feature | verified | `grep -c "codly.new(raw("` → index.typ 2, chapter1.typ 1, chapter2.typ 7 in advanced output |
| "`:linenos:` maps to `number-enabled`, `:lineno-start:` to `offset`, `:emphasize-lines:` to `highlighted`" | feature | verified | typsphinx/translator.py:2513-2520 |
| "New `typst_dependencies` configuration value" | config | verified | typsphinx/__init__.py:49 |
| "Template dependency drift warning ... (`template dependency drift: ...`)" | feature | verified | typsphinx/builder.py:2553, 2606 |
| Every version heading has a link reference and release tag | structure | verified | `diff` of `## [x]` headers vs `[x]:` link defs → identical; every numeric version has `refs/tags/v<ver>` |
| "Pass `--root <outdir>` when compiling a file that does not sit at the output directory's top level" (top-level wrappers compile with default root) | command | verified | `uv run python -c "typst.compile(<top-level wrapper>)"` for basic-example.typ and both charged-ieee paper.typ → PDFs (83205/77761/77760 bytes) |
| "Planned for Future Releases: Glossary generation" | status | stale | CHANGELOG.md:86; typsphinx/translator.py:6556-6570 `visit_glossary` already renders `.. glossary::` (BLK-04); index/pre-commit items remain unbuilt (translator.py:6515-6520 SkipNode; no .pre-commit-config.yaml) |

## Doc: examples/basic/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "sphinx-build -b typst . _build/typst" creates `basic-example.typ` and `index.typ` at the root, template at `_template/typst/` | command | verified | build to $SC/basic-typst → basic-example.typ, index.typ, _template/typst/base.typ |
| "sphinx-build -b typstpdf . _build/pdf" creates both `.typ` and `.pdf` | command | verified | $SC/basic-pdf → basic-example.pdf + .typ files |
| "typst compile _build/typst/basic-example.typ output.pdf" | command | verified | Typst CLI not installed; typst-py `typst.compile($SC/basic-typst/basic-example.typ)` with default root → 83205-byte PDF |
| conf.py contains `extensions = ['typsphinx']`, `typst_documents`, `typst_use_mitex` | config | verified | examples/basic/conf.py:15-17, 30, 40 |
| "Sphinx 9.1 or higher (below 10)" | config | verified | pyproject.toml:28 |

## Doc: examples/advanced/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| generated files advanced-example.typ, index.typ, chapter1.typ, chapter2.typ, `_template/typst/custom.typ` | command | verified | $SC/advanced-typst listing |
| toctree guard snippet `context { set heading(offset: heading.offset + 1) if "index#0>chapter1" in state(...)... }` | feature | verified | $SC/advanced-typst/index.typ:38-42 byte-matches |
| "Each wrapper publishes its own set of include edges as Typst state before including its content file" | feature | verified | $SC/advanced-typst/advanced-example.typ `#state("typsphinx:include-edges", ()).update(...)` then `#include("index.typ")` |
| inline math → ``mi(`E = mc^2`)`` without `#` | feature | verified | $SC/advanced-typst/index.typ:108 |
| admonitions note→info, warning→warning, tip→tip, important→warning(title), seealso→tip | feature | verified | typsphinx/translator.py:6201-6250 |
| "The custom template is already enabled in `conf.py` by `typst_template = "_typst/custom.typ"`" | config | verified | examples/advanced/conf.py:76 |
| `typst_elements` allowlist papersize / fontsize / lang; other keys abort | config | verified | typsphinx/template_engine.py:112-116 `ELEMENTS_ALLOWLIST` |
| "_typst/custom.typ declares all three" | config | verified | typstpdf build of examples/advanced → advanced-example.pdf with papersize/fontsize/lang passed |
| "sphinx-build -b typstpdf . _build/pdf" creates both `.typ` and `.pdf` | command | verified | $SC/advanced-pdf → advanced-example.pdf + .typ files |

## Doc: examples/charged-ieee/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "sphinx-build -b typst -c . source build/typst" then "typst compile paper.typ output.pdf" (both approaches) | command | verified | both approaches → paper.typ + index.typ; typst-py compile of paper.typ → PDFs; `-b typstpdf` → paper.pdf |
| Approach 2 template "hardcodes the department, organization and location for every author and derives each email from the author's name" | feature | verified | examples/charged-ieee/approach2/source/_typst/_template.typ ieee_authors map |
| Approach 1 config uses `typst_template_function` params route with `authors` dicts | config | verified | examples/charged-ieee/approach1/conf.py:22-60 |
| "`typst_package` and `typst_template` are mutually exclusive and cannot be set together" | config | stale | examples/charged-ieee/README.md:163-164; typsphinx/builder.py:2443-2450 accepts both, warns "unsupported" and honours `typst_template`, ignoring `typst_package` (examples/charged-ieee/approach2/conf.py:24-27 also claims a package-only switch) |

## Doc: typsphinx/templates/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| every bundle file is copied wholesale to `<outdir>/_template/typst/` | feature | verified | $SC/basic-typst/_template/typst/ contains base.typ and README.md |
| `<srcdir>/_typst/base.typ` shadow is found automatically | feature | verified | typsphinx/template_engine.py:41 `TEMPLATE_SEARCH_SUBDIR = "_typst"` |
| README.md is the wheel-content canary in ci.yml | integration | verified | .github/workflows/ci.yml:160 `target = 'typsphinx/templates/README.md'` |
| README.md is "the bundle's only non-`.typ` file" | structure | verified | `ls typsphinx/templates` → README.md, base.typ |
| own bundle via `typst_document_templates` selected by the fifth `typst_documents` element | config | verified | typsphinx/__init__.py:63; examples/charged-ieee/approach1/conf.py:17 fifth element `"typst"` |

## Doc: docs/S02-LOCAL-PARITY-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| `dot` provisioned in the flake devShell and graphviz installed for RTD | integration | verified | flake.nix:161-174; .readthedocs.yaml:19-26 `graphviz` |

## Doc: docs/S03-ARTIFACT-GATE-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| gate under test is `tests/test_graphviz_docs_gate.py` class `TestDogfoodedDiagramHTMLBuild` | structure | verified | tests/test_graphviz_docs_gate.py:550 |
| Measurement environment "Sphinx 8.2.3" | status | unverifiable | docs/S03-ARTIFACT-GATE-EVIDENCE.md:31; contradicts docs/S02-LOCAL-PARITY-EVIDENCE.md:20 (Sphinx 9.1.0) and pyproject.toml:28 `sphinx>=9.1,<10` (since 1743aefd, 2026-07-09); point-in-time reading cannot be re-measured; needs the 2026-10-03 run log |

## Doc: docs/S04-PUBLISHED-SITE-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Status: awaiting merge" and §3 post-merge assertions "no results yet" | status | stale | docs/S04-PUBLISHED-SITE-EVIDENCE.md:152, 559; `git show origin/main:.readthedocs.yaml` piped to `grep -c graphviz` → 2; HEAD is ancestor of origin/main; live https://typsphinx.readthedocs.io/en/latest/user_guide/diagrams.html → 200, `class="graphviz"` ×2, `src="../_images/graphviz-9d60…png"` |

## Doc: tests/fixtures/state_guard_shapes_evidence/49-SHAPES-RED-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| `tests/test_state_guard_shapes_gate.py`'s "no lost diagnostics" test asserts every warning recorded here | integration | verified | tests/test_state_guard_shapes_gate.py:60-69 reads this file; `uv run pytest tests/test_state_guard_shapes_gate.py` → 18 passed |

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

Scope: the `.agents/skills/**` files are installed third-party agent skill bundles describing external tools, and AGENTS.md / WORKFLOW.md describe the installed GSD Path pipeline and its source distribution; none makes a claim about the typsphinx product, so each is listed here rather than audited.

## Alignment (alignment mode only)

- **INTENT success criteria**: n/a (alignment mode: no)
- **Done tasks**: n/a (alignment mode: no)
- **SYNTHESIS decisions**: n/a (alignment mode: no)
- **STATE vs frontmatter**: n/a (alignment mode: no)

## User rulings

| Queue # | Ruling | User's words | Planned |
|---------|--------|--------------|---------|
| 1 | fix-doc | "4-1 fix-doc" | T001 |
| 2 | fix-doc | "4-2 fix-doc" | T001 |
| 3 | fix-doc | "4-3 fix-doc" | T001 |
| 4 | fix-doc | "Q2 a" (the file is deleted) | T001 |
| 5 | fix-doc | "Q2 a" (the file is deleted) | T001 |

## Remediation queue

| # | Doc | Claim | Verdict | Class | Suggested action |
|---|-----|-------|---------|-------|------------------|
| 1 | README.md | "Automatic line numbering" | stale | fix-doc | Say line numbers appear with `:linenos:` (README.md:26). |
| 2 | CHANGELOG.md | "Planned for Future Releases: Glossary generation" | stale | NEEDS-USER | Decide whether glossary rendering already satisfies this item and drop it, or reword it to what is still planned (CHANGELOG.md:86). |
| 3 | examples/charged-ieee/README.md | "`typst_package` and `typst_template` are mutually exclusive and cannot be set together" | stale | fix-doc | State that setting both is unsupported: the build warns and ignores `typst_package` (README.md:163-164; also approach2/conf.py:24-27). |
| 4 | docs/S03-ARTIFACT-GATE-EVIDENCE.md | Measurement environment "Sphinx 8.2.3" | unverifiable | NEEDS-USER | Owner confirms the actual Sphinx version of the 2026-10-03 run; append a Correction if 9.1.x (line 31). |
| 5 | docs/S04-PUBLISHED-SITE-EVIDENCE.md | "Status: awaiting merge" and §3 post-merge assertions "no results yet" | stale | fix-doc | Append a post-merge addendum recording A1-A3 against the live page, keeping the file append-only (lines 152, 559). |
