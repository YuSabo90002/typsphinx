---
id: T001
title: Update CLAUDE.md to match the code, retire the docs/S0x evidence files and their gate checks, and fix three stale doc claims
wave: 1
deps: []
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - CLAUDE.md
  - README.md
  - CHANGELOG.md
  - examples/charged-ieee/README.md
  - docs/S02-LOCAL-PARITY-EVIDENCE.md
  - docs/S03-ARTIFACT-GATE-EVIDENCE.md
  - docs/S04-PUBLISHED-SITE-EVIDENCE.md
  - tests/test_release_0_9_8_docs_gate.py
---

# T001 — Update CLAUDE.md to match the code, retire the docs/S0x evidence files and their gate checks, and fix three stale doc claims

## Context

Inspect at 660e3436 found CLAUDE.md out of date: its Architecture section describes `__init__`, builder, writer, translator, template_engine, typst_deps and pdf but not `typsphinx/template_registry.py` (resolves/validates `typst_document_templates` registry keys), `typsphinx/removed_config.py` (warns once at `config-inited` about removed config names such as `typst_template_assets`, `typst_authors`, `typst_toctree_defaults`, `typst_debug`) or `typsphinx/pathfmt.py` (leaf path-quoting/formatting helper); its Tests section presents the `rootdir` route although 142 test files build a project under `tests/fixtures/` via a `sys.executable -m sphinx` subprocess and only one uses `rootdir` (`tests/roots/` holds only `test-basic`); its CI statements say "py312–py313" while the test job runs on ubuntu/windows/macos. The owner ruled (C2): rewrite those three points (Q1 a); delete `docs/S02-LOCAL-PARITY-EVIDENCE.md`, `docs/S03-ARTIFACT-GATE-EVIDENCE.md`, `docs/S04-PUBLISHED-SITE-EVIDENCE.md` and the S03/S04 checks in `tests/test_release_0_9_8_docs_gate.py` (Q2 a); fix-doc DOCS-AUDIT #1 README.md:26 "Automatic line numbering" (numbering is opt-in via `:linenos:`), #2 CHANGELOG.md:85 "Glossary generation" under Unreleased `### Planned for Future Releases` (glossary rendering exists), #3 examples/charged-ieee/README.md:163-164 "`typst_package` and `typst_template` are mutually exclusive and cannot be set together" (setting both warns and ignores `typst_package`; approach2/conf.py:24-27). Python 3.14 is added to the CI matrix and tox by T002 in this wave, so CLAUDE.md states the py312/py313/py314 matrix.

## Approach

- CLAUDE.md: add one Architecture bullet per module in the existing style; rewrite the Tests paragraph so the `tests/fixtures/` subprocess-gate convention is the stated norm (fixture project + `test_*_gate.py`, building with `sys.executable -m sphinx`) and `tests/roots/` holds only `test-basic`; update every "py312–py313" matrix statement (Commands comment "Everything, matrixed across py312–py313", the `tox` env_list comment, the CI bullet) to py312–py314 and name the ubuntu/windows/macos test matrix. Read each module before describing its role.
- Do not change the tox-uv / tox-uv-bare rationale text: CLAUDE.md's toolchain-pin sync hazard ties it to `tests/test_toolchain_config_gate.py`.
- Delete the three `docs/S0*` files with `git rm`-equivalent removal (plain file deletion; the orchestrator lands it). In `tests/test_release_0_9_8_docs_gate.py` remove the `S03`/`S04` constants and `test_audit_9_s03_has_correction_citing_ci_run` / `test_audit_10_s04_has_post_merge_results`; keep every other test unchanged.
- CHANGELOG: remove only the "- Glossary generation" line; keep the `### Planned for Future Releases` heading and its other three items (two tests require the heading); do not touch any line in released sections (`## [0.9.8]` and below).
- README: replace "Automatic line numbering" with a sub-bullet saying line numbers appear for code blocks with `:linenos:`.
- charged-ieee README: state that setting both is unsupported — the build warns and ignores `typst_package` (check the warning text in `typsphinx/` and `examples/charged-ieee/approach2/conf.py:24-27` before wording it).

## Interface contract

- None

## Intent coverage

- SC1
- SC2
- SC4
- SC5
- SC6

## Acceptance criteria

1. SC1: CLAUDE.md's Architecture section has an entry for each of `template_registry.py`, `removed_config.py` and `pathfmt.py` stating its role; its Tests section states that most tests build a project under `tests/fixtures/` via a `sys.executable -m sphinx` subprocess and assert on the output, and that `tests/roots/` holds only `test-basic`; its CI statements name the ubuntu/windows/macos × py312/py313/py314 test matrix, and no "py312–py313" matrix statement remains.
2. SC2: `git ls-files 'docs/S0*'` prints nothing; `grep -rnE 'S0[234]-[A-Z-]+EVIDENCE' tests/ typsphinx/ docs/source/ CLAUDE.md README.md` returns no match; the remaining tests in `tests/test_release_0_9_8_docs_gate.py` pass.
3. SC4: README.md's codly feature list no longer says "Automatic line numbering" and states that line numbers appear for code blocks with `:linenos:`.
4. SC5: CHANGELOG.md's Unreleased `### Planned for Future Releases` no longer lists "Glossary generation", keeps the heading and its other items, and no line at or below `## [0.9.8]` changes.
5. SC6: examples/charged-ieee/README.md states that setting both `typst_package` and `typst_template` is unsupported: the build warns and ignores `typst_package`.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/test_release_0_9_8_docs_gate.py tests/test_deps_contract_docs_gate.py tests/test_toolchain_config_gate.py tests/test_changelog_extraction.py tests/test_examples_charged_ieee_gate.py -o addopts="" -q && test -z "$(git ls-files 'docs/S0*')" && ! test -e docs/S02-LOCAL-PARITY-EVIDENCE.md && ! test -e docs/S03-ARTIFACT-GATE-EVIDENCE.md && ! test -e docs/S04-PUBLISHED-SITE-EVIDENCE.md && ! grep -rnE 'S0[234]-[A-Z-]+EVIDENCE' tests/ typsphinx/ docs/source/ CLAUDE.md README.md && for m in template_registry.py removed_config.py pathfmt.py; do grep -q "$m" CLAUDE.md || exit 1; done && grep -q 'tests/fixtures/' CLAUDE.md && grep -q 'windows' CLAUDE.md && grep -q 'py314' CLAUDE.md && ! grep -n 'py312–py313' CLAUDE.md && ! grep -q 'Automatic line numbering' README.md && grep -q ':linenos:' README.md && ! sed -n '/^## \[Unreleased\]/,/^## \[0.9.8\]/p' CHANGELOG.md | grep -q 'Glossary generation' && test -z "$(git diff HEAD -- CHANGELOG.md | grep -E '^[-+][^-+]' | grep -vE 'Glossary generation')" && ! grep -q 'cannot be' examples/charged-ieee/README.md && grep -qi 'ignore' examples/charged-ieee/README.md
```

Heavy: no

## Log

- 2026-11-03 — created by plan (quick mode)
