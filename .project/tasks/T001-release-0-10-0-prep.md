---
id: T001
title: Prepare release 0.10.0 — version, README status, dated CHANGELOG section with breaking-change lead, newest-first order, and gate tests that follow the version
wave: 1
deps: []
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - pyproject.toml
  - uv.lock
  - README.md
  - CHANGELOG.md
  - tests/test_release_0_9_8_docs_gate.py
  - tests/test_deps_contract_docs_gate.py
  - tests/test_release_0_10_0_docs_gate.py
---

# T001 — Prepare release 0.10.0 — version, README status, dated CHANGELOG section with breaking-change lead, newest-first order, and gate tests that follow the version

## Context

At 81af8d6b `pyproject.toml:7` is `version = "0.9.8"`, `README.md:345` reads "**Status**: Stable (v0.9.8) - Production ready", and the project's own entry in `uv.lock` (`name = "typsphinx"`, ~line 1601) records `version = "0.9.8"`; `docs/source/conf.py` reads the version from pyproject. `CHANGELOG.md` `## [Unreleased]` (lines 8–88) holds the M002 deps.typ / `typst_dependencies` / drift-warning entries, the M004 "Breaking: codly is upgraded from 1.3.0 to 2.0.0" entry with its migration note, and the M005 Python 3.14 entries, followed by `### Planned for Future Releases`. The 0.9.8 section (line 89) opens with a lead paragraph. The owner ruled (C2): lead paragraph naming the breaking changes (Q1 a); move the misplaced `## [0.1.0b1]` section (~line 1389) below `## [0.2.0]` (~line 1562) unchanged (Q3 a, DOCS-AUDIT #3). Tests tied to the moved content: `tests/test_release_0_9_8_docs_gate.py::test_link_block_targets_v0_9_8` (asserts `[Unreleased]` compares `v0.9.8...HEAD`) and `tests/test_deps_contract_docs_gate.py::_unreleased_section` used by `test_changelog_unreleased_records_the_change` and `test_changelog_unreleased_records_the_codly_2_breaking_change`. Tag push / PyPI publish are out of scope (after merge, Q4 a).

## Approach

- Bump `pyproject.toml` to `0.10.0`, update the project version line in `uv.lock` (e.g. `uv lock`; confirm `uv lock --check` passes and that no dependency resolution changed), and the README status line to v0.10.0.
- CHANGELOG: create `## [0.10.0] - <YYYY-MM-DD>` directly above `## [0.9.8]`, dated with today's date, which will be the release-prep (landing) commit date; open it with a short lead paragraph in the 0.9.8 style naming the codly 2.0.0 breaking change, the shared `/_typsphinx/deps.typ` contract and the custom-template migration (point at templates.rst's migration note); move every former Unreleased entry under it in their existing subsections and order; leave `## [Unreleased]` with only `### Planned for Future Releases`. Link block: `[Unreleased]: …/compare/v0.10.0...HEAD`, add `[0.10.0]: …/releases/tag/v0.10.0` above `[0.9.8]`.
- Move `## [0.1.0b1]` and its body below `## [0.2.0]`'s section with its text unchanged; after the move every release heading is in strictly descending PEP 440 order.
- Tests: repoint `tests/test_deps_contract_docs_gate.py`'s changelog helpers to the `## [0.10.0]` section (keep every assertion's content; keep the `### Planned for Future Releases` check against `## [Unreleased]`); in `tests/test_release_0_9_8_docs_gate.py` change only the link-block test so it asserts the `[0.9.8]` tag link line is kept (not the `[Unreleased]` compare); add `tests/test_release_0_10_0_docs_gate.py` pinning SC1–SC3 and SC6: version 0.10.0 in pyproject and README status, Unreleased holds only the Planned subsection, the 0.10.0 heading date equals the commit date that introduced the heading (same `git log -S` technique as the 0.9.8 gate, falling back to today when uncommitted), the lead names `codly`, `2.0.0`, `deps.typ`, the link block lines, descending PEP 440 heading order (use `packaging.version`), and `scripts/extract_changelog_section.py 0.10.0` output contains `codly`, `2.0.0`, `deps.typ`. Tests must stay OS-neutral.
- Never write a literal triple-backtick in Verify; no index-reading checks.

## Interface contract

- None

## Intent coverage

- SC1
- SC2
- SC3
- SC6
- SC7

## Acceptance criteria

1. SC1: `pyproject.toml` version is `0.10.0`; the `uv.lock` project entry is `0.10.0` and `uv lock --check` passes; README.md's status line names v0.10.0; `uv build` then `uv run twine check dist/*` passes and produces `typsphinx-0.10.0` wheel and sdist.
2. SC2: `## [Unreleased]` contains only `### Planned for Future Releases`; `## [0.10.0] - <release-prep commit date>` sits directly above `## [0.9.8]`, opens with a lead paragraph naming codly 2.0.0, `/_typsphinx/deps.typ` and the custom-template migration, and holds every former Unreleased entry; link block `[Unreleased]` → `v0.10.0...HEAD`, `[0.10.0]` → `releases/tag/v0.10.0`, `[0.9.8]` kept; `uv run python scripts/extract_changelog_section.py 0.10.0` exits 0 and prints `codly`, `2.0.0`, `deps.typ`.
3. SC3: every `## [x.y.z…]` release heading is in strictly descending PEP 440 order; the moved `## [0.1.0b1]` section's text is unchanged.
4. SC6: the release-gate tests assert the 0.10.0 link block and no test asserts `[Unreleased]` compares from `v0.9.8`.
5. SC7: on the task's tree `LC_ALL=C uv run pytest tests/` reports 0 failed and `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` are clean.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && grep -q '^version = "0.10.0"' pyproject.toml && uv lock --check && grep -q 'Stable (v0.10.0)' README.md && uv run python scripts/extract_changelog_section.py 0.10.0 > /tmp/claude-1000/t001-relnotes.txt && grep -q 'codly' /tmp/claude-1000/t001-relnotes.txt && grep -q '2.0.0' /tmp/claude-1000/t001-relnotes.txt && grep -q 'deps.typ' /tmp/claude-1000/t001-relnotes.txt && ! grep -rnE 'v0[.]9[.]8[.]{3}HEAD' tests/ && LC_ALL=C uv run pytest tests/test_release_0_10_0_docs_gate.py tests/test_release_0_9_8_docs_gate.py tests/test_deps_contract_docs_gate.py tests/test_changelog_extraction.py -o addopts="" -q && D=$(mktemp -d) && uv build -o "$D" && ls "$D" | grep -q 'typsphinx-0.10.0' && uv run twine check "$D"/* && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/
```

Heavy: yes

## Log

- 2026-11-03 — created by plan (quick mode)
