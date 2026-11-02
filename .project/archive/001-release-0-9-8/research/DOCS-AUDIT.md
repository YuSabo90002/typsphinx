# Docs Audit

<!-- Written by the docs auditor (/gsd-path-docs-audit or /gsd-path-inspect).
     Every verdict carries evidence; a verdict without evidence is a defect. -->

Repo root: /home/yuta/Documents/typsphinx
Audited: 2026-11-03
Audited HEAD: fb3490356dd6b02e7153c421259170ceba8c9b5b
Alignment mode: no

## Summary

| Verdict | Count |
|---------|-------|
| verified | 50 |
| stale | 11 |
| aspirational | 2 |
| unverifiable | 0 |
| descriptive docs (no testable claims) | 36 |

Worst drift: README.md and CHANGELOG.md present 0.9.8 as a shipped, stable release (README "Status: Stable (v0.9.8)", CHANGELOG `[0.9.8] - 2026-09-30` linking `releases/tag/v0.9.8`), but no `v0.9.8` tag exists locally or on origin and PyPI's latest typsphinx is 0.9.7, so `pip install typsphinx` does not deliver the Graphviz rendering the docs describe.

Verification environment: all project commands ran only in the verify sidecar at fb349035, provisioned with `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` (no `docs` extra). Full suite, run once: `LC_ALL=C uv run pytest -q -p no:cacheprovider -o addopts=""` -> `1 failed, 1711 passed, 18 skipped`. The single failure is `tests/test_graphviz_render_gate.py::test_no_graphviz_binary_is_installed` (asserts `shutil.which("dot") is None`; the inherited devShell PATH carries `/nix/store/d5nx177j...-graphviz-12.2.1/bin/dot`, which `flake.nix:177` provisions per docs/S02-LOCAL-PARITY-EVIDENCE.md T02). The same test PASSED on ubuntu-latest in CI run 41152681591. Example builds wrote only to the session scratchpad.

## Doc: CHANGELOG.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "typsphinx carries **zero** bibliography-specific code (`grep -rc bibtex typsphinx/` totals 0)" | feature | verified | `grep -rc bibtex typsphinx/` summed -> 0 |
| "`docs/source/user_guide/bibliography.rst` states the required `conf.py` setup" | structure | verified | file exists at HEAD (`ls docs/source/user_guide/bibliography.rst`) |
| "## [0.9.8] - 2026-09-30" with link "[0.9.8]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.8" | status | aspirational | CHANGELOG.md:53, :1554; `git tag -l 'v0.9.*'` -> v0.9.0 v0.9.2 v0.9.6 v0.9.7; `git ls-remote --tags origin` has no v0.9.8; PyPI JSON `info.version` -> 0.9.7 |
| "`@preview/diagraph:0.3.7` ... declared identically in `writer.py`, `template_engine.py` and `templates/base.typ`, and `tests/test_preview_version_sync.py` now enforces agreement across five packages" | config | verified | writer.py:266-270, template_engine.py:705-709, templates/base.typ:8-23 all carry codly 1.3.0, codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1, diagraph 0.3.7; tests/test_preview_version_sync.py:38-42 lists five; test passed in sidecar |
| "`docs/source/user_guide/diagrams.rst` states what is and is not supported; ... typsphinx's own docs now contain a real diagram" | structure | verified | docs/source/user_guide/diagrams.rst:8 `.. graphviz::` |
| "No `dot` binary is invoked and none was added as a dependency" | feature | verified | `grep -rn subprocess typsphinx/*.py` -> none; pyproject.toml dependencies are sphinx, docutils, typst only |
| "`_visit_graphical_placeholder` itself is unchanged and keeps two callers — inheritance-diagram and the external-`.dot` refusal" | feature | verified | translator.py:6761 (graphviz external-file branch) and :6788 (inheritance diagram) are the only callers |
| "The 0.9.4 entry's "Graceful degradation" line no longer overstates what degrades." | structure | stale | CHANGELOG.md:135; no `## [0.9.4]` heading exists (headings jump 0.9.2 -> 0.9.6); the "Graceful degradation" line is CHANGELOG.md:986 inside `## [0.6.0] - 2026-07-13` |

## Doc: CLAUDE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "Builders are auto-discovered via `sphinx.builders` entry points (declared in `pyproject.toml`)" | config | verified | pyproject.toml `[project.entry-points."sphinx.builders"]` typst/typstpdf |
| "`TypstBuilder` (`name="typst"`) ... copies each used key's whole template bundle directory wholesale to its own `<outdir>/_template/<key>/` directory (`_copy_used_template_bundles()`)" | feature | verified | builder.py:690 `name = "typst"`, :2272 `def _copy_used_template_bundles`, :2482 `class TypstPDFBuilder(TypstBuilder)`; examples/basic build emitted `_template/typst/{base.typ,README.md}` |
| "`TypstWriter.translate()` ... branches on **master vs. included** documents via `_is_master_document()`" | feature | stale | `grep -n _is_master_document typsphinx/writer.py` -> none; writer.py:234-262 now writes every content file unconditionally with `@preview` imports and leaves template application to `render_wrapper()`; split landed in 36a5f588 (feat(47-02)) |
| "`TypstTranslator` ... ~2700 lines, ~140 `visit_*`/`depart_*` methods" | structure | stale | `wc -l typsphinx/translator.py` -> 8149; `grep -c` of visit_ and depart_ method defs -> 189 |
| "`pdf.py` — thin wrapper over `typst-py`: `check_typst_available()`, `get_typst_version()`, and compilation raising `TypstCompilationError`" | feature | verified | pdf.py:15, :59, :80, :110, :155 |
| "The four Typst Universe `@preview` package versions (`codly`, `codly-languages`, `mitex`, `gentle-clues`) are declared in **three** places" | config | stale | five packages now: `@preview/diagraph:0.3.7` at writer.py:270, template_engine.py:709, templates/base.typ:23; tests/test_preview_version_sync.py:5 names five |
| "`typst_documents` (defines master docs, format `[(source, target, title, author), ...]`)" | config | stale | __init__.py:58-61 comment: registry key is "a typst_documents entry's fifth element"; examples/charged-ieee/approach2/conf.py:15 uses a 5-tuple; README.md:84 documents `(source, target, title, author, documentclass)` (contradiction between the two docs) |
| "User-facing config values (all registered in `__init__.py`, prefix `typst_`) include: ... `typst_template` / `typst_template_mapping` / `typst_template_function`, `typst_package` / `typst_package_imports`, `typst_use_mitex` ... `typst_elements`, and `typst_debug`" | config | verified | __init__.py:45-62 add_config_value for each name |
| "the dedicated author-details value that once existed here was removed ... The asset-list config value ... was removed in Phase 54 (CONF-19)" | config | verified | typsphinx/removed_config.py:11-38 (`typst_authors`, `typst_template_assets` reported as removed) |
| "`sphinx.testing.fixtures` is loaded as a pytest plugin. `tests/roots/` holds ... `test-basic` ... `conftest.py` also provides `sample_doctree` and `temp_sphinx_app` fixtures" | structure | verified | tests/conftest.py:12, :22, :46; `ls tests/roots` -> test-basic |
| "tox # env_list: py312, py313, lint, type, cov, docs" | command | verified | tox.ini:2 |
| "`tox.ini` pins `tox-uv~=1.35`" and "`pyproject.toml`'s `dev` extra (the actual pin)" | config | verified | tox.ini:15 `requires = tox-uv~=1.35`; pyproject.toml dev `"tox-uv>=1.35,<2"` |
| "`tests/test_toolchain_config_gate.py`'s `test_dev_extra_pins_tox_uv_not_tox_uv_bare` docstring (the gate that enforces the pin)" | structure | verified | tests/test_toolchain_config_gate.py:268; passed in sidecar |
| "CI (`.github/workflows/ci.yml`) runs the py312–py313 + lint + type + cov matrix. A weekly `drift.yml` ... files an issue on breakage. `release.yml` publishes to PyPI." | integration | verified | ci.yml:18, :70, :91, :112; drift.yml:5 `cron: '0 0 * * 1'`, :37-43 gh issue; release.yml:127-133 publish-pypi |
| "black --check . / ruff check . / mypy typsphinx/ (match CI exactly)" | command | verified | tox.ini:49-58 lint/type commands identical; ci.yml runs `tox -e lint` / `tox -e type` |
| "PATH carries seven bare commands: `uv`, `tox`, `ruff`, `black`, `mypy`, `pytest` and `sphinx-build` ... a `typsphinx-shim:` line on stderr ... then the shim exits 127" | integration | verified | flake.nix:114-123 six venv shims + uvShim :146; :111-112 message and `exit 127`; `grep -q typsphinx-fhs-run "$(command -v uv)"` -> match |
| "`N802` is ignored in ruff because docutils' visitor pattern requires PascalCase" | config | verified | pyproject.toml:146 |
| "pytest -m "not slow"" | command | verified | pyproject.toml markers declare `slow`; tests/test_graphviz_render_gate.py:494 uses it |
| "`.claude/settings.local.json` sets `worktree.baseRef: "head"`" | config | verified | /home/yuta/Documents/typsphinx/.claude/settings.local.json:13 (untracked local file in primary checkout) |
| "`workflow.use_worktrees` is `true` ... the #683 fork-base auto-degrade does **not** fire ... (`worktree base-check` → `shouldDegrade: false, reason: "baseref-head"`)" | config | stale | no `.planning/` config exists in primary checkout or HEAD (`grep -rln use_worktrees .planning .gsd` -> nothing); HEAD fb349035 "adopt GSD Path 1.7.1 project contracts" — the GSD Core `worktree base-check` tooling this section describes is no longer the project's pipeline |

## Doc: README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "LaTeX syntax via mitex (`@preview/mitex:0.2.7`)" / "codly package (`@preview/codly:1.3.0`)" | config | verified | writer.py:266, :268; templates/base.typ:8, :14 |
| "Python 3.12 or higher / Sphinx 9.1 or higher / typst-py 0.15.0 or higher" | config | verified | pyproject.toml `requires-python = ">=3.12"`, `sphinx>=9.1,<10`, `typst>=0.15.0,<0.16` |
| "Each entry is a tuple `(source, target, title, author, documentclass)` ... When unset, typsphinx derives a single entry from `root_doc`, `project`, and `author` ... `project = "My Project"` yields `myproject.typ`" | config | verified | builder.py:664-675 `_default_typst_documents` uses `config.root_doc`, `make_filename_from_project(config.project) + ".typ"`; __init__.py:45 registers it as callable default; tests/test_default_typst_documents_gate.py passed in full suite |
| "sphinx-build -b typst source build/typst" / "sphinx-build -b typstpdf source build/pdf" | command | verified | ran both builders on examples/basic and examples/advanced in sidecar -> rc 0, `.typ` and `.pdf` emitted |
| "Keys are Sphinx metadata names; values are the template parameter names they map to." | config | verified | template_engine.py:533 `for sphinx_key, template_key in self.parameter_mapping.items()` |
| "Unknown nodes trigger `unknown_visit()` which logs a warning and extracts text content" | feature | verified | translator.py:5875-5886 logs `unknown node type` warning and does not raise SkipNode, so children are walked |
| "uv run tox -e lint / type / py312 / docs-html / docs-pdf / docs / linkcheck" | command | verified | tox.ini:45-98 defines every named env |
| Project Structure tree (`builder.py`, `writer.py`, `translator.py`, `template_engine.py`, `pdf.py`, `templates/`) | structure | verified | `ls typsphinx` at HEAD (also contains pathfmt.py, removed_config.py, template_registry.py — tree is a subset, not wrong) |
| "Example projects: `examples/basic/` and `examples/advanced/`" | structure | verified | `ls examples` -> advanced basic charged-ieee |
| Documentation quick links (installation, quickstart, user_guide, configuration, output_layout, examples, api, contributing, ja/latest) | integration | verified | `curl -L -w %{http_code}` -> 200 for all nine URLs on 2026-11-03 |
| "[docs/source/user_guide/bibliography.rst]" / "output_layout.rst" / "configuration.rst" links | structure | verified | all three exist under docs/source/user_guide/ |
| "**Status**: Stable (v0.9.8) - Production ready" | status | aspirational | README.md:344; pyproject.toml version 0.9.8, but no v0.9.8 tag locally or on origin and PyPI latest is 0.9.7 |

## Doc: docs/S02-LOCAL-PARITY-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "T02 — `dot` provisioned in the flake devShell" | integration | verified | flake.nix:161-177 adds `pkgs.graphviz` to the devShell; sidecar PATH resolves `dot` to /nix/store/d5nx177j...-graphviz-12.2.1/bin/dot. Side effect: tests/test_graphviz_render_gate.py:494-506 (R010, asserts no `dot` on PATH) now FAILS in this devShell (full-suite run), while it PASSED on CI ubuntu-latest (run 41152681591) |
| T02 invariants: "`targetPkgs = p: [ p.zlib ];`", "`venvShimNames` ... exactly `tox`, `ruff`, `black`, `mypy`, `pytest`, `sphinx-build`", "`grep -c '"dot"' flake.nix` ... **0**" | structure | verified | flake.nix:70, :116-123; `grep -c '"dot"' flake.nix` -> 0 |

## Doc: docs/S03-ARTIFACT-GATE-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "The gate under test is `tests/test_graphviz_docs_gate.py`'s third class, `TestDogfoodedDiagramHTMLBuild`" | structure | verified | tests/test_graphviz_docs_gate.py:550; class SKIPPED in sidecar (docs extra not provisioned) so only existence is verified |
| "`tests/test_readthedocs_config.py`, which asserts `graphviz` is in `.readthedocs.yaml`'s `build.apt_packages`" | config | verified | tests/test_readthedocs_config.py:13-15; .readthedocs.yaml:26 `- graphviz` |
| "GitHub Actions' `ubuntu-latest` image preinstalls `dot`, so in CI this class renders a real PNG and passes" | integration | stale | CI run 41152681591 (main, 2026-10-31) logs `tests/test_graphviz_render_gate.py::test_no_graphviz_binary_is_installed PASSED` on ubuntu-latest py3.12 and py3.13 — that test asserts `shutil.which("dot") is None`, so `dot` was not on PATH in those jobs |

## Doc: docs/S04-PUBLISHED-SITE-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "https://typsphinx.readthedocs.io/en/latest/user_guide/diagrams.html" with A1 "`class="graphviz"` appears **at least once**" / A2 referenced PNG | integration | verified | `curl` of the URL on 2026-11-03 -> 2x `class="graphviz"`, 1x `graphviz-9d601b68....png` |
| "## 3. The three post-merge assertions (PRE-REGISTERED — no results yet)" / "**Status: awaiting merge.**" | status | stale | S04:152, :560; the fix is merged (`6c55e5b1 Merge pull request #165 from YuSabo90002/milestone/M002`; .readthedocs.yaml graphviz from d6bc4889 is on HEAD) and the live page now satisfies A1/A2, but the file still records no post-merge result |

## Doc: examples/advanced/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "This will generate: `advanced-example.typ` ... `index.typ` ... `chapter1.typ` ... `chapter2.typ` ... `_template/typst/custom.typ`" | command | verified | `uv run sphinx-build -b typst . <scratch>/adv-typst` -> exactly those five files |
| "This generates a Typst compile-time guard ... `if "index#0>chapter1" in state("typsphinx:include-edges", ()).get() { include("chapter1.typ") }`" | feature | verified | emitted index.typ:47-49 matches verbatim |
| Admonitions: note -> info, warning -> warning, important -> warning(title: "Important"), tip -> tip | feature | verified | emitted chapter2.typ: `info(... title: "Note")`, `warning(... title: "Warning")`, `warning(... title: "Important")`, `tip(...)`; translator.py:6271-6315 |
| "sphinx-build -b typstpdf . _build/pdf" -> "both `.typ` and `.pdf` files" | command | verified | sidecar build -> advanced-example.pdf plus .typ files |
| "`_templates/`             # Sphinx's own templates_path override directory (HTML theme; empty here)" | structure | stale | `ls -a examples/advanced` -> no `_templates/` (conf.py:24 still sets `templates_path = ["_templates"]`; git does not track empty dirs) |
| "To use the custom template, edit `conf.py` and uncomment: typst_template = '_typst/custom.typ'" | config | stale | examples/advanced/conf.py:76 already sets `typst_template = "_typst/custom.typ"` uncommented; README.md:65 itself says the wrapper imports `custom.typ` by default |

## Doc: examples/basic/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "This will create two files at the root of `_build/typst/`: `basic-example.typ` ... and `index.typ` ... copied to `_build/typst/_template/typst/`" | command | verified | `uv run sphinx-build -b typst . <scratch>/basic-typst` -> basic-example.typ, index.typ, _template/typst/{base.typ,README.md} |
| "sphinx-build -b typstpdf . _build/pdf" -> "both `.typ` and `.pdf` files" | command | verified | sidecar build -> basic-example.pdf, basic-example.typ, index.typ |
| "`extensions = ['typsphinx']` ... `typst_documents` ... `typst_use_mitex`" in conf.py | config | verified | examples/basic/conf.py:15-17, :30-37, :40 |

## Doc: examples/charged-ieee/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| Approach 1 `typst_template_function = {"name": "ieee", "params": {... "authors": ieee_authors}}` with `typst_package` | config | verified | examples/charged-ieee/approach1/conf.py:22 `typst_package = "@preview/charged-ieee:0.1.4"`, :64 dict route |
| "sphinx-build -b typst -c . source build/typst" then "typst compile paper.typ output.pdf" (both approaches) | command | verified | both approaches built rc 0 emitting paper.typ; `typst.compile(paper.typ)` via typst-py succeeded for approach1 and approach2 |
| "Rich author details (department/organization/location/email) are declared through `typst_template_function["params"]["authors"]` on both approaches" | config | stale | approach2/conf.py:29 sets `typst_template_function = "project"` (string, no params); department/organization are hardcoded in approach2/source/_typst/_template.typ:30-31, matching the README's own Approach 2 example |

## Doc: tests/fixtures/state_guard_shapes_evidence/49-SHAPES-RED-EVIDENCE.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "`tests/test_state_guard_shapes_gate.py`'s "no lost diagnostics" test can assert every warning recorded here is still present post-fix" | structure | verified | `grep -l state_guard_shapes_evidence tests/*.py` -> test_state_guard_shapes_gate.py, test_include_ledger_removal_gate.py; both passed in sidecar |

## Doc: typsphinx/templates/README.md

| Claim | Type | Verdict | Evidence |
|-------|------|---------|----------|
| "every file in it, not just `base.typ`, is copied wholesale to `<outdir>/_template/typst/` on every build" | feature | verified | examples/basic build -> `_template/typst/base.typ` and `_template/typst/README.md` |
| "it is also the wheel-content canary for the packaging check in `.github/workflows/ci.yml`" | integration | verified | ci.yml:160 `target = 'typsphinx/templates/README.md'` |
| "place a file at `<srcdir>/_typst/base.typ` ... typsphinx finds it automatically" / "select it per document via the fifth element of the corresponding `typst_documents` entry" | config | verified | template_engine.py:40 `TEMPLATE_SEARCH_SUBDIR = "_typst"`, :338-345 priority 2 shadow; __init__.py:58-62 fifth-element registry key |

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
- AGENTS.md
- WORKFLOW.md

Scope reason: the `.agents/skills/` files are vendored third-party agent skills (pyproject.toml black `exclude` comment calls them "upstream Anthropic skill scripts"); their claims describe those skills, not typsphinx. AGENTS.md and WORKFLOW.md describe GSD Path's own pipeline and source distribution, an installed dependency in this application; they carry no typsphinx command, configuration, or integration promise.

## Alignment (alignment mode only)

Not applicable: alignment mode is false for this run.

## User rulings

<!-- Appended after the ruling walk (standalone runs). Verbatim, append-only.
     accept-drift rulings suppress the item in future audits.
     `planned: no` rows are the alignment queue: /gsd-path and /gsd-path-plan offer
     to absorb them until drained. When a ruling becomes a task, set
     planned to the task id — never delete the row. -->

| Queue # | Ruling | User's words | Planned |
|---------|--------|--------------|---------|
| 1 | fix-code | 上の 4 点を片付けて、v0.9.8 を公開する。 | T004 |
| 2 | fix-doc | 全部推奨で | T004 |
| 3 | fix-doc | 全部推奨で | T004 |
| 4 | fix-doc | 全部推奨で | T003 |
| 5 | fix-doc | 全部推奨で | T003 |
| 6 | fix-doc | 全部推奨で | T003 |
| 7 | fix-doc | 全部推奨で | T003 |
| 8 | fix-doc | 全部推奨で | T003 |
| 9 | fix-doc | 全部推奨で | T004 |
| 10 | fix-doc | 全部推奨で | T004 |
| 11 | fix-doc | 全部推奨で | T002 |
| 12 | fix-doc | 全部推奨で | T002 |
| 13 | fix-doc | 全部推奨で | T004 |

## Remediation queue

<!-- Every non-verified claim, classified. The user rules on this queue;
     the auditor never fixes anything.
     Numbers are unique and strictly increasing, not necessarily contiguous.
     A persisting row keeps its number; a new row takes a number above every
     prior queue number and every User rulings Queue #. Never reuse a retired
     number: a ruling stays bound to the item it was made for. -->

| # | Doc | Claim | Verdict | Class | Suggested action |
|---|-----|-------|---------|-------|------------------|
| 1 | README.md | "**Status**: Stable (v0.9.8) - Production ready" | aspirational | NEEDS-USER | Owner decides: publish v0.9.8 (tag + PyPI), or relabel the status as unreleased/0.9.7 |
| 2 | CHANGELOG.md | "## [0.9.8] - 2026-09-30" with link "[0.9.8]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.8" | aspirational | NEEDS-USER | Same ruling as #1: release v0.9.8 or fold the section back under Unreleased |
| 3 | CHANGELOG.md | "The 0.9.4 entry's "Graceful degradation" line no longer overstates what degrades." | stale | fix-doc | Point at the 0.6.0 entry (CHANGELOG.md:986), where the line actually lives |
| 4 | CLAUDE.md | "`TypstWriter.translate()` ... branches on **master vs. included** documents via `_is_master_document()`" | stale | fix-doc | Rewrite the writer bullet for the content-file plus `render_wrapper()` split |
| 5 | CLAUDE.md | "`TypstTranslator` ... ~2700 lines, ~140 `visit_*`/`depart_*` methods" | stale | fix-doc | Update to ~8100 lines / ~190 methods or drop the figures |
| 6 | CLAUDE.md | "The four Typst Universe `@preview` package versions (`codly`, `codly-languages`, `mitex`, `gentle-clues`) are declared in **three** places" | stale | fix-doc | Add `diagraph` and say five packages |
| 7 | CLAUDE.md | "`typst_documents` (defines master docs, format `[(source, target, title, author), ...]`)" | stale | fix-doc | Document the optional fifth element (template registry key), consistent with README.md |
| 8 | CLAUDE.md | "`workflow.use_worktrees` is `true` ... the #683 fork-base auto-degrade does **not** fire ... (`worktree base-check` → `shouldDegrade: false, reason: "baseref-head"`)" | stale | NEEDS-USER | Owner decides whether the GSD Core worktree-execution section is retired or restated for GSD Path |
| 9 | docs/S03-ARTIFACT-GATE-EVIDENCE.md | "GitHub Actions' `ubuntu-latest` image preinstalls `dot`, so in CI this class renders a real PNG and passes" | stale | fix-doc | Append a correction citing CI run 41152681591 (no `dot` on PATH in test jobs) |
| 10 | docs/S04-PUBLISHED-SITE-EVIDENCE.md | "## 3. The three post-merge assertions (PRE-REGISTERED — no results yet)" / "**Status: awaiting merge.**" | stale | fix-doc | Append the post-merge A1-A3 results (page now shows `class="graphviz"` and a PNG) or mark the record superseded |
| 11 | examples/advanced/README.md | "`_templates/`             # Sphinx's own templates_path override directory (HTML theme; empty here)" | stale | fix-doc | Drop the `_templates/` line from the tree or mark it as not present |
| 12 | examples/advanced/README.md | "To use the custom template, edit `conf.py` and uncomment: typst_template = '_typst/custom.typ'" | stale | fix-doc | Say the custom template is already enabled in conf.py:76 |
| 13 | examples/charged-ieee/README.md | "Rich author details (department/organization/location/email) are declared through `typst_template_function["params"]["authors"]` on both approaches" | stale | fix-doc | Limit the statement to Approach 1; Approach 2 hardcodes them in `_template.typ` |
