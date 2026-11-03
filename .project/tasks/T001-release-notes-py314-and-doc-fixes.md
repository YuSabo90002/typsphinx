---
id: T001
title: Add the Python 3.14 bullet to the 0.10.0 notes, make the advanced.rst ieee_abstract example single-line with a pinning test, and mark documentclass optional in README
wave: 1
deps: []
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - CHANGELOG.md
  - docs/source/examples/advanced.rst
  - README.md
  - tests/test_advanced_example_abstract_gate.py
---

# T001 — Add the Python 3.14 bullet to the 0.10.0 notes, make the advanced.rst ieee_abstract example single-line with a pinning test, and mark documentclass optional in README

## Context

At 6defa41d the 0.10.0 release notes omit Python 3.14 support: M005 commit 5aee2fb9 added the `Programming Language :: Python :: 3.14` classifier, black `py314`, the CI test matrix entry `3.14` (ubuntu/windows/macos) and tox `py314`, but no CHANGELOG entry; `## [0.10.0] - 2026-11-03` has `### Added` (CHANGELOG.md ~line 102) and `### Changed`. `docs/source/examples/advanced.rst:24-27` shows `ieee_abstract = """` / `This paper presents novel approaches to machine learning` / `applications in computer vision.` / `"""`, which renders line breaks at the start, after "learning" and at the end when passed through `TemplateEngine._format_typst_value` (inspect measurement); M006 commit 3c23c646 fixed the identical pattern in `examples/charged-ieee/approach1/conf.py` by concatenating string pieces on one logical line. README.md:83-84 and :233 describe `typst_documents` entries as `(source, target, title, author, documentclass)` without saying `documentclass` is optional (DOCS-AUDIT #4, fix-doc). The `v0.10.0` tag is pushed later by the owner's instruction (out of scope).

## Approach

- CHANGELOG: add one bullet under `## [0.10.0]` `### Added` stating Python 3.14 support (classifier and CI/tox test matrix). Do not change the heading line, any other 0.10.0 line, or any other section.
- advanced.rst: rewrite the example so the string has no embedded newline, keeping the same words (e.g. parenthesised adjacent string literals), mirroring commit 3c23c646.
- Add `tests/test_advanced_example_abstract_gate.py`: extract the `ieee_abstract` code from the advanced.rst code block, evaluate the string value (e.g. `ast.literal_eval` of the right-hand side, no `exec` of the whole block), assert it has no `\n` and that `TemplateEngine._format_typst_value(value)` contains no line break; the test must fail on the pre-fix file. OS-neutral.
- README: in both places say `documentclass` is an optional fifth element (template registry key into `typst_document_templates`), matching CLAUDE.md's configuration description.
- No literal triple-backtick in Verify; no index-reading checks.

## Interface contract

- None

## Intent coverage

- SC1
- SC2
- SC3
- SC4

## Acceptance criteria

1. SC1: `## [0.10.0]` `### Added` contains a Python 3.14 support bullet; `uv run python scripts/extract_changelog_section.py 0.10.0` exits 0 and prints `3.14`; the heading line `## [0.10.0] - 2026-11-03` and the other 0.10.0 lines are unchanged.
2. SC2: the advanced.rst `ieee_abstract` string has no embedded newline and the same words; `tests/test_advanced_example_abstract_gate.py` asserts that `TemplateEngine._format_typst_value` of it contains no line break and fails on the pre-fix file.
3. SC3: README.md's two `typst_documents` tuple descriptions mark `documentclass` as an optional fifth element.
4. SC4: on the task's tree `LC_ALL=C uv run pytest tests/` reports 0 failed and `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` are clean.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && uv run python scripts/extract_changelog_section.py 0.10.0 | grep -q '3\.14' && grep -q '^## \[0\.10\.0\] - 2026-11-03$' CHANGELOG.md && test "$(grep -c 'documentclass' README.md)" -ge 2 && test "$(grep -ci 'optional' README.md)" -ge 1 && LC_ALL=C uv run pytest tests/test_advanced_example_abstract_gate.py tests/test_release_0_10_0_docs_gate.py tests/test_changelog_extraction.py -o addopts="" -q && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/
```

Heavy: yes

## Log

- 2026-11-03 — created by plan (quick mode)
