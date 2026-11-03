# Docs Audit

Repo root: /home/yuta/Documents/typsphinx
Audited: 2026-11-03
Audited HEAD: 79ed090eb30aeb255e5775c699c41c9fc3dd766c
Alignment mode: no

## Summary

| Verdict | Count |
|---------|-------|
| verified | 35 |
| stale | 0 |
| aspirational | 0 |
| unverifiable | 1 |
| descriptive docs (no testable claims) | 37 |

Worst drift: none material; the only non-verified claim is S04's record of the live readthedocs.org page, which cannot be re-observed from the repo.

## Doc: README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "LaTeX syntax via mitex (`@preview/mitex:0.2.7`)" / "codly package (`@preview/codly:1.3.0`)" | config | verified | typsphinx/writer.py:266-268, typsphinx/templates/base.typ:8,14; `uv run pytest tests/test_preview_version_sync.py` → passed |
| "Python 3.12 or higher; Sphinx 9.1 or higher; typst-py 0.15.0 or higher" | config | verified | pyproject.toml:10 `>=3.12`, :28 `sphinx>=9.1,<10`, :30 `typst>=0.15.0,<0.16` |
| "typsphinx is auto-discovered via entry points" | integration | verified | pyproject.toml:69-71 `sphinx.builders` entry points typst/typstpdf |
| "typst_use_mitex = True ... (default: True)" | config | verified | typsphinx/__init__.py:48 |
| "`project = \"My Project\"` yields `myproject.typ`" / typst_documents derived from root_doc when unset | feature | verified | typsphinx/__init__.py:45 callable default `_default_typst_documents`; examples/basic build (no explicit doc list relied on) emitted basic-example.typ |
| "sphinx-build -b typst source build/typst" / "-b typstpdf" | command | verified | in sidecar: `cd examples/basic && uv run sphinx-build -q -b typstpdf . <scratch>/basic` → exit 0, basic-example.pdf/.typ, index.typ, _template/ |
| "Unknown nodes trigger `unknown_visit()` which logs a warning" | feature | verified | typsphinx/translator.py:5875-5886 |
| "uv run tox -e lint / type / py312 / docs-html / docs-pdf / docs / linkcheck" | command | verified | tox.ini:2 env_list, :45,:53,:67,:75,:83,:92 env sections (structure checked, envs not run) |
| "uv run tox -e docs  # Build both HTML and PDF docs" | command | verified | tox.ini:83-90 runs html then typstpdf |
| Project Structure: builder.py, writer.py, translator.py, template_engine.py, pdf.py, templates/ | structure | verified | `ls typsphinx` → all present (plus pathfmt.py, removed_config.py, template_registry.py not listed) |
| "Status: Stable (v0.9.8)" | status | verified | pyproject.toml:7 `version = "0.9.8"`; CHANGELOG.md:16 `## [0.9.8] - 2026-11-03` |

## Doc: CLAUDE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`setup(app)` registers both builders and all `typst_*` config values" | feature | verified | typsphinx/__init__.py:41-60 |
| "`_copy_used_template_bundles()` ... `<outdir>/_template/<key>/`" | feature | verified | typsphinx/builder.py:2272; advanced build produced `_template/typst/custom.typ` |
| "`TypstPDFBuilder` (`name=\"typstpdf\"`) subclasses it" | structure | verified | typsphinx/builder.py:2482,2493 |
| "`TypstWriter.render_wrapper()`" applies template | structure | verified | typsphinx/writer.py:279 |
| "`TypstTranslator` (subclass of `SphinxTranslator`)" | structure | verified | typsphinx/translator.py:512 |
| "pdf.py: check_typst_available(), get_typst_version(), TypstCompilationError" | structure | verified | typsphinx/pdf.py:15,59,80 |
| "five @preview versions declared in writer.py, template_engine.py, base.typ; test_preview_version_sync.py asserts" | config | verified | writer.py:266-270, template_engine.py:705-709, base.typ:8-23 all equal; sync test passed in sidecar |
| "`N802` is ignored in ruff"; "Line length 88 (black); E501 ignored" | config | verified | pyproject.toml:110,134,142,146 |
| "tox env_list: py312, py313, lint, type, cov, docs" | config | verified | tox.ini:2 |
| "tox.ini pins `tox-uv~=1.35`" and dev extra pins tox-uv | config | verified | tox.ini:17; pyproject.toml:38 `tox-uv>=1.35,<2`; `uv run pytest tests/test_toolchain_config_gate.py` → passed |
| "author-details value removed (CONF-10); asset-list value removed in Phase 54 (CONF-19)" | config | verified | typsphinx/removed_config.py:40-48 (`typst_template_assets`, `typst_authors` warnings) |
| "conftest.py provides sample_doctree and temp_sphinx_app; sphinx.testing.fixtures plugin; tests/roots/test-basic" | structure | verified | tests/conftest.py:12,22,46; `ls tests/roots` → test-basic |
| "CI runs py312–py313 ... weekly drift.yml files an issue; release.yml publishes to PyPI" | integration | verified | .github/workflows/ci.yml:18-23; drift.yml:5 cron weekly, :43 gh issue; release.yml:127-133 |
| "shims ... `typsphinx-fhs-run`" | integration | verified | flake.nix:66,89,148 |

## Doc: examples/basic/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`sphinx-build -b typst . _build/typst` creates basic-example.typ and index.typ; template copied to _template/typst/" | command | verified | sidecar typstpdf build → basic-example.typ, index.typ, _template/ |
| "`sphinx-build -b typstpdf . _build/pdf` creates both .typ and .pdf" | command | verified | same run → basic-example.pdf, exit 0 |

## Doc: examples/advanced/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| outputs advanced-example.typ, index.typ, chapter1.typ, chapter2.typ, _template/typst/custom.typ | command | verified | sidecar `uv run sphinx-build -q -b typstpdf . <scratch>/advanced` → exit 0, all listed files plus advanced-example.pdf |

## Doc: examples/charged-ieee/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "cd approach1/approach2; sphinx-build -b typst -c . source build/typst" produces paper.typ | command | verified | sidecar run of both approaches → exit 0, paper.typ + index.typ (typst compile step not run) |

## Doc: typsphinx/templates/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "every file ... copied wholesale to `<outdir>/_template/typst/`" | feature | verified | builder.py:2272; basic build produced `_template/` |
| "`<srcdir>/_typst/base.typ` ... found automatically" | feature | verified | typsphinx/template_engine.py:36-39 `TEMPLATE_SEARCH_SUBDIR = "_typst"` |
| "README.md is the wheel-content canary for the packaging check in ci.yml" | integration | verified | .github/workflows/ci.yml:151-169 |

## Doc: docs/S02-LOCAL-PARITY-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| flake supplies `dot` inside the FHS sandbox for sphinx.ext.graphviz | integration | verified | flake.nix:161-177 `pkgs.graphviz` |

## Doc: docs/S03-ARTIFACT-GATE-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| gate under test is `tests/test_graphviz_docs_gate.py` class `TestDogfoodedDiagramHTMLBuild` | structure | verified | tests/test_graphviz_docs_gate.py:550 |

## Doc: docs/S04-PUBLISHED-SITE-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "the Graphviz fix reaches the real page a reader loads from readthedocs.org" | integration | unverifiable | requires network fetch of the live RTD diagrams page; file is a pre-merge measurement record (lines 1-15); referenced by tests/test_release_0_9_8_docs_gate.py:33,170 |

## Doc: tests/fixtures/state_guard_shapes_evidence/49-SHAPES-RED-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| file is the verbatim RED record consumed by the shapes gate | structure | verified | tests/test_state_guard_shapes_gate.py:17-19 |

## Descriptive docs

Vendored agent skill bundles under .agents/skills/ and the GSD Path pipeline rule files (AGENTS.md, WORKFLOW.md) describe excluded dependencies, not this product. CHANGELOG.md is a historical record; its current version line is checked under README.md.

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
- CHANGELOG.md
- WORKFLOW.md

## User rulings

| Queue # | Ruling | User's words | Planned |
|---------|--------|--------------|---------|
| 1 | accept-drift | "S04はaccept-drift" | n/a (accept-drift) |

## Remediation queue

| # | Doc | Claim | Verdict | Class | Suggested action |
|---|-----|-------|---------|-------|------------------|
| 1 | docs/S04-PUBLISHED-SITE-EVIDENCE.md | "the Graphviz fix reaches the real page a reader loads from readthedocs.org" | unverifiable | NEEDS-USER | Confirm by fetching the live RTD diagrams page, or accept as a historical record |
