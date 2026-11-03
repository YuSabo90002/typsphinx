---
id: T005
title: Document typst_dependencies and the public /_typsphinx/deps.typ contract, record the change in CHANGELOG and CLAUDE.md, and prove the final quality bar
wave: 2
deps: [T001, T002, T003, T004]
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - docs/source/user_guide/configuration.rst
  - docs/source/user_guide/templates.rst
  - docs/source/user_guide/output_layout.rst
  - CHANGELOG.md
  - CLAUDE.md
  - tests/test_deps_contract_docs_gate.py
  - tests/test_release_0_9_8_docs_gate.py
  - tests/test_output_layout_docs_gate.py
---

# T005 — Document typst_dependencies and the public /_typsphinx/deps.typ contract, record the change in CHANGELOG and CLAUDE.md, and prove the final quality bar

## Context

The owner ruled that `/_typsphinx/deps.typ`, its exported names, and `typsphinx-init` are a public contract ("1.公開の約束にする"); external users exist (gdsfactory/quantum-rf-pdk pins codly 1.3.0 in its own template). Earlier tasks deliver four things. T001 delivers the generated default file and the two-line preamble (K3). T002 delivers `typst_dependencies` (K4). T003 delivers the drift warning (K5). T004 delivers pin-free in-repo templates, plus the SC5 no-pin test in `tests/test_preview_version_sync.py`. SYNTHESIS fixes the gentle-clues names the translator emits as exactly `abstract`, `danger`, `error`, `info`, `memo`, `notify`, `task`, `tip`, `warning` (`typsphinx/translator.py` `_visit_admonition` call sites). Other changes go on these pages. The configuration page (`docs/source/user_guide/configuration.rst`, near "Custom Template File" around line 118, and the "When the Build Stops" section around line 284) gets the new value. The templates page (`docs/source/user_guide/templates.rst`) gets the contract and the author guidance. `docs/source/user_guide/output_layout.rst` (lines ~38, ~72, ~156) describes the `_template/` reserved directory and the compile root, and must now also name `_typsphinx/`. CHANGELOG `## [Unreleased]` currently holds only `### Planned for Future Releases`, and `tests/test_release_0_9_8_docs_gate.py:133-135` asserts exactly that. That assertion was a 0.9.8 release-time check and must be relaxed so it does not forbid new Unreleased entries. CLAUDE.md's "The `@preview` version-sync hazard" section and its Architecture bullets for `writer.py` / `template_engine.py` still describe the three-site lockstep.

## Approach

- Configuration page, `typst_dependencies` entry: path rule (relative to srcdir, or absolute, resolved like `typst_template`); one global file for the whole build, never per template; copied verbatim (byte-identical) to `<outdir>/_typsphinx/deps.typ`; when unset (`None`) typsphinx generates the default file; `""` or a missing file stops the build with a `typst_dependencies:` error. Add the stop case to "When the Build Stops".
- Templates page, `deps.typ` contract section: the path `/_typsphinx/deps.typ` (compile root = outdir, as for `/_template/`); every exported name (`codly`, `codly-init`, `codly-languages`, `mi`, `mitex`, `render`, the nine gentle-clues names above, `typsphinx-init`); what `typsphinx-init` does; the default versions. Tell template authors to take package names from `#import "/_typsphinx/deps.typ": ...` rather than pinning `@preview/` versions. Mention the drift warning in its K5 form, as a best-effort aid that cannot see dynamically built or indirectly reached imports.
- Judgment prohibition N4 — Must not: "promise that a replaced `deps.typ` with other versions produces correct output". Detail: "the docs state plainly that only the default versions are supported and a replaced file is at the user's risk". Say this plainly on both pages: the translator targets the default versions' APIs, and output with a replaced `deps.typ` is not guaranteed. A replaced file must still export every contract name. Do not describe a version as "compatible" or "tested" unless the defaults are meant.
- Output layout page: name `_typsphinx/` as a reserved output directory next to `_template/` (a docname there is refused). State that content files and wrappers import `/_typsphinx/deps.typ`, so hand compiles of `-b typst` output must use the outdir as `--root`.
- CHANGELOG `## [Unreleased]`: record the single version source and generated `<outdir>/_typsphinx/deps.typ` + `typsphinx-init`, the new `typst_dependencies` value, the drift warning, the in-repo template cleanup, and the compile-root note for hand compiles. Keep `### Planned for Future Releases`. Change `tests/test_release_0_9_8_docs_gate.py` only so it stops asserting that Unreleased holds nothing else; keep its 0.9.8 assertions.
- CLAUDE.md: rewrite the `@preview` section for the single source (`typsphinx/typst_deps.py` → generated `deps.typ`). Name the gates: `tests/test_preview_version_sync.py` checks SC1 and the SC5 no-pin rule, and the drift warning covers user templates. Update the `writer.py` and `template_engine.py` Architecture bullets and the configuration-surface paragraph to list `typst_dependencies`. Do not alter the toolchain-pin or NixOS sections.
- `tests/test_deps_contract_docs_gate.py` reads the `.rst` sources, CHANGELOG.md, and CLAUDE.md and asserts each SC6 claim. It derives the export list from the generated default (`render_default_deps()` plus the gentle-clues names above), not from a hand-copied list, so a renamed export fails it.
- Do not rename `typst_package` / `typst_package_imports`, document a conf.py version dict, or promise per-template `deps.typ` (vetoes). Do not change any `.py` under `typsphinx/`.

## Interface contract

- K3 — Every `typst`/`typstpdf` build's outdir contains `<outdir>/_typsphinx/deps.typ`, imported by the root-absolute path `/_typsphinx/deps.typ` (compile root = outdir). The default file exports `codly`, `codly-init`, `codly-languages`, `mi`, `mitex`, `render`, `abstract`, `danger`, `error`, `info`, `memo`, `notify`, `task`, `tip`, `warning`, and `typsphinx-init`. Every content `.typ` and wrapper `.typ` contains the lines `#import "/_typsphinx/deps.typ": *` and `#show: typsphinx-init`.
- K4 — Config value `typst_dependencies`, registered as `app.add_config_value("typst_dependencies", None, "html", [str, type(None)])`. `None` (default) means the generated default file. A `str` is resolved as `os.path.join(srcdir, value)` (an absolute value passes through), and that one file is copied byte-identical to `<outdir>/_typsphinx/deps.typ`. `""`, a non-`str` value, or a resolved path that is not an existing file raises `sphinx.errors.ExtensionError` from `TypstBuilder.write()` before any `.typ` file is written, with a message that starts with `typst_dependencies:` and contains the configured value rendered by `typsphinx.pathfmt.quote_path()`.
- K5 — Drift warning: one `logger.warning` per mismatched (file, package), with message text exactly `template dependency drift: {quote_path(relpath)} pins @preview/{package}:{template_versions}, but _typsphinx/deps.typ has @preview/{package}:{deps_version}`. `relpath` is the outdir-relative POSIX path of the copied file (`_template/<key>/<rel>.typ`). `template_versions` is every differing version found in that file, sorted by numeric (major, minor, patch) and joined by `, `. Warnings are emitted in ascending (relpath, package) order. The build exits 0.

## Intent coverage

- SC6
- SC7

## Acceptance criteria

1. SC6: `docs/source/user_guide/configuration.rst` documents `typst_dependencies`: the path rule (srcdir-relative or absolute), a single global file, a verbatim copy, the generated default when unset, and the build stop on a missing or empty value.
2. SC6: `docs/source/user_guide/templates.rst` lists the public `deps.typ` contract: the path `/_typsphinx/deps.typ` and every exported name (`codly`, `codly-init`, `codly-languages`, `mi`, `mitex`, `render`, `abstract`, `danger`, `error`, `info`, `memo`, `notify`, `task`, `tip`, `warning`, `typsphinx-init`). It states that output with a replaced `deps.typ` is not guaranteed because the translator targets the default versions' APIs (N4).
3. SC6: `docs/source/user_guide/templates.rst` tells template authors to take package names from `/_typsphinx/deps.typ` rather than pinning versions. `docs/source/user_guide/output_layout.rst` names `_typsphinx/` as reserved and states the outdir compile-root rule.
4. SC6: CHANGELOG.md `## [Unreleased]` records the single version source with the generated `deps.typ`, `typst_dependencies`, and the drift warning. `tests/test_release_0_9_8_docs_gate.py` still passes and still checks the 0.9.8 section.
5. SC6: CLAUDE.md's `@preview` version-sync section describes the new single source (`typsphinx/typst_deps.py` generating `<outdir>/_typsphinx/deps.typ`) and no longer says the versions live in three places. Its `writer.py` / `template_engine.py` Architecture bullets match the new preamble.
6. SC6: `tests/test_deps_contract_docs_gate.py` asserts AC1–AC5 and passes. The HTML docs build renders both pages, and the built `user_guide/configuration.html` contains `typst_dependencies` and `user_guide/templates.html` contains `/_typsphinx/deps.typ`, both checked in Verify.
7. SC7: on this task's landed HEAD, which contains T001–T004, `LC_ALL=C uv run pytest tests/` reports 0 failed, and `uv run black --check .`, `uv run ruff check .`, and `uv run mypy typsphinx/` are clean.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/test_deps_contract_docs_gate.py tests/test_release_0_9_8_docs_gate.py tests/test_output_layout_docs_gate.py -o addopts="" -q && d=$(mktemp -d) && uv run sphinx-build -q -E -b html docs/source "$d/html" && grep -q 'typst_dependencies' "$d/html/user_guide/configuration.html" && grep -q '/_typsphinx/deps' "$d/html/user_guide/templates.html" && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/
```

Heavy: yes

## Log

- 2026-11-03 — created by planner
