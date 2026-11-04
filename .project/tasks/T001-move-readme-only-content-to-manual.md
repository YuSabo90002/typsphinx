---
id: T001
title: Add every README-only item to the manual and record the mapping table
wave: 1
deps: []
status: pending
agent: null
base: null
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
