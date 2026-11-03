---
id: T001
title: Update CLAUDE.md to match the code, retire the docs/S0x evidence files and their gate checks, and fix three stale doc claims
wave: 1
deps: []
status: done
agent: build_T001
base: 5aee2fb977eec2376e4f7bfed01492c6cd6dd4f5
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
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/test_release_0_9_8_docs_gate.py tests/test_deps_contract_docs_gate.py tests/test_toolchain_config_gate.py tests/test_changelog_extraction.py tests/test_examples_charged_ieee_gate.py -o addopts="" -q && ! test -e docs/S02-LOCAL-PARITY-EVIDENCE.md && ! test -e docs/S03-ARTIFACT-GATE-EVIDENCE.md && ! test -e docs/S04-PUBLISHED-SITE-EVIDENCE.md && ! grep -rnE 'S0[234]-[A-Z-]+EVIDENCE' tests/ typsphinx/ docs/source/ CLAUDE.md README.md && for m in template_registry.py removed_config.py pathfmt.py; do grep -q "$m" CLAUDE.md || exit 1; done && grep -q 'tests/fixtures/' CLAUDE.md && grep -q 'windows' CLAUDE.md && grep -q 'py314' CLAUDE.md && ! grep -n 'py312–py313' CLAUDE.md && ! grep -q 'Automatic line numbering' README.md && grep -q ':linenos:' README.md && ! sed -n '/^## \[Unreleased\]/,/^## \[0.9.8\]/p' CHANGELOG.md | grep -q 'Glossary generation' && test -z "$(git diff HEAD -- CHANGELOG.md | grep -E '^[-+][^-+]' | grep -vE 'Glossary generation')" && ! grep -q 'cannot be' examples/charged-ieee/README.md && grep -qi 'ignore' examples/charged-ieee/README.md
```

Heavy: no

## Log

- 2026-11-03 — created by plan (quick mode)
- 2026-11-03 — build_T001: CLAUDE.md gains Architecture bullets for `template_registry.py`, `removed_config.py`, `pathfmt.py` (roles read from each module); Tests paragraph now states the `tests/fixtures/` + `sys.executable -m sphinx` subprocess-gate norm and that `tests/roots/` holds only `test-basic`; Commands comment/tox env_list and CI bullet now py312–py314 with ubuntu/windows/macos test matrix; tox-uv rationale untouched. Deleted docs/S02/S03/S04-*-EVIDENCE.md from the working tree (no git rm, per brief). Removed `S03`/`S04` constants and `test_audit_9_s03_has_correction_citing_ci_run` / `test_audit_10_s04_has_post_merge_results` from tests/test_release_0_9_8_docs_gate.py. CHANGELOG: removed only "- Glossary generation" under Unreleased Planned. README: "Automatic line numbering" -> "Line numbers for code blocks with `:linenos:`". charged-ieee README: both set is unsupported, build warns and ignores `typst_package` (matches builder.py:2446-2449 warning). Verify: uv sync ok; pytest 45 passed; overall exit 1 solely because `git ls-files 'docs/S0*'` still lists the three files (deletions are unstaged in the index; staging is forbidden to the coder). Every other clause run separately: exit 0. Expect full pass once the orchestrator stages/lands the deletions.
- 2026-11-03 — orchestrator Verify (isolate gsd-path-task/T001): fail, exit 1; output tail:
  ```
  .............................................                            [100%]
  45 passed in 1.28s
  Resolved 95 packages in 0.54ms
  Checked 94 packages in 0.32ms
  ```
- 2026-11-03 — orchestrator plan defect repair: the Verify clause `test -z "$(git ls-files 'docs/S0*')"` reads the index, but the isolate Verify runs on the coder's unstaged working tree, so it can never pass before landing (coder diff otherwise complete; every other clause exit 0). The clause is removed; the three `! test -e docs/S0…` clauses and the repo grep still prove SC2 on the tree, and `git ls-files` absence is checked by review after landing. Rejected isolate diff: 8 declared paths (CHANGELOG.md, CLAUDE.md, README.md, examples/charged-ieee/README.md, tests/test_release_0_9_8_docs_gate.py, three docs/S0* deletions), patch sha256 d2cbc03c1a0f1fe3cddfef5442ec18c2e803a8293b9a5b488c31750a617e2ecf, preserved outside the repo for an unchanged re-apply at the new base.
- 2026-11-03 — orchestrator: serial retry at base 5aee2fb9 re-applied the preserved build_T001 ready diff unchanged (patch sha256 d2cbc03c1a0f1fe3cddfef5442ec18c2e803a8293b9a5b488c31750a617e2ecf, `git apply` clean, 8 declared paths); no orchestrator-authored product change. Authoritative Verify follows via `finish`.
- 2026-11-03 — orchestrator Verify (sidecar gsd-path-verify/task-t001-verify): pass, exit 0; output tail:
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
   + typsphinx==0.9.8 (from file:///home/yuta/.gsd-path/projects/4018706f853274cd7713143cf7ba094e230867e5ad2bfc5891d0cd69027eb98b/4b529697c911aff5766d6b9c03f122ba2ed9565d87a00e2f51ea62f3fd0642ec/verify/task-t001-verify)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.13.6
   + virtualenv==21.5.1
  ```
