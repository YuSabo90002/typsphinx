---
id: T001
title: Add every README-only item to the manual and record the mapping table
wave: 1
deps: []
status: done
agent: build_T001
base: c913040e95620798b3349f69846fcd10edb1eef3
worktree: null
task_branch: null
files:
  - docs/source/index.rst
  - docs/source/installation.rst
  - docs/source/quickstart.rst
  - docs/source/contributing.rst
  - docs/source/user_guide/index.rst
  - docs/source/user_guide/configuration.rst
  - docs/source/user_guide/templates.rst
  - docs/source/user_guide/bibliography.rst
  - docs/source/user_guide/diagrams.rst
  - docs/source/user_guide/builders.rst
  - docs/source/user_guide/output_layout.rst
---

# T001 — Add every README-only item to the manual and record the mapping table

## Context

M008 simplifies README.md (INTENT.md SC1–SC5, done by T002). Before README loses anything, every information item it states that the manual does not already state must be added to docs/source in English (SC6), so nothing is lost (prohibition N2). The README to compare is README.md at base c1606cd9 (348 lines). The sections T002 removes or shrinks are: Features detail (sub-bullets for math/codly, `@preview/` versions, the bibliography paragraph), the Quick Start `#### typst_documents` explanation, Advanced Usage (Custom Templates, Template Parameter Mapping, Multi-Document Projects, Working with Third-Party Extensions), Configuration Options, and Development (Setup, Testing Strategy, Project Structure). Plan measurement found the manual already covers most of this; README-only Development items found so far are the `typst_deps.py` Project Structure line, `uv run pytest --cov=typsphinx --cov-report=html`, and the `examples/basic/` / `examples/advanced/` testing note. The README `## Contributing` content (step list, Development Guidelines) is deleted, not moved (C5) — do not add it to the manual.

## Approach

- Compare item by item, not section by section: for each statement in the README sections above, find the docs/source page that states it; only when none does, add it to the most fitting page in the declared files.
- The manual wins on conflict (INTENT E6): where README and the manual disagree, keep the manual's statement and add only README-only information. Do not "fix" existing manual content (e.g. contributing.rst's structure diagram listing `pdf.py # TypstPDFBuilder` stays) — a broader contributing.rst review is a later milestone (C7).
- Moved content states the concrete information README stated (config values, code examples, constraints), never a vague summary or "see the source" pointer (prohibition N3, judged at final review).
- English only; no Japanese translation (scope out). No `typsphinx/` change. Do not edit README.md (T002 owns it).
- Keep the clean docs build warning-free: base c1606cd9 emits 0 warnings, so `sphinx-build -W -E` must pass (watch duplicate labels and cross-reference targets).
- docs/source pages are scanned by gates (`tests/test_registry_documentation_gate.py`, `tests/test_docs_template_layout_gate.py`, `tests/test_bundle_layout_sweep_gate.py`, `tests/test_quickstart_docs_gate.py`, `tests/test_bibliography_docs_gate.py`, `tests/test_graphviz_docs_gate.py`); added text must keep them passing.
- Append to this task's Log the list of items you added, each with its docs location (file § section). T002 records the full removed-item → docs location table after it rewrites README.

## Interface contract

- None

## Intent coverage

- SC6
- SC7

## Acceptance criteria

1. Every informational item in README.md@c1606cd9's removed/shrunk sections (listed in Context) is stated in a docs/source page, either already or added by this task, except README `## Contributing` content (C5); E6 (manual wins: existing manual statements unchanged, only README-only information added) and E7 (an item with no docs home is added, never dropped) hold.
2. docs/source/contributing.rst states the `typst_deps.py` module in its project structure, the `--cov-report=html` coverage command, and the example projects (`examples/basic/`, `examples/advanced/`) as part of testing; no other existing contributing.rst content is reworded.
3. A clean HTML build `sphinx-build -W -E -b html docs/source <fresh dir>` exits 0 (no warnings), and each `added` row's text appears in the built HTML page (E8: clean build only).
4. The Log lists every item this task added with its docs location (file § section).

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && out="$(mktemp -d)" && LC_ALL=C uv run sphinx-build -W -E -b html docs/source "$out" && grep -q 'typst_deps.py' docs/source/contributing.rst && grep -q 'cov-report=html' docs/source/contributing.rst && grep -q 'examples/basic' docs/source/contributing.rst && grep -rq 'typst_deps.py' "$out/contributing.html" && LC_ALL=C uv run pytest tests/test_registry_documentation_gate.py tests/test_docs_template_layout_gate.py tests/test_bundle_layout_sweep_gate.py tests/test_quickstart_docs_gate.py tests/test_bibliography_docs_gate.py tests/test_graphviz_docs_gate.py -o addopts="" -q
```

Heavy: no

## Log

- 2026-11-04 — created by plan (quick mode)
- 2026-11-04 — build_T001 (coder): README.md@c1606cd9 compared item by item against docs/source; manual statements left unchanged (E6), README-only items added:
  - Features "Standard docutils nodes" (paragraphs, sections, lists, tables, admonitions) → docs/source/index.rst § Key Features (new bullet)
  - Features codly sub-bullets (`:linenos:` line numbers, multiple languages, highlight specific lines) → docs/source/index.rst § Key Features (sub-bullets under Code Highlighting; highlight stated as `:emphasize-lines:`, which the translator maps from `hl_lines`)
  - Features "Multi-document support … toctree integration using `#include()`" → docs/source/index.rst § Key Features (new bullet)
  - Features bibliography: plain `[Ref]_` citations render directly → docs/source/index.rst § Key Features (new bullet) and docs/source/user_guide/bibliography.rst § Plain reStructuredText Citations (new section, example verified to build and compile with typstpdf)
  - Advanced Usage "Template Parameter Mapping" example (`project→doc_title`, `author→doc_authors`, `release→version`; keys are Sphinx metadata names, values template parameter names) → docs/source/user_guide/configuration.rst § Template Configuration › Template Parameter Mapping (new; also states the default mapping project→title, author→authors, release→date from template_engine.DEFAULT_PARAMETER_MAPPING)
  - Advanced Usage "Working with Third-Party Extensions" (mermaid `app.add_node` example verbatim, How it works bullets, Sphinx add_node API link) → docs/source/user_guide/configuration.rst § Third-Party Extension Nodes (new; unknown_visit stated as logging `unknown node type` and continuing into children, per translator.py)
  - Advanced Usage "Multi-Document Projects" toctree example (`:maxdepth: 2`, `:numbered:`) and "#include() with heading level adjustments" → docs/source/user_guide/output_layout.rst § Multi-Document Projects (new; offset rule `set heading(offset: heading.offset + 1)` per translator.py)
  - Development `typst_deps.py` Project Structure line → docs/source/contributing.rst § Project Structure (one line added)
  - Development `uv run pytest --cov=typsphinx --cov-report=html` → docs/source/contributing.rst § Running Tests (added)
  - Development Testing Strategy example projects `examples/basic/`, `examples/advanced/` → docs/source/contributing.rst § Coding Guidelines › Testing (bullet added)
  - Already covered, not added: `@preview` versions (templates.rst § Package Dependencies table), typst_documents explanation (configuration.rst § Typst Documents, quickstart.rst, builders.rst § Document Definitions, output_layout.rst § Wrapper and Content Files), auto-discovery (quickstart.rst note), bibliography setup/pybtex/CSL (bibliography.rst), custom template path (templates.rst/configuration.rst), typst_elements (configuration.rst § Paper Size and Format), Development setup/tox/TDD/unit+integration tests (contributing.rst). README `## Contributing` not moved (C5).
  - Verify: pass — uv sync ok; `sphinx-build -W -E -b html` build succeeded (0 warnings); three contributing.rst greps and contributing.html grep matched; 6 docs gates 78 passed. Added text confirmed present in built index/bibliography/configuration/output_layout/contributing HTML.
- 2026-11-04 — orchestrator Verify (sidecar gsd-path-verify/task-t001-verify): pass, exit 0; output tail:
  ```
   + sphinx-intl==2.4.0
   + sphinxcontrib-applehelp==2.0.0
   + sphinxcontrib-bibtex==2.7.0
   + sphinxcontrib-devhelp==2.0.0
   + sphinxcontrib-htmlhelp==2.1.0
   + sphinxcontrib-jsmath==1.0.1
   + sphinxcontrib-qthelp==2.0.0
   + sphinxcontrib-serializinghtml==2.0.0
   + tomli-w==1.2.0
   + tox==4.64.10
   + tox-uv==1.37.2
   + tox-uv-bare==1.37.2
   + twine==7.0.0
   + types-docutils==0.23.0.20260923
   + typing-extensions==4.16.0
   + typsphinx==0.10.0 (from file:///home/yuta/.gsd-path/projects/4018706f853274cd7713143cf7ba094e230867e5ad2bfc5891d0cd69027eb98b/4b529697c911aff5766d6b9c03f122ba2ed9565d87a00e2f51ea62f3fd0642ec/verify/task-t001-verify)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.13.6
   + virtualenv==21.5.1
  ```
