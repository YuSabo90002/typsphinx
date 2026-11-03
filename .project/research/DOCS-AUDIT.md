# Docs Audit

Repo root: /home/yuta/Documents/typsphinx
Audited: 2026-11-03
Audited HEAD: f8e9b152e13d05ff54b2c645cd950537cde0836f
Alignment mode: no

## Summary

| Verdict | Count |
|---------|-------|
| verified | 28 |
| stale | 1 |
| aspirational | 0 |
| unverifiable | 0 |
| descriptive docs (no testable claims) | 40 |

Worst drift: README.md's Project Structure tree omits `typsphinx/typst_deps.py`, the new single source of the five `@preview` package versions added in M002.

## Doc: CLAUDE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Builders are auto-discovered via `sphinx.builders` entry points" | config | verified | pyproject.toml:69-71 declares typst/typstpdf under `[project.entry-points."sphinx.builders"]` |
| "the single source of the five `@preview` package specs (`DEFAULT_PACKAGES`)" | structure | verified | typsphinx/typst_deps.py:66-70; grep of writer.py/templates/base.typ finds no `@preview` spec, template_engine.py:279 is a docstring example only |
| "`tests/test_preview_version_sync.py` asserts no five-package spec literal appears under `typsphinx/` outside `typst_deps.py`" | feature | verified | tests/test_preview_version_sync.py:1-23 module docstring states these assertions |
| "`_copy_used_template_bundles()`" copies bundles to `<outdir>/_template/<key>/` | feature | verified | typsphinx/builder.py:509 references `_copy_used_template_bundles()` |
| "`check_typst_available()`, `get_typst_version()`, ... `TypstCompilationError`" | structure | verified | typsphinx/pdf.py:15,59,80 |
| "`N802` is ignored in ruff" | config | verified | pyproject.toml:146 |
| "Line length 88 (black); `E501` is ignored in ruff" | config | verified | pyproject.toml:110,134,142 |
| "`tox.ini` pins `tox-uv~=1.35`" | config | verified | tox.ini:17 `requires = tox-uv~=1.35` |
| "env_list: py312, py313, lint, type, cov, docs" | config | verified | tox.ini:2 |
| "CI ... runs the py312–py313 + lint + type + cov matrix"; drift.yml and release.yml exist | integration | verified | .github/workflows/ci.yml:18 `['3.12', '3.13']`; ls .github/workflows → ci.yml docs.yml drift.yml links.yml release.yml |
| "`typst_dependencies` (path to one file ...; `None` = default)" registered in `__init__.py` | config | verified | typsphinx/__init__.py:49 `add_config_value("typst_dependencies", None, ...)` |
| "Python 3.12+ is required" | config | verified | pyproject.toml:10 `requires-python = ">=3.12"` |

## Doc: README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "LaTeX syntax via mitex (`@preview/mitex:0.2.7`)" / "codly package (`@preview/codly:1.3.0`)" | integration | verified | typsphinx/typst_deps.py:66,68 |
| "Python 3.12 or higher" / "Sphinx 9.1 or higher" / "typst-py 0.15.0 or higher" | config | verified | pyproject.toml:10,28 `sphinx>=9.1,<10`,30 `typst>=0.15.0,<0.16` |
| "typsphinx is auto-discovered via entry points" | config | verified | pyproject.toml:69-71 |
| "Unknown nodes trigger `unknown_visit()`" | feature | verified | typsphinx/translator.py:5875 `def unknown_visit` |
| tox envs docs-html, docs-pdf, linkcheck exist | command | verified | tox.ini:67,75,92 define the testenvs (static check; not run) |
| Linked docs `docs/source/user_guide/bibliography.rst`, `output_layout.rst`, `configuration.rst` | structure | verified | ls → all three files exist |
| Project Structure lists `builder.py writer.py translator.py template_engine.py pdf.py templates/` as the main package | structure | stale | README.md:279-287 omits typsphinx/typst_deps.py, which exists and is described in CLAUDE.md:60 and CHANGELOG.md Unreleased |

## Doc: CHANGELOG.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "New `typst_dependencies` configuration value" | config | verified | typsphinx/__init__.py:49 |
| "The five package versions have a single source ... `typsphinx/typst_deps.py`" | structure | verified | typsphinx/typst_deps.py:66-70; no `@preview` spec in writer.py or templates/base.typ (grep) |
| "## [0.9.8] - 2026-11-03" latest release | status | verified | pyproject.toml:7 `version = "0.9.8"` |

## Doc: examples/basic/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`basic-example.typ`" is the generated wrapper | feature | verified | examples/basic/conf.py:30-33 typst_documents target "basic-example.typ" |
| "`extensions = ['typsphinx']`", "`typst_use_mitex`" in conf.py | config | verified | examples/basic/conf.py:15,40 |
| Project Structure: conf.py, index.rst, README.md | structure | verified | ls examples/basic → README.md conf.py index.rst |

## Doc: examples/advanced/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`typst_template = "_typst/custom.typ"`" enabled in conf.py; `_typst/` directory | config | verified | examples/advanced/conf.py:76; ls examples/advanced → _typst chapter1.rst chapter2.rst conf.py index.rst |

## Doc: examples/charged-ieee/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| Approach 1 uses `typst_template_function` params route; approach1/ and approach2/ exist | config | verified | examples/charged-ieee/approach1/conf.py:2,22 (`typst_package = "@preview/charged-ieee:0.1.4"`); ls → approach1 approach2 |

## Doc: typsphinx/templates/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "it is also the wheel-content canary for the packaging check in `.github/workflows/ci.yml`" | integration | verified | .github/workflows/ci.yml:160 `target = 'typsphinx/templates/README.md'` |
| "place a file at `<srcdir>/_typst/base.typ` ... typsphinx finds it automatically" | feature | verified | typsphinx/template_engine.py:41 `TEMPLATE_SEARCH_SUBDIR = "_typst"` |

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
- docs/S02-LOCAL-PARITY-EVIDENCE.md
- docs/S03-ARTIFACT-GATE-EVIDENCE.md
- docs/S04-PUBLISHED-SITE-EVIDENCE.md
- tests/fixtures/state_guard_shapes_evidence/49-SHAPES-RED-EVIDENCE.md

Scope: `.agents/skills/**` are third-party agent skill bundles; AGENTS.md and WORKFLOW.md describe the installed GSD Path pipeline (a dependency); docs/S0*-EVIDENCE.md and the tests/fixtures evidence file are dated historical measurement records, not claims about current behaviour.

## User rulings

| Queue # | Ruling | User's words | Planned |
|---------|--------|--------------|---------|
| 1 | fix-doc | "4: fix-doc" | T001 |

## Remediation queue

| # | Doc | Claim | Verdict | Class | Suggested action |
|---|-----|-------|---------|-------|------------------|
| 1 | README.md | Project Structure lists `builder.py writer.py translator.py template_engine.py pdf.py templates/` as the main package | stale | fix-doc | Add `typst_deps.py` to the README project-structure tree |
